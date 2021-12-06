![](https://cdn.jsdelivr.net/gh/dbses/technotes@master/Python/零基础学Python/python_knowledge_map.jpg)

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