# AI Sleep & Distraction Tracker 😴🚀

An AI-powered computer vision system that monitors user fatigue and focus in real-time. By utilizing facial landmark detection and iris tracking, the application detects signs of drowsiness (closed eyes) or distraction (looking away/down) and triggers a dual-warning system (audio + video alerts) to regain the user's attention.

---

## ✨ Features

* **Real-time Fatigue Detection**: Calculates eye-opening height to detect when the user's eyes are closed (sleeping).
* **Distraction & Gaze Tracking**: Tracks relative iris positions to detect when the user is looking away or looking down (e.g., looking at a phone).
* **Personalized Auto-Calibration**: Calibrates dynamically to the user's normal eye level and sitting position during startup for personalized accuracy.
* **Dual Alert System**: 
  * 🔊 Plays a warning siren sound via Pygame mixer.
  * 📺 Displays a fullscreen video alert to immediately capture the user's attention.
* **Blink Counter**: Automatically tracks and displays the number of blinks during the session.
* **Exit Interface**: A simple on-screen exit button or press `ESC` key to close the application cleanly.

---

<h2>🛠️ Tech Stack</h2>

<p>

  <img src="https://skillicons.dev/icons?i=python" width="55" alt="Python"/>
  &nbsp;&nbsp;
  <img src="https://skillicons.dev/icons?i=opencv" width="55" alt="OpenCV"/>
  &nbsp;&nbsp;
  <img src="https://cdn.simpleicons.org/mediapipe/00C853" width="55" alt="MediaPipe"/>
  &nbsp;&nbsp;
  <img src="https://www.pygame.org/ftp/pygame-head-party.png" width="55" alt="Pygame"/>

</p>

<p>
  <b>🐍 Python</b> &nbsp; • &nbsp;
  <b>👁️ OpenCV</b> &nbsp; • &nbsp;
  <b>🎯 MediaPipe</b> &nbsp; • &nbsp;
  <b>🎮 Pygame</b>
</p>

<br>

| Technology | Purpose |
|:----------:|:--------|
| 🐍 **Python** | Core application logic |
| 👁️ **OpenCV** | Real-time camera feed processing & UI rendering |
| 🎯 **MediaPipe** | 468+ 3D facial landmarks & iris tracking |
| 🔊 **Pygame** | Warning sound & audio playback |

---

## 📋 Requirements

1. **Python 3.10+** installed on your system.
2. **Camera**: A built-in webcam or external USB camera.
3. **MediaPipe Face Landmarker Model**: 
   Download the `face_landmarker.task` bundle from [Google MediaPipe Tasks](https://developers.google.com/mediapipe/solutions/vision/face_landmarker#models) and place it in the root directory.

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/AI-Sleep-Tracker.git
cd AI-Sleep-Tracker
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python -m venv myenv
# Activate on Windows:
myenv\Scripts\activate
# Activate on macOS/Linux:
source myenv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Add Assets
Make sure you have an `assets` folder containing:
* `siren_alert.mp3` - The alert sound.
* `alert.mp4` - The alert video shown when fatigue is triggered.

### 5. Run the Application
```bash
python main.py
```

---

## ⚙️ How It Works (Calibration & Detection)

1. **Warmup & Setup (0-2s)**: Get comfortable and look directly at your screen.
2. **Calibration Phase (2-5s)**: The system reads your normal gaze and iris height to calibrate the "center" coordinate.
3. **Active Tracking**: 
   * If your eye height falls below the threshold, the system registers a **Sleep** state.
   * If your iris position drops significantly below your calibrated center, it registers a **Looking Down/Distracted** state.
   * A progress bar fills up at the bottom of the screen. If you remain distracted or asleep for more than **2 seconds**, the alarm sounds and the alert video plays.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---
