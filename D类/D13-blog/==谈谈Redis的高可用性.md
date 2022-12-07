# 谈谈Redis的高可用性



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

# 主库挂了，如何恢复数据？

AOF、RDB

AOF日志文件太大了怎么办？

那Redis是怎么判断日志太太的呢？

# 小结

本文为个人理解，如有误，欢迎交流指正。公众号【】



推广：年末面试季，Redis的这些高可用特性你能回答全面吗？