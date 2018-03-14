# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
from enum import Enum


class BaseEnum(Enum):
    def __repr__(self):
        return "{0:s}.{1:s}".format(
            self.__class__.__name__, self._name_
        )
