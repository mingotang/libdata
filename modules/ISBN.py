# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os
import re

from modules.ServiceComponents import FileIO


class ISBN(object):

    @staticmethod
    def check_isbn(isbn: str, isbn_type: int):
        """
        Check whether an isbn follows ISBN-10 rule  eg. ISBN 7302122601
        or whether an isbn follows ISBN-13 rule eg. ISBN 9787122004185
        :param isbn: isbn in string
        :param isbn_type: ISBN 10 or 13
        :return: Bool
        """
        if isbn_type == 10:
            isbn_check = isbn.replace('-', '')
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
                if config.isdigit():
                    config = int(config)
                check = 0
                for i in range(0, 9, 1):
                    check += int(isbn_check[i]) * (10 - i)
                check = 11 - check % 11
                if 1 <= check <= 9:  # tail - N
                    return config == check
                elif check == 11:  # tail - 0
                    return config == 0
                elif check == 10:  # tail - X
                    return config.isalpha() and config.lower() == 'x'
                else:
                    return False
        elif isbn_type == 13:
            isbn_check = isbn.replace('-', '')
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
                check = 10 - check % 10
                if 0 <= check <= 9:  # tail - N
                    return check == config
                elif check == 10:
                    return check == config
                else:
                    return False
        else:
            raise ValueError('ISBN.check_isbn: param {0:d} is not 10 or 13'.format(isbn_type))

    @staticmethod
    def is_isbn(isbn: str, isbn_type: int):
        """
        Check whether an isbn follows ISBN-10  eg. ISBN 7-302-12260-1,
        or whether an isbn follows ISBN-13  eg. ISBN 978-7-122-00418-5
        :param isbn:
        :param isbn_type:
        :return: Bool
        """
        if isbn_type == 10:   # TODO: finish isbn_like string checking
            pass
        elif isbn_type == 13:
            pass
        else:
            raise ValueError('ISBN.check_isbn: param {0:d} is not 10 or 13'.format(isbn_type))


# --------------------------------------------------------
class ISBNGen(object):
    def __init__(self, folder_path: str,
                 library_bookclassify='',
                 publisher_isbn='', ):
        # TODO: 索书号对应的编码列表，后期可以利用本列表编写用户可识别的编码信息
        self.bookClassifiTable = FileIO.load_csv(os.path.join(folder_path, library_bookclassify))
        # TODO: 出版社对应的isbn编号，后期可利用本列表找出图书借阅记录中的正确isbn
        self.publisherTable = FileIO.load_csv(os.path.join(folder_path, publisher_isbn))

    def derive_isbn(self, recordline):
        pass


if __name__ == '__main__':
    import time

    start_time = time.time()
    # ------------------------------
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration) // 3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.2f} s'.format(hour, minutes, seconds))
