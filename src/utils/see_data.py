# see_data.py
# Author: Caden Calderon 

import numpy as np

seq = np.load("collected_data/open_to_close/sequence_6.npy")  # <<< Adjust path here as needed 
print(seq.shape)  # (Sequence length, 63)
print(seq[0])        # See all the data 