# spotify_controller.py
# Author: Andrew Aberer

import spotipy
import sys
import os
import time
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spotipy.oauth2 import SpotifyOAuth
from constants.constants import SPOTIFY_COMMANDS

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SpotifyController:
    # init Spotify controller with API oauth
    def __init__(self):
        try:
            # creds - set these env vars in your zshrc/basrc or similar
            client_id = os.environ.get('SPOTIFY_CLIENT_ID')
            client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
            redirect_uri = os.environ.get('SPOTIFY_REDIRECT_URI')

            if not all([client_id, client_secret, redirect_uri]):
                logger.error(
                    "Missing Spotify API credentials. Please set environment variables.")
                raise ValueError(
                    "Spotify API credentials not found in environment variables")

            # auth levels
            scope = "user-read-playback-state user-modify-playback-state user-library-modify user-library-read"

            # init
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=scope,
                cache_path=".spotifycache"
            ))

            logger.info("Spotify controller initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Spotify controller: {str(e)}")
            raise

    # execute a Spotify command based on the input string
    def execute_command(self, command):
        logger.info(f"Executing Spotify command: {command}")

        command_map = {
            "play": self.play_music,
            "pause": self.pause_music,
            "next": self.next_track,
            "previous": self.previous_track,
            "volume_up": self.volume_up,
            "volume_down": self.volume_down,
            "toggle_shuffle": self.toggle_shuffle,
            "add_favorite": self.add_to_favorites
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

    # play/resume music
    def play_music(self):
        try:
            self.sp.start_playback()
            logger.info("Music playback started")
        except Exception as e:
            logger.error(f"Failed to start playback: {str(e)}")
            raise

    # pause music
    def pause_music(self):
        try:
            self.sp.pause_playback()
            logger.info("Music playback paused")
        except Exception as e:
            logger.error(f"Failed to pause playback: {str(e)}")
            raise

    # skip to next song
    def next_track(self):
        try:
            self.sp.next_track()
            logger.info("Skipped to next track")
            time.sleep(0.5)
            current_track = self.get_current_track_info()
            if current_track:
                logger.info(f"Now playing: {current_track}")
        except Exception as e:
            logger.error(f"Failed to skip to next track: {str(e)}")
            raise

    # go back to last song
    def previous_track(self):
        try:
            self.sp.previous_track()
            logger.info("Returned to previous track")
            time.sleep(0.5)
            current_track = self.get_current_track_info()
            if current_track:
                logger.info(f"Now playing: {current_track}")
        except Exception as e:
            logger.error(f"Failed to return to previous track: {str(e)}")
            raise

    # increase volume by increment percentage
    def volume_up(self, increment=10):
        try:
            # Get current playback info
            current_playback = self.sp.current_playback()
            if not current_playback:
                logger.warning("No active playback found")
                return

            current_volume = current_playback['device']['volume_percent']
            new_volume = min(current_volume + increment, 100)

            self.sp.volume(new_volume)
            logger.info(
                f"Volume increased from {current_volume}% to {new_volume}%")
        except Exception as e:
            logger.error(f"Failed to increase volume: {str(e)}")
            raise

    # decrease volume by decrement percentage
    def volume_down(self, decrement=10):
        try:
            current_playback = self.sp.current_playback()
            if not current_playback:
                logger.warning("No active playback found")
                return

            current_volume = current_playback['device']['volume_percent']
            new_volume = max(current_volume - decrement, 0)

            self.sp.volume(new_volume)
            logger.info(
                f"Volume decreased from {current_volume}% to {new_volume}%")
        except Exception as e:
            logger.error(f"Failed to decrease volume: {str(e)}")
            raise

    # toggle shuffle
    def toggle_shuffle(self):
        try:
            current_playback = self.sp.current_playback()
            if not current_playback:
                logger.warning("No active playback found")
                return

            current_shuffle = current_playback['shuffle_state']
            new_shuffle = not current_shuffle

            self.sp.shuffle(new_shuffle)
            logger.info(f"Shuffle {'enabled' if new_shuffle else 'disabled'}")
        except Exception as e:
            logger.error(f"Failed to toggle shuffle: {str(e)}")
            raise

    # add to liked songs
    def add_to_favorites(self):
        try:
            current_track = self.sp.current_user_playing_track()
            if not current_track:
                logger.warning("No track currently playing")
                return

            track_id = current_track['item']['id']
            track_name = current_track['item']['name']
            artist_name = current_track['item']['artists'][0]['name']

            self.sp.current_user_saved_tracks_add([track_id])
            logger.info(
                f"Added '{track_name}' by {artist_name} to your Liked Songs")
        except Exception as e:
            logger.error(f"Failed to add track to favorites: {str(e)}")
            raise

    # current song stats
    def get_current_track_info(self):
        try:
            current_track = self.sp.current_user_playing_track()
            if not current_track or not current_track['item']:
                return None

            track = current_track['item']
            artist = track['artists'][0]['name']
            track_name = track['name']

            return f"{track_name} by {artist}"
        except Exception as e:
            logger.error(f"Failed to get current track info: {str(e)}")
            return None


if __name__ == "__main__":
    import sys

    valid_commands = list(set(SPOTIFY_COMMANDS.values()))

    if len(sys.argv) != 2:
        print("Usage: python spotify_controller.py <command>")
        print(f"Available commands: {', '.join(valid_commands)}")
        sys.exit(1)

    command = sys.argv[1]
    controller = SpotifyController()
    result = controller.execute_command(command)

    if result:
        print(f"Command '{command}' executed successfully")
    else:
        print(f"Failed to execute command '{command}'")
