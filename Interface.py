# -*- encoding: UTF-8 -*-
from abc import ABCMeta, abstractmethod


def get_root_path():
    from os import path
    return path.abspath(path.dirname(__file__))


class AbstractDataObject:
    __metaclass__ = ABCMeta

    @abstractmethod
    def update_from(self, *args, **kwargs):
        raise NotImplemented

    @classmethod
    def init_from(cls, *args, **kwargs):
        raise NotImplemented

    @abstractmethod
    def compare_by(self, *args, **kwargs):
        raise NotImplemented


class AbstractPersist:
    __metaclass__ = ABCMeta

    @abstractmethod
    def set_state(self, type_s: type, state):
        assert isinstance(state, type_s)
        raise NotImplemented

    @abstractmethod
    def get_state(self, type_s: type):
        raise NotImplemented


class AbstractRecordable:
    __metaclass__ = ABCMeta

    @abstractmethod
    def record(self):
        raise NotImplemented


class AbstractCollector:
    __metaclass__ = ABCMeta

    @abstractmethod
    def add(self, *args, **kwargs):
        raise NotImplemented
