# -*- encoding: UTF-8 -*-
import datetime

from Interface import AbstractDataObject, AbstractEnvObject
from utils import attributes_repr


class Event(AbstractDataObject, AbstractEnvObject):
    __attributes__ = ('book_id', 'reader_id', 'event_date', 'event_type', 'times')
    __repr__ = attributes_repr

    def __init__(self, book_id: str, reader_id: str, event_date: str, event_type: str, **kwargs):
        AbstractDataObject.__init__(self)
        self.book_id = book_id
        self.reader_id = reader_id
        self.event_date = event_date
        self.event_type = event_type
        self.times = int(kwargs.get('times', 1))

    def __eq__(self, other):
        if type(self) == type(other):
            if self.event_date == other.event_date:
                if self.book_id == other.book_id and self.reader_id == other.reader_id and \
                        self.event_type == other.event_type:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    @property
    def date(self):
        """事件日期"""
        return datetime.datetime.strptime(self.event_date, '%Y%m%d').date()

    @property
    def month_from_reader_register(self):
        """从注册时间开始到借阅事件为止的月数"""
        reader = self.correspond_reader
        if reader.register_date is None:
            return None
        else:
            if reader.register_date >= self.date:
                return 0
            else:
                return int(((self.date - reader.register_date) / datetime.timedelta(days=1)) / 30)

    def update_from(self, value):
        if isinstance(value, type(self)):
            if self == value:
                self.times += 1
            else:
                pass
            return self
        else:
            from extended.Exceptions import ParamTypeError
            raise ParamTypeError('value', '{}'.format(self.__class__.__name__), value)

    def compare_by(self, **kwargs):
        for tag in kwargs:
            if tag not in self.__attributes__:
                raise AttributeError('Event has no attribute {}'.format(tag))
            else:
                if kwargs[tag] != getattr(self, tag):
                    return False
        return True

    @classmethod
    def init_from(cls, value):
        if isinstance(value, dict):
            new = cls(
                book_id=value['sysID'],
                reader_id=value['userID'],
                event_date=value['event_date'],
                event_type=value['event_type'],
            )
        else:
            from extended.Exceptions import ParamTypeError
            raise ParamTypeError('value', 'dict/DataObject', value)
        return new

    @property
    def hashable_key(self):
        return '|'.join([self.book_id, self.reader_id, self.event_date, self.event_type])

    @property
    def correspond_reader(self):
        from structures.Reader import Reader
        reader = self.env.data_proxy.readers[self.reader_id]
        assert isinstance(reader, Reader), str(self)
        return reader

    @property
    def correspond_book(self):
        from structures.Book import Book
        book = self.env.data_proxy.books[self.book_id]
        assert isinstance(book, Book), str(self)
        return book

    @property
    def book_index_class(self):
        """书目索引号类别"""
        return self.correspond_book.book_lib_index.index_class

    @staticmethod
    def define_table(meta):
        from sqlalchemy import MetaData, Table, Column, String, Integer
        assert isinstance(meta, MetaData)
        return Table(
            'events', meta,
            Column('book_id', String, primary_key=True),
            Column('reader_id', String, primary_key=True),
            Column('event_date', String, primary_key=True),
            Column('event_type', String, primary_key=True),
            Column('times', Integer),
        )
