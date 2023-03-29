import math
import sqlite3
import sys
import time
import traceback

import control
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from ADwin import ADwin, ADwinError
from peakdetect import peakdetect

plt.ion()

COMPLETEPLOT = False
SAMPLEPOINTS = 2500 # [points/batch]
FOURIERCALCULATED = False
SAFEFIGURE = {1: True , 2: False, 3: False}
SHOWGRAPH =  {1: False, 2: False, 3: False}
PERIOD = 1/1.4 * 14
FOURCALCTIME = PERIOD
MEASUREMENTTIME = FOURCALCTIME * 10 # [sec]
print(MEASUREMENTTIME)

# Create a new ADwin object
adwin = ADwin(DeviceNo= 1,raiseExceptions= 1, useNumpyArrays= 1)

BOOTFILE     = 'c:\ADwin\ADwin9.btl'
PROCESS1FILE = 'ADBasic/readTime.T91'
PROCESS2FILE = 'ADBasic/sendActuators.T92'
PROCESS3FILE = 'ADBasic/readGuralps.T93'
PROCESS4FILE = 'ADBasic/readExtras.T94'

ZMAT = np.matrix([[-1.745,	0.727,	1.534],
                  [-0.712,	1.02 , -0.724],
                  [ 1.0  ,  1.0  ,  1.0  ]])
ZMAT_INV = np.linalg.inv(ZMAT)
M = 24000 #[kg]

adwinPhases = {
    'eastX' : (lambda x: adwin.Set_FPar(62, x)),
    'westX' : (lambda x: adwin.Set_FPar(65, x)),
    'southY': (lambda x: adwin.Set_FPar(68, x)),
    'westY' : (lambda x: adwin.Set_FPar(71, x)),
    'southZ': (lambda x: adwin.Set_FPar(74, x)),
    'eastZ' : (lambda x: adwin.Set_FPar(77, x)),
    'westZ' : (lambda x: adwin.Set_FPar(80, x)),
}
adwinAmps = {
    'eastX' : (lambda x: adwin.Set_FPar(60, x)),
    'westX' : (lambda x: adwin.Set_FPar(63, x)),
    'southY': (lambda x: adwin.Set_FPar(66, x)),
    'westY' : (lambda x: adwin.Set_FPar(69, x)),
    'southZ': (lambda x: adwin.Set_FPar(72, x)),
    'eastZ' : (lambda x: adwin.Set_FPar(75, x)),
    'westZ' : (lambda x: adwin.Set_FPar(78, x)),
}
adwinFrequencies = {
    'eastX' : (lambda x: adwin.Set_FPar(61, x)),
    'westX' : (lambda x: adwin.Set_FPar(64, x)),
    'southY': (lambda x: adwin.Set_FPar(67, x)),
    'westY' : (lambda x: adwin.Set_FPar(70, x)),
    'southZ': (lambda x: adwin.Set_FPar(73, x)),
    'eastZ' : (lambda x: adwin.Set_FPar(76, x)),
    'westZ' : (lambda x: adwin.Set_FPar(79, x)),
}

error = None

t0 = 0
freq = 0

# Create the data arrays
def initDatabase():
    global date , meastime, cur, db
    meastime = time.localtime()
    date = time.strftime("%Y-%m-%d", meastime)
    meastime = time.strftime("%H%M%S", meastime)
    db = sqlite3.connect(f'data\{date} - {meastime}[Only guralps read].db')
    cur = db.cursor()
    cur.execute("CREATE TABLE guralp(t REAL PRIMARY KEY, topX REAL, topY REAL, topZ REAL, northX REAL, northY REAL, northZ REAL, eastX REAL, eastY REAL, eastZ REAL)")
    cur.execute("CREATE TABLE fourier(f REAL PRIMARY KEY, txamp REAL, txphase REAL, tyamp REAL, typhase REAL, tzamp REAL, tzphase REAL, nxamp REAL, nxphase REAL, nyamp REAL, nyphase REAL, nzamp REAL, nzphase REAL, examp REAL, exphase REAL, eyamp REAL, eyphase REAL, ezamp REAL, ezphase REAL)")
    cur.execute("CREATE TABLE extras(t REAL PRIMARY KEY, stepper REAL, accoustic REAL)")
    db.commit()

def initfig1():
    global fig1, fig1manager, plotxyz, plotx, ploty, plotz, topX, northX, eastX, ax, topY, northY, eastY, ay, topZ, northZ, eastZ, az, sinx, siny, sinz, ttopX, tnorthX, teastX, ttopY, tnorthY, teastY, ttopZ, tnorthZ, teastZ
    fig1 = plt.figure('XYZ-Data [INITIALIZING]', figsize=(15, 10))
    fig1manager = plt.get_current_fig_manager()
    SAFEFIGURE[1] = True

    #Create a Figure
    plotxyz = plt.subplot2grid((2,3), (1,0), colspan=3, )
    plotx   = plt.subplot2grid((2,3), (0,0), sharex=plotxyz, sharey=plotxyz, )
    ploty   = plt.subplot2grid((2,3), (0,1), sharex=plotxyz, sharey=plotxyz, )
    plotz   = plt.subplot2grid((2,3), (0,2), sharex=plotxyz, sharey=plotxyz, )

    topX, = plotx.plot([],[], '#ff0000', label= 'Top X')
    topY, = plotx.plot([],[], '#aa0000', label= 'Top Y')
    topZ, = plotx.plot([],[], '#550000', label= 'Top Z')
    ax, = plotx.plot([],[], 'k--', label= 'Average X')

    plotx.set_title('top')
    plotx.set_xlabel('Time (s)')
    plotx.set_ylabel('A (V)')
    plotx.set_xlim(0, 10)
    plotx.set_ylim(-1.5, 1.5)

    northX, = ploty.plot([],[], '#00ff00', label= 'North X')
    northY, = ploty.plot([],[], '#00aa00', label= 'North Y')
    northZ, = ploty.plot([],[], '#005500', label= 'North Z')
    ay, = ploty.plot([],[], 'k--', label= 'Average Y')

    ploty.set_title('north')
    ploty.set_xlabel('Time (s)')
    ploty.set_ylabel('A (V)')
    ploty.set_xlim(0, 10)
    ploty.set_ylim(-1.5, 1.5)

    eastX, = plotz.plot([],[], '#0000ff', label= 'East X')
    eastY, = plotz.plot([],[], '#0000aa', label= 'East Y')
    eastZ, = plotz.plot([],[], '#000055', label= 'East Z')
    az, = plotz.plot([],[], 'k--', label= 'Average Z')

    plotz.set_title('east')
    plotz.set_xlabel('Time (s)')
    plotz.set_ylabel('A (V)')
    plotz.set_xlim(0, 10)
    plotz.set_ylim(-1.5, 1.5)

    sinx, = plotx.plot([],[], 'gray', label='Sinus')
    siny, = ploty.plot([],[], 'gray', label='Sinus')
    sinz, = plotz.plot([],[], 'gray', label='Sinus')

    ttopX,ttopY,ttopZ,tnorthX,tnorthY,tnorthZ,teastX,teastY,teastZ= plotxyz.plot([],[], '#ff0000', [],[], '#aa0000', [],[], '#550000', 
                                                                                 [],[], '#00ff00', [],[], '#00aa00', [],[], '#005500',
                                                                                 [],[], '#0000ff', [],[], '#0000aa', [],[], '#000055', )

    if COMPLETEPLOT:
        plotxyz.set_title('X, Y, Z')
        ttopX.set_label('Top X')
        tnorthX.set_label('North X')
        teastX.set_label('East X')
        ttopY.set_label('Top Y')
        tnorthY.set_label('North Y')
        teastY.set_label('East Y')
        ttopZ.set_label('Top Z')
        tnorthZ.set_label('North Z')
        teastZ.set_label('East Z')
    else:
        plotxyz.set_title('X, Y, Z')
        ttopX.set_label('Average X')
        ttopY.set_label('Average Y')
        ttopZ.set_label('Average Z')

    plotxyz.set_xlabel('Time (s)')
    plotxyz.set_ylabel('A (V)')

    plotxyz.set_xlim(0, 10)
    plotxyz.set_ylim(-1.5, 1.5)

    plotx.legend()
    ploty.legend()
    plotz.legend()
    plotxyz.legend()

    fig1manager.window.showMaximized()
    plt.tight_layout()

def initfig2():
    global fig2, fig2manager, annlist, plotftx, plotfty, plotftz, plotfnx, plotfny, plotfnz, plotfex, plotfey, plotfez, lineftx, linefty, lineftz, linefnx, linefny, linefnz, linefex, linefey, linefez, plotVect, sVect, r1Vect, r2Vect, r3Vect
    SAFEFIGURE[2] = True

    fig2 = plt.figure('Fourier-Data [INITIALIZING]')
    fig2manager = plt.get_current_fig_manager()
    fig2.set_size_inches(12, 6)
    fig2.set_label('Fourier Analyses')
    annlist = np.array([])
    plotftx = fig2.add_subplot(3, 6, 1, )
    plotfty = fig2.add_subplot(3, 6, 7, sharex=plotftx, sharey=plotftx, )
    plotftz = fig2.add_subplot(3, 6, 13, sharex=plotftx, sharey=plotftx, )
    plotfnx = fig2.add_subplot(3, 6, 2, sharex=plotftx, sharey=plotftx, )
    plotfny = fig2.add_subplot(3, 6, 8, sharex=plotftx, sharey=plotftx, )
    plotfnz = fig2.add_subplot(3, 6, 14, sharex=plotftx, sharey=plotftx, )
    plotfex = fig2.add_subplot(3, 6, 3, sharex=plotftx, sharey=plotftx, )
    plotfey = fig2.add_subplot(3, 6, 9, sharex=plotftx, sharey=plotftx, )
    plotfez = fig2.add_subplot(3, 6, 15, sharex=plotftx, sharey=plotftx, )
    lineftx, = plotftx.plot([], [], 'k')
    linefty, = plotfty.plot([], [], 'k')
    lineftz, = plotftz.plot([], [], 'k')
    linefnx, = plotfnx.plot([], [], 'k')
    linefny, = plotfny.plot([], [], 'k')
    linefnz, = plotfnz.plot([], [], 'k')
    linefex, = plotfex.plot([], [], 'k')
    linefey, = plotfey.plot([], [], 'k')
    linefez, = plotfez.plot([], [], 'k')

    plotftx.set_title('Top x')
    plotfty.set_title('Top y')
    plotftz.set_title('Top z')
    plotfnx.set_title('North x')
    plotfny.set_title('North y')
    plotfnz.set_title('North z')
    plotfex.set_title('East x')
    plotfey.set_title('East y')
    plotfez.set_title('East z')

    plotftx.set_xlim(0, 50)
    plotftx.set_ylim(0, 0.25)

    plotVect = fig2.add_subplot(3, 6,(4,18))
    sVect = plotVect.quiver(0,0,0,0, angles='xy', scale_units='xy', scale=1, color='r')
    r1Vect = plotVect.quiver(0,0,0,0, angles='xy', scale_units='xy', scale=1, color='b')
    r2Vect = plotVect.quiver(0,0,0,0, angles='xy', scale_units='xy', scale=1, color='b')
    r3Vect = plotVect.quiver(0,0,0,0, angles='xy', scale_units='xy', scale=1, color='b')

    fig2.tight_layout()

def initfig3():
    global fig3, fig3manager, plotStepper, plotAccoustic, lineStepper, lineAccoustic, plotVect, sVect, r1Vect, r2Vect, r3Vect, stepperSignal, PTaccousticSignal
    fig3 = plt.figure("Extra Data [INITIALIZING]", figsize=(10,5))
    fig3manager = plt.get_current_fig_manager()
    SAFEFIGURE[3] = True

    plotStepper  = fig3.add_subplot(2,1,(1))
    plotAccoustic  = fig3.add_subplot(2,1,(2), sharex=plotStepper)

    lineStepper,  = plotStepper.plot([],[])
    lineAccoustic,  = plotAccoustic.plot([],[])



    plt.pause(0.001)

def initAdwin():
    # Load the program
    adwin.Boot(Filename=BOOTFILE)               # Load the boot file and boot the ADwin
    adwin.Load_Process(Filename=PROCESS1FILE)   # Load process 1
    adwin.Load_Process(Filename=PROCESS2FILE)   # Load process 2
    adwin.Load_Process(Filename=PROCESS3FILE)   # Load process 3
    adwin.Load_Process(Filename=PROCESS4FILE)   # Load process 4
    adwin.Set_Par(80, 1)
    # Start the program
    adwin.Start_Process(ProcessNo= 1)           # Start process 1
    adwin.Start_Process(ProcessNo= 2)           # Start process 2
    adwin.Start_Process(ProcessNo= 3)           # Start process 3
    adwin.Start_Process(ProcessNo= 4)           # Start process 4

def init():
    '''Initialize '''
    global t0
    in1 = input('show XYZ-data: Y/[N]\n')
    in2 = input('show Fourier data: Y/[N]\n')
    in3 = input('show Extra\'s data: Y/[N]\n')
    SHOWGRAPH[1] = True if in1.lower() in ["yes", "y"] else False
    SHOWGRAPH[2] = True if in2.lower() in ["yes", "y"] else False
    SHOWGRAPH[3] = True if in3.lower() in ["yes", "y"] else False
    
    initDatabase()
    for i in SHOWGRAPH:
        if SHOWGRAPH[i]:
            eval(f'initfig{i}()')
    initAdwin()
    
def main():
    global FOURCALCTIME, sVect, r1Vect, r2Vect, r3Vect, lineStepper, lineAccoustic, plotStepper, plotAccoustic, plotVect, plotftx, plotfty, plotftz, plotfnx, plotfny, plotfnz, plotfex, plotfey, plotfez, lineftx, linefty, lineftz, linefnx, linefny, linefnz, linefex, linefey, linefez, fig1, fig2, fig3, FOURIERCALCULATED, SAMPLEPOINTS, adwin
    
    if SHOWGRAPH[1]:
        fig1manager.set_window_title('XYZ-Data [RUNNING]')
    if SHOWGRAPH[2]:
        fig2manager.set_window_title('Fourier-Data [RUNNING]')
    if SHOWGRAPH[3]:
        fig3manager.set_window_title('Extra Data [RUNNING]')

    try:
        tstart = time.time()
        # Read the data
        while True:
            try:
                readData()

                if time.time() - tstart >= 120:
                    plotxyz.axvline(time.time()-tstart)
                    ploty.axvline(time.time()-tstart)
                    plotz.axvline(time.time()-tstart)
                    plotx.axvline(time.time()-tstart)
                    tstart = time.time()

            except KeyboardInterrupt:
                break



    except KeyboardInterrupt as ke:
        error = {'type': type(ke), 'str' :traceback.format_exc()}
        print(f'type: {error["type"]} \n{error["str"]}')
    except Exception as e:
        error = {'type': type(e), 'str' :traceback.format_exc()}
        print(f'type: {error["type"]} \n{error["str"]}')
def gettime():
    adwintime = cur.execute('SELECT MAX(t) FROM guralp').fetchone()[0]
    adwintime = adwintime if adwintime is not None else 0
    return adwintime

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

        data = np.array([dataT, dataTX, dataTY, dataTZ, dataNX, dataNY, dataNZ, dataEX, dataEY, dataEZ])
        cur.executemany('INSERT INTO guralp VALUES (?,?,?,?,?,?,?,?,?,?)', np.transpose(data).tolist())
        
        db.commit()

        if True in SHOWGRAPH.values():
            updatePlot()

def saveFigures():
    '''Save the figure as a svg and the data as a json file'''
    if error is None:
        if SAFEFIGURE[1] and SHOWGRAPH[1]:
            filename = time.strftime('Guralp Sensor Data - %Y%m%d%H%M%S')
            fig1.savefig(f'data/Guralp/svg/{filename}.svg', format='svg')
            fig1.savefig(f'data/Guralp/png/{filename}.png', format='png')
        if SAFEFIGURE[2] and SHOWGRAPH[2]:
            filename = time.strftime('fourier - %Y%m%d%H%M%S')
            fig2.savefig(f'data/fourier/svg/{filename}.svg', format='svg')
            fig2.savefig(f'data/fourier/png/{filename}.png', format='png')
        if SAFEFIGURE[3] and SHOWGRAPH[3]:
            filename = time.strftime('extra\'s - %Y%m%d%H%M%S')
            fig2.savefig(f'data/Extra data/svg/{filename}.svg', format='svg')
            fig2.savefig(f'data/Extra data/png/{filename}.png', format='png')

def updatePlot(COMPLETETIME:bool = False):
    if SHOWGRAPH[1]:
        query = """
        SELECT *
        FROM guralp
        ORDER BY t DESC
        LIMIT 5000;
        """ if not COMPLETETIME else """
        SELECT *
        FROM guralp
        ORDER BY t DESC;
        """

        cur.execute("""
        PRAGMA table_info(guralp);
        """)
        names = np.transpose(cur.fetchall())[1]
        cur.execute(query)
        ret = np.transpose(cur.fetchall())

        for name, data in zip(names, ret):
            if name == 't':
                plotxyz.set_xlim(ret[0][-1], ret[0][0])
                continue
            eval(f"{name}.set_data(ret[0], data)")
            eval(f"t{name}.set_data(ret[0], data)")
        plt.pause(0.01)

def calculateZamps(amplitude):
    Fz = np.matrix([[0],
                    [0],
                    [M * amplitude]])
    return (ZMAT_INV * Fz)
def setZs(amplitude, phase, frequency):
    adwinAmps['eastZ'](amplitude[0,0])
    adwinAmps['southZ'](amplitude[1,0])
    adwinAmps['westZ'](amplitude[2,0])
    adwinPhases['eastZ'](phase)
    adwinPhases['southZ'](phase)
    adwinPhases['westZ'](phase)
    adwinFrequencies['eastZ'](frequency)
    adwinFrequencies['southZ'](frequency)
    adwinFrequencies['westZ'](frequency)



def calculateFourier():
    global FOURIERCALCULATED, FOURCALCTIME, plotVect, sVect, r1Vect, r2Vect, r3Vect, annlist

    cur.execute('SELECT MAX(t) FROM guralp;')
    res = cur.fetchone()
    curt = res[0] if res[0] is not None else 0
    if curt > FOURCALCTIME:# and not FOURIERCALCULATED:

        cur.execute(f'SELECT * FROM guralp WHERE t BETWEEN {FOURCALCTIME-PERIOD} AND {FOURCALCTIME}')
        res = np.array(cur.fetchall())
        if len(res) > 0:
            data = {'t': res[:,0], 'tx': res[:,1], 'ty': res[:,2], 'tz': res[:,3], 'nx': res[:,4], 'ny': res[:,5], 'nz': res[:,6], 'ex': res[:,7], 'ey': res[:,8], 'ez': res[:,9]}

        tpCount = len(data['t'])
        values = np.arange(int(tpCount/2))
        timePeriod = tpCount / 1000
        frequencies = values / timePeriod
        cur.execute('DELETE FROM fourier')
        for freq in frequencies:
            cur.execute(f'INSERT INTO fourier(f) VALUES ({freq})')
        db.commit()

        if SHOWGRAPH[2]:
            for j in annlist:
                j.remove()
            annlist = []
        topamp = {}
        topfreq = {}
        topphase = {}
        for key in data:
            if key == 't':
                continue

            fourierTransform = np.fft.fft(data[key])/len(data[key])
            fourierTransform = fourierTransform[range(int(len(data[key])/2))]
            fourierTransform[1:] = 2* fourierTransform[1:]
            amp = np.abs(fourierTransform)
            phase = np.angle(fourierTransform)

            desf = 1.4 * np.ones_like(frequencies)


            f = np.argmin(np.abs(desf-frequencies))

            topamp[key] = amp[f]
            topfreq[key] = frequencies[f]
            topphase[key] = phase[f]
            
            cur.executemany(f'UPDATE fourier SET {key}amp = ?, {key}phase = ? WHERE f = ?', np.transpose([amp, phase, frequencies]).tolist())
            if SHOWGRAPH[2]:
                eval(f'linef{key}.set_data(frequencies, amp)')
                eval(f'annotateFourier(plotf{key}, topfreq[\'{key}\'], topamp[\'{key}\'], topphase[\'{key}\'])')

        db.commit()

        FOURIERCALCULATED = True
        FOURCALCTIME += PERIOD

        return topamp, topfreq, topphase

def annotateFourier(plot:plt.Axes, freq, amp, phase ):
   
    label = f'''$f = {freq:.4f} [Hz]$
    $A = {amp:.2f}$
    $\\varphi = {phase:.2f} [rad]$'''
    annlist.append(plot.annotate(label, (freq, amp), textcoords= "offset points", xytext=(30,10), ha= 'center'))



if __name__ == '__main__':
    init()
    main()
    print('done')
    
    adwin.Set_Par(80, 0)
    time.sleep(0.020)
    # Stop the program
    adwin.Stop_Process(1)
    adwin.Stop_Process(2)
    adwin.Stop_Process(3)
    
    if True in SHOWGRAPH.values() and error is None:
        # Turn off interactive mode
        if SHOWGRAPH[1]:

            updatePlot(True)
            fig1manager.set_window_title("XYZ-Data [DONE]")
            plotx.legend(loc= 'upper right')
            ploty.legend(loc = 'upper right')
            plotz.legend(loc= 'upper right')
            plotxyz.legend(loc = 'upper right')
        if SHOWGRAPH[2]:
            fig2manager.set_window_title("Fourier-Data [DONE]")
            plotVect.autoscale_view()
        if SHOWGRAPH[3]:
            fig3manager.set_window_title("Extra Data [INITIALIZING]")
        
        plt.ioff()
        plt.show()
        plt.pause(0.001)
        # Close the figure
        plt.close()
        saveFigures()
    # Close the program
    sys.exit()