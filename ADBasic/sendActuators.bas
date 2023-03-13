'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 3
' Initial_Processdelay           = 4000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 6.3.1
' Optimize                       = Yes
' Optimize_Level                 = 1
' Stacksize                      = 1000
' Info_Last_Save                 = GLMEETPC62  GLMEETPC62\lion
'<Header End>
#define MAXFREQ 40000000
#define VMAX 20
#define ADCMAX 2^16
#DEFINE PI 3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117067982148086513282306647093844

#DEFINE time_ticks PAR_10
#DEFINE time_s FPAR_10

#DEFINE EASTX PAR_60
#DEFINE EASTXVAL PAR_61
#DEFINE EASTXAMP FPAR_60
#DEFINE FREQUENCYEX FPAR_61
#DEFINE PHASEEX FPAR_62

#DEFINE WESTX PAR_63
#DEFINE WESTXVAL PAR_64
#DEFINE WESTXAMP FPAR_63
#DEFINE FREQUENCYWX FPAR_64
#DEFINE PHASEWX FPAR_65

#DEFINE SOUTHY PAR_66
#DEFINE SOUTHYVAL PAR_67
#DEFINE SOUTHYAMP FPAR_66
#DEFINE FREQUENCYSY FPAR_67
#DEFINE PHASESY FPAR_68

#DEFINE WESTY PAR_69
#DEFINE WESTYVAL PAR_70
#DEFINE WESTYAMP FPAR_69
#DEFINE FREQUENCYWY FPAR_70
#DEFINE PHASEWY FPAR_71

#DEFINE SOUTHZ PAR_72
#DEFINE SOUTHZVAL PAR_73
#DEFINE SOUTHZAMP FPAR_72
#DEFINE FREQUENCYSZ FPAR_73
#DEFINE PHASESZ FPAR_74

#DEFINE EASTZ PAR_75
#DEFINE EASTZVAL PAR_76
#DEFINE EASTZAMP FPAR_75
#DEFINE FREQUENCYEZ FPAR_76
#DEFINE PHASEEZ FPAR_77

#DEFINE WESTZ PAR_78
#DEFINE WESTZVAL PAR_79
#DEFINE WESTZAMP FPAR_78
#DEFINE FREQUENCYWZ FPAR_79
#DEFINE PHASEWZ FPAR_80

dim buf as FLOAT
dim i as long
DIM tick, tick_old, delta as LONG


init:
  PAR_80 = 1
  i = 1
  EASTX = 7
  WESTX = 6
  SOUTHY = 5
  WESTY = 4
  SOUTHZ = 3
  EASTZ = 1
  WESTZ = 2
  tick_old = read_timer()

event:
  
  tick = read_timer()
  delta = tick - tick_old
  time_ticks = time_ticks + delta
  time_s = time_s + cvt_Tick2ms(delta)
  tick_old = tick

  EASTXVAL  = driveActuator(EASTX , EASTXAMP , FREQUENCYEX, PHASEEX)
  WESTXVAL  = driveActuator(WESTX , WESTXAMP , FREQUENCYWX, PHASEWX)
  SOUTHYVAL = driveActuator(SOUTHY, SOUTHYAMP, FREQUENCYSY, PHASESY)
  WESTYVAL  = driveActuator(WESTY , WESTYAMP , FREQUENCYWY, PHASEWY)
  SOUTHZVAL = driveActuator(SOUTHZ, SOUTHZAMP, FREQUENCYSZ, PHASESZ)
  EASTZVAL  = driveActuator(EASTZ , EASTZAMP , FREQUENCYEZ, PHASEEZ)
  WESTZVAL  = driveActuator(WESTZ , WESTZAMP , FREQUENCYWZ, PHASEWZ)
  
  if (PAR_80 = 0) THEN
    end
  ENDIF
   
finish:
  EASTXVAL  = driveActuator(EASTX , 0 , 0, 0)
  WESTXVAL  = driveActuator(WESTX , 0 , 0, 0)
  SOUTHYVAL = driveActuator(SOUTHY, 0 , 0, 0)
  WESTYVAL  = driveActuator(WESTY , 0 , 0, 0)
  SOUTHZVAL = driveActuator(SOUTHZ, 0 , 0, 0)
  EASTZVAL  = driveActuator(EASTZ , 0 , 0, 0)
  WESTZVAL  = driveActuator(WESTZ , 0 , 0, 0)
     
FUNCTION CalcVoltage(ADCValue) as FLOAT
  CalcVoltage = ADCValue*VMAX/ADCMAX - 0.5*VMAX
ENDFUNCTION
FUNCTION calcADC(Voltage) as LONG
  CalcADC = Voltage*ADCMAX/VMAX + 0.5*ADCMAX
ENDFUNCTION

FUNCTION driveActuator(Actuator, Amplitude, Frequency, Phase) as LONG
  DIM omega, phi as Float
  DIM voltage as LONG
  omega = 2*PI * Frequency
  phi = Phase
  voltage = calcADC(Amplitude * sin(omega * time_s + phi))
  DAC(Actuator, voltage)
  driveActuator = voltage
ENDFUNCTION

FUNCTION cvt_Tick2ms(Tick) as FLOAT
  cvt_Tick2ms = Tick / MAXFREQ
ENDFUNCTION
