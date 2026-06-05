import cv2
import time
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pathlib import Path
import pygame

WINDOW_NAME = "AI Sleep Tracker"
SOUND_PATH = Path("assets/siren_alert.mp3")
VIDEO_PATH = Path("assets/alert.mp4")
MODEL_PATH = "face_landmarker.task"

pygame.mixer.init()

def play_sound():
    if SOUND_PATH.exists():
        try:
            pygame.mixer.music.load(str(SOUND_PATH))
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error playing sound: {e}")
    else:
        print(f"Sound file not found: {SOUND_PATH}")

def play_video(video_path):
    if not video_path.exists():
        print(f"Video file not found: {video_path}")
        return

    cap = cv2.VideoCapture(str(video_path))
    window_name = "SIREN ALERT"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        cv2.imshow(window_name, frame)
        if cv2.waitKey(25) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyWindow(window_name)

if not Path(MODEL_PATH).exists():
    print(f"CRITICAL ERROR: {MODEL_PATH} not found. Please download the task file.")
    exit()

base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1,
    min_face_detection_confidence=0.5,
    min_face_presence_confidence=0.5,
    min_tracking_confidence=0.5,
    output_face_blendshapes=True
)
face_landmarker = vision.FaceLandmarker.create_from_options(options)

LEFT_EYE_TOP = 159
LEFT_EYE_BOTTOM = 145
LEFT_EYE_LEFT = 33
LEFT_EYE_RIGHT = 133
LEFT_IRIS = 468

EYE_CLOSED_THRESHOLD = 0.012  
DOOM_TRIGGER_SECONDS = 2.0
VERTICAL_THRESHOLD = 0.15 

running = True

def on_mouse_click(event, x, y, flags, param):
    global running
    if event == cv2.EVENT_LBUTTONDOWN:
        width = param['width']
        if width - 120 < x < width - 20 and 20 < y < 60:
            running = False

def main():
    global running
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    cv2.namedWindow(WINDOW_NAME)
    
    calibration_data = []
    calibration_avg = 0.5 
    calibration_duration = 3
    warmup_time = 2.0 
    start_time = time.time()
    is_calibrated = False

    distraction_start_time = None
    blink_counter = 0
    doom_events = 0
    eye_was_closed = False 

    while running:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        cv2.setMouseCallback(WINDOW_NAME, on_mouse_click, {'width': w})

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp = int(time.time() * 1000)
        
        result = face_landmarker.detect_for_video(mp_image, timestamp)

        status_color = (0, 255, 0)
        status_text = "FOCUSED"
        is_distracted = False 

        if result.face_landmarks:
            landmarks = result.face_landmarks[0]

            l_iris = landmarks[LEFT_IRIS]
            top = landmarks[LEFT_EYE_TOP]
            bottom = landmarks[LEFT_EYE_BOTTOM]
            left_p = landmarks[LEFT_EYE_LEFT]
            right_p = landmarks[LEFT_EYE_RIGHT]

            eye_height = abs(top.y - bottom.y)
            
            if eye_height > 0:
                iris_ratio = (l_iris.y - top.y) / eye_height
            else:
                iris_ratio = 0.5

            elapsed_total = time.time() - start_time
            
            if not is_calibrated:
                if elapsed_total < warmup_time:
                    cv2.putText(frame, "GET READY...", (int(w/2) - 100, int(h/2)),
                                cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 0), 2)
                    cv2.putText(frame, "Look at your screen normally", (int(w/2) - 200, int(h/2) + 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
                
                elif elapsed_total < (warmup_time + calibration_duration):
                    calibration_data.append(iris_ratio)
                    remaining = int((warmup_time + calibration_duration) - elapsed_total)
                    cv2.putText(frame, f"CALIBRATING... {remaining+1}s", (int(w/2) - 150, int(h/2)),
                                cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 255), 3)
                
                else:
                    if calibration_data:
                        calibration_avg = sum(calibration_data) / len(calibration_data)
                    is_calibrated = True
                    print(f"Calibrated Center: {calibration_avg:.2f}")

            else:
                
                is_looking_down = iris_ratio > (calibration_avg + VERTICAL_THRESHOLD)
                is_sleeping = eye_height < EYE_CLOSED_THRESHOLD

                if is_sleeping:
                    if not eye_was_closed:
                        eye_was_closed = True
                else:
                    if eye_was_closed:
                        blink_counter += 1
                        eye_was_closed = False

                if is_looking_down or is_sleeping:
                    is_distracted = True
                    status_color = (0, 0, 255)
                    
                    if is_sleeping:
                        status_text = "SLEEPING"
                    else:
                        status_text = "LOOKING DOWN"

                if is_distracted:
                    if distraction_start_time is None:
                        distraction_start_time = time.time()
                    
                    duration = time.time() - distraction_start_time
                    
                    bar_width = int((duration / DOOM_TRIGGER_SECONDS) * w)
                    cv2.rectangle(frame, (0, h-20), (bar_width, h), (0, 0, 255), -1)

                    if is_looking_down:
                         cv2.putText(frame, "LOOK UP!", (int(w/2) - 100, int(h/2)), 
                                    cv2.FONT_HERSHEY_DUPLEX, 2.0, (0, 0, 255), 4)

                    if duration > DOOM_TRIGGER_SECONDS:
                        print("ALARM TRIGGERED")
                        doom_events += 1
                        play_sound()
                        play_video(VIDEO_PATH)
                        distraction_start_time = None 
                else:
                    distraction_start_time = None
 
        cv2.putText(frame, f"Status: {status_text}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
        cv2.putText(frame, f"Blinks: {blink_counter}", (20, 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 200, 0), 2)
        
        btn_x1, btn_y1, btn_x2, btn_y2 = w - 120, 20, w - 20, 60
        cv2.rectangle(frame, (btn_x1, btn_y1), (btn_x2, btn_y2), (0, 0, 200), -1)
        cv2.putText(frame, "EXIT", (btn_x1 + 25, btn_y1 + 28), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow(WINDOW_NAME, frame)

        if cv2.waitKey(1) & 0xFF == 27:
            running = False

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()