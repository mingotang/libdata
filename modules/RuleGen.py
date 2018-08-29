# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os
import time

from Config import DataConfig
from modules.DataProxy import DataProxy
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
        from algorithm import CollaborativeFiltering, SparseVectorCollector
        assert isinstance(base_type, CF_BaseType)
        assert isinstance(neighbor_type, CF_NeighborType)
        assert isinstance(time_range, (StandardTimeRange, GrowthTimeRange))

        self.log.debug_running('CF_BaseType.{}'.format(base_type.name), 'begin')
        if base_type == CF_BaseType.ReaderBase:
            events_data = self.__data_proxy__.events.to_data_dict()

            self.log.debug_running('TimeRange.{}'.format(time_range.__class__.__name__), 'trimming data')
            if isinstance(time_range, StandardTimeRange):
                events_data.trim_between_range(
                    attr_tag='date', range_start=time_range.start_time.date(), range_end=time_range.end_time.date(),
                    include_start=True, include_end=False, inline=True
                )
            elif isinstance(time_range, GrowthTimeRange):
                raise NotImplementedError
            else:
                raise RuntimeError
            events_data.trim_by_range('event_type', ('50', '62', '63'))

            self.log.debug_running('collecting possible neighbor data')
            reader2books_index = events_data.group_attr_by(group_attr='book_id', by_attr='reader_id')
            book2readers_index = events_data.group_attr_by(group_attr='reader_id', by_attr='book_id')
            possible_neighbors = dict()
            for reader_id in reader2books_index:
                possible_neighbors[reader_id] = set()
                for book_id in reader2books_index[reader_id]:
                    possible_neighbors[reader_id].update(book2readers_index[book_id])

            self.log.debug_running('collecting vector data')
            book_set = events_data.collect_attr('book_id')
            collector = SparseVectorCollector()
            for event in events_data.values():
                from structures import Event
                assert isinstance(event, Event)
                collector.add(event.reader_id, event.book_id, times=event.times)
            collector.finish(with_length=len(book_set))
        elif base_type == CF_BaseType.BookBase:
            raise NotImplementedError
        else:
            raise RuntimeError

        cf_go = CollaborativeFiltering(collector, in_memory=True)
        cf_result = cf_go.run(
            neighbor_type=neighbor_type, similarity_type=similarity_type,
            possible_neighbors=possible_neighbors
        )
        cf_result.to_csv()

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


def apply_collaborative_filtering(
        method,
        neighbor_type,
        simi_func, **kwargs
):
    from tqdm import tqdm
    from algorithm.CollaborativeFiltering import CollaborativeFiltering
    from structures import Book
    from structures.Reader import Reader
    from utils.FileSupport import save_csv

    max_length = kwargs.get('max_length', 10)

    books_by_reader = DataProxy.get_shelve('books_group_by_readers')
    readers_by_book = DataProxy.get_shelve('readers_group_by_books')

    if method == CF_BaseType.ReaderBase:
        # calculating similarity
        logger.debug_running('CollaborativeFilteringMethods.ReaderBase', 'begin')
        reader_attributes = DataProxy.get_shelve('reader_attributes')

        cf_generator = CollaborativeFiltering(reader_attributes, Reader)
        simi_result = cf_generator.run(
            neighbor_type=CF_NeighborType.All,
            similarity_type=simi_func,
        )

        # sorting and selecting books
        result_list = list()
        for reader_id in tqdm(simi_result.keys(), desc='finding books'):
            recommend_list = list()
            # recommend_list.append(reader)
            this_selected = books_by_reader[reader_id]
            assert isinstance(this_selected, set)
            for simi_reader in simi_result[reader_id]:
                for item in books_by_reader[simi_reader]:
                    assert isinstance(books_by_reader[simi_reader], set)
                    if item not in this_selected and item not in recommend_list:
                        recommend_list.append(item)
                    if len(recommend_list) >= max_length:
                        break
                if len(recommend_list) >= max_length:
                    break
            # recommend_list = [books[var].book_name for var in recommend_list]  # getting book names
            recommend_list.insert(0, reader_id)
            result_list.append(recommend_list)
        save_csv(result_list, 'CollaborativeFilteringMethods.ReaderBase')

        logger.debug_running('CollaborativeFilteringMethods.ReaderBase', 'end')
    elif method == CF_BaseType.BookBase:
        # calculating similarity
        logger.debug_running('CollaborativeFilteringMethods.BookBase', 'begin')
        book_attributes = DataProxy.get_shelve('book_attributes')

        cf_generator = CollaborativeFiltering(book_attributes, Book)
        simi_result = cf_generator.run(
            neighbor_type=CF_NeighborType.All,
            similarity_type=simi_func,
        )

        # sorting and selecting books
        result_list = list()
        for book_id in tqdm(simi_result.keys(), desc='finding books'):
            recommend_list = list()
            this_selected = books_by_reader[book_id]
            assert isinstance(this_selected, set)
            simi_books = simi_result[book_id]
            if len(simi_books) > max_length:
                recommend_list.extend(simi_books[:max_length])
            else:
                recommend_list.extend(simi_books)
            # recommend_list = [books[var].book_name for var in recommend_list]  # getting book names
            recommend_list.insert(0, book_id)
            result_list.append(recommend_list)

        save_csv(result_list, 'CollaborativeFilteringMethods.BookBase')
        logger.debug_running('CollaborativeFilteringMethods.BookBase', 'end')
    else:
        raise NotImplementedError


if __name__ == '__main__':
    import datetime
    from algorithm import CF_BaseType, CF_NeighborType, CF_SimilarityType

    rule_generator = RuleGenerator()
    rule_generator.log.initiate_time_counter()

    rule_generator.apply_collaborative_filtering(
        base_type=CF_BaseType.ReaderBase,
        similarity_type=CF_SimilarityType.Cosine,
        neighbor_type=CF_NeighborType.All,
        time_range=StandardTimeRange(start_time=datetime.date(2013, 1, 1), end_time=datetime.date(2014, 1, 1))
    )

    rule_generator.log.time_sleep(1)
    rule_generator.log.print_time_passed()
