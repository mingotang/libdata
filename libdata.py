# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging

from utils.Logger import LogInfo, RunTimeCounter, set_logging


set_logging()

RunTimeCounter.get_instance()


__i__ = logging.debug


# -------- storing data --------
from modules.DataStore import store_book, store_event, store_reader
# store_book()
# store_event()
# store_reader()

# -------- grouping data --------
from modules.Functions import group_by
# group_by(group_tag='books', by_tag='year')
# group_by(group_tag='readers', by_tag='college')
# group_by(group_tag='readers', by_tag='register_year')
# group_by(group_tag='readers', by_tag='rtype')

# -------- convert data --------
from utils.FileSupport import convert_pdict_to_dict
# convert_pdict_to_dict('books')
# convert_pdict_to_dict('events')
# convert_pdict_to_dict('readers')


print(LogInfo.time_passed())
