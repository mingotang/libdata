# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
from utils import get_logger


logger = get_logger(module_name=__file__)


if __name__ == '__main__':
    logger.initiate_time_counter()
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

    logger.print_time_passed()
