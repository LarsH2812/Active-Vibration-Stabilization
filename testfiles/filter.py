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

with open('data/Guralp/json/Guralp Sensor Data - 20230221163002.json', 'r') as file:
    data = json.load(file)
    print(data['top'].keys())

# Create the data arrays
t         = np.array(data['t'])
topX      = np.array(data['top']['topX'])
topY      = np.array(data['top']['topY'])
topZ      = np.array(data['top']['topZ'])
northX    = np.array(data['north']['northX'])
northY    = np.array(data['north']['northY'])
northZ    = np.array(data['north']['northZ'])
eastX     = np.array(data['east']['eastX'])
eastY     = np.array(data['east']['eastY'])
eastZ     = np.array(data['east']['eastZ'])

x = np.array([topX, northX, eastX])
y = np.array([topY, northY, eastY])
z = np.array([topZ, northZ, eastZ])

avgX = np.average(x, axis=0)
avgY = np.average(y, axis=0)
avgZ = np.average(z, axis=0)

sine = np.zeros((len(t)))


# Create the figure
fig1 = plt.figure('XYZ-Data')
plt.plot(t, avgX)

# Create the fourier transform
fourierTransform = np.fft.fft(avgX)/len(avgX)
fourierTransform = fourierTransform[range(int(len(avgX)/2))]
tpCount = len(avgX)
values = np.arange(int(tpCount/2))
timePeriod = tpCount / 1000
frequencies = values / timePeriod
topamp = np.sort(abs(fourierTransform))[-3:]
topfreq = frequencies[np.argsort(abs(fourierTransform))][-1]
omega = 2 * np.pi * topfreq

fig2 = plt.figure('Fourier-Data')
plotf = fig2.add_subplot(111)
plotf.set_xlabel('Frequency ($Hz$)')
plotf.set_ylabel('Amplitude')
four, = plotf.plot(frequencies, abs(fourierTransform))
fig2.show()
tindices = np.where(avgX == 0.5)

omega = 2 * np.pi * frequencies[np.where(abs(fourierTransform)> 0)]



plt.show()