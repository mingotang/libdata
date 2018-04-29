# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging
import os
import time

from Config import DataConfig
from Interface import AbstractDataObject, AbstractDataManager
from structures.Book import Book
from structures.Event import Event
from structures.Reader import Reader
from utils.Persisit import Pdict, Pseries


class DataStore(AbstractDataManager):

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

    def to_dict(self):
        return self.data


def store_book():
    from modules.DataLoad import RawDataProcessor
    from utils.FileSupport import init_pdict
    data_manager = DataStore(Book, 'index')
    for d_object in RawDataProcessor.iter_data_object(folder_path='data'):
        data_manager.include(Book.init_from(d_object))
    init_pdict(data_manager.to_dict(), 'books')


def store_reader():
    from modules.DataLoad import RawDataProcessor
    from utils.FileSupport import init_pdict
    data_manager = DataStore(Reader, 'index')
    for d_object in RawDataProcessor.iter_data_object(folder_path='data'):
        data_manager.include(Reader.init_from(d_object))
    init_pdict(data_manager.to_dict(), 'readers')


def store_event():
    from modules.DataLoad import RawDataProcessor
    from utils.FileSupport import init_pdict
    data_manager = DataStore(Event, 'hashable_key')
    for d_object in RawDataProcessor.iter_data_object(folder_path='data'):
        data_manager.include(Event.init_from(d_object))
    init_pdict(data_manager.to_dict(), 'events')


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
    def __init__(self, folder_path: str):
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
