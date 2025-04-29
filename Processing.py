# Author: Caden Calderon 

import math
import numpy as np


def center_landmarks(frame):
    frame = np.array(frame)
    # Get wrist coordinates 
    wrist_x = frame[0]
    wrist_y = frame[1]
    wrist_z = frame[2]
    centered = frame.copy()
    for i in range(21):  # Loop through the 21 landmarks 
        # Center relative to wrist 
        centered[i*3 + 0] -= wrist_x  
        centered[i*3 + 1] -= wrist_y
        centered[i*3 + 2] -= wrist_z
    return centered


def normalize_hand_size(frame, ref_start=0, ref_end=9):  # Wrist and middle finger MCP joint 
    frame = np.array(frame)
    x0, y0, z0 = frame[ref_start*3], frame[ref_start*3+1], frame[ref_start*3+2]  # Get start coordinates 
    x1, y1, z1 = frame[ref_end*3], frame[ref_end*3+1], frame[ref_end*3+2]  # Get end coordinates 
    hand_scale = math.sqrt((x1 - x0)**2 + (y1 - y0)**2 + (z1 - z0)**2)  # Euclidean distance between wrist and middle MCP
    if hand_scale == 0:  # If wrist and middle MCP are in same place (bad)
        hand_scale = 1e-6
    scaled = frame.copy()
    scaled /= hand_scale  # Scale relative to hand scale 
    return scaled


def lock_movement(frame, lock_x=False, lock_y=False, lock_z=False):
    frame = np.array(frame)
    for i in range(21):  # Loop through the 21 landmarks 
        if lock_x:
            frame[i*3 + 0] = 0.0
        if lock_y:
            frame[i*3 + 1] = 0.0
        if lock_z:
            frame[i*3 + 2] = 0.0
    return frame


def preprocess_frame(frame, center=True, normalize=True, lock_axes=(False, False, False)):
    processed = np.array(frame)
    if center:
        processed = center_landmarks(processed)
    if normalize:
        processed = normalize_hand_size(processed)
    processed = lock_movement(processed, *lock_axes)
    return processed
