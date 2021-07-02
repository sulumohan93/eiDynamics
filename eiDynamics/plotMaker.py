import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pickle
import os
sns.set_context("paper")


# tag: improve feature (remove hardcoded variables, fields, and values)

def plotMaker(cellpickleFile,ploty="peakRes",gridRow="numSquares",gridColumn="StimFreq",plotby="EI"):
    with open(cellpickleFile,'rb') as fin:
        x = pickle.load(fin)
    resp = x.response

    # load file
    # resp = cell.response
    resp1 = resp.copy()

    # tag: improve feature (to permanently remove hard coding the indices of calculated values,
    # use of tiers in pandas dataframe needs to be implemented)
    if ploty == "peakRes":
        vals = np.arange(1,9)
        valName = "PSC Value (mV)"
    elif ploty == "onsetDelay":
        vals = np.arange(9,17)
        valName = "Onset Delay (ms)"
    elif ploty == "peakTime":
        vals = np.arange(9,17)
        valName = "Time of Peak (ms)"
    else:
        print("Don't know what to plot. Plotting peak responses.")
        vals = np.arange(1,9)
        valName = "PSC Value (mV)"

    # Separate the identifier variables from valua variables by melting the dataframe
    respMelt = pd.melt(resp1,id_vars=["Repeat",gridRow,gridColumn,plotby],value_vars=vals,var_name='pulseIndex', value_name=valName)
    plt.figure()

    ## Initialize a grid of plots with an axis each for different fields
    grid = sns.FacetGrid(respMelt, col=gridColumn, row=gridRow, hue=plotby,palette="viridis")

    # Draw a scatter plot to show the PSP/PSC amplitude
    grid.map(plt.scatter,"pulseIndex",valName,marker="o")
    plt.legend()

    # # Adjust the tick positions and labels
    grid.set(xlim=(vals[0]-1,vals[-1]+1))
    grid.set(ylim=(-200,400))

    # Save and show figure
    exptDir = os.path.dirname(cellpickleFile)
    imageFile = exptDir + "\\" + "plot_" + ploty + "-vs-" + plotby + ".png"
    plt.savefig(imageFile)