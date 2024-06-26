import PySimpleGUI as sg
import time
import sys
from time import sleep

try:
    import RPi.GPIO as GPIO
    from picamera import PiCamera
    import pyfingerprint.pyfingerprint as FPF
except (ImportError, RuntimeError):
    # GPIO and Camera imports will only work on a Raspberry Pi
    GPIO = None
    PiCamera = None
    FPF = None

# Fingerprint sensor setup
sensor_path = '/dev/ttyS0'
baud_rate = 57600

# Initialize the camera if available
if PiCamera:
    camera = PiCamera()

# GPIO setup
if GPIO:
    GPIO.setmode(GPIO.BCM)
    solenoid_pins = [17, 27, 22, 23]  # GPIO pins for 4 solenoid locks
    ir_sensor_pins = [6, 13, 19, 26]  # GPIO pins for the IR sensors

# Image paths
enrollf_error_image = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\enrollf_error_image.png"
readingf_image =    "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\eadingf_image.png"
getoutf_image = '/home/sdam/hw_project/images/getoutf_image.png'
instruction_image = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\want_to_charge_img.png"
smile_face_image = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\smile.png"
thumbs_up_img = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\humsup.png"
locker_image = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\locker.png"
charge_complete_image = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\phone_charge_complete.png"
fingerprint_error_image = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\enrollf_error_image.png"

# Initialize List for lockers
lockers = ['Empty', 'Empty', 'Empty', 'Empty']  # Example for 4 solenoid locks

def initialize_sensor():
    if FPF:
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
    else:
        print('Fingerprint sensor library not available.')
        return None

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
            print(f'Fingerprint already exists at position #{position}')
            window[status_key].update(f'Fingerprint already exists at position #{position}')
            return True

        return True
    except Exception as e:
        print('Error during fingerprint capture:', e)
        sg.popup('Error during fingerprint capture:', image=fingerprint_error_image)
        window[status_key].update(f'Error during fingerprint capture: {e}')
        return False

def enroll_fingerprint(f, id, window, status_key):
    if not capture_fingerprint(f, window, status_key):
        return False

    print('Remove finger...')
    window['instruction_image'].update(filename=getoutf_image)
    window[status_key].update('Remove finger...')
    time.sleep(1)

    print('Place same finger again...')
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
        window[status_key].update('Failed to create fingerprint model')
        return False

def delete_fingerprint(f, id, window, status_key):
    try:
        if f.deleteTemplate(id):
            print(f'Fingerprint with ID #{id} deleted successfully!')
            window[status_key].update(f'Fingerprint with ID #{id} deleted successfully!')
            return True
        else:
            print('Failed to delete fingerprint!')
            window[status_key].update('Failed to delete fingerprint!')
            return False
    except Exception as e:
        print(f'Error deleting fingerprint: {e}')
        window[status_key].update(f'Error deleting fingerprint: {e}')
        return False

def create_main_window():
    layout = [
        [sg.Text('Smart Charging System', size=(30, 1), font=('Helvetica', 20), justification='center')],
        [sg.Button("Charge Phone", key="charge_phone", size=(20, 4), expand_x=True, expand_y=True, pad=(30, 30)), 
         sg.Button("Unlock Container", key="unlock_container", size=(20, 4), expand_x=True, expand_y=True, pad=(30, 30))],
    ]
    return sg.Window('Smart Charging System', layout, element_justification='center', size=(800, 400), finalize=True)

def charge_phone_window():
    layout = [
        [sg.Text('Do you want to charge your phone with safety?')],
        [sg.Image(filename=instruction_image, key='instruction_image')],
        [sg.Text('Hello', size=(30, 1), font=('Helvetica', 20), justification='center', key='text')],
        [sg.Button('Enroll Your Finger.', expand_x=True, expand_y=True, pad=(30, 30)), sg.Button('Exit', expand_x=True, expand_y=True, pad=(30, 30))]
    ]
    return sg.Window('Enter Your FingerPrint Here', layout, element_justification='center', size=(800, 400), finalize=True)

def face_image_capture_window():
    layout = [
        [sg.Text('Capture Your Face Image', font=('Helvetica', 15), justification='center', size=(200, 2))],
        [sg.Image(filename=smile_face_image, key='image')],
        [sg.Text('Please click the button below and place your face properly in the frame that follows and\n we will take a photo within five seconds.\nMake sure your face is clearly visible and well-lit.\n', justification='center', size=(150, 3), font=('Helvetica', 12), key='instruction_text')],
        [sg.Button('Take Photo', key='-TAKE_PHOTO-'), sg.Button('Exit')]
    ]
    return sg.Window('Capture Your Face Image', layout, element_justification='center', size=(800, 400), finalize=True)

def unlock_fingerprint_window():
    layout = [
        [sg.Text('We charged your phone safely, now you can take your phone.', font=('Helvetica', 15), justification='center', size=(200, 2))],
        [sg.Image(filename=charge_complete_image, key='instruction_image')],
        [sg.Button('Enroll Your Finger.', expand_x=True, expand_y=True, pad=(30, 30)), sg.Button('Exit', expand_x=True, expand_y=True, pad=(30, 30))]
    ]
    return sg.Window('Enter Your FingerPrint Here', layout, element_justification='center', size=(800, 400), finalize=True)

def setup_gpio():
    if GPIO:
        GPIO.setmode(GPIO.BCM)
        for pin in solenoid_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

def activate_solenoid(pin, duration):
    if GPIO:
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(pin, GPIO.LOW)

def cleanup_gpio():
    if GPIO:
        GPIO.cleanup()

def main():
    setup_gpio()

    f = initialize_sensor()
    window = create_main_window()

    while True:
        event, _ = window.read(timeout=10)
        if event == sg.WIN_CLOSED:
            break
        elif event == "charge_phone":
            charge_window = charge_phone_window()
            while True:
                event, _ = charge_window.read()
                if event == sg.WIN_CLOSED or event == "Exit":
                    charge_window.close()
                    break
                elif event == "Enroll Your Finger.":
                    available_container = next((idx for idx, locker in enumerate(lockers) if locker == 'Empty'), None)
                    if available_container is not None:
                        id = available_container + 1
                        charge_window['text'].update('Please place your finger...')
                        charge_window['instruction_image'].update(filename=readingf_image)
                        if f and enroll_fingerprint(f, id, charge_window, 'text'):
                            lockers[available_container] = 'Charging'
                            face_image_capture = face_image_capture_window()
                            while True:
                                event, _ = face_image_capture.read()
                                if event == sg.WIN_CLOSED or event == "Exit":
                                    face_image_capture.close()
                                    break
                                elif event == '-TAKE_PHOTO-':
                                    if PiCamera:
                                        photo_filename = 'photo.jpg'
                                        camera.start_preview()
                                        sleep(5)
                                        camera.capture(photo_filename)
                                        camera.stop_preview()
                                    sg.popup('Photo taken successfully!', image=thumbs_up_img)
                                    face_image_capture.close()
                                    break
                            sg.popup('Now the locker is activated, enter your mobile phone and close the door after that press the OK button.', image=locker_image)
                            activate_solenoid(solenoid_pins[available_container], 5)
                            charge_window.close()
                            break
                        else:
                            sg.popup('Fingerprint enrollment failed.', image=enrollf_error_image)

        elif event == "unlock_container":
            occupied_container = next((idx for idx, locker in enumerate(lockers) if locker == 'Charging'), None)
            if occupied_container is not None:
                id = occupied_container + 1
                unlock_finger_window = unlock_fingerprint_window()
                while True:
                    event, _ = unlock_finger_window.read()
                    if event == sg.WIN_CLOSED or event == "Exit":
                        unlock_finger_window.close()
                        break
                    elif event == "Enroll Your Finger.":
                        unlock_finger_window['instruction_image'].update(filename=readingf_image)
                        if f and delete_fingerprint(f, id, unlock_finger_window, 'status_text'):
                            lockers[occupied_container] = 'Empty'
                            sg.popup('Now the locker is unlocked, get your mobile phone and close the door.', image=locker_image)
                            activate_solenoid(solenoid_pins[occupied_container], 5)
                            unlock_finger_window.close()
                            break

    cleanup_gpio()
    window.close()

if __name__ == "__main__":
    main()
