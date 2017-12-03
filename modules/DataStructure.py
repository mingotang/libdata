# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


# --------------------------------------------------------
class GeneralDict(object):
    def __init__(self):
        self.stored_dict = dict()
        self.__list_for_iter__ = list()

    def __repr__(self):
        return str(self.stored_dict)

    def __len__(self):
        return len(self.stored_dict)

    def __getitem__(self, key: str):
        if key not in self.stored_dict:
            raise IndexError('{0:s}.__getitem__: index {1:s} not in dict'.format(self.__class__.__name__, key))
        else:
            return self.stored_dict[key]

    def __setitem__(self, key: str, value):
        self.stored_dict[key] = value

    def __contains__(self, key: str):
        if key in self.stored_dict:
            return True
        else:
            return False

    def __iter__(self):
        self.__list_for_iter__ = list(self.stored_dict)
        self.__list_for_iter__.reverse()
        return self

    def __next__(self):
        if len(self.__list_for_iter__) == 0:
            raise StopIteration()
        return self.__list_for_iter__.pop()

    def __eq__(self, other):
        raise NameError('Method {0:s}.__eq__ is not defined'.format(self.__class__.__name__))


# --------------------------------------------------------
class DataObject(GeneralDict):
    def keys(self):
        return self.stored_dict.keys()

    def set(self, key: str, element):
        self.__setitem__(key, element)


# --------------------------------------------------------
class CountingDict(GeneralDict):
    # def __init__(self):
    #     GeneralDict.__init__(self)

    def count(self, element: str, step=1):
        if element in self.stored_dict:
            self.stored_dict[element] += step
        else:
            self.stored_dict[element] = step

    def keys(self):
        return self.stored_dict.keys()

    def sort_by_weights(self, inverse=False):
        stored_list = list(self.stored_dict)
        for index_x in range(len(stored_list)):
            for index_y in range(index_x + 1, len(stored_list)):
                if self.stored_dict[stored_list[index_x]] > self.stored_dict[stored_list[index_y]]:
                    stored_list[index_x], stored_list[index_y] = stored_list[index_y], stored_list[index_x]
        if inverse is True:
            return stored_list.reverse()
        else:
            return stored_list

    def total_weights(self, tag_list=tuple()):
        total_num = 0
        if len(tag_list) > 0:
            for tag in tag_list:
                total_num += self.stored_dict[tag]
        else:
            for tag in self.stored_dict:
                total_num += self.stored_dict[tag]
        return total_num


# --------------------------------------------------------
class EventAction(object):
    def __init__(self, data_object=DataObject(), **kwargs):
        """
        :param data_object: DataObject
        :param kwargs: key: 'event_type', 'event_date', 'userID', 'sysID'
        """
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
        for index in range(len(self.stored_list)):
            if element.not_later_than(self.stored_list[index]):
                self.stored_list.insert(index, element)
                return
        self.stored_list.append(element)


# --------------------------------------------------------
class Reader(object):
    def __init__(self, data_object=DataObject(), **kwargs):
        """
        Data structure for readers
        :param data_object: DataObject
        :param kwargs: key: 'userID', 'user_type', 'collegeID'
        """
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

    def update(self, other):
        if len(self.type) > len(other.type):  # conflict modification
            self.type = other.type
        if len(self.college) > len(other.college):
            self.college = other.college


# --------------------------------------------------------
class Book(object):
    def __init__(self, data_object=DataObject(), **kwargs):
        """
        Data structure for books
        :param data_object: DataObject
        :param kwargs: key: 'sysID', 'libIndexID', 'bookname', 'isbn', 'author', 'publish_year', 'publisher'
        """
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

    def update(self, other):
        if len(self.author) != len(other.author):
            self.author = other.author
        if len(self.isbn) > other.isbn:
            self.isbn = other.isbn
        if len(self.name) > len(other.name):
            self.name = other.name
        if len(self.lib_index) > len(other.lib_index):
            self.lib_index = other.lib_index
        if len(self.year) > len(other.year):
            self.year = other.year
        if len(self.publisher) > len(other.publisher):
            self.publisher = other.publisher


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
