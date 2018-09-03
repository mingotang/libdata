# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


class Evaluator(object):

    def __init__(self, actual_data, predicted_data):
        from collections import Mapping
        assert isinstance(actual_data, Mapping)
        assert isinstance(predicted_data, Mapping)
        self.__actual_data__ = actual_data
        self.__predicted_data__ = predicted_data

    @property
    def match_percentage(self):
        match_count = 0

        for ac_key in self.__actual_data__.keys():
            if ac_key in self.__predicted_data__:
                match_count += 1

        return match_count / len(self.__actual_data__)

    def top_n_accuracy(self, n: int):
        """评价单个预测结果落在前n个实际结果中的比例 -> float"""
        match_count, hit_count = 0, 0.0

        for ac_key, ac_value in self.__actual_data__.items():
            assert isinstance(ac_value, list)
            if ac_key in self.__predicted_data__:
                match_count += 1
                if len(ac_value) >= n:
                    if self.__predicted_data__[ac_key] in ac_value[:n]:
                        hit_count += 1.0
                else:
                    # actual data is not enough
                    if self.__predicted_data__[ac_key] in ac_value:
                        hit_count += 1.0
            else:
                # no predicted data
                continue

        return hit_count / match_count

    def coverage_accuracy(self):
        """评价若干个预测结果可以覆盖多少比例的实际结果 -> float"""
        raise NotImplementedError
