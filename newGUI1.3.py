import PySimpleGUI as sg
# import RPi.GPIO as GPIO
import time
import pyfingerprint.pyfingerprint as FPF

# Mock functions to replace hardware-specific functions

def initialize_sensor():
    print('Mock: Found fingerprint sensor!')
    return True

def capture_fingerprint(f, window, status_key):
    try:
        print('Mock: Waiting for finger placement...')
        window[status_key].update('Waiting for finger placement...')
        time.sleep(1)  # Simulate delay

        print('Mock: Converting image...')
        window[status_key].update('Converting image...')
        time.sleep(1)  # Simulate delay

        print('Mock: Fingerprint already exists')
        window[status_key].update('Fingerprint already exists at position #1')
        return True
    except Exception as e:
        print('Mock: Error during fingerprint capture:', e)
        window[status_key].update(f'Error during fingerprint capture: {e}')
        return False

def enroll_fingerprint(f, id, window, status_key):
    if not capture_fingerprint(f, window, status_key):
        return False

    print('Mock: Remove finger...')
    window[status_key].update('Remove finger...')
    time.sleep(1)  # Simulate delay

    print('Mock: Place same finger again...')
    window[status_key].update('Place same finger again...')
    time.sleep(1)  # Simulate delay

    print('Mock: Converting image...')
    window[status_key].update('Converting image...')
    time.sleep(1)  # Simulate delay

    print('Mock: Creating fingerprint model...')
    window[status_key].update('Creating fingerprint model...')
    time.sleep(1)  # Simulate delay

    print('Mock: Storing fingerprint model...')
    window[status_key].update('Storing fingerprint model...')
    print(f'Mock: Fingerprint enrolled successfully with ID #{id}')
    window[status_key].update(f'Fingerprint enrolled successfully with ID #{id} at position #1')
    return True

def delete_fingerprint(f, id, window, status_key):
    try:
        print(f'Mock: Fingerprint with ID #{id} deleted successfully!')
        window[status_key].update(f'Fingerprint with ID #{id} deleted successfully!')
        return True
    except Exception as e:
        print(f'Mock: Error deleting fingerprint: {e}')
        window[status_key].update(f'Error deleting fingerprint: {e}')
        return False

def lock_locker(locker_id):
    print(f'Mock: Locker {locker_id} locked.')

def unlock_locker(locker_id):
    print(f'Mock: Locker {locker_id} unlocked.')

# GUI functions
def create_main_window():
    layout = [
        [sg.Text('Smart Charging System', size=(30, 1), font=('Helvetica', 20), justification='center')],
        [sg.Button("Charge Phone", key="charge_phone", size=(20, 4)), sg.Button("Unlock Container", key="unlock_container", size=(20, 4))]
    ]
    return sg.Window('Smart Charging System', layout, element_justification='center')

def charge_phone_window():
    layout = [
        [sg.Text('Enter Your FingerPrint Here', font=('Helvetica', 20), justification='center', size=(30, 1))],
        # [sg.Image('images.png', size=(200, 200),enable_events=True,key='-IMAGE-')],
        [sg.Output(size=(30, 10))],
        [sg.Text('PLACEHOLDER', key='status_text', justification='center', size=(30, 1))]
    ]
    return sg.Window('Enter Your FingerPrint Here', layout, element_justification='center')

def unlock_container_window():
    layout = [
        [sg.Text('Place Your Fingerprint', font=('Helvetica', 15), justification='center', size=(30, 1))],
        [sg.Text('TEXT GOES HERE', key='status_text')]
    ]
    return sg.Window('Unlock Container', layout, element_justification='center')

def face_image_capture_window():
    layout = [
        [sg.Text('Capture Face Image', font=('Helvetica', 20), justification='center', size=(30, 1))],
        [sg.Button("Take Image", key="-TAKE IMAGE-", size=(20, 4))]
        # Add elements for face image capture
    ]
    return sg.Window('Capture Face Image', layout, element_justification='center')

# Main function to run GUI
def main():
    f = initialize_sensor()
    if not f:
        return

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
                else:
                    available_container = 0  # Mock available container
                    if available_container is None:
                        sg.popup("No available container.")
                        break

                    id = available_container + 1

                    charge_window['status_text'].update('Please place your finger...')
                    # charge_window.refresh()
                    print("Hello Nishara")
                
                    result = enroll_fingerprint(f, id, charge_window, 'status_text')
                    print("Result")
                    print(result)
                    break


            charge_window.close()    


            # face_capture_window = face_image_capture_window()
            # while True:
                    
            #         event, values = face_capture_window.read()
            #         if event == sg.WIN_CLOSED:
            #             break

            #         # Implement image capture and storage here
            #         if event == '-TAKE IMAGE-':
            #             if available_container is not None:
            #                 unlock_locker(available_container)
            #                 sg.popup("Phone is now charging.")
                            
            #             else:
            #                 sg.popup("No available container.")

            #         print("close")
            #         face_capture_window.close()
                    

            

        elif event == "unlock_container":
            unlock_window = unlock_container_window()
            while True:
                event, values = unlock_window.read()
                if event == sg.WIN_CLOSED:
                    break

                unlock_window['status_text'].update('Please place your finger...')
                if capture_fingerprint(f, unlock_window, 'status_text'):
                    position = 0  # Mock position

                    if position >= 0:
                        unlock_locker(position)
                        delete_fingerprint(f, position, unlock_window, 'status_text')
                        sg.popup("Container unlocked. Have a nice day.")
                    else:
                        sg.popup("Fingerprint does not match.")
            unlock_window.close()

    window.close()

if __name__ == "__main__":
    main()
