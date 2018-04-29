# -*- encoding: UTF-8 -*-
from functions.DataStructure import EventAction


# --------------------------------------------------------
class EventActionList(object):
    def __init__(self):
        """
        Data structure for actions readers did
        """
        self.stored_list = list()
        self.__index_for_iter__ = int()

    def __repr__(self):
        return '\n'.join([str(var) for var in self.stored_list]) + '\n'

    def __len__(self):
        return len(self.stored_list)

    def __getitem__(self, index: int):
        return self.stored_list[index]

    def __setitem__(self, index: int, value: EventAction):
        self.stored_list[index] = value

    def __contains__(self, element: EventAction):
        if element in self.stored_list:
            return True
        else:
            return False

    def __iter__(self):
        self.__index_for_iter__ = 0
        return self

    def __next__(self):
        if self.__index_for_iter__ >= len(self.stored_list):
            raise StopIteration
        return self.stored_list[self.__index_for_iter__]

    def add(self, element: EventAction, allow_duplicated_record=True):
        if allow_duplicated_record is False:
            for index in range(len(self.stored_list)):
                if element == self.stored_list[index]:
                    return
        for index in range(len(self.stored_list)):  # sorting when element added could be improved
            if element.not_later_than(self.stored_list[index]):
                self.stored_list.insert(index, element)
                return
        self.stored_list.append(element)


# --------------------------------------------------------
# class LibDB_MySQL(object):
#     def __init__(self, host_ip: str, database: str):
#         self.host = host_ip
#         self.database = database
#         self.connection_status = None  # status list: None, Closed, Connected, Blocked
#         self.__connection__ = None
#
#     def __repr__(self):
#         return None
#
#     def connect(self, charset='utf8', cursor_class=pymysql.cursors.DictCursor):
#         sql_user_name, sql_password = self.__check_login_info__()
#         self.__connection__ = pymysql.connect(
#             host=self.host,
#             user=sql_user_name,
#             password=sql_password,
#             db=self.database,
#             charset=charset,
#             cursorclass=cursor_class)
#
#     def __check_login_info__(self):
#         user_name = input('Please input the user name of database {0:s}'.format(self.database))
#         user_password = input('Please input the password of username {0:s}'.format(user_name))
#         return user_name, user_password
#
#     def disconnect(self):
#         self.__connection__.close()
#
#     def execute_sql(self, sql: str):
#         try:
#             with self.__connection__.cursor() as cursor:
#                 cursor.execute(sql)
#                 self.__connection__.commit()
#                 result = cursor.fetchone()
#                 line = []
#                 for item in result:
#                     line.append(result[item])
#                 return line
#         except:
#             print('LibDB.execute_sql Warning! \t Wrong SQL !')
#             return None


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
# # CREATE TABLE functions.rawdata (
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
#     # connect_info[3] = 'functions'
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


class DataManagerByDB(AbstractDataManager):
    from modules.DataBase import SqliteWrapper
    """[Depreciated]"""

    def __init__(self, db: SqliteWrapper):
        """General class for libdata info management"""
        self._db = db

    def include(self, value):
        if isinstance(value, AbstractDataObject):
            if self._db.exists(value):
                self.__update_value__(value)
            else:
                self.__add_value__(value)
        else:
            raise TypeError

    def __update_value__(self, value):
        if isinstance(value, (Book, Reader)):
            stored_value = self._db.get_one(type(value), index=value.index)
            stored_value.update_from(value)
            self._db.merge(stored_value)
        elif isinstance(value, Event):
            stored_value = self._db.get_one(Event,
                                            book_id=value.book_id, reader_id=value.reader_id,
                                            event_date=value.event_date, event_type=value.event_type)
            stored_value.update_from(value)
            self._db.merge(stored_value)
        else:
            raise TypeError

    def __add_value__(self, value):
        if isinstance(value, list):
            self._db.add_all(value)
        else:
            self._db.add(value)

    def extend(self, value_list: list):
        for_add = list()
        for_change = list()
        check_list = self._db.exists(value_list)
        for i in range(len(value_list)):
            if check_list[i] is True:
                for_change.append(value_list[i])
            else:
                for_add.append(value_list[i])
        self.__add_value__(for_add)
        for item in for_change:
            self.__update_value__(item)
