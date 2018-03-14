# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
from utils import ParamNoContentError


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
