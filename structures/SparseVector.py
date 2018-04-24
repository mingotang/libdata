# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


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
