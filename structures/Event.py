# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import datetime

from Config import DataInfo
from structures.Base import BaseObject


class Event(BaseObject):
    __attributes__ = ('book_id', 'reader_id', 'event_date', 'event_type')

    def __init__(self, book_id: str, reader_id: str, event_date: str, event_type: str):
        self.book_id = book_id
        self.reader_id = reader_id
        self.event_date = event_date
        self.event_type = event_type

    @property
    def date(self):
        return datetime.datetime.strptime(self.event_date, DataInfo.event_date_format)
