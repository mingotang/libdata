# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------


class DataBaseConfig(object):
    file_path = '/Users/mingo/Downloads/Libdata.db'


class DataInfo(object):
    event_date_format = '%Y%m%d'
    raw_text_file_list = [
        '2016-11-16-guanyuan2013.txt',
        '2016-11-16-guanyuan2014.txt',
        '2016-11-16-guanyuan2015.txt',
    ]
    inner_tag_to_text_index_dict = {
        'sysID': 0,
        'libIndexID': 1,
        'bookname': 2,
        'isbn': 3,
        'author': 4,
        'publish_year': 5,
        'publisher': 6,
        'userID': 7,
        'event_date': 8,
        'event_type': 9,
        'user_type': 10,
        'collegeID': 11,
    }
    inner_tag_to_real_tag_dict = {
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
    event_index_to_real_tag_dict = {
        '50': '借书',
        '61': '还书',
        '62': '续借',
        '63': '续借2'
    }
    reader_index_to_real_tag_dict = {
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






