# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging
import os

from ServiceComponents import RawDataProcessor
from DataManagement import ReaderManager, BookManager, ReadersEventManager
from RulesGeneration import LibAssociationRulesGeneration
from ServiceComponents import FileIO

# --------------------------------------------------------


# --------------------------------------------------------


if __name__ == '__main__':
    import time
    start_time = time.time()
    # ------------------------------
    logging.basicConfig(
        level=logging.DEBUG,  # 定义输出到文件的log级别，
        format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',  # 定义输出log的格式
        datefmt='%Y-%m-%d %A %H:%M:%S',  # 时间
        # filename=param.log_file_name,  # log文件名
        # filemode='w',
    )
    data = RawDataProcessor.derive_raw_data(folder_path=os.path.join('data'),
                                            file_type='txt',
                                            file_list=[
                                                '2016-11-16-guanyuan2013.txt',
                                                '2016-11-16-guanyuan2014.txt',
                                                '2016-11-16-guanyuan2015.txt',
                                            ])
    book_data = BookManager()
    book_data.extend(data)
    reader_data = ReaderManager(folder_path=os.path.join('data'))
    reader_data.extend(data)
    reader_event_data = ReadersEventManager(folder_path=os.path.join('data'))
    reader_event_data.extend(data)
    # LibAssociationRulesGeneration.apriori(
    #     method='simple',
    #     # method='groupspecified', group_tag='collegeID',
    #     book=book_data, reader=reader_data, events=reader_event_data,
    #     basket_tag='userID', goods_tag='lib_index_class',
    #     min_support=0.2,
    # )
    recommend_info = LibAssociationRulesGeneration.collaborative_filtering(
        base='reader',
        book=book_data, reader=reader_data, events=reader_event_data,
    )
    FileIO.save_csv('CF_base-reader.csv', recommend_info)
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration)//3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.2f} s'.format(hour, minutes, seconds))
