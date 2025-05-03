# test_lifx.py
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
    from src.controller.lifx_controller import LifxController
    print("Successfully imported LifxController")
except ImportError as e:
    print(f"Unexpected ImportError: {e}")
    sys.exit(1)

# LIFX command mapping
lifx_commands = {
    0: "lights_on",
    1: "lights_off",
    2: "brightness_up",
    3: "brightness_down",
    4: "toggle",
    5: "set_color_warm",
    6: "set_color_cool",
    7: "set_color_red",
    8: "set_color_blue",
    9: "set_color_green",
    10: "set_color_purple",
    11: "pulse"
}

lifx_gesture_labels = [
    "open_palm_hold",     # lights on
    "closed_fist_hold",   # lights off
    "swipe_up_hold",      # brightness up
    "swipe_down_hold",    # brightness down
    "finger_snap",        # toggle lights
    "one_finger_circle",  # warm white
    "two_finger_circle",  # cool white
    "finger_gun",         # red color
    "ok_sign",            # blue color
    "wave",               # green color
    "peace_sign_hold",    # purple color
    "snap_and_point",     # pulse effect
]

# Create a reverse mapping from gesture name to index
gesture_name_to_index = {name: idx for idx,
                         name in enumerate(lifx_gesture_labels)}


def print_available_commands():
    print("\n===== AVAILABLE LIFX COMMANDS =====")
    print("Format: [INDEX] GESTURE_NAME - COMMAND")
    print("-" * 50)

    for idx, label in enumerate(lifx_gesture_labels):
        command = lifx_commands[idx]
        print(f"[{idx}] {label} - {command}")

    print("-" * 50)
    print("Enter command index, gesture name, or command name")
    print("Type 'list' to show commands again, 'state' for light status, or 'q' to quit")


def initialize_lifx():
    try:
        lifx_controller = LifxController()
        logger.info("LIFX controller initialized successfully")
        print("LIFX controller connected successfully!")
        return lifx_controller
    except Exception as e:
        logger.error(f"Failed to initialize LIFX controller: {str(e)}")
        print(f"Error connecting to LIFX: {str(e)}")
        print("Make sure your environment variables are set correctly:")
        print("  - LIFX_API_TOKEN")
        return None


def process_command(lifx, command_input):
    try:
        # Check if input is a number (index)
        if command_input.isdigit():
            idx = int(command_input)
            if idx < 0 or idx >= len(lifx_commands):
                print(
                    f"Error: Index {idx} out of range (0-{len(lifx_commands)-1})")
                return
            command = lifx_commands[idx]
            gesture = lifx_gesture_labels[idx]

        # Check if input is a gesture name
        elif command_input in gesture_name_to_index:
            idx = gesture_name_to_index[command_input]
            command = lifx_commands[idx]
            gesture = command_input

        # Check if input is a direct command name
        elif command_input in lifx_commands.values():
            command = command_input
            # Find the index of this command
            idx = next((i for i, cmd in lifx_commands.items()
                       if cmd == command), None)
            gesture = lifx_gesture_labels[idx] if idx is not None else "Unknown"

        else:
            print(f"Error: Unknown command '{command_input}'")
            return

        print(f"Executing: {command} (gesture: {gesture})")

        result = lifx.execute_command(command)

        if result:
            print(f"Command executed successfully!")
        else:
            print(f"Command failed!")

    except Exception as e:
        print(f"Error processing command: {str(e)}")


def get_light_states(lifx):
    try:
        light_states = lifx.get_light_states()
        if light_states:
            print("\n===== CURRENT LIGHT STATES =====")
            for light_id, state in light_states.items():
                print(f"Light: {state['label']}")
                print(f"  Power: {state['power']}")
                print(f"  Brightness: {state['brightness']:.2f}")
                print(f"  Color: {state['color']}")
                print("-" * 30)
        else:
            print("No lights found or all lights are off")
    except Exception as e:
        print(f"Error getting light states: {str(e)}")


def main():
    print("=" * 50)
    print("LIFX Controller Test Script")
    print("=" * 50)
    print("Initializing LIFX controller...")

    # init LIFX controller
    lifx = initialize_lifx()
    if lifx is None:
        print("Could not initialize LIFX controller. Exiting.")
        return

    print("Ready to test LIFX commands!")
    print_available_commands()

    while True:
        try:
            command_input = input(
                "\nEnter command, 'state' for light status, 'list', or 'q' to quit: ").strip().lower()

            if command_input == 'q':
                print("Exiting test script.")
                break
            elif command_input == 'list':
                print_available_commands()
                continue
            elif command_input == 'state':
                get_light_states(lifx)
                continue

            process_command(lifx, command_input)

        except KeyboardInterrupt:
            print("\nExiting test script.")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
