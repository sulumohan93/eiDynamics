import numpy as np
from scipy import signal
import pandas as pd

from eidynamics import pattern_index
from eidynamics import ephys_functions as ephysFunc


def expt2df(expt,neuron,eP):
    '''read experiment type and returns experiment object'''
    numSweeps = len(expt.stimCoords)

    # create the dataframe that stores analyzed experiment results
    df = pd.DataFrame()
    features = ["Sweep","Repeat","PatternID","numSquares","Intensity","pulseWidth","StimFreq","EI","unit"]  # removed "coords" from columns
    df = pd.DataFrame(columns=features)
    df.astype({"Sweep":'int8',"Repeat":"int8","PatternID":"int8",
               "numSquares":"int8","Intensity":"int8","pulseWidth":"int8",
               "StimFreq":"int8","EI":"string"})  # "Coords":'object',

    # fill in columns for experiment parameters,
    # they will serve as axes for sorting analysed data in plots
    for r,co in expt.stimCoords.items():
        df.loc[r,"Sweep"] = int(r)  # coords
        # df.loc[r,"Coords"]=np.array(co)  # coords
        df.loc[r,"numSquares"] = int(len(co))  # numSquares
        df.loc[r,"PatternID"] = int(pattern_index.givePatternID(co))

    df["StimFreq"] = eP.stimFreq  # stimulation pulse frequency
    df["Intensity"] = eP.intensity  # LED intensity
    repeatSeq = (np.concatenate([np.linspace(1, 1, int(numSweeps / eP.repeats)), np.linspace(2, 2, int(numSweeps / eP.repeats)), np.linspace(3, 3, int(numSweeps / eP.repeats))])).astype(int)
    df["Repeat"] = repeatSeq[:numSweeps]
    df["pulseWidth"] = eP.pulseWidth
    df["EI"] = str(eP.EorI)
    df["unit"] = str(eP.unit)
    df["cellID"] = str(eP.cellID)
    df.astype({"unit":'string'})
    df.astype({"EI":'string'})

    # Add analysed data columns
    '''IR'''
    df["IR"],IRflag = ephysFunc.IRcalc(expt.recordingData,eP.clamp,eP.IRBaselineEpoch,eP.IRsteadystatePeriod)
    expt.Flags.update({"IRFlag": IRflag})

    '''Ra'''
    df["Ra"],Raflag = ephysFunc.RaCalc(expt.recordingData,eP.clamp,eP.IRBaselineEpoch,eP.IRchargingPeriod,eP.IRsteadystatePeriod)
    expt.Flags.update({"RaFlag": Raflag})

    '''EPSP peaks'''
    df_peaks,APflag = ephysFunc.pulseResponseCalc(expt.recordingData,eP)
    expt.Flags.update({"APFlag": APflag})
    df = pd.concat([df, df_peaks],axis=1)

    # check if the response df already exists
    if not neuron.response.empty:
        neuron.response = pd.concat([neuron.response,df])
    else:
        neuron.response = df
    neuron.response = neuron.response.drop_duplicates()  # prevents duplicates from buildup if same experiment is run again.

    return expt

# FIXME: remove hardcoded variables, fields, and values
