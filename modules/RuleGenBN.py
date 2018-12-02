# -*- encoding: UTF-8 -*-
from Config import DataConfig

from modules.RuleGen import RuleGenerator


class RuleGenBN(RuleGenerator):
    def __init__(self, data_path: str=DataConfig.data_path, operation_path: str=DataConfig.operation_path):
        RuleGenerator.__init__(self, data_path=data_path, operation_path=operation_path)


if __name__ == '__main__':
    pass
