# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


class BaseObject(object):
    __attributes__ = tuple()

    def __repr__(self):
        return '\t'.join([(var + ': ' + str(self.__getattribute__(var))) for var in self.__attributes__])

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        else:
            for tag in self.__attributes__:
                if self.__getattribute__(tag) != other.__getattribute__(tag):
                    return False
            return True

    def update(self, other):
        for tag in self.__attributes__:
            if len(self.__dict__[tag]) < len(other.__dict__[tag]):
                self.__dict__[tag] = other.__dict__[tag]
