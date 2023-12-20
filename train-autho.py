import os
import cv2
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from python-dotenv import load_dotenv

load_dotenv()

def rename_files(directory):
    files = os.listdir(directory)

    for i in range(len(files)):
        print(f"Renaming {i} files")
        old_name = files[i]
        new_name = f"{i + 1}{os.path.splitext(old_name)[1]}"
        os.rename(os.path.join(directory, old_name), os.path.join(directory, new_name))


def encodings_authorized():
    cred = credentials.Certificate("key.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": os.getenv('DATABASE_URL'),
        "storageBucket": os.getenv('STORAGE_BUCKET')
    })

    folderPath = "data/authorized"
    pathList = os.listdir(folderPath)
    imgList = []
    authIds = []

    for path in pathList:
        imgList.append(cv2.imread(os.path.join(folderPath, path)))
        authIds.append(os.path.splitext(path)[0])

        fileName = f"{folderPath}/{path}"
        bucket = storage.bucket()
        blob = bucket.blob(fileName)
        blob.upload_from_filename(fileName)

    def findEncodings(imagesList):
        encodeList = []
        for img in imagesList:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    encodeListKnown = findEncodings(imgList)

    encodeListKnownWithIds = [encodeListKnown, authIds]

    with open("autoEnco.pkl", "wb") as f:
        pickle.dump(encodeListKnownWithIds, f)

def database_authorized():
    cred = credentials.Certificate("key.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": os.getenv('DATABASE_URL'),
        "storageBucket": os.getenv('STORAGE_BUCKET')
    })

    ref = db.reference("authorized")

    data = {
        "1":
        {
            "id": "1",
            "name": "Rohan Shaw",
            "gender": "Male",
            "dob": "05/10/2005 (18 years old)",
            "place": "Kolkata",
            "nationality": "India",
            "last_seen_time": "2022-12-11 00:54:34",
            "total_seen": 0,
        },
    }

    for key, value in data.items():
        ref.child(key).set(value)



# rename_files("data/images")
# encodings_authorized()
database_authorized()
