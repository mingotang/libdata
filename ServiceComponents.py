# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import pickle
import csv
import os
import re
import sys

import pymysql
from tqdm import tqdm

from Config import BasicInfo
from DataStructure import DataObject


# --------------------------------------------------------
class SupervisionInfo(object):

    @staticmethod
    def print_runningtime(running_time: float, end_line='', following=False, refresh=False):
        if refresh:
            print('\r', end='')
        hour = int(running_time) // 3600
        minutes = int(running_time) // 60 - 60 * hour
        seconds = running_time % 60
        if hour > 0:
            print('Running time: {0:d} h {1:d} m {2:.2f} s'.format(hour, minutes, seconds), end=end_line)
        elif minutes > 0:
            print('Running time: {0:d} m {1:.2f} s'.format(minutes, seconds), end=end_line)
        else:
            print('Running time: {0:.2f} s'.format(seconds), end=end_line)
        if following is False:
            sys.stdout.flush()

    @staticmethod
    def print_stepinfo(current_step: int, total_step: int, prefix_info='', end_line='',
                       following=False, refresh=False):
        if refresh:
            print('\r', end='')
        print(prefix_info, ' {0:d}/{1:d}'.format(current_step, total_step), end=end_line)
        if following is False:
            sys.stdout.flush()

    @staticmethod
    def print_statusinfo(info='', end_line='', following=False, refresh=True):
        if refresh:
            print('\r', end='')
        print(info, end=end_line)
        if following is False:
            sys.stdout.flush()


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
        spam_reader = csv.reader(csv_file,
                                 delimiter=',',
                                 quotechar='"'
                                 )
        for __line__ in spam_reader:
            __content__.append(__line__)
        return __content__

    @staticmethod
    def save_csv(file_path: str, content, encode='utf-8'):
        """
        save a list which is of two dimension to the file
        with lines in list and columns in sub_lists
        """
        if file_path[-4:] != '.csv':
            file_name = file_path + '.csv'
        else:
            file_name = file_path
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
            raise ValueError()
        csv_file = open(file_name, 'w', newline='', encoding=encode)
        spam_writer = csv.writer(csv_file,
                                 delimiter=',',
                                 quotechar='"',
                                 quoting=csv.QUOTE_MINIMAL
                                 )
        spam_writer.writerows(content_to_file)
        csv_file.close()

    @staticmethod
    def save_temp_bit(file_path: str, temp):
        pickle.dump(temp, open(file_path, 'wb'))

    @staticmethod
    def load_temp_bit(file_path: str):
        return pickle.load(open(file_path, 'rb'))


# --------------------------------------------------------
class RawDataProcessor(object):

    @staticmethod
    def derive_raw_data(folder_path: str, file_list: list,
                        file_type='txt', splitter='@',
                        text_encoding='gb18030',
                        ):
        if len(file_list) == 0:
            file_list = BasicInfo.raw_text_file_list
        data_list = list()
        data_match_dict = BasicInfo.inner_tag_to_text_index_dict
        for file_name in tqdm(file_list, desc='Reading file:'):
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
                            data_object[tag] = line_content[data_match_dict[tag]]
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
        if len(content) != len(BasicInfo.inner_tag_to_text_index_dict):
            return False
        if not re.search(r'[12][890123]\d\d[01]\d[0123]\d', content[8]):
            return False
        if content[9] not in BasicInfo.event_index_to_real_tag_dict:
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
            if cont[9] in BasicInfo.event_index_to_real_tag_dict:
                return cont
            elif cont[10] in BasicInfo.event_index_to_real_tag_dict:
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
class LibDB_MySQL(object):
    def __init__(self, host_ip: str, database: str):
        self.host = host_ip
        self.database = database
        self.connection_status = None  # status list: None, Closed, Connected, Blocked
        self.__connection__ = None

    def __repr__(self):
        return None

    def connect(self, charset='utf8', cursor_class=pymysql.cursors.DictCursor):
        sql_user_name, sql_password = self.__check_login_info__()
        self.__connection__ = pymysql.connect(
            host=self.host,
            user=sql_user_name,
            password=sql_password,
            db=self.database,
            charset=charset,
            cursorclass=cursor_class)

    def __check_login_info__(self):
        user_name = input('Please input the user name of database {0:s}'.format(self.database))
        user_password = input('Please input the password of username {0:s}'.format(user_name))
        return user_name, user_password

    def disconnect(self):
        self.__connection__.close()

    def execute_sql(self, sql: str):
        try:
            with self.__connection__.cursor() as cursor:
                cursor.execute(sql)
                self.__connection__.commit()
                result = cursor.fetchone()
                line = []
                for item in result:
                    line.append(result[item])
                return line
        except:
            print('LibDB.execute_sql Warning! \t Wrong SQL !')
            return None


# --------------------------------------------------------


# --------------------------------------------------------
# class TableClassic(object):
# # -*- encoding: UTF-8 -*-
# # Realize SQL connection by pymysql based on MySQL
# # --------------------------
# import pymysql
# # --------------------------
# # Example:
# # CREATE TABLE `users` (
# #     `id` int(11) NOT NULL AUTO_INCREMENT,
# #     `email` varchar(255) COLLATE utf8_bin NOT NULL,
# #     `password` varchar(255) COLLATE utf8_bin NOT NULL,
# #     PRIMARY KEY (`id`)
# # ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
# # AUTO_INCREMENT=1 ;
# # CREATE TABLE modules.rawdata (
# #  	sysID varchar(100),
# #  	indexID varchar(100),
# #  	bookname varchar(100),
# #  	isbn varchar(100),
# #  	author varchar(100),
# #  	publish_year varchar(100),
# #  	publisher varchar(100),
# #  	userID varchar(100),
# #  	event_date varchar(100),
# #  	event_type varchar(100),
# #  	user_type varchar(100),
# # 	collegeID varchar(100),
# # 	tableID INT NOT NULL PRIMARY KEY AUTO_INCREMENT
# # )
# # ENGINE=InnoDB
# # DEFAULT CHARSET=utf8
# # COLLATE=utf8_general_ci ;
#
#
#
#
# class SQL(object):
#     def __init__(self, host_ip,
#                  sql_user_name,
#                  sql_password,
#                  database,
#                  charset='utf8',
#                  cursorclass=pymysql.cursors.DictCursor
#                  ):
#         self.connection = pymysql.connect(host=host_ip,
#                                           user=sql_user_name,
#                                           password=sql_password,
#                                           db=database,
#                                           charset=charset,
#                                           cursorclass=cursorclass,
#                                           )
#         self.pyname2sqlname = {}
#         self.sqlname2pyname = {}
#
#     def add_into_table(self, tablename, headlist, contentdict):
#         try:
#             with self.connection.cursor() as cursor:
#                 sqllist = []
#                 sqllist.append("INSERT INTO `")
#                 sqllist.append(str(tablename))
#                 sqllist.append("` (")
#                 for head in headlist:
#                     sqllist.append("`")
#                     sqllist.append(self.pyname2sqlname[head])
#                     sqllist.append("`")
#                     sqllist.append(", ")
#                 sqllist.pop()
#                 sqllist.append(") VALUES (")
#                 for head in headlist:
#                     sqllist.append(contentdict[head])
#                     sqllist.append(", ")
#                 sqllist.pop()
#                 sqllist.append(")")
#                 sql = ''.join(sqllist)
#                 cursor.execute(sql)
#                 self.connection.commit()
#                 return 1
#         except:
#             print('\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tadd_into_rawdata Warning: - - - - - - ', contentdict)
#             return 0
#
#     def remove_from_rawdata(self, lineInList):
#         line = lineInList
#         try:
#             with self.connection.cursor() as cursor:
#                 # sql = "DELETE FROM `rawdata` WHERE name='百度' AND country='CN';"
#                 sql = "DELETE FROM `rawdata` " \
#                       "WHERE `sysID`=%s " \
#                       "AND `indexID`=%s " \
#                       "AND `bookname`=%s " \
#                       "AND `isbn`=%s " \
#                       "AND `author`=%s " \
#                       "AND `publish_year`=%s " \
#                       "AND `publisher`=%s " \
#                       "AND `userID`=%s " \
#                       "AND `event_date`=%s " \
#                       "AND `event_type`=%s " \
#                       "AND `user_type`=%s " \
#                       "AND `collegeID`=%s;"
#                 cursor.execute(sql, (line[0], line[1], line[2], line[3], line[4], line[5],
#                                      line[6], line[7], line[8], line[9], line[10], line[11]))
#                 self.connection.commit()
#                 return 1
#         except:
#             print('remove_from_rawdata Warning: ', line)
#             return 0
#
#     def select_from_table(self, table, tablenamelist, indexlist, IDlist):
#         tablenamelist = ['sysID', 'indexID', tag_book_name, tag_isbn, tag_author, 'publish_year',
#                          tag_publisher, 'userID', 'event_date', 'event_type', 'user_type', 'collegeID', 'tableID']
#         sqllist = ['SELECT']
#         for item in indexlist:
#             sqllist.append(' `')
#             sqllist.append(namelist[item])
#             sqllist.append('`')
#             sqllist.append(',')
#         sqllist.pop()
#         sqllist.append(' FROM `rawdata`;')
#         sql = ''.join(sqllist)
#         # print(sql)
#         try:
#             line = []
#             with self.connection.cursor() as cursor:
#                 cursor.execute(sql)
#                 self.connection.commit()
#                 result = cursor.fetchone()
#                 for item in indexlist:
#                     line.append(result[namelist[item]])
#             return line
#         except:
#             print('select_from_rawdata Warning!')
#             return None
#
#
# if __name__ == '__main__':
#     import time
#     start_time = time.time()
#     # ------------------------------------
#     # connect_info = load_data('bookdata/remote_libdata.pickle')
#     # connect_info = load_data('bookdata/local_libdata.pickle')
#     # print(connect_info)
#     # libdatabase = SQL(connect_info[0], connect_info[1], connect_info[2], connect_info[3])
#     # data = load_csv_2d('bookdata/guanyuan2015.csv')
#
#     # for item in data:
#     #     if item[9] == '50':
#     #         libdatabase.add_into_table('borrowdata', item)
#     # del data
#     # del libdatabase
#     # line = data[0]
#     # libdatabase.add_into_rawdata(line)
#     # libdatabase.remove_from_rawdata(line)
#     # test = libdatabase.select_from_rawdata([0, 1])
#     # print(test)
#     # print(type(test))
#     # ------------------------------------
#     # connect_info = load_data('bookdata/remote_libdata.pickle')
#     # print(connect_info)
#     # connect_info[0] = '192.168.3.116'
#     # connect_info[1] = 'mingotang'
#     # connect_info[2] = 'sql771422'
#     # connect_info[3] = 'modules'
#     # print(connect_info)
#     # save_data('bookdata/local_libdata.pickle', connect_info)
#     # ------------------------------------
#     end_time = time.time()
#     duration = end_time - start_time
#     hour = int(duration) // 3600
#     minutes = int(duration) // 60 - 60 * hour
#     seconds = duration % 60
#     print('\nRunning time: %d h %d m %f s' % (hour, minutes, seconds))
#
#



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
