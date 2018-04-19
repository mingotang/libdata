# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging
import os
import time

from Interface import AbstractDataObject, AbstractDataManager
from structures.Book import Book
from structures.Event import Event
from structures.Reader import Reader
from utils.Persisit import Pdict


class DataManager(AbstractDataManager):

    def __init__(self, data_type: type, index_tag: str):
        self.__index_tag__ = index_tag
        self.__data_type__ = data_type
        self.data = dict()

    def include(self, value):
        if isinstance(value, self.__data_type__):
            tag = getattr(value, self.__index_tag__)
            if tag not in self.data:
                self.data[tag] = value
            else:
                stored = self.data[tag]
                stored.update_from(value)
                self.data[tag] = stored
        else:
            logging.debug(LogInfo.variable_detail(value))
            raise TypeError

    def extend(self, iterable):
        for item in iterable:
            self.include(item)

    def to_pdict(self, data_path: str, keep_history=False):
        if not os.path.exists(data_path):
            os.mkdir(data_path)
        Pdict.init_from(self.data, data_path=data_path, keep_history=keep_history)


class DataManagerByDB(AbstractDataManager):
    from modules.DataBase import SqliteWrapper
    """[Depreciated]"""

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
    from Config import DataConfig
    from modules.DataLoad import RawDataProcessor
    from utils.Logger import LogInfo, set_logging

    set_logging()

    data_manager = DataManager(Book, 'index')
    for d_object in RawDataProcessor.iter_data_object(folder_path='data'):
        data_manager.include(Book.init_from(d_object))
    data_manager.to_pdict(os.path.join(DataConfig.persisted_data_path, 'books'), keep_history=False)

    data_manager = DataManager(Reader, 'index')
    for d_object in RawDataProcessor.iter_data_object(folder_path='data'):
        data_manager.include(Reader.init_from(d_object))
    data_manager.to_pdict(os.path.join(DataConfig.persisted_data_path, 'readers'), keep_history=False)

    data_manager = DataManager(Event, 'hashable_key')
    for d_object in RawDataProcessor.iter_data_object(folder_path='data'):
        data_manager.include(Event.init_from(d_object))
    data_manager.to_pdict(os.path.join(DataConfig.persisted_data_path, 'events'), keep_history=False)

    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration) // 3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    time.sleep(1)
    print('\nRunning time: {0:d} h {1:d} m {2:.2f} s'.format(hour, minutes, seconds))
