第一部分 数据结构与对象

# 第2章 简单动态字符串

Redis 没有直接使用 C 语言传统的字符串表示，而是自己构建了一种名为简单动态字符串（Simple dynamic string）的抽象类型，并将 SDS 用作 Redis 的默认字符串表示。

**2.1 SDS的定义 **

每个sds.h/sdshdr结构表示一个SDS值： 

```c
struct sdshdr {
    // 记录buf数组中已使用字节的数量
    // 等于SDS所保存字符串的长度
    int len;
    // 记录buf数组中未使用字节的数量
    int free;
    // 字节数组，用于保存字符串
    char buf[];
};
```

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120090833.png)

free 属性的值为 0，表示这个 SDS 没有分配任何未使用空间；<br>len 属性的值为 5，表示这个 SDS 保存了一个五字节长的字符串；<br>buf 属性是一个 char 类型的数组，数组的前五个字节分别保存了 'R'、'e'、'd'、'i'、's' 五个字符，而最后一个字节则保存了空字符 '\0'。

遵循空字符结尾这一惯例的好处是，SDS可以直接重用一部分C字符串函数库里面的函数。 

**2.2 SDS与C字符串的区别 **

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120090838.png)

- 2.2.1 常数复杂度获取字符串长度 

  通过使用 SDS 而不是 C 字符串，Redis 将获取字符串长度所需的复杂度从 O(N) 降低到了O(1)，这确保了获取字符串长度的工作不会成为 Redis 的性能瓶颈。 

- 2.2.2 杜绝缓冲区溢出 

  与 C 字符串不同，SDS 的空间分配策略完全杜绝了发生缓冲区溢出的可能性：当 SDS API 需要对 SDS 进行修改时，API 会先检查 SDS 的空间是否满足修改所需的要求，如果不满足的话，API 会自动将 SDS 的空间扩展至执行修改所需的大小，然后才执行实际的修改操作。

- 2.2.3 减少修改字符串时带来的内存重分配次数 

  通过未使用空间，SDS 实现了空间预分配和惰性空间释放两种优化策略。 

  空间预分配：如果对 SDS 进行修改之后，SDS 的长度（也即是 len 属性的值）将小于 1MB，那么程序分配和 len 属性同样大小的未使用空间 ；如果对 SDS 进行修改之后，SDS 的长度将大于等于 1MB，那么程序会分配 1MB 的未使用空间。  

  惰性空间释放：当 SDS 的 API 需要缩短 SDS 保存的
  字符串时，程序并不立即使用内存重分配来回收缩短后多出来的字节，而是使用 free 属性将这些字节的数量记录起来，并等待将来使用。 

- 2.2.4 二进制安全 

  SDS 使用 len 属性的值而不是空字符来判断字符串是否结束。

- 2.2.5 兼容部分 C 字符串函数 

  SDS 的 API 总会将 SDS 保存的数据的末尾设置为空字符，并且总会在为 buf 数组分配空间时多分配一个字节来容纳这个空字符，这是为了让那些保存文本数据的 SDS 可以重用一部分 <string.h> 库定义的函数。 

**2.3 SDS API **

# 第3章 链表 

**3.1 链表和链表节点的实现 **

每个链表节点使用一个 adlist.h/listNode 结构来表示： 

```c
typedef struct listNode {
    // 前置节点
    struct listNode * prev;
    // 后置节点
    struct listNode * next;
    // 节点的值
    void * value;
} listNode;
```

虽然仅仅使用多个listNode结构就可以组成链表，但使用 adlist.h/list 来持有链表的话，操作起来会更方便： 

```c
typedef struct list {
    // 表头节点
    listNode * head;
    // 表尾节点
    listNode * tail;
    // 链表所包含的节点数量
    unsigned long len;
    // 节点值复制函数
    void *(*dup)(void *ptr);
    // 节点值释放函数
    void (*free)(void *ptr);
    // 节点值对比函数
    int (*match)(void *ptr,void *key);
} list;
```

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120090844.png" style="zoom: 80%;" />

Redis 的链表实现的特性可以总结如下：

- 双端：链表节点带有 prev 和 next 指针，获取某个节点的前置节点和后置节点的复杂度都是O(1)。
- 无环：表头节点的 prev 指针和表尾节点的 next 指针都指向 NULL，对链表的访问以 NULL 为终点。
- 带表头指针和表尾指针：通过 list 结构的 head 指针和 tail 指针，程序获取链表的表头节点和表尾节点的复杂度为 O(1)。
- 带链表长度计数器：程序使用 list 结构的 len 属性来对 list 持有的链表节点进行计数，程序获取链表中节点数量的复杂度为 O(1)。
- 多态：链表节点使用void*指针来保存节点值，并且可以通过list结构的 dup、 free、 match 三个属性为节点值设置类型特定函数，所以链表可以用于保存各种不同类型的值。 

# 第4章 字典 

**4.1 字典的实现 **

Redis 的字典使用哈希表作为底层实现，一个哈希表里面可以有多个哈希表节点，而每个哈希表节点就保存了字典中的一个键值对。

接下来的三个小节将分别介绍 Redis 的哈希表、哈希表节点以及字典的实现。

- 4.1.1 哈希表

  Redis 字典所使用的哈希表由 dict.h/dictht 结构定义： 

  ```c
  typedef struct dictht {
      // 哈希表数组
      dictEntry **table;
      // 哈希表大小
      unsigned long size;
      // 哈希表大小掩码，用于计算索引值
      // 总是等于size-1
      unsigned long sizemask;
      // 该哈希表已有节点的数量
      unsigned long used;
  } dictht;
  ```

  table 属性是一个数组，数组中的每个元素都是一个指向 dict.h/dictEntry 结构的指针，每个 dictEntry 结构保存着一个键值对；

  size 属性记录了哈希表的大小，也即是 table 数组的大小；

  used 属性则记录了哈希表目前键值对的数量；

  sizemask 属性的值总是等于 size - 1，这个属性和哈希值一起决定一个键应该被放到 table 数组的哪个索引上面。

  下图展示了一个大小为 4 的空哈希表，没有包含任何键值对。

  <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120090850.png" style="zoom:80%;" />

- 4.1.2 哈希表节点

  哈希表节点使用dictEntry结构表示，每个dictEntry结构都保存着一个键值对： 

  ```c
  typedef struct dictEntry {
      // 键
      void *key;
      // 值
      // 可以是一个指针，或者是一个uint64_t整数
      // 又或者是一个int64_t整数。
      union {
          void *val;
          uint64_tu64;
          int64_ts64;
      } v;
      // 指向下个哈希表节点，形成链表
      struct dictEntry *next;
  } dictEntry;
  ```

  ![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120090854.png)

- 4.1.3 字典

  Redis 中的字典由 dict.h/dict 结构表示： 

  ```c
  typedef struct dict {
      // 类型特定函数
      dictType *type;
      // 私有数据
      void *privdata;
      // 哈希表
      dictht ht[2];
      // rehash索引
      // 当rehash不在进行时，值为-1
      in trehashidx; /* rehashing not in progress if rehashidx == -1 */
  } dict;
  ```

------

第二部分 单机数据库的实现

# 第9章 数据库 

**9.1 服务器中的数据库 **

Redis 服务器将所有数据库都保存在服务器状态 redis.h/redisServer 结构的db数组中， 每个 redisDb 结构代表一个数据库： 

```c
struct redisServer {
    // ...
    // 一个数组，保存着服务器中的所有数据库
    redisDb *db;
    // 服务器的数据库数量
    int dbnum;
};
```

dbnum属性的值由服务器配置的database选项决定，默认情况下，该选项的值为16，所以Redis服务器默认会创建16个数据库。

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120090859.png)

**9.2 切换数据库 **

# 第10章 RDB持久化

本章首先介绍 Redis 服务器保存和载入 RDB 文件的方法，重点说明 SAVE 命令和 BGSAVE 命令的实现方式。  之后，本章会继续介绍 Redis 服务器自动保存功能的实现原理。

**10.1 RDB文件的创建与载入**



- 10.1.1 SAVE命令执行时的服务器状态
- 10.1.2 BGSAVE命令执行时的服务器状态
- 10.1.3 RDB文件载入时的服务器状态



**10.2 自动间隔性保存**



- 10.2.1 设置保存条件

- 10.2.2 dirty计数器和lastsave属性
- 10.2.3 检查保存条件是否满足



**10.3 RDB文件结构**

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120090909.jpg)

> 用全大写单词标识常量，用全小写单词标示变量和数据。本章展示的所有 RDB 文件结构图都遵循这一规则。

REDIS 部分保存着 "REDIS" 五个字符，程序可以在载入文件时，快速检查所载入的文件是否是 RDB 文件。

db_version 长度为 4 字节，这个整数记录了 RDB 文件的版本号。

databases 部分包含着零个或任意多个数据库，以及各个数据库中的键值对数据。

EOF 常量的长度为 1 字节，这个常量标识着 RDB 文件正文内容的结束。

check_sum 是一个 8 字节长的无符号整数，保存着一个校验和。

例如：

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120090913.jpg)

- 10.3.1 databases部分
- 10.3.2 key_value_pairs部分
- 10.3.3 value的编码



**10.4 分析RDB文件**

我们使用 od 命令来分析 Redis 服务器产生的 RDB 文件。

- 10.4.1 不包含任何键值对的 RDB 文件
- 10.4.2 包含字符串键的 RDB 文件
- 10.4.3 包含带有过期时间的字符串键的 RDB 文件
- 10.4.4 包含一个集合键的 RDB 文件
- 10.4.5 关于分析RDB文件的说明



# 第11章 AOF持久化


