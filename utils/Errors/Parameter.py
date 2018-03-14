# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


class ParamTypeError(Exception):
    def __init__(self, param_name: str, param_target_type, param):
        self.name = param_name
        self.got_type = str(type(param))
        if isinstance(param_target_type, str):
            self.target_type = param_target_type
        elif isinstance(param_target_type, (list, tuple, set, frozenset)):
            target_type_list = list()
            for item in param_target_type:
                if isinstance(item, str):
                    target_type_list.append(item)
                else:
                    raise NotImplementedError()
            self.target_type = '/'.join(target_type_list)
        else:
            raise TypeError()

    def __repr__(self):
        return 'param {0:s} expect type {1:s} but got type {2:s}'.format(
            self.name, self.target_type, self.got_type,
        )


class ParamOutOfRangeError(Exception):
    def __init__(self, param_name: str, value_range: tuple, param):
        self.name = param_name
        self.range = value_range
        self.got_value = str(param)

    def __repr__(self):
        return 'param {0:s} range from {1} to {2} but got value {3:s}'.format(
            self.name, str(self.range[0]), str(self.range[1]), self.got_value,
        )


class ParamNoContentError(Exception):
    def __init__(self, param_name: str):
        self.name = param_name

    def __repr__(self):
        return 'param {0:s} gets no content'.format(self.name)


class ParamMissingError(Exception):
    def __init__(self, param_name: str):
        self.name = param_name

    def __repr__(self):
        return 'param {0:s} missing'.format(self.name)
