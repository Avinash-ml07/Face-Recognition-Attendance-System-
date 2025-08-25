import cv2
import face_recognition
import sqlite3
from datetime import datetime
import numpy as np 


ATTENDANCE_DB = 'attendance.db'

def load_known_encodings():
    # Fetch all encodings and names from the faces.db
    conn = sqlite3.connect('faces.db')
    c = conn.cursor()
    c.execute("SELECT name, image FROM users INNER JOIN face_images ON users.user_id = face_images.user_id")
    rows = c.fetchall()
    conn.close()

    known_encodings = []
    names = []
    for name, img_data in rows:
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        rgb_img = img[:, :, ::-1]
        enc = face_recognition.face_encodings(rgb_img)
        if enc:
            known_encodings.append(enc[0])
            names.append(name)
    return known_encodings, names


def recognize_and_mark_attendance():
    known_encodings, names = load_known_encodings()
    recognized_people = set()

    conn = sqlite3.connect(ATTENDANCE_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_name TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()

    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_encodings, encoding)
            name = "Unknown"
            if True in matches:
                name = names[matches.index(True)]

                # Mark attendance only once per session & per day
                today = datetime.now().date()
                c.execute("SELECT * FROM attendance WHERE user_name=? AND DATE(timestamp)=?", (name, today))
                if not c.fetchone() and name not in recognized_people:
                    c.execute("INSERT INTO attendance (user_name) VALUES (?)", (name,))
                    conn.commit()
                    recognized_people.add(name)
                    print(f"[INFO] Attendance marked for {name}")

            # Draw bounding box and name
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow("Face Recognition & Attendance", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    conn.close()
