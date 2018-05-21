# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging
import os
import shelve

from Config import DataConfig
from Interface import AbstractDataManager
from structures.Book import Book
from structures.Event import Event
from structures.Reader import Reader
from utils.Persisit import Pdict, Pseries


class DataProxy(AbstractDataManager):

    def __init__(self, writeback=False):
        from modules.DataBase import ShelveWrapper
        self.__books__ = ShelveWrapper(os.path.join(DataConfig.data_path, 'books'), writeback=writeback)
        self.__readers__ = ShelveWrapper(os.path.join(DataConfig.data_path, 'readers'), writeback=writeback)
        self.__events__ = ShelveWrapper(os.path.join(DataConfig.data_path, 'events'), writeback=writeback)

    def include(self, value):
        if isinstance(value, Book):
            if value.index in self.__books__:
                stored = self.__books__[value.index]
                stored.update_from(value)
                self.__books__[value.index] = stored
            else:
                self.__books__[value.index] = value
        elif isinstance(value, Reader):
            if value.index in self.__readers__:
                stored = self.__readers__[value.index]
                stored.update_from(value)
                self.__readers__[value.index] = stored
            else:
                self.__readers__[value.index] = value
        elif isinstance(value, Event):
            if value.hashable_key in self.__events__:
                stored = self.__events__[value.hashable_key]
                stored.update_from(value)
                self.__events__[value.hashable_key] = stored
            else:
                self.__events__[value.hashable_key] = value
        else:
            logging.debug(LogInfo.variable_detail(value))
            raise TypeError

    def extend(self, iterable):
        for item in iterable:
            try:
                self.include(item)
            except TypeError:
                pass

    def readers(self):
        for reader in self.__readers__.values():
            yield reader

    def books(self):
        for book in self.__books__.values():
            yield book

    def events(self):
        for event in self.__events__.values():
            yield event

    def close(self):
        self.__books__.close()
        self.__readers__.close()
        self.__events__.close()


def store_record_data():
    from tqdm import tqdm
    from modules.DataLoad import RawDataProcessor
    data_proxy = DataProxy()
    for d_object in tqdm(RawDataProcessor.iter_data_object(), desc='storing record data'):
        data_proxy.include(Book.init_from(d_object))
        data_proxy.include(Reader.init_from(d_object))
        data_proxy.include(Event.init_from(d_object))
    data_proxy.close()


def induct_events():
    from tqdm import tqdm
    from utils.FileSupport import get_pdict, load_pickle
    readers = get_pdict('readers')
    events = load_pickle('events')

    for reader_id in readers.keys():
        logging.debug(LogInfo.running('inducting', reader_id))
        sum_list = list()
        for event in tqdm(events.values(), desc='collecting events'):
            assert isinstance(event, Event)
            if event.reader_id == reader_id:
                sum_list.append(event)
        Pseries.init_from(
            sum_list,
            os.path.join(DataConfig.data_path, 'inducted_events', reader_id),
            index_tag='event_date'
        )


class DataInduction(object):
    def __init__(self):
        self.__path__ = folder_path

    def __pjoin__(self, name: str):
        return os.path.join(self.__path__, name)

    def get(self, key: str):
        if os.path.exists(self.__pjoin__(key)):
            return Pseries(self.__pjoin__(key), keep_history=True)
        else:
            return Pseries(self.__pjoin__(key), keep_history=False)


# --------------------------------------------------------
if __name__ == '__main__':
    from utils.Logger import LogInfo, set_logging
    set_logging()
    LogInfo.initiate_time_counter()
    # ------------------------------


    # ------------------------------
    print(LogInfo.time_passed())
