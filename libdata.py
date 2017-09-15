# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os

from modules.DataProcessing import RawDataProcessor
from modules.ReaderBookEventManagement import ReaderManager, BookManager, ReadersEventManager

# --------------------------------------------------------
data = RawDataProcessor.derive_raw_data(folder_path=os.path.join('data'))
manager_reader = ReaderManager(folder_path=os.path.join('data'))
print(manager_reader)
# manager_reader.extend(data)
# manager_reader.save()
manager_book = BookManager(folder_path=os.path.join('data'))
# manager_book.extend(data)
# manager_book.save()
manager_events = ReadersEventManager(folder_path=os.path.join('data'))
# manager_events.extend(data)
# manager_events.save()


# --------------------------------------------------------


if __name__ == '__main__':
    import time
    start_time = time.time()
    # ------------------------------
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration)//3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.2f} s'.format(hour, minutes, seconds))
