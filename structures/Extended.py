# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
from collections import Iterable


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
        if lower_limit is not None:
            for tag in self.keys():
                if self.__getitem__(tag) < higher_limit:
                    self.__delitem__(tag)

        if higher_limit is not None:
            for tag in self.keys():
                if self.__getitem__(tag) > higher_limit:
                    self.__delitem__(tag)

        return self


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
