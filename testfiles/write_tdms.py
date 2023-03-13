import sqlite3, matplotlib.pyplot as plt, numpy as np

db = sqlite3.connect('data/2023-03-07 - 100518.db')
cur = db.cursor()

ret = np.transpose(cur.execute('SELECT * FROM guralp').fetchall())

fig1 = plt.figure('XYZ-Data [INITIALIZING]', figsize=(15, 10))
fig1manager = plt.get_current_fig_manager()

#Create a Figure
plotxyz = plt.subplot2grid((2,3), (1,0), colspan=3)
plotx   = plt.subplot2grid((2,3), (0,0), sharex=plotxyz, sharey=plotxyz)
ploty   = plt.subplot2grid((2,3), (0,1), sharex=plotxyz, sharey=plotxyz)
plotz   = plt.subplot2grid((2,3), (0,2), sharex=plotxyz, sharey=plotxyz)

topX, = plotx.plot(ret[0],ret[1], '#ff0000', label= 'Top X')
northX, = plotx.plot(ret[0],ret[4], '#aa0000', label= 'North X')
eastX, = plotx.plot(ret[0],ret[7], '#550000', label= 'East X')
ax, = plotx.plot([],[], 'k--', label= 'Average X')

plotx.set_title('X')
plotx.set_xlabel('Time (s)')
plotx.set_ylabel('A (V)')
plotx.set_xlim(0, 10)
plotx.set_ylim(-1.5, 1.5)

topY, = ploty.plot(ret[0],ret[2], '#00ff00', label= 'Top Y')
northY, = ploty.plot(ret[0],ret[5], '#00aa00', label= 'North Y')
eastY, = ploty.plot(ret[0],ret[8], '#005500', label= 'East Y')
ay, = ploty.plot([],[], 'k--', label= 'Average Y')

ploty.set_title('Y')
ploty.set_xlabel('Time (s)')
ploty.set_ylabel('A (V)')
ploty.set_xlim(0, 10)
ploty.set_ylim(-1.5, 1.5)

topZ, = plotz.plot(ret[0],ret[3], '#0000ff', label= 'Top Z')
northZ, = plotz.plot(ret[0],ret[6], '#0000aa', label= 'North Z')
eastZ, = plotz.plot(ret[0],ret[9], '#000055', label= 'East Z')
az, = plotz.plot([],[], 'k--', label= 'Average Z')

plotz.set_title('Z')
plotz.set_xlabel('Time (s)')
plotz.set_ylabel('A (V)')
plotz.set_xlim(0, 10)
plotz.set_ylim(-1.5, 1.5)

plt.show()