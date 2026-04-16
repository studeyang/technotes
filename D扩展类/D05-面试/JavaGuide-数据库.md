> 来源：https://javaguide.cn/home.html

# 01 | 基础

# 02 | MySQL

## 2.1 MySQL 基础

**MySQL 基础架构**

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202210140702245.png)

从上图可以看出， MySQL 主要由下面几部分构成：

- **连接器：** 身份认证和权限相关(登录 MySQL 的时候)。
- **查询缓存：** 执行查询语句的时候，会先查询缓存（MySQL 8.0 版本后移除，因为这个功能不太实用）。
- **分析器：** 没有命中缓存的话，SQL 语句就会经过分析器，分析器说白了就是要先看你的 SQL 语句要干嘛，再检查你的 SQL 语句语法是否正确。
- **优化器：** 按照 MySQL 认为最优的方案去执行。
- **执行器：** 执行语句，然后从存储引擎返回数据。 执行语句之前会先判断是否有权限，如果没有权限的话，就会报错。
- **插件式存储引擎** ： 主要负责数据的存储和读取，采用的是插件式架构，支持 InnoDB、MyISAM、Memory 等多种存储引擎。

## 2.2 MySQL 存储引擎

**MySQL 支持哪些存储引擎？默认使用哪个？**

MySQL 支持多种存储引擎，你可以通过 `show engines` 命令来查看 MySQL 支持的所有存储引擎。

![查看 MySQL 提供的所有存储引擎](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202210140704273.png)

从上图我们可以查看出， MySQL 当前默认的存储引擎是 InnoDB。并且，所有的存储引擎中只有 InnoDB 是事务性存储引擎，也就是说只有 InnoDB 支持事务。

> 我这里使用的 MySQL 版本是 8.x，不同的 MySQL 版本之间可能会有差别。





# 03 | Redis

## 3.1 Redis 基础

**Redis 为什么这么快？**

Redis 内部做了非常多的性能优化，比较重要的主要有下面 3 点：

- Redis 基于内存，内存的访问速度是磁盘的上千倍；
- Redis 基于 Reactor 模式设计开发了一套高效的事件处理模型，主要是单线程事件循环和 IO 多路复用（Redis 线程模式后面会详细介绍到）；
- Redis 内置了多种优化过后的数据结构实现，性能非常高。

![why-redis-so-fast](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202210132139664.png)

## 3.2 Redis 数据结构



**使用 Set 实现抽奖系统需要用到什么命令？** 

- `SPOP key count` ： 随机移除并获取指定集合中一个或多个元素，适合不允许重复中奖的场景。
- `SRANDMEMBER key count` : 随机获取指定集合中指定数量的元素，适合允许重复中奖的场景。







## 3.3 







