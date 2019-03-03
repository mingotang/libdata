# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os
import datetime

from Interface import AbstractEnvObject
from structures import Book, Event, Reader


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
        # ------------------------------------------ #
        # # 获取 2013-2015 年注册的用户数量
        # readers = self.env.data_proxy.reader_dict.to_data_dict()
        # print('2013年注册的学生数量: {}'.format(len(readers.find_value_where(register_year=2013))))
        # print('2014年注册的学生数量: {}'.format(len(readers.find_value_where(register_year=2014))))
        # print('2015年注册的学生数量: {}'.format(len(readers.find_value_where(register_year=2015))))

        # ------------------------------------------ #
        # from os import path
        # from tqdm import tqdm
        # from structures import LibIndexClassObject
        # from extended import CountingDict, ObjectDict, TextObjDict
        #
        # lib_class_event_dict = dict()
        # books = self.env.data_proxy.book_dict.to_data_dict()
        #
        # for reader in tqdm(self.env.data_proxy.reader_dict.values(), desc='collect Event by lib index'):
        #     assert isinstance(reader, Reader)
        #
        #     # 排除2013年之前注册的无法确定初次接触某个类别的学生
        #     if reader.register_year is None:
        #         continue
        #     if reader.register_year < 2013:
        #         continue
        #
        #     # events = self.env.data_proxy.events.find_value_where(reader_id=reader.index)
        #     events = self.env.data_proxy.event_dict.query(Event).filter_by(
        #         reader_id=reader.index).order_by('event_date').all()
        #
        #     for event in events:
        #         assert isinstance(event, Event)
        #
        #         # 排除书籍归还事件
        #         if event.event_type == '61':
        #             continue
        #
        #         book = books[event.book_id]
        #         assert isinstance(book, Book)
        #
        #         book_lib_index = book.book_lib_index
        #         # 排除无法判断书籍类别的书籍
        #         if book_lib_index is None:
        #             continue
        #         assert isinstance(book_lib_index, LibIndexClassObject)
        #         if len(book_lib_index.sub_class) == 0:
        #             continue
        #
        #         if book_lib_index.sub_class not in lib_class_event_dict:
        #             lib_class_event_dict[book_lib_index.sub_class] = TextObjDict(
        #                 path.join(self.env.data_path, 'lib_sub_class_events', book_lib_index.sub_class), Event,
        #             )
        #
        #         lib_class_event_dict[book_lib_index.sub_class][event.hashable_key] = event

        # ------------------------------------------ #
        # from os import listdir, path
        # from structures import Event
        # from extended import CountingDict, TextObjDict
        # counter = CountingDict()
        # for tag in listdir(path.join(self.env.data_path, 'lib_sub_class_events')):
        #     if tag.startswith('.'):
        #         continue
        #     counter.set(tag, len(TextObjDict(path.join(self.env.data_path, 'lib_sub_class_events', tag), Event)))
        #
        # csv_list = list()
        #
        # for tag in counter.sort(reverse=True):
        #     lib_index = self.env.find_book_lib_index(tag)
        #     event_dict = TextObjDict(path.join(self.env.data_path, 'lib_sub_class_events', tag), Event).to_object_dict()
        #     length2013 = len(event_dict.find_value_where(date_year=2013))
        #     length2014 = len(event_dict.find_value_where(date_year=2014))
        #     length2015 = len(event_dict.find_value_where(date_year=2015))
        #     print(tag, lib_index.name, counter.get(tag), length2013, length2014, length2015)
        #
        #     csv_list.append([tag, lib_index.name, counter.get(tag), length2013, length2014, length2015])
        # print(len(counter))

        # ------------------------------------------ #
        from os import path
        from extended import TextObjDict
        lib_class = 'TP'
        event_dict = TextObjDict(
            path.join(self.env.data_path, 'lib_sub_class_events', lib_class), Event
        ).to_object_dict()

        # for lib_class_tag, event_dict in lib_class_event_dict.items():
        #     csv_line_list = list()
        #     assert isinstance(event_dict, ObjectDict)
        #     book_name_keyword_dict = CountingDict()
        #     for event in event_dict.values():
        #         assert isinstance(event, Event)
        #         book_name = event.correspond_book.book_name
        #         assert isinstance(book_name, BookName)
        #         for item in book_name.cleaned_list:
        #             book_name_keyword_dict.count(item)
        #
        #     key_word_list = book_name_keyword_dict.sort(reverse=True)
        #
        #     csv_line_list.append(lib_class_tag)
        #     csv_line_list.extend(key_word_list)
        #
        #     print(lib_class_tag, key_word_list)
        #
        #     csv_list.append(csv_line_list)
        #
        # from os import path
        # from utils import save_csv
        # save_csv(csv_list, path.expanduser('~/Downloads/output.csv'))

        # # 获取书籍类别
        # from structures import LibIndexClassObject
        # books = self.env.data_proxy.book_dict.to_data_dict()
        # for book in books.values():
        #     assert isinstance(book, Book)
        #     lib_index = book.book_lib_index
        #     if lib_index is None:
        #         continue
        #     assert isinstance(lib_index, LibIndexClassObject)

        from utils import save_csv
        save_csv(csv_list, path.expanduser('~/Downloads/output.csv'))

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
