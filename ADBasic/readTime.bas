'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 1000
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
#DEFINE time_ticks PAR_10
#DEFINE time_s FPAR_10
#define MAXFREQ 40000000

DIM tick, tick_old, delta as LONG

init:
  tick_old = read_timer()
event:
  tick = read_timer()
  delta = tick - tick_old
  time_ticks = time_ticks + delta
  time_s = time_s + cvt_Tick2ms(delta)
  tick_old = tick
  
FUNCTION cvt_Tick2ms(Tick) as FLOAT
  cvt_Tick2ms = Tick / MAXFREQ
ENDFUNCTION
