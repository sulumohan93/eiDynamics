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
# 0  Stim Freq
# 1  numSquares
# 2  intensity
# 3  pulse width
# 4  clamp potential
# 5  meanBaseline
# 6  E or I
# 7  Gabazine
# 8  IR
# 9  Ra
# 10 pattern ID
# 11:26 coords of spots
# 27:20026 Sample points for LED
# 20027:40027 Sample points for ephys recording.

ephysStart = 20026
ephysEnd   = 40026

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

    plt.figure( figsize = (10, 16 ) )

    for i, pat in enumerate( pattern5 ):
        ax = plt.subplot( len( pattern5 ), 1, i+1 )
        p0 = df.loc[ (df["patternID"]==pat) & (df["StimFreq"] == 50) & (df["GABAzineFlag"] == GABAzineFlag ) ]
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
    pattern15 = np.unique( df["patternID"][ df["numSq"] == 15] )

    plt.figure( figsize = (10, 16 ) )

    for i, pat in enumerate( pattern5 ):
        ax = plt.subplot( len( pattern5 ), 1, i+1 )
        p0 = df.loc[ (df["patternID"]==pat) & (df["StimFreq"] == 50) & (df["GABAzineFlag"] == 0 ) ]
        patdata = p0.iloc[:,ephysStart:ephysEnd]
        patmean = patdata.mean( axis = 0 )
        ax.plot( np.arange( 20000 ), patmean, label = "Mean of " + str( int(pat)) )

        p0 = df.loc[ (df["patternID"]==pat) & (df["StimFreq"] == 50) & (df["GABAzineFlag"] == 1 ) ]
        patdata = p0.iloc[:,ephysStart:ephysEnd]
        patmean = patdata.mean( axis = 0 )
        ax.plot( np.arange( 20000 ), patmean, label = "GABAzine: mean of " + str( int(pat)) )
        ax.set_xlabel( "sample #" )
        ax.set_ylabel( "EPSP (arb units)" )
        ax.legend()


def main():
    parser = argparse.ArgumentParser( description = "This is a program for analyzing a ephys data stored in hdf5 format" )
    parser.add_argument( "-f", "--filename", type = str, help = "Required: Name of hdf5 file. ", default = "../cell5291_trainingSet.h5" )
    args = parser.parse_args()

    t0 = time.time()
    with h5py.File( args.filename, "r") as f:
        print("Keys:", f.keys())
        print("data:", f['default'] )
        df = pd.DataFrame( f['default'] )
        df.rename( columns = {0:"StimFreq", 1:"numSq", 2: "intensity", 3: "pulseWidth", 4: "MeanBaseline", 5: "ClampingPotl", 6:"EorI", 7: "GABAzineFlag", 8:"InputRes", 9:"Ra", 10:"patternID"}, inplace = True )
        analyze( df )
        compareGABAzine( df )
        plt.show()
    return df
    #p2data = pd.read_hdf(args.filename )
    #return p2data

if __name__ == '__main__':
    main()

