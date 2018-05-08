# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging

from utils.Logger import LogInfo, RunTimeCounter, set_logging


set_logging()

RunTimeCounter.get_instance()


__i__ = logging.debug


# -------- storing data --------
from modules.DataStore import store_record_data
from utils.FileSupport import convert_pdict_to_dict, get_pdict
# store_record_data()
# convert_pdict_to_dict('books')
# convert_pdict_to_dict('events')
# convert_pdict_to_dict('readers')

# -------- process data --------
from modules.Functions import group_by
# group_by(group_tag='books', by_tag='year')
# group_by(group_tag='readers', by_tag='college')
# group_by(group_tag='readers', by_tag='register_year')
# group_by(group_tag='readers', by_tag='rtype')

from modules.Functions import index_events
index_events(get_pdict('events'))

# -------- clean data --------


print(LogInfo.time_passed())
