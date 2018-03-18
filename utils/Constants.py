# -*- encoding: UTF-8 -*-
from enum import Enum


class BaseEnum(Enum):
    def __repr__(self):
        return '{}.{}: {}'.format(self.__class__.__name__, self.name, self.value)

    @classmethod
    def to_str(cls):
        string = cls.__name__ + ': '
        string += ', '.join([var + ': ' + cls.__members__[var].value for var in cls.__members__])
        return string



