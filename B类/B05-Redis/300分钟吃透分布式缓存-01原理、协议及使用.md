> 参考资料：拉勾教育《300分钟吃透分布式缓存》第六章

# 第1讲：常用的缓存组件Redis是如何运行的？

**Redis 简介**

Redis 是 Remote dictionary server 即远程字典服务的缩写，是一款基于 ANSI C 语言编写的，日志型 key-value 存储组件，它的所有数据结构都存在内存中，可以用作缓存、数据库和消息中间件。

**Redis 特性**

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201120090939.png)

- 数据类型

Redis 具有 8 种核心数据类型，每种数据类型都有一系列操作指令对应。

- 高性能

Redis 性能很高，单线程压测可以达到 10~11w 的 QPS。

- 持久化

Redis 提供了 2 种持久化方式：快照方式，将某时刻所有数据都写入硬盘的 RDB 文件；追加文件方式，即将所有写命令都以追加的方式写入硬盘的 AOF 文件中。

- 读写分离

对于互联网系统的线上流量，读操作远远大于写操作。此时，可以使用 Redis 的复制特性，让一个 Redis 实例作为 master，然后通过复制挂载多个不断同步更新的副本，即多个 slave。通过读写分离，把所有写操作落在 Redis 的 master，所有读操作随机落在 Redis 的多个 slave 中，从而大幅提升 Redis 的读写能力。

- 事务支持

Redis 还支持事务，在 multi 指令后，指定多个操作，然后通过 exec 指令一次性执行，中途如果出现异常，则不执行所有命令操作，否则，按顺序一次性执行所有操作，执行过程中不会执行任何其他指令。

- Cluster 特性

Redis 还支持 Cluster 特性，可以通过自动或手动方式，将所有 key 按哈希分散到不同节点，在容量不足时，还可以通过 Redis 的迁移指令，把其中一部分 key 迁移到其他节点。

**Redis 高性能**

Redis 一般被看作单进程/单线程组件，Redis 基于 Epoll 事件模型开发，整个处理过程不存在竞争，不需要加锁，没有上下文切换开销，所有数据操作都是在内存中操作，所以 Redis 的性能很高，单个实例即可以达到 10w 级的 QPS。

除了主进程，Redis 还会 fork 一个子进程，来进行重负荷任务的处理。Redis fork 子进程主要有 3 种场景。

- 收到 bgrewriteaof 命令时，Redis 调用 fork，构建一个子进程，子进程往临时 AOF 文件中，写入重建数据库状态的所有命令，当写入完毕，子进程则通知父进程，父进程把新增的写操作也追加到临时 AOF 文件，然后将临时文件替换老的 AOF 文件，并重命名。
- 收到 bgsave 命令时，Redis 构建子进程，子进程将内存中的所有数据通过快照做一次持久化落地，写入到 RDB 中。
- 当需要进行全量复制时，master 也会启动一个子进程，子进程将数据库快照保存到 RDB 文件，在写完 RDB 快照文件后，master 就会把 RDB 发给 slave，同时将后续新的写指令都同步给 slave。

主进程中，除了主线程处理网络 IO 和命令操作外，还有 3 个辅助 BIO 线程。这 3 个 BIO 线程分别负责处理文件关闭、AOF 缓冲数据刷新到磁盘，以及清理对象这三个任务队列。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201120090945.png" style="zoom:80%;" />

Redis 在启动时，会同时启动这三个 BIO 线程，然后 BIO 线程休眠等待任务。当需要执行相关类型的后台任务时，就会构建一个 bio_job 结构，记录任务参数，然后将 bio_job 追加到任务队列尾部。然后唤醒 BIO 线程，即可进行任务执行。

**Redis 持久化**

RDB 只记录某个时间点的快照，可以通过设置指定时间内修改 keys 数的阀值，超过则自动构建 RDB 内容快照。

AOF 记录是构建整个数据库内容的命令，它会随着新的写操作不断进行追加操作。由于不断追加，AOF 会记录数据大量的中间状态，AOF 文件会变得非常大，此时，可以通过 bgrewriteaof 指令，对 AOF 进行重写，只保留数据的最后内容，来大大缩减 AOF 的内容。

> 线上 Redis 一般会同时使用两种方式，通过开启 appendonly 及关联配置项，将写命令及时追加到 AOF 文件，同时在每日流量低峰时，通过 bgsave 保存当时所有内存数据快照。 

**Redis 集群管理**

Redis 的集群管理有 3 种方式。

- client 分片访问，client 对 key 做 hash，然后按取模或一致性 hash，把 key 的读写分散到不同的 Redis 实例上。
- 在 Redis 前加一个 proxy，把路由策略、后端 Redis 状态维护的工作都放到 proxy 中进行，client 直接访问 proxy，后端 Redis 变更，只需修改 proxy 配置即可。
- 直接使用 Redis cluster。Redis 创建之初，使用方直接给 Redis 的节点分配 slot，后续访问时，对 key 做 hash 找到对应的 slot，然后访问 slot 所在的 Redis 实例。在需要扩容缩容时，可以在线通过 cluster setslot 指令，以及 migrate 指令，将 slot 下所有 key 迁移到目标节点，即可实现扩缩容的目的。

# 第2讲：如何理解、选择并使用Redis的核心数据类型？

**Redis 数据类型**

Redis 有 8 种核心数据类型，分别是：

string 字符串类型；list 列表类型；set 集合类型；sorted set 有序集合类型；hash 类型；bitmap 位图类型； geo 地理位置类型；HyperLogLog 基数统计类型。

- string 字符串

在字符串长度小于 1MB 时，按所需长度的 2 倍来分配，超过 1MB，则按照每次额外增加 1MB 的容量来预分配。

字符串数据类型对应使用的指令包括 set、get、mset、incr、decr 等。

```text
127.0.0.1:6379> set name "redis"
OK
127.0.0.1:6379> get name
"redis"
```

- list 列表

Redis 的 list 列表，是一个快速双向链表，存储了一系列的 string 类型的字串值。

操作 list 列表时，可以用 lpush、lpop、rpush、rpop、lrange 来进行常规的队列进出及范围获取操作，在某些特殊场景下，也可以用 lset、linsert 进行随机插入操作，用 lrem 进行指定元素删除操作；最后，在消息列表的消费时，还可以用 Blpop、Brpop 进行阻塞式获取，从而在列表暂时没有元素时，可以安静的等待新元素的插入，而不需要额外持续的查询。

```text
127.0.0.1:6379> lpush mylist aaa
(integer) 1
127.0.0.1:6379> lpush mylist bbb
(integer) 2
127.0.0.1:6379> lrange mylist 0 10
1) "bbb"
2) "aaa"
```

- set 集合

Redis 中的集合一般是通过 dict 哈希表实现的，所以插入、删除，以及查询元素，可以根据元素 hash 值直接定位，时间复杂度为 O(1)。

sismember 指令判断该 key 对应的 set 数据结构中，是否存在某个元素，如果存在返回 1，否则返回 0；

```
127.0.0.1:6379> sadd myset 111 
(integer) 1
127.0.0.1:6379> sadd myset 222
(integer) 2
127.0.0.1:6379> smembers myset
1) "111"
2) "222"
```

- sorted set 有序集合

Redis 中的 sorted set 有序集合也称为 zset，有序集合同 set 集合类似。有序集合中，每个元素都会关联一个 double 类型的 score 分数值。

```
127.0.0.1:6379> zadd myzset 3 abc
(integer) 1
127.0.0.1:6379> zadd myzset 1 abd
(integer) 2
127.0.0.1:6379> zrangebyscore myzset 0 10
1) "abd"
2) "abc"
```

- hash 哈希

hash 数据结构的特点是在单个 key 对应的哈希结构内部，可以记录多个键值对。

hash 结构中的一些重要指令，包括：hmset、hmget、hexists、hgetall、hincrby 等。

```
127.0.0.1:6379> hmset lilei name "LiLei" age 26 title "Senior"
OK
127.0.0.1:6379> hget lilei age
"26"
```

- bitmap 位图

bitmap 位图的特点是按位设置、求与、求或等操作很高效，而且存储成本非常低，用来存对象标签属性的话，一个 bit 即可存一个标签。

可以用 bitmap，存用户最近 N 天的登录情况，每天用 1 bit，登录则置 1。个性推荐在社交应用中非常重要，可以对新闻、feed 设置一系列标签，如军事、娱乐、视频、图片、文字等，用 bitmap 来存储这些标签，在对应标签 bit 位上置 1。

- geo 地理位置

移动社交时代，LBS 应用越来越多，比如微信、陌陌中附近的人，美团、大众点评中附近的美食、电影院，滴滴、优步中附近的专车等。

- hyperLogLog 基数统计

Redis 的 hyperLogLog 是用来做基数统计的数据类型，当输入巨大数量的元素做统计时，只需要很小的内存即可完成。

# 第3讲：Redis协议的请求和响应有哪些“套路”可循？

> 本节内容：
>
> Redis的设计原则、3种响应模式、2种请求格式、5种响应格式。

**设计原则**

Redis 序列化协议的设计原则有三个：

第一是实现简单；<br />第二是可快速解析；<br />第三是便于阅读。

**3种响应模式**

Redis 协议的请求响应模型有三种，除了 2 种特殊模式，其他基本都是 ping-pong 模式，即 client 发送一个请求，server 回复一个响应，一问一答的访问模式。

2 种特殊模式：

- pipeline 模式，即 client 一次连续发送多个请求，然后等待 server 响应，server 处理完请求后，把响应返回给 client。

- pub/sub 模式。即发布订阅模式，client 通过 subscribe 订阅一个 channel，然后 client 进入订阅状态，静静等待。当有消息产生时，server 会持续自动推送消息给 client，不需要 client 的额外请求。而且客户端在进入订阅状态后，只可接受订阅相关的命令如 SUBSCRIBE、PSUBSCRIBE、UNSUBSCRIBE 和 PUNSUBSCRIBE，除了这些命令，其他命令一律失效。

**2种请求格式**

Redis 协议的请求和响应也是有固定套路的。

 对于请求指令，格式有 2 种类型。

- 当你没有 redis-client，但希望可以用通用工具 telnet，直接与 Redis 交互时，Redis 协议虽然简单易于阅读，但在交互式会话中使用，并不容易拼写，此时可以用第一种格式，即 inline cmd 内联命令格式。使用 inline cmd 内联格式，只需要用空格分隔请求指令及参数，简单快速，一个简单的例子如 mget key1 key2\r\n。

- 第二种格式是 Array 数组格式类型。请求指令用的数组类型，与 Redis 响应的数组类型相同，后面在介绍响应格式类型时会详细介绍。

**5种响应格式**

Redis 协议的响应格式有 5 种，分别是：

1. simple strings 简单字符串类型，以 + 开头，后面跟字符串，以 CRLF（即 \r\n）结尾。这种类型不是二进制安全类型，字符串中不能包含 \r 或者 \n。比如许多响应回复以 OK 作为操作成功的标志，协议内容就是 +OK\r\n 。
2. Redis 协议将错误作为一种专门的类型，格式同简单字符串类型，唯一不同的是以 -（减号）开头。Redis 内部实现对 Redis 协议做了进一步规范，减号后面一般先跟 ERR 或者 WRONGTYPE，然后再跟其他简单字符串，最后以 CRLF（回车换行）结束。这里给了两个示例，client 在解析响应时，一旦发现 - 开头，就知道收到 Error 响应。
3. Integer 整数类型。整数类型以 ：开头，后面跟字符串表示的数字，最后以回车换行结尾。Redis 中许多命令都返回整数，但整数的含义要由具体命令来确定。比如，对于 incr 指令，：后的整数表示变更后的数值；对于 llen 表示 list 列表的长度，对于 exists 指令，1 表示 key 存在，0 表示 key 不存在。这里给个例子，：后面跟了个 1000，然后回车换行结束。
4. bulk strings 字符串块类型。字符串块分头部和真正字符串内容两部分。字符串块类型的头部， 为 $ 开头，随后跟真正字符串内容的字节长度，然后以 CRLF 结尾。字符串块的头部之后，跟随真正的字符串内容，最后以 CRLF 结束字符串块。字符串块用于表示二进制安全的字符串，最大长度可以支持 512MB。一个常规的例子，“$6\r\nfoobar\r\n”，对于空字串，可以表示为 “$0\r\n\r\n”，NULL字串： “$-1\r\n”。
5. Arrays 数组类型，如果一个命令需要返回多条数据就需要用数组格式类型，另外，前面提到 client 的请求命令也是主要采用这种格式。