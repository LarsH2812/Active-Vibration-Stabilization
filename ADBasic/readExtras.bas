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
' Info_Last_Save                 = LAPTOP-NC2U1K33  LAPTOP-NC2U1K33\larsh
'<Header End>
#DEFINE FREQ 40000000 '[Hz]
#DEFINE MAXPOINTS 5000
#DEFINE ADCMAX 2^16
#DEFINE VMAX 20 '[V]

DIM DATA_20[5000] as FLOAT as FIFO
DIM DATA_21[5000] as FLOAT as FIFO

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
  CalcVoltage = ADCValue*VMAX/ADCMAX - 0.5*VMAX
ENDFUNCTION
FUNCTION calcADC(Voltage) as LONG
  CalcADC = Voltage*ADCMAX/VMAX + 0.5*ADCMAX
ENDFUNCTION
