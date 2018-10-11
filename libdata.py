# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
from utils import get_logger


logger = get_logger(module_name=__file__)


if __name__ == '__main__':
    logger.initiate_time_counter()

    # -------- [1] --------
    # 第一步，储存txt数据至shelve
    # from modules.DataProxy import store_record_data
    # store_record_data()

    # -------- [2] --------
    # 整理数据
    # from modules.DataProxy import DataProxy
    # data_proxy = DataProxy()
    # data_proxy.execute_events_induction('date')

    # -------- get data --------
    from modules.DataProxy import DataProxy
    data = DataProxy()


    # --------  --------
    data.close()

    logger.print_time_passed()
