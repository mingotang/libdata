# -*- encoding: UTF-8 -*-
import datetime
import json

from Interface import AbstractDataObject
from utils import attributes_repr


class Event(AbstractDataObject):
    __attributes__ = ('book_id', 'reader_id', 'event_date', 'event_type')
    __information__ = ('times', )
    __repr__ = attributes_repr

    def __init__(self, book_id: str, reader_id: str, event_date: str, event_type: str, **kwargs):
        self.book_id = book_id
        self.reader_id = reader_id
        self.event_date = event_date
        self.event_type = event_type
        self.times = kwargs.get('times', 1)

    @classmethod
    def set_state_str(cls, state: str):
        return cls.set_state_dict(json.loads(state))

    def get_state_str(self):
        return json.dumps(self.get_state_dict())

    @classmethod
    def set_state_dict(cls, state: dict):
        return cls(**state)

    def get_state_dict(self):
        state = dict()
        for tag in self.__attributes__:
            state[tag] = getattr(self, tag)
        for tag in self.__information__:
            state[tag] = getattr(self, tag)
        return state

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
            new = cls(
                book_id=value['sysID'],
                reader_id=value['userID'],
                event_date=value['event_date'],
                event_type=value['event_type'],
            )
        elif isinstance(value, dict):
            new = cls.set_state_dict(value)
        elif isinstance(value, str):
            new = cls.set_state_str(value)
        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('value', 'dict/DataObject', value)
        return new

    @property
    def hashable_key(self):
        return '|'.join([self.book_id, self.reader_id, self.event_date, self.event_type])
