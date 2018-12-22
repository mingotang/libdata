# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import os
import json
import datetime

from structures import Event, DataDict


class BaseEventStore(object):
    def __init__(self, folder_path: str, new: bool = False,):
        if not os.path.exists(folder_path):
            if new is False:
                raise RuntimeError('{} folder should be inited before loading').__format__(self.__class__.__name__)
            else:
                os.makedirs(folder_path)

        self.__path__ = folder_path

    def __write__(self, key: str, data_dict: DataDict):
        file_path = os.path.join(self.__path__, '{}.json'.format(key))
        if os.path.exists(file_path):
            raise FileExistsError(file_path)
        else:
            json.dump(
                [getattr(var, 'get_state_dict').__call__() for var in data_dict.values()],
                open(file_path, 'w', encoding='utf-8')
            )

    def __read__(self, key: str):
        file_path = os.path.join(self.__path__, '{}.json'.format(key))
        new_dict = DataDict(Event)
        if os.path.exists(file_path):
            event_list = json.load(open(file_path, 'r', encoding='utf-8'))
            for event in event_list:
                new_event = Event.set_state_dict(event)
                new_dict[new_event.hashable_key] = new_event
        else:
            pass
        return new_dict

    def store(self, *args):
        raise NotImplementedError

    def get(self, *args):
        raise NotImplementedError

    def iter(self, *args):
        raise NotImplementedError


class DateEventStore(BaseEventStore):

    def store(self, event_data: DataDict):
        group_by_date = event_data.group_by('event_date')
        for date, date_dict in group_by_date.items():
            self.__write__(date, date_dict)

    def get(self, start_date: datetime.date, end_date: datetime.date):
        if start_date > end_date:
            raise ValueError('end_date should lay behind start date')

        new_dict = DataDict(Event)
        this_date = start_date
        while this_date <= end_date:
            new_dict.update(self.__read__(this_date.strftime('%Y%m%d')))
            this_date += datetime.timedelta(days=1)
        return new_dict

    def iter(self, start_date: datetime.date, end_date: datetime.date):
        if start_date > end_date:
            raise ValueError('end_date should lay behind start date')

        this_date = start_date
        while this_date <= end_date:
            yield self.__read__(this_date.strftime('%Y%m%d'))
            this_date += datetime.timedelta(days=1)


class RegisterMonthEventStore(BaseEventStore):

    def store(self, event_data: DataDict):
        group_by_date = event_data.group_by('month_from_reader_register')
        for month, date_dict in group_by_date.items():
            self.__write__(str(month), date_dict)

    def get(self, month_range):
        new_dict = DataDict(Event)
        for d_dict in self.iter(month_range):
            new_dict.update(d_dict)
        return new_dict

    def iter(self, month_range):
        from collections import Iterable
        if isinstance(month_range, int):
            yield self.__read__(str(month_range))
        elif isinstance(month_range, Iterable):
            for month in month_range:
                yield self.__read__(str(month))
        else:
            raise TypeError


class BaseObjectStore(object):
    def __init__(self, folder_path: str, obj_type: type, new: bool = False, ):
        if not os.path.exists(folder_path):
            if new is False:
                raise RuntimeError('{} folder should be inited before loading').__format__(self.__class__.__name__)
            else:
                os.makedirs(folder_path)

        self.__path__ = folder_path
        self.__obj_type__ = obj_type

    def keys(self):
        for tag in os.listdir(self.__path__):
            if tag.endswith('.json'):
                yield tag.replace('.json', '')

    def __write__(self, key: str, obj):
        assert hasattr(obj, 'get_state_dict'), str(obj)
        assert len(key) > 0, str(obj)
        file_path = os.path.join(self.__path__, '{}.json'.format(key))
        if os.path.exists(file_path):
            raise FileExistsError(file_path)
        else:
            json.dump(getattr(obj, 'get_state_dict').__call__(), open(file_path, 'w', encoding='utf-8'))

    def __read__(self, key: str):
        file_path = os.path.join(self.__path__, '{}.json'.format(key))
        if os.path.exists(file_path):
            obj_dict = json.load(open(file_path, 'r', encoding='utf-8'))
            return getattr(self.__obj_type__, 'set_state_dict').__call__(obj_dict)
        else:
            raise KeyError('No such file {}'.format(file_path))

    def store(self, obj_data: DataDict):
        for obj in obj_data.values():
            assert hasattr(obj, 'hashable_key'), str(obj)
            if len(getattr(obj, 'hashable_key')) == 0:
                print(obj)
                continue
            self.__write__(getattr(obj, 'hashable_key'), obj)

    def get(self, key: str, default=None):
        try:
            return self.__read__(key)
        except KeyError:
            if default is None:
                raise KeyError
            else:
                return default

    def iter(self):
        for tag in self.keys():
            yield self.get(tag)
