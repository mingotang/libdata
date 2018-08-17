# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os
import time

from Config import DataConfig, DBName
from algorithm import AprioriMethods, CollaborativeFilteringMethods, RecommendMethods
from algorithm.CollaborativeFiltering import NeighborType, SimilarityType
from modules.DataProxy import DataProxy
from structures import ShelveWrapper


class RuleGenerator(object):
    def __init__(self, data_path: str=DataConfig.data_path, operation_path: str=DataConfig.operation_path):
        from modules.DataProxy import DataProxy
        from structures import InductedEvents
        from structures import TextRecorder
        from utils import get_logger
        self.__logger__ = get_logger(self.__class__.__name__)

        self.__data_path__ = data_path
        self.__operation_path__ = operation_path

        self.__recorder__ = TextRecorder()
        # self.__persister__ =

        self.__data_proxy__ = DataProxy(data_path=self.__data_path__)
        self.__inducted_events__ = InductedEvents(DBName.inducted_events)

    def apply(self, method: RecommendMethods, logic_method,
              **kwargs):
        if method == RecommendMethods.Apriori:
            # self.log.debug_running('{}.apply RecommendMethods.Apriori', 'begin')
            # assert isinstance(logic_method, AprioriMethods)
            # self.log.debug_running('{}.apply RecommendMethods.Apriori', 'end')
            raise NotImplementedError
        elif method == RecommendMethods.CollaborativeFiltering:
            self.log.debug_running('{}.apply RecommendMethods.CollaborativeFiltering', 'begin')
            assert isinstance(logic_method, CollaborativeFilteringMethods)
            self.log.debug_running('{}.apply RecommendMethods.CollaborativeFiltering', 'end')
        else:
            raise RuntimeError

    def __apply_apriori__(self, logic_method: AprioriMethods):
        from algorithm.Apriori import Apriori
        from algorithm import collect_baskets

        if method == AprioriMethods.Basic:
            events_dict = DataProxy.get_shelve('events')

            logger.debug_running('collecting baskets', 'begin')
            basket = collect_baskets(events_dict, 'index')  # '/Users/mingo/Downloads/basket_dict'
            logger.debug_running('collecting baskets', 'end')

            apri_inst = Apriori(basket, force_origin=True)

            while True:
                min_support = kwargs.get('min_support', 0.1)

                logger.debug_running('Apriori rules for', 'min_support={0:.2f}: '.format(min_support))
                result = apri_inst.run(min_support=min_support)

                while True:
                    min_conf = kwargs.get('min_conf', 0.2)

                    result.show_results(min_conf)
                    print('Max rules: {0:d}'.format(len(result.generate_rules(min_conf=0.0001))))
                    config = input('Are you satisfied with the result? (y/n)  ')
                    if config.lower() == 'y':
                        break
                    elif config.lower() == 'n':
                        min_conf = float(input('Please input new min_conf:  '))
                    else:
                        continue
                config = input('Are you satisfied with the results above? (y/n)  ')
                if config.lower() == 'y':
                    break
                elif config.lower() == 'n':
                    min_support = float(input('Please input new min_support:  '))
                else:
                    continue
        elif method == AprioriMethods.GroupByReaderCollege:
            logger.debug_running('AprioriMethods.GroupByReaderCollege', 'start')

            readers_in_college = DataProxy.get_shelve('readers_group_by_college')
            events_dict = DataProxy.get_shelve('events')

            for college in readers_in_college.keys():
                reader_set = readers_in_college[college]

                logger.debug_running('collecting baskets for {}'.format(college), 'begin')
                events_list = list()
                for event in events_dict.values():
                    assert isinstance(event, Event)
                    if event.reader_id in reader_set:
                        events_list.append(event)
                basket = collect_baskets(events_list, 'book_name')  # '/Users/mingo/Downloads/basket_dict'
                del events_list
                logger.debug_running('collecting baskets for {}'.format(college), 'end')

                apri_inst = Apriori(basket, force_origin=True, depth=2)

                min_support = kwargs.get('min_support', 0.5)
                min_conf = kwargs.get('min_conf', 0.6)

                # while True:
                for min_support in [
                    0.5, 0.4, 0.3, 0.2, 0.15,  # 0.1,  # 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01,
                ]:
                    logger.debug_running('Apriori rules for', 'min_support={0:.2f}: '.format(min_support))

                    tp_01 = time.time()
                    result = apri_inst.run(min_support=min_support)
                    result.generate_rules(min_conf=min_conf)
                    tp_02 = time.time()
                    if len(result.generate_rules(min_conf=min_conf)) > 20 or tp_02 - tp_01 > 10:
                        result.save_rules(min_conf, college)
                        break
                    else:
                        continue
                # result.save_rules(min_conf, college)
                del readers_in_college[college]
                # result.save_rules(min_conf, college)
                # time.sleep(1)
                # break
                # print('rules number: {0:d}'.format(len(result.generate_rules(min_conf=min_conf))))

                # while True:
                #     result.show_results(min_conf)
                #     time.sleep(1)
                #     print('Max rules: {0:d}'.format(len(result.generate_rules(min_conf=0.0001))))
                # config = input('Are you satisfied with the result? (y/n)  ')
                # if config.lower() == 'y':
                #     break
                # elif config.lower() == 'n':
                #     min_conf = float(input('Please input new min_conf:  '))
                # else:
                #     continue
                # config = input('Are you satisfied with the results above? (y/n)  ')
                # if config.lower() == 'y':
                #     result.save_rules(min_conf, college)
                #     break
                # else:
                #     min_support = float(input('Please input new min_support:  '))
            logger.debug_running('AprioriMethods.GroupByReaderCollege', 'end')
        else:
            raise NotImplementedError

    def get_shelve(self, db_name: str, new=False):
        """get shelve db from operation path -> ShelveWrapper"""
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
        method: CollaborativeFilteringMethods,
        neighbor_type: NeighborType,
        simi_func: SimilarityType, **kwargs
):
    from tqdm import tqdm
    from algorithm.CollaborativeFiltering import CollaborativeFiltering
    from structures import Book
    from structures.Reader import Reader
    from utils.FileSupport import save_csv

    max_length = kwargs.get('max_length', 10)

    books_by_reader = DataProxy.get_shelve('books_group_by_readers')
    readers_by_book = DataProxy.get_shelve('readers_group_by_books')

    if method == CollaborativeFilteringMethods.ReaderBase:
        # calculating similarity
        logger.debug_running('CollaborativeFilteringMethods.ReaderBase', 'begin')
        reader_attributes = DataProxy.get_shelve('reader_attributes')

        cf_generator = CollaborativeFiltering(reader_attributes, Reader)
        simi_result = cf_generator.run(
            neighbor_type=NeighborType.All,
            sim_type=simi_func,
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
    elif method == CollaborativeFilteringMethods.BookBase:
        # calculating similarity
        logger.debug_running('CollaborativeFilteringMethods.BookBase', 'begin')
        book_attributes = DataProxy.get_shelve('book_attributes')

        cf_generator = CollaborativeFiltering(book_attributes, Book)
        simi_result = cf_generator.run(
            neighbor_type=NeighborType.All,
            sim_type=simi_func,
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
    from algorithm.CollaborativeFiltering import NeighborType, SimilarityType

    logger.initiate_time_counter()
    apply_apriori(AprioriMethods.GroupByReaderCollege)
    apply_collaborative_filtering(
        CollaborativeFilteringMethods.ReaderBase,
        neighbor_type=NeighborType.All,
        simi_func=SimilarityType.Cosine,
    )

    logger.print_time_passed()
