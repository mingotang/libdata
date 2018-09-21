# -*- encoding: UTF-8 -*-
from tqdm import tqdm

from Config import DataConfig
from algorithm import AP_Type, CF_BaseType


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
        print('number of total readers: {}'.format(len(readers)))

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
