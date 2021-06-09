import pyabf
import numpy as np

def abf2data(abfFile,ephysParams):
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

    # Also exporting time axis and Ch0 command waveform for every sweep
    for i in range(numSweeps): 
        abf.setSweep(sweepNumber=i)
        sweepArray.update({'cmd':abf.sweepC})
        for j in range(numChannels):
            abf.setSweep(sweepNumber=i, channel=j)
            sweepArray.update({j:baselineSubtractor(abf.sweepY,ephysParams)})        
        sweepArray.update({'Time':abf.sweepX})
        data[i] = sweepArray
        sweepArray = {}
    
    print('Datafile has {} sweeps in {} channels: \n Ch0: Cell, \n Ch1: FrameTTL, \n Ch2: Photodiode, \n Ch3: Field, \n Time: Time Axis, \n cmd: Ch0 Command Signal'.format(numSweeps,numChannels+2))
    
    return data  

    # abf.setSweep(sweepNumber: 3, channel: 0)
    # print(abf.sweepY) # displays sweep data (ADC)
    # print(abf.sweepX) # displays sweep times (seconds)
    # print(abf.sweepC) # displays command waveform (DAC)

def baselineSubtractor(sweep,ephysParams):
    if ephysParams.baselineSubtraction:        
        sweepNew = sweep - np.mean(sweep[ephysParams.baselineWindow])
        return sweepNew
    else:
        return sweep    