# -*- encoding: UTF-8 -*-

from modules.RuleGen import RuleGenerator


class RuleGenBN(RuleGenerator):
    def __init__(self):
        RuleGenerator.__init__(self)

    def statistic(self):
        # ------------------------------------------ #
        from os import path, listdir
        from json import load as json_load
        from extended import CountingDict

        for lib_index_tag in listdir(path.join(self.env.data_path, 'sub_lib_index_class_importance_dicts')):
            lib_index_tag = lib_index_tag.split('.')[0]

            self.log.debug_running('executing {}'.format(lib_index_tag))

            source_result_dict = json_load(open(path.join(
                self.env.data_path,
                'sub_lib_index_class_importance_dicts',
                '{}.json'.format(lib_index_tag),
            ), mode='r' ))

            keyword_set = set()
            for stage_str in ['0', '1', '2']:
                keyword_source_dict = source_result_dict[stage_str]
                assert isinstance(keyword_source_dict, dict)
                keyword_set.update(keyword_source_dict.keys())

            def check_next_larger(content_list: list, strict: bool = True):
                for i in range(len(content_list)):
                    for j in range(i + 1, len(content_list)):
                        if strict is True:
                            if content_list[i] >= content_list[j]:
                                return False
                        else:
                            if content_list[i] > content_list[j]:
                                return False
                return True

            def check_next_smaller(content_list: list, strict: bool = True):
                for i in range(len(content_list)):
                    for j in range(i + 1, len(content_list)):
                        if strict is True:
                            if content_list[i] <= content_list[j]:
                                return False
                        else:
                            if content_list[i] < content_list[j]:
                                return False
                return True

            from numpy import std as np_std
            from numpy import mean as np_mean

            keyword_rank_dict = dict()
            increasing_important_dict = CountingDict()
            decreasing_important_dict = CountingDict()
            for keyword in keyword_set:
                if len(keyword) == 1:
                    continue
                index_list = list()
                # TODO: 从 0，1，2 进行
                for weight_dict in [
                    source_result_dict['0'], source_result_dict['1'], source_result_dict['2'],
                ]:
                    assert isinstance(weight_dict, dict)
                    index_list.append(weight_dict.get(keyword, 0.0))

                # for i in range(len(index_list)):
                #     index_list[i] = index_list[i] / len(keyword_set)

                keyword_rank_dict[keyword] = index_list
                # 随着发展重要程度上升
                if check_next_larger(index_list):
                    increasing_important_dict[keyword] = np_std(index_list) * np_mean(index_list)
                # 随着发展重要程度下降
                if check_next_smaller(index_list):
                    decreasing_important_dict[keyword] = np_std(index_list) * np_mean(index_list)

            from json import dump as json_dump
            # from utils import save_csv

            json_dump(
                increasing_important_dict,
                open(path.join(
                    self.env.data_path,
                    'sub_lib_index_class_increasing_importance_dicts',
                    '{}.json'.format(lib_index_tag),
                ), mode='w'))
            # csv_out = list()
            # increasing_important_list = increasing_important_dict.sort(reverse=True)
            # print(increasing_important_list)
            # for tag in increasing_important_list:
            #     line_list = list()
            #     line_list.append(tag)
            #     line_list.append(increasing_important_dict[tag])
            #     line_list.extend(keyword_rank_dict[tag])
            #     csv_out.append(line_list)
            #     print(tag, increasing_important_dict[tag], keyword_rank_dict[tag])

            json_dump(
                decreasing_important_dict,
                open(path.join(
                    self.env.data_path,
                    'sub_lib_index_class_decreasing_importance_dicts',
                    '{}.json'.format(lib_index_tag),
                ), mode='w'))

            # csv_out = list()
            # decreasing_important_list = decreasing_important_dict.sort(reverse=True)
            # print(decreasing_important_list)
            # for tag in decreasing_important_list:
            #     line_list = list()
            #     line_list.append(tag)
            #     line_list.append(decreasing_important_dict[tag])
            #     line_list.extend(keyword_rank_dict[tag])
            #     csv_out.append(line_list)
            # save_csv(csv_out, path.expanduser('~/Downloads'), 'D9_decreasing_importance.csv')

            # save_csv(csv_list, path.expanduser('~/Downloads/output.csv'))


if __name__ == '__main__':
    rg = RuleGenBN()
    rg.statistic()
