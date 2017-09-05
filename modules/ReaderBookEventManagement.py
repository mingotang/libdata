# -*- encoding: UTF-8 -*-
# --------------------------------------------------------
import pickle
from modules.DataStructure import GeneralDict, DataObject
# --------------------------------------------------------


# --------------------------------------------------------
class GeneralManager(GeneralDict):
    def __init__(self):
        GeneralDict.__init__(self)
# --------------------------------------------------------


# --------------------------------------------------------
class BookManager(GeneralManager):
    def __init__(self):
        GeneralManager.__init__(self)
# --------------------------------------------------------


# --------------------------------------------------------
class ReaderManager(GeneralManager):
    def __init__(self):
        GeneralManager.__init__(self)
# --------------------------------------------------------


# --------------------------------------------------------
class ReadersEventManager(GeneralManager):
    def __init__(self):
        GeneralManager.__init__(self)
# --------------------------------------------------------


# --------------------------------------------------------
# --------------------------------------------------------


# --------------------------------------------------------
if __name__ == '__main__':
    import time
    start_time = time.time()
    # ------------------------------
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration) // 3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.2f} s'.format(hour, minutes, seconds))
