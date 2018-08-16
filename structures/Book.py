# -*- encoding: UTF-8 -*-
import datetime

from Interface import AbstractDataObject
from structures import BookName, ISBN, LibIndex
from utils import attributes_repr


def define_book_table(meta):
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
    def book_name(self):
        return BookName(self.name)
        # return re.sub(r'\W', ' ', self.name).strip()

    @property
    def update_date(self):
        return datetime.datetime.strptime(self.op_dt, '%Y%m%d').date()

    @property
    def book_isbn(self):
        return ISBN(self.isbn)

    @property
    def book_lib_index(self):
        return LibIndex(self.lib_index)

    def update_from(self, value):
        if isinstance(value, type(self)):
            if self.update_date >= value.update_date:
                return None
            else:
                for tag in self.__attributes__:
                    if tag in value.__dict__:
                        if value.__dict__[tag] is not None:
                            if len(self.__dict__[tag]) < len(value.__dict__[tag]):
                                self.__dict__[tag] = value.__dict__[tag]
                return self
        else:
            from utils.Exceptions import ParamTypeError
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
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('value', 'dict/DataObject', value)


def collect_book_attributes(events, **kwargs):
    import os
    from collections import defaultdict
    from Config import DataConfig
    from structures import ShelveWrapper
    from structures import SparseVector

    book_attributes = defaultdict(SparseVector)

    # TODO: finish collecting book attributes

    auto_save = kwargs.get('auto_save', False)
    if auto_save is True:
        ShelveWrapper.init_from(
            book_attributes,
            db_path=os.path.join(DataConfig.operation_path, 'book_attributes')
        ).close()

    return book_attributes


if __name__ == '__main__':
    pass
