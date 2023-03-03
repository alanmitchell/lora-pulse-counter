# Functions releated to LoRa communication

def send_reboot(e5_uart):
    """Send a message indicating that a reboot occurred."""
    print('reboot')     # debug print
    cmd = bytes('AT+MSGHEX="02"\n', 'utf-8')
    e5_uart.write(cmd)

def send_data(msg_data, e5_uart):
    """Send data in message."""
    cmd = bytes(f'AT+MSGHEX="{msg_data}"\n', 'utf-8')
    e5_uart.write(cmd)

def check_for_downlink(lin, e5_uart, config):
    """'lin' is a line received from the E5 module.  Check to see if it is
    a Downlink message, and if so, process the request. config is the
    configuration object for the application."""
    if 'PORT: 1; RX: "' in lin:
        # this is a Downlink message. Pull out the Hex string data.  First two
        # characters indicate the request type.
        data = lin.split('"')[-2]
        if data[:2] == '01':
            # Request to change Data Rate. Data rate is given in the 3rd & 4th 
            # characters.
            dr = int(data[2:4], 16)
            if dr in (0, 1, 2, 3):
                cmd = bytes('AT+DR=%s\n' % dr, 'utf-8')
                e5_uart.write(cmd)

        elif data[:2] == '03':
            # Request to change time between transmissions, 2 byte (4 Hex characters)
            secs = int(data[2:6], 16)
            print('Setting time between transmits to', secs, 'seconds')
            config.secs_between_xmit = secs
