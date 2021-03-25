# Libraries
import numpy as np
from abf2data import abf2data
from expt2df import expt2df
import pandas as pd

class Neuron:
    '''All properties and behaviours of a recorded neuron
    are captured in this class'''

    def __init__(self, eP):
        self.animalID = eP.animalID
        self.dateofBirth = eP.dateofBirth
        self.dateofExpt = eP.dateofExpt
        self.exptLocation = eP.location
        self.experiment = {} #Experiment class object
        self.properties = {} #ePhys properties, derived in order: expt -> response -> properties
        self.response = pd.DataFrame()

    # tag: improve feature (avoid adding duplicate experiments)

    def createExperiment(self,datafile,coordfile,exptParams):
        data = abf2data(datafile,exptParams) #create a dict holding sweepwisedata
        coords = Coords(coordfile).coords # create a dict holding sweepwise coords extracted from coords object
        expt = Experiment(self,exptParams,data,coords)
        # tag: improve feature (add multiple experiments of same exptType in the neuron.experiment dict)
        self.experiment.update({exptParams.exptType:expt})
        expt.analyzeExperiment(self)


class Experiment:
    '''All different kinds of experiments conducted on a patched
    neuron are captured by this superclass.'''

    def __init__(self,neuron,eP,data,coords=None):
        # self.neuron = neuron # tag: removed feature (recursive reference to the parent neuron object)
        self.exptParams = eP
        self.recordingData = data
        self.stimCoords = coords
        self.numSweeps = len(self.recordingData.keys())
        self.sweepIndex = 0  #start of the iterator over sweeps
        self.Flags = {"IRFlag","APFlag","NoisyBaselineFlag"}
    
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
            return self.inputRes()
        elif 'Hz' in self.exptParams.exptType:
            #Call a function to analyze the freq dependent response
            return self.FreqResponse(neuron)

    def sealTest(self):
        # calculate access resistance from data
        return self

    def inputRes(self):
        # calculate input resistance from data
        self.neuron.properties.update({'IR':150})
        return self
    # tag: improve feature (do away with so many nested functions)
    def FreqResponse(self,neuron):
        # there can be multiple kinds of freq based responses.
        expt2df(self,neuron) # this function takes expt and convert to a dataframe
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