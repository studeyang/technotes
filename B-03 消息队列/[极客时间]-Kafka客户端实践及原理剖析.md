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

**什么是拦截器？**

拦截器的基本思想就是允许应用程序在不修改逻辑的情况下，动态地实现一组可插拔的事件处理逻辑链。

它们插入的逻辑可以是修改待发送的消息，也可以是创建新的消息，甚至是丢弃消息。这些功能都是以配置拦截器类的方式动态插入到应用程序中的，故可以快速地切换不同的拦截器而不影响主程序逻辑。

作为一个非常小众的功能，Kafka 拦截器自 0.10.0.0 版本被引入后并未得到太多的实际应用。

**Kafka 拦截器**

Kafka 拦截器分为生产者拦截器和消费者拦截器。

生产者拦截器允许你在发送消息前以及消息提交成功后植入你的拦截器逻辑；

而消费者拦截器支持在消费消息前以及提交位移后编写特定逻辑。

添加拦截器的代码如下：

```java
Properties props = new Properties();
List<String> interceptors = new ArrayList<>();
interceptors.add("com.yourcompany.kafkaproject.interceptors.AddTimestampInterceptor"); // 拦截器 1
interceptors.add("com.yourcompany.kafkaproject.interceptors.UpdateCounterInterceptor"); // 拦截器 2
props.put(ProducerConfig.INTERCEPTOR_CLASSES_CONFIG, interceptors);
```

其中 `AddTimestampInterceptor`和`UpdateCounterInterceptor`要继承`org.apache.kafka.clients.producer.ProducerInterceptor `接口。

```java
/** 方法中省略入参和出参类型 */
public interface ProducerInterceptor {
  /** 该方法会在消息发送之前被调用 */
  void onSend();
  /** 该方法会在消息成功提交或发送失败之后被调用，且要早于callback的调用 */
  void onAcknowledgement();
}
```

> 注意：
>
> 1. `onAcknowledgement`方法和`onSend`不是在同一个线程中被调用的，因此如果你在这两个方法中调用了某个共享可变对象，一定要保证线程安全；
> 2. `onAcknowledgement`这个方法处在 Producer 发送的主路径中，所以最好别放一些太重的逻辑进去，否则你会发现你的 Producer TPS 直线下降；

指定消费者拦截器也是同样的方法，具体的实现类要实现`org.apache.kafka.clients.consumer.ConsumerInterceptor`接口。

```java
/** 方法中省略入参和出参类型 */
public interface ConsumerInterceptor {
  /** 该方法在消息返回给Consumer程序之前调用 */
  void onConsume();
  /** Consumer在提交位移之后调用该方法 */
  void onCommit();
}
```

**典型使用场景**

Kafka 拦截器可以应用于包括客户端监控、端到端系统性能检测、消息审计等多种功能在内的场景。

**使用案例**

某公司的某个业务只有一个 Producer 和一个 Consumer，他们想知道该业务消息从被生产出来到最后被消费的平均总时长是多少。了解了拦截器后，可以用拦截器来满足这个需求。

既然是要计算总延时，那么一定要有个公共的地方来保存它，并且这个公共的地方还是要让生产者和消费者程序都能访问的。在这个例子中，我们假设数据被保存在 Redis 中。

我们先来实现生产者拦截器：

```java
public class AvgLatencyProducerInterceptor implements ProducerInterceptor<String, String> {
 
    private Jedis jedis; // 省略 Jedis 初始化
 
    @Override
    public ProducerRecord<String, String> onSend(ProducerRecord<String, String> record) {
        jedis.incr("totalSentMessage");
        return record;
    }
    @Override
    public void onAcknowledgement(RecordMetadata metadata, Exception exception) {
    }
    @Override
    public void close() {
    }
    @Override
    public void configure(Map<java.lang.String, ?> configs) {
    }
}
```

再来实现消费者端的拦截器：

```java
public class AvgLatencyConsumerInterceptor implements ConsumerInterceptor<String, String> {

    private Jedis jedis; // 省略 Jedis 初始化

    @Override
    public ConsumerRecords<String, String> onConsume(ConsumerRecords<String, String> records) {
        long lantency = 0L;
        for (ConsumerRecord<String, String> record : records) {
            lantency += (System.currentTimeMillis() - record.timestamp());
        }
        jedis.incrBy("totalLatency", lantency);
        long totalLatency = Long.parseLong(jedis.get("totalLatency"));
        long totalSentMsgs = Long.parseLong(jedis.get("totalSentMessage"));
        jedis.set("avgLatency", String.valueOf(totalLatency / totalSentMsgs));
        return records;
    }
    @Override
    public void onCommit(Map<TopicPartition, OffsetAndMetadata> offsets) {
    }
    @Override
    public void close() {
    }
    @Override
    public void configure(Map<String, ?> configs) {
    }
}
```

# 13 | Java生产者是如何管理TCP连接的？

Apache Kafka 的所有通信都是基于 TCP 的，而不是基于 HTTP 或其他协议。无论是生产者、消费者，还是 Broker 之间的通信都是如此。

**为何采用 TCP?**

从社区的角度来看，在开发客户端时，人们能够利用 TCP 本身提供的一些高级功能，比如多路复用请求以及同时轮询多个连接的能力。

> 所谓的多路复用请求，即 multiplexing request，是指将两个或多个数据流合并到底层单一物理连接中的过程。TCP 的多路复用请求会在一条物理连接上创建若干个虚拟连接，每个虚拟连接负责流转各自对应的数据流。其实严格来说，TCP 并不能多路复用，它只是提供可靠的消息交付语义保证，比如自动重传丢失的报文。
>

除了 TCP 提供的这些高级功能有可能被 Kafka 客户端的开发人员使用之外，社区还发现，目前已知的 HTTP 库在很多编程语言中都略显简陋。

基于这两个原因，Kafka 社区决定采用 TCP 协议作为所有请求通信的底层协议。

**Kafka 生产者程序概览**

Kafka 的 Java 生产者 API 主要的对象就是 KafkaProducer。通常我们开发一个生产者的步骤有 4 步。

```java
// 第 1 步：构造生产者对象所需的参数对象。
Properties props = new Properties ();
props.put(“参数 1”, “参数 1 的值”)；
props.put(“参数 2”, “参数 2 的值”)；
// ……
// 第 2 步：利用第 1 步的参数对象，创建 KafkaProducer 对象实例。
try (Producer<String, String> producer = new KafkaProducer<>(props)) {
    // 第 3 步：使用 KafkaProducer 的 send 方法发送消息。
    producer.send(new ProducerRecord<String, String>(……), callback);
    // ……
}
// 第 4 步：调用 KafkaProducer 的 close 方法关闭生产者并释放各种系统资源。
```

当我们开发一个 Producer 应用时，生产者会向 Kafka 集群中指定的主题（Topic）发送消息，这必然涉及与 Kafka Broker 创建 TCP 连接。那么，Kafka 的 Producer 客户端是如何管理这些 TCP 连接的呢？

要回答这个问题，我们首先要弄明白生产者代码是什么时候创建 TCP 连接的。

**何时创建 TCP 连接？**

在创建 KafkaProducer 实例时，生产者应用会在后台创建并启动一个名为 Sender 的线程，该 Sender 线程开始运行时首先会创建与 Broker 的连接。

为了说明这一点，测试环境中我为 bootstrap.servers 配置了 localhost:9092、localhost:9093 来模拟不同的 Broker。下面是测试环境的日志：

```
[2018-12-09 09:35:45,620] DEBUG [Producer clientId=producer-1] Initialize connection to node localhost:9093 (id: -2 rack: null) for sending metadata request (org.apache.kafka.clients.NetworkClient:1084)
```

```
[2018-12-09 09:35:45,622] DEBUG [Producer clientId=producer-1] Initiating connection to node localhost:9093 (id: -2 rack: null) using address localhost/127.0.0.1 (org.apache.kafka.clients.NetworkClient:914)
```

```
[2018-12-09 09:35:45,814] DEBUG [Producer clientId=producer-1] Initialize connection to node localhost:9092 (id: -1 rack: null) for sending metadata request (org.apache.kafka.clients.NetworkClient:1084)
```

```
[2018-12-09 09:35:45,815] DEBUG [Producer clientId=producer-1] Initiating connection to node localhost:9092 (id: -1 rack: null) using address localhost/127.0.0.1 (org.apache.kafka.clients.NetworkClient:914)
```

```
[2018-12-09 09:35:45,828] DEBUG [Producer clientId=producer-1] Sending metadata request (type=MetadataRequest, topics=) to node localhost:9093 (id: -2 rack: null) (org.apache.kafka.clients.NetworkClient:1068)
```

Producer 会连接 bootstrap.servers 参数指定的所有 Broker。

> bootstrap.servers 参数：指定了这个 Producer 启动时要连接的 Broker 地址。如果你为这个参数指定了 1000 个 Broker 连接信息，你的 Producer 启动时会首先创建与这 1000 个 Broker 的 TCP 连接。
>
> 因引在实际使用过程中，通常你指定 3～4 台就足以了。因为 Producer 一旦连接到集群中的任一台 Broker，就能拿到整个集群的 Broker 信息，故没必要为 bootstrap.servers 指定所有的 Broker。

日志输出中的最后一行表明 Producer 向某一台 Broker 发送了 METADATA 请求，尝试获取集群的元数据信息。

目前我们的结论是这样的：TCP 连接是在创建 KafkaProducer 实例时建立的。

TCP 连接还可能在两个地方被创建：一个是在更新元数据后，另一个是在消息发送时。当 Producer 更新了集群的元数据信息之后，如果发现与某些 Broker 当前没有连接，那么它就会创建一个 TCP 连接。同样地，当要发送消息时，Producer 发现尚不存在与目标 Broker 的连接，也会创建一个。

> 为什么说是可能？因为这两个地方并非总是创建 TCP 连接。

接下来，我们来看看 Producer 更新集群元数据信息的两个场景。

场景一：当 Producer 尝试给一个不存在的主题发送消息时，Broker 会告诉 Producer 说这个主题不存在。此时 Producer 会发送 METADATA 请求给 Kafka 集群，去尝试获取最新的元数据信息。

场景二：Producer 通过 metadata.max.age.ms 参数定期地去更新元数据信息。该参数的默认值是 300000，即 5 分钟，也就是说不管集群那边是否有变化，Producer 每 5 分钟都会强制刷新一次元数据以保证它是最及时的数据。

**何时关闭 TCP 连接？**

Producer 端关闭 TCP 连接的方式有两种：一种是用户主动关闭；一种是 Kafka 自动关闭。

先说第一种。这里的主动关闭实际上是广义的主动关闭，甚至包括用户调用 kill -9 主动“杀掉”Producer 应用。当然最推荐的方式还是调用 producer.close() 方法来关闭。

第二种是 Kafka 帮你关闭，这与 Producer 端参数 connections.max.idle.ms 的值有关。默认情况下该参数值是 9 分钟，即如果在 9 分钟内没有任何请求“流过”某个 TCP 连接，那么 Kafka 会主动帮你把该 TCP 连接关闭。用户可以在 Producer 端设置 connections.max.idle.ms=-1 禁掉这种机制。一旦被设置成 -1，TCP 连接将成为永久长连接。当然这只是软件层面的“长连接”机制，由于 Kafka 创建的这些 Socket 连接都开启了 keepalive，因此 keepalive 探活机制还是会遵守的。

值得注意的是，在第二种方式中，TCP 连接是在 Broker 端被关闭的，但其实这个 TCP 连接的发起方是客户端，因此在 TCP 看来，这属于被动关闭的场景，即 passive close。被动关闭的后果就是会产生大量的 CLOSE_WAIT 连接，因此 Producer 端或 Client 端没有机会显式地观测到此连接已被中断。

# 14 | 幂等生产者和事务生产者是一回事吗？

消息交付可靠性保障有以下三种：

- 最多一次（at most once）：消息可能会丢失，但绝不会被重复发送。
- 至少一次（at least once）：消息不会丢失，但有可能被重复发送。
- 精确一次（exactly once）：消息不会丢失，也不会被重复发送。

目前，Kafka 默认提供的交付可靠性保障是第二种。

什么情况下 Kafka 发送至少一次消息？如果 Broker 的应答没有成功发送回 Producer 端，比如网络出现瞬时抖动，那么 Producer 就无法确定消息是否真的提交成功了。因此，它只能选择重试。

Kafka 也可以提供最多一次交付保障，只需要让 Producer 禁止重试即可。这样一来，消息要么写入成功，要么写入失败，但绝不会重复发送。

不过大部分用户还是希望消息只会被交付一次，这样的话，消息既不会丢失，也不会被重复处理。或者说，即使 Producer 端重复发送了相同的消息，Broker 端也能做到自动去重。在下游 Consumer 看来，消息依然只有一条。

那么 Kafka 是怎么做到精确一次的呢？简单来说，是通过两种机制：幂等性（Idempotence）和事务（Transaction）。

**什么是幂等性（Idempotence）？**

幂等指的是某些操作或函数能够被执行多次，但每次得到的结果都是不变的。

幂等性最大的优势在于我们可以安全地重试任何幂等性操作，反正它们也不会破坏我们的系统状态。

**幂等性 Producer**

在 Kafka 中，Producer 默认不是幂等性的。在 0.11.0.0 版本引入了幂等性功能。使用方法如下：

```
props.put("enable.idempotence", ture)
或 props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true)
```

具体的原理很简单，就是经典的用空间去换时间的优化思路，即在 Broker 端多保存一些字段。当 Producer 发送了具有相同字段值的消息后，Broker 能够自动知晓这些消息已经重复了，于是可以在后台默默地把它们“丢弃”掉。

> 当然，实际的实现原理并没有这么简单，但你大致可以这么理解。

实际上，我们必须要了解幂等性 Producer 的作用范围。

首先，它只能保证单分区上的幂等性，即一个幂等性 Producer 能够保证某个主题的一个分区上不出现重复消息，它无法实现多个分区的幂等性。

其次，它只能实现单会话上的幂等性，不能实现跨会话的幂等性。当你重启了 Producer 进程之后，这种幂等性保证就丧失了。

那如果我想实现多分区以及多会话上的消息无重复，应该怎么做呢？答案就是事务（transaction）或者依赖事务型 Producer。

**事务（transaction）**

Kafka 自 0.11 版本开始也提供了对事务的支持，目前主要是在 read committed 隔离级别上做事情。它能保证多条消息原子性地写入到目标分区，同时也能保证 Consumer 只能看到事务成功提交的消息。

**事务型 Producer**

事务型 Producer 能够保证将消息原子性地写入到多个分区中。这批消息要么全部写入成功，要么全部失败。另外，事务型 Producer 也不惧进程的重启。Producer 重启回来后，Kafka 依然保证它们发送消息的精确一次处理。

使用事务型 Producer 的配置如下：

- 开启 enable.idempotence = true
- 设置 Producer 端参数 transctional.id。最好为其设置一个有意义的名字

此外，你还需要在 Producer 代码中做一些调整，如这段代码所示：

```java
producer.initTransactions();
try {
    producer.beginTransaction();
    producer.send(record1);
    producer.send(record2);
    producer.commitTransaction();
} catch (KafkaException e) {
    producer.abortTransaction();
}
```

这段代码能够保证 Record1 和 Record2 被当作一个事务统一提交到 Kafka，要么它们全部提交成功，要么全部写入失败。

实际上即使写入失败，Kafka 也会把它们写入到底层的日志中，也就是说 Consumer 还是会看到这些消息。因此在 Consumer 端，读取事务型 Producer 发送的消息也是需要一些变更的。修改起来也很简单，设置 isolation.level 参数的值即可。当前这个参数有两个取值：

- read_uncommitted：这是默认值，表明 Consumer 能够读取到 Kafka 写入的任何消息，不论事务型 Producer 提交事务还是终止事务，其写入的消息都可以读取。很显然，如果你用了事务型 Producer，那么对应的 Consumer 就不要使用这个值。
- read_committed：表明 Consumer 只会读取事务型 Producer 成功提交事务写入的消息。当然了，它也能看到非事务型 Producer 写入的所有消息。

# 15 | 消费者组到底是什么？

**消费者组（Consumer Group）特性**

消费者组，即 Consumer Group，是 Kafka 提供的可扩展且具有容错性的消费者机制。

组内可以有多个消费者或消费者实例（Consumer Instance），它们共享一个公共的 ID，这个 ID 被称为 Group ID。组内的所有消费者协调在一起来消费订阅主题（Subscribed Topics）的所有分区（Partition）。当然，每个分区只能由同一个消费者组内的一个 Consumer 实例来消费。

Consumer Group 有下面这三个特性：

1. Consumer Group 下可以有一个或多个 Consumer 实例。这里的实例可以是一个单独的进程，也可以是同一进程下的线程。
2. Group ID 是一个字符串，在一个 Kafka 集群中是唯一的。
3. 主题的单个分区只能分配给 Consumer Group 的某个 Consumer 实例消费。当然也可以被其他的 Group 消费。

**Consumer Group 与传统的消息引擎模型**

传统的消息引擎模型有两大类，分别是点对点模型（即消息队列模型）和发布 / 订阅模型。

消息队列模型的特性在于消息一旦被消费，就会从队列中被删除，而且只能被下游的一个 Consumer 消费。很显然，这种模型的伸缩性（scalability）很差，因为下游的多个 Consumer 都要“抢”这个共享消息队列的消息。

发布 / 订阅模型倒是允许消息被多个 Consumer 消费，但它的问题也是伸缩性不高，因为每个订阅者都必须要订阅主题的所有分区。这种全量订阅的方式既不灵活，也会影响消息的真实投递效果。

Kafka 的 Consumer Group 避开了这两种模型的缺陷，同时又兼具它们的优点。如果所有实例都属于同一个 Group，那么它实现的就是消息队列模型；如果所有实例分别属于不同的 Group，那么它实现的就是发布 / 订阅模型。

当 Consumer Group 订阅了多个主题后，组内的每个实例不要求一定要订阅主题的所有分区，它只会消费部分分区中的消息。

**Group 里多少个 Consumer 合适？**

那么在实际使用场景中，我怎么知道一个 Group 下该有多少个 Consumer 实例呢？理想情况下，Consumer 实例的数量应该等于该 Group 订阅主题的分区总数。

举个简单的例子，假设一个 Consumer Group 订阅了 3 个主题，分别是 A、B、C，它们的分区数依次是 1、2、3，那么通常情况下，为该 Group 设置 6 个 Consumer 实例是比较理想的情形，因为它能最大限度地实现高伸缩性。

> 这里理论描述值与举例值矛盾啊！

你可能会问，我能设置小于或大于 6 的实例吗？当然可以！如果你有 3 个实例，那么平均下来每个实例大约消费 2 个分区（6 / 3 = 2）；如果你设置了 8 个实例，那么很遗憾，有 2 个实例（8 – 6 = 2）将不会被分配任何分区，它们永远处于空闲状态。因此，在实际使用过程中一般不推荐设置大于总分区数的 Consumer 实例。设置多余的实例只会浪费资源，而没有任何好处。

**Kafka 是怎么管理位移的？**

消费者在消费的过程中需要记录自己消费了多少数据，即消费位置信息。在 Kafka 中，这个位置信息有个专门的术语：位移（Offset）。

其实对于 Consumer Group 而言，它是一组 KV 对，Key 是分区，V 对应 Consumer 消费该分区的最新位移。

在新版本的 Consumer Group 中，Kafka 社区重新设计了 Consumer Group 的位移管理方式，采用了将位移保存在 Kafka 内部主题的方法。这个内部主题就是 __consumer_offsets。

**Consumer Group 端重平衡**

Rebalance 本质上是一种协议，规定了一个 Consumer Group 下的所有 Consumer 如何达成一致，来分配订阅 Topic 的每个分区。比如某个 Group 下有 20 个 Consumer 实例，它订阅了一个具有 100 个分区的 Topic。正常情况下，Kafka 平均会为每个 Consumer 分配 5 个分区。这个分配的过程就叫 Rebalance。

Rebalance 的触发条件有 3 个。

1. 组成员数发生变更。
2. 订阅主题数发生变更。
3. 订阅主题的分区数发生变更。

举个例子，假设目前某个 Consumer Group 下有两个 Consumer，比如 A 和 B，当第三个成员 C 加入时，Kafka 会触发 Rebalance，并根据默认的分配策略重新为 A、B 和 C 分配分区，如下图所示：

![image-20201203230433441](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201203230433.png)

Rebalance 之后的分配依然是公平的。

不过，Rebalance 也有一些缺陷。在 Rebalance 过程中，所有 Consumer 实例都会停止消费，等待 Rebalance 完成，这跟 JVM 垃圾回收的 stop the world 很类似。

其次，目前 Rebalance 的设计是所有 Consumer 实例共同参与，全部重新分配所有分区。其实更高效的做法是尽量减少分配方案的变动。这样的话，就不用重新创建连接其他 Broker 的 Socket 资源。

最后，Rebalance 实在是太慢了。曾经，有个国外用户的 Group 内有几百个 Consumer 实例，成功 Rebalance 一次要几个小时！这完全是不能忍受的。最悲剧的是，目前社区对此无能为力，至少现在还没有特别好的解决方案。所谓“本事大不如不摊上”，也许最好的解决方案就是避免 Rebalance 的发生吧。

# 16 | 揭开神秘的“位移主题”面纱

**引入位移主题的背景及原因**

老版本 Consumer 的位移管理是依托于 Apache ZooKeeper 的，它会自动或手动地将位移数据提交到 ZooKeeper 中保存。当 Consumer 重启后，它能自动从 ZooKeeper 中读取位移数据，从而在上次消费截止的地方继续消费。这种设计使得 Kafka Broker 不需要保存位移数据，减少了 Broker 端需要持有的状态空间，因而有利于实现高伸缩性。

但是，ZooKeeper 其实并不适用于这种高频的写操作，因此，Kafka 社区自 0.8.2.x 版本开始，就在酝酿修改这种设计，并最终在新版本 Consumer 中正式推出了全新的位移管理机制，也包括这个新的位移主题。

**位移主题的消息格式**

新版本 Consumer 的位移管理机制其实也很简单，就是将 Consumer 的位移数据作为一条条普通的 Kafka 消息，提交到 \_\_consumer_offsets 中。可以这么说，__consumer_offsets 的主要作用是保存 Kafka 消费者的位移信息。

那么这个主题存的是什么格式的消息呢？位移主题的 Key 中应该保存 3 部分内容：<Group ID，主题名，分区号 >。位移主题的消息体可以简单地认为就是保存了位移值。

实际上，位移主题的消息格式除了上面这种，还保存下面 2 种格式：

- 用于保存 Consumer Group 信息的消息

  它是用来注册 Consumer Group 的。

- 用于删除 Group 过期位移甚至是删除 Group 的消息

  这种格式有个专属的名字：tombstone 消息，即墓碑消息，也称 delete mark，它们指的是一个东西。这些消息只出现在源码中而不暴露给你。它的主要特点是它的消息体是 null，即空消息体。

一旦某个 Consumer Group 下的所有 Consumer 实例都停止了，而且它们的位移数据都已被删除时，Kafka 会向位移主题的对应分区写入 tombstone 消息，表明要彻底删除这个 Group 的信息。

**位移主题是怎么被创建的？**

通常来说，当 Kafka 集群中的第一个 Consumer 程序启动时，Kafka 会自动创建位移主题。位移主题就是普通的 Kafka 主题，那么它自然也有对应的分区数。但如果是 Kafka 自动创建的，分区数是怎么设置的呢？

这就要看 Broker 端参数 offsets.topic.num.partitions 的取值了。它的默认值是 50，因此 Kafka 会自动创建一个 50 分区的位移主题。

除了分区数，副本数或备份因子是怎么控制的呢？答案也很简单，这就是 Broker 端另一个参数 offsets.topic.replication.factor 要做的事情了。它的默认值是 3。

当然，你也可以选择手动创建位移主题，具体方法就是，在 Kafka 集群尚未启动任何 Consumer 之前，使用 Kafka API 创建它。手动创建的好处在于，你可以创建满足你实际场景需要的位移主题。比如很多人说 50 个分区对我来讲太多了，我不想要这么多分区，那么你可以自己创建它，不用理会 offsets.topic.num.partitions 的值。

> 不过我给你的建议是，还是让 Kafka 自动创建比较好。目前 Kafka 源码中有一些地方硬编码了 50 分区数，因此如果你自行创建了一个不同于默认分区数的位移主题，可能会碰到各种各种奇怪的问题。这是社区的一个 bug，目前代码已经修复了，但依然在审核中。

**什么地方会用到位移主题？**

目前 Kafka Consumer 提交位移的方式有两种：自动提交位移和手动提交位移。

Consumer 端有个参数叫 enable.auto.commit，如果值是 true，则 Consumer 在后台默默地为你定期提交位移，提交间隔由一个专属的参数 auto.commit.interval.ms 来控制。自动提交位移有一个显著的优点，就是省事，你不用操心位移提交的事情，就能保证消息消费不会丢失。但这一点同时也是缺点。因为它太省事了，以至于丧失了很大的灵活性和可控性，你完全没法把控 Consumer 端的位移管理。

> 自动提交位移还可能存在一个问题：只要 Consumer 一直启动着，它就会无限期地向位移主题写入消息。

手动提交位移，即设置 enable.auto.commit = false。一旦设置了 false，Consumer 应用就要承担起位移提交的责任。Kafka Consumer API 提供了位移提交的方法，如 consumer.commitSync 等。当调用这些方法时，Kafka 会向位移主题写入相应的消息。

**Kafka 怎么删除位移主题的过期消息？**

Kafka 是怎么删除位移主题中的过期消息的呢？答案就是 Compaction。

Kafka 使用 Compact 策略来删除位移主题中的过期消息，避免该主题无限膨胀。那么应该如何定义 Compact 策略中的过期呢？对于同一个 Key 的两条消息 M1 和 M2，如果 M1 的发送时间早于 M2，那么 M1 就是过期消息。Compact 的过程就是扫描日志的所有消息，剔除那些过期的消息，然后把剩下的消息整理在一起

这一张来自官网的图片，可以说明 Compact 过程。

![image-20201204234938194](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201204234943.png)

图中位移为 0、2 和 3 的消息的 Key 都是 K1。Compact 之后，分区只需要保存位移为 3 的消息，因为它是最新发送的。

Kafka 提供了专门的后台线程定期地巡检待 Compact 的主题，看看是否存在满足条件的可删除数据。这个后台线程叫 Log Cleaner。

> 很多实际生产环境中都出现过位移主题无限膨胀占用过多磁盘空间的问题，如果你的环境中也有这个问题，我建议你去检查一下 Log Cleaner 线程的状态，通常都是这个线程挂掉了导致的。

# 17 | 消费者组重平衡能避免吗？

要避免 Rebalance，还是要从 Rebalance 发生的时机入手。我们在前面说过，Rebalance 发生的时机有三个：

- 组成员数量发生变化
- 订阅主题数量发生变化
- 订阅主题的分区数发生变化

如果 Consumer Group 下的 Consumer 实例数量发生变化，就一定会引发 Rebalance，这是 Rebalance 发生的最常见的原因。后面两个通常都是运维的主动操作，所以它们引发的 Rebalance 大都是不可避免的。接下来，我们主要说说因为组成员数量变化而引发的 Rebalance 该如何避免。

通常来说，增加 Consumer 实例的操作都是计划内的，可能是出于增加 TPS 或提高伸缩性的需要。它不属于我们要规避的那类“不必要 Rebalance”。

Group 下实例数减少是我们要关注的。Coordinator 会在什么情况下认为某个 Consumer 实例已挂从而要退组呢？

**Kafka 如何感知 Consumer 是否挂掉？**

当 Consumer Group 完成 Rebalance 之后，每个 Consumer 实例都会定期地向 Coordinator 发送心跳请求，表明它还存活着。如果某个 Consumer 实例不能及时地发送这些心跳请求，Coordinator 就会认为该 Consumer 已经“死”了，从而将其从 Group 中移除，然后开启新一轮 Rebalance。Consumer 端有个参数，叫 session.timeout.ms，就是被用来表征此事的。该参数的默认值是 10 秒，即如果 Coordinator 在 10 秒之内没有收到 Group 下某 Consumer 实例的心跳，它就会认为这个 Consumer 实例已经挂了。

除了这个参数，Consumer 还提供了一个允许你控制发送心跳请求频率的参数，就是 heartbeat.interval.ms。这个值设置得越小，Consumer 实例发送心跳请求的频率就越高。

除了以上两个参数，Consumer 端还有一个参数，用于控制 Consumer 实际消费能力对 Rebalance 的影响，即 max.poll.interval.ms 参数。它限定了 Consumer 端应用程序两次调用 poll 方法的最大时间间隔。它的默认值是 5 分钟，表示你的 Consumer 程序如果在 5 分钟之内无法消费完 poll 方法返回的消息，那么 Consumer 会主动发起“离开组”的请求，Coordinator 也会开启新一轮 Rebalance。

**哪些 Rebalance 是不必要的？**

第一类非必要 Rebalance 是因为未能及时发送心跳，导致 Consumer 被“踢出”Group 而引发的。

因此，你需要仔细地设置 session.timeout.ms 和 heartbeat.interval.ms的值。要保证 Consumer 实例在被判定为“dead”之前，能够发送至少 3 轮的心跳请求，即 session.timeout.ms >= 3 * heartbeat.interval.ms。

我在这里给出一些推荐数值，你可以“无脑”地应用在你的生产环境中。

- 设置 session.timeout.ms = 6s。
- 设置 heartbeat.interval.ms = 2s。

将 session.timeout.ms 设置成 6s 主要是为了让 Coordinator 能够更快地定位已经挂掉的 Consumer，早日把它们踢出 Group。

第二类非必要 Rebalance 是 Consumer 消费时间过长导致的。我之前有一个客户，在他们的场景中，Consumer 消费数据时需要将消息处理之后写入到 MongoDB。显然，这是一个很重的消费逻辑。MongoDB 的一丁点不稳定都会导致 Consumer 程序消费时长的增加。此时，max.poll.interval.ms 参数值的设置显得尤为关键。如果要避免非预期的 Rebalance，你最好将该参数值设置得大一点，比你的下游最大处理时间稍长一点。就拿 MongoDB 这个例子来说，如果写 MongoDB 的最长时间是 7 分钟，那么你可以将该参数设置为 8 分钟左右。

如果你按照上面的推荐数值恰当地设置了这几个参数，却发现还是出现了 Rebalance，那么我建议你去排查一下 Consumer 端的 GC 表现，比如是否出现了频繁的 Full GC 导致的长时间停顿，从而引发了 Rebalance。为什么特意说 GC？那是因为在实际场景中，我见过太多因为 GC 设置不合理导致程序频发 Full GC 而引发的非预期 Rebalance 了。

# 18 | Kafka中位移提交那些事儿

今天我们要聊的位移是 Consumer 的消费位移，它记录了 Consumer 要消费的下一条消息的位移。

> 切记是下一条消息的位移，而不是目前最新消费消息的位移。

因为 Consumer 能够同时消费多个分区的数据，所以位移的提交实际上是在分区粒度上进行的，即 Consumer 需要为分配给它的每个分区提交各自的位移数据。

**自动提交位移**

Consumer 端有个参数 enable.auto.commit，它的默认值是 true。即 Java Consumer 默认就是自动提交位移的。如果启用了自动提交，Consumer 端还有个参数就派上用场了：auto.commit.interval.ms。它的默认值是 5 秒，表明 Kafka 每 5 秒会为你自动提交一次位移。

下面代码展示了设置自动提交位移的方法。

```java
Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("group.id", "test");
props.put("enable.auto.commit", "true");
props.put("auto.commit.interval.ms", "2000");
props.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
props.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("foo", "bar"));
while (true) {
  ConsumerRecords<String, String> records = consumer.poll(100);
  for (ConsumerRecord<String, String> record : records)
    System.out.printf("offset = %d, key = %s, value = %s%n", record.offset(), record.key(), record.value());
}
```

在默认情况下，Consumer 每 5 秒自动提交一次位移。现在，我们假设提交位移之后的 3 秒发生了 Rebalance 操作。在 Rebalance 之后，所有 Consumer 从上一次提交的位移处继续消费，但该位移已经是 3 秒前的位移数据了，故在 Rebalance 发生前 3 秒消费的所有数据都要重新再消费一次。

虽然你能够通过减少 auto.commit.interval.ms 的值来提高提交频率，但这么做只能缩小重复消费的时间窗口，不可能完全消除它。这是自动提交机制的一个缺陷。

**手动同步提交**

开启手动提交位移的方法就是设置 enable.auto.commit 为 false。可以调用`KafkaConsumer#commitSync()`同步提交位移。

下面这段代码展示了 commitSync() 的使用方法。

```java
while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofSeconds(1));
    process(records); // 处理消息
    try {
        consumer.commitSync();
    } catch (CommitFailedException e) {
        handle(e); // 处理提交失败异常
    }
}
```

手动提交位移的好处就在于更加灵活，你完全能够把控位移提交的时机和频率。

但是，它也有一个缺陷，就是在调用 commitSync() 时，Consumer 程序会处于阻塞状态，直到远端的 Broker 返回提交结果，这个状态才会结束。在任何系统中，因为程序而非资源限制而导致的阻塞都可能是系统的瓶颈，会影响整个应用程序的 TPS。

**手动异步提交**

鉴于上面这个问题，Kafka 社区为手动提交位移提供了另一个 API 方法：KafkaConsumer#commitAsync()。调用 commitAsync() 之后，它会立即返回，不会阻塞，因此不会影响 Consumer 应用的 TPS。

由于它是异步的，Kafka 提供了回调函数（callback），供你实现提交之后的逻辑，比如记录日志或处理异常等。下面这段代码展示了调用 commitAsync() 的方法。

```java
while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofSeconds(1));
    process(records); // 处理消息
    consumer.commitAsync((offsets, exception) -> {
        if (exception != null) {
            handle(exception);
        }
    });
}
```

commitAsync 是否能够替代 commitSync 呢？

答案是不能。commitAsync 的问题在于，出现问题时它不会自动重试。因为它是异步操作，倘若提交失败后自动重试，那么它重试时提交的位移值可能早已经“过期”或不是最新值了。因此，异步提交的重试其实没有意义，所以 commitAsync 是不会重试的。

**手动同异步结合提交**

显然，如果是手动提交，我们需要将 commitSync 和 commitAsync 组合使用才能到达最理想的效果，原因有两个：

1. 我们可以利用 commitSync 的自动重试来规避那些瞬时错误，比如网络的瞬时抖动，Broker 端 GC 等。因为这些问题都是短暂的，自动重试通常都会成功，因此，我们不想自己重试，而是希望 Kafka Consumer 帮我们做这件事。
2. 我们不希望程序总处于阻塞状态，影响 TPS。

下面这段代码，将两个 API 方法结合使用进行手动提交。

```java
try {
    while (true) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofSeconds(1));
        process(records); // 处理消息
        consumer.commitAysnc(); // 使用异步提交规避阻塞
    }
} catch (Exception e) {
    handle(e); // 处理异常
} finally {
    try {
        consumer.commitSync(); // 最后一次提交使用同步阻塞式提交
    } finally {
        consumer.close();
    }
}
```

对于常规性、阶段性的手动提交，我们调用 commitAsync() 避免程序阻塞，而在 Consumer 要关闭前，我们调用 commitSync() 方法执行同步阻塞式的位移提交，以确保 Consumer 关闭前能够保存正确的位移数据。将两者结合后，我们既实现了异步无阻塞式的位移管理，也确保了 Consumer 位移的正确性。

所以，如果你需要自行编写代码开发一套 Kafka Consumer 应用，那么我推荐你使用上面的代码范例来实现手动的位移提交。

**更精细化的位移提交**

我们说了自动提交和手动提交，也说了同步提交和异步提交，这些就是 Kafka 位移提交的全部了吗？其实，我们还差一部分。实际上，Kafka Consumer API 还提供了一组更为方便的方法，可以帮助你实现更精细化的位移管理功能。

设想这样一个场景：你的 poll 方法返回的不是 500 条消息，而是 5000 条。那么，你肯定不想把这 5000 条消息都处理完之后再提交位移，因为一旦中间出现差错，之前处理的全部都要重来一遍。这类似于我们数据库中的事务处理。很多时候，我们希望将一个大事务分割成若干个小事务分别提交，这能够有效减少错误恢复的时间。

在 Kafka 中也是相同的道理。对于一次要处理很多消息的 Consumer 而言，它会关心社区有没有方法允许它在消费的中间进行位移提交。比如前面这个 5000 条消息的例子，你可能希望每处理完 100 条消息就提交一次位移，这样能够避免大批量的消息重新消费。

Kafka Consumer API 为手动提交提供了这样的方法：commitSync(Map<TopicPartition, OffsetAndMetadata>) 和 commitAsync(Map<TopicPartition, OffsetAndMetadata>)。它们的参数是一个 Map 对象，键就是 TopicPartition，即消费的分区，而值是一个 OffsetAndMetadata 对象，保存的主要是位移数据。

就拿刚刚提过的那个例子来说，如何每处理 100 条消息就提交一次位移呢？在这里，我以 commitAsync 为例，展示一段代码，实际上，commitSync 的调用方法和它是一模一样的。

```java
private Map<TopicPartition, OffsetAndMetadata> offsets = new HashMap<>();
int count = 0;
……
while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofSeconds(1));
    for (ConsumerRecord<String, String> record: records) {
        process(record);  // 处理消息
        offsets.put(new TopicPartition(record.topic(), record.partition()), 
                    new OffsetAndMetadata(record.offset() + 1)；
        if（count % 100 == 0）{
            consumer.commitAsync(offsets, null); // 回调处理逻辑是 null
        }
        count++;
    }
}
```

程序先是创建了一个 Map 对象，用于保存 Consumer 消费处理过程中要提交的分区位移，之后开始逐条处理消息，并构造要提交的位移值。

> 还记得之前我说过要提交下一条消息的位移吗？就是这里构造 OffsetAndMetadata 对象时，使用当前消息位移加 1 的原因。

代码的最后部分是做位移的提交。我在这里设置了一个计数器，每累计 100 条消息就统一提交一次位移。与调用无参的 commitAsync 不同，这里调用了带 Map 对象参数的 commitAsync 进行细粒度的位移提交。这样，这段代码就能够实现每处理 100 条消息就提交一次位移，不用再受 poll 方法返回的消息总数的限制了。

# 19 | CommitFailedException异常怎么处理？

所谓 CommitFailedException，顾名思义就是 Consumer 客户端在提交位移时出现了错误或异常，而且还是那种不可恢复的严重异常。如果异常是可恢复的瞬时错误，提交位移的 API 自己就能规避它们了，因为很多提交位移的 API 方法是支持自动错误重试的，比如我们在上一期中提到的 commitSync 方法。

下面我们就来讨论下该异常是什么时候被抛出的。从源代码方面来说，CommitFailedException 异常通常发生在手动提交位移时，即用户显式调用 KafkaConsumer.commitSync() 方法时。从使用场景来说，有两种典型的场景可能遭遇该异常。

**场景一：消息处理时间过长**

当消息处理的总时间超过预设的 max.poll.interval.ms 参数值时，Kafka Consumer 端会抛出 CommitFailedException 异常。

下面代码展示了这个异常：

```java
…
Properties props = new Properties();
…
props.put("max.poll.interval.ms", 5000);
consumer.subscribe(Arrays.asList("test-topic"));

while (true) {
    ConsumerRecords<String, String> records = 
		consumer.poll(Duration.ofSeconds(1));
    // 使用 Thread.sleep 模拟真实的消息处理逻辑
    Thread.sleep(6000L);
    consumer.commitSync();
}
```

如果要防止这种场景下抛出异常，你需要简化你的消息处理逻辑。具体来说有 4 种方法。

- 缩短单条消息处理的时间

  比如，之前下游系统消费一条消息的时间是 100 毫秒，优化之后成功地下降到 50 毫秒，那么此时 Consumer 端的 TPS 就提升了一倍。

- 增加 Consumer 端允许下游系统消费一批消息的最大时长

  这取决于 Consumer 端参数 max.poll.interval.ms 的值。在最新版的 Kafka 中，该参数的默认值是 5 分钟。如果你的消费逻辑不能简化，那么提高该参数值是一个不错的办法。

  > 值得一提的是，Kafka 0.10.1.0 之前的版本是没有这个参数的，因此如果你依然在使用 0.10.1.0 之前的客户端 API，那么你需要增加 session.timeout.ms 参数的值。不幸的是，session.timeout.ms 参数还有其他的含义，因此增加该参数的值可能会有其他方面的“不良影响”，这也是社区在 0.10.1.0 版本引入 max.poll.interval.ms 参数，将这部分含义从 session.timeout.ms 中剥离出来的原因之一。

  

- 减少下游系统一次性消费的消息总数

  这取决于 Consumer 端参数 max.poll.records 的值。当前该参数的默认值是 500 条，表明调用一次 KafkaConsumer.poll 方法，最多返回 500 条消息。可以说，该参数规定了单次 poll 方法能够返回的消息总数的上限。如果前两种方法对你都不适用的话，降低此参数值是避免 CommitFailedException 异常最简单的手段。

- 下游系统使用多线程来加速消费

  这应该算是“最高级”同时也是最难实现的解决办法了。具体的思路就是，让下游系统手动创建多个消费线程处理 poll 方法返回的一批消息。

  > 事实上，很多主流的大数据流处理框架使用的都是这个方法，比如 Apache Flink 在集成 Kafka 时，就是创建了多个 KafkaConsumerThread 线程，自行处理多线程间的数据消费。不过，凡事有利就有弊，这个方法实现起来并不容易，特别是在多个线程间如何处理位移提交这个问题上，更是极容易出错。

综合以上这 4 个处理方法，我个人推荐你首先尝试采用方法 1 来预防此异常的发生。优化下游系统的消费逻辑是百利而无一害的法子，不像方法 2、3 那样涉及到 Kafka Consumer 端 TPS 与消费延时（Latency）的权衡。如果方法 1 实现起来有难度，那么你可以按照下面的法则来实践方法 2、3。

**场景二：同时出现相同的 GroupId**

如果你的应用中同时出现了设置相同 group.id 值的消费者组程序和独立消费者程序，那么当独立消费者程序手动提交位移时，Kafka 就会立即抛出 CommitFailedException 异常，因为 Kafka 无法识别这个具有相同 group.id 的消费者实例，于是就向它返回一个错误，表明它不是消费者组内合法的成员。

> Kafka Java Consumer 端还提供了一个名为 Standalone Consumer 的独立消费者。它没有消费者组的概念，每个消费者实例都是独立工作的，彼此之间毫无联系。
>
> 不过，你需要注意的是，独立消费者的位移提交机制和消费者组是一样的，因此独立消费者的位移提交也必须遵守之前说的那些规定，比如独立消费者也要指定 group.id 参数才能提交位移。

虽然说这个场景很冷门，但也并非完全不会遇到。在一个大型公司中，特别是那些将 Kafka 作为全公司级消息引擎系统的公司中，每个部门或团队都可能有自己的消费者应用，谁能保证各自的 Consumer 程序配置的 group.id 没有重复呢？一旦出现不凑巧的重复，发生了上面提到的这种场景，你使用之前提到的哪种方法都不能规避该异常。令人沮丧的是，无论是刚才哪个版本的异常说明，都完全没有提及这个场景，因此，如果是这个原因引发的 CommitFailedException 异常，前面的 4 种方法全部都是无效的。

