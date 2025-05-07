# main.py
# Author: Andrew Aberer & Caden Calderon

from constants.constants import (
    GESTURE_LIST,
    COMMAND_DESCRIPTIONS,
    ControllerType
)
from controller.controller_manager import ControllerManager
from gestures.predict_gestures import run_gesture_recognition, ResultHolder
import logging
import time
import sys
import os
import multiprocessing
from queue import Empty
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MainProgram:
    def __init__(self, result_holder=None, queue=None):
        # stores the most recent result
        self.result_holder = result_holder if result_holder else ResultHolder()
        self.queue = queue if queue else multiprocessing.Queue()  # inter-process result queue
        self.gesture_process = None

        self.controller_manager = ControllerManager()

        if not self.controller_manager.has_available_controllers():
            logger.warning("No controllers are available")

    def process_result(self, result):
        print(f"Received result: {result}")
        if isinstance(result, dict) and 'gesture_index' in result:
            gesture_index = result['gesture_index']
            print(
                f"Detected gesture: {GESTURE_LIST[gesture_index]} (index: {gesture_index})")

            # Let the controller manager handle the gesture
            success, info = self.controller_manager.handle_gesture(
                gesture_index)

            if success and info:
                # Handle different result types
                if info["type"] == "switch":
                    print(
                        f"Switched to {info['controller'].upper()} controller")
                elif info["type"] == "command":
                    controller = info["controller"]
                    command = info["command"]
                    description = info["description"]
                    print(f"{controller.capitalize()}: {command} ({description})")
        else:
            logger.warning(f"Received invalid result format: {result}")

    def start_gesture_recognition(self):
        if self.gesture_process is not None and self.gesture_process.is_alive():
            logger.warning("Gesture recognition process already running")
            return

        self.gesture_process = multiprocessing.Process(
            target=run_gesture_recognition,
            args=(self.queue,),
            daemon=True
        )
        self.gesture_process.start()
        logger.info("Gesture recognition process started")

    def stop_gesture_recognition(self):
        if self.gesture_process is None:
            return

        self.gesture_process.terminate()
        self.gesture_process.join(timeout=1.0)
        self.gesture_process = None
        logger.info("Gesture recognition process stopped")

    def manual_control_menu(self):
        try:
            active_controller = self.controller_manager.get_active()

            if not active_controller:
                print("No active controller")
                return

            commands = self.controller_manager.get_commands_for_active()
            command_map = self.controller_manager.command_maps.get(
                active_controller, {})
            title = f"{active_controller.upper()} CONTROLLER"

            print(f"\n===== {title} =====")
            print("Available commands:")
            for idx, command in commands.items():
                if idx in [6, 7]:  # Skip controller switching gestures
                    continue
                gesture = GESTURE_LIST[idx]
                # Get description from COMMAND_DESCRIPTIONS instead of executing the command
                description = COMMAND_DESCRIPTIONS.get(command, "")
                print(f"[{idx}] {gesture} - {command} - {description}")

            print(
                "\nEnter command index, 'switch' to change controller, or 'back' to return:")

            choice = input("> ").strip().lower()

            if choice == 'back':
                return
            elif choice == 'switch':
                active_controller = self.controller_manager.get_active()
                if active_controller == ControllerType.SPOTIFY and self.controller_manager.lifx_available:
                    self.controller_manager.set_active(ControllerType.LIFX)
                    print("Switched to LIFX controller")
                elif active_controller == ControllerType.LIFX and self.controller_manager.spotify_available:
                    self.controller_manager.set_active(ControllerType.SPOTIFY)
                    print("Switched to Spotify controller")
                else:
                    print("No alternative controller available")
            elif choice.isdigit():
                idx = int(choice)
                success, info = self.controller_manager.handle_gesture(idx)
                if success and info and info["type"] == "command":
                    print(f"Executed: {info['command']}")
                elif not success:
                    print("Command failed or not available")
            else:
                print("Invalid choice")
        except KeyboardInterrupt:
            # Let the KeyboardInterrupt bubble up to be caught in the run method
            print("\nReturning to main menu...")
            raise

    def run(self):
        print("=" * 50)
        print("Gesture Control System")
        print("=" * 50)

        if not self.controller_manager.has_available_controllers():
            print("Error: No controllers available. Please check your configuration.")
            return

        # Flag to control the main loop
        running = True

        while running:
            try:
                active_controller = self.controller_manager.get_active()

                print("\nMain Menu:")
                print("-" * 50)
                print(
                    f"Current mode: {active_controller.upper() if active_controller else 'None'}")
                print("1. Start gesture recognition")
                print("2. Stop gesture recognition")
                print("3. Manual control")
                print("4. Switch controller")
                print("q. Exit")
                print("-" * 50)

                choice = input("Select an option: ").strip().lower()

                if choice == 'q':
                    running = False
                elif choice == '1':
                    self.start_gesture_recognition()
                    print("Gesture recognition started")
                    print("Listening for gestures... (Press Ctrl+C to return to menu)")

                    listening = True
                    while listening:
                        try:
                            # Check for new gestures with a small timeout
                            result = self.queue.get(timeout=0.1)
                            self.result_holder.update(result)
                            self.process_result(result)
                        except Empty:
                            # No new gesture, continue waiting
                            continue
                        except KeyboardInterrupt:
                            # Set listening to False to exit the inner loop
                            listening = False
                            print("\nReturning to menu...")

                elif choice == '2':
                    self.stop_gesture_recognition()
                    print("Gesture recognition stopped")

                elif choice == '3':
                    try:
                        self.manual_control_menu()
                    except KeyboardInterrupt:
                        print("\nReturning to menu...")

                elif choice == '4':
                    active_controller = self.controller_manager.get_active()
                    if active_controller == ControllerType.SPOTIFY and self.controller_manager.lifx_available:
                        self.controller_manager.set_active(ControllerType.LIFX)
                        print("Switched to LIFX controller")
                    elif active_controller == ControllerType.LIFX and self.controller_manager.spotify_available:
                        self.controller_manager.set_active(
                            ControllerType.SPOTIFY)
                        print("Switched to Spotify controller")
                    else:
                        print("No alternative controller available")

            except KeyboardInterrupt:
                # Allow KeyboardInterrupt to exit to the main menu instead of exiting the program
                print("\nReturning to main menu...")
                continue

        self.stop_gesture_recognition()
        print("\nExiting program. Goodbye!")


if __name__ == "__main__":
    # Create a queue for passing results from the worker
    queue = multiprocessing.Queue()
    holder = ResultHolder()  # Instantiate a holder to keep track of the latest gesture

    main_program = MainProgram(holder, queue)

    # Spawn the worker process that captures & predicts gestures continually
    process = multiprocessing.Process(
        target=run_gesture_recognition,
        args=(queue,),
        daemon=True
    )
    process.start()

    # Start the main loop to consume and handle results
    try:
        main_program.run()
    finally:
        # Cleanup when main loop exits
        process.terminate()
        process.join()
