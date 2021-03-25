"""
Created on Friday 12th March 2021

@author: Aditya Asopa, Bhalla Lab, NCBS
"""
## Import libraries
import sys
import os
import EIDynamics
import imp
import pandas as pd
import pickle
from plotMaker import plotMaker

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
    print('Local parameters loaded')
except:
    print ("No special instructions, using default variables.")
    try:
        import ExperimentParameters_Default as eP
    except:
        print ("No analysis variable found!")

# importing stimulation coordinates
try:
    coordfile = exptDir + "\\" + fileID + "_coords.txt"
    os.path.isfile(coordfile)
    print('Loading local coord file')  
except:
    print('No coord file found, probably there isn\'t one')
    coordfile = ''

# Recording cell data and analyses
try:
    cellFile = exptDir + "\\" + "cell.pkl"
    print('Loading local cell data')
    cell = pickle.load(cellFile)
except:
    print('Local cell data not found, creating new cell')
    cell = EIDynamics.Neuron(eP)

cell.createExperiment(datafile=datafile,coordfile=coordfile,exptParams=eP)

# saving 
with open(cellFile,"wb") as f:
    pickle.dump(cell.response, f)  

# Plots
plotMaker(cellFile)