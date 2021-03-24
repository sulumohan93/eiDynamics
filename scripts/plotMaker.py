import pandas as pd
import seaborn as sns
import numpy as np
import pickle
sns.set_context("paper")

def plotMaker(cellpickleFile):
    cell = pickle.load(cellpickleFile)



    # load file
    resp = cell.response
    
    resp1 = resp.drop(["Sweep","Pattern","pulseWidth","Coords","IR","Intensity","minPeakResponse","maxPeakResponse"],axis=1)

    # Separate the identifier variables from valua variables by melting the dataframe
    respMelt = pd.melt(resp1,id_vars=["Repeat","numSquares","StimFreq","EI"],value_vars=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],var_name='pulseIndex', value_name='PSC Value')

    ## Initialize a grid of plots with an axis each for different fields
    grid = sns.FacetGrid(respMelt, col="StimFreq", row="numSquares", hue="EI",palette="viridis")

    # Draw a line plot to show the PSP/PSC amplitude
    grid.map(plt.plot, "pulseIndex", "PSC Value", marker="o")

    # # Adjust the tick positions and labels
    grid.set(xlim=(7.5, 17))
    plt.legend()
    # Adjust the arrangement of the plots
    # grid.fig.tight_layout(w_pad=1)

    '''Do it for peak minimas'''
    # Initialize a grid of plots with an Axes for each walk
    grid = sns.FacetGrid(respMelt, col="StimFreq", row="numSquares", hue="EI",palette="viridis")

    # Draw a line plot to show the PSP/PSC amplitude
    grid.map(plt.plot, "pulseIndex", "PSC Value", marker="o")

    # # Adjust the tick positions and labels
    grid.set(xlim=(-0.5,7.5))
    plt.legend()

