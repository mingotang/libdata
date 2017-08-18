# -*- encoding: UTF-8 -*-
# Realize SQL connection by pymysql based on MySQL
# --------------------------
import pymysql.cursors
# --------------------------
# Example:
# CREATE TABLE `users` (
#     `id` int(11) NOT NULL AUTO_INCREMENT,
#     `email` varchar(255) COLLATE utf8_bin NOT NULL,
#     `password` varchar(255) COLLATE utf8_bin NOT NULL,
#     PRIMARY KEY (`id`)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
# AUTO_INCREMENT=1 ;
# CREATE TABLE modules.rawdata (
#  	sysID varchar(100),
#  	indexID varchar(100),
#  	bookname varchar(100),
#  	isbn varchar(100),
#  	author varchar(100),
#  	publish_year varchar(100),
#  	publisher varchar(100),
#  	userID varchar(100),
#  	event_date varchar(100),
#  	event_type varchar(100),
#  	user_type varchar(100),
# 	collegeID varchar(100),
# 	tableID INT NOT NULL PRIMARY KEY AUTO_INCREMENT
# )
# ENGINE=InnoDB
# DEFAULT CHARSET=utf8
# COLLATE=utf8_general_ci ;


def connect_database(host_ip, sql_user_name, sql_password, database,
                 charset='utf8', cursorclass=pymysql.cursors.DictCursor):
    return pymysql.connect(host=host_ip,
                             user=sql_user_name,
                             password=sql_password,
                             db=database,
                             charset=charset,
                             cursorclass=cursorclass)


def disconnect_database(connection):
    connection.close()
    return 0


def execute_sql(connection, sql):
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            connection.commit()
            result = cursor.fetchone()
            line = []
            for item in result:
                line.append(result[item])
            return line
    except:
        print('execute_sql Warning! \t Wrong SQL !')
        return None


class SQL(object):
    def __init__(self, host_ip,
                 sql_user_name,
                 sql_password,
                 database,
                 charset='utf8',
                 cursorclass=pymysql.cursors.DictCursor
                 ):
        self.connection = pymysql.connect(host=host_ip,
                                 user=sql_user_name,
                                 password=sql_password,
                                 db=database,
                                 charset=charset,
                                 cursorclass=cursorclass
                                          )
        self.pyname2sqlname = {}
        self.sqlname2pyname = {}

    def add_into_table(self, tablename, headlist, contentdict):
        try:
            with self.connection.cursor() as cursor:
                sqllist = []
                sqllist.append("INSERT INTO `")
                sqllist.append(str(tablename))
                sqllist.append("` (")
                for head in headlist:
                    sqllist.append("`")
                    sqllist.append(self.pyname2sqlname[head])
                    sqllist.append("`")
                    sqllist.append(", ")
                sqllist.pop()
                sqllist.append(") VALUES (")
                for head in headlist:
                    sqllist.append(contentdict[head])
                    sqllist.append(", ")
                sqllist.pop()
                sqllist.append(")")
                sql = ''.join(sqllist)
                cursor.execute(sql)
                self.connection.commit()
                return 1
        except:
            print('\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tadd_into_rawdata Warning: - - - - - - ', contentdict)
            return 0

    def remove_from_rawdata(self, lineInList):
        line = lineInList
        try:
            with self.connection.cursor() as cursor:
                # sql = "DELETE FROM `rawdata` WHERE name='百度' AND country='CN';"
                sql = "DELETE FROM `rawdata` " \
                      "WHERE `sysID`=%s " \
                      "AND `indexID`=%s " \
                      "AND `bookname`=%s " \
                      "AND `isbn`=%s " \
                      "AND `author`=%s " \
                      "AND `publish_year`=%s " \
                      "AND `publisher`=%s " \
                      "AND `userID`=%s " \
                      "AND `event_date`=%s " \
                      "AND `event_type`=%s " \
                      "AND `user_type`=%s " \
                      "AND `collegeID`=%s;"
                cursor.execute(sql, (line[0], line[1], line[2], line[3], line[4], line[5],
                                     line[6], line[7], line[8], line[9], line[10], line[11]))
                self.connection.commit()
                return 1
        except:
            print('remove_from_rawdata Warning: ', line)
            return 0

    def select_from_table(self, table, tablenamelist, indexlist, IDlist):
        tablenamelist = ['sysID', 'indexID', tag_book_name, tag_isbn, tag_author, 'publish_year',
                         tag_publisher, 'userID', 'event_date', 'event_type', 'user_type', 'collegeID', 'tableID']
        sqllist = ['SELECT']
        for item in indexlist:
            sqllist.append(' `')
            sqllist.append(namelist[item])
            sqllist.append('`')
            sqllist.append(',')
        sqllist.pop()
        sqllist.append(' FROM `rawdata`;')
        sql = ''.join(sqllist)
        # print(sql)
        try:
            line = []
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
                self.connection.commit()
                result = cursor.fetchone()
                for item in indexlist:
                    line.append(result[namelist[item]])
            return line
        except:
            print('select_from_rawdata Warning!')
            return None


if __name__ == '__main__':
    import time
    start_time = time.time()
    # ------------------------------------
    # connect_info = load_data('bookdata/remote_libdata.pickle')
    # connect_info = load_data('bookdata/local_libdata.pickle')
    # print(connect_info)
    # libdatabase = SQL(connect_info[0], connect_info[1], connect_info[2], connect_info[3])
    # data = load_csv_2d('bookdata/guanyuan2015.csv')

    # for item in data:
    #     if item[9] == '50':
    #         libdatabase.add_into_table('borrowdata', item)
    # del data
    # del libdatabase
    # line = data[0]
    # libdatabase.add_into_rawdata(line)
    # libdatabase.remove_from_rawdata(line)
    # test = libdatabase.select_from_rawdata([0, 1])
    # print(test)
    # print(type(test))
    # ------------------------------------
    # connect_info = load_data('bookdata/remote_libdata.pickle')
    # print(connect_info)
    # connect_info[0] = '192.168.3.116'
    # connect_info[1] = 'mingotang'
    # connect_info[2] = 'sql771422'
    # connect_info[3] = 'modules'
    # print(connect_info)
    # save_data('bookdata/local_libdata.pickle', connect_info)
    # ------------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration) // 3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: %d h %d m %f s' % (hour, minutes, seconds))


