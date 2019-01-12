# -*- encoding: UTF-8 -*-
import json

from abc import abstractmethod
from extended import AbstractPersistObject


class AbstractEnvObject:

    @property
    def env(self):
        from Environment import Environment
        env = Environment.get_instance()
        assert isinstance(env, Environment)
        return env


class AbstractDataObject(AbstractPersistObject):
    __attributes__ = tuple()

    def __init__(self, *args, **kwargs):
        pass

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ', '.join([str(var) + ': ' + str(getattr(self, var)) for var in self.__attributes__])
        )

    def get_state(self):
        new_d = dict()
        for tag in self.__attributes__:
            new_d[tag] = getattr(self, tag)
        return json.dumps(new_d)

    @classmethod
    def set_state(cls, state: str):
        new_d = json.loads(state)
        return cls(**new_d)

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

    @staticmethod
    def define_table(meta):
        from sqlalchemy import MetaData
        assert isinstance(meta, MetaData)
        raise NotImplementedError
