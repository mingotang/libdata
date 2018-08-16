# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


def trim_range(data_bag, attr_tag: str, range_start, range_end,
               include_start: bool=True, include_end: bool=False):
    """
    把 data_bag 的内容对象根据 attr_tag 属性进行修剪，返回一个新的数据集
    :param data_bag: 数据对象
    :param attr_tag:
    :param range_start:
    :param range_end:
    :param include_start:
    :param include_end:
    :return: dict / list
    """
    from collections import Iterable, Mapping
    if isinstance(data_bag, Mapping):
        result = dict()
        if range_start is None:
            for key, value in data_bag.items():
                result[key] = value
        else:
            if include_start is True:
                for key, value in data_bag.items():
                    if range_start <= getattr(value, attr_tag):
                        result[key] = value
            else:
                for key, value in data_bag.items():
                    if range_start < getattr(value, attr_tag):
                        result[key] = value

        if range_end is not None:
            if include_end is True:
                for key in list(result.keys()):
                    value = result[key]
                    if getattr(value, attr_tag) > range_end:
                        result.pop(key)
            else:
                for key in list(result.keys()):
                    value = result[key]
                    if getattr(value, attr_tag) >= range_end:
                        result.pop(key)
        return result
    elif isinstance(data_bag, Iterable):
        raise NotImplemented
    else:
        from utils.Exceptions import ParamTypeError
        raise ParamTypeError('data_bag', 'Iterable/Mapping', data_bag)

def group_by(data_dict, group_tag: str, by_tag: str, auto_save: bool=False):
    """
    把 data_dict 内容对象（group_tag）按照 by_tag 属性分组，得到 { by_tag: {obj1, obj2, }}
    :param data_dict: Mapping
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

        stored_set = grouped_dict[by_value]
        stored_set.add(index)
        grouped_dict[by_value] = stored_set

    if auto_save is True:
        from utils import ShelveWrapper
        ShelveWrapper.init_from(
            grouped_dict,
            os.path.join(DataConfig.operation_path, '{}_group_by_{}'.format(group_tag, by_tag))
        ).close()
    logger.debug_running('group {} by {}'.format(group_tag, by_tag), 'end')
    return grouped_dict


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
