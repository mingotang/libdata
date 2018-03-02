# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import datetime
import re

from BasicInfo import DataInfo


# --------------------------------------------------------
class Reader(object):
    __attributes__ = ('index', 'rtype', 'college')

    def __init__(self, index: str, rtype: str, college: str):
        self.index = index
        self.rtype = rtype
        self.college = college

    def __repr__(self):
        return '\t'.join([(var + ': ' + str(self.__dict__[var])) for var in self.__attributes__])

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        else:
            for tag in self.__attributes__:
                if self.__dict__[tag] != other.__dict__[tag]:
                    return False
            return True

    def update(self, other):
        if len(other.college) == 5 and len(self.college) < 5:
            self.college = other.college
        if len(other.rtype) == 2 and len(self.rtype) < 2:
            self.rtype = other.rtype


class Book(object):
    __attributes__ = ('index', 'lib_index', 'name', 'isbn', 'author', 'year', 'publisher')

    def __init__(self, index: str, lib_index: str, name: str,
                 isbn: str, author: str, year: str, publisher: str):
        self.index = index
        self.lib_index = lib_index
        self.name = name
        self.isbn = isbn
        self.author = author
        self.year = year
        self.publisher = publisher

    def __repr__(self):
        return '\t'.join([(var + ': ' + str(self.__dict__[var])) for var in self.__attributes__])

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        else:
            for tag in self.__attributes__:
                if self.__dict__[tag] != other.__dict__[tag]:
                    return False
            return True

    def update(self, other):
        for tag in self.__attributes__:
            if len(self.__dict__[tag]) < len(other.__dict__[tag]):
                self.__dict__[tag] = other.__dict__[tag]


class EventAction(object):
    __attributes__ = ('book_id', 'reader_id', 'event_date', 'event_type')

    def __init__(self, book_id: str, reader_id: str,
                 event_date: str, event_type: str):
        self.book_id = book_id
        self.reader_id = reader_id
        self.event_date = event_date
        self.event_type = event_type

    def __repr__(self):
        return '\t'.join([(var + ': ' + str(self.__dict__[var])) for var in self.__attributes__])

    def __eq__(self, other):
        return self.book_id == other.book_id and self.reader_id == other.reader_id \
            and self.event_date == other.event_date and self.event_type == other.event_type

    @property
    def date(self):
        return datetime.datetime.strptime(self.event_date, DataInfo.event_date_format)


# --------------------------------------------------------


# --------------------------------------------------------
class DataObject(dict):
    inner_tag_to_line_index = {
        'libIndexID': 1,
        'bookname': 2,
        'isbn': 3,
        'author': 4,
        'publish_year': 5,
        'publisher': 6,
        'event_date': 8,
        'event_type': 9,
        'user_type': 10,
        'collegeID': 11,
    }
    def __init__(self, from_list: list):
        dict.__init__(self)
        self.__setitem__('sysID', re.sub(r'\W', '', from_list[0]))
        self.__setitem__('userID', re.sub(r'\W', '', from_list[7].upper()))
        for tag in self.inner_tag_to_line_index:
            self.__setitem__(tag, from_list[self.inner_tag_to_line_index[tag]])


# --------------------------------------------------------
class CountingDict(dict):
    def __init__(self):
        dict.__init__(self)

    def __mul__(self, other):
        if isinstance(other, dict):
            result = 0
            for self_element in self.keys():
                if self_element in other:
                    result += self.__getitem__(self_element) * other[self_element]
            return result
        else:
            raise TypeError()

    def count(self, element: str, step=1):
        if isinstance(step, int):
            if self.__contains__(element):
                self.__setitem__(element, self.__getitem__(element)+step)
            else:
                self.__setitem__(element, step)
        else:
            raise TypeError('step should be in type int instead of {0:s}'.format(step.__class__.__name__))

    def sort_by_weights(self, inverse=False):
        """ 按照值从小到大排序 """
        stored_list = list(self.keys())
        for index_x in range(len(stored_list)):
            for index_y in range(index_x + 1, len(stored_list)):
                if self[stored_list[index_x]] > self[stored_list[index_y]]:
                    stored_list[index_x], stored_list[index_y] = stored_list[index_y], stored_list[index_x]
        if inverse is True:
            return stored_list.reverse()
        else:
            return stored_list

    def total_weights(self, tag_list):
        if isinstance(tag_list, (list, tuple, set, frozenset)):
            total_num = 0
            if len(tag_list) > 0:
                for tag in tag_list:
                    total_num += self.__getitem__(tag)
            else:
                for tag in self.keys():
                    total_num += self.__getitem__(tag)
            return total_num
        else:
            raise TypeError()


# --------------------------------------------------------
class LogInfo(object):
    @staticmethod
    def running(running: str, status: str):
        return '[running]: {0:s} - now {1:s}'.format(
            running, status,
        )

    @staticmethod
    def variable_detail(variable):
        return '[variable]: {0:s} got type {1:s} and content {2:s}'.format(
            str(id(variable)), str(type(variable)), str(variable)
        )


# --------------------------------------------------------
class ParamTypeError(Exception):
    def __init__(self, param_name: str, param_target_type: str, param):
        self.name = param_name
        self.target_type = param_target_type
        self.got_type = str(type(param))

    def __repr__(self):
        return 'param {0:s} expect type {1:s} but got type {2:s}'.format(
            self.name, self.target_type, self.got_type,
        )


class ParamOutOfRangeError(Exception):
    def __init__(self, param_name: str, value_range: tuple, param):
        self.name = param_name
        self.range = value_range
        self.got_value = str(param)

    def __repr__(self):
        return 'param {0:s} range from {1} to {2} but got value {3:s}'.format(
            self.name, str(self.range[0]), str(self.range[1]), self.got_value,
        )


class ParamNoContentError(Exception):
    def __init__(self, param_name: str):
        self.name = param_name

    def __repr__(self):
        return 'param {0:s} has no content'.format(self.name)


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
