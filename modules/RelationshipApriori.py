# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import sys
# ---------------------------------------------------------------------------


class Apriori(object):
    def __init__(self, data_sets,
                 min_support=0.5,
                 min_confidence=0.5,
                 depth=sys.maxsize):
        self.min_support = min_support  # setting parameters
        self.min_confidence = min_confidence
        self.depth = min(max(len(var) for var in data_sets), depth)
        transaction_sets = [set(var) for var in data_sets]
        freq_set_level = 1  # starting apriori
        self.frequent_sets = {}
        self.frequent_sets_support = {}
        freq_sets_k = self.__find_primary_goods__(transaction_sets)         # collecting frequent set
        freq_sets_k, freq_sets_support = self.__collect_freq_support__(freq_sets_k, transaction_sets)
        self.frequent_sets[str(freq_set_level)] = freq_sets_k
        self.frequent_sets_support.update(freq_sets_support)
        while freq_set_level <= self.depth and len(freq_sets_k) > 0:
            freq_set_level += 1
            freq_sets_k = self.generate_super_frequent_sets(freq_sets_k)
            freq_sets_k, freq_sets_support = self.__collect_freq_support__(freq_sets_k, transaction_sets)
            self.frequent_sets[str(freq_set_level)] = freq_sets_k
            self.frequent_sets_support.update(freq_sets_support)
        self.rules = self.generate_rules()
        # tag whether the process stops when there is no super frequent sets
        if len(freq_sets_k) > 0:
            self.is_finished = False
        else:
            self.is_finished = True
        del transaction_sets
        del freq_sets_k
        del freq_sets_support
        del freq_set_level

    @staticmethod
    def __find_primary_goods__(datasets):
        l1 = []
        for transaction in datasets:
            for __item__ in transaction:
                if [__item__] not in l1:
                    l1.append([__item__])
        l1.sort()
        return [frozenset(var) for var in l1]

    def __collect_freq_support__(self, freq_sets, datasets):
        freq_set_count = {}
        for baskets in datasets:  # 对于每一条transaction
            for can in freq_sets:  # 对于每一个候选项集can，检查是否是transaction的一部分 # 即该候选can是否得到transaction的支持
                if can.issubset(baskets):
                    freq_set_count[can] = freq_set_count.get(can, 0) + 1
        num_of_items = float(len(datasets))
        ret_list = []
        support_dict = {}
        for key in freq_set_count:
            support = freq_set_count[key] / num_of_items  # 每个项集的支持度
            if support >= self.min_support:  # 将满足最小支持度的项集，加入retList
                ret_list.append(key)
            support_dict[key] = support  # 汇总支持度数据
        return ret_list, support_dict

    @staticmethod
    def generate_super_frequent_sets(old_freq_sets):
        ret_list = []
        num_of_freq_sets = len(old_freq_sets)
        if num_of_freq_sets >= 2:
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
            return []

    def generate_rules(self, default_min_conf=-1.0):
        min_conf = self.min_confidence if default_min_conf < 0 else float(default_min_conf)
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

    def show_results(self):
        print("\n所有候选项集的支持度信息：")
        for __item__ in self.frequent_sets_support:
            print('\t' + str(__item__) + ':' + str(self.frequent_sets_support[__item__]))
        print('\nrules:')
        for __item__ in self.rules:
            print('\t' + str(__item__[0]) + ' ---> ' + str(__item__[1]) + ' , conf: ' + str(__item__[2]))


if __name__ == '__main__':
    import time
    start_time = time.time()
    # ------------------------------
    my_dat = [[1, 3, 4, 5],
              [2, 3, 5],
              [1, 2, 3, 4, 5],
              [2, 3, 4, 5]
              ]
    result1 = Apriori(my_dat, min_support=0.5, min_confidence=0.7, depth=2)
    result1.show_results()
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration) // 3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.4f} s'.format(hour, minutes, seconds))
