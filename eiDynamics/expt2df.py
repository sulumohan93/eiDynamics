import numpy as np
from scipy import signal
import pandas as pd
from . import patternIndex
from . import ePhysFunctions as ephysFunc

# tag: improve feature (remove hardcoded variables, fields, and values)
def expt2df(expt,neuron):
    # read experiment type
    eP = expt.exptParams
    numSweeps = len(expt.stimCoords)
    
    # create the dataframe that stores analyzed experiment results
    df = pd.DataFrame()
    features = ["Sweep","Repeat","PatternID","numSquares","Coords","Intensity","pulseWidth","StimFreq"]
    df = pd.DataFrame(columns=features)
    df.astype({'Coords': 'object'})

    # fill in columns for experiment parameters,
    # they will serve as axes for sorting analysed data in plots
    for r,co in expt.stimCoords.items():
        df.loc[r,"Sweep"]=r # coords
        df.loc[r,"Coords"]=co # coords
        df.loc[r,"numSquares"]=int(len(co)) #numSquares
        df.loc[r,"numSquares"]=int(len(co))
        df.loc[r,"PatternID"] = patternIndex.givePatternID(co)

    df["StimFreq"] = eP.stimFreq #stimulation pulse frequency
    df["Intensity"] = eP.intensity # LED intensity
    df["Repeat"] = eP.repeats
    df["pulseWidth"] = eP.pulseWidth
    df["EI"] = eP.EorI

    # Add analysed data columns
    '''IR'''
    df["IR"],IRflag = ephysFunc.IRcalc(expt.recordingData,eP.clamp,eP.IR_baselineWindow,eP.IR_steadystateWindow)
    expt.Flags.update({"IRFlag": IRflag})

    '''EPSP peaks'''
    df_peaks,APflag = ephysFunc.pulseResponseCalc(expt)
    expt.Flags.update({"APFlag": APflag})
    df = pd.concat([df, df_peaks],axis=1)

    # check if the response df already exists
    if not neuron.response.empty:
        neuron.response = pd.concat([neuron.response,df])
    else:
        neuron.response = df

    return expt