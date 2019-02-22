# -*- coding: utf-8 -*-
import os
import platform


class Environment(object):
    """
    变量传递结构，在程序的各个部分之间（特别是文件之间）传递各项参数

    需要注意，在 python 当中，结构化的内容在函数之间是引用传递的，比如 3 是值传递，而 [3,]就可以引用传递
    """
    _env = None

    def __init__(self):
        from utils import load_yaml, get_logger
        if Environment._env is None:
            Environment._env = self
        else:
            raise RuntimeError("Environment has been created.")

        # public
        self.config = load_yaml(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.yaml'))
        self.log = get_logger(self.__class__.__name__)

        # private
        self.__data__ = dict()

    @classmethod
    def get_instance(cls):
        """
        返回已经创建的 Environment 对象
        """
        if Environment._env is None:
            Environment()
        assert isinstance(Environment._env, Environment)
        return Environment._env

    @property
    def data_path(self):
        if platform.system() == 'Darwin':
            d_path = os.path.expanduser(self.config.get('Resources', dict()).get('MacDataPath'))
        else:
            raise NotImplementedError(platform.system())
        if not os.path.exists(d_path):
            os.makedirs(d_path)
        return d_path

    @property
    def data_proxy(self):
        from modules.DataProxy import DataProxy
        data_proxy = self.__data__.get('data_proxy')
        if data_proxy is None:
            data_proxy = DataProxy(data_path=self.data_path)
            self.__data__.__setitem__('data_proxy', data_proxy)
        assert isinstance(data_proxy, DataProxy), 'set DataProxy before using.'
        return data_proxy

    @property
    def book_lib_index_code_name_map(self):
        """索引号 编码 - 名称 的字典 -> dict"""
        book_lib_index_code_name_map = self.__data__.get('book_lib_index_code_name_map')
        if book_lib_index_code_name_map is None:
            self.__load_book_index_info__()
            book_lib_index_code_name_map = self.book_lib_index_code_name_map
        assert isinstance(book_lib_index_code_name_map, dict)
        return book_lib_index_code_name_map

    def __load_book_index_info__(self):
        from pandas import read_csv
        from structures import LibIndexClassObject
        pd_data = read_csv(
            os.path.join(self.root_path, 'data', 'ChineseLibraryBookClassification.csv'),
            header=None,
        )
        pd_data.fillna(value='', inplace=True)
        book_lib_index_code_name_map = dict()
        for index in pd_data.index:
            new_obj = LibIndexClassObject(
                pd_data.loc[index, 0], pd_data.loc[index, 1], pd_data.loc[index, 2], pd_data.loc[index, 3]
            )
            if len(new_obj.base_class) > 0:
                book_lib_index_code_name_map[new_obj.base_class] = new_obj
            elif len(new_obj.sub_class) > 0:
                book_lib_index_code_name_map[new_obj.sub_class] = new_obj
            elif len(new_obj.main_class) > 0:
                book_lib_index_code_name_map[new_obj.main_class] = new_obj
            else:
                raise NotImplementedError(new_obj)
        self.__data__.__setitem__('book_lib_index_code_name_map', book_lib_index_code_name_map)

    @property
    def root_path(self):
        return os.path.abspath(os.path.dirname(__file__))

    def exit(self):
        from extended import SqliteWrapper
        for obj in SqliteWrapper.connection_dict.values():
            obj.close()

        if 'data_proxy' in self.__data__:
            self.__data__['data_proxy'].close()
