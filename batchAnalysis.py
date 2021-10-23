import os
import sys

import analysis
from eidynamics.plotmaker   import make_plots
from eidynamics             import ephys_classes
from allcells               import *


def batchAnalysis(cellDirectory,add_cell_to_database=False):
    print("++++++++++| Analyzing New Cell from: {} |++++++++++".format(cellDirectory))
    try:
        fileExt = "rec.abf"
        recFiles = [os.path.join(cellDirectory, recFile) for recFile in os.listdir(cellDirectory) if recFile.endswith(fileExt)]

        for recFile in recFiles:
            
            print("Now analysing: ",recFile)
            cellFile = analysis.main(recFile,saveTrial=True)

        if add_cell_to_database:
            ephys_classes.Neuron.addCell2db(cellFile)
        print("Saving traces for training")
        ephys_classes.Neuron.save_training_set(cellFile)
        
        return cellFile
    except:
        pass


def batchPlot(cellFile):
    try:
            
        make_plots(cellFile, ploty="PeakRes",  gridRow="NumSquares", plotby="EI",        clipSpikes=True)
        make_plots(cellFile, ploty="PeakRes",  gridRow="NumSquares", plotby="PatternID", clipSpikes=True)
        make_plots(cellFile, ploty="PeakRes",  gridRow="PatternID",  plotby="Repeat",    clipSpikes=True)

        make_plots(cellFile, ploty="PeakTime", gridRow="NumSquares", plotby="EI",        clipSpikes=True)
        make_plots(cellFile, ploty="PeakTime", gridRow="NumSquares", plotby="PatternID", clipSpikes=True)
        make_plots(cellFile, ploty="PeakTime", gridRow="PatternID",  plotby="Repeat",    clipSpikes=True)
    except:
        pass

def metaAnalysis(cellFile):
    pass


def metaPlot(allCellsFile):
    pass


if __name__ == "__main__":
    if "analyse" in sys.argv:
        print("Analysing recordings...")
        for cellDirectory in allCells:
            cf = batchAnalysis((projectPathRoot+cellDirectory),add_cell_to_database=True)
            print("Data saved in cell file: ",cf)
            batchPlot(cf)
    elif "codetest" in sys.argv:
        print("Checking if analysis pipline is working...")
        for cellDirectory in testCells:
            cf = batchAnalysis((projectPathRoot+cellDirectory),add_cell_to_database=True)
            print(cf)
            # batchPlot(cf)
            print('All Tests Passed!')
    else:
        for cellDirectory in allCells:
            try:
                print("Looking for analysed cell pickles to plot directly from")
                cf = [os.path.join(cellDirectory, pickleFile) for pickleFile in os.listdir(cellDirectory) if pickleFile.endswith("cell.pkl")]
                print("Plotting from: ",cf[0])
                batchPlot(cf[0])
            except FileNotFoundError:
                print("Cell pickle not found. Beginning analysis.")
                cf = batchAnalysis(cellDirectory)
                print(cf)
                batchPlot(cf)
