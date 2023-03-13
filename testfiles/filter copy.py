import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math
import traceback
import sys
import control
import ADwin
import time
from peakdetect import peakdetect


omega = 2*np.pi * 1.4
omega2 = 2*np.pi * 50
t = np.linspace(0, 1/2 * 20, 10000)


sin = 10*np.sin(omega * t) + -1*np.sin(omega2*t) + 0.2
fourierTransform = np.fft.fft(sin)/len(sin)
fourierTransform = fourierTransform[range(int(len(sin)/2))]

fft = np.fft.fft(sin)/len(sin)
fft = fft[range(int(len(sin)/2))]
fft[1:] = 2* fft[1:]
tpCount = len(sin)
values = np.arange(int(tpCount/2))
timePeriod = tpCount / 1000
ffreq = values / timePeriod

fig = plt.figure()
plot = fig.add_subplot(2,1,1)
plots = fig.add_subplot(2,1,2, sharex=plot)
plot.set_xlim(0,5)
plots.set_xlim(0,1)
plot.plot(ffreq, np.abs(fft))
plots.plot(ffreq, np.angle(fft))

plt.show()

