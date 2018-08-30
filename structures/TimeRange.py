# -*- encoding: UTF-8 -*-
import datetime


class TimeRange(object):

    def __init__(self, start_time, end_time):
        if isinstance(start_time, datetime.datetime):
            self.__start_time__ = start_time
        elif isinstance(start_time, datetime.date):
            self.__start_time__ = datetime.datetime.combine(start_time, datetime.time())
        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('start_time', (datetime.datetime, datetime.date), start_time)

        if isinstance(end_time, datetime.datetime):
            self.__end_time__ = end_time
        elif isinstance(end_time, datetime.date):
            self.__end_time__ = datetime.datetime.combine(end_time, datetime.time())
        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('end_time', (datetime.datetime, datetime.date), end_time)

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

        if isinstance(stage_list[0], (int, float)):
            for item in stage_list:
                if not isinstance(item, (int, float)):
                    raise ParamTypeError('item in stage', (int, float), item)
        elif isinstance(stage_list[0], tuple):
            for item in stage_list:
                if not isinstance(item, tuple) or len(item) != 2:
                    raise ParamTypeError('item in stage', tuple, item)
        else:
            raise ParamTypeError('item in stage', (int, float, tuple), stage_list[0])

        self.__growth_stage_list__ = stage_list
        self.__growth_stage_tag__ = stage_tag

    @property
    def growth_stage(self):
        if self.__growth_stage_list__ is None or self.__growth_stage_tag__ is None:
            raise RuntimeError('growth stage should be set by set_growth_stage() before use.')
        else:
            return self.__growth_stage_tag__, self.__growth_stage_list__
