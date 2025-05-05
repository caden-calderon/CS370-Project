
import tensorflow as tf
import numpy as np
from glob import glob
from tensorflow.keras.layers import Normalization, LSTM, Dense
from tensorflow.keras import Sequential

gesture_list = ["closed_to_open", "open_to_closed", "swipe_left", "swipe_right", "swipe_up", "swipe_down", "one", "two", "three", "four"]

label_map = {name: idx for idx, name in enumerate(gesture_list)}

X, y = [], []

for gesture in gesture_list:
    for path in glob(f"collected_data/{gesture}/*.npy"):
        sequence = np.load(path)
        if len(sequence) != 20:
            print("error")
        X.append(sequence)
        y.append(label_map[gesture])
X = np.stack(X)
y = np.array(y)

print(y.shape)
print(y)

