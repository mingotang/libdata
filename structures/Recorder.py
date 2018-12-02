# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os

from Interface import AbstractRecordable


class BaseRecorder(object):
    def __init__(self, output_path: str):
        from datetime import datetime

        self.recos = dict()

        self.__time__ = datetime.now().strftime('%Y%m%d %H%M%S')
        self.__output_path__ = output_path

    def __del__(self):
        for reco in self.recos:
            reco.close()

    def add_recoder(self, *args, **kwargs):
        raise NotImplementedError

    def record(self, *args, **kwargs):
        raise NotImplementedError

    def close(self):
        for reco in self.recos:
            reco.close()


class CSVRecorder(BaseRecorder):

    def __init__(self, output_path: str):
        super(CSVRecorder, self).__init__(output_path)

        self.__recos_column__ = dict()

    def add_recoder(self, name: str, columns: list):
        file_path = os.path.join(self.__output_path__, 'Record {} {}.txt'.format(name, self.__time__))
        self.recos[name] = open(file_path, mode='w', encoding='utf-8')
        self.recos[name].write(','.join(columns) + '\n')
        self.__recos_column__[name] = columns

    def record(self, name: str, content):
        assert isinstance(content, AbstractRecordable)
        try:
            new_line = list()
            dict_for_record = content.record()
            for tag in self.__recos_column__[name]:
                new_line.append(dict_for_record[tag])
            self.recos[name].write(','.join(new_line) + '\n')
        except KeyError:
            raise RuntimeError('{}.record: add_recorder before record action.'.format(self.__class__.__name__))


class TextRecorder(BaseRecorder):
    def add_recoder(self, name: str):
        file_path = os.path.join(self.__output_path__, 'Record {} {}.txt'.format(name, self.__time__))
        self.recos[name] = open(file_path, mode='w', encoding='utf-8')

    def record(self, name: str, content):
        assert isinstance(content, AbstractRecordable)
        try:
            self.recos[name].write(str(content.record()) + '\n')
        except KeyError:
            raise RuntimeError('{}.record: add_recorder before record action.'.format(self.__class__.__name__))
