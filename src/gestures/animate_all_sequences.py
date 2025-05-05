import os, glob, time, re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

HAND_CONNECTIONS = [(0,1), (1,2), (2,3), (3,4),
                    (0,5), (5,6), (6,7), (7,8),
                    (0,9), (9,10), (10,11), (11,12),
                    (0,13),(13,14),(14,15),(15,16),
                    (0,17),(17,18),(18,19),(19,20)]

def show_all_sequences(rel_folder="collected_data/three"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.normpath(os.path.join(script_dir, "..", "..", rel_folder))

    # grab & numerically sort .npy files
    files = sorted(
        glob.glob(os.path.join(data_folder, "sequence_*.npy")),
        key=lambda fn: int(re.search(r"sequence_(\d+)\.npy", fn).group(1))
    )

    print("Will animate:", files)
    for fpath in files:
        sequence = np.load(fpath)  # shape (20,63)
        fig, ax = plt.subplots()
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)

        # scatter + line objects
        points, = ax.plot([], [], 'o', markersize=5)
        lines  = [ax.plot([], [], '-', lw=2)[0] for _ in HAND_CONNECTIONS]

        def update(idx):
            frame = sequence[idx]
            x, y = frame[0::3], frame[1::3]
            points.set_data(x, y)
            for line, (i,j) in zip(lines, HAND_CONNECTIONS):
                line.set_data([x[i], x[j]], [y[i], y[j]])
            return [points, *lines]

        # build the animation
        ani = animation.FuncAnimation(
            fig,
            update,
            frames=len(sequence),
            interval=100,
            blit=True,
            repeat=False
        )

        plt.title(os.path.basename(fpath))

        # show non-blocking, pause for the duration of the animation + a buffer
        plt.show(block=False)
        total_time = len(sequence) * (100/1000) + 0.5  # 100 ms per frame + 0.5 s
        plt.pause(total_time)

        # clean up & move on
        plt.close(fig)

if __name__ == "__main__":
    show_all_sequences()
