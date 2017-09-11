# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os
import pickle
from modules.DataStructure import GeneralDict
from modules.ServiceComponents import Book, Reader, EventAction, EventActionList


# --------------------------------------------------------
class GeneralManager(GeneralDict):
    global_info = 'Test'
    def __init__(self, folder_path: str, data_postfix='.libdata', loading_name='GeneralData'):
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
        try:
            self.load(file_name=loading_name)
        except FileNotFoundError:
            self.save(file_name=loading_name)
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

    def loads(self, content: dict):
        self.stored_dict = content

    def load(self, file_name=''):
        data_file_name = self.__check_file_name__(file_name)
        data_dict = pickle.load(open(os.path.join(self.folder_path, data_file_name), 'rb'))
        self.loads(content=data_dict)

    def saves(self):
        return self.stored_dict

    def save(self, file_name=''):
        data_file_name = self.__check_file_name__(file_name)
        content = self.saves()
        pickle.dump(content, open(os.path.join(self.folder_path, data_file_name), 'wb'))
        self.__saved_or_not__ = True

    def include(self, key: str, value):
        self.__saved_or_not__ = False
        if key in self.stored_dict:
            self.update_member(key, value)
        else:
            self.__setitem__(key, value)

    def extend(self, key: str, value_list: list):
        for item in value_list:
            self.include(key, item)
        self.save()
        self.__saved_or_not__ = True

    def update_member(self, key: str, value):
        self.__saved_or_not__ = False
        raise NameError('Method {0:s}.update_member is not defined'.format(self.__class__.__name__))


# --------------------------------------------------------
class BookManager(GeneralManager):
    def __init__(self, folder_path: str, data_postfix='.libdata', loading_name='BookData'):
        GeneralManager.__init__(self, folder_path, data_postfix=data_postfix,
                                loading_name=loading_name)

    def __setitem__(self, key: str, value: Book):
        self.stored_dict[key] = value

    def update_member(self, key: str, value: Book):
        if value == self.stored_dict[key]:
            return None
        else:   # TODO: finish update member
            pass


# --------------------------------------------------------
class ReaderManager(GeneralManager):
    def __init__(self, folder_path: str, data_postfix='.libdata', loading_name='ReaderData'):
        GeneralManager.__init__(self, folder_path, data_postfix=data_postfix,
                                loading_name=loading_name)

    def __setitem__(self, key: str, value: Reader):
        self.stored_dict[key] = value


# --------------------------------------------------------
class ReadersEventManager(GeneralManager):
    def __init__(self, folder_path: str, data_postfix='.libdata', loading_name='ReaderEventsData'):
        GeneralManager.__init__(self, folder_path, data_postfix=data_postfix,
                                loading_name=loading_name)

    def __setitem__(self, key: str, value: EventActionList):
        self.stored_dict[key] = value

    def add_action(self, reader_id: str, action_event: EventAction):
        if reader_id not in self.stored_dict:
            self.stored_dict[reader_id] = EventActionList()
        self.stored_dict[reader_id].add(action_event)


# --------------------------------------------------------


# --------------------------------------------------------
if __name__ == '__main__':
    import time
    start_time = time.time()
    # ------------------------------
    print(ReaderManager.global_info)
    manager = ReaderManager(folder_path=os.path.join('..', 'data'))
    print(manager)
    print(manager.global_info)
    # manager.save()
    # del manager
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration) // 3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.2f} s'.format(hour, minutes, seconds))
