# Written by Arno Bakker
# see LICENSE.txt for license information

'''
The Core package contains the core functionalities of the Tribler project
'''

from threading import RLock
import logging

# Written by BitTornado authors and Arno Bakker
# see LICENSE.txt for license information

from Tribler import LIBRARYNAME
from Tribler.Core.version import version_id

logger = logging.getLogger(__name__)

if LIBRARYNAME == "Tribler":
    product_name = 'Tribler'
    version_short = 'Tribler-' + version_id
    report_email = 'tribler@tribler.org'
    # Arno: looking at Azureus BTPeerIDByteDecoder this letter is free
    # 'T' is BitTornado, 'A' is ABC, 'TR' is Transmission
    TRIBLER_PEERID_LETTER = 'R'
else:
    version_id = '3.2.0'  # aka M32
    product_name = 'NextShare'
    version_short = 'NextShare-' + version_id
    report_email = 'support@p2p-next.org'
    # Arno: looking at Azureus BTPeerIDByteDecoder this letter is free
    # 'T' is BitTornado, 'A' is ABC, 'TR' is Transmission
    TRIBLER_PEERID_LETTER = 'N'


version = version_short + ' (' + product_name + ')'


def warnIfDispersyThread(func):
    """
    We'd rather not be on the Dispersy thread, but if we are lets continue and
    hope for the best. This was introduced after the database thread stuffs
    caused deadlocks. We weren't sure we got all of them, so we implemented
    warnings instead of errors because they probably wouldn't cause a deadlock,
    but if they did we would have the warning somewhere.

    Niels dixit.
    """
    def invoke_func(*args, **kwargs):
        from twisted.python.threadable import isInIOThread
        from traceback import print_stack

        if isInIOThread():
            import inspect
            caller = inspect.stack()[1]
            callerstr = "%s %s:%s" % (caller[3], caller[1], caller[2])

            from time import time
            logger.error("%d CANNOT BE ON DISPERSYTHREAD %s %s:%s called by %s", long(time()),
                        func.__name__, func.func_code.co_filename, func.func_code.co_firstlineno, callerstr)
            print_stack()

        return func(*args, **kwargs)

    invoke_func.__name__ = func.__name__
    return invoke_func


class NoDispersyRLock():

    def __init__(self):
        self.lock = RLock()
        self.__enter__ = self.lock.__enter__
        self.__exit__ = self.lock.__exit__

    @warnIfDispersyThread
    def acquire(self, blocking=1):
        return self.lock.acquire(blocking)

    @warnIfDispersyThread
    def release(self):
        return self.lock.release()
