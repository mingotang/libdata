# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


class BaseFileSupport(object):
    __file_type__ = 'none'

    @classmethod
    def check_file_type(cls, file_path: str):
        """check and correct file_path to target file type -> str"""

        if '.' in file_path:
            if file_path.split('.')[-1] == cls.__file_type__:
                return file_path
            else:
                return '.'.join([file_path, cls.__file_type__])
        else:
            return '.'.join([file_path, cls.__file_type__])

    @classmethod
    def load(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def save(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def loads(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def saves(cls, *args, **kwargs):
        raise NotImplementedError
