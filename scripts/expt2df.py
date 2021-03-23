import numpy as np
from scipy import signal
import pandas as pd
import ePhysFunctions as ephysFunc

def expt2df(expt):
    # read experiment type
    exptType = expt.exptParams.exptType
    eP = expt.exptParams
    numSweeps = len(expt.stimCoords)
    
    # create the dataframe that stores analyzed experiment results
    df = pd.DataFrame()
    features = ["Sweep","Repeat","Pattern","numSquares","Coords","Intensity","pulseWidth","StimFreq"]
    df = pd.DataFrame(index=np.arange(1,numSweeps+1),columns=features)

    # fill in columns for experiment parameters,
    # they will serve as axes for sorting analysed data in plots
    for r,co in expt.stimCoords.items(): df.loc[r,"Sweep"]=r # coords
    for r,co in expt.stimCoords.items(): df.loc[r,"Coords"]=co # coords
    for r,co in expt.stimCoords.items(): df.loc[r,"numSquares"]=int(len(co)) #numSquares

    df["StimFreq"] = eP.stimFreq #stimulation pulse frequency
    df["Intensity"] = eP.intensity # LED intensity
    print('--------',len(df))

    df["Pattern"] = eP.patterns
    df["Repeat"] = eP.repeats
    df["pulseWidth"] = eP.pulseWidth

    print('--------',len(df))
    # Add analysed data columns
    df["IR"],IRflag = ephysFunc.IRcalc(expt.recordingData,eP.IR_baselineWindow,eP.IR_steadystateWindow)
    expt.Flags.update({"IRflag": IRflag})








    # check if the response df already exists
    if not expt.neuron.response.empty:
        expt.neuron.response = pd.concat([expt.neuron.response,df])
    else:
        expt.neuron.response = df

    return expt