# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import random
import pandas as pd

from modules.Algorithm import Apriori
from modules.DataManagement import Book, Reader, EventAction, EventActionList
from modules.DataManagement import BookManager
from modules.DataManagement import ReaderManager
from modules.DataManagement import ReadersEventManager
from modules.ServiceComponents import FileIO


# --------------------------------------------------------


# --------------------------------------------------------
class LibAssociationRulesGeneration(object):

    @staticmethod
    def apriori(method='simple',
                min_support=0.1, **kwargs):
        """

        :param method:
        :param min_support:
        :param kwargs: Key: 'book', 'reader', 'events', 'basket_tag', 'goods_tag'
                            'group_tag',
        :return:
        """
        if method == 'simple' and 'group_tag' not in kwargs:
            basket_list = LibAssociationRulesGeneration.__apriori_collect_basket__(**kwargs)
            # FileIO.save_temp_bit('/Users/mingo/Downloads/basket_dict.temp', basket_dict)
            result = Apriori(basket_list, min_support=min_support)
            print(result.generate_rules(min_conf=0.5))
        elif method == 'groupspecified':
            basket_dict = LibAssociationRulesGeneration.__apriori_collect_basket__(**kwargs)
            
        else:
            raise ValueError('LibAssociationRulesGeneration.apriori param method is not legal')

    @staticmethod
    def __apriori_collect_basket__(**kwargs):
        """

        :param kwargs: Key: 'book', 'reader', 'events', 'basket_tag', 'goods_tag'
                            'group_tag',
        :return:
        """
        collected_dict = dict()
        if 'group_tag' not in kwargs:
            if kwargs['basket_tag'] == 'userID':
                for user_tag in kwargs['reader'].keys():
                    if user_tag not in collected_dict:
                        collected_dict[user_tag] = set()
                    for action in kwargs['events'][user_tag]:
                        if kwargs['goods_tag'] in Book.tag_index_list:
                            collected_dict[user_tag].add(kwargs['book'][action.book_id][kwargs['goods_tag']])
                        elif kwargs['goods_tag'] in Reader.tag_index_list:
                            collected_dict[user_tag].add(kwargs['reader'][action.user_id][kwargs['goods_tag']])
                        else:
                            raise ValueError('{0:s} param contain_tag {1:s} is not legal'.format(
                                LibAssociationRulesGeneration.__class__.__name__,
                                kwargs['goods_tag'],
                            ))
            elif kwargs['basket_tag'] == 'sysID':
                raise ModuleNotFoundError()
            else:
                raise ValueError('{0:s} param basket_tag {1:s} not legal'.format(
                    LibAssociationRulesGeneration.__class__.__name__,
                    kwargs['basket_tag'],))

        else:
            if kwargs['group_tag'] in Reader.tag_index_list:
                mass_reader_manager = kwargs['reader'].group_by(kwargs['group_tag'])
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
        return list(list(collected_dict[var]) for var in collected_dict)

    @staticmethod
    def collaborative_filtering(base: str, **kwargs):
        if base == 'reader2reader':
            if 'reader_events_dict' in kwargs:
                pass
            else:
                raise ValueError(
                    'LibAssociationRulesGeneration.collaborative_filtering: missing param reader_events_dict'
                )
        elif base == 'book2book':
            if 'reader_events_dict' in kwargs:
                pass
            else:
                raise ValueError(
                    'LibAssociationRulesGeneration.collaborative_filtering: missing param reader_events_dict'
                )
        else:
            raise ValueError(
                'LibAssociationRulesGeneration.collaborative_filtering: base {0:s} is not legal'.format(base)
            )


# --------------------------------------------------------


if __name__ == '__main__':
    import os
    import time
    start_time = time.time()
    # ------------------------------
    book_data = BookManager(folder_path=os.path.join('..', 'data'))
    reader_data = ReaderManager(folder_path=os.path.join('..', 'data'))
    reader_event_data = ReadersEventManager(folder_path=os.path.join('..', 'data'),
                                            loading_name='ReaderEventsData Thu Dec 21 13:15:47 2017.libdata')
    LibAssociationRulesGeneration.apriori(
        method='simple',
        book=book_data, reader=reader_data, events=reader_event_data,
        basket_tag='userID', goods_tag='sysID',
        min_support=0.2,
    )
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration)//3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.2f} s'.format(hour, minutes, seconds))
