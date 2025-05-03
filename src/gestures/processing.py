# processing.py
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


# Wrist and middle finger MCP joint
def normalize_hand_size(frame, ref_start=0, ref_end=9):
    frame = np.array(frame)
    x0, y0, z0 = frame[ref_start*3], frame[ref_start*3 +
                                           # Get start coordinates
                                           1], frame[ref_start*3+2]
    x1, y1, z1 = frame[ref_end*3], frame[ref_end*3 +
                                         # Get end coordinates
                                         1], frame[ref_end*3+2]
    # Euclidean distance between wrist and middle MCP
    hand_scale = math.sqrt((x1 - x0)**2 + (y1 - y0)**2 + (z1 - z0)**2)
    if hand_scale == 0:  # If wrist and middle MCP are in same place (bad)
        hand_scale = 1e-6
    scaled = frame.copy()
    scaled /= hand_scale  # Scale relative to hand scale
    return scaled


def normalize_wrist_angle(frame_vector, ref_start=0, ref_end=5):
    # 1) reshape to (21, 3) so we can index x,y easily
    pts = np.array(frame_vector, dtype=float).reshape(21, 3)

    # 2) get the 2D vector from landmark ref_start to ref_end
    p0 = pts[ref_start, :2]  # [x0, y0]
    p5 = pts[ref_end, :2]  # [x5, y5]
    V = p5 - p0            # vector in the XY plane

    # 3) signed angle between V and positive Y axis:
    #    angle = atan2(Vx, Vy)
    angle = np.arctan2(V[0], V[1])

    # 4) rotation matrix to “undo” that angle
    c, s = np.cos(-angle), np.sin(-angle)
    R = np.array([[c, -s],
                  [s,  c]])

    # 5) translate pts so p0 is origin, rotate, then translate back
    xy = pts[:, :2] - p0      # shift origin
    xy = xy.dot(R.T)          # rotate in-plane
    pts[:, :2] = xy + p0      # shift back

    # 6) flatten back to 63-vector
    return pts.reshape(-1)


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


def extract_motion_deltas(sequence):
    sequence = np.array(sequence)  # safety check

    deltas = np.diff(sequence, axis=0)  # compute frame-to-frame differences

    return deltas


def preprocess_frame(frame,
                     center=True,
                     rotate=False,
                     scale=True,
                     lock_axes=(False, False, False)):
    # 1) Copy
    pts = np.array(frame, dtype=float)

    # 2) Center (e.g. subtract your chosen origin)
    if center:
        pts = center_landmarks(pts)

    # 3) Rotate so forearm is vertical
    if rotate:
        pts = normalize_wrist_angle(pts)

    # 4) Uniformly scale to canonical hand size
    if scale:
        pts = normalize_hand_size(pts)

    # 5) Finally, zero out any axes you want locked
    pts = lock_movement(pts, *lock_axes)

    return pts
