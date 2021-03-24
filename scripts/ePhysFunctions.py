import numpy as np
from scipy import signal
import pandas as pd


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

def pulseResponseCalc(expt):
    pulsePeriods = []
    PeakResponses = []
    df_peaks = pd.DataFrame()
    eP = expt.exptParams

    for sweepID,sweep in expt.recordingData.items():
        ch0_cell = sweep[0]
        ch1_frameTTL = sweep[1]
        ch2_photodiode = sweep[2]

        #calculate first pulse time
        # x = np.diff(ch1_frameTTL)
        # peaks, _ = signal.find_peaks(x,height=np.max(x))
        # pulseStartTime = peaks[0]

        
        # slice out the pulse periods
        sf = eP.stimFreq

        # inter-pulse interval
        IPI = int(20*(1000/sf))

        # pulse start times
        y = ch2_photodiode
        z = np.where(y>0.5*np.max(y),1,0)
        peaks_pd, _ = signal.find_peaks(z,distance=100,height=0.5)
        widths = signal.peak_widths(z,peaks_pd,rel_height=1.0)
        pst = widths[2]

        # pulse period slices
        pst2 = pst+(pst[1]-pst[0])

        res = []
        for t1,t2 in zip(pst,pst2):
            res.append(ch0_cell[int(t1):int(t2)])
        res = np.array(res)

        if eP.EorI = 'I':
            minRes = np.min(res,axis=1)
            PeakResponses.append(np.min(minRes))
            df_peaks.loc[sweepID,[1,2,3,4,5,6,7,8]] = minRes
        else eP.EorI = 'E':
            maxRes = np.max(res,axis=1)
            PeakResponses.append(np.max(maxRes))
            df_peaks.loc[sweepID,[1,2,3,4,5,6,7,8]] = maxRes
            if np.max(maxRes)>80:
                df_peaks.loc[sweepID,"AP"] = 1
                APflag = True
            else:
                 df_peaks.loc[sweepID,"AP"] = 0       

        # tag: improve feature (AP flag sweep wise) 
        APflag = 0
    
    df_peaks["PeakResponse"] = PeakResponses
    if 
    # df_peaks["APflag"] = APflags

    return df_peaks, APflag