第三部分：认识DBMS

# 38丨初识Redis：Redis为什么会这么快？

**Redis 是什么，为什么这么快**

Redis 全称是 REmote DIctionary Server，从名字中你也能看出来它用字典结构存储数据，也就是 key-value 类型的数据。

Redis 的查询效率非常高，根据官方提供的数据，Redis 每秒最多处理的请求可以达到 10 万次。

为什么这么快呢？

1. Redis 采用 ANSI C 语言编写，它和 SQLite 一样。采用 C 语言进行编写的好处是底层代码执行效率高，依赖性低，因为使用 C 语言开发的库没有太多运行时（Runtime）依赖，而且系统的兼容性好，稳定性高。
2. Redis 是基于内存的数据库，我们之前讲到过，这样可以避免磁盘 I/O，因此 Redis 也被称为缓存工具。
3. 数据结构结构简单，Redis 采用 Key-Value 方式进行存储，也就是使用 Hash 结构进行操作，数据的操作复杂度为 O(1)。
4. Redis 采用单进程单线程模型，这样做的好处就是避免了上下文切换和不必要的线程之间引起的资源竞争。
5. Redis 采用了多路 I/O 复用技术。这里的多路指的是多个 socket 网络连接，复用指的是复用同一个线程。采用多路 I/O 复用技术的好处是可以在同一个线程中处理多个 I/O 请求，尽量减少网络 I/O 的消耗，提升使用效率。

**Redis 的数据类型**

相比 Memcached，Redis 有一个非常大的优势，就是支持多种数据类型。Redis 支持的数据类型包括字符串、哈希、列表、集合、有序集合等。

1. 字符串（String）

```
> set name zhangfei
> get name
"zhangfei"
```

2. 哈希（hash）

```
> hset user1 username zhangfei
> hset user1 age 28
> hget user1 username
"zhangfei"
```

或者下面写法：

```
> Hmset user1 username zhangfei age 28
```

3. 字符串列表（list）

字符串列表（list）的底层是一个双向链表结构，所以我们可以向列表的两端添加元素，时间复杂度都为 O(1)，同时我们也可以获取列表中的某个片段。

```
> LPUSH heroList zhangfei guanyu liubei
> RPUSH heroList dianwei lvbu
> LRANGE heroList 0 4
1> "liubei"
2> "guanyu"
3> "zhangfei"
4> "dianwei"
5> "lvbu"
```

4. 字符串集合（set）

字符串集合（set）是字符串类型的无序集合，与列表（list）的区别在于集合中的元素是无序的，同时元素不能重复。

```
> SADD heroSet zhangfei guanyu liubei dianwei lvbu
```

如果想要在集合中删除某元素：

```
> SREM heroSet liubei lvbu
```

如果想要获取集合中所有的元素：

```
> SMEMBERS heroSet
1> "dianwei"
2> "guanyu"
3> "zhangfei"
```

如果想要判断集合中是否存在某个元素：

```
> SISMEMBER heroSet zhangfei
> SISMEMBER heroSet liubei
```

5. 有序字符串集合（SortedSet，简称 ZSET）

我们可以把有序字符串集合理解成集合的升级版。实际上 ZSET 是在集合的基础上增加了一个分数属性，这个属性在添加修改元素的时候可以被指定。每次指定后，ZSET 都会按照分数来进行自动排序，也就是说我们在给集合 key 添加 member 的时候，可以指定 score。

```
> ZADD heroScore 8341 zhangfei 7107 guanyu 6900 liubei 7516 dianwei 7344 lvbu
```

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201119225302.png)

如果我们想要获取某个元素的分数：

```
> ZSCORE heroScore guanyu
```

如果我们想要删除一个或多元素：

```
> ZREM heroScore guanyu
```

我们也可以获取某个范围的元素列表：

```
> ZREVRANGE heroScore 0 2 WITHSCORES
```

WITHSCORES 是个可选项，如果使用 WITHSCORES 会将分数一同显示出来。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201119225309.png" style="zoom:50%;" />

# 39丨如何使用Redis来实现多用户抢票问题

今天我们来更加深入地了解一下 Redis 的原理，内容包括以下几方面：

1. Redis 的事务处理机制是怎样的？与 RDBMS 有何不同？
2. Redis 的事务处理的命令都有哪些？如何使用它们完成事务操作？

**Redis 的事务处理机制**

在此之前，让我们先来回忆下 RDBMS 中事务满足的 4 个特性 ACID，它们分别代表原子性、一致性、隔离性和持久性。

Redis 的事务处理与 RDBMS 的事务有一些不同。

首先 Redis 不支持事务的回滚机制（Rollback），这也就意味着当事务发生了错误（只要不是语法错误），整个事务依然会继续执行下去，直到事务队列中所有命令都执行完毕。

只有当编程语法错误的时候，Redis 命令执行才会失败。这种错误通常出现在开发环境中，而很少出现在生产环境中，没有必要开发事务回滚功能。

另外，Redis 是内存数据库，与基于文件的 RDBMS 不同，通常只进行内存计算和操作，无法保证持久性。不过 Redis 也提供了两种持久化的模式，分别是 RDB 和 AOF 模式。

RDB（Redis DataBase）持久化可以把当前进程的数据生成快照保存到磁盘上，触发 RDB 持久化的方式分为手动触发和自动触发。因为持久化操作与命令操作不是同步进行的，所以无法保证事务的持久性。

AOF（Append Only File）持久化采用日志的形式记录每个写操作，弥补了 RDB 在数据一致性上的不足，但是采用 AOF 模式，就意味着每条执行命令都需要写入文件中，会大大降低 Redis 的访问性能。启用 AOF 模式需要手动开启，有 3 种不同的配置方式，默认为 everysec，也就是每秒钟同步一次。其次还有 always 和 no 模式，分别代表只要有数据发生修改就会写入 AOF 文件，以及由操作系统决定什么时候记录到 AOF 文件中。

Redis 是单线程程序，在事务执行时不会中断事务，其他客户端提交的各种操作都无法执行，因此你可以理解为 Redis 的事务处理是串行化的方式，总是具有隔离性的。

**Redis 的事务处理命令**

了解了 Redis 的事务处理机制之后，我们来看下 Redis 的事务处理都包括哪些命令。

1. MULTI：开启一个事务；
2. EXEC：事务执行，将一次性执行事务内的所有命令；
3. DISCARD：取消事务；
4. WATCH：监视一个或多个键，如果事务执行前某个键发生了改动，那么事务也会被打断；
5. UNWATCH：取消 WATCH 命令对所有键的监视。

需要说明的是 Redis 实现事务是基于 COMMAND 队列，如果 Redis 没有开启事务，那么任何的 COMMAND 都会立即执行并返回结果。如果 Redis 开启了事务，COMMAND 命令会放到队列中，并且返回排队的状态 QUEUED，只有调用 EXEC，才会执行 COMMAND 队列中的命令。

比如我们使用事务的方式存储 5 名玩家所选英雄的信息：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201119225315.png" style="zoom: 33%;" />

你能看到在 MULTI 和 EXEC 之间的 COMMAND 命令都会被放到 COMMAND 队列中，并返回排队的状态，只有当 EXEC 调用时才会一次性全部执行。

我们经常使用 Redis 的 WATCH 和 MULTI 命令来处理共享资源的并发操作，比如秒杀，抢票等。实际上 WATCH+MULTI 实现的是乐观锁。下面我们用两个 Redis 客户端来模拟下抢票的流程。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201119225320.png" style="zoom:50%;" />

我们启动 Redis 客户端 1，执行上面的语句，然后在执行 EXEC 前，等待客户端 2 先完成上面的执行，客户端 2 的结果如下：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201119225329.png" style="zoom: 50%;" />

然后客户端 1 执行 EXEC，结果如下：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201119225334.png" style="zoom:50%;" />

你能看到实际上最后一张票被客户端 2 抢到了，这是因为客户端 1WATCH 的票的变量在 EXEC 之前发生了变化，整个事务就被打断，返回空回复（nil）。

需要说明的是 MULTI 后不能再执行 WATCH 命令，否则会返回 WATCH inside MULTI is not allowed 错误（因为 WATCH 代表的就是在执行事务前观察变量是否发生了改变，如果变量改变了就不将事务打断，所以在事务执行之前，也就是 MULTI 之前，使用 WATCH）。同时，如果在执行命令过程中有语法错误，Redis 也会报错，整个事务也不会被执行，Redis 会忽略运行时发生的错误，不会影响到后面的执行。

**模拟多用户抢票**

在 Python 中，Redis 事务是通过 pipeline 封装而实现的，因此在创建 Redis 连接后，需要获取管道 pipeline，然后通过 pipeline 使用 WATCH、MULTI 和 EXEC 命令。

具体代码如下：

```python
import redis
import threading
# 创建连接池
pool = redis.ConnectionPool(host = '127.0.0.1', port=6379, db=0)
# 初始化 redis
r = redis.StrictRedis(connection_pool = pool)
 
# 设置 KEY
KEY="ticket_count"
# 模拟第 i 个用户进行抢票
def sell(i):
    # 初始化 pipe
    pipe = r.pipeline()
    while True:
        try:
            # 监视票数
            pipe.watch(KEY)
            # 查看票数
            c = int(pipe.get(KEY))      
            if c > 0:
                # 开始事务
                pipe.multi()            
                c = c - 1
                pipe.set(KEY, c)        
                pipe.execute()
                print('用户 {} 抢票成功，当前票数 {}'.format(i, c))
                break
            else:
                print('用户 {} 抢票失败，票卖完了'.format(i))
                break
        except Exception as e:
            print('用户 {} 抢票失败，重试一次'.format(i))
            continue
        finally:
            pipe.unwatch()
 
if __name__ == "__main__":
    # 初始化 5 张票
    r.set(KEY, 5)  
    # 设置 8 个人抢票
    for i in range(8):
        t = threading.Thread(target=sell, args=(i,))
        t.start()
```

运行结果：

```
用户 0 抢票成功，当前票数 4
用户 4 抢票失败，重试一次
用户 1 抢票成功，当前票数 3
用户 2 抢票成功，当前票数 2
用户 4 抢票失败，重试一次
用户 5 抢票失败，重试一次
用户 6 抢票成功，当前票数 1
用户 4 抢票成功，当前票数 0
用户 5 抢票失败，重试一次
用户 3 抢票失败，重试一次
用户 7 抢票失败，票卖完了
用户 5 抢票失败，票卖完了
用户 3 抢票失败，票卖完了
```

**思考题**

Redis 既然是单线程程序，在执行事务过程中按照顺序执行，为什么还会用 WATCH+MULTI 的方式来实现乐观锁的并发控制呢？

答：单线程不一定代表要执行的事务的条件都满足，因为其他客户端的命令可能会在WATCH之后修改了KEY的值（如文中例子），导致事务条件不满足，打断事务执行的情况。

上面例子中，将客户端 2 的 SET ticket 设置为 1，请问此时客户端 1 和客户端 2 的执行结果是怎样的？

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201119225346.png" style="zoom:50%;" />

答：客户端2 即使SET ticket的数值没有变化，也是对ticket进行了“修改”，也就是数据的版本发生了变化，因此和文章中的例子一样，客户端2会返回OK，客户端1是 nil。

