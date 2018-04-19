# -*- encoding: UTF-8 -*-
import datetime

from Interface import AbstractDataObject
from utils.String import attributes_repr


NOW_YEAR = datetime.datetime.now().date().year


def define_reader_table(meta):
    from sqlalchemy import MetaData, Table, Column, String
    assert isinstance(meta, MetaData)
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
        return datetime.datetime.strptime(self.op_dt, '%Y%m%d').date()

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
        return self

    def compare_by(self, **kwargs):
        for tag in kwargs:
            if tag not in self.__attributes__:
                raise AttributeError('Reader has no attribute {}'.format(tag))
            else:
                if kwargs[tag] != getattr(self, tag):
                    return False
        return True

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

    @property
    def register_year(self):
        if len(self.index) == 10:
            if self.index.startswith('5'):  # 本科生学号
                r_y = int(self.index[1:3]) + 2000
            elif self.index.startswith('0'):   # 博士生学号
                r_y = int(self.index[1:3]) + 2000
            elif self.index.startswith('1'):  # 研究生学号
                r_y = int(self.index[1:3]) + 2000
            elif self.index.startswith('7'):  # 医学院本科生学号
                r_y = int(self.index[1:3]) + 2000
            elif self.index.startswith('S'):
                r_y = int(self.index[1:3]) + 2000
            elif self.index.startswith('J'):
                r_y = int(self.index[2:4]) + 2000
            elif self.index.startswith('T'):  # 博士后
                r_y = int(self.index[2:4]) + 2000
            else:
                return None
            if r_y <= NOW_YEAR:
                return r_y
            else:
                return None
        else:
            return None
