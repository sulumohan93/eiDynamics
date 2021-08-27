'''Make GLM
Steps
1: Get alpha function for V(t) = alpha(t-ts) = Vmax*(t-t_onset/tau)*exp(-(t-t_onset-tau)/tau)
2: Sum for (all squares x weights)
3: Write a function for cosecutive pulses, Vn = V1 * f(delT, n)
4: Combine all together
'''

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.optimize import curve_fit

from eiDynamics.abf2data                        import abf2data
import eiDynamics.ExperimentParameters_Default  as eP
