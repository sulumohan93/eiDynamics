import numpy as np
import datetime

## Animal
animalID = 'GXXX' # Base genotype Grik4Cre C57BL/6-Tg(Grik4-cre)G32-4Stl/J (Jax Stock No. 006474)
sex = '' # 'M' or 'F'
dateofBirth = datetime.date(2021,1,1)
dateofInj =   datetime.date(2021,1,28)
dateofExpt =  datetime.date(2021,2,26)

#Virus Injection
site = {'RC':1.9,'ML':2.0,'DV':1.5} # from bregma, right hemisphere in rostrocausal, mediolateral, and dorsoventral axes
injectionParams = {'Pressure':8,'pulseWidth':10,'duration':30} #picospritzer nitrogen pressure in psi, pulse width in millisecond, duration in minutes
virus = 'ChR2' # ChR2 (Addgene 18917) or ChETA (Addgene 35507)
virusTitre = 6e12 # GC/ml, after dilution
dilution = 0.5 # in PBS to make up the titre
volumeInj = 5e-4 # approx volume in ml
ageAtInj = (dateofInj-dateofBirth)
ageAtExp = (dateofExpt-dateofBirth)
incubation = (ageAtExp - ageAtInj)

## Polygon
objMag = 40 # magnification in x
frameSize = np.array([12960,6912]) #frame size in um, with 1x magnification
gridSize = 24 #corresponds to pixel size of 13x8 µm
pixelSize = frameSize/(gridSize*objMag)

## Experiment
intensity = 100
stimFreq = 20 # in Hz
pulseWidth = 5

bathTemp = 32 # degree celsius
location = ''
clamp = ''
EorI = ''
patterns = ''
repeats = ''

numPulses = 8 # a fixed number for all frequencies

exptTypes = ['GapFree','IR','CurrentStep','20Hz','30Hz','40Hz','50Hz','100Hz']
exptType = exptTypes[-1]

conditions = ['Control','Gabazine']
condition = conditions[0]

Fs = 20
baselineSubtraction = False
baselineCriterion = 0.1 # baseline fluctuations of 10% are allowed
baselineStart = 0
baselineEnd = 200 # milliseconds, end of baseline time
baselineWindow = Fs*np.arange(baselineStart,baselineEnd)

IR_baselineEnd = 1000 # milliseconds, end of baseline time
IR_baselineStart = IR_baselineEnd-200
IR_baselineWindow = np.arange(baselineStart,baselineEnd)

IR_steadystateEnd = 1300 # End of hyperpolarizing pulse to measure IR
IR_steadstateStart = IR_steadystateEnd-200 # 
IR_steadystateWindow = np.arange(IR_steadstateStart,IR_steadystateEnd)

## Analysis
# Filtering
filter = {0:'',1:'bessel'}
filtering = filter[0]