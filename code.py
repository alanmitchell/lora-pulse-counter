"""CircuitPython code to implement a dual channel pulse counter and send the data 
via LoRaWAN.  Cumulative counts are tracked and transmitted.
"""
import time
import board
import busio
from digitalio import DigitalInOut, Direction, Pull
import supervisor
import sys

import lora
from config import config

# The number of milliseconds to wait for bouncing to stop
BOUNCE_MS = 20

# Serial port talking to LoRaWAN module, SEEED Grove E5.
e5_uart = busio.UART(
    board.TX, board.RX, 
    baudrate=9600, 
    timeout=0.0,                 # need some timeout for readline() to work.
    receiver_buffer_size=128,     # when downlink is received, about 90 bytes are received.
)

# wait for join before sending reboot; join only occurs during power up.
time.sleep(8.0)
lora.send_reboot(e5_uart)
time.sleep(7.0)    # need to wait for send to continue.

# Set up the pins that accept dry switch pulses
pin_pulse = [DigitalInOut((board.A0)), DigitalInOut((board.A1))]
for pin in pin_pulse:
    pin.direction = Direction.INPUT
    pin.pull = Pull.UP

# variable to accumulate characters read in from the E5 Lora module.
recv_buf = ''

# initial values of the pulse pins
pin_value = [pin.value for pin in pin_pulse]

# array to hold cumulative pulse counts
counts = config.starting_counts

COUNT_ROLLOVER = 2**24     # only let the above counts reach 2**24

# Using a state machine to track whether waiting for transition or waiting
# for the debounce period to end.
STATE_LOOKING = 0
STATE_DEBOUNCING = 1
pin_state = [STATE_LOOKING] * len(pin_pulse)

# Tracks the supervisor time (ms) when the transition first occured.
pin_transition_time = [None] * len(pin_pulse)

# Tracks when the last LoRa transmit occurred
_TICKS_MAX = const((1<<29) - 1)
last_xmit = supervisor.ticks_ms()

while True:

    try:
        # cycle through all the pins to analyze current state
        for ix, pin in enumerate(pin_pulse):

            current_pin_value = pin.value

            if pin_state[ix] == STATE_DEBOUNCING:
                if (supervisor.ticks_ms() - pin_transition_time[ix]) & _TICKS_MAX >= BOUNCE_MS:
                    if current_pin_value != pin_value[ix] and current_pin_value == False:
                        # a falling transition occurred
                        counts[ix] = (counts[ix] + 1) % COUNT_ROLLOVER
                        
                    pin_value[ix] = current_pin_value
                    pin_state[ix] =  STATE_LOOKING

            elif pin_state[ix] == STATE_LOOKING:
                if current_pin_value != pin_value[ix]:
                    pin_state[ix] =  STATE_DEBOUNCING
                    pin_transition_time[ix] = supervisor.ticks_ms()

        # Read a character that may have been sent by the E5 module.  Check to 
        # see if they are downlinks & process if so.
        ch = e5_uart.read(1)
        if ch is not None:
            if ch in (b'\n', b'\r'):
                if len(recv_buf):
                    print(recv_buf)
                    lora.check_for_downlink(recv_buf, e5_uart)
                    recv_buf = ''
            else:
                try:
                    recv_buf += str(ch, 'ascii')
                except:
                    print('Bad character:', ch)

        # Check to see if it is time to transmit
        cur_ticks = supervisor.ticks_ms()
        ticks_since_xmit = (cur_ticks - last_xmit) & _TICKS_MAX
        if ticks_since_xmit >= config.secs_between_xmit * 1000:
            last_xmit = cur_ticks
            content = ''
            for ct in counts:
                content += f'{ct:06X}'
            msg = '06' + content
            print(msg)
            lora.send_data(msg, e5_uart)
            # store heat and flow counts in case reboot
            config.starting_counts = counts

    except KeyboardInterrupt:
        sys.exit()
    
    except:
        print('Unknown error.')
        raise
        time.sleep(1)
