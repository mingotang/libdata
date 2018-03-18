# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging
import time

from Interface import AbstractDataObject, AbstractDataManager
from modules.DataBase import SqliteWrapper
from structures.Book import Book
from structures.Event import Event
from structures.Reader import Reader


class DataManager(AbstractDataManager):

    def __init__(self, db: SqliteWrapper):
        """General class for libdata info management"""
        self._db = db

    def include(self, value):
        if isinstance(value, AbstractDataObject):
            if self._db.exists(value):
                self.__update_value__(value)
            else:
                self.__add_value__(value)
        else:
            raise TypeError

    def __update_value__(self, value):
        if isinstance(value, (Book, Reader)):
            stored_value = self._db.get_one(type(value), index=value.index)
            stored_value.update_from(value)
            self._db.merge(stored_value)
        elif isinstance(value, Event):
            stored_value = self._db.get_one(Event,
                                            book_id=value.book_id, reader_id=value.reader_id,
                                            event_date=value.event_date, event_type=value.event_type)
            stored_value.update_from(value)
            self._db.merge(stored_value)
        else:
            raise TypeError

    def __add_value__(self, value):
        if isinstance(value, list):
            self._db.add_all(value)
        else:
            self._db.add(value)

    def extend(self, value_list: list):
        for_add = list()
        for_change = list()
        check_list = self._db.exists(value_list)
        for i in range(len(value_list)):
            if check_list[i] is True:
                for_change.append(value_list[i])
            else:
                for_add.append(value_list[i])
        self.__add_value__(for_add)
        for item in for_change:
            self.__update_value__(item)


# --------------------------------------------------------
if __name__ == '__main__':
    # import time
    start_time = time.time()
    # ------------------------------
    # store data to sqlite database
    from tqdm import tqdm
    from modules.DataBase import SqliteWrapper
    from modules.DataLoad import RawDataProcessor
    from utils.Logger import LogInfo, set_logging

    set_logging()

    local_db = SqliteWrapper(clear_db=True, exist_optimize=False)
    logging.info(LogInfo.running('connect sqlite3 database', 'finished'))
    logging.warning(LogInfo.running('flush sqlite3 database when connect', 'finished'))

    data = RawDataProcessor.derive_raw_data(folder_path='data')
    logging.info(LogInfo.running('loading raw data', 'loaded'))

    data_manager = DataManager(local_db)

    # book_dict = dict()
    # for item in tqdm([Book.init_from(var) for var in data], desc='converting Book info'):
    #     if item.index in book_dict:
    #         book_dict[item.index].update_from(item)
    #     else:
    #         book_dict[item.index] = item
    # data_manager.extend(list(book_dict.values()))
    # logging.info(LogInfo.running('extending Book info', 'finished'))
    # del book_dict

    reader_dict = dict()
    for item in tqdm([Reader.init_from(var) for var in data], desc='converting Book info'):
        if item.index in reader_dict:
            reader_dict[item.index].update_from(item)
        else:
            reader_dict[item.index] = item
    data_manager.extend(list(reader_dict.values()))
    data_manager.extend([Reader.init_from(var) for var in data])
    logging.info(LogInfo.running('extending Reader info', 'finished'))
    #
    # data_manager.extend([Event.init_from(var) for var in data])
    # logging.info(LogInfo.running('extending Event info', 'finished'))
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration) // 3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    time.sleep(1)
    print('\nRunning time: {0:d} h {1:d} m {2:.2f} s'.format(hour, minutes, seconds))
