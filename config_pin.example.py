"""Configuration file that identifies which pins are pulse inputs.
Copy this file to "config_pin.py" and modify accordingly.
"""
import board

# The list of pin names to use for pulse inputs.  Any number of pins can
# be accommodated.  3 bytes per pin will be transmitted by LoRaWAN plus a one byte
# message type.  So, only 3 pins can fit within the SF10 11-byte US limit.

PINS = [board.D0, board.D1]     # 2 pulse inputs
# PINS = [board.D0, board.D1, board.D2]        # 3 pulse inputs
