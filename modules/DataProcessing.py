# -*- coding: utf-8 -*-
# In this document text file is prepared for the project
# --------------------------
import os
import jieba
import csv
import re
import copy
from modules.BasicDataSetting import *
from modules.ISBN import ISBNGen


class RawDataProcessor(object):
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        self.match_dict = {
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
        source_file_dict = dict()
        for file_name in raw_file_list:
            source_file_dict[file_name] = open(os.path.join(self.folder_path, file_name),
                                               'r', encoding=text_encoding)

    class RawDataReader(object):
        def __init__(self, filenamelist):
            self.sourcefiledict = {}
            for file in filenamelist:
                self.sourcefiledict[file] = open(file, 'r', encoding="gb18030")
            self.headlist = get_headlist()

        def readnextline(self):
            try:
                __content__ = next(self.__readrecordlineiteration__())
                return __content__
            except StopIteration:
                return None

        def __readrecordlineiteration__(self):
            for file in self.sourcefiledict:
                textline = self.sourcefiledict[file].readline()
                while textline:
                    line_content = textline.split('@')
                    line_content.pop()
                    line_content = self.__data_processing__(line_content)
                    if line_content is not None:
                        if len(line_content) != 12:
                            print("On read: unqualified data : ", textline, '  Splitted as: ', line_content)
                            yield None
                        else:
                            line_content = dict(zip(self.headlist, line_content))
                            for item in line_content:
                                if line_content[item] == '':
                                    line_content[item] = None
                            # print(list(line_content))
                            yield line_content
                    else:
                        yield None
                    textline = self.sourcefiledict[file].readline()

        def __data_processing__(self, __content__):
            """modify the line readed in raw data and fix it into the sequence we want"""
            if len(__content__) < 12:
                return None
            else:
                if __content__[9] in self.eventlist:
                    return __content__
                elif __content__[10] in self.eventlist:
                    if len(__content__[4]) == 17:
                        __content__[2] = __content__[2] + __content__[3]
                        del __content__[3]
                        return __content__
                        # print(content)
                    elif len(__content__[3]) == 17:
                        __content__[4] = __content__[4] + __content__[5]
                        del __content__[5]
                        return __content__
                        # print(content)
                    else:
                        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~', __content__)
                        return None
                else:
                    print("data_cleaning. unqualified data : ", __content__)
                    return None

    def load_csv_2d(self, filename: str, encode='utf-8'):
        """
        load a list which is of two dimension
        with lines in list and columns in sub_lists
        """
        csv_file = open(os.path.join(self.folder_path, filename), 'r', newline='', encoding=encode)
        __content__ = list()
        spam_reader = csv.reader(csv_file,
                                 delimiter=',',
                                 quotechar='"'
                                 )
        for __line__ in spam_reader:
            __content__.append(__line__)
        print('load_csv_2d. File {0:s} is loaded !'.format(filename))
        return list

    def save_csv_2d(self, filename: str, content: list, encode='utf-8'):
        """
        save a list which is of two dimension to the file
        with lines in list and columns in sub_lists
        """
        if filename[-4:] != '.csv':
            file_name = filename + '.csv'
        else:
            file_name = filename
        csv_file = open(os.path.join(self.folder_path, file_name), 'w', newline='', encoding=encode)
        spam_writer = csv.writer(csv_file,
                                 delimiter=',',
                                 quotechar='"',
                                 quoting=csv.QUOTE_MINIMAL
                                 )
        spam_writer.writerows(content)
        csv_file.close()
        print('save_csv_2d. File {0:s} is saved ! '.format(file_name))




def get_headlist():
    line = list()
    line.append(tag_system_id)  # 0
    line.append(tag_biblio)  # 1
    line.append(tag_book_name)  # 2
    line.append(tag_isbn)  # 3
    line.append(tag_author)  # 4
    line.append(tag_publish_year)  # 5
    line.append(tag_publisher)  # 6
    line.append(tag_reader_id)  # 7
    line.append(tag_event_date)  # 8
    line.append(tag_event_type)  # 9
    line.append(tag_reader_type)  # 10
    line.append(tag_reader_college)  # 11
    return line


# --------------------------------------------------------
# read and write csv file
def load_csv_2d(filename, encode='utf-8'):
    """
    load a list which is of two dimension
    with lines in list and columns in sub_lists
    """
    csv_file = open(filename, 'r', newline='', encoding=encode)
    __content__ = list()
    spam_reader = csv.reader(csv_file,
                            delimiter=',',
                            quotechar='"'
                    )
    for __line__ in spam_reader:
        __content__.append(__line__)
    print('load_csv_2d. File %s is loaded !' % filename)
    return list


def save_csv_2d(filename, content, encode='utf-8'):
    """
    save a list which is of two dimension to the file
    with lines in list and columns in sub_lists
    """
    csv_file = open(filename, 'w', newline='', encoding=encode)
    spam_writer = csv.writer(csv_file,
                            delimiter=',',
                            quotechar='"',
                            quoting=csv.QUOTE_MINIMAL
                    )
    spam_writer.writerows(content)
    csv_file.close()
    print('save_csv_2d. File %s is saved ! ' % (filename))
# --------------------------------------------------------


# --------------------------------------------------------

# --------------------------------------------------------


# --------------------------------------------------------
# clean the raw data
class CleanRecord(object):
    def __init__(self, library_classi, publish_isbn):
        self.isbn_gen = ISBNGen(library_classi, publish_isbn)

    def clean_record(self, record_line,
                     head_specified=(tag_biblio,
                                     tag_book_name,
                                     tag_isbn,
                                     tag_event_date,
                                     tag_reader_college)
                     ):
        if tag_biblio in head_specified:
            self.derive_biblio(record_line)
        if tag_book_name in head_specified:
            self.derive_bookname(record_line)
        if tag_isbn in head_specified:
            self.derive_isbn(record_line)
        if tag_event_date in head_specified:
            self.derive_date(record_line)
        if tag_reader_college in head_specified:
            self.derive_college(record_line)
        return record_line

    def derive_biblio(self, recordline):
        """return biblio information in a list"""
        text = copy.copy(recordline[tag_biblio])
        if text is None:
            return None
        else:
            bilist = text.split('/')
            typelist = bilist[0].split('.')
            classifier = typelist[0]
            classifier = re.sub('\W', '', classifier)
            normclassi = re.match('[a-zA-Z]*\d', classifier)
            if normclassi:
                if re.sub('\d', '', normclassi.group()) != '':
                    recordline[tag_biblio_simplified_to_category_plus_one_digit] = normclassi.group()
                    return True
                else:
                    return None
            else:
                normclassi = re.match('[a-zA-Z]*', classifier)
                if normclassi:
                    if normclassi.group() != '':
                        return normclassi.group()
                    else:
                        return None
                else:
                    return None

    def derive_college(self, recordline):
        if len(recordline[tag_reader_college]) > 2:
            return True
        else:
            recordline[tag_reader_college] = None
            return None

    def derive_date(self, record):
        """return event data in a dict { year(str), month(str), date(str)}"""
        text = copy.copy(record[tag_event_date])
        if text is not None:
            text = re.sub(r'\D', '', text)
            if len(text) == 8:
                record[tag_event_date_year] = text[0:4]
                record[tag_event_date_month] = text[4:6]
                record[tag_event_date_date] = text[6:8]
                return True
            else:
                print('Warning derive_date:', record[tag_system_id], record[tag_event_date])
                record[tag_event_date_year] = None
                record[tag_event_date_month] = None
                record[tag_event_date_date] = None
                return None
        else:
            return None

    def derive_bookname(self, recordline):
        "return the book name in a list [ bookname(str), splitted_name(list)]"
        bookname = copy.copy(recordline[tag_book_name])
        if bookname is not None:
            bookname = bookname.strip()
            clean_list = ['及', '与', '及其', '的', '之']
            namesplit = '/'.join(jieba.cut(bookname)).split('/')
            for i in range(len(namesplit)):
                namesplit[i] = re.sub(r'\W', '', namesplit[i])
                namesplit[i] = re.sub(r'\d', '', namesplit[i])
                for item in clean_list:
                    namesplit[i] = namesplit[i].replace(item, '')
            while '' in namesplit:
                namesplit.remove('')
            recordline[tag_book_name_keywords_list] = namesplit
            return True
        else:
            return None

    def derive_isbn(self, record_line):
        record_line[tag_isbn_corrected] = self.isbn_gen.derive_isbn(record_line)

    def __is_eng_char__(self, uchar):
        if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
            return True
        else:
            return False

    def __is_chi_char__(self, uchar):
        """判断一个unicode是否是汉字 utf-16:\u4e00-\u9fa5"""
        if u'\u4e00' <= uchar and uchar <= u'\u9fa5':
            return True
        else:
            return False
# --------------------------------------------------------


# --------------------------------------------------------
def derive_tag_A_to_tag_B_dict(tag_A, tag_B, raw_file_list, output=False, filename='default_filename',
                               watch_result=False):
    """return a dict: tag_A -> list(tag_B's)"""
    raw_data = RawDataReader(raw_file_list)
    __content__ = raw_data.readnextline()
    a2b_dict = dict()
    while __content__:
        if __content__[tag_A] in a2b_dict:
            a2b_dict[__content__[tag_A]].append(__content__[tag_B])
        else:
            a2b_dict[__content__[tag_A]] = list()
            a2b_dict[__content__[tag_A]].append(__content__[tag_B])
        __content__ = raw_data.readnextline()
    for __item__ in a2b_dict:
        a2b_dict[__item__] = list(set(a2b_dict[__item__]))
    if watch_result is True:
        for __item__ in a2b_dict:
            print('{', __item__, ':', a2b_dict[__item__], '}')
    if output is True:
        save_data(filename, a2b_dict)


def derive_tag_A_to_object_B_dict(tag_A, object_B_tag_list, raw_file_list,watch_result=False,
                                   output=False, filename='default'):
    """return a dict: tag_A -> dict{tag_B: tag_B_content}"""
    __raw_data__ = RawDataReader(raw_file_list)
    __content__ = __raw_data__.readnextline()
    a2b_dict = dict()
    while __content__:
        if __content__[tag_A] in a2b_dict:
            pass
        else:
            a2b_dict[__content__[tag_A]] = dict()
            for __item__ in object_B_tag_list:
                a2b_dict[__content__[tag_A]][__item__] = __content__[__item__]
        __content__ = __raw_data__.readnextline()
    if watch_result is True:
        for __item__ in a2b_dict:
            print('{', __item__, ':', a2b_dict[__item__], '}')
    if output is True:
        save_data(filename, a2b_dict)

if __name__ == '__main__':
    import time
    start_time = time.time()
    # ------------------------------ cleaning records
    rawfilelist = [
                   '../rawData/2016-11-16-guanyuan2013.txt'
                   # '../rawData/2016-11-16-guanyuan2014.txt',
                   # '../rawData/2016-11-16-guanyuan2015.txt'
                   ]
    rawdata = RawDataReader(rawfilelist)
    cleaner = CleanRecord()
    count = 0
    content = rawdata.readnextline()
    while content:
        count += 1
        cleaner.clean_record(content)
        print(content)
        time.sleep(0.1)
        content = rawdata.readnextline()
    del rawdata

    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration) // 3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.4f} s'.format(hour, minutes, seconds))
