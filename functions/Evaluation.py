# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
from collections import Iterable, Sized


def top_n_accuracy(recommend_book_list, target_book_list, n: int):
    assert isinstance(recommend_book_list, Iterable) and isinstance(recommend_book_list, Sized)
    assert isinstance(target_book_list, Iterable) and isinstance(target_book_list, Sized)
    assert len(recommend_book_list) == len(target_book_list)

    hit_count = 0.0
    for index in range(len(recommend_book_list)):
        book_list = recommend_book_list[index]
        assert isinstance(book_list, list)
        assert len(book_list) >= n
        target = target_book_list[index]
        assert isinstance(target, str)
        if target in book_list[:n]:
            hit_count += 1.0
    return hit_count / len(recommend_book_list)

def coverage_accuracy(recommend_book_list, target_book_list):
    assert isinstance(recommend_book_list, Iterable) and isinstance(recommend_book_list, Sized)
    assert isinstance(target_book_list, Iterable) and isinstance(target_book_list, Sized)
    assert len(recommend_book_list) == len(target_book_list)

    accu_sum = 0.0
    for index in range(len(recommend_book_list)):
        book_list = recommend_book_list[index]
        assert isinstance(book_list, list)
        target_list = target_book_list[index]
        assert isinstance(target_list, list)
