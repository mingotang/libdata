# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os

from Config import DataConfig
from modules.structures.Book import Book
from modules.structures.Event import Event
from modules.structures.Reader import Reader
from utils.Logger import get_logger


logger = get_logger(module_name=__file__)


class DataProxy(object):

    def __init__(self, writeback=False, data_path=DataConfig.data_path):
        from utils.DataBase import ShelveWrapper
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        self.__path__ = data_path
        self.__books__ = ShelveWrapper(os.path.join(self.__path__, 'books'), writeback=writeback)
        self.__readers__ = ShelveWrapper(os.path.join(self.__path__, 'readers'), writeback=writeback)
        self.__events__ = ShelveWrapper(os.path.join(self.__path__, 'events'), writeback=writeback)

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

    @property
    def readers(self):
        return self.__readers__

    @property
    def books(self):
        return self.__books__

    @property
    def events(self):
        return self.__events__

    def close(self):
        self.__books__.close()
        self.__readers__.close()
        self.__events__.close()

    @staticmethod
    def get_shelve(db_name: str, new=False):
        from utils.DataBase import ShelveWrapper
        if new is False:
            if os.path.exists(os.path.join(DataConfig.operation_path, db_name)):
                return ShelveWrapper(os.path.join(DataConfig.operation_path, db_name))
            else:
                raise FileNotFoundError(
                    'Shelve database {} not exists.'.format(os.path.join(DataConfig.operation_path, db_name))
                )
        else:
            return ShelveWrapper(os.path.join(DataConfig.operation_path, db_name))

    @staticmethod
    def get_shelve_temp():
        import datetime
        from utils.DataBase import ShelveWrapper
        return ShelveWrapper(os.path.join(
            DataConfig.operation_path,
            '__temp_{}__'.format(datetime.datetime.now().strftime('%Y%m%d %H%M%S.%f'))
        ))


def store_record_data():
    from tqdm import tqdm
    from modules.DataLoad import RawDataProcessor
    data_proxy = DataProxy()
    for d_object in tqdm(RawDataProcessor.iter_data_object(), desc='storing record data'):
        data_proxy.include(Book.init_from(d_object))
        data_proxy.include(Reader.init_from(d_object))
        data_proxy.include(Event.init_from(d_object))
    data_proxy.close()


if __name__ == '__main__':
    from utils.Logger import LogInfo, set_logging
    set_logging()
    LogInfo.initiate_time_counter()
    # ------------------------------
    store_record_data()
    # data_manager = DataManager(writeback=False)
    # ------------------------------
    LogInfo.time_sleep(1)
    print(LogInfo.time_passed())
