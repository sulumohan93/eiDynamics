import numpy as np
import datetime

# Animal
# Base genotype Grik4Cre C57BL/6-Tg(Grik4-cre)G32-4Stl/J (Jax Stock No. 006474)
# NCBS Strain: Grik4Cre_2018
animalID        = 'GXXX'
sex             = 'X'
dateofBirth     = datetime.date(2021, 5, 7)
dateofInj       = datetime.date(2021, 6, 13)
dateofExpt      = datetime.date(2021, 7, 30)
sliceThickness  = 400 											# um

# Virus Injection
site            = {'RC':1.9, 'ML':2.0, 'DV':1.5} 					# from bregma, right hemisphere in rostrocaudal, mediolateral, and dorsoventral axes
injectionParams = {'Pressure':8, 'pulseWidth':15, 'duration':30}  # picospritzer nitrogen pressure in psi, pulse width in millisecond, duration in minutes
virus           = 'ChR2'											# ChR2 (Addgene 18917) or ChETA (Addgene 35507)
virusTitre      = 6e12											# GC/ml, after dilution
dilution        = 0.5												# in PBS to make up the titre
volumeInj       = 5e-4 											# approx volume in ml
ageAtInj        = (dateofInj	- dateofBirth)
ageAtExp        = (dateofExpt	- dateofBirth)
incubation      = (ageAtExp	- ageAtInj)

# Polygon
objMag          = 40 												# magnification in x
frameSize       = np.array([13032.25, 7419.2])					# frame size in um, with 1x magnification
gridSize        = 24												# corresponds to pixel size of 13x8 µm
squareSize      = frameSize / (gridSize * objMag)

# Internal solution (is)
isBatch         = datetime.date(2021, 7, 29)
ispH            = 7.35
isOsm           = 292												# mOsm/kg H2O

# Recording solution (aCSF)
aCSFpH          = 7.40
aCSFOsm         = 310												# mOsm/kg H2O
gabaConc        = 2e-6                                            # mol/litre, if gabazine experiments were done

# Experiment
cellID			= 'XXXN'

bathTemp		= 32												# degree celsius
location		= ''
clamp			= ''
EorI			= ''
unit			= ''
clampPotential  = ''

datafile		= ''
polygonProtocol	= ''

intensity		= 100
pulseWidth		= 2
stimFreq		= 20 												# in Hz
repeats			= 3
numPulses		= 1												# a fixed number for all frequencies

exptTypes		= ['GapFree','IR','CurrentStep','1sq20Hz','FreqSweep','LTMSeq','LTMRand','convergence']
exptType		= exptTypes[4]

conditions		= ['Control','Gabazine']
condition		= conditions[0]

# Signal parameters
Fs						= 2e4
signalScaling			= 1											# usually 1, but sometimes the DAQ does not save current values in proper units
baselineSubtraction		= True
baselineCriterion		= 0.1										# baseline fluctuations of 10% are allowed
DAQfilterBand           = [0, 10000]

# Epochs (time in seconds)
sweepDuration           = [0, 2.0]
sweepBaselineEpoch      = [0, 0.2]    								# seconds, end of baseline time
opticalStimEpoch        = [0.231, 1.231]
IRBaselineEpoch         = [1.331, 1.531]
IRpulseEpoch            = [1.531, 1.831]
IRchargingPeriod        = [1.531, 1.581]
IRsteadystatePeriod     = [1.681, 1.831]
interSweepInterval      = 30                                        # seconds

# Analysis
# Filtering
filters			        = {0:'',1:'bessel',2:'butter',3:'decimate'}
filter                  = filters[0]
filterHighCutoff        = 2e4