# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging


# --------------------------------------------------------
class CollaborativeFiltering(object):
    def __init__(self, dict_person_book, dict_book_person):
        self.person_book = load_data(dict_person_book)
        self.book_person = load_data(dict_book_person)

    def reader_based_simple_filtering(self, reader_id, expect_book_amount):
        __recommend__ = set()
        __book_borrowed__ = set(self.person_book[reader_id])
        __similar_people__ = \
            self.__double_check_list__(reader_id,
                                       self.person_book,
                                       self.book_person)
        __similar_people__ = \
            self.__sort_list_by_appearance_time__(
                __similar_people__,
                self.__derive_appearance_times_in_dict_from_list__(__similar_people__)
            )
        while len(__similar_people__) > 0 and len(__recommend__) < expect_book_amount:
            __temp__ = set(self.person_book[__similar_people__[-1]])
            if __temp__.issubset(__book_borrowed__):
                pass
            else:
                __possible_book_list__ = list(__temp__ - __book_borrowed__)
                for __book__ in __possible_book_list__:
                    __recommend__.add(__book__)
                    if len(__recommend__) >= expect_book_amount:
                        break
            __similar_people__.pop()
        return __recommend__

    def __triple_check_listinlist__(self, tag, dict_1, dict_2):
        __one_dicted_list__ = dict_1[tag]
        __two_dicted_list__ = list()
        __three_dicted_list__ = list()
        for __item__ in __one_dicted_list__:
            __two_dicted_list__.extend(dict_2[__item__])
        del __one_dicted_list__
        __two_dicted_list__ = list(set(__two_dicted_list__))
        while tag in __two_dicted_list__:
            __two_dicted_list__.remove(tag)
        for __item__ in __two_dicted_list__:
            __three_dicted_list__.append(dict_1[__item__])
        del __two_dicted_list__
        return __three_dicted_list__

    def __double_check_list__(self, tag, dict1, dict2):
        __one_dicted_list__ = dict1[tag]
        __two_dicted_list__ = list()
        for __item__ in __one_dicted_list__:
            __two_dicted_list__.extend(dict2[__item__])
        while tag in __two_dicted_list__:
            __two_dicted_list__.remove(tag)
        return __two_dicted_list__

    def __derive_appearance_times_in_dict_from_list__(self, batch):
        count = dict()
        for __item__ in batch:
            if __item__ not in count:
                count[__item__] = 1
            else:
                count[__item__] += 1
        return count

    def __sort_list_by_appearance_time__(self, original_list, count_dict):
        """from smallest to largest"""
        # To improve this sorting in the future
        new_list = list()
        candidates = set(original_list)
        for __i__ in range(len(original_list)):
            for __can__ in count_dict:
                if count_dict[__can__] == __i__ + 1:
                    new_list.append(__can__)
                    candidates.remove(__can__)
        return new_list

    def book_based_simple_filtering(self, item_id, expected_book_number):
        __recommend__ = set()
        __similar_book__ = self.__double_check_list__(item_id,
                                                      self.book_person,
                                                      self.person_book)
        __similar_book__ = \
            self.__sort_list_by_appearance_time__(
                __similar_book__,
                self.__derive_appearance_times_in_dict_from_list__(__similar_book__)
            )
        while len(__similar_book__) > 0 and len(__recommend__) < expected_book_number:
            __recommend__.add(__similar_book__[-1])
            __similar_book__.pop()
        return __recommend__


if __name__ == '__main__':
    # ------------------------------
    logging.basicConfig(
        level=logging.DEBUG,  # 定义输出到文件的log级别，
        format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',  # 定义输出log的格式
        datefmt='%Y-%m-%d %A %H:%M:%S',  # 时间
    )
    # ------------------------------
    # Test CF
    # ------------------------------
