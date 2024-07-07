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
db_ref = db.reference('Hardware_project')

# Reference to your Firebase Storage bucket
bucket = storage.bucket()

def upload_file(id, file_path, destination_blob_name):
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return

        # Upload file to Firebase Storage
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(file_path)
        print(f"File {file_path} uploaded to {destination_blob_name}.")
        blob.make_public()

        # Get the public URL of the uploaded image
        image_url = blob.public_url

        # Store image URL along with the ID in Firebase Database
        data = {'id': id, 'imageUrl': image_url}
        db_ref.push(data)
        print(f"Data sent to Firebase: {data}")

    except Exception as e:
        print(f"Error uploading file or data: {e}")

def main():
    photo_directory = r"D:\Hardware Project\firebase\images"
    if not os.path.exists(photo_directory):
        print(f"Photo directory '{photo_directory}' does not exist.")
        return

    id = 2
    file_name = f"image_{id}.png"
    file_path = os.path.join(photo_directory, file_name)
    destination_blob_name = f"photos/{file_name}"  # Use consistent folder name

    # print(f"Looking for file at: {file_path}")
    # print(f"Current working directory: {os.getcwd()}")

    upload_file(id, file_path, destination_blob_name)
    print(destination_blob_name)

if __name__ == '__main__':
    main()
