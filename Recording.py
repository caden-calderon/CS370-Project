# Author: Caden Calderon 

import cv2
import mediapipe as mp
import numpy as np
import os
import Processing
import time
import math
import inspect, mediapipe as mp

last_good = None

class Config:
    SEQUENCE_LENGTH = 20            
    CAMERA_PORT = 4  # Default webcam port 
    DATA_DIR = "collected_data"
    GESTURE = "open_to_close"  # <<< Adjust as needed 


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
    global last_good  # Keep record of last good frame for smoothing 

    # 1) No detection → re-use last_good if available
    if not results.multi_hand_landmarks:
        if is_recording and last_good is not None:
            buffer.append(last_good)
            cv2.putText(frame,
                        f"Rec: {len(buffer)}/{Config.SEQUENCE_LENGTH}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        return frame, buffer

    # 2) We have one or more hands – find the first right hand
    for idx, hl in enumerate(results.multi_hand_landmarks):
        handedness_label = results.multi_handedness[idx].classification[0].label
        if handedness_label != "Right":
            continue

        # draw the landmarks
        mp_drawing.draw_landmarks(frame, hl, mp_hands.HAND_CONNECTIONS)

        # flatten to [x0,y0,z0,...,x20,y20,z20]
        coords = [c for lm in hl.landmark for c in (lm.x, lm.y, lm.z)]

        # preprocess + record
        proc = Processing.preprocess_frame(
            coords,
            center=True,
            rotate=False,
            scale=True,
            lock_axes=(False, False, False)
        )
        last_good = proc

        if is_recording:
            buffer.append(proc)
            cv2.putText(frame,
                        f"Rec: {len(buffer)}/{Config.SEQUENCE_LENGTH}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

        break  # only process the first right hand

    return frame, buffer

def save_sequence(buffer, recording_id, cfg):
    arr = np.array(buffer)
    path = os.path.join(cfg.DATA_DIR, cfg.GESTURE, f"sequence_{recording_id}.npy")
    np.save(path, arr)
    print(f"Saved → {path}")


def main():
    cfg = Config()
    cap = cv2.VideoCapture(cfg.CAMERA_PORT, cv2.CAP_V4L2)        # Set camera with port 
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FPS, 30)
    print("Format:", cap.get(cv2.CAP_PROP_FOURCC))
    print("FPS:   ", cap.get(cv2.CAP_PROP_FPS))

    #cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)           # optional: lower latency

    mp_hands_mod = mp.solutions.hands              # MediaPipe setup
    mp_drawing = mp.solutions.drawing_utils
    mp_kwargs = dict(static_image_mode=False,
                     max_num_hands=1,
                     min_detection_confidence=0.2,
                     min_tracking_confidence=0.2)
    
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