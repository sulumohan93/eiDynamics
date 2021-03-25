import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pickle
sns.set_context("paper")

# tag: improve feature (remove hardcoded variables, fields, and values)

def plotMaker(cellpickleFile):
    resp = pd.read_pickle(cellpickleFile)



    # load file
    # resp = cell.response
    
    resp1 = resp.drop(["Sweep","Pattern","pulseWidth","Coords","IR","Intensity","PeakResponse","AP"],axis=1)
    # resp1 = resp1.loc[resp1["EI"]=='I']

    # Separate the identifier variables from valua variables by melting the dataframe
    respMelt = pd.melt(resp1,id_vars=["Repeat","numSquares","StimFreq","EI"],value_vars=[1,2,3,4,5,6,7,8],var_name='pulseIndex', value_name='PSC Value')

    ## Initialize a grid of plots with an axis each for different fields
    grid = sns.FacetGrid(respMelt, col="StimFreq", row="numSquares", hue="EI",palette="viridis")

    # Draw a line plot to show the PSP/PSC amplitude
    grid.map(plt.scatter, "pulseIndex", "PSC Value",marker=".")

    # # Adjust the tick positions and labels
    grid.set(xlim=(0,9))
    plt.legend()
    # Adjust the arrangement of the plots
    # grid.fig.tight_layout(w_pad=1)

    # '''Do it for peak minimas'''
    # # Initialize a grid of plots with an Axes for each walk
    # grid = sns.FacetGrid(respMelt, col="StimFreq", row="numSquares", hue="EI",palette="viridis")

    # # Draw a line plot to show the PSP/PSC amplitude
    # grid.map(plt.plot, "pulseIndex", "PSC Value", marker="o")

    # # # Adjust the tick positions and labels
    # grid.set(xlim=(0,9))
    # plt.legend()

