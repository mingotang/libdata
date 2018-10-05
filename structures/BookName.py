# -*- encoding: UTF-8 -*-
import re

import jieba


BLACK_LIST = (
    '与', '和', '的', '及', '及其',
    'a', 's', 'of', 'or', 'for', 'and', 'on', 'in', 'to', 'the',
)


class BookName(object):
    def __init__(self, data_book_name: str):

        self.__data__ = data_book_name

    @property
    def cleaned_list(self):
        name_list = list()
        for item in list(jieba.cut(re.sub(r'\W', ' ', self.__data__))):
            if len(re.sub(r' ', '', item)) == 0:
                continue
            if item.lower() in BLACK_LIST:
                continue
            if item.isdigit():
                continue
            name_list.append(item.lower())
        return name_list
