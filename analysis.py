"""
Created on Friday 12th March 2021

@author: Aditya Asopa, Bhalla Lab, NCBS
"""

import sys
import os
import pathlib
import imp

from eidynamics             import ephys_classes
from eidynamics.errors      import *
from eidynamics.plot_maker   import dataframe_to_plots

def create_cell(cellDirectory, add_cell_to_database=False, export_training_set=False, save_experiment_to_cell=False,save_plots=True):
    cellDirectory = pathlib.Path(cellDirectory)
    print(120*"-","\nAnalyzing New Cell from: ",cellDirectory)
    try:
        fileExt = "rec.abf"
        recFiles = [os.path.join(cellDirectory, recFile) for recFile in os.listdir(cellDirectory) if recFile.endswith(fileExt)]
        recFiles = list(cellDirectory.glob('*'+fileExt))

        for recFile in recFiles:
            print("Now analysing: ",recFile.name)
            # try:
            cell,cellFile = main(recFile,save_experiment_to_cell=save_experiment_to_cell, show_plots=False)
            # except:
                # pass
            # saving
        
        cell.generate_expected_traces()

        if add_cell_to_database:
            cell.addCell2db()

        if export_training_set:
            print("Saving traces for training")
            cell.save_training_set(cellDirectory)

        if save_experiment_to_cell:
            cellFile            = cellDirectory / str(str(cell.cellID) + ".pkl" )
            cellFile_csv        = cellDirectory / str(str(cell.cellID) + ".xlsx")
            ephys_classes.Neuron.saveCell(cell, cellFile)
            cell.response.to_excel(cellFile_csv)
        else:
            cell.response.to_excel(cellDirectory / str(str(cell.cellID) + "_temp.xlsx") )
            
    except UnboundLocalError as err:
        print("Check if there are '_rec' labeled .abf files in the directory.")

    # Plots
    if save_plots:        
        dataframe_to_plots(cellFile, ploty="PeakRes",  gridRow="NumSquares", plotby="EI",        clipSpikes=True)
        dataframe_to_plots(cellFile, ploty="PeakRes",  gridRow="NumSquares", plotby="PatternID", clipSpikes=True)
        dataframe_to_plots(cellFile, ploty="PeakRes",  gridRow="PatternID",  plotby="Repeat",    clipSpikes=True)

        dataframe_to_plots(cellFile, ploty="PeakTime", gridRow="NumSquares", plotby="EI",        clipSpikes=True)
        dataframe_to_plots(cellFile, ploty="PeakTime", gridRow="NumSquares", plotby="PatternID", clipSpikes=True)
        dataframe_to_plots(cellFile, ploty="PeakTime", gridRow="PatternID",  plotby="Repeat",    clipSpikes=True)

        dataframe_to_plots(cellFile, ploty="AUC",      gridRow="NumSquares", plotby="EI",        clipSpikes=True)
        dataframe_to_plots(cellFile, ploty="AUC",      gridRow="NumSquares", plotby="PatternID", clipSpikes=True)
        dataframe_to_plots(cellFile, ploty="AUC",      gridRow="PatternID",  plotby="Repeat",    clipSpikes=True)
        
    return cell,cellFile

    # except Exception as err:
    #     print("xxxxxxxxxxxx Error in: ",cellDirectory,"xxxxxxxxxxxxxx")
    #     print(err)
    #     pass

def main(inputFile, save_experiment_to_cell=True, show_plots=False):
    datafile      = pathlib.Path(inputFile)
    exptDir       = datafile.parent
    exptFile      = datafile.name
    fileID        = exptFile[:15]
    parameterFile = exptDir / str(fileID + "_experiment_parameters.py")
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
        coordfile       = pathlib.Path.cwd() / "polygonProtocols" / coordfileName
        # os.path.isfile(coordfile)
        print('Local coord file loaded from: ', coordfile)
    except FileNotFoundError:
        print('No coord file found, probably there isn\'t one')
        coordfile       = ''
    except Exception as err:
        print(err)
        coordfile       = ''

    # Recording cell data and analyses
    cellFile            = exptDir / str(str(exptParams.cellID) + ".pkl")
    cellFile_csv        = exptDir / str(str(exptParams.cellID) + ".xlsx")
    try:
        print('Loading local cell data')
        cell            = ephys_classes.Neuron.loadCell(cellFile)
    except FileNotFoundError as err:
        print('Creating new cell.')
        cell            = ephys_classes.Neuron(exptParams)
    except Exception as err:
        print('Creating new cell.')
        cell            = ephys_classes.Neuron(exptParams)

    cell.addExperiment(datafile=datafile, coordfile=coordfile, exptParams=exptParams)

    if save_experiment_to_cell:
        ephys_classes.Neuron.saveCell(cell, cellFile)
        cell.response.to_excel(cellFile_csv)
        # ephys_classes.Neuron.save_training_set(cellFile)
    else:
        cell.response.to_excel(exptDir + "\\" + str(cell.cellID) + "_temp.xlsx")

    return cell,cellFile

if __name__ == "__main__":
    main(sys.argv[1])
else:
    print("Programme accessed from outside")