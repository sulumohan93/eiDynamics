"""
Created on Friday 12th March 2021

@author: Aditya Asopa, Bhalla Lab, NCBS
"""
## Import libraries
import sys
import os
import EIDynamics
import imp

#Get the path
datafile = os.path.realpath(sys.argv[1])
exptDir = os.path.dirname(datafile)
exptFile = os.path.basename(datafile)
fileID = exptFile.split('_rec')[0]

# Import Experiment Variables
try:
    print ("Looking for experiment parameters locally")
    exptPath = exptDir + "\\" + fileID + "_ExperimentParameters.py"
    eP = imp.load_source('ExptParams',exptPath)
    print('Local parameters loaded')
except:
    print ("No special instructions, using default variables.")
    try:
        import ExperimentParameters_Default as eP
        print('Default parameters loaded, Check parameters manually')
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


cell = EIDynamics.Neuron(date=eP.dateofExpt,location=eP.location,ID=eP.animalID)
cell.createExperiment('FreqSweep','control',datafile=datafile,coordfile=coordfile)
