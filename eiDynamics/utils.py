import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import filter_design
from scipy.signal import butter, bessel, decimate, sosfiltfilt

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


def findPSPstart(x):
    y = baseline(x)
    stdX = np.std(y[:100])
    movAvgX = moving_average(y,10)
    y = np.where(movAvgX > 3. * stdX)
    return y[0][0]


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