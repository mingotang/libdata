# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
from enum import Enum

from extended import CountingDict
from structures import SparseVector


from utils.Maths import (
        CosineSimilarity, EuclideanSimilarity,
        PearsonCorrelationCoefficient, TanimotoCoefficient
    )


class CF_NeighborType(Enum):
    ThresholdBased = 'THRESHOLD'
    FixSize = 'K'
    All = 'ALL'


class CF_SimilarityType(Enum):
    Cosine = CosineSimilarity
    Euclidean = EuclideanSimilarity
    Pearson = PearsonCorrelationCoefficient
    Tanimoto = TanimotoCoefficient


class CollaborativeFiltering(object):
    """
    CF: finding neighbors
    """
    def __init__(self, vec_data: dict, possible_neighbor_dict: dict = None):
        """ """
        from utils import get_logger
        self.__logger__ = get_logger(module_name=self.__class__.__name__)

        self.vec_data = dict()
        for k, v in vec_data.items():
            if isinstance(v, SparseVector):
                self.vec_data.__setitem__(k, v)
            else:
                raise NotImplementedError(type(v))

        if isinstance(possible_neighbor_dict, dict):
            self.__possible_neighbor_dict__ = dict()
            for k, v in possible_neighbor_dict.items():
                assert isinstance(v, (set, frozenset, list, tuple)), str(type(v))
                # assert k in self.vec_data, 'unknown vector key {}'.format(k)
                self.__possible_neighbor_dict__[k] = frozenset(v)
        elif possible_neighbor_dict is None:
            self.__possible_neighbor_dict__ = None
        else:
            raise TypeError(type(possible_neighbor_dict))

        self.__neighbor_type__ = CF_NeighborType.All
        self.__similarity_type__ = CF_SimilarityType.Cosine

    def set_neighbor_type(self, n_t: CF_NeighborType):
        self.__neighbor_type__ = n_t
        return self

    def set_similarity_type(self, s_t: CF_SimilarityType):
        self.__similarity_type__ = s_t
        return self

    # def __collect_vec_data__(self):
    #     from collections import defaultdict
    #     self.vec_data = SparseVectorCollector()
    #     main2item, item2main = defaultdict(set), defaultdict(set)
    #     self.__possible_neighbor_dict__ = defaultdict(set)
    #
    #     for value in self.__events__.values():
    #         assert isinstance(value, Event)
    #         main_value, item_value = getattr(value, self.__main_tag__), getattr(value, self.__item_tag__)
    #         if isinstance(item_value, str):
    #             self.vec_data.add(main_value, item_value, getattr(value, self.__item_vector_value_tag__))
    #             main2item[main_value].add(item_value)
    #             item2main[item_value].add(main_value)
    #         else:
    #             raise NotImplementedError
    #
    #     self.vec_data = self.vec_data.finish(with_length=len(self.__events__.collect_attr_set(self.__item_tag__)))
    #     for m_tag, m_value in main2item.items():
    #         for i_tag in m_value:
    #             self.__possible_neighbor_dict__[m_tag].update(item2main[i_tag])

    def run(self, fixed_size: int = None, limited_size: int = None):
        """ -> dict(vector_id: CountingDict(item: similarity, ), )"""
        from tqdm import tqdm
        self.__logger__.debug_running('running CollaborativeFiltering')

        result_dict = dict()
        if self.__neighbor_type__ == CF_NeighborType.All:
            for u_i in tqdm(list(self.vec_data.keys()), desc='collect neighbors'):
                result_dict[u_i] = self.__find_all_neighbors__(u_i, self.__similarity_type__)
                # simi_result.add_list(u_i, self.__find_all_neighbors__(u_i, self.__similarity_type__))

        elif self.__neighbor_type__ == CF_NeighborType.FixSize:
            if fixed_size is None:
                from extended.Exceptions import ParamMissingError
                raise ParamMissingError('fixed_size')

            if fixed_size > 0:
                for u_i in tqdm(list(self.vec_data.keys()), desc='collect neighbors'):
                    result_dict[u_i] = self.__find_k_neighbors__(u_i, fixed_size, self.__similarity_type__)
            else:
                from extended.Exceptions import ParamOutOfRangeError
                raise ParamOutOfRangeError('fixed_size', (1, 'inf'), fixed_size)

        elif self.__neighbor_type__ == CF_NeighborType.ThresholdBased:
            if limited_size is None:
                from extended.Exceptions import ParamMissingError
                raise ParamMissingError('limited_size')

            if limited_size > 0:
                for u_i in tqdm(list(self.vec_data.keys()), desc='collect neighbors'):
                    result_dict[u_i] = self.__find_limited_neighbors__(u_i, limited_size, self.__similarity_type__)
            else:
                from extended.Exceptions import ParamOutOfRangeError
                raise ParamOutOfRangeError('limited_size', (1, 'inf'), limited_size)
        else:
            raise RuntimeError

        return result_dict

    # def __collect_neighbors__(self, simi_result: RecoResult, max_recommend_list: int):
    #     from tqdm import tqdm
    #     used_data = self.__events__.group_attr_set_by(self.__item_tag__, self.__main_tag__)
    #     reco_result = RecoResult()
    #     for u_i, simi_list in tqdm(simi_result.items(), desc='collect recommendation'):
    #         reco_list = list()
    #         main_set = used_data[u_i]
    #         for sub_i in simi_list:
    #             sub_set = used_data[sub_i]
    #             reco_set = sub_set - main_set
    #             for item in reco_set:
    #                 if len(reco_list) > max_recommend_list:
    #                     continue
    #                 if item not in reco_list:
    #                     reco_list.append(item)
    #         reco_result.add_list(u_i, reco_list)
    #     return reco_result

    def __calculate_neighbors__(self, ui_tag: str, sim_type):
        result = CountingDict()

        if self.__possible_neighbor_dict__ is None:
            for tag in self.vec_data.keys():
                if tag == ui_tag:
                    continue
                if tag not in self.vec_data:
                    continue
                result.set(tag, abs(sim_type.__call__(self.vec_data[ui_tag], self.vec_data[tag])))
        else:
            possible_neighbor_set = self.__possible_neighbor_dict__[ui_tag]
            # self.__logger__.debug_variable(possible_neighbor_set)
            for tag in possible_neighbor_set:
                if tag == ui_tag:
                    continue
                if tag not in self.vec_data:
                    continue
                result.set(tag, abs(sim_type.__call__(self.vec_data[ui_tag], self.vec_data[tag])))

        return result

    def __find_all_neighbors__(self, ui_tag: str, simi_type):
        """find all neighborhoods ordered by similarity -> list"""
        return self.__calculate_neighbors__(ui_tag, simi_type)

    def __find_k_neighbors__(self, ui_tag: str, k_num: int, simi_type):
        result = self.__calculate_neighbors__(ui_tag, simi_type)
        return result.sub_dict(result.sort(reverse=True)[: k_num])

    def __find_limited_neighbors__(self, ui_tag: str, limit: float, simi_type):
        return self.__calculate_neighbors__(ui_tag, simi_type).trim(lower_limit=limit)


class SparseVectorCollector(object):
    def __init__(self):
        from collections import defaultdict
        self.data = defaultdict(SparseVector)

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

    def regulate(self, multiply: float = 1.0, add: float = 0.0):
        for vector in self.values():
            assert isinstance(vector, SparseVector)
            for key in vector.keys():
                vector[key] = vector[key] * multiply + add

    def add(self, user: str, item: str, times=1):
        self.data[user][item] = self.data[user][item] + times

    def finish(self, with_length: int):
        assert with_length >= 0
        for tag in self.data:
            self.data[tag].set_length(with_length)
        return self.data

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
