#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

ftrain = open('maindata/train_data.txt','rb')
fr = ftrain.readlines()

stu_id_set = set()
book_name_set = set()
ftrain = open('maindata/simple_stu_data.txt','w')
fstu = open('maindata/stu_id_set.txt','w')
fbook = open('maindata/book_name_set.txt','w')
for line in fr:
    if "@@" in line:
        l = line.rstrip().split("@@")
        if l[1] == '' or l[0] == '': # 保证数据不坑爹
            continue
        if 1:
            stu_id_set.add(str(l[1])+"\n")
            book_name_set.add(l[0]+"\n")
        else:
            continue
        ftrain.write(l[1] + "@" + l[0] + "\n")
fstu.writelines(stu_id_set)
fbook.writelines(book_name_set)
fstu.close()
fbook.close()
ftrain.close()
# print len(stu_id_set)
