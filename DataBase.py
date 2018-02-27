# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------

from sqlalchemy import create_engine
from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import create_session, mapper

from Config import DataBaseConfig
from DataStructure import Book, Reader, EventAction


# --------------------------------------------------------
class LibDB(object):
    def __init__(self, db_path=DataBaseConfig.file_path.value):
        self.engine = create_engine('sqlite:///{host}'.format(host=db_path), echo=False)
        self.metadata = MetaData(bind=self.engine)
        self.__table_definition__()
        self.metadata.create_all(bind=self.engine, checkfirst=True)
        self.__table_mapping__()
        self.session = create_session(bind=self.engine)

    def __table_definition__(self):
        self.user_table = Table(
            'users', self.metadata,
            Column('reader_id', String, nullable=False, primary_key=True),
            Column('rtype', String, nullable=False),
            Column('college', String),
        )
        self.book_table = Table(
            'books', self.metadata,
            Column('book_id', String, nullable=False, primary_key=True),
            Column('lib_index', String),
            Column('name', String),
            Column('isbn', String),
            Column('author', String),
            Column('year', String),
            Column('publisher', String),
        )
        self.events_table = Table(
            'events', self.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('book_id', String, ForeignKey('books.id')),
            Column('reader_id', String, ForeignKey('users.id')),
            Column('event_date', Date),
            Column('event_type', String),
        )

    def __table_mapping__(self):
        mapper(self.user_table, Reader)
        mapper(self.book_table, Book)
        mapper(self.events_table, EventAction)

    def clear_db(self):
        self.metadata.drop_all(bind=self.engine)


# --------------------------------------------------------


if __name__ == '__main__':
    import time
    start_time = time.time()
    # ------------------------------
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration)//3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.2f} s'.format(hour, minutes, seconds))
