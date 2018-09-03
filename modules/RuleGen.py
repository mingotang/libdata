# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os

from Config import DataConfig
from structures import StandardTimeRange, GrowthTimeRange


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
        assert isinstance(time_range, (StandardTimeRange, GrowthTimeRange))

        self.log.debug_running('CF_BaseType.{}'.format(base_type.name))
        if base_type == CF_BaseType.ReaderBase:
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

            self.log.debug_running('TimeRange.{}'.format(time_range.__class__.__name__))
            if isinstance(time_range, StandardTimeRange):

                self.log.debug_running('collecting possible neighbor data')
                possible_neighbors = events_data.neighbor_attr_by('reader_id', 'book_id')

                self.log.debug_running('collecting vector data')
                collector = self.__collect_simple_sparse_vector__(
                    events_data, 'reader_id', 'book_id', time_tag='times'
                )

                self.log.debug_running('running CollaborativeFiltering')
                cf_result = CollaborativeFiltering(collector, in_memory=True).run(
                    neighbor_type=neighbor_type, similarity_type=similarity_type, possible_neighbors=possible_neighbors
                )

            elif isinstance(time_range, GrowthTimeRange):
                from algorithm.CollaborativeFiltering import CFResult
                stage_tag, stage_list = time_range.growth_stage
                cf_result = CFResult()
                for stage in stage_list:
                    self.log.debug_running('trimming event data by stage {}'.format(stage))
                    if isinstance(stage, int):
                        this_events = events_data.trim_by_range(stage_tag, (stage, ))
                    elif isinstance(stage, tuple):
                        this_events = events_data.trim_between_range(stage_tag, stage[0], stage[1])
                    else:
                        raise RuntimeError
            else:
                raise TypeError

            cf_result.to_csv()

            return cf_result

        elif base_type == CF_BaseType.BookBase:
            raise NotImplementedError
        else:
            raise RuntimeError

    def __collect_simple_sparse_vector__(self, data, key_tag: str, attr_tag: str, time_tag: str=None):
        from algorithm import SparseVectorCollector
        from structures import DataDict
        assert isinstance(data, DataDict)

        result = SparseVectorCollector()
        for value in data.values():
            if time_tag is None:
                result.add(getattr(value, key_tag), getattr(value, attr_tag))
            else:
                result.add(getattr(value, key_tag), getattr(value, attr_tag), getattr(value, time_tag))
        result.finish(with_length=len(data.collect_attr(attr_tag)))

        return result

    def get_shelve(self, db_name: str, new=False):
        """get shelve db from operation path -> ShelveWrapper"""
        from structures import ShelveWrapper
        if new is False:
            if os.path.exists(os.path.join(self.__operation_path__, db_name)):
                return ShelveWrapper(os.path.join(self.__operation_path__, db_name))
            else:
                raise FileNotFoundError(
                    'Shelve database {} not exists.'.format(os.path.join(self.__operation_path__, db_name))
                )
        else:
            return ShelveWrapper.init_from(None, os.path.join(self.__operation_path__, db_name))

    def get_shelve_dict(self, db_name: str):
        from structures import ShelveWrapper
        if os.path.exists(os.path.join(self.__operation_path__, db_name)):
            return ShelveWrapper.get_data_dict(os.path.join(self.__operation_path__, db_name))
        else:
            raise FileNotFoundError(
                'Shelve database {} not exists.'.format(os.path.join(self.__operation_path__, db_name))
            )

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
        rule_generator.apply_collaborative_filtering(
            base_type=CF_BaseType.ReaderBase,
            similarity_type=CF_SimilarityType.Cosine,
            neighbor_type=CF_NeighborType.All,
            time_range=StandardTimeRange(start_time=datetime.date(2013, 1, 1), end_time=datetime.date(2014, 1, 1))
        )
    except KeyboardInterrupt:
        rule_generator.close()
    finally:
        rule_generator.close()

    rule_generator.log.time_sleep(1)
    rule_generator.log.print_time_passed()
