# Author: Caden Calderon 

import cv2
import mediapipe as mp
import numpy as np
import time
import mediapipe as mp
import tensorflow as tf
from collections import deque
from . import processing
from tensorflow.keras.models import load_model


gesture_list = ["closed_to_open", "open_to_closed", "swipe_left", "swipe_right", "swipe_up", "swipe_down", "one", "two", "three", "four"]
last_good = None

class Config:
    SEQUENCE_LENGTH = 20
    CAMERA_PORT = 4  # Default webcam port
    PREDICT_THRESHOLD = 0.7  # How confident the model needs to be in order to say a prediction 

# A object to store the latest gesture
class ResultHolder:
    def __init__(self):
        self.latest_result = None

    def update(self, result):
        self.latest_result = result

    def get_latest(self):
        return self.latest_result


def capture_frame(cap):
    ret, frame = cap.read()
    if not ret:  # Frame was not successfully captured
        return None, None
    return cv2.flip(frame, 1), None  # Flip frame


def process_landmarks(frame, results, buffer, mp_drawing, mp_hands):
    global last_good  # Keep record of last good frame for smoothing

    # 1) No detection -> re-use last_good if available
    if not results.multi_hand_landmarks:
        if last_good is not None:
            buffer.append(last_good)
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
        proc = processing.preprocess_frame(
            coords,
            center=True,
            rotate=False,
            scale=True,
            lock_axes=(False, False, False)
        )
        last_good = proc
        
        buffer.append(proc)

    return frame, buffer


def predict(model, sequence, threshold=0.7):
    x = np.expand_dims(sequence, axis=0).astype(np.float32)
    probs = model.predict(x)[0]                 # shape (10,)
    cls  = np.argmax(probs)                     # int in [0..9]
    conf = probs[cls]                           # float in [0..1]
    if conf >= threshold:
        return cls, conf
    return None, None


def run_gesture_recognition(q):
    model = load_model('best_gesture_lstm.h5')
    cfg   = Config()
    cap   = cv2.VideoCapture(cfg.CAMERA_PORT, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FPS, 30)

    buffer = deque(maxlen=cfg.SEQUENCE_LENGTH)
    last_predict_at = 0
    PREDICT_COOLDOWN = 1.5

    last_cls  = None
    last_conf = 0.0

    mp_hands_mod = mp.solutions.hands
    mp_kwargs = dict(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.2,
        min_tracking_confidence=0.2
    )

    with mp_hands_mod.Hands(**mp_kwargs) as hands:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            frame, buffer = process_landmarks(
                frame, results,
                buffer,
                mp.solutions.drawing_utils,
                mp.solutions.hands
            )

            # Only predict once per cooldown interval
            if len(buffer) == cfg.SEQUENCE_LENGTH and results.multi_hand_landmarks:
                now = time.time()
                if now - last_predict_at > PREDICT_COOLDOWN:
                    cls, conf = predict(model, list(buffer), cfg.PREDICT_THRESHOLD)
                    if cls is not None:
                        last_cls, last_conf = cls, conf
                        q.put(gesture_list[last_cls])  # <-- send result to main
                    buffer.clear()
                    last_predict_at = now

            # Put the last prediction on every frame
            if last_cls is not None:
                cv2.putText(
                    frame,
                    f"{gesture_list[last_cls]} ({last_conf:.2f})",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )

            cv2.imshow("Live", frame)
            if cv2.waitKey(1) == 27:
                break
            
    cap.release()
    cv2.destroyAllWindows()
    
    
if __name__ == "__main__":
    run_gesture_recognition()

