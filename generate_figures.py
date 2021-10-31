'''Generate figure 1
'''
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import h5py
import eidynamics.utils as utils

allCellDataFile = "C:\\Users\\aditya\\OneDrive\\NCBS\\Lab\\Projects\\EI_Dynamics\\training_data\\allCells_trainingSet_short.h5"
ephysStart = 27
ephysEnd   = 20027

def main():
    
    with h5py.File( allCellDataFile, "r") as f:
        print("Keys:", f.keys())
        print("data:", f['default'] )
        df = pd.DataFrame( f['default'] )
        df.rename( columns = {0:"StimFreq", 1:"numSq", 2: "intensity", 3: "pulseWidth", 4: "MeanBaseline", 5: "ClampingPotl", 6:"Clamp", 7: "GABAzineFlag", 8:"InputRes", 9:"Ra", 10:"patternID",27:"AP"}, inplace = True )
        # figure1(df)
        figure2(df)
        plt.show()
    
    return df


def figure1(df):
    df = df.loc[ (df["Clamp"]==0) & (df["numSq"]!=1) & (df["patternID"]<56) & (df["intensity"]==100) & (df["GABAzineFlag"] == 0 ) & (df["pulseWidth"]==2) & (df["AP"]==0) ]
    freqs = np.unique(df["StimFreq"])
    spots = np.unique(df["numSq"])
    
    for i,sq in enumerate(spots):
        for j,freq in enumerate(freqs):
            subplotWin = (4*(i)+j+1)
            print(i,j,sq,freq,subplotWin)
            ax = plt.subplot(2,4,subplotWin)
            p0 = df.loc[(df["numSq"]==sq) & (df["StimFreq"]==freq)]
            patdata = p0.iloc[:,ephysStart:ephysEnd]
            patmean = patdata.mean( axis = 0 )
            
            for k, p1 in patdata.iterrows():
                ax.plot( np.linspace(0,1000,20000), p1, color='#d1e5f0',alpha=0.8)
            ax.plot( np.linspace(0,1000,20000), patmean, color="#2166ac", label = str( int(sq)) +"Sq_" + str(int(freq))+"Hz" )
            ax.set_xlabel( "Time (ms)" )
            ax.set_ylabel( "EPSP (mV)" )
            ax.set_ylim([-5.0,10])
            ax.legend(loc="upper right")
    # plt.show()

def figure2(df):
    df = df.loc[ (df["Clamp"]==1) & (df["numSq"]!=1)& (df["numSq"]!=7) & (df["patternID"]<56) & (df["GABAzineFlag"] == 0 ) & (df["AP"]==0) ]
    # df.to_numpy(dtype='float16')
    freqs = np.unique(df["StimFreq"])[:-1]
    spots = np.unique(df["numSq"])
    clamps = np.unique(df["ClampingPotl"])
    for i,sq in enumerate(spots):
        for j,freq in enumerate(freqs):
            for k,ei in enumerate(clamps):
                subplotWin = (4*(i)+j+1)

                ax = plt.subplot(2,4,subplotWin)
                p0 = df.loc[(df["numSq"]==sq) & (df["StimFreq"]==freq) & (df["ClampingPotl"]==ei)]
                
                patdata = p0.iloc[:,ephysStart:ephysEnd]
                patmean = patdata.mean( axis = 0 )
                
                if k==0:
                    for m, p1 in patdata.iterrows():
                        epsc1Peak = -1*np.min(p1)
                        p1 = p1/epsc1Peak
                        p1 = utils.filter_data(p1, filter_type='butter',high_cutoff=300,sampling_freq=2e4)
                        ax.plot( np.linspace(0,1000,20000), p1, color='#d1e5f0',alpha=0.2 )
                    epsc1Peak_formean = -1*np.min(patmean)
                    patmean = patmean/epsc1Peak_formean
                    patmean = utils.filter_data(patmean, filter_type='butter',high_cutoff=300,sampling_freq=2e4)
                    ax.plot( np.linspace(0,1000,20000), patmean, color="#2166ac", label = str( int(sq)) +"Sq_" + str(int(freq))+"Hz_"+str(int(ei)) )

                elif k==1:
                    for m, p1 in patdata.iterrows():
                        
                        epsc1Peak = np.max(p1)
                        p1 = p1/epsc1Peak
                        p1 = utils.filter_data(p1, filter_type='butter',high_cutoff=300,sampling_freq=2e4)
                        ax.plot( np.linspace(0,1000,20000), p1, color='#fddbc7',alpha=0.2 )
                    epsc1Peak_formean = np.max(patmean)
                    patmean = patmean/epsc1Peak_formean
                    patmean = utils.filter_data(patmean, filter_type='butter',high_cutoff=300,sampling_freq=2e4)
                    ax.plot( np.linspace(0,1000,20000), patmean, color="#ef8a62", label = str( int(sq)) +"Sq_" + str(int(freq))+"Hz_"+str(int(ei)) )
                
                ax.set_xlabel("Time (ms)")
                ax.set_ylabel( "EPSC (pA)" )
                ax.legend(loc="upper right")
    
if __name__ == "__main__":
    main()