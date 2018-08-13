# -*- encoding: UTF-8 -*-
from .wrapper.Log import LogWrapper
from .wrapper.Persisit import Pdict, Plist, PqueueFIFO, PqueueLIFO, Pset
from .wrapper.Recorder import CSVRecorder, TextRecorder
from .wrapper.Shelve import ShelveWrapper
from .wrapper.Sqlite import SqliteWrapper
from .wrapper.UnicodeStr import UnicodeStr

from Config import DEFAULT_LOG_LEVEL


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


def set_logging(level: int=DEFAULT_LOG_LEVEL):
    import logging
    logging.basicConfig(
        level=level,  # 定义输出到文件的log级别，
        format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',  # 定义输出log的格式
        datefmt='%Y-%m-%d %A %H:%M:%S',  # 时间
        # filename=param.log_file_name,  # log文件名
        # filemode='w',
    )


def get_logger(module_name: str='', level: int=DEFAULT_LOG_LEVEL):
    """

    :param level: logging level
    :param module_name: str
    :return: :class:`~logging.Logger`
    """
    import logging
    logger = LogWrapper(module_name, level)
    logger.setLevel(level)

    screen_handler = logging.StreamHandler()
    screen_handler.setFormatter(logging.Formatter('%(asctime)s %(filename)s:  %(levelname)s, %(message)s'))
    logger.addHandler(screen_handler)

    return logger
