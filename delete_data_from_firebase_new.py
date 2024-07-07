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

def delete_file_and_record(id):
    try:
        # Query the database for the record with the given ID
        snapshot = db_ref.order_by_child('id').equal_to(id).get()
        if not snapshot:
            print(f"No record found with id: {id}")
            return

        for key, val in snapshot.items():
            # Delete the image from Firebase Storage
            image_url = val.get('imageUrl')
            if image_url:
                blob_name = image_url.split('/')[-1]
                blob = bucket.blob(f'photos/{blob_name}')
                if blob.exists():
                    blob.delete()
                    print(f"Image {blob_name} deleted from storage.")

            # Delete the record from the database
            db_ref.child(key).delete()
            print(f"Record with id {id} deleted from database.")

    except Exception as e:
        print(f"Error deleting file or record: {e}")


def main():
    id = 1
    delete_file_and_record(id)


if __name__ == '__main__':
    main()