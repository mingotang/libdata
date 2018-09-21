# -*- encoding: UTF-8 -*-
import datetime


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
            from utils.Exceptions import ParamTypeError
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
        from utils.Exceptions import ParamTypeError
        if len(stage_list) == 0:
            from utils.Exceptions import ParamNoContentError
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
