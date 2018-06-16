# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging
import os

from tqdm import tqdm

from Config import DataConfig
from structures.Book import Book
from structures.Event import Event
from utils.Logger import get_logger
from utils.Persisit import Pdict, Plist


logger = get_logger(module_name=__file__)


def group_by(data_dict, group_tag: str, by_tag: str, auto_save: bool=False):
    """

    :param data_dict:
    :param group_tag:
    :param by_tag: related attribute
    :param auto_save: bool
    :return: dict( key: set())
    """
    from collections import Mapping
    from tqdm import tqdm
    assert isinstance(data_dict, Mapping)

    logger.debug_running('group {} by {}'.format(group_tag, by_tag), 'begin')

    grouped_dict = dict()

    for index in tqdm([var for var in data_dict.keys()], desc='grouping {} by {}'.format(group_tag, by_tag)):
        obj = data_dict[index]
        by_value = getattr(obj, by_tag)

        if by_value is None:
            continue

        if not isinstance(by_value, str):
            by_value = str(by_value)

        if len(by_value) == 0:  # jump to next iteration if no content
            continue

        if by_value not in grouped_dict:
            grouped_dict[by_value] = set()

        stored = grouped_dict[by_value]
        stored.add(index)
        grouped_dict[by_value] = stored

    if auto_save is True:
        from utils.DataBase import ShelveWrapper
        ShelveWrapper.init_from(
            grouped_dict,
            os.path.join(DataConfig.operation_path, '{}_group_by_{}'.format(group_tag, by_tag))
        ).close()
    logging.debug(LogInfo.running('group {} by {}'.format(group_tag, by_tag), 'end'))
    return grouped_dict


def trim_range(data_bag, attr_tag: str, range_start, range_end, include_start: bool=True, include_end: bool=False):
    from collections import Iterable, Mapping
    if isinstance(data_bag, Mapping):
        result = dict()
        for d_k, d_v in data_bag.items():
            if include_start is True and include_end is True:
                if range_start <= getattr(d_v, attr_tag) <= range_end:
                    result[d_k] = d_v
            elif include_start is True and include_end is False:
                if range_start <= getattr(d_v, attr_tag) < range_end:
                    result[d_k] = d_v
            elif include_start is False and include_end is True:
                if range_start < getattr(d_v, attr_tag) <= range_end:
                    result[d_k] = d_v
            else:
                if range_start < getattr(d_v, attr_tag) < range_end:
                    result[d_k] = d_v
        return result
    elif isinstance(data_bag, Iterable):
        raise NotImplemented
    else:
        from utils.Exceptions import ParamTypeError
        raise ParamTypeError('data_bag', 'Iterable/Mapping', data_bag)


def index_books2readers(events_bag, auto_save: bool=False, books2readers_first: bool=True):
    from collections import defaultdict, Mapping, Iterable
    from tqdm import tqdm

    books_group_by_readers = defaultdict(set)
    readers_group_by_books = defaultdict(set)

    if isinstance(events_bag, Mapping):
        for e_key in tqdm(events_bag.keys(), desc='indexing book2reader from events'):
            event = events_bag[e_key]
            assert isinstance(event, Event)
            books_group_by_readers[event.reader_id].add(event.book_id)
            readers_group_by_books[event.book_id].add(event.reader_id)
    elif isinstance(events_bag, Iterable):
        for event in tqdm(events_bag, desc='grouping events'):
            assert isinstance(event, Event)
            books_group_by_readers[event.reader_id].add(event.book_id)
            readers_group_by_books[event.book_id].add(event.reader_id)
    else:
        from utils.Exceptions import ParamTypeError
        raise ParamTypeError('events_bag', 'Mapping/Iterable', events_bag)

    if auto_save is True:
        from utils.DataBase import ShelveWrapper
        ShelveWrapper.init_from(
            books_group_by_readers,
            os.path.join(DataConfig.operation_path, 'books_group_by_readers')
        ).close()
        ShelveWrapper.init_from(
            readers_group_by_books,
            os.path.join(DataConfig.operation_path, 'readers_group_by_books')
        ).close()

    if books2readers_first is True:
        return books_group_by_readers, readers_group_by_books
    else:
        return readers_group_by_books, books_group_by_readers


def induct_events_by_date(events_bag, auto_save: bool=False):
    from collections import Mapping, Iterable
    from structures.Extended import OrderedList

    result = dict()

    if isinstance(events_bag, Mapping):
        for event in tqdm(events_bag.values(), desc='inducting events'):
            assert isinstance(event, Event)
            if event.reader_id not in result:
                result[event.reader_id] = OrderedList(Event, 'date')
            result[event.reader_id].append(event)
    elif isinstance(events_bag, Iterable):
        for event in tqdm(events_bag, desc='inducting events'):
            assert isinstance(event, Event)
            if event.reader_id not in result:
                result[event.reader_id] = OrderedList(Event, 'date')
            result[event.reader_id].append(event)
    else:
        from utils.Exceptions import ParamTypeError
        raise ParamTypeError('events_bag', 'Iterable/Mapping', events_bag)

    if auto_save is True:
        from utils.DataBase import ShelveWrapper
        ShelveWrapper.init_from(
            result,
            os.path.join(DataConfig.operation_path, 'inducted_events')
        ).close()

    return result


def collect_baskets(events_bag, book_tag: str):
    from collections import Iterable, Mapping
    from algorithm.Apriori import BasketCollector
    from modules.DataProxy import DataProxy

    logger.debug_running('collect_baskets', 'start')

    books = DataProxy().books

    new_basket = BasketCollector()
    if isinstance(events_bag, Iterable):
        for event in events_bag:
            assert isinstance(event, Event)
            book = books[event.book_id]
            assert isinstance(book, Book)
            new_basket.add(event.reader_id, getattr(book, book_tag))
    elif isinstance(events_bag, Mapping):
        for event in events_bag.values():
            book = books[event.book_id]
            new_basket.add(event.reader_id, getattr(book, book_tag))
    else:
        from utils.Exceptions import ParamTypeError
        raise ParamTypeError('events_bag', '', events_bag)

    logger.debug_running('collect_baskets', 'end')

    return new_basket


def collect_reader_attributes(events, **kwargs):

    from tqdm import tqdm
    from collections import defaultdict
    from modules.DataProxy import DataProxy
    from structures.SparseVector import SparseVector
    from utils.DataBase import ShelveWrapper

    reader_attributes = defaultdict(SparseVector)

    if isinstance(events, (list, Plist)):
        for i in tqdm(range(len(events)), desc='checking events'):
            event = events[i]
            assert isinstance(event, Event)
            reader_attributes[event.reader_id][event.book_id] = event.times
    elif isinstance(events, (dict, Pdict, ShelveWrapper)):
        for event in tqdm(events.values(), desc='checking events'):
            reader_attributes[event.reader_id][event.book_id] = event.times
    else:
        from utils.Exceptions import ParamTypeError
        raise ParamTypeError('events', 'list/Plist/dict/Pdict/ShelveWrapper', events)

    total_books = kwargs.get('length', DataProxy.get_shelve('books').__len__())

    for reader_id in reader_attributes:
        reader_attributes[reader_id].set_length(total_books)

    auto_save = kwargs.get('auto_save', False)
    if auto_save is True:
        ShelveWrapper.init_from(
            reader_attributes,
            db_path=os.path.join(DataConfig.operation_path, 'reader_attributes')
        ).close()

    return reader_attributes


if __name__ == '__main__':
    logger.initiate_time_counter()

    # collect_reader_attributes()

    logger.print_time_passed()
