# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging
import os

from tqdm import tqdm

from Config import DataConfig
from utils.Logger import LogInfo
from utils.Persisit import Pdict


def group_by(group_tag: str, by_tag: str, in_memory=True):
    """

    :param group_tag: 'readers'/'books'
    :param by_tag: related attribute
    :return: None
    """
    logging.debug(LogInfo.running('group {} by {}', 'begin'))

    pdata = Pdict(os.path.join(DataConfig.persisted_data_path, group_tag), keep_history=True)

    if in_memory is True:
        grouped_dict = dict()
    else:
        grouped_dict = Pdict(
            data_path=os.path.join(DataConfig.persisted_data_path, '{}_group_by_{}'.format(group_tag, by_tag)),
            keep_history=False,
        )

    for index in tqdm(pdata.keys(), desc='grouping {} by {}'.format(group_tag, by_tag)):
        obj = pdata[index]
        by_value = getattr(obj, by_tag)

        if by_value is None:
            continue

        if not isinstance(by_value, str):
            by_value = str(by_value)

        if len(by_value) == 0:  # jump to next iteration if no content
            continue

        if by_value not in grouped_dict:
            grouped_dict[by_value] = set()

        stored = grouped_dict[by_value]
        stored.add(index)
        grouped_dict[by_value] = stored

    if in_memory is True:
        Pdict.init_from(
            grouped_dict,
            data_path=os.path.join(DataConfig.persisted_data_path, '{}_group_by_{}'.format(group_tag, by_tag)),
            keep_history=False,
        )


if __name__ == '__main__':
    from utils.Logger import set_logging
    set_logging()

    group_by(group_tag='books', by_tag='author')
