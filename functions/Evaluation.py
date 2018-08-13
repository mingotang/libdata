# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
from collections import Iterable, Sized


def top_n_accuracy(recommend_list, target_list, n: int):
    """评价单个预测结果落在前n个实际结果中的比例 -> float"""
    assert isinstance(recommend_list, Iterable) and isinstance(recommend_list, Sized)
    assert isinstance(target_list, Iterable) and isinstance(target_list, Sized)
    assert len(recommend_list) == len(target_list)

    hit_count = 0.0
    for index in range(len(recommend_list)):
        book_list = recommend_list[index]
        assert isinstance(book_list, (list, set))
        # assert len(book_list) >= n
        target = target_list[index]
        # assert isinstance(target, str)
        if len(book_list) >= n:
            if target in book_list[:n]:
                hit_count += 1.0
        elif len(book_list) == 0:
            # 未来需要考虑没有验证数据的该怎么办
            pass
        else:
            if target in book_list:
                hit_count += 1.0
    return hit_count / len(recommend_list)

def coverage_accuracy(recommend_list, target_list):
    """评价若干个预测结果可以覆盖多少比例的实际结果 -> float"""
    assert isinstance(recommend_list, Iterable) and isinstance(recommend_list, Sized)
    assert isinstance(target_list, Iterable) and isinstance(target_list, Sized)
    assert len(recommend_list) == len(target_list)

    accu_sum = 0.0
    for index in range(len(recommend_list)):
        book_list = recommend_list[index]
        assert isinstance(book_list, list)
        target_list = target_list[index]
        assert isinstance(target_list, list)

    raise NotImplementedError
