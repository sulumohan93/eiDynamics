import matplotlib.pyplot as plt
import seaborn as sns
sns.set_context("talk")

def abf2df(abfFile):
    try:
        if abfFile:
            import pyabf
            import numpy as np
    except:
        print('Please provide valid file')

    abf = pyabf.ABF(abfFile)
    numSweeps = abf.sweepCount
    numChannels = abf.channelCount

    data ={}
    sweepArray = {}

    for i in range(numSweeps):
        for j in range(numChannels):
            abf.setSweep(sweepNumber=i,channel=j)
            sweepArray.update({j:abf.sweepY})
        sweepArray.update({'Time':abf.sweepX})
        data[i] = sweepArray
        sweepArray = {}

    print('Datafile has {} sweeps in {} channels: \n Ch0: Cell, \n Ch1: FrameTTL, \n Ch2: Photodiode, \n Time: Time Axis'.format(numSweeps,numChannels+1))
    
    return data  