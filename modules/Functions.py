# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os

from tqdm import tqdm

from Config import DataConfig
from structures.Event import Event
from utils import get_logger


logger = get_logger(module_name=__file__)


def index_books2readers(events_bag, auto_save: bool=False, books2readers_first: bool=True):
    """建立谁借了书和书被谁借了的快速索引字典 -> dict( key: set())"""
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
        from utils import ShelveWrapper
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


def extract_reader_event_set(events_bag, auto_save: bool=False, reader_first: bool=True):
    """抽取行为数据集中涉及到的读者和书籍的编号 -> set(), set()"""
    from collections import Mapping, Iterable
    from modules.DataProxy import DataProxy

    reader_set, book_set = set(), set()
    logger.debug_running('extract_reader_event_set', 'extracting book/reader')
    if isinstance(events_bag, Mapping):
        for event in tqdm(events_bag.values(), desc='extracting book/reader'):
            assert isinstance(event, Event)
            reader_set.add(event.reader_id)
            book_set.add(event.book_id)
    elif isinstance(events_bag, Iterable):
        for event in tqdm(events_bag, desc='extracting book/reader'):
            assert isinstance(event, Event)
            reader_set.add(event.reader_id)
            book_set.add(event.book_id)
    else:
        from utils.Exceptions import ParamTypeError
        raise ParamTypeError('events_bag', 'Iterable/Mapping', events_bag)

    data = DataProxy(writeback=False)
    reader_db = data.get_shelve('readers')
    book_db = data.get_shelve('books')

    if auto_save is True:
        logger.debug_running('extract_reader_event_set', 'saving books/readers')
        for r_id in reader_set:
            reader_db[r_id] = data.readers[r_id]
        for b_id in book_set:
            book_db[b_id] = data.books[b_id]

    if reader_first is True:
        return reader_set, book_set
    else:
        return book_set, reader_set


if __name__ == '__main__':
    from modules.DataProxy import DataProxy

    logger.initiate_time_counter()

    data_proxy = DataProxy(writeback=False)

    logger.print_time_passed()
