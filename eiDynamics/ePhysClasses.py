# Libraries
import numpy as np
import pandas as pd
import pickle
import os

from eiDynamics.abf2data        import abf2data
from eiDynamics.expt2df         import expt2df
from eiDynamics.ePhysFunctions  import IRcalc
from eiDynamics.errors          import *
from allCells                   import *


class Neuron:
    '''All properties and behaviours of a recorded neuron
    are captured in this class'''

    def __init__(self, exptParams):
        # Neuron attributes
        try:
            self.cellParamsParser(exptParams)
        except ParameterMismatchError as err:
            print(err)

        # derived in order: neuron.expt -> neuron.response -> neuron.properties
        self.experiment = {}                # Experiment class object, a dict holding experiment objects as values and exptType as keys
        self.response   = pd.DataFrame()    # a pandas dataframe container to hold the table of responses to all experiments
        self.properties = {}                # ePhys properties, derived from analyzing and stats on the response dataframe

    # FIXME: avoid adding duplicate experiments
    def createExperiment(self,datafile,coordfile,exptParams):
        data    = abf2data(datafile,exptParams)                     # create a dict holding sweepwisedata
        coords  = Coords(coordfile).coords if coordfile else ''    # create a dict holding sweepwise coords extracted from coords object
        expt    = Experiment(exptParams,data,coords)                # create an object of experiment class with the recording data and coords

        exptObj = expt.analyzeExperiment(self,exptParams)           # send the experiment object for analysis and analysed data saved in Neuron.resonse dataframe
        self.updateExperiment(exptObj,self.experiment,exptParams.condition,exptParams.exptType,exptParams.stimFreq,exptParams.EorI)

    def __iter__(self):
        return self.experiment.iteritems()

    @staticmethod
    def loadCell(filename):
        try:
            with open(filename,'rb') as fin:
                return pickle.load(fin)
        except FileNotFoundError:
            print("File not found.")
            raise Exception

    def saveCell(self,filename):
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(filename, 'wb') as fout:
            print("Neuron object saved into pickle. Use loadCell to load back.")
            pickle.dump(self, fout, pickle.HIGHEST_PROTOCOL)

    def cellParamsParser(self,ep):
        try:
            self.animal = {"animalID":ep.animalID,          "sex":ep.sex,
                           "dateofBirth":ep.dateofBirth,    "dateofInjection":ep.dateofInj,
                           "dateofExpt":ep.dateofExpt}
            self.virus  = {"site":ep.site,                  "injParams":ep.injectionParams,
                           "virus":ep.virus,                "virusTitre":ep.virusTitre,
                           "injVolume":ep.volumeInj,        "ageatInj":ep.ageAtInj,
                           "ageatExpt":ep.ageAtExp,         "incubation":ep.incubation}
            self.device = {"objMag":ep.objMag,              "polygonFrameSize":ep.frameSize,
                           "polygonGridSize":ep.gridSize,   "polygonSquareSize":ep.squareSize,
                           "DAQ":'Digidata 1440',           "Amplifier":'Multiclamp 700B'}
        except Exception as e:
            raise ParameterMismatchError(message=e)

        return self

    def updateExperiment(self,exptObj,exptDict,condition,exptType,stimFreq,EorI):
        if condition not in exptDict:
            exptDict.update({condition:{exptType:{stimFreq:{EorI:exptObj}}}})
        else:
            if exptType not in exptDict[condition]:
                exptDict[condition].update({exptType:{stimFreq:{EorI:exptObj}}})
            else:
                if stimFreq not in exptDict[condition][exptType]:
                    exptDict[condition][exptType].update({stimFreq:{EorI:exptObj}})
                else:
                    if EorI not in exptDict[condition][exptType][stimFreq]:
                        exptDict[condition][exptType][stimFreq].update({EorI:exptObj})

        exptDict.update(exptDict)
        return exptDict

    def addCell2db(self):
        tempDF = pd.read_excel(allCellsResponseFile)
        outDF = pd.concat([self.response,tempDF],axis=1)
        outDF = outDF.drop_duplicates()
        outDF.to_excel(allCellsResponseFile)


class Experiment:
    '''All different kinds of experiments conducted on a patched
    neuron are captured by this superclass.'''

    def __init__(self,eP,data,coords=None):
        try:
            self.exptParamsParser(eP)
        except ParameterMismatchError as err:
            print(err)
        # self.exptParams = eP
        self.recordingData = data[0]
        self.meanBaseline = data[1]
        self.stimCoords = coords
        self.numSweeps = len(self.recordingData.keys())
        self.sweepIndex = 0  # start of the iterator over sweeps
        self.Flags = {"IRFlag":False,"APFlag":False,"NoisyBaselineFlag":False,"RaChangeFlag":False}
        self.Flags["NoisyBaselineFlag"] = data[2]

    def __iter__(self):
        return self

    def __next__(self):
        if self.sweepIndex >= self.numSweeps:
            raise StopIteration
        currentSweepIndex = self.sweepIndex
        self.sweepIndex += 1
        return self.recordingData[currentSweepIndex]

    def analyzeExperiment(self,neuron,exptParams):

        if self.exptType == 'sealTest':
            # Call a function to calculate access resistance from recording
            return self.sealTest()
        elif self.exptType == 'IR':
            # Call a function to calculate cell input resistance from recording
            return self.inputRes(self,neuron)
        elif self.exptType in ['1sq20Hz','FreqSweep','LTMRand','LTMSeq','convergence']:
            # Call a function to analyze the freq dependent response
            return self.FreqResponse(neuron,exptParams)

    def sealTest(self):
        # calculate access resistance from data, currently not implemented
        return self

    def inputRes(self,neuron):
        # calculate input resistance from data
        neuron.properties.update({'IR':np.mean(IRcalc(self.recordingData,np.arange[1,200],np.arange[500,700]))})
        return self

    # tag: improve feature (do away with so many nested functions)
    def FreqResponse(self,neuron,exptParams):
        # there can be multiple kinds of freq based experiments and their responses.
        return expt2df(self,neuron,exptParams)  # this function takes expt and converts to a dataframe of responses

    def exptParamsParser(self,ep):
        try:
            self.dataFile = ep.datafile
            self.cellID = ep.cellID
            self.stimIntensity = ep.intensity
            self.stimFreq = ep.stimFreq
            self.pulseWidth = ep.pulseWidth
            self.bathTemp = ep.bathTemp
            self.location = ep.location
            self.clamp = ep.clamp
            self.EorI = ep.EorI
            self.polygonProtocolFile = ep.polygonProtocol
            self.numRepeats = ep.repeats
            self.numPulses = ep.numPulses
            self.ISI = round(1000 / ep.stimFreq, 1)
            self.Fs = ep.Fs
            self.exptType = ep.exptType
            self.unit = 'pA' if self.clamp == 'VC' else 'mV' if self.clamp == 'CC' else 'a.u.'
        except Exception as e:
            raise ParameterMismatchError(message=e)

        return self


class Coords:
    '''A Sweep wise record of coordinates of all the square points
    illuminated in the experiment.
    currently class "Coords" is not being used except in generating
    a dict containing sweep wise coords
    '''

    def __init__(self,coordFile):
        self.gridSize = []
        self.numSweeps = []
        self.coords = self.coordParser(coordFile)

    def coordParser(self,coordFile):
        coords = {}
        import csv
        with open(coordFile,'r') as cf:
            c = csv.reader(cf, delimiter=" ")
            for lines in c:
                intline = []
                for i in lines:
                    intline.append(int(i))
                coords[intline[0]] = (intline[3:])
        self.gridSize = [intline[1],intline[2]]
        self.numSweeps = len(coords)
        return coords

    def __iter__(self):
        return self

    def __next__(self):
        self.sweepIndex = 0  # start of the iterator over sweeps
        if self.sweepIndex >= self.numSweeps:
            raise StopIteration
        currentSweepIndex = self.sweepIndex
        self.sweepIndex += 1
        return self.coords[currentSweepIndex]
