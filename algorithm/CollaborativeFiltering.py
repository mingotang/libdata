# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
from Interface import AbstractCollector
from structures import CountingDict, RecoResult, SparseVector
from structures import ShelveWrapper


class CollaborativeFiltering(object):
    """
    CF: finding neighbors
    """
    def __init__(self, vec_data, used_data, in_memory: bool=True):
        """

        :param vec_data: dict/ShelveWrapper/PreferenceCollector
        :param in_memory: bool
        """
        from utils import get_logger
        self.__logger__ = get_logger(module_name=self.__class__.__name__)

        self.used_data = self.__check_used_data__(used_data)
        self.vec_data = self.__clean_vector_data__(vec_data, in_memory)
        self.__possible_neighbor_dict__ = None

    def __check_used_data__(self, used_data):
        from utils.Exceptions import ParamTypeError
        if isinstance(used_data, dict):
            for value in used_data.values():
                if not isinstance(value, set):
                    raise ParamTypeError('value in used_data', set, value)
        else:
            raise ParamTypeError('used_data', dict, used_data)
        return used_data

    def __clean_vector_data__(self, vec_data, in_memory: bool):
        # 检查参数
        if not len(vec_data) > 0:
            from utils.Exceptions import ParamNoContentError
            raise ParamNoContentError('vec_data')

        # 运行数据是否储存在内存中
        if in_memory is True:
            if isinstance(vec_data, dict):
                data = vec_data
            elif isinstance(vec_data, ShelveWrapper):
                data = vec_data.to_dict()
            elif isinstance(vec_data, SparseVectorCollector):
                data = vec_data.to_dict()
            else:
                from utils.Exceptions import ParamTypeError
                raise ParamTypeError('vec_data', (dict, ShelveWrapper, SparseVectorCollector), vec_data)
        else:
            data = ShelveWrapper.get_temp()
            if isinstance(vec_data, (ShelveWrapper, dict)):
                data.update(vec_data)
            elif isinstance(vec_data, SparseVectorCollector):
                data.update(vec_data.to_dict())
            else:
                from utils.Exceptions import ParamTypeError
                raise ParamTypeError('vec_data', (dict, ShelveWrapper, SparseVectorCollector), vec_data)

        # 检查数据格式是否符合要求
        self.__logger__.debug_running('checking input data')
        for value in data.values():
            if not isinstance(value, (dict, SparseVector)):
                from utils.Exceptions import ValueTypeError
                raise ValueTypeError('value in vec_data', (dict, SparseVector), value)
        return data

    def __check_possible_neighbors__(self, possible_neighbors: dict=None):
        if possible_neighbors is not None:
            self.__logger__.debug_running('cf with acceleration')
            for value in possible_neighbors.values():
                if not isinstance(value, (set, list, frozenset, tuple)):
                    from utils.Exceptions import ParamTypeError
                    ParamTypeError('value in possible_neighbors', set, value)

    def delete_data(self):
        if isinstance(self.vec_data, ShelveWrapper):
            self.vec_data.delete()
        del self.vec_data
        self.__logger__.debug_running('{}.delete_data'.format(self.__class__.__name__), 'finished')

    def collect_neighbors(
            self, neighbor_type, similarity_type,
            fixed_size: int=None, limited_size: int=None,
            possible_neighbors: dict = None
    ):
        from . import CF_NeighborType
        assert isinstance(neighbor_type, CF_NeighborType)

        self.__possible_neighbor_dict__ = possible_neighbors
        self.__check_possible_neighbors__(possible_neighbors)

        self.__logger__.debug_running('collecting neighbors')
        simi_result = RecoResult()
        # self.__logger__.debug_running('executing NeighborType.{}'.format(neighbor_type.name))
        if neighbor_type == CF_NeighborType.All:
            for u_i in list(self.vec_data.keys()):
                simi_result.add_list(u_i, self.find_all_neighbors(u_i, similarity_type))

        elif neighbor_type == CF_NeighborType.FixSize:
            if fixed_size is None:
                from utils.Exceptions import ParamMissingError
                raise ParamMissingError('fixed_size')

            if fixed_size > 0:
                for u_i in list(self.vec_data.keys()):
                    simi_result.add_list(u_i, self.find_k_neighbors(u_i, fixed_size, similarity_type))
            else:
                from utils.Exceptions import ParamOutOfRangeError
                raise ParamOutOfRangeError('fixed_size', (1, 'inf'), fixed_size)

        elif neighbor_type == CF_NeighborType.ThresholdBased:
            if limited_size is None:
                from utils.Exceptions import ParamMissingError
                raise ParamMissingError('limited_size')

            if limited_size > 0:
                for u_i in list(self.vec_data.keys()):
                    simi_result.add_list(u_i, self.find_limited_neighbors(u_i, limited_size, similarity_type))
            else:
                from utils.Exceptions import ParamOutOfRangeError
                raise ParamOutOfRangeError('limited_size', (1, 'inf'), limited_size)
        else:
            raise RuntimeError
        return simi_result

    def collect_recommend_list(self, simi_result: RecoResult, max_recommend_list: int=100):
        if max_recommend_list <= 0:
            from utils.Exceptions import ParamOutOfRangeError
            raise ParamOutOfRangeError('max_recommend_list', (0, 'inf'), max_recommend_list)

        self.__logger__.debug_running('collecting recommend list')

        reco_result = RecoResult()
        for u_i, simi_list in simi_result.items():
            reco_list = list()
            main_set = self.used_data[u_i]
            for sub_i in simi_list:
                sub_set = self.used_data[sub_i]
                reco_set = sub_set - main_set
                for item in reco_set:
                    if len(reco_list) > max_recommend_list:
                        continue
                    if item not in reco_list:
                        reco_list.append(item)
            reco_result.add_list(u_i, reco_list)

        return reco_result

    def run(self, neighbor_type, similarity_type,
            fixed_size: int=None, limited_size: int=None,
            possible_neighbors: dict=None, max_recommend_list: int=100):
        simi_result = self.collect_neighbors(
            neighbor_type, similarity_type, fixed_size=fixed_size, limited_size=limited_size,
            possible_neighbors=possible_neighbors
        )

        reco_result = self.collect_recommend_list(simi_result, max_recommend_list)

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

    def find_all_neighbors(self, ui_tag: str, simi_type):
        """find all neighborhoods ordered by similarity -> list"""
        return self.__calculate_neighbors__(ui_tag, simi_type).sort(inverse=True)

    def find_k_neighbors(self, ui_tag: str, k_num: int, simi_type):
        assert k_num > 0
        return self.find_all_neighbors(ui_tag, simi_type)[:k_num]

    def find_limited_neighbors(self, ui_tag: str, limit: float, simi_type):
        simi = self.__calculate_neighbors__(ui_tag, simi_type).trim(lower_limit=limit)
        return simi.sort(inverse=True)


class SlippingRangeCollaborativeFiltering(CollaborativeFiltering):
    def __init__(self, vec_data, next_vec_data, used_data, in_memory: bool=True):
        """

        :param vec_data: dict/ShelveWrapper/PreferenceCollector
        :param in_memory: bool
        """
        super(SlippingRangeCollaborativeFiltering, self).__init__(vec_data, used_data, in_memory)
        if next_vec_data is not None:
            from utils.Exceptions import ParamNoContentError
            try:
                self.next_vec_data = self.__clean_vector_data__(next_vec_data, in_memory)
            except ParamNoContentError:
                self.next_vec_data = None
        else:
            self.next_vec_data = None

    def __calculate_neighbors__(self, ui_tag: str, sim_type):
        result = CountingDict()
        if self.next_vec_data is None:
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
        else:
            if self.__possible_neighbor_dict__ is None:
                for tag in self.next_vec_data.keys():
                    if tag == ui_tag:
                        continue
                    result.set(tag, abs(sim_type.__call__(self.vec_data[ui_tag], self.next_vec_data[tag])))
            else:
                possible_neighbor_set = self.__possible_neighbor_dict__[ui_tag]
                for tag in possible_neighbor_set:
                    if tag == ui_tag:
                        continue
                    if tag not in self.next_vec_data:
                        continue
                    result.set(tag, abs(sim_type.__call__(self.vec_data[ui_tag], self.next_vec_data[tag])))

        return result


class DateBackCollaborativeFiltering(CollaborativeFiltering):
    def __init__(self, vec_data, date_back_data, used_data, date_back_used_data, in_memory: bool=True):
        """

        :param vec_data: dict/ShelveWrapper/PreferenceCollector
        :param in_memory: bool
        """
        super(DateBackCollaborativeFiltering, self).__init__(vec_data, used_data, in_memory)
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


class SparseVectorCollector(AbstractCollector):
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
