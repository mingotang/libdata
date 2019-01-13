class ShelveObjectDict(ShelveWrapper):
    def __init__(self, db_path: str, obj_type: type, writeback: bool = False, new: bool = False):
        ShelveWrapper.__init__(self, db_path=db_path, writeback=writeback, new=new)
        self.__obj_type__ = obj_type

    def __setitem__(self, key: str, value):
        assert isinstance(value, self.__obj_type__), type(value)
        self.__db__[key] = getattr(value, 'get_state_str').__call__()
        self.__closed__ = False

    def __getitem__(self, key: str):
        return getattr(self.__obj_type__, 'set_state_str').__call__(self.__db__[key])

    def to_data_dict(self, key_range=None):
        from extended import DataDict
        new_d = DataDict()
        keys = list(self.keys()) if key_range is None else key_range
        for key in keys:
            new_d[key] = self.__getitem__(key)
        return new_d
