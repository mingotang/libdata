# -*- encoding: UTF-8 -*-
import datetime

from sqlalchemy import MetaData, Table, Column, String, Integer

from Interface import AbstractDataObject
from structures import OrderedList
from utils import attributes_repr


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
        return datetime.datetime.strptime(self.event_date, '%Y%m%d').date()

    def update_from(self, value):
        if isinstance(value, type(self)):
            if self == value:
                self.times += 1
            else:
                pass
            return self
        else:
            from utils.Exceptions import ParamTypeError
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
            return cls(
                book_id=value['sysID'],
                reader_id=value['userID'],
                event_date=value['event_date'],
                event_type=value['event_type'],
            )
        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('value', 'dict/DataObject', value)

    @property
    def hashable_key(self):
        return '|'.join([self.book_id, self.reader_id, self.event_date, self.event_type])


class InductedEvents(object):
    def __init__(self, db_path: str):
        from utils import ShelveWrapper
        self.__db__ = ShelveWrapper(db_path=db_path, writeback=False)

    def keys(self):
        return self.__db__.keys()

    def value(self):
        for d_v in self.__db__.values():
            assert isinstance(d_v, OrderedList)
            yield d_v

    def items(self):
        for d_k, d_v in self.__db__.items():
            assert isinstance(d_v, OrderedList)
            yield d_k, d_v

    def __getitem__(self, reader_id: str):
        ordered_list = self.__db__[reader_id]
        assert isinstance(ordered_list, OrderedList)
        return ordered_list

    def get(self, reader_id: str, default=OrderedList(Event, 'date')):
        try:
            return self.__getitem__(reader_id)
        except KeyError:
            return default

    def do_induct(self, events_bag):
        """把数据集中的行为数据按照某种顺序排列归类"""
        from collections import Mapping, Iterable
        from tqdm import tqdm
        from structures import OrderedList

        result = dict()

        if isinstance(events_bag, Mapping):
            for event in tqdm(events_bag.values(), desc='inducting events'):
                assert isinstance(event, Event)
                if event.reader_id not in result:
                    result[event.reader_id] = OrderedList(Event, 'date')
                result[event.reader_id].append(event)
        elif isinstance(events_bag, Iterable):
            for event in tqdm(events_bag, desc='inducting events'):
                assert isinstance(event, Event)
                if event.reader_id not in result:
                    result[event.reader_id] = OrderedList(Event, 'date')
                result[event.reader_id].append(event)
        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('events_bag', 'Iterable/Mapping', events_bag)

        self.__db__.clear()
        self.__db__.update(result)
