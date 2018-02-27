# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import sys
import time

from ServiceComponents import SupervisionInfo


# --------------------------------------------------------
class Apriori(object):
    # 关联规则就是有关联的规则，形式是这样定义的：两个不相交的非空集合X、Y，如果有X–>Y，就说X–>Y是一条关联规则。
    # 支持度的定义：support(X–>Y) = |X交Y|/N=集合X与集合Y中的项在一条记录中同时出现的次数/数据记录的个数。
    # 自信度的定义：confidence(X–>Y) = |X交Y|/|X| = 集合X与集合Y中的项在一条记录中同时出现的次数/集合X出现的个数 。
    def __init__(self,
                 data_sets: list,
                 min_support=0.5,
                 depth=sys.maxsize):
        self.min_support = min_support  # setting parameters
        # self.min_confidence = min_confidence
        self.depth = min(max(len(var) for var in data_sets), depth)
        # self.interation_round = 1
        transaction_sets = [set(var) for var in data_sets]
        self.freq_set_level = 1  # starting apriori
        self.start_time = time.time()
        self.frequent_sets = {}
        self.frequent_sets_support = {}
        freq_sets_k = self.__find_primary_goods__(transaction_sets)         # collecting frequent set
        freq_sets_k, freq_sets_support = self.__collect_freq_support__(freq_sets_k, transaction_sets)
        self.frequent_sets[str(self.freq_set_level)] = freq_sets_k
        self.frequent_sets_support.update(freq_sets_support)
        while self.freq_set_level <= self.depth and len(freq_sets_k) > 0:
            self.freq_set_level += 1
            freq_sets_k = self.generate_super_frequent_sets(freq_sets_k)
            freq_sets_k, freq_sets_support = self.__collect_freq_support__(freq_sets_k, transaction_sets)
            self.frequent_sets[str(self.freq_set_level)] = freq_sets_k
            self.frequent_sets_support.update(freq_sets_support)
        # tag whether the process stops when there is no super frequent sets
        if len(freq_sets_k) > 0:
            self.is_finished = False
        else:
            self.is_finished = True
        SupervisionInfo.print_runningtime(time.time() - self.start_time, end_line='\n', refresh=True, following=False)

    def __find_primary_goods__(self, datasets: list):
        print('\rApriori: running at frequent set size {0:d} finding primary goods'.format(
            self.freq_set_level), end='\t')
        SupervisionInfo.print_runningtime(time.time() - self.start_time, end_line='', refresh=False)
        l1 = []
        for transaction_index in range(len(datasets)):
            transaction = datasets[transaction_index]
            for __item__ in transaction:
                if [__item__] not in l1:
                    l1.append([__item__])
        l1.sort()
        return [frozenset(var) for var in l1]

    def __collect_freq_support__(self, freq_sets, datasets: list):
        freq_set_count = {}
        num_of_items = float(len(datasets))
        print('\rApriori: running at frequent set size {0:d} collecting freq support'.format(
            self.freq_set_level), end='\t')
        SupervisionInfo.print_runningtime(time.time() - self.start_time, end_line='', refresh=False)
        for baskets_index in range(len(datasets)):  # 对于每一条transaction
            baskets = datasets[baskets_index]
            for can in freq_sets:  # 对于每一个候选项集can，检查是否是transaction的一部分 # 即该候选can是否得到transaction的支持
                if can.issubset(baskets):
                    freq_set_count[can] = freq_set_count.get(can, 0) + 1
        ret_list = []
        support_dict = {}
        for key in freq_set_count:
            support = freq_set_count[key] / num_of_items  # 每个项集的支持度
            if support >= self.min_support:  # 将满足最小支持度的项集，加入retList
                ret_list.append(key)
            support_dict[key] = support  # 汇总支持度数据
        return ret_list, support_dict

    def generate_super_frequent_sets(self, old_freq_sets):
        ret_list = []
        num_of_freq_sets = len(old_freq_sets)
        if num_of_freq_sets >= 2:
            old_level = len(old_freq_sets[0])
            print('\rApriori: running at frequent set size {0:d} generating super sets'.format(
                self.freq_set_level), end='\t')
            SupervisionInfo.print_runningtime(time.time() - self.start_time, end_line='', refresh=False)
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
            return []

    def __rules_from_conseq__(self, freq_set, hyper_set, rule_list, min_conf):
        m = len(hyper_set[0])
        if len(freq_set) > m + 1:  # 查看频繁项集是否足够大，以到于移除大小为 m的子集，否则继续生成m+1大小的频繁项集
            super_hyper_set = self.generate_super_frequent_sets(hyper_set)
            super_hyper_set = self.__check_config__(freq_set, super_hyper_set, rule_list, min_conf)
            # 对于新生成的m+1大小的频繁项集，计算新生成的关联规则的右则的集合
            if len(super_hyper_set) > 1:  # 如果不止一条规则满足要求（新生成的关联规则的右则的集合的大小大于1），进一步递归合并，
                # 这样做的结果就是会有“[1|多]->多”(右边只会是“多”，因为合并的本质是频繁子项集变大，
                # 而calcConf函数的关联结果的右侧就是频繁子项集）的关联结果
                self.__rules_from_conseq__(freq_set, super_hyper_set, rule_list, min_conf)

    def __check_config__(self, freq_set, hyper_set, brl, min_conf):  # 规则生成与评价
        pruned_h = []
        for conseq in hyper_set:
            conf = self.frequent_sets_support[freq_set] / self.frequent_sets_support[freq_set - conseq]
            if conf >= min_conf:
                brl.append((freq_set - conseq, conseq, conf))
                pruned_h.append(conseq)
        return pruned_h

    def generate_rules(self, min_conf=0.0):
        rule_list = []
        for i in range(1, len(self.frequent_sets)):
            for freq_set in self.frequent_sets[str(i + 1)]:  # 对于每一个频繁项集的集合
                hyper_set = [frozenset([__item__]) for __item__ in freq_set]
                if i > 1:  # 如果频繁项集中的元素个数大于2，需要进一步合并，这样做的结果就是会有“[1|多]->多”(右边只会是“多”，
                    # 因为合并的本质是频繁子项集变大，而calcConf函数的关联结果的右侧就是频繁子项集），的关联结果
                    self.__rules_from_conseq__(freq_set, hyper_set, rule_list, min_conf)
                else:
                    self.__check_config__(freq_set, hyper_set, rule_list, min_conf)
        for index in range(len(rule_list)):
            temp = (list(rule_list[index][0]),
                    list(rule_list[index][1]),
                    rule_list[index][2]
                    )
            rule_list[index] = temp
        return rule_list

    def show_results(self):
        print("\n所有候选项集的支持度信息：")
        for __item__ in self.frequent_sets_support:
            print('\t' + str(__item__) + ':' + str(self.frequent_sets_support[__item__]))
        # print('\nrules:')
        # for __item__ in self.rules:
        #     print('\t' + str(__item__[0]) + ' ---> ' + str(__item__[1]) + ' , conf: ' + str(__item__[2]))


# --------------------------------------------------------
# class CollaborativeFiltering(object):
#     def __init__(self, dict_person_book, dict_book_person):
#         self.person_book = load_data(dict_person_book)
#         self.book_person = load_data(dict_book_person)
#
#     def reader_based_simple_filtering(self, reader_id, expect_book_amount):
#         __recommend__ = set()
#         __book_borrowed__ = set(self.person_book[reader_id])
#         __similar_people__ = \
#             self.__double_check_list__(reader_id,
#                                        self.person_book,
#                                        self.book_person)
#         __similar_people__ = \
#             self.__sort_list_by_appearance_time__(
#                 __similar_people__,
#                 self.__derive_appearance_times_in_dict_from_list__(__similar_people__)
#             )
#         while len(__similar_people__) > 0 and len(__recommend__) < expect_book_amount:
#             __temp__ = set(self.person_book[__similar_people__[-1]])
#             if __temp__.issubset(__book_borrowed__):
#                 pass
#             else:
#                 __possible_book_list__ = list(__temp__ - __book_borrowed__)
#                 for __book__ in __possible_book_list__:
#                     __recommend__.add(__book__)
#                     if len(__recommend__) >= expect_book_amount:
#                         break
#             __similar_people__.pop()
#         return __recommend__
#
#     def __triple_check_listinlist__(self, tag, dict_1, dict_2):
#         __one_dicted_list__ = dict_1[tag]
#         __two_dicted_list__ = list()
#         __three_dicted_list__ = list()
#         for __item__ in __one_dicted_list__:
#             __two_dicted_list__.extend(dict_2[__item__])
#         del __one_dicted_list__
#         __two_dicted_list__ = list(set(__two_dicted_list__))
#         while tag in __two_dicted_list__:
#             __two_dicted_list__.remove(tag)
#         for __item__ in __two_dicted_list__:
#             __three_dicted_list__.append(dict_1[__item__])
#         del __two_dicted_list__
#         return __three_dicted_list__
#
#     def __double_check_list__(self, tag, dict1, dict2):
#         __one_dicted_list__ = dict1[tag]
#         __two_dicted_list__ = list()
#         for __item__ in __one_dicted_list__:
#             __two_dicted_list__.extend(dict2[__item__])
#         while tag in __two_dicted_list__:
#             __two_dicted_list__.remove(tag)
#         return __two_dicted_list__
#
#     def __derive_appearance_times_in_dict_from_list__(self, batch):
#         count = dict()
#         for __item__ in batch:
#             if __item__ not in count:
#                 count[__item__] = 1
#             else:
#                 count[__item__] += 1
#         return count
#
#     def __sort_list_by_appearance_time__(self, original_list, count_dict):
#         """from smallest to largest"""
#         # To improve this sorting in the future
#         new_list = list()
#         candidates = set(original_list)
#         for __i__ in range(len(original_list)):
#             for __can__ in count_dict:
#                 if count_dict[__can__] == __i__ + 1:
#                     new_list.append(__can__)
#                     candidates.remove(__can__)
#         return new_list
#
#     def book_based_simple_filtering(self, item_id, expected_book_number):
#         __recommend__ = set()
#         __similar_book__ = self.__double_check_list__(item_id,
#                                                       self.book_person,
#                                                       self.person_book)
#         __similar_book__ = \
#             self.__sort_list_by_appearance_time__(
#                 __similar_book__,
#                 self.__derive_appearance_times_in_dict_from_list__(__similar_book__)
#             )
#         while len(__similar_book__) > 0 and len(__recommend__) < expected_book_number:
#             __recommend__.add(__similar_book__[-1])
#             __similar_book__.pop()
#         return __recommend__


if __name__ == '__main__':
    # ------------------------------
    # Test Apriori
    my_dat = [[1, 3, 4, 5],
              [2, 3, 5],
              [1, 2, 3, 4, 5],
              [2, 3, 4, 5]
              ]
    result1 = Apriori(my_dat, min_support=0.5, depth=2)
    result1.show_results()
    # ------------------------------
    # Test CF
    # ------------------------------
