# -*- encoding: UTF-8 -*-
import datetime

from extended import DataDict, CountingDict
from modules.RuleGen import RuleGenerator
from structures import Book, Event, Reader
from structures import RecommendResult, SparseVector
from structures import StandardTimeRange, GrowthTimeRange, DateBackTimeRange
from structures import ReaderLibClassAccessDay


class RuleGenCF(RuleGenerator):
    def __init__(self):
        RuleGenerator.__init__(self)

    def apply_collaborative_filtering(self, time_range):
        # from algorithm.CollaborativeFiltering import CollaborativeFiltering
        assert isinstance(time_range, StandardTimeRange)

        # 获取用户群体范围
        self.log.debug_running('fetching reader range')
        reader_lib_class_access_date_dict = dict()
        for obj in self.env.sqlite_db.session.query(ReaderLibClassAccessDay).all():
            assert isinstance(obj, ReaderLibClassAccessDay)
            if obj.reader_id not in reader_lib_class_access_date_dict:
                reader_lib_class_access_date_dict[obj.reader_id] = dict()
            reader_lib_class_access_date_dict[obj.reader_id][obj.lib_sub_class] = obj.date

        # 抓取符合时间条件的借阅事件
        events_data = self.env.data_proxy.events
        self.log.debug_running('trimming event data from date {} to date {}'.format(
            time_range.start_time.date(), time_range.end_time.date())
        )
        events_data.trim_include_between_attr_value(
            attr_tag='date', range_start=time_range.start_time.date(), range_end=time_range.end_time.date(),
            include_start=True, include_end=False, inline=True,
        )

        # 排除还书行为
        self.log.debug_running('trimming event data by event_type 50/62/63')
        events_data.trim_include_by_attr_value('event_type', ('50', '62', '63'), inline=True)

        # from structures import LibIndexClassObject
        # # 搜集用户向量
        # vector_collector = SparseVectorCollector()
        # for event in events_data.values():
        #     assert isinstance(event, Event)
        #     book = event.correspond_book
        #     assert isinstance(book, Book)
        #     book_lib_index = book.book_lib_index
        #     if isinstance(book_lib_index, LibIndexClassObject):
        #         if book_lib_index.sub_class == 'TP':
        #             pass
        #         else:
        #             continue
        #     else:
        #         continue
        #     # if event.reader_id not in reader_lib_class_access_date_dict:
        #     #     continue
        #     vector_collector.add(event.reader_id, event.book_id, event.times)
        # vector_collector.finish(with_length=len(events_data.collect_attr_set('book_id')))
        #
        # cf_result = CollaborativeFiltering(
        #     vector_collector.to_dict(),
        #     possible_neighbor_dict=events_data.neighbor_attr_by(
        #         'reader_id', 'book_id'
        #     ))
        # cf_result.set_neighbor_type(CF_NeighborType.All).set_similarity_type(CF_SimilarityType.Cosine)
        # reader_similarity_dict = cf_result.run(fixed_size=None, limited_size=None, )
        #
        # output_dict = dict()
        # for reader_id, reader_simi in reader_similarity_dict.items():
        #     assert isinstance(reader_simi, CountingDict)
        #     output_dict[reader_id] = reader_simi.copy()
        #
        # from os import path
        # from json import dump as json_dump
        # json_dump(output_dict, open(path.join(self.env.data_path, '2013-2014CF_TP_result.json'), mode='w'))

        from os import path, listdir
        from json import load as json_load

        events_data.trim_include_by_attr_value('correspond_book_lib_index_sub_class', ('TP', ), inline=True)

        increasing_class_keywords_dict = dict()
        for tag in listdir(path.join(self.env.data_path, 'sub_lib_index_class_increasing_importance_dicts')):
            if tag.startswith('.'):
                continue
            tag = tag.split('.')[0]
            increasing_class_keywords_dict[tag] = json_load(open(path.join(
                self.env.data_path,
                'sub_lib_index_class_increasing_importance_dicts',
                '{}.json'.format(tag), ), mode='r'))

        decreasing_class_keywords_dict = dict()
        for tag in listdir(path.join(self.env.data_path, 'sub_lib_index_class_decreasing_importance_dicts')):
            if tag.startswith('.'):
                continue
            tag = tag.split('.')[0]
            decreasing_class_keywords_dict[tag] = json_load(open(path.join(
                self.env.data_path,
                'sub_lib_index_class_decreasing_importance_dicts',
                '{}.json'.format(tag), ), mode='r'))

        # 用户借阅书籍集合
        reader_book_set_dict = events_data.group_attr_set_by(group_attr='book_id', by_attr='reader_id')

        books = self.env.data_proxy.book_dict.to_data_dict()

        from math import sqrt
        from tqdm import tqdm
        from structures import LibIndexClassObject
        reader_similarity_dict = json_load(open(path.join(self.env.data_path, '2013-2014CF_TP_result.json'), mode='r'))
        assert isinstance(reader_similarity_dict, dict)

        recommend_result = RecommendResult()

        # reader_similarity_list = CountingDict.init_from(reader_similarity_dict).sort(reverse=True)
        # if len(reader_similarity_list) >= 30:
        #     reader_similarity_list = reader_similarity_list[:30]

        for reader_id, simi_dict in tqdm(reader_similarity_dict.items(), desc='collecting books'):
            assert isinstance(simi_dict, dict)
            finished_book_set = reader_book_set_dict[reader_id]
            assert isinstance(finished_book_set, set)
            book_count_dict = CountingDict()
            for simi_reader_id in CountingDict.init_from(simi_dict).sort(reverse=True, limit=30):
                for book_id in reader_book_set_dict[simi_reader_id]:
                    if book_id in finished_book_set:
                        continue
                    else:
                        # book_count_dict.count(book_id, simi_dict[simi_reader_id])
                        book = books[book_id]
                        assert isinstance(book, Book)
                        book_lib_index = book.book_lib_index
                        book_weight = 1.0
                        if isinstance(book_lib_index, LibIndexClassObject):
                            if len(book_lib_index.sub_class) > 0:
                                if book_lib_index.sub_class in increasing_class_keywords_dict:
                                    this_change_dict = increasing_class_keywords_dict[book_lib_index.sub_class]
                                    for tag in book.book_name.cleaned_list:
                                        if len(tag) <= 1:
                                            continue
                                        if tag in this_change_dict:
                                            book_weight = sqrt(abs(1 + len(tag) * sqrt(abs(this_change_dict[tag])))) * book_weight
                                if book_lib_index.sub_class in decreasing_class_keywords_dict:
                                    this_change_dict = decreasing_class_keywords_dict[book_lib_index.sub_class]
                                    for tag in book.book_name.cleaned_list:
                                        if len(tag) <= 1:
                                            continue
                                        if tag in this_change_dict:
                                            book_weight = sqrt(abs(1 - len(tag) * sqrt(abs(this_change_dict[tag])))) * book_weight
                                if book_lib_index.sub_class not in increasing_class_keywords_dict and book_lib_index.sub_class not in decreasing_class_keywords_dict:
                                    book_weight = 0.0
                        book_count_dict.count(book_id, simi_dict[simi_reader_id] * book_weight)
            recommend_result.add_list(reader_id, book_count_dict.sort(reverse=True))

        recommend_result.to_csv(path.join(self.env.data_path, 'CF_RecoBook'))

        # readers = self.env.data_proxy.readers
        # for key in list(cf_result.keys()):
        #     reader = readers[key]
        #     from structures import Reader
        #     assert isinstance(reader, Reader)
        #     if reader.growth_index(time_range.end_time.date()) is None:
        #         cf_result.pop(key)
        # cf_result.to_csv()
        # return cf_result

    # def apply_slipped_collaborative_filtering(self, time_range):
    #     from algorithm.CollaborativeFiltering import SlippingRangeCollaborativeFiltering
    #     assert isinstance(time_range, GrowthTimeRange)
    #
    #     self.log.debug_running('trimming event data from date {} to date {}'.format(
    #         time_range.start_time.date(), time_range.end_time.date()
    #     ))
    #     self.log.debug_running('trimming event data by event_type 50/62/63')
    #     events_data = self.env.data_proxy.events.trim_between_range(
    #         attr_tag='date', range_start=time_range.start_time.date(), range_end=time_range.end_time.date(),
    #         include_start=True, include_end=False, inline=True
    #     ).trim_by_range('event_type', ('50', '62', '63'), inline=True)
    #
    #     self.log.debug_running('TimeRange.{}'.format(time_range.__class__.__name__))
    #
    #     stage_tag, stage_list = time_range.growth_stage
    #     cf_result = RecommendResult()
    #     readers = self.env.data_proxy.readers
    #     for i in range(len(stage_list)):
    #         stage = stage_list[i]
    #
    #         this_event = DataDict()
    #         next_event = DataDict()
    #         for key, value in events_data.items():
    #             # assert isinstance(value, Event)
    #             this_growth = getattr(readers[value.reader_id], stage_tag).__call__(time_range.end_time.date())
    #             if this_growth is None:
    #                 continue
    #
    #             if isinstance(stage, int):
    #                 if this_growth == stage:
    #                     this_event[key] = value
    #                 else:
    #                     next_event[key] = value
    #             elif isinstance(stage, tuple):
    #                 if stage[0] <= this_growth < stage[1]:
    #                     this_event[key] = value
    #                 elif this_growth >= stage[1]:
    #                     next_event[key] = value
    #                 else:
    #                     continue
    #                     # next_event[key] = value
    #             else:
    #                 raise RuntimeError
    #
    #         if len(this_event) == 0:
    #             continue
    #
    #         self.log.debug_running('collecting vector data for stage {}'.format(stage))
    #         srcf = SlippingRangeCollaborativeFiltering(this_event, next_event).set_relation_tag('reader_id', 'book_id')
    #         srcf.set_neighbor_type(CF_NeighborType.FixSize).set_similarity_type(CF_SimilarityType.Cosine)
    #         srcf.set_item_vector_value_tag('times')
    #         cf_result.update(srcf.run(fixed_size=5, max_recommend_list=100))
    #
    #     cf_result.to_csv()
    #
    #     return cf_result

    # def apply_refered_slipped_collaborative_filtering(self, similarity_type, neighbor_type, time_range):
    #     from algorithm import CollaborativeFiltering
    #     from structures import RecommendResult
    #     assert isinstance(neighbor_type, CF_NeighborType)
    #     assert isinstance(time_range, GrowthTimeRange)
    #
    #     # events_data = self.__data_proxy__.events.to_data_dict()
    #
    #     self.log.debug_running('trimming event data from date {} to date {}'.format(
    #         time_range.start_time.date(), time_range.end_time.date()
    #     ))
    #     events_data.trim_between_range(
    #         attr_tag='date', range_start=time_range.start_time.date(), range_end=time_range.end_time.date(),
    #         include_start=True, include_end=False, inline=True
    #     )
    #
    #     self.log.debug_running('trimming event data by event_type 50/62/63')
    #     events_data.trim_by_range('event_type', ('50', '62', '63'), inline=True)
    #
    #     self.log.debug_running('collecting possible neighbor data')
    #     possible_neighbors = events_data.neighbor_attr_by('reader_id', 'book_id')
    #
    #     self.log.debug_running('TimeRange.{}'.format(time_range.__class__.__name__))
    #
    #     stage_tag, stage_list = time_range.growth_stage
    #     cf_result = RecommendResult()
    #     readers = self.__data_proxy__.readers
    #     for i in range(len(stage_list)):
    #         stage = stage_list[i]
    #
    #         this_event = DataDict()
    #         for key, value in events_data.items():
    #             # assert isinstance(value, Event)
    #             this_growth = getattr(readers[value.reader_id], stage_tag).__call__(time_range.end_time.date())
    #             if this_growth is None:
    #                 continue
    #
    #             if isinstance(stage, int):
    #                 if this_growth == stage:
    #                     this_event[key] = value
    #             elif isinstance(stage, tuple):
    #                 if stage[0] <= this_growth < stage[1]:
    #                     this_event[key] = value
    #             else:
    #                 raise RuntimeError
    #
    #         if len(this_event) == 0:
    #             continue
    #
    #         self.log.debug_running('collecting vector data for stage {}'.format(stage))
    #         collector = self.__collect_simple_sparse_vector__(
    #             this_event, time_tag='times', finish_length=len(events_data)
    #         )
    #         self.log.debug_running('running CollaborativeFiltering for stage {}'.format(stage))
    #         this_result = CollaborativeFiltering(
    #             collector, events_data.group_attr_set_by('book_id', 'reader_id'), in_memory=True
    #         ).run(
    #             neighbor_type=neighbor_type, similarity_type=similarity_type,
    #             possible_neighbors=possible_neighbors
    #         )
    #
    #         cf_result.update(this_result)
    #
    #     cf_result.to_csv()
    #
    #     return cf_result

    @property
    def log(self):
        return self.__logger__


if __name__ == '__main__':
    import datetime
    from Environment import Environment
    env = Environment()

    rule_generator = RuleGenCF()
    rule_generator.log.initiate_time_counter()

    try:
        # running StandardTimeRange
        this_time_range = StandardTimeRange(start_time=datetime.date(2014, 1, 1), end_time=datetime.date(2014, 12, 31))

        # running GrowthTimeRange
        # this_time_range = GrowthTimeRange(start_time=datetime.date(2013, 1, 1), end_time=datetime.date(2013, 7, 1))
        # this_time_range.set_growth_stage('growth_index', [(0, 1), (1, 2), (2, 3), (3, 4), (4, 6), (6, 100)])

        # running DateBackTimeRange
        # this_time_range = DateBackTimeRange(datetime.date(2013, 1, 1), datetime.date(2013, 7, 1),
        #                                     datetime.date(2013, 3, 1))

        this_re = rule_generator.apply_collaborative_filtering(this_time_range,)

        # this_re = rule_generator.apply_slipped_collaborative_filtering(
        #     CF_SimilarityType.Cosine, CF_NeighborType.All, this_time_range, )

        # this_re = rule_generator.apply_refered_slipped_collaborative_filtering(
        #     CF_SimilarityType.Cosine, CF_NeighborType.All, this_time_range,)

        # this_re = rule_generator.apply_date_back_collaborative_filtering(
        #     CF_SimilarityType.Cosine, CF_NeighborType.All, this_time_range,)

        # this_re = rule_generator.merge_result('2013-06 growth weighted simple.csv', '2013-06 slipped.csv', top_n=10)

        # rule_generator.log.info(' --- [real time] ---')
        # rule_generator.evaluate_single_result(result_data=this_re, time_range=this_time_range, top_n=20)

        # print('--- [similarity] ---')
        # rule_generator.evaluate_result_similarity(
        #     '2013-06 simple.csv',
        #     '2013-06 date back.csv', )

        # rule_generator.evaluate_single_result(
        #     result_data='cf_result_20181208_165855.csv',
        #     time_range=this_time_range, top_n=10)

        # print('--- [growth timerange] ---')
        # rule_generator.evaluate_single_result(
        #     result_data='2013-2014 slipped CF.csv',
        #     time_range=this_time_range, )

        # print('--- [date back timerange] ---')
        # rule_generator.evaluate_single_result(
        #     result_data='/Users/mingo/Downloads/persisted_libdata/this_operation/cf_result_20180920_193451.csv',
        #     time_range=this_time_range
        # )

    except KeyboardInterrupt:
        pass
    finally:
        pass

    rule_generator.log.time_sleep(1)
    rule_generator.log.print_time_passed()
