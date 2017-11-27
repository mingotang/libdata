# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os
import re

from tqdm import tqdm

from modules.DataStructure import DataObject


# --------------------------------------------------------
class RawDataProcessor(object):
    default_raw_file_list = [
        '2016-11-16-guanyuan2013.txt',
        '2016-11-16-guanyuan2014.txt',
        '2016-11-16-guanyuan2015.txt',
    ]
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
    event_type_dict = {
        '50': '借书',
        '61': '还书',
        '62': '续借',
        '63': '续借2'
    }
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

    @staticmethod
    def derive_raw_data(folder_path: str,
                        file_list: list,
                        file_type='txt',
                        splitter='@',
                        text_encoding='gb18030',
                        ):
        if len(file_list) == 0:
            file_list = RawDataProcessor.default_raw_file_list
        data_list = list()
        data_match_dict = RawDataProcessor.match_index_dict
        for file_name in tqdm(file_list, desc='reading file'):
            if file_type == 'txt':
                data_file = open(os.path.join(folder_path, file_name), 'r', encoding=text_encoding)
                text_line = data_file.readline()
                __temp_list__ = list()
                while text_line:
                    line_content = text_line.split(splitter)
                    line_content.pop()
                    line_content = RawDataProcessor.__raw_data_line_clean__(line_content, __temp_list__)
                    if RawDataProcessor.__check_data_line__(line_content):
                        data_object = DataObject()
                        for tag in data_match_dict:
                            data_object.set(key=tag, element=line_content[data_match_dict[tag]])
                        data_list.append(data_object)
                    elif len(line_content) == 0:
                        pass
                    else:
                        print("{0:s}: Unqualified data :  ".format(RawDataProcessor.__class__.__name__), line_content)
                    text_line = data_file.readline()
            else:
                raise ValueError('RawDataProcessor.derive_raw_data file type {0:s} not legal'.format(file_type))
        return data_list

    @staticmethod
    def __check_data_line__(content: list):
        if len(content) != len(RawDataProcessor.match_index_dict):
            return False
        if not re.search(r'[12][890123]\d\d[01]\d[0123]\d', content[8]):
            return False
        if content[9] not in RawDataProcessor.event_type_dict:
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
            if cont[9] in RawDataProcessor.event_type_dict:
                return cont
            elif cont[10] in RawDataProcessor.event_type_dict:
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


if __name__ == '__main__':
    import time
    start_time = time.time()
    # ------------------------------ cleaning records
    data = RawDataProcessor.derive_raw_data(folder_path=os.path.join('..', '_data'),
                                            file_type='txt', file_list=[])
    for data_item in data:
        print(data_item)
        time.sleep(0.2)
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration) // 3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.4f} s'.format(hour, minutes, seconds))
