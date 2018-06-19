# -*- encoding: UTF-8 -*-
from algorithm import AprioriMethods, CollaborativeFilteringMethods, RecommendMethods
from algorithm.Apriori import Apriori
from algorithm.CollaborativeFiltering import CollaborativeFiltering
from modules.DataProxy import DataProxy
from utils.Logger import get_logger


logger = get_logger(module_name=__file__)


def generate_recommend_result(re_method: RecommendMethods, algo_method, ):
    assert isinstance(algo_method, (AprioriMethods, CollaborativeFilteringMethods))

    data_proxy = DataProxy()

    # cleaned data
    books = data_proxy.get_shelve('books')
    readers = data_proxy.get_shelve('readers')
    events = data_proxy.get_shelve('events')
    inducted_events = data_proxy.get_shelve('inducted_events')

    if re_method == RecommendMethods.CollaborativeFiltering:

        logger.debug_running('RecommendMethods', 'CollaborativeFiltering')

        if algo_method == CollaborativeFilteringMethods.ReaderBase:
            from structures.Reader import Reader
            logger.debug_running('CollaborativeFilteringMethods', 'ReaderBase')

            reader_attributes = data_proxy.get_shelve('reader_attributes')

            rule_generator = CollaborativeFiltering(reader_attributes, Reader)

        # CollaborativeFilteringMethods.BookBase
        elif algo_method == CollaborativeFilteringMethods.BookBase:
            from structures.Book import Book
            logger.debug_running('CollaborativeFilteringMethods', 'BookBase')

            book_attributes = data_proxy.get_shelve('book_attributes')
        else:
            raise RuntimeError

    elif re_method == RecommendMethods.Apriori:

        logger.debug_running('RecommendMethods', 'Apriori')

        if algo_method == AprioriMethods.Basic:
            pass
        elif algo_method == AprioriMethods.GroupByReaderCollege:
            pass
        else:
            raise NotImplementedError

    else:
        raise RuntimeError
