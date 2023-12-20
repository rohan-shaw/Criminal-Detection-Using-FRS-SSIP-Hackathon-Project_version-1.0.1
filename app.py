from flask import Flask, render_template, request, redirect, url_for, session, Response
from flask_wtf import CSRFProtect
from flask_login import LoginManager
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import cvzone
import numpy as np
import cv2
import face_recognition
import pickle
import os
from ultralytics import YOLO
import supervision as sv
from datetime import datetime
from python-dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
app.secret_key = 'os.getenv('SECRET_KEY')

csrf = CSRFProtect(app)

engine = pyttsx3.init()

camera = cv2.VideoCapture(0)

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": os.getenv('DATABASE_URL'),
    "storageBucket": os.getenv('STORAGE_BUCKET')
})

bucket = storage.bucket()

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_name):
    return user_name


detected_ids = []
det_names = []
det_time = []
ddet = []
cdet = []
sdet = []
bdet = []
bbdet = []

@app.route('/')
def index():
    if 'user_name' in session:
        return render_template('home.html')
    else:
        return render_template('index.html')

@app.route('/base')
def base():
    return render_template('base.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']

        try:
            admin_name = "Rohan"
            admin_password = "@RohanShaw"

            if user == admin_name:
                # Perform password verification
                if admin_password == password:
                    session['user_name'] = user
                    return redirect('/')
                else:
                    error = "Password is incorrect"
            else:
                error = "User email not found"

        except Exception as e:
            error = str(e)
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop("user_name", None)
    session.clear()
    return redirect(url_for('login'))

@app.route('/database')
def update_database():
    return render_template('u-data.html')

# @app.route('/train')
# def train():
#     return render_template('train-ai.html')
@app.route('/ai')
def ai():
    return render_template('ai.html')

# @app.route('/logs')
# def logs():
#     return render_template('logs.html')

@app.route('/database/criminals')
def criminal_database():
    crimInfo = []
    ref = db.reference("criminals")
    res = ref.get()
    l = len(res)
    for i in range(l):
        d = db.reference(f"criminals/{i}").get()
        crimInfo.append(d)
    return render_template('c-data.html', criminalInfo = crimInfo, index = i)

@app.route('/database/authorized')
def authorized_database():
    authInfo = []
    ref = db.reference("authorized")
    res = ref.get()
    l = len(res)
    for i in range(l):
        d = db.reference(f"authorized/{i}").get()
        authInfo.append(d)
    return render_template('a-data.html', authInfo = authInfo)

# @app.route('/train/criminals')
# def criminal_train():
#     return render_template('index.html')

# @app.route('/train/authorized')
# def authorized_train():
#     return render_template('index.html')


def generate_frames():
    file = open('authEnco.pkl', 'rb')
    encodeListKnownWithIds = pickle.load(file)
    file.close()

    encodeListKnown, criminalIds = encodeListKnownWithIds

    # print(criminalIds)

    counter = 0

    id = -1

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            faceCurFrame = face_recognition.face_locations(imgS)
            encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

            if faceCurFrame:
                for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                    matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                    faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                    # print("matches", matches)
                    # print("faceDis", faceDis)

                    matchIndex = np.argmin(faceDis)
                    # print("Match Index", matchIndex)

                    if matches[matchIndex]:
                        print("Known Face Detected")
                        # print(criminalIds[matchIndex])
                        y1, x2, y2, x1 = faceLoc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        # bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                        bbox = x1, y1, x2-x1, y2-y1
                        # imgBackground = cvzone.cornerRect(frame, bbox, rt=0)
                        imgBackground = cv2.rectangle(frame, (x1, y1), (x2, y2), (255,255,255), 2)
                        id = criminalIds[matchIndex]
                        if counter == 0:
                            cv2.putText(frame, "Loading", (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 1)
                            # cvzone.putTextRect(frame, "Loading", (x1+6, y2-6), scale=1, thickness=2)
                            counter = 1

                if counter!=0:
                    if counter==1:
                        criminalInfo = db.reference(f"criminals/{id}").get()
                        print(criminalInfo)
                        with open('criminalDetect.txt', 'a') as f:
                            f.write(f"Id : {criminalInfo['id']} | Name : {str(criminalInfo['family_name']+''+criminalInfo['fore_name'])} | Time : {criminalInfo['last_seen_time']} \n")
                        datetimeObject = datetime.strptime(criminalInfo['last_seen_time'],"%Y-%m-%d %H:%M:%S")
                        secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                        # print(secondsElapsed)
                        if secondsElapsed > 30:
                            ref = db.reference(f'criminals/{id}')
                            criminalInfo['total_seen'] += 1
                            ref.child('total_seen').set(criminalInfo['total_seen'])
                            ref.child('last_seen_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    cv2.putText(frame, str(criminalInfo['fore_name'] +" "+ criminalInfo['family_name']), (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 1)

                    counter+=1

            else:
                counter = 0
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def gen_fr_au():
    authorized_face_encodings = []
    authorized_face_names = []
    authorized_faces_dir = "static/data/authorized"  

    for filename in os.listdir(authorized_faces_dir):
        if filename.endswith(".jpeg"):
            img = face_recognition.load_image_file(os.path.join(authorized_faces_dir, filename))
            face_encoding = face_recognition.face_encodings(img)[0]
            authorized_face_encodings.append(face_encoding)
            authorized_face_names.append(os.path.splitext(filename)[0])
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Find all face locations and encodings in the current frame
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # Check if the detected face matches any authorized faces
                matches = face_recognition.compare_faces(authorized_face_encodings, face_encoding)
                name = "Unknown"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = authorized_face_names[first_match_index]

                    if name == "1" or name == 1:
                        name = "Rohan Shaw"

                    id = authorized_face_names[first_match_index]
                    authInfo = db.reference(f"authorized/{id}").get()
                    with open('authDetect.txt', 'a') as f:
                        f.write(f"Id : {authInfo['id']} | Name : {authInfo['name']} | Time : {authInfo['last_seen_time']} \n")
                    # if name!="1" or name!=1:
                    #     engine.say(f"Detected Unauthorized Person")
                    datetimeObject = datetime.strptime(authInfo['last_seen_time'],"%Y-%m-%d %H:%M:%S")
                    secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                    # print(secondsElapsed)
                    if secondsElapsed > 30:
                        ref = db.reference(f'criminals/{id}')
                        authInfo['total_seen'] += 1
                        ref.child('total_seen').set(authInfo['total_seen'])
                        ref.child('last_seen_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                # Draw a rectangle around the face and display the name
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
            # engine.runAndWait()
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')    

def gen_fr_wd():
    model=YOLO('best.pt')

    box_annotate = sv.BoxAnnotator(
        thickness=2,
        text_thickness=2,
        text_scale=1
    )
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            results = model(frame)[0]

            detections = sv.Detections.from_ultralytics(results)

            bounding_box_annotator = sv.BoundingBoxAnnotator()
            label_annotator = sv.LabelAnnotator()

            labels = [
                results.names[class_id]
                for class_id in detections.class_id
            ]

            frame = bounding_box_annotator.annotate(scene=frame, detections=detections)
            frame = label_annotator.annotate(scene=frame, detections=detections, labels=labels)
            with open('weaponDetect.txt', 'a') as f:
                f.write(f"Detected : {labels}")
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
def generate_frames_br():
    # camera.set(3, 1080)
    # camera.set(4, 720)

    file = open('crimEnco.pkl', 'rb')
    encodeListKnownWithIds = pickle.load(file)
    file.close()

    encodeListKnown, criminalIds = encodeListKnownWithIds

    counter = 0

    id = -1

    model=YOLO('best.pt')

    box_annotate = sv.BoxAnnotator(
        thickness=1,
        text_thickness=1,
        text_scale=1
    )

    message_list = []

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            message = ""
            message_list.append(message.encode('utf-8'))

            results = model(frame)[0]

            detections = sv.Detections.from_ultralytics(results)

            # imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            faceCurFrame = face_recognition.face_locations(imgS, , model="hog")
            encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

            bounding_box_annotator = sv.BoundingBoxAnnotator()
            label_annotator = sv.LabelAnnotator()

            # labels = [
            #     results.names[class_id]
            #     for class_id in detections.class_id
            # ]

            labels = ['Gun']

            frame = bounding_box_annotator.annotate(scene=frame, detections=detections)
            # frame = label_annotator.annotate(scene=frame, detections=detections, labels=labels)
            message = f"Detected {labels} at {datetime.now()}"
            message_list.append(message.encode('utf-8'))
            with open('brahmDetect.txt', 'a') as f:
                f.write(f"Detected : {labels} | {datetime.now()} \n")


            if faceCurFrame:
                for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                    matches = face_recognition.compare_faces(encodeListKnown, encodeFace, tolerance=0.5)
                    faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                    # print("matches", matches)
                    # print("faceDis", faceDis)

                    matchIndex = np.argmin(faceDis)
                    print("Match Index", matchIndex)

                    if matches[matchIndex]:
                        print("Known Face Detected")
                        # print(criminalIds[matchIndex])
                        y1, x2, y2, x1 = faceLoc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        # bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                        bbox = x1, y1, x2-x1, y2-y1
                        # imgBackground = cvzone.cornerRect(frame, bbox, rt=0)
                        imgBackground = cv2.rectangle(frame, (x1, y1), (x2, y2), (255,255,255), 2)
                        id = criminalIds[matchIndex]
                        if counter == 0:
                            cv2.putText(frame, "Loading", (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 1)
                            # cvzone.putTextRect(frame, "Loading", (x1+6, y2-6), scale=1, thickness=2)
                            counter = 1

                if counter!=0:
                    if counter==1:
                        criminalInfo = db.reference(f"criminals/{id}").get()
                        print(criminalInfo)
                        with open('brahmDetect.txt', 'a') as f:
                            f.write(f"Id : {criminalInfo['id']} | Name : {str(criminalInfo['fore_name'] +' '+ criminalInfo['family_name'])} | Time : {criminalInfo['last_seen_time']} \n")
                        # engine.say(f"Detected {str(criminalInfo['fore_name'] +' '+ criminalInfo['family_name'])}")
                        datetimeObject = datetime.strptime(criminalInfo['last_seen_time'],"%Y-%m-%d %H:%M:%S")
                        secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                        # print(secondsElapsed)
                        if secondsElapsed > 30:
                            ref = db.reference(f'criminals/{id}')
                            criminalInfo['total_seen'] += 1
                            ref.child('total_seen').set(criminalInfo['total_seen'])
                            ref.child('last_seen_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    cv2.putText(frame, str(criminalInfo['family_name']+""+criminalInfo['fore_name']), (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 1)

                    counter+=1

            else:
                counter = 0
            # engine.runAndWait()
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route("/ai/brahmyuh/feed")
def brahmyuh_feed():
    return Response(generate_frames_br(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route('/ai/brahmyuh')
def brahmyuh():
    return render_template('brahmyuh.html')

@app.route('/ai/brahmyuh/det')
def brahmyuh_det():
    # global bbsdet
    with open('brahmDetect.txt', 'r') as rd:
        detc = rd.read()
        lines = detc.split("\n")
        bbdet.append(lines)

    bbsdet = bbdet[-3:]
    return {"details" : lines}

@app.route('/ai/chakyuh/det')
def chakyuh_det():
    # global bbsdet
    with open('authDetect.txt', 'r') as rd:
        detc = rd.read()
        lines = detc.split("\n")
        bbdet.append(lines)

    bbsdet = bbdet[-3:]
    return {"details" : lines}

@app.route('/ai/brahmyuh/detections')
def bharmyuh_detections():
    with open('brahmDetect.txt', 'r') as rd:
        det = rd.read()
        for line in det:
            bdet.append(line)
    return render_template('brahmyuh-detect.html', bdet = bdet)


@app.route("/ai/dharmyuh/feed")
def dharmyuh_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route('/ai/dharmyuh')
def dharmyuh():
    return render_template('dharmyuh.html')

@app.route('/ai/dharmyuh/detections')
def dharmyuh_detections():
    with open('criminalDetect.txt', 'r') as rd:
        det = rd.read()
        for line in det.split('\n'):
            ddet.append(line)
    return render_template('dharmyuh-detect.html', ddet = ddet)

@app.route("/ai/chakyuh/feed")
def chakyuh_feed():
    return Response(gen_fr_au(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route('/ai/chakyuh')
def chakyuh():
    return render_template('chakyuh.html')


@app.route('/ai/chakyuh/detections')
def chakyuh_detections():
    with open('authDetect.txt', 'r') as rd:
        det = rd.read()
        for line in det.split('\n'):
            cdet.append(line)
    return render_template('chakyuh-detect.html', cdet = cdet)

@app.route("/ai/shastryuh/feed")
def shastryuh_feed():
    return Response(gen_fr_wd(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route('/ai/shastryuh')
def shastryuh():
    return render_template('shastryuh.html')

@app.route('/ai/shastryuh/detections')
def shastryuh_detections():
    with open('weaponDetect.txt', 'r') as rd:
        det = rd.read()
        for line in det.split('\n'):
            sdet.append(line)
    return render_template('shastryuh-detect.html', wdet = sdet)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0",port="3000")
