# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


class LibIndex(object):
    __index_class_map__ = None

    def __init__(self, data_lib_index: str):

        self.__data__ = data_lib_index

    @property
    def index_class(self):
        if '/' in self.__data__:
            return self.__data__.split('/')[0]
        elif ' ' in self.__data__:
            return self.__data__.split(' ')[0]
        elif '#' in self.__data__:
            return self.__data__.split('#')[0]
        elif len(self.__data__.replace(' ', '')) == 0:
            return ''
        else:
            if self.__data__ in self.index_class_map:
                return self.__data__
            else:
                for i in range(min(len(self.__data__), 8), 0, -1):
                    if self.__data__[:i] in self.index_class_map:
                        return self.__data__[:i]
                return ''

    @property
    def index_class_name(self):
        if len(self.index_class) > 0:
            return self.index_class_map[self.index_class]
        else:
            return ''

    @property
    def index_class_map(self):
        if LibIndex.__index_class_map__ is None:
            from os import path
            from pandas import read_csv
            pd_data = read_csv(path.join('..', 'data', 'ChineseLibraryBookClassification.csv'), header=None)
            i_c_map = dict()
            for index in pd_data.index:
                i_c_map[pd_data.loc[index, 0]] = pd_data.loc[index, 1]
            LibIndex.__index_class_map__ = i_c_map
        assert isinstance(LibIndex.__index_class_map__, dict), type(LibIndex.__index_class_map__)
        return LibIndex.__index_class_map__


if __name__ == '__main__':
    from Environment import Environment
    from modules.DataProxy import DataProxy
    from structures import Book

    env_inst = Environment()
    d_p = DataProxy()
    env_inst.set_data_proxy(d_p)

    try:
        for book in d_p.books.values():
            assert isinstance(book, Book)
            lib_index = book.book_lib_index
            # lib_index.index_class_map
            if lib_index.index_class is None:
                print(book.lib_index, book)
    except KeyboardInterrupt:
        d_p.close()
    finally:
        d_p.close()
