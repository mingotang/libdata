# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os

from Config import DataConfig
from structures import Book, Event, Reader
from structures import ShelveWrapper, TimeRange
from utils import get_logger


logger = get_logger(module_name=__file__)


class EventStore(object):
    def __init__(
            self, folder_path: str=os.path.join(DataConfig.data_path, 'events'),
            writeback: bool=False, new: bool=False,
    ):
        if not os.path.exists(folder_path):
            if new is False:
                raise RuntimeError('EventStore folder should be inited before loading')
            else:
                os.makedirs(folder_path)

        self.__path__ = folder_path
        self.__data__ = self.__connect_folder__(writeback=writeback)

    def store(self, data):
        from collections import Iterable, Mapping

        stored = self.__connect_folder__(False)

        # check data
        if isinstance(data, Mapping):
            for event in data.values():
                assert event.date.strftime('%Y%m') not in stored, 'Already has data in month {}'.format(event.date)

        elif isinstance(data, Iterable):
            for event in data:
                assert isinstance(event, Event)
                assert event.date.strftime('%Y%m') not in stored, 'Already has data in month {}'.format(event.date)

        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('data', (Iterable, Mapping), data)

        # storing data
        if isinstance(data, Mapping):
            for event in data.values():
                assert isinstance(event, Event)
                tag = event.date.strftime('%Y%m')

                if tag not in stored:
                    stored_db = ShelveWrapper(os.path.join(self.__path__, tag), new=True)
                    stored[tag] = stored_db
                else:
                    stored_db = stored[tag]

                if tag in stored_db:
                    stored_event = stored_db[event.hashable_key]
                    stored_event.update_from(event)
                    stored_db[event.hashable_key] = stored_event
                else:
                    stored_db[event.hashable_key] = event

        elif isinstance(data, Iterable):
            for event in data:
                assert isinstance(event, Event)
                tag = event.date.strftime('%Y%m')

                if tag not in stored:
                    stored_db = ShelveWrapper(os.path.join(self.__path__, tag), new=True)
                    stored[tag] = stored_db
                else:
                    stored_db = stored[tag]

                if tag in stored_db:
                    stored_event = stored_db[event.hashable_key]
                    stored_event.update_from(event)
                    stored_db[event.hashable_key] = stored_event
                else:
                    stored_db[event.hashable_key] = event

        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('data', (Iterable, Mapping), data)

        for tag in stored:
            stored[tag].close()

    def __connect_folder__(self, writeback: bool):
        connect = dict()

        for file in os.listdir(self.__path__):

            if len(file) == 0:
                continue
            if file[0] in ('.', '_', '$', '@'):
                continue

            file = file.split('.')
            file = file[0]

            connect[file] = ShelveWrapper(os.path.join(self.__path__, file), writeback=writeback)

        return connect

    def derive(self, time_range: TimeRange):
        from structures import DataDict
        start = time_range.start_time.date().strftime('%Y%m')
        end = time_range.end_time.date().strftime('%Y%m')
        derive_data = DataDict()
        for time, db in self.__data__.items():
            if start <= time <= end:
                assert isinstance(db, ShelveWrapper)
                for key, event in db.items():
                    assert isinstance(event, Event)
                    if start <= event.date.strftime('%Y%m') <= end:
                        derive_data[key] = event
        return derive_data


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

        self.__event_store__ = None

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
    def event_store(self):
        if self.__event_store__ is None:
            self.__event_store__ = EventStore(folder_path=os.path.join(DataConfig.data_path, 'events'))

        return self.__event_store__

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
        elif isinstance(self.__inducted_events__, ShelveWrapper):
            return self.__inducted_events__
        else:
            raise RuntimeError

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
    d_p = DataProxy(new=True)
    for d_object in tqdm(RawDataProcessor.iter_data_object(), desc='storing record data'):
        d_p.include(Book.init_from(d_object))
        d_p.include(Reader.init_from(d_object))
        d_p.include(Event.init_from(d_object))
    d_p.close()


if __name__ == '__main__':
    logger.initiate_time_counter()
    # ------------------------------
    # store_record_data()
    # data_manager = DataManager(writeback=False)
    # data_proxy = DataProxy()
    # data_proxy.execute_events_induction('date')
    # data_proxy.close()

    from tqdm import tqdm
    from modules.DataLoad import RawDataProcessor

    data_proxy = DataProxy()

    event_store = EventStore(new=True)
    event_store.store(data_proxy.events.to_dict())
    # ------------------------------
    logger.print_time_passed()
