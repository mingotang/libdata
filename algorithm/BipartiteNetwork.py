# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------

from structures import DataDict, SparseVector
from structures import Event


class BipartiteNetwork(object):

    def __init__(self, event_dict, in_memory: bool = True):
        from structures import ShelveWrapper
        from utils import get_logger
        self.__logger__ = get_logger(module_name=self.__class__.__name__)

        if in_memory is True:
            if isinstance(self.__event_dict__, DataDict):
                self.__event_dict__ = event_dict
            elif isinstance(self.__event_dict__, (dict, ShelveWrapper)):
                self.__event_dict__ = DataDict.init_from(Event, event_dict)
            else:
                from utils.Exceptions import ParamTypeError
                raise ParamTypeError('event_dict', 'dict/ShelveWrapper/DataDict', event_dict)
        else:
            raise NotImplementedError

        self.book_weight = self.__init_weight__('book_id')    # 书籍权重
        self.reader_weight = self.__init_weight__('reader_id')    # 读者权重
        # self.__calculated_bw__ = SparseVector()    # 计算书籍权重
        # self.__calculated_rw__ = SparseVector()     # 计算读者权重

    def __init_weight__(self, tag: str):
        from structures import CountingDict
        if isinstance(self.__event_dict__, DataDict):
            data_dict = self.__event_dict__
        else:
            data_dict = DataDict.init_from(Event, self.__event_dict__)
        new_vector = SparseVector(data_dict.count_attr(tag))
        new_vector.update(CountingDict.init_from(data_dict.collect_attr_list(tag)))
        return new_vector

    def run(self):
        if isinstance(self.__event_dict__, DataDict):
            b_w, r_w = SparseVector(len(self.book_weight)), SparseVector(len(self.reader_weight))
        else:
            raise NotImplementedError

        while (self.book_weight - b_w).sum_squared < 0.1 and (self.reader_weight - r_w).sum_squared < 0.1:
            
