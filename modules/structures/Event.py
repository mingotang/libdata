# -*- encoding: UTF-8 -*-
import datetime

from sqlalchemy import MetaData, Table, Column, String, Integer

from Interface import AbstractDataObject
from utils.UnicodeStr import attributes_repr


def define_event_table(meta: MetaData):
    return Table(
        'events', meta,
        Column('book_id', String, primary_key=True),
        Column('reader_id', String, primary_key=True),
        Column('event_date', String, primary_key=True),
        Column('event_type', String, primary_key=True),
        Column('times', Integer),
    )


class Event(AbstractDataObject):
    __attributes__ = ('book_id', 'reader_id', 'event_date', 'event_type')
    __repr__ = attributes_repr

    def __init__(self, book_id: str, reader_id: str, event_date: str, event_type: str):
        self.book_id = book_id
        self.reader_id = reader_id
        self.event_date = event_date
        self.event_type = event_type
        self.times = 1

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        else:
            if self.event_date == other.event_date:
                if self.book_id == other.book_id and self.reader_id == other.reader_id and \
                        self.event_type == other.event_type:
                    return True
                else:
                    return False
            else:
                return False

    @property
    def date(self):
        return datetime.datetime.strptime(self.event_date, '%Y%m%d').date()

    def update_from(self, value):
        if type(value) == type(self):
            if self == value:
                self.times += 1
            else:
                pass
        else:
            raise NotImplementedError
        return self

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
            return cls(
                book_id=value['sysID'],
                reader_id=value['userID'],
                event_date=value['event_date'],
                event_type=value['event_type'],
            )
        else:
            raise NotImplementedError

    @property
    def hashable_key(self):
        return '|'.join([self.book_id, self.reader_id, self.event_date, self.event_type])
