# 图书推荐 `python` 实现

对图书馆借阅流水数据进行处理，做出书籍相关推荐。


BY： [Mingo Tang](mailto:mtang024@126.com)


## 目录

- [代码部署要求](#running_requirements)
- [已实现功能](#realized_funcs)
- [待实现功能](#unrealized_funcs)
- [方法说明](#pyfile_comment)
- [结果说明](#result_comment)


## 代码部署要求<a id='running_requirements'></a>

所有代码均使用 `Python3.5` 并编译通过

Python3.5自带包：

- pickle: 暂存数据
- csv: 读取csv文件
- re: 正则表达式
- copy: 参数复制
- time: 获取时间

Python3.5扩展包：

- [jieba](https://github.com/fxsjy/jieba)：结巴分词
- [pymysql](https://github.com/PyMySQL/PyMySQL)：连接SQL数据库

## 已实现功能<a id='realized_funcs'></a>

- 连接数据库并进行数据库操作
- 按照数据标签（如学工号）构造购物篮并应用apriori算法
- 从索书号当中获取书籍分类
- 分解书名，并尝试用书名中的字段构造购物篮应用apriori算法
-


## 待实现功能<a id='unrealized_funcs'></a>

- 从出版社的isbn代码对书籍isbn进行拆解
- 优化apriori使其可以对按人分类的总书目进行关联规则挖掘（瓶颈为内存）


## 方法说明<a id='pyfile_comment'></a>

### 购物篮算法

```
Apriori(data_sets, min_support, min_confidence, depth=sys.maxsize)
```

标准购物篮算法

参数：
- data_sets, 购物篮列表，为列表嵌套列表
- min_support, 最小支持度
- min_confidence, 最小置信度
- depth, 截断层级，不再挖掘超过depth大小的频繁集


### 协同过滤算法

```
CollaborativeFiltering.reader_based_simple_filtering(reader_id, expect_book_amount)
```

基于用户相似度的简单协同过滤。具体做法：从用户ID找到他选的书，再找到所有选这些书的人，计算这些人和用户选的书当中的重合度，重合度越高的排在越前，再从排序后的相似用户列表找到这些相似用户选的书（这些书用户ID没有选过）直到达到最大期望数目数量

参数：

- reader_id, 学工号
- expect_book_amount, 想要的推荐结果数目数量
 


```
CollaborativeFiltering.book_based_simple_filtering(self, item_id, expected_book_number)
```

基于书目相似度的简单协同过滤。具体做法：从书目ID找到选书目ID的人，再找到这些人选的书，计算这些人选的书的热度，按照从高到低排序之后选取前期望书目数量本书

参数

- item_id, 书目编号（即记录当中的系统编号）
- expect_book_amount, 想要的推荐结果数目数量


## 结果说明<a id='result_comment'></a>

    文件 `Reader based CF - simple - 10.txt`

基于读者的简单协同过滤实现，每人至多推荐10本