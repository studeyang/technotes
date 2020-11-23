> 来源：极客时间《Kafka核心技术与实战》

# 09 | 生产者消息分区机制原理剖析

在使用 Apache Kafka 生产和消费消息的时候，如何将大的数据量均匀地分配到 Kafka 的各个 Broker 上？

今天就来说说 Kafka 生产者如何实现这个需求。

**为什么要分区？**

Kafka 的消息组织方式实际上是三级结构：主题 - 分区 - 消息。主题下的每条消息只会保存在某一个分区中，而不会在多个分区中被保存多份。官网上的这张图非常清晰地展示了 Kafka 的三级结构，如下所示：

![image-20201123223445119](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201123223445.png)

Kafka 为什么使用分区的概念而不是直接使用多个主题呢？

- 提供负载均衡的能力

- 实现系统的高伸缩性（Scalability）

  不同的分区能够被放置到不同节点的机器上，而数据的读写操作也都是针对分区这个粒度而进行的，这样每个节点的机器都能独立地执行各自分区的读写请求处理。

- 增加整体系统的吞吐量

  我们还可以通过添加新的节点机器来增加整体系统的吞吐量。

除了提供负载均衡这种最核心的功能之外，利用分区也可以实现其他一些业务级别的需求，比如实现业务级别的消息顺序的问题。

**分区策略都有哪些？**

- 自定义分区策略

  在编写生产者程序时，编写一个具体的类实现`org.apache.kafka.clients.producer.Partitioner`接口。这个接口定义了两个方法：partition() 和 close()。

  ```java
  int partition(String topic, 
                Object key, 
                byte[] keyBytes, 
                Object value, 
                byte[] valueBytes, 
                Cluster cluster);
  ```

- 轮询策略

  也称 Round-robin 策略，即顺序分配。

  <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201123224819.png" alt="image-20201123224819043" style="zoom:40%;" align="left" />

  轮询策略是 Kafka Java 生产者 API 默认提供的分区策略。

- 随机策略

  也称 Randomness 策略。所谓随机就是我们随意地将消息放置到任意一个分区上，如下面这张图所示。

  <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201123225047.png" alt="image-20201123225047297" style="zoom:40%;" align="left"/>

  实现随机策略版的 partition 方法如下：

  ```java
  int partition(String topic, Object key, byte[] keyBytes, 
                Object value, byte[] valueBytes, Cluster cluster) {
      // 计算出该主题总的分区数
      List<PartitionInfo> partitions = cluster.partitionsForTopic(topic);
      return ThreadLocalRandom.current().nextInt(partitions.size());
  }
  ```

  随机策略是老版本生产者使用的分区策略。

- 按消息键保序策略

  也称 Key-ordering 策略。Kafka 允许为每条消息定义消息键，简称为 Key。一旦消息被定义了 Key，那么就可以保证同一个 Key 的所有消息都进入到相同的分区里面，由于每个分区下的消息处理都是有顺序的，故这个策略被称为按消息键保序策略，如下图所示。

  <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201123225837.png" alt="image-20201123225837947" style="zoom:40%;" align="left" />

  实现这个策略的 partition 方法如下：

  ```java
  int partition(String topic, Object key, byte[] keyBytes, 
                Object value, byte[] valueBytes, Cluster cluster) {
      // 计算出该主题总的分区数
      List<PartitionInfo> partitions = cluster.partitionsForTopic(topic);
      return Math.abs(key.hashCode()) % partitions.size();
  }
  ```

- 其他分区策略

  针对大规模的 Kafka 集群，可以采用按地理位置的分区策略。假如这个集群中必然有一部分机器在北京，另外一部分机器在广州。

  如果你需要把南北方注册用户的注册消息正确地发送到位于南北方的不同机房中，实现如下：

  ```java
  int partition(String topic, Object key, byte[] keyBytes, 
                Object value, byte[] valueBytes, Cluster cluster) {
      // 计算出该主题总的分区数
      List<PartitionInfo> partitions = cluster.partitionsForTopic(topic);
      return partitions.stream()
        .filter(p -> isSouth(p.leader().host()))
        .map(PartitionInfo::partition)
        .findAny()
        .get();
  }
  ```

  我们可以从所有分区中找出那些 Leader 副本在南方的所有分区，然后随机挑选一个进行消息发送。









