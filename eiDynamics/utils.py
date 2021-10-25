import sys
import numpy as np
import matplotlib.pyplot as plt

from scipy.signal import filter_design
from scipy.signal import butter, bessel, decimate, sosfiltfilt
from scipy.signal import find_peaks, peak_widths

frameSize = [13032.25, 7419.2]  # Aug 2021 calibration


def gridSizeCalc(sqSize,objMag,frameSz=frameSize):

    gridSize = np.array([1,1])

    frameSize = (1.0 / objMag) * np.array(frameSz)
    print('frame Size is (um):', frameSize)

    gridSize[0] = frameSize[0] / sqSize[0]
    gridSize[1] = frameSize[1] / sqSize[1]

    print(f"A grid of {gridSize[0]} x {gridSize[1]} squares will create squares of"
          f" required {sqSize[0]} x {sqSize[1]} µm with an aspect ratio of {sqSize[0]/sqSize[1]}")
    print('Nearest grid Size option is...')
    print('A grid of {} squares x {} squares'.format(int(np.ceil(gridSize[0])),int(np.ceil(gridSize[1]))))

    squareSizeCalc(np.ceil(gridSize),objMag)


def squareSizeCalc(gridSize,objMag,frameSz=frameSize):
    '''
    Pass two values as the arguments for the file: [gridSizeX, gridSizeY], objectiveMag
    command line syntax should look like:  [24 24] 40
    '''
    squareSize_1x = np.array(frameSz) * (1 / objMag)
    ss = np.array([1, 1])

    if len(gridSize) == 2:
        ss[0] = squareSize_1x[0] / gridSize[0]
        ss[1] = squareSize_1x[1] / gridSize[1]
    else:
        ss = squareSize_1x / gridSize

    print(f"Polygon Square will be {ss[0]} x {ss[1]} µm with an aspect ratio of {ss[0]/ ss[1]}.")
    return ss


def filter_data(x, filter_type='butter',high_cutoff=2e3,sampling_freq=2e4):
    if filter_type == 'butter':
        sos = butter(N=2, Wn=high_cutoff, fs=sampling_freq, output='sos')
        y = sosfiltfilt(sos,x)
    elif filter_type == 'bessel':
        sos = bessel(4, high_cutoff, fs=sampling_freq, output='sos')
        y = sosfiltfilt(sos,x)
    elif filter_type == 'decimate':
        y = decimate(x, 10, n=4)
    else:
        y = x
    return y


def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w


def baseline(x):
    baselineWindow = int(0.1*len(x))
    return x - np.mean(x[:baselineWindow])


def plot_abf_data(dataDict):
    numChannels = len(dataDict[0])
    fig,axs     = plt.subplots(numChannels-1,1,sharex=True)
    for sweep in range(len(dataDict)):
        sweepData   = dataDict[sweep]       
        i           = 0
        axs[0].plot(sweepData['Time'][::5],sweepData['Cmd'][::5],'r')
        for i in range(numChannels-2):
            axs[i+1].plot(sweepData['Time'][::5],sweepData[i][::5],'b')
            axs[i+1].set_ylabel('Ch#'+str(i))

    axs[0].set_ylabel('Ch#0 Command')
    axs[-1].set_xlabel('Time (s)')
    axs[-1].annotate('* Data undersampled for plotting',xy=(1.0, -0.5),xycoords='axes fraction',ha='right',va="center",fontsize=6)
    fig.suptitle('ABF Data*')
    plt.show()


def find_resposne_start(x,method='stdDev'):
    if method == 'stdDev':    
        y = np.abs(baseline(x))
        stdX = np.std(y[:4600])
        movAvgX = moving_average(y,10)
        z = np.where(movAvgX > 5. * stdX)
        return z[0][0]
    elif method == 'slope':
        y = np.abs(baseline(x))
        dy = np.diff(y,n=2) # using second derivative
        z = np.where(dy==np.max(dy))
        return z[0][0]


def epoch_to_datapoints(epoch,Fs):
    t1 = epoch[0]
    t2 = epoch[1]
    x = np.arange(t1, t2, 1 / Fs)
    return (x * Fs).astype(int)


def charging_membrane(t, A, tau):
    y = A * (1 - np.exp(-t / tau))
    return y


def alpha_synapse(x,Vmax,tau):
    a = 1/tau
    y = Vmax*(a*x)*np.exp(1-a*x)
    return y


def PSP_start_time_1sq(response_array_1sq,clamp,EorI,stimStartTime=0.231,Fs=2e4):
    '''
    Input: nxm array where n is number of frames, m is datapoints per sweep
    '''
    if len(response_array_1sq.shape)==1:
        avgAllSpots     = response_array_1sq - rolling_variance_baseline(response_array_1sq)[0]
        avgAllSpots     = avgAllSpots[:5600]
        avgAllSpots     = np.where(avgAllSpots>30,30,avgAllSpots)        
    else:
        avgAllSpots     = np.mean(response_array_1sq[:,:5600],axis=0) #clipping signal for speed
    if clamp == 'VC' and EorI == 'E':
        avgAllSpots     = -1*avgAllSpots
    w                   = 40 if np.max(avgAllSpots)>=30 else 60
    stimStart           = int(Fs*stimStartTime)
    avgAllSpots         = filter_data(avgAllSpots, filter_type='butter',high_cutoff=300,sampling_freq=Fs)
    movAvgAllSpots      = moving_average(np.append(avgAllSpots,np.zeros(19)),20)
    response            = movAvgAllSpots - avgAllSpots
    stdDevResponse      = np.std(response[:stimStart])
    responseSign        = np.sign(response-stdDevResponse)
    peaks               = find_peaks(responseSign[stimStart:],distance=100,width=w)

    zeroCrossingPoint   = peaks[1]['left_ips']

    PSPStartTime_1sq    = stimStart + zeroCrossingPoint
    PSPStartTime_1sq    = PSPStartTime_1sq/Fs
    
    try:
        synDelay_ms        = 1000*(PSPStartTime_1sq[0] - stimStartTime)
    except:
        synDelay_ms        = np.NaN
    
    return synDelay_ms


def delayed_alpha_function(t,A,tau,delta):
    tdel = np.zeros(int(2e4*delta))
    T   = np.append(tdel,t)
    T = T[:len(t)]
    a   = 1/tau
    y   = A*(a*T)*np.exp(1-a*T)
    return y

def rolling_variance_baseline(vector,window=500,slide=50):
    t1          = 0
    leastVar    = 1000
    leastVarTime= 0
    lastVar     = 1000
    mu          = 0
    count       = int(len(vector)/slide)
    for i in range(count):
        t2      = t1+window        
        sigmaSq = np.var(vector[t1:t2])
        if sigmaSq<leastVar:
            leastVar     = sigmaSq
            leastVarTime = t1
            mu           = np.mean(vector[t1:t2])
        t1      = t1+slide
    
    baselineAvg      = mu
    baselineVariance = sigmaSq
    baselineAvgWindow= np.arange(leastVarTime,leastVarTime+window)
    return [baselineAvg,baselineVariance,baselineAvgWindow]