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
PROCESS1FILE = 'ADBasic/readGuralps.T91'
PROCESS2FILE = 'ADBasic/readExtras.T92'
PROCESS3FILE = 'ADBasic/sendActuators.T93',

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
    db = sqlite3.connect(f'data\{date} - {meastime}.db')
    cur = db.cursor()
    cur.execute("CREATE TABLE guralp(t REAL PRIMARY KEY, topX REAL, topY REAL, topZ REAL, northX REAL, northY REAL, northZ REAL, eastX REAL, eastY REAL, eastZ REAL)")
    cur.execute("CREATE TABLE fourier(f REAL PRIMARY KEY, txamp REAL, txphase REAL, tyamp REAL, typhase REAL, tzamp REAL, tzphase REAL, nxamp REAL, nxphase REAL, nyamp REAL, nyphase REAL, nzamp REAL, nzphase REAL, examp REAL, exphase REAL, eyamp REAL, eyphase REAL, ezamp REAL, ezphase REAL)")
    cur.execute("CREATE TABLE extras(t REAL PRIMARY KEY, stepper REAL, accoustic REAL)")
    db.commit()

def initfig1():
    global fig1, fig1manager, plotx, ploty, plotz, plotrx, plotry, plotrz
    fig1 = plt.figure('6DoF-Data [INITIALIZING]', figsize=(15, 10))
    fig1manager = plt.get_current_fig_manager()

    #Create a Figure
    plotx    = plt.subplot2grid((6,6), (0,0), colspan=6)
    ploty    = plt.subplot2grid((6,6), (1,0), colspan=6, sharex=plotx, sharey=plotx,) 
    plotz    = plt.subplot2grid((6,6), (2,0), colspan=6, sharex=plotx, sharey=plotx,)
    plotrx   = plt.subplot2grid((6,6), (3,0), colspan=6, sharex=plotx, sharey=plotx,)
    plotry   = plt.subplot2grid((6,6), (4,0), colspan=6, sharex=plotx, sharey=plotx,)
    plotrz   = plt.subplot2grid((6,6), (5,0), colspan=6, sharex=plotx, sharey=plotx,)



    fig1manager.window.showMaximized()
    plt.tight_layout()


def initAdwin():
    # Load the program
    adwin.Boot(Filename=BOOTFILE)               # Load the boot file and boot the ADwin
    adwin.Load_Process(Filename=PROCESS1FILE)   # Load process 1
    adwin.Load_Process(Filename=PROCESS2FILE)   # Load process 2
    adwin.Load_Process(Filename=PROCESS3FILE)   # Load process 3
    adwin.Set_Par(80, 1)
    # Start the program
    adwin.Start_Process(ProcessNo= 1)           # Start process 1
    adwin.Start_Process(ProcessNo= 2)           # Start process 2
    adwin.Start_Process(ProcessNo= 3)           # Start process 3

def init():
    '''Initialize '''
    global t0

    
    initDatabase()
    initfig1()
    initAdwin()
    
def main():
    global FOURCALCTIME, sVect, r1Vect, r2Vect, r3Vect, lineStepper, lineAccoustic, plotStepper, plotAccoustic, plotVect, plotftx, plotfty, plotftz, plotfnx, plotfny, plotfnz, plotfex, plotfey, plotfez, lineftx, linefty, lineftz, linefnx, linefny, linefnz, linefex, linefey, linefez, fig1, fig2, fig3, FOURIERCALCULATED, SAMPLEPOINTS, adwin
    
    fig1manager.set_window_title('6DoF-Data [RUNNING]')

    try:
        # Read the data
        while gettime() <= FOURCALCTIME:
            readData()
                        
        


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
            
        updatePlot()

def saveFigures():
    '''Save the figure as a svg and the data as a json file'''
    if error is None:

        filename = time.strftime('Guralp Sensor Data - %Y%m%d%H%M%S')
        fig1.savefig(f'data/Guralp/svg/{filename}.svg', format='svg')
        fig1.savefig(f'data/Guralp/png/{filename}.png', format='png')


def updatePlot(COMPLETETIME:bool = False):
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
            plotx.set_xlim(ret[0][-1], ret[0][0])
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


        updatePlot(True)
        fig1manager.set_window_title("6DoF-Data [DONE]")
        plotx.legend(loc= 'upper right')
        ploty.legend(loc = 'upper right')
        plotz.legend(loc= 'upper right')

        
        plt.ioff()
        plt.show()
        plt.pause(0.001)
        # Close the figure
        plt.close()
        saveFigures()
    # Close the program
    sys.exit()