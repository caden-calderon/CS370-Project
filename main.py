# main.py

import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
import logging
from spotify_controller import SpotifyController
from lifx_controller import LifxController
import time

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# init controllers
spotify = SpotifyController()
lifx = LifxController()

# TODO - finalize mapping
gesture_mappings = {
    # Spotify Controls  ----------------------------------------
    0: {"controller": "spotify", "command": "play"},
    1: {"controller": "spotify", "command": "pause"},
    2: {"controller": "spotify", "command": "next"},
    3: {"controller": "spotify", "command": "previous"},
    4: {"controller": "spotify", "command": "volume_up"},
    5: {"controller": "spotify", "command": "volume_down"},
    6: {"controller": "spotify", "command": "toggle_shuffle"},
    7: {"controller": "spotify", "command": "add_favorite"},
    8: {"controller": "spotify", "command": "like"},
    9: {"controller": "spotify", "command": "dislike"},
    10: {"controller": "spotify", "command": "switch_playlist"},
    # LIFX Light Controls --------------------------------------
    11: {"controller": "lifx", "command": "lights_on"},
    12: {"controller": "lifx", "command": "lights_off"},
    13: {"controller": "lifx", "command": "brightness_up"},
    14: {"controller": "lifx", "command": "brightness_down"},
    15: {"controller": "lifx", "command": "toggle"},
    16: {"controller": "lifx", "command": "set_color_warm"},
    17: {"controller": "lifx", "command": "set_color_cool"},
    18: {"controller": "lifx", "command": "set_color_red"},
    19: {"controller": "lifx", "command": "set_color_blue"},
    20: {"controller": "lifx", "command": "pulse"}
}

# MediaPipe Hands for Spotify
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1
)
mp_drawing = mp.solutions.drawing_utils

# TODO - load model
try:
    # model = tf.keras.models.load_model('path/to/your/gesture_recognition_model.h5')
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {str(e)}")
    exit(1)

# TODO - load model mappings
gesture_labels = [
    # Spotify Controls (0-10) ----------------------------------
    "open_palm",    # play
    "closed_fist",  # pause
    "swipe_right",  # next track
    "swipe_left",   # previous track
    "swipe_up",     # volume up
    "swipe_down",   # volume down
    "circular",     # toggle shuffle
    "two_fingers",  # add to favorites
    "thumbs_up",    # like
    "thumbs_down",  # dislike
    "peace_sign",   # switch playlist
    
    # LIFX Controls (11-20) ------------------------------------
    "open_palm_hold",      # lights on
    "closed_fist_hold",    # lights off
    "swipe_up_hold",       # brightness up
    "swipe_down_hold",     # brightness down
    "finger_snap",         # toggle lights
    "one_finger_circle",   # warm white
    "two_finger_circle",   # cool white
    "finger_gun",          # red color
    "ok_sign",             # blue color
    "wave",                # pulse effect
]

# extract and normalize hand landmarks
def process_landmarks(hand_landmarks):
    landmarks = []
    for landmark in hand_landmarks.landmark:
        landmarks.extend([landmark.x, landmark.y, landmark.z])
    return landmarks

# execute a command on the specified controller
def execute_controller_command(controller_name, command):
    if controller_name == "spotify":
        return spotify.execute_command(command)
    elif controller_name == "lifx":
        return lifx.execute_command(command)
    else:
        logger.warning(f"Unknown controller: {controller_name}")
        return False


def main():
    # init webcam
    cap = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX

    # collect gesture sequence
    sequence = []
    sequence_length = 30  # Number of frames to collect for a gesture

    # smooth predictions (avoid fluctuations)
    gesture_smoothing_window = []
    smoothing_window_size = 5

    # cooldown to prevent rapid-fire commands
    last_command_time = 0
    cooldown_time = 2.0  # seconds

    # main loop
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            logger.warning("Failed to read from webcam")
            continue

        # convert to RGB for MediaPipe
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # process hand landmarks
        results = hands.process(image_rgb)

        # draw landmarks on the image
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # extract landmarks from first detected hand
            landmarks = process_landmarks(results.multi_hand_landmarks[0])

            # sequence buffer
            sequence.append(landmarks)
            if len(sequence) > sequence_length:
                sequence.pop(0)

            # if enough frames collected, predict gesture
            if len(sequence) == sequence_length:
                # preprocess and predict
                input_data = np.expand_dims(sequence, axis=0)
                prediction = model.predict(input_data, verbose=0)[0]
                gesture_index = np.argmax(prediction)
                confidence = prediction[gesture_index]

                # smoothing window
                gesture_smoothing_window.append(gesture_index)
                if len(gesture_smoothing_window) > smoothing_window_size:
                    gesture_smoothing_window.pop(0)

                # determine most common gesture in the window
                if len(gesture_smoothing_window) == smoothing_window_size:
                    # get most common gesture in the window
                    from collections import Counter
                    gesture_counts = Counter(gesture_smoothing_window)
                    stable_gesture_index, count = gesture_counts.most_common(1)[
                        0]

                    # only proceed if the gesture is stable (appears multiple times)
                    if count >= 3 and stable_gesture_index in gesture_mappings:
                        # cooldown
                        current_time = time.time()
                        if current_time - last_command_time >= cooldown_time:
                            # execute command
                            mapping = gesture_mappings[stable_gesture_index]
                            controller = mapping["controller"]
                            command = mapping["command"]

                            logger.info(
                                f"Detected gesture: {gesture_labels[stable_gesture_index]} ({confidence:.2f})")
                            logger.info(f"Executing: {controller} - {command}")

                            result = execute_controller_command(
                                controller, command)
                            if result:
                                # reset after successful command
                                last_command_time = current_time
                                sequence = []
                                gesture_smoothing_window = []

                # display prediction on frame
                gesture_name = gesture_labels[gesture_index] if gesture_index < len(
                    gesture_labels) else "Unknown"
                status_text = f"{gesture_name} ({confidence:.2f})"
                cv2.putText(image, status_text, (10, 30), font,
                            1, (0, 255, 0), 2, cv2.LINE_AA)

        # display the resulting frame
        cv2.imshow('Gesture Control', image)

        # Exit on ESC
        if cv2.waitKey(5) & 0xFF == 27:
            break

    # project clean up
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
