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
ZMAT = np.matrix([
#     Fe    |  Fs    | Fw
    [ 1     ,  1     , 1    ],  # sum(Fz)
    [-1.745 ,  0.727 , 1.534],  # sum(Mx)
    [ 0.712 , -1.02  , 0.724],  # sum(My)
])
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
    db = sqlite3.connect(f'data\{date} - {meastime}.db')
    cur = db.cursor()
    cur.executescript("""
BEGIN;
CREATE TABLE guralp(
    t REAL PRIMARY KEY, 
    topX REAL, topY REAL,topZ REAL, 
    northX REAL, northY REAL, northZ REAL, 
    eastX REAL, eastY REAL, eastZ REAL
);
CREATE TABLE DoF(
    t REAL PRIMARY KEY,
    x REAL,
    y REAL,
    z REAL,
    rx REAL,
    ry REAL,
    rz REAL,
    FOREIGN KEY(t) REFERENCES guralp(t)
);
CREATE TABLE fourier(
    f REAL PRIMARY KEY,
    txamp REAL, txphase REAL, tyamp REAL, typhase REAL, tzamp REAL, tzphase REAL, 
    nxamp REAL, nxphase REAL, nyamp REAL, nyphase REAL, nzamp REAL, nzphase REAL, 
    examp REAL, exphase REAL, eyamp REAL, eyphase REAL, ezamp REAL, ezphase REAL
);
CREATE TABLE extras(t REAL PRIMARY KEY, stepper REAL, accoustic REAL);
COMMIT;
""")
    
def initfig1():
    global fig1, fig1manager
    global plotx, ploty, plotz, plotrx, plotry, plotrz
    global linex, liney, linez, linerx, linery, linerz

    fig1, (plotx, ploty,plotz, plotrx,plotry,plotrz) = plt.subplots(6,1, sharex=True, sharey=True)
    plt.tight_layout()
    fig1.subplots_adjust(hspace=0)
    fig1manager = plt.get_current_fig_manager()

    linex, = plotx.plot([],[], 'b')
    liney, = ploty.plot([],[], 'b')
    linez, = plotz.plot([],[], 'b')
    linerx, = plotrx.plot([],[], 'b')
    linery, = plotry.plot([],[], 'b')
    linerz, = plotrz.plot([],[], 'b')

    fig1manager.window.showMaximized()

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
    adwin.Start_Process(ProcessNo= 4)           # Start process 3

def init():
    '''Initialize '''
    global t0

    
    initDatabase()
    initfig1()
    initAdwin()
    
def main():
    global FOURCALCTIME, fig1, FOURIERCALCULATED, SAMPLEPOINTS, adwin
    
    fig1manager.set_window_title('6DoF-Data [RUNNING]')

    try:
        # Read the data
        tstart = time.time()
        t0 = time.time()
        freqs = np.linspace(0,5,30)
        i = 0
        tdur = 1/freqs[1] * 5
        print(tdur)
        while True:
            try:
                readData()

                if (time.time() - tstart) >= (tdur):
                    i += 1
                    tdur = 1/freqs[i] * 5
                    print(tdur)
                    
                    if i == len(freqs):
                        break

                    # [Fe, Fs, Fw] = calculateZamps(1)
                    # adwinAmps['eastZ'](Fe)
                    # adwinAmps['southZ'](Fs)
                    # adwinAmps['westZ'](Fw)

                    
                    adwinFrequencies['eastZ'](freqs[i])
                    adwinFrequencies['southZ'](freqs[i])
                    adwinFrequencies['westZ'](freqs[i])
                    fig1manager.set_window_title(f'6DoF-Data [RUNNING] ({freqs[i]})')
                    tstart = time.time()

                    plotx.axvline(x = (tstart-t0))
                    ploty.axvline(x = (tstart-t0))
                    plotz.axvline(x = (tstart-t0))
                    plotrx.axvline(x = (tstart-t0))
                    plotry.axvline(x = (tstart-t0))
                    plotrz.axvline(x = (tstart-t0))
                    
                plt.pause(0.01)
                        
        
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
        
        dataStepper = adwin.GetFifo_Float(20, SAMPLEPOINTS)
        dataAccoustic = adwin.GetFifo_Float(21, SAMPLEPOINTS)
        data = np.array([dataT, dataStepper, dataAccoustic])
        cur.executemany('INSERT INTO extras VALUES (?,?,?)', np.transpose(data).tolist())
        db.commit()

        calculate6DoF(dataT, -dataNY, dataNZ, -dataEX, dataEZ, -dataTX, -dataTY)
            
        updatePlot()

def calculate6DoF(t,ny,nz,ex,ez,tx,ty):
        
    meas = np.matrix([ny, nz, ex, ez, tx, ty])
    meas /= 1000


    outmat = AMAT_INV * meas
    outmat = np.array(outmat)
    outmat = np.array([t,outmat[0],outmat[1],outmat[2],outmat[3],outmat[4],outmat[5]])
    cur.executemany('INSERT INTO DoF VALUES (?,?,?,?,?,?,?)', np.transpose(outmat))
    db.commit()



def saveFigures(prefix:str = ''):
    '''Save the figure as a svg and the data as a json file'''
    if error is None:

        filename = time.strftime('Guralp Sensor Data - %Y%m%d%H%M%S')
        prefix = f'[{prefix}]' if prefix is not '' else ''
        fig1.savefig(f'data/xyz/svg/{prefix}{filename}.svg', format='svg')
        fig1.savefig(f'data/xyz/png/{prefix}{filename}.png', format='png')


def updatePlot(COMPLETETIME:bool = False):
    query = """
    SELECT *
    FROM DoF
    ORDER BY t DESC
    LIMIT 5000;
    """ if not COMPLETETIME else """
    SELECT *
    FROM DoF
    ORDER BY t DESC;
    """
    ret = cur.execute(query).fetchall()
    if not len(ret) > 0:
        return
    
    t,x,y,z,rx,ry,rz= np.transpose(ret)
    total = len(ret)
        
    linex.set_data(t, x)
    liney.set_data(t, y)
    linez.set_data(t, z)
    linerx.set_data(t, rx)
    linery.set_data(t, ry)
    linerz.set_data(t, rz)
    outerlim = 10/1000
    plotx.set_xlim(t[-1], t[0]);plotx.set_ylim(-1.05*outerlim,1.05*outerlim)
    plotx.set_yticks(np.linspace(-0.95*outerlim,0.95*outerlim,5))
    
    plt.pause(0.01)



def calculateZamps(amplitude):
    Fz = np.matrix([[amplitude],
                    [0        ],
                    [0        ]])
    out = np.array(ZMAT_INV * Fz)
    return out

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
    
    if error is None:
        # Turn off interactive mode


        # updatePlot(True)
        fig1manager.set_window_title("6DoF-Data [DONE]")
        updatePlot(True)
        saveFigures(input(''))
        
        plt.ioff()
        plt.show()
        # saveFigures('specific view')
        plt.pause(0.001)
        # Close the figure
        plt.close()
    # Close the program
    sys.exit()