# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


class DataDict(dict):

    def __init__(self, data_type: type=None):
        super(DataDict, self).__init__()

        self.__data_type__ = data_type

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
            return None
        else:
            return self.__data_type__

    def to_dict(self):
        new_d = dict()
        for k, v in self.items():
            new_d[k] = v
        return new_d

    def trim(self, attr_tag: str, range_start, range_end,
             include_start: bool=True, include_end: bool=False):
        """
        删选合适的数据进入内存 -> dict
        :param attr_tag:
        :param range_start:
        :param range_end:
        :param include_start:
        :param include_end:
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

            stored_set = grouped_dict[by_value]
            stored_set.add(index)
            grouped_dict[by_value] = stored_set

        return grouped_dict

    def group_attr_by(self, group_attr: str, by_attr: str):
        """
        建立属性之间映射的快速索引字典 -> dict( key: set())
        :param group_attr:
        :param by_attr:
        :return: dict( key: set())
        """
        grouped_dict = dict()

        for obj in self.values():
            key = getattr(obj, by_attr)
            if key not in grouped_dict:
                grouped_dict[key] = set()

            value = getattr(obj, group_attr)
            grouped_dict[key].add(value)

        return grouped_dict

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
