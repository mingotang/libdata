# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
from tqdm import tqdm

from structures.Event import Event
from utils import get_logger


logger = get_logger(module_name=__file__)


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
