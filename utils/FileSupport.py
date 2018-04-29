# -*- encoding: UTF-8 -*-
import csv
import logging
import pickle
import os

from collections import Iterable, Mapping

from Config import DataConfig
from utils.Persisit import Pdict, Pseries, Plist


def get_pdict(*args, keep_history=True):
    assert len(args) > 0
    return Pdict(
        os.path.join(DataConfig.data_path, os.path.sep.join(args)),
        keep_history=keep_history,
    )


def convert_pdict_to_dict(*args):
    assert len(args) > 0
    name = os.path.sep.join(args)
    save_pickle(
        Pdict(os.path.join(DataConfig.data_path, name), keep_history=True).copy(),
        os.path.join(DataConfig.data_path, name)
    )


def init_pdict(inst, *args):
    return Pdict.init_from(
        inst,
        os.path.join(DataConfig.data_path, os.path.sep.join(args)),
        keep_history=False,
    )

def get_pseries(*args, keep_history=True):
    assert len(args) > 0
    return Pseries(
        os.path.join(DataConfig.data_path, os.path.sep.join(args)),
        keep_history=keep_history
    )

def init_pseries(inst, *args, index_tag='index', **kwargs):
    return Pseries.init_from(
            inst,
            os.path.join(DataConfig.data_path, os.path.sep.join(args)),
            index_tag=index_tag, keep_history=False
        )


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
    file_path = __check_type__(os.path.join(DataConfig.data_path, os.path.sep.join(args)), 'pick')
    logging.debug('pickle file {} loading.'.format(file_path))
    return pickle.load(open(file_path, 'rb'))


def save_pickle(content, *args):
    assert len(args) > 0
    file_path = __check_type__(os.path.join(DataConfig.data_path, os.path.sep.join(args)), 'pick')
    pickle.dump(content, open(file_path, 'wb'))
    logging.debug('pickle file {} dumped.'.format(file_path))


def load_csv(*args, **kwargs):
    assert len(args) > 0
    file_path = __check_type__(os.path.join(DataConfig.data_path, os.path.sep.join(args)), 'csv')

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

    assert len(args) > 0
    file_path = __check_type__(os.path.join(DataConfig.data_path, os.path.sep.join(args)), 'csv')

    # optional parameters
    file_encoding = kwargs.get('encoding', 'utf-8')
    assert isinstance(file_encoding, str), repr(TypeError)

    content_to_file = list()
    if isinstance(content, (list, Plist, set)):
        for item in content:
            if isinstance(item, (list, Plist, set)):
                content_to_file.append([var for var in item])
            elif isinstance(item, (dict, Pdict)):
                line_to_file = list()
                for k, v in item.items():
                    line_to_file.append(k)
                    line_to_file.append(v)
                content_to_file.append(line_to_file)
            else:
                raise TypeError
    elif isinstance(content, (dict, Pdict)):
        for tag, item in content.items():
            line_to_file = list()
            line_to_file.append(tag)
            if isinstance(item, (list, Plist, set)):
                line_to_file.extend([var for var in item])
            elif isinstance(item, (dict, Pdict)):
                for k, v in item.items():
                    line_to_file.append(k)
                    line_to_file.append(v)
            else:
                raise ValueError()
            content_to_file.append(line_to_file)
    else:
        raise TypeError

    csv_file = open(file_path, 'w', newline='', encoding=file_encoding)
    spam_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    spam_writer.writerows(content_to_file)
    csv_file.close()
    logging.debug('csv file {} saved.'.format(file_path))


if __name__ == '__main__':
    convert_pdict_to_dict('books_group_by_readers')
    convert_pdict_to_dict('readers_group_by_books')
