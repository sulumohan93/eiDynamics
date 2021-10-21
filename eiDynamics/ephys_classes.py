# Libraries
import numpy as np
import pandas as pd
import pickle
import os
from scipy.optimize  import curve_fit

# EI Dynamics module
from eidynamics.abf_to_data         import abf_to_data
from eidynamics.expt_to_dataframe   import expt2df
from eidynamics.ephys_functions     import IRcalc
from eidynamics.utils               import delayed_alpha_function,PSP_start_time_1sq
from eidynamics                     import pattern_index
from eidynamics.errors              import *
from allcells                       import *


class Neuron:
    """
    All properties and behaviours of a recorded neuron are captured in this class.
    Methods:    Create experiment, update experiment
    Attributes: Neuron.experiment   = a dict holding experiment objects as values and exptType as keys
                Neuron.response     = a pandas dataframe container to hold the table of responses to all experiments
                Neuron.properties   = ePhys properties, derived from analyzing and stats on the response dataframe
                Neuron.animal,
                Neuron.virus
                Neuron.device
    """

    def __init__(self, exptParams):
        # Neuron attributes
        try:
            self.cell_params_parser(exptParams)
        except ParameterMismatchError as err:
            print(err)

        # derived in order: neuron.experiment -> neuron.response -> neuron.properties
        self.experiment         = {}
        self.response           = pd.DataFrame()
        self.properties         = {}
        self.expectedResponse   = {}
        self.spotExpectedDict   = {}
        self.singleSpotDataParsed     = False
        self.spotStimFreq       = 20

    def addExperiment(self,datafile,coordfile,exptParams):
        """
        A function that takes filenames and creates an experiment object for a cell object
        """
        newExpt         = Experiment(exptParams,datafile,coordfile)
        newExpt.analyze_experiment(self,exptParams)
        self.updateExperiment(newExpt,self.experiment,exptParams.condition,exptParams.exptType,exptParams.stimFreq,exptParams.EorI)

        if exptParams.exptType == '1sq20Hz':
            self.singleSpotDataParsed = True
            self.spotStimFreq         = exptParams.stimFreq
            _1sqExpectedDict = self.make_spot_profile(newExpt)
            # self.spotExpectedDict.update({exptParams.condition:{exptParams.stimFreq:{exptParams.EorI:_1sqExpectedDict}}})
            self.updateExperiment(_1sqExpectedDict, self.spotExpectedDict, exptParams.condition, exptParams.exptType, exptParams.stimFreq, exptParams.EorI)

        if self.singleSpotDataParsed == True and exptParams.exptType == 'FreqSweep':
            spotExpectedDict_1sq = self.spotExpectedDict[exptParams.condition]['1sq20Hz'][self.spotStimFreq][exptParams.EorI]
            frameExpectedDict    = self.find_frame_expected(newExpt,spotExpectedDict_1sq)
            self.updateExperiment(frameExpectedDict, self.expectedResponse, exptParams.condition, exptParams.exptType, exptParams.stimFreq, exptParams.EorI)

        return self

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
        directory       = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(filename, 'wb') as fout:
            print("Neuron object saved into pickle. Use loadCell to load back.")
            pickle.dump(self, fout, pickle.HIGHEST_PROTOCOL)

    def cell_params_parser(self,ep):
        """
        Stores the animal related details into Neuron attributes
        from experiment parameter file
        """
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
        except Exception as err:
            raise ParameterMismatchError(message=err)

        return self

    def updateExperiment(self,exptObj,exptDict,condition,exptType,stimFreq,EorI):
        """
        Accommodates all the expriment objects into a dictionary
        Kind of a HACK
        """
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

    @staticmethod
    def addCell2db(cellFile):
        cell        = Neuron.loadCell(cellFile)
        allCellFile = os.path.join(projectPathRoot,allCellsResponseFile)
        tempDF      = pd.read_excel(allCellFile)
        outDF       = pd.concat([cell.response,tempDF],axis=1)
        outDF       = outDF.drop_duplicates()
        outDF.to_excel(allCellsResponseFile)
        print("Cell experiment data has been added to {}".format(allCellsResponseFile))

    def make_spot_profile(self,exptObj1sq):
        if not exptObj1sq.exptType == '1sq20Hz':
            raise ParameterMismatchError(message='Experiment object has to be a 1sq experiment')

        Fs                      = exptObj1sq.Fs
        IPI                     = exptObj1sq.IPI # 0.05 seconds
        numSweeps               = exptObj1sq.numSweeps

        # Get trial averaged stim and response traces for every spot
        pd                      = exptObj1sq.extract_trial_averaged_data(channels=[2])[2] # 45 x 40000
        cell                    = exptObj1sq.extract_trial_averaged_data(channels=[0])[0] # 45 x 40000
        # Get a dict of all spots
        spotCoords              = dict([(k, exptObj1sq.stimCoords[k]) for k in range(1,1+int(exptObj1sq.numSweeps/exptObj1sq.numRepeats))])
        
        firstPulseTime          = int(Fs*(exptObj1sq.stimStart)) # 4628 sample points
        secondPulseTime         = int(Fs*(exptObj1sq.stimStart + IPI)) # 5628 sample points

        # Get the synaptic delay from the average responses of all the spots
        avgResponseStartTime    = PSP_start_time_1sq(cell,stimStartTime=exptObj1sq.stimStart,Fs=Fs)   # 0.2365 seconds
        avgSecondResponseStartTime = avgResponseStartTime + IPI # 0.2865 seconds
        avgSynapticDelay        = avgResponseStartTime-exptObj1sq.stimStart # ~0.0055 seconds

        spotExpectedDict        = {}

        for i in range(len(spotCoords)):
            spotPD_trialAvg               = pd[i,int(Fs*avgResponseStartTime):int(Fs*avgSecondResponseStartTime)] # 1 x 1000
            spotCell_trialAVG_pulse2pulse = cell[i,firstPulseTime:secondPulseTime+200]

            t                   = np.linspace(0,IPI+0.01,len(spotCell_trialAVG_pulse2pulse)) # seconds at Fs sampling
            T                   = np.linspace(0,0.4,int(0.4*Fs)) # seconds at Fs sampling
            popt,_              = curve_fit(delayed_alpha_function,t,spotCell_trialAVG_pulse2pulse,p0=([0.5,0.05,0.005])) #p0 are initial guesses A=0.5 mV, tau=50ms,delta=5ms
            A,tau,delta         = popt
            fittedSpotRes       = delayed_alpha_function(T,*popt) # 400 ms = 8000 datapoints long predicted trace from the fit for the spot, not really usable
            
            spotExpectedDict[spotCoords[i+1][0]] = [avgSynapticDelay,A,tau,delta,spotCell_trialAVG_pulse2pulse,fittedSpotRes]
        
        all1sqAvg                     = np.mean(cell[:,firstPulseTime:secondPulseTime+200],axis=0)
        popt,_                        = curve_fit(delayed_alpha_function,t,all1sqAvg,p0=([0.5,0.05,0.005])) #p0 are initial guesses A=0.5 mV, tau=50ms,delta=5ms
        A,tau,delta                   = popt
        all1sqAvg_fittedSpotRes       = delayed_alpha_function(T,*popt)
        spotExpectedDict['1sqAvg']    = [avgSynapticDelay,A,tau,delta,all1sqAvg,all1sqAvg_fittedSpotRes]

        return spotExpectedDict

    def find_frame_expected(self,exptObj,spotExpectedDict_1sq):
        stimFreq        = exptObj.stimFreq
        IPI             = exptObj.IPI # IPI of current freq sweep experiment
        numPulses       = exptObj.numPulses
        numSweeps       = exptObj.numSweeps
        numRepeats      = exptObj.numRepeats
        cell            = exptObj.extract_trial_averaged_data(channels=[0])[0][:,:20000] # 8 x 40000
        stimCoords      = dict([(k, exptObj.stimCoords[k]) for k in range(1,1+int(numSweeps/numRepeats))]) # {8 key dict}
        stimStart       = 0.2314
        Fs              = 2e4
    
        frameExpected   = {}
        for i in range(len(stimCoords)):
            coordsTemp = stimCoords[i+1] # nd array of spot coords
            frameID    = pattern_index.get_patternID(coordsTemp)
            numSq      = len(coordsTemp)
            firstPulseExpected = np.zeros((int(Fs*(IPI+0.01))))
            firstPulseFitted   = np.zeros((int(Fs*(0.4))))# added 0.01 second = 10 ms to IPI, check line 41,43,68,69
            for spot in coordsTemp:            
                spotExpected        = spotExpectedDict_1sq[spot][4]
                spotFitted          = spotExpectedDict_1sq['1sqAvg'][5]
                firstPulseExpected  += spotExpected[:len(firstPulseExpected)]
                firstPulseFitted    += spotFitted[:len(firstPulseFitted)]
            avgSynapticDelay    = spotExpectedDict_1sq[spot][0]
            expectedResToPulses = np.zeros(len(cell[0,:]))
            fittedResToPulses = np.zeros(len(cell[0,:]))
            t1 = int(Fs*stimStart)
            for k in range(numPulses):
                
                t2 = t1+int(Fs*IPI+avgSynapticDelay)
                T2 = t1+int(0.4*Fs)
                window1 = range(t1,t2)
                window2 = range(t1,T2)
                expectedResToPulses[window1] += firstPulseExpected[:len(window1)]
                fittedResToPulses[window2]   += firstPulseFitted[:len(window2)]
                t1 = t1+int(Fs*IPI)

            frameExpected[frameID] = [numSq,stimFreq,exptObj.stimIntensity,exptObj.pulseWidth,expectedResToPulses,fittedResToPulses,firstPulseFitted,firstPulseExpected]
        
        return frameExpected


class Experiment:
    '''All different kinds of experiments conducted on a patched
    neuron are captured by this superclass.'''

    def __init__(self,exptParams,datafile,coordfile=None):
        try:
            self.exptParamsParser(exptParams)
        except ParameterMismatchError as err:
            print(err)

        self.Flags          = {"IRFlag":False,"APFlag":False,"NoisyBaselineFlag":False,"RaChangeFlag":False}

        data                = abf_to_data(datafile,
                                          baseline_criterion=exptParams.baselineCriterion,
                                          sweep_baseline_epoch=exptParams.sweepBaselineEpoch,
                                          signal_scaling=exptParams.signalScaling,
                                          sampling_freq=exptParams.Fs,
                                          filter_type=exptParams.filter,
                                          filter_cutoff=exptParams.filterHighCutoff,
                                          plot_data=False)
        self.recordingData  = data[0]
        self.meanBaseline   = data[1]        
        self.Flags["NoisyBaselineFlag"] = data[2]
        del data
        
        self.stimCoords     = Coords(coordfile).coords if coordfile else ''

        self.numSweeps      = len(self.recordingData.keys())
        self.sweepIndex     = 0  # start of the iterator over sweeps

    def __iter__(self):
        return self

    def __next__(self):
        if self.sweepIndex >= self.numSweeps:
            raise StopIteration
        currentSweepIndex   = self.sweepIndex
        self.sweepIndex     += 1
        return self.recordingData[currentSweepIndex]

    def extract_channelwise_data(self,channels=[0,1,2,'Cmd','Time']):
        '''
        Returns a dictionary holding channels as keys,
        and sweeps as keys in an nxm 2-d array format where n is number of sweeps
        and m is number of datapoints in the recording per sweep.
        '''
        channelDict = {}
        tempChannelData = np.zeros((self.numSweeps,len(self.recordingData[0][0])))
        for ch in channels:
            for i in range(self.numSweeps):
                tempChannelData[i,:] = self.recordingData[i][ch]
            channelDict[ch] = tempChannelData
            tempChannelData = 0.0*tempChannelData            
        return channelDict

    def extract_trial_averaged_data(self,channels=[0]):
        '''
        Returns a dictionary holding channels as keys,
        and trial averaged sweeps as an nxm 2-d array where n is number of patterns
        and m is number of datapoints in the recording per sweep.
        '''
        chData = self.extract_channelwise_data(channels=channels)
        chMean = {}
        for ch in channels:
            chData_temp = np.reshape(chData[ch],(self.numRepeats,int(self.numSweeps/self.numRepeats),-1))
            chMean[ch] = np.mean(chData_temp,axis=0)

        return chMean

    def analyze_experiment(self,neuron,exptParams):

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

    # FIXME: improve feature (do away with so many nested functions)
    def FreqResponse(self,neuron,exptParams):
        # there can be multiple kinds of freq based experiments and their responses.
        return expt2df(self,neuron,exptParams)  # this function takes expt and converts to a dataframe of responses

    def exptParamsParser(self,ep):
        try:
            self.dataFile           = ep.datafile
            self.cellID             = ep.cellID
            self.stimIntensity      = ep.intensity
            self.stimFreq           = ep.stimFreq
            self.pulseWidth         = ep.pulseWidth
            self.bathTemp           = ep.bathTemp
            self.location           = ep.location
            self.clamp              = ep.clamp
            self.EorI               = ep.EorI
            self.polygonProtocolFile= ep.polygonProtocol
            self.numRepeats         = ep.repeats
            self.numPulses          = ep.numPulses
            self.IPI                = 1 / ep.stimFreq
            self.stimStart          = ep.opticalStimEpoch[0]
            self.Fs                 = ep.Fs
            self.exptType           = ep.exptType
            self.condition          = ep.condition
            self.unit = 'pA' if self.clamp == 'VC' else 'mV' if self.clamp == 'CC' else 'a.u.'
        except Exception as err:
            raise ParameterMismatchError(message=err)

        return self


class Coords:
    """
    An object that stores Sweep wise record of coordinates of all the square points
    illuminated in the experiment.
    currently class "Coords" is not being used except in generating
    a dict containing sweep wise coords
    """

    def __init__(self,coordFile):
        self.gridSize       = []
        self.numSweeps      = []
        self.coords         = self.coordParser(coordFile)

    def coordParser(self,coordFile):
        coords              = {}
        import csv
        with open(coordFile,'r') as cf:
            c               = csv.reader(cf, delimiter=" ")
            for lines in c:
                intline     = []
                for i in lines:
                    intline.append(int(i))
                frameID     = intline[0]
                coords[frameID] = (intline[3:])
        self.gridSize       = [intline[1],intline[2]]
        self.numSweeps      = len(coords)
        return coords

    def __iter__(self):
        return self

    def __next__(self):
        self.sweepIndex = 0  # start of the iterator over sweeps
        if self.sweepIndex >= self.numSweeps:
            raise StopIteration
        currentSweepIndex   = self.sweepIndex
        self.sweepIndex += 1
        return self.coords[currentSweepIndex]

# TODO
class EphysData:
    """
    Experimental Class: actual experimental data.
    """
    def __init__(self,abfFile, exptParams):
        self.datafile           = abfFile

        self.filter             = exptParams.filter
        self.filterCutoff       = exptParams.filterHighCutoff
        self.sweepBaselineEpoch = exptParams.sweepBaselineEpoch
        self.baselineSubtraction= exptParams.baselineSubtraction
        self.scaling            = exptParams.signalScaling

        self.data               = self.parseABF()
        self.numSweeps          = 0        
        self.numChannels        = 0

    def parseABF(self,exptParams):
        self.data = abf_to_data(self.datafile,
                                baseline_criterion=exptParams.baselineCriterion,
                                sweep_baseline_epoch=exptParams.sweepBaselineEpoch,
                                signal_scaling=exptParams.signalScaling,
                                sampling_freq=exptParams.Fs,
                                filter_type=exptParams.filter,
                                filter_cutoff=exptParams.filterHighCutOff,
                                plot_sample_data=False)
    
    def plotEphysData(self):
        return None