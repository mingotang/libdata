# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging
import time

from tqdm import tqdm

from modules.DataStructure import Reader, Book, EventAction
from utils.Errors import ParamTypeError


# --------------------------------------------------------
class GeneralManager(object):

    def __init__(self):
        """General class for libdata info management"""
        self.stored_dict = dict()
        self.stored_list = list()

    def include(self, value):
        """
        add value to manager data
        :param value: defined object
        :return: None
        """
        if isinstance(value, Book):
            if value.index in self.stored_dict:
                self.update_member(value)
            else:
                self.stored_dict[value.index] = value
        elif isinstance(value, Reader):
            if value.index in self.stored_dict:
                self.update_member(value)
            else:
                self.stored_dict[value.index] = value
        elif isinstance(value, EventAction):
            self.stored_list.append(value)
        else:
            raise ParamTypeError('value', 'Book/Reader/EventAction', value)

    def update_member(self, value):
        raise NotImplementedError()

    def extend(self, data_list: list):
        raise NotImplementedError()

    @property
    def data(self):
        raise NotImplementedError()


# --------------------------------------------------------
class BookManager(GeneralManager):

    def update_member(self, value: Book):
        if value.index == self.stored_dict[value.index].index:
            origin = self.stored_dict[value.index]
            origin.update(value)
            self.stored_dict[value.index] = origin
        else:
            logging.warning('Conflict info - BookManager:\n\t{0:s}\n\t{1:s}'.format(
                str(value), str(self.stored_dict[value.index])
            ))

    def extend(self, data_list: list):
        for item in tqdm(data_list, desc='{0:s}.extending'.format(self.__class__.__name__)):
            self.include(Book(
                index=item['sysID'],
                lib_index=item['libIndexID'],
                name=item['bookname'],
                isbn=item['isbn'],
                author=item['author'],
                year=item['publish_year'],
                publisher=item['publisher'],
            ))

    @property
    def data(self):
        return [self.stored_dict[var] for var in self.stored_dict]


class ReaderManager(GeneralManager):

    def update_member(self, value: Reader):
        if value.index == self.stored_dict[value.index].index:
            origin = self.stored_dict[value.index]
            origin.update(value)
            self.stored_dict[value.index] = origin
        else:
            logging.warning('Conflict info - ReaderManager:\n\t{0:s}\n\t{1:s}'.format(
                str(value), str(self.stored_dict[value.index])
            ))  # print and output error

    def extend(self, data_list: list):
        for item in tqdm(data_list, desc='{0:s}.extending'.format(self.__class__.__name__)):
            self.include(Reader(
                index=item['userID'],
                rtype=item['user_type'],
                college=item['collegeID'],
                ))

    @property
    def data(self):
        return [self.stored_dict[var] for var in self.stored_dict]


class ReadersEventManager(GeneralManager):

    def extend(self, data_list: list):
        for item in tqdm(data_list, desc='{0:s}.extending'.format(self.__class__.__name__)):
            self.include(
                value=EventAction(
                    book_id=item['sysID'],
                    reader_id=item['userID'],
                    event_date=item['event_date'],
                    event_type=item['event_type'],
                )
            )

    def update_member(self, value):
        pass

    @property
    def data(self):
        return self.stored_list


# --------------------------------------------------------


# --------------------------------------------------------
if __name__ == '__main__':
    # import time
    start_time = time.time()
    # ------------------------------
    # store data to sqlite database
    from modules.DataBaseWrapper import SqliteWrapper
    from modules.DataStructure import LogInfo
    from ServiceComponents import RawDataProcessor

    logging.basicConfig(
        level=logging.DEBUG,  # 定义输出到文件的log级别，
        format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',  # 定义输出log的格式
        datefmt='%Y-%m-%d %A %H:%M:%S',  # 时间
    )

    local_db = SqliteWrapper(flush_db=True)
    logging.info(LogInfo.running('connect sqlite3 database', 'finished'))
    logging.warning(LogInfo.running('flush sqlite3 database when connect', 'finished'))

    data = RawDataProcessor.derive_raw_data(folder_path='data', file_range=[])
    logging.info(LogInfo.running('loading raw data', 'loaded'))

    reader_data = ReaderManager()
    reader_data.extend(data)
    local_db.add_all(reader_data.data)
    logging.info(LogInfo.running('storing reader data', 'finished'))
    del reader_data

    book_data = BookManager()
    book_data.extend(data)
    local_db.add_all(book_data.data)
    logging.info(LogInfo.running('storing book data', 'finished'))
    del book_data

    reader_event_data = ReadersEventManager()
    reader_event_data.extend(data)
    local_db.add_all(reader_event_data.data)
    logging.info(LogInfo.running('storing reader events data', 'finished'))
    del reader_event_data

    del data
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration) // 3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    time.sleep(1)
    print('\nRunning time: {0:d} h {1:d} m {2:.2f} s'.format(hour, minutes, seconds))
