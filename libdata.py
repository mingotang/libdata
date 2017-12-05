# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os

from modules.ServiceComponents import RawDataProcessor
from modules.DataManagement import ReaderManager, BookManager, ReadersEventManager

# --------------------------------------------------------


# --------------------------------------------------------


if __name__ == '__main__':
    import time
    start_time = time.time()
    # ------------------------------
    import sys
    for progress in range(100):
        # time.sleep(0.2)
        #
        print('\rtest {0:d}'.format(progress), end='')
        sys.stdout.flush()
        time.sleep(2)
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration)//3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.2f} s'.format(hour, minutes, seconds))
