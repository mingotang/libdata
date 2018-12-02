# -*- encoding: UTF-8 -*-
import logging


def attributes_repr(inst):
    return "{}({})".format(
        inst.__class__.__name__,
        ', '.join([str(var) + ': ' + str(getattr(inst, var)) for var in inst.__attributes__])
    )


def slots_repr(inst):
    return "{}({})".format(
        inst.__class__.__name__,
        ', '.join([str(k) + ': ' + str(v) for k, v in slots(inst).items()])
    )


def slots(inst):
    result = dict()
    for slot in inst.__slots__:
        result[slot] = getattr(inst, slot)
    return result


def load_yaml(path: str):
    """载入yml格式配置文件"""
    import codecs
    import yaml
    with codecs.open(path, encoding='utf-8') as y_f:
        return yaml.load(y_f)


def set_logging(level: int):
    # import logging
    logging.basicConfig(
        level=level,  # 定义输出到文件的log级别，
        format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',  # 定义输出log的格式
        datefmt='%Y-%m-%d %A %H:%M:%S',  # 时间
        # filename=param.log_file_name,  # log文件名
        # filemode='w',
    )


class RunTimeCounter(object):
    __instance__ = None
    __default_time_pattern__ = '%H h %M m %S s %f ms'

    def __init__(self, back_run=False):
        import time
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
        import time
        self.__origin_time__ = time.time()

    def set_time_pattern(self, pattern: str):
        self.__time_pattern__ = pattern

    @property
    def tp_time(self):
        import time
        import datetime
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


class LogWrapper(logging.Logger):

    def __init__(self, name: str, level=logging.NOTSET):
        super(LogWrapper, self).__init__(name=name, level=level)

    @staticmethod
    def initiate_time_counter():
        RunTimeCounter.get_instance()

    @staticmethod
    def time_sleep(seconds):
        from time import sleep
        sleep(seconds)

    @staticmethod
    def print_time_passed():
        print('\nTime passed: {0:s}'.format(RunTimeCounter.get_instance().tp_str))

    def debug_running(self, *args, **kwargs):
        # self.debug('[running]: {0:s} - now {1:s}'.format(running, status))
        if self.isEnabledFor(logging.DEBUG):
            if len(args) == 2:
                self._log(
                    logging.DEBUG,
                    '[running]: {0:s} - now {1:s}'.format(args[0], args[1]),
                    tuple(), **kwargs
                )
            elif len(args) == 1:
                self._log(logging.DEBUG, '[running]: {0:s}'.format(args[0]), tuple(), **kwargs)
            else:
                self._log(logging.DEBUG, *args, **kwargs)

    def debug_variable(self, variable, *args, **kwargs):
        from collections import Sized
        log_info = '[variable]: {0:s} has content {1:s} and of type {2:s} '.format(
                    str(id(variable)), str(variable), str(type(variable)),
                )
        if isinstance(variable, Sized):
            log_info += ', of size {}'.format(len(variable))
        if self.isEnabledFor(logging.DEBUG):
            self._log(logging.DEBUG, log_info, args, **kwargs)

    def debug_if(self, check: bool, msg: str, *args, **kwargs):
        if check is True and self.isEnabledFor(logging.DEBUG):
            self._log(logging.DEBUG, msg, args, **kwargs)

    def info_if(self, check: bool, msg: str, *args, **kwargs):
        if check is True and self.isEnabledFor(logging.INFO):
            self._log(logging.INFO, msg, args, **kwargs)

    def warning_if(self, check: bool, msg: str, *args, **kwargs):
        if check is True and self.isEnabledFor(logging.WARNING):
            self._log(logging.WARNING, msg, args, **kwargs)


LOG_LEVEL_MAP = {
    'None': logging.NOTSET,
    'debug': logging.DEBUG,
    'info': logging.INFO,
}


def get_logger(module_name: str=''):
    """

    :param level: logging level
    :param module_name: str
    :return: :class:`~logging.Logger`
    """
    from Environment import Environment
    config = Environment.get_instance().config
    log_level = LOG_LEVEL_MAP[config.get('Log', dict()).get('LogLevel', 'None')]
    logger = LogWrapper(module_name, log_level)

    screen_handler = logging.StreamHandler()
    screen_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(filename)s %(funcName)s %(lineno)d:  %(levelname)s, %(message)s'
    ))
    logger.addHandler(screen_handler)

    return logger
