# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import csv
import pymysql


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
    def save_csv(file_path: str, content: list, encode='utf-8'):
        """
        save a list which is of two dimension to the file
        with lines in list and columns in sub_lists
        """
        if file_path[-4:] != '.csv':
            file_name = file_path + '.csv'
        else:
            file_name = file_path
        csv_file = open(file_name, 'w', newline='', encoding=encode)
        spam_writer = csv.writer(csv_file,
                                 delimiter=',',
                                 quotechar='"',
                                 quoting=csv.QUOTE_MINIMAL
                                 )
        spam_writer.writerows(content)
        csv_file.close()


# --------------------------------------------------------
class LibDB(object):
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
class TableClassic(object):
    inner_tag_to_sql_tag = {
        'sysID': '',
        'userID': '',
    }


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
