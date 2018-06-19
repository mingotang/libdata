# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os

from collections import defaultdict, Mapping
from enum import Enum

from Interface import AbstractCollector
from structures.Book import Book
from structures.Extended import CountingDict
from structures.Reader import Reader
from structures.SparseVector import SparseVector
from utils.DataBase import ShelveWrapper
from utils.Logger import get_logger


logger = get_logger(module_name=__file__)


class NeighborType(Enum):
    ThresholdBased = 'THRESHOLD'
    FixSize = 'K'
    All = 'ALL'


class SimilarityType(Enum):
    from functions.Maths import (
        CosineSimilarity, EuclideanSimilarity,
        PearsonCorrelationCoefficient, TanimotoCoefficient
    )
    Cosine = CosineSimilarity
    Euclidean = EuclideanSimilarity
    Pearson = PearsonCorrelationCoefficient
    Tanimoto = TanimotoCoefficient


class CFResult(dict):
    def __init__(self):
        super(CFResult, self).__init__()

    def add_list(self, key: str, value: list):
        self.__setitem__(key, value)


class CollaborativeFiltering(object):
    """
    CF: finding neighbors
    """
    def __init__(self, data, attr_belong: type, **kwargs):
        """

        :param data: dict/Pdict/ShelveWrapper/PreferenceCollector
        :param attr_belong:
        :param kwargs: in_memory bool/book2reader dict/reader2book dict
        """
        import datetime
        from Config import DataConfig
        from modules.DataProxy import DataProxy
        from utils.Persisit import Pdict

        if not len(data) > 0:
            from utils.Exceptions import ParamNoContentError
            raise ParamNoContentError('data')

        if attr_belong in (Book, Reader):
            self.__attr_belong__ = attr_belong
        else:
            from utils.Exceptions import ParamOutOfRangeError
            raise ParamOutOfRangeError('attr_belong', ('Book', 'Reader'), attr_belong)

        # indexing data in order to speed up calculation
        if kwargs.get('book2reader', None) is None and kwargs.get('reader2book', None) is None:
            try:
                self.book2reader = DataProxy.get_shelve('readers_group_by_books')
                self.reader2book = DataProxy.get_shelve('books_group_by_readers')
                logger.debug_running('CollaborativeFiltering.init', 'start with GENERAL searching mode')
            except FileNotFoundError:
                self.book2reader, self.reader2book = None, None
                logger.debug_running('CollaborativeFiltering.init', 'start with STUPID searching mode')
        elif kwargs.get('book2reader', None) is not None and kwargs.get('reader2book', None) is not None:
            self.book2reader, self.reader2book = kwargs.get('book2reader'), kwargs.get('reader2book')
            # checking book2reader and reader2book Mapping
            if not isinstance(self.book2reader, Mapping):
                from utils.Exceptions import ParamTypeError
                raise ParamTypeError('book2reader', 'Mapping', self.book2reader)
            if not isinstance(self.reader2book, Mapping):
                from utils.Exceptions import ParamTypeError
                raise ParamTypeError('reader2book', 'Mapping', self.reader2book)
            logger.debug_running('CollaborativeFiltering.init', 'start with BEST searching mode')
        else:
            raise RuntimeError('parameter book2reader and reader2book should be set at the same time')

        self.__in_memory__ = kwargs.get('in_memory', True)  # tag whether record goods in memory
        self.__origin_db__ = False  # tag whether input data_sets is db

        now = datetime.datetime.now()

        # pre operation
        if self.__in_memory__ is True:
            if isinstance(data, dict):
                self.data = data  # dict
            elif isinstance(data, Pdict):
                self.data = data.copy()
            elif isinstance(data, (ShelveWrapper, PreferenceCollector)):
                self.data = data.to_dict()
            else:
                from utils.Exceptions import ParamTypeError
                raise ParamTypeError('data_sets', 'dict/Pdict/ShelveWrapper/PreferenceCollector', data)
        else:
            local_path = os.path.join(
                DataConfig.operation_path,
                '__cofilter_temp_{}__'.format(now.strftime('%Y%m%d %H%M%S.%f'))
            )
            if isinstance(data, (dict, Pdict)):
                self.data = ShelveWrapper.init_from(data, local_path, writeback=False)
            elif isinstance(data, PreferenceCollector):
                self.data_sets = ShelveWrapper.init_from(data.to_dict(), local_path, writeback=False)
            elif isinstance(data, ShelveWrapper):
                self.data = data
                self.__origin_db__ = True
            else:
                from utils.Exceptions import ParamTypeError
                raise ParamTypeError('data_sets', 'dict/Pdict/ShelveWrapper/PreferenceCollector', data)

        # check data
        for value in self.data.values():
            if not isinstance(value, (dict, SparseVector)):
                from utils.Exceptions import ValueTypeError
                raise ValueTypeError('data', 'dict/SparseVector', value)

    def delete_data(self):
        if self.__in_memory__ is True:
            assert isinstance(self.data, dict)
            self.data.clear()
        else:
            assert isinstance(self.data, ShelveWrapper)
            if self.__origin_db__ is False:
                self.data.delete()

    def run(self, neighbor_type: NeighborType=NeighborType.All,
            sim_type: SimilarityType=SimilarityType.Cosine,
            **kwargs):
        """

        :param neighbor_type:
        :param sim_type:
        :param kwargs:
            size:
            limit:
        :return:
        """
        logger.debug_running('CollaborativeFiltering.run', 'start')

        result = CFResult()
        if neighbor_type == NeighborType.All:
            for u_i in self.data.keys():
                result.add_list(u_i, self.find_all_neighbors(u_i, sim_type))
        elif neighbor_type == NeighborType.FixSize:
            if 'size' in kwargs:
                size = kwargs['size']
            else:
                from utils.Exceptions import ParamMissingError
                raise ParamMissingError('size')
            for u_i in self.data.keys():
                result.add_list(u_i, self.find_k_neighbors(u_i, size, sim_type))
        elif neighbor_type == NeighborType.ThresholdBased:
            if 'limit' in kwargs:
                limit = kwargs['limit']
            else:
                from utils.Exceptions import ParamMissingError
                raise ParamMissingError('limit')
            for u_i in self.data.keys():
                result.add_list(u_i, self.find_limited_neighbors(u_i, limit, sim_type))
        else:
            raise ValueError

        logger.debug_running('CollaborativeFiltering.run', 'end')
        return result

    def __calculate_neighbors__(self, ui_tag: str, sim_type: SimilarityType):
        result = CountingDict()
        if self.book2reader is None or self.reader2book is None:
            for tag in self.data.keys():
                if tag == ui_tag:
                    continue
                result.set(tag, abs(sim_type.value.__call__(self.data[ui_tag], self.data[tag])))
        else:
            if self.__attr_belong__ == Book:
                for reader_i in self.book2reader[ui_tag]:
                    for book_i in self.reader2book[reader_i]:
                        if book_i == ui_tag:
                            continue
                        if book_i not in result:
                            result.set(book_i, abs(
                                sim_type.value.__call__(self.data[ui_tag], self.data[book_i])
                            ))
            else:
                for book_i in self.reader2book[ui_tag]:
                    for reader_i in self.book2reader[book_i]:
                        if reader_i == ui_tag:
                            continue
                        if reader_i not in result:
                            result.set(reader_i, abs(
                                sim_type.value.__call__(self.data[ui_tag], self.data[reader_i])
                            ))
        return result

    def find_all_neighbors(self, ui_tag: str, simi_type: SimilarityType):
        """find all neighborhoods ordered by similarity -> list"""
        return self.__calculate_neighbors__(ui_tag, simi_type).sort(inverse=True)

    def find_k_neighbors(self, ui_tag: str, k_num: int, simi_type: SimilarityType):
        assert k_num > 0
        return self.find_all_neighbors(ui_tag, simi_type)[:k_num]

    def find_limited_neighbors(self, ui_tag: str, limit: float, simi_type: SimilarityType):
        simi = self.__calculate_neighbors__(ui_tag, simi_type).trim(lower_limit=limit)
        return simi.sort(inverse=True)


class PreferenceCollector(AbstractCollector):
    def __init__(self):
        self.data = defaultdict(SparseVector)

    def __getitem__(self, key: str):
        return self.data.__getitem__(key)

    def __iter__(self):
        for tag in self.data.keys():
            yield tag

    def keys(self):
        return self.data.keys()

    def add(self, user: str, item: str, times=1):
        self.data[user][item] = self.data[user][item] + times

    def finish(self, with_length=None):
        if with_length is not None:
            for tag in self.data:
                self.data[tag].set_length(with_length)

    def to_dict(self):
        return self.data.copy()


if __name__ == '__main__':
    logger.initiate_time_counter()
    # ------------------------------

    # ------------------------------
    logger.print_time_passed()
