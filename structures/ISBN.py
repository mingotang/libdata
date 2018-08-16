# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


class ISBN(object):
    """国际标准书号（International Standard Book Number）"""

    def __init__(self, data_isbn: str):

        self.__data__ = data_isbn

    @staticmethod
    def check_isbn(isbn: str):
        """
        Check whether an isbn follows ISBN-10 rule  eg. ISBN 7302122601 or ISBN 7-302-12260-1
        or whether an isbn follows ISBN-13 rule eg. ISBN 9787122004185 or ISBN 978-7-122-00418-5
        :param isbn: isbn in string
        :return: Bool
        """
        isbn_check = isbn.replace('-', '')  # remove '-'

        if len(isbn_check) == 10:  # ISBN-10 rule

            # 检查校验码是否满足于 数字、字母x X、罗马数字ⅹ Ⅹ
            if 48 <= ord(isbn_check[9]) <= 57:
                config = int(isbn_check[9])
            elif ord(isbn_check[9]) in (120, 88, 8569, 8553):
                config = 'X'  # 字母 X
            else:
                raise ValueError(isbn)

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

        else:
            raise ValueError('ISBN.check_isbn: param isbn {0:s} is not isbn-10 or isbn-13'.format(isbn_check))

    @staticmethod
    def is_isbn(isbn: str, isbn_type: int):
        """
        Check whether an isbn follows ISBN-10  eg. ISBN 7-302-12260-1,
        or whether an isbn follows ISBN-13  eg. ISBN 978-7-122-00418-5
        :param isbn:
        :param isbn_type:
        :return: Bool
        """
        raise NotImplementedError()
