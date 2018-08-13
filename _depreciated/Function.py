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
