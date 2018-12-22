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

    @property
    def hashable_key(self):
        raise NotImplementedError

    @abstractmethod
    def update_from(self, *args, **kwargs):
        """以相关信息更新数据对象 -> DataObject/None"""
        raise NotImplementedError

    @classmethod
    def init_from(cls, *args, **kwargs):
        """以相关信息创建数据对象 -> DataObject"""
        raise NotImplementedError

    @abstractmethod
    def compare_by(self, *args, **kwargs):
        """根据相关信息进行数据比较 -> DataObject"""
        raise NotImplementedError


class AbstractCollector:
    __metaclass__ = ABCMeta

    @abstractmethod
    def add(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def delete(self):
        raise NotImplementedError


class AbstractPersist:
    __metaclass__ = ABCMeta

    def set_state(self, type_s: type, state):
        """
        从 state 信息设定对象
        :param type_s: state 数据类型
        :param state: 数据内容
        :return: None
        """
        assert isinstance(state, type_s)
        raise NotImplementedError

    def get_state(self, type_s: type):
        """
        获取对象数据内容 state
        :param type_s: state 的数据类型
        :return: type_s
        """
        raise NotImplementedError

    @classmethod
    def set_state_str(cls, state: str):
        raise NotImplementedError

    def get_state_str(self):
        raise NotImplementedError

    @classmethod
    def set_state_dict(cls, state: dict):
        raise NotImplementedError

    def get_state_dict(self):
        raise NotImplementedError


class AbstractRecordable:
    __metaclass__ = ABCMeta

    @abstractmethod
    def record(self):
        """
        记录相关数据
        :return: dict
        """
        raise NotImplementedError
