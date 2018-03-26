# -*- encoding: UTF-8 -*-
import logbook

logbook.set_datetime_format("local")

# 系统日志
system_log = logbook.Logger("system_log")

# 调试系统日志
info_log = logbook.Logger("info_log")

# 危险日志
warning_log = logbook.Logger("warning_log")

def set_logbook():
    pass

def set_logging():
    import logging
    logging.basicConfig(
        level=logging.DEBUG,  # 定义输出到文件的log级别，
        format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',  # 定义输出log的格式
        datefmt='%Y-%m-%d %A %H:%M:%S',  # 时间
    )


class LogInfo(object):
    @staticmethod
    def running(running: str, status: str):
        return '[running]: {0:s} - now {1:s}'.format(
            running, status,
        )

    @staticmethod
    def variable_detail(variable):
        return '[variable]: {0:s} got type {1:s} and content {2:s}'.format(
            str(id(variable)), str(type(variable)), str(variable)
        )
