# constants.py
# Author: Andrew Aberer

# gesture type enum
GESTURE_LIST = [
    "closed_to_open",  # 0
    "open_to_closed",  # 1
    "swipe_left",      # 2
    "swipe_right",     # 3
    "swipe_up",        # 4
    "swipe_down",      # 5
    "one",             # 6 - reserved for Spotify
    "two",             # 7 - reserved for Lifx
    "three",           # 8
    "four"             # 9
]


class ControllerType:
    SPOTIFY = "spotify"
    LIFX = "lifx"


SPOTIFY_COMMANDS = {
    0: "play",          # closed_to_open
    1: "pause",         # open_to_closed
    2: "previous",      # swipe_left
    3: "next",          # swipe_right
    4: "volume_up",     # swipe_up
    5: "volume_down",   # swipe_down
    8: "toggle_shuffle",  # three
    9: "add_favorite",   # four
    # 6 and 7 reserved for controller switching
}

LIFX_COMMANDS = {
    0: "lights_on",      # closed_to_open
    1: "lights_off",     # open_to_closed
    2: "toggle",         # swipe_left
    3: "toggle",         # swipe_right
    4: "brightness_up",  # swipe_up
    5: "brightness_down",  # swipe_down
    8: "set_color_red",  # three
    9: "set_color_blue"  # four
    # 6 and 7 reserved for controller switching
}

CONTROLLER_SWITCH_GESTURES = {
    6: ControllerType.SPOTIFY,  # "one" gesture switches to Spotify
    7: ControllerType.LIFX      # "two" gesture switches to LIFX
}

COMMAND_DESCRIPTIONS = {
    # Spotify commands
    "play": "Play or resume music",
    "pause": "Pause music playback",
    "previous": "Go to previous track",
    "next": "Skip to next track",
    "volume_up": "Increase volume",
    "volume_down": "Decrease volume",
    "toggle_shuffle": "Toggle shuffle mode on/off",
    "add_favorite": "Add current track to favorites",

    # LIFX commands
    "lights_on": "Turn on all lights",
    "lights_off": "Turn off all lights",
    "toggle": "Toggle lights on/off",
    "brightness_up": "Increase brightness",
    "brightness_down": "Decrease brightness",
    "set_color_red": "Change lights to red color",
    "set_color_blue": "Change lights to blue color"
}


# reverse mappings, easier lookup
def create_gesture_to_index_map():
    return {gesture: idx for idx, gesture in enumerate(GESTURE_LIST)}


def create_spotify_command_to_index_map():
    return {cmd: idx for idx, cmd in SPOTIFY_COMMANDS.items()}


def create_lifx_command_to_index_map():
    return {cmd: idx for idx, cmd in LIFX_COMMANDS.items()}


GESTURE_TO_INDEX = create_gesture_to_index_map()
SPOTIFY_COMMAND_TO_INDEX = create_spotify_command_to_index_map()
LIFX_COMMAND_TO_INDEX = create_lifx_command_to_index_map()


# command mapping by controller type
def get_command_map(controller_type):
    if controller_type == ControllerType.SPOTIFY:
        return SPOTIFY_COMMANDS
    elif controller_type == ControllerType.LIFX:
        return LIFX_COMMANDS
    else:
        raise ValueError(f"Unknown controller type: {controller_type}")
