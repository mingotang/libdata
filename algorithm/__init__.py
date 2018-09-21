# -*- encoding: UTF-8 -*-
from enum import Enum

from .Apriori import Apriori, BasketCollector, collect_baskets
from .CollaborativeFiltering import (
    CollaborativeFiltering,
    SlippingRangeCollaborativeFiltering,
    DateBackCollaborativeFiltering,
    SparseVectorCollector,
)
from utils.Maths import (
        CosineSimilarity, EuclideanSimilarity,
        PearsonCorrelationCoefficient, TanimotoCoefficient
    )


class AP_Type(Enum):
    Basic = 'ReaderIDAsBuyer_BookIDAsGoods'
    GroupByReaderCollege = 'ReaderIDAsBuyer_BookIDAsGoods-GroupByReaderCollege'


class CF_BaseType(Enum):
    ReaderBase = 'ReaderBase'
    BookBase = 'BookBase'


class CF_NeighborType(Enum):
    ThresholdBased = 'THRESHOLD'
    FixSize = 'K'
    All = 'ALL'


class CF_SimilarityType(Enum):
    Cosine = CosineSimilarity
    Euclidean = EuclideanSimilarity
    Pearson = PearsonCorrelationCoefficient
    Tanimoto = TanimotoCoefficient
