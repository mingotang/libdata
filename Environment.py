# -*- coding: utf-8 -*-
import os


class Environment(object):
    """
    变量传递结构，在程序的各个部分之间（特别是文件之间）传递各项参数

    需要注意，在 python 当中，结构化的内容在函数之间是引用传递的，比如 3 是值传递，而 [3,]就可以引用传递
    """
    _env = None

    def __init__(self):
        from utils import load_yaml
        if Environment._env is None:
            Environment._env = self
        else:
            raise RuntimeError("Environment has been created.")

        # public
        self.config = load_yaml(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.yaml'))

        # private
        self.__data_proxy__ = None  # 数据接口

    @classmethod
    def get_instance(cls):
        """
        返回已经创建的 Environment 对象
        """
        if Environment._env is None:
            Environment._env = Environment()
        assert isinstance(Environment._env, Environment)
        return Environment._env

    @property
    def data_path(self):
        d_path = self.config.get('Resources', dict()).get('DataPath')
        if not os.path.exists(d_path):
            os.makedirs(d_path)
        return d_path

    @property
    def data_proxy(self):
        from modules.DataProxy import DataProxy
        if self.__data_proxy__ is None:
            self.__data_proxy__ = DataProxy(data_path=self.config.get('Resources', dict()).get('DataPath'))
        assert isinstance(self.__data_proxy__, DataProxy), 'set DataProxy before using.'
        return self.__data_proxy__
