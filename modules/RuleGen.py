# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging
import time
import os

from types import FunctionType

from utils.Constants import BaseEnum


__ = logging.debug


class AprioriMethods(BaseEnum):
    Basic = 'ReaderIDAsBuyer_BookIDAsGoods'
    GroupByReaderCollege = 'ReaderIDAsBuyer_BookIDAsGoods-GroupByReaderCollege'


class CollaborativeFilteringMethods(BaseEnum):
    ReaderBase = 'ReaderBase'
    BookBase = 'BookBase'


# --------------------------------------------------------
def apply_apriori(method: AprioriMethods, **kwargs):
    """

    :param method:
    :return:
    """
    from algorithm.Apriori import Apriori
    from modules.Functions import collect_baskets
    from structures.Event import Event
    if method == AprioriMethods.Basic:
        __(LogInfo.running('AprioriMethods.Basic', 'start'))

        events_dict = get_pdict('events')

        __(LogInfo.running('collecting baskets', 'begin'))
        basket = collect_baskets(events_dict, 'index')  # '/Users/mingo/Downloads/basket_dict'
        __(LogInfo.running('collecting baskets', 'end'))

        __(LogInfo.running('initiate apriori', 'begin'))
        apri_inst = Apriori(basket, force_origin=True)
        __(LogInfo.running('initiate apriori', 'end'))

        while True:
            min_support = kwargs.get('min_support', 0.1)

            __(LogInfo.running('Apriori rules for', 'min_support={0:.2f}: '.format(min_support)))
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
        __(LogInfo.running('AprioriMethods.GroupByReaderCollege', 'start'))

        # events_dict = Pdict(os.path.join(DataConfig.persisted_data_path, 'events'), keep_history=True)
        readers_in_college = get_pdict('readers_group_by_college')
        events_dict = load_pickle('events')

        for college in readers_in_college.keys():
            reader_set = readers_in_college[college]

            __(LogInfo.running('collecting baskets for {}'.format(college), 'begin'))
            events_list = list()
            for event in events_dict.values():
                assert isinstance(event, Event)
                if event.reader_id in reader_set:
                    events_list.append(event)
            basket = collect_baskets(events_list, 'book_name')  # '/Users/mingo/Downloads/basket_dict'
            del events_list
            __(LogInfo.running('collecting baskets for {}'.format(college), 'end'))

            __(LogInfo.running('initiate apriori for {}'.format(college), 'begin'))
            apri_inst = Apriori(basket, force_origin=True, depth=2)
            __(LogInfo.running('initiate apriori for {}'.format(college), 'end'))

            min_support = kwargs.get('min_support', 0.5)
            min_conf = kwargs.get('min_conf', 0.6)

            # while True:
            for min_support in [
                0.5, 0.4, 0.3, 0.2, 0.15,  # 0.1,  # 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01,
            ]:
                __(LogInfo.running('Apriori rules for', 'min_support={0:.2f}: '.format(min_support)))
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
    else:
        raise NotImplementedError


def apply_collaborative_filtering(method: CollaborativeFilteringMethods, simi_func: FunctionType, **kwargs):
    from tqdm import tqdm
    from modules.Functions import collect_reader_attributes
    from structures.Extended import CountingDict
    from utils.FileSupport import get_pdict, save_csv

    max_length = kwargs.get('max_length', 10)
    books = get_pdict('books')
    books_by_reader = get_pdict('books_group_by_readers')
    readers_by_book = get_pdict('readers_group_by_books')

    if method == CollaborativeFilteringMethods.ReaderBase:

        # calculating similarity
        simi_dict = dict()
        reader_attributes = get_pdict('reader_attributes').copy()
        for reader_a in tqdm(reader_attributes.keys(), desc='calculating similarity'):
            this_simi = CountingDict()
            vec_a = reader_attributes[reader_a]
            possible_readers = set()
            for book_id in books_by_reader[reader_a]:
                possible_readers.update(readers_by_book[book_id])
            for reader_b in possible_readers:
                if reader_b == reader_a:
                    continue
                else:
                    this_simi.set(reader_b, simi_func.__call__(vec_a, reader_attributes[reader_b]))
            simi_dict[reader_a] = this_simi
        del reader_attributes

        # sorting and selecting books
        result = dict()
        for reader in tqdm(simi_dict.keys(), desc='finding books'):
            recommend_list = list()
            this_selected = books_by_reader[reader]
            assert isinstance(this_selected, set)
            simi_list = simi_dict[reader].sort(inverse=True)
            for simi_reader in simi_list:
                for item in books_by_reader[simi_reader]:
                    assert isinstance(books_by_reader[simi_reader], set)
                    if item not in this_selected and item not in recommend_list:
                        recommend_list.append(item)
                    if len(recommend_list) >= max_length:
                        break
                if len(recommend_list) >= max_length:
                    break

            recommend_list = [books[var].book_name for var in recommend_list]  # getting book names
            recommend_list.insert(0, reader)
            result[reader] = recommend_list

        save_csv([result[var] for var in result.keys()], 'CollaborativeFilteringMethods.ReaderBase')
    else:
        raise NotImplemented


if __name__ == '__main__':
    from utils.Logger import set_logging, LogInfo
    from functions.Maths import EuclideanSimilarity
    LogInfo.initiate_time_counter()
    set_logging()
    apply_apriori(AprioriMethods.GroupByReaderCollege)
    # apply_collaborative_filtering(CollaborativeFilteringMethods.ReaderBase, EuclideanSimilarity)

    print(LogInfo.time_passed())
