> 参考资料：https://help.aliyun.com/document_detail/68151.html?spm=a2c4g.11174283.6.545.fbe14f3bzR4gWZ

# 01 | 产品简介

**1.1 什么是消息队列 Kafka 版？**

消息队列 Kafka 版是阿里云提供的分布式、高吞吐、可扩展的消息队列服务。消息队列Kafka版广泛用于日志收集、监控数据聚合、流式数据处理、在线和离线分析等大数据领域。

**1.2 消息队列 Kafka 版系统架构**

一个消息队列Kafka版集群包括Producer、Kafka Broker、Consumer Group、ZooKeeper。

![系统架构](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201117225936.png)

Zookeeper：管理集群的配置、选举 Leader 分区、并且在 Consumer Group 发生变化时，进行负载均衡。

消息队列 Kafka 版采用发布/订阅模型，如下图所示。

![发布订阅模型](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201117231304.png)

一个 Consumer Group 可以同时订阅多个 Topic；

一个 Topic 也可以被多个 Consumer Group 同时订阅，但该 Topic 的消息只能被同一个 Consumer Group 内的任意一个 Consumer 消费。

**1.3 优势**

- 全托管服务

  HouseKeeping（健康巡检组件）、业务监控与告警、OpenAPI。

- 高可用性

  数据落盘可靠性高、海量消息堆积也能保持集群的高吞吐能力、数万级 Topic 高并发读写。

- 数据安全

  提供鉴权与授权机制、主子账号、SASL 身份认证、SSL 加密传输、专有网络 VPC。

- 弹性计算

  集群横向扩容、支持数万级 Topic 快速扩容

**1.4 应用场景**

- 网站活动跟踪

  可以实时收集网站活动数据（例如注册、登录、充值、支付、购买），根据业务数据类型将消息发布到不同的 Topic，然后利用订阅消息的实时投递，将消息流用于实时处理、实时监控或者加载到 Hadoop、MaxConpute 等离线数据仓库系统进行离线处理。

- 日志聚合

  消息队列 Kafka 版可以实现更强的数据持久化以及更短的端到端响应时间。

- 流计算处理

  流计算模型能实现在数据流动的过程中对数据进行实时地捕捉和处理，并根据业务需求进行计算分析，最终把结果保存或者分发给需要的组件。

- 数据中转枢纽

  利用 Kafka 作为数据中转枢纽，同份数据可以被导入到不同专用系统中。

**1.5 名词解释**

- Broker

  Kafka 集群中一个独立的服务器。

- Consumer

  消费者，向 Kafka 读取消息并进行消费。

- Consumer Group

  一类 Consumer，这类 Consumer 通常接收并消费同一类消息，且逻辑一致。

- 分区顺序消息

  默认情况下，保证相同 Key 的消息分布在同一个分区中，且分区内消息按照发送顺序存储。

  集群中出现机器宕机时，不会造成消息乱序。但是会出现部分分区发送消息失败，等到宕机机器重新上线后即可恢复正常。

- 普通消息

  默认情况下，保证相同 Key 的消息分布在同一个分区中，且分区内消息按照发送顺序存储。

  集群中出现机器宕机时，可能会造成消息乱序。

- Local 存储

  存储消息的一种方式。

- Partition

  分区，物理上的概念。每个 Topic 包含一个或多个分区。

- Producer

  消息生产者。负责生产并发送消息到 Kafka。

- Topic

  消息的类型。Kafka 通过 Topic 对消息进行分类。一个 Topic 由一个或多个 Partition 组成，存储在一个或多个 Broker 上。

- 云存储

  存储消息的一种方式，底层接入阿里云云盘的多副本能力。

# 02 | 快速入门

**2.1 安装 Java 依赖库**

```xml
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-clients</artifactId>
    <version>0.10.2.2</version>
</dependency>
<dependency>
    <groupId>org.slf4j</groupId>
    <artifactId>slf4j-log4j12</artifactId>
    <version>1.7.6</version>
</dependency>
```

**2.2 准备配置**

创建 Log4j 配置文件 log4j.properties。

```properties
log4j.rootLogger=INFO, STDOUT

log4j.appender.STDOUT=org.apache.log4j.ConsoleAppender
log4j.appender.STDOUT.layout=org.apache.log4j.PatternLayout
log4j.appender.STDOUT.layout.ConversionPattern=[%d] %p %m (%c)%n
```

创建 Kafka 配置文件 kafka.properties。

```properties
## 配置接入点，即控制台的实例详情页面显示的默认接入点。
bootstrap.servers=xxxxxxxxxxxxxxxxxxxxx
## 配置Topic，可以在控制台上创建Topic。
topic=alikafka-topic-demo
## 配置Consumer Group，可以在控制台创建Consumer Group。
group.id=CID-consumer-group-demo
```

**2.3 发送/订阅消息 Demo**

参考：https://help.aliyun.com/document_detail/99957.html?spm=a2c4g.11186623.2.22.5adc64a0eCKJJY

# 03 | 发布者最佳实践

**3.1 发送消息**

发送消息的示例代码如下：

```java
Future<RecordMetadata> metadataFuture = producer.send(new ProducerRecord<String, String>(
        topic,   //消息主题。
        null,   //分区编号。建议为null，由Producer分配。
        System.currentTimeMillis(),   //时间戳。
        String.valueOf(value.hashCode()),   //消息键。
        value   //消息值。
));
```

**3.2 Key 和 Value**

0.10.2.2版本的Kafka的消息字段只有两个：Key和Value。

- Key：消息的标识。
- Value：消息内容。

为了便于追踪，请为消息设置一个唯一的Key。您可以通过Key追踪某消息，打印发送日志和消费日志，了解该消息的发送和消费情况。

**3.3 失败重试**

分布式环境下，由于网络等原因偶尔发送失败是常见的。导致这种失败的原因可能是消息已经发送成功，但是Ack失败，也有可能是确实没发送成功。

消息队列Kafka版是VIP网络架构，会主动断开空闲连接（30秒没活动），因此，不是一直活跃的客户端会经常收到 "connection rest by peer" 错误，建议重试消息发送。

您可以根据业务需求，设置以下重试参数：

- `retries`，重试次数，建议设置为`3`。
- `retry.backoff.ms`，重试间隔，建议设置为`1000`。

**3.4 异步发送**

发送接口是异步的，如果您想得到发送的结果，可以调用`metadataFuture.get(timeout, TimeUnit.MILLISECONDS)`。

**3.5 线程安全**

Producer是线程安全的，且可以往任何Topic发送消息。通常情况下，一个应用对应一个Producer就足够了。

**3.6 Acks**

Acks的说明如下：

- `acks=0`：无需服务端的Response、性能较高、丢数据风险较大。
- `acks=1`：服务端主节点写成功即返回Response、性能中等、丢数据风险中等、主节点宕机可能导致数据丢失。
- `acks=all`：服务端主节点写成功且备节点同步成功才返回Response、性能较差、数据较为安全、主节点和备节点都宕机才会导致数据丢失。

一般建议选择`acks=1`，重要的服务可以设置`acks=all`。

**3.7 Batch**

Batch的基本思路是：把消息缓存在内存中，并进行打包发送。Kafka通过Batch来提高吞吐，但同时也会增加延迟，生产时应该对两者予以权衡。 在构建Producer时，需要考虑以下两个参数：

- `batch.size` : 发往每个分区（Partition）的消息缓存量（消息内容的字节数之和，不是条数）达到这个数值时，就会触发一次网络请求，然后客户端把消息真正发往服务器。
- `linger.ms` : 每条消息待在缓存中的最长时间。若超过这个时间，就会忽略`batch.size`的限制，然后客户端立即把消息发往服务器。

因此，Kafka客户端什么时候把消息真正发往服务器是由`batch.size`和`linger.ms`共同决定的。您可以根据具体业务需求进行调整。

**3.8 buffer.memory**

结合Kafka的Batch设计思路，Kafka会缓存消息并打包发送，如果缓存太多，则有可能造成OOM（Out of Memory）。

- `buffer.memory` : 所有缓存消息的总体大小超过这个数值后，就会触发把消息发往服务器。此时会忽略`batch.size`和`linger.ms`的限制。
- `buffer.memory`的默认数值是32 MB，对于单个Producer来说，可以保证足够的性能。 需要注意的是，如果您在同一个JVM中启动多个Producer，那么每个Producer都有可能占用32 MB缓存空间，此时便有可能触发OOM。
- 在生产时，一般没有必要启动多个Producer；如果特殊情况需要，则需要考虑`buffer.memory`的大小，避免触发OOM。

**3.9 分区顺序**

单个分区（Partition）内，消息是按照发送顺序储存的，是基本有序的。

默认情况下，消息队列Kafka版为了提升可用性，并不保证单个分区内绝对有序，在升级或者宕机时，会发生少量消息乱序（某个分区挂掉后把消息Failover到其它分区）。

对于包年包月计费模式下的专业版实例，如果业务要求分区保证严格有序，请在创建Topic时指定保序。

# 04 | 订阅者最佳实践

**4.1 消费消息基本流程**

Kafka 订阅者在订阅消息时的基本流程是：

1. Poll数据。
2. 执行消费逻辑。
3. 再次 poll 数据。

**4.2 负载均衡**

例如Consumer Group A订阅了Topic A，并开启三个消费实例C1、C2、C3，则发送到Topic A的每条消息最终只会传给C1、C2、C3的某一个。Kafka默认会均匀地把消息传给各个消息实例，以做到消费负载均衡。

Kafka负载消费的内部原理是，把订阅的Topic的分区，平均分配给各个消费实例。因此，消费实例的个数不要大于分区的数量，否则会有实例分配不到任何分区而处于空跑状态。这个负载均衡发生的时间，除了第一次启动上线之外，后续消费实例发生重启、增加、减少等变更时，都会触发一次负载均衡。

Kafka 的每个Topic的分区数量默认是16个。

**4.3 多个订阅**

消息队列Kafka版支持以下多个订阅方式：

- Consumer Group 订阅多个 Topic。

  一个 Consumer Group 可以订阅多个 Topic，多个 Topic 的消息被 Cosumer Group 中的 Consumer 均匀消费。例如 Consumer Group A 订阅了 Topic A、Topic B、Topic C，则这三个 Topic 中的消息，被 Consumer Group 中的Consumer 均匀消费。 

  Consumer Group 订阅多个 Topic 的示例代码如下：

  ```java
  String topicStr = kafkaProperties.getProperty("topic");
  String[] topics = topicStr.split(",");
  for (String topic: topics) {
      subscribedTopics.add(topic.trim());
  }
  consumer.subscribe(subscribedTopics);
  ```

- Topic 被多个 Consumer Group 订阅。

  一个 Topic 可以被多个 Consumer Group 订阅，且各个 Consumer Group 独立消费 Topic 下的所有消息。例如 Consumer Group A 订阅了 Topic A，Consumer Group B 也订阅了 Topic A，则发送到 Topic A 的每条消息，不仅会传一份给 Consumer Group A 的消费实例，也会传一份给 Consumer Group B 的消费实例，且这两个过程相互独立，相互没有任何影响。

**4.4 消费位点**

每个 Topic 会有多个分区，每个分区会统计当前消息的总条数，这个称为最大位点MaxOffset。

Consumer 会按顺序依次消费分区内的每条消息，记录已经消费了的消息条数，称为 ConsumerOffset。

剩余的未消费的条数（也称为消息堆积量）= MaxOffset - ConsumerOffset。

**4.5 消费位点提交**

消息队列Kafka版消费者有两个相关参数：

- enable.auto.commit：默认值为true。
- auto.commit.interval.ms： 默认值为1000，即1s。

这两个参数组合的结果就是，每次poll数据前会先检查上次提交位点的时间，如果距离当前时间已经超过参数auto.commit.interval.ms规定的时长，则客户端会启动位点提交动作。

因此，如果将enable.auto.commit设置为true，则需要在每次poll数据时，确保前一次poll出来的数据已经消费完毕，否则可能导致位点跳跃。

如果想自己控制位点提交，请把enable.auto.commit设为false，并调用commit(offsets)函数自行控制位点提交。

**4.6 消费位点重置**

以下两种情况，会发生消费位点重置：

- 当服务端不存在曾经提交过的位点时（例如客户端第一次上线）。
- 当从非法位点拉取消息时（例如某个分区最大位点是10，但客户端却从11开始拉取消息）。

Java客户端可以通过auto.offset.reset来配置重置策略，主要有三种策略： 

- latest：从最大位点开始消费。
- earliest：从最小位点开始消费。
- none：不做任何操作，即不重置。

**4.7 拉取大消息**

消费过程是由客户端主动去服务端拉取消息的，在拉取大消息时，需要注意控制拉取速度，注意修改配置：

- max.poll.records：如果单条消息超过1 MB，建议设置为1。
- fetch.max.bytes：设置比单条消息的大小略大一点。
- max.partition.fetch.bytes：设置比单条消息的大小略大一点。

拉取大消息的核心是逐条拉取的。

**4.8 拉取公网**

通过公网消费消息时，通常会因为公网带宽的限制导致连接被断开，此时需要注意控制拉取速度，修改配置：

1. fetch.max.bytes：建议设置成公网带宽的一半（注意该参数的单位是bytes，公网带宽的单位是bits）
2. max.partition.fetch.bytes：建议设置成fetch.max.bytes的三分之一或者四分之一。

**4.9 消息重复和消费幂等**

消息队列Kafka版消费的语义是at least once， 也就是至少投递一次，保证消息不丢失，但是无法保证消息不重复。在出现网络问题、客户端重启时均有可能造成少量重复消息，此时应用消费端如果对消息重复比较敏感（例如订单交易类），则应该做消息幂等。

以数据库类应用为例，常用做法是：

- 发送消息时，传入key作为唯一流水号ID。
- 消费消息时，判断key是否已经消费过，如果已经消费过了，则忽略，如果没消费过，则消费一次。

当然，如果应用本身对少量消息重复不敏感，则不需要做此类幂等检查。

**4.10 消费失败**

消息队列Kafka版是按分区逐条消息顺序向前推进消费的，如果消费端拿到某条消息后执行消费逻辑失败，例如应用服务器出现了脏数据，导致某条消息处理失败，等待人工干预，那么有以下两种处理方式：

- 失败后一直尝试再次执行消费逻辑。这种方式有可能造成消费线程阻塞在当前消息，无法向前推进，造成消息堆积。
- 由于消息队列Kafka版没有处理失败消息的设计，实践中通常会打印失败的消息或者存储到某个服务（例如创建一个Topic专门用来放失败的消息），然后定时检查失败消息的情况，分析失败原因，根据情况处理。

**4.11 消费延迟**

消息队列 Kafka 版的消费机制是由客户端主动去服务端拉取消息进行消费的。因此，一般来说，如果客户端能够及时消费，则不会产生较大延迟。如果产生了较大延迟，请先关注是否有堆积，并注意提高消费速度。

**4.12 消费阻塞以及堆积**

消费端最常见的问题就是消费堆积，最常造成堆积的原因是：

- 消费速度跟不上生产速度，此时应该提高消费速度。
- 消费端产生了阻塞。

消费端拿到消息后，执行消费逻辑，通常会执行一些远程调用，如果这个时候同步等待结果，则有可能造成一直等待，消费进程无法向前推进。

消费端应该竭力避免堵塞消费线程，如果存在等待调用结果的情况，建议设置等待的超时时间，超时后作为消费失败进行处理。

**4.13 提高消费速度**

提高消费速度有以下两个办法：

- 增加 Consumer 实例个数。

  可以在进程内直接增加（需要保证每个实例对应一个线程，否则没有太大意义），也可以部署多个消费实例进程；需要注意的是，实例个数超过分区数量后就不再能提高速度，将会有消费实例不工作。

- 增加消费线程。

  增加 Consumer 实例本质上也是增加线程的方式来提升速度，因此更加重要的性能提升方式是增加消费线程，最基本的步骤如下： 

  1. 定义一个线程池。
  2. Poll 数据。
  3. 把数据提交到线程池进行并发处理。
  4. 等并发结果返回成功后，再次 poll 数据执行。

**4.14 消息过滤**

消息队列 Kafka 版自身没有消息过滤的语义。实践中可以采取以下两个办法：

- 如果过滤的种类不多，可以采取多个 Topic 的方式达到过滤的目的。
- 如果过滤的种类多，则最好在客户端业务层面自行过滤。

实践中请根据业务具体情况进行选择，也可以综合运用上面两种办法。

**4.15 消息广播**

消息队列 Kafka 版没有消息广播的语义，可以通过创建不同的 Consumer Group 来模拟实现。

**4.16 订阅关系**

同一个 Consumer Group 内，各个消费实例订阅的 Topic 最好保持一致，避免给排查问题带来干扰。

