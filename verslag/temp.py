import sqlite3, numpy as np, matplotlib.pyplot as plt

db = sqlite3.connect("data/2023-03-28 - 163820[Only guralps read].db")
cur = db.cursor()

ret = np.transpose(cur.execute('SELECT * FROM guralp WHERE t BETWEEN 590 AND 630').fetchall())
names = np.transpose(cur.execute('PRAGMA table_info(guralp)').fetchall())[1]

data = {name: dat for name, dat in zip(names, ret)}

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

meas = np.matrix([data['northY'],data['northZ'],data['eastX'],data['eastZ'],data['topX'],data['topY']])
meas /= 1000


outmat = AMAT_INV * meas
outmat = np.array(outmat)


fig1, (plotx, ploty,plotz, plotrx,plotry,plotrz) = plt.subplots(6,1, sharex=True, sharey=True)
plt.tight_layout()
fig1.subplots_adjust(hspace=0)
fig1manager = plt.get_current_fig_manager()

linex, = plotx.plot(data['t'],outmat[0], 'b')
liney, = ploty.plot(data['t'],outmat[1], 'b')
linez, = plotz.plot(data['t'],outmat[2], 'b')
linerx, = plotrx.plot(data['t'],outmat[3], 'b')
linery, = plotry.plot(data['t'],outmat[4], 'b')
linerz, = plotrz.plot(data['t'],outmat[5], 'b')

outerlim = 1.5/1000
plotx.set_xlim(data['t'][0], data['t'][-1]);plotx.set_ylim(-1.05*outerlim,1.05*outerlim)
plotx.set_yticks(np.linspace(-0.95*outerlim,0.95*outerlim,5))

fig1manager.window.showMaximized()

plt.show()