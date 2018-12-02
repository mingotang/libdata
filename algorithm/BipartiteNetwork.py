# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


from Interface import AbstractCollector
from structures import DataDict, RecoResult
from structures import Event


class BipartiteNetwork(object):

    def __init__(self, event_dict, in_memory: bool=True):
        from utils import get_logger
        self.__logger__ = get_logger(module_name=self.__class__.__name__)

        if in_memory is True:
            self.__event_dict__ = event_dict
        else:
            raise NotImplementedError


