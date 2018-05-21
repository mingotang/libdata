# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging

from utils.Logger import LogInfo, RunTimeCounter, set_logging


set_logging()

RunTimeCounter.get_instance()


__i__ = logging.debug


# -------- storing data --------
from modules.DataProxy import store_record_data
store_record_data()

# -------- process data --------
# group_by(group_tag='books', by_tag='year')
# group_by(group_tag='readers', by_tag='college')
# group_by(group_tag='readers', by_tag='register_year')
# group_by(group_tag='readers', by_tag='rtype')


# -------- clean data --------


print(LogInfo.time_passed())
