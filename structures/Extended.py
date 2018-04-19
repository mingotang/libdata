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


class SparseVector(object):
    def __init__(self, length=None, default_value=0):
        assert isinstance(length, (type(None), int))
        self.__length__ = length
        self.data = dict()
        self.__default_value__ = default_value

    def __len__(self):
        if self.__length__ is None:
            raise RuntimeError('SparseVector defined without length.')
        else:
            return self.__length__

    def __setitem__(self, key, value):
        if value != self.__default_value__:
            self.data.__setitem__(key, value)
        else:
            if key in self.data:
                del self.data[key]
            else:
                pass

    def __getitem__(self, key):
        try:
            return self.data.__getitem__(key)
        except KeyError:
            return self.__default_value__

    def __iter__(self):
        assert isinstance(self.__length__, int), str('SparseVector defined without length.')
        for k in self.data.keys():
            yield k

    def __contains__(self, item):
        return item in self.data

    def __mul__(self, other):
        """ * """
        if isinstance(other, SparseVector):
            assert self.__len__() == other.__len__() and self.__default_value__ == other.__default_value__
            result = 0.0
            for tag in other:
                result += self.__getitem__(tag) * other.__getitem__(tag)
            return result
        elif isinstance(other, (int, float)):
            new_vector = SparseVector(self.__len__(), default_value=self.__default_value__)
            for tag in self.keys():
                new_vector[tag] = other * self.__getitem__(tag)
        else:
            raise NotImplemented

    def __sub__(self, other):
        """ - """
        if isinstance(other, SparseVector):
            assert self.__len__() == other.__len__() and self.__default_value__ == other.__default_value__
            new_vector = SparseVector(self.__len__(), default_value=self.__default_value__)
            tag_set = set(self.data.keys()).union(set(other.keys()))
            for tag in tag_set:
                new_vector[tag] = self.__getitem__(tag) - other.__getitem__(tag)
            return new_vector
        else:
            raise NotImplemented

    def __add__(self, other):
        """ + """
        if isinstance(other, SparseVector):
            assert self.__len__() == other.__len__() and self.__default_value__ == other.__default_value__
            new_vector = SparseVector(self.__len__(), default_value=self.__default_value__)
            tag_set = set(self.data.keys()).union(set(other.keys()))
            for tag in tag_set:
                new_vector[tag] = self.__getitem__(tag) + other.__getitem__(tag)
            return new_vector
        else:
            raise NotImplemented

    def keys(self):
        for k in self.data.keys():
            yield k

    def get(self, key):
        return self.__getitem__(key)

    def set(self, key, value):
        self.__setitem__(key, value)

    def set_length(self, length: int):
        self.__length__ = length

    @property
    def sum(self):
        total = 0
        for tag in self.data:
            total += self.data[tag]
        return total

    @property
    def sum_squared(self):
        total = 0
        for tag in self.data:
            total += self.data[tag] ** 2
        return total


class ResultStore(object):
    def __init__(self):
        self.data = dict()


