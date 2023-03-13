'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 40000
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
#DEFINE FREQ 40000000 '[Hz]
#DEFINE MAXPOINTS 5000
#DEFINE ADCMAX 2^16
#DEFINE VMAX 10 '[V]
#DEFINE UNITS 1/1000 '[m/Vs]

DIM tick, tick_old, delta as LONG
DIM curt as FLOAT

#DEFINE time_ticks PAR_10
#DEFINE time_s FPAR_10



DIM DATA_1[MAXPOINTS] as FLOAT as FIFO
DIM DATA_2[MAXPOINTS] as FLOAT as FIFO
DIM DATA_3[MAXPOINTS] as FLOAT as FIFO
DIM DATA_4[MAXPOINTS] as FLOAT as FIFO
DIM DATA_5[MAXPOINTS] as FLOAT as FIFO
DIM DATA_6[MAXPOINTS] as FLOAT as FIFO
DIM DATA_7[MAXPOINTS] as FLOAT as FIFO
DIM DATA_8[MAXPOINTS] as FLOAT as FIFO
DIM DATA_9[MAXPOINTS] as FLOAT as FIFO
DIM DATA_10[MAXPOINTS] as FLOAT as FIFO

INIT:
  initFIFO()
  
EVENT:
  
  
  readADC()
  cvt_ADC2V()
  storeData()
   
  if (par_80 = 0)then
    end
  endif
  
SUB initFIFO()
  FIFO_clear(1)
  FIFO_clear(2)
  FIFO_clear(3)
  FIFO_clear(4)
  FIFO_clear(5)
  FIFO_clear(6)
  FIFO_clear(7)
  FIFO_clear(8)
  FIFO_clear(9)
  FIFO_clear(10)
ENDSUB

FUNCTION CalcVoltage(ADCValue) as FLOAT
  DIM ADCval as LONG
  DIM Vval as FLOAT
  ADCval = ADCValue - 0.5 * ADCMAX
  Vval = ADCval * VMAX / ADCMAX
  CalcVoltage = Vval
ENDFUNCTION



SUB readADC()
  PAR_1 = adc(1)
  PAR_2 = adc(3)
  PAR_3 = adc(5)
  PAR_4 = adc(2)
  PAR_5 = adc(4)
  PAR_6 = adc(6)
  PAR_7 = adc(7)
  PAR_8 = adc(9)
  PAR_9 = adc(11)
ENDSUB

SUB cvt_ADC2V()
  FPAR_1 = CalcVoltage(PAR_1)
  FPAR_2 = CalcVoltage(PAR_2)
  FPAR_3 = CalcVoltage(PAR_3)
  FPAR_4 = CalcVoltage(PAR_4)
  FPAR_5 = CalcVoltage(PAR_5)
  FPAR_6 = CalcVoltage(PAR_6)
  FPAR_7 = CalcVoltage(PAR_7)
  FPAR_8 = CalcVoltage(PAR_8)
  FPAR_9 = CalcVoltage(PAR_9)
ENDSUB

SUB storeData()
  if (FIFO_EMPTY(10) > 0) THEN
    DATA_1  = FPAR_1
    DATA_2  = FPAR_2
    DATA_3  = FPAR_3
    DATA_4  = FPAR_4
    DATA_5  = FPAR_5
    DATA_6  = FPAR_6
    DATA_7  = FPAR_7
    DATA_8  = FPAR_8
    DATA_9  = FPAR_9
    DATA_10 = FPAR_10
    PAR_40 = FIFO_FULL(10)
  ENDIF
ENDSUB
