import numpy as np
import sys

def gridSizeCalc(sqSize,objMag):
    
    gridSize = np.array([1,1])

    frameSize = (1.0/objMag)*np.array([12960,6912])
    print('frame Size is (um):', frameSize)

    gridSize[0] = frameSize[0]/sqSize[0]
    gridSize[1] = frameSize[1]/sqSize[1]
        
    print("A grid of {} x {} squares will create squares of required {} x {} µm with an aspect ratio of {}".format(gridSize[0],gridSize[1],sqSize[0],sqSize[1],sqSize[0]/sqSize[1]))
    print('Nearest grid Size option is...')
    print('A grid of {} squares x {} squares'.format(int(np.ceil(gridSize[0])),int(np.ceil(gridSize[1]))))

    squareSizeCalc(np.ceil(gridSize),objMag)

def squareSizeCalc(gridSize,objMag):
    '''Pass two values as the arguments for the file: [gridSizeX, gridSizeY], objectiveMag
    command line syntax should look like:  [24 24] 40'''     
    squareSize_1x = np.array([12960,6912])*(1/objMag)
    ss = np.array([1,1])

    if len(gridSize) == 2:
        ss[0] = squareSize_1x[0]/gridSize[0]
        ss[1] = squareSize_1x[1]/gridSize[1]
    else:
        ss = squareSize_1x/gridSize

    print('Polygon Square will be {} x {} µm with an aspect ratio of {}.'.format(ss[0],ss[1],ss[0]/ss[1]))
    return ss