import numpy as np
from scipy import signal
import pandas as pd
import matplotlib.pyplot as plt

# tag: improve feature (remove hardcoded variables, fields, and values)

def IRcalc(recordingData,clamp,steadystateWindow1,steadystateWindow2):
    ''' recordingData is the data dictionary with sweeps numbers as keys
    Provide steadystateWindow values in milliseconds'''
    
    Fs = 20
    IRtrend = []
    for s in recordingData.values():
        cmdSig = s['cmd']
        ss1_cmd = np.mean(cmdSig[steadystateWindow1*Fs])
        ss2_cmd = np.mean(cmdSig[steadystateWindow2*Fs])
        delCmd = ss2_cmd-ss1_cmd


        recSig = s[0]
        ss1_rec = np.mean(recSig[steadystateWindow1*Fs])
        ss2_rec = np.mean(recSig[steadystateWindow2*Fs])
        delRes = ss2_rec-ss1_rec

        if clamp == 'VC':
            ir = 1000*delCmd/delRes
        else:
            ir = 1000*delRes/delCmd

        IRtrend.append(ir) # mult with 1000 to convert to MOhms

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
        
        # slice out the pulse periods
        sf = eP.stimFreq #pulse frequency
        IPI = int(20*(1000/sf)) # inter-pulse interval

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
        # print(sweepID,'---',np.shape(res))
        peakTimes =[]

        if eP.EorI == 'I' or eP.clamp == 'CC':
            maxRes = np.max(res,axis=1)
            PeakResponses.append(np.max(maxRes))
            df_peaks.loc[sweepID+1,[1,2,3,4,5,6,7,8]] = maxRes
            for resSlice in res:
                maxVal = np.max(resSlice)
                pr = np.where(resSlice == maxVal)[0] #signal.find_peaks(resSlice,height=maxVal)
                peakTimes.append(pr[0]/20)
            df_peaks.loc[sweepID+1,[9,10,11,12,13,14,15,16]]=peakTimes[:]
            df_peaks.loc[sweepID+1,"firstPulseTime"]=peakTimes[0]
            df_peaks.loc[sweepID+1,"AP"] = False
            if eP.clamp == 'CC':
                df_peaks.loc[sweepID+1,"AP"] = bool(np.max(maxRes)>80)
                APflag = bool(df_peaks.loc[sweepID+1,"AP"] == True)
        elif eP.EorI == 'E' and eP.clamp == 'VC':
            minRes = np.min(res,axis=1)
            PeakResponses.append(np.min(minRes))
            df_peaks.loc[sweepID+1,[1,2,3,4,5,6,7,8]] = minRes
            for resSlice in res:
                minVal = np.min(resSlice) 
                pr = np.where(resSlice == minVal)[0] #pr,_ = signal.find_peaks(-1*resSlice,height=np.max(-1*resSlice))
                peakTimes.append(pr[0]/20)
            df_peaks.loc[sweepID+1,[9,10,11,12,13,14,15,16]]=peakTimes[:]
            df_peaks.loc[sweepID+1,"firstPulseTime"]=peakTimes[0]
            
            df_peaks.loc[sweepID+1,"AP"] = bool(np.max(-1*minRes)>80)
            APflag = bool(df_peaks.loc[sweepID+1,"AP"] == True)
                   

        # tag: improve feature (AP flag sweep wise) 
        APflag = 0
    
    df_peaks["PeakResponse"] = PeakResponses

    return df_peaks, APflag