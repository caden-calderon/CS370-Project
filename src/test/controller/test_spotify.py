# test_spotify.py
# Author: Andrew Aberer

import logging
import sys
import os
import time

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


current_dir = os.path.dirname(os.path.abspath(__file__))
test_dir = os.path.dirname(current_dir)
src_dir = os.path.dirname(test_dir)
project_root = os.path.dirname(src_dir)

sys.path.insert(0, project_root)

try:
    from src.controller.spotify_controller import SpotifyController
    print("Successfully imported SpotifyController")
except ImportError as e:
    print("Unexpected ImportError")
    sys.exit(1)

# Spotify command mapping
spotify_commands = {
    0: "play",
    1: "pause",
    2: "next",
    3: "previous",
    4: "volume_up",
    5: "volume_down",
    6: "toggle_shuffle",
    7: "add_favorite",
    8: "like",
    9: "dislike",
    10: "switch_playlist"
}

spotify_gesture_labels = [
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
]

# Create a reverse mapping from gesture name to index
gesture_name_to_index = {name: idx for idx,
                         name in enumerate(spotify_gesture_labels)}


def print_available_commands():
    print("\n===== AVAILABLE SPOTIFY COMMANDS =====")
    print("Format: [INDEX] GESTURE_NAME - COMMAND")
    print("-" * 50)

    for idx, label in enumerate(spotify_gesture_labels):
        command = spotify_commands[idx]
        print(f"[{idx}] {label} - {command}")

    print("-" * 50)
    print("Enter command index, gesture name, or command name")
    print("Type 'list' to show commands again, or 'q' to quit")


def initialize_spotify():
    try:
        spotify_controller = SpotifyController()
        logger.info("Spotify controller initialized successfully")
        print("Spotify controller connected successfully!")
        return spotify_controller
    except Exception as e:
        logger.error(f"Failed to initialize Spotify controller: {str(e)}")
        print(f"Error connecting to Spotify: {str(e)}")
        print("Make sure your environment variables are set correctly:")
        print("  - SPOTIFY_CLIENT_ID")
        print("  - SPOTIFY_CLIENT_SECRET")
        print("  - SPOTIFY_REDIRECT_URI")
        return None


def process_command(spotify, command_input):
    try:
        # Check if input is a number (index)
        if command_input.isdigit():
            idx = int(command_input)
            if idx < 0 or idx >= len(spotify_commands):
                print(
                    f"Error: Index {idx} out of range (0-{len(spotify_commands)-1})")
                return
            command = spotify_commands[idx]
            gesture = spotify_gesture_labels[idx]

        # Check if input is a gesture name
        elif command_input in gesture_name_to_index:
            idx = gesture_name_to_index[command_input]
            command = spotify_commands[idx]
            gesture = command_input

        # Check if input is a direct command name
        elif command_input in spotify_commands.values():
            command = command_input
            # Find the index of this command
            idx = next((i for i, cmd in spotify_commands.items()
                       if cmd == command), None)
            gesture = spotify_gesture_labels[idx] if idx is not None else "Unknown"

        else:
            print(f"Error: Unknown command '{command_input}'")
            return

        print(f"Executing: {command} (gesture: {gesture})")

        result = spotify.execute_command(command)

        if result:
            print(f"Command executed successfully!")
        else:
            print(f"Command failed!")

    except Exception as e:
        print(f"Error processing command: {str(e)}")


def get_current_track(spotify):
    try:
        track_info = spotify.get_current_track_info()
        if track_info:
            print(f"Currently playing: {track_info}")
        else:
            print("No track currently playing")
    except Exception as e:
        print(f"Error getting track info: {str(e)}")


def main():
    print("=" * 50)
    print("Spotify Controller Test Script")
    print("=" * 50)
    print("Initializing Spotify controller...")

    # init Spotify controller
    spotify = initialize_spotify()
    if spotify is None:
        print("Could not initialize Spotify controller. Exiting.")
        return

    print("Ready to test Spotify commands!")
    print_available_commands()

    while True:
        try:
            command_input = input(
                "\nEnter command, 'track' for current track, 'list', or 'q' to quit: ").strip().lower()

            if command_input == 'q':
                print("Exiting test script.")
                break
            elif command_input == 'list':
                print_available_commands()
                continue
            elif command_input == 'track':
                get_current_track(spotify)
                continue

            process_command(spotify, command_input)

        except KeyboardInterrupt:
            print("\nExiting test script.")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
