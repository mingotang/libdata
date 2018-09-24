# -*- encoding: UTF-8 -*-
import datetime
from Config import DataConfig


class RuleOneGenerator(object):
    def __init__(self, data_path: str=DataConfig.data_path, operation_path: str=DataConfig.operation_path):
        from modules.DataProxy import DataProxy
        from utils import get_logger
        self.__logger__ = get_logger(self.__class__.__name__)

        self.__data_path__ = data_path
        self.__operation_path__ = operation_path

        self.__data_proxy__ = DataProxy(data_path=self.__data_path__)

    def simple_statistic(self):
        readers = self.__data_proxy__.readers
        print('total readers: {}'.format(len(readers)))

        books = self.__data_proxy__.books
        print('total books: {}'.format(len(books)))

        events = self.__data_proxy__.events.to_data_dict()
        print('total events: {}'.format(len(events)))
        print('2013 events: {}'.format(events.trim_between_range(
            'date', datetime.date(2013, 1, 1), datetime.date(2014, 1, 1))))
        print('2014 events: {}'.format(events.trim_between_range(
            'date', datetime.date(2014, 1, 1), datetime.date(2015, 1, 1))))
        print('2015 events: {}'.format(events.trim_between_range(
            'date', datetime.date(2015, 1, 1), datetime.date(2016, 1, 1))))


    @property
    def log(self):
        return self.__logger__

    def close(self):
        self.__data_proxy__.close()


if __name__ == '__main__':
    rule_one = RuleOneGenerator()
    rule_one.log.initiate_time_counter()

    try:
        rule_one.simple_statistic()
    except KeyboardInterrupt:
        rule_one.close()
    finally:
        rule_one.close()

    rule_one.log.time_sleep(1)
    rule_one.log.print_time_passed()
