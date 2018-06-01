# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging

from utils.Logger import LogInfo, RunTimeCounter, set_logging


set_logging()

RunTimeCounter.get_instance()


__i__ = logging.debug


if __name__ == '__main__':
    # -------- storing data --------
    # from modules.DataProxy import store_record_data
    # store_record_data()

    # -------- get data --------
    from modules.DataProxy import DataProxy
    data = DataProxy()

    # -------- process data --------
    from modules.Functions import group_by
    # group_by(group_tag='books', by_tag='year')
    group_by(data_dict=data.readers, group_tag='readers', by_tag='college', auto_save=True)
    group_by(data_dict=data.readers, group_tag='readers', by_tag='register_year', auto_save=True)
    group_by(data_dict=data.readers, group_tag='readers', by_tag='rtype', auto_save=True)

    from modules.Functions import index_books2readers
    index_books2readers(data.events, auto_save=True)

    from modules.Functions import induct_events_by_date
    induct_events_by_date(data.events, auto_save=True)

    # -------- clean data --------

    # -------- finishing --------
    data.close()

    LogInfo.time_sleep(1)
    print(LogInfo.time_passed())
