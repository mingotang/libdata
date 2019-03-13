# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


class Evaluator(object):

    def __init__(self, actual_data, predicted_data):
        """

        :param actual_data: dict{ reader_id: list(book1, book2, ...)}
        :param predicted_data:
        """
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

    def coverage(self):
        recommend_set = set()
        data_set = set()

        for re_key, re_list in self.__predicted_data__.items():
            for tag in re_list:
                recommend_set.add(tag)
        for ac_key, ac_list in self.__actual_data__.items():
            for tag in ac_list:
                data_set.add(tag)

        return len(recommend_set) / (len(data_set) + len(recommend_set))

    def f_value(self):
        precision = self.precision_accuracy()
        recall = self.recall_accuracy()
        return 2 * precision * recall / (precision + recall)

    def recall_accuracy(self):

        match_count, hit_list = 0, list()

        for ac_key, ac_list in self.__actual_data__.items():
            assert isinstance(ac_list, list)
            if ac_key in self.__predicted_data__:
                pre_list = self.__predicted_data__[ac_key]
                match_count += 1
                assert isinstance(pre_list, list)
                if len(pre_list) == 0:
                    continue
                count = 0
                for tag in pre_list:
                    if tag in ac_list:
                        count += 1
                hit_list.append(count / len(pre_list))
            else:
                continue

        return sum(hit_list) / len(hit_list)

    def precision_accuracy(self):

        match_count, hit_list = 0, list()

        for ac_key, ac_list in self.__actual_data__.items():
            assert isinstance(ac_list, list)
            if len(ac_list) == 0:
                continue

            if ac_key in self.__predicted_data__:
                pre_list = self.__predicted_data__[ac_key]
                match_count += 1
                assert isinstance(pre_list, list)
                count = 0
                for tag in pre_list:
                    if tag in ac_list:
                        count += 1
                hit_list.append(count / len(ac_list))
            else:
                continue

        return sum(hit_list) / len(hit_list)

    def top_n_accuracy(self, n: int):
        """评价单个预测结果落在前n个实际结果中的比例 -> float"""
        if n < 1:
            from extended.Exceptions import ParamOutOfRangeError
            raise ParamOutOfRangeError('n', (1, 'inf'), n)

        match_count, hit_count = 0, 0.0

        for ac_key, ac_value in self.__actual_data__.items():
            assert isinstance(ac_value, list), str(ac_value)
            if ac_key in self.__predicted_data__:
                pre_value = self.__predicted_data__[ac_key]
                if len(pre_value) >= 1:
                    pre_value = pre_value[0]
                else:
                    pre_value = None
                assert isinstance(pre_value, (str, type(None))), pre_value
                match_count += 1
                if len(ac_value) >= n:
                    if pre_value in ac_value[:n]:
                        hit_count += 1.0
                else:
                    # actual data is not enough
                    if pre_value in ac_value:
                        hit_count += 1.0
            else:
                # no predicted data
                continue

        return hit_count / match_count

    def front_i_top_n_accuracy(self, i: int = 1, n: int = 100):
        """评价若干个预测结果可以覆盖多少比例的实际结果 -> float"""
        assert i >= 1 and n >= 1
        match_count, hit_count = 0, 0.0

        for ac_key, ac_list in self.__actual_data__.items():
            assert isinstance(ac_list, list)
            if ac_key in self.__predicted_data__:
                pre_list = self.__predicted_data__[ac_key]
                assert isinstance(pre_list, list), pre_list
                match_count += 1
                if len(ac_list) >= n:
                    ac_index = n
                else:
                    ac_index = len(ac_list)
                if len(pre_list) >= i:
                    pre_index = i
                else:
                    pre_index = len(pre_list)
                for pre_value in pre_list[:pre_index]:
                    if pre_value in ac_list[:ac_index]:
                        hit_count += 1.0
                        break
            else:
                # no predicted data
                continue

        return hit_count / match_count
