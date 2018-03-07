# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import csv
import logging
import pickle

from enum import Enum

from utils.Errors import FileTypeError
from utils.Errors import ParamTypeError
from utils.Logger import LogInfo


class FileType(Enum):
    csv = 'csv'
    bytes = 'bytes'


class FileIO(object):

    @staticmethod
    def __check_file_type__(file_path: str, target_type):
        """check and correct file_path to target file type -> str """
        # check file type
        if isinstance(target_type, str):
            this_type = FileType(target_type).value
        elif isinstance(target_type, FileType):
            this_type = target_type.value
        else:
            raise ParamTypeError('target_type', (str, FileType), target_type)

        if '.' in file_path:
            if file_path.split('.')[-1] == this_type:
                return file_path
            else:
                return '.'.join([file_path, this_type])
        else:
            return '.'.join([file_path, this_type])

    @staticmethod
    def load_csv(file_path: str, encoding='utf-8', res_type=list):
        """Return content of csv file in predefined type -> res_type"""
        if res_type == list:
            file_name = FileIO.__check_file_type__(file_path, FileType.csv)
            csv_file = open(file_name, 'r', newline='', encoding=encoding)
            __content__ = list()
            spam_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            for __line__ in spam_reader:
                __content__.append(__line__)
            return __content__
        else:
            raise NotImplementedError()

    @staticmethod
    def save_csv(file_path: str, content, encode='utf-8'):
        """save a list which is of two dimension to the file with lines in list and columns in sub_lists"""
        assert file_path == FileIO.__check_file_type__(file_path, FileType.csv), repr(
            FileTypeError(file_path, FileType.csv)
        )

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

        csv_file = open(file_path, 'w', newline='', encoding=encode)
        spam_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        spam_writer.writerows(content_to_file)
        csv_file.close()

    @staticmethod
    def save_bytes(file_path: str, temp):
        pickle.dump(temp, open(file_path, 'wb'))

    @staticmethod
    def load_bytes(file_path: str):
        return pickle.load(open(file_path, 'rb'))
