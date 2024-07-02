import PySimpleGUI as sg
import time
import sys
from time import sleep

sg.theme('black')

try:
    import RPi.GPIO as GPIO
    from picamera import PiCamera
    import pyfingerprint.pyfingerprint as FPF
    import board
    import busio
    from adafruit_ina219 import INA219
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

# Initialize I2C bus
# i2c_bus = busio.I2C(board.SCL, board.SDA)

# Initialize INA219 sensors with different addresses
# ina219_1 = INA219(i2c_bus)
# ina219_2 = INA219(i2c_bus, addr=0x41)
# ina219_3 = INA219(i2c_bus, addr=0x44)
# ina219_4 = INA219(i2c_bus, addr=0x45)

#current_sensor=[ina219_1,ina219_2,ina219_3,ina219_4]

# GPIO setup
if GPIO:
    GPIO.setmode(GPIO.BCM)
    solenoid_pins = [17, 27, 22, 23]  # GPIO pins for 4 solenoid locks
    ir_sensor_pins = [6, 13, 19, 26]  # GPIO pins for the IR sensors

# Image paths
enrollf_error_image = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\enrollf_error_image.png"
readingf_image = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\eadingf_image.png"
getoutf_image = '/home/sdam/hw_project/images/getoutf_image.png'
instruction_image = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\want_to_charge_img.png"
smile_face_image = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\smile.png"
thumbs_up_img = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\humsup.png"
locker_image = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\locker.png"
charge_complete_image = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\phone_charge_complete.png"
fingerprint_error_image = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\enrollf_error_image.png"
face_img = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\smile.png"

# Initialize List for lockers
lockers = ['Charging', 'Empty', 'Empty', 'Empty']  # Example for 4 solenoid locks

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
        [sg.Button("Charge Phone", key="charge_phone", size=(20, 4),  pad=(10,10))], 
        [sg.Button("Unlock Container", key="unlock_container", size=(20, 4),  pad=(10,10))],
        [sg.Button("Help", key="help", size=(20, 4),  pad=(10,10))],
    ]
    return sg.Window('Smart Charging System', layout, element_justification='center', size=(800, 400), finalize=True)

def charge_phone_window():
    layout = [
        [sg.Text('Do you want to charge your phone with safety?', font=('Helvetica', 15), justification='center')],
        [sg.Image(filename=instruction_image, key='instruction_image')],
        [sg.Output(size=(60, 2),  font=("Helvetica", 18))],
        [sg.Button('Enroll Your Finger.', expand_x=True, expand_y=True, pad=(15,15)), sg.Button('Exit', expand_x=True, expand_y=True,pad=(15,15))]
    ]
    return sg.Window('Enter Your FingerPrint Here', layout, element_justification='center', size=(800, 400), finalize=True)

def face_image_capture_window():
    layout = [
        [sg.Text('Capture Your Face Image', font=('Helvetica', 15), justification='center', size=(200, 2))],
        [sg.Image(filename=face_img, key='image')],
        [sg.Text('Please click the button below and place your face properly in the frame that follows and\n we will take a photo within five seconds.\nMake sure your face is clearly visible and well-lit.\n', justification='center', size=(150, 3), font=('Helvetica', 12), key='instruction_text')],
        [sg.Button('Take Photo', key='-TAKE_PHOTO-',font=('helvetica',12),expand_x=True,expand_y=True), sg.Button('Exit',font=('helvetica',12),expand_x=True,expand_y=True)]
    ]
    return sg.Window('Capture Your Face Image', layout, element_justification='center', size=(800, 400), finalize=True)

#to ask again about photo
def face_image_secondask_window(photo_id):
    layout = [
        [sg.Text('Image', font=('Helvetica', 15), justification='center', size=(200, 2))],
        [sg.Image(filename=locker_image, key='image1')],
        [sg.Button('Retake Photo', key='Retake Photo', expand_x=True, font=('helvetica',12)), sg.Button('Continue', expand_x=True, font=('helvetica',12))]
    ]
    return sg.Window('Retake or Continue', layout, element_justification='center', size=(800, 400), finalize=True)

def unlock_fingerprint_window():
    layout = [
        [sg.Text('We charged your phone safely, now you can take your phone.', font=('Helvetica', 15), justification='center')],
        [sg.Image(filename=charge_complete_image, key='instruction_image')],
        [sg.Output(size=(60,2))],
        [sg.Button('To Get Phone.', expand_x=True, expand_y=True, pad=(30, 30),visible=True), sg.Button('Exit', expand_x=True, expand_y=True, pad=(30, 30))]
    ]
    return sg.Window('Enter Your FingerPrint Here', layout, element_justification='center', size=(800, 400), finalize=True)

def charging_status_window():
    layout = [
        [sg.Text('Your phone is charging, please wait...', font=('Helvetica', 15), justification='center')],
        [sg.Image(filename=locker_image, key='instruction_image')],
        [sg.Text('Phone is still charging.Do you want to unlock the door?', justification='center', size=(150, 3), font=('Helvetica', 12), key='status_text')],
        [sg.Button('Unlock locker',expand_x=True, expand_y=True, pad=(10, 10)),sg.Button('Exit', expand_x=True, expand_y=True, pad=(10, 10))]
    ]
    return sg.Window('Charging Status', layout, element_justification='center', size=(800, 400), finalize=True)

def Help_page():
    sg.theme('black')
    layout = [[sg.Text('Help page',justification='center', size=(20,1), font=('Helvetica', 20))],
              [sg.Text('This is the help page')],
              [sg.Button('Back', size=(10,1)), sg.Button('contact', size=(10,1))]
              ]
    return sg.Window('Help page', layout,element_justification='center', size=(800, 400), finalize=True)

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
        event, _ = window.read()
        if event == sg.WIN_CLOSED:
            window.close()
            break
        elif event == "charge_phone":
            charge_window = charge_phone_window()
            while True:
                event, values = charge_window.read()
                if event == sg.WIN_CLOSED or event == "Exit":
                    charge_window.close()
                    break
                elif event == "Enroll Your Finger.":
                    available_container = next((idx for idx, locker in enumerate(lockers) if locker == 'Empty'), None)
                    if available_container is not None:
                        id = available_container + 1
                        # charge_window['text'].update('Please place your finger...')
                        # charge_window['instruction_image'].update(filename=readingf_image)
                        #if f and capture_fingerprint(f, unlock_finger_window, 'status_text'):
                        if True:
                            # lockers[available_container] = 'Charging'
                            # face_image_capture = face_image_capture_window()
                            while True:
                                # Create and display the face image capture window
                                face_image_capture = face_image_capture_window()
                                event, _ = face_image_capture.read()

                                if event == sg.WIN_CLOSED or event == "Exit":
                                    face_image_capture.close()
                                    break
                                elif event == '-TAKE_PHOTO-':
                                    # Uncomment and configure camera code as needed
                                    # if PiCamera:
                                    #     photo_filename = f'photo_{available_container}.jpg'
                                    #     camera.start_preview()
                                    #     sleep(5)  # Give time for the camera to adjust before taking the photo
                                    #     camera.capture(photo_filename)
                                    #     camera.stop_preview()
                                    # sg.popup('Photo taken successfully!', image=thumbs_up_img)

                                    face_image_capture.close()
                                    
                                    # Create and display the second window to ask the user if they want to retake the photo
                                    while True:
                                        face_second_window = face_image_secondask_window(1)
                                        event1, _ = face_second_window.read()
                                        
                                        if event1 == sg.WIN_CLOSED or event1 == "Exit":
                                            face_second_window.close()
                                            break  # Exit the second window loop, proceed to the next steps
                                            
                                        elif event1 == 'Retake Photo':
                                            face_second_window.close()
                                            break  # Close second window to re-open the photo capture window
                                            
                                        elif event1 == 'Continue':
                                            face_second_window.close()
                                            sg.popup('Now the locker is activated, enter your mobile phone and close the door after that press the OK button.', image=locker_image)
                                            # activate_solenoid(solenoid_pins[available_container], 5)
                                            charge_window.close()
                                            sg.popup('Photo taken successfully!', image=thumbs_up_img, auto_close=True, auto_close_duration=3,no_titlebar=True, keep_on_top=True,button_type=sg.POPUP_BUTTONS_NO_BUTTONS)

                                            break  # Exit the second window loop, proceed to the next steps
                                    
                                    if event1 != 'Retake Photo':
                                        break
                                        #continue # Exit the main loop if not retaking photo
        
                                    # Notify the user about the next steps
                                    # activate_solenoid(solenoid_pins[available_container], 5)
                                    
                                    #charge_window.close()
                                    #break
                                elif event == 'Exit':
                                    break
                            # auto close popup with thumbs up image, after 5 seconds without ok button
                            # sg.popup('Now the locker is activated, enter your mobile phone and close the door after that press the OK button.', image=locker_image)
                            # activate_solenoid(solenoid_pins[available_container], 5)

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
                    elif event == "To Get Phone.":
                        unlock_finger_window['instruction_image'].update(filename=readingf_image)
                        unlock_finger_window['To Get Phone.'].update(visible=False)  
                        
                        #if f and capture_fingerprint(f, unlock_finger_window, 'status_text'):
                        if True:
                            #f.searchTemplate()
                            chargin_stastus_window=charging_status_window()
                            while True:
                                event1, _ = chargin_stastus_window.read()
                                if event1==sg.WIN_CLOSED or event1=="Exit":
                                    chargin_stastus_window.close()
                                    break
                                elif event1=="Unlock locker":
                                    #activate_solenoid(solenoid_pins[occupied_container], 5)
                                    sg.popup('Now the locker is unlocked, get your mobile phone and close the door.', image=locker_image)
                                    chargin_stastus_window.close()
                                    unlock_finger_window.close()
                                    sg.popup('Photo taken successfully!', image=thumbs_up_img, auto_close=True, auto_close_duration=3,no_titlebar=True, keep_on_top=True,button_type=sg.POPUP_BUTTONS_NO_BUTTONS)
                                    
                                    break
                            #sg.popup('Now the locker is unlocked, get your mobile phone and close the door.', image=locker_image)
                            #activate_solenoid(solenoid_pins[occupied_container], 5)
                            #unlock_finger_window.close()
                            #break
                    #unlock_finger_window['To Get Phone.'].update[visible=False]
                #sg.popup('Photo taken successfully!', image=thumbs_up_img, auto_close=True, auto_close_duration=3,no_titlebar=True, keep_on_top=True,button_type=sg.POPUP_BUTTONS_NO_BUTTONS)

        elif event == "help":
            help_window = Help_page()
            while True:
                event, _ = help_window.read()
                if event == sg.WIN_CLOSED or event == "Back":
                    help_window.close()
                    break
                elif event == "contact":
                    while True:
                        # Create and display the face image capture window
                        face_image_capture = face_image_capture_window()
                        event, _ = face_image_capture.read()

                        if event == sg.WIN_CLOSED or event == "Exit":
                            face_image_capture.close()
                            break
                        elif event == '-TAKE_PHOTO-':
                            # Uncomment and configure camera code as needed
                            # if PiCamera:
                            #     photo_filename = f'photo_{available_container}.jpg'
                            #     camera.start_preview()
                            #     sleep(5)  # Give time for the camera to adjust before taking the photo
                            #     camera.capture(photo_filename)
                            #     camera.stop_preview()
                            # sg.popup('Photo taken successfully!', image=thumbs_up_img)

                            face_image_capture.close()
                            
                            # Create and display the second window to ask the user if they want to retake the photo
                            while True:
                                face_second_window = face_image_secondask_window(1)
                                event1, _ = face_second_window.read()
                                
                                if event1 == sg.WIN_CLOSED or event1 == "Exit":
                                    face_second_window.close()
                                    break  # Exit the second window loop, proceed to the next steps
                                    
                                elif event1 == 'Retake Photo':
                                    face_second_window.close()
                                    break  # Close second window to re-open the photo capture window
                                    
                                elif event1 == 'Continue':
                                    face_second_window.close()
                                    sg.popup('The Super user contact you soon.', image=locker_image)
                                    # activate_solenoid(solenoid_pins[available_container], 5)
                                    face_image_capture.close()
                                    
                                    #sg.popup('Photo taken successfully!', image=thumbs_up_img, auto_close=True, auto_close_duration=3,no_titlebar=True, keep_on_top=True,button_type=sg.POPUP_BUTTONS_NO_BUTTONS)

                                    break  # Exit the second window loop, proceed to the next steps
                            
                            if event1 != 'Retake Photo':
                                break
                                #continue # Exit the main loop if not retaking photo

                            # Notify the user about the next steps
                            # activate_solenoid(solenoid_pins[available_container], 5)
                            
                            #charge_window.close()
                            #break
                        # elif event == 'Exit':
                        #     break
        

    cleanup_gpio()
    #window.close()

if __name__ == "__main__":
    main()
