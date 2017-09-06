# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os
from modules.DataProcessing import RawDataProcessor
# ---------------------------------------------------------------------------


# --------------------------------------------------------
# --------------------------------------------------------


if __name__ == '__main__':
    import time
    start_time = time.time()
    # ------------------------------
    # raw_data = RawDataProcessor(folder_path=os.path.join('data'))
    # data = raw_data.derive_raw_data()
    data = RawDataProcessor(folder_path='data').derive_raw_data()
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration)//3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.2f} s'.format(hour, minutes, seconds))
