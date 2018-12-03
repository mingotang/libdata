# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


from Interface import AbstractCollector
from structures import DataDict, RecoResult
from structures import Event


class BipartiteNetwork(object):

    def __init__(self, event_dict, in_memory: bool=True):
        from structures import ShelveWrapper
        from utils import get_logger
        self.__logger__ = get_logger(module_name=self.__class__.__name__)

        if in_memory is True:
            if isinstance(self.__event_dict__, (dict, ShelveWrapper, DataDict)):
                self.__event_dict__ = DataDict.init_from(Event, event_dict)
            else:
                from utils.Exceptions import ParamTypeError
                raise ParamTypeError('event_dict', 'dict/ShelveWrapper/DataDict', event_dict)
        else:
            raise NotImplementedError

        

