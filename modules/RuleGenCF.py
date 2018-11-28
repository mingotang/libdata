# -*- encoding: UTF-8 -*-
import datetime
from Config import DataConfig

from algorithm import SparseVectorCollector
from modules.RuleGen import RuleGenerator
from structures import Book, Event, Reader
from structures import DataDict, SparseVector
from structures import StandardTimeRange, GrowthTimeRange, DateBackTimeRange


class RuleGeneratorCF(RuleGenerator):
    def __init__(self, data_path: str=DataConfig.data_path, operation_path: str=DataConfig.operation_path):
        RuleGenerator.__init__(self, data_path=data_path, operation_path=operation_path)

    def simple_statistic(self):
        readers = self.__data_proxy__.readers
        print('total readers: {}'.format(len(readers)))

        books = self.__data_proxy__.books
        print('total books: {}'.format(len(books)))

        events = self.__data_proxy__.events
        print('total events: {}'.format(len(events)))
        # print('2013 events: {}'.format(events.trim_between_range('date', datetime.date(2013, 1, 1), datetime.date(2014, 1, 1))))
        # print('2014 events: {}'.format(events.trim_between_range('date', datetime.date(2014, 1, 1), datetime.date(2015, 1, 1))))
        # print('2015 events: {}'.format(events.trim_between_range('date', datetime.date(2015, 1, 1), datetime.date(2016, 1, 1))))

    def apply_collaborative_filtering(self, similarity_type, neighbor_type, time_range):
        from algorithm import CF_NeighborType
        from algorithm import CollaborativeFiltering
        assert isinstance(neighbor_type, CF_NeighborType)
        assert isinstance(time_range, StandardTimeRange)

        events_data = self.__data_proxy__.events

        self.log.debug_running('trimming event data from date {} to date {}'.format(
            time_range.start_time.date(), time_range.end_time.date()
        ))
        events_data.trim_between_range(
            attr_tag='date', range_start=time_range.start_time.date(), range_end=time_range.end_time.date(),
            include_start=True, include_end=False, inline=True
        )

        self.log.debug_running('trimming event data by event_type 50/62/63')
        events_data.trim_by_range('event_type', ('50', '62', '63'), inline=True)

        self.log.debug_running('collecting possible neighbor data')
        # possible_neighbors = events_data.neighbor_attr_by('reader_id', 'book_id')
        possible_neighbors = self.__collect_possible_neighbors_by_keyword__(events_data)

        self.log.debug_running('TimeRange.{}'.format(time_range.__class__.__name__))

        self.log.debug_running('collecting vector data to speed up')
        collector = self.__collect_mixed_sparse_vector__(
            events_data, ref_date=time_range.end_time.date(), time_tag='times',)
        collector = self.__collect_simple_sparse_vector__(events_data, time_tag='times',)
        # collector = self.__collect_growth_weighted_sparse_vector__(events_data)
        # collector = self.__collect_keyword_sparse_vector(events_data)

        self.log.debug_running('running CollaborativeFiltering')
        cf_result = CollaborativeFiltering(
            collector, events_data.group_attr_by('book_id', 'reader_id'), in_memory=True
        ).run(
            neighbor_type=neighbor_type, similarity_type=similarity_type, possible_neighbors=possible_neighbors
        )

        readers = self.__data_proxy__.readers
        for key in list(cf_result.keys()):
            reader = readers[key]
            from structures import Reader
            assert isinstance(reader, Reader)
            if reader.growth_index(time_range.end_time.date()) is None:
                cf_result.pop(key)

        cf_result.to_csv()

        return cf_result

    def apply_slipped_collaborative_filtering(self, similarity_type, neighbor_type, time_range):
        from algorithm import CF_NeighborType
        from algorithm import SlippingRangeCollaborativeFiltering
        from structures import RecoResult
        from structures import DataDict, Event
        assert isinstance(neighbor_type, CF_NeighborType)
        assert isinstance(time_range, GrowthTimeRange)

        events_data = self.__data_proxy__.events

        self.log.debug_running('trimming event data from date {} to date {}'.format(
            time_range.start_time.date(), time_range.end_time.date()
        ))
        events_data.trim_between_range(
            attr_tag='date', range_start=time_range.start_time.date(), range_end=time_range.end_time.date(),
            include_start=True, include_end=False, inline=True
        )

        self.log.debug_running('trimming event data by event_type 50/62/63')
        events_data.trim_by_range('event_type', ('50', '62', '63'), inline=True)

        self.log.debug_running('collecting possible neighbor data')
        possible_neighbors = events_data.neighbor_attr_by('reader_id', 'book_id')

        self.log.debug_running('TimeRange.{}'.format(time_range.__class__.__name__))

        stage_tag, stage_list = time_range.growth_stage
        cf_result = RecoResult()
        readers = self.__data_proxy__.readers
        for i in range(len(stage_list)):
            stage = stage_list[i]

            this_event = DataDict(data_type=Event)
            next_event = DataDict(data_type=Event)
            for key, value in events_data.items():
                # assert isinstance(value, Event)
                this_growth = getattr(readers[value.reader_id], stage_tag).__call__(time_range.end_time.date())
                if this_growth is None:
                    continue

                if isinstance(stage, int):
                    if this_growth == stage:
                        this_event[key] = value
                    else:
                        next_event[key] = value
                elif isinstance(stage, tuple):
                    if stage[0] <= this_growth < stage[1]:
                        this_event[key] = value
                    elif this_growth >= stage[1]:
                        next_event[key] = value
                    else:
                        continue
                        # next_event[key] = value
                else:
                    raise RuntimeError

            if len(this_event) == 0:
                continue

            self.log.debug_running('collecting vector data for stage {}'.format(stage))
            # collector = self.__collect_simple_sparse_vector__(
            #     this_event, time_tag='times', finish_length=len(events_data))
            collector = self.__collect_growth_weighted_sparse_vector__(this_event, finish_length=len(events_data))

            # next_collector = self.__collect_simple_sparse_vector__(
            #     next_event, time_tag='times', finish_length=len(events_data))
            next_collector = self.__collect_growth_weighted_sparse_vector__(next_event, len(events_data))
            self.log.debug_running('running CollaborativeFiltering for stage {}'.format(stage))
            this_result = SlippingRangeCollaborativeFiltering(
                collector, next_collector, events_data.group_attr_by('book_id', 'reader_id'), in_memory=True
            ).run(
                neighbor_type=neighbor_type, similarity_type=similarity_type,
                possible_neighbors=possible_neighbors
            )

            cf_result.update(this_result)

        cf_result.to_csv()

        return cf_result

    def apply_refered_slipped_collaborative_filtering(self, similarity_type, neighbor_type, time_range):
        from algorithm import CF_NeighborType
        from algorithm import CollaborativeFiltering
        from structures import RecoResult
        from structures import DataDict, Event
        assert isinstance(neighbor_type, CF_NeighborType)
        assert isinstance(time_range, GrowthTimeRange)

        events_data = self.__data_proxy__.events.to_data_dict()

        self.log.debug_running('trimming event data from date {} to date {}'.format(
            time_range.start_time.date(), time_range.end_time.date()
        ))
        events_data.trim_between_range(
            attr_tag='date', range_start=time_range.start_time.date(), range_end=time_range.end_time.date(),
            include_start=True, include_end=False, inline=True
        )

        self.log.debug_running('trimming event data by event_type 50/62/63')
        events_data.trim_by_range('event_type', ('50', '62', '63'), inline=True)

        self.log.debug_running('collecting possible neighbor data')
        possible_neighbors = events_data.neighbor_attr_by('reader_id', 'book_id')

        self.log.debug_running('TimeRange.{}'.format(time_range.__class__.__name__))

        stage_tag, stage_list = time_range.growth_stage
        cf_result = RecoResult()
        readers = self.__data_proxy__.readers
        for i in range(len(stage_list)):
            stage = stage_list[i]

            this_event = DataDict(data_type=Event)
            for key, value in events_data.items():
                # assert isinstance(value, Event)
                this_growth = getattr(readers[value.reader_id], stage_tag).__call__(time_range.end_time.date())
                if this_growth is None:
                    continue

                if isinstance(stage, int):
                    if this_growth == stage:
                        this_event[key] = value
                elif isinstance(stage, tuple):
                    if stage[0] <= this_growth < stage[1]:
                        this_event[key] = value
                else:
                    raise RuntimeError

            if len(this_event) == 0:
                continue

            self.log.debug_running('collecting vector data for stage {}'.format(stage))
            collector = self.__collect_simple_sparse_vector__(
                this_event, time_tag='times', finish_length=len(events_data)
            )
            self.log.debug_running('running CollaborativeFiltering for stage {}'.format(stage))
            this_result = CollaborativeFiltering(
                collector, events_data.group_attr_by('book_id', 'reader_id'), in_memory=True
            ).run(
                neighbor_type=neighbor_type, similarity_type=similarity_type,
                possible_neighbors=possible_neighbors
            )

            cf_result.update(this_result)

        cf_result.to_csv()

        return cf_result

    def apply_date_back_collaborative_filtering(self, similarity_type, neighbor_type, time_range):
        from algorithm import CF_NeighborType
        from algorithm import DateBackCollaborativeFiltering
        assert isinstance(neighbor_type, CF_NeighborType)
        assert isinstance(time_range, DateBackTimeRange)

        events_data = self.__data_proxy__.events

        self.log.debug_running('trimming event data from date {} to date {}'.format(
            time_range.start_time.date(), time_range.end_time.date()
        ))
        events_data.trim_between_range(
            attr_tag='date', range_start=time_range.start_time.date(), range_end=time_range.end_time.date(),
            include_start=True, include_end=False, inline=True
        )

        self.log.debug_running('trimming event data by event_type 50/62/63')
        events_data.trim_by_range('event_type', ('50', '62', '63'), inline=True)

        self.log.debug_running('collecting possible neighbor data')
        possible_neighbors = events_data.neighbor_attr_by('reader_id', 'book_id')

        self.log.debug_running('TimeRange.{}'.format(time_range.__class__.__name__))

        first_data = events_data.trim_between_range(
            'date', time_range.start_time.date(), time_range.end_first_time.date(), True, False, False
        )

        second_data = events_data.trim_between_range(
            'date', time_range.start_second_time.date(), time_range.end_time.date(), True, False, False
        )

        self.log.debug_running('collecting vector data')
        first_collector = self.__collect_simple_sparse_vector__(
            first_data, time_tag='times', finish_length=len(events_data)
        )
        second_collector = self.__collect_simple_sparse_vector__(
            second_data, time_tag='times', finish_length=len(events_data)
        )

        self.log.debug_running('running CollaborativeFiltering')
        cf_result = DateBackCollaborativeFiltering(
            second_collector, first_collector,
            second_data.group_attr_by('book_id', 'reader_id'),
            first_data.group_attr_by('book_id', 'reader_id'),
            in_memory=True
        ).run(
            neighbor_type=neighbor_type, similarity_type=similarity_type,
            possible_neighbors=possible_neighbors
        )

        cf_result.to_csv()

        return cf_result

    def __collect_simple_sparse_vector__(
            self, data: DataDict, time_tag: str=None, finish_length: int=None
    ):
        result = SparseVectorCollector()

        for value in data.values():
            assert isinstance(value, Event)
            if time_tag is None:
                result.add(value.reader_id, value.book_id)
            else:
                result.add(value.reader_id, value.book_id, getattr(value, time_tag))

        if finish_length is None:
            result.finish(with_length=len(data.collect_attr('book_id')))
        else:
            result.finish(with_length=finish_length)
            self.log.debug_running('collected sparse vector with length {}'.format(finish_length))

        return result

    def __collect_mixed_sparse_vector__(
            self, data: DataDict, ref_date: datetime.date, time_tag: str=None,
    ):
        readers = self.__data_proxy__.readers
        result = SparseVectorCollector()

        for value in data.values():
            assert isinstance(value, Event)
            if time_tag is None:
                result.add(value.reader_id, value.book_id)
            else:
                result.add(value.reader_id, value.book_id, getattr(value, time_tag))

        result.regulate(multiply=0.01)

        for reader_id in list(result.keys()):
            sp_vec = result[reader_id]
            assert isinstance(sp_vec, SparseVector)
            reader = readers[reader_id]
            # assert isinstance(reader, Reader)

            # 注册年份
            if reader.growth_index(ref_date) is None:
                result.data.pop(reader_id)
            else:
                sp_vec.set('growth_index', 1 / reader.growth_index(ref_date))

        result.finish(with_length=len(self.__data_proxy__.books))

        return result

    def __collect_growth_weighted_sparse_vector__(self, data: DataDict, finish_length: int=None):
        readers = self.__data_proxy__.readers
        result = SparseVectorCollector()

        for event in data.values():
            # self.log.debug_variable(event)
            assert isinstance(event, Event)
            reader = readers[event.reader_id]
            if reader.register_date is None:
                continue
            result.add(
                event.reader_id, event.book_id,
                (event.date - reader.register_date) / datetime.timedelta(days=1)
            )
        if finish_length is None:
            result.finish(with_length=len(data.collect_attr('book_id')))
        else:
            result.finish(with_length=finish_length)
        return result

    def __collect_keyword_sparse_vector(self, data: DataDict, finish_length: int=None):
        from structures import BookName
        books, readers = self.__data_proxy__.books, self.__data_proxy__.readers
        keyword_set = set()
        result = SparseVectorCollector()

        for event in data.values():
            assert isinstance(event, Event), str(type(event)) + ': ' + str(event)
            book = books[event.book_id]
            assert isinstance(book, Book)
            reader = readers[event.reader_id]
            assert isinstance(reader, Reader)
            book_name = BookName(book.name)
            for key in book_name.cleaned_list:
                if reader.register_date is None:
                    continue
                keyword_set.add(key)
                # result.add(
                #     event.reader_id, key, (event.date - reader.register_date) / datetime.timedelta(days=1)
                # )
                result.add(event.reader_id, key, 1.0)
        if finish_length is None:
            result.finish(with_length=len(keyword_set))
        else:
            result.finish(with_length=finish_length)
        return result

    def __collect_possible_neighbors_by_keyword__(self, data: DataDict):
        from structures import BookName
        books, readers = self.__data_proxy__.books, self.__data_proxy__.readers

        reader2keyword, keyword2reader = dict(), dict()
        for event in data.values():
            assert isinstance(event, Event), str(type(event)) + ': ' + str(event)
            book = books[event.book_id]
            assert isinstance(book, Book)
            reader = readers[event.reader_id]
            assert isinstance(reader, Reader)
            if event.reader_id not in reader2keyword:
                reader2keyword[event.reader_id] = set()
            book_name = BookName(book.name)
            for key in book_name.cleaned_list:
                if reader.register_date is None:
                    continue
                reader2keyword[event.reader_id].add(key)
                if key not in keyword2reader:
                    keyword2reader[key] = set()
                keyword2reader[key].add(event.reader_id)

        result = dict()
        for reader_id, reader_key_set in reader2keyword.items():
            result[reader_id] = set()
            for reader_key in reader_key_set:
                result[reader_id].update(keyword2reader[reader_key])
            print(len(result[reader_id]))
        return result

    @property
    def log(self):
        return self.__logger__

    def close(self):
        self.__data_proxy__.close()


if __name__ == '__main__':
    import datetime
    from algorithm import CF_NeighborType, CF_SimilarityType

    rule_generator = RuleGeneratorCF()
    rule_generator.log.initiate_time_counter()

    try:
        # running StandardTimeRange
        # this_time_range = StandardTimeRange(start_time=datetime.date(2013, 1, 1), end_time=datetime.date(2013, 7, 1))

        # running GrowthTimeRange
        this_time_range = GrowthTimeRange(start_time=datetime.date(2013, 1, 1), end_time=datetime.date(2013, 7, 1))
        this_time_range.set_growth_stage('growth_index', [(0, 1), (1, 2), (2, 3), (3, 4), (4, 6), (6, 100)])

        # running DateBackTimeRange
        # this_time_range = DateBackTimeRange(datetime.date(2013, 1, 1), datetime.date(2013, 7, 1),
        #                                     datetime.date(2013, 3, 1))

        # this_re = rule_generator.apply_collaborative_filtering(
        #     CF_SimilarityType.Euclidean, CF_NeighborType.All, this_time_range,)

        # this_re = rule_generator.apply_slipped_collaborative_filtering(
        #     CF_SimilarityType.Cosine, CF_NeighborType.All, this_time_range, )

        # this_re = rule_generator.apply_refered_slipped_collaborative_filtering(
        #     CF_SimilarityType.Cosine, CF_NeighborType.All, this_time_range,)

        # this_re = rule_generator.apply_date_back_collaborative_filtering(
        #     CF_SimilarityType.Cosine, CF_NeighborType.All, this_time_range,)

        # this_re = rule_generator.merge_result('2013-06 growth weighted simple.csv', '2013-06 slipped.csv', top_n=10)

        # print(' --- [real time] ---')
        # rule_generator.evaluate_single_result(result_data=this_re, time_range=this_time_range, top_n=20)

        # print('--- [similarity] ---')
        # rule_generator.evaluate_result_similarity(
        #     '2013-06 simple.csv',
        #     '2013-06 date back.csv', )

        rule_generator.evaluate_single_result(
            result_data='2013-2015 slipped CF.csv',
            time_range=this_time_range, top_n=10)

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
        rule_generator.close()
    finally:
        rule_generator.close()

    rule_generator.log.time_sleep(1)
    rule_generator.log.print_time_passed()