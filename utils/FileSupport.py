# -*- encoding: UTF-8 -*-
import csv
import pickle

from utils.Constants import BaseEnum


class FileType(BaseEnum):
    csv = 'csv'
    byte = 'bytes'
    pickle = 'pickle'


class BaseFileSupport(object):
    __file_type__ = None

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


class PickleSupport(BaseFileSupport):
    __file_type__ = FileType.pickle

    @classmethod
    def load(cls, *args, **kwargs):
        """BytesSupport.load(file_path) -> object"""
        try:  # parameters
            file_path = args[0]
            assert isinstance(file_path, str), repr(TypeError)
            file_path = cls.check_file_type(file_path)
        except IndexError:
            raise ValueError('file_path is missing.')

        return pickle.load(open(file_path, 'rb'))

    @classmethod
    def loads(cls, *args, **kwargs):
        """BytesSupport.load(bytes_content) -> object"""
        try:
            bytes_content = args[0]
            assert isinstance(bytes_content, bytes), repr(TypeError)
        except IndexError:
            raise ValueError('bytes_content is missing.')

        return pickle.loads(bytes_content)

    @classmethod
    def save(cls, *args, **kwargs):

        try:  # parameters
            file_path = args[0]
            assert isinstance(file_path, str), repr(TypeError)
            file_path = cls.check_file_type(file_path)
        except IndexError:
            raise ValueError('file_path is missing.')
        try:
            content = args[1]
        except IndexError:
            raise ValueError('content is missing')

        pickle.dump(content, open(file_path, 'wb'))

    @classmethod
    def saves(cls, *args, **kwargs):

        try:
            content = args[0]
        except IndexError:
            raise ValueError('content is missing')

        return pickle.dumps(content)


class CSVSupport(BaseFileSupport):
    __file_type__ = FileType.csv

    @classmethod
    def load(cls, *args, **kwargs):
        """ Return content of csv file in predefined type -> return_type """

        try:  # parameters
            file_path = args[0]
            assert isinstance(file_path, str), repr(TypeError)
            file_path = cls.check_file_type(file_path)
        except IndexError:
            raise ValueError('file_path is missing')

        # optional parameters
        if 'encoding' in kwargs:
            file_encoding = kwargs['encoding']
            assert isinstance(file_encoding, str), repr(TypeError)
        else:
            file_encoding = 'utf-8'
        if 'return_type' in kwargs:
            file_return_type = kwargs['return_type']
            assert isinstance(file_return_type, type), repr(TypeError)
        else:
            file_return_type = list

        # loading data
        if file_return_type == list:
            csv_file = open(file_path, 'r', newline='', encoding=file_encoding)
            content = list()
            spam_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            for l in spam_reader:
                content.append(l)
            return content
        else:
            raise NotImplementedError

    @classmethod
    def save(cls, *args, **kwargs):
        """save csv file"""

        try:  # parameters
            file_path = args[0]
            assert isinstance(file_path, str), repr(TypeError)
            file_path = cls.check_file_type(file_path)
        except IndexError:
            raise ValueError('file_path is missing.')
        try:
            content = args[1]
        except IndexError:
            raise ValueError('content is missing')

        # optional parameters
        if 'encoding' in kwargs:
            file_encoding = kwargs['encoding']
            assert isinstance(file_encoding, str), repr(TypeError)
        else:
            file_encoding = 'utf-8'

        if isinstance(content, list):
            content_to_file = content
        elif isinstance(content, dict):
            content_to_file = list()
            for tag in content:
                line_to_file = list()
                line_to_file.append(tag)
                if type(content[tag]) == list:
                    line_to_file.extend(content[tag])
                else:
                    raise ValueError()
        else:
            raise TypeError

        csv_file = open(file_path, 'w', newline='', encoding=file_encoding)
        spam_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        spam_writer.writerows(content_to_file)
        csv_file.close()
