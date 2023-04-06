""" ADC-DAC class for communication with Teensy ADC-DAC Board """
# (C) Copyright 2023 ELD/LION, Leiden University
#
# Written by        : H. Visser & A.C.J. van Amersfoort
# Dependencies      : (py)serial
# Python Version    : 3
# Initial date      : February 24, 2023
# Last Modified     : April 4, 2023

import time
import serial

from eldutils import bytes_to_hex

class ADCDACDevice():
  """ ADC-DAC class """

  # Teensy back buffer size. Match this with the value in the Teensy firmware!
  TEENSY_BACK_BUFFER_SIZE = 20

  # Status flags from Teensy
  TEENSY_FLAG_OVERRUN = 0x01
  TEENSY_FLAG_UNDERRUN = 0x02
  TEENSY_FLAG_SYNC_ERR = 0x04

  # Control flags for Teensy
  HOST_FLAG_RESET = 0x01

  # Class constructor
  def __init__(self,
               port_name=None,
               read_timeout=5,
               write_timeout=0.1,
               baudrate=10000000,
               adc_count=16,
               dac_count=8,
               adc_byte_size=4,
               dac_byte_size=4):
    self._port_name = port_name
    self._port = None
    self._read_timeout = read_timeout
    self._write_timeout = write_timeout
    self._baudrate = baudrate
    self._adc_count = adc_count
    self._dac_count = dac_count
    self._adc_byte_size = adc_byte_size
    self._dac_byte_size = dac_byte_size
    self._adc_block_size = (adc_count + 1) * adc_byte_size
    self._dac_block_size = (dac_count + 1) * dac_byte_size
    self.adc_flags = 0x00
    self.dac_flags = 0x00
    self.debug = False


  def init(self, reset=True):
    """ Init device """
    if self._port_name != "DUMMY":
      self._port = serial.Serial(port=self._port_name,
                                 baudrate=self._baudrate,
                                 timeout=self._read_timeout,
                                 write_timeout=self._write_timeout)

    if reset:
      self.reset()


  def reset(self):
    """ Reset device """
    for _x in range(self.TEENSY_BACK_BUFFER_SIZE):
      self.dac_flags = self.HOST_FLAG_RESET # Reset Teensy
      byte_data = self.pack_dac_data(None)
      self.put_dac_block(byte_data)

    time.sleep(1)

    self._port.reset_input_buffer()
#    self._port.reset_output_buffer()

    for _x in range(self.TEENSY_BACK_BUFFER_SIZE):
      self.dac_flags = 0x00 # Stop reset Teensy
      byte_data = self.pack_dac_data(None)
      self.put_dac_block(byte_data)

    # Reset adc flags, to prevent race condition between reset and first ADC transfer
    self.adc_flags = 0x00



  def deinit(self):
    """ Deinit device """
    if self._port is not None and self._port.is_open:
      self._port.close()


  def get_adc_block(self):
    """ Get block of ADC data """
    # @TODO: Timeout handling
    adc_data = bytearray()
    while True:
      if not self._port is None:
        ser_data = self._port.read(self._adc_block_size - len(adc_data))
        if not ser_data:
          return None

        adc_data += ser_data
        if self.debug:
          print(f"ser_data len={len(ser_data)}")
      else:
        # Good data:
        adc_data = (b'\xFF\x00\x00\x00'
                    b'\x00\x01\x02\x03'
                    b'\x01\x11\x12\x13'
                    b'\x02\x21\x22\x23'
                    b'\x03\x31\x32\x33'
                    b'\x04\x41\x42\x43'
                    b'\x05\x51\x52\x53'
                    b'\x06\x61\x62\x63'
                    b'\x07\x71\x72\x73'
                    b'\x08\x81\x82\x83'
                    b'\x09\x91\x92\x93'
                    b'\x0A\xA1\xA2\xA3'
                    b'\x0B\xB1\xB2\xB3'
                    b'\x0C\xC1\xC2\xC3'
                    b'\x0D\xD1\xD2\xD3'
                    b'\x0E\xE1\xE2\xE3'
                    b'\x0F\xF1\xF2\xF3'
                  )
        # Bad data:
#        adc_data += b'\x00\x02\xa1\x01\x00\x03a\xfe\xff\x04\x1e\xff\xff\x05\n2\x00\x06\xbc\xfe\xff\x07\x18\x03\x00\x08\xf1\xff\xff\t\x82\xfd\xff\n\xfa\xff\xff\x0bC\x00\x00\x0c4\xfe\xff\r\xfd\xff\xff\x0e\x00\x00\x00\x0f\xbf\xfe\xff \x9f\xfe\xff\x01(\x02'
        adc_data += b'\x00\x02\xa1\x01\x00\x03a\xfe\xff\x04\x1e\xff\xff\x05\n2\x00\x06\xbc\xfe\xff\x07\x18\x03\x00\x08\xf1\xff\xff\t\x82\xfd\xff\n\xfa\xff\xff\x0bC\x00\x00\x0c4\xfe\xff\r\xfd\xff\xff\x0e\x00\x00\x00\x0f\xbf\xfe\xff \x9f\xfe\xff\x01('
        adc_data = adc_data[0:self._adc_block_size]

      if self.debug:
        print(f"adc_data len={len(adc_data)}")
        print(f"adc_data={bytes_to_hex(adc_data)}")

      if len(adc_data) == self._adc_block_size:
        last_ff = 0
        sync_ok = True
        for byte_idx, data_byte in enumerate(adc_data):
          # Keep track of last 0xFF in case sync fails
          if data_byte == 0xFF:
            last_ff = byte_idx

          # Check sync byte positions
          if byte_idx % self._adc_byte_size == 0:
            field_idx = byte_idx // self._adc_byte_size

            # NOTE: First field holds flags, of which MSB is all 1's
            match_byte = (0xFF if field_idx == 0 else field_idx - 1)
            if data_byte != match_byte:  # Check (successive) ADC sync numbers:
              sync_ok = False

              if last_ff > 0:
                adc_data = adc_data[last_ff:]
              elif byte_idx < len(adc_data) - 1:
                adc_data = adc_data[(byte_idx + 1):]
              else:
                del adc_data[:]

              if self.debug:
                print(adc_data)
                print(f"sync failed at offset {byte_idx}. {bytes_to_hex(data_byte)} should be {bytes_to_hex(match_byte)}")

              break  # Get more data & retry

        # If we got the correct amount of data and the sync numbers are correct, we're done:
        if sync_ok:
          break

    # buffer should always have _adc_block_size at this point:
    if self.debug:
      print(f"adc_byte_data={bytes_to_hex(adc_data)}")

    return adc_data


  def put_dac_block(self, data):
    """ Put block DAC data """
    if not self._port is None:
      self._port.write(data)


  def unpack_adc_data(self, byte_data):
    """ Unpack byte based data and return as int data """
    int_samples = [0, [0] * (self._adc_count)]
    for byte_idx, _data in enumerate(byte_data):
      if byte_idx % 4 == 3:
        field_idx = byte_idx // 4
        if field_idx == 0:
          # Field 0 is status field
          self.adc_flags = byte_data[byte_idx - 2]
          sample_count = byte_data[(byte_idx - 1)]
          int_samples[0] = sample_count
        else:
          sample_as_bytes = byte_data[(byte_idx - 2):(byte_idx + 1)]
          int_samples[1][field_idx - 1] = int.from_bytes(sample_as_bytes, byteorder='little', signed=True)

    if self.debug:
      print(f"adc_int_samples={int_samples}")

    return int_samples


  def pack_dac_data(self, int_data, clip_int=False):
    """ Pack int data into bytes """
    byte_data = bytearray(self._dac_block_size)
    for field_idx in range(self._dac_count + 1):
      byte_idx = field_idx * 4

      # First field contains DAC-flags
      if field_idx == 0:
        byte_data[byte_idx] = 0xFF  # Control field
        byte_data[byte_idx + 1] = self.dac_flags
        byte_data[byte_idx + 2] = (int_data[0] if not int_data is None else 0)  # Sample #
        byte_data[byte_idx + 3] = 0x00  # Unused for now
      else:
        int_byte_size = self._dac_byte_size - 1
        if not int_data is None:
          int_val = int_data[1][field_idx - 1]
        else:
          int_val = 0

        if clip_int:
          # Clip values to min/max byte values (2's complement)
          int_val = max(min(int_val, 2**((int_byte_size * 8) - 1) - 1), -2**((int_byte_size * 8) - 1))

        if self.debug:
          print(f"int_data={int_val}")
        sample_as_bytes = int_val.to_bytes(length=int_byte_size,
                                           byteorder='little',
                                           signed=True)

        if self.debug:
          print(f"sample={bytes_to_hex(sample_as_bytes)}")

        # Store ADC-num in MSB:
        byte_data[byte_idx] = field_idx - 1

        byte_data[byte_idx + 1:byte_idx + 4] = sample_as_bytes
        if self.debug:
          print(f"dac_byte={bytes_to_hex(byte_data)}")

    if self.debug:
      print(f"dac_byte_samples={bytes_to_hex(byte_data)}")

    return byte_data
