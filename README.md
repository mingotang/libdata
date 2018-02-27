# 图书推荐 `python` 实现及开发文档

对图书馆借阅流水数据进行处理，做出书籍相关推荐。

BY： [Mingo Tang](mailto:mtang024@163.com)


## 目录

- [部署要求](#running_requirements)
- [文件及对象](#file_and_objects)


## 部署要求<a id='running_requirements'></a>

代码均使用 `Python3.6` 并编译通过

Package requirements：

- [tqdm](https://github.com/tqdm/tqdm): 显示进度条
- [pandas](https://github.com/pandas-dev/pandas): 数据分析与数据结构
- [mlxtend](https://github.com/rasbt/mlxtend): 机器学习算法库
- [jieba](https://github.com/fxsjy/jieba)：结巴分词
- [pymysql](https://github.com/PyMySQL/PyMySQL)：连接SQL数据库


## 文件及对象<a id='file_and_objects'></a>

数据相关文件

**`DataStructure`**



**`DataStructure`**

- GeneralDict：
	- 扩展内置dict的功能
- DataObject <- GeneralDict：
	- 标准化数据对象，类似于dict，以`str`格式字符作为索引，索引内容见文件 modules.BasicSettings 中的 inner_tag
	- keys()：返回一个可迭代的索引列表
- CountingDict <- GeneralDict：
	- 专用于计数的字典，类似于按照 项目：计数额 组织的字典
	- count(element: str, step=1)：按照step增加element的计数
	- sort_by_weights(inverse=False)：按照计数从小到大排序，inverse表示是否从大到小
	- total_weights(tag_list)：获取tag_list中标签的权重之和, tag_list为空则获取所有权重
- EventAction：
	- 用于记录用户操作行为的数据结构
	- __eq__(), is_one_event(other)：判断两个行为是否是同一个行为
	- earlier_than(other), same_time(other), later_than(other)：判断对象的发生时间是否与另一个相同、更早或者更晚
	- not_earlier_than(other), not_later_than(other)
- EventActionList：
	- 用于记录某个用户操作行为的数据结构，属性中的列表用于包含用户操作行为
	- add(element: EventAction, allow_duplicated_record=True)：添加用户操作行为，操作行为按时间从早到晚排序，可以选择是否允许重复行为
- Reader：
	- 用于记录读者信息的数据结构
	- is_one_reader(other)：以id判断是否是同一个读者
	- update(other)：遇到重复的Reader对象时更新Reader内容
- Book：
	- 用于记录书本信息的数据结构
	- is_one_book(other)：以id判断是否是同一本书
	- update(other)：遇到重复的Book对象时更新内容

**`DataStructure`**


