# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging

from utils.Constants import BaseEnum
from utils.Logger import LogInfo


# --------------------------------------------------------
class AprioriMethods(BaseEnum):
    Basic = 'ReaderIDAsBuyer_BookIDAsGoods'
    GroupByReaderCollege = 'ReaderIDAsBuyer_BookIDAsGoods-GroupByReaderCollege'


class CollaborativeFilteringMethods(BaseEnum):
    pass


# --------------------------------------------------------
def apply_apriori(method: AprioriMethods, min_support=0.1):
    """

    :param method:
    :param min_support:
    :param kwargs: Key: 'basket_tag', 'goods_tag', 'group_tag',
    :return:
    """
    from Config import DataConfig
    from algorithm.Apriori import BasketCollector, Apriori
    from structures.Event import Event
    from utils.Persisit import Pdict
    if method == AprioriMethods.Basic:
        logging.debug(LogInfo.running('AprioriMethods.Basic', 'start'))

        events_dict = Pdict(DataConfig.persisted_event_path, keep_history=True)

        logging.debug(LogInfo.running('collecting baskets', 'begin'))
        basket = BasketCollector()  # '/Users/mingo/Downloads/basket_dict'
        for event in events_dict.values():
            # if isinstance(event, Event):
            basket.add(event.reader_id, event.book_id)
        basket = basket.to_list()  # '/Users/mingo/Downloads/basket_dict'
        logging.debug(LogInfo.running('collecting baskets', 'end'))

        logging.debug(LogInfo.running('applying apriori', 'begin'))
        result = Apriori(basket, min_support=min_support)
        logging.debug(LogInfo.running('applying apriori', 'end'))
        while True:
            min_conf = 0.2
            print('Apriori rules for min_conf={0:.2f}: '.format(min_conf))
            result.show_results(min_conf)
            # print('Result rules: ', result.show_results(min_conf))
            print('Max rules: {0:d}'.format(len(result.generate_rules(min_conf=0.0001))))
            config = input('Are you satisfied with the result above? (y/n)  ')
            if config.lower() == 'y':
                break
            elif config.lower() == 'n':
                # print(result.show_results())
                min_conf = float(input('Please input new min_conf:  '))
            else:
                break
                # min_conf = float(input('Please input new min_conf:  '))
    elif method == AprioriMethods.GroupByReaderCollege:
        pass
    else:
        raise NotImplementedError


def collaborative_filtering(base: str, max_length=20, **kwargs):
    """

    :param base: str, 'reader', 'book'
    :param kwargs: kwargs: Key: 'book', 'reader', 'events', 'chara_tag'
    :return:
    """
    reader2book_dict = dict()
    book2reader_dict = dict()
    for user_index in tqdm(kwargs['events'].keys(), desc='CF.settiing up'):
        for action_index in range(len(kwargs['events'][user_index])):
            if user_index not in reader2book_dict:
                reader2book_dict[user_index] = CountingDict()
            if kwargs['events'][user_index][action_index].book_id not in book2reader_dict:
                book2reader_dict[kwargs['events'][user_index][action_index].book_id] = CountingDict()
            reader2book_dict[user_index].count(kwargs['events'][user_index][action_index].book_id)
            book2reader_dict[kwargs['events'][user_index][action_index].book_id].count(user_index)
    if base == 'reader':
        similarity_ref = LibAssociationRulesGeneration.__cf__setup__similarity__(reader2book_dict)
        recommend_list = dict()
        for reader in similarity_ref:
            recommend_list[reader] = list()
            sorted_list = similarity_ref[reader].sort_by_weights(inverse=True)
            for sorted_index in range(len(sorted_list)):
                similar_reader = sorted_list[sorted_index]
                ref_book_list = reader2book_dict[similar_reader].sort_by_weights(inverse=True)
                for ref_book in ref_book_list:
                    if ref_book not in reader2book_dict[reader] and len(recommend_list[reader]) <= max_length:
                        recommend_list[reader].append(ref_book)
        return recommend_list
    elif base == 'book':
        raise ModuleNotFoundError()
    else:
        raise ValueError(
            'collaborative_filtering: base {0:s} not legal'.format(base)
        )

def __cf__setup__similarity__(base_dict: dict):
    similarity_dict = dict()
    tag_list = list(base_dict.keys())
    tag_list.sort()
    for front_index in tqdm(range(len(tag_list)), desc='CF.calculating similarity'):
        if tag_list[front_index] not in similarity_dict:
            similarity_dict[tag_list[front_index]] = CountingDict()
        for back_index in range(front_index, len(tag_list)):
            if tag_list[back_index] not in similarity_dict:
                similarity_dict[tag_list[back_index]] = CountingDict()
            similarity_dict[tag_list[front_index]][tag_list[back_index]] = \
                similarity_dict[tag_list[back_index]][tag_list[front_index]] = \
                base_dict[tag_list[front_index]] * base_dict[tag_list[back_index]]
    return similarity_dict


if __name__ == '__main__':
    from utils.Logger import set_logging
    set_logging()
    apply_apriori(AprioriMethods.Basic, min_support=0.1)
