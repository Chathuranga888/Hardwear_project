import time
import firebase_admin
from firebase_admin import credentials, db, storage
import random
import os


# Path to your Firebase Admin SDK JSON file
service_account_path = 'hardware-project-a6b3e-firebase-adminsdk-3v5lq-be4baa3b0d.json'

# Initialize Firebase
cred = credentials.Certificate(service_account_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://hardware-project-a6b3e-default-rtdb.firebaseio.com/',
    'storageBucket': 'hardware-project-a6b3e.appspot.com'
})

# Reference to your Firebase database path
db_ref = db.reference('Real_Time_Image_URL')

# Reference to your Firebase Storage bucket
bucket = storage.bucket()

def upload_file(file_path, destination_blob_name):
    """Uploads a file to the bucket."""
    try:
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(file_path)
        print(f"File {file_path} uploaded to {destination_blob_name}.")
        blob.make_public()
        image_url = blob.public_url

        data = {'imageUrl': image_url}
        db_ref.push(data)
        print(f"Data sent to Firebase: {data}")
    except Exception as e:
        print(f"Failed to upload {file_path} to {destination_blob_name}: {e}")
        blob.make_public()

def send_notification(message):
    ref = db.reference('notifications')
    ref.push({'message': message})
    print("Notification sent successfully")




def main():
    photo_directory =  r"D:\Hardware Project\firebase\images" # where path of images save

    if not os.path.exists(photo_directory):
        print(f"Photo directory '{photo_directory}' does not exist.")
        return
    
    file_name = f"image_3.png"
    print(file_name)
    file_path = os.path.join(photo_directory, file_name)
    destination_blob_name = f"Real Time Photos/{file_name}"
    upload_file(file_path,destination_blob_name)

    message = "Notification from Raspberry Pi"
    send_notification(message)

if __name__ == '__main__':
    main()