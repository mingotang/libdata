# -*- encoding: UTF-8 -*-
import datetime
import logging
import time


def set_logging(level: int=logging.DEBUG):
    logging.basicConfig(
        level=level,  # 定义输出到文件的log级别，
        format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',  # 定义输出log的格式
        datefmt='%Y-%m-%d %A %H:%M:%S',  # 时间
        # filename=param.log_file_name,  # log文件名
        # filemode='w',
    )


class LogWrapper(object):

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    @staticmethod
    def initiate_time_counter():
        RunTimeCounter.get_instance()

    @staticmethod
    def time_sleep(seconds):
        time.sleep(seconds)

    @staticmethod
    def print_time_passed():
        print('\nRunning time: {0:s}'.format(RunTimeCounter.get_instance().tp_str))

    def debug(self, msg: str, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def debug_if(self, check: bool, msg: str, *args, **kwargs):
        if check is True:
            self.debug(msg, *args, **kwargs)

    def debug_running(self, running: str, status: str):
        self.debug('[running]: {0:s} - now {1:s}'.format(running, status))

    def debug_variable(self, variable):
        self.debug('[variable]: {0:s} got type {1:s} and content {2:s}'.format(
                str(id(variable)), str(type(variable)), str(variable)
            ))

    def info(self, msg: str, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def info_if(self, check: bool, msg: str, *args, **kwargs):
        if check is True:
            self.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def warning_if(self, check: bool, msg: str, *args, **kwargs):
        if check is True:
            self.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)


def get_logger(level: int=logging.DEBUG, module_name: str=''):
    """

    :param level: logging level
    :return: :class:`~logging.Logger`
    """
    if module_name == '':
        logger = logging.getLogger()
    else:
        logger = logging.getLogger(module_name)
    logger.setLevel(level)

    screen_handler = logging.StreamHandler()
    screen_handler.setFormatter(logging.Formatter('%(asctime)s %(filename)s:  %(levelname)s, %(message)s'))
    logger.addHandler(screen_handler)

    return LogWrapper(logger)


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
