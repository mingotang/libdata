# -*- encoding: UTF-8 -*-
import datetime

from sqlalchemy import MetaData, Table, Column, String

from Interface import AbstractDataObject
from utils.String import attributes_repr


def define_book_table(meta: MetaData):
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


class Book(AbstractDataObject):
    __attributes__ = ('index', 'lib_index', 'name', 'isbn', 'author', 'year', 'publisher')
    __repr__ = attributes_repr

    def __init__(self, index: str, lib_index: str, name: str,
                 isbn: str, author: str, year: str, publisher: str,
                 op_dt=None):
        self.index = index
        self.lib_index = lib_index
        self.name = name
        self.isbn = isbn
        self.author = author
        self.year = year
        self.publisher = publisher
        self.op_dt = op_dt

    @property
    def update_date(self):
        return datetime.datetime.strptime(self.op_dt, '%Y%m%d')

    def update_from(self, value):
        if type(value) == type(self):
            if self.update_date >= value.update_date:
                return
        else:
            raise NotImplementedError

        for tag in self.__attributes__:
            if tag in value.__dict__:
                if value.__dict__[tag] is not None:
                    if len(self.__dict__[tag]) < len(value.__dict__[tag]):
                        self.__dict__[tag] = value.__dict__[tag]

    @classmethod
    def init_from(cls, value):
        if isinstance(value, dict):
            return cls(
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
            raise NotImplementedError


if __name__ == '__main__':
    pass
