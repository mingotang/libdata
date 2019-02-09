# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
from enum import Enum

from extended import CountingDict, DataDict
from structures import RecoResult, SparseVector
from structures import Event


from utils.Maths import (
        CosineSimilarity, EuclideanSimilarity,
        PearsonCorrelationCoefficient, TanimotoCoefficient
    )


class CF_BaseType(Enum):
    ReaderBase = 'ReaderBase'
    BookBase = 'BookBase'


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
    def __init__(self, events_dict):
        """

        :param events_dict: DataDict
        """
        from utils import get_logger
        self.__logger__ = get_logger(module_name=self.__class__.__name__)

        assert isinstance(events_dict, dict)
        self.__events__ = events_dict

        self.__main_tag__, self.__item_tag__ = None, None
        self.__neighbor_type__ = CF_NeighborType.All
        self.__similarity_type__ = CF_SimilarityType.Cosine
        self.__item_vector_value_tag__ = None               # Event 对象中获取向量值的属性

        self.vec_data = None
        self.__possible_neighbor_dict__ = None

    def set_relation_tag(self, main_tag: str, item_tag: str):
        self.__main_tag__, self.__item_tag__ = main_tag, item_tag
        return self

    def set_neighbor_type(self, n_t: CF_NeighborType):
        self.__neighbor_type__ = n_t
        return self

    def set_similarity_type(self, s_t: CF_SimilarityType):
        self.__similarity_type__ = s_t
        return self

    def set_item_vector_value_tag(self, v_tag: str):
        self.__item_vector_value_tag__ = v_tag
        return self

    def __collect_vec_data__(self):
        from collections import defaultdict
        self.vec_data = SparseVectorCollector()
        main2item, item2main = defaultdict(set), defaultdict(set)
        self.__possible_neighbor_dict__ = defaultdict(set)

        for value in self.__events__.values():
            assert isinstance(value, Event)
            main_value, item_value = getattr(value, self.__main_tag__), getattr(value, self.__item_tag__)
            if isinstance(item_value, str):
                self.vec_data.add(main_value, item_value, getattr(value, self.__item_vector_value_tag__))
                main2item[main_value].add(item_value)
                item2main[item_value].add(main_value)
            else:
                raise NotImplementedError

        self.vec_data = self.vec_data.finish(with_length=len(self.__events__.collect_attr_set(self.__item_tag__)))
        for m_tag, m_value in main2item.items():
            for i_tag in m_value:
                self.__possible_neighbor_dict__[m_tag].update(item2main[i_tag])

    def run(self, fixed_size: int = None, limited_size: int = None, max_recommend_list: int = 100):
        from tqdm import tqdm
        self.__logger__.debug_running('running CollaborativeFiltering')

        self.__logger__.debug_running('collecting neighbors')
        self.__collect_vec_data__()

        self.__logger__.debug_running('collecting neighbors')

        simi_result = RecoResult()
        if self.__neighbor_type__ == CF_NeighborType.All:
            for u_i in tqdm(list(self.vec_data.keys()), desc='collect neighbors'):
                simi_result.add_list(u_i, self.__find_all_neighbors__(u_i, self.__similarity_type__))

        elif self.__neighbor_type__ == CF_NeighborType.FixSize:
            if fixed_size is None:
                from utils.Exceptions import ParamMissingError
                raise ParamMissingError('fixed_size')

            if fixed_size > 0:
                for u_i in tqdm(list(self.vec_data.keys()), desc='collect neighbors'):
                    simi_result.add_list(u_i, self.__find_k_neighbors__(u_i, fixed_size, self.__similarity_type__))
            else:
                from utils.Exceptions import ParamOutOfRangeError
                raise ParamOutOfRangeError('fixed_size', (1, 'inf'), fixed_size)

        elif self.__neighbor_type__ == CF_NeighborType.ThresholdBased:
            if limited_size is None:
                from utils.Exceptions import ParamMissingError
                raise ParamMissingError('limited_size')

            if limited_size > 0:
                for u_i in tqdm(list(self.vec_data.keys()), desc='collect neighbors'):
                    simi_result.add_list(u_i, self.__find_limited_neighbors__(
                        u_i, limited_size, self.__similarity_type__))
            else:
                from utils.Exceptions import ParamOutOfRangeError
                raise ParamOutOfRangeError('limited_size', (1, 'inf'), limited_size)
        else:
            raise RuntimeError

        self.__logger__.debug_running('collecting recommend list')

        if max_recommend_list <= 0:
            from utils.Exceptions import ParamOutOfRangeError
            raise ParamOutOfRangeError('max_recommend_list', (0, 'inf'), max_recommend_list)

        return self.__collect_neighbors__(simi_result, max_recommend_list)

    def __collect_neighbors__(self, simi_result: RecoResult, max_recommend_list: int):
        from tqdm import tqdm
        used_data = self.__events__.group_attr_set_by(self.__item_tag__, self.__main_tag__)
        reco_result = RecoResult()
        for u_i, simi_list in tqdm(simi_result.items(), desc='collect recommendation'):
            reco_list = list()
            main_set = used_data[u_i]
            for sub_i in simi_list:
                sub_set = used_data[sub_i]
                reco_set = sub_set - main_set
                for item in reco_set:
                    if len(reco_list) > max_recommend_list:
                        continue
                    if item not in reco_list:
                        reco_list.append(item)
            reco_result.add_list(u_i, reco_list)
        return reco_result

    def __calculate_neighbors__(self, ui_tag: str, sim_type):
        result = CountingDict()

        if self.__possible_neighbor_dict__ is None:
            for tag in self.vec_data.keys():
                if tag == ui_tag:
                    continue
                result.set(tag, abs(sim_type.__call__(self.vec_data[ui_tag], self.vec_data[tag])))
        else:
            possible_neighbor_set = self.__possible_neighbor_dict__[ui_tag]
            # self.__logger__.debug_variable(possible_neighbor_set)
            for tag in possible_neighbor_set:
                if tag == ui_tag:
                    continue
                result.set(tag, abs(sim_type.__call__(self.vec_data[ui_tag], self.vec_data[tag])))

        return result

    def __find_all_neighbors__(self, ui_tag: str, simi_type):
        """find all neighborhoods ordered by similarity -> list"""
        return self.__calculate_neighbors__(ui_tag, simi_type).sort(inverse=True)

    def __find_k_neighbors__(self, ui_tag: str, k_num: int, simi_type):
        assert k_num > 0
        return self.__find_all_neighbors__(ui_tag, simi_type)[:k_num]

    def __find_limited_neighbors__(self, ui_tag: str, limit: float, simi_type):
        simi = self.__calculate_neighbors__(ui_tag, simi_type).trim(lower_limit=limit)
        return simi.sort(inverse=True)


class SlippingRangeCollaborativeFiltering(CollaborativeFiltering):
    def __init__(self, events_dict, next_vec_data):
        CollaborativeFiltering.__init__(self, events_dict)
        assert isinstance(next_vec_data, DataDict)
        self.__next_event__ = next_vec_data
        self.next_vec_data = None

    def __collect_vec_data__(self):
        from collections import defaultdict
        self.vec_data, self.next_vec_data = SparseVectorCollector(), SparseVectorCollector()
        main2item, item2main = defaultdict(set), defaultdict(set)
        self.__possible_neighbor_dict__ = defaultdict(set)

        for value in self.__events__.values():
            assert isinstance(value, Event)
            main_value, item_value = getattr(value, self.__main_tag__), getattr(value, self.__item_tag__)
            if isinstance(item_value, str):
                self.vec_data.add(main_value, item_value, getattr(value, self.__item_vector_value_tag__))
                main2item[main_value].add(item_value)
                item2main[item_value].add(main_value)
            else:
                raise NotImplementedError

        for value in self.__next_event__.values():
            assert isinstance(value, Event)
            main_value, item_value = getattr(value, self.__main_tag__), getattr(value, self.__item_tag__)
            if isinstance(item_value, str):
                self.next_vec_data.add(main_value, item_value, getattr(value, self.__item_vector_value_tag__))
                main2item[main_value].add(item_value)
                item2main[item_value].add(main_value)
            else:
                raise NotImplementedError

        self.vec_data = self.vec_data.finish(with_length=len(self.__events__.collect_attr_set(self.__item_tag__)))
        self.next_vec_data = self.next_vec_data.finish(len(self.__next_event__.collect_attr_set(self.__item_tag__)))
        for m_tag, m_value in main2item.items():
            for i_tag in m_value:
                self.__possible_neighbor_dict__[m_tag].update(item2main[i_tag])

    def __calculate_neighbors__(self, ui_tag: str, sim_type):
        result = CountingDict()
        if self.next_vec_data is None:
            if self.__possible_neighbor_dict__ is None:
                for tag in self.vec_data.keys():
                    if tag == ui_tag:
                        continue
                    result.set(tag, abs(sim_type.__call__(self.vec_data[ui_tag], self.vec_data[tag])))
            else:
                for tag in self.__possible_neighbor_dict__[ui_tag]:
                    if tag == ui_tag:
                        continue
                    result.set(tag, abs(sim_type.__call__(self.vec_data[ui_tag], self.vec_data[tag])))
        else:
            if self.__possible_neighbor_dict__ is None:
                for tag in self.next_vec_data.keys():
                    if tag == ui_tag:
                        continue
                    result.set(tag, abs(sim_type.__call__(self.vec_data[ui_tag], self.next_vec_data[tag])))
            else:
                for tag in self.__possible_neighbor_dict__[ui_tag]:
                    if tag == ui_tag:
                        continue
                    if tag not in self.next_vec_data:
                        continue
                    result.set(tag, abs(sim_type.__call__(self.vec_data[ui_tag], self.next_vec_data[tag])))

        return result


class DateBackCollaborativeFiltering(CollaborativeFiltering):
    def __init__(self, events_dict, date_back_data, used_data, date_back_used_data, in_memory: bool=True):
        """

        :param events_dict: dict/ShelveWrapper/PreferenceCollector
        :param in_memory: bool
        """
        super(DateBackCollaborativeFiltering, self).__init__(events_dict, used_data, in_memory)
        self.last_vec_data = self.__clean_vector_data__(date_back_data, in_memory)
        self.last_used_data = self.__check_used_data__(date_back_used_data)

    def __calculate_neighbors__(self, ui_tag: str, sim_type):
        result = CountingDict()
        if self.__possible_neighbor_dict__ is None:
            for tag in self.last_vec_data.keys():
                if tag == ui_tag:
                    continue
                result.set(tag, abs(sim_type.__call__(self.vec_data[ui_tag], self.vec_data[tag])))
        else:
            possible_neighbor_set = self.__possible_neighbor_dict__[ui_tag]
            # self.__logger__.debug_variable(possible_neighbor_set)
            for tag in possible_neighbor_set:
                if tag == ui_tag:
                    continue
                if tag not in self.last_vec_data:
                    continue
                result.set(tag, abs(sim_type.__call__(self.vec_data[ui_tag], self.vec_data[tag])))
        return result

    def collect_recommend_list(self, simi_result: RecoResult, max_recommend_list: int=100):
        if max_recommend_list <= 0:
            from utils.Exceptions import ParamOutOfRangeError
            raise ParamOutOfRangeError('max_recommend_list', (0, 'inf'), max_recommend_list)

        self.__logger__.debug_running('collecting recommend list')

        reco_result = RecoResult()
        for u_i, simi_list in simi_result.items():
            reco_list = list()
            main_set = self.used_data[u_i]
            if u_i in self.last_used_data:
                # assert isinstance(main_set, set)
                main_set.update(self.last_used_data[u_i])
            for sub_i in simi_list:
                try:
                    sub_set = self.last_used_data[sub_i]
                except KeyError:
                    continue
                reco_set = sub_set - main_set
                for item in reco_set:
                    if len(reco_list) > max_recommend_list:
                        continue
                    if item not in reco_list:
                        reco_list.append(item)
            reco_result.add_list(u_i, reco_list)

        return reco_result


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

    def regulate(self, multiply: float=1.0, add: float=0.0):
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
