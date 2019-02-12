# -*- encoding: UTF-8 -*-

from Interface import AbstractEnvObject


class BookGenerator(AbstractEnvObject):
    def __init__(self):
        pass

    def get_book_by_book_id(self, book_id: str):
        from structures.Book import Book
        book = self.env.data_proxy.book_dict[book_id]
        assert isinstance(book, Book)
        return book

    def get_book_by_sum_book_id(self, sum_book_id: str):
        from structures import BookMap
        b_map_list = self.env.data_proxy.book_map_dict.query(BookMap).filter_by(content_id=sum_book_id).all()
        if len(b_map_list) == 1:
            b_map = b_map_list[0]
        elif len(b_map_list) == 0:
            raise NotImplementedError(sum_book_id)
        else:
            print(b_map_list)
            raise NotImplementedError(sum_book_id)
        assert isinstance(b_map, BookMap)
        return self.get_book_by_book_id(b_map.raw_book_id)
