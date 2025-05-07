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
    from src.constants.constants import (
        GESTURE_LIST,
        LIFX_COMMANDS,
        GESTURE_TO_INDEX,
        COMMAND_DESCRIPTIONS,
        ControllerType
    )
    print("Successfully imported LifxController &")
except ImportError as e:
    print(f"Unexpected ImportError: {e}")
    sys.exit(1)


def print_available_commands():
    print("\n===== AVAILABLE LIFX COMMANDS =====")
    print("Format: [INDEX] GESTURE_NAME - COMMAND")
    print("-" * 50)

    for idx, gesture in enumerate(GESTURE_LIST):
        # inedx 6 and 7 are reserved for controller switching
        if idx in [6, 7]:
            print(f"[{idx}] {gesture} - Reserved for controller switching")
            continue

        if idx in LIFX_COMMANDS:
            command = LIFX_COMMANDS[idx]
            description = COMMAND_DESCRIPTIONS.get(command, "")
            print(f"[{idx}] {gesture} - {command} - {description}")
        else:
            print(f"[{idx}] {gesture} - No command assigned")

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
            if idx not in LIFX_COMMANDS:
                print(f"Error: Index {idx} is not a valid LIFX command")
                return
            command = LIFX_COMMANDS[idx]
            gesture = GESTURE_LIST[idx]

        # Check if input is a gesture name
        elif command_input in GESTURE_TO_INDEX:
            idx = GESTURE_TO_INDEX[command_input]
            if idx not in LIFX_COMMANDS:
                print(
                    f"Error: Gesture '{command_input}' is not mapped to a LIFX command")
                return
            command = LIFX_COMMANDS[idx]
            gesture = command_input

        # Check if input is a direct command name
        elif command_input in LIFX_COMMANDS.values():
            command = command_input
            # Find the index of this command (use the first index if multiple exist)
            idx = next((i for i, cmd in LIFX_COMMANDS.items()
                       if cmd == command), None)
            gesture = GESTURE_LIST[idx] if idx is not None else "Unknown"

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
