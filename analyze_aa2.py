'''
author: U. S. Bhalla, NCBS
26 Oct, 2021
'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import h5py
import argparse

# Field ordering:
# 0  Stim Freq : 10, 20, 30, 40, 50, 100 Hz
# 1  numSquares : 1, 5, 7, 15 sq
# 2  intensity : 100 or 50%
# 3  pulse width : 2 or 5 ms
# 4  meanBaseline : mV
# 5  clamp potential: -70 or 0 mV
# 6  CC or VC : CC = 0, VC = 1
# 7  Gabazine : Control = 0, Gabazine = 1
# 8  IR : MOhn
# 9  Ra : membrane time constant
# 10 pattern ID : refer to pattern ID in pattern index
# 11:26 coords of spots [11,12,13,14,15, 16,17,18,19,20, 21,22,23,24,25]
# 26 AP : 1 if yes, 0 if no
# 27:20026 Sample points for LED
# 20027:40027 Sample points for ephys recording.

ephysStart = 20027
ephysEnd   = 40027

def analyze( df, GABAzineFlag = 0 ):
    print( "Unique patterns: ", np.unique( df["patternID"] ) )
    print( "Unique numSquares: ", np.unique( df["numSq"] ) )
    print( "Unique freqs: ", np.unique( df["StimFreq"] ) )
    print( "Unique intensity: ", np.unique( df["intensity"] ) )
    print( "Unique pulseWidth: ", np.unique( df["pulseWidth"] ) )
    pattern5 = np.unique( df["patternID"][ df["numSq"] == 5] )
    pattern15 = np.unique( df["patternID"][ df["numSq"] == 15] )
    print( "5sq patterns = ", pattern5 )
    print( "15sq patterns = ", pattern15 )
    print("Unique AP values: ", np.unique( df["AP"] ))
    
    plt.figure( figsize = (10, 16 ) )
    x = [52, 53, 55]

    for i, pat in enumerate( pattern5 ):
        ax = plt.subplot( len( pattern5 ), 1, i+1 )
        p0 = df.loc[ (df["patternID"]==pat) & (df["intensity"]==100) & (df["StimFreq"] == 50) & (df["GABAzineFlag"] == GABAzineFlag ) & (df["pulseWidth"]==2) & (df["Clamp"]==0)]# & (df["AP"]==0)]
        print( "P0 shape = ", p0.shape )
        patdata = p0.iloc[:,ephysStart:ephysEnd]
        print( "patdata shape = ", patdata.shape )

        for j, p1 in patdata.iterrows():
            print( "P1 shape = ", len(p1) )
            ax.plot( np.arange( 20000 ), p1, label = j )

        patmean = patdata.mean( axis = 0 )
        ax.plot( np.arange( 20000 ), patmean, label = "mean of " + str( int(pat)) )
        print( "patmean shape = ", patmean.shape )

        ax.set_xlabel( "sample #" )
        ax.set_ylabel( "EPSP (arb units)" )
        ax.legend()

def compareGABAzine( df ):
    pattern5 = np.unique( df["patternID"][ df["numSq"] == 5] )
    pattern15 = np.unique( df["patternID"][df["patternID"]<56] )
    print(pattern15)
    plt.figure( figsize = (10, 16 ) )
    x = [52, 53, 55]

    for i, pat in enumerate( pattern5 ):
        ax = plt.subplot( len( pattern5 ), 1, i+1 )
        p0 = df.loc[ (df["patternID"]==pat) & (df["intensity"]==100) & (df["StimFreq"] == 50) & (df["GABAzineFlag"] == 0 ) & (df["pulseWidth"]==2) & (df["Clamp"]==0)]# & (df["AP"]==0)]
        patdata = p0.iloc[:,ephysStart:ephysEnd]
        patmean = patdata.mean( axis = 0 )
        ax.plot( np.arange( 20000 ), patmean, label = "Mean of " + str( int(pat)) )

        p0 = df.loc[ (df["patternID"]==pat) & (df["intensity"]==100) & (df["StimFreq"] == 50) & (df["GABAzineFlag"] == 1 ) & (df["pulseWidth"]==2) & (df["Clamp"]==0)]# & (df["AP"]==0)]
        patdata = p0.iloc[:,ephysStart:ephysEnd]
        patmean = patdata.mean( axis = 0 )
        ax.plot( np.arange( 20000 ), patmean, label = "GABAzine: mean of " + str( int(pat)) )
        ax.set_xlabel( "sample #" )
        ax.set_ylabel( "EPSP (arb units)" )
        ax.legend()

def subtract_gabazine( df ):

    # if numSq ==15:
    #     patterns = [52, 53, 55]
    # elif numSq == 5:
    #     patterns = np.unique( df["patternID"][ df["numSq"] == 5] )
    plt.figure( figsize = (10, 16 ) )
    freqs = [20,50]
    sqs = [5,15]
    k=0
    for i,f in enumerate(freqs):

        for j,sq in enumerate(sqs):
            
            ax = plt.subplot( 2,1,j+1 )
            gabaDF = df.loc[ (df["numSq"]==sq) & (df["intensity"]==100) & (df["StimFreq"] == f) & (df["GABAzineFlag"] == 1 ) & (df["pulseWidth"]==2) & (df["Clamp"]==0) & (df["AP"]==0)]
            ctrlDF = df.loc[ (df["numSq"]==sq) & (df["intensity"]==100) & (df["StimFreq"] == f) & (df["GABAzineFlag"] == 0 ) & (df["pulseWidth"]==2) & (df["Clamp"]==0) & (df["AP"]==0)]
            
            gabaTrials   = gabaDF.iloc[:,ephysStart:ephysEnd]
            ctrlTrials   = ctrlDF.iloc[:,ephysStart:ephysEnd]

            meanGaba   = gabaTrials.mean( axis = 0 )
            meanCtrl   = ctrlTrials.mean( axis = 0 )

            gabaDiff   = meanGaba - meanCtrl
        
            labal = "Gaba-Ctrl for " + str(int(f)) + "Hz" + str(int(sq)) +"Sq"
            ax.plot( np.linspace(0,1000,20000), gabaDiff, label =  labal)
            # ax.plot( np.linspace(0,1000,20000), i+j*np.linspace(0,1000,20000), label =  labal)
            ax.set_xlabel( "Time (ms)" )
            ax.set_ylabel( "EPSP (arb units)" )
            ax.legend()
    # figFile = "Gaba-ctrl-diff_"+str(freq)+'Hz_'+str(numSq)+"sq_withAP.png"
    # plt.savefig(figFile)



def main():
    parser = argparse.ArgumentParser( description = "This is a program for analyzing a ephys data stored in hdf5 format" )
    parser.add_argument( "-f", "--filename", type = str, help = "Required: Name of hdf5 file. ", default = "../cell5291_trainingSet.h5" )
    args = parser.parse_args()

    t0 = time.time()
    with h5py.File( args.filename, "r") as f:
        print("Keys:", f.keys())
        print("data:", f['default'] )
        df = pd.DataFrame( f['default'] )
        df.rename( columns = {0:"StimFreq", 1:"numSq", 2: "intensity", 3: "pulseWidth", 4: "MeanBaseline", 5: "ClampingPotl", 6:"Clamp", 7: "GABAzineFlag", 8:"InputRes", 9:"Ra", 10:"patternID",27:"AP"}, inplace = True )
        # analyze( df )
        # compareGABAzine( df )
        # subtract_gabazine(df)
        subtract_gabazine(df)

        plt.show()
    return df
    #p2data = pd.read_hdf(args.filename )
    #return p2data

if __name__ == '__main__':
    main()

