""" ELDUtils Class """
# (C) Copyright 2020-2023 ELD/LION, Leiden University
#
# Written by        : ing. A.C.J. van Amersfoort
# Python Version    : 3
# Initial date      : 2017
# Last Modified     : April 4, 2023
# Description       : Library with various handy Python functions

import sys

def print_stdout(line):
  """ Print to stdout without linefeed """
  sys.stdout.write(line)


def print_stderr(line):
  """ Print to stderr without linefeed """
  sys.stderr.write(line)


####################################################
# Helper function to write line to stdout          #
# also flushes stdout else pipes may work properly #
####################################################
def printn_stdout(line):
  """ Print to stdout with linefeed """
  sys.stdout.write(line + "\n")
#  sys.stdout.flush()


####################################################
# Helper function to write line to stdout          #
# also flushes stdout else pipes may work properly #
####################################################
def printn_stderr(line):
  """ Print to stderr with linefeed """
  sys.stderr.write(line + "\n")
#  sys.stderr.flush()


def clamp(num, min_value, max_value):
  """ Clamp passed value to min/max """
  return max(min(num, max_value), min_value)


def bytes_to_hex(data):
  """ Debug function to print data byte(s) as hex """
  if isinstance(data, bytes) or isinstance(data, bytearray) or isinstance(data, list):
    hex_str = ' '.join(f'0x{x:02X}' for x in data)
  else:
    hex_str = f'0x{data:02X}'

  return hex_str
