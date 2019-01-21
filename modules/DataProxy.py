# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os

from collections.abc import Mapping, Iterable
from extended import DataDict, ShelveWrapper, SqliteWrapper

from structures import Book, BookMap, Event, Reader, RecommendListObject, SumBook


class SqliteDict(Mapping, Iterable):

    def __init__(self, db: SqliteWrapper, obj_type: type, obj_index_attr: str):
        self.db = db
        assert hasattr(obj_type, 'define_table')
        self.__obj_type__ = obj_type
        self.__obj_index_attr__ = obj_index_attr

    def __iter__(self):
        return self.keys()

    def __setitem__(self, key: str, value):
        assert hasattr(value, self.__obj_index_attr__) and isinstance(value, self.__obj_type__)
        self.db.add(value)

    def __getitem__(self, key: str):
        return self.db.session.query(self.__obj_type__).filter_by(**{self.__obj_index_attr__: key}).one()

    @property
    def query(self):
        return self.db.session.query

    def keys(self):
        for obj in self.values():
            yield getattr(obj, self.__obj_index_attr__)

    def values(self):
        for obj in self.db.session.query(self.__obj_type__).all():
            yield obj

    def items(self):
        for obj in self.values():
            yield getattr(obj, self.__obj_index_attr__), obj

    def __len__(self):
        return len(self.db.session.query(self.__obj_type__).all())

    def to_data_dict(self):
        new_d = DataDict()
        for k, v in self.items():
            new_d[k] = v
        return new_d


class DataProxy(object):
    __db__ = None

    def __init__(self, data_path: str,):
        from utils import get_logger
        self.log = get_logger(self.__class__.__name__)

        self.__path__ = data_path
        if not os.path.exists(self.__path__):
            os.makedirs(self.__path__)

        self.__operation_path__ = os.path.join(self.__path__, 'this_operation')
        if not os.path.exists(self.__operation_path__):
            os.makedirs(self.__operation_path__)

        if DataProxy.__db__ is None:
            DataProxy.__db__ = SqliteWrapper(db_path=os.path.join(self.__path__, 'libdata.db'))
            DataProxy.__db__.map(Book, Book.define_table(self.__db__.metadata))
            DataProxy.__db__.map(BookMap, BookMap.define_table(self.__db__.metadata))
            DataProxy.__db__.map(Event, Event.define_table(self.__db__.metadata))
            DataProxy.__db__.map(Reader, Reader.define_table(self.__db__.metadata))
            DataProxy.__db__.map(RecommendListObject, RecommendListObject.define_table(self.__db__.metadata))
            DataProxy.__db__.map(SumBook, SumBook.define_table(self.__db__.metadata))
            self.sqlite.metadata.create_all(checkfirst=True)

        self.book_dict = SqliteDict(self.__db__, Book, 'index')
        self.reader_dict = SqliteDict(self.__db__, Reader, 'index')
        self.event_dict = SqliteDict(self.__db__, Event, 'hashable_key')

        self.__books__, self.__events__, self.__readers__ = None, None, None
        self.__inducted_events__ = None

    @property
    def readers(self):
        if self.__readers__ is None:
            self.__readers__ = self.reader_dict.to_data_dict()
        assert isinstance(self.__readers__, DataDict)
        return self.__readers__

    @property
    def books(self):
        if self.__books__ is None:
            self.__books__ = self.book_dict.to_data_dict()
        assert isinstance(self.__books__, DataDict)
        return self.__books__

    @property
    def events(self):
        if self.__events__ is None:
                self.__events__ = self.event_dict.to_data_dict()
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

    @property
    def sqlite(self):
        assert isinstance(self.__db__, SqliteWrapper)
        return self.__db__

    def close(self):
        if isinstance(self.__books__, ShelveWrapper):
            self.__books__.close()

        if isinstance(self.__readers__, ShelveWrapper):
            self.__readers__.close()

        if isinstance(self.__events__, ShelveWrapper):
            self.__events__.close()

        if isinstance(self.__inducted_events__, ShelveWrapper):
            self.__inducted_events__.close()


def store_record_data():
    """把txt文件的数据记录到 shelve 数据库中"""
    from tqdm import tqdm
    from Environment import Environment
    from modules.DataLoad import RawDataProcessor
    env = Environment.get_instance()
    books, events, readers = dict(), dict(), dict()

    db = SqliteWrapper.get_instance(os.path.join(env.data_path, 'libdata.db'))
    book_table, reader_table = Book.define_table(db.metadata), Reader.define_table(db.metadata)
    event_table = Event.define_table(db.metadata)
    db.metadata.drop_all()
    db.metadata.create_all(checkfirst=True)
    db.map(Book, book_table)
    db.map(Event, event_table)
    db.map(Reader, reader_table)

    for d_object in tqdm(
            RawDataProcessor.iter_data_object(),
            desc='storing record data'
    ):
        value = Book.init_from(d_object)
        if len(value.index) == 0:
            pass
        elif value.index in books:
            stored = books[value.index]
            stored.update_from(value)
            books[value.index] = stored
        else:
            books[value.index] = value
        value = Reader.init_from(d_object)
        if len(value.index) == 0:
            pass
        elif value.index in readers:
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

    db.add_all(books.values())
    db.add_all(readers.values())
    db.add_all(events.values())

    book_store = dict()
    for key, book in books.items():
        book_store[key] = book.get_state()
    ShelveWrapper.init_from(book_store, os.path.join(env.data_path, 'books')).close()

    reader_store = dict()
    for key, reader in readers.items():
        reader_store[key] = reader.get_state()
    ShelveWrapper.init_from(reader_store, os.path.join(env.data_path, 'readers')).close()

    event_store = dict()
    for key, event in events.items():
        event_store[key] = event.get_state()
    ShelveWrapper.init_from(event_store, os.path.join(env.data_path, 'events')).close()

    db.close()


def store_sum_book():
    from Environment import Environment



if __name__ == '__main__':
    # ------------------------------
    from Environment import Environment
    env_instance = Environment()
    store_record_data()
    env_instance.exit()
    # store_readers_and_books()
    # data_manager = DataManager(writeback=False)

    # data_proxy = DataProxy()
    # data_proxy.execute_events_induction('date')
    # data_proxy.close()

    # store_events_by_date()
    # ------------------------------
