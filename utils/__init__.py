# -*- encoding: UTF-8 -*-
from .Logger import get_logger
from .Persisit import Pdict, Plist, PqueueFIFO, PqueueLIFO, Pset
from .ShelveWrapper import ShelveWrapper
from .SqliteWrapper import SqliteWrapper
from .UnicodeStr import UnicodeStr


def attributes_repr(inst):
    return "{}({})".format(
        inst.__class__.__name__,
        ', '.join([str(var) + ': ' + str(getattr(inst, var)) for var in inst.__attributes__])
    )


def slots_repr(inst):
    return "{}({})".format(
        inst.__class__.__name__,
        ', '.join([str(k) + ': ' + str(v) for k, v in slots(inst).items()])
    )


def slots(inst):
    result = dict()
    for slot in inst.__slots__:
        result[slot] = getattr(inst, slot)
    return result
