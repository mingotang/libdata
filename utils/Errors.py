# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
from enum import Enum


# --------------------------------------------------------
class ParamTypeError(Exception):
    def __init__(self, param_name: str, param_target_type, param):
        self.name = param_name
        self.got_type = str(type(param))
        if isinstance(param_target_type, str):
            self.target_type = param_target_type
        elif isinstance(param_target_type, (list, tuple, set, frozenset)):
            target_type_list = list()
            for item in param_target_type:
                if isinstance(item, str):
                    target_type_list.append(item)
                elif isinstance(item, type):  # object instance
                    target_type_list.append(item.__class__.__name__)
                else:
                    raise NotImplementedError()
            self.target_type = '/'.join(target_type_list)
        else:
            raise TypeError()

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
        return 'param {0:s} gets no content'.format(self.name)


class FileTypeError(Exception):
    def __init__(self, file_path: str, target_type):
        # get wrong file_type
        if '.' in file_path:
            self.file_type = file_path.split('.')[-1]
        else:
            self.file_type = str(type(None))
        # get file path
        self.file_path = file_path
        # get target path
        if isinstance(target_type, str):
            self.target_type = target_type
        elif isinstance(target_type, Enum):
            self.target_type = target_type.value
        else:
            raise TypeError()

    def __repr__(self):
        return 'file {0:s} expect type {1:s} but got type {2:s}'.format(
            self.file_path, self.target_type, self.file_type,
        )
