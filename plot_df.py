import matplotlib.pyplot as plt
import numpy as np
# from scipy.signal import find_peaks, peak_widths
# from scipy.signal import butter, bessel, decimate, sosfiltfilt
# from scipy.optimize import curve_fit
# import os
# import sys
# import imp
import pandas as pd
# import h5py
import seaborn as sns

# from eidynamics import ephys_classes
from eidynamics.utils               import delayed_alpha_function,rolling_variance_baseline,filter_data,moving_average
# from eidynamics                     import pattern_index
# from allcells                       import *

excelFile = "C:\\Users\\Adity\\OneDrive\\NCBS\\Lab\\Projects\\EI_Dynamics\\AnalysisFiles\\allCells.xlsx"
df = pd.read_excel(excelFile)
df = df.iloc[:,:44]
df2 = df.loc[ (df["Clamp"]=='CC') & (df["NumSquares"]!=1) & (df["ExptType"] != 'LTMRand') &\
               (df["Intensity"] == 100) & (df["PulseWidth"] == 2) & (df["datafile"] != '2021_04_03_0004_rec.abf') &\
                 (df["datafile"] != '2021_04_03_0004_rec.abf')& (df["datafile"] != '2021_07_30_0005_rec.abf') ]#& (df["AP"]==1)]
              #                  \
                #   \
                #   #&\
                #   (df["AP"] == False)  ]'''
                  
df3 = df2.rename(columns ={ 1:"P1", 2:"P2", 3:"P3", 4:"P4", 5:"P5", 6:"P6", 7:"P7", 8:"P8",\
                            9:"PT1",10:"PT2",11:"PT3",12:"PT4",13:"PT5",14:"PT6",15:"PT7",16:"PT8",\
                            17:"A1",18:"A2",19:"A3",20:"A4",21:"A5",22:"A6",23:"A7",24:"A8"} )

df3.loc[:,["A1","A2","A3","A4","A5","A6","A7","A8"]] *= (1/20000)

print( "5 Sq patterns: " ,    np.unique( df["PatternID"][ df["NumSquares"] == 5] ))
print( "15 Sq patterns: " ,   np.unique( df["PatternID"][ df["NumSquares"] == 15] ))
print( "1 sq Unique patterns: ",   np.unique( df["PatternID"] ) )
print( "Unique numSquares: ", np.unique( df["NumSquares"] ) )
print( "Unique freqs: ",      np.unique( df["StimFreq"] ) )
print( "Unique intensity: ",  np.unique( df["Intensity"] ) )
print( "Unique pulseWidth: ", np.unique( df["PulseWidth"] ) )
print( "Unique Expt Types: ", np.unique( df["ExptType"] ) )

def plot_df_slice(df3,ploty="peak",plotby='Condition'):

    unit = df3.iloc[1,df3.columns.get_loc("Unit")]
    
    if ploty == "peak":
        vals = ["P1","P2","P3","P4","P5","P6","P7","P8"]
        valName = "Peak Response Value (" + unit + ")"
    elif ploty == "peakTime":
        vals = ["PT1","PT2","PT3","PT4","PT5","PT6","PT7","PT8"]
        valName = "Onset Delay (ms)"
    elif ploty == "auc":
        vals = ["A1","A2","A3","A4","A5","A6","A7","A8"]
        valName = "AUC (mV-s)"

    # Separate the identifier variables from value variables by melting the dataframe
    respMelt = pd.melt(df3,id_vars=["Repeat","StimFreq","EI","PatternID","NumSquares","Condition"],value_vars=vals,var_name='PulseIndex', value_name=valName)
    
    grid = sns.FacetGrid(respMelt, row="NumSquares", col="StimFreq", hue=plotby, palette="viridis", legend_out=True)
    grid.map(sns.lineplot,"PulseIndex",valName,marker="o")
    # plt.ylim(bottom=0,top=200)
    grid.add_legend()
    '''
    sqs = np.unique(df3["NumSquares"])
    conds = np.unique(df3["Condition"])
    freqs = np.unique(df3["StimFreq"])`

    fig,ax = plt.subplots(2,4,sharex=True)
    fig.tight_layout()

    for i,sq in enumerate(sqs):
        for j,freq in enumerate(freqs):
            for k,cond in enumerate(conds):
                p0 = df3.loc[(df["NumSquares"]==sq) & (df["StimFreq"]==freq) & (df["Condition"]==cond)]
                
                patdata = p0.loc[:,["A1","A2","A3","A4","A5","A6","A7","A8"]]
                patmean = patdata.mean( axis = 0 )
                
                if cond=='Control':
                    for m, p1 in patdata.iterrows():
                        ax[i,j].plot( np.linspace(1,8,8), p1, color='#D5E0E8',alpha=1)
                    ctrl = ax[i,j].plot( np.linspace(1,8,8), patmean, color="#31688E")
                    ax[i,j].set_xlabel("Time (ms)") if i==1 else None
                    ax[i,j].set_ylabel( "Control" ) if j==0 else None
                    # ax[i,j].set_ylim([0,0.12])
                    # ax[i+1,j].legend(loc="upper right")
                    # ax[i,j].set_title((str(int(freq))+" Hz"))

                elif cond=='Gabazine':
                    ax2 = ax[i,j].twinx()
                    for m, p1 in patdata.iterrows():                        
                        ax2.plot( np.linspace(1,8,8), p1, color='#D6F0E4',alpha=1 )
                    gaba = ax2.plot( np.linspace(1,8,8), patmean, color="#35B779")
                    # ax2.set_ylim([0,1.2])
                    # ax[1,j].set_xlabel("Time (ms)") if i==1 else None
                    ax2.set_ylabel( "Gabazine" ) if j==3 else None
                    # ax[i,j].legend(loc="upper right")
                    # ax[i,j].set_title((str(int(freq))+" Hz"))
    fig.legend([ctrl,gaba],labels=['Control','Gabazine'],loc='right')
    '''

    return df3,grid




# def plot_IR(parsedDF):
#     Ra = 1000*parsedDF['Ra']/20
#     IR = parsedDF['IR']
#     fig1 = sns.histplot(Ra,bins=1000)
#     fig1.xlim(0,5)
#     fig1.xlabel('Membrane Time Constant, Tau_m (ms)')
    
#     fig2 = sns.histplot(IR,bins=1000)
#     fig2.xlabel('Cell Input Resistance (MOhm)')

# parsedDF = plot_df_slice(df3,ploty="peak",plotby='Condition')
# grid1.set_axis_labels("Pulse Index","Peak Resonse (mV)")

parsedDF,grid2 = plot_df_slice(df3,ploty="auc",plotby="Condition")
grid2.set_axis_labels("Pulse Index","AuC of Response (mV-s)")

plt.show()
