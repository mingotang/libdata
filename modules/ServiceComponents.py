# -*- encoding: UTF-8 -*-
# --------------------------------------------------------
import os
import csv
from modules.DataStructure import DataObject
# --------------------------------------------------------


# --------------------------------------------------------
class EventAction(object):
    def __init__(self, data_object=DataObject(), **kwargs):
        self.__attr_tag_list__ = ('event_type', 'event_date', 'userID', 'sysID')
        if len(data_object) > 0:
            user_id = data_object['userID']
            book_id = data_object['sysID']
            event_type = data_object['event_type']
            event_date = data_object['event_date']
        else:
            user_id = kwargs['userID']
            book_id = kwargs['sysID']
            event_type = kwargs['event_type']
            event_date = kwargs['event_date']
        self.event_type = event_type
        self.year = event_date[0:4]
        self.month = event_date[4:6]
        self.day = event_date[6:8]
        self.book_id = book_id
        self.reader_id = user_id


# --------------------------------------------------------
class Reader(object):
    def __init__(self, data_object=DataObject(), **kwargs):
        self.__attr_tag_list__ = ('userID', 'user_type', 'collegeID')
        if len(data_object) > 0:
            user_id = data_object['userID']
            user_type = data_object['user_type']
            college = data_object['collegeID']
        else:
            user_id = kwargs['userID']
            user_type = kwargs['user_type']
            college = kwargs['collegeID']
        self.id = user_id
        self.type = user_type
        self.college = college


# --------------------------------------------------------
class Book(object):
    def __init__(self, data_object=DataObject(), **kwargs):
        if len(data_object) > 0:
            book_id = data_object['sysID']
            book_lib = data_object['libIndexID']
            book_name = data_object['bookname']
            book_isbn = data_object['isbn']
            book_author = data_object['author']
            book_year = data_object['publish_year']
            book_publisher = data_object['publisher']
        else:
            book_id = kwargs['sysID']
            book_lib = kwargs['libIndexID']
            book_name = kwargs['bookname']
            book_isbn = kwargs['isbn']
            book_author = kwargs['author']
            book_year = kwargs['publish_year']
            book_publisher = kwargs['publisher']
        self.id = book_id
        self.lib_index = book_lib
        self.name = book_name
        self.isbn = book_isbn
        self.author = book_author
        self.year = book_year
        self.publisher = book_publisher


# --------------------------------------------------------
class FileIO(object):
    @staticmethod
    def load_csv_2d(folder_path: str, filename: str, encode='utf-8'):
        """
        load a list which is of two dimension
        with lines in list and columns in sub_lists
        """
        csv_file = open(os.path.join(folder_path, filename), 'r', newline='', encoding=encode)
        __content__ = list()
        spam_reader = csv.reader(csv_file,
                                 delimiter=',',
                                 quotechar='"'
                                 )
        for __line__ in spam_reader:
            __content__.append(__line__)
        print('load_csv_2d. File {0:s} is loaded !'.format(filename))
        return __content__

    @staticmethod
    def save_csv_2d(folder_path: str, filename: str, content: list, encode='utf-8'):
        """
        save a list which is of two dimension to the file
        with lines in list and columns in sub_lists
        """
        if filename[-4:] != '.csv':
            file_name = filename + '.csv'
        else:
            file_name = filename
        csv_file = open(os.path.join(folder_path, file_name), 'w', newline='', encoding=encode)
        spam_writer = csv.writer(csv_file,
                                 delimiter=',',
                                 quotechar='"',
                                 quoting=csv.QUOTE_MINIMAL
                                 )
        spam_writer.writerows(content)
        csv_file.close()
        print('save_csv_2d. File {0:s} is saved ! '.format(file_name))
# --------------------------------------------------------


# --------------------------------------------------------
# --------------------------------------------------------


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
