# CS370-Project
# Gesture Based Smart Home System

A Raspberry Pi-powered system that uses computer vision and machine learning to control Spotify and LIFX smart lights through hand gestures.

## Quick Start

1. Install dependencies:

   ```
   python dependencies.py
   ```

2. Set up API credentials in the `.env` file

3. Run the application:
   ```
   python main.py
   ```

## Supported Gestures - (TODO FINALIZE MAPPINGS)

### Spotify Controls

- Open palm → Play
- Closed fist → Pause
- Swipe right → Next track
- Swipe left → Previous track
- Swipe up → Volume up
- Swipe down → Volume down
- More here?

### LIFX Controls

- Open palm (hold) → Lights on
- Closed fist (hold) → Lights off
- Swipe up (hold) → Brightness up
- Swipe down (hold) → Brightness down
- More here?

## Project Structure

- `main.py` - Main application with gesture recognition pipeline
- `spotify_controller.py` - Handles Spotify API interactions
- `lifx_controller.py` - Manages LIFX smart light controls
- `dependencies.py` - Script to install dependencies
