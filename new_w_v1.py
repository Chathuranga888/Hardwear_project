import PySimpleGUI as sg
#import RPi.GPIO as GPIO
import time
import pyfingerprint.pyfingerprint as FPF
#from picamera import PiCamera
from time import sleep

# Fingerprint sensor setup
sensor_path = '/dev/ttyS0'
baud_rate = 57600

# Initialize the camera
#camera = PiCamera()

# # GPIO setup
# GPIO.setmode(GPIO.BCM)
# solenoid_pins = [17, 27, 22, 23]  # GPIO pins for 4 solenoid locks
# ir_sensor_pins = [6, 13, 19, 26] # GPIO pins for the IR sensors

#Imamges
# enrollf_error_image = '/home/sdam/hw_project/images/enrollf_error_image.png'
# readingf_image =  "/home/sdam/hwproject/image/eadingf_image.png"  
# getoutf_image = '/home/sdam/hw_project/images/getoutf_image.png'
# instruction_image = "/home/sdam/hwproject/image/want_to_charge_img.png"
# smile_face_image = "/home/sdam/hwproject/image/smile.png"
# thumbs_up_img = "/home/sdam/hwproject/image/humsup.png"
# locker_image = "/home/sdam/hwproject/image/locker.png"

enrollf_error_image = '/home/sdam/hw_project/images/enrollf_error_image.png'
readingf_image =    "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\eadingf_image.png"
getoutf_image = '/home/sdam/hw_project/images/getoutf_image.png'
instruction_image = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\want_to_charge_img.png"
smile_face_image = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\smile.png"
thumbs_up_img = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\humsup.png"
locker_image = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\locker.png"
charge_complete_image = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\phone_charge_complete.png"
fingerprint_error_image = "D:\L1S2\INteligent machine Inspiration Project - CM1900\GUI\gui_with_chathuranga\Hardwear_project\image\enrollf_error_image.png"
# Initialize List for lockers
lokers = ['Empty', 'Empty', 'Empty', 'Empty']  # Example GPIO pins for 4 solenoid locks

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
        sg.popup('Error during fingerprint capture:', image=fingerprint_error_image)
        window[status_key].update(f'Error during fingerprint capture: {e}')
        return False


def enroll_fingerprint(f, id, window, status_key):
    # Add code to interact with fingerprint sensor
    if not capture_fingerprint(f, window, status_key):
        return False

    print('Remove finger...')
    window['instruction_image'].update(filename=getoutf_image)
    window[status_key].update('Remove finger...')
    time.sleep(1)

    print('Place same finger again...')
    #window['instruction_image'].update(filename=readingf_image)
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
        #window['instruction_image'].update(filename=enrollf_error_image)
        window[status_key].update('Failed to create fingerprint model')
        return False

# Function to delete fingerprint
def delete_fingerprint(f, id, window, status_key):
    try:
        #sg.popup('Tring to delete', image=enrollf_error_image)
        if f.deleteTemplate(id):
            print(f'Fingerprint with ID #{id} deleted successfully!')
            window[status_key].update(f'Fingerprint with ID #{id} deleted successfully!')
            return True
        else:
            #sg.popup('Failed to delete fingerprint!', image=enrollf_error_image)
            print('Failed to delete fingerprint!')
            window[status_key].update('Failed to delete fingerprint!')
            return False
    except Exception as e:
        #sg.popup(f'Error deleting fingerprint: {e}', image=enrollf_error_image)
        print(f'Error deleting fingerprint: {e}')
        window[status_key].update(f'Error deleting fingerprint: {e}')
        return False
    
    

# Function to initialize GUI
def create_main_window():
    layout = [
    [sg.Text('Smart Charging System', size=(30, 1), font=('Helvetica', 20), justification='center')],
    [sg.Button("Charge Phone", key="charge_phone", size=(20, 4),expand_x=True,expand_y=True,pad=(30,30)), sg.Button("Unlock Container", key="unlock_container", size=(20, 4),expand_x=True,expand_y=True,pad=(30,30))],
             ]
    return sg.Window('Smart Charging System', layout, element_justification='center',size=(800, 400), finalize=True)

# Function to create charge phone window
def charge_phone_window():
    layout = [
    [sg.Text('Do you want to charge your phone with safety?')],
    [sg.Image(filename=instruction_image,key='instruction_image')],  # Replace with your actual image path
    [sg.Text('Hellow', size=(30, 1), font=('Helvetica', 20), justification='center', key='text')],
    [sg.Button('Enroll Your Finger.',expand_x=True,expand_y=True,pad=(30,30)), sg.Button('Exit',expand_x=True,expand_y=True,pad=(30,30))]
                    ]   
    return sg.Window('Enter Your FingerPrint Here', layout, element_justification='center',size=(800, 400), finalize=True)

# Function to create face image capture
def face_image_capture_window():
    layout = [
    [sg.Text('Capture Your Face Image', font=('Helvetica', 15), justification='center', size=(200, 2))],
    
    [sg.Image(filename=smile_face_image, key='image')],
    [sg.Text('Please click the button below and place your face properly in the frame that follows and\n we will take a photo within five seconds.\nMake sure your face is clearly visible and well lite.\n',justification='center', size=(150, 3),font=('Helvetica', 12),key='instruction_text')],
    [sg.Button('Take Photo', key='-TAKE_PHOTO-'), sg.Button('Exit')]
            ]
    return sg.Window('Capture Your Face Image',layout,element_justification='center',size=(800, 400), finalize=True)

# Function to create unlock fingerprint window
def unlock_fingerprint_window():
    layout = [
    [sg.Text('We charged your phone safly, now you can take your phone.',font=('Helvetica', 15), justification='center', size=(200, 2))],
    [sg.Image(filename=charge_complete_image,key='instruction_image')],  # Replace with your actual image path
    #[sg.Output('status_text')],
    [sg.Button('Enroll Your Finger.',expand_x=True,expand_y=True,pad=(30,30)), sg.Button('Exit',expand_x=True,expand_y=True,pad=(30,30))]
                    ]   
    return sg.Window('Enter Your FingerPrint Here', layout, element_justification='center',size=(800, 400), finalize=True)


# Define the GPIO pins for the solenoids
solenoid_pins = [17, 18, 27, 22]

# def setup():
#     GPIO.setmode(GPIO.BCM)
#     for pin in solenoid_pins:
#         GPIO.setup(pin, GPIO.OUT)
#         GPIO.output(pin, GPIO.LOW)

# def activate_solenoid(pin, duration):
#     GPIO.output(pin, GPIO.HIGH)
#     time.sleep(duration)
#     GPIO.output(pin, GPIO.LOW)

# def cleanup():
#     GPIO.cleanup()




def main():
    # Initialize fingerprint sensor
    # f = initialize_sensor()
    # if not f:
    #     return

    window = create_main_window()
    while True:
        event, values = window.read(timeout=10)
        if event == sg.WIN_CLOSED:
            break
        elif event == "charge_phone":
            charge_window = charge_phone_window()
            while True:
                event, values = charge_window.read()
                if event == sg.WIN_CLOSED:
                    break
                elif event == "Enroll Your Finger.":
                    # for idx, pin in enumerate(ir_sensor_pins):
                    #     if GPIO.input(pin) == GPIO.LOW:  # Assuming LOW means container is empty
                    #         available_container = idx
                    #         break
                    available_container = 0
                    for idx, locker in enumerate(lokers):
                        if locker == 'Empty':
                            available_container = idx
                            print(available_container)
                            break
                    id = available_container + 1
                    charge_window['text'].update('Please place your finger...')
                    charge_window['instruction_image'].update(filename=readingf_image)
                    # charge_window.refresh()
                    # want to uncomment this for the fingerprint sensor
                    # enroll_fingerprint(f, id, charge_window, 'text')
                    print(2)
                    face_image_capture = face_image_capture_window()
                    while True:
                        event, values = face_image_capture.read()
                        if event == sg.WIN_CLOSED:
                            break
                        elif event == '-TAKE_PHOTO-':
                            # Capture and save photo
                            photo_filename = 'photo.jpg'
                            # camera.start_preview()
                            sleep(5)  # Adjust if necessary (gives time for camera to adjust)
                            # camera.capture(photo_filename)
                            # camera.stop_preview()
                            
  
                            break
                    face_image_capture.close()

                    # # Unlock the container based on the id
                    # GPIO.output(solenoid_pins[available_container], GPIO.HIGH)
                    sg.popup('Now the locker is activated, enter your mobile phone and close the door after that press the OK button.', image=locker_image)
                    # GPIO.output(solenoid_pins[available_container], GPIO.LOW)
                    break
                

                    # Unlock the container based on the id
                    # Assuming you have a function called unlock_container that takes the id as an argument
                    # unlock_container(id)
                elif event == "Exit":
                    charge_window.close()
                    break
        
            charge_window.close()
            # auto_close_popup()
            sg.popup_auto_close('We charge your phone safly!', auto_close_duration=5, keep_on_top=True, button_type=sg.POPUP_BUTTONS_NO_BUTTONS,image=thumbs_up_img)


        elif event == "unlock_container":
            # for idx, pin in enumerate(ir_sensor_pins):
            #     if GPIO.input(pin) == GPIO.HIGH:  # Assuming HIGH means container is occupied
            #         occupied_container = idx
            #         break
            occupied_container = 0
            for idx, locker in enumerate(lokers):
                if locker == 'Charging':
                    occupied_container = idx
                    break
            id = occupied_container + 1
            # Unlock the container based on the id
            # Assuming you have a function called unlock_container that takes the id as an argument
            # unlock_container(id)
            #activate_solenoid(solenoid_pins[occupied_container], 5)
            #lockers[occupied_container] = 'Empty'
            unloch_finger_window=unlock_fingerprint_window()
            while True:
                event, values = unloch_finger_window.read()
                if event == sg.WIN_CLOSED:
                    break
                elif event == "Enroll Your Finger.":
                    unloch_finger_window['status_text'].update('Please place your finger...')
                    unloch_finger_window['instruction_image'].update(filename=readingf_image)
                    # want to uncomment this for the fingerprint sensor
                    # if delete_fingerprint(f, id, unloch_finger_window, 'status_text'):
                    #     # lock_locker(locker_id)
                    #     lockers[occupied_container] = 'Empty'
                    #     break
                    sg.popup('Now the locker is unlocked, get your mobile phone and close the door.', image=locker_image)
                    

                    
                elif event == "Exit":
                    unloch_finger_window.close()
                    break
        elif event == "Exit":
            break

    
    window.close()
if __name__ == "__main__":
    main()
