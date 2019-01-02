# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import re


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
    from modules.DataProxy import DataProxy
    from structures import Book

    env_inst = Environment()
    d_p = DataProxy()
    env_inst.set_data_proxy(d_p)

    try:
        for book in d_p.book_dict.values():
            assert isinstance(book, Book)
            isbn = book.book_isbn
            if book.index == '000891639':
                isbn.__data__ = '7-5078-1457-2'
            elif book.index == '000951589':
                isbn.__data__ = '978-7-5633-4578-6'
            try:
                if isbn.check is False:
                    print(isbn, book)
            except ValueError as e:
                print(book)
                raise e
    except KeyboardInterrupt:
        d_p.close()
    finally:
        d_p.close()
