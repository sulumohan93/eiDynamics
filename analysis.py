"""
Created on Friday 12th March 2021

@author: Aditya Asopa, Bhalla Lab, NCBS
"""

import sys
import os
import imp

from eiDynamics             import ePhysClasses
from eiDynamics.errors      import *
from eiDynamics.plotMaker   import plotMaker


def main(inputFile, saveTrial=False, makePlots=False):
    datafile            = os.path.realpath(inputFile)
    exptDir             = os.path.dirname(datafile)
    exptFile            = os.path.basename(datafile)
    fileID              = exptFile[:15]
    parameterFile       = exptDir + "\\" + fileID + "_ExperimentParameters.py"
    parameterFile       = os.path.abspath(parameterFile)

    # Import Experiment Variables
    try:
        print("Looking for experiment parameters locally")
        exptParams      = imp.load_source('ExptParams', parameterFile)
        if not exptParams.datafile == exptFile:
            raise FileMismatchError()
        # assert(eP.datafile == exptFile), "Datafile mismatch!\n"
        # "Make sure the data file in experiment parameters is same as recording file supplied."
        print('Experiment parameters loaded from: ', parameterFile)
    except FileMismatchError as err:
        print(err)
        print("No special instructions, using default variables.")
        import eiDynamics.ExperimentParameters_Default as exptParams
        saveTrial = False
        print('Default Experiment Parameters loaded.\n'
              'Experiment will not be added to the cell pickle file,\n'
              'only excel file of cell response will be created.')
    except Exception:
        print("Experiment Parameters error. Quitting!")
        sys.exit()

    # Import stimulation coordinates
    try:
        coordfileName = exptParams.polygonProtocol
        coordfile = os.path.join(os.getcwd(), "polygonProtocols", coordfileName)
        os.path.isfile(coordfile)
        print('Local coord file loaded from: ', coordfile)
    except FileNotFoundError:
        print('No coord file found, probably there isn\'t one')
        coordfile = ''
    except Exception as err:
        print(err)
        coordfile = ''

    # Recording cell data and analyses
    cellFile = exptDir + "\\" + exptParams.cellID + ".pkl"
    cellFile_csv = exptDir + "\\" + exptParams.cellID + ".xlsx"
    try:
        cell = ePhysClasses.Neuron.loadCell(cellFile)
        print('Loading local cell data')
    except FileNotFoundError:
        print('Local cell data not found, creating new cell.')
        cell = ePhysClasses.Neuron(exptParams)
    except Exception as err:
        print(err)

    cell.createExperiment(datafile=datafile, coordfile=coordfile, exptParams=exptParams)

    # saving
    if saveTrial:
        ePhysClasses.Neuron.saveCell(cell, cellFile)
        cell.response.to_excel(cellFile_csv)  # save a csv of responses
    else:
        cell.response.to_excel(exptDir + "\\" + exptParams.cellID + "_temp.xlsx")

    # Plots
    if makePlots:
        plotMaker(cellFile, ploty="peakRes", gridRow="numSquares", plotby="EI", clipSpikes=True)
        plotMaker(cellFile, ploty="peakRes", gridRow="numSquares", plotby="PatternID", clipSpikes=True)
        plotMaker(cellFile, ploty="peakRes", gridRow="PatternID", plotby="Repeat", clipSpikes=True)

        plotMaker(cellFile, ploty="peakTime", gridRow="numSquares", plotby="EI", clipSpikes=True)
        plotMaker(cellFile, ploty="peakTime", gridRow="numSquares", plotby="PatternID", clipSpikes=True)
        plotMaker(cellFile, ploty="peakTime", gridRow="PatternID", plotby="Repeat", clipSpikes=True)

    return cellFile


if __name__ == "__main__":
    main(sys.argv[1])
else:
    print("Programme accessed from outside")
