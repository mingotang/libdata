# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
from enum import Enum

from Interface import AbstractCollector, AbstractResult
from structures import CountingDict, SparseVector
from structures import ShelveWrapper


class NeighborType(Enum):
    ThresholdBased = 'THRESHOLD'
    FixSize = 'K'
    All = 'ALL'


class SimilarityType(Enum):
    from utils.Maths import (
        CosineSimilarity, EuclideanSimilarity,
        PearsonCorrelationCoefficient, TanimotoCoefficient
    )
    Cosine = CosineSimilarity
    Euclidean = EuclideanSimilarity
    Pearson = PearsonCorrelationCoefficient
    Tanimoto = TanimotoCoefficient


class CFResult(AbstractResult):
    def __init__(self):
        pass

    def add_list(self, key: str, value: list):
        pass


class CollaborativeFiltering(object):
    """
    CF: finding neighbors
    """
    def __init__(self, vec_data, in_memory: bool=False):
        """

        :param vec_data: dict/ShelveWrapper/PreferenceCollector
        :param in_memory: bool
        """
        from utils import get_logger
        self.__logger__ = get_logger(module_name=self.__class__.__name__)
        self.__logger__.debug_running('{}.__init__'.format(self.__class__.__name__), 'begin')

        # 检查参数
        if not len(vec_data) > 0:
            from utils.Exceptions import ParamNoContentError
            raise ParamNoContentError('vec_data')

        # 运行数据是否储存在内存中
        if in_memory is True:
            if isinstance(vec_data, dict):
                self.data = vec_data
            elif isinstance(vec_data, ShelveWrapper):
                self.data = vec_data.to_dict()
            elif isinstance(vec_data, SparseVectorCollector):
                self.data = vec_data.to_dict()
            else:
                from utils.Exceptions import ParamTypeError
                raise ParamTypeError('vec_data', (dict, ShelveWrapper, SparseVectorCollector), vec_data)
        else:
            self.data = ShelveWrapper.get_temp()
            if isinstance(vec_data, (ShelveWrapper, dict)):
                self.data.update(vec_data)
            elif isinstance(vec_data, SparseVectorCollector):
                self.data.update(vec_data.to_dict())
            else:
                from utils.Exceptions import ParamTypeError
                raise ParamTypeError('vec_data', (dict, ShelveWrapper, SparseVectorCollector), vec_data)

        # 检查数据格式是否符合要求
        self.__logger__.debug_running('{}.__init__'.format(self.__class__.__name__), 'checking data')
        for value in self.data.values():
            if not isinstance(value, (dict, SparseVector)):
                from utils.Exceptions import ValueTypeError
                raise ValueTypeError('value in vec_data', (dict, SparseVector), value)

        self.__logger__.debug_running('{}.__init__'.format(self.__class__.__name__), 'end')

    def delete_data(self):
        if isinstance(self.data, ShelveWrapper):
            self.data.delete()
        del self.data
        self.__logger__.debug_running('{}.delete_data'.format(self.__class__.__name__), 'finished')

    def run(self, neighbor_type: NeighborType=NeighborType.All,
            similarity_type: SimilarityType=SimilarityType.Cosine,
            fixed_size: int=None, limited_size: int=None,):
        """

        :param neighbor_type: NeighborType
        :param similarity_type: SimilarityType
        :param fixed_size: int
        :param limited_size: int
        :return:
        """
        self.__logger__.debug_running('{}.run'.format(self.__class__.__name__), 'begin')

        result = CFResult()
        self.__logger__.debug_running(
            '{}.run'.format(self.__class__.__name__),
            'executing {}.{}'.format(NeighborType.__class__.__name__, neighbor_type.name)
        )
        if neighbor_type == NeighborType.All:
            for u_i in self.data.keys():
                result.add_list(u_i, self.find_all_neighbors(u_i, similarity_type))

        elif neighbor_type == NeighborType.FixSize:
            if fixed_size is None:
                from utils.Exceptions import ParamMissingError
                raise ParamMissingError('fixed_size')

            if fixed_size > 0:
                for u_i in self.data.keys():
                    result.add_list(u_i, self.find_k_neighbors(u_i, fixed_size, similarity_type))
            else:
                from utils.Exceptions import ParamOutOfRangeError
                raise ParamOutOfRangeError('fixed_size', (1, 'inf'), fixed_size)

        elif neighbor_type == NeighborType.ThresholdBased:
            if limited_size is None:
                from utils.Exceptions import ParamMissingError
                raise ParamMissingError('limited_size')

            if limited_size > 0:
                for u_i in self.data.keys():
                    result.add_list(u_i, self.find_limited_neighbors(u_i, limited_size, similarity_type))
            else:
                from utils.Exceptions import ParamOutOfRangeError
                raise ParamOutOfRangeError('limited_size', (1, 'inf'), limited_size)
        else:
            raise RuntimeError

        self.__logger__.debug_running('{}.run'.format(self.__class__.__name__), 'end')
        return result

    def __calculate_neighbors__(self, ui_tag: str, sim_type: SimilarityType):
        result = CountingDict()
        for tag in self.data.keys():
            if tag == ui_tag:
                continue
            result.set(tag, abs(sim_type.value.__call__(self.data[ui_tag], self.data[tag])))
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


class SparseVectorCollector(AbstractCollector):
    def __init__(self):
        self.data = dict()

    def __getitem__(self, key: str):
        return self.data.__getitem__(key)

    def __setitem__(self, key: str, value: SparseVector):
        if value.has_size:
            self.data.__setitem__(key, value)
        else:
            raise RuntimeError('SparseVector has no size.')

    def __iter__(self):
        for tag in self.data.keys():
            yield tag

    def add(self, user: str, item: str, times=1):
        self.data[user][item] = self.data[user][item] + times

    def finish(self, with_length=None):
        if with_length is not None:
            for tag in self.data:
                self.data[tag].set_length(with_length)

    def to_dict(self):
        return self.data.copy()

    def delete(self):
        del self.data

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

    def __len__(self):
        return self.data.__len__()

    def __contains__(self, key: str):
        return self.data.__contains__(key)


if __name__ == '__main__':
    from utils import get_logger
    logger = get_logger(__file__)
    logger.initiate_time_counter()
    # ------------------------------

    # ------------------------------
    logger.print_time_passed()
