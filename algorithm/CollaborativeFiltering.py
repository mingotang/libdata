# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging

from collections import defaultdict
from enum import Enum

from Interface import AbstractCollector
from structures.Extended import CountingDict
from structures.SparseVector import SparseVector
from utils.Logger import LogInfo


__ = logging.debug


class NeighborType(Enum):
    ThresholdBased = 'THRESHOLD'
    FixSize = 'K'
    All = 'ALL'


class SimilarityType(Enum):
    from functions.Maths import CosineSimilarity, EuclideanSimilarity, PearsonCorrelationCoefficient, TanimotoCoefficient
    Cosine = CosineSimilarity
    Euclidean = EuclideanSimilarity
    Pearson = PearsonCorrelationCoefficient
    Tanimoto = TanimotoCoefficient


class CollaborativeFiltering(object):
    def __init__(self, data, **kwargs):
        assert isinstance(data, PreferenceCollector)
        self.data = data

    def run(self, **kwargs):
        __(LogInfo.running('CollaborativeFiltering.run', 'start'))

        calcu_type = kwargs.get('type', NeighborType.All)
        if isinstance(calcu_type, NeighborType):
            pass
        elif isinstance(calcu_type, str):
            calcu_type = NeighborType(calcu_type)
        else:
            raise TypeError

        __(LogInfo.running('CollaborativeFiltering.run', 'end'))

    def __calculate_neighbors__(self, ui_tag: str, simi_type: SimilarityType):
        simi = CountingDict()
        for tag in self.data:
            simi.set(tag, abs(
                simi_type.value.__call__(self.data[ui_tag], self.data[tag])
            ))
        return simi

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


if __name__ == '__main__':
    from utils.Logger import set_logging, RunTimeCounter
    RunTimeCounter(back_run=True)
    # ------------------------------
    set_logging()

    # ------------------------------
    print('Running time: {}'.format(RunTimeCounter.get_instance().tp_str))
