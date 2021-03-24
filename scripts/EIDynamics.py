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
        self.properties = {} #ePhys properties
        self.response = pd.DataFrame()

    # tag: improve feature (avoid adding duplicate experiments)

    def createExperiment(self,datafile,coordfile,eP):
        data = abf2data(datafile,eP) #create a dict holding sweepwisedata
        coords = Coords(coordfile).coords # create a dict holding sweepwise coords extracted from coords object
        expt = Experiment(self,eP,data,coords)
        self.experiment.update({eP.exptType:expt})
        # self.response.update({self.exptParams.exptType:expt.analyzeExperiment()})
        return expt.analyzeExperiment()


class Experiment:
    '''All different kinds of experiments conducted on a patched
    neuron are captured by this superclass.'''

    def __init__(self,neuron,eP,data,coords=None):
        self.neuron = neuron
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
        
    def analyzeExperiment(self):

        if self.exptParams.exptType == 'sealTest':
            #Call a function to calculate access resistance from recording
            return self.sealTest()
        elif self.exptParams.exptType == 'IR':
            #Call a function to calculate cell input resistance from recording 
            return self.inputRes()
        elif 'Hz' in self.exptParams.exptType:
            #Call a function to analyze the freq dependent response
            return self.FreqResponse()

    def sealTest(self):
        # calculate access resistance from data
        return self

    def inputRes(self):
        # calculate input resistance from data
        self.neuron.properties.update({'IR':150})
        return self

    def FreqResponse(self):
        expt2df(self)         
        return self


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