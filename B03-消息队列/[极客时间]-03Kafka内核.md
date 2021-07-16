> 来源：极客时间《Kafka核心技术与实战》

# 23 | Kafka副本机制详解

所谓的副本机制（Replication），通常是指分布式系统在多台网络互联的机器上保存有相同的数据拷贝。副本机制有什么好处呢？

- 提供数据冗余：增加系统整体的可用性。
- 提供高伸缩性：能够通过增加机器的方式来提升读性能，进而提高读操作吞吐量。
- 改善数据局部性：允许将数据放入与用户地理位置相近的地方，从而降低系统延时。

然而对于 Apache Kafka 而言，目前只能享受到副本机制带来的第 1 个好处。即便如此，副本机制依然是 Kafka 设计架构的核心所在，它也是 Kafka 确保系统高可用和消息高持久性的重要基石。

**副本定义**

所谓副本（Replica），本质就是一个只能追加写消息的提交日志。同一个分区下的所有副本保存有相同的消息序列，这些副本分散保存在不同的 Broker 上，从而能够对抗部分 Broker 宕机带来的数据不可用。

> 在实际生产环境中，每台 Broker 都可能保存有各个主题下不同分区的不同副本，因此，单个 Broker 上存有成百上千个副本的现象是非常正常的。

接下来我们来看一张图，它展示的是一个有 3 台 Broker 的 Kafka 集群上的副本分布情况。

![image-20210715225817802](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210715225817.png)

从这张图中，我们可以看到，主题 1 分区 0 的 3 个副本分散在 3 台 Broker 上，其他主题分区的副本也都散落在不同的 Broker 上，从而实现数据冗余。

**副本角色**

我们该如何确保副本中所有的数据都是一致的呢？

Apache Kafka 采用了基于领导者（Leader-based）的副本机制，工作原理如下图所示：

![image-20210715230922759](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210715230922.png)

对于上图，有几点信息需要明确：

第一，每个分区在创建时都要选举一个副本作为领导者副本，其余的副本则为追随者副本。

第二，在 Kafka 中，追随者副本是不对外提供服务的，所有的请求都必须由领导者副本来处理。

第三，当领导者副本所在的 Broker 宕机时，会立即开启新一轮的领导者选举。

追随者副本不对外提供，Kafka 为什么要这样设计呢？

第一，方便实现 “Read-your-writes”。当你使用生产者 API 向 Kafka 成功写入消息后，可以马上使用消费者 API 去读取刚才生产的消息。

第二，方便实现单调读（Monotonic Reads）。对于一个消费者用户而言，在多次消费消息时，它不会看到某条消息一会儿存在一会儿不存在。

**In-sync Replicas（ISR）**

怎么度量追随者副本与 Leader 不同步呢？

Kafka 引入了 In-sync Replicas，即 ISR 副本集合。ISR 中的副本都是与 Leader 同步的副本，相反，不在 ISR 中的追随者副本就被认为是与 Leader 不同步的。

> Leader 副本天然就在 ISR 中。也就是说，ISR 不只是追随者副本集合，它必然包括 Leader 副本。甚至在某些情况下，ISR 只有 Leader 这一个副本。

能够进入到 ISR 的追随者副本要满足一定的标准，这个标准就是 Broker 端参数 replica.lag.time.max.ms 参数值。这个参数的含义是 Follower 副本能够落后 Leader 副本的最长时间间隔，当前默认值是 10 秒。

> 只要一个 Follower 副本落后 Leader 副本的时间不连续超过 10 秒，那么 Kafka 就认为该 Follower 副本与 Leader 是同步的，即使此时 Follower 副本中保存的消息明显少于 Leader 副本中的消息。

**Unclean Leader Election**

当出现 ISR 为空，就说明 Leader 副本也“挂掉”了，Kafka 需要从非同步副本中选举一个新的 Leader，选举这种副本的过程称为 Unclean 领导者选举。

通常来说，非同步副本（ISR 集合外的副本）落后 Leader 太多，如果选择这些副本作为新 Leader，就可能出现数据的丢失。Broker 端可通过参数 unclean.leader.election.enable 控制是否允许 Unclean 领导者选举。

开启 Unclean 领导者选举可能会造成数据丢失，但好处是，它使得分区 Leader 副本一直存在，不至于停止对外提供服务，因此提升了高可用性。

反之，禁止 Unclean 领导者选举的好处在于维护了数据的一致性，避免了消息丢失，但牺牲了高可用性。

Kafka 赋予了你选择 C 或 A 的权利。我强烈建议你不要开启它，毕竟我们还可以通过其他的方式来提升高可用性。如果为了这点儿高可用性的改善，牺牲了数据一致性，那就非常不值当了。

# 24 | 请求是怎么被处理的？

今天，我们来详细讨论一下 Kafka Broker 端处理请求的全流程。

**常见处理请求的方式**

关于如何处理请求，我们很容易想到的方案有两个。

- 顺序处理请求

伪代码大概是这个样子：

```java
while (true) {
    Request request = accept(connection);
    handle(request);
}
```

这种方式的吞吐量太差，每个请求都必须等待前一个请求处理完毕才能得到处理。适用于请求发送非常不频繁的系统。

- 异步处理请求

伪代码大概是这个样子：

```java
while (true) {
    Request = request = accept(connection);
    Thread thread = new Thread(() -> handle(request););
    thread.start();
}
```

这个方法的好处是，它是完全异步的，每个请求的处理都不会阻塞下一个请求。

缺陷是开销极大，在某些场景下甚至会压垮整个服务。这个方法也只适用于请求发送频率很低的业务场景。

**Kafka 处理请求的方式**

Kafka 使用的是 Reactor 模式。

简单来说，Reactor 模式是事件驱动架构的一种实现方式，特别适合应用于处理多个客户端并发向服务器端发送请求的场景。Reactor 模式的架构图如下：

![image-20210716233202622](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210716233202.png)

根据上图，Reactor 模式主要特点是分发。

Reactor 有个请求分发线程 Dispatcher，也就是图中的 Acceptor，它会将不同的请求下发到多个工作线程中处理。

> Acceptor 线程只是用于请求分发，不涉及具体的逻辑处理，非常轻量级，因此有很高的吞吐量表现。而这些工作线程可以根据实际业务处理需要任意增减，从而动态调节系统负载能力。

Kafka 的处理请求模型类似：

![image-20210716233715438](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210716233715.png)

SocketServer 组件：它也有对应的 Acceptor 线程和一个网络线程池。

Acceptor 线程：采用轮询的方式将入站请求公平地发到所有网络线程中。

网络线程池：处理 Acceptor 线程分发的工作任务。

Kafka 提供了 Broker 端参数 num.network.threads，用于调整该网络线程池的线程数。其默认值是 3，表示每台 Broker 启动时会创建 3 个网络线程，专门处理客户端发送的请求。

**Kafka 网络线程处理请求的具体过程**

客户端发来的请求会被 Broker 端的 Acceptor 线程分发到任意一个网络线程中，Kafka 在这个环节又做了一层异步线程池的处理，我们一起来看一看下面这张图。

![image-20210716234619473](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210716234619.png)

主要步骤如下：

1. 当网络线程拿到请求后，会将请求放入到一个共享请求队列中。

2. Broker 端有个 IO 线程池，负责从该队列中取出请求，执行真正的处理。

   > Broker 端参数 num.io.threads 控制了这个线程池中的线程数。 目前该参数默认值是 8，表示每台 Broker 启动后自动创建 8 个 IO 线程处理请求。

3. 处理请求。如果是 PRODUCE 生产请求，则将消息写入到底层的磁盘日志中；如果是 FETCH 请求，则从磁盘或页缓存中读取消息。

4. IO 线程处理完请求后，会将生成的响应发送到网络线程池的响应队列中，然后由对应的网络线程负责将 Response 返还给客户端。

> 为什么网络线程不直接处理？即为什么要有 2、3 步骤？

**请求队列与响应队列的差别**

请求队列是所有网络线程共享的，而响应队列则是每个网络线程专属的。

这么设计的原因就在于，Dispatcher 只是用于请求分发而不负责响应回传，因此只能让每个网络线程自己发送 Response 给客户端，所以这些 Response 也就没必要放在一个公共的地方。

**Purgatory 组件**

图中还有一个叫 Purgatory 的组件，这是 Kafka 中著名的“炼狱”组件。它是用来缓存延时请求（Delayed Request）的。

所谓延时请求，就是那些一时未满足条件不能立刻处理的请求。比如设置了 acks=all 的 PRODUCE 请求，一旦设置了 acks=all，那么该请求就必须等待 ISR 中所有副本都接收了消息后才能返回，此时处理该请求的 IO 线程就必须等待其他 Broker 的写入结果。当请求不能立刻处理时，它就会暂存在 Purgatory 中。稍后一旦满足了完成条件，IO 线程会继续处理该请求，并将 Response 放入对应网络线程的响应队列中。







