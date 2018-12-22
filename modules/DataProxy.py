# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os

from modules.DataStore import BaseObjectStore, DateEventStore, RegisterMonthEventStore
from structures import Book, Event, Reader, DataDict
from structures import ShelveWrapper


class DataProxy(object):

    def __init__(self, data_path: str = None, writeback: bool = False,):
        from Environment import Environment
        from utils import get_logger
        self.log = get_logger(self.__class__.__name__)
        env = Environment.get_instance()

        if data_path is None:
            self.__path__ = env.data_path
        else:
            self.__path__ = data_path
        if not os.path.exists(self.__path__):
            os.makedirs(self.__path__)

        self.__operation_path__ = os.path.join(self.__path__, 'this_operation')
        if not os.path.exists(self.__operation_path__):
            os.makedirs(self.__operation_path__)

        self.book_dict = BaseObjectStore(os.path.join(self.__path__, 'books'), Book, new=True)
        self.reader_dict = BaseObjectStore(os.path.join(self.__path__, 'readers'), Reader, new=True)

        self.__db_writeback__ = writeback
        self.__books__, self.__events__, self.__readers__ = None, None, None
        self.__inducted_events__ = None
        self.__event_store_by_date__ = None
        self.__event_store_by_register_month__ = None

    def execute_events_induction(self, by_attr: str = 'date'):
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
    def event_store_by_date(self):
        if self.__event_store_by_date__ is None:
            self.__event_store_by_date__ = DateEventStore(folder_path=os.path.join(self.__path__, 'events_by_date'))

        return self.__event_store_by_date__

    @property
    def event_store_by_register_month(self):
        if self.__event_store_by_register_month__ is None:
            self.__event_store_by_register_month__ = RegisterMonthEventStore(
                folder_path=os.path.join(self.__path__, 'events_by_register_month'))

        return self.__event_store_by_register_month__

    @property
    def readers(self):
        if self.__readers__ is None:
            db_path = os.path.join(self.__path__, 'readers')
            try:
                self.__readers__ = ShelveWrapper(db_path, writeback=self.__db_writeback__).convert_to_data_dict(Reader)
                self.log.debug('DataDict converted from {}'.format(db_path))
            except FileNotFoundError:
                raise RuntimeError('No db {} exists, create new before using.'.format(db_path))
        assert isinstance(self.__readers__, DataDict)
        return self.__readers__

    @property
    def books(self):
        if self.__books__ is None:
            db_path = os.path.join(self.__path__, 'books')
            try:
                self.__books__ = ShelveWrapper(db_path, writeback=self.__db_writeback__).convert_to_data_dict(Book)
                self.log.debug('DataDict converted from {}'.format(db_path))
            except FileNotFoundError:
                raise RuntimeError('No db {} exists, create new before using.'.format(db_path))
        assert isinstance(self.__books__, DataDict)
        return self.__books__

    @property
    def events(self):
        if self.__events__ is None:
            db_path = os.path.join(self.__path__, 'events')
            try:
                self.__events__ = ShelveWrapper(db_path, writeback=self.__db_writeback__).convert_to_data_dict(Event)
                self.log.debug('DataDict converted from {}'.format(db_path))
            except FileNotFoundError:
                raise RuntimeError('No db {} exists, create new before using.'.format(db_path))
        assert isinstance(self.__events__, DataDict)
        return self.__events__

    @property
    def inducted_events(self):
        if self.__inducted_events__ is None:
            try:
                self.__inducted_events__ = ShelveWrapper(os.path.join(self.__path__, 'inducted_events'))
            except FileNotFoundError:
                pass

        if self.__inducted_events__ is None:
            raise RuntimeError('Events should be inducted before calling inducted events')

        assert isinstance(self.__inducted_events__, ShelveWrapper)
        return self.__inducted_events__

    def close(self):
        if isinstance(self.__books__, ShelveWrapper):
            self.__books__.close()

        if isinstance(self.__readers__, ShelveWrapper):
            self.__readers__.close()

        if isinstance(self.__events__, ShelveWrapper):
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
    from Environment import Environment
    from modules.DataLoad import RawDataProcessor
    env = Environment.get_instance()
    books, events, readers = dict(), dict(), dict()

    for d_object in tqdm(
            RawDataProcessor.iter_data_object(),
            desc='storing record data'
    ):
        value = Book.init_from(d_object)
        if value.index in books:
            stored = books[value.index]
            stored.update_from(value)
            books[value.index] = stored
        else:
            books[value.index] = value
        value = Reader.init_from(d_object)
        if value.index in readers:
            stored = readers[value.index]
            stored.update_from(value)
            readers[value.index] = stored
        else:
            readers[value.index] = value
        value = Event.init_from(d_object)
        if value.hashable_key in events:
            stored = events[value.hashable_key]
            stored.update_from(value)
            events[value.hashable_key] = stored
        else:
            events[value.hashable_key] = value

    book_store = ShelveWrapper(os.path.join(env.data_path, 'books'), new=True)
    for key, book in books.items():
        book_store[key] = book.get_state_str()
    book_store.close()

    reader_store = ShelveWrapper(os.path.join(env.data_path, 'readers'), new=True)
    for key, reader in readers.items():
        reader_store[key] = reader.get_state_str()
    reader_store.close()

    event_store = ShelveWrapper(os.path.join(env.data_path, 'events'), new=True)
    for key, event in events.items():
        event_store[key] = event.get_state_str()
    event_store.close()


def store_readers_and_books():
    from Environment import Environment
    env = Environment.get_instance()
    book_dict = BaseObjectStore(os.path.join(env.data_path, 'books'), Book, new=True)
    reader_dict = BaseObjectStore(os.path.join(env.data_path, 'readers'), Reader, new=True)
    book_dict.store(env.data_proxy.books)
    reader_dict.store(env.data_proxy.readers)


def store_events_by_date():
    from Environment import Environment
    env = Environment.get_instance()
    d_s = DateEventStore(folder_path=os.path.join(env.data_path, 'events_by_date'), new=True)
    d_s.store(env.data_proxy.events)


def store_events_by_register_month():
    from Environment import Environment
    env = Environment.get_instance()
    d_s = RegisterMonthEventStore(folder_path=os.path.join(env.data_path, 'events_by_register_month'), new=True)
    d_s.store(env.data_proxy.events)


if __name__ == '__main__':
    # ------------------------------
    from Environment import Environment
    env_instance = Environment()
    store_readers_and_books()
    # data_manager = DataManager(writeback=False)

    # data_proxy = DataProxy()
    # data_proxy.execute_events_induction('date')
    # data_proxy.close()

    store_events_by_date()
    # ------------------------------
