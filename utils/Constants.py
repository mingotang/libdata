# -*- encoding: UTF-8 -*-
from enum import Enum


class BaseEnum(Enum):
    def __repr__(self):
        return '{}.{}: {}'.format(self.__class__.__name__, self.name, self.value)

    @classmethod
    def to_str(cls):
        string = cls.__name__ + ': '
        string += ', '.join([var + ': ' + cls.__members__[var].value for var in cls.__members__])
        return string


inner_tag_chinese_map = {
    'sysID': '系统号',
    'libIndexID': '索书号',
    'bookname': '书名',
    'isbn': 'isbn号',
    'author': '作者',
    'publish_year': '出版年',
    'publisher': '出版社',
    'userID': '学工号',
    'event_date': '借书（还书、续借）发生日期',
    'event_type': '事件类型（借书、还书、续借）',
    'user_type': '读者身份类别',
    'collegeID': '学院代码',
}


event_type_chinese_map = {
    '50': '借书',
    '61': '还书',
    '62': '续借',
    '63': '续借2'
}


reader_type_chinese_map = {
    '11': '教授、副教授及各系列高级职称',
    '12': '教师、各系列中级职称',
    '13': '教职工、各系列初级职称',
    '14': '访问学者',
    '15': '离、退休职工',
    '21': '博士生',
    '22': '硕博连读生',
    '23': '硕士生',
    '24': '八年制本硕博连读生博士阶段',
    '25': '八年制本硕博连读生硕士阶段',
    '26': '七年制本硕连读生硕士阶段',
    '27': '六年制本硕连读生硕士阶段',
    '31': '四年制本科生',
    '32': '五年制本科生',
    '33': '六年制本硕连读生本科阶段',
    '34': '七年制本硕连读生本科阶段',
    '35': '八年制本硕博连读生本科阶段',
    '41': '校友卡读者',
    '42': '高职',
    '43': '二级学院及其他',
    '44': '校外普通读者',
    '45': '校外特殊读者',
    '51': '馆际互借',
    '52': '团体读者',
    '61': '研究生VIP1',
    '62': '研究生VIP2',
    '63': '研究生VIP3',
}


STAFF_TYPES = ('11', '12', '13', '14', '15')

UNDER_GRADUATE_TYPES = ('31', '32', '33', '34', '35')

GRADUATE_TYPES = ('21', '22', '23', '24', '25', '26', '27', '61', '62', '63')

NON_STUDENT_TYPES = ('41', '42', '42', '43', '44', '45', '51', '52')

NONE_INDIVIDUAL_TYPES = ('42', '43', '51', '52')

def get_individual_reader_types():
    indi_types = list()
    indi_types.extend(STAFF_TYPES)
    indi_types.extend(UNDER_GRADUATE_TYPES)
    indi_types.extend(GRADUATE_TYPES)
    indi_types.extend(['41', '42', '44', '45'])
    return indi_types
