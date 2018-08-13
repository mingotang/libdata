# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


class DataDict(dict):

    def __init__(self, *args, **kwargs):
        super(DataDict, self).__init__(*args, **kwargs)

    def to_dict(self):
        new_d = dict()
        for k, v in self.items():
            new_d[k] = v
        return new_d

    def trim(self, attr_tag: str, range_start, range_end,
             include_start: bool=True, include_end: bool=False):
        """
        删选合适的数据进入内存 -> dict
        :param attr_tag:
        :param range_start:
        :param range_end:
        :param include_start:
        :param include_end:
        :return: dict
        """
        result = dict()
        if range_start is None:
            for key, value in self.items():
                result[key] = value
        else:
            if include_start is True:
                for key, value in self.items():
                    if range_start <= getattr(value, attr_tag):
                        result[key] = value
            else:
                for key, value in self.items():
                    if range_start < getattr(value, attr_tag):
                        result[key] = value

        if range_end is not None:
            if include_end is True:
                for key in list(result.keys()):
                    value = result[key]
                    if getattr(value, attr_tag) > range_end:
                        result.pop(key)
            else:
                for key in list(result.keys()):
                    value = result[key]
                    if getattr(value, attr_tag) >= range_end:
                        result.pop(key)
        return result

    def group_by(self, by_tag: str):
        """
        把 data_dict 内容对象（group_tag）按照 by_tag 属性分组，得到 { by_tag: {obj1, obj2, }}
        :param by_tag: related attribute
        :return: dict( key: set())
        """
        grouped_dict = dict()

        for index in self.keys():
            obj = self.__getitem__(index)
            by_value = getattr(obj, by_tag)

            if by_value is None:
                continue

            if not isinstance(by_value, str):
                by_value = str(by_value)

            if len(by_value) == 0:  # jump to next iteration if no content
                continue

            if by_value not in grouped_dict:
                grouped_dict[by_value] = set()

            stored_set = grouped_dict[by_value]
            stored_set.add(index)
            grouped_dict[by_value] = stored_set

        return grouped_dict
