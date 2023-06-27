import sqlite3
import sys
import control
import ADwin
import time
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math
import json
import traceback
import matplotlib

plt.rcParams.update({'font.size': 22})

with sqlite3.connect('data/2023-03-03 - 123611.db') as db:
    ret = db.cursor().execute('SELECT t,northY,northZ,eastX,eastZ,topX,topY FROM guralp').fetchall()

ret = np.transpose(ret)
fig1, ax = plt.subplots(1,1,gridspec_kw=dict(hspace=0))

fit = lambda t,p : 0.0005*np.sin(1.4*2*np.pi * t + p)

DISTANCES = {
'gnx':1.3750, 'gex':0.0000, 'gtx':0.0559,
'gny':0.0000, 'gey':1.3750, 'gty':0.3449,
'gnz':0.7528, 'gez':0.7528, 'gtz':3.2772,
}
AMAT = np.matrix([
#    x | y | z |        rx         |        ry         |          rz
    [0 , 1 , 0 , -DISTANCES['gnz'] ,                 0 , -DISTANCES['gnx']],    # northY
    [0 , 0 , 1 , -DISTANCES['gny'] ,  DISTANCES['gnx'] ,                 0],    # northZ
    [1 , 0 , 0 ,                 0 ,  DISTANCES['gez'] ,  DISTANCES['gey']],    # eastX
    [0 , 0 , 1 , -DISTANCES['gey'] ,  DISTANCES['gex'] ,                 0],    # eastZ
    [1 , 0 , 0 ,                 0 , -DISTANCES['gtz'] ,  DISTANCES['gty']],    # topX
    [0 , 1 , 0 ,  DISTANCES['gtz'] ,                 0 , -DISTANCES['gtx']],    # topY
])
AMAT_INV = np.linalg.inv(AMAT)

meas = np.matrix(ret[1:])
out = np.array(AMAT_INV * meas)

out /= 1000

# (p),_ = sp.optimize.curve_fit(fit,ret[0],out[0])
# print(p)
netspeed = np.sqrt((np.power(out[0],2) + np.power(out[1],2) + np.power(out[2],2)))
labels = np.arange(0,2.6,0.1)
print(labels)

# for i,a in enumerate(ax[:-1]):
#     a.plot(ret[0],out[i])
# sin = 0.0005*np.sin(1.4*2*np.pi * ret[0] + p)
ax.plot(ret[0]-25,out[0],label='langs de x-as',color='black')#, ret[0], sin)
ax.legend()
ax.set_title('Trilling gemeten in de cryostaat')
ax.set_ylabel('snelheid $[m/s]$')
ax.set_xlabel('tijd $[t]$')

ax.set_xlim(labels.min(),labels.max())
ax.set_ylim(-0.0006,0.0006)
ax.set_xticks(labels)

# plt.get_current_fig_manager().full_screen_toggle()
fig1.set_size_inches(25,20)
plt.pause(0.001)
fig1.tight_layout()
plt.pause(0.001)

plt.show()