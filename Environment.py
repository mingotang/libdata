# -*- coding: utf-8 -*-
import os


class Environment(object):
    """
    变量传递结构，在程序的各个部分之间（特别是文件之间）传递各项参数

    需要注意，在 python 当中，结构化的内容在函数之间是引用传递的，比如 3 是值传递，而 [3,]就可以引用传递
    """
    _env = None

    def __init__(self):
        from Interface import get_root_path
        from utils import load_yaml
        Environment._env = self

        # public
        self.config = load_yaml(os.path.join(get_root_path(), 'config.yaml'))

        # private
        self.__data_proxy__ = None  # 数据接口

    @classmethod
    def get_instance(cls):
        """
        返回已经创建的 Environment 对象
        """
        if Environment._env is None:
            raise RuntimeError("Environment has not been created.")
        assert isinstance(Environment._env, Environment)
        return Environment._env

    @property
    def data_path(self):
        d_path = self.config.get('Resources', dict()).get('ShelveDataPath')
        if not os.path.exists(d_path):
            os.makedirs(d_path)
        return d_path

    @property
    def data_proxy(self):
        from modules.DataProxy import DataProxy
        assert isinstance(self.__data_proxy__, DataProxy), 'set DataProxy before using.'
        return self.__data_proxy__

    def set_data_proxy(self, data_proxy):
        from modules.DataProxy import DataProxy
        assert isinstance(data_proxy, DataProxy)
        self.__data_proxy__ = data_proxy