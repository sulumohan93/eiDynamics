"""
Created on Friday 12th March 2021

@author: Aditya Asopa, Bhalla Lab, NCBS
"""
## Import libraries
import sys
import os
import imp
from eiDynamics import ePhysClasses
from eiDynamics.plotMaker import plotMaker
    
#Main function
def main(inputFile,makePlots=False):   
    datafile = os.path.realpath(inputFile)
    exptDir = os.path.dirname(datafile)
    exptFile = os.path.basename(datafile)
    fileID = exptFile.split('_rec')[0]
    epFile = exptDir + "\\" + fileID + "_ExperimentParameters.py"
    epFile = os.path.abspath(epFile)

    # Import Experiment Variables
    try:
        print ("Looking for experiment parameters locally")
        eP = imp.load_source('ExptParams',epFile)
        assert (eP.datafile == exptFile),"Datafile mismatch! Make sure the data file in experiment parameters is same as recording file supplied."
        saveTrial = True
        print('Experiment parameters loaded from: ',epFile)
    except:
        print ("No special instructions, using default variables.")
        try:
            import eiDynamics.ExperimentParameters_Default as eP
            saveTrial = False
            print('Default Experiment Parameters loaded')
        except:
            print ("Experiment Parameters error. Quitting!")
            sys.exit()

    # importing stimulation coordinates
    try:
        coordfileName = eP.polygonProtocol    
        coordfile = os.path.join(os.getcwd(),"polygonProtocols",coordfileName)
        os.path.isfile(coordfile)
        print('Local coord file loaded from: ',coordfile)
    except:
        print('No coord file found, probably there isn\'t one')
        coordfile = ''

    # Recording cell data and analyses
    cellFile = exptDir + "\\" + "cell.pkl"
    cellFile_csv = exptDir + "\\" + "cell.xlsx"
    try:
        cell = ePhysClasses.Neuron.loadCell(cellFile)
        print('Loading local cell data')
    except:
        print('Local cell data not found, creating new cell.')
        cell = ePhysClasses.Neuron(eP)

    cell.createExperiment(datafile=datafile,coordfile=coordfile,exptParams=eP)

    # saving
    if saveTrial:
        ePhysClasses.Neuron.saveCell(cell,cellFile)
        cell.response.to_excel(cellFile_csv) # save a csv of responses

    # Plots
    if makePlots:
        plotMaker(cellFile,ploty="peakRes",gridRow="numSquares",plotby="EI",clipSpikes=True)
        plotMaker(cellFile,ploty="peakRes",gridRow="numSquares",plotby="PatternID",clipSpikes=True)
        plotMaker(cellFile,ploty="peakRes",gridRow="PatternID",plotby="Repeat",clipSpikes=True)

        plotMaker(cellFile,ploty="peakTime",gridRow="numSquares",plotby="EI",clipSpikes=True)
        plotMaker(cellFile,ploty="peakTime",gridRow="numSquares",plotby="PatternID",clipSpikes=True)
        plotMaker(cellFile,ploty="peakTime",gridRow="PatternID",plotby="Repeat",clipSpikes=True)

    return cellFile

if __name__ == "__main__":
    main(sys.argv[1])
else:
    print("Programme accessed from outside")