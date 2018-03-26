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

    def count(self, element, step=1):
        try:
            self.__setitem__(element, self.__getitem__(element) + step)
        except KeyError:
            self.__setitem__(element, step)

    def sort_by_weights(self, inverse=False):
        """ 按照值从小到大排序 """
        stored_list = list(self.keys())
        for index_x in range(len(stored_list)):
            for index_y in range(index_x + 1, len(stored_list)):
                if self[stored_list[index_x]] > self[stored_list[index_y]]:
                    stored_list[index_x], stored_list[index_y] = stored_list[index_y], stored_list[index_x]
        if inverse is True:
            return stored_list.reverse()
        else:
            return stored_list

    def total_weights(self, tag_list):
        if isinstance(tag_list, (list, tuple, set, frozenset)):
            total_num = 0
            if len(tag_list) > 0:
                for tag in tag_list:
                    total_num += self.__getitem__(tag)
            else:
                for tag in self.keys():
                    total_num += self.__getitem__(tag)
            return total_num
        else:
            raise TypeError()


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

    def __getitem__(self, key):
        try:
            return self.data.__getitem__(key)
        except KeyError:
            return self.__default_value__

    def __iter__(self):
        assert isinstance(self.__length__, int), str('SparseVector defined without length.')
        for k in self.data:
            yield k

    def __contains__(self, item):
        return item in self.data

    def __mul__(self, other):
        if isinstance(other, (SparseVector, dict)):
            assert self.__len__() == other.__len__()
            result = 0.0
            for tag in other:
                try:
                    result += self.data.__getitem__(tag) * other.__getitem__(tag)
                except KeyError:
                    pass
            return result
        else:
            raise NotImplementedError

    def get(self, key):
        return self.__getitem__(key)

    def set(self, key, value):
        self.__setitem__(key, value)
