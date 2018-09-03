# -*- encoding: UTF-8 -*-
from modules.DataProxy import DataProxy
from structures import Evaluator, RecoResult


def evaluate_cf_top_n_accuracy(result_path: str):
    result = RecoResult.load_csv(result_path)



    evaluator = Evaluator(actual_data=None, predicted_data=result)
