# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import random
import pandas as pd

from tqdm import tqdm

from modules.Algorithm import Apriori
# from modules.DataStructure import Book, Reader, EventAction
from modules.DataManagement import BookManager
from modules.DataManagement import ReaderManager
from modules.DataManagement import ReadersEventManager


# --------------------------------------------------------
class Results(object):
    def __init__(self, result_model):
        self.model = result_model


class ResultsApriori(Results):
    def __init__(self, result_model, method: str):
        Results.__init__(self, result_model)
        self.method = method


# --------------------------------------------------------
class LibAssociationRulesGeneration(object):

    @staticmethod
    def apriori(book: BookManager, reader: ReaderManager, events: ReadersEventManager,
                basket_tag: str, goods_tag: str, method='simple', classification_tag=None,
                min_support=0.1):
        if method == 'simple':
            basket_dict = LibAssociationRulesGeneration.__apriori_collect_basket__(
                by_tag=basket_tag, contain_tag=goods_tag,
                book=book.stored_dict, reader=reader.stored_dict, events=events.stored_dict,
            )
            basket_list = list()
            for tag in basket_dict:
                basket_list.append(list(basket_dict[tag]))
            basket_list = random.sample(basket_list, 1000)
            result = Apriori(basket_list, min_support=min_support)
            return ResultsApriori(result_model=result, method=method)
        elif method == 'classified':
            basket_dict = LibAssociationRulesGeneration.__apriori_collect_basket__()
        else:
            raise ValueError('LibAssociationRulesGeneration.apriori param method is not legal')

    @staticmethod
    def __apriori_collect_basket__(by_tag: str, contain_tag: str,
                                   book: dict, reader: dict, events: dict,
                                   constrain_tag=None, constrain_value=None):
        collected_dict = dict()
        if by_tag == 'userID':
            for tag in tqdm(
                    events.keys(),
                    desc='LibAssociationRulesGeneration.apriori collecting baskets '
            ):
                if tag not in collected_dict:
                    collected_dict[tag] = set()
                action_list = events[tag]
                for action_index in range(len(action_list)):
                    action = action_list[action_index]
                    if contain_tag == 'sysID':
                        collected_dict[tag].add(action.book_id)
                    elif contain_tag == 'bookname':
                        collected_dict[tag].add(book[action.book_id].name)
                    elif contain_tag == 'author':
                        collected_dict[tag].add(book[action.book_id].author)
                    else:
                        raise ValueError('{0:s} param contain_tag {1:s} is not legal'.format(
                            LibAssociationRulesGeneration.__class__.__name__,
                            contain_tag,
                        ))
        elif by_tag == 'sysID':
            raise ValueError('{0:s} param contain_tag {1:s} is not defined'.format(
                LibAssociationRulesGeneration.__class__.__name__,
                contain_tag,
            ))
        else:
            raise ValueError('{0:s} param by_tag {1:s} is not legal'.format(
                LibAssociationRulesGeneration.__class__.__name__,
                by_tag,
            ))
        return collected_dict

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
    book_data = BookManager(folder_path=os.path.join('..', '_data'))
    reader_data = ReaderManager(folder_path=os.path.join('..', '_data'))
    reader_event_data = ReadersEventManager(folder_path=os.path.join('..', '_data'),
                                            loading_name='ReaderEventsData Tue Dec  5 15:47:29 2017.libdata')
    LibAssociationRulesGeneration.apriori(book=book_data, reader=reader_data, events=reader_event_data,
                                          basket_tag='userID', goods_tag='sysID')
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration)//3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.2f} s'.format(hour, minutes, seconds))
