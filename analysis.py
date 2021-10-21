"""
Created on Friday 12th March 2021

@author: Aditya Asopa, Bhalla Lab, NCBS
"""

import sys
import os
import imp

from eidynamics             import ephys_classes
from eidynamics.errors      import *
from eidynamics.plotmaker   import make_plots


def main(inputFile, saveTrial=False, makePlots=False):
    datafile      = os.path.realpath(inputFile)
    exptDir       = os.path.dirname(datafile)
    exptFile      = os.path.basename(datafile)
    fileID        = exptFile[:15]
    parameterFile = exptDir + "\\" + fileID + "_experiment_parameters.py"
    parameterFile = os.path.abspath(parameterFile)

    # Import Experiment Variables
    try:
        print("Looking for experiment parameters locally")
        exptParams = imp.load_source('ExptParams', parameterFile)
        if not exptParams.datafile == exptFile:
            raise FileMismatchError()
        print('Experiment parameters loaded from: ', parameterFile)
    except (FileMismatchError,FileNotFoundError) as err:
        print(err)
        print("No special instructions, using default variables.")
        import eidynamics.experiment_parameters_default as exptParams
        saveTrial  = False
        print('Default Experiment Parameters loaded.\n'
              'Experiment will not be added to the cell pickle file,\n'
              'only excel file of cell response will be created.')
    except Exception as err:
        print(err)
        print("Experiment Parameters error. Quitting!")
        sys.exit()

    # Import stimulation coordinates
    try:
        coordfileName   = exptParams.polygonProtocol
        if not coordfileName:
            raise FileNotFoundError
        coordfile       = os.path.join(os.getcwd(), "polygonProtocols", coordfileName)
        os.path.isfile(coordfile)
        print('Local coord file loaded from: ', coordfile)
    except FileNotFoundError:
        print('No coord file found, probably there isn\'t one')
        coordfile       = ''
    except Exception as err:
        print(err)
        coordfile       = ''

    # Recording cell data and analyses
    cellFile            = exptDir + "\\" + str(exptParams.cellID) + ".pkl"
    cellFile_csv        = exptDir + "\\" + str(exptParams.cellID) + ".xlsx"
    try:
        cell            = ephys_classes.Neuron.loadCell(cellFile)
        print('Loading local cell data')
    except FileNotFoundError as err:
        print('Creating new cell.')
        cell            = ephys_classes.Neuron(exptParams)
    except Exception as err:
        print('Creating new cell.')
        cell            = ephys_classes.Neuron(exptParams)

    cell.addExperiment(datafile=datafile, coordfile=coordfile, exptParams=exptParams)

    # saving
    if saveTrial:
        ephys_classes.Neuron.saveCell(cell, cellFile)
        cell.response.to_excel(cellFile_csv)
    else:
        cell.response.to_excel(exptDir + "\\" + exptParams.cellID + "_temp.xlsx")

    # Plots
    if makePlots:
        make_plots(cellFile, ploty="peakRes", gridRow="numSquares", plotby="EI",         clipSpikes=True)
        make_plots(cellFile, ploty="peakRes", gridRow="numSquares", plotby="PatternID",  clipSpikes=True)
        make_plots(cellFile, ploty="peakRes", gridRow="PatternID",  plotby="Repeat",     clipSpikes=True)

        make_plots(cellFile, ploty="peakTime", gridRow="numSquares", plotby="EI",        clipSpikes=True)
        make_plots(cellFile, ploty="peakTime", gridRow="numSquares", plotby="PatternID", clipSpikes=True)
        make_plots(cellFile, ploty="peakTime", gridRow="PatternID",  plotby="Repeat",    clipSpikes=True)

    return cellFile

if __name__ == "__main__":
    main(sys.argv[1])
else:
    print("Programme accessed from outside")