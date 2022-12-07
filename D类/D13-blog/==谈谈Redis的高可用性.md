# 前言

前几天在知乎看到一个问题：如何建立自己的知识体系？在一篇高赞回答中讲述了建立“外脑”是关键。

> 大脑是用来思考的，不是用来记忆的。

> 查理芒格图片

我很认同这样的看法，我的账号名为“杨同学technotes”，technotes 源于我最近几年总结的 github 项目，意为“技术笔记”，也就是“外脑”的意思。我将一直往里面填充东西，不断优化内容，欢迎关注。

> Github: https://github.com/studeyang/technotes
>
> technotes站点：https://www.dbses.cn/technotes

本文来自我的 technotes Redis篇。

# 谈谈Redis的高可用性

下面是一张 Redis 全景图，我觉得画得非常全面。

> 图源：极客时间蒋德均老师的《Redis核心技术与实战》课程



# 数据不可用怎么办？

Redis主从库模式

数据同步

**注意**: 从 Redis 5 起使用 [REPLICAOF](https://www.redis.com.cn/commands/replicaof.html) 替代 [SLAVEOF](https://www.redis.com.cn/commands/slaveof.html) 。当然，为了向后兼容 [SLAVEOF](https://www.redis.com.cn/commands/slaveof.html) 命令仍然可用。

![image-20221124151152754](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221124151152754.png)

> 这里我解释一下 Replication，中文翻译为副本，Redis 概念中 Replication 分为 Master Replication 和 Slave Replication，即主从副本。

# 主从库间网络断了怎么办？

repl_backlog_buffer



# 主库挂了，如何不间断服务？

Redis哨兵机制

![图源网络](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221124174919856.png)

# 主库挂了，如何快速恢复数据？

我们知道，Redis 是内存数据库，一旦宕机，内存里的数据将会清空。因此，Redis 提供了两种数据持久化的方法，分别是 AOF 和 RDB。



RDB xxx。

AOF xxx。



Redis 4.0 中提出了一个混合使用 AOF 和 RDB 的方法。

AOF 日志文件太大了怎么办？

那Redis是怎么判断日志太太的呢？

# 小结

本文为个人理解，如有误，欢迎交流指正。公众号【】



推广：年末面试季，Redis的这些高可用特性你能回答全面吗？