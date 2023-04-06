#!/usr/bin/env python3

""" ADCDAC (CLI) (Threading) Sample Program """
# (C) Copyright 2023 ELD/LION, Leiden University
#
# Version           : 0.2-BETA
# Written by        : H. Visser & A.C.J. van Amersfoort
# Dependencies      : pyserial
#                     adcdac_device, adcdac_threading, eldutils
# Python Version    : 3
# Required Hardware : ADC-DAC
# Initial date      : March 9, 2023
# Last Modified     : April 4, 2023

import sys
import signal
import time

from adcdac_device import ADCDACDevice
from adcdac_threading import ADCDACThreading
from eldutils import bytes_to_hex

COM_PORT = 'COM8'
#COM_PORT = 'COM5'
#COM_PORT = 'DUMMY'

class MainApp(object):
  """ Application class used by the main program """
  def __init__(self, debug=False):
    self._adcdac_device = None
    self._adcdac_thread = None
    self._debug = debug


  def __del__(self):
    print("\nProgram normally terminated\n")


  def signal_handler(self, sig, frame):
    """ (CTRL-C) signal handler """
    self.deinit()
    sys.exit(0)


  def deinit(self):
    """ Deinit (stop thread) """
    if not self._adcdac_thread is None:
      self._adcdac_thread.stop()


  def init(self):
    """ Init device etc."""
    self._adcdac_device = ADCDACDevice(port_name=COM_PORT,
                                       adc_count=16,
                                       dac_count=8,
                                       adc_byte_size=4,
                                       dac_byte_size=4)
    self._adcdac_device.debug = self._debug
    self._adcdac_device.init()

    self._adcdac_thread = ADCDACThreading(adcdac_device=self._adcdac_device)

    return True


  def run(self):
    """ App main (run) function """
    signal.signal(signal.SIGINT, self.signal_handler)
    self._adcdac_thread.start()

    while True:
      time.sleep(0.01)  # Sleep 10ms

      # Check if thread is (still) running
      if not self._adcdac_thread.is_running():
        print("ADC-DAC thread terminated")
        sys.exit(1)

      # Process any incoming data as soon as possible
      while self._adcdac_thread.has_adc_data():
        # Get ADC data from (thread) queue
        adc_byte_data = self._adcdac_thread.get_adc_data()

        # Check Teensy status
        self._adcdac_thread.check_status()

        adc_int_data = self._adcdac_device.unpack_adc_data(adc_byte_data)

        # TODO: Process data here, for now just invert data
        #print(f"before int={adc_int_data[0]}")
        # NOTE: adc_int_data[0] contains sample #, adc_int_data[1][..] contains all int-samples
        dac_int_data = [adc_int_data[0], [int_val * -1 for int_val in adc_int_data[1]]]
        #print(f"after int={dac_int_data[0]}")

        # Pack int data as bytes
        dac_byte_data = self._adcdac_device.pack_dac_data(dac_int_data, clip_int=True)

        print(f"data_in ={bytes_to_hex(adc_byte_data)}")
        print(f"data_out={bytes_to_hex(dac_byte_data)}")

        # Put DAC in (thread) queue
        self._adcdac_thread.put_dac_data(dac_byte_data)


def main(_argv):
  """ Main program """
  app = MainApp(debug=False)

  # Init app
  if not app.init():
    sys.exit(1)

  # Run app
  app.run()


#######################
# Program entry point #
#######################
if __name__ == "__main__":
  main(sys.argv[1:])
