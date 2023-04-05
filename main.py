import math
import sqlite3 as sql
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

def set_fase(actuator:str = None, fase:float = 0):
    if actuator.lower() not in ['eastx','westx','southy','westy','southz','eastz','westz']:
        raise ValueError(f"Specified actuator is not correct.\n\t\tMust be one of the following {['eastx','westx','southy','westy','southz','eastz','westz']}")
    if actuator.lower() == 'eastx':
        adwin.Set_FPar(62, fase)
    elif actuator.lower() == 'westx':
        adwin.Set_FPar(65, fase)
    elif actuator.lower() == 'southy':
        adwin.Set_FPar(68, fase)
    elif actuator.lower() == 'westy':
        adwin.Set_FPar(71, fase)
    elif actuator.lower() == 'southz':
        adwin.Set_FPar(74, fase)
    elif actuator.lower() == 'eastz':
        adwin.Set_FPar(77, fase)
    elif actuator.lower() == 'westz':
        adwin.Set_FPar(80, fase)
    return True
def set_amplitude(actuator:str = None, amplitude:float = 0):
    if actuator.lower() not in ['eastx','westx','southy','westy','southz','eastz','westz']:
        raise ValueError(f"Specified actuator is not correct.\n\t\tMust be one of the following {['eastx','westx','southy','westy','southz','eastz','westz']}")
    if actuator.lower() == 'eastx':
        adwin.Set_FPar(60, amplitude)
    elif actuator.lower() == 'westx':
        adwin.Set_FPar(63, amplitude)
    elif actuator.lower() == 'southy':
        adwin.Set_FPar(66, amplitude)
    elif actuator.lower() == 'westy':
        adwin.Set_FPar(69, amplitude)
    elif actuator.lower() == 'southz':
        adwin.Set_FPar(72, amplitude)
    elif actuator.lower() == 'eastz':
        adwin.Set_FPar(75, amplitude)
    elif actuator.lower() == 'westz':
        adwin.Set_FPar(78, amplitude)
    return True      
def set_frequentie(actuator:str = None, frequentie:float = 0):
    if actuator.lower() not in ['eastx','westx','southy','westy','southz','eastz','westz']:
        raise ValueError(f"Specified actuator is not correct.\n\t\tMust be one of the following {['eastx','westx','southy','westy','southz','eastz','westz']}")
    if actuator.lower() == 'eastx':
        adwin.Set_FPar(60, frequentie)
    elif actuator.lower() == 'westx':
        adwin.Set_FPar(63, frequentie)
    elif actuator.lower() == 'southy':
        adwin.Set_FPar(66, frequentie)
    elif actuator.lower() == 'westy':
        adwin.Set_FPar(69, frequentie)
    elif actuator.lower() == 'southz':
        adwin.Set_FPar(72, frequentie)
    elif actuator.lower() == 'eastz':
        adwin.Set_FPar(75, frequentie)
    elif actuator.lower() == 'westz':
        adwin.Set_FPar(78, frequentie)
    return True

error = None

t0 = 0
freq = 0

# Create the data arrays
def initDatabase():
    global db, cur
    try:
        current_time = time.localtime()
        current_date = time.strftime("%Y-%m-%d", current_time)
        current_time = time.strftime("%H%M%S", current_time)
        
        db = sql.connect(f'data\{current_date} - {current_time}.db')
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
        return True, db, cur
    except Exception as e:
        print(f'type: {type(e)}\nerror: {traceback.format_exc()}')
        return False, None, None

def initfig1():
    global fig1, fig1manager
    global plotx, ploty, plotz, plotrx, plotry, plotrz
    global linex, liney, linez, linerx, linery, linerz

    fig1, (plotx, ploty,plotz, plotrx,plotry,plotrz) = plt.subplots(6,1, sharex=True, sharey=True)
    plt.tight_layout()
    fig1.subplots_adjust(hspace=0)
    fig1manager = plt.get_current_fig_manager()

    linex, = plotx.plot([],[], 'k')
    liney, = ploty.plot([],[], 'k')
    linez, = plotz.plot([],[], 'k')
    linerx, = plotrx.plot([],[], 'k')
    linery, = plotry.plot([],[], 'k')
    linerz, = plotrz.plot([],[], 'k')

    fig1manager.window.showMaximized()

def initfig2():
    global fig2, fig2manager
    global plotfx, plotfy, plotfz, plotfrx, plotfry, plotfrz
    global linefx, linefy, linefz, linefrx, linefry, linefrz
    
    fig2, (plotfx, plotfy, plotfz, plotfrx, plotfry, plotfrz) = plt.subplots(6,1, sharex= True, sharey= True)
    plt.tight_layout()
    fig2.subplots_adjust(hspace=0)
    fig2manager = plt.get_current_fig_manager()

    linefx, = plotfx.plot([],[],'k')
    linefy, = plotfy.plot([],[],'k')
    linefz, = plotfz.plot([],[],'k')
    linefrx, = plotfrx.plot([],[],'k')
    linefry, = plotfry.plot([],[],'k')
    linefrz, = plotfrz.plot([],[],'k')
    
    fig2manager.window.showMaximized()

def initfig3():
    global fig3, fig3manager
    global plotbax, plotbpx, plotbay, plotbpy, plotbaz, plotbpz
    global plotbarx,plotbprx,plotbary,plotbpry,plotbarz,plotbprz
    global linebax,  linebpx,  linebay,  linebpy,  linebaz,  linebpy
    global linebarx, linebprx, linebary, linebpry, linebarz, linebprz
    
    fig3, ((plotbax,plotbarx),
            (plotbpx,plotbprx),
            (plotbay,plotbary),
            (plotbpy,plotbpry),
            (plotbaz,plotbarz),
            (plotbpz,plotbprz)) = plt.subplots(6,2)

    fig3manager = plt.get_current_fig_manager()

    plotbpx. sharex(plotbax)
    plotbpy. sharex(plotbay)
    plotbpz. sharex(plotbaz)
    plotbprx.sharex(plotbarx)
    plotbpry.sharex(plotbary)
    plotbprz.sharex(plotbarz)

    plotbax. set_xscale('log');plotbax. set_yscale('log')
    plotbay. set_xscale('log');plotbay. set_yscale('log')
    plotbaz. set_xscale('log');plotbaz. set_yscale('log')
    plotbarx.set_xscale('log');plotbarx.set_yscale('log')
    plotbary.set_xscale('log');plotbary.set_yscale('log')
    plotbarz.set_xscale('log');plotbarz.set_yscale('log')

    plotbax. grid(True, which= 'both', axis= 'both');plotbpx. grid(True, which= 'both', axis= 'both')
    plotbay. grid(True, which= 'both', axis= 'both');plotbpy. grid(True, which= 'both', axis= 'both')
    plotbaz. grid(True, which= 'both', axis= 'both');plotbpz. grid(True, which= 'both', axis= 'both')
    plotbarx.grid(True, which= 'both', axis= 'both');plotbprx.grid(True, which= 'both', axis= 'both')
    plotbary.grid(True, which= 'both', axis= 'both');plotbpry.grid(True, which= 'both', axis= 'both')
    plotbarz.grid(True, which= 'both', axis= 'both');plotbprz.grid(True, which= 'both', axis= 'both')

    linebax,  = plotbax. plot([],[],'k');linebpx,  = plotbpx. plot([],[],'k')
    linebay,  = plotbay. plot([],[],'k');linebpy,  = plotbpy. plot([],[],'k')
    linebaz,  = plotbaz. plot([],[],'k');linebpy,  = plotbpz. plot([],[],'k')
    linebarx, = plotbarx.plot([],[],'k');linebprx, = plotbprx.plot([],[],'k')
    linebary, = plotbary.plot([],[],'k');linebpry, = plotbpry.plot([],[],'k')
    linebarz, = plotbarz.plot([],[],'k');linebprz, = plotbprz.plot([],[],'k')
    fig3manager.window.showMaximized()
    plt.pause((0.001))
    plt.tight_layout()
    plt.pause(0.001)

def initAdwin():
    """
    This function initializes the ADwin system by booting up the system, loading the 4 process files, starting the process files
    """    
    try:
        adwin.Boot(Filename=BOOTFILE)               # Boot the ADwin
    
        adwin.Load_Process(Filename=PROCESS1FILE)   # Load the time keeping process
        adwin.Load_Process(Filename=PROCESS2FILE)   # Load the actuator driving process
        adwin.Load_Process(Filename=PROCESS3FILE)   # Load the guralp data gathering process
        adwin.Load_Process(Filename=PROCESS4FILE)   # Load the extra data gathering process
        
        adwin.Start_Process(ProcessNo=1)            # Load the time keeping process
        adwin.Start_Process(ProcessNo=2)            # Load the actuator driving process
        adwin.Start_Process(ProcessNo=3)            # Load the guralp data gathering process
        adwin.Start_Process(ProcessNo=4)            # Load the extra data gathering process
        
        return True
    except Exception as e:
        print(f'type: {type(e)}\nerror: {traceback.format_exc()}')
        return False

def init():
    '''Initialize '''
    global t0
    in1 = input('show XYZ-data: Y/n\n')
    in2 = input('show Fourier data: Y/n\n')
    in3 = input('show Extra\'s data: Y/n\n')
    SHOWGRAPH[1] = False if in1.lower() in ["no","nee", "n"] else True
    SHOWGRAPH[2] = False if in2.lower() in ["no","nee", "n"] else True
    SHOWGRAPH[3] = False if in3.lower() in ["no","nee", "n"] else True
    
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
        # Read the data
        pass

    except KeyboardInterrupt as ke:
        error = {'type': type(ke), 'str' :traceback.format_exc()}
        print(f'type: {error["type"]} \n{error["str"]}')
    except Exception as e:
        error = {'type': type(e), 'str' :traceback.format_exc()}
        print(f'type: {error["type"]} \n{error["str"]}')

def gettime():
    adwintime = adwin.get_Fpar(10)
    return adwintime

def get_data_time():
    datatime = cur.execute('SELECT MAX(t) FROM guralp').fetchone()[0]
    return datatime if datatime is not None else 0

def readData(dataTX = 0):
    """Read out 2500 points of data from the FIFO data registers.

    `dataT`
        Time data
    `dataTX`
        data read out from the topX direction
    `dataTY`
        data read out from the topY direction
    `dataTZ`
        data read out from the topZ direction
    `dataNX`
        data read out from the northX direction
    `dataNY`
        data read out from the northY direction
    `dataNZ`
        data read out from the northZ direction
    `dataEX`
        data read out from the eastX direction
    `dataEY`
        data read out from the eastY direction
    `dataEZ`
        data read out from the eastZ direction
    `dataStepper`
        data read out from the stepper signal
    `dataAccoustic`
        data read out from the accoustic signal
    
    """
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