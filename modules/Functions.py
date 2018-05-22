# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging
import os

from tqdm import tqdm

from Config import DataConfig
from utils.Logger import LogInfo
from utils.Persisit import Pdict, Plist

from structures.Book import Book
from structures.Event import Event
from structures.Reader import Reader


__i__ = logging.debug


def group_by(data_dict, group_tag: str, by_tag: str, auto_save=False):
    """

    :param group_tag:
    :param by_tag: related attribute
    :return: dict( key: set())
    """
    from tqdm import tqdm
    from modules.DataBase import ShelveWrapper
    from utils.FileSupport import save_pickle
    assert isinstance(data_dict, ShelveWrapper)

    logging.debug(LogInfo.running('group {} by {}'.format(group_tag, by_tag), 'begin'))

    grouped_dict = dict()

    for index in tqdm(data_dict.keys(), desc='grouping {} by {}'.format(group_tag, by_tag)):
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
        save_pickle(
            grouped_dict,
            os.path.join(DataConfig.operation_path, '{}_group_by_{}'.format(group_tag, by_tag))
        )
    logging.debug(LogInfo.running('group {} by {}'.format(group_tag, by_tag), 'end'))
    return grouped_dict


def index_books2readers_in_events(events_bag, auto_save=False, books2readers_first=True):
    from collections import defaultdict, Mapping, Iterable
    from tqdm import tqdm
    from utils.FileSupport import save_pickle

    books_group_by_readers = defaultdict(set)
    readers_group_by_books = defaultdict(set)

    if isinstance(events_bag, Mapping):
        for event in tqdm(events_bag.values(), desc='grouping events'):
            assert isinstance(event, Event)
            books_group_by_readers[event.reader_id].add(event.book_id)
            readers_group_by_books[event.book_id].add(event.reader_id)
    elif isinstance(events_bag, Iterable):
        for event in tqdm(events_bag, desc='grouping events'):
            assert isinstance(event, Event)
            books_group_by_readers[event.reader_id].add(event.book_id)
            readers_group_by_books[event.book_id].add(event.reader_id)
    else:
        raise TypeError

    if auto_save is True:
        save_pickle(
            books_group_by_readers,
            os.path.join(DataConfig.operation_path, 'books_group_by_readers')
        )
        save_pickle(
            readers_group_by_books,
            os.path.join(DataConfig.operation_path, 'readers_group_by_books')
        )

    if books2readers_first is True:
        return books_group_by_readers, readers_group_by_books
    else:
        return readers_group_by_books, books_group_by_readers


def induct_events(events_bag):
    from collections import defaultdict, Mapping, Iterable
    from utils.FileSupport import init_pseries

    sum_dict = defaultdict(list)

    if isinstance(events_bag, Mapping):
        for event in tqdm(events_bag.values(), desc='inducting events'):
            assert isinstance(event, Event)
            sum_dict[event.reader_id].append(event)
    elif isinstance(events_bag, Iterable):
        for event in tqdm(events_bag, desc='inducting events'):
            assert isinstance(event, Event)
            sum_dict[event.reader_id].append(event)
    else:
        raise TypeError

    for reader_id in sum_dict.keys():
        init_pseries(sum_dict[reader_id], 'temp', 'inducted_events', reader_id, index_tag='event_date')


def collect_baskets(events_bag, book_tag: str):

    from algorithm.Apriori import BasketCollector
    from utils.FileSupport import get_pdict, init_pdict

    books = get_pdict('books', keep_history=True)

    new_basket = BasketCollector()
    if isinstance(events_bag, (list, Plist)):
        for i in range(len(events_bag)):
            event = events_bag[i]
            # assert isinstance(event, Event)
            book = books[event.book_id]
            # assert isinstance(book, Book)
            new_basket.add(event.reader_id, getattr(book, book_tag))
    elif isinstance(events_bag, (dict, Pdict)):
        for event in events_bag.values():
            book = books[event.book_id]
            new_basket.add(event.reader_id, getattr(book, book_tag))
    else:
        raise TypeError

    # new_dict = new_basket.to_dict()
    # for key in new_dict.keys():
    #     print(key, new_dict[key])
    # print(len(new_dict))
    return new_basket


def collect_reader_attributes(events, **kwargs):

    from collections import defaultdict
    from structures.SparseVector import SparseVector
    from tqdm import tqdm
    from utils.FileSupport import get_pdict, init_pdict

    reader_attributes = defaultdict(SparseVector)

    if isinstance(events, (list, Plist)):
        for i in tqdm(range(len(events)), desc='checking events'):
            event = events[i]
            assert isinstance(event, Event)
            reader_attributes[event.reader_id][event.book_id] = event.times
    elif isinstance(events, (dict, Pdict)):
        for event in tqdm(events.values(), desc='checking events'):
            reader_attributes[event.reader_id][event.book_id] = event.times
    else:
        raise TypeError

    total_books = kwargs.get('length', len(get_pdict('books')))

    for reader_id in reader_attributes:
        reader_attributes[reader_id].set_length(total_books)

    init_pdict(reader_attributes, 'reader_attributes')
    return reader_attributes


if __name__ == '__main__':
    from utils.FileSupport import save_pickle, load_pickle, get_pdict
    from utils.Logger import set_logging, LogInfo
    LogInfo.initiate_time_counter()
    set_logging()

    collect_reader_attributes(get_pdict('events'))

    print(LogInfo.time_passed())
