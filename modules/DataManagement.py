# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os
import time
import pickle

from tqdm import tqdm

from modules.DataStructure import GeneralDict, DataObject


# --------------------------------------------------------
class EventAction(GeneralDict):
    tag_index_list = ['event_type', 'event_date', 'userID', 'sysID']

    def __init__(self, data_object=DataObject(), **kwargs):
        """
        :param data_object: DataObject
        :param kwargs: key: see EventAction.tag_index_list
        """
        GeneralDict.__init__(self)
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
        self.year = event_date[0:4]
        self.month = event_date[4:6]
        self.day = event_date[6:8]
        self.stored_dict['event_date'] = event_date
        self.event_type = self.stored_dict['event_type'] = event_type
        self.book_id = self.stored_dict['sysID'] = book_id
        self.reader_id = self.stored_dict['userID'] = user_id

    def __repr__(self):
        return ' '.join(['event_date:', self.year + self.month + self.day,
                         'event_type:', self.event_type,
                         'userID:', self.reader_id, 'sysID', self.book_id])

    def __eq__(self, other):
        if self.day == other.day and self.month == other.month and self.year == other.year:
            if self.book_id == other.book_id and self.reader_id == other.reader_id:
                if self.event_type == other.event_type:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_one_event(self, other):
        return self.__eq__(other)

    def earlier_than(self, other):
        if self.year < other.year:
            return True
        elif self.year == other.year:
            if self.month < other.month:
                return True
            elif self.month == other.month:
                if self.day < other.day:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def same_time(self, other):
        if self.year == other.year and self.month == other.month and self.day == other.day:
            return True
        else:
            return False

    def later_than(self, other):
        if self.year > other.year:
            return True
        elif self.year == other.year:
            if self.month > other.month:
                return True
            elif self.month == other.month:
                if self.day > other.day:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def not_earlier_than(self, other):
        if self.same_time(other) and self.later_than(other):
            return True
        else:
            return False

    def not_later_than(self, other):
        if self.same_time(other) and self.earlier_than(other):
            return True
        else:
            return False


# --------------------------------------------------------
class EventActionList(object):
    def __init__(self):
        """
        Data structure for actions readers did
        """
        self.stored_list = list()
        self.__index_for_iter__ = int()

    def __repr__(self):
        return '\n'.join(self.stored_list)

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
class Reader(GeneralDict):
    tag_index_list = ['userID', 'user_type', 'collegeID']

    def __init__(self, data_object=DataObject(), **kwargs):
        """
        Data structure for readers
        :param data_object: DataObject
        :param kwargs: key: see Reader.tag_index_list
        """
        GeneralDict.__init__(self)
        self.id = None
        self.type = None
        self.college = None
        self.update(other=data_object, kwargs=kwargs)

    def update(self, other, **kwargs):
        if type(other) == DataObject:
            if len(other) > 0:
                user_id = other['userID']
                user_type = other['user_type']
                college = other['collegeID']
            else:
                user_id = kwargs['userID']
                user_type = kwargs['user_type']
                college = kwargs['collegeID']
            self.id = self.stored_dict['userID'] = user_id
            self.type = self.stored_dict['user_type'] = user_type
            self.college = self.stored_dict['collegeID'] = college
        elif type(other) == type(self):
            if len(self.type) > len(other.type):  # conflict modification
                self.type = self.stored_dict['user_type'] = other.type
            if len(self.college) > len(other.college):
                self.college = self.stored_dict['collegeID'] = other.college
        else:
            raise ValueError('{0:s} param other not legal'.format(self.__class__.__name__))

    def __repr__(self):
        return ' '.join(['readerID:', self.id, 'reader_type:', self.type,
                         'college:', self.college])

    def __eq__(self, other):
        if self.id == other.id and self.type == other.type and self.college == other.college:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_one_reader(self, other):
        if self.id == other.id:
            return True
        else:
            return False


# --------------------------------------------------------
class Book(GeneralDict):
    tag_index_list = ['sysID', 'libIndexID', 'bookname', 'isbn', 'author',
                      'publish_year', 'publisher', ]

    def __init__(self, data_object=DataObject(), **kwargs):
        """
        Data structure for books
        :param data_object: DataObject
        :param kwargs: key: see Book.tag_index_list
        """
        GeneralDict.__init__(self)
        self.id = None
        self.lib_index = None
        self.name = None
        self.isbn = None
        self.author = None
        self.year = None
        self.publisher = None
        self.update(other=data_object, kwargs=kwargs)

    def update(self, other, **kwargs):
        if type(other) == DataObject:
            if len(other) > 0:
                book_id = other['sysID']
                book_lib = other['libIndexID']
                book_name = other['bookname']
                book_isbn = other['isbn']
                book_author = other['author']
                book_year = other['publish_year']
                book_publisher = other['publisher']
            else:
                book_id = kwargs['sysID']
                book_lib = kwargs['libIndexID']
                book_name = kwargs['bookname']
                book_isbn = kwargs['isbn']
                book_author = kwargs['author']
                book_year = kwargs['publish_year']
                book_publisher = kwargs['publisher']
            self.id = self.stored_dict['sysID'] = book_id
            self.lib_index = self.stored_dict['libIndexID'] = book_lib
            self.name = self.stored_dict['bookname'] = book_name
            self.isbn = self.stored_dict['isbn'] = book_isbn
            self.author = self.stored_dict['author'] = book_author
            self.year = self.stored_dict['publish_year'] = book_year
            self.publisher = self.stored_dict['publisher'] = book_publisher
        elif type(other) == type(self):
            if len(self.author) != len(other.author):
                self.author = self.stored_dict['author'] = other.author
            if len(self.isbn) > other.isbn:
                self.isbn = self.stored_dict['isbn'] = other.isbn
            if len(self.name) > len(other.name):
                self.name = self.stored_dict['bookname'] = other.name
            if len(self.lib_index) > len(other.lib_index):
                self.lib_index = self.stored_dict['libIndexID'] = other.lib_index
            if len(self.year) > len(other.year):
                self.year = self.stored_dict['publish_year'] = other.year
            if len(self.publisher) > len(other.publisher):
                self.publisher = self.stored_dict['publisher'] = other.publisher
        else:
            raise ValueError('{0:s} param other not legal'.format(self.__class__.__name__))

    def __repr__(self):
        return ' '.join(['BookID:', self.id, 'BookLibIndex:', self.lib_index,
                         'BookName:', self.name, 'ISBN:', self.isbn, 'author:', self.author,
                         'publish_year:', self.year, 'publisher:', self.publisher])

    def __eq__(self, other):
        if self.id == other.id:
            if self.author == other.author and self.isbn == other.isbn and self.name == other.name:
                if self.lib_index == other.lib_index and self.year == other.year and self.publisher == other.publisher:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_one_book(self, other):
        if self.id == other.id:
            return True
        else:
            return False


# --------------------------------------------------------
class GeneralManager(GeneralDict):

    def __init__(self, folder_path: str, data_postfix='.libdata', loading_name='GeneralData', new_manager=False):
        """
        General class for libdata info management
        :param folder_path: path in which data info stored.
        :param data_postfix: data file postfix.
        :param loading_name: default data file name
        """
        GeneralDict.__init__(self)
        self.folder_path = folder_path
        self.__postfix__ = data_postfix
        self.__loading_name__ = loading_name
        self.__saved_or_not__ = False
        if not new_manager:
            try:
                self.load(file_name=loading_name)
                self.__saved_or_not__ = True
            except FileNotFoundError:
                self.__saved_or_not__ = False

    def __repr__(self):
        text = '{0:s}\'s content: \n'.format(self.__class__.__name__)
        if len(self.stored_dict) > 0:
            count = 1
            for item in self.stored_dict:
                text += str(count) + '.  ' + str(self.stored_dict[item])
                count += 1
        else:
            text += 'None.'
        return text

    def keys(self):
        return self.stored_dict.keys()

    def __check_file_name__(self, file_name: str):
        if file_name != '':
            correct_name = file_name
        else:
            correct_name = self.__loading_name__
        postfix_length = len(self.__postfix__)
        if len(correct_name) < postfix_length:
            name = correct_name + self.__postfix__
        else:
            index = 0 - postfix_length
            if correct_name[index:] == self.__postfix__:
                name = correct_name
            else:
                name = correct_name + self.__postfix__
        return name

    def loads(self, content):
        self.stored_dict = content

    def saves(self):
        return self.stored_dict

    def load(self, file_name=''):
        data_file_name = self.__check_file_name__(file_name)
        data_dict = pickle.load(open(os.path.join(self.folder_path, data_file_name), 'rb'))
        self.loads(content=data_dict)

    def save(self, file_name=''):
        data_file_name = self.__check_file_name__(file_name)
        content = self.saves()
        pickle.dump(content, open(os.path.join(self.folder_path, data_file_name), 'wb'))
        self.__saved_or_not__ = True

    def include(self, key: str, value):
        """
        add value to manager data
        :param key: str
        :param value: defined object
        :return: None
        """
        self.__saved_or_not__ = False
        if key in self.stored_dict:
            self.update_member(key, value)
        else:
            self.__setitem__(key, value)

    def extend(self, data_list: list):
        raise NameError('Method {0:s}.extend is not defined'.format(self.__class__.__name__))

    def update_member(self, key: str, value):
        self.__saved_or_not__ = False
        raise NameError('Method {0:s}.update_member is not defined'.format(self.__class__.__name__))

    def collect(self, method: str, target_tag: str):
        if method == 'distinct':
            distinct_result = set(self.collect(method, target_tag))
            return list(distinct_result)
        elif method == 'duplicated':
            result = list()
            for data_item in self.stored_dict:
                result.append(data_item[target_tag])
            return result
        else:
            raise ValueError('{0:s} param method {1:s} not legal'.format(self.__class__.__name__,method))


# --------------------------------------------------------
class BookManager(GeneralManager):
    def __init__(self, folder_path: str, data_postfix='.libdata', loading_name='BookData', new_manager=False):
        GeneralManager.__init__(self, folder_path, data_postfix=data_postfix,
                                loading_name=loading_name, new_manager=new_manager)

    def __setitem__(self, key: str, value: Book):
        self.stored_dict[key] = value

    def extend(self, data_list: list):
        for item in tqdm(data_list, desc='BookManager.extending'):
            self.include(key=item['sysID'], value=Book(data_object=item))

    def update_member(self, key: str, value: Book):
        if value == self.stored_dict[key]:
            return
        else:
            if value.is_one_book(self.stored_dict[key]):
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

    def group_by(self, group_tag: str):
        result = dict()
        tag_value_list = self.collect(method='distinct', target_tag=group_tag)
        for value in tag_value_list:
            sub_manager = BookManager(folder_path=self.folder_path, data_postfix=self.__postfix__, new_manager=True)
            for inner_tag in self.keys():
                if self.stored_dict[inner_tag][group_tag] == value:
                    sub_manager[inner_tag] = self.stored_dict[inner_tag]
            result[value] = sub_manager
        return result


# --------------------------------------------------------
class ReaderManager(GeneralManager):
    def __init__(self, folder_path: str, data_postfix='.libdata', loading_name='ReaderData', new_manager=False):
        GeneralManager.__init__(self, folder_path, data_postfix=data_postfix,
                                loading_name=loading_name, new_manager=new_manager)

    def __setitem__(self, key: str, value: Reader):
        self.stored_dict[key] = value

    def extend(self, data_list: list):
        for item in tqdm(data_list, desc='ReaderManager.extending'):
            self.include(key=item['userID'], value=Reader(data_object=item))

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

    def group_by(self, group_tag: str):
        result = dict()
        tag_value_list = self.collect(method='distinct', target_tag=group_tag)
        for value in tag_value_list:
            sub_manager = ReaderManager(folder_path=self.folder_path, data_postfix=self.__postfix__, new_manager=True)
            for inner_tag in self.keys():
                if self.stored_dict[inner_tag][group_tag] == value:
                    sub_manager[inner_tag] = self.stored_dict[inner_tag]
            result[value] = sub_manager
        return result


# --------------------------------------------------------
class ReadersEventManager(GeneralManager):
    def __init__(self, folder_path: str, data_postfix='.libdata', loading_name='ReaderEventsData',
                 allow_duplicated_record=True):
        GeneralManager.__init__(self, folder_path, data_postfix=data_postfix,
                                loading_name=loading_name)
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
            self.include(key=item['userID'], value=EventAction(data_object=item))


# --------------------------------------------------------


# --------------------------------------------------------
if __name__ == '__main__':
    # import time
    start_time = time.time()
    # ------------------------------
    from modules.ServiceComponents import RawDataProcessor
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
