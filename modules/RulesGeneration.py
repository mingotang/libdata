# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import pandas as pd

from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

from modules.DataManagement import BookManager
from modules.DataManagement import ReaderManager
from modules.DataManagement import ReadersEventManager


# --------------------------------------------------------
class LibAssociationRulesGeneration(object):

    @staticmethod
    def apriori(manager, basket: str, item: str):
        if type(manager) == BookManager:
            pass
        elif type(manager) == ReaderManager:
            pass
        elif type(manager) == ReadersEventManager:
            pass
        else:
            raise ValueError(
                'LibAssociationRulesGeneration.apriori: manager is not legal'
            )

    @staticmethod
    def collaborative_filtering(base: str, **kwargs):
        if base == 'reader2reader':
            if 'reader_events_dict' in kwargs:
                pass
            else:
                raise ValueError(
                    'LibAssociationRulesGeneration.collaborative_filtering: missing param reader_events_dict'
                )
        elif base == 'book2book':
            if 'reader_events_dict' in kwargs:
                pass
            else:
                raise ValueError(
                    'LibAssociationRulesGeneration.collaborative_filtering: missing param reader_events_dict'
                )
        else:
            raise ValueError(
                'LibAssociationRulesGeneration.collaborative_filtering: base {0:s} is not legal'.format(base)
            )


# --------------------------------------------------------


if __name__ == '__main__':
    import time
    start_time = time.time()
    # ------------------------------
    LibAssociationRulesGeneration.apriori(base='c')
    df = pd.read_excel('http://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx')
    # print(df.head())
    df['Description'] = df['Description'].str.strip()
    df.dropna(axis=0, subset=['InvoiceNo'], inplace=True)
    df['InvoiceNo'] = df['InvoiceNo'].astype('str')
    df = df[~df['InvoiceNo'].str.contains('C')]
    basket = (df[df['Country'] == "France"]
              .groupby(['InvoiceNo', 'Description'])['Quantity']
              .sum().unstack().reset_index().fillna(0)
              .set_index('InvoiceNo'))
    print(basket)
    def encode_units(x):
        if x <= 0:
            return 0
        if x >= 1:
            return 1
    basket_sets = basket.applymap(encode_units)
    basket_sets.drop('POSTAGE', inplace=True, axis=1)
    frequent_itemsets = apriori(basket_sets, min_support=0.07, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)
    # print(rules.head())
    # rules[(rules['lift'] >= 6) & (rules['confidence'] >= 0.8)]

    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration)//3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.2f} s'.format(hour, minutes, seconds))
