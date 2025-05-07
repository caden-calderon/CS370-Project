# lifx_controller.py
# Author: Andrew Aberer

import requests
import os
import logging
import time
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any, List, Optional
from constants.constants import LIFX_COMMANDS

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LifxController:
    # init LIFX controller with API token.
    def __init__(self):
        try:
            # API token - set these env vars in your zshrc/bashrc or similar
            self.api_token = os.environ.get('LIFX_API_TOKEN')

            if not self.api_token:
                logger.error(
                    "Missing LIFX API token. Please set LIFX_API_TOKEN environment variable.")
                raise ValueError(
                    "LIFX API token not found in environment variables")

            self.api_url = "https://api.lifx.com/v1/lights"
            self.headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }

            # test connection by getting avail. lights
            self.get_lights()
            logger.info("LIFX controller initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize LIFX controller: {str(e)}")
            raise

    # execute LIFX command based on the input string
    def execute_command(self, command: str) -> bool:
        logger.info(f"Executing LIFX command: {command}")

        command_map = {
            "lights_on": self.turn_on,
            "lights_off": self.turn_off,
            "toggle": self.toggle,
            "brightness_up": self.brightness_up,
            "brightness_down": self.brightness_down,
            "set_color_red": lambda: self.set_color("red"),
            "set_color_blue": lambda: self.set_color("blue")
        }

        if command in command_map:
            try:
                command_map[command]()
                return True
            except Exception as e:
                logger.error(f"Error executing command '{command}': {str(e)}")
                return False
        else:
            logger.warning(f"Unknown command: {command}")
            return False

    # get all LIFX lights associated with the account
    def get_lights(self) -> List[Dict[str, Any]]:
        try:
            response = requests.get(
                self.api_url + "/all", headers=self.headers)
            response.raise_for_status()
            lights = response.json()
            logger.info(f"Found {len(lights)} LIFX lights")
            return lights
        except Exception as e:
            logger.error(f"Failed to get lights: {str(e)}")
            raise

    # get current state of all lights
    def get_light_states(self) -> Dict[str, Any]:
        try:
            lights = self.get_lights()
            states = {}
            for light in lights:
                light_id = light["id"]
                states[light_id] = {
                    "label": light["label"],
                    "power": light["power"],
                    "brightness": light["brightness"],
                    "color": light["color"]
                }
            return states
        except Exception as e:
            logger.error(f"Failed to get light states: {str(e)}")
            raise

    # turn on all lights or a specific light
    def turn_on(self, selector: str = "all") -> None:
        try:
            data = {"power": "on"}
            response = requests.put(
                f"{self.api_url}/{selector}/state",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            logger.info(f"Turned on lights: {selector}")
        except Exception as e:
            logger.error(f"Failed to turn on lights: {str(e)}")
            raise

    # turn off all lights or a specific light
    def turn_off(self, selector: str = "all") -> None:
        try:
            data = {"power": "off"}
            response = requests.put(
                f"{self.api_url}/{selector}/state",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            logger.info(f"Turned off lights: {selector}")
        except Exception as e:
            logger.error(f"Failed to turn off lights: {str(e)}")
            raise

    # toggle state of all lights or a specific light
    def toggle(self, selector: str = "all") -> None:
        try:
            response = requests.post(
                f"{self.api_url}/{selector}/toggle",
                headers=self.headers
            )
            response.raise_for_status()
            logger.info(f"Toggled lights: {selector}")
        except Exception as e:
            logger.error(f"Failed to toggle lights: {str(e)}")
            raise

    # set brightness level for lights
    # args:
    #     brightness: Float between 0.0 and 1.0
    #     selector: Light selector string
    #     duration: Transition time in seconds
    def set_brightness(self, brightness: float, selector: str = "all", duration: float = 1.0) -> None:
        try:
            # check brightness is within bounds
            brightness = max(0.0, min(1.0, brightness))

            data = {
                "brightness": brightness,
                "duration": duration
            }

            response = requests.put(
                f"{self.api_url}/{selector}/state",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            logger.info(
                f"Set brightness to {brightness:.2f} for lights: {selector}")
        except Exception as e:
            logger.error(f"Failed to set brightness: {str(e)}")
            raise

    # increase brightness by increment (capped at 1.0)
    def brightness_up(self, increment: float = 0.2, selector: str = "all") -> None:
        try:
            # current light states and only powered-on lights
            lights = self.get_lights()
            on_lights = [light for light in lights if light["power"] == "on"]

            if not on_lights:
                # if no lights are on, turn them on at low brightness
                self.turn_on(selector)
                self.set_brightness(increment, selector)
                return

            avg_brightness = sum(light["brightness"]
                                 for light in on_lights) / len(on_lights)

            new_brightness = min(1.0, avg_brightness + increment)
            self.set_brightness(new_brightness, selector)

        except Exception as e:
            logger.error(f"Failed to increase brightness: {str(e)}")
            raise

    # decrease brightness by decrement (minimum 0.1)
    def brightness_down(self, decrement: float = 0.2, selector: str = "all") -> None:
        try:
            # current light states and only powered-on lights
            lights = self.get_lights()
            on_lights = [light for light in lights if light["power"] == "on"]

            if not on_lights:
                logger.info("No lights are currently on")
                return

            avg_brightness = sum(light["brightness"]
                                 for light in on_lights) / len(on_lights)

            new_brightness = max(0.1, avg_brightness - decrement)

            # if very dim, just turn off
            if new_brightness <= 0.1:
                self.turn_off(selector)
            else:
                self.set_brightness(new_brightness, selector)

        except Exception as e:
            logger.error(f"Failed to decrease brightness: {str(e)}")
            raise

    # set color for lights
    # args:
    #     color: Color string (LIFX format or common name)
    #     selector: Light selector string
    #     duration: Transition time in seconds
    def set_color(self, color: str, selector: str = "all", duration: float = 1.0) -> None:
        try:
            color_map = {
                "red": "red",
                "blue": "blue",
            }

            color_value = color_map.get(color.lower(), color)

            data = {
                "color": color_value,
                "duration": duration
            }

            response = requests.put(
                f"{self.api_url}/{selector}/state",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            logger.info(f"Set color to {color} for lights: {selector}")
        except Exception as e:
            logger.error(f"Failed to set color: {str(e)}")
            raise


if __name__ == "__main__":
    import sys

    valid_commands = list(set(LIFX_COMMANDS.values()))

    if len(sys.argv) != 2:
        print("Usage: python lifx_controller.py <command>")
        print("Available commands:")
        print(f"Available commands: {', '.join(valid_commands)}")
        sys.exit(1)

    command = sys.argv[1]
    controller = LifxController()
    result = controller.execute_command(command)

    if result:
        print(f"Command '{command}' executed successfully")
    else:
        print(f"Failed to execute command '{command}'")
