# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging
import os

from utils.Constants import BaseEnum
from utils.Logger import LogInfo


__i__ = logging.debug


# --------------------------------------------------------
class AprioriMethods(BaseEnum):
    Basic = 'ReaderIDAsBuyer_BookIDAsGoods'
    GroupByReaderCollege = 'ReaderIDAsBuyer_BookIDAsGoods-GroupByReaderCollege'


class CollaborativeFilteringMethods(BaseEnum):
    pass


# --------------------------------------------------------
def apply_apriori(method: AprioriMethods):
    """

    :param method:
    :return:
    """
    from Config import DataConfig
    from algorithm.Apriori import BasketCollector, Apriori
    from structures.Event import Event
    from utils.Persisit import Pdict
    if method == AprioriMethods.Basic:
        __i__(LogInfo.running('AprioriMethods.Basic', 'start'))

        events_dict = Pdict(os.path.join(DataConfig.persisted_data_path, 'events'), keep_history=True)

        __i__(LogInfo.running('collecting baskets', 'begin'))
        basket = BasketCollector()  # '/Users/mingo/Downloads/basket_dict'

        for event in events_dict.values():
            assert isinstance(event, Event)
            basket.add(event.reader_id, event.book_id)

        # basket = basket.to_dict()   # '/Users/mingo/Downloads/basket_dict'
        __i__(LogInfo.running('collecting baskets', 'end'))

        __i__(LogInfo.running('initiate apriori', 'begin'))
        apri_inst = Apriori(basket, force_origin=True)
        __i__(LogInfo.running('initiate apriori', 'end'))

        while True:
            min_conf = 0.2
            print('Apriori rules for min_conf={0:.2f}: '.format(min_conf))
            result = apri_inst.run(min_support=min_support)
            result.show_results(min_conf)
            # print('Result rules: ', result.show_results(min_conf))
            print('Max rules: {0:d}'.format(len(result.generate_rules(min_conf=0.0001))))
            config = input('Are you satisfied with the result above? (y/n)  ')
            if config.lower() == 'y':
                break
            elif config.lower() == 'n':
                # print(result.show_results())
                min_conf = float(input('Please input new min_conf:  '))
            else:
                break
                # min_conf = float(input('Please input new min_conf:  '))
    elif method == AprioriMethods.GroupByReaderCollege:
        pass
    else:
        raise NotImplementedError


def collaborative_filtering(base: str, max_length=20, **kwargs):
    """

    :param base: str, 'reader', 'book'
    :param kwargs: kwargs: Key: 'book', 'reader', 'events', 'chara_tag'
    :return:
    """
    pass


if __name__ == '__main__':
    from utils.Logger import set_logging
    set_logging()
    apply_apriori(AprioriMethods.Basic, min_support=0.1)
