# main.py
# Author: Andrew Aberer & Caden Calderon


import logging
from gestures.predict_gestures import run_gesture_recognition
from src.controller.spotify_controller import SpotifyController
from src.controller.lifx_controller import LifxController
import time

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# init controllers
spotify = SpotifyController()
lifx = LifxController()

# TODO - finalize mapping (Define hand gesture number 1-4 mappings)
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

# execute a command on the specified controller


def execute_controller_command(controller_name, command):
    if controller_name == "spotify":
        return spotify.execute_command(command)
    elif controller_name == "lifx":
        return lifx.execute_command(command)
    else:
        logger.warning(f"Unknown controller: {controller_name}")
        return False


# TODO - load model
try:
    # model = tf.keras.models.load_model('path/to/your/gesture_recognition_model.h5')
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {str(e)}")
    exit(1)


def main():
    
    return


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
