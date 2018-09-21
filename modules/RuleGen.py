# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import datetime
from Config import DataConfig
from structures import StandardTimeRange, GrowthTimeRange, DateBackTimeRange


class RuleGenerator(object):
    def __init__(self, data_path: str=DataConfig.data_path, operation_path: str=DataConfig.operation_path):
        from modules.DataProxy import DataProxy
        from structures import TextRecorder
        from utils import get_logger
        self.__logger__ = get_logger(self.__class__.__name__)

        self.__data_path__ = data_path
        self.__operation_path__ = operation_path

        self.__recorder__ = TextRecorder()

        self.__data_proxy__ = DataProxy(data_path=self.__data_path__)

    def apply_collaborative_filtering(self, base_type, similarity_type, neighbor_type, time_range):
        from algorithm import CF_BaseType, CF_NeighborType
        from algorithm import CollaborativeFiltering
        assert isinstance(base_type, CF_BaseType)
        assert isinstance(neighbor_type, CF_NeighborType)
        assert isinstance(time_range, StandardTimeRange)

        self.log.debug_running('CF_BaseType.{}'.format(base_type.name))
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

        self.log.debug_running('collecting vector data')
        collector = self.__collect_mixed_sparse_vector__(
            events_data, 'reader_id', 'book_id', ref_date=time_range.end_time.date(), time_tag='times',
        )
        # collector = self.__collect_simple_sparse_vector__(
        #     events_data, 'reader_id', 'book_id', time_tag='times',
        # )

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

    def apply_slipped_collaborative_filtering(self, base_type, similarity_type, neighbor_type, time_range):
        from algorithm import CF_BaseType, CF_NeighborType
        from algorithm import SlippingRangeCollaborativeFiltering
        from structures import RecoResult
        from structures import DataDict, Event
        assert isinstance(base_type, CF_BaseType)
        assert isinstance(neighbor_type, CF_NeighborType)
        assert isinstance(time_range, GrowthTimeRange)

        self.log.debug_running('CF_BaseType.{}'.format(base_type.name))
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
                    else:
                        next_event[key] = value
                else:
                    raise RuntimeError

            if len(this_event) == 0:
                continue

            self.log.debug_running('collecting vector data for stage {}'.format(stage))
            collector = self.__collect_simple_sparse_vector__(
                this_event, 'reader_id', 'book_id', time_tag='times', finish_length=len(events_data)
            )

            next_collector = self.__collect_simple_sparse_vector__(
                next_event, 'reader_id', 'book_id', time_tag='times', finish_length=len(events_data)
            )
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

    def apply_date_back_collaborative_filtering(self, base_type, similarity_type, neighbor_type, time_range):
        from algorithm import CF_BaseType, CF_NeighborType
        from algorithm import DateBackCollaborativeFiltering
        assert isinstance(base_type, CF_BaseType)
        assert isinstance(neighbor_type, CF_NeighborType)
        assert isinstance(time_range, DateBackTimeRange)

        self.log.debug_running('CF_BaseType.{}'.format(base_type.name))
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

        first_data = events_data.trim_between_range(
            'date', time_range.start_time.date(), time_range.end_first_time.date(), True, False, False
        )

        second_data = events_data.trim_between_range(
            'date', time_range.start_second_time.date(), time_range.end_time.date(), True, False, False
        )

        self.log.debug_running('collecting vector data')
        first_collector = self.__collect_simple_sparse_vector__(
            first_data, 'reader_id', 'book_id', time_tag='times', finish_length=len(events_data)
        )
        second_collector = self.__collect_simple_sparse_vector__(
            second_data, 'reader_id', 'book_id', time_tag='times', finish_length=len(events_data)
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
            self, data, key_tag: str, attr_tag: str, time_tag: str=None, finish_length: int=None
    ):
        from algorithm import SparseVectorCollector
        from structures import DataDict
        assert isinstance(data, DataDict)

        result = SparseVectorCollector()

        for value in data.values():
            if time_tag is None:
                result.add(getattr(value, key_tag), getattr(value, attr_tag))
            else:
                result.add(getattr(value, key_tag), getattr(value, attr_tag), getattr(value, time_tag))

        if finish_length is None:
            result.finish(with_length=len(data.collect_attr(attr_tag)))
        else:
            result.finish(with_length=finish_length)
            self.log.debug_running('collected sparse vector with length {}'.format(finish_length))

        return result

    def __collect_mixed_sparse_vector__(
            self, data, key_tag: str, attr_tag: str, ref_date: datetime.date, time_tag: str=None,
    ):
        from algorithm import SparseVectorCollector
        from structures import DataDict, Reader, SparseVector
        assert isinstance(data, DataDict)

        readers = self.__data_proxy__.readers

        result = SparseVectorCollector()

        for value in data.values():
            if time_tag is None:
                result.add(getattr(value, key_tag), getattr(value, attr_tag))
            else:
                result.add(getattr(value, key_tag), getattr(value, attr_tag), getattr(value, time_tag))

        result.regulate(multiply=0.01)

        for reader_id in list(result.keys()):
            sp_vec = result[reader_id]
            assert isinstance(sp_vec, SparseVector)
            reader = readers[reader_id]
            assert isinstance(reader, Reader)

            # 注册年份
            if reader.growth_index(ref_date) is None:
                result.data.pop(reader_id)
            else:
                sp_vec.set('growth_index', 100000 / reader.growth_index(ref_date))

        result.finish(with_length=len(self.__data_proxy__.books))

        return result


    def evaluate_single_result(self, result_data, time_range):
        import os
        from structures import Evaluator, RecoResult, TimeRange
        assert isinstance(time_range, TimeRange)

        if isinstance(result_data, str):
            result_data = os.path.join(DataConfig.operation_path, result_data)
            result = RecoResult.load_csv(result_data).derive_top(10)
        elif isinstance(result_data, RecoResult):
            result = result_data.derive_top(10)
        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('result_data', (str, RecoResult), result_data)

        actual_data = dict()
        inducted_events = self.__data_proxy__.inducted_events.to_dict()
        for reco_key, events_list in inducted_events.items():
            from structures import OrderedList
            assert isinstance(events_list, OrderedList)
            events_list = events_list.trim_between_range(
                'date', time_range.start_time.date(), time_range.start_time.date() + datetime.timedelta(days=300)
            ).to_attr_list('book_id')
            actual_data[reco_key] = events_list

        evaluator = Evaluator(actual_data=actual_data, predicted_data=result)
        print(evaluator.match_percentage)
        print(evaluator.top_n_accuracy(100))
        print(evaluator.coverage_i_top_n_accuracy(10, 100))
        print(evaluator.coverage_i_top_n_accuracy(100, 100))

    @property
    def log(self):
        return self.__logger__

    def close(self):
        self.__data_proxy__.close()


if __name__ == '__main__':
    import datetime
    from algorithm import CF_BaseType, CF_NeighborType, CF_SimilarityType

    rule_generator = RuleGenerator()
    rule_generator.log.initiate_time_counter()

    try:
        # running StandardTimeRange
        # this_time_range = StandardTimeRange(start_time=datetime.date(2013, 1, 1), end_time=datetime.date(2015, 1, 1))

        # running GrowthTimeRange
        this_time_range = GrowthTimeRange(start_time=datetime.date(2013, 1, 1), end_time=datetime.date(2015, 1, 1))
        this_time_range.set_growth_stage('growth_index', [(0, 1), (1, 2), (2, 3), (3, 4), (4, 6), (6, 100)])

        # running DateBackTimeRange
        # this_time_range = DateBackTimeRange(datetime.date(2013, 1, 1), datetime.date(2014, 1, 1), datetime.date(2013, 7, 1))

        # this_re = rule_generator.apply_collaborative_filtering(
        #     CF_BaseType.ReaderBase, CF_SimilarityType.Cosine,
        #     CF_NeighborType.All, this_time_range,)

        this_re = rule_generator.apply_slipped_collaborative_filtering(
            CF_BaseType.ReaderBase, CF_SimilarityType.Cosine,
            CF_NeighborType.All, this_time_range,)

        # this_re = rule_generator.apply_date_back_collaborative_filtering(
        #     CF_BaseType.ReaderBase, CF_SimilarityType.Cosine,
        #     CF_NeighborType.All, this_time_range,)

        print(' --- [] ---')
        rule_generator.evaluate_single_result(result_data=this_re, time_range=this_time_range)

        # print('--- [standard timerange] ---')
        # rule_generator.evaluate_single_result(
        #     result_data='cf_result_20180921_135227.csv',
        #     time_range=this_time_range, )
        # print('--- [standard timerange] ---')
        # rule_generator.evaluate_single_result(
        #     result_data='cf_result_20180920_215921 standard timerange 2013-2014.csv',
        #     time_range=this_time_range
        # )
        # print('--- [growth timerange] ---')
        # rule_generator.evaluate_single_result(
        #     result_data='cf_result_20180921_133542.csv',
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
