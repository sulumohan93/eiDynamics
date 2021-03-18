# Libraries
import numpy as np

class Neuron:
    '''All properties and behaviours of a recorded neuron
    are captured in this class'''

    def __init__(self, date='',location='',ID=''):
        self.date = date #date of experiment
        self.location = location #CA3, CA1, or IN
        self.animalID = ID # Animal genotype ID for reference
        self.experiment = {} #Experiment class object
        self.properties = {} #ePhys properties
        self.response = {}
        

    def createExperiment(self,exptType,condition,data,coords=None):
        expt = Experiment(self,exptType,condition,data,coords)
        self.experiment.update({exptType:expt})
        self.response.update({exptType:expt.analyzeExperiment()})
        # return expt.analyzeExperiment()


         

class Experiment:
    '''All different kinds of experiments conducted on a patched
    neuron are captured by this superclass.'''

    def __init__(self,neuron,exptType,condition,data,coords=None):
        self.neuron = neuron
        self.condition = condition        
        self.recordingData = data
        self.stimCoords = coords
        self.exptType = exptType
        self.numSweeps = len(self.recordingData.keys())
        self.sweepIndex = 0 #start of the iterator over sweeps

    def __iter__(self):
        return self

    def __next__(self):
        if self.sweepIndex >= self.numSweeps:
            raise StopIteration
        currentSweepIndex = self.sweepIndex
        self.sweepIndex += 1
        return self.recordingData[currentSweepIndex]
        

    def analyzeExperiment(self):

        if self.exptType == 'sealTest':
            #Call a function to calculate access resistance from recording
            return self.sealTest()
        elif self.exptType == 'IR':
            #Call a function to calculate cell input resistance from recording 
            return self.inputRes()
        elif self.exptType == 'FreqSweep':
            #Call a function to analyze the freq dependent response
            return self.FreqResponse()
            # return 500

    def sealTest(self):
        # calculate access resistance from data
        return self

    def inputRes(self):
        # calculate input resistance from data
        self.neuron.properties.update({'IR':150})
        return self

    def FreqResponse(self):
        self.response = 5
        self.pulseWidth = 5 # milliseconds
        self.neuron.properties.update({'intensity':100}) # % LED power
        return self