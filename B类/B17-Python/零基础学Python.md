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

列表：

```python
a_list = ['abc', 'xyz']
a_list.append('X')
print (a_list) # ['abc', 'xyz', 'X']
a_list.remove('xyz')
print(a_list) # ['abc', 'X']
```

# 03 | 条件和循环

## 条件语句

```
if 表达式:
  代码块
elif 表达式：
  代码块
else:
  代码块
```

test_if.py

```python
x = 'abcd'
if x == 'abc':
    print('x 的值和abc 相等')
else:
    print('x和 abc不相等')
```

chinese_zodiac_v2.py

```python
# 记录生肖，根据年份来判断生肖

chinese_zodiac = '猴鸡狗猪鼠牛虎兔龙蛇马羊'

year = int(input('请用户输入出生年份'))

if (chinese_zodiac[year % 12]) == '狗':
    print('狗年运势。。。')
```

## 循环语句

**for 循环**

```
for 迭代变量 in 可迭代对象:
  代码块
```

chinese_zodiac_v2.py

```python
chinese_zodiac = '猴鸡狗猪鼠牛虎兔龙蛇马羊'

for cz in chinese_zodiac:
    print(cz)

for i in range(1, 13):
    print(i)

for year in range(2000, 2019):
    print('%s 年的生肖是 %s' % (year, chinese_zodiac[year % 12]))
```

**while 循环**

```
while 表达式:
  代码块
```

样例：

```python
import time
num = 5
while True:
    num = num + 1

    if num == 10:
        continue

    print(num)
    time.sleep(1)
```

**for 循环语句中的 if 嵌套**

```python
zodiac_name = (u'摩羯座', u'水瓶座', u'双鱼座', u'白羊座', u'金牛座', u'双子座',
               u'巨蟹座', u'狮子座', u'处女座', u'天秤座', u'天蝎座', u'射手座')
zodiac_days = ((1, 20), (2, 19), (3, 21), (4, 21), (5, 21), (6, 22),
               (7, 23), (8, 23), (9, 23), (10, 23), (11, 23), (12, 23))

# 用户输入月份和日期
int_month = int(input('请输入月份：'))
int_day = int(input('请输入日期：'))

for zd_num in range(len(zodiac_days)):
    if zodiac_days[zd_num] >= (int_month, int_day):
        print(zodiac_name[zd_num])
        break
    elif int_month == 12 and int_day > 23:
        print(zodiac_name[0])
        break
```

**while 循环语句中的 if 嵌套**

```python
zodiac_name = (u'摩羯座', u'水瓶座', u'双鱼座', u'白羊座', u'金牛座', u'双子座',
               u'巨蟹座', u'狮子座', u'处女座', u'天秤座', u'天蝎座', u'射手座')
zodiac_days = ((1, 20), (2, 19), (3, 21), (4, 21), (5, 21), (6, 22),
               (7, 23), (8, 23), (9, 23), (10, 23), (11, 23), (12, 23))

# 用户输入月份和日期
int_month = int(input('请输入月份：'))
int_day = int(input('请输入日期：'))

n = 0
while zodiac_days[n] < (int_month, int_day):
    if int_month == 12 and int_day > 23:
        break
    n += 1

print(zodiac_name[n])
```

## 映射的类型：字典

字典包含哈希值和指向的对象，例如：

{"哈希值"： "对象"}、{'length':180, ’width':80}

```python
dict1 = {}
print(type(dict1)) # <class 'dict'>
dict2 = {'x': 1, 'y': 2}
dict2['z'] = 3

print(dict2) # {'x': 1, 'y': 2, 'z': 3}
```

统计生肖出现的次数：

```python
chinese_zodiac = '猴鸡狗猪鼠牛虎兔龙蛇马羊'
zodiac_name = (u'摩羯座', u'水瓶座', u'双鱼座', u'白羊座', u'金牛座', u'双子座',
               u'巨蟹座', u'狮子座', u'处女座', u'天秤座', u'天蝎座', u'射手座')
zodiac_days = ((1, 20), (2, 19), (3, 21), (4, 21), (5, 21), (6, 22),
               (7, 23), (8, 23), (9, 23), (10, 23), (11, 23), (12, 23))

cz_num = {}
for i in chinese_zodiac:
    cz_num[i] = 0

z_num = {}
for i in zodiac_name:
    z_num[i] = 0

while True:

    # 用户输入出生年份月份和日期
    year = int(input('请输入年份：'))
    month = int(input('请输入月份：'))
    day = int(input('请输入日期:'))

    n = 0
    while zodiac_days[n] < (month, day):
        if month == 12 and day > 23:
            break
        n += 1
    # 输出生肖和星座
    print(zodiac_name[n])

    print('%s 年的生肖是 %s' % (year, chinese_zodiac[year % 12]))

    cz_num[chinese_zodiac[year % 12]] += 1
    z_num[zodiac_name[n]] += 1

    # 输出生肖和星座的统计信息
    for each_key in cz_num.keys():
        print('生肖 %s 有 %d 个' % (each_key, cz_num[each_key]))

    for each_key in z_num.keys():
        print('星座 %s 有 %d 个' % (each_key, z_num[each_key]))
```

## 列表推导式

```python
# 从1 到 10 所有偶数的平方

# 普通写法
alist = []
for i in range(1, 11):
    if i % 2 == 0:
        alist.append(i * i)

# 列表推导式
alist = [i * i for i in range(1, 11) if (i % 2) == 0]
```

## 字典推导式

```python
zodiac_name = (u'摩羯座', u'水瓶座', u'双鱼座', u'白羊座', u'金牛座', u'双子座',
               u'巨蟹座', u'狮子座', u'处女座', u'天秤座', u'天蝎座', u'射手座')

# 普通写法
z_num = {}
for i in zodiac_name:
    z_num[i] = 0

# 字典推导式
z_num = {i: 0 for i in zodiac_name}
```

# 04 | 文件、输入输出、异常

## 文件内建函数和方法

- open()：打开文件
- read()：输入
- readline()：输入一行
- seek()：文件内移动
- write()：输出
- close()：关闭文件

file_op.py

```python
# 将小说的主要人物记录在文件中
# 写
file1 = open('name.txt', 'w')
file1.write('诸葛亮')
file1.close()

# 读
file2 = open('name.txt')
print(file2.read())
file2.close()

# 追加写
file3 = open('name.txt', 'a')
file3.write('刘备')
file3.close()

# 读一行
file4 = open('name.txt')
for line in file4.readlines():
    print(line)
    print('=====')
file4.close()
```

偏移操作：

```python
file6 = open('name.txt')
print('当前文件指针的位置 %s' % file6.tell())  # 0
print('当前读取到了一个字符，字符的内容是 %s' % file6.read(1))
print('当前文件指针的位置 %s' % file6.tell())  # 1
# 第一个参数代表偏移位置
# 第二个参数: 0表示从文件开头偏移; 1表示从当前位置偏移; 2从文件结尾偏移;
file6.seek(5, 0)
print('我们进行了seek操作')
print('当前文件指针的位置 %s' % file6.tell())
print('当前读取到了一个字符，字符的内容是 %s' % file6.read(1))
print('当前文件指针的位置 %s' % file6.tell())
file6.close()
```

## 异常

异常是在出现错误时采用正常控制流以外的动作。

```
try:
  <监控异常>
except Exception[, reason]:
  <异常处理代码>
finally:
  <无论异常是否发生都执行>
```

捕获异常：

```python
try:
    year = int(input('input year:'))
except ValueError:
    print('年份要输入数字')
```

抛出异常：

```python
try:
    raise NameError('helloError')
except NameError:
    print('my custom error')
```

finnally 块：

```python
try:
    a = open('name.txt')
except Exception as e:
    print(e)

finally:
    a.close()
```

# 05 | 函数、模块

## 函数

函数是对程序逻辑进行结构化的一种编程方法。

函数的定义：

```
def 函数名称():
    代码
    return 需要返回的内容
```

函数的调用：

```
函数名称()
```

**统计小说人物出现次数案例总结**

sanguo.py

```python
def func(filename):
    print(open(filename).read())
    print('test func')


func('name.txt')
```

sanguo_v2.py

```python
import re


def find_item(hero):
    with open('sanguo.txt', encoding='GB18030') as f:
        data = f.read().replace('\n', '')
        name_num = re.findall(hero, data)
        # print('主角 %s  出现 %s  次' %(hero, len(name_num)))

    return len(name_num)


# 读取人物的信息
name_dict = {}
with open('name.txt') as f:
    for line in f:
        names = line.split('|')
        for n in names:
            # print(n)
            name_num = find_item(n)
            name_dict[n] = name_num

name_sorted = sorted(name_dict.items(), key=lambda item: item[1], reverse=True)
print(name_sorted[0:10])
```

### 函数的可变长参数

对于 print 函数，参数个数可变：

```python
print('abc', end='\n')
print('abc')
```

函数的参数可不按顺序写入：

```python
def func(a, b, c):
    print('a= %s' % a)
    print('b= %s' % b)
    print('c= %s' % c)


func(1, c=3, b=2)
```

函数的可变长参数：

```python
# 取得参数的个数
def howlong(first, *other):
    print(1 + len(other))


howlong(123)
```

### 函数的变量作用域

全局变量：

```python
var1 = 123


def func():
    global var1
    var1 = 456
    print(var1)


func() # 456
print(var1) # 456
```

### 函数的迭代器与生成器

```python
list1 = [1, 2, 3]
it = iter(list1)
print(next(it))
print(next(it))
print(next(it))
print(next(it))  # except
```

对于 range 方法，步长无法传入浮点数：

![image-20211129220544615](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211129220549.png)

下面我们使用 yield 来重新实现该方法：

```python
def frange(start, stop, step):
    x = start
    while x < stop:
        yield x
        x += step


for i in frange(10, 20, 0.5):
    print(i)
```

### lambda 表达式

```python
lambda x: x <= (month, day)


def func1(x):
    return x <= (month, day)
```

### Python 内置函数

filter()

```python
a = [1, 2, 3, 4, 5, 6, 7]
list(filter(lambda x: x > 2, a))
```

map()

```python
a = [1, 2, 3]
b = [4, 5, 6]
list(map(lambda x, y: x + y, a, b)) # [5, 7, 9]
```

reduce()

```python
from functools import reduce
reduce(lambda x, y: x + y, [2, 3, 4], 1) # 10
```

zip()

```python
for i in zip((1, 2, 3), (4, 5, 6)):
    print(i)
# (1, 4)
# (2, 5)
# (3, 6)


# 用于字典的 key, value 对调
dicta = {'a': 'aa', 'b': 'bb'}
dictb = zip(dicta.values(), dicta.keys())
print(dict(dictb))
# {'aa': 'a', 'bb': 'b'}
```

### 闭包

内部函数引用外部变量，做叫闭包。

```python
def func():
    a = 1
    b = 2
    return a + b


num1 = func()

# 等同于

def sum(a):
    def add(b):
        return a + b

    return add


num2 = sum(2)
print(num2(4))
```

闭包的应用

```python
# 实现计数器
def counter(FIRST=0):
    cnt = [FIRST]

    def add_one():
        cnt[0] += 1
        return cnt[0]

    return add_one


num5 = counter(5)
num10 = counter(10)

print(num5()) # 6
print(num5()) # 7
print(num5()) # 8
print(num10()) # 11
print(num10()) # 12
```

```python
# 求 a*x + b = y
def a_line(a, b):
    def arg_y(x):
        return a * x + b

    return arg_y


# 使用 lambda 简写
def a_line(a, b):
    return lambda x: a * x + b


line1 = a_line(3, 5)
print(line1(10)) # 35
```

### 装饰器

装饰器将函数作为参数传入。

```python
import time


def timmer(func):
    def wrapper():
        start_time = time.time()
        func()
        stop_time = time.time()
        print("运行时间是 %s 秒 " % (stop_time - start_time))

    return wrapper


@timmer
def i_can_sleep():
    time.sleep(3)


i_can_sleep()
```

带参数的装饰器。

```python
def new_tips(argv):
    def tips(func):
        def nei(a, b):
            print('start %s %s' % (argv, func.__name__))
            func(a, b)
            print('stop')

        return nei

    return tips


@new_tips('add_module')
def add(a, b):
    print(a + b)


@new_tips('sub_module')
def sub(a, b):
    print(a - b)


print(add(4, 5))
print(sub(7, 3))
```

### 自定义上下文管理器

```python
fd = open('name.txt')
try:
    for line in fd:
        print(line)
finally:
    fd.close()

# 可简写成

with open('name.txt') as f:
    for line in f:
        print(line)

```

## 模块

模块是在代码量变得相当大之后， 为了将需要重复使用的有组织的代码段放在一起， 这部分代码可以附加到现有的程序中， 附加的过程叫做导入(import)。

导入模块的一般写法：

```
import 模块名称
import 模块名称 as 新名称
from 模块名称 import 方法名
```

mymod.py

```python
def print_me():
    print('me')
```

```python
import mymod

mymod.print_me()
```

## PEP8 编码规范

https://www.python.org/dev/peps/pep-0008/

可安装 autopep8 插件。

```
pycharm 安装PEP8
cmd窗口输入：pip install autopep8
Tools→Extends Tools→点击加号

Name：Autopep8（可以随便取）
- Tools settings:
    - Programs：`autopep8` （前提是你已经安装了哦）
    - Parameters:`--in-place --aggressive --aggressive $FilePath$`
    - Working directory:`$ProjectFileDir$`
- 点击Output Filters→添加，在对话框中的：Regular expression to match output中输入：`$FILE_PATH$\:$LINE$\:$COLUMN$\:.*`
```

# 06 | 面向对象编程



# 07 | 多线程编程



# 08 | 标准库、机器学习库



# 09 | 第三方库



# 10 | 综合项目

