""" ADC-DAC Data Threading """
# (C) Copyright 2023 ELD/LION, Leiden University
#
# Written by        : ing. A.C.J. van Amersfoort
# Dependencies      : pyserial(pip3)
#                     ADCDACDevice, ELDUtils
# Python Version    : 3
# Required Hardware : ADC-DAC
# Initial date      : February 27, 2023
# Last Modified     : April 3, 2023

import threading
import queue
import serial

from adcdac_device import ADCDACDevice
from eldutils import printn_stderr

class ADCDACThreading(threading.Thread):
  """ ADC-DAC Data (acquisition) thread """
  ADC_DAC_DATA_BUF_SIZE = 50  # (Maximum) number of samples in ADC/DAC data buffers

  def __init__(self,
               adcdac_device):

    # Call baseclass constructor
    threading.Thread.__init__(self, name="ADCDACThread")

    self._adcdac_device = adcdac_device
    self._stop_event = threading.Event()
    self._reset_event = threading.Event()
    self._error_event = threading.Event()
    self._adc_data = queue.Queue(maxsize=self.ADC_DAC_DATA_BUF_SIZE)
    self._dac_data = queue.Queue(maxsize=self.ADC_DAC_DATA_BUF_SIZE)


  def _put_adc_data(self, data):
    """ Store adc data to be used by caller (thread) """
    # Data thread is different from caller (=main) thread, so we need a lock
    if self._adc_data.full():
      printn_stderr("ERROR: ADC FIFO full!")
      return False

    self._adc_data.put(data)

    return True


  def get_adc_data(self):
    """ Get ADC data from our queue """
    if self._adc_data.empty():
      printn_stderr("WARNING: ADC FIFO empty!")
      return None

    return self._adc_data.get()


  def has_adc_data(self):
    """ Return if any adc data in queue """
    return not self._adc_data.empty()


  def put_dac_data(self, data):
    """ Store dac data to be used by by device (in this thread) """

    if self._dac_data.full():
      printn_stderr("ERROR: DAC FIFO full!")
      return False

    self._dac_data.put(data)

    return True


  def _has_dac_data(self):
    """ Return if any dac data in queue """
    return not self._dac_data.empty()


  def _get_dac_data(self):
    """ Get adc data (thread safe) from this thread """
    if self._dac_data.empty():
      printn_stderr("ERROR: DAC FIFO empty!")
      return None

    return self._dac_data.get()


  def is_running(self):
    """ Is thread (still) running? """
    return self.is_alive()


  def get_teensy_flags(self):
    """ Get Teensy flags from most recent ADC transfer """
    return self._adcdac_device.adc_flags


  def is_error_flagged(self, auto_clear=True):
    """ Return if an error occurred """
    if self._error_event.is_set():
      if auto_clear:
        self._error_event.clear()
      return True

    return False


  def stop(self, timeout=None):
    """ Stop data thread (called from main thread) """
    self._stop_event.set()  # Set stop event to terminate data thread

    # And block until done
    threading.Thread.join(self, timeout)

    # Explictly deinit device
#    self._adcdac_device.deinit()


  def _reset_internal(self):
    """ Reset device & thread """
    if not self._adcdac_device is None:
      self._adcdac_device.reset()

    # Reset queues
    self._adc_data = queue.Queue(maxsize=self.ADC_DAC_DATA_BUF_SIZE)
    self._dac_data = queue.Queue(maxsize=self.ADC_DAC_DATA_BUF_SIZE)
    self._error_event.clear()


  def reset(self):
    """ Reset device/thread using thread event call """
    self._reset_event.set()


  def check_status(self):
    """ Check Teensy status and reset in case of unrecoverable error """
    # No point checking status when resetting
    if self._reset_event.is_set():
      return False

    if self.is_error_flagged():
      printn_stderr("ERROR: Thread reported an error. Resetting!")
      self.reset()
      return False

    teensy_flags = self.get_teensy_flags()
    if teensy_flags != 0x00:
      printn_stderr(f"WARNING: Teensy ADC flags is {teensy_flags:>08b}")
      if (teensy_flags & ADCDACDevice.TEENSY_FLAG_OVERRUN or
          teensy_flags & ADCDACDevice.TEENSY_FLAG_SYNC_ERR):
        printn_stderr("  Overrun or sync error. Resetting!")
        self.reset()
        return False

    return True


  def run(self):
    """ ADC-DAC data thread main loop """
    while not self._stop_event.is_set() and threading.main_thread().is_alive():
      if self._reset_event.is_set():
        self._reset_internal()
        self._reset_event.clear()

      # Handle ADC data (from Teensy)
      adc_data = self._adcdac_device.get_adc_block()
      if adc_data is None:
        self._error_event.set()
        printn_stderr("ERROR: Failure getting ADC data")
      else:
        # Update adc data
        if not self._put_adc_data(adc_data):
          self._error_event.set()
          printn_stderr("ERROR: Failure storing ADC data")

      # Handle all(!) DAC data (to Teensy)
      while self._has_dac_data():
        dac_data = self._get_dac_data()
        # NOTE: put_dac_block() is a blocking call, so in case hardware buffers
        #       are full we block the loop when not using a write timeout!
        try:
          self._adcdac_device.put_dac_block(dac_data)
        except serial.SerialTimeoutException:
          self._error_event.set()
          break  # Break loop so we don't block
