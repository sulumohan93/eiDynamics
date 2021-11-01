import matplotlib.pyplot as plt
import numpy as np
# from scipy.signal import find_peaks, peak_widths
# from scipy.signal import butter, bessel, decimate, sosfiltfilt
# from scipy.optimize import curve_fit
import os
# import sys
# import imp
import pandas as pd
import h5py
import seaborn as sns

# from eidynamics import ephys_classes
# from eidynamics.utils               import delayed_alpha_function,rolling_variance_baseline,filter_data,moving_average
# from eidynamics                     import pattern_index
# from allcells                       import *


trainingDataDirectory = "C:\\Users\\aditya\\OneDrive\\NCBS\\Lab\\Projects\\EI_Dynamics\\training_data\\"
fileExt = "Set.h5"
dataFiles = [os.path.join(trainingDataDirectory, dataFile) for dataFile in os.listdir(trainingDataDirectory) if dataFile.endswith(fileExt)]
outputFile = "C:\\Users\\aditya\\OneDrive\\NCBS\\Lab\\Projects\\EI_Dynamics\\training_data\\allCells_trainingSet_short.h5"
n0 = np.zeros((1,40026))

for datasetFile in dataFiles:
    with h5py.File( datasetFile, "r") as f:
        n1 = f.get('default')      
        n0 = np.concatenate((n0,n1),axis=0)
        f.close()

n0_1 = n0[:,:27]
n0_AP = np.zeros( (n0_1.shape[0],1) )
n0_2 = n0[:,20027:]
for i in range(n0_2.shape[0]):
    if np.max(n0_2[i,:])>50:
        n0_AP[i,0] = 1

n0_short = np.concatenate((n0_1,n0_AP,n0_2),axis=1)


print(n0_short.shape)
with h5py.File(outputFile, 'w') as hf:
    dset = hf.create_dataset("default", data = n0_short)
    hf.close()



# DF.to_hdf(outputFile,key="default")