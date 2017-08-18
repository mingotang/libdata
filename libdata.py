#! /usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------import------------------------------------
import os
from modules.BasicDataSetting import *
from modules.DataProcessing import load_data, save_csv_2d
from modules.RelationshipCF import CollaborativeFiltering
# ---------------------------------------------------------------------------


# -------------------------------------------------------- CF preparing
from modules.DataProcessing import derive_tag_A_to_tag_B_dict
from modules.DataProcessing import derive_tag_A_to_object_B_dict


def prepare_for_colla_filtering(raw_file):
    # initialing temp to accelerate searching, all temp stored in temp/
    # Hash table: systemID -> readerID
    derive_tag_A_to_tag_B_dict(tag_system_id, tag_reader_id, raw_file,
                               watch_result=False,
                               output=True,
                               filename=os.path.join('temp', filename_dict_systemID_readerID))
    # Hash table: readerID -> systemID
    derive_tag_A_to_tag_B_dict(tag_reader_id, tag_system_id, raw_file,
                               watch_result=False,
                               output=True,
                               filename=os.path.join('temp', filename_dict_readerID_systemID))


def prepare_for_monitoring(raw_file):
    # Hash table: systemID -> other info
    derive_tag_A_to_object_B_dict(tag_system_id,
                                  [tag_biblio,
                                   tag_book_name,
                                   tag_isbn,
                                   tag_author,
                                   tag_publish_year,
                                   tag_publisher],
                                  raw_file,
                                  watch_result=False,
                                  output=True,
                                  filename=os.path.join('temp', filename_dict_systemID_bookinfo))
    # Hash table: readerID -> other info
    derive_tag_A_to_object_B_dict(tag_reader_id,
                                  [tag_reader_type,
                                   tag_reader_college],
                                  raw_file,
                                  watch_result=False,
                                  output=True,
                                  filename=os.path.join('temp', filename_dict_readerID_readerinfo))


def act_reader_based_collafilter(book_num, watch_result=False, output=True):
    colla_result = list()
    cf_recommend = CollaborativeFiltering(os.path.join('temp', filename_dict_readerID_systemID),
                                          os.path.join('temp', filename_dict_systemID_readerID)
                                          )
    reader_list = load_data(os.path.join('temp', filename_dict_readerID_readerinfo))
    for reader in reader_list:
        colla_result.append([reader])
        colla_result[-1].extend(list(cf_recommend.reader_based_simple_filtering(reader, book_num)))
    if watch_result:
        for result in colla_result:
            print(result[0], end=' - ')
            if len(result) >= 2:
                print(result[1:])
            else:
                print(' ')
    if output:
        save_csv_2d(os.path.join('results', 'Reader based CF - simple - {0:d}.txt'.format(book_num)),
                    colla_result)


def act_book_based_collafilter(book_num, watch_result=False, output=True):
    colla_result = list()
    cf_recommend = CollaborativeFiltering(os.path.join('temp', filename_dict_readerID_systemID),
                                          os.path.join('temp', filename_dict_systemID_readerID)
                                          )
    book_list = load_data(os.path.join('temp', filename_dict_systemID_bookinfo))
    for book in book_list:
        colla_result.append([book])
        colla_result[-1].extend(list(cf_recommend.book_based_simple_filtering(book, book_num)))
    if watch_result:
        for result in colla_result:
            print(result[0], end=' - ')
            if len(result) >= 2:
                print(result[1:])
            else:
                print(' ')
    if output:
        save_csv_2d(os.path.join('results', 'Book based CF - simple - {0:d}.txt'.format(book_num)),
                    colla_result)
# --------------------------------------------------------


if __name__ == '__main__':
    import time
    start_time = time.time()
    # ------------------------------
    print(os.getcwd())
    file_name_list = (os.path.join('rawData', '2016-11-16-guanyuan2013.txt'),
                      os.path.join('rawData', '2016-11-16-guanyuan2014.txt'),
                      os.path.join('rawData', '2016-11-16-guanyuan2015.txt')
                      )
    # ------------------------------ Apriori
    # ------------------------------
    # ------------------------------ CF
    # prepare_for_colla_filtering(file_name_list)
    # prepare_for_monitoring(file_name_list)
    # act_reader_based_collafilter(10)
    act_book_based_collafilter(10)
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration)//3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.4f} s'.format(hour, minutes, seconds))
