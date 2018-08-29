# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


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

    def find_next(self, p_object, count: int=1):
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

    def find_next_by(self, attr_data, count: int=1):
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


    def trim(self, attr_tag: str, range_start, range_end,
             include_start: bool=True, include_end: bool=False, resort_tag=None):
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

    def to_dict(self, index_tag: str):
        """
        将列表内容存入一个新的字典中
        :param index_tag:
        :return: dict
        """
        new_dict = dict()
        for value in self.__data__:
            new_dict[getattr(value, index_tag)] = value
        return new_dict
