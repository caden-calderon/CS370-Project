# Author: Caden Calderon
# Use to find deleted data (gaps) in the folders of collected_data

import os

files = os.listdir('collected_data/swipe_up_train')  # <--Adjust file path as needed 
numbers = sorted([int(f.split('_')[1].split('.')[0]) for f in files if f.endswith('.npy')])

missing = [i for i in range(numbers[0], numbers[-1] + 1) if i not in numbers]  

print("Missing numbers:", missing)
