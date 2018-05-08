# -*- encoding: UTF-8 -*-
import csv
import logging
import pickle
import os

from Config import DataConfig
from utils.Persisit import Pdict, Pseries, Plist


def __get_path__(*args, is_file: bool):
    path = os.path.join(DataConfig.data_path, DataConfig.name, os.path.sep.join(args))
    if is_file is True:
        make_path(path, is_file=True)
    else:
        if os.path.exists(path):
            pass
        else:
            make_path(path, is_file=False)
    return path


def get_pdict(*args, keep_history=True):
    assert len(args) > 0
    try:
        return load_pickle(*args)
    except FileNotFoundError:
        return Pdict(__get_path__(*args, is_file=False), keep_history=keep_history)


def get_plist(*args, keep_history=True):
    return Plist(__get_path__(*args, is_file=False), keep_history=keep_history)


def convert_pdict_to_dict(*args):
    assert len(args) > 0
    path = __get_path__(*args, is_file=False)
    save_pickle(
        Pdict(path, keep_history=True).copy(),
        path.split(os.path.sep)[-1],
    )


def init_pdict(inst, *args, load_optimize=False):
    new_pdict = Pdict.init_from(
        inst,
        __get_path__(*args, is_file=False),
        keep_history=False,
    )
    if load_optimize is True:
        convert_pdict_to_dict(*args)
    return new_pdict


def get_pseries(*args, keep_history=True):
    assert len(args) > 0
    return Pseries(
        __get_path__(*args, is_file=False),
        keep_history=keep_history
    )


def init_pseries(inst, *args, index_tag='index'):
    return Pseries.init_from(
            inst,
            __get_path__(*args, is_file=False),
            index_tag=index_tag, keep_history=False
        )


def make_path(path: str, is_file=True):
    path_list = path.split(os.path.sep)
    for i in range(len(path_list)):
        if i + 1 == len(path_list) and is_file is True:  # file path
            continue
        sub_path = os.path.sep.join(path_list[:i + 1])
        if sub_path == '':
            continue
        if os.path.exists(sub_path):
            continue
        else:
            os.mkdir(sub_path)


def __check_type__(file_path: str, file_type: str):
    if '.' in file_path:
        if file_path.split('.')[-1] == file_type:
            return file_path
        else:
            return '.'.join([file_path, file_type])
    else:
        return '.'.join([file_path, file_type])


def load_pickle(*args):
    """BytesSupport.load(file_path) -> object"""
    assert len(args) > 0
    file_path = __check_type__(__get_path__(*args, is_file=True), 'pick')
    logging.debug('pickle file {} loading.'.format(file_path))
    return pickle.load(open(file_path, 'rb'))


def save_pickle(content, *args):
    assert len(args) > 0
    file_path = __check_type__(__get_path__(*args, is_file=True), 'pick')
    pickle.dump(content, open(file_path, 'wb'))
    logging.debug('pickle file {} dumped.'.format(file_path))


def load_csv(*args, **kwargs):
    assert len(args) > 0
    file_path = __check_type__(__get_path__(*args, is_file=True), 'csv')

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


def save_csv(content, *args, **kwargs):
    """
    save csv
    :param content: list of str in lists
    :param args: path
    :param kwargs: encoding
    :return:
    """

    assert len(args) > 0
    file_path = __check_type__(__get_path__(*args, is_file=True), 'csv')

    # optional parameters
    file_encoding = kwargs.get('encoding', 'utf-8')
    assert isinstance(file_encoding, str), repr(TypeError)

    # saving data
    csv_file = open(file_path, 'w', newline='', encoding=file_encoding)
    spam_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    spam_writer.writerows(content)
    csv_file.close()
    logging.debug('csv file {} saved.'.format(file_path))


if __name__ == '__main__':
    convert_pdict_to_dict('books_group_by_readers')
    convert_pdict_to_dict('readers_group_by_books')
