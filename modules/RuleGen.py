# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import datetime

from Config import DataConfig


class RuleGenerator(object):
    def __init__(self, data_path: str=DataConfig.data_path, operation_path: str=DataConfig.operation_path):
        from modules.DataProxy import DataProxy
        from structures import TextRecorder
        from utils import get_logger
        self.__logger__ = get_logger(self.__class__.__name__)

        self.__data_path__ = data_path
        self.__operation_path__ = operation_path

        self.__recorder__ = TextRecorder()

        self.__data_proxy__ = DataProxy(data_path=self.__data_path__)

    def __load_result__(self, result_data):
        import os
        from structures import RecoResult

        if isinstance(result_data, str):
            result_data = os.path.join(DataConfig.operation_path, result_data)
            result = RecoResult.load_csv(result_data)
        elif isinstance(result_data, RecoResult):
            result = result_data
        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('result_data', (str, RecoResult), result_data)

        return result

    def evaluate_result_similarity(self, result_01, result_02, top_n: int=10, descrip: str=''):
        from structures import Evaluator
        result_01 = self.__load_result__(result_01).derive_top(top_n)
        result_02 = self.__load_result__(result_02).derive_top(top_n)
        evaluator = Evaluator(result_01, result_02)
        eva_res = list()
        if descrip != '':
            eva_res.append(['Evaluation result - {} with top {}'.format(descrip, top_n), ])
        else:
            eva_res.append(['Evaluation result with top {}'.format(top_n), ])
        eva_res.append(['percentage', evaluator.match_percentage])
        print('coverage', evaluator.coverage)
        print('top_10_accuracy', evaluator.top_n_accuracy(10))
        print('top_100_accuracy', evaluator.top_n_accuracy(100))
        print('recall_accuracy', evaluator.recall_accuracy(10, 100))
        print('precision_accuracy', evaluator.precision_accuracy(10, 100))
        print('f', evaluator.f_value(10, 100))
        print('front_10_top_100_accuracy', evaluator.front_i_top_n_accuracy(10, 100))
        print('front_100_top_100_accuracy', evaluator.front_i_top_n_accuracy(100, 100))

    def evaluate_single_result(self, result_data, time_range, top_n: int=10):
        from structures import Evaluator, TimeRange
        assert isinstance(time_range, TimeRange)

        result = self.__load_result__(result_data).derive_top(top_n)

        actual_data = dict()
        inducted_events = self.__data_proxy__.inducted_events.to_dict()
        for reco_key, events_list in inducted_events.items():
            from structures import OrderedList
            assert isinstance(events_list, OrderedList)
            events_list = events_list.trim_between_range(
                'date', time_range.end_time.date(), time_range.end_time.date() + datetime.timedelta(days=30)
            ).to_attr_list('book_id')
            actual_data[reco_key] = events_list

        evaluator = Evaluator(actual_data=actual_data, predicted_data=result)
        print('size', len(result))
        print('match percentage', evaluator.match_percentage)
        print('coverage', evaluator.coverage(
            len(self.__data_proxy__.events.trim_between_range(
                'date', time_range.start_time.date(), time_range.end_time.date()).count_attr('book_id'))))
        print('top_10_accuracy', evaluator.top_n_accuracy(10))
        # print('top_100_accuracy', evaluator.top_n_accuracy(100))
        print('recall_accuracy', evaluator.recall_accuracy(20, 100))
        print('precision_accuracy', evaluator.precision_accuracy(20, 100))
        print('f', evaluator.f_value(20, 100))
        print('front_10_top_100_accuracy', evaluator.front_i_top_n_accuracy(20, 100))
        # print('front_100_top_100_accuracy', evaluator.front_i_top_n_accuracy(100, 100))

    def merge_result(self, result_01, result_02, top_n: int=10):
        from structures import RecoResult
        result_01 = self.__load_result__(result_01).derive_top(top_n)
        result_02 = self.__load_result__(result_02).derive_top(top_n)
        result = RecoResult()
        tag_set = set(list(result_01.keys()))
        tag_set.update(set(list(result_02.keys())))
        for tag in tag_set:
            if tag not in result_01:
                r_list = result_02[tag]
            elif tag not in result_02:
                r_list = result_01[tag]
            else:
                r_list = result_01[tag]
                for book in result_02[tag]:
                    if book not in r_list:
                        r_list.append(book)
            result.add_list(tag, r_list)
        return result

    @property
    def log(self):
        return self.__logger__

    def close(self):
        self.__data_proxy__.close()


if __name__ == '__main__':
    import datetime
    from algorithm import CF_NeighborType, CF_SimilarityType

    rule_generator = RuleGenerator()
    rule_generator.log.initiate_time_counter()

    try:
        pass
        # running StandardTimeRange
        # this_time_range = StandardTimeRange(start_time=datetime.date(2013, 1, 1), end_time=datetime.date(2013, 7, 1))

        # running GrowthTimeRange
        # this_time_range = GrowthTimeRange(start_time=datetime.date(2013, 1, 1), end_time=datetime.date(2013, 7, 1))
        # this_time_range.set_growth_stage('growth_index', [(0, 1), (1, 2), (2, 3), (3, 4), (4, 6), (6, 100)])

        # running DateBackTimeRange
        # this_time_range = DateBackTimeRange(datetime.date(2013, 1, 1), datetime.date(2013, 7, 1),
        #                                     datetime.date(2013, 3, 1))

        # this_re = rule_generator.apply_collaborative_filtering(
        #     CF_SimilarityType.Euclidean, CF_NeighborType.All, this_time_range,)

        # this_re = rule_generator.apply_slipped_collaborative_filtering(
        #     CF_SimilarityType.Cosine, CF_NeighborType.All, this_time_range,)

        # this_re = rule_generator.apply_refered_slipped_collaborative_filtering(
        #     CF_SimilarityType.Cosine, CF_NeighborType.All, this_time_range,)

        # this_re = rule_generator.apply_date_back_collaborative_filtering(
        #     CF_SimilarityType.Cosine, CF_NeighborType.All, this_time_range,)

        # this_re = rule_generator.merge_result('2013-06 growth weighted simple.csv', '2013-06 slipped.csv', top_n=10)

        # print(' --- [real time] ---')
        # rule_generator.evaluate_single_result(result_data=this_re, time_range=this_time_range, top_n=20)

        # print('--- [similarity] ---')
        # rule_generator.evaluate_result_similarity(
        #     '2013-06 simple.csv',
        #     '2013-06 date back.csv', )

        # rule_generator.evaluate_single_result(
        #     result_data='cf_result_20181017_163617.csv',
        #     time_range=this_time_range, top_n=10)

        # print('--- [growth timerange] ---')
        # rule_generator.evaluate_single_result(
        #     result_data='2013-2014 slipped CF.csv',
        #     time_range=this_time_range, )

        # print('--- [date back timerange] ---')
        # rule_generator.evaluate_single_result(
        #     result_data='/Users/mingo/Downloads/persisted_libdata/this_operation/cf_result_20180920_193451.csv',
        #     time_range=this_time_range
        # )

    except KeyboardInterrupt:
        rule_generator.close()
    finally:
        rule_generator.close()

    rule_generator.log.time_sleep(1)
    rule_generator.log.print_time_passed()
