import numpy as np

## Animal
animalID = 'Grik-xxx'
dateofBirth = ''
dateofExpt = ''


## Polygon
intensity = 100
gridSize = 24
stimFreq = 100 # in Hz
pulseWidth = 5

## Experiment
patterns = ["A","B","C","D","E","F","G","H","I","J"]*3
repeats = 10*[1]+10*[2]+10*[3]

numPulses = 8 # a fixed number for all frequencies
location = 'CA1'

exptTypes = ['GapFree','IR','CurrentStep','20Hz','50Hz','100Hz']
exptType = exptTypes[-1]

conditions = ['Control','Gabazine']
condition = conditions[0]

Fs = 20
baselineStart = 0
baselineEnd = 200 # milliseconds, end of baseline time
baselineWindow = np.arange(baselineStart,baselineEnd)

IR_baselineEnd = 1000 # milliseconds, end of baseline time
IR_baselineStart = IR_baselineEnd-100
IR_baselineWindow = np.arange(baselineStart,baselineEnd)

IR_steadystateEnd = 1300 # End of hyperpolarizing pulse to measure IR
IR_steadstateStart = IR_steadystateEnd-100 # 
IR_steadystateWindow = np.arange(IR_steadstateStart,IR_steadystateEnd)

## Analysis
# Filtering
filter = {0:'',1:'bessel'}
filtering = filter[1]