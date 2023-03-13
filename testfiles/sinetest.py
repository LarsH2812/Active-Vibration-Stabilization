import numpy as np
from ADwin import ADwin, ADwinError
import time
from copy import deepcopy



BOOTFILE = 'c:\ADwin\ADwin9.btl'
PROCESS1FILE = 'ADBasic/readGuralps.T91'
PROCESS2FILE = 'ADBasic/readExtras.T92'
PROCESS3FILE = 'ADBasic/sendActuators.T93'

VMAX = 20
ADCMAX = 2**16
convADC = lambda x: x*VMAX/ADCMAX - 0.5*VMAX
convV = lambda x: x*ADCMAX/VMAX + 0.5*ADCMAX

adwin = ADwin(DeviceNo=1, raiseExceptions= 1, useNumpyArrays= 1)


omega = 2 * np.pi * 0.25
phi = 0
cont = True



adwin.Boot(BOOTFILE)
adwin.Set_Par(51, 1)
adwin.Load_Process(PROCESS3FILE)
adwin.Start_Process(3)

t0 = time.time()

while(cont):
    if adwin.Get_Par(51) == 0:
        cont = False
    t = time.time() - t0

    val = 1* np.sin(omega * t + phi)
    adwin.Set_Par(50, int(convV(val)))

adwin.Stop_Process(3)
