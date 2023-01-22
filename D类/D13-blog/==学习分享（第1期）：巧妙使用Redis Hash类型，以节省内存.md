# 学习分享（第1期）之Redis：巧用Hash类型节省内存

## 回顾

上篇文章[《Redis的String类型，原来这么占内存》](https://mp.weixin.qq.com/s/jRoZdFExGvASvb8HRQL6kA)中的思考题：既然 String 类型这么占内存，那么你有好的方案来节省内存吗？

## 用什么数据结构可以节省内存？

String, Hash, List, Set, Sorted Set。

因为 ziplist 节约内存的性质， 哈希键、列表键和有序集合键初始化的底层实现皆采用 ziplist。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220217220143.png" alt="image-20220217220143729" style="zoom:50%;" />

> Set 为什么没有使用压缩列表？



除了 String 和 Hash，我们还可以使用 Sorted Set 类型进行保存。Sorted Set 的元素有 member 值和 score 值，可以像 Hash 那样，使用二级编码进行保存。具体做法是，把图片 ID 的前 7 位作为 Sorted Set 的 key，把图片 ID 的后 3 位作为 member 值，图片存储对象 ID 作为 score 值。

Sorted Set 中元素较少时，Redis 会使用压缩列表进行存储，可以节省内存空间。不过，和 Hash 不一样，Sorted Set 插入数据时，需要按 score 值的大小排序。当底层结构是压缩列表时，Sorted Set 的插入性能就比不上 Hash。所以，在我们这节课描述的场景中，Sorted Set 类型虽然可以用来保存，但并不是最优选项。



压缩列表（ziplist）是为了节约内存而设计的，是由一系列特殊编码的连续内存块组成的顺序性（sequential）数据结构，一个压缩列表可以包含多个节点，每个节点可以保存一个字节数组或者一个整数值。

Redis 有一种底层数据结构，叫压缩列表（ziplist），这是一种非常节省内存的结构。

压缩列表表头有三个字段 zlbytes、zltail 和 zllen，分别表示列表长度、列表尾的偏移量，以及列表中的 entry 个数。压缩列表尾还有一个 zlend，表示列表结束。

![image-20221020213433269](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202210202134308.png)

- zlbytes：4字节
- zltail：4字节
- zllen：2字节
- entry：
- zlend：1字节



压缩列表之所以能节省内存，就在于它是用一系列连续的 entry 保存数据。每个 entry 的元数据包括下面几部分。

- prev_len，表示前一个 entry 的长度。

  > prev_len 有两种取值情况：1 字节或 5 字节。取值 1 字节时，表示上一个 entry 的长度小于 254 字节。虽然 1 字节的值能表示的数值范围是 0 到 255，但是压缩列表中 zlend 的取值默认是 255，因此，就默认用 255 表示整个压缩列表的结束，其他表示长度的地方就不能再用 255 这个值了。所以，当上一个 entry 长度小于 254 字节时，prev_len 取值为 1 字节，否则，就取值为 5 字节。

- encoding：表示编码方式，1 字节；

- len：表示自身长度，4 字节；

- content：保存实际数据。

这些 entry 会挨个儿放置在内存中，不需要再用额外的指针进行连接，这样就可以节省指针所占用的空间。

我们以保存图片存储对象 ID 为例，来分析一下压缩列表是如何节省内存空间的。

每个 entry 保存一个图片存储对象 ID（8 字节），此时，每个 entry 的 prev_len 只需要 1 个字节就行，因为每个 entry 的前一个 entry 长度都只有 8 字节，小于 254 字节。这样一来，一个图片的存储对象 ID 所占用的内存大小是 14 字节（1+1+4+8=14），实际分配 16 字节。

> key 占用 1+17 = 18 个字节。1 字符占 1 字节？
>
> value: RedisObject 包括 8 字节元数据，8 字节指针。
>
> ​          ziplist 占用 16 个字节
>
> 共 18+16+16=50 字节。不对呀！

## 巧用集合类型

这个方案听起来很好，但还存在一个问题：在一个键对应一个值（也就是单值键值对）的情况下，我们该怎么用集合类型来保存这种单值键值对呢？

如何用集合类型保存单值的键值对？

在保存单值的键值对时，可以采用基于 Hash 类型的二级编码方法。这里说的二级编码，就是把一个单值的数据拆分成两部分，前一部分作为 Hash 集合的 key，后一部分作为 Hash 集合的 value，这样一来，我们就可以把单值数据保存到 Hash 集合中了。

以图片 ID 1101000060 和图片存储对象 ID 3302000080 为例，我们可以把图片 ID 的前 7 位（1101000）作为 Hash 类型的键，把图片 ID 的最后 3 位（060）和图片存储对象 ID 分别作为 Hash 类型值中的 key 和 value。

```shell
127.0.0.1:6379> info memory
# Memory
used_memory:871872
127.0.0.1:6379> hset 1101000 060 3302000080 061 3302000081 ...
(integer) 1
127.0.0.1:6379> info memory
# Memory
used_memory:872152
```

增加了280字段。

## 一定要7+3存储 key 吗？

不过，你可能也会有疑惑：“二级编码一定要把图片 ID 的前 7 位作为 Hash 类型的键，把最后 3 位作为 Hash 类型值中的 key 吗？”

答案是肯定的。

Redis Hash 类型的两种底层实现结构，分别是压缩列表和哈希表。Hash 类型设置了用压缩列表保存数据时的两个阈值，一旦超过了阈值，Hash 类型就会用哈希表来保存数据了。

如果我们往 Hash 集合中写入的元素个数超过了 `hash-max-ziplist-entries` （默认512个），或者写入的单个元素大小超过了 `hash-max-ziplist-value` （默认64字节），Redis 就会自动把 Hash 类型的实现结构由压缩列表转为哈希表。一旦从压缩列表转为了哈希表，Hash 类型就会一直用哈希表进行保存，而不会再转回压缩列表了。在节省内存空间方面，哈希表就没有压缩列表那么高效了。

为了能充分使用压缩列表的精简内存布局，我们一般要控制保存在 Hash 集合中的元素个数。所以，在刚才的二级编码中，我们只用图片 ID 最后 3 位作为 Hash 集合的 key，也就保证了 Hash 集合的元素个数不超过 1000，同时，我们把 `hash-max-ziplist-entries` 设置为 1000，这样一来，Hash 集合就可以一直使用压缩列表来节省内存空间了。





## 参考资料

- 文中的一些命令，参考菜鸟教程：https://www.runoob.com/redis/redis-tutorial.html
- Redis 的 key 也是 SDS 类型的，参考：https://www.cnblogs.com/lonely-wolf/p/14261486.html
- SDS 的定义，参考：https://juejin.cn/post/6844903936520880135#heading-6
- 极客时间《Redis核心技术与实战》
- 书籍《Redis设计与实现》
- 压缩列表：https://redisbook.readthedocs.io/en/latest/compress-datastruct/ziplist.html
- 哈希表：http://redisbook.com/preview/object/hash.html

## 说明

之前的分享内容都是相对零散的知识点，不成体系。以后的每周分享，我会尽量将每篇文章串连起来，于是我决定做一个专栏，名字就叫《学习分享》。这是该系列的第一篇。

《学习分享》每周一或周二发表。这些内容大多来自我平时学习过程中的笔记，笔记仓库在 Github：[studeyang/technotes](https://github.com/studeyang/technotes)。其中我认为有深度、有帮助的内容，就会以文章的形式发表在该专栏，内容会发表在我的[公众号](https://mp.weixin.qq.com/s/TWRVaQPhrQf9oPxsAsuIKQ)、[掘金](https://juejin.cn/user/2594503173605767/posts)和[今日头条](https://www.toutiao.com/c/user/token/MS4wLjABAAAArFlpgpSvRI74ttxw76bAENUnFIFcYTJQnZYS77fZmNQ/?source=mp_msg&tab=article)，也会维护在 Github：[studeyang/leanrning-share](https://github.com/studeyang/learning-share)。

## 相关文章

也许你对下面文章也感兴趣。

- [Redis高可用之哨兵机制实现细节](https://mp.weixin.qq.com/s/phU5BzyyG5Wxvw0sqkkK4A)
- [Redis高可用全景一览](https://mp.weixin.qq.com/s/tsH45bpwc_WCSzi-wnRDbA)
- [海量数据下，如何统计用户的签到信息？](https://mp.weixin.qq.com/s/vcdmfZljCiv5ICJaRkvAAA)

