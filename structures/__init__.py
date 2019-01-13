# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import datetime

from collections import namedtuple

from .Book import Book
from .BookName import BookName
from .DataObject import OrderedList
from .Evaluator import Evaluator
from .Event import Event
from .BookISBN import BookISBN
from .Reader import Reader
from .SparseVector import SparseVector


LibIndexClassObject = namedtuple('LibIndexClassObject', [
    'main_class', 'sub_class', 'base_class', 'name',
])


class RecommendListObject(object):
    def __init__(self, list_name: str, book_index: str, rank: int = -1):
        self.list_name, self.book_index, self.rank = list_name, book_index, rank

    @staticmethod
    def define_table(meta):
        from sqlalchemy import MetaData, Table, Column, String, Integer
        assert isinstance(meta, MetaData)
        return Table(
            'recommend_list', meta,
            Column('list_name', String, nullable=False, primary_key=True),
            Column('book_index', String, nullable=False, primary_key=True),
            Column('rank', Integer),
        )


class RecoResult(dict):
    def __init__(self):
        dict.__init__(self)

    def add(self, *args, **kwargs):
        self.add_list(*args, **kwargs)

    def add_list(self, key: str, value: list):
        if self.__contains__(key):
            raise KeyError
        else:
            self.__setitem__(key, value)

    def derive_top(self, n: int = 1):
        if n < 1:
            from extended.Exceptions import ParamOutOfRangeError
            raise ParamOutOfRangeError('n', (1, 'inf'), n)
        assert n >= 1

        result = RecoResult()
        for key, value in self.items():
            if len(value) >= n:
                result.add_list(key, value[:n])
            else:
                result.add_list(key, value)

        return result

    def to_csv(self, folder_path: str = None):
        import os
        import datetime
        from Environment import Environment
        env = Environment.get_instance()
        file_name = 'cf_result_{}.csv'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        if folder_path is None:
            target_path = os.path.join(os.path.join(env.data_path, 'this_operation'), file_name)
        else:
            if os.path.exists(folder_path) is False:
                os.makedirs(folder_path)
            target_path = os.path.join(folder_path, file_name)
        with open(target_path, 'w', encoding='utf-8') as file:
            for key, value in self.items():
                file.write(key)
                file.write(',')
                file.write(','.join(value))
                file.write('\n')
        file.close()

    @classmethod
    def load_csv(cls, csv_path: str, encoding: str = 'utf-8'):
        import os
        if not os.path.exists(csv_path):
            raise FileNotFoundError(csv_path)
        result = cls()
        file = open(csv_path, 'r', encoding=encoding)
        content = file.readlines()
        # assert isinstance(content, str)
        # content = content.split('\n')
        for line in content:
            line = line.split(',')
            if len(line) > 1:
                result[line[0]] = line[1:]
            else:
                result[line[0]] = list()
        return result


class TimeRange(object):

    def __init__(self, start_time, end_time):
        self.__start_time__ = self.__clean_date__(start_time)
        self.__end_time__ = self.__clean_date__(end_time)

    @staticmethod
    def __clean_date__(date):
        if isinstance(date, datetime.datetime):
            return date
        elif isinstance(date, datetime.date):
            return datetime.datetime.combine(date, datetime.time())
        else:
            from extended.Exceptions import ParamTypeError
            raise ParamTypeError('date', (datetime.datetime, datetime.date), date)

    @property
    def start_time(self):
        assert isinstance(self.__start_time__, datetime.datetime)
        return self.__start_time__

    @property
    def end_time(self):
        assert isinstance(self.__end_time__, datetime.datetime)
        return self.__end_time__


class StandardTimeRange(TimeRange):
    def __init__(self, start_time, end_time):
        super(StandardTimeRange, self).__init__(start_time, end_time)


class GrowthTimeRange(TimeRange):
    def __init__(self, start_time, end_time):
        super(GrowthTimeRange, self).__init__(start_time, end_time)
        self.__growth_stage_list__ = None
        self.__growth_stage_tag__ = None

    def set_growth_stage(self, stage_tag: str, stage_list: list):
        from extended.Exceptions import ParamTypeError
        if len(stage_list) == 0:
            from extended.Exceptions import ParamNoContentError
            raise ParamNoContentError('stage')

        if isinstance(stage_list[0], int):
            for item in stage_list:
                if not isinstance(item, int):
                    raise ParamTypeError('item in stage', (int, float), item)
        elif isinstance(stage_list[0], tuple):
            for item in stage_list:
                if not isinstance(item, tuple) or len(item) != 2:
                    raise ParamTypeError('item in stage', tuple, item)
        else:
            raise ParamTypeError('item in stage', (int, tuple), stage_list[0])

        self.__growth_stage_list__ = stage_list
        self.__growth_stage_tag__ = stage_tag

    @property
    def growth_stage(self):
        if self.__growth_stage_list__ is None or self.__growth_stage_tag__ is None:
            raise RuntimeError('growth stage should be set by set_growth_stage() before use.')
        else:
            return self.__growth_stage_tag__, self.__growth_stage_list__


class DateBackTimeRange(TimeRange):
    def __init__(self, start_time, end_time, date_back_split_time):
        super(DateBackTimeRange, self).__init__(start_time, end_time)
        self.__date_back_time__ = self.__clean_date__(date_back_split_time)

    @property
    def start_second_time(self):
        assert isinstance(self.__date_back_time__, datetime.datetime)
        return self.__date_back_time__

    @property
    def end_first_time(self):
        assert isinstance(self.__date_back_time__, datetime.datetime)
        return self.__date_back_time__
