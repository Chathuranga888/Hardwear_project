import PySimpleGUI as sg
# import RPi.GPIO as GPIO
import time
import pyfingerprint.pyfingerprint as FPF
# from picamera import PiCamera

# Fingerprint sensor setup
sensor_path = '/dev/ttyS0'
baud_rate = 57600

#Imamges
enrollf_error_image = '/home/sdam/hw_project/images/enrollf_error_image.png'
readingf_image = '/home/sdam/hw_project/images/readingf_image.png'
getoutf_image = '/home/sdam/hw_project/images/getoutf_image.png'

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
    [sg.Button("Charge Phone", key="charge_phone", size=(20, 4),expand_x=True,expand_y=True,pad=(30,30)), sg.Button("Unlock Container", key="unlock_container", size=(20, 4),expand_x=True,expand_y=True,pad=(30,30))],
             ]
    return sg.Window('Smart Charging System', layout, element_justification='center',size=(800, 400), finalize=True)

# Function to create charge phone window
def charge_phone_window():
    layout = [
    [sg.Text('Do you want to charge your phone with safety?')],
    [sg.Image(filename='instruction_image.png')],  # Replace with your actual image path
    [sg.Button('Charge My Phone'), sg.Button('Exit')]
                    ]   
    return sg.Window('Enter Your FingerPrint Here', layout, element_justification='center',size=(800, 400), finalize=True)


def main():
    # Initialize fingerprint sensor
    # f = initialize_sensor()
    # if not f:
    #     return

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

if __name__ == "__main__":
    main()