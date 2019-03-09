# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import datetime


class BookMap(object):
    def __init__(self, raw_book_id: str, content_id: str):
        self.raw_book_id, self.content_id = raw_book_id, content_id

    @staticmethod
    def define_table(meta):
        from sqlalchemy import MetaData, Table, Column, String
        assert isinstance(meta, MetaData)
        return Table(
            'book_map', meta,
            Column('raw_book_id', String, nullable=False, primary_key=True),
            Column('content_id', String, nullable=False, primary_key=True),
        )


class ReaderLibClassAccessDay(object):
    def __init__(self, reader_id: str, lib_sub_class: str, day: str):
        self.reader_id = reader_id
        self.lib_sub_class = lib_sub_class
        self.day = day

    @property
    def date(self):
        return datetime.datetime.strptime(self.day, '%Y%m%d')

    @staticmethod
    def define_table(meta):
        from sqlalchemy import MetaData, Table, Column, String
        assert isinstance(meta, MetaData)
        return Table(
            'ReaderLibClassAccessDay', meta,
            Column('reader_id', String, nullable=False, primary_key=True),
            Column('lib_sub_class', String, nullable=False, primary_key=True),
            Column('day', String),
        )


class RecommendListObject(object):
    def __init__(self, list_name: str, book_index: str, rank: int = -1):
        self.list_name, self.book_index, self.rank = list_name, book_index, rank

    @staticmethod
    def define_table(meta):
        from sqlalchemy import MetaData, Table, Column, String, Integer
        assert isinstance(meta, MetaData)
        return Table(
            'recommend_list', meta,
            Column('list_name', String, nullable=False, primary_key=True),
            Column('book_index', String, nullable=False, primary_key=True),
            Column('rank', Integer),
        )
