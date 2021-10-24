import os
import sys

import analysis
from eidynamics.plotmaker   import dataframe_to_plots
from eidynamics             import ephys_classes
from allcells               import *


def batch_analysis(cellDirectory,add_cell_to_database=False, export_training_set=False, save_experiment_to_cell=False,save_plots=False):
    _,savedCellFile = analysis.create_cell(cellDirectory,
                                        add_cell_to_database = add_cell_to_database,
                                        export_training_set = export_training_set,
                                        save_experiment_to_cell = save_experiment_to_cell,
                                        save_plots = save_plots)

    return savedCellFile

def batch_plot(cellFile):
    try:
        dataframe_to_plots(cellFile, ploty="PeakRes",  gridRow="NumSquares", plotby="EI",        clipSpikes=True)
        dataframe_to_plots(cellFile, ploty="PeakRes",  gridRow="NumSquares", plotby="PatternID", clipSpikes=True)
        dataframe_to_plots(cellFile, ploty="PeakRes",  gridRow="PatternID",  plotby="Repeat",    clipSpikes=True)

        dataframe_to_plots(cellFile, ploty="PeakTime", gridRow="NumSquares", plotby="EI",        clipSpikes=True)
        dataframe_to_plots(cellFile, ploty="PeakTime", gridRow="NumSquares", plotby="PatternID", clipSpikes=True)
        dataframe_to_plots(cellFile, ploty="PeakTime", gridRow="PatternID",  plotby="Repeat",    clipSpikes=True)
    except:
        pass

def meta_analysis(cellFile):
    pass

def meta_plot(allCellsFile):
    pass

if __name__ == "__main__":
    if "analyse" in sys.argv:
        print("Analysing all catalogued cells recordings...")
        for cellDirectory in allCells:
            savedCellFile = batch_analysis((projectPathRoot+cellDirectory),add_cell_to_database=True, export_training_set=True, save_experiment_to_cell=True,save_plots=True)
            print("Data saved in cell file: ",savedCellFile)
            batch_plot(savedCellFile)
    elif "codetest" in sys.argv:
        print("Checking if analysis pipline is working...")
        for cellDirectory in testCells:
            savedCellFile = batch_analysis((projectPathRoot+cellDirectory),add_cell_to_database=False, export_training_set=True, save_experiment_to_cell=True,save_plots=True)
            print(savedCellFile)
            # batchPlot(cf)
        print('All Tests Passed!')
    else:
        for cellDirectory in allCells:
            try:
                print("Looking for analysed cell pickles to plot directly from...")
                cf = [os.path.join(cellDirectory, pickleFile) for pickleFile in os.listdir(cellDirectory) if pickleFile.endswith("cell.pkl")]
                print("Plotting from: ",cf[0])
                batch_plot(cf[0])
            except FileNotFoundError:
                print("Cell pickle not found. Beginning analysis.")
                savedCellFile = batch_analysis((projectPathRoot+cellDirectory),add_cell_to_database=True, export_training_set=True, save_experiment_to_cell=True,save_plots=True)
                print("Data saved in cell file: ",savedCellFile)
                batch_plot(savedCellFile)
