import numpy as np
import pandas as pd
from scipy          import signal
from scipy.optimize import curve_fit

from eidynamics.utils import epoch_to_datapoints as e2dp
from eidynamics.utils import charging_membrane
from eidynamics.utils import PSP_start_time

def RaCalc(recordingData, clamp, IRBaselineEpoch, IRchargingPeriod, IRsteadystatePeriod, Fs=2e4):
    ''' recordingData is the data dictionary with sweeps numbers as keys.
        Provide steadystateWindow values in milliseconds'''

    RaTrend = []
    for s in recordingData.values():
        cmdSig      = s['Cmd']
        resSig      = s[0]
        time        = s['Time']

        chargeTime  = time[e2dp(IRchargingPeriod,Fs)] - IRchargingPeriod[0]
        chargeRes   = resSig[e2dp(IRchargingPeriod,Fs)]

        popt,_      = curve_fit(charging_membrane,chargeTime,chargeRes,bounds=([-10,0],[10,100]),p0=([0.5,0.05]))

        RaTrend.append(popt[1])

        # Ra change flag
        # Ra change screening criterion is 20% change in Ra during the recording
        Raflag      = 0
        if (np.max(RaTrend) - np.min(RaTrend)) / np.mean(RaTrend) > 0.2:
            Raflag  = 1

    return RaTrend, Raflag


def IRcalc(recordingData,clamp,IRBaselineEpoch,IRsteadystatePeriod,Fs=2e4):
    ''' recordingData is the data dictionary with sweeps numbers as keys.
        Provide steadystateWindow values in milliseconds'''

    IRtrend = []
    for s in recordingData.values():
        cmdSig = s['Cmd']
        ss1_cmd = np.mean(cmdSig[e2dp(IRBaselineEpoch,Fs)])
        ss2_cmd = np.mean(cmdSig[e2dp(IRsteadystatePeriod,Fs)])
        delCmd = ss2_cmd - ss1_cmd

        recSig = s[0]
        ss1_rec = np.mean(recSig[e2dp(IRBaselineEpoch,Fs)])
        ss2_rec = np.mean(recSig[e2dp(IRsteadystatePeriod,Fs)])
        delRes = ss2_rec - ss1_rec

        if clamp == 'VC':
            ir = 1000 * delCmd / delRes  # mult with 1000 to convert to MOhms
        else:
            ir = 1000 * delRes / delCmd  # mult with 1000 to convert to MOhms

        IRtrend.append(ir)

        # IR change flag
        # IR change screening criterion is 20% change in IR during the recording
        IRflag = 0
        if (np.max(IRtrend) - np.min(IRtrend)) / np.mean(IRtrend) > 0.2:
            IRflag = 1

    return IRtrend, IRflag


def pulseResponseCalc(recordingData,eP):
    pulsePeriods    = []
    PeakResponses   = []
    AUCResponses    = []
    df_peaks        = pd.DataFrame()

    APflag          = bool(0)

    for sweepID,sweep in recordingData.items():
        ch0_cell        = sweep[0]
        ch1_frameTTL    = sweep[1]
        ch2_photodiode  = sweep[2]

        stimfreq        = eP.stimFreq  # pulse frequency
        Fs              = eP.Fs
        IPI_samples     = int(Fs * (1 / stimfreq))          # inter-pulse interval in datapoints
        firstPulseStart = int(Fs * eP.opticalStimEpoch[0])
        
        res             = []
        t1              = firstPulseStart
        for i in range(eP.numPulses):
            t2 = t1 + IPI_samples
            res.append(ch0_cell[t1:t2])
            t1 = t2
        res             = np.array(res)
        
        peakTimes       = []
        df_peaks.loc[sweepID + 1, "firstPulseDelay"],_ = PSP_start_time(ch0_cell,eP.clamp,eP.EorI,stimStartTime=eP.opticalStimEpoch[0],Fs=Fs)

        if eP.EorI == 'I' or eP.clamp == 'CC':
            maxRes = np.max(res, axis=1)
            aucRes = np.trapz(res,axis=1)
            PeakResponses.append(np.max(maxRes))
            
            df_peaks.loc[sweepID + 1, [1,2,3,4,5,6,7,8]] = maxRes
            
            for resSlice in res:
                maxVal = np.max(resSlice)
                pr = np.where(resSlice == maxVal)[0]  # signal.find_peaks(resSlice,height=maxVal)
                peakTimes.append(pr[0] / 20)
            df_peaks.loc[sweepID + 1, [9,10,11,12,13,14,15,16]] = peakTimes[:]
            
            df_peaks.loc[sweepID + 1, "AP"] = bool(False)
            if eP.clamp == 'CC':
                df_peaks.loc[sweepID + 1, "AP"] = bool(np.max(maxRes) > 80) # 80 mV take as a threshold above baseline to count a response as a spike
                APflag = bool(df_peaks.loc[sweepID + 1, "AP"] == True)
            
            df_peaks.loc[sweepID + 1, [17,18,19,20,21,22,23,24]] = aucRes

        elif eP.EorI == 'E' and eP.clamp == 'VC':
            minRes = np.min(res, axis=1)
            aucRes = np.trapz(res,axis=1)
            PeakResponses.append(np.min(minRes))

            df_peaks.loc[sweepID + 1, [1,2,3,4,5,6,7,8]] = minRes
            
            for resSlice in res:
                minVal = np.min(resSlice)
                pr = np.where(resSlice == minVal)[0]  # pr,_ = signal.find_peaks(-1*resSlice,height=np.max(-1*resSlice))
                peakTimes.append(pr[0] / 20)
            
            df_peaks.loc[sweepID + 1, [9,10,11,12,13,14,15,16]] = peakTimes[:]
            df_peaks.loc[sweepID + 1, "AP"] = bool(np.max(-1 * minRes) > 80)
            APflag = bool(df_peaks.loc[sweepID + 1, "AP"] == True)

            df_peaks.loc[sweepID + 1, [17,18,19,20,21,22,23,24]] = aucRes

    df_peaks.astype({"AP":'bool'})    
    df_peaks["PeakResponse"]                     = PeakResponses
    df_peaks["datafile"]                         = eP.datafile

    return df_peaks, APflag

# FIXME: remove hardcoded variables, fields, and values
