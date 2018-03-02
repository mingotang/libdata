# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import csv
import logging
import pickle
import re
import os

from BasicInfo import DataInfo
from DataStructure import DataObject, LogInfo, ParamTypeError


# --------------------------------------------------------


# --------------------------------------------------------
class FileIO(object):

    @staticmethod
    def load_csv(file_path: str, encode='utf-8'):
        """
        load a list which is of two dimension
        with lines in list and columns in sub_lists
        """
        if file_path[-4:] != '.csv':
            file_name = file_path + '.csv'
        else:
            file_name = file_path
        csv_file = open(file_name, 'r', newline='', encoding=encode)
        __content__ = list()
        spam_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        for __line__ in spam_reader:
            __content__.append(__line__)
        return __content__

    @staticmethod
    def save_csv(file_path: str, content, encode='utf-8'):
        """
        save a list which is of two dimension to the file
        with lines in list and columns in sub_lists
        """
        logging.debug(LogInfo.running('save_csv', 'checking file type'))
        if file_path[-4:] != '.csv':
            file_name = file_path + '.csv'
        else:
            file_name = file_path

        logging.debug(LogInfo.running('save_csv', 'making up lists in list'))
        if type(content) == list:
            content_to_file = content
        elif type(content) == dict:
            content_to_file = list()
            for tag in content:
                line_to_file = list()
                line_to_file.append(tag)
                if type(content[tag]) == list:
                    line_to_file.extend(content[tag])
                else:
                    raise ValueError()
        else:
            raise ParamTypeError('content', 'list/dict', content)

        logging.debug(LogInfo.running('save_csv', 'writing csv file'))
        csv_file = open(file_name, 'w', newline='', encoding=encode)
        spam_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        spam_writer.writerows(content_to_file)
        csv_file.close()

    @staticmethod
    def save_bit(file_path: str, temp):
        pickle.dump(temp, open(file_path, 'wb'))

    @staticmethod
    def load_bit(file_path: str):
        return pickle.load(open(file_path, 'rb'))


# --------------------------------------------------------
class RawDataProcessor(object):

    @staticmethod
    def derive_raw_data(folder_path: str, file_range=DataInfo.raw_text_file_list,
                        splitter='@', text_encoding='gb18030',
                        ):
        logging.debug(LogInfo.running('derive_raw_data', 'checking file'))

        data_list = list()
        for file_name in file_range:
            logging.debug(LogInfo.running('derive_raw_data', 'reading file {0}'.format(str(file_name))))
            data_file = open(os.path.join(folder_path, file_name), 'r', encoding=text_encoding)

            text_line = data_file.readline()
            __temp_list__ = list()
            while text_line:
                line_content = text_line.split(splitter)
                line_content.pop()
                line_content = RawDataProcessor.__raw_data_line_clean__(line_content, __temp_list__)
                if RawDataProcessor.__check_data_line__(line_content):
                    data_object = DataObject(line_content)
                    data_list.append(data_object)
                elif len(line_content) == 0:
                    logging.debug('RawDataProcessor: empty line')
                else:
                    logging.warning("Unqualified data :  {0:s}".format(str(line_content)))
                text_line = data_file.readline()
        return data_list

    @staticmethod
    def __check_data_line__(content: list):
        if len(content) != len(DataInfo.inner_tag_to_text_index_dict):  # 数量长度必须和预设相同
            return False
        else:
            if not re.search(r'[12][890123]\d\d[01]\d[0123]\d', content[8]):  # event_date 必须遵循 YYYYmmdd格式
                return False
            else:
                if content[9] not in DataInfo.event_index_to_real_tag_dict:  # event_type 必须在预定范围内
                    return False
                else:
                    return True

    @staticmethod
    def __raw_data_line_clean__(content: list, __temp_list__: list):
        if len(content) < 12:
            if len(__temp_list__) > 0:
                __temp_list__.extend(content)
                temp_list = RawDataProcessor.__raw_data_line_clean__(__temp_list__, __temp_list__)
                if len(temp_list) > 0:
                    __temp_list__.clear()
                    return temp_list
                else:
                    __temp_list__.clear()
                    logging.warning('Unqualified data : {0:s}'.format(str(temp_list)))
                    return list()
            else:
                __temp_list__.extend(content)
                return list()
        else:
            cont = list()
            cont.extend(content)
            __temp_list__.clear()
            if cont[9] in DataInfo.event_index_to_real_tag_dict:
                return cont
            elif cont[10] in DataInfo.event_index_to_real_tag_dict:
                if len(cont[4]) == 17:
                    cont[2] = cont[2] + cont[3]
                    del cont[3]
                    return cont
                    # print(content)
                elif len(cont[3]) == 17:
                    cont[4] = cont[4] + cont[5]
                    del cont[5]
                    return cont
                    # print(content)
                else:
                    logging.warning('Unqualified data : {0:s}'.format(str(cont)))
                    return list()
            else:
                logging.warning('Unqualified data : {0:s}'.format(str(cont)))
                return list()


# --------------------------------------------------------
class UnicodeChar(object):

    @staticmethod
    def __is_chinese_char__(uchar):
        if u'\u4e00' <= uchar <= u'\u9fa5':
            return True
        else:
            return False

    @staticmethod
    def __is_digit__(uchar):
        """判断一个unicode是否是数字"""
        if u'\u0030' <= uchar <= u'\u0039':
            return True
        else:
            return False

    @staticmethod
    def __is_alphabetical_char__(uchar):
        """判断一个unicode是否是英文字母"""
        if (u'\u0041' <= uchar <= u'\u005a') or (u'\u0061' <= uchar <= u'\u007a'):
            return True
        else:
            return False

    @staticmethod
    def halfwidth_to_fullwidth(uchar):
        """半角转全角"""
        inside_code = ord(uchar)
        if inside_code < 0x0020 or inside_code > 0x7e:  # 不是半角字符就返回原来的字符
            return uchar
        if inside_code == 0x0020:  # 除了空格其他的全角半角的公式为:半角=全角-0xfee0
            inside_code = 0x3000
        else:
            inside_code += 0xfee0
        return chr(inside_code)

    @staticmethod
    def fullwidth_to_halfwidth(uchar):
        """全角转半角"""
        inside_code = ord(uchar)
        if inside_code == 0x3000:
            inside_code = 0x0020
        else:
            inside_code -= 0xfee0
        if inside_code < 0x0020 or inside_code > 0x7e:  # 转完之后不是半角字符返回原来的字符
            return uchar
        return chr(inside_code)


class UnicodeString(UnicodeChar):

    @staticmethod
    def full_2_half(ustring):
        """把字符串全角转半角"""
        return ''.join([UnicodeChar.fullwidth_to_halfwidth(uchar) for uchar in ustring])

    @staticmethod
    def uniform(ustring):
        """格式化字符串，完成全角转半角，大写转小写的工作"""
        return UnicodeString.full_2_half(ustring).lower()


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
