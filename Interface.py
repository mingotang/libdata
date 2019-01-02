# -*- encoding: UTF-8 -*-
import json

from abc import abstractmethod


class AbstractDataObject(object):
    __attributes__ = tuple()

    def __init__(self, *args, **kwargs):
        pass

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ', '.join([str(var) + ': ' + str(getattr(self, var)) for var in self.__attributes__])
        )

    @classmethod
    def set_state_str(cls, state: str):
        return cls.set_state_dict(json.loads(state))

    def get_state_str(self):
        return json.dumps(self.get_state_dict())

    @classmethod
    def set_state_dict(cls, state: dict):
        return cls(**state)

    def get_state_dict(self):
        state = dict()
        for tag in self.__attributes__:
            state[tag] = getattr(self, tag)
        return state

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


# class AbstractDataStructure()
