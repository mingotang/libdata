# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging
import os

from tqdm import tqdm

from Config import DataConfig
from utils.Logger import LogInfo
from utils.Persisit import Pdict


__i__ = logging.debug


def group_by(group_tag: str, by_tag: str, in_memory=True):
    """

    :param group_tag: 'readers'/'books'
    :param by_tag: related attribute
    :param in_memory: bool
    :return: None
    """

    __i__(LogInfo.running('group {} by {}', 'begin'))

    pdata = Pdict(os.path.join(DataConfig.persisted_data_path, group_tag), keep_history=True)

    if in_memory is True:
        grouped_dict = dict()
    else:
        grouped_dict = Pdict(
            data_path=os.path.join(DataConfig.persisted_data_path, '{}_group_by_{}'.format(group_tag, by_tag)),
            keep_history=False,
        )

    for index in tqdm(pdata.keys(), desc='grouping {} by {}'.format(group_tag, by_tag)):
        obj = pdata[index]
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

    if in_memory is True:
        Pdict.init_from(
            grouped_dict,
            data_path=os.path.join(DataConfig.persisted_data_path, '{}_group_by_{}'.format(group_tag, by_tag)),
            keep_history=False,
        )

    __i__(LogInfo.running('group {} by {}', 'end'))


from structures.Book import Book
from structures.Event import Event


def collect_basket(events_list, book_tag: str):
    """

    :param events_list:
    :param book_tag:
    :return:
    """
    from algorithm.Apriori import BasketCollector

    assert isinstance(events_list, (dict, Pdict))

    books = Pdict(os.path.join(DataConfig.persisted_data_path, 'books'), keep_history=True)

    new_basket = BasketCollector()
    for event in events_list:
        # assert isinstance(event, Event)
        book = books[event.book_id]
        # assert isinstance(book, Book)
        new_basket.add(event.reader_id, getattr(book, book_tag))

    return new_basket


if __name__ == '__main__':
    from utils.Logger import set_logging
    set_logging()

    group_by(group_tag='books', by_tag='year')
