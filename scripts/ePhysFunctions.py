import numpy as np
from scipy import signal

def IRcalc(recordingData,steadystateWindow1,steadystateWindow2):
    ''' recordingData is the data dictionary with sweeps numbers as keys
    Provide steadystateWindow values in milliseconds'''
    
    Fs = 20
    IRtrend = []
    for s in recordingData.values():
        cmdSig = s['cmd']
        ss1_cmd = np.mean(cmdSig[steadystateWindow1*Fs])
        ss2_cmd = np.mean(cmdSig[steadystateWindow2*Fs])
        delV = ss2_cmd-ss1_cmd

        recSig = s[0]
        ss1_rec = np.mean(recSig[steadystateWindow1*Fs])
        ss2_rec = np.mean(recSig[steadystateWindow2*Fs])
        delI = ss2_rec-ss1_rec

        IRtrend.append(1000*delV/delI) # mult with 1000 to convert to MOhms

        # IR change flag
        # IR change screening criterion is 20% change in IR during the recording
        IRflag = 0
        if (np.max(IRtrend)-np.min(IRtrend))/np.mean(IRtrend) > 0.2:
            IRflag = 1

    return IRtrend, IRflag

    
    
    
    


