import PySimpleGUI as sg
import RPi.GPIO as GPIO
import time
import pyfingerprint.pyfingerprint as FPF
from threading import Thread
import requests
from flask import Flask, request, jsonify

# Fingerprint sensor setup
sensor_path = '/dev/ttyS0'
baud_rate = 57600

# File paths for images
want_to_charge_img = "/home/sdam/Documents/gui/image/want_to_charge_img.png"
safe_charging_img = "/home/sdam/Documents/gui/image/safe_charging_img.png"
getoutf_image =  "/home/sdam/Documents/gui/image/1.png"
readingf_image = "/home/sdam/Documents/gui/image/readingf_image.png"
enrollf_error_image = "/home/sdam/Documents/gui/image/enrollf_error_image.png"
thumbs_up_img = "/home/sdam/Documents/gui/image/thumbs_up_img.png"

# GPIO setup
GPIO.setmode(GPIO.BCM)
lock_pins = [17, 27, 22, 23]  # GPIO pins for 4 solenoid locks
for pin in lock_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

def initialize_sensor():
    try:
        f = FPF.PyFingerprint(sensor_path, baud_rate, 0xFFFFFFFF, 0x00000000)
        if not f.verifyPassword():
            raise ValueError('The given fingerprint sensor password is wrong!')

        print('Found fingerprint sensor!')
        return f
    except Exception as e:
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        return None

# Function to capture fingerprint
def capture_fingerprint(f, window, status_key):
    try:
        print('Waiting for finger placement...')
        window[status_key].update('Waiting for finger placement...')
        while not f.readImage():
            pass

        print('Converting image...')
        window[status_key].update('Converting image...')
        f.convertImage(0x01)

        result = f.searchTemplate()
        position = result[0]
        if position >= 0:
            print('Fingerprint already exists at position #', position)
            window[status_key].update(f'Fingerprint already exists at position # {position}')
            return True

        return True
    except Exception as e:
        print('Error during fingerprint capture:', e)
        window[status_key].update(f'Error during fingerprint capture: {e}')
        return False

# Function to enroll fingerprint
def enroll_fingerprint(f, id, window, status_key):
    if not capture_fingerprint(f, window, status_key):
        return False

    print('Remove finger...')
    window['instruction_image'].update(filename=getoutf_image)
    window[status_key].update('Remove finger...')
    time.sleep(1)

    print('Place same finger again...')
    window['instruction_image'].update(filename=readingf_image)
    window[status_key].update('Place same finger again...')
    while not f.readImage():
        pass

    print('Converting image...')
    window[status_key].update('Converting image...')
    f.convertImage(0x02)

    print('Creating fingerprint model...')
    window[status_key].update('Creating fingerprint model...')
    if f.createTemplate():
        print('Storing fingerprint model...')
        window[status_key].update('Storing fingerprint model...')
        position = f.storeTemplate(id)
        print(f'Fingerprint enrolled successfully with ID #{id} at position #{position}')
        window[status_key].update(f'Fingerprint enrolled successfully with ID #{id} at position #{position}')
        return True
    else:
        print('Failed to create fingerprint model')
        window['instruction_image'].update(filename=enrollf_error_image)
        window[status_key].update('Failed to create fingerprint model')
        return False

# Function to delete fingerprint
def delete_fingerprint(f, id, window, status_key):
    try:
        sg.popup('Tring to delete', image=enrollf_error_image)
        if f.deleteTemplate(id):
            print(f'Fingerprint with ID #{id} deleted successfully!')
            window[status_key].update(f'Fingerprint with ID #{id} deleted successfully!')
            return True
        else:
            sg.popup('Failed to delete fingerprint!', image=enrollf_error_image)
            print('Failed to delete fingerprint!')
            window[status_key].update('Failed to delete fingerprint!')
            return False
    except Exception as e:
        sg.popup(f'Error deleting fingerprint: {e}', image=enrollf_error_image)
        print(f'Error deleting fingerprint: {e}')
        window[status_key].update(f'Error deleting fingerprint: {e}')
        return False

# Function to lock a specific locker
def lock_locker(locker_id):
    GPIO.output(lock_pins[locker_id], GPIO.HIGH)
    time.sleep(1)
    GPIO.output(lock_pins[locker_id], GPIO.LOW)

# Function to unlock a specific locker
def unlock_locker(locker_id):
    GPIO.output(lock_pins[locker_id], GPIO.HIGH)
    time.sleep(1)
    GPIO.output(lock_pins[locker_id], GPIO.LOW)

# Function to create the main window
def create_main_window(locker_status):
    layout = [
        [sg.Text('Smart Charging System', size=(200, 2), font=('Helvetica', 15), justification='center')],
        [sg.Button(f'Locker {i+1}', key=f'LOCKER_{i+1}', size=(15, 3), 
                   button_color=('white', 'green' if locker_status[i] == 'empty' else 'red'), pad=(10, 10), expand_x=True, expand_y=True) for i in range(2)],
        [sg.Button(f'Locker {i+3}', key=f'LOCKER_{i+3}', size=(15, 3), 
                   button_color=('white', 'green' if locker_status[i+2] == 'empty' else 'red'), pad=(10, 10), expand_x=True, expand_y=True) for i in range(2)],
        [sg.Exit(expand_x=True, expand_y=True)]
    ]
    return sg.Window('Smart Charging System', layout, size=(800, 400), finalize=True)

# Function to create the locking window
def create_locking_window():
    layout = [
        [sg.Text('Do you want to charge your phone with safety?', font=('Helvetica', 15), justification='center', size=(200, 2))],
        [sg.Image(filename=want_to_charge_img, key='instruction_image', size=(400, 200), expand_x=True, expand_y=True)],  # Replace with your actual image path
        [sg.Output(size=(100, 3))],
        [sg.Text('Status Text', key='status_text')],
        [sg.Button('Charge My Phone', size=(15, 3)), sg.Button('Exit', size=(15, 3))]
    ]
    return sg.Window('Locking Window', layout, size=(800, 400), finalize=True)

# Function to create the unlocking window
def create_unlocking_window():
    layout = [
        [sg.Text('We charge your Phone safely...', font=('Helvetica', 15), justification='center', size=(200, 2))],
        [sg.Image(filename=safe_charging_img, key='instruction_image', size=(400, 200), expand_x=True, expand_y=True)],  # Replace with your actual image path
        [sg.Output(size=(100, 3))],
        [sg.Text('Charging status:', key='status_text')],
        [sg.Button('Unlock', size=(15, 3), pad=(10, 10), expand_x=True, expand_y=True), sg.Button('Exit', size=(15, 3), pad=(10, 10), expand_x=True, expand_y=True)]
    ]
    return sg.Window('Unlocking Window', layout, size=(800, 400), finalize=True)


# Flask server setup
app = Flask(_name_)

API_KEY = '1234'  # Change this to a secure key

@app.route('/unlock', methods=['POST'])
def unlock():
    if 'API_KEY' not in request.headers or request.headers['API_KEY'] != API_KEY:
        return jsonify({'error': 'Unauthorized'}), 403

    if not request.json or 'locker_id' not in request.json:
        return jsonify({'error': 'Bad request'}), 400

    locker_id = request.json['locker_id']
    if 0 <= locker_id < 4:
        # Unlock the locker
        unlock_locker(locker_id)
        f = initialize_sensor()
        # Delete the associated fingerprint
        position = locker_id + 1  # Assuming position ID matches locker ID + 1
        delete_success = delete_fingerprint(f,1,None,None)  # No need for window or status_key here

        if delete_success:
            return jsonify({'status': 'Locker unlocked successfully', 'deleted_position': position}), 200
        else:
            return jsonify({'error': 'Failed to delete fingerprint'}), 500
    else:
        return jsonify({'error': 'Invalid locker ID'}), 400


def run_flask():
    app.run(host='0.0.0.0', port=5000)

def main():
    # Initialize fingerprint sensor
    f = initialize_sensor()
    if not f:
        return

    # Start Flask server in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    locker_status = ['empty', 'empty', 'empty', 'empty']
    main_window = create_main_window(locker_status)

    while True:
        event, values = main_window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        if 'LOCKER_' in event:
            locker_id = int(event.split('_')[1]) - 1

            if locker_status[locker_id] == 'empty':
                locking_window = create_locking_window()
                while True:
                    l_event, l_values = locking_window.read()
                    if l_event in (sg.WIN_CLOSED, 'Exit'):
                        break

                    if l_event == 'Charge My Phone':
                        id = locker_id + 1
                        locking_window['status_text'].update('Please place your finger...')
                        locking_window['instruction_image'].update(filename=readingf_image)
                        if enroll_fingerprint(f, id, locking_window, 'status_text'):
                            lock_locker(locker_id)
                            locker_status[locker_id] = 'charging'
                            main_window[event].update(button_color=('white', 'red'))
                            sg.popup('Locker locked successfully!', image=thumbs_up_img)
                            break
                        else:
                            locking_window['status_text'].update('Fingerprint enrollment failed. Try again.')
                locking_window.close()

            elif locker_status[locker_id] == 'charging':
                unlocking_window = create_unlocking_window()
                while True:
                    ul_event, ul_values = unlocking_window.read()
                    if ul_event in (sg.WIN_CLOSED, 'Exit'):
                        break

                    if ul_event == 'Unlock':
                        unlocking_window['status_text'].update('Please place your finger...')
                        unlocking_window['instruction_image'].update(filename=readingf_image)
                        if capture_fingerprint(f, unlocking_window, 'status_text'):
                            result = f.searchTemplate()
                            print(result)
                            print(result[0])
                            print(locker_id)
                            position = result[0]
                            if position == locker_id + 1:
                                unlock_locker(locker_id)
                                delete_fingerprint(f, position, unlocking_window, 'status_text')
                                locker_status[locker_id] = 'empty'
                                main_window[event].update(button_color=('white', 'green'))
                                sg.popup('Locker unlocked successfully! Thank you.', image=thumbs_up_img)
                                break
                            else:
                                unlocking_window['status_text'].update('Fingerprint does not match. Try again.')
                                unlocking_window['instruction_image'].update(filename=enrollf_error_image)
                unlocking_window.close()


    main_window.close()
    GPIO.cleanup()

if _name_ == "_main_":
    main()