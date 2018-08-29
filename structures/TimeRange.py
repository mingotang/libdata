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
