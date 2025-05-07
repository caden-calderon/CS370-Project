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
    from src.constants.constants import (
        GESTURE_LIST,
        SPOTIFY_COMMANDS,
        GESTURE_TO_INDEX,
        COMMAND_DESCRIPTIONS,
        ControllerType
    )
    print("Successfully imported SpotifyController & constants")
except ImportError as e:
    print("Unexpected ImportError")
    sys.exit(1)


def print_available_commands():
    print("\n===== AVAILABLE SPOTIFY COMMANDS =====")
    print("Format: [INDEX] GESTURE_NAME - COMMAND")
    print("-" * 50)

    for idx, gesture in enumerate(GESTURE_LIST):
        # inedx 6 and 7 are reserved for controller switching
        if idx in [6, 7]:
            print(f"[{idx}] {gesture} - Reserved for controller switching")
            continue

        if idx in SPOTIFY_COMMANDS:
            command = SPOTIFY_COMMANDS[idx]
            description = COMMAND_DESCRIPTIONS.get(command, "")
            print(f"[{idx}] {gesture} - {command} - {description}")
        else:
            print(f"[{idx}] {gesture} - No command assigned")

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
            if idx not in SPOTIFY_COMMANDS:
                print(f"Error: Index {idx} is not a valid Spotify command")
                return
            command = SPOTIFY_COMMANDS[idx]
            gesture = GESTURE_LIST[idx]

        # Check if input is a gesture name
        elif command_input in GESTURE_TO_INDEX:
            idx = GESTURE_TO_INDEX[command_input]
            if idx not in SPOTIFY_COMMANDS:
                print(
                    f"Error: Gesture '{command_input}' is not mapped to a Spotify command")
                return
            command = SPOTIFY_COMMANDS[idx]
            gesture = command_input

        # Check if input is a direct command name
        elif command_input in SPOTIFY_COMMANDS.values():
            command = command_input
            # Find the index of this command
            idx = next((i for i, cmd in SPOTIFY_COMMANDS.items()
                       if cmd == command), None)
            gesture = GESTURE_LIST[idx] if idx is not None else "Unknown"

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
