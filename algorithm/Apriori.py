# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import datetime
import os
import sys

from collections import defaultdict

from Interface import AbstractCollector
from structures import ShelveWrapper
from utils import get_logger


logger = get_logger(module_name=__file__)


# -------------------------------------------------------------------------------- #
# 关联规则就是有关联的规则，形式是这样定义的：两个不相交的非空集合X、Y，如果有X–>Y，就说X–>Y是一条关联规则。
# 支持度的定义：support(X–>Y) = |X交Y|/N=集合X与集合Y中的项在一条记录中同时出现的次数/数据记录的个数。
# 自信度的定义：confidence(X–>Y) = |X交Y|/|X| = 集合X与集合Y中的项在一条记录中同时出现的次数/集合X出现的个数 。
# -------------------------------------------------------------------------------- #


class AprioriResult(object):
    def __init__(self, min_support: float):
        self.__freq_sets__ = dict()
        self.__freq_sets_support__ = dict()
        self.__min_support__ = min_support
        self.__finished__ = None
        self.rules = dict()

    @property
    def min_support(self):
        return self.__min_support__

    @property
    def is_finished(self):
        if self.__finished__ is None:
            raise RuntimeError
        return self.__finished__

    def finish_with(self, with_value=True):
        self.__finished__ = with_value

    def add_freq_set(self, freq_level: int, freq_set: list):
        self.__freq_sets__[freq_level] = freq_set

    def add_freq_set_support(self, support: dict):
        self.__freq_sets_support__.update(support)

    def generate_rules(self, min_conf=0.0):
        if min_conf in self.rules:
            return self.rules[min_conf]
        else:
            rule_list = list()
            for x_index in range(1, len(self.__freq_sets__) + 1):
                for y_index in range(x_index + 1, len(self.__freq_sets__) + 1):
                    for suber_set in self.__freq_sets__[x_index]:
                        for hyper_set in self.__freq_sets__[y_index]:
                            if suber_set.issubset(hyper_set):
                                config = self.__freq_sets_support__[hyper_set] / self.__freq_sets_support__[suber_set]
                                if config >= min_conf:
                                    rule_list.append((set(suber_set), set(hyper_set) - set(suber_set), config))
            self.rules[min_conf] = rule_list
            return rule_list

    def show_results(self, rules_by_conf=None):
        print("\n所有候选项集的支持度信息：")
        for __item__ in self.__freq_sets_support__:
            print('\t' + str(__item__) + ':' + str(self.__freq_sets_support__[__item__]))
        if rules_by_conf is not None:
            from utils.Exceptions import ParamTypeError
            assert isinstance(rules_by_conf, float), repr(ParamTypeError('rules_by_config', 'float', rules_by_conf))
            print('\nrules:')
            for __item__ in self.generate_rules(rules_by_conf):
                print('\t' + str(__item__[0]) + ' ---> ' + str(__item__[1]) + ' , conf: ' + str(__item__[2]))

    def save_rules(self, min_conf: float, name: str, sep='|'):
        from utils.FileSupport import save_csv
        assert isinstance(sep, str)
        rules = self.generate_rules(min_conf)
        content_list = [['X', 'Y', 'confidence']]
        for i in range(len(rules)):
            content_list.append([sep.join(rules[i][0]), sep.join(rules[i][1]), str(rules[i][2])])
        save_csv(
            content_list,
            'results', 'Apriori rules {} - min_support {} min_config {} at {}'.format(
                name, self.min_support, min_conf, datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')
            ))


class Apriori(object):
    def __init__(self, data_sets, **kwargs):
        """

        :param data_sets: sets in list/Plist
        :param float min_support:
        :param kwargs: depth int, temp_path str
        """
        from modules.DataProxy import DataConfig

        if isinstance(data_sets, BasketCollector):
            data_sets = data_sets.to_list()

        if not len(data_sets) > 0:
            from utils.Exceptions import ParamNoContentError
            raise ParamNoContentError('data_sets')

        self.__in_memory__ = kwargs.get('in_memory', True)  # tag whether record goods in memory
        self.__origin_db__ = False  # tag whether input data_sets is db

        # pre operation
        if self.__in_memory__ is True:
            if isinstance(data_sets, list):
                self.data_sets = [set(var) for var in data_sets.copy()]
            elif isinstance(data_sets, (dict, ShelveWrapper)):
                self.data_sets = [set(var) for var in data_sets.values()]
            else:
                from utils.Exceptions import ParamTypeError
                raise ParamTypeError('data_sets', 'list/Plist/dict/Pdict/ShelveWrapper', data_sets)
        else:
            local_path = os.path.join(
                DataConfig.operation_path,
                '__aprioi_temp_{}__'.format(datetime.datetime.now().strftime('%Y%m%d %H%M%S.%f'))
            )
            if isinstance(data_sets, list):
                self.data_sets = ShelveWrapper.init_from(
                    dict(zip([str(i) for i in range(len(data_sets))], [set(var) for var in data_sets])),
                    local_path, writeback=False
                )
            elif isinstance(data_sets, dict):
                self.data_sets = ShelveWrapper.init_from(
                    dict(zip([str(i) for i in range(len(data_sets))], [set(var) for var in data_sets.values()])),
                    local_path, writeback=False)
            elif isinstance(data_sets, ShelveWrapper):
                self.data_sets = data_sets
                self.__origin_db__ = True
            else:
                from utils.Exceptions import ParamTypeError
                raise ParamTypeError('data_sets', 'list/Plist/dict/Pdict/ShelveWrapper', data_sets)

        self.depth = min(max(len(var) for var in self.data_sets), kwargs.get('depth', sys.maxsize))

    def run(self, min_support: float):
        # setting parameters
        this_result = AprioriResult(min_support)
        # starting apriori
        freq_set_level = 1

        # 基本频繁项数据
        freq_sets_k, freq_sets_support = self.find_primary_freq_goods(this_result)  # collecting frequent set
        this_result.add_freq_set(freq_set_level, freq_sets_k)
        this_result.add_freq_set_support(freq_sets_support)

        # 频繁项超集数据
        while freq_set_level <= self.depth and len(freq_sets_k) > 0:
            freq_set_level += 1
            logger.debug_running('running at frequent set level {}'.format(freq_set_level), 'begin')
            freq_sets_k = self.generate_super_frequent_sets(freq_sets_k)
            freq_sets_k, freq_sets_support = self.collect_freq_support(freq_sets_k, this_result)
            this_result.add_freq_set(freq_set_level, freq_sets_k)
            this_result.add_freq_set_support(freq_sets_support)

        # tag whether the process stops when there is no super frequent sets
        if len(freq_sets_k) > 0:
            this_result.finish_with(False)
        else:
            this_result.finish_with(True)

        return this_result

    @classmethod
    def run_once(cls):
        pass

    def find_primary_freq_goods(self, result: AprioriResult):
        """ frozensets in list, support of frozenset in dict """
        logger.debug_running('finding_primary_goods', 'begin')

        # 收集频繁度数据
        basic_freq = defaultdict(int)
        if self.__in_memory__ is True:
            assert isinstance(self.data_sets, list)
            for transaction_index in range(len(self.data_sets)):
                for item in self.data_sets[transaction_index]:
                    basic_freq[frozenset([item])] += 1
        else:
            assert isinstance(self.data_sets, ShelveWrapper)
            for goods_set in self.data_sets.values():
                for item in goods_set:
                    basic_freq[frozenset([item])] += 1

        # 排除非频繁项
        ret_list = list()
        support_dict = dict()
        for item in basic_freq:
            print(type(self.data_sets), self.data_sets.__len__())
            support = basic_freq[item] / len(self.data_sets)
            if support >= result.min_support:
                ret_list.append(item)
                support_dict[item] = support
        ret_list.sort()

        logger.debug_running('finding_primary_goods', 'end')

        return ret_list, support_dict

    def collect_freq_support(self, freq_sets: list, result: AprioriResult):
        """ frozensets in list, support of frozenset in dict """
        logger.debug_running('collect_freq_support', 'begin')

        # 收集频繁度数据
        freq_count = defaultdict(int)

        if self.__in_memory__ is True:
            assert isinstance(self.data_sets, list)
            for can in freq_sets:   # 对于每一个候选项集can，检查是否是transaction的一部分
                for index in range(len(self.data_sets)):  # 对于每一条transaction
                    if can.issubset(self.data_sets[index]):
                        freq_count[can] += 1
        else:
            assert isinstance(self.data_sets, ShelveWrapper)
            for can in freq_sets:
                for goods_set in self.data_sets.values():
                    if can.issubset(goods_set):
                        freq_count[can] += 1

        ret_list = list()
        support_dict = dict()
        for can in freq_sets:
            support = freq_count[can] / len(self.data_sets)  # 每个项集的支持度
            if support >= result.min_support:  # 将满足最小支持度的项集，加入retList
                ret_list.append(can)
                support_dict[can] = support  # 汇总支持度数据

        logger.debug_running('collect_freq_support', 'end')
        return ret_list, support_dict

    def generate_super_frequent_sets(self, old_freq_sets: list):
        num_of_freq_sets = len(old_freq_sets)

        if num_of_freq_sets >= 2:
            ret_list = list()
            old_level = len(old_freq_sets[0])
            for i in range(num_of_freq_sets):
                left = list(old_freq_sets[i])
                left.sort()
                left = left[:old_level - 1]
                for j in range(i + 1, num_of_freq_sets):
                    right = list(old_freq_sets[j])
                    right.sort()
                    right = right[:old_level - 1]
                    if left == right:
                        ret_list.append(old_freq_sets[i] | old_freq_sets[j])
            return ret_list
        else:
            return list()

    def delete_data_set(self):
        if self.__in_memory__ is True:
            assert isinstance(self.data_sets, list)
            self.data_sets.clear()
        else:
            assert isinstance(self.data_sets, ShelveWrapper)
            if self.__origin_db__ is False:
                self.data_sets.delete()


class BasketCollector(AbstractCollector):
    def __init__(self, in_memory=True):
        if in_memory is True:
            self.data = dict()
        else:
            self.data = ShelveWrapper.get_temp()

    def add(self, customer: str, good):
        if customer not in self.data:
            self.data[customer] = set()
        stored_set = self.data[customer]
        stored_set.add(good)
        self.data[customer] = stored_set

    def to_list(self):
        return [set(self.data[var]) for var in self.data.keys()]

    def to_dict(self):
        if isinstance(self.data, ShelveWrapper):
            return self.data.to_dict()
        else:
            return self.data

    def delete(self):
        if isinstance(self.data, ShelveWrapper):
            self.data.delete()
        del self.data


def collect_baskets(events_bag, book_tag: str):
    from collections import Iterable, Mapping
    from modules.DataProxy import DataProxy
    from modules.DataProxy import Book
    from structures.Event import Event

    logger.debug_running('collect_baskets', 'start')

    books = DataProxy().books

    new_basket = BasketCollector()
    if isinstance(events_bag, Iterable):
        for event in events_bag:
            assert isinstance(event, Event)
            book = books[event.book_id]
            assert isinstance(book, Book)
            new_basket.add(event.reader_id, getattr(book, book_tag))
    elif isinstance(events_bag, Mapping):
        for event in events_bag.values():
            book = books[event.book_id]
            new_basket.add(event.reader_id, getattr(book, book_tag))
    else:
        from utils.Exceptions import ParamTypeError
        raise ParamTypeError('events_bag', '', events_bag)

    logger.debug_running('collect_baskets', 'end')

    return new_basket


if __name__ == '__main__':
    logger.initiate_time_counter()

    # Test Apriori
    my_dat = [[1, 3, 4, 5],
              [2, 3, 5],
              [1, 2, 3, 4, 5],
              [2, 3, 4, 5]
              ]
    apri_1 = Apriori(my_dat, in_memory=False)
    result1 = apri_1.run(0.2)
    result1.show_results(0.1)
    apri_1.delete_data_set()

    logger.print_time_passed()
