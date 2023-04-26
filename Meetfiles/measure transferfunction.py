import math
import sqlite3 as sql
import sys, os
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
STARTTIME = time.time()

F_MIN  = 0.5 # [Hz]
F_MAX  = 3.0 # [Hz]
F_STEP = 0.05 # [Hz]
F_POINTS = int((F_MAX-F_MIN)/F_STEP)+1

STARTTIME = time.localtime(STARTTIME)
current_date = time.strftime("%Y-%m-%d", STARTTIME)
current_time = time.strftime("%H%M%S", STARTTIME)

save_dir = f'{os.getcwd()}/Meetfiles/data/{current_date}' 
save_file = f'{save_dir}\{current_date} - {current_time}'
try:
    os.mkdir(save_dir)
except:
    print('directory already exists')


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
        # adwin.Load_Process(Filename=PROCESS4FILE)   # Load the extra data gathering process
        
        adwin.Start_Process(ProcessNo=1)            # Load the time keeping process
        adwin.Start_Process(ProcessNo=2)            # Load the actuator driving process
        adwin.Start_Process(ProcessNo=3)            # Load the guralp data gathering process
        # adwin.Start_Process(ProcessNo=4)            # Load the extra data gathering process
        
        return True
    except Exception as e:
        print(f'type: {type(e)}\nerror: {traceback.format_exc()}')
        return False
def stop_adwin():
    adwin.Stop_Process(1)
    adwin.Stop_Process(2)
    adwin.Stop_Process(3)
    # adwin.Stop_Process(4)
    
def get_time():
    try:
        adwintime = adwin.Get_FPar(10)
        return adwintime
    except:
        pass

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

def init_database(frequentie: None|float = None):
    try:
        db = sql.connect(f'{save_file} ({frequentie:.2f}).db')
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
                        COMMIT;
                        """)
        return True, db, cur
    except Exception as e:
        print(f'type: {type(e)}\nerror: {traceback.format_exc()}')
        return False, None, None

def get_data_time():
    datatime = cur_meet_resultaten.execute('SELECT MAX(t) FROM guralp').fetchone()[0]
    return datatime if datatime is not None else 0

def read_data(dataPoints: int = SAMPLEPOINTS):
    if adwin.Fifo_Full(10) >= dataPoints:
        dataTX = adwin.GetFifo_Float(1, dataPoints)
        dataTY = adwin.GetFifo_Float(2, dataPoints)
        dataTZ = adwin.GetFifo_Float(3, dataPoints)
        dataNX = adwin.GetFifo_Float(4, dataPoints)
        dataNY = adwin.GetFifo_Float(5, dataPoints)
        dataNZ = adwin.GetFifo_Float(6, dataPoints)
        dataEX = adwin.GetFifo_Float(7, dataPoints)
        dataEY = adwin.GetFifo_Float(8, dataPoints)
        dataEZ = adwin.GetFifo_Float(9, dataPoints)
        dataT = adwin.GetFifo_Float(10, dataPoints)
        try:
            data = np.array([dataT, dataTX, dataTY, dataTZ, dataNX, dataNY, dataNZ, dataEX, dataEY, dataEZ])
            cur_meet_resultaten.executemany('INSERT INTO guralp VALUES (?,?,?,?,?,?,?,?,?,?)', np.transpose(data).tolist())

            db_meet_resultaten.commit()
        except sql.IntegrityError as sql_error:
            print(f'Error: {sql_error}\nContinuing...')
        
        return True
    return False



if __name__ == "__main__":
    once = True
    frequenties = np.linspace(F_MIN, F_MAX, F_POINTS)
    print(frequenties)
    time.sleep(0.5)
    t_passed = 0
    t_total = 0
    for f in frequenties:
        t_total += 500/f
        t_total += 20
        t_total += 500/f

    print(f'{t_total//3600:.0f}:{t_total%60:.0f}')

    for f in frequenties:

        ret_database, db_meet_resultaten, cur_meet_resultaten = init_database(f)
        ret_adwin = init_adwin()
        MEASUREMENTTMES = np.array([])
        if False in [ret_database, ret_adwin]:
            sys.exit(-1)
        
        t0 = get_time()
        periode = 1 / f
        set_amplitude('eastz', 2)
        set_frequentie('eastz', 0)

        MEASUREMENTTMES = np.append(MEASUREMENTTMES, 0.0)
        MEASUREMENTTMES = np.append(MEASUREMENTTMES, t0)
        print(f'0-meting')
        try:
            while get_time() <= (t0+500*periode):
                try:
                    print(f'[{t_passed/t_total *100:>3.0f}%] 0 meettijd {f:.1f}/{F_MAX:.1f}:\t {(t0 + 500*periode) - get_time()}')
                    read_data()
                except Exception as e:
                    print(f'type:\t{type(e)}\nstring:\t{traceback.format_exc()}')
                    break
            t1 = get_time()
            MEASUREMENTTMES = np.append(MEASUREMENTTMES,t1)
            t_passed += 500*periode
            try:
                MEASUREMENTTMES = np.append(MEASUREMENTTMES,f)
                
                print(f)
                set_amplitude('eastz', 2)
                set_frequentie('eastz', f)
                
                t1 = get_time()
                while get_time() <= (t1 + 20):
                    print(f'[{t_passed/t_total *100:>3.0f}%] insteltijd {f:.1f}/{F_MAX:.1f}:\t {(t1 + 20) - get_time()}')
                    read_data()
                t1 = get_time()
                MEASUREMENTTMES = np.append(MEASUREMENTTMES,t1)
                t_passed += 20
                print(f'meting {1}: Freq= {f}')
                while get_time() <= (t1 + 500*periode):
                    print(f'[{t_passed/t_total *100:>3.0f}%] meettijd {f:.1f}/{F_MAX:.1f}:\t {(t1 + 500*periode) - get_time()}')
                    read_data()
            except KeyboardInterrupt:
                pass

            t1 = get_time()
            MEASUREMENTTMES = np.append(MEASUREMENTTMES,t1)
            t_passed += 500*periode
        
        except ADwinError as ADE:
            print(f'type: {type(ADE)}\nerror: {traceback.format_exc()}')
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f'type: {type(e)}\nerror: {traceback.format_exc()}')
        # print([MEASUREMENTTMES[i+1]-MEASUREMENTTMES[i] for i in range(0,len(MEASUREMENTTMES)-1)])
        read_data(adwin.Fifo_Full(10))
        print('Done')
        np.save(f'{save_file} ({f:.2f})',MEASUREMENTTMES,allow_pickle= True)


        stop_adwin()
        db_meet_resultaten.close()

        print(f'''Saved file in:
                {save_file} ({f:.2f}).db
                {save_file} ({f:.2f}).npy''')