# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import csv

from utils import ParamMissingError, ParamTypeError
from utils.File.Base import BaseFileSupport


class CSVSupport(BaseFileSupport):
    __file_type__ = 'csv'

    @classmethod
    def load(cls, *args, **kwargs):
        """ Return content of csv file in predefined type -> return_type """

        try:  # parameters
            file_path = args[0]
            assert isinstance(file_path, str), repr(ParamTypeError('file_path', 'str', file_path))
            file_path = cls.check_file_type(file_path)
        except IndexError:
            raise ParamMissingError('file_path')

        # optional parameters
        if 'encoding' in kwargs:
            file_encoding = kwargs['encoding']
            assert isinstance(file_encoding, str), repr(ParamTypeError('encoding', 'str', file_encoding))
        else:
            file_encoding = 'utf-8'
        if 'return_type' in kwargs:
            file_return_type = kwargs['return_type']
            assert isinstance(file_return_type, type), repr(ParamTypeError('return_type', 'type', file_return_type))
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
            assert isinstance(file_path, str), repr(ParamTypeError('file_path', 'str', file_path))
            file_path = cls.check_file_type(file_path)
        except IndexError:
            raise ParamMissingError('file_path')
        try:
            content = args[1]
        except IndexError:
            raise ParamMissingError('content')

        # optional parameters
        if 'encoding' in kwargs:
            file_encoding = kwargs['encoding']
            assert isinstance(file_encoding, str), repr(ParamTypeError('encoding', 'str', file_encoding))
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
            raise ParamTypeError('content', (list, dict), content)

        csv_file = open(file_path, 'w', newline='', encoding=file_encoding)
        spam_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        spam_writer.writerows(content_to_file)
        csv_file.close()
