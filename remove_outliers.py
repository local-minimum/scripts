import numpy as np
import os
import glob
import numpy.ma as ma

NPS = glob.glob('image*.npy')

for n in NPS:
    array = np.load(n)
    array_masked = np.ma.masked_array(array, np.isnan(array))
    mean = np.mean(array_masked)
    #print mean
    if mean > 10000000:
	os.rename(n, ("_BAD" + n))
    
