# Libraries
import numpy as np
import pandas as pd

from eiDynamics.abf2data import abf2data
from eiDynamics.expt2df import expt2df
from eiDynamics.ePhysFunctions import IRcalc


class Neuron:
    '''All properties and behaviours of a recorded neuron
    are captured in this class'''

    def __init__(self, eP):
        self.animalID = eP.animalID
        self.dateofBirth = eP.dateofBirth
        self.dateofExpt = eP.dateofExpt
        self.exptLocation = eP.location
        
        # derived in order: neuron.expt -> neuron.response -> neuron.properties
        self.experiment = {} #Experiment class object, a dict holding experiment objects as values and exptType as keys
        self.response = pd.DataFrame() # a pandas dataframe container to hold the table of responses to all experiments
        self.properties = {} #ePhys properties, derived from analyzing and stats on the response dataframe
        

    # tag: improve feature (avoid adding duplicate experiments)

    def createExperiment(self,datafile,coordfile,exptParams):
        data = abf2data(datafile,exptParams) #create a dict holding sweepwisedata
        coords = Coords(coordfile).coords # create a dict holding sweepwise coords extracted from coords object
        expt = Experiment(self,exptParams,data,coords) # create an object of experiment class with the recording data and coords
        # tag: improve feature (add multiple experiments of same exptType in the neuron.experiment dict)
        self.experiment.update({exptParams.exptType:expt}) #exptTypes = ['GapFree','IR','CurrentStep','20Hz','30Hz','40Hz','50Hz','100Hz']
        expt.analyzeExperiment(self) # send the experiment object for analysis and analysed data saved in Neuron.resonse dataframe


class Experiment:
    '''All different kinds of experiments conducted on a patched
    neuron are captured by this superclass.'''

    def __init__(self,eP,data,coords=None):
        self.exptParams = eP
        self.recordingData = data[0]
        self.meanBaseline = data[1]
        self.stimCoords = coords
        self.numSweeps = len(self.recordingData.keys())
        self.sweepIndex = 0  #start of the iterator over sweeps
        self.Flags = {"IRFlag","APFlag","NoisyBaselineFlag","RaChangeFlag"}
        self.Flags["NoisyBaselineFlag"] = data[2]
    
    def __iter__(self):
        return self

    def __next__(self):
        if self.sweepIndex >= self.numSweeps:
            raise StopIteration
        currentSweepIndex = self.sweepIndex
        self.sweepIndex += 1
        return self.recordingData[currentSweepIndex]
        
    def analyzeExperiment(self,neuron):

        if self.exptParams.exptType == 'sealTest':
            #Call a function to calculate access resistance from recording
            return self.sealTest()
        elif self.exptParams.exptType == 'IR':
            #Call a function to calculate cell input resistance from recording 
            return self.inputRes(self,neuron)
        elif 'Hz' in self.exptParams.exptType:
            #Call a function to analyze the freq dependent response
            return self.FreqResponse(neuron)

    def sealTest(self):
        # calculate access resistance from data
        return self

    def inputRes(self,neuron):
        # calculate input resistance from data
        neuron.properties.update({'IR':np.mean(IRcalc(self.recordingData,np.arange[1,200],np.arange[500,700]))})
        return self

    # tag: improve feature (do away with so many nested functions)
    def FreqResponse(self,neuron):
        # there can be multiple kinds of freq based responses.
        expt2df(self,neuron) # this function takes expt and converts to a dataframe of responses
        return self

# currently class "Coords" is not being used
# except in generating a dict containing sweep wise coords
class Coords:
    '''A Sweep wise record of coordinates of all the square points
    illuminated in the experiment'''

    def __init__(self,coordFile):
        self.gridSize = []
        self.numSweeps = []
        self.coords = self.coordParser(coordFile)

    def coordParser(self,coordFile):
        coords ={}
        import csv
        with open(coordFile,'r') as cf:
            c = csv.reader(cf,delimiter=" ")
            for lines in c:
                intline = []
                for i in lines:
                    intline.append(int(i))
                coords[intline[0]]= (intline[3:])
        self.gridSize = [intline[1],intline[2]]
        self.numSweeps = len(coords)
        return coords

    def __iter__(self):
        return self

    def __next__(self):
        self.sweepIndex = 0 #start of the iterator over sweeps
        if self.sweepIndex >= self.numSweeps:
            raise StopIteration
        currentSweepIndex = self.sweepIndex
        self.sweepIndex += 1
        return self.coords[currentSweepIndex] 