# -*- encoding: UTF-8 -*-
import logging
import shelve

from collections import Iterable, Mapping

from Config import DataBaseConfig
from structures.Book import Book
from structures.Event import Event
from structures.Reader import Reader


class SqliteWrapper(object):
    def __init__(self, db_path=DataBaseConfig.file_path,
                 clear_db=False, exist_optimize=True, action_limit=True):
        from sqlalchemy import create_engine, MetaData
        from sqlalchemy.orm import sessionmaker
        self.engine = create_engine('sqlite:///{host}'.format(host=db_path), echo=False)
        self.metadata = MetaData(bind=self.engine)
        self.__table_definition__()
        if clear_db is True:
            self.clear_db()
        self.metadata.create_all(bind=self.engine, checkfirst=True)
        self.__table_mapping__()
        session = sessionmaker(bind=self.engine)
        self.session = session()
        self.__book_dict__ = None
        self.__reader_dict__ = None
        self.__event_dict__ = None
        self.__action_range__ = None
        self.__optimize_check__ = exist_optimize
        self.__action_limit__ = action_limit
        self.optimize()
        # from sqlalchemy.orm import create_session
        # self.session = create_session(bind=self.engine)
        if self.__action_limit__ is True:
            self.__init_action_limit__()

    def __table_definition__(self):
        from structures.Book import define_book_table
        from structures.Event import define_event_table
        from structures.Reader import define_reader_table
        self.user_table = define_reader_table(self.metadata)
        self.book_table = define_book_table(self.metadata)
        self.events_table = define_event_table(self.metadata)

    def __table_mapping__(self):
        from sqlalchemy.orm import mapper
        mapper(Reader, self.user_table)
        mapper(Book, self.book_table)
        mapper(Event, self.events_table)

    def optimize(self):
        if self.__optimize_check__ is True:
            self.__optimize_book_check__()
            self.__optimize_reader_check__()
            self.__optimize_event_check__()

    def __optimize_book_check__(self):
        tmp = self.session.query(Book).all()  # TODO: 数据量比较大的时候需要只 select index
        self.__book_dict__ = {var.index: None for var in tmp}

    def __optimize_reader_check__(self):
        tmp = self.session.query(Reader).all()
        self.__reader_dict__ = {var.index: None for var in tmp}

    def __optimize_event_check__(self):
        tmp = self.session.query(Event).all()
        self.__event_dict__ = dict()
        for event in tmp:
            key = event.hashable_key
            if key not in self.__event_dict__:
                self.__event_dict__[key] = None

    def __init_action_limit__(self):
        tmp = [event.date for event in self.session.query(Event).all()]
        self.__action_range__ = (min(tmp), max(tmp))

    def add_all(self, obj):
        if len(obj) > 0:
            self.session.add_all(obj)
            self.session.commit()
            self.optimize()

    def add(self, obj):
        self.session.add(obj)
        self.session.commit()
        if self.__optimize_check__ is True:
            if isinstance(obj, Book):   # updating exsiting_optimation
                self.__book_dict__[obj.index] = None
            elif isinstance(obj, Reader):
                self.__reader_dict__[obj.index] = None
            elif isinstance(obj, Event):
                self.__event_dict__[obj.hashable_key] = None
            else:
                raise TypeError

    def drop_tables(self, table):
        from sqlalchemy import Table
        assert isinstance(table, Table), str(TypeError('table should be of type sqlalchemy.Table'))
        self.metadata.remove(table)

    def clear_db(self):
        self.metadata.drop_all()

    def get_all(self, obj_type: type, **filter_by):
        """get_all all {obj_type} filter by {kwargs} -> list"""
        return self.session.query(obj_type).filter_by(**filter_by).all()

    def get_one(self, obj_type: type, **filter_by):
        return self.session.query(obj_type).filter_by(**filter_by).one()

    def exists_book(self, value: Book):
        from sqlalchemy.orm.exc import NoResultFound
        try:
            return value.index in self.__book_dict__
        except TypeError:
            try:
                self.session.query(Book).filter_by(index=value.index).one()
                return True
            except NoResultFound:
                return False

    def exists_reader(self, value: Reader):
        from sqlalchemy.orm.exc import NoResultFound
        try:
            return value.index in self.__reader_dict__
        except TypeError:
            try:
                self.session.query(Reader).filter_by(index=value.index).one()
                return True
            except NoResultFound:
                return False

    def exists_event(self, event: Event):
        from sqlalchemy.orm.exc import NoResultFound
        try:
            return event.hashable_key in self.__event_dict__
        except TypeError:
            try:
                self.session.query(Event).filter_by(
                    book_id=event.book_id, reader_id=event.reader_id,
                    event_date=event.event_date, event_type=event.event_type
                ).one()
                return True
            except NoResultFound:
                return False

    def exists(self, obj):
        """wrapper.exists(obj) -> bool -- check whether obj exits in database"""
        if isinstance(obj, (list, tuple, set)):
            check_list = list()
            for i in range(len(obj)):
                check_list.append(self.exists(obj[i]))
            return check_list
        elif isinstance(obj, Book):
            return self.exists_book(obj)
        elif isinstance(obj, Reader):
            return self.exists_reader(obj)
        elif isinstance(obj, Event):
            return self.exists_event(obj)
        else:
            raise TypeError

    def merge(self, inst, load=True):
        if isinstance(inst, (Book, Reader)):
            self.session.merge(inst, load=load)
        elif isinstance(inst, Event):
            if self.__action_limit__ is True:
                if self.__action_range__[0] <= inst.date <= self.__action_range__[1]:
                    raise PermissionError('Event {} can be changed since created.'.format(inst.__repr__()))
                else:
                    self.session.merge(inst, load=load)
            else:
                self.session.merge(inst, load=load)
        else:
            raise TypeError


class ShelveWrapper(Mapping):

    def __init__(self, db_path: str, writeback=False):
        Mapping.__init__(self)
        if '.' in db_path:
            if db_path.split('.')[-1] == 'db':
                path = db_path
            else:
                path = '.'.join([db_path, 'db'])
        else:
            path = '.'.join([db_path, 'db'])

        self.__path__ = path
        self.__db__ = shelve.open(self.__path__, writeback=writeback, protocol=None)
        logging.debug('Connected to shelve database {}'.format(path))

    def __iter__(self):
        for key in self.keys():
            yield key

    def __getitem__(self, key: str):
        return self.__db__[key]

    def __setitem__(self, key: str, value):
        self.__db__[key] = value

    def __contains__(self, key: str):
        return self.__db__.__contains__(key)

    def __delitem__(self, key):
        del self.__db__[key]

    def __len__(self):
        self.__db__.__len__()

    def __del__(self):
        logging.debug('shelve database {} closed.'.format(self.__path__))
        self.close()
        del self.__db__
        del self.__path__

    def keys(self):
        return self.__db__.keys()

    def values(self):
        return self.__db__.values()

    def items(self):
        return self.__db__.items()

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def flush(self):
        self.__db__.sync()

    def clear(self):
        self.__db__.clear()

    def close(self):
        self.__db__.close()


if __name__ == '__main__':
    shelve_db = ShelveWrapper('/Users/mingo/Downloads/persisted_libdata/test.db')
