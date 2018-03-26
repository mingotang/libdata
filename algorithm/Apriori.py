# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging
import sys

from collections import defaultdict

from utils.Logger import LogInfo
from utils.Exceptions import ParamNoContentError, ParamTypeError
from utils.Persisit import Pdict, Plist

# -------------------------------------------------------------------------------- #
# 关联规则就是有关联的规则，形式是这样定义的：两个不相交的非空集合X、Y，如果有X–>Y，就说X–>Y是一条关联规则。
# 支持度的定义：support(X–>Y) = |X交Y|/N=集合X与集合Y中的项在一条记录中同时出现的次数/数据记录的个数。
# 自信度的定义：confidence(X–>Y) = |X交Y|/|X| = 集合X与集合Y中的项在一条记录中同时出现的次数/集合X出现的个数 。
# -------------------------------------------------------------------------------- #


class Apriori(object):
    def __init__(self, data_sets, min_support=0.5, depth=sys.maxsize, temp_path=None):
        """

        :param data_sets: sets in list/Plist
        :param float min_support:
        :param int depth:
        :param temp_path:
        """
        assert isinstance(data_sets, (list, Plist)), str(
            ParamTypeError('data_sets', 'list/Plist', data_sets)
        )
        # setting parameters
        self.min_support = min_support
        self.depth = min(max(len(var) for var in data_sets), depth)
        self.data_length = len(data_sets)

        freq_set_level = 1  # starting apriori
        self.freq_sets = dict()
        self.freq_sets_support = dict()

        # pre operation
        assert len(data_sets) > 0, repr(ParamNoContentError('data_sets'))

        if isinstance(data_sets[0], (set, frozenset)):
            transaction_sets = data_sets
        else:
            if temp_path is None:
                transaction_sets = [set(var) for var in data_sets]
            elif isinstance(temp_path, str):
                transaction_sets = Plist(temp_path)
                for var in data_sets:
                    transaction_sets.append(set(var))
            else:
                raise ParamTypeError('temp_path', 'str', temp_path)

        # 基本频繁项数据
        freq_sets_k, freq_sets_support = self.find_primary_freq_goods(transaction_sets)     # collecting frequent set
        self.freq_sets[freq_set_level] = freq_sets_k
        self.freq_sets_support.update(freq_sets_support)

        # 频繁项超集数据
        while freq_set_level <= self.depth and len(freq_sets_k) > 0:
            freq_set_level += 1
            logging.debug(LogInfo.running('running at frequent set level {}'.format(freq_set_level), 'begin'))
            freq_sets_k = self.generate_super_frequent_sets(freq_sets_k)
            freq_sets_k, freq_sets_support = self.collect_freq_support(freq_sets_k, transaction_sets)
            self.freq_sets[freq_set_level] = freq_sets_k
            self.freq_sets_support.update(freq_sets_support)

        # tag whether the process stops when there is no super frequent sets
        if len(freq_sets_k) > 0:
            self.__finished__ = False
        else:
            self.__finished__ = True

    @property
    def is_finished(self):
        return self.__finished__

    def find_primary_freq_goods(self, datasets: list):
        """ frozensets in list, support of frozenset in dict """
        logging.debug(LogInfo.running('finding_primary_goods', 'begin'))

        # 收集频繁度数据
        basic_freq = defaultdict(int)
        for transaction_index in range(len(datasets)):
            for item in datasets[transaction_index]:
                basic_freq[frozenset([item])] += 1

        # 排除非频繁项
        ret_list = list()
        support_dict = dict()
        for item in basic_freq:
            support = basic_freq[item] / self.data_length
            if support >= self.min_support:
                ret_list.append(item)
                support_dict[item] = support
        ret_list.sort()
        logging.debug(LogInfo.running('finding_primary_goods', 'end'))
        return ret_list, support_dict

    def collect_freq_support(self, freq_sets: list, datasets: list):
        """ frozensets in list, support of frozenset in dict """
        logging.debug(LogInfo.running('collect_freq_support', 'begin'))

        # 收集频繁度数据
        freq_count = defaultdict(int)
        for can in freq_sets:  # 对于每一个候选项集can，检查是否是transaction的一部分
            for index in range(len(datasets)):  # 对于每一条transaction
                if can.issubset(datasets[index]):
                    freq_count[can] += 1

        ret_list = list()
        support_dict = dict()
        for can in freq_sets:
            support = freq_count[can] / self.data_length  # 每个项集的支持度
            if support >= self.min_support:  # 将满足最小支持度的项集，加入retList
                ret_list.append(can)
                support_dict[can] = support  # 汇总支持度数据
        logging.debug(LogInfo.running('collect_freq_support', 'end'))
        return ret_list, support_dict

    def generate_super_frequent_sets(self, old_freq_sets):
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

    def generate_rules(self, min_conf=0.0):
        rule_list = list()

        for x_index in range(1, len(self.freq_sets)+1):
            for y_index in range(x_index + 1, len(self.freq_sets)+1):
                for suber_set in self.freq_sets[x_index]:
                    for hyper_set in self.freq_sets[y_index]:
                        if suber_set.issubset(hyper_set):
                            config = self.freq_sets_support[hyper_set] / self.freq_sets_support[suber_set]
                            if config >= min_conf:
                                rule_list.append((suber_set, hyper_set, config))
        return rule_list

    def show_results(self, rules_by_conf=None):
        print("\n所有候选项集的支持度信息：")
        for __item__ in self.freq_sets_support:
            print('\t' + str(__item__) + ':' + str(self.freq_sets_support[__item__]))
        if rules_by_conf is not None:
            assert isinstance(rules_by_conf, float), repr(ParamTypeError('rules_by_config', 'float', rules_by_conf))
            print('\nrules:')
            for __item__ in self.generate_rules(rules_by_conf):
                print('\t' + str(__item__[0]) + ' ---> ' + str(__item__[1]) + ' , conf: ' + str(__item__[2]))


class BasketCollector(object):
    def __init__(self, data_path=None):
        if data_path is not None:
            assert isinstance(data_path, str), str(ParamTypeError('data_path', 'str', data_path))
            self.data = Pdict(data_path)
        else:
            self.data = dict()

    def add(self, customer: str, good):
        if customer not in self.data:
            self.data[customer] = set()
        stored_set = self.data[customer]
        stored_set.add(good)
        self.data[customer] = stored_set

    def to_list(self, data_path=None):
        if data_path is not None:
            assert isinstance(data_path, str), str(ParamTypeError('data_path', 'str', data_path))
            this_list = Plist(data_path)
        else:
            this_list = list()
        for tag in self.data:
            this_list.append(self.data[tag])
        return this_list


if __name__ == '__main__':
    # ------------------------------
    logging.basicConfig(
        level=logging.DEBUG,  # 定义输出到文件的log级别，
        format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',  # 定义输出log的格式
        datefmt='%Y-%m-%d %A %H:%M:%S',  # 时间
    )
    # Test Apriori
    my_dat = [[1, 3, 4, 5],
              [2, 3, 5],
              [1, 2, 3, 4, 5],
              [2, 3, 4, 5]
              ]
    result1 = Apriori(my_dat, min_support=0.5, depth=2)
    result1.show_results(0.0)
