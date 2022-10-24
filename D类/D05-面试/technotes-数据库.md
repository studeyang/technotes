# 01 | MySQL

#  02 | Redis

## 2.1 基础篇

**1. 手写一个键值库需要有哪些模块？**

一个键值数据库包括了访问框架、操作模块、索引模块和存储模块四部分。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220214212224.png" alt="image-20220214212224815" style="zoom:50%;" />

- 访问框架：以 Socket 通信的形式对外提供键值对操作；
- 操作模块：可以对数据做什么操作？
- 索引模块：如何定位键值对的位置？
- 存储模块：可以存哪些数据？

**2. Redis 总体包含哪些模块？**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220214214942.png" alt="image-20220214214942389"  />

**3. Redis 底层数据结构有哪些？**

Redis 底层数据结构一共有 6 种，分别是简单动态字符串、整数数组、双向链表、哈希表、压缩列表和跳表。它们和数据类型的对应关系如下图所示：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/20220217220143.png" alt="image-20220217220143729" style="zoom:50%;" />

- 压缩列表

压缩列表实际上类似于一个数组，数组中的每一个元素都对应保存一个数据。和数组不同的是，压缩列表在表头有三个字段 zlbytes、zltail 和 zllen，分别表示列表长度、列表尾的偏移量和列表中的 entry 个数；压缩列表在表尾还有一个 zlend，表示列表结束。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/20220221211852.png" alt="image-20220221211852113" style="zoom:50%;" />

在压缩列表中，如果我们要查找定位第一个元素和最后一个元素，可以通过表头三个字段的长度直接定位，复杂度是 O(1)。而查找其他元素时，就没有这么高效了，只能逐个查找，此时的复杂度就是 O(N) 了。

- 跳表

跳表在链表的基础上，增加了多级索引，通过索引位置的几个跳转，实现数据的快速定位，如下图所示：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/20220221210646.png" alt="image-20220221210646026" style="zoom: 67%;" />

当数据量很大时，跳表的查找复杂度就是 O(logN)。

**4. 谈谈 Redis 渐进式 rehash**

Redis 默认使用了两个全局哈希表：哈希表 1 和哈希表 2。一开始，当你刚插入数据时，默认使用哈希表 1，此时的哈希表 2 并没有被分配空间。随着数据逐步增多，Redis 开始执行 rehash，这个过程分为三步：

1. 给哈希表 2 分配更大的空间，例如是当前哈希表 1 大小的两倍；
2. 把哈希表 1 中的数据重新映射并拷贝到哈希表 2 中；
3. 释放哈希表 1 的空间，留作下一次 rehash 扩容备用。

渐进式 rehash 简单来说就是在第二步拷贝数据时，Redis 仍然正常处理客户端请求，每处理一个请求时，从哈希表 1 中的第一个索引位置开始，顺带着将这个索引位置上的所有 entries 拷贝到哈希表 2 中；等处理下一个请求时，再顺带拷贝哈希表 1 中的下一个索引位置的 entries。如下图所示：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/20220217214803.png" alt="image-20220217214803853" style="zoom:67%;" />

**5. 单线程 Redis 为什么那么快？**

第一，Redis 的大部分操作在内存上完成；

第二，Redis 采用了高效的数据结构，例如哈希表和跳表；

第三，Redis 采用了多路复用机制，使其在网络 IO 操作中能并发处理大量的客户端请求，实现高吞吐率。

**6. 谈谈 Redis 的 IO 多路复用模型**

Linux 中的 IO 多路复用机制是指一个线程处理多个 IO 流，就是我们经常听到的 select/epoll 机制。下图就是基于多路复用的 Redis IO 模型。Redis 网络框架调用 epoll 机制，让内核监听这些套接字。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/20220223221150.png" alt="image-20220223221150517" style="zoom:67%;" />

为了在请求到达时能通知到 Redis 线程，select/epoll 提供了基于事件的回调机制，即针对不同事件的发生，调用相应的处理函数。这些事件会被放进一个事件队列，Redis 单线程对该事件队列不断进行处理。

以连接请求和读数据请求为例。这两个请求分别对应 Accept 事件和 Read 事件，Redis 分别对这两个事件注册 accept 和 get 回调函数。当 Linux 内核监听到有连接请求或读数据请求时，就会触发 Accept 事件和 Read 事件，此时，内核就会回调 Redis 相应的 accept 和 get 函数进行处理。













