# -*- encoding: UTF-8 -*-
from tqdm import tqdm

from algorithm import AprioriMethods, CollaborativeFilteringMethods, RecommendMethods
from algorithm.CollaborativeFiltering import CollaborativeFiltering, NeighborType, SimilarityType
from modules.DataProxy import DataProxy
from utils import get_logger


logger = get_logger(module_name=__file__)


def generate_recommend_result(re_method: RecommendMethods, algo_method, **kwargs):
    """

    :param re_method:
    :param algo_method:
    :param kwargs:
        neighbor_type: NeighborType
        sim_type: SimilarityType
        max_length: int,
    :return:
    """
    from utils.FileSupport import save_csv
    assert isinstance(algo_method, (AprioriMethods, CollaborativeFilteringMethods))

    data_proxy = DataProxy()

    # cleaned data
    # books = data_proxy.get_shelve('books')
    # readers = data_proxy.get_shelve('readers')
    # events = data_proxy.get_shelve('events')
    # inducted_events = data_proxy.get_shelve('inducted_events')

    if re_method == RecommendMethods.CollaborativeFiltering:

        logger.debug_running('RecommendMethods', 'CollaborativeFiltering')

        if algo_method == CollaborativeFilteringMethods.ReaderBase:
            from structures.Reader import Reader
            logger.debug_running('CollaborativeFilteringMethods', 'ReaderBase')

            reader_attributes = data_proxy.get_shelve('reader_attributes')
            # book2reader = DataProxy.get_shelve('readers_group_by_books')
            reader2book = DataProxy.get_shelve('books_group_by_readers')
            neighbor_type = kwargs.get('neighbor_type', NeighborType.All)
            sim_type = kwargs.get('sim_type', SimilarityType.Euclidean)
            max_length = kwargs.get('max_length', 10)

            rule_generator = CollaborativeFiltering(reader_attributes, Reader)

            result = rule_generator.run(
                neighbor_type=neighbor_type, similarity_type=sim_type,
            )

            # sorting and selecting books
            result_list = list()
            for reader_id in tqdm(result.keys(), desc='finding books'):
                recommend_list = list()
                this_selected = reader2book[reader_id]
                assert isinstance(this_selected, set)
                for simi_reader in result[reader_id]:
                    for item in reader2book[simi_reader]:
                        # assert isinstance(reader2book[simi_reader], set)
                        if item not in this_selected and item not in recommend_list:
                            recommend_list.append(item)
                        if len(recommend_list) >= max_length:
                            break
                    if len(recommend_list) >= max_length:
                        break
                # recommend_list = [books[var].book_name for var in recommend_list]  # getting book names
                recommend_list.insert(0, reader_id)
                result_list.append(recommend_list)
            save_csv(
                result_list,
                'CollaborativeFilteringMethods.ReaderBase_NeighborType.{}_SimilarityType.{}'.format(
                    neighbor_type.name, sim_type.name
                )
            )

        # CollaborativeFilteringMethods.BookBase
        elif algo_method == CollaborativeFilteringMethods.BookBase:
            from structures import Book
            logger.debug_running('CollaborativeFilteringMethods', 'BookBase')

            book_attributes = data_proxy.get_shelve('book_attributes')

            rule_generator = CollaborativeFiltering(book_attributes, Book)

            result = rule_generator.run(
                neighbor_type=NeighborType.All, similarity_type=SimilarityType.Euclidean,
            )
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


if __name__ == '__main__':
    generate_recommend_result(
        re_method=RecommendMethods.CollaborativeFiltering,
        algo_method=CollaborativeFilteringMethods.ReaderBase,
    )
