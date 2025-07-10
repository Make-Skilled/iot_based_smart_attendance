import cv2
import face_recognition
import os
import csv
import requests
import time
from datetime import datetime
import tkinter as tk
from PIL import Image, ImageTk
from threading import Thread

# Folder setup
os.makedirs("faces", exist_ok=True)
os.makedirs("data", exist_ok=True)

# ThingSpeak Configuration
THINGSPEAK_CHANNEL_ID = "3005560"
READ_API_KEY = "VHSDV3DSF21N8QFB"
WRITE_API_KEY = "ALW22BSTI0HSVEIO"

current_frame = None
recognized_name = "Unknown"
camera_running = True
exit_after_success = False

def wait_for_trigger():
    print("🔄 Waiting for motion trigger from ThingSpeak...")
    url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/fields/1/last.json?api_key={READ_API_KEY}"
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                field_value = int(data['field1']) if data['field1'] else 0
                print(f"🔍 Motion Status: {field_value}")
                if field_value == 1:
                    print("✅ Trigger received from ThingSpeak!")
                    return
        except Exception as e:
            print("❌ Error checking ThingSpeak:", e)
        time.sleep(3)

def reset_thingspeak_trigger():
    url = "https://api.thingspeak.com/update.json"
    data = {
        "api_key": WRITE_API_KEY,
        "field1": 0
    }
    try:
        requests.post(url, data=data)
        print("✅ Reset ThingSpeak trigger to 0.")
    except:
        print("❌ Failed to reset trigger.")

def load_known_faces():
    encodings, names = [], []
    for file in os.listdir("faces"):
        if file.endswith(".jpg"):
            path = f"faces/{file}"
            img = face_recognition.load_image_file(path)
            enc = face_recognition.face_encodings(img)
            if enc:
                encodings.append(enc[0])
                names.append(file[:-4])
    return encodings, names

def is_face_registered(frame):
    encodings, names = load_known_faces()
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = face_recognition.face_encodings(rgb)
    if not faces:
        return False, None
    for known_encoding, known_name in zip(encodings, names):
        match = face_recognition.compare_faces([known_encoding], faces[0])[0]
        distance = face_recognition.face_distance([known_encoding], faces[0])[0]
        if match and distance < 0.5:
            return True, known_name
    return False, None

def register_face():
    global current_frame, exit_after_success
    name = name_entry.get().strip()
    if not name:
        status_label.config(text="⚠️ Enter name first!")
        return
    found, existing_name = is_face_registered(current_frame)
    if found:
        status_label.config(text=f"⚠️ Face already registered as {existing_name}")
        return
    file_path = f"faces/{name}.jpg"
    rgb = cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)
    locs = face_recognition.face_locations(rgb)
    if len(locs) != 1:
        status_label.config(text="❌ Show only one face")
        return
    cv2.imwrite(file_path, current_frame)
    status_label.config(text=f"✅ Registered {name}")
    exit_after_success = True
    root.quit()

def mark_attendance(action):
    global recognized_name, exit_after_success
    if recognized_name == "Unknown":
        status_label.config(text="❌ Face not recognized")
        return
    filename = f"data/{recognized_name}.csv"
    date = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%H:%M:%S")

    if os.path.exists(filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
            if any(date in line and action in line for line in lines):
                status_label.config(text=f"⚠️ {action} already marked")
                return
            if action == "Check-out" and not any("Check-in" in line and date in line for line in lines):
                status_label.config(text="❌ No check-in found")
                return

    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([date, time_now, action])
    status_label.config(text=f"✅ {action} for {recognized_name}")
    exit_after_success = True
    root.quit()

def update_camera():
    global current_frame, recognized_name, camera_running
    encodings, names = load_known_faces()
    cap = cv2.VideoCapture(0)
    while camera_running:
        ret, frame = cap.read()
        current_frame = frame.copy()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        small = cv2.resize(rgb, (0, 0), fx=0.25, fy=0.25)
        face_locations = face_recognition.face_locations(small)
        face_encodings = [face_recognition.face_encodings(small, [loc])[0]
                          for loc in face_locations if face_recognition.face_encodings(small, [loc])]
        name = "Unknown"

        for encoding in face_encodings:
            matches = face_recognition.compare_faces(encodings, encoding)
            distances = face_recognition.face_distance(encodings, encoding)
            if distances.any():
                best = distances.argmin()
                if matches[best] and distances[best] < 0.5:
                    name = names[best]
        recognized_name = name

        for loc in face_locations:
            top, right, bottom, left = [v * 4 for v in loc]
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

    cap.release()

# 🔁 Main Loop
while True:
    wait_for_trigger()
    exit_after_success = False

    root = tk.Tk()
    root.title("Smart Face Attendance System")
    root.geometry("850x600")

    video_label = tk.Label(root)
    video_label.pack()

    tk.Label(root, text="Enter Name (for Register):").pack()
    name_entry = tk.Entry(root)
    name_entry.pack()

    tk.Button(root, text="📸 Register", width=20, command=register_face).pack(pady=2)
    tk.Button(root, text="✅ Check-In", width=20, command=lambda: mark_attendance("Check-in")).pack(pady=2)
    tk.Button(root, text="🔁 Check-Out", width=20, command=lambda: mark_attendance("Check-out")).pack(pady=2)
    tk.Button(root, text="❌ Quit", width=20, command=root.quit).pack(pady=2)

    status_label = tk.Label(root, text="", fg="blue")
    status_label.pack(pady=5)

    camera_running = True
    thread = Thread(target=update_camera)
    thread.start()

    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()
    camera_running = False

    reset_thingspeak_trigger()

    if not exit_after_success:
        print("🛑 GUI manually closed. Exiting loop.")
        break
