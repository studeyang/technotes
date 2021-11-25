> 来源极客时间《零基础学Python》--尹会生

![](https://cdn.jsdelivr.net/gh/dbses/technotes@master/B类/B17-Python/python_knowledge_map.jpg)

# 01 | Python介绍与安装

## 在Windows系统上安装Python

访问：https://www.python.org/downloads/release/python-365/。

进入&退出 python 环境：

```shell
yanglulu@yangluludeMBP ~ % python3
Python 3.8.2 (default, Sep 24 2020, 19:37:08) 
[Clang 12.0.0 (clang-1200.0.32.21)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> 
>>> 
>>> 
KeyboardInterrupt
>>> exit
Use exit() or Ctrl-D (i.e. EOF) to exit
>>> exit()
yanglulu@yangluludeMBP ~ %
```

**安装pip**

```shell
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
```

```shell
python get-pip.py
```

## 第一个Python程序

```python
# 这是我的第一个Python程序

import time # 我导入了一个时间模块


print(time.time()) #在屏幕上打印出从1970年1月1日0:00 到现在经过了多少秒

if  10-9 > 0:
    # 这行需要缩进，缩进用4个空格
    print('10大于9')
```

**Python程序的书写规则**

```python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# Imports 符号”#” 后面可以跟注释
import numpy as np
import tensorflow as tf

tf.logging.set_verbosity(tf.logging.INFO)

# Our application logic will be added here

if __name__ == "__main__":
    tf.app.run() #代码缩进
```

**学习Python编程的利器**

- Python官方文档：https://www.python.org/doc/
- iPython：https://www.python.org/doc/
- jupyter notebook：http://jupyter-notebook.readthedocs.io/en/latest/
- sublime text：https://www.sublimetext.com
- PyCharm：https://www.jetbrains.com/pycharm/
- pip：https://pip.pypa.io/en/stable/installing/

**标准库**

Python标准库的官方文档在如下位置：https://docs.python.org/3/library/index.html

日常应用比较广泛的模块是：
1. 文字处理的 re
2. 日期类型的time、datetime
3. 数字和数学类型的math、random
4. 文件和目录访问的pathlib、os.path
5. 数据压缩和归档的tarfile
6. 通用操作系统的os、logging、argparse
7. 多线程的 threading、queue
8. Internet数据处理的 base64 、json、urllib
9. 结构化标记处理工具的 html、xml
10. 开发工具的unitest
11. 调试工具的 timeit
12. 软件包发布的venv
13. 运行服务的`__main__`

## 基本数据类型

- 整数(int)：8
- 浮点数(float)：8.8
- 字符串(str)：“8” “Python”
- 布尔值(bool)：True False

# 02 | 变量、数字、序列、映射和集合

## 变量

**网络带宽计算器案例**

我们经常要估算一个文件要多久能传输完成，可以写一个计算器来计算传输时间。

network_bandwidth.py

```python
# 网络带宽计算
# print(100/8)

bandwidth = 100
ratio = 8

print(bandwidth/ratio)
```

## 序列

序列是指它的成员都是有序排列，并且可以通过下标偏移量访问到它的一个或几个成员。序列包括：

- 字符串："abcd"
- 列表：[ 0, "abcd"]
- 元组：("abc"， "def"）

**序列的基本操作**

- 对象 [not] in 序列
- 序列 + 序列
- 序列 * 整数
- 序列[0:整数]

**计算生肖和星座案例**

chinese_zodiac.py

```python
# 记录生肖，根据年份来判断生肖

chinese_zodiac = '猴鸡狗猪鼠牛虎兔龙蛇马羊'

print (chinese_zodiac[0:4] ) # 猴鸡狗猪

print (chinese_zodiac[-1]) # 羊

year = 2018
print (year % 12) # 2

print (chinese_zodiac[year % 12]) # 狗

print ( '狗'  not in chinese_zodiac ) # False

print (chinese_zodiac + 'abcd') # 猴鸡狗猪鼠牛虎兔龙蛇马羊abcd

print (chinese_zodiac * 3 ) # 猴鸡狗猪鼠牛虎兔龙蛇马羊猴鸡狗猪鼠牛虎兔龙蛇马羊猴鸡狗猪鼠牛虎兔龙蛇马羊
```

zodiac.py

```python
zodiac_name = (u'摩羯座', u'水瓶座', u'双鱼座', u'白羊座', u'金牛座', u'双子座',
           u'巨蟹座', u'狮子座', u'处女座', u'天秤座', u'天蝎座', u'射手座')
zodiac_days = ((1, 20), (2, 19), (3, 21), (4, 21), (5, 21), (6, 22),
              (7, 23), (8, 23), (9, 23), (10, 23), (11, 23), (12, 23))


(month, day) = (2, 15)

zodiac_day = filter(lambda  x: x<=(month, day), zodiac_days)
print(list(zodiac_day)) # [(1, 20)]

zodac_len = len(list(zodiac_day)) % 12
print(zodiac_name[zodac_len]) # 摩羯座
```





# 03 | 条件和循环



# 04 | 文件、输入输出、异常



# 05 | 函数、模块



# 06 | 面向对象编程



# 07 | 多线程编程



# 08 | 标准库、机器学习库



# 09 | 第三方库



# 10 | 综合项目

