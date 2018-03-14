# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
from structures.Base import BaseObject


class Reader(BaseObject):
    __attributes__ = ('index', 'rtype', 'college')

    def __init__(self, index: str, rtype: str, college: str):
        self.index = index
        self.rtype = rtype
        self.college = college

    def update(self, other):
        if len(other.college) == 5 and len(self.college) < 5:
            self.college = other.college
        if len(other.rtype) == 2 and len(self.rtype) < 2:
            self.rtype = other.rtype
