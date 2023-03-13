import sys
import control
import ADwin
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math

fig1 = plt.figure('XYZ-Data', figsize=(10,5))

plot1 = fig1.add_subplot(2,4,(1,2))
plot2 = fig1.add_subplot(2,4,(5,6))
plot3 = fig1.add_subplot(2,4,(3,8))

plt.show()