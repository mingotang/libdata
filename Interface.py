# -*- encoding: UTF-8 -*-
from abc import ABCMeta, abstractmethod, abstractclassmethod, abstractstaticmethod


class AbstractDataManager:
    __metaclass__ = ABCMeta

    @abstractmethod
    def include(self, value):
        """include value to data"""
        raise NotImplementedError

    @abstractmethod
    def __update_value__(self, value):
        """update value in data if value already in data"""
        raise NotImplementedError

    @abstractmethod
    def __add_value__(self, value):
        """add value to data if value is not in data"""
        raise NotImplementedError

    @abstractmethod
    def extend(self, value_list):
        raise NotImplementedError


class AbstractDataObject:
    __metaclass__ = ABCMeta

    @abstractmethod
    def update_from(self, value):
        raise NotImplementedError

    @abstractclassmethod
    def init_from(cls, value):
        raise NotImplementedError
