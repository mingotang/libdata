# -*- encoding: UTF-8 -*-
import math

from structures import SparseVector


def EuclideanDistance(x, y):
    """欧几里德距离（Euclidean Distance）"""
    if isinstance(x, SparseVector) and isinstance(y, SparseVector):
        return (x - y).sum_squared
    else:
        raise NotImplementedError


def EuclideanSimilarity(x, y):
    if isinstance(x, SparseVector) and isinstance(y, SparseVector):
        return 1 / (1 + EuclideanDistance(x, y))
    else:
        raise NotImplementedError


def PearsonCorrelationCoefficient(x, y):
    """皮尔逊相关系数（Pearson Correlation Coefficient）"""
    if isinstance(x, SparseVector) and isinstance(y, SparseVector):
        n = len(x)
        return (x * y * n - x.sum * y.sum) / (
            math.sqrt(n * x.sum_squared - x.sum **2) * math.sqrt(n * y.sum_squared - y.sum **2)
        )
    else:
        raise NotImplementedError


def CosineSimilarity(x, y):
    """Cosine 相似度（Cosine Similarity）"""
    if isinstance(x, SparseVector) and isinstance(y, SparseVector):
        try:
            return x * y / (
                math.sqrt(x.sum_squared) * math.sqrt(y.sum_squared)
            )
        except ZeroDivisionError:
            return 0.0
    else:
        raise NotImplementedError


def TanimotoCoefficient(x, y):
    """Tanimoto 系数（Tanimoto Coefficient）"""
    if isinstance(x, SparseVector) and isinstance(y, SparseVector):
        return x * y / (
            math.sqrt(x.sum_squared) + math.sqrt(y.sum_squared) - x * y
        )
    else:
        raise NotImplementedError


if __name__ == '__main__':
    # ------------------------------
    pass

    # ------------------------------
