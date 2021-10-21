import numpy as np
import pandas as pd
from scipy          import signal
from scipy.optimize import curve_fit

from eidynamics.utils import epoch_to_datapoints as e2dp
from eidynamics.utils import charging_membrane

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

        popt,_      = curve_fit(charging_membrane,chargeTime,chargeRes)

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
    df_peaks        = pd.DataFrame()

    APflag          = bool(0)

    for sweepID,sweep in recordingData.items():
        ch0_cell        = sweep[0]
        ch1_frameTTL    = sweep[1]
        ch2_photodiode  = sweep[2]

        # # slice out the pulse periods
        # stimfreq        = eP.stimFreq  # pulse frequency
        # IPI_samples     = int(20 * (1000 / stimfreq))  # inter-pulse interval
        # firstPulseStart = int(231.4 * 20)

        # for i in range(eP.numPulses):
        #     pst[i]      = firstPulseStart + i*IPI_samples

        # # pulse start times
        
        # z           = np.where(ch2_photodiode > 0.5 * np.max(ch2_photodiode[4800:6000]), 1, 0)  # z is the binarized photodiode signal
        # peaks_pd, _ = signal.find_peaks(z, distance=150, height=0.5)  # at least 7.5 ms apart pulses
        # widths      = signal.peak_widths(z, peaks_pd, rel_height=1.0)
        # pst         = widths[2]

        # # pulse period slices
        # pst2        = pst + (pst[1] - pst[0])
        stimfreq        = eP.stimFreq  # pulse frequency
        IPI_samples     = int(20 * (1000 / stimfreq))  # inter-pulse interval
        firstPulseStart = int(231.4 * 20)
        pst = np.zeros(eP.numPulses)
        pst2 = np.zeros(eP.numPulses)
        for i in range(eP.numPulses):
            pst[i]      = firstPulseStart + i*IPI_samples
        pst2    = pst + (pst[1]-pst[0])
        
        res         = []
        for t1,t2 in zip(pst,pst2):
            res.append(ch0_cell[int(t1):int(t2)])

        res         = np.array(res)

        peakTimes   = []

        if eP.EorI == 'I' or eP.clamp == 'CC':
            maxRes = np.max(res, axis=1)
            PeakResponses.append(np.max(maxRes))
            df_peaks.loc[sweepID + 1, [1,2,3,4,5,6,7,8]] = maxRes
            for resSlice in res:
                maxVal = np.max(resSlice)
                pr = np.where(resSlice == maxVal)[0]  # signal.find_peaks(resSlice,height=maxVal)
                peakTimes.append(pr[0] / 20)
            df_peaks.loc[sweepID + 1, [9,10,11,12,13,14,15,16]] = peakTimes[:]
            df_peaks.loc[sweepID + 1, "firstPulseTime"] = peakTimes[0]
            df_peaks.loc[sweepID + 1, "AP"] = bool(False)
            if eP.clamp == 'CC':
                df_peaks.loc[sweepID + 1, "AP"] = bool(np.max(maxRes) > 80)
                APflag = bool(df_peaks.loc[sweepID + 1, "AP"] == True)
        elif eP.EorI == 'E' and eP.clamp == 'VC':
            minRes = np.min(res, axis=1)
            PeakResponses.append(np.min(minRes))
            df_peaks.loc[sweepID + 1, [1,2,3,4,5,6,7,8]] = minRes
            for resSlice in res:
                minVal = np.min(resSlice)
                pr = np.where(resSlice == minVal)[0]  # pr,_ = signal.find_peaks(-1*resSlice,height=np.max(-1*resSlice))
                peakTimes.append(pr[0] / 20)
            df_peaks.loc[sweepID + 1, [9,10,11,12,13,14,15,16]] = peakTimes[:]
            df_peaks.loc[sweepID + 1, "firstPulseTime"] = peakTimes[0]
            df_peaks.loc[sweepID + 1, "AP"] = bool(np.max(-1 * minRes) > 80)
            APflag = bool(df_peaks.loc[sweepID + 1, "AP"] == True)

    df_peaks.astype({"AP":'bool'})
    df_peaks["PeakResponse"] = PeakResponses
    df_peaks["datafile"] = eP.datafile

    return df_peaks, APflag

# FIXME: remove hardcoded variables, fields, and values
