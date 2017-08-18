# -*- coding: utf-8 -*-
import re
import copy
from modules.BasicDataSetting import *
# --------------------------------------------------------
# checking isbn
def isISBN10(isbn):
    """Check whether an isbn follows ISBN-10  eg. ISBN 7-302-12260-1"""
    if len(isbn) != 13:
        return False
    isbn_new = copy.copy(isbn)
    isbn_check = isbn_new.replace('-', '')
    if len(isbn_check) != 10:
        return False
    num_part = isbn_check[0:9]
    check_part = isbn_check[9:10]
    num_part = re.sub(r'[^0123456789]', '', num_part)
    check_part = re.sub(r'[^0123456789Xx]', '', check_part)
    isbn_check = num_part + check_part
    if len(isbn_check) != 10:
        return False
    else:
        config = isbn_check[-1]
        if config >= '0' and config <= '9':
            config = int(config)
        check = 0
        for i in range(0, 9, 1):
            check += int(isbn_check[i]) * (10 - i)
        check = check % 11
        check = int(11 - int(check))
        if check >= 1 and check <= 9:  # tail - N
            if config != check:
                return False
            else:
                return True
        elif check == 11:  # tail - 0
            if config != 0:
                return False
            else:
                return True
        elif check == 10:  # tail - X
            if config != 'X' and config != 'x':
                return False
            else:
                return True
        else:
            return False


def isISBN13(isbn):
    """Check whether an isbn follows ISBN-13  eg. ISBN 978-7-122-00418-5"""
    if len(isbn) != 17:
        return False
    isbn_new = copy.copy(isbn)
    isbn_check = isbn_new.replace('-', '')
    isbn_check = re.sub(r'[^0123456789]', '', isbn_check)
    if len(isbn_check) != 13:
        return False
    else:
        config = int(isbn_check[-1])
        check = 0
        for i in range(0, 12, 1):
            if i % 2 == 0:
                check += int(isbn_check[i]) * 1
            else:
                check += int(isbn_check[i]) * 3
        check = check % 10
        check = int(10 - int(check))
        if 0 <= check <= 9:  # tail - N
            if config != check:
                return False
            else:
                return True
        elif check == 10:
            if config != 0:
                return False
            else:
                return True
        else:
            return False
# --------------------------------------------------------


class ISBNGen(object):
    def __init__(self,
                 filename_chinese_library_bookclassify,
                 filename_chinese_publisher_identifier
                 ):
        self.bookClassifiTable = load_csv_2d(filename_chinese_library_bookclassify)
        # 索书号对应的编码列表，后期可以利用本列表编写用户可识别的编码信息
        self.publisherTable = load_csv_2d(filename_chinese_publisher_identifier)
        # 出版社对应的isbn编号，后期可利用本列表找出图书借阅记录中的正确isbn

    def derive_isbn(self, recordline):
        text = copy.copy(recordline[tag_isbn])
        if text is not None:
            isbn_list = copy.copy(text)
            isbn_list = isbn_list.split('-')
            for i in range(len(isbn_list)):
                isbn_list[i] = re.sub(r'[^0123456789Xx]', '', isbn_list[i])
            while '' in isbn_list:
                isbn_list.remove('')
            backup_isbn = '-'.join(isbn_list)
            if len(isbn_list) == 4:
                if isISBN10('-'.join(isbn_list)):
                    return '-'.join(isbn_list)
                else:
                    if len(isbn_list[3]) != 1:
                        isbn_list[3] = isbn_list[3][0]
                        if isISBN10('-'.join(isbn_list)):
                            return '-'.join(isbn_list)
                        elif self.__isISBN10like__('-'.join(isbn_list)):
                            return '-'.join(isbn_list)
                        else:
                            return backup_isbn
                    else:
                        if self.__isISBN10like__('-'.join(isbn_list)):
                            return '-'.join(isbn_list)
                        else:
                            return backup_isbn
            elif len(isbn_list) == 5:
                if isISBN13('-'.join(isbn_list)):
                    return '-'.join(isbn_list)
                else:
                    if len(isbn_list[4]) != 1:
                        isbn_list[4] = isbn_list[4][0]
                        if isISBN13('-'.join(isbn_list)):
                            return '-'.join(isbn_list)
                        elif self.__isISBN13like__('-'.join(isbn_list)):
                            return '-'.join(isbn_list)
                        else:
                            return backup_isbn
                    else:
                        if self.__isISBN13like__('-'.join(isbn_list)):
                            return '-'.join(isbn_list)
                        else:
                            return backup_isbn
            elif len(isbn_list) == 1:
                if len(isbn_list[0]) >= 10:
                    if self.__isnakeISBN10__(isbn_list[0][0:10]):
                        return isbn_list[0][0:10]
                    elif len(isbn_list[0]) >= 13:
                        if self.__isnakeISBN13__(isbn_list[0][0:13]):
                            return isbn_list[0][0:13]
                    else:
                        return backup_isbn
                else:
                    return None
            else:
                return backup_isbn
        else:
            return None

    def __isISBN10like__(self, isbn):
        """check whether isbn looks like ISBN-10, eg. 7-301-04815-7 """
        isbn_list = isbn.split('-')
        for i in range(len(isbn_list)):
            isbn_list[i] = re.sub(r'[^0123456789Xx]', '', isbn_list[i])
        if len(''.join(isbn_list)) != 10:
            return False
        else:
            part_one = (''.join(isbn_list))[0:9]
            part_one = re.sub(r'[^0123456789]', '', part_one)
            if len(part_one) != 9:
                return False
            else:
                if self.__isnakeISBN10__(''.join(isbn_list)):
                    return True
                else:
                    if len(isbn_list) == 4:
                        if len(isbn_list[3]) == 1:
                            return True
                        else:
                            return False
                    elif len(isbn_list) == 3:
                        if len(isbn_list[2]) == 1:
                            return True
                        else:
                            return False
                    else:
                        return False

    def __isISBN13like__(self, isbn):
        """check whether isbn looks like ISBN-13, eg. 978-7-122-00418-5 """
        isbn_list = isbn.split('-')
        for i in range(len(isbn_list)):
            isbn_list[i] = re.sub(r'[^0123456789]', '', isbn_list[i])
        numline = ''.join(isbn_list)
        if len(numline) != 13:
            return False
        else:
            if self.__isnakeISBN13__(numline):
                return True
            else:
                if re.match('978', numline) or re.match('979', numline):
                    return True
                else:
                    if len(isbn_list) == 5:
                        if len(isbn_list[4]) == 1:
                            return True
                        else:
                            return False
                    elif len(isbn_list) == 4:
                        if len(isbn_list[3]) == 1:
                            return True
                        else:
                            return False
                    else:
                        return False

    def __isnakeISBN10__(self, isbn):
        """Check whether an isbn follows ISBN-10  eg. ISBN 7-302-12260-1"""
        if len(isbn) != 10:
            return False
        isbn_check = copy.copy(isbn)
        num_part = isbn_check[0:9]
        check_part = isbn_check[9:10]
        num_part = re.sub(r'[^0123456789]', '', num_part)
        check_part = re.sub(r'[^0123456789Xx]', '', check_part)
        isbn_check = num_part + check_part
        if len(isbn_check) != 10:
            return False
        else:
            config = isbn_check[-1]
            if config >= '0' and config <= '9':
                config = int(config)
            check = 0
            for i in range(0, 9, 1):
                check += int(isbn_check[i]) * (10 - i)
            check = check % 11
            check = int(11 - int(check))
            if 1 <= check <= 9:  # tail - N
                if config != check:
                    return False
                else:
                    return True
            elif check == 11:  # tail - 0
                if config != 0:
                    return False
                else:
                    return True
            elif check == 10:  # tail - X
                if config != 'X' and config != 'x':
                    return False
                else:
                    return True
            else:
                return False

    def __isnakeISBN13__(self, isbn):
        """Check whether an isbn follows ISBN-13  eg. ISBN 978-7-122-00418-5"""
        if len(isbn) != 13:
            return False
        isbn_check = copy.copy(isbn)
        isbn_check = re.sub(r'[^0123456789]', '', isbn_check)
        if len(isbn_check) != 13:
            return False
        else:
            config = int(isbn_check[-1])
            check = 0
            for i in range(0, 12, 1):
                if i % 2 == 0:
                    check += int(isbn_check[i]) * 1
                else:
                    check += int(isbn_check[i]) * 3
            check = check % 10
            check = int(10 - int(check))
            if 0 <= check <= 9:  # tail - N
                if config != check:
                    return False
                else:
                    return True
            elif check == 10:
                if config != 0:
                    return False
                else:
                    return True
            else:
                return False


if __name__ == '__main__':
    pass
