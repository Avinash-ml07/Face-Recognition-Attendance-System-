# Face Recognition Attendance System (Tkinter + OpenCV)

A simple, offline attendance system using **Python**, **Tkinter**, **OpenCV**, and **face_recognition**.  
It lets you:

- Capture faces with **guided angles** (Center → Left → Right)
- Store encodings in **SQLite** (`faces.db`)
- Recognize faces from webcam and **mark attendance** (`attendance.db`)
- View attendance in the GUI

---

## ✨ Features

- **Guided Face Capture**: On-screen prompts to look **CENTER**, **LEFT**, **RIGHT** and capture three positions.
- **Reliable Matching**: Uses 128-D encodings and distance thresholding.
- **Duplicate Protection**: Attendance marked **once per person per day**.
- **All-in-One GUI**: No terminal prompts; everything from Tkinter.

---

## 🧰 Requirements

- Python **3.8+**
- Packages:
  - `opencv-python`
  - `face_recognition` (uses `dlib`)
  - `numpy`
 

## Demo Video

[Watch the demo]([demo.mp4](https://drive.google.com/file/d/1YP1fkU4KMJiqdy1tjkP_kPzQPlCZzJcA/view?usp=sharing))

Install:
```bash
pip install opencv-python face_recognition numpy





