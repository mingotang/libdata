# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


class LibIndex(object):

    def __init__(self, data_lib_index: str):

        self.__data__ = data_lib_index

    @staticmethod
    def derive_specified_tag_list(lib_index: str):
        """
        dict{ 'content_class': x, }
        :param lib_index:
        :return:
        """
        lib_index_dict = dict()
        if '/' in lib_index:  # chinese lib index
            content_class = lib_index.split('/')[0]
        else:
            content_class = lib_index.split(' ')[0]
        if '.' in content_class:
            content_class = content_class.split('.')[0]
        if '-' in content_class:
            content_class = content_class.split('-')[0]
        lib_index_dict['content_class'] = content_class
        return lib_index_dict


# --------------------------------------------------------


if __name__ == '__main__':
    pass
