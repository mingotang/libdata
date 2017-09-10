# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os
import re

from modules.DataStructure import DataObject


# --------------------------------------------------------
class RawDataProcessor(object):
    @staticmethod
    def get_data_match_dict():
        match_index_dict = {
            'sysID': 0,
            'libIndexID': 1,
            'bookname': 2,
            'isbn': 3,
            'author': 4,
            'publish_year': 5,
            'publisher': 6,
            'userID': 7,
            'event_date': 8,
            'event_type': 9,
            'user_type': 10,
            'collegeID': 11,
        }
        return match_index_dict

    @staticmethod
    def match_raw_data_index(inner_tag: str):
        index_dict = RawDataProcessor.get_data_match_dict()
        return index_dict[inner_tag]

    @staticmethod
    def get_column_name(inner_tag: str):
        head_dict = {
            'sysID': '系统号',
            'libIndexID': '索书号',
            'bookname': '书名',
            'isbn': 'isbn号',
            'author': '作者',
            'publish_year': '出版年',
            'publisher': '出版社',
            'userID': '学工号',
            'event_date': '借书（还书、续借）发生日期',
            'event_type': '事件类型（借书、还书、续借）',
            'user_type': '读者身份类别',
            'collegeID': '学院代码',
        }
        return head_dict[inner_tag]

    @staticmethod
    def get_event_type_dict():
        event_type_dict = {
            '50': '借书',
            '61': '还书',
            '62': '续借',
            '63': '续借2'
        }
        return event_type_dict

    @staticmethod
    def get_event_type(event_type_tag: str):
        return RawDataProcessor.get_event_type_dict()[event_type_tag]

    @staticmethod
    def get_reader_type(reader_type_tag: str):
        reader_type_dict = {
            '11': '教授、副教授及各系列高级职称',
            '12': '教师、各系列中级职称',
            '13': '教职工、各系列初级职称',
            '14': '访问学者',
            '15': '离、退休职工',
            '21': '博士生',
            '22': '硕博连读生',
            '23': '硕士生',
            '24': '八年制本硕博连读生博士阶段',
            '25': '八年制本硕博连读生硕士阶段',
            '26': '七年制本硕连读生硕士阶段',
            '27': '六年制本硕连读生硕士阶段',
            '31': '四年制本科生',
            '32': '五年制本科生',
            '33': '六年制本硕连读生本科阶段',
            '34': '七年制本硕连读生本科阶段',
            '35': '八年制本硕博连读生本科阶段',
            '41': '校友卡读者',
            '42': '高职',
            '43': '二级学院及其他',
            '44': '校外普通读者',
            '45': '校外特殊读者',
            '51': '馆际互借',
            '52': '团体读者',
            '61': '研究生VIP1',
            '62': '研究生VIP2',
            '63': '研究生VIP3',
        }
        return reader_type_dict[reader_type_tag]

    @staticmethod
    def derive_raw_data(folder_path: str,
                        text_encoding='gb18030',
                        raw_file_list=('2016-11-16-guanyuan2013.txt',
                                       '2016-11-16-guanyuan2014.txt',
                                       '2016-11-16-guanyuan2015.txt',
                                       )
                        ):
        data_list = list()
        __temp_list__ = list()
        data_match_dict = RawDataProcessor.get_data_match_dict()
        for file_name in raw_file_list:
            data_file = open(os.path.join(folder_path, file_name), 'r', encoding=text_encoding)
            text_line = data_file.readline()
            while text_line:
                line_content = text_line.split('@')
                line_content.pop()
                line_content = RawDataProcessor.__raw_data_line_clean__(line_content, __temp_list__)
                if RawDataProcessor.check_data_line(line_content):
                    data_object = DataObject()
                    for tag in data_match_dict:
                        data_object.set(key=tag, element=line_content[RawDataProcessor.match_raw_data_index(tag)])
                    data_list.append(data_object)
                elif len(line_content) == 0:
                    pass
                else:
                    print("{0:s}: Unqualified data :  ".format(RawDataProcessor.__class__.__name__), line_content)
                text_line = data_file.readline()
        return data_list

    @staticmethod
    def check_data_line(content: list):
        if len(content) != len(RawDataProcessor.get_data_match_dict()):
            return False
        if not re.search(r'[12][890123]\d\d[01]\d[0123]\d', content[8]):
            return False
        if content[9] not in RawDataProcessor.get_event_type_dict():
            return False
        return True

    @staticmethod
    def __raw_data_line_clean__(content: list, __temp_list__: list):
        warning_info = "{0:s}.__raw_data_line_clean__: Unqualified data :  ".format(RawDataProcessor.__class__.__name__)
        warning_info += str(content)
        if len(content) < 12:
            if len(__temp_list__) > 0:
                __temp_list__.extend(content)
                temp_list = RawDataProcessor.__raw_data_line_clean__(__temp_list__, __temp_list__)
                if len(temp_list) > 0:
                    __temp_list__.clear()
                    return temp_list
                else:
                    __temp_list__.clear()
                    print(warning_info)
                    return list()
            else:
                __temp_list__.extend(content)
                return list()
        else:
            cont = list()
            cont.extend(content)
            __temp_list__.clear()
            if cont[9] in RawDataProcessor.get_event_type_dict():
                return cont
            elif cont[10] in RawDataProcessor.get_event_type_dict():
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
                    print(warning_info)
                    return list()
            else:
                print(warning_info)
                return list()


# --------------------------------------------------------


# --------------------------------------------------------
class RecordOperator(object):
    def __init__(self):
        pass

#     def derive_biblio(self, recordline):
#         """return biblio information in a list"""
#         text = copy.copy(recordline[tag_biblio])
#         if text is None:
#             return None
#         else:
#             bilist = text.split('/')
#             typelist = bilist[0].split('.')
#             classifier = typelist[0]
#             classifier = re.sub('\W', '', classifier)
#             normclassi = re.match('[a-zA-Z]*\d', classifier)
#             if normclassi:
#                 if re.sub('\d', '', normclassi.group()) != '':
#                     recordline[tag_biblio_simplified_to_category_plus_one_digit] = normclassi.group()
#                     return True
#                 else:
#                     return None
#             else:
#                 normclassi = re.match('[a-zA-Z]*', classifier)
#                 if normclassi:
#                     if normclassi.group() != '':
#                         return normclassi.group()
#                     else:
#                         return None
#                 else:
#                     return None
#
#     def derive_college(self, recordline):
#         if len(recordline[tag_reader_college]) > 2:
#             return True
#         else:
#             recordline[tag_reader_college] = None
#             return None
#
#     def derive_date(self, record):
#         """return event data in a dict { year(str), month(str), date(str)}"""
#         text = copy.copy(record[tag_event_date])
#         if text is not None:
#             text = re.sub(r'\D', '', text)
#             if len(text) == 8:
#                 record[tag_event_date_year] = text[0:4]
#                 record[tag_event_date_month] = text[4:6]
#                 record[tag_event_date_date] = text[6:8]
#                 return True
#             else:
#                 print('Warning derive_date:', record[tag_system_id], record[tag_event_date])
#                 record[tag_event_date_year] = None
#                 record[tag_event_date_month] = None
#                 record[tag_event_date_date] = None
#                 return None
#         else:
#             return None
#
#     def derive_bookname(self, recordline):
#         "return the book name in a list [ bookname(str), splitted_name(list)]"
#         bookname = copy.copy(recordline[tag_book_name])
#         if bookname is not None:
#             bookname = bookname.strip()
#             clean_list = ['及', '与', '及其', '的', '之']
#             namesplit = '/'.join(jieba.cut(bookname)).split('/')
#             for i in range(len(namesplit)):
#                 namesplit[i] = re.sub(r'\W', '', namesplit[i])
#                 namesplit[i] = re.sub(r'\d', '', namesplit[i])
#                 for item in clean_list:
#                     namesplit[i] = namesplit[i].replace(item, '')
#             while '' in namesplit:
#                 namesplit.remove('')
#             recordline[tag_book_name_keywords_list] = namesplit
#             return True
#         else:
#             return None
#
#     def derive_isbn(self, record_line):
#         record_line[tag_isbn_corrected] = self.isbn_gen.derive_isbn(record_line)
#
#     def __is_eng_char__(self, uchar):
#         if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
#             return True
#         else:
#             return False
#
#     def __is_chi_char__(self, uchar):
#         """判断一个unicode是否是汉字 utf-16:\u4e00-\u9fa5"""
#         if u'\u4e00' <= uchar and uchar <= u'\u9fa5':
#             return True
#         else:
#             return False
# --------------------------------------------------------


# --------------------------------------------------------
# def derive_tag_A_to_tag_B_dict(tag_A, tag_B, raw_file_list, output=False, filename='default_filename',
#                                watch_result=False):
#     """return a dict: tag_A -> list(tag_B's)"""
#     raw_data = RawDataReader(raw_file_list)
#     __content__ = raw_data.readnextline()
#     a2b_dict = dict()
#     while __content__:
#         if __content__[tag_A] in a2b_dict:
#             a2b_dict[__content__[tag_A]].append(__content__[tag_B])
#         else:
#             a2b_dict[__content__[tag_A]] = list()
#             a2b_dict[__content__[tag_A]].append(__content__[tag_B])
#         __content__ = raw_data.readnextline()
#     for __item__ in a2b_dict:
#         a2b_dict[__item__] = list(set(a2b_dict[__item__]))
#     if watch_result is True:
#         for __item__ in a2b_dict:
#             print('{', __item__, ':', a2b_dict[__item__], '}')
#     if output is True:
#         save_data(filename, a2b_dict)
#
#
# def derive_tag_A_to_object_B_dict(tag_A, object_B_tag_list, raw_file_list,watch_result=False,
#                                    output=False, filename='default'):
#     """return a dict: tag_A -> dict{tag_B: tag_B_content}"""
#     __raw_data__ = RawDataReader(raw_file_list)
#     __content__ = __raw_data__.readnextline()
#     a2b_dict = dict()
#     while __content__:
#         if __content__[tag_A] in a2b_dict:
#             pass
#         else:
#             a2b_dict[__content__[tag_A]] = dict()
#             for __item__ in object_B_tag_list:
#                 a2b_dict[__content__[tag_A]][__item__] = __content__[__item__]
#         __content__ = __raw_data__.readnextline()
#     if watch_result is True:
#         for __item__ in a2b_dict:
#             print('{', __item__, ':', a2b_dict[__item__], '}')
#     if output is True:
#         save_data(filename, a2b_dict)

if __name__ == '__main__':
    import time
    start_time = time.time()
    # ------------------------------ cleaning records
    data = RawDataProcessor.derive_raw_data(folder_path=os.path.join('..', 'data'))
    print(data)
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration) // 3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.4f} s'.format(hour, minutes, seconds))
