# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


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
