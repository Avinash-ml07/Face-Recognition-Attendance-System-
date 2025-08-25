import cv2, sqlite3
import numpy as np

DB_PATH = 'faces.db'
ANGLES = ['center', 'left', 'right']

def insert_user(name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO users (name) VALUES (?)', (name,))
    user_id = c.lastrowid
    conn.commit()
    conn.close()
    return user_id

def capture_faces(user_id, angle, image):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    _, buf = cv2.imencode('.jpg', image)
    c.execute('INSERT INTO face_images (user_id, angle, image) VALUES (?,?,?)',
              (user_id, angle, buf.tobytes()))
    conn.commit()
    conn.close()

def capture_angles():
    cap = cv2.VideoCapture(0)
    name = input("Enter name: ").strip()
    user_id = insert_user(name)
    print("Position your face: look CENTER, then press space.")
    for angle in ANGLES:
        while True:
            ret, frame = cap.read()
            cv2.imshow('Capture', frame)
            key = cv2.waitKey(1)
            if key == 32:  # Spacebar
                capture_faces(user_id, angle, frame)
                print(f"{angle.capitalize()} image captured.")
                break
            # Prompt instructions on screen
            cv2.putText(frame, f"Press space when looking {angle.upper()}",
                        (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    capture_angles()
