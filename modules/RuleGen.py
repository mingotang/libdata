# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import time

from tqdm import tqdm

from algorithm import Apriori
from modules import SqliteWrapper
from structures import Book, Reader
from structures import CountingDict
from utils.Constants import BaseEnum


# --------------------------------------------------------
class AprioriMethods(BaseEnum):
    Basic = 'ReaderIDAsBuyer_BookIDAsGoods'
    GroupByReaderCollege = 'ReaderIDAsBuyer_BookIDAsGoods-GroupByReaderCollege'


class CollaborativeFilteringMethods(BaseEnum):
    pass


# --------------------------------------------------------
class LibAssociationRulesGeneration(object):
    def __init__(self, local_db: SqliteWrapper):
        self.db = local_db

    @staticmethod
    def apriori(method: AprioriMethods, min_support=0.1, min_conf=0.2, **kwargs):
        """

        :param method:
        :param min_support:
        :param kwargs: Key: 'basket_tag', 'goods_tag', 'group_tag',
        :return:
        """
        if method == AprioriMethods.Basic:
            basket_list = LibAssociationRulesGeneration.__apriori_collect_basket__(**kwargs)
            print(basket_list)
            result = Apriori(basket_list, min_support=min_support)
            while True:
                print('Apriori rules for min_conf={0:.2f}: '.format(min_conf))
                print('Result rules: ', result.generate_rules(min_conf=min_conf))
                print('Max rules: {0:d}'.format(len(result.generate_rules(min_conf=0.0001))))
                config = input('Are you satisfied with the result above? (y/n)  ')
                if config.lower() == 'y':
                    break
                elif config.lower() == 'p':
                    print(result.show_results())
                    min_conf = float(input('Please input new min_conf:  '))
                else:
                    min_conf = float(input('Please input new min_conf:  '))
        elif method == AprioriMethods.GroupByReaderCollege:
            result = dict()
            basket_dict = LibAssociationRulesGeneration.__apriori_collect_basket__(**kwargs)
            for group_value in basket_dict:
                print('Running apriori for {0:s}'.format(str(group_value)))
                result[group_value] = Apriori(basket_dict[group_value], min_support=min_support)
                print(basket_dict[group_value])
                while True:
                    print('Apriori rules for group {0:s} min_conf={1:.2f}: '.format(group_value, min_conf))
                    print('Result rules: ', result[group_value].generate_rules(min_conf=min_conf))
                    print('Max rules: {0:d}'.format(len(result[group_value].generate_rules(min_conf=0.0001))))
                    config = input('Are you satisfied with the result above? (y/n)  ')
                    if config.lower() == 'y':
                        break
                    elif config.lower() == 'p':
                        print(result[group_value].show_results())
                        min_conf = float(input('Please input new min_conf:  '))
                    else:
                        min_conf = float(input('Please input new min_conf:  '))
        else:
            raise ValueError('LibAssociationRulesGeneration.apriori param method & group_tag not legal')

    @staticmethod
    def __apriori_collect_basket__(**kwargs):
        """

        :param kwargs: Key: 'book', 'reader', 'events', 'basket_tag', 'goods_tag'
                            'group_tag',
        :return:
        """
        apriori_collect_start_time = time.time()
        if 'group_tag' not in kwargs:
            collected_dict = dict()
            if kwargs['basket_tag'] == 'userID':
                for user_tag in kwargs['reader'].keys():
                    if user_tag not in collected_dict:
                        collected_dict[user_tag] = CountingDict()
                    for action_index in range(len(kwargs['events'][user_tag])):
                        if kwargs['goods_tag'] in Book.tag_index_list:
                            collected_dict[user_tag].count(
                                kwargs['book'][kwargs['events'][user_tag][action_index].book_id][kwargs['goods_tag']]
                            )
                        elif kwargs['goods_tag'] in Reader.tag_index_list:
                            collected_dict[user_tag].count(
                                kwargs['reader'][kwargs['events'][user_tag][action_index].user_id][kwargs['goods_tag']]
                            )
                        else:
                            raise ValueError('{0:s} param contain_tag {1:s} is not legal'.format(
                                LibAssociationRulesGeneration.__class__.__name__,
                                kwargs['goods_tag']))
            elif kwargs['basket_tag'] == 'sysID':
                raise ModuleNotFoundError()
            else:
                raise ValueError('{0:s} param basket_tag {1:s} not legal'.format(
                    LibAssociationRulesGeneration.__class__.__name__,
                    kwargs['basket_tag']))
            return list(list(collected_dict[var].keys()) for var in collected_dict)
        else:
            collected_dict = dict()
            if kwargs['group_tag'] in Reader.tag_index_list:
                mass_reader_manager = kwargs['reader'].group_by(kwargs['group_tag'])
                print('Group_value: ', list([var, len(mass_reader_manager[var])] for var in mass_reader_manager.keys()))
                for mass_tag in mass_reader_manager:
                    collected_dict[mass_tag] = LibAssociationRulesGeneration.__apriori_collect_basket__(
                        book=kwargs['book'], reader=mass_reader_manager[mass_tag], events=kwargs['events'],
                        basket_tag=kwargs['basket_tag'], goods_tag=kwargs['goods_tag'],
                    )
            elif kwargs['group_tag'] in Book.tag_index_list:
                raise ModuleNotFoundError()
            else:
                raise ValueError('{0:s} param group_tag {1:s} not legal'.format(
                    LibAssociationRulesGeneration.__class__.__name__,
                    kwargs['group_tag'], ))
            return collected_dict

    @staticmethod
    def __apriori_apply_rules(**kwargs):
        """

        :param kwargs:
        :return:
        """
        pass

    @staticmethod
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

    @staticmethod
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


# --------------------------------------------------------


if __name__ == '__main__':
    # import time
    start_time = time.time()
    # ------------------------------
    # LibAssociationRulesGeneration.apriori(
    #     method='simple',
    #     # method='groupspecified', group_tag='collegeID',
    #     book=book_data, reader=reader_data, events=reader_event_data,
    #     basket_tag='userID', goods_tag='lib_index_class',
    #     min_support=0.2,
    # )
    recommend_info = LibAssociationRulesGeneration.collaborative_filtering(
        base='reader',
        book=book_data, reader=reader_data, events=reader_event_data,
    )
    from ServiceComponents import FileIO
    FileIO.save_csv('CF_base-reader.csv', recommend_info)
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration)//3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.2f} s'.format(hour, minutes, seconds))
