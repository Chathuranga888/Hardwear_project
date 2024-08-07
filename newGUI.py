import PySimpleGUI as sg
import RPi.GPIO as GPIO
import time
import pyfingerprint.pyfingerprint as FPF
from threading import Thread
import requests
from flask import Flask, request, jsonify
from picamera import PiCamera
import io
from PIL import Image
#import firebase_admin

#Imamges
enrollf_error_image = '/home/sdam/hw_project/images/enrollf_error_image.png'
readingf_image = '/home/sdam/hw_project/images/readingf_image.png'
getoutf_image = '/home/sdam/hw_project/images/getoutf_image.png'


# import firebase_admin
# from firebase_admin import credentials, firestore, storage

# # Initialize Firebase
# cred = credentials.Certificate("path/to/your/firebase-adminsdk.json")
# firebase_admin.initialize_app(cred, {
#     'storageBucket': 'your-project-id.appspot.com'
# })

# db = firestore.client()
# bucket = storage.bucket()

# Firebase configuration
# firebaseConfig = {
#     "apiKey": "AIzaSyC4O_SqJ6xh_aZUzxs5YEx-Fg54qwh6hZQ",
#     "authDomain": "hardware-project-288b1.firebaseapp.com",
#     "databaseURL": "https://console.firebase.google.com/project/hardware-project-288b1/firestore/databases/-default-/data/~2F",
#     "projectId": "hardware-project-288b1",
#     "storageBucket": "hardware-project-288b1.appspot.com",
#     "messagingSenderId": "877734039049",
#     "appId": "1:877734039049:web:80a5aab2cd253bef3832d8"
# }
#database url not sure

# firebase = pyrebase.initialize_app(firebaseConfig)
# storage = firebase.storage()

# Fingerprint sensor setup
sensor_path = '/dev/ttyS0'
baud_rate = 57600

# Initialize the camera
camera = PiCamera()
camera.resolution = (320, 240)

# GPIO setup
GPIO.setmode(GPIO.BCM)
solenoid_pins = [17, 27, 22, 23]  # GPIO pins for 4 solenoid locks
ir_sensor_pins = [6, 13, 19, 26] # GPIO pins for the IR sensors

Set solenoid pins as output and IR sensor pins as input
for pin in solenoid_pins:
    GPIO.setup(pin, GPIO.OUT)

for pin in ir_sensor_pins:
    GPIO.setup(pin, GPIO.IN)


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
    


# Function to initialize GUI
def create_main_window():
    layout = [
    [sg.Text('Smart Charging System', size=(30, 1), font=('Helvetica', 20), justification='center')],
    [sg.Button("Charge Phone", key="charge_phone", size=(20, 4),expand_x=True,expand_y=True), sg.Button("Unlock Container", key="unlock_container", size=(20, 4),expand_x=True,expand_y=True)]
             ]
    return sg.Window('Smart Charging System', layout, element_justification='center',size=(800, 400), finalize=True)

# Function to create charge phone window
def charge_phone_window():
    layout = [
        [sg.Text('Enter Your FingerPrint Here', font=('Helvetica', 20), justification='center', size=(30, 1))],
        [sg.Image(readingf_image,size=(200,200),enable_events=True,key='image')],
        [sg.Text('PLACEHOLDER', key='status_text', justification='center', size=(30, 1))]
    ]
    return sg.Window('Enter Your FingerPrint Here', layout, element_justification='center',size=(800, 400), finalize=True)

# Function to create unlock container window
def unlock_container_window():
        layout = [
        [sg.Text('Place Your Fingerprint', font=('Helvetica', 15), justification='center', size=(200, 2))],
        [sg.Button('Place Finger',key='-PLACE_FINGER-',size=(20, 4))],
        [sg.Text('TEXT GOES HERE',key='status_key')]
        ]
        return sg.Window('Place Your Fingerprint',layout,element_justification='center',size=(800, 400), finalize=True)

# Function to create face image capture
def face_image_capture_window():
    layout = [
    [sg.Text('Capture Your Face Image', font=('Helvetica', 15), justification='center', size=(200, 2))],
    
    [sg.Image(filename='', key='image')],
    [sg.Button('Take Photo', key='-TAKE_PHOTO-')]
            ]
    return sg.Window('Capture Your Face Image',layout,element_justification='center',size=(800, 400), finalize=True)

# Function to get the image from the camera
def get_image_from_camera(camera):
    stream = io.BytesIO()
    camera.capture(stream, format='jpeg')
    stream.seek(0)
    return Image.open(stream)

# Function to upload image to Firebase
# def upload_image_to_firebase(image):
#     bio = io.BytesIO()
#     image.save(bio, format='PNG')
#     bio.seek(0)
#     storage.child("images/image.png").put(bio)

# function to take image from user
def capture_photo(output_file):
    # Initialize the PiCamera
    with picamera.PiCamera() as camera:
        # Adjust camera settings as needed (optional)
        camera.resolution = (1280, 720)  # Example: set resolution
        camera.rotation = 180  # Example: rotate image 180 degrees

        # Wait for the camera to warm up (optional)
        time.sleep(2)

        # Capture a photo and save it to the specified file
        camera.capture(output_file)

        print(f"Captured photo saved to {output_file}")



# Function to handle fingerprint sensor interaction

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

def enroll_fingerprint(f, id, window, status_key):
    # Add code to interact with fingerprint sensor
    if not capture_fingerprint(f, window, status_key):
        return False

    print('Remove finger...')
    #window['instruction_image'].update(filename=getoutf_image)
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
    

# Function to lock a specific locker
def lock_locker(locker_id):
    GPIO.output(solenoid_pins[locker_id], GPIO.HIGH)
    time.sleep(1)
    GPIO.output(solenoid_pins[locker_id], GPIO.LOW)

# Function to unlock a specific locker
def unlock_locker(locker_id):
    GPIO.output(solenoid_pins[locker_id], GPIO.HIGH)
    time.sleep(1)
    GPIO.output(solenoid_pins[locker_id], GPIO.LOW)

# Function to store fingerprint ID and picture in Firebase
# def store_user_data(fingerprint_id, image_path):
#     # Store fingerprint ID in Firestore
#     db.collection('users').document(fingerprint_id).set({
#         'fingerprint_id': fingerprint_id
#     })

#     # Upload the image to Firebase Storage
#     blob = bucket.blob(f'images/{fingerprint_id}.jpg')
#     blob.upload_from_filename(image_path)

def main():
    # Initialize fingerprint sensor
    f = initialize_sensor()
    if not f:
        return
    #
    
    # Start Flask server in a separate thread
    # flask_thread = Thread(target=run_flask)
    # flask_thread.daemon = True
    # flask_thread.start()
    #
    
    window = create_main_window()
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break

        elif event == "charge_phone":
            charge_window = charge_phone_window()
            while True:
                event, values = charge_window.read()
                if event == sg.WIN_CLOSED:
                    break

                # Check for available container using IR sensors
                if event == 'image':
                    available_container = 0
                    for idx, pin in enumerate(ir_sensor_pins):
                        if GPIO.input(pin) == GPIO.LOW:  # Assuming LOW means container is empty
                            available_container = idx
                            break

                    #write code for if no available box
                    id = available_container + 1

                    #fingerprint enrollment
                    charge_window['status_text'].update('Please place your finger...')
                    charge_window['image'].update(filename=readingf_image) 
                    enroll_fingerprint_value = enroll_fingerprint(f, id, charge_window, 'status_text')

                    #create method to do if enroll fingerprint fail
                    if enroll_fingerprint_value == 1:
                        break

            charge_window.close()

                        

            face_image_capture = face_image_capture_window()
            while True:
                event, values = face_image_capture.read()
                if event == sg.WIN_CLOSED:
                    break

                # if fingerprint_id:  # Take image through ESP32 camera module
                #     image_path = f'/tmp/{fingerprint_id}.jpg'
                #     if capture_image_from_esp32(image_path):
                #         store_user_data(fingerprint_id, image_path)

                # if event == 'take_photo':
                #         output_file = "test.jpg"  # Specify the output file name
                #         capture_image_value = capture_photo(output_file) # no returning any value
                #         face_image_capture['status_key'].update('Image taken succesfully')

                if event == '-TAKE_PHOTO-':
                    # Get the current frame from the camera
                    # image = get_image_from_camera(camera)
                    # Upload the image to Firebase
                    # upload_image_to_firebase(image)
                    sg.popup('Photo taken and uploaded to Firebase!')

                # else:
                #     sg.popup("Failed to capture image from camera.")
                #     #back to the face image capture

                # Get the current frame from the camera
                # image = get_image_from_camera(camera)

                # Update the image in the PySimpleGUI window
                # bio = io.BytesIO()
                # image.save(bio, format='PNG')
                # window['-IMAGE-'].update(data=bio.getvalue())
                # camera.close()





                #if enroll_fingerprint_value and capture_image_value:
                if available_container is not None:

                    # Open the available container
                    GPIO.output(solenoid_pins[available_container], GPIO.HIGH)
                    time.sleep(1)  # Keep the solenoid lock open for 1 second
                    GPIO.output(solenoid_pins[available_container], GPIO.LOW)
                    sg.popup("Phone is now charging.")
                    break
                else:
                    sg.popup("No available container.")
                    break
            face_image_capture.close()

            

                
        elif event == "unlock_container":
            unlock_window = unlock_container_window() #need to create
            while True:
                event, values = unlock_window.read()
                if event == sg.WIN_CLOSED:
                    break

                if event == '-PLACE_FINGER-':
                    unlock_window['status_key'].update('Please place your finger...')
                    unlock_window.refresh()
                    #unlock_container_window['instruction_image'].update(filename=readingf_image)['instruction_image'].update(filename=readingf_image)
                    
                    if capture_fingerprint(f,unlock_container_window,'status_key'):
                        #all the code for fingerprint
                        result = f.searchTemplate()
                        position = result[0]


                        unlock_locker(position)
                        delete_fingerprint(f, position,unlock_container_window, 'status_key')





                    #all code for removing fingerprint sensor record in firebase
                    # if fingerprint_id: # Check fingerprint ID in Firebase
                        
                    #     user_doc = db.collection('users').document(fingerprint_id).get()
                    #     if user_doc.exists:
                    #         # Open corresponding container
                    #         sg.popup("Container unlocked. Have a nice day.")
                    #     else:
                    #         sg.popup("Fingerprint does not match.")
            unlock_container_window.close()

    window.close()

if __name__ == "__main__":
    main()

