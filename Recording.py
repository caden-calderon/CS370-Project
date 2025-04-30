# Author: Caden Calderon 

import cv2
import mediapipe as mp
import numpy as np
import os
import Processing
import time
import math


class Config:
    SEQUENCE_LENGTH = 20            
    CAMERA_PORT = 0  # Default webcam port 
    DATA_DIR = "collected_data"
    GESTURE = "gesture_name"  # <<< Adjust as needed 


def get_next_recording_id(cfg):
    path = os.path.join(cfg.DATA_DIR, cfg.GESTURE)
    os.makedirs(path, exist_ok=True)  # Make directory if not made 
    return len(os.listdir(path))


def capture_frame(cap):
    ret, frame = cap.read()
    if not ret:  # Frame was not successfully captured 
        return None, None
    return cv2.flip(frame, 1), None  # Flip frame 


def process_landmarks(frame, results, is_recording, buffer, mp_drawing, mp_hands):
    if not results.multi_hand_landmarks:  # Didn't find hand landmarks (e.g hand is not in frame)
        return frame, buffer

    for hl in results.multi_hand_landmarks:  # Loop over each hand detected, 1 hand by default  
        mp_drawing.draw_landmarks(frame, hl, mp_hands.HAND_CONNECTIONS)  # Draw dots and lines connecting on landmarks 
        coords = [coord for lm in hl.landmark for coord in (lm.x, lm.y, lm.z)]  # Coordinates of landmarks 
        if is_recording:
            proc = Processing.preprocess_frame(
                coords, center=True, normalize=True, lock_axes=(False,False,False)  # Center, normalize, or lock coordinates 
            )
            buffer.append(proc)
            cv2.putText(frame, f"Rec: {len(buffer)}/{Config.SEQUENCE_LENGTH}",  # Display frame count 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    return frame, buffer


def save_sequence(buffer, recording_id, cfg):
    arr = np.array(buffer)
    path = os.path.join(cfg.DATA_DIR, cfg.GESTURE, f"sequence_{recording_id}.npy")
    np.save(path, arr)
    print(f"Saved → {path}")


def main():
    cfg = Config()
    cap = cv2.VideoCapture(cfg.CAMERA_PORT)        # Set camera with port 
    #cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)           # optional: lower latency
    
    mp_hands_mod = mp.solutions.hands              # MediaPipe setup
    mp_drawing = mp.solutions.drawing_utils
    mp_kwargs = dict(static_image_mode=False,
                     max_num_hands=1,
                     min_detection_confidence=0.7,
                     min_tracking_confidence=0.5)
    
    recording_id = get_next_recording_id(cfg)
    is_recording = False
    buffer = []    
    
    with mp_hands_mod.Hands(**mp_kwargs) as hands:
        while cap.isOpened():
            frame, _ = capture_frame(cap)
            if frame is None:
                break
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Convert BGR to RGB 
            results = hands.process(rgb_frame)
            frame, buffer = process_landmarks(frame, results, is_recording, buffer, mp_drawing, mp_hands_mod)

            cv2.imshow("Collect", frame)
            key = cv2.waitKey(1)

            # handle keypresses
            if key == ord('r') and not is_recording:  # Press R to start recording 
                print("\n\nRecording started")
                is_recording, buffer = True, []
            elif is_recording and len(buffer) >= cfg.SEQUENCE_LENGTH:  # If gesture is done recording save it 
                save_sequence(buffer, recording_id, cfg)
                is_recording, buffer = False, []
                recording_id += 1
            elif key == 27:  # Press esc to end session 
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()