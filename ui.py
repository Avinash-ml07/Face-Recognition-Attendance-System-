import tkinter as tk
from tkinter import messagebox, ttk
import cv2
import os
import sqlite3
import face_recognition
import numpy as np
from datetime import datetime

# ========================= Database Setup =========================
def init_face_db():
    conn = sqlite3.connect('faces.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS faces (
                    name TEXT,
                    encoding BLOB)''')
    conn.commit()
    conn.close()

def init_attendance_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    name TEXT,
                    date TEXT,
                    time TEXT)''')
    conn.commit()
    conn.close()

init_face_db()
init_attendance_db()

# ========================= Face Capture =========================
def capture_face():
    name = name_entry.get().strip()
    if not name:
        messagebox.showerror("Error", "Please enter a name first.")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open the camera.")
        return

    messagebox.showinfo("Instructions", "Position your face clearly. Capturing 3 frames.")

    face_encodings = []
    count = 0
    while count < 3:
        ret, frame = cap.read()
        if not ret:
            break
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb_frame)
        cv2.putText(frame,f"press space to capture{count+1}/3",(50,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
        cv2.imshow("Capture Face", frame)
        key = cv2.waitKey(1)

        if key == ord('q'):
            break
        if key == 32:  # Spacebar to capture
            if faces:
                encodings = face_recognition.face_encodings(rgb_frame, faces)

                if encodings:
                    face_encodings.append(encodings[0])
                    count += 1
                    messagebox.showinfo("Captured", f"Captured {count}/3 successfully.")
                else:
                    messagebox.showwarning("Warning", "Face not clear. Try again.")
            else:
                messagebox.showwarning("Warning", "No face detected. Try again.")
            cv2.putText(frame, f"Captured {count}/3", (50,50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        cv2.imshow("Capture Face", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if len(face_encodings) == 0:
        messagebox.showerror("Error", "No face detected.")
        return

    avg_encoding = np.mean(face_encodings, axis=0)

    conn = sqlite3.connect('faces.db')
    c = conn.cursor()
    c.execute("INSERT INTO faces (name, encoding) VALUES (?, ?)",
              (name, avg_encoding.tobytes()))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", f"Face data stored for {name}")

# ========================= Recognize & Mark Attendance =========================
def recognize_and_mark_attendance():
    # Load known encodings
    conn = sqlite3.connect('faces.db')
    c = conn.cursor()
    c.execute("SELECT name, encoding FROM faces")
    data = c.fetchall()
    conn.close()

    if not data:
        messagebox.showerror("Error", "No faces stored. Please capture first.")
        return

    known_names = []
    known_encodings = []
    for row in data:
        known_names.append(row[0])
        arr = np.frombuffer(row[1], dtype=np.float64)
        # Ensure shape is (128,)
        arr = arr.reshape((128,))
        known_encodings.append(arr)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open the camera.")
        return

    recognized_today = set()
    today = datetime.now().strftime('%Y-%m-%d')

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encs = face_recognition.face_encodings(rgb_frame, face_locations)

        for enc, (top, right, bottom, left) in zip(face_encs, face_locations):
            # Compute distances and find best match
            if len(known_encodings) > 0:
                distances = face_recognition.face_distance(known_encodings, enc)
                best_match_index = np.argmin(distances)
                if distances[best_match_index] < 0.5:  # tolerance
                    name = known_names[best_match_index]
                    if name not in recognized_today:
                        mark_attendance(name, today)
                        recognized_today.add(name)
                else:
                    name = "Unknown"
            else:
                name = "Unknown"

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Recognize & Mark Attendance (Press 'q' to quit)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    refresh_attendance_list()
    messagebox.showinfo("Done", "Recognition session ended.")


# ========================= Attendance DB Handling =========================
def mark_attendance(name, today):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT * FROM attendance WHERE name=? AND date=?", (name, today))
    if c.fetchone() is None:
        c.execute("INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)",
                  (name, today, datetime.now().strftime('%H:%M:%S')))
        conn.commit()
    conn.close()

# ========================= Attendance List UI =========================
def refresh_attendance_list():
    for row in tree.get_children():
        tree.delete(row)
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT name, date, time FROM attendance")
    rows = c.fetchall()
    conn.close()
    for r in rows:
        tree.insert('', tk.END, values=r)

# ========================= GUI =========================
root = tk.Tk()
root.title("Face Recognition Attendance System")
root.geometry("700x500")

# Name entry
tk.Label(root, text="Enter Name:").pack(pady=5)
name_entry = tk.Entry(root, width=30)
name_entry.pack(pady=5)

# Buttons
tk.Button(root, text="Capture Face", command=capture_face).pack(pady=10)
tk.Button(root, text="Recognize & Mark Attendance", command=recognize_and_mark_attendance).pack(pady=10)

# Attendance list display
tk.Label(root, text="Attendance List:").pack(pady=5)
columns = ("Name", "Date", "Time")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.pack(pady=10, fill=tk.BOTH, expand=True)

tk.Button(root, text="Refresh Attendance List", command=refresh_attendance_list).pack(pady=10)

root.mainloop()
