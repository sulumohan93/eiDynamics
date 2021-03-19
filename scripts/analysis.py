"""
Created on Friday 12th March 2021

@author: Aditya Asopa, Bhalla Lab, NCBS
"""
## Import libraries
import sys
import os
from abf2df import abf2df
import EIDynamics
import imp

#Get the path
inFile = os.path.abspath(sys.argv[1])
exptDir = os.path.dirname(inFile)
exptFile = os.path.basename(inFile)
fileID = exptFile.split('_rec')[0]

# access experimental parameters from recording folder
eP = imp.load_source('ExptParams',exptDir + '\\' + fileID + "_ExperimentParameters.py")

# Import Experiment Variables
try:
    print ("Looking for experiment parameters locally")
    eP = imp.load_source('ExptParams',exptDir + '\\' + fileID + "_ExperimentParameters.py")
except:
    print ("No special instructions, using default variables.")
    try:
        import ExperimentParameters_Default as eP
    except:
        print ("No analysis variable found!")

data = abf2df(inFile)
cell = EIDynamics.Neuron(date=eP.dateofExpt,location=eP.location,ID=eP.animalID)
cell.createExperiment('FreqSweep','control',data,coords='')
