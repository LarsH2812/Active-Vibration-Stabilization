import os
import sys

import matplotlib.pyplot as plt
import numpy as np

path = __file__
filePath = ''
for s in path.split('\\')[:-1]:
    filePath += s + '\\'

n = 5

fig1 = plt.figure('Overdracht uitgelegd', figsize=(n,n*2))
fig1manager = plt.get_current_fig_manager()

plt1 = fig1.add_subplot(2,1,1, aspect='equal')
plt2 = fig1.add_subplot(2,1,2, sharex= plt1, sharey= plt1, aspect='equal')

plt1.set_xlim(-1,1); plt1.set_ylim(-1,1)
plt1.grid(True, zorder=2);plt2.grid(True, zorder=2)
plt1.set_xlabel('Re()');plt1.set_ylabel('Im()')
plt2.set_xlabel('Re()');plt2.set_ylabel('Im()')

plt1.set_xticklabels([]);plt2.set_xticklabels([])
plt1.set_yticklabels([]);plt2.set_yticklabels([])

plt1.annotate(f'$f = 1.3 [Hz]$', xy= (-1,1), xycoords='data', xytext=(0.01, .99), textcoords= 'axes fraction', va= 'top', ha= 'left')
plt2.annotate(f'$f = 1.3 [Hz]$', xy= (-1,1), xycoords='data', xytext=(0.01, .99), textcoords= 'axes fraction', va= 'top', ha= 'left')


fig1.tight_layout()

a1 = 1
a2 = 0.5
phi1 = 1/4 * np.pi
phi2 = 1/2 * np.pi

u1 = a1* np.cos(phi1)
v1 = a1* np.sin(phi1)
u2 = a2* np.cos(phi2)
v2 = a2* np.sin(phi2)
u3 = u2-u1
v3 = v2-v1

plt1.quiver(0, 0, u1, v1, color='#000000ff', angles='xy', scale_units='xy', scale=1, zorder=100)
plt2.quiver(0, 0, u1, v1, color='#00000088', angles='xy', scale_units='xy', scale=1, zorder=100)
plt2.quiver(0, 0, u2, v2, color='#000000ff', angles='xy', scale_units='xy', scale=1, zorder=100)
plt2.quiver(u1,v1,u3, v3, color='#00ff00ff', angles='xy', scale_units='xy', scale=1, zorder=100)

plt1.annotate('$S_1$', (u1/2,v1/2), (10,-10), textcoords='offset points')
plt2.annotate('$S_1$', (u1/2,v1/2), (10,-10), textcoords='offset points', color='#00000088')
plt2.annotate('$S_2$', (u2/2,v2/2), (-5,0), textcoords='offset points', ha='right',va='bottom')
plt2.annotate('$H$', (u1 + u3/2 ,v1 + v3/2), (-10,10), textcoords='offset points')


plt.show()
