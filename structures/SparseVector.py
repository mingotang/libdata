# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
from collections import Mapping, Sized


class SparseVector(Mapping, Sized):
    """稀疏向量 类 defaultdict"""
    def __init__(self, length: int = None, default_value=0):
        assert isinstance(length, (type(None), int))
        self.__length__ = length
        self.data = dict()
        self.__default_value__ = default_value

    def __repr__(self):
        return str(self.copy_to_dict())

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
        return self.data.keys()

    def __contains__(self, item):
        return item in self.data

    def __mul__(self, other):
        """ * """
        if isinstance(other, SparseVector):
            assert self.__default_value__ == other.__default_value__
            # assert self.__len__() == other.__len__()
            tag_set = set(self.keys()).intersection(set(other.keys()))
            result = 0.0
            for tag in tag_set:
                result += self.__getitem__(tag) * other.__getitem__(tag)
            return result
        elif isinstance(other, (int, float)):
            new_vector = SparseVector(self.__len__(), default_value=self.__default_value__)
            for tag in self.keys():
                new_vector[tag] = other * self.__getitem__(tag)
            return new_vector
        elif isinstance(other, Mapping):
            tag_set = set(self.keys()).intersection(set(other.keys()))
            result = 0.0
            for tag in tag_set:
                result += self.__getitem__(tag) * other.__getitem__(tag)
            return result
        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('other', (SparseVector, int, float, Mapping), other)

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
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('other', SparseVector, other)

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
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('other', SparseVector, other)

    def update(self, obj):
        if isinstance(obj, Mapping):
            for k, v in obj.items():
                self.set(k, v)
        else:
            raise NotImplementedError

    def copy(self):
        new_vec = SparseVector(self.__length__, self.__default_value__)
        new_vec.update(self)
        return new_vec

    def copy_to_dict(self):
        new_dict = dict()
        new_dict.update(self)
        return new_dict

    def get(self, key):
        return self.__getitem__(key)

    def set(self, key, value):
        self.__setitem__(key, value)

    def set_length(self, length: int):
        self.__length__ = length

    @property
    def sum(self):
        total = 0
        for tag in self.data.keys():
            total += self.data[tag]
        return total

    @property
    def sum_squared(self):
        total = 0
        for tag in self.data.keys():
            total += self.data[tag] ** 2
        return total

    def normalization(self):
        return self * (1 / self.sum_squared)

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

    @property
    def has_size(self):
        return isinstance(self.__length__, int)
