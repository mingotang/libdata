# -*- encoding: UTF-8 -*-

from utils.FileSupport import FileType


class FileTypeError(Exception):
    def __init__(self, file_path: str, target_type):

        if '.' in file_path:  # get_all wrong file_type
            self.file_type = file_path.split('.')[-1]
        else:
            self.file_type = str(type(None))

        self.file_path = file_path  # get_all file path

        if isinstance(target_type, str):  # get_all target path
            self.target_type = FileType(target_type)
        elif isinstance(target_type, FileType):
            self.target_type = target_type.value
        else:
            raise TypeError()

    def __repr__(self):
        return 'file {0:s} expect type {1:s} but got type {2:s}'.format(
            self.file_path, self.target_type, self.file_type,
        )


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
    def __init__(self, param_name: str, value_range, param):
        self.name = param_name
        if isinstance(value_range, tuple):
            if len(value_range) == 2:
                self.range = '{} to {}'.format(value_range[0], value_range[1])
            else:
                raise ValueError
        elif isinstance(value_range, str):
            self.range = value_range
        else:
            raise TypeError
        self.got_value = str(param)

    def __repr__(self):
        return 'param {0:s} should take value in {1:s} but got value {2:s}'.format(
            self.name, self.range, self.got_value,
        )


class ParamNoContentError(Exception):
    def __init__(self, param_name: str):
        self.name = param_name

    def __repr__(self):
        return 'param {0:s} gets no content'.format(self.name)


class ParamMissingError(Exception):
    def __init__(self, param_name: str):
        self.name = param_name

    def __repr__(self):
        return 'param {0:s} missing'.format(self.name)



