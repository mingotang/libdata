# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


class CountingDict(dict):
    def __init__(self):
        dict.__init__(self)

    def __mul__(self, other):
        if isinstance(other, dict):
            result = 0
            for self_element in self.keys():
                if self_element in other:
                    result += self.__getitem__(self_element) * other[self_element]
            return result
        else:
            raise TypeError()

    @classmethod
    def init_from(cls, obj):
        from collections.abc import Iterable
        assert isinstance(obj, Iterable)
        new_cd = cls()
        for item in obj:
            new_cd.count(item)
        return new_cd

    def set(self, element, value):
        self.__setitem__(element, value)

    def count(self, element, step=1):
        try:
            self.__setitem__(element, self.__getitem__(element) + step)
        except KeyError:
            self.__setitem__(element, step)

    def sort(self, inverse=False):
        """ 按照值从小到大排序 """
        stored_list = list(self.keys())
        for index_x in range(len(stored_list)):
            for index_y in range(index_x + 1, len(stored_list)):
                if self[stored_list[index_x]] > self[stored_list[index_y]]:
                    stored_list[index_x], stored_list[index_y] = stored_list[index_y], stored_list[index_x]
        if inverse is True:
            stored_list.reverse()
            return stored_list
        else:
            return stored_list

    def weights(self, tag_or_list=None):
        """根据 tag_or_list 的标签收集权重信息"""
        from collections import Iterable
        total_num = 0
        if isinstance(tag_or_list, Iterable):
            for tag in tag_or_list:
                total_num += self.__getitem__(tag)
        elif isinstance(tag_or_list, type(None)):
            for tag in self.keys():
                total_num += self.__getitem__(tag)
        else:
            raise TypeError()
        return total_num

    def trim(self, lower_limit=None, higher_limit=None):
        """修剪值不符合要求的标签"""
        if lower_limit is not None:
            for tag in self.keys():
                if self.__getitem__(tag) < higher_limit:
                    self.__delitem__(tag)

        if higher_limit is not None:
            for tag in self.keys():
                if self.__getitem__(tag) > higher_limit:
                    self.__delitem__(tag)

        return self

    @property
    def sum(self):
        result = 0
        for value in self.values():
            result += value
        return result


class DataDict(dict):

    def __init__(self, data_type: type = None):
        super(DataDict, self).__init__()

        self.__data_type__ = data_type

    @classmethod
    def init_from(cls, data_type: type, obj):
        from collections.abc import Mapping
        if isinstance(obj, Mapping):
            new_d = cls(data_type=data_type)
            for key, value in obj.items():
                if not isinstance(data_type, type(None)):
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

    def trim_between_range(self, attr_tag: str, range_start, range_end, include_start: bool = True,
                           include_end: bool = False, inline: bool = False):
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

    def trim_by_range(self, attr_tag: str, range_iterable, inline: bool = False):
        """

        :param attr_tag:
        :param range_iterable:
        :param inline:
        :return: DataDict
        """
        if isinstance(range_iterable, (set, frozenset, list, tuple)):
            range_iterable = frozenset(range_iterable)
        elif isinstance(range_iterable, (str, int, float)):
            range_iterable = (range_iterable, )
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

    def trim_exclude_range(self, attr_tag: str, exclude_iterable, inline: bool = False):
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
        grouped_dict = DataDict(DataDict)

        for index, val in self.items():
            obj = self.__getitem__(index)
            by_value = getattr(obj, by_tag)

            if by_value is None:
                continue

            if not isinstance(by_value, str):
                by_value = str(by_value)

            if len(by_value) == 0:  # jump to next iteration if no content
                continue

            if by_value not in grouped_dict:
                grouped_dict[by_value] = DataDict(self.__data_type__)

            grouped_dict[by_value][index] = val

        return grouped_dict

    def group_attr_set_by(self, group_attr: str, by_attr: str):
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
            grouped_dict[key].add(getattr(obj, group_attr))

        return grouped_dict

    def neighbor_attr_by(self, neighbor_tag: str, shadow_tag: str):
        """
        根据另一个属性(shadow_tag)建立同一个属性不同数据的联系集 -> dict( neighbor_tag_1: set(neighbor_tag_2, ...))
        :param neighbor_tag:
        :param shadow_tag:
        :return: dict( neighbor_tag_1: set(neighbor_tag_2, ...))
        """
        neighbor_dict = dict()

        first_level_index = self.group_attr_set_by(group_attr=shadow_tag, by_attr=neighbor_tag)
        second_level_index = self.group_attr_set_by(group_attr=neighbor_tag, by_attr=shadow_tag)
        for first_k in first_level_index.keys():
            neighbor_dict[first_k] = set()
            for second_k in first_level_index[first_k]:
                neighbor_dict[first_k].update(second_level_index[second_k])

        return neighbor_dict

    def collect_attr_set(self, attr_tag: str):
        """
        收集出现过的属性内容
        :param attr_tag: str
        :return: set()
        """
        collected_set = set()

        for obj in self.values():
            collected_set.add(getattr(obj, attr_tag))

        return collected_set

    def collect_attr_list(self, attr_tag: str):
        collected_list = list()

        for obj in self.values():
            collected_list.append(getattr(obj, attr_tag))

        return collected_list

    def count_attr(self, attr_tag: str):
        """
        对出现过的属性内容计数
        :param attr_tag: str
        :return: CountingDict
        """
        counted_dict = CountingDict()

        for obj in self.values():
            counted_dict.count(getattr(obj, attr_tag))

        return counted_dict

    def sort_by_attr(self, attr_tag: str):
        new_list = OrderedList(self.__data_type__, attr_tag)
        new_list.extend(list(self.values()))
        return new_list


class OrderedList(object):
    def __init__(self, obj_type: type, sort_attribute: str):
        """
        根据 sort_attribute 排序的类 list 类型
        :param obj_type: OrderedList 可以储存的数据类型
        :param sort_attribute: 排序的标签依据
        """
        self.__type__ = obj_type
        self.__stag__ = sort_attribute
        self.__data__ = list()

    def __find_index__(self, p_object):
        this_index = getattr(p_object, self.__stag__)
        for i in range(self.__data__.__len__()):
            if getattr(self.__data__.__getitem__(i), self.__stag__) <= this_index:
                continue
            else:
                return i
        return self.__data__.__len__()

    @classmethod
    def init_from(cls, inst, obj_type: type, sort_attribute: str):
        """ create a list according to inst -> OrderedList """
        from collections import Iterable, Mapping
        new_obj = cls(obj_type, sort_attribute)
        if isinstance(inst, Iterable):
            for item in inst:
                new_obj.append(item)
        elif isinstance(inst, Mapping):
            for item in inst.values():
                new_obj.append(item)
        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('inst', 'Iterable/Mapping', inst)
        return new_obj

    def append(self, p_object):
        """ add p_object to this list -> None """
        if isinstance(p_object, self.__type__):
            self.__data__.insert(self.__find_index__(p_object), p_object)
        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('p_object', '{}'.format(self.__type__), p_object)

    def copy(self):
        """ create a copy of this list -> list"""
        return [var for var in self.__data__]

    def count(self, p_object):
        """ count the appearance time of p_object -> int"""
        if isinstance(p_object, self.__type__):
            count = 0
            for i in range(self.__data__.__len__()):
                if self.__data__.__getitem__(i) == p_object:
                    count += 1
            return count
        else:
            return 0

    def extend(self, iterable):
        from collections import Iterable
        if isinstance(iterable, Iterable):
            for item in iterable:
                self.append(item)
        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('iterable', 'Iterable', iterable)

    def index(self, value, start=None, stop=None):
        """
        L.index(value, [start, [stop]]) -> integer -- return first index of value.
        Raises ValueError if the value is not present.
        """
        s = start if isinstance(start, int) else 0
        e = stop if isinstance(stop, int) else self.__data__.__len__()
        for i in range(s, e):
            if self.__data__.__getitem__(i) == value:
                return i
        raise ValueError

    def pop(self, index=None):
        """
        L.pop([index]) -> item -- remove and return item at index (default last).
        Raises IndexError if list is empty or index is out of range.
        """
        return self.__data__.pop(index)

    def remove(self, value):
        """
        L.remove(value) -> None -- remove first occurrence of value.
        Raises ValueError if the value is not present.
        """
        self.__data__.remove(value)

    def get(self, k: int, d=None):
        try:
            return self.__getitem__(k)
        except IndexError:
            return d

    def __delitem__(self, index: int):
        self.__data__.__delitem__(index)

    def __eq__(self, value):
        """ Return self==value. """
        if isinstance(value, (list, type(self))):
            if self.__len__() == len(value):
                for i in range(self.__len__()):
                    if self[i] != value[i]:
                        return False
                return True
            else:
                return False
        else:
            return False

    def __len__(self):
        return self.__data__.__len__()

    def __getitem__(self, y: int):
        self.__data__.__getitem__(y)

    def __reversed__(self):
        """ L.__reversed__() -- return a reverse iterator over the list """
        for i in range(0, self.__data__.__len__(), -1):
            yield self.__data__.__getitem__(i)

    def find_next(self, p_object, count: int = 1):
        """find object next to p_object -> p_object/list, return None if no result found."""
        # check param
        if isinstance(p_object, self.__type__):
            for index in range(len(self.__data__)):
                if getattr(p_object, self.__stag__) < getattr(self.__data__[index], self.__stag__):
                    if count == 1:
                        return self.__data__[index]
                    elif count > 1:
                        if index + count <= len(self.__data__):
                            return self.__data__[index:index + count - 1]
                        else:
                            return self.__data__[index:]
                    else:
                        from utils.Exceptions import ParamOutOfRangeError
                        raise ParamOutOfRangeError('count', (1, 'infinite'), count)
            return None
        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('p_object', self.__type__.__name__, p_object)

    def find_next_by(self, attr_data, count: int = 1):
        for index in range(len(self.__data__)):
            if attr_data < getattr(self.__data__[index], self.__stag__):
                if count == 1:
                    return self.__data__[index]
                elif count > 1:
                    if index + count <= len(self.__data__):
                        return self.__data__[index:index + count - 1]
                    else:
                        return self.__data__[index:]
                else:
                    from utils.Exceptions import ParamOutOfRangeError
                    raise ParamOutOfRangeError('count', (1, 'infinite'), count)
        return None

    def trim_between_range(self, attr_tag: str, range_start, range_end,
                           include_start: bool = True, include_end: bool = False, resort_tag: bool = None):
        """
        在列表内容中删减出需要的内容
        :param attr_tag: 删减的标签
        :param range_start:
        :param range_end:
        :param include_start: 是否包含开始值
        :param include_end: 是否包含结束值
        :param resort_tag: 是否重新根据另一个标签（而不是原列表排序标签）排序
        :return: new OrderedList
        """
        trimed_list = list()
        for d_v in self.__data__:
            if include_start is True and include_end is True:
                if range_start <= getattr(d_v, attr_tag) <= range_end:
                    trimed_list.append(d_v)
            elif include_start is True and include_end is False:
                if range_start <= getattr(d_v, attr_tag) < range_end:
                    trimed_list.append(d_v)
            elif include_start is False and include_end is True:
                if range_start < getattr(d_v, attr_tag) <= range_end:
                    trimed_list.append(d_v)
            else:
                if range_start < getattr(d_v, attr_tag) < range_end:
                    trimed_list.append(d_v)

        if resort_tag is None:
            return OrderedList.init_from(trimed_list, self.__type__, self.__stag__)
        elif isinstance(resort_tag, str):
            return OrderedList.init_from(trimed_list, self.__type__, resort_tag)
        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('resort_tag', 'str/NoneType', resort_tag)

    def to_list(self):
        """将列表内容存入一个新的列表（不排序）中 -> list"""
        return self.__data__

    def to_attr_list(self, attr_tag: str):
        new_list = list()
        for value in self.__data__:
            new_list.append(getattr(value, attr_tag))
        return new_list

    def to_dict(self, index_tag: str = None):
        """
        将列表内容存入一个新的字典中
        :param index_tag:
        :return: dict
        """
        new_dict = dict()
        if index_tag is None:
            for value in self.__data__:
                new_dict[getattr(value, self.__stag__)] = value
        else:
            for value in self.__data__:
                new_dict[getattr(value, index_tag)] = value
        return new_dict
