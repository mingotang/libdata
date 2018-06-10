# -*- encoding: UTF-8 -*-
import csv
import logging
import pickle
import os

import pandas as pd

from Config import DataConfig
from utils.Logger import get_logger


logger = get_logger()


def get_shelve_db(db_name: str):
    from utils.DataBase import ShelveWrapper
    return ShelveWrapper(DataConfig.operation_path, db_name)


def __check_type__(file_path: str, file_type: str):
    if '.' in file_path:
        if file_path.split('.')[-1] == file_type:
            return file_path
        else:
            return '.'.join([file_path, file_type])
    else:
        return '.'.join([file_path, file_type])


def load_pickle(path: str):
    """BytesSupport.load(file_path) -> object"""
    file_path = __check_type__(path, 'pick')
    logging.debug('pickle file {} loading.'.format(file_path))
    return pickle.load(open(file_path, 'rb'))


def save_pickle(content, path: str):
    file_path = __check_type__(path, 'pick')
    pickle.dump(content, open(file_path, 'wb'))
    logging.debug('pickle file {} dumped.'.format(file_path))


def load_csv(*args, **kwargs):
    assert len(args) > 0
    file_path = __check_type__(args[0], 'csv')

    # optional parameters
    file_encoding = kwargs.get('encoding', 'utf-8')
    assert isinstance(file_encoding, str), repr(TypeError)

    file_return_type = kwargs.get('return_type', list)
    assert isinstance(file_return_type, type)

    # loading data
    logging.debug('csv file {} loading.'.format(file_path))
    if file_return_type == list:
        csv_file = open(file_path, 'r', newline='', encoding=file_encoding)
        content = list()
        spam_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        for l in spam_reader:
            content.append(l)
        return content
    else:
        raise NotImplementedError


def save_csv(content, *path, **kwargs):
    """
    save csv
    :param content: list of str in lists
    :param path: path
    :param kwargs: encoding
    :return:
    """
    assert len(path) > 0
    file_path = __check_type__(os.path.sep.join(path), 'csv')

    # optional parameters
    file_encoding = kwargs.get('encoding', 'utf-8')
    assert isinstance(file_encoding, str), repr(TypeError)

    # saving data
    if isinstance(content, list):
        csv_file = open(file_path, 'w', newline='', encoding=file_encoding)
        spam_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        spam_writer.writerows(content)
        csv_file.close()
    elif isinstance(content, pd.DataFrame):
        content.to_csv(file_path, encoding=file_encoding)
    else:
        from utils.Exceptions import ParamTypeError
        raise ParamTypeError('content', 'list(list)/pd.DataFrame', content)

    logger.debug('csv file {} saved.'.format(file_path))


if __name__ == '__main__':
    pass
