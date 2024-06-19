import PySimpleGUI as sg
import RPi.GPIO as GPIO
import time
import pyfingerprint.pyfingerprint as FPF
from threading import Thread
import requests
from flask import Flask, request, jsonify

import firebase_admin
from firebase_admin import credentials, firestore, storage

# Initialize Firebase
cred = credentials.Certificate("path/to/your/firebase-adminsdk.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'your-project-id.appspot.com'
})

db = firestore.client()
bucket = storage.bucket()


#######################################################

# Fingerprint sensor setup
sensor_path = '/dev/ttyS0'
baud_rate = 57600

# GPIO setup
GPIO.setmode(GPIO.BCM)
solenoid_pins = [17, 27, 22, 23]  # GPIO pins for 4 solenoid locks
ir_sensor_pins = [6, 13, 19, 26] # GPIO pins for the IR sensors

# Set solenoid pins as output and IR sensor pins as input
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
        [sg.Text('Smart Charging System', size=(200, 2), font=('Helvetica', 15), justification='center')],
        [sg.Button("Charge Phone", key="charge_phone",size=(15, 3))],
        [sg.Button("Unlock Container", key="unlock_container",size=(15, 3))]
    ]
    return sg.Window("Phone Charging and Locking System", layout)

# Function to create charge phone window
def charge_phone_window():
    layout = [
        [sg.Text('Enter Your FingerPrint', font=('Helvetica', 15), justification='center', size=(200, 2))],
        [sg.Text('TEXT GOES HERE',key='-PLACEHOLDER_1-')]
        #continue

    ]

# Function to create unlock container window
def unlock_container_window():
    pass

# Function to create face image capture
def face_image_capture_window():
    pass



# Function to capture a picture from ESP32 camera module
def capture_image_from_esp32(image_path):
    esp32_camera_url = "http://<ESP32_CAMERA_IP>/capture"
    response = requests.get(esp32_camera_url, stream=True)
    if response.status_code == 200:
        with open(image_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return True
    return False



# Function to handle fingerprint sensor interaction
def enroll_fingerprint():
    # Add code to interact with fingerprint sensor
    pass

# Function to store fingerprint ID and picture in Firebase
def store_user_data(fingerprint_id, image_path):
    # Store fingerprint ID in Firestore
    db.collection('users').document(fingerprint_id).set({
        'fingerprint_id': fingerprint_id
    })

    # Upload the image to Firebase Storage
    blob = bucket.blob(f'images/{fingerprint_id}.jpg')
    blob.upload_from_filename(image_path)

def main():
    # Initialize fingerprint sensor
    f = initialize_sensor()
    if not f:
        return
    #
    
    # Start Flask server in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    #
    
    window = create_main_window()
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break

        elif event == "charge_phone":
            charge_phone_window = charge_phone_window() #need to create
            while True:
                event, values = charge_phone_window.read()
                if event == sg.WIN_CLOSED:
                    break

                fingerprint_id = enroll_fingerprint()  #fingerprint enrollment

                face_image_capture = face_image_capture_window() #need to create
                while True:
                    event, values = face_image_capture.read()
                    if event == sg.WIN_CLOSED:
                        break
                    if fingerprint_id:  # Take image through ESP32 camera module
                        image_path = f'/tmp/{fingerprint_id}.jpg'
                        if capture_image_from_esp32(image_path):
                            store_user_data(fingerprint_id, image_path)

                            # Check for available container using IR sensors
                            available_container = None
                            for idx, pin in enumerate(ir_sensor_pins):
                                if GPIO.input(pin) == GPIO.LOW:  # Assuming LOW means container is empty
                                    available_container = idx
                                    break


                        if available_container is not None:

                            # Open the available container
                            GPIO.output(solenoid_pins[available_container], GPIO.HIGH)
                            time.sleep(1)  # Keep the solenoid lock open for 1 second
                            GPIO.output(solenoid_pins[available_container], GPIO.LOW)
                            sg.popup("Phone is now charging.")
                        else:
                            sg.popup("No available container.")
                    else:
                        sg.popup("Failed to capture image from ESP32 camera.")
            charge_phone_window.close()

                
        elif event == "unlock_container":
            unlock_container_window = unlock_container_window() #need to create
            while True:
                event, values = unlock_container_window.read()
                if event == sg.WIN_CLOSED:
                    break

                fingerprint_id = get_fingerprint() #all the code for fingerprint

                #all code for removing fingerprint sensor record in firebase
                if fingerprint_id: # Check fingerprint ID in Firebase
                    
                    user_doc = db.collection('users').document(fingerprint_id).get()
                    if user_doc.exists:
                        # Open corresponding container
                        sg.popup("Container unlocked. Have a nice day.")
                    else:
                        sg.popup("Fingerprint does not match.")
            unlock_container_window.close()

    window.close()

if __name__ == "__main__":
    main()

