'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 4
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

DIM DATA_20[5000] AS FLOAT AS FIFO
DIM DATA_21[5000] AS FLOAT AS FIFO

DIM _ AS FLOAT


INIT:
  FIFO_clear(20)
  FIFO_clear(21)
event:
  
  PAR_20 = ADC(16)
  _ = ADC(15)
  PAR_21 = ADC(14)


  
  data_20 = CalcVoltage(PAR_20)
  data_21 = CalcVoltage(PAR_21)


  PAR_41 = FIFO_FULL(20)
  
  if (par_80 = 0)then
    end
  endif
    
FUNCTION CalcVoltage(ADCValue) as FLOAT
  DIM ADCval as LONG
  ADCval = ADCValue - 0.5 * ADCMAX
  CalcVoltage = ADCval * VMAX / ADCMAX
ENDFUNCTION
