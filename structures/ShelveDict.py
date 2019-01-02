# -*- encoding: UTF-8 -*-
import os
import shelve

from collections import Mapping, Sized


class ShelveWrapper(Mapping, Sized):

    def __init__(self, db_path: str, writeback: bool = False, new: bool = False):
        from utils import get_logger
        Mapping.__init__(self)
        self.log = get_logger(self.__class__.__name__)
        self.__closed__ = False   # tag whether db is closed

        if '.' in db_path:
            if db_path.split('.')[-1] == 'db':
                self.__path__ = db_path
            else:
                self.__path__ = '.'.join([db_path, 'db'])

        else:
            self.__path__ = '.'.join([db_path, 'db'])

        if os.path.exists(self.__path__):
            if new is True:
                os.remove(self.__path__)
            self.__db__ = shelve.open(self.__path__, writeback=writeback, protocol=None)
        else:
            if new is False:
                raise FileNotFoundError(self.__path__)
            self.__db__ = shelve.open(self.__path__, writeback=writeback, protocol=None)

        self.log.info('Connected to shelve database {}'.format(self.__path__))

    @classmethod
    def init_from(cls, data, db_path: str, writeback=False):
        if data is None:
            new_db = cls(db_path=db_path, writeback=writeback, new=True)
        elif isinstance(data, Mapping):
            new_db = cls(db_path=db_path, writeback=writeback, new=True)
            for k, v in data.items():
                new_db[k] = v
        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('data', 'Mapping/NoneType', data)
        return new_db

    @classmethod
    def connect(cls, db_path: str, writeback=False):
        return cls(db_path=db_path, writeback=writeback)

    def __iter__(self):
        for key in self.keys():
            yield key

    def __getitem__(self, key: str):
        return self.__db__[key]

    def __setitem__(self, key: str, value):
        self.__db__[key] = value
        self.__closed__ = False

    def __contains__(self, key: str):
        return self.__db__.__contains__(key)

    def __delitem__(self, key):
        del self.__db__[key]
        self.__closed__ = False

    def __len__(self):
        return self.__db__.__len__()

    def keys(self):
        return self.__db__.keys()

    def values(self):
        for key in self.keys():
            yield self.__getitem__(key)

    def items(self):
        for key in self.keys():
            yield key, self.__getitem__(key)

    def set(self, key: str, value):
        self.__setitem__(key, value)

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def flush(self):
        self.__db__.sync()
        self.__closed__ = False

    def clear(self):
        self.__db__.clear()
        self.__closed__ = False
        self.log.debug('shelve database {} cleared.'.format(self.__path__))

    def close(self):
        self.__db__.close()
        self.__closed__ = True
        self.log.debug('shelve database {} closed.'.format(self.__path__))

    def delete(self):
        from os import remove
        self.__db__.clear()
        self.__db__.close()
        self.__closed__ = True
        remove(self.__path__)

    @property
    def is_active(self):
        return not self.__closed__

    def to_dict(self, key_range=None):
        new_d = dict()
        if key_range is None:
            for key, value in self.items():
                new_d[key] = value
        else:
            for key, value in self.items():
                if key in key_range:
                    new_d[key] = value
        return new_d

    def convert_to_data_dict(self, new_type, key_range=None):
        from structures import DataDict
        new_d = DataDict()
        if key_range is None:
            for key, value in self.items():
                new_d[key] = new_type.set_state_str(value)
        else:
            for key, value in self.items():
                if key in key_range:
                    new_d[key] = new_type.set_state_str(value)
        return new_d

    def update(self, data):
        from collections import Mapping
        if isinstance(data, Mapping):
            for key, value in data.items():
                self.__setitem__(key, value)
        else:
            from utils.Exceptions import ParamTypeError
            raise ParamTypeError('data', 'Mapping', data)


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
        from structures import DataDict
        new_d = DataDict()
        keys = list(self.keys()) if key_range is None else key_range
        for key in keys:
            new_d[key] = self.__getitem__(key)
        return new_d


if __name__ == '__main__':
    shelve_db = ShelveWrapper('/Users/mingo/Downloads/persisted_libdata/test.db')
    shelve_db.log.debug('status: {}'.format(shelve_db.is_active))
    shelve_db.close()
