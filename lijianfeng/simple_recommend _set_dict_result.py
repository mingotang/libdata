#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import math
import time
import copy
import random
from operator import itemgetter
t1 = time.clock()
ftrain = open('maindata/simple_stu_data.txt', 'r')
user_set = set()  # 由于user_list的顺序是固定的，所以其索引就可以的当做序号。
book_set = set()
for line in ftrain:
    user,book = line.rstrip().split('@')
    user_set.add(user)
    book_set.add(book)
user_list = list(user_set)
book_list = list(book_set)
n_users = len(user_list)
n_books = len(book_list)
print 'Number of users = ' + str(n_users) + ' | Number of books = ' + str(n_books)

user_dict = {}
book_dict = {}
for i in xrange(n_users):
    user_dict[user_list[i]] = i
for i in xrange(n_books):
    book_dict[book_list[i]] = i

import time
start = time.clock()
data_matrix = {} # 创建评分矩阵{user:set()}
train_data_matrix = {} #训练集
train_data_matrixT = {}#转置矩阵
test_data_matrix = {} #创建测试集集
ftrain = open('maindata/simple_stu_data.txt', 'r')
pivot = 0.6 #太大则p小r大，0.7为初始,后来改为0.6
for line in ftrain:
    user,book = line.rstrip().split('@')
    data_matrix.setdefault(user_dict[user], set())
    data_matrix[user_dict[user]].add(book_dict[book])
    if random.random()<pivot:
        train_data_matrix.setdefault(user_dict[user],set())
        train_data_matrix[user_dict[user]].add(book_dict[book])
        train_data_matrixT.setdefault(book_dict[book], set())
        train_data_matrixT[book_dict[book]].add(user_dict[user])
    else:
        test_data_matrix.setdefault(user_dict[user], set())
        test_data_matrix[user_dict[user]].add(book_dict[book])
ftrain.close()
end = time.clock()
#print 'basic reading spends',end-start

knn =100
topn =10
def sumof(dic):
    s = 0
    for k,v in dic.iteritems():
        s += len(v)
    return s
print "train_data_matrix is done with valid value",sumof(train_data_matrix)

def set_threshhold(dic,t):
    for k, v in dic.items():
        if v < t:
            del dic[k]
    return

def keep_top(dic,n):
    if n>=len(dic):
        return
    else:
        threshold = sorted(dic.values(),reverse=True)[n]
        #threshold = np.sort(dic.values())[-n]
        l = len(dic)
        for k,v in dic.items():#这里不能用iteritems，因为dic一直在变，所以要一次性读取
            if v<threshold:
                del dic[k]
        return
def JaccardSimilar(set1,set2):
    num = len(set1&set2)
    num2 =len(set1|set2)
    #return random.randint(0,1) 很快
    return num*1.0/num2
    return 0
def cosSimilar(set1,set2):
    num = len(set1&set2)
    return num * 1.0 / ((len(set1) * len(set2)) ** 0.5)  # 这里有点偷工减料，因为所有的value是1，所以模^2刚好是lenth
    # try:
    #     return num*1.0/((len(set1)*len(set2))**0.5) #这里有点偷工减料，因为所有的value是1，所以模^2刚好是lenth
    # except:
    #     print "cosSimilar wrong",dict1,dict2
    #     return 0
def Similarity(matrix,matrixT):  # 2维字典列表
    # build inverse table for user_users
    user_users = {} # 对于每一个用户，找出其有相关度的用户并存在（）中
    for book in matrixT.keys():
        users = matrixT[book]#是集合set()
        if len(users) == 1:
            continue
        for user in users: #复杂度？
            user_users.setdefault(user,set())
            user_users[user] = user_users[user]|(users-set([user])) #这里用的是真好，省了len(users)的复杂度

    users_withsim = set()
    for user in user_users.keys():
        if len(user_users[user]) > 0:#0值500个，1值500个
            users_withsim.add(user)
    print len(users_withsim),'users_withsim in',len(matrix),'n_users'

    n = len(matrix)
    sim_matrix = {}# 创建2维字典列表
    for i in users_withsim:  # 对有相似用户的任意用户i
        sim_matrix.setdefault(i,{})
        for j in user_users[i]: #强者，一下降低了好多变成了n*len(user_users[i])
            #sim = random.random()
            #sim = JaccardSimilar(matrix[i], matrix[j])
            sim = cosSimilar(matrix[i], matrix[j]) # 纵向的话相似度差的太多有可能要设置阈值。
            if sim == 1:
                #print "sim == 1 between ",user_list[i],user_list[j] ## 这个问题需要考虑，只借了同一本书，导致sim =1，最后怎么考虑
                break
            elif sim != 0:
                sim_matrix[i][j] = sim
        k = knn
        keep_top(sim_matrix[i], k)
            # 引入参数N，每一行只存留最大k个相似度，即k近邻
    return sim_matrix

import time
start = time.clock()
user_similarity = Similarity(train_data_matrix,train_data_matrixT)
#item_similarity = Similarity(train_data_matrixT,train_data_matrix)
item_similarity = 1
end = time.clock()
print "similarity is done"+" with time spent ",end-start

def predict(ratings, user_similarity, item_similarity, type='user'):#n*n矩阵乘以n*m矩阵,其实没相似度的就根本不管了。
    if type == 'user':
        predictions = {} # {user:{book:pred}}
        recommendations = {} #{user:set(books)}
        count1 = 0
        for u in user_similarity.keys():
            predictions.setdefault(u, {})
            for k1, weight in user_similarity[u].iteritems():
                for book_index in ratings.get(k1, set()):
                    predictions[u][book_index] = predictions[u].get(book_index, 0) + weight# 一元评价的评分就是1
            #把已经借阅过的图书从predictions里面删去
            for book in predictions[u].keys():
                if book in ratings[u]:
                    del predictions[u][book]
            N = topn  # 推荐书目量
            keep_top(predictions[u], N) #很重要，不然内存空间不够放。
            #threshold = N_th
            #set_threshhold(predictions[u], threshhold)
            #recommendations[u] = set(predictions[u].keys())
            recommendations[u] = set([k for k, v in sorted(predictions[u].items(), key=itemgetter(1), reverse=True)[0:N]])
            # l = len(recommendations[u])
            # if l == 0: # 带入item_similarity 的用途
            #     count1 += 1
            #     predictions.setdefault(u, {})
            #     for j in ratings[u]:
            #         for i, v in item_similarity.get(j, {}).iteritems():
            #             predictions[u][i] = predictions[u].get(i, 0) + v * 1  # 一元评价的评分就是1
            #
            #     # 把已经借阅过的图书从predictions里面删去
            #     for book in predictions[u].keys():
            #         if book in ratings[u]:
            #             del predictions[u][book]
            #     N = topn  # 推荐书目量
            #     keep_top(predictions[u], N)  # 很重要，不然内存空间不够放。
            #     recommendations[u] = recommendations[u] & set([k for k, v in sorted(predictions[u].items(), key=itemgetter(1), reverse=True)[0:N-l]])
        print 'there are',count1,'users have no recommendations'
        return predictions,recommendations

start = time.clock()
predictions, recommendations = predict(train_data_matrix,user_similarity,item_similarity)
end = time.clock()
print "predictions is done"+" with time spent ",end-start

def recommend(user_predictions, item_predictions): # 混合算法，在user-based上层叠item-based
    recommendations = {}
    count1 = 0
    N = topn
    for u in user_predictions.keys():
        recommendations.setdefault(u,{})
        l = len(u)
        recommendations[u] = set([k for k, v in sorted(user_predictions[u].items(), key=itemgetter(1), reverse=True)[0:N]])
        #if l < N:# 实际的预测评分项都少于N
        #    count1 +=1
        #    recommendations[u] = recommendations[u]&set([k for k, v in sorted(item_predictions[u].items(), key=itemgetter(1), reverse=True)[0:N-l]])
    print count1
    return recommendations
#recommendations = recommend(user_predictions, item_predictions)

def random_reco():
    N = topn  # 推荐书目量
    random_recommendations = {}#{user:set(books)}
    for i in xrange(n_users):
        random_recommendations[i] = set([random.randint(0,n_books-1) for x in xrange(N)])
    return random_recommendations
#　random_recommendations = random_reco()

def popular_reco():
    N = topn
    book_popularity = {}
    for k, v in train_data_matrixT.iteritems():
        book_popularity[k] = len(v)
    popular_books = [k for k,v in sorted(book_popularity.items() , key = itemgetter(1) ,reverse=True)[0:N]]
    return popular_books

def records(id):
    row = user_list.index(id)
    print 'train_data of',id,' as follow'
    for book in train_data_matrix[row]:
        print book_list[book]
    print 'test_data of',id,'as follow'
    for book in test_data_matrix[row]:
        print book_list[book]
    return 


def knn(similarity,k,id):
    row = user_list.index(id)
    users = sorted(similarity[row].items(), key=itemgetter(1), reverse=True)[0:k]
    for k,v in users:
        print v ,user_list[k]
    return users



def recommend_books(id):
    reco_books = []
    row = user_list.index(id)
    pred = predictions[row].copy()
    keep_top(pred, 10)
    for k,v in sorted(pred.items(),key=itemgetter(1), reverse=True):
        print v, book_list[k]
        reco_books.append(book_list[k])
    return

def showresult(id):
    idstr = id
    records(idstr)
    users = knn(user_similarity,10,idstr)
    for k,v in users:
        print v,user_list[k],
        for book in train_data_matrix[k]:
            print book_list[book],
    recommend_books(idstr)

showresult('5130209358')
#showresult('5140209102')


def evaluation(users):
    like_matrix = copy.deepcopy(test_data_matrix) # 记得改成test，{user:set(books)}
    reco_matrix = copy.deepcopy(recommendations) # {user:set(books)}
    # 标准测度方法
    liked_sum = 0
    reco_sum = 0
    hit_count = 0
    all_rec_books = set()
    for user in users:#xrange(n_users): # 这里可能有个问题?没有hit的user就压根不计算recall和precision了？
        a= like_matrix.get(user,set())
        b= reco_matrix.get(user,set())
        hit_count += len(a&b)
        liked_sum +=  len(a)
        reco_sum += len(b)
        c = recommendations.get(user, set())
        #all_rec_books = all_rec_books|c
    r = hit_count*1.0/liked_sum
    p = hit_count*1.0/reco_sum
    f = p*r*2.0/(p+r)
    c = len(all_rec_books)*1.0/n_books
    print 'recall rate of all is ',r
    print 'precision rate of all is ',p  # 这里有点问题，比如对某用户推荐10本书，但是在test集合里面只有3本书，那最大值也就是30%
    print 'f value of all is ', f
    print 'coverage rate of all is', c
    return r,p,f,c

interval = [0,5,10,20,50,100,10000]
books_num = [len(v) for k,v in data_matrix.iteritems()]
u1,u2,u3,u4,u5,u6 = [],[],[],[],[],[]
for user in xrange(n_users):
    b = len(data_matrix[user])#books_num[user]
    if b <= 5: u1.append(user)
    elif b <= 10: u2.append(user)
    elif b <= 20: u3.append(user)
    elif b <= 50: u4.append(user)
    elif b <= 100: u5.append(user)
    else: u6.append(user)
if 1:
    print 'there are ',len(u2+u3+u4+u5+u6),'users in this subset'
    print evaluation(u2+u3+u4+u5+u6)




# 自定义测度方法
# hit_matrix = {}# {user:set(books)}
# recall_matrix = {} #{user:recall rate}
# precision_matrix = {}
# for user in user_dict.values():
#     hit_matrix[user] = like_matrix[user] & reco_matrix[user] #.get(user,set())
#     recall_matrix[user] = len(hit_matrix[user]) * 1.0 / len(like_matrix[user])
#     precision_matrix[user] = len(hit_matrix[user]) * 1.0 / len(reco_matrix[user])
# id = '513029358'
# print 'recall rate of ',id, 'is ', recall_matrix[user_dict['5130209358']]
# print 'precision rate of ',id, 'is ', precision_matrix[user_dict['5130209358']]

t2 = time.clock()
print 'whole program spends',t2-t1,'before evaluation'
