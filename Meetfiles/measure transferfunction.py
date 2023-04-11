import math
import sqlite3 as sql
import sys
import time
import traceback

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from ADwin import ADwin, ADwinError
from peakdetect import peakdetect

SAMPLEPOINTS = 2500 # [points/batch]
PERIOD = 1/1.4 * 14
FOURCALCTIME = 5 * PERIOD
MEASUREMENTTIME = FOURCALCTIME
MEASUREMENTTMES = np.array([])
STARTTIME = time.time()

adwin = ADwin(
    DeviceNo= 1,
    raiseExceptions= 1,
    useNumpyArrays= 1
)

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

def init_adwin():
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
def stop_adwin():
    adwin.Stop_Process(1)
    adwin.Stop_Process(2)
    adwin.Stop_Process(3)
    adwin.Stop_Process(4)
    
    
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

def get_amplitude(actuator:str = None):
    if actuator.lower() not in ['eastx','westx','southy','westy','southz','eastz','westz']:
        raise ValueError(f"Specified actuator is not correct.\n\t\tMust be one of the following {['eastx','westx','southy','westy','southz','eastz','westz']}")
    if actuator.lower() == 'eastx':
        ret:float = adwin.Get_FPar(60)
    elif actuator.lower() == 'westx':
        ret:float = adwin.Get_FPar(63)
    elif actuator.lower() == 'southy':
        ret:float = adwin.Get_FPar(66)
    elif actuator.lower() == 'westy':
        ret:float = adwin.Get_FPar(69)
    elif actuator.lower() == 'southz':
        ret:float = adwin.Get_FPar(72)
    elif actuator.lower() == 'eastz':
        ret:float = adwin.Get_FPar(75)
    elif actuator.lower() == 'westz':
        ret:float = adwin.Get_FPar(78)
    return ret
        
def set_frequentie(actuator:str = None, frequentie:float = 0):
    if actuator.lower() not in ['eastx','westx','southy','westy','southz','eastz','westz']:
        raise ValueError(f"Specified actuator is not correct.\n\t\tMust be one of the following {['eastx','westx','southy','westy','southz','eastz','westz']}")
    if actuator.lower() == 'eastx':
        adwin.Set_FPar(61, frequentie)
    elif actuator.lower() == 'westx':
        adwin.Set_FPar(64, frequentie)
    elif actuator.lower() == 'southy':
        adwin.Set_FPar(67, frequentie)
    elif actuator.lower() == 'westy':
        adwin.Set_FPar(70, frequentie)
    elif actuator.lower() == 'southz':
        adwin.Set_FPar(73, frequentie)
    elif actuator.lower() == 'eastz':
        adwin.Set_FPar(76, frequentie)
    elif actuator.lower() == 'westz':
        adwin.Set_FPar(79, frequentie)
    return True

def init_database():
    try:
        current_time = time.localtime(STARTTIME)
        current_date = time.strftime("%Y-%m-%d", current_time)
        current_time = time.strftime("%H%M%S", current_time)
        
        db = sql.connect(f'Meetfiles\data\{current_date} - {current_time}.db')
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

def get_time():
    adwintime = adwin.Get_FPar(10)
    return adwintime

def get_data_time():
    datatime = cur_meet_resultaten.execute('SELECT MAX(t) FROM guralp').fetchone()[0]
    return datatime if datatime is not None else 0

def read_data():
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
        cur_meet_resultaten.executemany('INSERT INTO guralp VALUES (?,?,?,?,?,?,?,?,?,?)', np.transpose(data).tolist())
        
        dataStepper = adwin.GetFifo_Float(20, SAMPLEPOINTS)
        dataAccoustic = adwin.GetFifo_Float(21, SAMPLEPOINTS)
        data = np.array([dataT, dataStepper, dataAccoustic])
        cur_meet_resultaten.executemany('INSERT INTO extras VALUES (?,?,?)', np.transpose(data).tolist())
        db_meet_resultaten.commit()
        
        return True
    return False



if __name__ == "__main__":
    ret_database, db_meet_resultaten, cur_meet_resultaten = init_database()
    ret_adwin = init_adwin()
    
    if False in [ret_database, ret_adwin]:
        sys.exit(-1)
    
    t0 = get_time()

    frequenties = np.arange(0.5,3.1,0.1,)
    set_amplitude('eastz', 0)
    
    while get_time() <= (t0 +20):
        read_data()
    t1 = get_time()

    
    MEASUREMENTTMES = np.append(MEASUREMENTTMES, t1)
    
    for f in frequenties:
        try:
            times = {'frequency' : f}
            periode = 1 / f
            print(f)
            
            
            set_amplitude('eastz', 1)
            set_frequentie('eastz', f)
            
            while get_time() <= (t1 +20):
                print(f'(f = {f}) Setting: {t1 + 20 - get_time() }')
                read_data()
            t1 = get_time()
            times['settingtime': t1]
            MEASUREMENTTMES = np.append(MEASUREMENTTMES, t1)
            
            while get_time() <= (t1 + 5*periode):
                print(f'(f = {f}) Measuring 1: {t1 + 5*periode - get_time()}')
                read_data()
            t1 = get_time()
            times['measure time 1': t1]
            MEASUREMENTTMES = np.append(MEASUREMENTTMES, t1)
            while get_time() <= (t1 + 5*periode):
                print(f'(f = {f}) Measuring 2: {t1 + 5*periode - get_time()}')
                read_data()
            t1 = get_time()
            times['measure time 2': t1]
            MEASUREMENTTMES = np.append(MEASUREMENTTMES, t1)
            while get_time() <= (t1 + 5*periode):
                print(f'(f = {f}) Measuring 3: {t1 + 5*periode - get_time()}')
                read_data()
            t1 = get_time()
            times['measure time 3': t1]
            MEASUREMENTTMES = np.append(MEASUREMENTTMES, t1)
            while get_time() <= (t1 + 5*periode):
                print(f'(f = {f}) Measuring 4: {t1 + 5*periode - get_time()}')
                read_data()
            t1 = get_time()
            times['measure time 4': t1]
            MEASUREMENTTMES = np.append(MEASUREMENTTMES, t1)
            
        
        except ADwinError as ADE:
            print(f'type: {type(ADE)}\nerror: {traceback.format_exc()}')
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f'type: {type(e)}\nerror: {traceback.format_exc()}')
    # print([MEASUREMENTTMES[i+1]-MEASUREMENTTMES[i] for i in range(0,len(MEASUREMENTTMES)-1)])
    filename = time.strftime("%Y-%m-%d-%H%M%S",time.localtime(STARTTIME))
    np.save(f'Meetfiles\data\{filename}',MEASUREMENTTMES)


    stop_adwin()
    db_meet_resultaten.close()