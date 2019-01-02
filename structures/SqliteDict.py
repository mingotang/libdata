# -*- encoding: UTF-8 -*-

from collections import Mapping, Iterable
from sqlalchemy import MetaData, Table, Column, String, Integer


def define_book_table(meta):
    assert isinstance(meta, MetaData)
    return Table(
        'books', meta,
        Column('index', String, nullable=False, primary_key=True),
        Column('lib_index', String),
        Column('name', String),
        Column('isbn', String),
        Column('author', String),
        Column('year', String),
        Column('publisher', String),
        Column('op_dt', String)
    )


def define_reader_table(meta):
    assert isinstance(meta, MetaData)
    return Table(
        'users', meta,
        Column('index', String, nullable=False, primary_key=True),
        Column('rtype', String, nullable=False),
        Column('college', String),
        Column('op_dt', String),
    )


def define_event_table(meta: MetaData):
    return Table(
        'events', meta,
        Column('book_id', String, primary_key=True),
        Column('reader_id', String, primary_key=True),
        Column('event_date', String, primary_key=True),
        Column('event_type', String, primary_key=True),
        Column('times', Integer),
    )


class SqliteWrapper(object):
    def __init__(self, db_path: str):
        from sqlalchemy import create_engine, MetaData
        from sqlalchemy.orm import sessionmaker
        # 建立连接
        self.engine = create_engine('sqlite:///{host}'.format(host=db_path), echo=False)
        self.metadata = MetaData(bind=self.engine)
        self.__table_definition__()
        # 若目标表格不存在则创建
        self.metadata.create_all(bind=self.engine, checkfirst=True)
        # 建立表格映射
        self.__table_mapping__()
        session = sessionmaker(bind=self.engine)
        self.session = session()

        # from sqlalchemy.orm import create_session
        # self.session = create_session(bind=self.engine)

    def __table_definition__(self):
        self.user_table = define_reader_table(self.metadata)
        self.book_table = define_book_table(self.metadata)
        self.events_table = define_event_table(self.metadata)

    def __table_mapping__(self):
        from sqlalchemy.orm import mapper
        from structures import Book, Event, Reader
        mapper(Reader, self.user_table)
        mapper(Book, self.book_table)
        mapper(Event, self.events_table)

    def add_all(self, obj):
        if len(obj) > 0:
            self.session.add_all(obj)
            self.session.commit()

    def add(self, obj):
        self.session.add(obj)
        self.session.commit()

    def delete_table(self, table):
        from sqlalchemy import Table
        assert isinstance(table, Table), str(TypeError('table should be of type sqlalchemy.Table'))
        self.metadata.remove(table)

    def clean(self):
        self.metadata.drop_all()

    def get_all(self, obj_type: type, **filter_by):
        """get_all all {obj_type} filter by {kwargs} -> list"""
        return self.session.query(obj_type).filter_by(**filter_by).all()

    def get_one(self, obj_type: type, **filter_by):
        return self.session.query(obj_type).filter_by(**filter_by).one()

    # def exists_reader(self, value: Reader):
    #     from sqlalchemy.orm.exc import NoResultFound
    #     try:
    #         return value.index in self.__reader_dict__
    #     except TypeError:
    #         try:
    #             self.session.query(Reader).filter_by(index=value.index).one()
    #             return True
    #         except NoResultFound:
    #             return False

    def merge(self, inst, **kwargs):
        self.session.merge(inst, load=kwargs.get('load', True))


class SqliteDict(SqliteWrapper, Mapping, Iterable):
    def __init__(self, db_path: str, obj_type: type, obj_index_attr: str):
        SqliteWrapper.__init__(self, db_path=db_path)
        self.__obj_type__ = obj_type
        self.__obj_index_attr__ = obj_index_attr

    def __setitem__(self, key: str, value):
        assert hasattr(value, self.__obj_index_attr__) and isinstance(value, self.__obj_type__)
        self.add(value)

    def __getitem__(self, key: str):
        return self.get_one(self.__obj_type__, **{self.__obj_index_attr__: key})

    def keys(self):
        for obj in self.values():
            yield getattr(obj, self.__obj_index_attr__)

    def values(self):
        for obj in self.session.query(self.__obj_type__).all():
            yield obj

    def items(self):
        for obj in self.values():
            yield getattr(obj, self.__obj_index_attr__), obj

    def __len__(self):
        return len(self.session.query(self.__obj_type__).all())


if __name__ == '__main__':
    pass
