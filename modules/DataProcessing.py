# -*- coding: utf-8 -*-
# In this document text file is prepared for the project
# --------------------------
import os

from modules.DataStructure import DataObject


# --------------------------------------------------------
class RawDataProcessor(object):
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        self.match_index_dict = {
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
        self.head_dict = {
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
        self.event_type_dict = {
            '50': '借书',
            '61': '还书',
            '62': '续借',
            '63': '续借2'
        }
        self.reader_type_dict = {
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

    def derive_raw_data(self, text_encoding='gb18030',
                        raw_file_list=('2016-11-16-guanyuan2013.txt',
                                       '2016-11-16-guanyuan2014.txt',
                                       '2016-11-16-guanyuan2015.txt',
                                       )
                        ):
        data_list = list()
        for file_name in raw_file_list:
            data_file = open(os.path.join(self.folder_path, file_name), 'r', encoding=text_encoding)
            text_line = data_file.readline()
            while text_line:
                line_content = text_line.split('@')
                line_content.pop()
                line_content = self.__raw_data_line_clean__(line_content)
                if len(line_content) == len(self.match_index_dict):
                    data_object = DataObject()
                    for tag in self.match_index_dict:
                        data_object.set(key=tag, element=line_content[self.match_index_dict[tag]])
                    data_list.append(data_object)
                text_line = data_file.readline()
        return data_list

    def __raw_data_line_clean__(self, content: list):
        warning_info = "{0:s}.__raw_data_line_clean__: Unqualified data :  ".format(self.__class__.__name__)
        warning_info += str(content)
        if len(content) < 12:
            print(warning_info)
            return list()
        else:
            if content[9] in self.event_type_dict:
                return content
            elif content[10] in self.event_type_dict:
                if len(content[4]) == 17:
                    content[2] = content[2] + content[3]
                    del content[3]
                    return content
                    # print(content)
                elif len(content[3]) == 17:
                    content[4] = content[4] + content[5]
                    del content[5]
                    return content
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

# class CleanRecord(object):
#     def __init__(self, library_classi, publish_isbn):
#         self.isbn_gen = ISBNGen(library_classi, publish_isbn)
#
#
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
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration) // 3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.4f} s'.format(hour, minutes, seconds))
