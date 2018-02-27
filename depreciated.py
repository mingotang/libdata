# -*- encoding: UTF-8 -*-
from .DataStructure import EventAction


# --------------------------------------------------------
class EventActionList(object):
    def __init__(self):
        """
        Data structure for actions readers did
        """
        self.stored_list = list()
        self.__index_for_iter__ = int()

    def __repr__(self):
        return '\n'.join([str(var) for var in self.stored_list]) + '\n'

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
