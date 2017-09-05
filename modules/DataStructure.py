# -*- encoding: UTF-8 -*-
# --------------------------------------------------------


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


# --------------------------------------------------------


# --------------------------------------------------------
if __name__ == '__main__':
    import time
    start_time = time.time()
    # ------------------------------
    l = CountingDict()
    print(l.__class__.__name__, type(l.__class__.__name__))
    print(l.__module__)
    print(l.__dict__)
    print(l.__getattribute__('stored_dict'))
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration) // 3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.2f} s'.format(hour, minutes, seconds))
