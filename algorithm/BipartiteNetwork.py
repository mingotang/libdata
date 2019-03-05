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

    def __init__(self, con_list, max_item_occupy):
        from collections import Iterable
        from Environment import Environment
        from utils import get_logger
        assert isinstance(con_list, Iterable)
        assert isinstance(max_item_occupy, dict)
        self.log = get_logger(module_name=self.__class__.__name__)
        self.env = Environment.get_instance()

        self.con_list = ObjectList()
        for obj in con_list:
            if isinstance(obj, BipartiteNetworkBaseConnection):
                self.con_list.append(obj)
            else:
                raise NotImplementedError(type(obj))

        # 权重向量
        self.subject_weight = self.__init_base_weight__('subject')
        self.item_weight = self.__init_base_weight__('item')
        # 最大项目占用
        self.max_item_occupy = max_item_occupy
        # 初始化主体到项目的范围
        self.subject2item_dict = self.con_list.group_attr_set_by('item', 'subject')
        # 初始化项目到主体的连接
        self.item2subject_connection = self.__init_item2subject_weight__()

    def __init_base_weight__(self, tag: str):
        new_vector = SparseVector(len(self.con_list.collect_attr_set(tag)))
        count_d = CountingDict()
        for obj in self.con_list:
            assert isinstance(obj, BipartiteNetworkBaseConnection)
            count_d.count(getattr(obj, tag), obj.weight)
        new_vector.update(count_d)
        return new_vector

    def __init_item2subject_weight__(self):
        item2subject_connection = dict()
        for item_tag, sub_con_list in self.con_list.group_by_attr('item').items():
            count_d = CountingDict()
            for obj in sub_con_list:
                assert isinstance(obj, BipartiteNetworkBaseConnection)
                count_d.count(obj.subject, obj.weight)
            new_v = SparseVector(len(self.subject2item_dict))
            new_v.update(count_d)
            item2subject_connection[item_tag] = new_v
        return item2subject_connection

    # def __collect_max_book_occupy__(self):
    #     from collections import defaultdict
    #     max_occupy, now_occupy = defaultdict(int), defaultdict(int)
    #     for event_dict in self.env.data_proxy.event_store_by_date.iter(
    #             start_date=min(self.__event_dict__.collect_attr_set('date')),
    #             end_date=max(self.__event_dict__.collect_attr_set('date'))
    #     ):
    #         for event in event_dict.values():
    #             assert isinstance(event, Event)
    #             if event.event_type == '61':  # 还书
    #                 if now_occupy[event.book_id] > 0:
    #                     if max_occupy[event.book_id] < now_occupy[event.book_id]:
    #                         max_occupy[event.book_id] = now_occupy[event.book_id]
    #                     else:
    #                         pass
    #                     now_occupy[event.book_id] = now_occupy[event.book_id] - 1
    #                 else:
    #                     if max_occupy[event.book_id] < 1:
    #                         max_occupy[event.book_id] = 1
    #                     else:
    #                         pass
    #             else:
    #                 now_occupy[event.book_id] = now_occupy[event.book_id] + 1
    #                 if max_occupy[event.book_id] < now_occupy[event.book_id]:
    #                     max_occupy[event.book_id] = now_occupy[event.book_id]
    #                 else:
    #                     pass
    #     return max_occupy

    def run(self, subject_first: bool = True, item_check: float = 0.01, subject_check: float = 0.01):
        b_w, r_w = SparseVector(len(self.item_weight)), SparseVector(len(self.subject_weight))

        round_i = 0
        left_check, right_check = (self.item_weight - b_w).sum_squared, (self.subject_weight - r_w).sum_squared
        self.log.debug_running('round {}\tbook_check: {}, reader_check: {}'.format(round_i, left_check, right_check), )

        while left_check > item_check and right_check > subject_check:
            round_i += 1
            for book_id in self.item_weight.keys():
                b_w[book_id] = self.subject_weight * self.item2subject_connection[book_id]
            for reader_id in self.subject_weight.keys():
                r_w[reader_id] = sum([
                    (self.item_weight[var] / self.max_item_occupy[var]) for var in self.subject2item_dict[reader_id]
                ])
            self.item_weight, self.subject_weight = b_w * (1.0 / b_w.sum), r_w * (1.0 / r_w.sum)
            left_check, right_check = (self.item_weight - b_w).sum_squared, (self.subject_weight - r_w).sum_squared
            self.log.debug_running('round {}\tbook_check: {}'.format(round_i, left_check),
                                   'reader_check: {}'.format(right_check))
        if subject_first:
            return self.subject_weight, self.item_weight
        else:
            return self.item_weight, self.subject_weight


if __name__ == '__main__':
    import datetime
    from Environment import Environment
    env = Environment()

    bn = BipartiteNetwork(env.data_proxy.events.trim_between_range(
        'date', datetime.date(2013, 1, 1), datetime.date(2013, 2, 1)))
    bn.run(item_check=0.01, subject_check=0.01)
