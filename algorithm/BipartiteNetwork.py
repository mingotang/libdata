# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
from structures import SparseVector
from structures import Event

from extended import CountingDict, ObjectList


class BipartiteNetworkBaseConnection(object):
    def __init__(self, subject: str, item: str, weight: float):
        self.subject = subject
        self.item = item
        self.weight = weight


class BipartiteNetwork(object):

    def __init__(self, con_list):
        from collections import Iterable
        from Environment import Environment
        from utils import get_logger
        assert isinstance(con_list, Iterable)
        self.log = get_logger(module_name=self.__class__.__name__)
        self.env = Environment.get_instance()

        self.con_list = ObjectList()
        for obj in con_list:
            if isinstance(obj, BipartiteNetworkBaseConnection):
                self.con_list.append(obj)
            else:
                raise NotImplementedError(type(obj))

        self.subject_weight = self.__init_weight__('subject')
        self.item_weight = self.__init_weight__('item')
        self.subject2item_dict = self.con_list.group_attr_set_by('item', 'subject')
        self.item2subject_connection = dict()

    def __init_weight__(self, tag: str):
        new_vector = SparseVector(len(self.con_list.collect_attr_set(tag)))
        count_d = CountingDict()
        for obj in self.con_list:
            assert isinstance(obj, BipartiteNetworkBaseConnection)
            count_d.count(getattr(obj, tag), obj.weight)
        new_vector.update(count_d)
        return new_vector

    def __collect_max_book_occupy__(self):
        from collections import defaultdict
        max_occupy, now_occupy = defaultdict(int), defaultdict(int)
        for event_dict in self.env.data_proxy.event_store_by_date.iter(
                start_date=min(self.__event_dict__.collect_attr_set('date')),
                end_date=max(self.__event_dict__.collect_attr_set('date'))
        ):
            for event in event_dict.values():
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

    def run(self, reader_weight_first: bool = True, book_check: float = 0.01, reader_check: float = 0.01):
        b_w, r_w = SparseVector(len(self.book_weight)), SparseVector(len(self.reader_weight))

        # self.__logger__.debug_running('init', 'repeat_times')
        repeat_times = dict()
        for book_id, book_event in tqdm(self.__event_dict__.group_by('book_id').items(), desc='init repeat_times'):
            # book_event = self.__event_dict__.trim_by_range('book_id', [book_id, ])
            repeat_times[book_id] = SparseVector(len(book_event.collect_attr_set('reader_id')))
            repeat_times[book_id].update(CountingDict.init_from(book_event.collect_attr_list('reader_id')))

        self.log.debug_running('init', 'book_count')
        book_count = self.__collect_max_book_occupy__()

        round_i = 0
        left_check, right_check = (self.book_weight - b_w).sum_squared, (self.reader_weight - r_w).sum_squared
        self.log.debug_running('round {}\tbook_check: {}'.format(round_i, left_check),
                               'reader_check: {}'.format(right_check))
        while left_check > book_check and right_check > reader_check:
            round_i += 1
            for book_id in self.book_weight.keys():
                b_w[book_id] = self.reader_weight * repeat_times[book_id]
            for reader_id in self.reader_weight.keys():
                r_w[reader_id] = sum([(self.book_weight[var] / book_count[var]) for var in self.subject2item[reader_id]])
            self.book_weight, self.reader_weight = b_w * (1.0 / b_w.sum), r_w * (1.0 / r_w.sum)
            # self.log.debug_running('round {} book weight'.format(round_i), str(self.book_weight))
            # self.log.debug_running('round {} reader weight'.format(round_i), str(self.reader_weight))
            left_check, right_check = (self.book_weight - b_w).sum_squared, (self.reader_weight - r_w).sum_squared
            self.log.debug_running('round {}\tbook_check: {}'.format(round_i, left_check),
                                   'reader_check: {}'.format(right_check))

        if reader_weight_first:
            return self.reader_weight, self.book_weight
        else:
            return self.book_weight, self.reader_weight


if __name__ == '__main__':
    import datetime
    from Environment import Environment
    env = Environment()

    bn = BipartiteNetwork(env.data_proxy.events.trim_between_range(
        'date', datetime.date(2013, 1, 1), datetime.date(2013, 2, 1)))
    bn.run(book_check=0.01, reader_check=0.01)
