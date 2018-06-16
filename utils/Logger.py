# -*- encoding: UTF-8 -*-
import datetime
import logging
import time

from libdata import DEFAULT_LOG_LEVEL


def set_logging(level: int=logging.DEBUG):
    logging.basicConfig(
        level=level,  # 定义输出到文件的log级别，
        format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',  # 定义输出log的格式
        datefmt='%Y-%m-%d %A %H:%M:%S',  # 时间
        # filename=param.log_file_name,  # log文件名
        # filemode='w',
    )


class LogWrapper(logging.Logger):

    def __init__(self, name: str, level=logging.NOTSET):
        super(LogWrapper, self).__init__(name=name, level=level)

    @staticmethod
    def initiate_time_counter():
        RunTimeCounter.get_instance()

    @staticmethod
    def time_sleep(seconds):
        time.sleep(seconds)

    @staticmethod
    def print_time_passed():
        print('\nRunning time: {0:s}'.format(RunTimeCounter.get_instance().tp_str))

    def debug_running(self, running: str, status: str, *args, **kwargs):
        self.debug('[running]: {0:s} - now {1:s}'.format(running, status))
        if self.isEnabledFor(logging.DEBUG):
            self._log(
                logging.DEBUG,
                '[running]: {0:s} - now {1:s}'.format(running, status),
                args, **kwargs
            )

    def debug_variable(self, variable, *args, **kwargs):
        if self.isEnabledFor(logging.DEBUG):
            self._log(
                logging.DEBUG,
                '[variable]: {0:s} got type {1:s} and content {2:s}'.format(
                    str(id(variable)), str(type(variable)), str(variable)
                ), args, **kwargs
            )

    def debug_if(self, check: bool, msg: str, *args, **kwargs):
        if check is True and self.isEnabledFor(logging.DEBUG):
            self._log(logging.DEBUG, msg, args, **kwargs)

    def info_if(self, check: bool, msg: str, *args, **kwargs):
        if check is True and self.isEnabledFor(logging.INFO):
            self._log(logging.INFO, msg, args, **kwargs)

    def warning_if(self, check: bool, msg: str, *args, **kwargs):
        if check is True and self.isEnabledFor(logging.WARNING):
            self._log(logging.WARNING, msg, args, **kwargs)


def get_logger(module_name: str='', level: int=DEFAULT_LOG_LEVEL):
    """

    :param level: logging level
    :param module_name: str
    :return: :class:`~logging.Logger`
    """
    logger = LogWrapper(module_name, level)
    logger.setLevel(level)

    screen_handler = logging.StreamHandler()
    screen_handler.setFormatter(logging.Formatter('%(asctime)s %(filename)s:  %(levelname)s, %(message)s'))
    logger.addHandler(screen_handler)

    return logger


class RunTimeCounter(object):
    __instance__ = None
    __default_time_pattern__ = '%H h %M m %S s %f ms'

    def __init__(self, back_run=False):
        self.__time_pattern__ = self.__default_time_pattern__
        self.__origin_time__ = time.time()
        if back_run is True:
            RunTimeCounter.__instance__ = self

    @classmethod
    def get_instance(cls):
        if RunTimeCounter.__instance__ is None:
            return cls(back_run=True)
        else:
            return RunTimeCounter.__instance__

    def reset(self):
        self.__origin_time__ = time.time()

    def set_time_pattern(self, pattern: str):
        self.__time_pattern__ = pattern

    @property
    def tp_time(self):
        t_period = time.time() - self.__origin_time__
        micro_second = int((t_period - int(t_period)) * 1000)
        minutes, seconds = divmod(int(t_period), 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        return datetime.time(
            hour=hours, minute=minutes, second=seconds, microsecond=micro_second,
        )

    @property
    def tp_str(self):
        return self.tp_time.strftime(self.__time_pattern__)
