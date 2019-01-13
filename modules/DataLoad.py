# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import re
import os

from utils.Constants import event_type_chinese_map


class DataObject(dict):
    list_index_to_inner_tag_dict = {
        0: 'sysID',
        1: 'libIndexID',
        2: 'bookname',
        3: 'isbn',
        4: 'author',
        5: 'publish_year',
        6: 'publisher',
        7: 'userID',
        8: 'event_date',
        9: 'event_type',
        10: 'user_type',
        11: 'collegeID',
    }

    def __init__(self, from_list: list):
        dict.__init__(self)
        for index, inner_tag in self.list_index_to_inner_tag_dict.items():
            self[inner_tag] = from_list[index]

        # data cleaning
        self['sysID'] = re.sub(r'\W', '', self['sysID'])
        self['userID'] = re.sub(r'\W', '', self['userID'].upper())


class RawDataProcessor(object):

    @staticmethod
    def derive_raw_data(splitter='@', text_encoding='gb18030', ):
        from Environment import Environment
        config = Environment.get_instance().config.get('Resources')
        # logger.debug_running('derive_raw_data', 'checking file')

        data_list = list()
        for file_name in config.get('RawDataList'):
            # logger.debug_running('derive_raw_data', 'reading file {0}'.format(str(file_name)))
            data_file = open(os.path.join(config.get('RawDataPath'), file_name), 'r', encoding=text_encoding)

            text_line = data_file.readline()
            __temp_list__ = list()
            while text_line:
                line_content = text_line.split(splitter)
                line_content.pop()
                line_content = RawDataProcessor.__raw_data_line_clean__(line_content, __temp_list__)
                if RawDataProcessor.__check_data_line__(line_content):
                    data_object = DataObject(line_content)
                    data_list.append(data_object)
                elif len(line_content) == 0:
                    # logger.debug('RawDataProcessor: empty line')
                    pass
                else:
                    # logger.warning("Unqualified data :  {0:s}".format(str(line_content)))
                    pass
                text_line = data_file.readline()
        return data_list

    @staticmethod
    def iter_data_object(splitter='@', text_encoding='gb18030', ):
        from Environment import Environment
        config = Environment.get_instance().config.get('Resources')
        # logger.debug_running('derive_raw_data', 'checking file')

        # data_list = list()
        for file_name in config.get('RawDataList'):
            # logger.debug_running('derive_raw_data', 'reading file {0}'.format(str(file_name)))
            data_file = open(os.path.join(config.get('RawDataPath'), file_name), 'r', encoding=text_encoding)

            text_line = data_file.readline()
            __temp_list__ = list()
            while text_line:
                line_content = text_line.split(splitter)
                line_content.pop()
                line_content = RawDataProcessor.__raw_data_line_clean__(line_content, __temp_list__)
                if RawDataProcessor.__check_data_line__(line_content):
                    data_object = DataObject(line_content)
                    yield data_object
                elif len(line_content) == 0:
                    pass
                    # logger.debug('RawDataProcessor: empty line')
                else:
                    raise RuntimeError("Unqualified data :  {0:s}".format(str(line_content)))
                    # logger.warning("Unqualified data :  {0:s}".format(str(line_content)))
                text_line = data_file.readline()

    @staticmethod
    def __check_data_line__(content: list):
        if len(content) != len(DataObject.list_index_to_inner_tag_dict):  # 数量长度必须和预设相同
            return False
        else:
            if not re.search(r'[12][890123]\d\d[01]\d[0123]\d', content[8]):  # event_date 必须遵循 YYYYmmdd格式
                return False
            else:
                if content[9] not in event_type_chinese_map:  # event_type 必须在预定范围内
                    return False
                else:
                    return True

    @staticmethod
    def __raw_data_line_clean__(content: list, __temp_list__: list):
        if len(content) < 12:
            if len(__temp_list__) > 0:
                __temp_list__.extend(content)
                temp_list = RawDataProcessor.__raw_data_line_clean__(__temp_list__, __temp_list__)
                if len(temp_list) > 0:
                    __temp_list__.clear()
                    return temp_list
                else:
                    __temp_list__.clear()
                    print('Unqualified data : {0:s}'.format(str(temp_list)))
                    return list()
            else:
                __temp_list__.extend(content)
                return list()
        else:
            cont = list()
            cont.extend(content)
            __temp_list__.clear()
            if cont[9] in event_type_chinese_map:
                return cont
            elif cont[10] in event_type_chinese_map:
                if len(cont[4]) == 17:
                    cont[2] = cont[2] + cont[3]
                    del cont[3]
                    return cont
                    # print(content)
                elif len(cont[3]) == 17:
                    cont[4] = cont[4] + cont[5]
                    del cont[5]
                    return cont
                    # print(content)
                else:
                    print('Unqualified data : {0:s}'.format(str(cont)))
                    return list()
            else:
                print('Unqualified data : {0:s}'.format(str(cont)))
                return list()


def convert_pdf_2_text(path: str):
    from io import StringIO
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfpage import PDFPage
    retstr = StringIO()
    rsrcmgr = PDFResourceManager()
    device = TextConverter(rsrcmgr, retstr, codec='utf-8', laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    with open(path, 'rb') as fp:
        for page in PDFPage.get_pages(fp, set()):
            interpreter.process_page(page)
        text = retstr.getvalue()
    device.close()
    retstr.close()
    text_line = text.split('\n')
    for line_no, line in enumerate(text_line):
        print(line_no, line)
    return text


def compare_string(left: str, right: str):
    if len(left) == 0 or len(right) == 0:
        raise RuntimeWarning
    count = 0
    for item in left:
        if item in right:
            count += 1
    return count * count / (len(left) * len(right))


def load_listst_one():
    """2014新生专题书架-207种"""
    from Environment import Environment
    from extended import CountingDict
    from structures import Book
    from utils import save_csv
    env = Environment()
    content = convert_pdf_2_text('/Users/mingo/Nutstore Files/我的坚果云/清华大学图书馆-系列书单推荐/2014新生专题书架-207种.pdf')
    book_index_list = list()
    content_to_be_processed = list()
    content_to_be_processed.append(('book_name', 'possible'))
    for line in content.split('\n'):
        if len(line.replace(' ', '')) == 0:
            continue
        counter = CountingDict()
        for book in env.data_proxy.books.values():
            assert isinstance(book, Book)
            if len(book.name) == 0:
                continue
            counter.__setitem__(book.index, compare_string(line, book.name))
        counter.trim(lower_limit=0.9)
        if len(counter) == 1:
            book_index_list.append(list(counter.keys())[0])
        elif len(counter) == 0:
            continue
        else:
            content_to_be_processed.append((line, ''))
            for b_i in counter.sort(inverse=True):
                content_to_be_processed.append(('', str(env.data_proxy.books[b_i])))
                # print(b_i, env.data_proxy.books[b_i], counter[b_i])
            # raise NotImplementedError
    save_csv(content_to_be_processed, os.path.expanduser('~/Downloads/test.csv'))
    print(book_index_list)


if __name__ == '__main__':
    import time
    start_time = time.time()
    # ------------------------------
    load_listst_one()
    # ------------------------------
    end_time = time.time()
    duration = end_time - start_time
    hour = int(duration) // 3600
    minutes = int(duration) // 60 - 60 * hour
    seconds = duration % 60
    print('\nRunning time: {0:d} h {1:d} m {2:.2f} s'.format(hour, minutes, seconds))
