# -*- encoding: UTF-8 -*-
import datetime
import json

from Interface import AbstractDataObject
from structures.BookName import BookName
from structures.BookISBN import BookISBN
from structures.BookLibIndex import BookLibIndex


class Book(AbstractDataObject):
    __attributes__ = ('index', 'lib_index', 'name', 'isbn', 'author', 'year', 'publisher', 'op_dt')

    def __init__(self, index: str, lib_index: str, name: str, isbn: str,
                 author: str, year: str, publisher: str, op_dt=None):
        AbstractDataObject.__init__(self)
        self.index = index
        self.lib_index = lib_index
        self.name = name
        self.isbn = isbn
        self.author = author
        self.year = year
        self.publisher = publisher
        self.op_dt = op_dt

    @property
    def hashable_key(self):
        return self.index

    @property
    def publish_year(self):
        year = int(self.year)
        if 1800 <= year <= datetime.date.today().year:
            return year
        else:
            return None

    @property
    def book_name(self):
        return BookName(self.name)

    @property
    def update_date(self):
        return datetime.datetime.strptime(self.op_dt, '%Y%m%d').date()

    @property
    def book_isbn(self):
        return BookISBN(self.isbn)

    @property
    def book_lib_index(self):
        return BookLibIndex(self.lib_index)

    def update_from(self, value):
        if isinstance(value, type(self)):
            # if self.update_date >= value.update_date:
            #     return self
            # else:
            for tag in self.__attributes__:
                if tag in value.__dict__:
                    if value.__dict__[tag] is not None:
                        if len(self.__dict__[tag]) < len(value.__dict__[tag]):
                            self.__dict__[tag] = value.__dict__[tag]
            return self
        else:
            from extended.Exceptions import ParamTypeError
            raise ParamTypeError('value', '{}'.format(self.__class__.__name__), value)

    def compare_by(self, **kwargs):
        for tag in kwargs:
            if tag not in self.__attributes__:
                raise AttributeError('Book has no attribute {}'.format(tag))
            else:
                if kwargs[tag] != getattr(self, tag):
                    return False
        return True

    @classmethod
    def init_from(cls, value):
        if isinstance(value, dict):
            new = cls(
                index=value['sysID'],
                lib_index=value['libIndexID'],
                name=value['bookname'],
                isbn=value['isbn'],
                author=value['author'],
                year=value['publish_year'],
                publisher=value['publisher'],
                op_dt=value['event_date'],
            )
        else:
            from extended.Exceptions import ParamTypeError
            raise ParamTypeError('value', 'dict', value)
        return new

    @staticmethod
    def define_table(meta):
        from sqlalchemy import MetaData, Table, Column, String
        assert isinstance(meta, MetaData)
        return Table(
            'books', meta,
            Column('index', String, nullable=False, primary_key=True),
            Column('lib_index', String),
            Column('name', String),
            Column('isbn', String),
            Column('author', String),
            Column('year', String),
            Column('publisher', String),
            Column('op_dt', String)
        )


if __name__ == '__main__':
    from Environment import Environment
    from structures import Book

    env_inst = Environment()

    try:
        for book in env_inst.data_proxy.books.values():
            assert isinstance(book, Book)
            if book.publish_year is None:
                print(book.lib_index, book)
    except KeyboardInterrupt:
        env_inst.exit()
    finally:
        env_inst.exit()
