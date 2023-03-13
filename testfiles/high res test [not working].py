import sys,traceback, time, math, sqlite3
from ADwin import ADwin, ADwinError
import numpy as np, control
from peakdetect import peakdetect
import matplotlib.pyplot as plt, matplotlib.animation as animation

plt.ion()

COMPLETEPLOT = False
MEASUREMENTTIME = 60 # [sec]
SAMPLEPOINTS = 2500 # [points/batch]
FOURIERCALCULATED = False
SAFEFIGURE = True
SHOWGRAPH = True

# Create a new ADwin object
adwin = ADwin(DeviceNo= 1,raiseExceptions= 1, useNumpyArrays= 1)

BOOTFILE = 'c:\ADwin\ADwin9.btl'
PROCESS1FILE = 'ADBasic/readGuralps.T91'
PROCESS2FILE = 'ADBasic/readExtras.T92'
PROCESS3FILE = 'ADBasic/sendActuators.T93'

error = None

t0 = 0
freq = 0
omegaX = 2 * math.pi * freq
omegaY = 2 * math.pi * freq
omegaZ = 2 * math.pi * freq
phaseX = 0
phaseY = 0
phaseZ = 0
topampX = 0
topampY = 0
topampZ = 0

# Create the data arrays
t      = np.zeros((0))

X      = np.zeros((0,3))
Y      = np.zeros((0,3))
Z      = np.zeros((0,3))
topX   = np.zeros((0))
topY   = np.zeros((0))
topZ   = np.zeros((0))
northX = np.zeros((0))
northY = np.zeros((0))
northZ = np.zeros((0))
eastX  = np.zeros((0))
eastY  = np.zeros((0))
eastZ  = np.zeros((0))
sinex   = np.zeros((0))
siney   = np.zeros((0))
sinez   = np.zeros((0))
avgX = np.array([])
avgY = np.array([])
avgZ = np.array([])

def initDatabase():
    global date , meastime, cur, db
    meastime = time.localtime()
    date = time.strftime("%Y-%m-%d", meastime)
    meastime = time.strftime("%H%M%S", meastime)
    db = sqlite3.connect(f'data\{date} - {meastime}.db')
    cur = db.cursor()
    cur.execute("CREATE TABLE guralp(t REAL PRIMARY KEY, topX REAL, topY REAL, topZ REAL, northX REAL, northY REAL, northZ REAL, eastX REAL, eastY REAL, eastZ REAL)")
    cur.execute("CREATE TABLE fourier(f REAL PRIMARY KEY, txamp REAL, txphase REAL, tyamp REAL, typhase REAL, tzamp REAL, tzphase REAL, nxamp REAL, nxphase REAL, nyamp REAL, nyphase REAL, nzamp REAL, nzphase REAL, examp REAL, exphase REAL, eyamp REAL, eyphase REAL, ezamp REAL, ezphase REAL)")
    cur.execute("CREATE TABLE extras(t REAL PRIMARY KEY, stepper REAL, accoustic REAL)")
    db.commit()
def initfig1():
    global fig1, plotxyz, plotx, ploty, plotz, tx, nx, ex, ax, ty, ny, ey, ay, tz, nz, ez, az, t, topX, northX, eastX, avgX, topY, northY, eastY, avgY, topZ, northZ, eastZ, avgZ, sinx, siny, sinz, ttx, tnx, tex, tty, tny, tey, ttz, tnz, tez
    fig1 = plt.figure('XYZ-Data', figsize=(15, 10))

    #Create a Figure
    plotxyz = plt.subplot2grid((2,3), (1,0), colspan=3)
    plotx   = plt.subplot2grid((2,3), (0,0), sharex=plotxyz, sharey=plotxyz)
    ploty   = plt.subplot2grid((2,3), (0,1), sharex=plotxyz, sharey=plotxyz)
    plotz   = plt.subplot2grid((2,3), (0,2), sharex=plotxyz, sharey=plotxyz)

    tx, = plotx.plot(t, topX, '#ff0000', label= 'Top X')
    nx, = plotx.plot(t, northX, '#aa0000', label= 'North X')
    ex, = plotx.plot(t, eastX, '#550000', label= 'East X')
    ax, = plotx.plot(t, avgX, 'k--', label= 'Average X')

    plotx.set_title('X')
    plotx.set_xlabel('Time (s)')
    plotx.set_ylabel('A (V)')
    plotx.set_xlim(0, 10)
    plotx.set_ylim(-1.5, 1.5)

    ty, = ploty.plot(t, topY, '#00ff00', label= 'Top Y')
    ny, = ploty.plot(t, northY, '#00aa00', label= 'North Y')
    ey, = ploty.plot(t, eastY, '#005500', label= 'East Y')
    ay, = ploty.plot(t, avgY, 'k--', label= 'Average Y')

    ploty.set_title('Y')
    ploty.set_xlabel('Time (s)')
    ploty.set_ylabel('A (V)')
    ploty.set_xlim(0, 10)
    ploty.set_ylim(-1.5, 1.5)

    tz, = plotz.plot(t, topZ, '#0000ff', label= 'Top Z')
    nz, = plotz.plot(t, northZ, '#0000aa', label= 'North Z')
    ez, = plotz.plot(t, eastZ, '#000055', label= 'East Z')
    az, = plotz.plot(t, avgZ, 'k--', label= 'Average Z')

    plotz.set_title('Z')
    plotz.set_xlabel('Time (s)')
    plotz.set_ylabel('A (V)')
    plotz.set_xlim(0, 10)
    plotz.set_ylim(-1.5, 1.5)

    sinx, = plotx.plot(t, sinex, 'gray', label='Sinus')
    siny, = ploty.plot(t, siney, 'gray', label='Sinus')
    sinz, = plotz.plot(t, sinez, 'gray', label='Sinus')

    ttx,tnx,tex,tty,tny,tey,ttz,tnz,tez= plotxyz.plot(t, topX, '#ff0000', t, northX, '#aa0000', t, eastX, '#550000', 
                                                    t, topY, '#00ff00', t, northY, '#00aa00', t, eastY, '#005500',
                                                    t, topZ, '#0000ff', t, northZ, '#0000aa', t, eastZ, '#000055',)

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

    plotxyz.set_xlim(0, 10)
    plotxyz.set_ylim(-1.5, 1.5)

    mng = plt.get_current_fig_manager()
    mng.window.showMaximized()
    plt.tight_layout()
def initfig2():
    global fig2, plotftx, plotfty, plotftz, plotfnx, plotfny, plotfnz, plotfex, plotfey, plotfez, lineftx, linefty, lineftz, linefnx, linefny, linefnz, linefex, linefey, linefez
    fig2 = plt.figure('Fourier-Data')
    fig2.set_size_inches(9, 9)
    fig2.set_label('Fourier Analyses')
    plotftx = fig2.add_subplot(331)
    plotfty = fig2.add_subplot(334, sharex=plotftx, sharey=plotftx)
    plotftz = fig2.add_subplot(337, sharex=plotftx, sharey=plotftx)
    plotfnx = fig2.add_subplot(332, sharex=plotftx, sharey=plotftx)
    plotfny = fig2.add_subplot(335, sharex=plotftx, sharey=plotftx)
    plotfnz = fig2.add_subplot(338, sharex=plotftx, sharey=plotftx)
    plotfex = fig2.add_subplot(333, sharex=plotftx, sharey=plotftx)
    plotfey = fig2.add_subplot(336, sharex=plotftx, sharey=plotftx)
    plotfez = fig2.add_subplot(339, sharex=plotftx, sharey=plotftx)
    lineftx, = plotftx.plot([1], [1], 'k')
    linefty, = plotfty.plot([1], [1], 'k')
    lineftz, = plotftz.plot([1], [1], 'k')
    linefnx, = plotfnx.plot([1], [1], 'k')
    linefny, = plotfny.plot([1], [1], 'k')
    linefnz, = plotfnz.plot([1], [1], 'k')
    linefex, = plotfex.plot([1], [1], 'k')
    linefey, = plotfey.plot([1], [1], 'k')
    linefez, = plotfez.plot([1], [1], 'k')

    plotftx.set_xlim(0, 50)
    plotftx.set_ylim(0, 0.25)
    fig2.tight_layout()
def initfig3():
    global fig3, plotStepper, plotAccoustic, lineStepper, lineAccoustic, plotVect, sVect, r1Vect, r2Vect, r3Vect, stepperSignal, PTaccousticSignal
    fig3 = plt.figure("Extra's", figsize=(10,5))

    plotStepper  = fig3.add_subplot(2,4,(1,2))
    plotAccoustic  = fig3.add_subplot(2,4,(5,6), sharex=plotStepper)

    lineStepper,  = plotStepper.plot([],[])
    lineAccoustic,  = plotAccoustic.plot([],[])

    plotVect = fig3.add_subplot(2,4,(3,8))
    sVect = plotVect.quiver(0,0,0,0, angles='xy', scale_units='xy', scale=1, color='r')
    r1Vect = plotVect.quiver(0,0,0,0, angles='xy', scale_units='xy', scale=1, color='b')
    r2Vect = plotVect.quiver(0,0,0,0, angles='xy', scale_units='xy', scale=1, color='b')
    r3Vect = plotVect.quiver(0,0,0,0, angles='xy', scale_units='xy', scale=1, color='b')

    plotVect.set_xlim(-1, 1)
    plotVect.set_ylim(-1, 1)

    plt.pause(0.001)

def init():
    '''Initialize '''
    global t0
    # Load the program
    adwin.Boot(Filename=BOOTFILE)               # Load the boot file and boot the ADwin
    adwin.Load_Process(Filename=PROCESS1FILE)   # Load process 1
    adwin.Load_Process(Filename=PROCESS2FILE)   # Load process 2
    adwin.Load_Process(Filename=PROCESS3FILE)   # Load process 3
    
    initDatabase()
    initfig1()
    initfig2()
    initfig3()

    # Start the program
    adwin.Start_Process(ProcessNo= 1)           # Start process 1
    adwin.Start_Process(ProcessNo= 2)           # Start process 2
    adwin.Start_Process(ProcessNo= 3)           # Start process 3

    t0 = time.time()
def main():
    global fourierTransformX, fourierTransformY, fourierTransformZ, frequencies, topX, topY, topZ, northX, northY, northZ, eastX, eastY, eastZ, t0, dt, t, topampX, topampY, topampZ, topfreqX, topfreqY, topfreqZ, sVect, r1Vect, r2Vect, r3Vect, lineStepper, lineAccoustic, plotStepper, plotAccoustic, plotVect, plotftx, plotfty, plotftz, plotfnx, plotfny, plotfnz, plotfex, plotfey, plotfez, lineftx, linefty, lineftz, linefnx, linefny, linefnz, linefex, linefey, linefez, fig1, fig2, fig3, omegaX, omegaY, omegaZ, phaseX, phaseY, phaseZ, FOURIERCALCULATED, SAMPLEPOINTS, adwin
    try:
        while True:
            try:
                # Read the data
                t1 = time.time()
                # Calculate the time since start
                dt = t1 - t0

                # Read the data
                readData()
                
                # Update the data arrays 
                X = np.array([topX, northX, eastX])
                Y = np.array([topY, northY, eastY])
                Z = np.array([topZ, northZ, eastZ])


                calculateFourier()

                
                    
                # lineStepper.set_data(t[1:], stepperSignal[1:])
                # plotStepper.set_xlim(t[-1] -10, t[-1])
                # plotStepper.set_ylim(np.min(stepperSignal)-0.2, np.max(stepperSignal)+0.2)
                # lineAccoustic.set_data(t[1:], PTaccousticSignal[1:])
                # plotAccoustic.set_xlim(t[-1] -10, t[-1])
                # plotAccoustic.set_ylim(np.min(PTaccousticSignal)-0.2, np.max(PTaccousticSignal)+0.2)
                
                print(f't: {t[-1]:.2f}\ttopampX: {topampX}\tomegaX: {omegaX}\tphaseX: {phaseX}')
                sinex = topampX * np.sin(omegaX * t - phaseX)
                siney = topampY * np.sin(omegaX * t - phaseY)
                sinez = topampZ * np.sin(omegaX * t - phaseZ)

                sinx.set_data(t, sinex)
                siny.set_data(t, siney)
                sinz.set_data(t, sinez)

                ax.set_data(t, avgX)
                ay.set_data(t, avgY)
                az.set_data(t, avgZ)

                if COMPLETEPLOT:
                    tx.set_data(t, X[0])
                    nx.set_data(t, X[1])
                    ex.set_data(t, X[2])
                    ty.set_data(t, Y[0])
                    ny.set_data(t, Y[1])
                    ey.set_data(t, Y[2])
                    tz.set_data(t, Z[0])
                    nz.set_data(t, Z[1])
                    ez.set_data(t, Z[2])
                    
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

                plotxyz.set_xlim(t[-1]-10, t[-1])

                plt.pause(0.001)

                if t[-1] > (MEASUREMENTTIME): 
                    print('done')

                    plotxyz.set_xlim(0, t[-1])
                    plotStepper.set_xlim(0, t[-1])
                    plotAccoustic.set_xlim(0, t[-1])
                    break
            except KeyboardInterrupt:
                break
                # pass
            except Exception as e:
                error = {'type': type(e), 'str' :traceback.format_exc()}
                print(f'type: {error["type"]} \n{error["str"]}')
                break
    except KeyboardInterrupt as e:
        error = {'type': type(e), 'str' :traceback.format_exc()}
        print(f'type: {error["type"]} \n{error["str"]}')

def annotateFourier():
    global fourierTransformX, fourierTransformY, fourierTransformZ, frequencies
    for a in topampX:
        index = np.where(abs(fourierTransformX) == a)[0][0]
        amp = a
        freq = frequencies[index]
        label = f'{amp:.2f}@{freq:.2f}'
        plotftx.annotate(label, (freq, amp), textcoords= "offset points", xytext=(30,10), ha= 'center')
        plotfnx.annotate(label, (freq, amp), textcoords= "offset points", xytext=(30,10), ha= 'center')
        plotfex.annotate(label, (freq, amp), textcoords= "offset points", xytext=(30,10), ha= 'center')
    for a in topampY:
        index = np.where(abs(fourierTransformY) == a)[0][0]
        amp = a
        freq = frequencies[index]
        label = f'{amp:.2f}@{freq:.2f}'
        plotfty.annotate(label, (freq, amp), textcoords= "offset points", xytext=(30,10), ha= 'center')
        plotfny.annotate(label, (freq, amp), textcoords= "offset points", xytext=(30,10), ha= 'center')
        plotfey.annotate(label, (freq, amp), textcoords= "offset points", xytext=(30,10), ha= 'center')
    for a in topampZ:
        index = np.where(abs(fourierTransformZ) == a)[0][0]
        amp = a
        freq = frequencies[index]
        label = f'{amp:.2f}@{freq:.2f}'
        plotftz.annotate(label, (freq, amp), textcoords= "offset points", xytext=(30,10), ha= 'center')
        plotfnz.annotate(label, (freq, amp), textcoords= "offset points", xytext=(30,10), ha= 'center')
        plotfez.annotate(label, (freq, amp), textcoords= "offset points", xytext=(30,10), ha= 'center')

def readData():
    if adwin.Fifo_Full(10) >= SAMPLEPOINTS:
        dataTX = adwin.GetFifo_Float(1, SAMPLEPOINTS)
        dataTY = adwin.GetFifo_Float(2, SAMPLEPOINTS)
        dataTZ = adwin.GetFifo_Float(3, SAMPLEPOINTS)
        dataNX = adwin.GetFifo_Float(4, SAMPLEPOINTS)
        dataNY = adwin.GetFifo_Float(5, SAMPLEPOINTS)
        dataNZ = adwin.GetFifo_Float(6, SAMPLEPOINTS)
        dataEX = adwin.GetFifo_Float(7, SAMPLEPOINTS)
        dataEY = adwin.GetFifo_Float(8, SAMPLEPOINTS)
        dataEZ = adwin.GetFifo_Float(9, SAMPLEPOINTS)
        dataT = adwin.GetFifo_Float(10, SAMPLEPOINTS)

        data = np.array(dataT, dataTX, dataTY, dataTZ, dataNX, dataNY, dataNZ, dataEX, dataEY, dataEZ)
        cur.executemany('INSERT INTO guralp VALUES (?,?,?,?,?,?,?,?,?,?)', np.transpose(data))
        
        dataStepper = adwin.GetFifo_Float(20, SAMPLEPOINTS)
        dataAccoustic = adwin.GetFifo_Float(21, SAMPLEPOINTS)
        data = np.array([t, dataStepper, dataAccoustic])
        cur.executemany('INSERT INTO extras VALUES (?,?,?)', np.transpose(data))
        db.commit()

def saveData():
    '''Save the figure as a svg and the data as a json file'''
    if error is None:
        if SAFEFIGURE:
            filename = time.strftime('Guralp Sensor Data - %Y%m%d%H%M%S',time.localtime(time.time()))
            fig1.savefig(f'data/Guralp/svg/{filename}.svg', format='svg')
            fig1.savefig(f'data/Guralp/png/{filename}.png', format='png')

            filename = time.strftime('fourier - %Y%m%d%H%M%S',time.localtime(time.time()))
            fig2.savefig(f'data/fourier/svg/{filename}.svg', format='svg')
            fig2.savefig(f'data/fourier/png/{filename}.png', format='png')

    # Turn off interactive mode
    plt.ioff()
    plt.show()

def calculateFourier():
    global FOURIERCALCULATED

    cur.execute('SELECT * FROM guralp')
    res = np.array(cur.fetchall())
   
    data = {'t': res[:,0], 'tx': res[:,1], 'ty': res[:,2], 'tz': res[:,3], 'nx': res[:,4], 'ny': res[:,5], 'nz': res[:,6], 'ex': res[:,7], 'ey': res[:,8], 'ez': res[:,9]}

    if len(res) > 0 and (t[-1] > 10 and not FOURIERCALCULATED):
        i = np.where(data['t'] > 10)[0][0]
        FOURIERCALCULATED = True

        tpCount = len(data['t'][:i])
        values = np.arange(int(tpCount/2))
        timePeriod = tpCount / 1000
        frequencies = values / timePeriod
        for freq in frequencies:
            cur.execute(f'INSERT INTO fourier(f) VALUES ({freq})')
        db.commit()

        for key in data:
            if key == 't':
                continue

            fourierTransform = np.fft.fft(data[key][:i])/len(data[key][:i])
            fourierTransform = fourierTransform[range(int(len(data[key][:i])/2))]
            amp = np.abs(fourierTransform)
            phase = np.angle(fourierTransform)

            cur.executemany(f'UPDATE fourier SET {key} = ?, {key}phase = ? WHERE f = ?', np.transpose([amp, phase, frequencies]))

        db.commit()



        # peaks = peakdetect(PTaccousticSignal, t, lookahead=100)
        # omegaX = 2 * np.pi * topfreqX
        # omegaY = 2 * np.pi * topfreqY
        # omegaZ = 2 * np.pi * topfreqZ

        # adwin.Set_FPar(20, topfreqZ)
        # adwin.Set_FPar(21, phaseZ)

        # plotVect.cla()
        # plotVect.set_xlim(-1,1)
        # plotVect.set_ylim(-1,1)

        # u,v = topampX * math.cos(phaseX),topampX * math.sin(phaseX)
        # sVect = plotVect.quiver(0,0,u,v, angles='xy', scale_units='xy', scale=1, color='r')
        # rx, ry = topampX * np.cos(phaseX), topampX * np.sin(phaseX)
        # r1u, r1v = topampX * math.cos(phaseX), topampX * math.sin(phaseX)
        # r2u, r2v = topampX * math.cos(phaseX + math.radians(120)), topampX * math.sin(phaseX + math.radians(120))
        # r3u, r3v = topampX * math.cos(phaseX - math.radians(120)), topampX * math.sin(phaseX - math.radians(120))
        # r1Vect  = plotVect.quiver(rx, ry, r1u, r1v, angles='xy', scale_units='xy', scale=1, color='b')
        # r2Vect  = plotVect.quiver(rx, ry, r2u, r2v, angles='xy', scale_units='xy', scale=1, color='b')
        # r3Vect  = plotVect.quiver(rx, ry, r3u, r3v, angles='xy', scale_units='xy', scale=1, color='b')


if __name__ == '__main__':
    init()
    main()
    annotateFourier()
    saveData()

    # Stop the program
    adwin.Stop_Process(1)
    adwin.Stop_Process(2)
    adwin.Stop_Process(3)

    plotx.legend(loc= 'upper right')
    ploty.legend(loc = 'upper right')
    plotz.legend(loc= 'upper right')
    plotxyz.legend(loc = 'upper right')
    plt.pause(0.001)

    # Close the figure
    plt.close()

    # Close the program
    sys.exit()