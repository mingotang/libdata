# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging
import re
import os

from Config import DataInfo, DataConfig
from utils.Constants import event_type_chinese_map
from utils.Logger import LogInfo


class DataObject(dict):
    list_index_to_inner_tag_dict = {
        0: 'sysID',
        1: 'libIndexID',
        2: 'bookname',
        3: 'isbn',
        4: 'author',
        5: 'publish_year',
        6: 'publisher',
        7: 'userID',
        8: 'event_date',
        9: 'event_type',
        10: 'user_type',
        11: 'collegeID',
    }

    def __init__(self, from_list: list):
        dict.__init__(self)
        for index, inner_tag in self.list_index_to_inner_tag_dict.items():
            self[inner_tag] = from_list[index]

        # data cleaning
        self['sysID'] = re.sub(r'\W', '', self['sysID'])
        self['userID'] = re.sub(r'\W', '', self['userID'].upper())


class RawDataProcessor(object):

    @staticmethod
    def derive_raw_data(file_range=DataInfo.raw_text_file_list,
                        splitter='@', text_encoding='gb18030',
                        ):
        logging.debug(LogInfo.running('derive_raw_data', 'checking file'))

        data_list = list()
        for file_name in file_range:
            logging.debug(LogInfo.running('derive_raw_data', 'reading file {0}'.format(str(file_name))))
            data_file = open(os.path.join(DataConfig.raw_data_folder, file_name), 'r', encoding=text_encoding)

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
    def iter_data_object(file_range=DataInfo.raw_text_file_list,
                         splitter='@', text_encoding='gb18030',):
        logging.debug(LogInfo.running('derive_raw_data', 'checking file'))

        # data_list = list()
        for file_name in file_range:
            logging.debug(LogInfo.running('derive_raw_data', 'reading file {0}'.format(str(file_name))))
            data_file = open(os.path.join(DataConfig.raw_data_folder, file_name), 'r', encoding=text_encoding)

            text_line = data_file.readline()
            __temp_list__ = list()
            while text_line:
                line_content = text_line.split(splitter)
                line_content.pop()
                line_content = RawDataProcessor.__raw_data_line_clean__(line_content, __temp_list__)
                if RawDataProcessor.__check_data_line__(line_content):
                    data_object = DataObject(line_content)
                    yield data_object
                    # data_list.append(data_object)
                elif len(line_content) == 0:
                    logging.debug('RawDataProcessor: empty line')
                else:
                    logging.warning("Unqualified data :  {0:s}".format(str(line_content)))
                text_line = data_file.readline()
        # return data_list

    @staticmethod
    def __check_data_line__(content: list):
        if len(content) != len(DataObject.list_index_to_inner_tag_dict):  # 数量长度必须和预设相同
            return False
        else:
            if not re.search(r'[12][890123]\d\d[01]\d[0123]\d', content[8]):  # event_date 必须遵循 YYYYmmdd格式
                return False
            else:
                if content[9] not in event_type_chinese_map:  # event_type 必须在预定范围内
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
            if cont[9] in event_type_chinese_map:
                return cont
            elif cont[10] in event_type_chinese_map:
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
