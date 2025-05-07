# CS370-Project
# Gesture Based Smart Home System

A Raspberry Pi-powered system that uses computer vision and machine learning to control Spotify and LIFX smart lights through hand gestures.

## Requirements
### Spotify
Setup an application via [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) <br>  
Set application credentials in your `.env`
### LIFX
Generate a personal access token [here](https://cloud.lifx.com/settings) <br>  
Add token to `.env`

# API Documentation
[Spotify Web API Docs](https://developer.spotify.com/documentation/web-api) <br>  
[Lifx API Docs](https://api.developer.lifx.com/reference/introduction)

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

## Supported Gestures

### Reserved Controls
- 1 finger - Toggle Spotify Controls
- 2 fingers - Toggle LIFX Controls

### Spotify Controls

- Open palm → Play
- Closed fist → Pause
- Swipe right → Next track
- Swipe left → Previous track
- Swipe up → Volume up
- Swipe down → Volume down
- 3 fingers → Toggle shuffle
- 4 fingers → Add to favorites

### LIFX Controls

- Open palm → Lights on
- Closed fist → Lights off
- Swipe right → Toggle light
- Swipe up → Brightness up
- Swipe down → Brightness down
- 3 fingers → Set Color Red
- 4 fingers → Set Color Blue

## Project Structure

- `main.py` - Main application with gesture recognition pipeline
- `spotify_controller.py` - Handles Spotify API interactions
- `lifx_controller.py` - Manages LIFX smart light controls
- `dependencies.py` - Script to install dependencies
