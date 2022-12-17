# Redis高可用之哨兵机制实现细节

在上一篇的文章xxx中，我们学习了 Redis 的高可用性。

Redis高可用
  |-保证服务少中断 
    -> 多副本
    -> 主从库模式保证数据一致及从库的高可用
    -> 哨兵保证主库的高可用
    -> 哨兵集群保证哨兵高可用
  |-保证数据少丢失
    -> AOF日志
    -> AOF恢复数据较慢
    -> RDB内存快照
    -> 执行快照间隔不宜过短
    -> AOF+RDB

并且我们学习了哨兵三个职责，分别是：

哨兵其实就是一个运行在特殊模式下的 Redis 进程，主从库实例运行的同时，它也在运行。哨兵主要负责的就是三个任务：监控、选主（选择主库）和通知。

今天我们就深入学习一下哨兵机制。首先来说一下监控。



## 一、如何判断主库是否下线？

### 三个定时监控任务

![image-20221217175041331](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221217175041331.png)

三个定时任务：

```
每隔10秒， 每个Sentinel节点会向主节点和从节点发送info命令获取最新的拓扑结构。
每隔2秒， 每个Sentinel节点会向Redis数据节点的__sentinel__:hello 频道上发送该Sentinel节点对于主节点的判断以及当前Sentinel节点的信息
每隔1秒， 每个Sentinel节点会向主节点、 从节点、 其余Sentinel节点发送一条ping命令做一次心跳检测， 来确认这些节点当前是否可达。
```

**每隔10秒**， 每个Sentinel节点会向主节点和从节点发送info命令获取最新的拓扑结构。

执行 info 的结果是什么样的？

```
在主节点上执行 info replication 的结果：
# Replication
role:master
connected_slaves:2
slave0:ip=127.0.0.1,port=6380,state=online,offset=4917,lag=1
slave1:ip=127.0.0.1,port=6381,state=online,offset=4917,lag=1
```

定时任务的作用：

- 通过向主节点执行info命令， 获取从节点的信息， 这也是为什么 Sentinel 节点不需要显式配置监控从节点。  
- 当有新的从节点加入时都可以立刻感知出来。  
- 节点不可达或者故障转移后， 可以通过info命令实时更新节点拓扑信息。

**每隔2秒**

![image-20221217175732219](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221217175732219.png)

哨兵是如何感知其他哨兵存在的呢？

**每隔1秒**

![image-20221217180039020](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221217180039020.png)



Redis 源码中包含了一个名为 sentinel.conf 的文件，运行一个 Sentinel 所需的最少配置如下所示：

```
sentinel monitor mymaster 127.0.0.1 6379 2
sentinel down-after-milliseconds mymaster 60000
sentinel failover-timeout mymaster 180000
sentinel parallel-syncs mymaster 1

sentinel monitor resque 192.168.1.3 6380 4
sentinel down-after-milliseconds resque 10000
sentinel failover-timeout resque 180000
sentinel parallel-syncs resque 5
```

第一行配置指示 Sentinel 去监视一个名为 mymaster 的主服务器， 这个主服务器的 IP 地址为 127.0.0.1 ， 端口号为 6379 ， 而将这个主服务器判断为失效至少需要 2 个 Sentinel 同意 （只要同意 Sentinel 的数量不达标，自动故障迁移就不会执行）。

### 1.1 主观下线和客观下线

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202210142201865.png" alt="image-20221014220135766" style="zoom: 67%;" />

- down-after-milliseconds 选项指定了 Sentinel 认为服务器已经断线所需的毫秒数。

如果服务器在给定的毫秒数之内， 没有返回 Sentinel 发送的 PING 命令的回复， 或者返回一个错误， 那么 Sentinel 将这个服务器标记为主观下线（subjectively down，简称 SDOWN ）。

不过只有一个 Sentinel 将服务器标记为主观下线并不一定会引起服务器的自动故障迁移： 只有在足够数量的 Sentinel 都将一个服务器标记为主观下线之后， 服务器才会被标记为客观下线（objectively down， 简称 ODOWN ）， 这时自动故障迁移才会执行。

将服务器标记为客观下线所需的 Sentinel 数量由对主服务器的配置决定。（具体的配置是什么呢？）

一个 Sentinel 可以通过向另一个 Sentinel 发送 SENTINEL is-master-down-by-addr 命令来询问对方是否认为给定的服务器已下线。

如果 master-down-after-milliseconds 选项的值为 30000 毫秒（30 秒）， 那么只要服务器能在每 29 秒之内返回至少一次有效回复， 这个服务器就仍然会被认为是处于正常状态的。

每个 Sentinel 以每秒钟一次的频率向它所知的主服务器、从服务器以及其他 Sentinel 实例发送一个 PING 命令。

当没有足够数量的 Sentinel 同意主服务器已经下线， 主服务器的客观下线状态就会被移除。 当主服务器重新向 Sentinel 的 PING 命令返回有效回复时， 主服务器的主观下线状态就会被移除。







## 二、如何选定新主库？

### 2.1 三轮选举

首先要过滤掉不适合做主库的从库。

第一轮：优先级最高的从库得分高。

第二轮：和旧主库同步程度最接近的从库得分高。

第三轮：ID 号小的从库得分高。

### 2.2 由哪个哨兵执行主从切换？

## 三、将新主库通知给从库和客户端



### 3.1 哨兵是如何知道从库的 IP 地址和端口的？

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202210172154962.png" alt="image-20221017215455883" style="zoom:67%;" />

自动发现哨兵和从服务器

你无须为运行的每个 Sentinel 分别设置其他 Sentinel 的地址， 因为 Sentinel 可以通过发布与订阅功能来自动发现正在监视相同主服务器的其他 Sentinel ， 这一功能是通过向频道 sentinel:hello 发送信息来实现的。

每个 Sentinel 会以每两秒一次的频率， 通过发布与订阅功能， 向被它监视的所有主服务器和从服务器的 **sentinel**:hello 频道发送一条信息， 信息中包含了 Sentinel 的 IP 地址、端口号和运行 ID （runid）。

### 3.2 基于 pub/sub 机制的客户端事件通知



## 致谢

http://www.redis.cn/topics/sentinel.html

https://redis.io/docs/management/sentinel

本文为个人理解，如有误，欢迎交流指正。公众号【】



推广：年末面试季，Redis的这些高可用特性你能回答全面吗？