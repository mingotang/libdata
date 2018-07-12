# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


class OrderedList(object):
    def __init__(self, obj_type: type, sort_attribute: str):
        self.__type__ = obj_type
        self.__stag__ = sort_attribute
        self.__data__ = list()

    def __get_sorted_index__(self, p_object):
        return getattr(p_object, self.__stag__)

    def __find_index__(self, p_object):
        this_index = self.__get_sorted_index__(p_object)
        for i in range(self.__data__.__len__()):
            if self.__get_sorted_index__(self.__data__.__getitem__(i)) <= this_index:
                continue
            else:
                return i
        return self.__data__.__len__()

    @classmethod
    def init_from(cls, inst, obj_type: type, sort_attribute: str):
        from collections import Iterable, Mapping
        new_obj = cls(obj_type, sort_attribute)
        if isinstance(inst, Iterable):
            for item in inst:
                new_obj.append(item)
        elif isinstance(inst, Mapping):
            for item in inst.values():
                new_obj.append(item)
        else:
            raise TypeError('inst is not iterable/mapping')
        return new_obj

    def append(self, p_object):
        if isinstance(p_object, self.__type__):
            self.__data__.insert(self.__find_index__(p_object), p_object)
        else:
            raise TypeError('param p_object should be of type {} but got type {}'.format(self.__type__, type(p_object)))

    def copy(self):
        return [var for var in self.__data__]

    def count(self, p_object):
        if isinstance(p_object, self.__type__):
            count = 0
            for i in range(self.__data__.__len__()):
                if self.__data__.__getitem__(i) == p_object:
                    count += 1
            return count
        else:
            return 0

    def extend(self, iterable):
        for item in iterable:
            try:
                self.append(item)
            except TypeError:
                pass

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
        """find object next to p_object, raise ValueError if no result found."""
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
            raise ValueError

        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('p_object', self.__type__.__name__, p_object)

    def trim(self, attr_tag: str, range_start, range_end,
             include_start: bool=True, include_end: bool=False, resort_tag=None):

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
        return self.__data__

    def to_dict(self, index_tag: str):
        new_dict = dict()
        for value in self.__data__:
            new_dict[getattr(value, index_tag)] = value
        return new_dict
