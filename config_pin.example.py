"""Configuration file that identifies which pins are pulse inputs.
Copy this file to "config_pin.py" and modify accordingly.
"""
import board

# The list of pin names to use for pulse inputs.  Any number of pins can
# be accommodated.  3 bytes per pin will be transmitted by LoRaWAN plus a one byte
# message type.  So, only 3 pins can fit within the SF10 11-byte US limit.
PINS = [board.A0, board.A1]
