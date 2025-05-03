# dependencies.py
# Author: Andrew Aberer

import subprocess
import sys
import os


def install_requirements():
    print("Installing required packages...")

    # core dependencies
    packages = [
        "numpy",
        "tensorflow",
        "opencv-python",
        "mediapipe",
        "spotipy",
        "requests",
        "python-dotenv",
    ]

    # pip version and upgrade if needed
    subprocess.check_call([sys.executable, "-m", "pip",
                          "install", "--upgrade", "pip"])

    # install packages
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError:
            print(f"Error installing {package}")
            return False

    print("\nAll packages installed successfully!")
    print("\nReminder: You'll need to set up environment variables for API access:")
    print("- SPOTIFY_CLIENT_ID")
    print("- SPOTIFY_CLIENT_SECRET")
    print("- SPOTIFY_REDIRECT_URI")
    print("- LIFX_API_TOKEN")

    # create .env file - or can set vars in basrc/zshrc
    create_env_file()

    return True


def create_env_file():
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("""# Spotify API Credentials
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback

# LIFX API Token
LIFX_API_TOKEN=your_lifx_api_token
""")
        print("\nCreated a sample .env file. Please edit it with your actual credentials.")
        print("Then load it in your main.py with:")
        print("from dotenv import load_dotenv\nload_dotenv()")


if __name__ == "__main__":
    install_requirements()
