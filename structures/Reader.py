# -*- encoding: UTF-8 -*-
import datetime

from sqlalchemy import MetaData, Table, Column, String

from Interface import AbstractDataObject
from utils.String import attributes_repr


def define_reader_table(meta: MetaData):
    return Table(
        'users', meta,
        Column('index', String, nullable=False, primary_key=True),
        Column('rtype', String, nullable=False),
        Column('college', String),
        Column('op_dt', String),
    )


class Reader(AbstractDataObject):
    __attributes__ = ('index', 'rtype', 'college')
    __repr__ = attributes_repr

    def __init__(self, index: str, rtype: str, college: str, op_dt=None):
        self.index = index
        self.rtype = rtype
        self.college = college
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
                index=value['userID'],
                rtype=value['user_type'],
                college=value['collegeID'],
                op_dt=value['event_date'],
            )
        else:
            raise NotImplementedError
