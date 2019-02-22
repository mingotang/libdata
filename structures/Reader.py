# -*- encoding: UTF-8 -*-
import datetime

from Interface import AbstractDataObject
from utils import attributes_repr
from utils.Constants import (
    GRADUATE_TYPES, UNDER_GRADUATE_TYPES, STUDENT_TYPES,
    STAFF_TYPES, OTHER_INDIVIDUAL_TYPES, NONE_INDIVIDUAL_TYPES,
    # MICHIGAN_TYPES,
)


TODAY = datetime.datetime.now().date()


class Reader(AbstractDataObject):
    __attributes__ = ('index', 'rtype', 'college', 'op_dt')
    __repr__ = attributes_repr

    def __init__(self, index: str, rtype: str, college: str, op_dt=None):
        AbstractDataObject.__init__(self)
        self.index = index
        self.rtype = rtype
        self.college = college
        self.op_dt = op_dt

    @property
    def hashable_key(self):
        return self.index

    @property
    def update_date(self):
        """check the update date of reader info which is derived from events list"""
        return datetime.datetime.strptime(self.op_dt, '%Y%m%d').date()

    def update_from(self, value):
        if isinstance(value, type(self)):
            # if self.update_date >= value.update_date:
            #     return None
            # else:
            for tag in self.__attributes__:
                if tag in value.__dict__:
                    if value.__dict__[tag] is not None:
                        if len(self.__dict__[tag]) < len(value.__dict__[tag]):
                            self.__dict__[tag] = value.__dict__[tag]
            return self
        else:
            from extended.Exceptions import ParamTypeError
            raise ParamTypeError('value', '{}'.format(self.__class__.__name__), value)

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
            new = cls(
                index=value['userID'],
                rtype=value['user_type'],
                college=value['collegeID'],
                op_dt=value['event_date'],
            )
        else:
            from extended.Exceptions import ParamTypeError
            raise ParamTypeError('value', 'dict/DataObject', value)
        return new

    @property
    def register_year(self):
        if len(self.index) == 10:
            if self.is_outer_reader:
                return None
            elif self.is_student:
                if self.index[0] in ('0', '1', '3', '4', '5', '7', 'S'):
                    r_y = int(self.index[1:3]) + 2000
                elif self.index[0] in ('J', 'T', ):
                    r_y = int(self.index[2:4]) + 2000
                elif self.index[0] in ('X', ):
                    r_y = int(self.index[1:5])
                elif self.index.startswith('HY'):
                    r_y = int(self.index[2:4]) + 2000
                else:
                    return None  # Exception: Reader(index: 3205821979, rtype: 21, college: )
            elif self.is_college_staff or not self.is_individual_reader:
                return None
            else:
                return None

            if r_y <= TODAY.year:
                return r_y
            else:
                # Exception :   Reader(index: 3965589366, rtype: 35, college: )
                #               Reader(index: 3205821979, rtype: 21, college: )
                return None
        else:
            return None

    @property
    def register_date(self):
        if self.register_year is None:
            return None
        else:
            return datetime.date(self.register_year, 9, 1)

    def growth_index(self, ref_date: datetime.date):
        """calculate the growth index of a student, return None if not known"""
        if self.register_year is None:
            return None

        begin_date = datetime.date(self.register_year, 9, 1)
        if begin_date >= ref_date:
            return None
        else:
            return (ref_date - begin_date) / datetime.timedelta(days=365)

    @property
    def is_student(self):
        return self.rtype in STUDENT_TYPES

    @property
    def is_graduate_student(self):
        return self.rtype in GRADUATE_TYPES

    @property
    def is_undergraduate_student(self):
        return self.rtype in UNDER_GRADUATE_TYPES

    @property
    def is_college_staff(self):
        return self.rtype in STAFF_TYPES

    @property
    def is_individual_reader(self):
        return self.rtype not in NONE_INDIVIDUAL_TYPES

    @property
    def is_outer_reader(self):
        return self.rtype in OTHER_INDIVIDUAL_TYPES

    @staticmethod
    def define_table(meta):
        from sqlalchemy import MetaData, Table, Column, String
        assert isinstance(meta, MetaData)
        return Table(
            'users', meta,
            Column('index', String, nullable=False, primary_key=True),
            Column('rtype', String, nullable=False),
            Column('college', String),
            Column('op_dt', String),
        )


if __name__ == '__main__':
    from Environment import Environment
    env = Environment()

    for reader in env.data_proxy.readers.values():
        if not isinstance(reader.register_year, int):
            # continue
            if reader.is_outer_reader:
                print(reader.register_year, reader)
        else:
            continue
