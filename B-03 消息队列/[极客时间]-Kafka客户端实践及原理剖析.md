> 来源：极客时间《Kafka核心技术与实战》

# 09 | 生产者消息分区机制

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

# 10 | 生产者压缩算法

压缩（compression），具体来说就是用 CPU 时间去换磁盘空间或网络 I/O 传输量。

**怎么压缩？**

Kafka 的消息层次都分为两层：消息集合（message set）以及消息（message）。一个消息集合中包含若干条日志项（record item），而日志项才是真正封装消息的地方。Kafka 底层的消息日志由一系列消息集合日志项组成。Kafka 通常不会直接操作具体的一条条消息，它总是在消息集合这个层面上进行写入操作。

目前 Kafka 共有两大类消息模式，分别为 V1 版本和 V2 版本。V2 版本是 Kafka 0.11.0.0 中正式引入的。

V2 版本把消息的公共部分抽取出来放到外层消息集合里面，这样就不用每条消息都保存这些信息了。

V2 版本还有一个和压缩息息相关的改进，就是保存压缩消息的方法发生了变化。之前 V1 版本中保存压缩消息的方法是把多条消息进行压缩然后保存到外层消息的消息体字段中；而 V2 版本的做法是对整个消息集合进行压缩。

**何时压缩？**

压缩可能发生在两个地方：生产者端和 Broker 端。

生产者程序中配置 compression.type 参数即表示启用指定类型的压缩算法。比如下面这段程序代码展示了如何构建一个开启 GZIP 的 Producer 对象：

```java
Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("acks", "all");
props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
// 开启 GZIP 压缩
props.put("compression.type", "gzip");

Producer<String, String> producer = new KafkaProducer<>(props);
```

大部分情况下 Broker 从 Producer 端接收到消息后仅仅是原封不动地保存而不会对其进行任何修改。但有两种例外情况就可能让 Broker 重新压缩消息。

情况一：Broker 端指定了和 Producer 端不同的压缩算法。

如果 Broker 端设置了与 Producer 端不同的 compression.type 值，就会发生压缩/解压缩操作。这个参数的默认值是 `producer`，表示使用 Producer 端的压缩算法。

情况二：Broker 端发生了消息格式转换。

为了兼容老版本的格式，Broker 端会对新版本消息执行向老版本格式的转换。这个过程中会涉及消息的解压缩和重新压缩。

**何时解压缩？**

通常来说解压缩发生在消费者程序中。那 Consumer 怎么知道这些消息是用何种压缩算法压缩的呢？

Kafka 会将启用了哪种压缩算法封装进消息集合中，这样当 Consumer 读取到消息集合时，它自然就知道了这些消息使用的是哪种压缩算法。

除了在 Consumer 端解压缩，Broker 端也会进行解压缩，目的就是为了对消息执行各种验证。

**各种压缩算法对比**

在 Kafka 2.1.0 版本之前，Kafka 支持 3 种压缩算法：GZIP、Snappy 和 LZ4。

从 2.1.0 开始，Kafka 正式支持 Zstandard 算法（简写为 zstd）。它是 Facebook 开源的一个压缩算法，能够提供超高的压缩比（compression ratio）。

衡量压缩算法有两个重要的指标：一个指标是压缩比；另一个指标就是压缩 / 解压缩吞吐量。

> 压缩比：原先占 100 份空间的东西经压缩之后变成了占 20 份空间，那么压缩比就是 5，压缩比越高越好；
>
> 吞吐量：比如每秒能压缩或解压缩多少 MB 的数据。吞吐量也是越高越好；

下面这张表是 Facebook Zstandard 官网提供的一份压缩算法 benchmark 比较结果：

![image-20201124230704644](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201124230704.png)

吞吐量方面：LZ4 > Snappy > zstd 和 GZIP；

压缩比方面，zstd > LZ4 > GZIP > Snappy。

**最佳实践**

何时启用压缩是比较合适的时机呢？

启用压缩的一个条件就是 Producer 程序运行机器上的 CPU 资源要很充足。如果 Producer 运行机器本身 CPU 已经消耗殆尽了，那么启用消息压缩无疑是雪上加霜，只会适得其反。

如果 CPU 资源充足，且你的环境中带宽资源有限，那么我建议你开启压缩。

一旦启用压缩，解压缩是不可避免的事情。但要尽量规避掉那些意料之外的解压缩，比如兼容老版本消息格式而引起的解压缩。

# 11 | 无消息丢失配置怎么实现？

**Kafka 到底在什么情况下才能保证消息不丢失呢？**

一句话概括，Kafka 只对“已提交”的消息（committed message）做有限度的持久化保证。

这句话里面有两个核心要素。

第一个核心要素是“已提交的消息”。当 Kafka 的若干个 Broker 成功地接收到一条消息并写入到日志文件后，它们会告诉生产者程序这条消息已成功提交。此时，这条消息在 Kafka 看来就正式变为“已提交”消息了。

第二个核心要素就是“有限度的持久化保证”。Kafka 不可能保证在任何情况下都做到不丢失消息。举个极端点的例子，如果地球都不存在了，Kafka 显然不能保存任何消息了。

Kafka 是能做到不丢失消息的，只不过这些消息必须是已提交的消息，而且还要满足一定的条件。假如你的消息保存在 N 个 Kafka Broker 上，那么这个前提条件就是这 N 个 Broker 中至少有 1 个存活。

**消息丢失案例1：生产者程序丢失数据**

目前 Kafka Producer 是异步发送消息的，也就是说如果你调用的是 `producer.send(msg)`这个 API，那么它通常会立即返回，但此时你不能认为消息发送已成功完成。如果出现消息丢失，我们是无法知晓的。

Producer 永远要使用带有回调通知的方法发送 API，即使用`producer.send(msg, callback)`。

**消息丢失案例2：消费者程序丢失数据**

Consumer 程序有个“位移”的概念，表示的是这个 Consumer 当前消费到的 Topic 分区的位置。

![image-20201125224030536](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201125224030.png)

保证 Consumer 端的消息不丢失，可以维持先消费消息，再更新位移的顺序。当然，这种处理方式可能带来的问题是消息的重复处理。

还有一种比较隐蔽的消息丢失场景。Consumer 程序从 Kafka 获取到消息后开启了多个线程异步处理消息，而 Consumer 程序自动地向前更新位移。假如其中某个线程运行失败了，它负责的消息没有被成功处理，但位移已经被更新了，因此这条消息对于 Consumer 而言实际上是丢失了。

这个问题的解决方案很简单：如果是多线程异步处理消费消息，Consumer 程序不要开启自动提交位移，而是要应用程序手动提交位移。

**最佳实践**

Producer：

1. 不要使用 producer.send(msg)，而要使用 producer.send(msg, callback)。
2. 设置 acks = all。acks 是 Producer 的一个参数，代表了你对“已提交”消息的定义。如果设置成 all，则表明所有副本 Broker 都要接收到消息，该消息才算是“已提交”。
3. 设置 retries 为一个较大的值。这里的 retries 同样是 Producer 的参数，对应前面提到的 Producer 自动重试。当出现网络的瞬时抖动时，消息发送可能会失败，此时配置了 retries > 0 的 Producer 能够自动重试消息发送，避免消息丢失。

Broker：

1. 设置 unclean.leader.election.enable = false。它控制的是哪些 Broker 有资格竞选分区的 Leader。如果一个 Broker 落后原先的 Leader 太多，那么它一旦成为新的 Leader，必然会造成消息的丢失。故一般都要将该参数设置成 false，即不允许这种情况的发生。
2. 设置 replication.factor >= 3。其实这里想表述的是，最好将消息多保存几份，毕竟目前防止消息丢失的主要机制就是冗余。
3. 设置 min.insync.replicas > 1。控制的是消息至少要被写入到多少个副本才算是“已提交”。设置成大于 1 可以提升消息持久性。在实际环境中千万不要使用默认值 1。
4. 确保 replication.factor > min.insync.replicas。如果两者相等，那么只要有一个副本挂机，整个分区就无法正常工作了。我们不仅要改善消息的持久性，防止数据丢失，还要在不降低可用性的基础上完成。推荐设置成 replication.factor = min.insync.replicas + 1。

Consumer：

1. 确保消息消费完成再提交。Consumer 端有个参数 enable.auto.commit，最好把它设置成 false，并采用手动提交位移的方式。就像前面说的，这对于单 Consumer 多线程处理的场景而言是至关重要的。

# 12 | Kafka 拦截器























