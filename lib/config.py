"""Has Configuration class; some info is stored in
non-volatile memory.
"""
from microcontroller import nvm        # non-volatile memory
import struct

class Configuration:

    # --- Settings related to Average Power Reader
    # If not changed by a downlink, this is the default number seconds between
    # transmission of an average power value.
    SECS_BETWEEN_XMIT_DEFAULT = 600

    def __init__(self, pin_count):

        # read values from non-volatile storage. Need the "<" in the format 
        # string so no padding is included in the bytes.
        try:
            vals = struct.unpack('<H' + 'I' * pin_count, nvm[0:2 + pin_count * 4])
        except:
            # Initial values in nvm overflow small int for counts
            vals = [0] * (pin_count + 1)
            vals[0] = Configuration.SECS_BETWEEN_XMIT_DEFAULT
        self._secs_between_xmit = vals[0]
        self._starting_counts = list(vals[1:])

        # set to defaults, if values haven't been initialized
        if self._secs_between_xmit > 24 * 3600:
            self._secs_between_xmit = Configuration.SECS_BETWEEN_XMIT_DEFAULT
        for ix, val in enumerate(self._starting_counts):
            if val > 2**24 - 1:
                self._start_flow_count[ix] = 0

        # code above may have changed values, so save to NVM.
        self.save_to_nvm()

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
