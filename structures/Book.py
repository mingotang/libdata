# -*- encoding: UTF-8 -*-
import datetime
import re

from Interface import AbstractDataObject, AbstractEnvObject


class SumBook(AbstractDataObject, AbstractEnvObject):
    __attributes__ = ('index', 'lib_index', 'name', 'author', )

    def __init__(self, index: str, lib_index: str, name: str, author: str, ):
        AbstractDataObject.__init__(self)
        self.index = index
        self.lib_index = lib_index
        self.name = name
        self.author = author

    @property
    def hashable_key(self):
        return self.index

    @property
    def book_name(self):
        return BookName(self.name)

    @property
    def book_lib_index(self):
        return self.env.find_book_lib_index(self.lib_index)

    @staticmethod
    def define_table(meta):
        from sqlalchemy import MetaData, Table, Column, String
        assert isinstance(meta, MetaData)
        return Table(
            'sum_books', meta,
            Column('index', String, nullable=False, primary_key=True),
            Column('lib_index', String),
            Column('name', String),
            Column('author', String),
        )


class Book(SumBook):
    __attributes__ = ('index', 'lib_index', 'name', 'isbn', 'author', 'year', 'publisher', 'op_dt')

    def __init__(self, index: str, lib_index: str, name: str, isbn: str,
                 author: str, year: str, publisher: str, op_dt=None):
        SumBook.__init__(self, index=index, lib_index=lib_index, name=name, author=author)
        self.isbn = isbn
        self.year = year
        self.publisher = publisher
        self.op_dt = op_dt

    @property
    def cleaned_author(self):
        from extended import is_chinese_char
        if len(self.author) > 0:
            chi_count = 0
            for char in self.author:
                if is_chinese_char(char):
                    chi_count += 1
            # 中文作者名
            if chi_count >= 0.5:
                return re.sub(r'\W', '', self.author)
            else:
                return self.author
        else:
            return ''

    @property
    def book_isbn(self):
        return BookISBN(self.isbn)

    @property
    def publish_year(self):
        year = int(self.year)
        if 1800 <= year <= datetime.date.today().year:
            return year
        else:
            return None

    @property
    def update_date(self):
        return datetime.datetime.strptime(self.op_dt, '%Y%m%d').date()

    def update_from(self, value):
        if isinstance(value, type(self)):
            # if self.update_date >= value.update_date:
            #     return self
            # else:
            for tag in self.__attributes__:
                if tag in value.__dict__:
                    if value.__dict__[tag] is not None:
                        if len(self.__dict__[tag]) < len(value.__dict__[tag]):
                            self.__dict__[tag] = value.__dict__[tag]
            return self
        else:
            from extended.Exceptions import ParamTypeError
            raise ParamTypeError('value', '{}'.format(self.__class__.__name__), value)

    def compare_by(self, **kwargs):
        for tag in kwargs:
            if tag not in self.__attributes__:
                raise AttributeError('Book has no attribute {}'.format(tag))
            else:
                if kwargs[tag] != getattr(self, tag):
                    return False
        return True

    @classmethod
    def init_from(cls, value):
        if isinstance(value, dict):
            new = cls(
                index=value['sysID'],
                lib_index=value['libIndexID'],
                name=value['bookname'],
                isbn=value['isbn'],
                author=value['author'],
                year=value['publish_year'],
                publisher=value['publisher'],
                op_dt=value['event_date'],
            )
        else:
            from extended.Exceptions import ParamTypeError
            raise ParamTypeError('value', 'dict', value)
        return new

    @staticmethod
    def define_table(meta):
        from sqlalchemy import MetaData, Table, Column, String
        assert isinstance(meta, MetaData)
        return Table(
            'books', meta,
            Column('index', String, nullable=False, primary_key=True),
            Column('lib_index', String),
            Column('name', String),
            Column('isbn', String),
            Column('author', String),
            Column('year', String),
            Column('publisher', String),
            Column('op_dt', String)
        )


# BOOK_NAME_BLACK_LIST = (
#     '与', '和', '的', '及', '及其',
#     'a', 's', 'of', 'or', 'for', 'and', 'on', 'in', 'to', 'the',
# )


class BookName(object):
    def __init__(self, data_book_name: str):

        self.__data__ = data_book_name

    @property
    def cleaned_list(self):
        # import time
        # import jieba
        # import jieba.analyse
        import jieba.posseg
        name_list = list()
        # for item in jieba.lcut(re.sub(r'[^+\w]', ' ', self.__data__)):
        for item, flag in jieba.posseg.cut(re.sub(r'[^+\w]', ' ', self.__data__)):
            # for item in jieba.analyse.textrank(
            #         re.sub(r'[^+\w]', ' ', self.__data__), allowPOS=('ns', 'n', 'vn')
            # ):
            if flag in ('uj', 'p', 'c'):
                continue
            if len(re.sub(r' ', '', item)) == 0:
                continue
            if item.isdigit():
                continue
            # print(item, flag)
            # time.sleep(0.3)
            name_list.append(item.lower())
        return name_list


class BookISBN(object):
    """国际标准书号（International Standard Book Number）"""

    def __init__(self, data_isbn: str):
        if '(' in data_isbn and ')' in data_isbn:
            try:
                self.__data__ = re.match(r"([\w\-]*).*\(.*\)", data_isbn).group(1)
            except AttributeError:
                raise RuntimeError(data_isbn)
        elif ' ' in data_isbn:
            self.__data__ = data_isbn.split(' ')[0]
        else:
            self.__data__ = re.sub(r'\W', '', data_isbn)

    def __repr__(self):
        return self.__data__

    @property
    def check(self):
        """
        Check whether an isbn follows ISBN-10 rule  eg. ISBN 7302122601 or ISBN 7-302-12260-1
        or whether an isbn follows ISBN-13 rule eg. ISBN 9787122004185 or ISBN 978-7-122-00418-5
        :return: Bool
        """
        isbn_check = self.__data__.replace('-', '')  # remove '-'

        if len(isbn_check) == 10:  # ISBN-10 rule

            # 检查校验码是否满足于 数字、字母x X、罗马数字ⅹ Ⅹ
            if 48 <= ord(isbn_check[9]) <= 57:
                config = int(isbn_check[9])
            elif ord(isbn_check[9]) in (120, 88, 8569, 8553):
                config = 'X'  # 字母 X
            else:
                raise ValueError(self.__data__)

            # 计算校验码
            check = 0
            for i in range(0, 9, 1):
                check += int(isbn_check[i]) * (10 - i)
            check = 11 - check % 11

            # 检查校验码是否正确
            if 1 <= check <= 9:  # tail - N
                return config == check
            elif check == 11:  # tail - 0
                return config == 0
            elif check == 10:  # tail - X
                return config == 'X'
            else:
                return ValueError()

        elif len(isbn_check) == 13:  # ISBN-13 rule

            # 计算校验码
            check = 0
            for i in range(0, 12, 1):
                if i % 2 == 0:
                    check += int(isbn_check[i]) * 1
                else:
                    check += int(isbn_check[i]) * 3
            check = 10 - check % 10

            # 检查校验码是否正确
            if 1 <= check <= 9:  # tail - N
                return int(isbn_check[-1]) == check
            elif check == 10:
                return int(isbn_check[-1]) == 0
            else:
                return ValueError()

        elif len(isbn_check) == 0:
            return False

        elif len(isbn_check) <= 9 or 11 <= len(isbn_check) <= 12 or 14 <= len(isbn_check):
            return False

        else:
            raise ValueError("ISBN.check_isbn: param isbn '{0:s}' is not isbn-10 or isbn-13".format(self.__data__))


if __name__ == '__main__':
    from Environment import Environment
    from structures import Book

    env_inst = Environment()

    try:
        from structures import LibIndexClassObject
        unqualified_list = list()
        for book in env_inst.data_proxy.book_dict.values():
            assert isinstance(book, Book)
            book_lib_index = book.book_lib_index
            # if book.book_lib_index is None:
            #     print('\n'+'='*50)
            #     print(book.book_lib_index)
            #     print(book.lib_index)
            #     print(book.name)
            #     unqualified_list.append(book)
            if isinstance(book_lib_index, LibIndexClassObject):
                if len(book_lib_index.sub_class) == 0:
                    print('\n'+'='*50)
                    print(book.book_lib_index)
                    print(book.lib_index)
                    print(book.name)
                    unqualified_list.append(book)
        print(len(unqualified_list))
    except KeyboardInterrupt:
        env_inst.exit()
    finally:
        env_inst.exit()
