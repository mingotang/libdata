# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os
import time
import pickle
import datetime

from tqdm import tqdm

from .Config import BasicInfo
from .DataStructure import Reader, Book, EventAction


# --------------------------------------------------------
class GeneralManager(object):

    def __init__(self):
        """
        General class for libdata info management
        :param folder_path: path in which data info stored.
        """
        self.stored_dict = dict()

    def __repr__(self):
        text = '{0:s}\'s content: \n'.format(self.__class__.__name__)
        if len(self.stored_dict) > 0:
            count = 1
            for item in self.stored_dict:
                text += '\t' + str(count) + ':  ' + str(self.stored_dict[item])
                count += 1
        else:
            text += 'None.'
        return text

    def include(self, key: str, value):
        """
        add value to manager data
        :param key: str
        :param value: defined object
        :return: None
        """
        if key in self.stored_dict:
            self.update_member(key, value)
        else:
            self.stored_dict[key] = value

    def extend(self, data_list: list):
        raise NameError('Method {0:s}.extend is not defined'.format(self.__class__.__name__))

    def update_member(self, key: str, value):
        raise NameError('Method {0:s}.update_member is not defined'.format(self.__class__.__name__))


# --------------------------------------------------------
class BookManager(GeneralManager):
    def __init__(self):
        GeneralManager.__init__(self)

    def extend(self, data_list: list):
        for item in tqdm(data_list, desc='BookManager.extending'):
            self.include(
                key=item['sysID'],
                value=Book(
                    book_id=item['sysID'],
                    lib_index=item['libIndexID'],
                    name=item['bookname'],
                    isbn=item['isbn'],
                    author=item['author'],
                    year=item['publish_year'],
                    publisher=item['publisher'],
                )
            )

    def update_member(self, key: str, value: Book):
        if value == self.stored_dict[key]:
            return
        else:
            if value.id == self.stored_dict[key].id:
                self.stored_dict[key].update(value)
                self.__saved_or_not__ = False
            else:
                print('Conflict info - BookManager:')  # print and output error
                print('\t', value)
                print('\t', self.stored_dict[key])
                store_path = os.path.join(self.folder_path, 'BookManager - conflict book info.pickle')
                try:
                    input_file = open(store_path, 'rb')
                    conf_info = pickle.load(input_file)
                    input_file.close()
                    os.remove(store_path)
                except FileNotFoundError:
                    conf_info = list()
                conf_info.append([value, self.stored_dict[key]])
                output_file = open(store_path, 'wb')
                pickle.dump(conf_info, output_file)
                output_file.close()


# --------------------------------------------------------
class ReaderManager(GeneralManager):
    def __init__(self, folder_path: str, data_postfix='.libdata', loading_name='ReaderData', new_manager=False):
        GeneralManager.__init__(self, folder_path, data_postfix=data_postfix,
                                loading_name=loading_name, new_manager=new_manager)

    def __setitem__(self, key: str, value: Reader):
        self.stored_dict[key] = value

    def extend(self, data_list: list):
        for item in tqdm(data_list, desc='ReaderManager.extending'):
            self.include(
                key=item['userID'],
                value=Reader(
                    reader_id=item['userID'],
                    rtype=item['user_type'],
                    college=item['collegeID'],
                )
            )

    def update_member(self, key: str, value: Reader):
        if value == self.stored_dict[key]:
            return
        else:
            if value.is_one_reader(self.stored_dict[key]):
                self.stored_dict[key].update(value)
                self.__saved_or_not__ = False
            else:
                print('Conflict info - ReaderManager:')
                print('\t', value)
                print('\t', self.stored_dict[key])
                store_path = os.path.join(self.folder_path, 'ReaderManager - conflict book info.pickle')
                try:
                    input_file = open(store_path, 'rb')
                    conf_info = pickle.load(input_file)
                    input_file.close()
                    os.remove(store_path)
                except FileNotFoundError:
                    conf_info = list()
                conf_info.append([value, self.stored_dict[key]])
                output_file = open(store_path, 'wb')
                pickle.dump(conf_info, output_file)
                output_file.close()


# --------------------------------------------------------
class ReadersEventManager(GeneralManager):
    def __init__(self, folder_path: str, data_postfix='.libdata', loading_name='ReaderEventsData',
                 allow_duplicated_record=True, new_manager=True):
        GeneralManager.__init__(self, folder_path, data_postfix=data_postfix,
                                loading_name=loading_name, new_manager=new_manager)
        self.allow_duplicated_events = allow_duplicated_record
        self.lock = None
        if self.__saved_or_not__ is True:
            self.lock = True
        else:
            self.lock = False

    def __setitem__(self, key: str, value: EventActionList):
        self.stored_dict[key] = value

    def saves(self):
        content_for_save = list()
        content_for_save.append(self.stored_dict)
        content_for_save.append(self.allow_duplicated_events)
        return content_for_save

    def loads(self, content: list, read_only=True):
        self.allow_duplicated_events = content.pop()
        self.stored_dict = content.pop()

    def __check_file_name__(self, file_name: str):
        if file_name != '':
            correct_name = file_name
        else:
            correct_name = self.__loading_name__
        postfix_length = len(self.__postfix__)
        if len(correct_name) < postfix_length:
            name = correct_name + ' {0:s}'.format(time.asctime()) + self.__postfix__
        else:
            index = 0 - postfix_length
            if correct_name[index:] == self.__postfix__:
                name = correct_name
            else:
                name = correct_name + ' {0:s}'.format(time.asctime()) + self.__postfix__
        return name

    def include(self, key: str, value: EventAction):
        """
        include user action data to readers events list
        :param key: reader_id, str
        :param value: EventAction
        :return: None
        """
        if self.lock:
            print('Warning: ReadersEventManager loaded from file is locked! ')
            return
        else:
            if key not in self.stored_dict:
                self.stored_dict[key] = EventActionList()
            else:
                self.__saved_or_not__ = False
                self.stored_dict[key].add(value, allow_duplicated_record=self.allow_duplicated_events)

    def extend(self, data_list: list):
        """
        extend and save user action data
        :param data_list:
        :return:
        """
        for item in tqdm(data_list, desc='ReadersEventManager.extending'):
            self.include(
                key=item['userID'],
                value=EventAction(
                    book_id=item['sysID'],
                    reader_id=item['userID'],
                    event_date=datetime.datetime.strptime(item['event_date'], BasicInfo.event_date_format),
                    event_type=item['event_type'],
                )
            )


# --------------------------------------------------------


# --------------------------------------------------------
if __name__ == '__main__':
    # import time
    start_time = time.time()
    # ------------------------------
    from ServiceComponents import RawDataProcessor
    data = RawDataProcessor.derive_raw_data(folder_path=os.path.join('..', 'data'),
                                            file_type='txt', file_list=[])
    book_data = BookManager(folder_path=os.path.join('..', 'data'))
    book_data.extend(data)
    book_data.save()
    reader_data = ReaderManager(folder_path=os.path.join('..', 'data'))
    reader_data.extend(data)
    reader_data.save()
    reader_event_data = ReadersEventManager(folder_path=os.path.join('..', 'data'))
    reader_event_data.extend(data)
    reader_event_data.save()
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration) // 3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    time.sleep(1)
    print('\nRunning time: {0:d} h {1:d} m {2:.2f} s'.format(hour, minutes, seconds))
