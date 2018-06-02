# -*- encoding: UTF-8 -*-
from abc import ABCMeta, abstractmethod


def get_root_path():
    from os import path
    return path.abspath(path.dirname(__file__))


class AbstractDataManager:
    __metaclass__ = ABCMeta

    @abstractmethod
    def include(self, value):
        """include value to data"""
        raise NotImplementedError

    @abstractmethod
    def extend(self, value_list):
        raise NotImplementedError


class AbstractDataObject:
    __metaclass__ = ABCMeta

    @abstractmethod
    def update_from(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
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


class AbstractCollector:
    __metaclass__ = ABCMeta

    @abstractmethod
    def add(self, *args, **kwargs):
        raise NotImplementedError
