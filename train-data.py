import os
import cv2
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

def rename_files(directory):
    files = os.listdir(directory)

    for i in range(len(files)):
        print(f"Renaming {i} files")
        old_name = files[i]
        new_name = f"{i + 1}{os.path.splitext(old_name)[1]}"
        os.rename(os.path.join(directory, old_name), os.path.join(directory, new_name))

def encodings():
    cred = credentials.Certificate("key.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://rakshai-b950b-default-rtdb.asia-southeast1.firebasedatabase.app",
        "storageBucket": "rakshai-b950b.appspot.com"
    })

    folderPath = "static/data/images"
    pathList = os.listdir(folderPath)
    imgList = []
    criminalIds = []

    for path in pathList:
        imgList.append(cv2.imread(os.path.join(folderPath, path)))
        criminalIds.append(os.path.splitext(path)[0])

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

    encodeListKnownWithIds = [encodeListKnown, criminalIds]

    with open("crimEnco.pkl", "wb") as f:
        pickle.dump(encodeListKnownWithIds, f)
def database():
    cred = credentials.Certificate("key.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://rakshai-b950b-default-rtdb.asia-southeast1.firebasedatabase.app",
        "storageBucket": "rakshai-b950b.appspot.com"
    })

    ref = db.reference("criminals")

    data = {
        "1":
        {
            "id": "1",
            "family_name": "Chauhan",
            "fore_name": "Ram",
            "gender": "Male",
            "dob": "11/04/1972 (51 years old)",
            "place": "SAINIK FARMS, NEW DELHI",
            "nationality": "India",
            "charges": "Punishment for criminal breach of trust, Cheating and dishonestly inducing delivery of property, Criminal conspiracy to commit an offence, Common intention.",
            "last_seen_time": "2022-12-11 00:54:34",
            "total_seen": 0,
        },
        "2":
        {
            "id": "2",
            "family_name": "Singh",
            "fore_name": "Vikramjeet",
            "gender": "Male",
            "dob": "06/06/1990 (33 years old)",
            "place": "Rajasthan",
            "nationality": "India",
            "charges": "House-trespass in order to commit offence punishable with death, attempts to commit offences not made punishable by other specific sections, criminal conspiracy, certain offences related to Arms/Ammunitions.",
            "last_seen_time": "2022-12-11 00:54:34",
            "total_seen": 0,
        },
        "3":
        {
            "id": "3",
            "family_name": "Jain",
            "fore_name": "Harshit Babulal",
            "gender": "Male",
            "dob": "02/12/1985 (37 years old)",
            "place": "Ahmedabad, Gujarat",
            "nationality": "India",
            "charges": "Cheating, Forgery, Criminal Conspiracy, offense related to IT Act, Offences related to Prevention of Gambling Act.",
            "last_seen_time": "2022-12-11 00:54:34",
            "total_seen": 0,
        },
        "4":
        {
            "id": "4",
            "family_name": "Kadian",
            "fore_name": "Yogesh",
            "gender": "Male",
            "dob": "12/07/2004 (19 years old)",
            "place": "VILLAGE BERI, DISTRICT JHAJJAR, HARYANA",
            "nationality": "India",
            "charges": "criminal conspiracy,attempt to murder, acts done by several persons in furtherance of a common intention, possession and use of prohibited arms and ammunition.",
            "last_seen_time": "2022-12-11 00:54:34",
            "total_seen": 0,
        },
        "5":
        {
            "id": "5",
            "family_name": "Singh",
            "fore_name": "Harbhej",
            "gender": "Male",
            "dob": "18/08/1998 (25 years old)",
            "place": "VILLAGE LOHARKA KALAN, AMRITSAR, PUNJAB",
            "nationality": "India",
            "charges": "Offense related to Narcotic Drugs and Psychotropic Substances Act, 1985 & Possessing illegal weapon.",
            "last_seen_time": "2022-12-11 00:54:34",
            "total_seen": 0,
        },
        "6":
        {
            "id": "6",
            "family_name": "Shaw",
            "fore_name": "Rohan",
            "gender": "Male",
            "dob": "05/10/2005 (18 years old)",
            "place": "Nalhati, Birbhum, West Bengal",
            "nationality": "India",
            "charges": "Test Case.",
            "last_seen_time": "2022-12-11 00:54:34",
            "total_seen": 0,
        },
    }

    for key, value in data.items():
        ref.child(key).set(value)

# rename_files("data/images")
# encodings()
database()