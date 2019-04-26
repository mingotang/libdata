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
        from structures import RecommendResult

        if isinstance(result_data, str):
            result_data = os.path.join(self.__operation_path__, result_data)
            result = RecommendResult.load_csv(result_data)
        elif isinstance(result_data, RecommendResult):
            result = result_data
        else:
            from extended.Exceptions import ParamTypeError
            raise ParamTypeError('result_data', (str, RecommendResult), result_data)

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
        # # # 检查读者涉及到多少个书籍类别
        # from os import path
        # from json import dump as json_dump
        # from collections import defaultdict
        # from extended import CountingDict
        # from utils import save_csv
        #
        # reader_lib_class_dict = defaultdict(set)
        #
        # for event in self.env.data_proxy.event_dict.values():
        #     assert isinstance(event, Event)
        #     book = event.correspond_book
        #     assert isinstance(book, Book)
        #     try:
        #         book_lib_class = book.book_lib_index.sub_class
        #     except AttributeError:
        #         continue
        #     if len(book_lib_class) == 0:
        #         continue
        #     reader_lib_class_dict[event.reader_id].add(book_lib_class)
        #
        # for reader_id in reader_lib_class_dict.keys():
        #     reader_lib_class_dict[reader_id] = list(reader_lib_class_dict[reader_id])
        #
        # json_dump(reader_lib_class_dict, open(path.expanduser('~/Downloads/reader_lib_class_dict.json'), 'w'))
        #
        # class_num_count = CountingDict()
        # for reader_id, lib_index_set in reader_lib_class_dict.items():
        #     class_num_count.count(len(lib_index_set), 1)
        #
        # json_dump(class_num_count, open(path.expanduser('~/Downloads/reader_lib_class_num_count.json'), 'w'))
        # save_csv([(k, v) for k, v in class_num_count.items()],
        #          path.expanduser('~/Downloads/reader_lib_class_num_count.csv'))
        #
        # for k, v in class_num_count.items():
        #     print(k, v)

        # ------------------------------------------ #
        # 把2013年、2014年、2015年注册的学生所有借阅事件提取出来
        from os import path
        from tqdm import tqdm
        from structures import LibIndexClassObject
        from extended import CountingDict, ObjectDict, TextObjDict

        book_set, reader_set, event_count = set(), set(), 0
        # lib_class_event_dict = dict()
        books = self.env.data_proxy.book_dict.to_data_dict()

        for reader in tqdm(self.env.data_proxy.reader_dict.values(), desc='collect Event by lib index'):
            assert isinstance(reader, Reader)

            # 排除2013年之前注册的无法确定初次接触某个类别的学生
            if reader.register_year is None:
                continue
            if reader.register_year < 2013:
                continue

            # events = self.env.data_proxy.events.find_value_where(reader_id=reader.index)
            events = self.env.data_proxy.event_dict.query(Event).filter_by(
                reader_id=reader.index).order_by('event_date').all()

            reader_set.add(reader.index)

            for event in events:
                assert isinstance(event, Event)

                # 排除书籍归还事件
                if event.event_type == '61':
                    continue

                book = books[event.book_id]
                assert isinstance(book, Book)

                book_set.add(book.index)

                book_lib_index = book.book_lib_index
                # 排除无法判断书籍类别的书籍
                if book_lib_index is None:
                    continue
                assert isinstance(book_lib_index, LibIndexClassObject)
                if len(book_lib_index.sub_class) == 0:
                    continue

                event_count += 1

                # if book_lib_index.sub_class not in lib_class_event_dict:
                #     # lib_class_event_dict[book_lib_index.sub_class] = TextObjDict(
                #     #     path.join(self.env.data_path, 'lib_sub_class_events', book_lib_index.sub_class), Event,
                #     # )
                #     lib_class_event_dict[book_lib_index.sub_class] = dict()
                #
                # lib_class_event_dict[book_lib_index.sub_class][event.hashable_key] = event

        print('reader_count: {}'.format(len(reader_set)))
        print('book_count: {}'.format(len(book_set)))
        print('event_count: {}'.format(event_count))

        # ------------------------------------------ #
        # 检查每个分类的事件数量
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
        #     event_dict = TextObjDict(
        #         path.join(self.env.data_path, 'lib_sub_class_events', tag), Event
        #     ).to_object_dict()
        #     length2013 = len(event_dict.find_value_where(date_year=2013))
        #     length2014 = len(event_dict.find_value_where(date_year=2014))
        #     length2015 = len(event_dict.find_value_where(date_year=2015))
        #     print(tag, lib_index.name, counter.get(tag), length2013, length2014, length2015)
        #
        #     csv_list.append([tag, lib_index.name, counter.get(tag), length2013, length2014, length2015])
        # print(len(counter))

        # ------------------------------------------ #
        # 检查需要多少数目的书籍才可以完成所有的借阅
        # from os import path
        # from json import dump as json_dump
        # # from pickle import dump as pickle_dump
        # from collections import defaultdict
        # start_date, end_date = datetime.date(2013, 1, 1), datetime.date(2015, 12, 31)
        # max_occupy, now_occupy = defaultdict(int), defaultdict(int)
        #
        # now_date = start_date
        # while now_date <= end_date:
        #     self.log.debug('seaching events {}'.format(now_date))
        #     for event in self.env.data_proxy.event_dict.query(Event).filter_by(
        #             event_date=now_date.strftime('%Y%m%d')).all():
        #         assert isinstance(event, Event)
        #         if event.event_type == '61':  # 还书
        #             if now_occupy[event.book_id] > 0:
        #                 if max_occupy[event.book_id] < now_occupy[event.book_id]:
        #                     max_occupy[event.book_id] = now_occupy[event.book_id]
        #                 else:
        #                     pass
        #                 now_occupy[event.book_id] = now_occupy[event.book_id] - 1
        #             else:
        #                 if max_occupy[event.book_id] < 1:
        #                     max_occupy[event.book_id] = 1
        #                 else:
        #                     pass
        #         else:
        #             now_occupy[event.book_id] = now_occupy[event.book_id] + 1
        #             if max_occupy[event.book_id] < now_occupy[event.book_id]:
        #                 max_occupy[event.book_id] = now_occupy[event.book_id]
        #             else:
        #                 pass
        #     now_date += datetime.timedelta(days=1)
        # json_dump(max_occupy.copy(), open(path.expanduser('~/Downloads/output.pick'), 'w'))

        # ------------------------------------------ #
        # 检查学生第一次借阅某个分类书籍的时间
        # from os import listdir, path
        # from Environment import Environment
        # from structures import Event, ReaderLibClassAccessDay
        # from extended import TextObjDict, ObjectDict
        #
        # sqlite_db = Environment.get_instance().sqlite_db
        #
        # reader_lib_class_day_list = list()
        # for tag in listdir(path.join(self.env.data_path, 'lib_sub_class_events')):
        #     if tag.startswith('.'):
        #         continue
        #     self.log.debug_running('collecting ReaderLibClassAccessDay', tag)
        #     event_dict = TextObjDict(path.join(
        #         self.env.data_path, 'lib_sub_class_events', tag), Event).to_object_dict()
        #
        #     for reader_id, sub_event_dict in event_dict.group_by_attr('reader_id').items():
        #         assert isinstance(sub_event_dict, ObjectDict)
        #         date = min(sub_event_dict.collect_attr_set('date'))
        #         assert isinstance(date, datetime.date)
        #         reader_lib_class_day_list.append(ReaderLibClassAccessDay(
        #             reader_id=reader_id, lib_sub_class=tag, day=date.strftime('%Y%m%d'),
        #         ))
        #
        # sqlite_db.add_all(obj=reader_lib_class_day_list)

        # ------------------------------------------ #
        # # 识别所有的关键字变化
        # from os import path, listdir
        # from json import load as json_load
        # from json import dump as json_dump
        # from algorithm.BipartiteNetwork import BipartiteNetworkBaseConnection, BipartiteNetwork
        # from extended import CountingDict, TextObjDict
        # for tag in listdir(path.join(self.env.data_path, 'lib_sub_class_events')):
        #     if tag.startswith('.'):
        #         continue
        #     lib_class = tag
        #     event_dict = TextObjDict(
        #         path.join(self.env.data_path, 'lib_sub_class_events', lib_class), Event
        #     ).to_object_dict().trim_include_between_attr_value(
        #         'date', datetime.date(2013, 1, 1), datetime.date(2015, 1, 1)
        #     )
        #     self.log.debug_running('collecting 2013-2014 result {} {}'.format(tag, len(event_dict)))
        #     bn0, bn1, bn2 = list(), list(), list()
        #
        #     for reader_id, sub_event_dict in event_dict.group_by_attr('reader_id').items():
        #         reader = self.env.data_proxy.readers[reader_id]
        #         assert isinstance(reader, Reader)
        #
        #         first_date = min(sub_event_dict.collect_attr_set('date'))
        #         assert isinstance(first_date, datetime.date)
        #
        #         for event in sub_event_dict.values():
        #             assert isinstance(event, Event), str(type(event))
        #             days_gap = (event.date - first_date) / datetime.timedelta(days=1)
        #             if days_gap <= 180:
        #                 bn_list = bn0
        #             elif 180 < days_gap <= 360:
        #                 bn_list = bn1
        #             elif 360 < days_gap:
        #                 bn_list = bn2
        #             else:
        #                 continue
        #             for w in event.correspond_book.book_name.cleaned_list:
        #                 # words.count(w, 1)
        #                 bn_list.append(BipartiteNetworkBaseConnection(event.reader_id, w, 1.0))
        #     print(tag, len(bn0), len(bn1), len(bn2))
        #     # continue_or_not = input('Continue or not (y/n): ')
        #     # if str(continue_or_not) == 'y':
        #     #     pass
        #     # else:
        #     #     continue
        #     if len(bn0) >= 50 and len(bn1) >= 10 and len(bn2) >= 10:
        #         pass
        #     else:
        #         json_dump(list(), open(path.expanduser(
        #             '~/Downloads/unrecoginzable/{}.json'.format(lib_class)
        #         ), mode='w'))
        #         continue
        #
        #     keywords_dict = dict()
        #     # result_list = list()
        #     for bn_list in (bn0, bn1, bn2):
        #         max_running_keywords = CountingDict()
        #         max_running_book = json_load(open(
        #             path.expanduser('~/Documents/persisted_libdata/max_running_books.json'), mode='r'))
        #         for book_id in max_running_book.keys():
        #             book = self.env.data_proxy.books[book_id]
        #             assert isinstance(book, Book)
        #             for w in book.book_name.cleaned_list:
        #                 max_running_keywords.count(w, max_running_book[book_id])
        #         # print(max_running_book)
        #         bn_net = BipartiteNetwork(bn_list, max_running_keywords)
        #         reader_weight, keyword_weight = bn_net.run()
        #         sorted_result = CountingDict.init_from(keyword_weight).sort(reverse=True)
        #         # result_list.append(sorted_result)
        #         level = len(keywords_dict)
        #         keywords_dict[level] = keyword_weight.copy_to_dict()
        #         # print(sorted_result)
        #
        #     # json_dump(result_list, open(path.expanduser(
        #     #     '~/Downloads/sub_lib_index_class_importance/{}.json'.format(lib_class)
        #     # ), mode='w'))
        #     json_dump(keywords_dict, open(path.expanduser(
        #         '~/Downloads/sub_lib_index_class_importance_dicts/{}.json'.format(lib_class)
        #     ), mode='w'))

        # ------------------------------------------ #
        # from os import path
        # from json import load as json_load
        # from extended import CountingDict
        #
        # result_list = json_load(open(
        #     path.expanduser('~/Documents/persisted_libdata/sub_lib_index_class_importance/TP.json'),
        #     mode='r'))
        #
        # keyword_set = set()
        # for sorted_result in result_list:
        #     keyword_set.update(sorted_result)
        #
        # def check_next_larger(content_list: list, strict: bool = True):
        #     for i in range(len(content_list)):
        #         for j in range(i + 1, len(content_list)):
        #             if strict is True:
        #                 if content_list[i] >= content_list[j]:
        #                     return False
        #             else:
        #                 if content_list[i] > content_list[j]:
        #                     return False
        #     return True
        #
        # def check_next_smaller(content_list: list, strict: bool = True):
        #     for i in range(len(content_list)):
        #         for j in range(i + 1, len(content_list)):
        #             if strict is True:
        #                 if content_list[i] <= content_list[j]:
        #                     return False
        #             else:
        #                 if content_list[i] < content_list[j]:
        #                     return False
        #     return True
        #
        # from numpy import std as np_std
        # from numpy import mean as np_mean
        # keyword_rank_dict = dict()
        # increasing_important_dict = CountingDict()
        # decreasing_important_dict = CountingDict()
        # for keyword in keyword_set:
        #     if len(keyword) == 1:
        #         continue
        #     index_list = list()
        #     for sorted_result in result_list:
        #         assert isinstance(sorted_result, list)
        #         try:
        #             index_list.append(sorted_result.index(keyword) + 1)
        #         except ValueError:
        #             continue
        #     if len(index_list) <= 1:
        #         continue
        #
        #     # for i in range(len(index_list)):
        #     #     index_list[i] = index_list[i] / len(keyword_set)
        #
        #     keyword_rank_dict[keyword] = index_list
        #     # 随着发展重要程度上升
        #     if check_next_smaller(index_list):
        #         increasing_important_dict[keyword] = np_std(index_list) / np_mean(index_list)
        #     # 随着发展重要程度下降
        #     if check_next_larger(index_list):
        #         decreasing_important_dict[keyword] = np_std(index_list) / np_mean(index_list)
        #
        # csv_out = list()
        #
        # increasing_important_list = increasing_important_dict.sort(reverse=True)
        # print(increasing_important_list)
        # for tag in increasing_important_list[:40]:
        #     print(tag, increasing_important_dict[tag], keyword_rank_dict[tag])
        # decreasing_important_list = decreasing_important_dict.sort(reverse=True)
        # print(decreasing_important_list)
        # for tag in decreasing_important_list[:20]:
        #     print(tag, decreasing_important_dict[tag], keyword_rank_dict[tag])

        # from os import path
        from utils import save_csv
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

        # from utils import save_csv
        # save_csv(csv_list, path.expanduser('~/Downloads/output.csv'))

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

    def fetch_actual_data(self, time_range, user_set: set):
        from collections import defaultdict
        from structures import TimeRange
        assert isinstance(time_range, TimeRange)
        actual_data = defaultdict(list)
        now_date = time_range.end_time.date()
        while now_date <= time_range.end_time.date() + datetime.timedelta(days=90):
            for event in self.env.data_proxy.event_dict.query(Event).filter_by(
                    event_date=now_date.strftime('%Y%m%d')
            ).all():
                assert isinstance(event, Event)
                if event.event_type == '61':
                    continue
                if event.reader_id not in user_set:
                    continue
                if event.correspond_book_lib_index_sub_class != 'TP':
                    continue
                actual_data[event.reader_id].append(event.book_id)
            now_date = now_date + datetime.timedelta(days=1)
        return actual_data

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
        from collections import defaultdict
        from structures import Evaluator, TimeRange
        from utils import save_csv
        assert isinstance(time_range, TimeRange)

        result = self.__load_result__(result_data).derive_top(top_n)
        print(result.keys())

        actual_data = defaultdict(list)
        now_date = time_range.end_time.date()
        while now_date <= time_range.end_time.date() + datetime.timedelta(days=90):
            for event in self.env.data_proxy.event_dict.query(Event).filter_by(
                    event_date=now_date.strftime('%Y%m%d')
            ).all():
                assert isinstance(event, Event)
                if event.event_type == '61':
                    continue
                if event.reader_id not in result:
                    continue
                if event.correspond_book_lib_index_sub_class != 'TP':
                    continue
                actual_data[event.reader_id].append(event.book_id)
            now_date = now_date + datetime.timedelta(days=1)
        print(actual_data)
        # # events = self.__data_proxy__.events
        # # for reco_key in tqdm(list(result.keys()), desc='collecting actual data'):
        # #     events_list = events.trim_by_range('reader_id', [reco_key, ])
        # #     events_list.trim_between_range(
        # #         'date', time_range.end_time.date(),
        # #         time_range.end_time.date() + datetime.timedelta(days=30), inline=True
        # #     ).sort_by_attr('date').to_attr_list('book_id')
        # #     actual_data[reco_key] = events_list
        # inducted_events = self.env.data_proxy.inducted_events.to_dict()
        # for reco_key, events_list in inducted_events.items():
        #     # from structures import OrderedList
        #     # assert isinstance(events_list, OrderedList)
        #     events_list = events_list.trim_between_range(
        #         'date', time_range.end_time.date(), time_range.end_time.date() + datetime.timedelta(days=180)
        #     ).to_attr_list('book_id')
        #     actual_data[reco_key] = events_list

        self.log.debug_running('evaluating single result ')
        evaluator = Evaluator(actual_data=actual_data, predicted_data=result)

        eva_res = self.__evaluation_list__(evaluator, top_n=top_n)
        if descrip != '':
            des_tag = 'Evaluation result - {} with top {}'.format(descrip, top_n)
        else:
            des_tag = 'Evaluation result with top {}'.format(top_n)
        eva_res.insert(0, [des_tag, ])

        # # 寻找匹配程度最高的用户
        # def calculate_match_percentage(l01: list, l02: list):
        #     from math import sqrt
        #     if len(l02) == 0 or len(l01) == 0:
        #         return 0.0
        #     else:
        #         # count = 0
        #         # for i in l01:
        #         #     if i in l02:
        #         #         count += 1
        #         # return count
        #         return len(set(l01).intersection(set(l02))) / (sqrt(len(l01)) * sqrt(len(l02)))
        #
        # from extended import CountingDict
        # best_matcher = CountingDict()
        # users = self.env.data_proxy.reader_dict.to_data_dict()
        # for user_id in result.keys():
        #     if user_id not in actual_data:
        #         continue
        #     user = users[user_id]
        #     assert isinstance(user, Reader)
        #     if user.register_year != 2013:
        #         continue
        #     match_percentage = calculate_match_percentage(result[user_id], actual_data[user_id])
        #     if match_percentage > 0:
        #         best_matcher.set(user_id, match_percentage)
        # best_match_user = best_matcher.sort(reverse=True)[0]
        #
        # best_match_user = '5130209132'
        # books = self.env.data_proxy.book_dict.to_data_dict()
        # print(best_match_user)
        # print([books[var].name for var in actual_data[best_match_user]])
        # print([books[var].name for var in result[best_match_user]])

        # 5130209132

        # for item in eva_res:
        #     print(item)

        save_csv(eva_res, self.__operation_path__, '..', '{} - {}.csv'.format(
            des_tag, datetime.datetime.now().strftime('%Y-%m-%d %H%M%S')))

    def merge_result(self, result_01, result_02, top_n: int = 10):
        """把两个结果合并在一起"""
        from structures import RecommendResult
        result_01 = self.__load_result__(result_01).derive_top(top_n)
        result_02 = self.__load_result__(result_02).derive_top(top_n)
        result = RecommendResult()
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


    def calculate_match_percentage(l01: list, l02: list):
        from math import sqrt
        if len(l02) == 0 or len(l01) == 0:
            return 0.0
        else:
            count = 0
            for i in l01:
                if i in l02:
                    count += 1
            return count
            # return len(set(l01).intersection(set(l02))) / (sqrt(len(l01)) * sqrt(len(l02)))

    try:
        # rule_generator.statistic()
        from os import path
        from structures import StandardTimeRange, RecommendResult
        this_time_range = StandardTimeRange(start_time=datetime.date(2015, 1, 1), end_time=datetime.date(2015, 3, 31))
        # this_time_range = StandardTimeRange(start_time=datetime.date(2014, 1, 1), end_time=datetime.date(2014, 12, 31))
        this_result = RecommendResult.load_csv(path.join(
            env_inst.data_path, 'CF_RecoBook', 'cf_result_20190414_150101.csv'
        ))
        rule_generator.evaluate_single_result(
            result_data=this_result,
            time_range=this_time_range,
            top_n=10,
        )
        # normal_result = RecommendResult.load_csv(path.join(
        #     env_inst.data_path, 'CF_RecoBook', 'cf_result_20190309_000752.csv'
        # )).derive_top(12)
        # this_result = RecommendResult.load_csv(path.join(
        #     env_inst.data_path, 'CF_RecoBook', 'cf_result_20190309_001857.csv'
        # )).derive_top(12)
        # this_user_set = set(normal_result.keys())
        # this_user_set.update(this_result.keys())
        # books = env_inst.data_proxy.book_dict.to_data_dict()
        # actual_result = rule_generator.fetch_actual_data(time_range=this_time_range, user_set=this_user_set)
        # for user_id in this_user_set:
        #     assert isinstance(user_id, str)
        #     user_id = user_id.replace('\n', '')
        #     if user_id not in normal_result:
        #         continue
        #     if user_id not in this_result:
        #         continue
        #     if user_id not in actual_result:
        #         continue
        #     normal_match = calculate_match_percentage(actual_result[user_id], normal_result[user_id])
        #     this_match = calculate_match_percentage(
        #         actual_result[user_id], this_result[user_id],
        #     )
        #     if normal_match < this_match:
        #         try:
        #             print(user_id, normal_match, this_match)
        #             print([books[var].name for var in actual_result[user_id]])
        #             print([books[var].name for var in normal_result[user_id]])
        #             print([books[var].name for var in this_result[user_id]])
        #         except KeyError:
        #             continue

    except KeyboardInterrupt:
        env_inst.exit()
    finally:
        env_inst.exit()

    rule_generator.log.time_sleep(1)
    rule_generator.log.print_time_passed()
