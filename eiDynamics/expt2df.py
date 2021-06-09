import numpy as np
from scipy import signal
import pandas as pd

from . import ePhysFunctions as ephysFunc

# tag: improve feature (remove hardcoded variables, fields, and values)
def expt2df(expt,neuron):
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
    df["Pattern"] = eP.patterns
    df["Repeat"] = eP.repeats
    df["pulseWidth"] = eP.pulseWidth
    df["EI"] = eP.EorI

    # Add analysed data columns
    # IR
    df["IR"],IRflag = ephysFunc.IRcalc(expt.recordingData,eP.clamp,eP.IR_baselineWindow,eP.IR_steadystateWindow)
    expt.Flags.update({"IRFlag": IRflag})

    # EPSP peaks
    df_peaks,APflag = ephysFunc.pulseResponseCalc(expt)
    expt.Flags.update({"APFlag": APflag})
    df = pd.concat([df, df_peaks],axis=1)


    # check if the response df already exists
    if not neuron.response.empty:
        neuron.response = pd.concat([neuron.response,df])
    else:
        neuron.response = df

    return expt