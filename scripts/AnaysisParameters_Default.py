import numpy as np

# Experiment Parameters
Fs = 20000 #sampling rate

baselineStart = 0
baselineEnd = 200 # milliseconds, end of baseline time
baselineWindow = np.arange(baselineStart*Fs,baselineEnd*Fs)

IR_steadystateEnd = 1300 # End of hyperpolarizing pulse to measure IR
IR_steadstateStart = IR_steadystateEnd -200 # 
IR_steadystateWindow = np.arange(IR_steadstateStart*Fs,IR_steadystateEnd*Fs)

# Filtering
filter={0:'',1:'bessel'}
filtering = filter[1]