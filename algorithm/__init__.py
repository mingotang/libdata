# -*- encoding: UTF-8 -*-
from enum import Enum


class AprioriMethods(Enum):
    Basic = 'ReaderIDAsBuyer_BookIDAsGoods'
    GroupByReaderCollege = 'ReaderIDAsBuyer_BookIDAsGoods-GroupByReaderCollege'


class CollaborativeFilteringMethods(Enum):
    ReaderBase = 'ReaderBase'
    BookBase = 'BookBase'


class RecommendMethods(Enum):
    Apriori = AprioriMethods
    CollaborativeFiltering = CollaborativeFilteringMethods
