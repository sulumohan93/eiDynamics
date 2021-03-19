import numpy as np

## Animal
animalID = 'Grik-xxx'
dateofBirth = ''
dateofExpt = ''
location = 'CA1'

## Polygon
intensity = 100
gridSize = 24

## Experiment
exptTypes = ['GapFree','IR','CurrentStep','1sqPSP','FreqSweep']
exptType = exptTypes[-1]

conditions = ['Control','Gabazine']
condition = conditions[0]

Fs = 20000
baselineStart = 0
baselineEnd = 200 # milliseconds, end of baseline time
baselineWindow = np.arange(baselineStart*Fs,baselineEnd*Fs)

IR_steadystateEnd = 1300 # End of hyperpolarizing pulse to measure IR
IR_steadstateStart = IR_steadystateEnd-200 # 
IR_steadystateWindow = np.arange(IR_steadstateStart*Fs,IR_steadystateEnd*Fs)

## Analysis
# Filtering
filter = {0:'',1:'bessel'}
filtering = filter[1]