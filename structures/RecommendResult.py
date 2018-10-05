# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


class RecoResult(dict):
    def __init__(self):
        dict.__init__(self)

    def add(self, *args, **kwargs):
        self.add_list(*args, **kwargs)

    def add_list(self, key: str, value: list):
        if self.__contains__(key):
            raise KeyError
        else:
            self.__setitem__(key, value)

    def derive_top(self, n: int=1):
        if n < 1:
            from utils.Exceptions import ParamOutOfRangeError
            raise ParamOutOfRangeError('n', (1, 'inf'), n)
        assert n >= 1

        result = RecoResult()
        for key, value in self.items():
            if len(value) >= n:
                result.add_list(key, value[:n])
            else:
                result.add_list(key, value)

        return result

    def to_csv(self, folder_path: str=None):
        import os
        import datetime
        from Config import DataConfig
        file_name = 'cf_result_{}.csv'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        if folder_path is None:
            target_path = os.path.join(DataConfig.operation_path, file_name)
        else:
            if os.path.exists(folder_path) is False:
                os.makedirs(folder_path)
            target_path = os.path.join(folder_path, file_name)
        with open(target_path, 'w', encoding='utf-8') as file:
            for key, value in self.items():
                file.write(key)
                file.write(',')
                file.write(','.join(value))
                file.write('\n')
        file.close()

    @classmethod
    def load_csv(cls, csv_path: str, encoding: str='utf-8'):
        import os
        if not os.path.exists(csv_path):
            raise FileNotFoundError(csv_path)
        result = cls()
        file = open(csv_path, 'r', encoding=encoding)
        content = file.readlines()
        # assert isinstance(content, str)
        # content = content.split('\n')
        for line in content:
            line = line.split(',')
            if len(line) > 1:
                result[line[0]] = line[1:]
            else:
                result[line[0]] = list()
        return result
