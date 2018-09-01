# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os

from Config import DataConfig
from structures import Book, Event, Reader
from structures import ShelveWrapper
from utils import get_logger


logger = get_logger(module_name=__file__)


class DataProxy(object):

    def __init__(self, writeback: bool=False,
                 data_path: str=DataConfig.data_path,
                 operation_path: str=DataConfig.operation_path,
                 new: bool=False,
                 ):

        if not os.path.exists(data_path):
            os.makedirs(data_path)
        self.__path__ = data_path
        if not os.path.exists(operation_path):
            os.makedirs(operation_path)
        self.__operation_path__ = operation_path

        self.__books__ = ShelveWrapper(os.path.join(self.__path__, 'books'), writeback=writeback, new=new)
        self.__readers__ = ShelveWrapper(os.path.join(self.__path__, 'readers'), writeback=writeback, new=new)
        self.__events__ = ShelveWrapper(os.path.join(self.__path__, 'events'), writeback=writeback, new=new)

        try:
            self.__inducted_events__ = ShelveWrapper(os.path.join(self.__path__, 'inducted_events'))
        except FileNotFoundError:
            self.__inducted_events__ = None

    def include(self, value):
        """
        add value to shelve DB
        :param value: Book/Reader/Event
        :return: None
        """
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
            logger.debug_variable(value)
            raise TypeError('value should be of type Book/Event/Reader but got'.format(type(value)))

    def extend(self, iterable):
        from collections import Iterable
        if not isinstance(iterable, Iterable):
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('iterable', 'Iterable', iterable)
        else:
            for item in iterable:
                try:
                    self.include(item)
                except TypeError as e:
                    logger.error('elements of iterable should be Book/Event/Reader but got {}'.format(type(item)))
                    raise e

    def execute_events_induction(self, by_attr: str='date'):
        from tqdm import tqdm
        from structures import OrderedList

        inducted_events_dict = dict()

        for event in tqdm(self.events.values(), desc='inducting'):
            assert isinstance(event, Event)
            if event.reader_id not in inducted_events_dict:
                inducted_events_dict[event.reader_id] = OrderedList(Event, by_attr)
            inducted_events_dict[event.reader_id].append(event)

        inducted_events_db = ShelveWrapper.init_from(
            inducted_events_dict,
            os.path.join(self.__path__, 'inducted_events'),
            writeback=False
        )
        self.__inducted_events__ = inducted_events_db

        return inducted_events_db

    @property
    def readers(self):
        return self.__readers__

    @property
    def books(self):
        return self.__books__

    @property
    def events(self):
        return self.__events__

    @property
    def inducted_events(self):
        if self.__inducted_events__ is None:
            raise RuntimeError('Events should be inducted before calling inducted events')
        else:
            return self.__inducted_events__

    def close(self):
        self.__books__.close()
        self.__readers__.close()
        self.__events__.close()
        if isinstance(self.__inducted_events__, ShelveWrapper):
            self.__inducted_events__.close()

    def get_shelve(self, db_name: str, new=False):
        if new is False:
            if os.path.exists(os.path.join(self.__operation_path__, db_name)):
                return ShelveWrapper(os.path.join(self.__operation_path__, db_name))
            else:
                raise FileNotFoundError(
                    'Shelve database {} not exists.'.format(os.path.join(self.__operation_path__, db_name))
                )
        else:
            return ShelveWrapper(os.path.join(self.__operation_path__, db_name))


def store_record_data():
    """把txt文件的数据记录到 shelve 数据库中"""
    from tqdm import tqdm
    from modules.DataLoad import RawDataProcessor
    data_proxy = DataProxy(new=True)
    for d_object in tqdm(RawDataProcessor.iter_data_object(), desc='storing record data'):
        data_proxy.include(Book.init_from(d_object))
        data_proxy.include(Reader.init_from(d_object))
        data_proxy.include(Event.init_from(d_object))
    data_proxy.close()


if __name__ == '__main__':
    logger.initiate_time_counter()
    # ------------------------------
    store_record_data()
    # data_manager = DataManager(writeback=False)
    data_proxy = DataProxy()
    data_proxy.execute_events_induction('date')
    data_proxy.close()
    # ------------------------------
    logger.print_time_passed()
