# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------

from structures import CountingDict, DataDict, SparseVector
from structures import Event


class BipartiteNetwork(object):

    def __init__(self, event_dict, in_memory: bool = True):
        from structures import ShelveWrapper
        from utils import get_logger
        self.__logger__ = get_logger(module_name=self.__class__.__name__)

        if in_memory is True:
            if isinstance(event_dict, DataDict):
                self.__event_dict__ = event_dict
            elif isinstance(event_dict, (dict, ShelveWrapper)):
                self.__event_dict__ = DataDict.init_from(Event, event_dict)
            else:
                from utils.Exceptions import ParamTypeError
                raise ParamTypeError('event_dict', 'dict/ShelveWrapper/DataDict', event_dict)
        else:
            raise NotImplementedError

        self.__logger__.debug_running('init', 'book_weight/reader_weight')
        self.book_weight = self.__init_weight__('book_id')    # 书籍权重
        self.reader_weight = self.__init_weight__('reader_id')    # 读者权重
        # self.__calculated_bw__ = SparseVector()    # 计算书籍权重
        # self.__calculated_rw__ = SparseVector()     # 计算读者权重

    def __init_weight__(self, tag: str):
        if isinstance(self.__event_dict__, DataDict):
            data_dict = self.__event_dict__
        else:
            data_dict = DataDict.init_from(Event, self.__event_dict__)
        new_vector = SparseVector(len(data_dict.collect_attr_set(tag)))
        new_vector.update(CountingDict.init_from(data_dict.collect_attr_list(tag)))
        return new_vector

    def __collect_max_book_occupy__(self):
        from collections import defaultdict
        from structures import OrderedList
        ordered_events = OrderedList(Event, 'date')
        ordered_events.extend(list(self.__event_dict__.values()))
        max_occupy, now_occupy = defaultdict(int), defaultdict(int)
        for event in ordered_events:
            assert isinstance(event, Event)
            if event.event_type == '61':  # 还书
                if now_occupy[event.book_id] > 0:
                    if max_occupy[event.book_id] < now_occupy[event.book_id]:
                        max_occupy[event.book_id] = now_occupy[event.book_id]
                    else:
                        pass
                    now_occupy[event.book_id] = now_occupy[event.book_id] - 1
                else:
                    if max_occupy[event.book_id] < 1:
                        max_occupy[event.book_id] = 1
                    else:
                        pass
            else:
                now_occupy[event.book_id] = now_occupy[event.book_id] + 1
                if max_occupy[event.book_id] < now_occupy[event.book_id]:
                    max_occupy[event.book_id] = now_occupy[event.book_id]
                else:
                    pass
        return max_occupy

    def run(self, reader_weight_first: bool = True):
        if isinstance(self.__event_dict__, DataDict):
            b_w, r_w = SparseVector(len(self.book_weight)), SparseVector(len(self.reader_weight))
        else:
            raise NotImplementedError

        self.__logger__.debug_running('init', 'repeat_times')
        repeat_times = dict()
        for book_id in self.book_weight.keys():
            book_event = self.__event_dict__.trim_by_range('book_id', [book_id, ])
            repeat_times[book_id] = SparseVector(len(book_event.collect_attr_set('reader_id')))
            repeat_times[book_id].update(CountingDict.init_from(book_event.collect_attr_list('reader_id')))

        self.__logger__.debug_running('init', 'book_count')
        book_count = self.__collect_max_book_occupy__()

        self.__logger__.debug_running('init', 'reader2book')
        reader2book = self.__event_dict__.group_attr_set_by('book_id', 'reader_id')

        round = 1
        while (self.book_weight - b_w).sum_squared < 0.1 and (self.reader_weight - r_w).sum_squared < 0.1:
            for book_id in self.book_weight.keys():
                b_w[book_id] = self.reader_weight * repeat_times[book_id]
            for reader_id in self.reader_weight.keys():
                r_w[reader_id] = sum([(self.book_weight[var] / book_count) for var in reader2book[reader_id]])
            self.book_weight, self.reader_weight = b_w * 1 / b_w.sum, r_w * 1 / r_w.sum
            self.__logger__.debug_running('round {} book weight'.format(round), self.book_weight)
            self.__logger__.debug_running('round {} reader weight'.format(round), self.reader_weight)
            round += 1

        if reader_weight_first:
            return self.reader_weight, self.book_weight
        else:
            return self.book_weight, self.reader_weight


if __name__ == '__main__':
    import datetime
    from Environment import Environment
    from modules.DataProxy import DataProxy
    env = Environment()
    env.set_data_proxy(DataProxy())

    bn = BipartiteNetwork(env.data_proxy.events.trim_between_range(
        'date', datetime.date(2013, 1, 1), datetime.date(2013, 2, 1)))
    bn.run()
