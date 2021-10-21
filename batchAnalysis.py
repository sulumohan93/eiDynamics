import os
import sys

import analysis
from eidynamics.plotmaker           import make_plots
from allcells                       import *


def batchAnalysis(cellDirectory):
    fileExt = "rec.abf"
    recFiles = [os.path.join(cellDirectory, recFile) for recFile in os.listdir(cellDirectory) if recFile.endswith(fileExt)]

    for recFile in recFiles:
        print("+++++++++++++++++++++++++++++++++++++++++++")
        print("Now analysing: ",recFile)
        cellFile = analysis.main(recFile,saveTrial=True)

    return cellFile


def batchPlot(cellFile):
    make_plots(cellFile,ploty="peakRes",gridRow="numSquares",plotby="EI",clipSpikes=True)
    make_plots(cellFile,ploty="peakRes",gridRow="numSquares",plotby="PatternID",clipSpikes=True)
    make_plots(cellFile,ploty="peakRes",gridRow="PatternID",plotby="Repeat",clipSpikes=True)

    make_plots(cellFile,ploty="peakTime",gridRow="numSquares",plotby="EI",clipSpikes=True)
    make_plots(cellFile,ploty="peakTime",gridRow="numSquares",plotby="PatternID",clipSpikes=True)
    make_plots(cellFile,ploty="peakTime",gridRow="PatternID",plotby="Repeat",clipSpikes=True)


def metaAnalysis(cellFile):
    pass


def metaPlot(allCellsFile):
    pass


if __name__ == "__main__":
    if "analyse" in sys.argv:
        print("Analysing recordings...")
        for cellDirectory in allCells:
            print("Now analysing cell from: ", cellDirectory)
            cf = batchAnalysis(cellDirectory)
            print(cf)
            batchPlot(cf)
    elif "codetest" in sys.argv:
        print("Checking if analysis pipline is working...")
        for cellDirectory in testCells:
            print("Now analysing cell from: ", cellDirectory)
            cf = batchAnalysis((cloudDataPath+cellDirectory))
            print(cf)
            batchPlot(cf)
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
                print("Now analysing cell from: ", cellDirectory)
                cf = batchAnalysis(cellDirectory)
                print(cf)
                batchPlot(cf)
