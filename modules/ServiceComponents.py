# -*- encoding: UTF-8 -*-
# --------------------------------------------------------
import os
import csv
from modules.DataStructure import DataObject
# --------------------------------------------------------


# --------------------------------------------------------
class EventAction(object):
    def __init__(self, data_object=DataObject(), **kwargs):
        self.__attr_tag_list__ = ('event_type', 'event_date')
        self.event_type = str()
        self.year = str()
        self.month = str()
        self.day = str()


# --------------------------------------------------------
class Reader(object):
    def __init__(self, data_object=DataObject(), **kwargs):
        self.id = str()
        self.type = str()
        self.college = str()


# --------------------------------------------------------
class Book(object):
    def __init__(self, data_object=DataObject(), **kwargs):
        self.id = str()
        self.lib_index = str()
        self.name = str()
        self.isbn = str()
        self.author = str()
        self.year = str()
        self.publisher = str()


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
