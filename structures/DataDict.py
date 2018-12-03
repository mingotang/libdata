# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
from collections.abc import Mapping


class DataDict(dict):

    def __init__(self, data_type: type=None):
        super(DataDict, self).__init__()

        self.__data_type__ = data_type

    @classmethod
    def init_from(cls, data_type: type, obj):
        if isinstance(obj, Mapping):
            new_d = cls(data_type=data_type)
            for key, value in obj.items():
                if data_type != type(None):
                    assert isinstance(value, data_type)
                new_d[key] = value
            return new_d
        else:
            raise NotImplementedError

    def __repr__(self):
        content = '{\n'
        for key, value in self.items():
            content += '\t{}: {}\n'.format(key, value)
        content += '}'
        return content

    def copy(self):
        new_d = DataDict(data_type=self.type)
        for k, v in self.items():
            new_d.__setitem__(k, v)
        return new_d

    @property
    def type(self):
        if self.__data_type__ is None:
            for value in self.values():
                if value is not None:
                    return type(value)
            return type(None)
        else:
            return self.__data_type__

    def to_dict(self):
        new_d = dict()
        for k, v in self.items():
            new_d[k] = v
        return new_d

    def trim_between_range(self, attr_tag: str, range_start, range_end,
                           include_start: bool=True, include_end: bool=False,
                           inline: bool=False):
        """
        删选合适的数据进入内存 -> dict
        :param attr_tag:
        :param range_start:
        :param range_end:
        :param include_start:
        :param include_end:
        :param inline: whether modify data in self
        :return: DataDict
        """
        result = DataDict(data_type=self.type)

        if range_start is None:
            for key, value in self.items():
                result[key] = value
        else:
            if include_start is True:
                for key, value in self.items():
                    if range_start <= getattr(value, attr_tag):
                        result[key] = value
            else:
                for key, value in self.items():
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

        if inline is True:
            self.clear()
            self.update(result)
            return self
        else:
            return result

    def trim_by_range(self, attr_tag: str, range_iterable, inline: bool=False):
        """

        :param attr_tag:
        :param range_iterable:
        :param inline:
        :return: DataDict
        """
        if isinstance(range_iterable, (set, frozenset, list, tuple)):
            range_iterable = frozenset(range_iterable)
        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('range_iterable', (set, frozenset, list, tuple), range_iterable)

        result = DataDict(data_type=self.type)

        for key, value in self.items():
            if getattr(value, attr_tag) in range_iterable:
                result[key] = value

        if inline is True:
            self.clear()
            self.update(result)
            return self
        else:
            return result

    def trim_exclude_range(self, attr_tag: str, exclude_iterable, inline: bool=False):
        if isinstance(exclude_iterable, (set, frozenset, list, tuple)):
            exclude_iterable = frozenset(exclude_iterable)
        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('exclude_iterable', (set, frozenset, list, tuple), exclude_iterable)

        result = DataDict(data_type=self.type)

        for key, value in self.items():
            if getattr(value, attr_tag) not in exclude_iterable:
                result[key] = value

        if inline is True:
            self.clear()
            self.update(result)
            return self
        else:
            return result

    def group_by(self, by_tag: str):
        """
        把内容对象按照 by_tag 属性分组，得到 { by_tag: {obj1, obj2, }}
        :param by_tag: related attribute
        :return: dict( key: set())
        """
        grouped_dict = dict()

        for index in self.keys():
            obj = self.__getitem__(index)
            by_value = getattr(obj, by_tag)

            if by_value is None:
                continue

            if not isinstance(by_value, str):
                by_value = str(by_value)

            if len(by_value) == 0:  # jump to next iteration if no content
                continue

            if by_value not in grouped_dict:
                grouped_dict[by_value] = set()

            stored_set = grouped_dict.__getitem__(by_value)
            stored_set.add(index)
            grouped_dict[by_value] = stored_set

        return grouped_dict

    def group_attr_by(self, group_attr: str, by_attr: str):
        """
        建立属性之间映射的快速索引字典 -> dict( by_attr: set(group_attr, ))
        :param group_attr:
        :param by_attr:
        :return: dict( by_attr: set())
        """
        grouped_dict = dict()

        for obj in self.values():
            key = getattr(obj, by_attr)
            if key not in grouped_dict:
                grouped_dict[key] = set()

            value = getattr(obj, group_attr)
            grouped_dict[key].add(value)

        return grouped_dict

    def neighbor_attr_by(self, neighbor_tag: str, shadow_tag: str):
        """
        根据另一个属性(shadow_tag)建立同一个属性不同数据的联系集 -> dict( neighbor_tag_1: set(neighbor_tag_2, ...))
        :param neighbor_tag:
        :param shadow_tag:
        :return: dict( neighbor_tag_1: set(neighbor_tag_2, ...))
        """
        neighbor_dict = dict()

        first_level_index = self.group_attr_by(group_attr=shadow_tag, by_attr=neighbor_tag)
        second_level_index = self.group_attr_by(group_attr=neighbor_tag, by_attr=shadow_tag)
        for first_k in first_level_index.keys():
            neighbor_dict[first_k] = set()
            for second_k in first_level_index[first_k]:
                neighbor_dict[first_k].update(second_level_index[second_k])

        return neighbor_dict

    def collect_attr(self, attr_tag: str):
        """
        收集出现过的属性内容
        :param attr_tag: str
        :return: set()
        """
        collected_set = set()

        for obj in self.values():
            collected_set.add(getattr(obj, attr_tag))

        return collected_set

    def count_attr(self, attr_tag: str):
        """
        对出现过的属性内容计数
        :param attr_tag: str
        :return: CountingDict
        """
        from .CountingDict import CountingDict
        counted_dict = CountingDict()

        for obj in self.values():
            counted_dict.count(getattr(obj, attr_tag))

        return counted_dict
