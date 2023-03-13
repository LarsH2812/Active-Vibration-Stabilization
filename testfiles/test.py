import sys
import control
import ADwin
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math
import json
import traceback
from np2json import NumpyArrayEncoder

plt.ion()

COMPLETEPLOT = False
SAMPLETIME = 0.2 # [minutes]

error = None

#Create a Figure
plotxyz = plt.subplot2grid((2,3), (1,0), colspan=3)
plotx = plt.subplot2grid((2,3), (0,0), sharex=plotxyz, sharey=plotxyz)
ploty = plt.subplot2grid((2,3), (0,1), sharex=plotxyz, sharey=plotxyz)
plotz = plt.subplot2grid((2,3), (0,2), sharex=plotxyz, sharey=plotxyz)

# Create the data arrays
t = np.linspace(0, 0, 1)

X      = np.zeros((1,3))
Y      = np.zeros((1,3))
Z      = np.zeros((1,3))
topX   = np.zeros((1))
topY   = np.zeros((1))
topZ   = np.zeros((1))
northX = np.zeros((1))
northY = np.zeros((1))
northZ = np.zeros((1))
eastX  = np.zeros((1))
eastY  = np.zeros((1))
eastZ  = np.zeros((1))
sine   = np.zeros((1))
avgX = np.average(topX, axis=0)
avgY = np.average(topY, axis=0)
avgZ = np.average(topZ, axis=0)

sin, = plotx.plot(t, sine, 'g:')

tx, nx, ex, ax = plotx.plot(t, topX, 'r',t, northX, 'r',t, eastX, 'r', t, avgX, 'k--')
sx = plotx.scatter(t, topX, c='r', marker='o', s=10)
tx.set_label('Top X')
nx.set_label('North X')
ex.set_label('East X')
ax.set_label('Average X')
tx.set_color('#ff0000')
nx.set_color('#aa0000')
ex.set_color('#550000')
plotx.set_title('X')
plotx.set_xlabel('Time (s)')
plotx.set_ylabel('A (V)')
plotx.legend()
plotx.set_xlim(0, 10)
plotx.set_ylim(-10, 10)

ty, ny, ey, ay = ploty.plot(t, topY, 'g',t, northY, 'g',t, eastY, 'g', t, avgY, 'k--')
ty.set_label('Top Y')
ny.set_label('North Y')
ey.set_label('East Y')
ay.set_label('Average Y')
ty.set_color('#00ff00')
ny.set_color('#00aa00')
ey.set_color('#005500')
ploty.set_title('Y')
ploty.legend()
ploty.set_xlabel('Time (s)')
ploty.set_ylabel('A (V)')
ploty.set_xlim(0, 10)
ploty.set_ylim(-10, 10)

tz, nz, ez, az = plotz.plot(t, topZ, 'b', t, northZ, 'b',t, eastZ, 'b', t, avgZ, 'k--')
tz.set_label('Top Z')
nz.set_label('North Z')
ez.set_label('East Z')
az.set_label('Average Z')
tz.set_color('#0000ff')
nz.set_color('#0000aa')
ez.set_color('#000055')
plotz.legend()
plotz.set_title('Z')
plotz.set_xlabel('Time (s)')
plotz.set_ylabel('A (V)')
plotz.set_xlim(0, 10)
plotz.set_ylim(-10, 10)

ttx, tnx, tex, tty, tny, tey, ttz, tnz, tez = plotxyz.plot(t, topX, 'r',t, northX, 'r',t, eastX, 'r', t, topY, 'g',t, northY, 'g',t, eastY, 'g', t, topZ, 'b', t, northZ, 'b',t, eastZ, 'b')

if COMPLETEPLOT:
    plotxyz.set_title('X, Y, Z')
    ttx.set_label('Top X')
    tnx.set_label('North X')
    tex.set_label('East X')
    tty.set_label('Top Y')
    tny.set_label('North Y')
    tey.set_label('East Y')
    ttz.set_label('Top Z')
    tnz.set_label('North Z')
    tez.set_label('East Z')
else:
    plotxyz.set_title('X, Y, Z')
    ttx.set_label('Average X')
    tty.set_label('Average Y')
    ttz.set_label('Average Z')

plotxyz.set_xlabel('Time (s)')
plotxyz.set_ylabel('A (V)')
plotxyz.legend()
plotxyz.set_xlim(0, 10)
plotxyz.set_ylim(-10, 10)
mng = plt.get_current_fig_manager()
mng.full_screen_toggle()

plt.tight_layout()
plt.draw()
plt.pause(0.01)

# Create a new ADwin object
adwin = ADwin.ADwin(DeviceNo= 1,raiseExceptions= 1, useNumpyArrays= 1)
i = 0

# Load the program
adwin.Boot(Filename="c:\ADwin\ADwin9.btl")
adwin.Load_Process(Filename="test.T91")


# Start the program
adwin.Start_Process(ProcessNo= 1)
t0 = time.time()
while True:
    try:
        # Read the data
        t1 = time.time()
        dataT = adwin.Get_Par_Block(1,3)
        fDataT = adwin.Get_FPar_Block(1,3)
        dataN = adwin.Get_Par_Block(4,3)
        fDataN = adwin.Get_FPar_Block(4,3)
        dataE = adwin.Get_Par_Block(7,3)
        fDataE = adwin.Get_FPar_Block(7,3)

        topX = np.append(topX, [fDataT[0]], 0)
        topY = np.append(topY, [fDataT[1]], 0)
        topZ = np.append(topZ, [fDataT[2]], 0)
        northX = np.append(northX, [fDataN[0]], 0)
        northY = np.append(northY, [fDataN[1]], 0)
        northZ = np.append(northZ, [fDataN[2]], 0)
        eastX = np.append(eastX, [fDataE[0]], 0)
        eastY = np.append(eastY, [fDataE[1]], 0)
        eastZ = np.append(eastZ, [fDataE[2]], 0)        

        # Calculate the time step
        dt = t1 - t0

        # Update the data arrays
        t = np.append(t, [dt], 0)
        tsin = np.linspace(t[0], t[-1], 1000)
        sine = np.sin(8.7964594 * tsin + 0.1 * np.pi)
        X = np.array([topX, northX, eastX])
        Y = np.array([topY, northY, eastY])
        Z = np.array([topZ, northZ, eastZ])

        avgX = np.average(X, axis=0)
        avgY = np.average(Y, axis=0)
        avgZ = np.average(Z, axis=0)


        # Update the plots
        sin.set_data(tsin, sine)
        # sx.set_offsets(np.c_[t, X[0]])
        tx.set_data(t, X[0])
        nx.set_data(t, X[1])
        ex.set_data(t, X[2])
        ax.set_data(t, avgX)
        
        ty.set_data(t, Y[0])
        ny.set_data(t, Y[1])
        ey.set_data(t, Y[2])
        ay.set_data(t, avgY)

        tz.set_data(t, Z[0])
        nz.set_data(t, Z[1])
        ez.set_data(t, Z[2])
        az.set_data(t, avgZ)

        if COMPLETEPLOT:
            plotxyz.set_title('X, Y, Z')
            ttx.set_data(t, X[0])
            tty.set_data(t, Y[0])
            ttz.set_data(t, Z[0])
            tnx.set_data(t, X[1])
            tny.set_data(t, Y[1])
            tnz.set_data(t, Z[1])
            tex.set_data(t, X[2])
            tey.set_data(t, Y[2])
            tez.set_data(t, Z[2])
        else:
            ttx.set_data(t, avgX)
            tty.set_data(t, avgY)
            ttz.set_data(t, avgZ)

        plotxyz.set_xlim(dt-10, dt)
                
        #combine all the plots
        plt.pause(0.001)

        if dt > (SAMPLETIME * 60): 
            print('done')
            plotxyz.set_xlim(0, dt)
            break
    except KeyboardInterrupt:
        break
        # pass
    except Exception as e:
        error = {'type': type(e), 'str' :traceback.format_exc()}
        print(f'type: {error["type"]} \n{error["str"]}')
        break

# Save the figure as a svg and the data as a json file
if error is None:
    dataTop = {'topX': topX.tolist(), 'topY': topY.tolist(), 'topZ': topZ.tolist()}
    dataNorth = {'northX': northX.tolist(), 'northY': northY.tolist(), 'northZ': northZ.tolist()}
    dataEast = {'eastX': eastX.tolist(), 'eastY': eastY.tolist(), 'eastZ': eastZ.tolist()}
    data = {'t': t.tolist(), 'top': dataTop, 'north': dataNorth, 'east': dataEast}
    filename = time.strftime('Guralp Sensor Data - %Y%m%d%H%M%S',time.localtime(time.time()))
    plt.savefig(f'data\svg\{filename}.svg', format='svg')
    plt.savefig(f'data\png\{filename}.png', format='png')
    with open(f'data\json\{filename} lowres.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)


# Turn off interactive mode
plt.ioff()
plt.show()

# Stop the program
adwin.Stop_Process(1)

# Close the figure
plt.close()

# Close the program
sys.exit()