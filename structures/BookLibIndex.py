# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
from Interface import AbstractEnvObject


class BookLibIndex(AbstractEnvObject):
    __index_class_map__ = None

    def __init__(self, data_lib_index: str):

        self.__data__ = data_lib_index

    @property
    def index_class(self):
        """索书号包含的类型"""
        if '/' in self.__data__:
            check_str = self.__data__.split('/')[0]
        elif ' ' in self.__data__:
            check_str = self.__data__.split(' ')[0]
        elif '#' in self.__data__:
            check_str = self.__data__.split('#')[0]
        elif len(self.__data__.replace(' ', '')) == 0:
            check_str = ''
        else:
            check_str = self.__data__

        if check_str in self.env.book_lib_index_code_name_map:
            return check_str
        else:
            for i in range(min(len(check_str), 8), -1, -1):
                if check_str[:i] in self.env.book_lib_index_code_name_map:
                    return check_str[:i]
            return ''

    @property
    def index_class_name(self):
        if len(self.index_class) > 0:
            return self.env.book_lib_index_code_name_map[self.index_class]
        else:
            return ''


if __name__ == '__main__':
    from Environment import Environment
    from structures import Book

    env_inst = Environment()
    d_p = env_inst.data_proxy

    try:
        this_dict = dict()
        for book in d_p.book_dict.values():
            assert isinstance(book, Book)
            lib_index = book.book_lib_index
            if not isinstance(lib_index.index_class_name, str):
                this_dict[lib_index.index_class] = book
        this_set = set(this_dict.keys())
        this_list = list(this_set)
        this_list.sort()
        for tag in this_list:
            print('lib_index: {}, book: {}'.format(tag, this_dict[tag]))
            # if len(lib_index.index_class_name) == 0:
            #     print(lib_index.index_class, lib_index.index_class_name)
    except KeyboardInterrupt:
        d_p.close()
    finally:
        d_p.close()
