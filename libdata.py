# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


if __name__ == '__main__':

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
    from Environment import Environment
    from modules.DataProxy import store_events_by_date, store_events_by_register_month, store_readers_and_books

    env = Environment()
    store_readers_and_books()

    # --------  --------
