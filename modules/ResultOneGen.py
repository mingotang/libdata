# -*- encoding: UTF-8 -*-
from algorithm import AprioriMethods, CollaborativeFilteringMethods, RecommendMethods
from modules.DataProxy import DataProxy


def generate_recommend_result(re_method: RecommendMethods, algo_method, ):
    assert isinstance(algo_method, (AprioriMethods, CollaborativeFilteringMethods))

    data_proxy = DataProxy()

    # cleaned data
    books = data_proxy.get_shelve('books')
    readers = data_proxy.get_shelve('readers')
    events = data_proxy.get_shelve('events')
    inducted_events = data_proxy.get_shelve('inducted_events')

    if re_method == RecommendMethods.CollaborativeFiltering:
        if algo_method == CollaborativeFilteringMethods.ReaderBase:
            pass
        elif algo_method == CollaborativeFilteringMethods.BookBase:
            pass
        else:
            raise RuntimeError
    elif re_method == RecommendMethods.Apriori:
        if algo_method == AprioriMethods.Basic:
            pass
        else:
            raise NotImplementedError
    else:
        raise RuntimeError
