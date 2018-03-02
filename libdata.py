# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging

from ServiceComponents import RawDataProcessor
from DataBaseWrapper import SqliteWrapper
from DataManagement import ReaderManager, BookManager, ReadersEventManager
from ServiceComponents import LogInfo


logging.basicConfig(
        level=logging.DEBUG,  # 定义输出到文件的log级别，
        format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',  # 定义输出log的格式
        datefmt='%Y-%m-%d %A %H:%M:%S',  # 时间
        # filename=param.log_file_name,  # log文件名
        # filemode='w',
    )


# --------------------------------------------------------
def store_raw_data_to_local_database():
    """ 大概需要内存 3GB， 运行时间 7 分钟"""
    local_db = SqliteWrapper(flush_db=True)

    logging.info(LogInfo.running('connect sqlite3 database', 'finished'))
    logging.warning(LogInfo.running('flush sqlite3 database when connect', 'finished'))

    data = RawDataProcessor.derive_raw_data(folder_path='data')
    logging.info(LogInfo.running('loading raw data', 'loaded'))

    reader_data = ReaderManager()
    reader_data.extend(data)
    local_db.add_all(reader_data.data)
    logging.info(LogInfo.running('storing reader data', 'finished'))
    del reader_data

    book_data = BookManager()
    book_data.extend(data)
    local_db.add_all(book_data.data)
    logging.info(LogInfo.running('storing book data', 'finished'))
    del book_data

    reader_event_data = ReadersEventManager()
    reader_event_data.extend(data)
    local_db.add_all(reader_event_data.data)
    logging.info(LogInfo.running('storing reader events data', 'finished'))
    del reader_event_data

    del data


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
