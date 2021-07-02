import pyabf
import numpy as np

def abf2data(abfFile,*args):
    ''' A wrapper around pyabf module to generate sweep wise dictionary of recorded traces.
    The first argument should be the abf file, second can be the experiment parameters, which
    if not supplied will be loaded from defaults. Baseline Subtraction is OFF by default.'''
        
    try:
        if abfFile:
            print('Loading ABF file')                        
    except:
        print('Please provide valid file')

    abf = pyabf.ABF(abfFile)
    numSweeps = abf.sweepCount
    numChannels = abf.channelCount

    data ={}
    sweepArray = {}

    try:
        eP = args[0]
    except:
        print('Something wrong with ep Params or not supplied. Using default.')
        from . import ExperimentParameters_Default as eP

    # Also exporting time axis and Ch0 command waveform for every sweep
    baselineValues = np.zeros([numSweeps,1])
    baselineFlag = False
    for i in range(numSweeps): 
        abf.setSweep(sweepNumber=i)
        sweepArray.update({'cmd':abf.sweepC})
        for j in range(numChannels):
            abf.setSweep(sweepNumber=i, channel=j)
            parsedSweep,swpBaseline = baselineSubtractor(abf.sweepY,eP,subtractBaseline=True)
            sweepArray.update({j:parsedSweep})
            if j==0:
                baselineValues[i] = swpBaseline
                parsedSweep,swpBaseline = baselineSubtractor(abf.sweepY,eP,eP.baselineSubtraction)
        sweepArray.update({'Time':abf.sweepX})
        data[i] = sweepArray
        sweepArray = {}

    meanBaseline =  np.mean(baselineValues)
    if ((np.max(baselineValues)-np.min(baselineValues))/np.mean(baselineValues))-1 > eP.baselineCriterion:
        baselineFlag = True
    else:
        baselineFlag = False

    
    print('Datafile has {} sweeps in {} channels: \n Ch0: Cell, \n Ch1: FrameTTL, \n Ch2: Photodiode, \n Ch3: Field, \n Time: Time Axis, \n cmd: Ch0 Command Signal'.format(numSweeps,numChannels+2))
    
    return data,meanBaseline,baselineFlag  

    '''pyABF sweep extraction reference'''
    # abf.setSweep(sweepNumber: 3, channel: 0)
    # print(abf.sweepY) # displays sweep data (ADC)
    # print(abf.sweepX) # displays sweep times (seconds)
    # print(abf.sweepC) # displays command waveform (DAC)

def baselineSubtractor(sweep,ephysParams,subtractBaseline):
    sweepBaseline = np.mean(sweep[ephysParams.baselineWindow])
    if subtractBaseline:        
        sweepNew = sweep - sweepBaseline
        return sweepNew, sweepBaseline
    else:
        return sweep, sweepBaseline    