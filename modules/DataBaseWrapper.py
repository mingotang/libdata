# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging

from sqlalchemy import create_engine
from sqlalchemy import Table, MetaData, Column, Integer, String
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.exc import IntegrityError

from BasicInfo import DataBaseConfig
from modules.DataStructure import Book, Reader, EventAction
from utils.Errors import ParamNoContentError, ParamTypeError
from utils.String import LogInfo


# --------------------------------------------------------
class SqliteWrapper(object):
    def __init__(self, db_path=DataBaseConfig.file_path.value, flush_db=False):
        self.engine = create_engine('sqlite:///{host}'.format(host=db_path), echo=False)
        self.metadata = MetaData(bind=self.engine)
        self.__table_definition__()
        if flush_db is True:
            self.metadata.drop_all()
        self.metadata.create_all(bind=self.engine, checkfirst=True)
        self.__table_mapping__()
        session = sessionmaker(bind=self.engine)
        self.session = session()
        # self.session = create_session(bind=self.engine)

    def __table_definition__(self):
        self.user_table = Table(
            'users', self.metadata,
            Column('index', String, nullable=False, primary_key=True),
            Column('rtype', String, nullable=False),
            Column('college', String),
        )
        self.book_table = Table(
            'books', self.metadata,
            Column('index', String, nullable=False, primary_key=True),
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
            Column('book_id', String),
            Column('reader_id', String),
            Column('event_date', String),
            Column('event_type', String),
        )

    def __table_mapping__(self):
        mapper(Reader, self.user_table)
        mapper(Book, self.book_table)
        mapper(EventAction, self.events_table)

    def add_all(self, obj, pass_duplicated=False):
        if len(obj) > 0:
            if pass_duplicated is False:
                self.session.add_all(obj)
                self.session.commit()
            else:
                for i in range(len(obj)):
                    try:
                        self.add(obj[i])
                    except IntegrityError:
                        logging.debug(LogInfo.variable_detail(obj[i]))
                        self.session.rollback()
                        continue
        else:
            logging.warning(repr(ParamNoContentError('obj')))

    def add(self, obj):
        if isinstance(obj, (Book, Reader, EventAction)):
            self.session.add(obj)
            self.session.commit()
        else:
            raise ParamTypeError('obj', 'Book/Reader/EventAction', obj)


# --------------------------------------------------------


if __name__ == '__main__':
    import time
    start_time = time.time()
    # ------------------------------
    local_db = SqliteWrapper()

    print(local_db.session.query(Reader).filter_by(index='11395').one())
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration)//3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.2f} s'.format(hour, minutes, seconds))
