# Author: Caden Calderon 
# Run in Jupyter notebooks terminal 

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Load a saved gesture sequence
sequence = np.load('collected_data/closed_to_open/sequence_1.npy')  # <<< Adjust path here as needed 
print(f"Sequence shape: {sequence.shape}")  # Should be (Sequence length, 63)

# MediaPipe landmark connections (for drawing bones)
HAND_CONNECTIONS = [
    (0,1), (1,2), (2,3), (3,4),        # Thumb
    (0,5), (5,6), (6,7), (7,8),        # Index
    (0,9), (9,10), (10,11), (11,12),   # Middle
    (0,13), (13,14), (14,15), (15,16), # Ring
    (0,17), (17,18), (18,19), (19,20)  # Pinky
]

# Set up plot
fig, ax = plt.subplots()

ax.set_xlim(-3, 3)
ax.set_ylim(-3, 3)

ax.set_title("Gesture Sequence Playback")
points, = ax.plot([], [], 'bo')  # blue dots
lines = []  # to store bone lines

for _ in HAND_CONNECTIONS:
    line, = ax.plot([], [], 'r-')  # red lines
    lines.append(line)

# Update function for animation
def update(frame_idx):
    frame = sequence[frame_idx]

    x = frame[::3]  # Take every third element starting at 0 (x values)
    y = frame[1::3] # Starting at 1 (y values)
    z = frame[2::3] # Starting at 2 (z values, unused for 2D plotting)

    points.set_data(x, y)

    for i, (start_idx, end_idx) in enumerate(HAND_CONNECTIONS):
        line = lines[i]
        line.set_data([x[start_idx], x[end_idx]], [y[start_idx], y[end_idx]])

    return [points] + lines

# Create animation
ani = animation.FuncAnimation(fig, update, frames=range(sequence.shape[0]), interval=100)

plt.show()
