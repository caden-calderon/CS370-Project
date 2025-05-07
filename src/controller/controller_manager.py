# controller_manager.py
# Author: Andrew Aberer

import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controller.lifx_controller import LifxController
from controller.spotify_controller import SpotifyController
from constants.constants import (
    GESTURE_LIST,
    SPOTIFY_COMMANDS,
    LIFX_COMMANDS,
    COMMAND_DESCRIPTIONS,
    ControllerType
)

logger = logging.getLogger(__name__)


class ControllerManager:
    def __init__(self):
        self.controllers = {}
        self.active_controller = None
        self.command_maps = {
            ControllerType.SPOTIFY: SPOTIFY_COMMANDS,
            ControllerType.LIFX: LIFX_COMMANDS
        }

        self.spotify_available = self._init_spotify()
        self.lifx_available = self._init_lifx()

        # default controller (Spotify if available)
        if self.spotify_available:
            self.active_controller = ControllerType.SPOTIFY
        elif self.lifx_available:
            self.active_controller = ControllerType.LIFX

    def _init_spotify(self):
        try:
            spotify = SpotifyController()
            logger.info("Spotify controller initialized successfully")
            self.controllers[ControllerType.SPOTIFY] = spotify
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Spotify controller: {str(e)}")
            return False

    def _init_lifx(self):
        try:
            lifx = LifxController()
            logger.info("LIFX controller initialized successfully")
            self.controllers[ControllerType.LIFX] = lifx
            return True
        except Exception as e:
            logger.error(f"Failed to initialize LIFX controller: {str(e)}")
            return False

    def has_available_controllers(self):
        return self.spotify_available or self.lifx_available

    def set_active(self, controller_type):
        if controller_type in self.controllers:
            self.active_controller = controller_type
            return True
        return False

    def handle_gesture(self, gesture_index):
        if gesture_index < 0 or gesture_index >= len(GESTURE_LIST):
            logger.warning(f"Invalid gesture index: {gesture_index}")
            return False, None

        gesture_name = GESTURE_LIST[gesture_index]
        logger.info(
            f"Processing gesture: {gesture_name} (index: {gesture_index})")

        # Store current controller to detect switches
        prev_controller = self.active_controller

        # Handle controller switching gestures (6 for Spotify, 7 for LIFX)
        if gesture_index == 6:  # One - Switch to Spotify
            success = self.set_active(ControllerType.SPOTIFY)
            if success:
                return True, {"type": "switch", "controller": ControllerType.SPOTIFY}
            return False, None
        elif gesture_index == 7:  # Two - Switch to LIFX
            success = self.set_active(ControllerType.LIFX)
            if success:
                return True, {"type": "switch", "controller": ControllerType.LIFX}
            return False, None

        # Execute on active controller if available
        if not self.active_controller or self.active_controller not in self.controllers:
            logger.warning("No active controller available")
            return False, None

        command_map = self.command_maps.get(self.active_controller)
        if not command_map or gesture_index not in command_map:
            logger.warning(
                f"Gesture {gesture_index} not mapped for {self.active_controller}")
            return False, None

        # Get command and execute
        controller = self.controllers[self.active_controller]
        command = command_map[gesture_index]

        try:
            success = controller.execute_command(command)
            if success:
                # Get command description
                description = COMMAND_DESCRIPTIONS.get(command, "")
                return success, {
                    "type": "command",
                    "controller": self.active_controller,
                    "command": command,
                    "description": description
                }
            return False, None
        except Exception as e:
            logger.error(f"Error executing command {command}: {str(e)}")
            return False, None

    def get_active(self):
        return self.active_controller

    def get_commands_for_active(self):
        if not self.active_controller:
            return {}
        return self.command_maps.get(self.active_controller, {})
