# -*- encoding: UTF-8 -*-
from abc import ABCMeta, abstractmethod, abstractclassmethod


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
    def update_from(self, *args, **kwargs):
        raise NotImplementedError

    @abstractclassmethod
    def init_from(cls, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def compare_by(self, *args, **kwargs):
        raise NotImplementedError


class AbstractPersistent:
    __metaclass__ = ABCMeta

    @abstractmethod
    def set_state(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_state(self):
        raise NotImplementedError
