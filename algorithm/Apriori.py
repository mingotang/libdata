# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging
import sys
import datetime

from collections import defaultdict

from Interface import AbstractCollector
from utils.Logger import LogInfo
from utils.Exceptions import ParamNoContentError, ParamTypeError
from utils.Persisit import Pdict, Plist

__i__ = logging.debug


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
        self.__rules__ = dict()

    @property
    def min_support(self):
        return self.__min_support__

    @property
    def is_finished(self):
        if self.__finished__ is None:
            raise RuntimeError
        return self.__finished__

    def finish(self, with_value=True):
        self.__finished__ = with_value

    def add_freq_set(self, freq_level: int, freq_set: list):
        self.__freq_sets__[freq_level] = freq_set

    def add_freq_set_support(self, support: dict):
        self.__freq_sets_support__.update(support)

    def generate_rules(self, min_conf=0.0):
        if min_conf in self.__rules__:
            return self.__rules__[min_conf]
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
            self.__rules__[min_conf] = rule_list
            return rule_list

    def show_results(self, rules_by_conf=None):
        print("\n所有候选项集的支持度信息：")
        for __item__ in self.__freq_sets_support__:
            print('\t' + str(__item__) + ':' + str(self.__freq_sets_support__[__item__]))
        if rules_by_conf is not None:
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
            )
        )


class Apriori(object):
    def __init__(self, data_sets, **kwargs):
        """

        :param data_sets: sets in list/Plist
        :param float min_support:
        :param kwargs: depth int, temp_path str
        """
        if isinstance(data_sets, BasketCollector):
            data_sets = data_sets.to_list()

        assert isinstance(data_sets, (list, Plist)), str(ParamTypeError('data_sets', 'list/Plist', data_sets))
        assert len(data_sets) > 0, repr(ParamNoContentError('data_sets'))

        # pre operation
        if isinstance(data_sets, Plist) and isinstance(data_sets[0], (set, frozenset)):
            self.data_sets = data_sets
        elif kwargs.get('force_origin', False) is True:
            self.data_sets = [set(var) for var in data_sets]
        else:
            self.data_sets = Plist(kwargs.get('temp_path', None))
            for var in data_sets:
                self.data_sets.append(set(var))
            del data_sets
        self.depth = min(max(len(var) for var in self.data_sets), kwargs.get('depth', sys.maxsize))

    def run(self, min_support: float):
        # setting parameters
        this_result = AprioriResult(min_support)

        freq_set_level = 1  # starting apriori

        # 基本频繁项数据
        freq_sets_k, freq_sets_support = self.find_primary_freq_goods(this_result)  # collecting frequent set
        this_result.add_freq_set(freq_set_level, freq_sets_k)
        this_result.add_freq_set_support(freq_sets_support)

        # 频繁项超集数据
        while freq_set_level <= self.depth and len(freq_sets_k) > 0:
            freq_set_level += 1
            __i__(LogInfo.running('running at frequent set level {}'.format(freq_set_level), 'begin'))
            freq_sets_k = self.generate_super_frequent_sets(freq_sets_k)
            freq_sets_k, freq_sets_support = self.collect_freq_support(freq_sets_k, this_result)
            this_result.add_freq_set(freq_set_level, freq_sets_k)
            this_result.add_freq_set_support(freq_sets_support)

        # tag whether the process stops when there is no super frequent sets
        if len(freq_sets_k) > 0:
            this_result.finish(False)
        else:
            this_result.finish(True)

        return this_result

    @classmethod
    def run_once(cls):
        pass

    def find_primary_freq_goods(self, result: AprioriResult):
        """ frozensets in list, support of frozenset in dict """
        __i__(LogInfo.running('finding_primary_goods', 'begin'))

        # 收集频繁度数据
        basic_freq = defaultdict(int)
        for transaction_index in range(len(self.data_sets)):
            for item in self.data_sets[transaction_index]:
                basic_freq[frozenset([item])] += 1

        # 排除非频繁项
        ret_list = list()
        support_dict = dict()
        for item in basic_freq:
            support = basic_freq[item] / len(self.data_sets)
            if support >= result.min_support:
                ret_list.append(item)
                support_dict[item] = support
        ret_list.sort()

        __i__(LogInfo.running('finding_primary_goods', 'end'))

        return ret_list, support_dict

    def collect_freq_support(self, freq_sets: list, result: AprioriResult):
        """ frozensets in list, support of frozenset in dict """
        __i__(LogInfo.running('collect_freq_support', 'begin'))

        # 收集频繁度数据
        freq_count = defaultdict(int)
        for can in freq_sets:  # 对于每一个候选项集can，检查是否是transaction的一部分
            for index in range(len(self.data_sets)):  # 对于每一条transaction
                if can.issubset(self.data_sets[index]):
                    freq_count[can] += 1

        ret_list = list()
        support_dict = dict()
        for can in freq_sets:
            support = freq_count[can] / len(self.data_sets)  # 每个项集的支持度
            if support >= result.min_support:  # 将满足最小支持度的项集，加入retList
                ret_list.append(can)
                support_dict[can] = support  # 汇总支持度数据
        __i__(LogInfo.running('collect_freq_support', 'end'))
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

    # def __rules_from_conseq__(self, freq_set: frozenset, hyper_set: list, rule_list, min_conf: float):
    #     """ generate_rules __rules_from_conseq__ """
    #     m = len(hyper_set[0])
    #     if len(freq_set) > m + 1:  # 查看频繁项集是否足够大，以到于移除大小为 m的子集，否则继续生成m+1大小的频繁项集
    #         super_hyper_set = self.generate_super_frequent_sets(hyper_set)
    #         super_hyper_set = self.__check_config__(freq_set, super_hyper_set, rule_list, min_conf)
    #         # 对于新生成的m+1大小的频繁项集，计算新生成的关联规则的右则的集合
    #         if len(super_hyper_set) > 1:  # 如果不止一条规则满足要求（新生成的关联规则的右则的集合的大小大于1），进一步递归合并，
    #             # 这样做的结果就是会有“[1|多]->多”(右边只会是“多”，因为合并的本质是频繁子项集变大，
    #             # 而calcConf函数的关联结果的右侧就是频繁子项集）的关联结果
    #             self.__rules_from_conseq__(freq_set, super_hyper_set, rule_list, min_conf)
    #
    # def __check_config__(self, freq_set: frozenset, hyper_set: list, brl, min_conf: float):
    #     """ generate_rules __check_config__ 规则生成与评价"""
    #     pruned_h = list()
    #     for conseq in hyper_set:
    #         conf = self.freq_sets_support[freq_set] / self.freq_sets_support[freq_set - conseq]
    #         if conf >= min_conf:
    #             brl.append((freq_set - conseq, conseq, conf))
    #             pruned_h.append(conseq)
    #     return pruned_h

    # def generate_rules(self, min_conf=0.0):
    #     rule_list = list()
    #
    #     for i in range(1, len(self.freq_sets)):
    #         for freq_set in self.freq_sets[i+1]:  # 对于每一个频繁项集的集合
    #             hyper_set = [frozenset([var]) for var in freq_set]
    #             if i > 1:  # 如果频繁项集中的元素个数大于2，需要进一步合并，这样做的结果就是会有“[1|多]->多”(右边只会是“多”，
    #                 # 因为合并的本质是频繁子项集变大，而calcConf函数的关联结果的右侧就是频繁子项集），的关联结果
    #                 self.__rules_from_conseq__(freq_set, hyper_set, rule_list, min_conf)
    #             else:
    #                 self.__check_config__(freq_set, hyper_set, rule_list, min_conf)
    #
    #     # convert frozenset in rule_list to set
    #     for index in range(len(rule_list)):
    #         temp = (set(rule_list[index][0]),
    #                 set(rule_list[index][1]),
    #                 rule_list[index][2])
    #         rule_list[index] = temp
    #     return rule_list


class BasketCollector(AbstractCollector):
    def __init__(self, *args):
        if len(args) == 0:
            self.data = dict()
        else:
            assert len(args) == 1
            assert isinstance(args[0], str)
            self.data = Pdict(args[0])

    def add(self, customer: str, good):
        if customer not in self.data:
            self.data[customer] = set()
        stored_set = self.data[customer]
        stored_set.add(good)
        self.data[customer] = stored_set

    def to_list(self):
        return [set(self.data[var]) for var in self.data.keys()]

    def to_plist(self, *args):
        assert len(args) == 1, 'to_plist takes one and only one param data_path'
        return Plist.init_from(self.to_list(), args[0])

    def to_dict(self):
        if isinstance(self.data, Pdict):
            return self.data.copy()
        else:
            return self.data


if __name__ == '__main__':
    # ------------------------------
    from utils.Logger import set_logging, RunTimeCounter
    set_logging()
    import time
    RunTimeCounter.get_instance()
    time.sleep(3)
    # Test Apriori
    my_dat = [[1, 3, 4, 5],
              [2, 3, 5],
              [1, 2, 3, 4, 5],
              [2, 3, 4, 5]
              ]
    apri_1 = Apriori(my_dat, force_origin=True)
    result1 = apri_1.run(0.2)
    result1.show_results(0.1)
    __i__(LogInfo.time_passed())
