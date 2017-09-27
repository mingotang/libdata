# 图书推荐 `python` 实现

对图书馆借阅流水数据进行处理，做出书籍相关推荐。

BY： [Mingo Tang](mailto:mtang024@163.com)


## 目录

- [部署要求](#running_requirements)
- [数据结构](#data_structure)
- [待实现功能](#unrealized_funcs)
- [方法说明](#pyfile_comment)
- [结果说明](#result_comment)


## 部署要求<a id='running_requirements'></a>

代码均使用 `Python3.6` 并编译通过

requirements：

- [tqdm](https://github.com/tqdm/tqdm): 显示进度条
- [pandas](https://github.com/pandas-dev/pandas): 数据分析与数据结构
- [mlxtend](https://github.com/rasbt/mlxtend): 机器学习算法库
- [jieba](https://github.com/fxsjy/jieba)：结巴分词
- [pymysql](https://github.com/PyMySQL/PyMySQL)：连接SQL数据库

快速安装 requirements：

在本项目目录下有文件 `requirements.txt`

    $ cd libdata
    $ pip install -r requirements.txt

## 数据结构<a id='data_structure'></a>



## 待实现功能<a id='unrealized_funcs'></a>

- 从出版社的isbn代码对书籍isbn进行拆解
- 优化apriori使其可以对按人分类的总书目进行关联规则挖掘（瓶颈为内存）


## 方法说明<a id='pyfile_comment'></a>



## 结果说明<a id='result_comment'></a>
