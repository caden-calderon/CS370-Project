# Author: Caden Calderon 

import tensorflow as tf
import numpy as np
from glob import glob
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Normalization, LSTM, Dropout, Dense
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

gesture_list = ["closed_to_open", "open_to_closed", "swipe_left", "swipe_right", "swipe_up", "swipe_down", "one", "two", "three", "four"]
gesture_partition = ["train", "test", "validate"]

label_map = {name: idx for idx, name in enumerate(gesture_list)}

X = {p: [] for p in gesture_partition}
y = {p: [] for p in gesture_partition}

def load_data():
    for gesture in gesture_list:
        for partition in gesture_partition:
            for path in glob(f"collected_data/{gesture}_{partition}/*.npy"):
                sequence = np.load(path)
                if len(sequence) != 20:
                    print(f"Error: sequence length mismatch in {path}")
                X[partition].append(sequence)
                y[partition].append(label_map[gesture])

    # Convert lists to arrays (if non-empty)
    for partition in gesture_partition:
        if X[partition]:
            X[partition] = np.stack(X[partition]).astype(np.float32)
            y[partition] = np.array(y[partition], dtype=np.int32)
        else:
            print(f"Warning: No data for {partition}")
            X[partition] = np.empty((0,))  # Adjust shape if needed
            y[partition] = np.empty((0,))

    # Unpack to individual variables
    X_train, y_train = X["train"], y["train"]
    X_test, y_test = X["test"], y["test"]
    X_validate, y_validate = X["validate"], y["validate"]
    
    return X_train, y_train, X_test, y_test, X_validate, y_validate

def train_lstm(X_train, y_train, X_test, y_test, X_validate, y_validate):
    normalizer = Normalization(axis=-1, input_shape=(20,63))
    flat_train = X_train.reshape(-1, 63)  # Flatten first 2 dims for normaliztion 
    normalizer.adapt(flat_train)  # Compute mean and variance 
    
    model = Sequential([
        normalizer,
        LSTM(128, return_sequences=True),  # Adjust units based on data size  
        Dropout(0.2),  # Drop 20% of outputs for regularzation 
        LSTM(64), 
        Dropout(0.2),
        Dense(len(gesture_list), activation='softmax')  # Turn output into probability disto over gestures 
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',  # Set loss func for multi-class 
        metrics=['accuracy']  # Track accuracy during training and validation 
    )
    
    model.summary()  # Detailed summary of model 
    
    # Callbacks
    early_stop = EarlyStopping(
        monitor='val_loss',  # Watch validation loss
        patience=5,  # If there’s no improvement for 5 consecutive epochs, it stops.
        restore_best_weights=True  # Restore to best model weights
    )
    checkpoint = ModelCheckpoint(
        'best_gesture_lstm.h5',  # File path to save 
        monitor='val_accuracy',  # Watch validation accuracy
        save_best_only=True      # Save only when validation accuracy improves  
    )
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss', 
        factor=0.5, 
        patience=3
    )
    
    # Shuffle the training data
    idx = np.random.permutation(len(X_train))
    X_train, y_train = X_train[idx], y_train[idx]

    # Train 
    history = model.fit(
        X_train, y_train,
        validation_data=(X_validate, y_validate),
        epochs=50,
        batch_size=32,
        callbacks=[early_stop, checkpoint, reduce_lr]
    )
    
    # Evaluate on test set
    test_loss, test_acc = model.evaluate(X_test, y_test)
    print(f"Test accuracy: {test_acc:.3%}")
    model.save('gesture_lstm_with_norm.h5')


    
def main():
    X_train, y_train, X_test, y_test, X_validate, y_validate = load_data()
    train_lstm(X_train, y_train, X_test, y_test, X_validate, y_validate)
    

if __name__ == "__main__":
    main()