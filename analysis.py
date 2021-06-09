"""
Created on Friday 12th March 2021

@author: Aditya Asopa, Bhalla Lab, NCBS
"""
## Import libraries
from eiDynamics import plotMaker
import sys
import os
import imp
import matplotlib.pyplot as plt
import pandas as pd
import pickle
import eiDynamics
from eiDynamics import ePhysClasses
from eiDynamics.plotMaker import plotMaker

#Get the path
datafile = os.path.realpath(sys.argv[1])
exptDir = os.path.dirname(datafile)
exptFile = os.path.basename(datafile)
fileID = exptFile.split('_rec')[0]
epFile = exptDir + "\\" + fileID + "_ExperimentParameters.py"
epFile = os.path.abspath(epFile)

# Import Experiment Variables
try:
    print ("Looking for experiment parameters locally")
    eP = imp.load_source('ExptParams',epFile)
    print('Local parameters loaded from: ',epFile)
except:
    print ("No special instructions, using default variables.")
    try:
        import eiDynamics.ExperimentParameters_Default as eP
        print('Default Experiment Parameters loaded')
    except:
        print ("No analysis variable found!")

# importing stimulation coordinates
try:
    coordfile = exptDir + "\\" + fileID + "_coords.txt"
    os.path.isfile(coordfile)
    print('Local coord file loaded from: ',coordfile)  
except:
    print('No coord file found, probably there isn\'t one')
    coordfile = ''

# Recording cell data and analyses
cellFile = exptDir + "\\" + "cell.pkl"
try:    
    print('Loading local cell data')
    cell = pickle.load(cellFile)
except:
    print('Local cell data not found, creating new cell')
    cell = ePhysClasses.Neuron(eP)

cell.createExperiment(datafile=datafile,coordfile=coordfile,exptParams=eP)

# saving 
with open(cellFile,"wb") as f:
    pickle.dump(cell.response, f)  

# Plots

plotMaker(cellFile,ploty="peakRes",plotby="EI")
plotMaker(cellFile,ploty="peakTime",plotby="EI")