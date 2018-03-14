# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import pickle

from utils import ParamMissingError, ParamTypeError
from utils.File.Base import BaseFileSupport


class BytesSupport(BaseFileSupport):
    __file_type__ = 'pick'

    @classmethod
    def load(cls, *args, **kwargs):
        """BytesSupport.load(file_path) -> object"""
        try:  # parameters
            file_path = args[0]
            assert isinstance(file_path, str), repr(ParamTypeError('file_path', 'str', file_path))
            file_path = cls.check_file_type(file_path)
        except IndexError:
            raise ParamMissingError('file_path')

        return pickle.load(open(file_path, 'rb'))

    @classmethod
    def loads(cls, *args, **kwargs):
        """BytesSupport.load(bytes_content) -> object"""
        try:
            bytes_content = args[0]
            assert isinstance(bytes_content, bytes), repr(ParamTypeError('bytes_content', 'bytes', bytes_content))
        except IndexError:
            raise ParamMissingError('bytes_content')

        return pickle.loads(bytes_content)

    @classmethod
    def save(cls, *args, **kwargs):

        try:  # parameters
            file_path = args[0]
            assert isinstance(file_path, str), repr(ParamTypeError('file_path', 'str', file_path))
            file_path = cls.check_file_type(file_path)
        except IndexError:
            raise ParamMissingError('file_path')
        try:
            content = args[1]
        except IndexError:
            raise ParamMissingError('content')

        pickle.dump(content, open(file_path, 'wb'))

    @classmethod
    def saves(cls, *args, **kwargs):

        try:
            content = args[0]
        except IndexError:
            raise ParamMissingError('content')

        return pickle.dumps(content)
