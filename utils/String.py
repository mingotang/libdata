# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging

from utils.Errors import ParamNoContentError


class LogInfo(object):
    @staticmethod
    def running(running: str, status: str):
        return '[running]: {0:s} - now {1:s}'.format(
            running, status,
        )

    @staticmethod
    def variable_detail(variable):
        return '[variable]: {0:s} got type {1:s} and content {2:s}'.format(
            str(id(variable)), str(type(variable)), str(variable)
        )


class UnicodeStr(object):

    @staticmethod
    def is_chinese(uchar):
        if u'\u4e00' <= uchar <= u'\u9fa5':
            return True
        else:
            return False

    # @staticmethod
    # def is_digit(uchar):
    #     """判断一个unicode是否是数字"""
    #     if u'\u0030' <= uchar <= u'\u0039':
    #         return True
    #     else:
    #         return False
    #
    # @staticmethod
    # def is_alphabet(uchar):
    #     """判断一个unicode是否是英文字母"""
    #     if (u'\u0041' <= uchar <= u'\u005a') or (u'\u0061' <= uchar <= u'\u007a'):
    #         return True
    #     else:
    #         return False

    @staticmethod
    def half_to_full(uchar: str):
        """半角转全角"""
        assert len(uchar) >= 1, repr(ParamNoContentError('uchar'))

        char_list = list()
        for char in uchar:
            inside_code = ord(char)
            if inside_code < 0x0020 or inside_code > 0x7e:  # 不是半角字符就返回原来的字符
                char_list.append(char)
            else:
                if inside_code == 0x0020:  # 除了空格其他的全角半角的公式为:半角=全角-0xfee0
                    inside_code = 0x3000
                else:
                    inside_code += 0xfee0
                char_list.append(chr(inside_code))
        return ''.join(char_list)

    @staticmethod
    def full_to_half(uchar: str):
        """全角转半角"""
        assert len(uchar) >= 1, repr(ParamNoContentError('uchar'))

        char_list = list()
        for char in uchar:
            inside_code = ord(char)
            if inside_code == 0x3000:
                inside_code = 0x0020
            else:
                inside_code -= 0xfee0
            if inside_code < 0x0020 or inside_code > 0x7e:  # 转完之后不是半角字符返回原来的字符
                char_list.append(char)
            else:
                char_list.append(chr(inside_code))
        return ''.join(char_list)


class ISBN(object):
    """国际标准书号（International Standard Book Number）"""

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


# --------------------------------------------------------


# --------------------------------------------------------
class LibIndex(object):

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
    logging.basicConfig(
        level=logging.DEBUG,  # 定义输出到文件的log级别，
        format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',  # 定义输出log的格式
        datefmt='%Y-%m-%d %A %H:%M:%S',  # 时间
        # filename=param.log_file_name,  # log文件名
        # filemode='w',
    )
