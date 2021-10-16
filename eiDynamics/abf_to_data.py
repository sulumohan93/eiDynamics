import sys
import pyabf
import numpy as np
import matplotlib.pyplot as plt

# tag FIXME HACK 
try:
    from eidynamics.utils import epoch_to_datapoints, filter_data, plot_abf_data
except ModuleNotFoundError:
    from utils import epoch_to_datapoints, filter_data, plot_abf_data

def abf_to_data(abf_file,exclude_channels=[],baseline_criterion=0.1,sweep_baseline_epoch=[0, 0.2],baseline_subtraction=True,signal_scaling=1,sampling_freq=2e4,filter_type='',filter_cutoff=2e3,plot_data=False):
    """
    A wrapper around pyabf module to generate sweep wise dictionary of recorded traces.
    Returns a list with [dict holding sweepwisedata, mean baseline value, baseline fluctuation flag]
    Usual Channel Labels:
        0       : Cell,
        1       : FrameTTL,
        2       : Photodiode,
        3       : Field,
        'Time'  : Time Axis,
        'Cmd'   : Ch0 Command Signal
    """

    try:
        if abf_file:
            print('Loading ABF file')
    except FileNotFoundError as err:
        print(err)
        print('Please provide valid file')

    abf             = pyabf.ABF(abf_file)
    numSweeps       = abf.sweepCount
    numChannels     = abf.channelCount

    data            = {}
    sweepArray      = {}

    baselineValues  = np.zeros([numSweeps,1])
    meanBaseline    = 0.0
    baselineFlag    = False

    for sweep in range(numSweeps):
        abf.setSweep(sweepNumber=sweep)
        # Optionally exporting time axis and Ch0 command waveform for every sweep
        if not 'Cmd' in exclude_channels:
            sweepArray.update({'Cmd':abf.sweepC})
        if not 'Time' in exclude_channels:
            sweepArray.update({'Time':abf.sweepX})

        for ch in range(numChannels):
            abf.setSweep(sweepNumber=sweep, channel=ch)
            if ch==0 and not ch in exclude_channels:
                _parsedSweep,_swpBaseline   = _baseline_subtractor(abf.sweepY,sweep_baseline_epoch,sampling_freq,subtract_baseline=baseline_subtraction)
                baselineValues[sweep]       = _swpBaseline
                parsedSweep                 = filter_data(_parsedSweep,filter_type=filter_type,high_cutoff=filter_cutoff,sampling_freq=sampling_freq)
                sweepArray.update({ch:signal_scaling * parsedSweep})
            elif ch!=0 and not ch in exclude_channels:
                parsedSweep,_               = _baseline_subtractor(abf.sweepY,sweep_baseline_epoch,sampling_freq,subtract_baseline=True)
                sweepArray.update({ch:signal_scaling * parsedSweep})
            else:
                pass

        
        data[sweep] = sweepArray
        sweepArray = {}
    if not np.all(baselineValues):    
        meanBaseline = np.mean(baselineValues)
        baselineFlag = ((np.max(baselineValues) - np.min(baselineValues)) / np.mean(baselineValues)) - 1 > baseline_criterion
    # if ((np.max(baselineValues) - np.min(baselineValues)) / np.mean(baselineValues)) - 1 > baseline_criterion:
    #     baselineFlag = True
    # else:
    #     baselineFlag = False

    print(f'Datafile has {numSweeps} sweeps in {len(data[0])} channels.')

    if plot_data:
        plot_abf_data(data)

    return data,meanBaseline,baselineFlag

    '''pyABF sweep extraction reference'''
    # abf.setSweep(sweepNumber: 3, channel: 0)
    # print(abf.sweepY) # displays sweep data (ADC)
    # print(abf.sweepX) # displays sweep times (seconds)
    # print(abf.sweepC) # displays command waveform (DAC)


def _baseline_subtractor(sweep,sweep_baseline_epoch,sampling_freq,subtract_baseline):
    baselineWindow = epoch_to_datapoints(sweep_baseline_epoch,sampling_freq)
    sweepBaseline = np.mean(sweep[baselineWindow])
    if subtract_baseline:
        sweepNew = sweep - sweepBaseline
        return sweepNew, sweepBaseline
    else:
        return sweep, sweepBaseline

if __name__ == '__main__':
    abfFile = sys.argv[1]
    abf_to_data(abfFile,plot_data=True)