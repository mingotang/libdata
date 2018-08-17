# -*- encoding: UTF-8 -*-
from abc import ABCMeta, abstractmethod


def get_root_path():
    """
    获取根目录绝对值
    :return: str
    """
    from os import path
    return path.abspath(path.dirname(__file__))


class AbstractDataObject:
    __metaclass__ = ABCMeta

    @abstractmethod
    def update_from(self, *args, **kwargs):
        """以相关信息更新数据对象 -> DataObject/None"""
        raise NotImplemented

    @classmethod
    def init_from(cls, *args, **kwargs):
        """以相关信息创建数据对象 -> DataObject"""
        raise NotImplemented

    @abstractmethod
    def compare_by(self, *args, **kwargs):
        """根据相关信息进行数据比较 -> DataObject"""
        raise NotImplemented


class AbstractPersist:
    __metaclass__ = ABCMeta

    @abstractmethod
    def set_state(self, type_s: type, state):
        """
        从 state 信息设定对象
        :param type_s: state 数据类型
        :param state: 数据内容
        :return: None
        """
        assert isinstance(state, type_s)
        raise NotImplemented

    @abstractmethod
    def get_state(self, type_s: type):
        """
        获取对象数据内容 state
        :param type_s: state 的数据类型
        :return: type_s
        """
        raise NotImplemented


class AbstractRecordable:
    __metaclass__ = ABCMeta

    @abstractmethod
    def record(self):
        """
        记录相关数据
        :return: dict
        """
        raise NotImplemented


class AbstractCollector:
    __metaclass__ = ABCMeta

    @abstractmethod
    def add(self, *args, **kwargs):
        raise NotImplemented

    @abstractmethod
    def delete(self):
        raise NotImplemented
