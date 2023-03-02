"""Holds configuration information and also stores/retrieves some settings
from non-volatile memory.
"""
from microcontroller import nvm        # non-volatile memory
import struct

class Configuration:

    # --- Settings related to Average Power Reader
    # If not changed by a downlink, this is the default number seconds between
    # transmission of an average power value.
    SECS_BETWEEN_XMIT_DEFAULT = 600

    def __init__(self):
        # for the few settings that are changeable via downlink, check non-volatile 
        # memory to see what value to use.  NVM bytes will be 255 if they have never
        # been written before.

        # read values from non-volatile storage. Need the "<" in the format 
        # string so no padding is included in the bytes.
        # FIX ME: Need to know how many counts there are before reading from NVM.
        vals = struct.unpack('<HII', nvm[0:10])
        self._secs_between_xmit = vals[0]
        self._starting_counts = vals[1:]

        # set to defaults, if values haven't been initialized
        if self._secs_between_xmit > 24 * 3600:
            self._secs_between_xmit = SECS_BETWEEN_XMIT_DEFAULT
        for ix, val in enumerate(self._starting_counts):
            if val > 2**24 - 1:
                self._start_flow_count[ix] = 0

    def save_to_nvm(self):
        """Saves the key config variables to non-volatile storage. 
        """
        # need the "<" in the format string to avoid padding.
        pack_fmt = '<H' + 'I' * len(self.starting_counts)
        byte_count = 2 + 4 * len(self._starting_counts)
        nvm[0:byte_count] = struct.pack(
            pack_fmt, 
            self._secs_between_xmit,
            *self._starting_counts
            )

    @property
    def secs_between_xmit(self):
        """With the Averaging Reader, seconds between transmission
        of average values."""
        return self._secs_between_xmit

    @secs_between_xmit.setter
    def secs_between_xmit(self, val):
        if val < 2**16:
            self._secs_between_xmit = val
            self.save_to_nvm()

    @property
    def starting_counts(self):
        """Returns the starting count heat and flow counts.
        """
        return self._starting_counts

    @starting_counts.setter
    def starting_counts(self, counts):
        self._starting_counts = counts
        self.save_to_nvm()

# Instantiate a Config object that will be imported by modules that need access
# to the configuration information.  So, those modules will execute:
#    from config import config
# to get this object.
config = Configuration()
