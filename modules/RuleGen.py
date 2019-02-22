# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os
import datetime

from Interface import AbstractEnvObject


class RuleGenerator(AbstractEnvObject):
    def __init__(self):
        from utils import get_logger
        self.__logger__ = get_logger(self.__class__.__name__)

        self.__data_path__ = self.env.data_path
        self.__operation_path__ = os.path.join(self.__data_path__, 'this_operation')

    def __load_result__(self, result_data):
        import os
        from structures import RecoResult

        if isinstance(result_data, str):
            result_data = os.path.join(self.__operation_path__, result_data)
            result = RecoResult.load_csv(result_data)
        elif isinstance(result_data, RecoResult):
            result = result_data
        else:
            from extended.Exceptions import ParamTypeError
            raise ParamTypeError('result_data', (str, RecoResult), result_data)

        return result

    def simple_statistic(self):
        readers = self.env.data_proxy.readers
        print('total readers: {}'.format(len(readers)))

        books = self.env.data_proxy.books
        print('total books: {}'.format(len(books)))

        events = self.env.data_proxy.events
        print('total events: {}'.format(len(events)))
        print('2013 events: {}'.format(
            events.trim_between_range('date', datetime.date(2013, 1, 1), datetime.date(2014, 1, 1))))
        print('2014 events: {}'.format(
            events.trim_between_range('date', datetime.date(2014, 1, 1), datetime.date(2015, 1, 1))))
        print('2015 events: {}'.format(
            events.trim_between_range('date', datetime.date(2015, 1, 1), datetime.date(2016, 1, 1))))

    def statistic(self):
        """"""
        # 获取 2013-2015 年注册的用户数量
        readers = self.env.data_proxy.reader_dict.to_data_dict()
        print('2013年注册的学生数量: {}'.format(len(readers.find_value_where(register_year=2013))))
        print('2014年注册的学生数量: {}'.format(len(readers.find_value_where(register_year=2014))))
        print('2015年注册的学生数量: {}'.format(len(readers.find_value_where(register_year=2015))))

    @staticmethod
    def __evaluation_list__(evaluator, top_n: int = 10):
        from structures import Evaluator
        assert isinstance(evaluator, Evaluator)
        eva_res = list()
        eva_res.append(['match_percentage', evaluator.match_percentage])
        eva_res.append(['coverage', evaluator.coverage()])
        eva_res.append(['top_5_accuracy', evaluator.top_n_accuracy(5)])
        eva_res.append(['top_{}_accuracy'.format(top_n), evaluator.top_n_accuracy(top_n)])
        eva_res.append(['recall_accuracy', evaluator.recall_accuracy()])
        eva_res.append(['precision_accuracy', evaluator.precision_accuracy()])
        eva_res.append(['f_value', evaluator.f_value()])
        eva_res.append(['front_1_top_{}_accuracy'.format(top_n), evaluator.front_i_top_n_accuracy(1, top_n)])
        eva_res.append(['front_2_top_{}_accuracy'.format(top_n), evaluator.front_i_top_n_accuracy(2, top_n)])
        eva_res.append(['front_5_top_{}_accuracy'.format(top_n), evaluator.front_i_top_n_accuracy(5, top_n)])
        eva_res.append(['front_10_top_{}_accuracy'.format(top_n), evaluator.front_i_top_n_accuracy(10, top_n)])
        eva_res.append(['front_{}_top_{}_accuracy'.format(top_n, top_n),
                        evaluator.front_i_top_n_accuracy(top_n, top_n)])
        return eva_res

    def evaluate_result_similarity(self, result_01, result_02, top_n: int = 10, descrip: str = ''):
        from structures import Evaluator
        from utils import save_csv
        result_01 = self.__load_result__(result_01).derive_top(top_n)
        result_02 = self.__load_result__(result_02).derive_top(top_n)
        evaluator = Evaluator(result_01, result_02)
        eva_res = self.__evaluation_list__(evaluator, top_n=top_n)
        if descrip != '':
            des_tag = 'Evaluation result - {} with top {}'.format(descrip, top_n)
        else:
            des_tag = 'Evaluation result with top {}'.format(top_n)
        eva_res.insert(0, [des_tag, ])

        save_csv(eva_res, self.__operation_path__, '..', '{} - {}.csv'.format(
            des_tag, datetime.datetime.now().strftime('%Y-%m-%d %H%M%S')))

    def evaluate_single_result(self, result_data, time_range, top_n: int = 10, descrip: str = ''):
        """评价单个结果并以csv文件形式输出"""
        from structures import Evaluator, TimeRange
        from utils import save_csv
        assert isinstance(time_range, TimeRange)

        result = self.__load_result__(result_data).derive_top(top_n)

        actual_data = dict()
        # events = self.__data_proxy__.events
        # for reco_key in tqdm(list(result.keys()), desc='collecting actual data'):
        #     events_list = events.trim_by_range('reader_id', [reco_key, ])
        #     events_list.trim_between_range(
        #         'date', time_range.end_time.date(),
        #         time_range.end_time.date() + datetime.timedelta(days=30), inline=True
        #     ).sort_by_attr('date').to_attr_list('book_id')
        #     actual_data[reco_key] = events_list
        inducted_events = self.env.data_proxy.inducted_events.to_dict()
        for reco_key, events_list in inducted_events.items():
            # from structures import OrderedList
            # assert isinstance(events_list, OrderedList)
            events_list = events_list.trim_between_range(
                'date', time_range.end_time.date(), time_range.end_time.date() + datetime.timedelta(days=30)
            ).to_attr_list('book_id')
            actual_data[reco_key] = events_list

        self.log.debug_running('evaluating single result ')
        evaluator = Evaluator(actual_data=actual_data, predicted_data=result)

        eva_res = self.__evaluation_list__(evaluator, top_n=top_n)
        if descrip != '':
            des_tag = 'Evaluation result - {} with top {}'.format(descrip, top_n)
        else:
            des_tag = 'Evaluation result with top {}'.format(top_n)
        eva_res.insert(0, [des_tag, ])

        save_csv(eva_res, self.__operation_path__, '..', '{} - {}.csv'.format(
            des_tag, datetime.datetime.now().strftime('%Y-%m-%d %H%M%S')))

    def merge_result(self, result_01, result_02, top_n: int = 10):
        """把两个结果合并在一起"""
        from structures import RecoResult
        result_01 = self.__load_result__(result_01).derive_top(top_n)
        result_02 = self.__load_result__(result_02).derive_top(top_n)
        result = RecoResult()
        tag_set = set(list(result_01.keys()))
        tag_set.update(set(list(result_02.keys())))
        for tag in tag_set:
            if tag not in result_01:
                r_list = result_02[tag]
            elif tag not in result_02:
                r_list = result_01[tag]
            else:
                r_list = result_01[tag]
                for book in result_02[tag]:
                    if book not in r_list:
                        r_list.append(book)
            result.add_list(tag, r_list)
        return result

    @property
    def log(self):
        return self.__logger__


if __name__ == '__main__':
    from Environment import Environment
    env_inst = Environment.get_instance()

    rule_generator = RuleGenerator()
    rule_generator.log.initiate_time_counter()

    try:
        rule_generator.statistic()

    except KeyboardInterrupt:
        env_inst.exit()
    finally:
        env_inst.exit()

    rule_generator.log.time_sleep(1)
    rule_generator.log.print_time_passed()
