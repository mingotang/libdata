# -*- encoding: UTF-8 -*-
import datetime

from extended import DataDict
from algorithm.CollaborativeFiltering import CF_NeighborType, CF_SimilarityType
from modules.RuleGen import RuleGenerator
from structures import Book, Event, Reader
from structures import RecoResult, SparseVector
from structures import StandardTimeRange, GrowthTimeRange, DateBackTimeRange


class RuleGenCF(RuleGenerator):
    def __init__(self):
        RuleGenerator.__init__(self)

    def apply_collaborative_filtering(self, time_range):
        from algorithm.CollaborativeFiltering import CollaborativeFiltering
        assert isinstance(time_range, StandardTimeRange)

        events_data = self.env.data_proxy.events
        self.log.debug_running('trimming event data from date {} to date {}'.format(
            time_range.start_time.date(), time_range.end_time.date()))
        events_data.trim_include_between_attr_value(
            attr_tag='date', range_start=time_range.start_time.date(), range_end=time_range.end_time.date(),
            include_start=True, include_end=False, inline=True, )

        self.log.debug_running('trimming event data by event_type 50/62/63')
        events_data.trim_include_by_attr_value('event_type', ('50', '62', '63'), inline=True)

        cf_result = CollaborativeFiltering(events_data).set_relation_tag('reader_id', 'book_id')
        cf_result.set_neighbor_type(CF_NeighborType.FixSize).set_similarity_type(CF_SimilarityType.Cosine)
        cf_result.set_item_vector_value_tag('times')
        cf_result = cf_result.run(fixed_size=5, max_recommend_list=100)

        readers = self.env.data_proxy.readers
        for key in list(cf_result.keys()):
            reader = readers[key]
            from structures import Reader
            assert isinstance(reader, Reader)
            if reader.growth_index(time_range.end_time.date()) is None:
                cf_result.pop(key)
        cf_result.to_csv()
        return cf_result

    def apply_slipped_collaborative_filtering(self, time_range):
        from algorithm.CollaborativeFiltering import SlippingRangeCollaborativeFiltering
        assert isinstance(time_range, GrowthTimeRange)

        self.log.debug_running('trimming event data from date {} to date {}'.format(
            time_range.start_time.date(), time_range.end_time.date()
        ))
        self.log.debug_running('trimming event data by event_type 50/62/63')
        events_data = self.env.data_proxy.events.trim_between_range(
            attr_tag='date', range_start=time_range.start_time.date(), range_end=time_range.end_time.date(),
            include_start=True, include_end=False, inline=True
        ).trim_by_range('event_type', ('50', '62', '63'), inline=True)

        self.log.debug_running('TimeRange.{}'.format(time_range.__class__.__name__))

        stage_tag, stage_list = time_range.growth_stage
        cf_result = RecoResult()
        readers = self.env.data_proxy.readers
        for i in range(len(stage_list)):
            stage = stage_list[i]

            this_event = DataDict()
            next_event = DataDict()
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
            srcf = SlippingRangeCollaborativeFiltering(this_event, next_event).set_relation_tag('reader_id', 'book_id')
            srcf.set_neighbor_type(CF_NeighborType.FixSize).set_similarity_type(CF_SimilarityType.Cosine)
            srcf.set_item_vector_value_tag('times')
            cf_result.update(srcf.run(fixed_size=5, max_recommend_list=100))

        cf_result.to_csv()

        return cf_result

    def apply_refered_slipped_collaborative_filtering(self, similarity_type, neighbor_type, time_range):
        from algorithm import CollaborativeFiltering
        from structures import RecoResult
        assert isinstance(neighbor_type, CF_NeighborType)
        assert isinstance(time_range, GrowthTimeRange)

        # events_data = self.__data_proxy__.events.to_data_dict()

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

            this_event = DataDict()
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
                collector, events_data.group_attr_set_by('book_id', 'reader_id'), in_memory=True
            ).run(
                neighbor_type=neighbor_type, similarity_type=similarity_type,
                possible_neighbors=possible_neighbors
            )

            cf_result.update(this_result)

        cf_result.to_csv()

        return cf_result

    def apply_date_back_collaborative_filtering(self, similarity_type, neighbor_type, time_range):
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
            second_data.group_attr_set_by('book_id', 'reader_id'),
            first_data.group_attr_set_by('book_id', 'reader_id'),
            in_memory=True
        ).run(
            neighbor_type=neighbor_type, similarity_type=similarity_type,
            possible_neighbors=possible_neighbors
        )

        cf_result.to_csv()

        return cf_result

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
        this_time_range = StandardTimeRange(start_time=datetime.date(2013, 1, 1), end_time=datetime.date(2013, 7, 1))

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

        rule_generator.log.info(' --- [real time] ---')
        rule_generator.evaluate_single_result(result_data=this_re, time_range=this_time_range, top_n=20)

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
        rule_generator.close()
    finally:
        rule_generator.close()

    rule_generator.log.time_sleep(1)
    rule_generator.log.print_time_passed()
