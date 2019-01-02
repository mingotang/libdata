# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os
import datetime


class RuleGenerator(object):
    def __init__(self):
        from Environment import Environment
        from modules.DataProxy import DataProxy
        # from structures import TextRecorder
        from utils import get_logger
        self.__logger__ = get_logger(self.__class__.__name__)

        env = Environment.get_instance()
        self.__data_path__ = env.data_path
        self.__operation_path__ = os.path.join(self.__data_path__, 'this_operation')
        # self.__recorder__ = TextRecorder()

        self.__data_proxy__ = DataProxy(data_path=self.__data_path__)

    def __load_result__(self, result_data):
        import os
        from structures import RecoResult

        if isinstance(result_data, str):
            result_data = os.path.join(self.__operation_path__, result_data)
            result = RecoResult.load_csv(result_data)
        elif isinstance(result_data, RecoResult):
            result = result_data
        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('result_data', (str, RecoResult), result_data)

        return result

    def simple_statistic(self):
        readers = self.__data_proxy__.readers
        print('total readers: {}'.format(len(readers)))

        books = self.__data_proxy__.books
        print('total books: {}'.format(len(books)))

        events = self.__data_proxy__.events
        print('total events: {}'.format(len(events)))
        print('2013 events: {}'.format(
            events.trim_between_range('date', datetime.date(2013, 1, 1), datetime.date(2014, 1, 1))))
        print('2014 events: {}'.format(
            events.trim_between_range('date', datetime.date(2014, 1, 1), datetime.date(2015, 1, 1))))
        print('2015 events: {}'.format(
            events.trim_between_range('date', datetime.date(2015, 1, 1), datetime.date(2016, 1, 1))))

    def statistic_one(self):
        """"""
        from collections import defaultdict
        from tqdm import tqdm
        from structures import Book, CountingDict, Event
        from utils.FileSupport import save_csv

        one_book = self.__data_proxy__.books[list(self.__data_proxy__.books.keys())[0]]
        assert isinstance(one_book, Book)

        for lib_index_key, event_dict in self.__data_proxy__.events.group_by(
                'correspond_book.book_lib_index.index_class'):

            book_weight_dict = defaultdict(CountingDict)
            for event in tqdm(event_dict.values(), desc='collect book_weight_dict'):
                assert isinstance(event, Event)
                try:
                    book_weight_dict[event.book_id].count(event.date.year - event.correspond_book.publish_year)
                except TypeError:
                    book_weight_dict[event.book_id].count(1)

            book_weight = CountingDict()
            for book_id, book_count in tqdm(book_weight_dict.items(), desc='collect book_weight'):
                weighted_sum = 0
                for k, v in book_count.items():
                    weighted_sum += k * v
                book_weight.set(book_id, weighted_sum / book_count.sum)

            self.log.debug_running('outputing result')
            output_csv = [['book_name', 'weight'], ]
            for key in book_weight.sort(inverse=True):
                output_csv.append([self.__data_proxy__.books[key].name, book_weight.get(key)])
            save_csv(output_csv, self.__operation_path__, '..', 'book_weight_one_{}.csv'.format(
                one_book.book_lib_index.index_class_map[lib_index_key]
            ))

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
        from utils.FileSupport import save_csv
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
        from utils.FileSupport import save_csv
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
        inducted_events = self.__data_proxy__.inducted_events.to_dict()
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

    def close(self):
        self.__data_proxy__.close()


if __name__ == '__main__':
    from Environment import Environment
    from modules.DataProxy import DataProxy
    env_inst = Environment()
    env_inst.set_data_proxy(DataProxy())

    rule_generator = RuleGenerator()
    rule_generator.log.initiate_time_counter()

    try:
        rule_generator.statistic_one()

    except KeyboardInterrupt:
        rule_generator.close()
    finally:
        rule_generator.close()

    rule_generator.log.time_sleep(1)
    rule_generator.log.print_time_passed()
