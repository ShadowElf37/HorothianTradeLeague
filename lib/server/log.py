"""
log.py
Project Mercury
Yovel Key-Cohen
"""
import time

class Log:
    STATUS = 'STATUS'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'

    """For tracking information; use over print for the automatic timestamps."""
    def __init__(self, debug=False, include_level=False):
        self.ledger = []
        self.debug = debug
        self.include_level = include_level

    # Logs any number of strings in its ledger
    def log(self, *event, lvl=INFO):
        event = tuple(map(str, event))
        if self.include_level:
            item = (lvl, self.get_time(), ' '.join(event))
        else:
            item = (self.get_time(), ' '.join(event))
        if self.debug:
            print(item)
        self.ledger.append(item)

    # Dumps the current ledger to a unique log file; should be called on server close
    def dump(self):
        # Gets current log number
        lcf = open("data/log_counter.dat", 'r')
        lc = int(lcf.read())
        lcf.close()
        lcf = open("data/log_counter.dat", 'w')
        lcf.write(str(lc+1))
        lcf.close()

        # Creates file and writes ledger
        f = open("logs/%d_ProjectMercuryLog_%s.log" % (lc, Log.get_time_alt()), 'w')
        f.write('\n'.join(map(str, self.ledger)))
        f.close()

    # Gets a timestamp
    @staticmethod
    def get_time():
        timestamp = time.strftime('%d %H:%M:%S')
        return timestamp

    # Gets a timestamp (made for dump())
    @staticmethod
    def get_time_alt():
        timestamp = time.strftime('%y-%m-%d_%H;%M;%S')
        return timestamp