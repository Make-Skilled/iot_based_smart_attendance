
# 📸 IoT-Based Smart Attendance System using ESP32, ThingSpeak, and Face Recognition

This is a smart attendance system that combines IoT and AI to automate attendance tracking. It uses:
- **ESP32 + IR sensor** to detect motion and trigger an event.
- **ThingSpeak** for cloud-based communication.
- **Python + OpenCV + Face Recognition + Tkinter** for facial identification and GUI.
- **CSV logging** for Check-in/Check-out actions.

---

## 🔧 Hardware Components
- ESP32
- IR Sensor
- Buzzer
- USB Cable
- Wi-Fi connection (e.g., Wokwi-GUEST)

---

## 💻 Software & Tools
- Arduino IDE (for ESP32)
- Python 3.x
- Required Python libraries:
  ```bash
  pip install opencv-python face_recognition pillow requests
  ```

---

## 📁 Folder Structure
```
iot_based_smart_attendance/
│
├── main.ino            # ESP32 code (Arduino)
├── main.py             # Python GUI + Face Recognition
├── faces/              # Folder storing registered faces
├── data/               # Folder for attendance logs (CSV)
└── README.md           # This file
```

---

## 🌐 ThingSpeak Configuration
- Create a ThingSpeak account: https://thingspeak.com/
- Create a new **channel** with one field:
  - Field 1: `MotionTrigger`
- Note down your:
  - Channel ID
  - Write API Key (for ESP32)
  - Read API Key (for Python script)

---

## 🚀 How It Works

### ESP32 (main.ino)
- Detects motion using IR sensor.
- On detection:
  - Activates buzzer.
  - Updates ThingSpeak Field1 to `1`.

### Python (main.py)
- Polls ThingSpeak Field1 until it detects `1`.
- Launches GUI with:
  - Live face detection.
  - Face registration.
  - Check-in / Check-out options.
- Recognizes faces and stores attendance logs in `data/{name}.csv`.
- Resets ThingSpeak Field1 back to `0`.

---

## 🖥️ How to Run the System

### 1. Flash ESP32
- Open `main.ino` in Arduino IDE.
- Set your Wi-Fi SSID/password and ThingSpeak Write API key.
- Upload to ESP32.

### 2. Run Python Script
```bash
python main.py
```

### 3. Face GUI
- Register a face (only one face visible in the camera).
- Click "Check-in" or "Check-out".
- Data saved in `data/` folder.

---

## ✅ Features
- Real-time motion detection using IR sensor.
- Face recognition via webcam.
- GUI for face registration & attendance marking.
- ThingSpeak integration for wireless trigger.
- Logs stored as CSV (local).

---

## 📈 Example CSV Output

```
data/John.csv

Date         | Time     | Action
-------------|----------|--------
2025-07-10   | 09:15:32 | Check-in
2025-07-10   | 17:45:11 | Check-out
```

---

## 🔐 Security Tips
- Don't expose your ThingSpeak API keys in public repositories.
- Add basic authentication to your GUI if used in shared environments.
- Use environment variables for secret keys in production.

---

## 🛠️ Future Enhancements
- Google Sheets or Firebase integration.
- Admin dashboard using Flask.
- Facial spoofing detection for added security.
- Multi-user support with different access roles.

---

## 📸 Demo Screenshots

> _(Include screenshots of GUI, ThingSpeak panel, and face recognition in action here)_

---

## 👩‍💻 Author
GitHub: [Make-Skilled](https://github.com/Make-Skilled)

---

## 📜 License
This project is licensed under the MIT License. Feel free to modify and use it.
