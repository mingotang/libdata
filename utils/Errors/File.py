# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
from enum import Enum


class FileTypeError(Exception):
    def __init__(self, file_path: str, target_type):
        # get wrong file_type
        if '.' in file_path:
            self.file_type = file_path.split('.')[-1]
        else:
            self.file_type = str(type(None))
        # get file path
        self.file_path = file_path
        # get target path
        if isinstance(target_type, str):
            self.target_type = target_type
        elif isinstance(target_type, Enum):
            self.target_type = target_type.value
        else:
            raise TypeError()

    def __repr__(self):
        return 'file {0:s} expect type {1:s} but got type {2:s}'.format(
            self.file_path, self.target_type, self.file_type,
        )
