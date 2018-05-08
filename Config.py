# -*- encoding: UTF-8 -*-


class DataConfig(object):
    name = 'test'
    raw_data_folder = '/Users/mingo/Downloads/persisted_libdata/raw_data'
    data_path = '/Users/mingo/Downloads/persisted_libdata'


class DataBaseConfig(object):
    file_path = '/Users/mingo/Downloads/Libdata.db'


class DataInfo(object):
    event_date_format = '%Y%m%d'
    raw_text_file_list = [
        # '2016-11-16-guanyuan2013.txt',
        # '2016-11-16-guanyuan2014.txt',
        '2016-11-16-guanyuan2015.txt',
    ]
