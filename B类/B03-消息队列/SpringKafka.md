> 参考资料：
>
> - https://docs.spring.io/spring-kafka/reference/index.html
> - https://github.com/spring-projects/spring-kafka/tree/main/samples
> - [在 Spring 应用中整合 Apache Kafka 以生产、消费消息](https://springdoc.cn/spring-kafka/)

# 一、快速开始

```xml
<dependency>
  <groupId>org.springframework.kafka</groupId>
  <artifactId>spring-kafka</artifactId>
  <version>3.2.3</version>
</dependency>
```

适用版本：

- Apache Kafka 客户端 3.7.x
- Spring Framework 6.1.x
- 最低 Java 版本：17

## 1.1 Spring Boot 消费者

```java
@SpringBootApplication
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

    @Bean
    public NewTopic topic() {
        return TopicBuilder.name("topic1")
                .partitions(10)
                .replicas(1)
                .build();
    }

    @KafkaListener(id = "myId", topics = "topic1")
    public void listen(String in) {
        System.out.println(in);
    }

}
```

## 1.2 Spring Boot 生产者

```java
@SpringBootApplication
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

    @Bean
    public NewTopic topic() {
        return TopicBuilder.name("topic1")
                .partitions(10)
                .replicas(1)
                .build();
    }

    @Bean
    public ApplicationRunner runner(KafkaTemplate<String, String> template) {
        return args -> {
            template.send("topic1", "test");
        };
    }

}
```

## 1.3 使用Java配置

```java
public class Sender {

    public static void main(String[] args) {
        AnnotationConfigApplicationContext context = new AnnotationConfigApplicationContext(Config.class);
        context.getBean(Sender.class).send("test", 42);
    }

    private final KafkaTemplate<Integer, String> template;

    public Sender(KafkaTemplate<Integer, String> template) {
        this.template = template;
    }

    public void send(String toSend, int key) {
        this.template.send("topic1", key, toSend);
    }

}

public class Listener {

    @KafkaListener(id = "listen1", topics = "topic1")
    public void listen1(String in) {
        System.out.println(in);
    }

}

@Configuration
@EnableKafka
public class Config {

    @Bean
    ConcurrentKafkaListenerContainerFactory<Integer, String>
                        kafkaListenerContainerFactory(ConsumerFactory<Integer, String> consumerFactory) {
        ConcurrentKafkaListenerContainerFactory<Integer, String> factory =
                                new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory);
        return factory;
    }

    @Bean
    public ConsumerFactory<Integer, String> consumerFactory() {
        return new DefaultKafkaConsumerFactory<>(consumerProps());
    }

    private Map<String, Object> consumerProps() {
        Map<String, Object> props = new HashMap<>();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "group");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, IntegerDeserializer.class);
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        // ...
        return props;
    }

    @Bean
    public Sender sender(KafkaTemplate<Integer, String> template) {
        return new Sender(template);
    }

    @Bean
    public Listener listener() {
        return new Listener();
    }

    @Bean
    public ProducerFactory<Integer, String> producerFactory() {
        return new DefaultKafkaProducerFactory<>(senderProps());
    }

    private Map<String, Object> senderProps() {
        Map<String, Object> props = new HashMap<>();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.LINGER_MS_CONFIG, 10);
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, IntegerSerializer.class);
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        //...
        return props;
    }

    @Bean
    public KafkaTemplate<Integer, String> kafkaTemplate(ProducerFactory<Integer, String> producerFactory) {
        return new KafkaTemplate<>(producerFactory);
    }

}
```

# 二、在Spring中使用Kafka

## 2.1 连接Kafka

### 1、Factory Listeners

从版本 2.5 开始，可以使用`Listener`配置`DefaultKafkaProducerFactory`和`DefaultKafkaConsumerFactory`，以便在创建或关闭生产者或消费者时接收通知。

*Producer Factory Listener*

```java
interface Listener<K, V> {

    default void producerAdded(String id, Producer<K, V> producer) {
    }

    default void producerRemoved(String id, Producer<K, V> producer) {
    }

}
```

*Consumer Factory Listener*

```java
interface Listener<K, V> {

    default void consumerAdded(String id, Consumer<K, V> consumer) {
    }

    default void consumerRemoved(String id, Consumer<K, V> consumer) {
    }

}
```

### 2、默认Client ID前缀

从版本 3.2 开始，使用 `spring.application.name` 定义的服务名，现在用作自动生成的客户端 ID 的默认前缀。包括以下客户端类型：

- 不使用消费者组的消费者客户端
- 生产者客户端
- admin clients

这让服务端能够识别这些客户端，以进行故障排查或应用配额。

*表 1. 使用*`spring.application.name=myapp` *Spring Boot 应用程序生成的示例客户端 ID*

| 客户端类型                | 没有应用程序名称   | 有应用程序名称     |
| :------------------------ | :----------------- | :----------------- |
| 没有消费者组的消费者      | consumer-null-1    | myapp-consumer-1   |
| 消费者组“mygroup”的消费者 | consumer-mygroup-1 | consumer-mygroup-1 |
| producer                  | producer-1         | myapp-producer-1   |
| admin                     | adminclient-1      | myapp-admin-1      |

## 2.2 配置Topic



## 2.3 发送消息

### 1、使用KafkaTemplate

`KafkaTemplate`包装了生产者并提供了将数据发送到 Kafka 主题的便捷方法。

您可以配置生产者工厂并在模板的构造函数中提供它。以下示例展示了如何执行此操作：

```java
@Bean
public ProducerFactory<Integer, String> producerFactory() {
    return new DefaultKafkaProducerFactory<>(producerConfigs());
}

@Bean
public Map<String, Object> producerConfigs() {
    Map<String, Object> props = new HashMap<>();
    props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
    props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, IntegerSerializer.class);
    props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
    // See https://kafka.apache.org/documentation/#producerconfigs for more properties
    return props;
}

@Bean
public KafkaTemplate<Integer, String> kafkaTemplate() {
    return new KafkaTemplate<Integer, String>(producerFactory());
}
```

从版本 2.5 开始，您现在可以覆盖工厂的`ProducerConfig`属性，以创建具有来自同一工厂的不同生产者配置的模板。

```java
@Bean
public KafkaTemplate<String, String> stringTemplate(ProducerFactory<String, String> pf) {
    return new KafkaTemplate<>(pf);
}

@Bean
public KafkaTemplate<String, byte[]> bytesTemplate(ProducerFactory<String, byte[]> pf) {
    return new KafkaTemplate<>(pf,
            Collections.singletonMap(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, ByteArraySerializer.class));
}
```

您可以使用`ProducerListener`配置`KafkaTemplate` ，以获取包含发送结果（成功或失败）的异步回调，而不是等待`Future`完成。以下清单显示了`ProducerListener`接口的定义：

```java
public interface ProducerListener<K, V> {

    void onSuccess(ProducerRecord<K, V> producerRecord, RecordMetadata recordMetadata);

    void onError(ProducerRecord<K, V> producerRecord, RecordMetadata recordMetadata,
            Exception exception);

}
```

默认情况下，模板配置有`LoggingProducerListener` ，它会记录错误，并且在发送成功时不执行任何操作。

发送方法返回`CompletableFuture<SendResult>` 。您可以向侦听器注册回调以异步接收发送结果。以下示例展示了如何执行此操作：

```java
CompletableFuture<SendResult<Integer, String>> future = template.send("myTopic", "something");
future.whenComplete((result, ex) -> {
    ...
});
```

*示例 1. 非阻塞（异步）*

```java
public void sendToKafka(final MyOutputData data) {
    final ProducerRecord<String, String> record = createRecord(data);

    CompletableFuture<SendResult<Integer, String>> future = template.send(record);
    future.whenComplete((result, ex) -> {
        if (ex == null) {
            handleSuccess(data);
        }
        else {
            handleFailure(data, record, ex);
        }
    });
}
```

*示例2. 阻塞（同步）*

```java
public void sendToKafka(final MyOutputData data) {
    final ProducerRecord<String, String> record = createRecord(data);

    try {
        template.send(record).get(10, TimeUnit.SECONDS);
        handleSuccess(data);
    }
    catch (ExecutionException e) {
        handleFailure(data, record, e.getCause());
    }
    catch (TimeoutException | InterruptedException e) {
        handleFailure(data, record, e);
    }
}
```

### 2、使用RoutingKafkaTemplate

从版本 2.5 开始，您可以使用`RoutingKafkaTemplate`根据目标`topic`名称在运行时选择生产者。

以下简单的 Spring Boot 应用程序提供了一个示例，说明如何使用相同的模板发送到不同的 Topic，每个 Topic 使用不同的值序列化器。

```javascript
@SpringBootApplication
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

    @Bean
    public RoutingKafkaTemplate routingTemplate(GenericApplicationContext context,
            ProducerFactory<Object, Object> pf) {

        // Clone the PF with a different Serializer, register with Spring for shutdown
        Map<String, Object> configs = new HashMap<>(pf.getConfigurationProperties());
        configs.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, ByteArraySerializer.class);
        DefaultKafkaProducerFactory<Object, Object> bytesPF = new DefaultKafkaProducerFactory<>(configs);
        context.registerBean("bytesPF", DefaultKafkaProducerFactory.class, () -> bytesPF);

        Map<Pattern, ProducerFactory<Object, Object>> map = new LinkedHashMap<>();
        map.put(Pattern.compile("two"), bytesPF);
        map.put(Pattern.compile(".+"), pf); // Default PF with StringSerializer
        return new RoutingKafkaTemplate(map);
    }

    @Bean
    public ApplicationRunner runner(RoutingKafkaTemplate routingTemplate) {
        return args -> {
            routingTemplate.send("one", "thing1");
            routingTemplate.send("two", "thing2".getBytes());
        };
    }

}
```

### 3、使用DefaultKafkaProducerFactory

```java
@Bean
public ProducerFactory<Integer, CustomValue> producerFactory() {
    return new DefaultKafkaProducerFactory<>(producerConfigs(), null, () -> new CustomValueSerializer());
}

@Bean
public KafkaTemplate<Integer, CustomValue> kafkaTemplate() {
    return new KafkaTemplate<Integer, CustomValue>(producerFactory());
}
```

### 4、使用ReplyingKafkaTemplate

2.1.3版本引入了`KafkaTemplate`的子类来提供请求/回复语义。该类名为`ReplyingKafkaTemplate` ，并且有两个附加方法；下面显示了方法签名：

```java
RequestReplyFuture<K, V, R> sendAndReceive(ProducerRecord<K, V> record);

RequestReplyFuture<K, V, R> sendAndReceive(ProducerRecord<K, V> record,
    Duration replyTimeout);
```

结果是一个`CompletableFuture` ，它异步填充结果（或超时的异常）。结果还有一个`sendFuture`属性，它是调用`KafkaTemplate.send()`的结果。您可以使用这个 future 来确定发送操作的结果。

以下 Spring Boot 应用程序显示了如何使用该功能的示例：

```java
@SpringBootApplication
public class KRequestingApplication {

    public static void main(String[] args) {
        SpringApplication.run(KRequestingApplication.class, args).close();
    }

    @Bean
    public ApplicationRunner runner(ReplyingKafkaTemplate<String, String, String> template) {
        return args -> {
            if (!template.waitForAssignment(Duration.ofSeconds(10))) {
                throw new IllegalStateException("Reply container did not initialize");
            }
            ProducerRecord<String, String> record = new ProducerRecord<>("kRequests", "foo");
            RequestReplyFuture<String, String, String> replyFuture = template.sendAndReceive(record);
            SendResult<String, String> sendResult = replyFuture.getSendFuture().get(10, TimeUnit.SECONDS);
            System.out.println("Sent ok: " + sendResult.getRecordMetadata());
            ConsumerRecord<String, String> consumerRecord = replyFuture.get(10, TimeUnit.SECONDS);
            System.out.println("Return value: " + consumerRecord.value());
        };
    }

    @Bean
    public ReplyingKafkaTemplate<String, String, String> replyingTemplate(
            ProducerFactory<String, String> pf,
            ConcurrentMessageListenerContainer<String, String> repliesContainer) {

        return new ReplyingKafkaTemplate<>(pf, repliesContainer);
    }

    @Bean
    public ConcurrentMessageListenerContainer<String, String> repliesContainer(
            ConcurrentKafkaListenerContainerFactory<String, String> containerFactory) {

        ConcurrentMessageListenerContainer<String, String> repliesContainer =
                containerFactory.createContainer("kReplies");
        repliesContainer.getContainerProperties().setGroupId("repliesGroup");
        repliesContainer.setAutoStartup(false);
        return repliesContainer;
    }

    @Bean
    public NewTopic kRequests() {
        return TopicBuilder.name("kRequests")
            .partitions(10)
            .replicas(2)
            .build();
    }

    @Bean
    public NewTopic kReplies() {
        return TopicBuilder.name("kReplies")
            .partitions(10)
            .replicas(2)
            .build();
    }

}
```

## 2.4 接收消息

### 1、消息监听器

```java
//当使用自动提交或容器管理的提交方法之一时，使用此接口处理从 Kafka 消费者poll()操作接收到的单个ConsumerRecord实例。
public interface MessageListener<K, V> {
    void onMessage(ConsumerRecord<K, V> data);
}

//当使用手动提交方法之一时，使用此接口处理从 Kafka 消费者poll()操作接收到的各个ConsumerRecord实例。
public interface AcknowledgingMessageListener<K, V> {
    void onMessage(ConsumerRecord<K, V> data, Acknowledgment acknowledgment);
}

//当使用自动提交或容器管理的提交方法之一时，使用此接口处理从 Kafka 消费者poll()操作接收到的单个ConsumerRecord实例。提供对Consumer对象的访问。
public interface ConsumerAwareMessageListener<K, V> extends MessageListener<K, V> {
    void onMessage(ConsumerRecord<K, V> data, Consumer<?, ?> consumer);
}

//当使用手动提交方法之一时，使用此接口处理从 Kafka 消费者poll()操作接收到的各个ConsumerRecord实例。提供对Consumer对象的访问。
public interface AcknowledgingConsumerAwareMessageListener<K, V> extends MessageListener<K, V> {
    void onMessage(ConsumerRecord<K, V> data, Acknowledgment acknowledgment, Consumer<?, ?> consumer);
}

//当使用自动提交或容器管理的提交方法之一时，使用此接口处理从 Kafka 消费者poll()操作接收到的所有ConsumerRecord实例。使用此接口时不支持AckMode.RECORD，因为监听器会获得完整的批次。
public interface BatchMessageListener<K, V> {
    void onMessage(List<ConsumerRecord<K, V>> data);
}

//当使用手动提交方法之一时，使用此接口处理从 Kafka 消费者poll()操作接收到的所有ConsumerRecord实例。
public interface BatchAcknowledgingMessageListener<K, V> {
    void onMessage(List<ConsumerRecord<K, V>> data, Acknowledgment acknowledgment);
}

//当使用自动提交或容器管理的提交方法之一时，使用此接口处理从 Kafka 消费者poll()操作接收到的所有ConsumerRecord实例。使用此接口时不支持AckMode.RECORD，因为监听器会获得完整的批次。提供对Consumer对象的访问。
public interface BatchConsumerAwareMessageListener<K, V> extends BatchMessageListener<K, V> {
    void onMessage(List<ConsumerRecord<K, V>> data, Consumer<?, ?> consumer);
}

//当使用手动提交方法之一时，使用此接口处理从 Kafka 消费者poll()操作接收到的所有ConsumerRecord实例。提供对Consumer对象的访问。
public interface BatchAcknowledgingConsumerAwareMessageListener<K, V> extends BatchMessageListener<K, V> {
    void onMessage(List<ConsumerRecord<K, V>> data, Acknowledgment acknowledgment, Consumer<?, ?> consumer);
}
```

### 2、消息监听器容器

提供了两个`MessageListenerContainer`实现：

- `KafkaMessageListenerContainer`
- `ConcurrentMessageListenerContainer`

`KafkaMessageListenerContainer`在单个线程上接收来自所有主题或分区的所有消息。

`ConcurrentMessageListenerContainer` 委托给一个或多个`KafkaMessageListenerContainer`实例以提供多线程消费。

#### 使用`KafkaMessageListenerContainer`

```java
public KafkaMessageListenerContainer(ConsumerFactory<K, V> consumerFactory,
                    ContainerProperties containerProperties)
```

它接收`ConsumerFactory`以及有关主题和分区的信息，以及`ContainerProperties`对象中的其他配置。 `ContainerProperties`有以下构造函数：

```java
public ContainerProperties(TopicPartitionOffset... topicPartitions)

public ContainerProperties(String... topics)

public ContainerProperties(Pattern topicPattern)
```

第一个构造函数采用`TopicPartitionOffset`参数数组来显式指示容器要使用哪些分区（使用 Consumer 的`assign()`方法）并带有可选的初始偏移量。默认情况下，正值是绝对偏移量。默认情况下，负值是相对于分区内当前最后一个偏移量的。提供了带有附加`boolean`参数的`TopicPartitionOffset`构造函数。如果这是`true` ，则初始偏移（正或负）相对于该消费者的当前位置。偏移量在容器启动时应用。

第二个采用主题数组，Kafka 根据`group.id`属性分配分区 - 在 Group 中分配分区。

第三个使用正则表达式`Pattern`来选择主题。

要将`MessageListener`分配给容器，您可以使用 `ContainerProps.setMessageListener` 创建Container时的方法。以下示例展示了如何执行此操作：

```java
ContainerProperties containerProps = new ContainerProperties("topic1", "topic2");
containerProps.setMessageListener(new MessageListener<Integer, String>() {
    ...
});
DefaultKafkaConsumerFactory<Integer, String> cf =
                        new DefaultKafkaConsumerFactory<>(consumerProps());
KafkaMessageListenerContainer<Integer, String> container =
                        new KafkaMessageListenerContainer<>(cf, containerProps);
return container;
```

请注意，在创建`DefaultKafkaConsumerFactory`时，使用仅接受上述属性的构造函数意味着从配置中选取键和值`Deserializer`类。或者， `Deserializer`实例可以传递到`DefaultKafkaConsumerFactory`构造函数以获取键和/或值，在这种情况下，所有消费者共享相同的实例。另一种选择是提供`Supplier<Deserializer>` （从版本2.3开始），它将用于为每个`Consumer`获取单独的`Deserializer`实例：

#### 使用 `ConcurrentMessageListenerContainer`

单个构造函数类似于`KafkaListenerContainer`构造函数。以下清单显示了构造函数的签名：

```java
public ConcurrentMessageListenerContainer(ConsumerFactory<K, V> consumerFactory,
                            ContainerProperties containerProperties)
```

它还具有`concurrency`属性。例如， `container.setConcurrency(3)`创建三个`KafkaMessageListenerContainer`实例。

#### 监听器容器自动启动

侦听器容器实现`SmartLifecycle` ，并且`autoStartup`默认情况下为`true` 。容器在后期启动 ( `Integer.MAX-VALUE - 100` )。实现`SmartLifecycle`来处理来自侦听器的数据的其他组件应在早期阶段启动。 `- 100`为后续阶段留出了空间，使组件能够在容器之后自动启动。

### 3、提交 Offsets

提供了几个用于提交偏移量的选项。如果`enable.auto.commit`消费者属性为`true` ，Kafka会根据其配置自动提交偏移量。如果为`false` ，则容器支持多种`AckMode`设置（在下一个列表中描述）。默认`AckMode`是`BATCH` 。从版本 2.3 开始，框架将`enable.auto.commit`设置为`false` ，除非在配置中明确设置。以前，如果未设置该属性，则使用 Kafka 默认值 ( `true` )。

消费者`poll()`方法返回一个或多个`ConsumerRecords` 。为每条记录调用`MessageListener` 。以下列表描述了容器对每个`AckMode`采取的操作（当未使用事务时）：

- `RECORD`: 当侦听器处理记录后返回时提交偏移量。
- `BATCH`: 当`poll()`返回的所有记录都已处理完毕时提交偏移量。
- `TIME`: 当`poll()`返回的所有记录都已处理完毕时，只要超过了自上次提交以来的`ackTime` ，就提交偏移量。
- `COUNT`: 当`poll()`返回的所有记录都已处理完毕时，只要自上次提交以来已收到`ackCount`记录，就提交偏移量。
- `COUNT_TIME`: 与`TIME`和`COUNT`类似，但如果任一条件为`true` ，则执行提交。
- `MANUAL`: 消息侦听器负责`acknowledge()` `Acknowledgment` 。之后，应用与`BATCH`相同的语义。
- `MANUAL_IMMEDIATE`: 当侦听器调用`Acknowledgment.acknowledge()`方法时立即提交偏移量。

### 4、异步@KafkaListener返回类型

从版本 3.2 开始， `@KafkaListener` （和`@KafkaHandler` ）方法可以指定异步返回类型，从而异步发送回复。返回类型包括`CompletableFuture<?>` 、 `Mono<?>`和 Kotlin `suspend`函数。

```java
@KafkaListener(id = "myListener", topics = "myTopic")
public CompletableFuture<String> listen(String data) {
    ...
    CompletableFuture<String> future = new CompletableFuture<>();
    future.complete("done");
    return future;
}

@KafkaListener(id = "myListener", topics = "myTopic")
public Mono<Void> listen(String data) {
    ...
    return Mono.empty();
}
```

### 5、@KafkaListener注解

`@KafkaListener`注解用于将 bean 方法指定为侦听器容器的侦听器。这个 Bean 被包裹在一个 `MessagingMessageListenerAdapter` 配置了各种功能，例如用于转换数据的转换器（如有必要）以匹配方法参数。

`@KafkaListener`注解为简单的 POJO 监听器提供了一种机制。以下示例展示了如何使用它：

```java
public class Listener {

    @KafkaListener(id = "foo", topics = "myTopic", clientIdPrefix = "myClientId")
    public void listen(String data) {
        ...
    }

}
```

此机制需要在`@Configuration`类之一和侦听器容器工厂上使用`@EnableKafka`注释，该工厂用于配置底层 `ConcurrentMessageListenerContainer` 。默认情况下，需要名为`kafkaListenerContainerFactory`的 bean。下面的例子展示了如何使用 `ConcurrentMessageListenerContainer` :

```java
@Configuration
@EnableKafka
public class KafkaConfig {

    @Bean
    KafkaListenerContainerFactory<ConcurrentMessageListenerContainer<Integer, String>>
                        kafkaListenerContainerFactory() {
        ConcurrentKafkaListenerContainerFactory<Integer, String> factory =
                                new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory());
        factory.setConcurrency(3);
        factory.getContainerProperties().setPollTimeout(3000);
        return factory;
    }

    @Bean
    public ConsumerFactory<Integer, String> consumerFactory() {
        return new DefaultKafkaConsumerFactory<>(consumerConfigs());
    }

    @Bean
    public Map<String, Object> consumerConfigs() {
        Map<String, Object> props = new HashMap<>();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        ...
        return props;
    }
}
```

请注意，要设置容器属性，您必须使用工厂上的`getContainerProperties()`方法。它用作注入到容器中的实际属性的模板。

#### 显式分配分区

您还可以使用显式主题和分区（以及可选的初始偏移量）配置 POJO 侦听器。以下示例展示了如何执行此操作：

```java
@KafkaListener(id = "thing2", topicPartitions =
        { @TopicPartition(topic = "topic1", partitions = { "0", "1" }),
          @TopicPartition(topic = "topic2", partitions = "0",
             partitionOffsets = @PartitionOffset(partition = "1", initialOffset = "100"))
        })
public void listen(ConsumerRecord<?, ?> record) {
    ...
}
```

您可以在`partitions`或`partitionOffsets`属性中指定每个分区，但不能同时指定两者。

与大多数注释属性一样，您可以使用 SpEL 表达式；从版本 2.5.5 开始，您可以将初始偏移应用于所有分配的分区：

```java
@KafkaListener(id = "thing3", topicPartitions =
        { @TopicPartition(topic = "topic1", partitions = { "0", "1" },
             partitionOffsets = @PartitionOffset(partition = "*", initialOffset = "0"))
        })
public void listen(ConsumerRecord<?, ?> record) {
    ...
}
```

`*`通配符代表`partitions`属性中的所有分区。每个`@TopicPartition`中只能有一个带有通配符的`@PartitionOffset` 。

从版本 2.6.4 开始，您可以指定以逗号分隔的分区列表或分区范围：

```java
@KafkaListener(id = "pp", autoStartup = "false",
        topicPartitions = @TopicPartition(topic = "topic1",
                partitions = "0-5, 7, 10-15"))
public void process(String in) {
    ...
}
```

指定初始偏移量时可以使用相同的技术：

```java
@KafkaListener(id = "thing3", topicPartitions =
        { @TopicPartition(topic = "topic1",
             partitionOffsets = @PartitionOffset(partition = "0-5", initialOffset = "0"))
        })
public void listen(ConsumerRecord<?, ?> record) {
    ...
}
```

从3.2开始， `@PartitionOffset`支持`SeekPosition.END` ， `SeekPosition.BEGINNING` ， `SeekPosition.TIMESTAMP` ， `seekPosition`匹配`SeekPosition`枚举名称：

```java
@KafkaListener(id = "seekPositionTime", topicPartitions = {
        @TopicPartition(topic = TOPIC_SEEK_POSITION, partitionOffsets = {
                @PartitionOffset(partition = "0", initialOffset = "723916800000", seekPosition = "TIMESTAMP"),
                @PartitionOffset(partition = "1", initialOffset = "0", seekPosition = "BEGINNING"),
                @PartitionOffset(partition = "2", initialOffset = "0", seekPosition = "END")
        })
})
public void listen(ConsumerRecord<?, ?> record) {
    ...
}
```

如果seekPosition设置为`END`或`BEGINNING`将忽略`initialOffset`和`relativeToCurrent` 。如果seekPosition设置了`TIMESTAMP` ， `initialOffset`表示时间戳。

#### 手动确认

当使用手动`AckMode`时，您还可以向侦听器提供`Acknowledgment` 。以下示例还展示了如何使用不同的容器工厂。

```java
@KafkaListener(id = "cat", topics = "myTopic",
          containerFactory = "kafkaManualAckListenerContainerFactory")
public void listen(String data, Acknowledgment ack) {
    ...
    ack.acknowledge();
}
```

#### 消费记录元数据

最后，有关记录的元数据可从消息标头获得。您可以使用以下标头名称来检索消息的标头：

- `KafkaHeaders.OFFSET`
- `KafkaHeaders.RECEIVED_KEY`
- `KafkaHeaders.RECEIVED_TOPIC`
- `KafkaHeaders.RECEIVED_PARTITION`
- `KafkaHeaders.RECEIVED_TIMESTAMP`
- `KafkaHeaders.TIMESTAMP_TYPE`

以下示例展示了如何使用标头：

```java
@KafkaListener(id = "qux", topicPattern = "myTopic1")
public void listen(@Payload String foo,
        @Header(name = KafkaHeaders.RECEIVED_KEY, required = false) Integer key,
        @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
        @Header(KafkaHeaders.RECEIVED_TOPIC) String topic,
        @Header(KafkaHeaders.RECEIVED_TIMESTAMP) long ts
        ) {
    ...
}
```

> 监听方法的具体实现上必须指定参数注解（ `@Payload` 、 `@Header` ）；如果它们是在接口上定义的，则不会检测到它们。

从版本 2.5 开始，您可以在`ConsumerRecordMetadata`参数中接收记录元数据，而不是使用离散标头。

```java
@KafkaListener(...)
public void listen(String str, ConsumerRecordMetadata meta) {
    ...
}
```

#### 批量监听器

要配置 ListenerContainerFactory 以创建批量侦听器，您可以设置`batchListener`属性。以下示例展示了如何执行此操作：

```java
@Bean
public KafkaListenerContainerFactory<?> batchFactory() {
    ConcurrentKafkaListenerContainerFactory<Integer, String> factory =
            new ConcurrentKafkaListenerContainerFactory<>();
    factory.setConsumerFactory(consumerFactory());
    factory.setBatchListener(true);  // <<<<<<<<<<<<<<<<<<<<<<<<<
   return factory;
}
```

以下示例显示如何接收文本集合：

```java
@KafkaListener(id = "list", topics = "myTopic", containerFactory = "batchFactory")
public void listen(List<String> list) {
    ...
}
```

主题、分区、偏移量等在与有效负载并行的标头中可用。以下示例展示了如何使用标头：

```java
@KafkaListener(id = "list", topics = "myTopic", containerFactory = "batchFactory")
public void listen(List<String> list,
        @Header(KafkaHeaders.RECEIVED_KEY) List<Integer> keys,
        @Header(KafkaHeaders.RECEIVED_PARTITION) List<Integer> partitions,
        @Header(KafkaHeaders.RECEIVED_TOPIC) List<String> topics,
        @Header(KafkaHeaders.OFFSET) List<Long> offsets) {
    ...
}
```

或者，您可以接收`Message<?>`对象`List` ，其中包含每条消息中的每个偏移量和其他详细信息，但它必须是唯一的参数（除了可选的`Acknowledgment` ，当使用手动提交和/或`Consumer<?, ?>`参数）在方法上定义。以下示例展示了如何执行此操作：

```java
@KafkaListener(id = "listMsg", topics = "myTopic", containerFactory = "batchFactory")
public void listen1(List<Message<?>> list) {
    ...
}

@KafkaListener(id = "listMsgAck", topics = "myTopic", containerFactory = "batchFactory")
public void listen2(List<Message<?>> list, Acknowledgment ack) {
    ...
}

@KafkaListener(id = "listMsgAckConsumer", topics = "myTopic", containerFactory = "batchFactory")
public void listen3(List<Message<?>> list, Acknowledgment ack, Consumer<?, ?> consumer) {
    ...
}
```

您还可以接收`ConsumerRecord<?, ?>`对象的列表，但它必须是该方法上定义的唯一参数（除了可选的`Acknowledgment` ，当使用手动提交和`Consumer<?, ?>`参数时）。以下示例展示了如何执行此操作：

```java
@KafkaListener(id = "listCRs", topics = "myTopic", containerFactory = "batchFactory")
public void listen(List<ConsumerRecord<Integer, String>> list) {
    ...
}

@KafkaListener(id = "listCRsAck", topics = "myTopic", containerFactory = "batchFactory")
public void listen(List<ConsumerRecord<Integer, String>> list, Acknowledgment ack) {
    ...
}
```

#### 注释属性

从版本 2.0 开始， `id`属性（如果存在）用作 Kafka 消费者`group.id`属性，覆盖消费者工厂中配置的属性（如果存在）。您还可以显式设置`groupId`或将`idIsGroup`设置为 false 以恢复之前使用消费者工厂`group.id`的行为。

您可以在大多数注释属性中使用属性占位符或 SpEL 表达式，如以下示例所示：

```java
@KafkaListener(topics = "${some.property}")

@KafkaListener(topics = "#{someBean.someProperty}",
    groupId = "#{someBean.someProperty}.group")
```

从版本 2.1.2 开始，SpEL 表达式支持特殊标记： `__listener` 。它是一个伪 bean 名称，表示此注释所在的当前 bean 实例。

例如：

```java
@Bean
public Listener listener1() {
    return new Listener("topic1");
}

@Bean
public Listener listener2() {
    return new Listener("topic2");
}
```

上一个示例中的 bean，我们可以使用以下内容：

```java
public class Listener {

    private final String topic;

    public Listener(String topic) {
        this.topic = topic;
    }

    @KafkaListener(topics = "#{__listener.topic}",
        groupId = "#{__listener.topic}.group")
    public void listen(...) {
        ...
    }

    public String getTopic() {
        return this.topic;
    }

}
```

如果万一您有一个名为`__listener`的实际 bean，则可以使用`beanRef`属性更改表达式标记。以下示例展示了如何执行此操作：

```java
@KafkaListener(beanRef = "__x", topics = "#{__x.topic}", groupId = "#{__x.topic}.group")
```

从版本 2.2.4 开始，您可以直接在注释上指定 Kafka 消费者属性，这些属性将覆盖消费者工厂中配置的任何同名属性。您**不能**以这种方式指定`group.id`和`client.id`属性；他们会被忽视；使用`groupId`和`clientIdPrefix`注释属性。

这些属性被指定为具有正常 Java `Properties`文件格式的单独字符串： `foo:bar` 、 `foo=bar`或`foo bar` ，如以下示例所示：

```java
@KafkaListener(topics = "myTopic", groupId = "group", properties = {
    "max.poll.interval.ms:60000",
    ConsumerConfig.MAX_POLL_RECORDS_CONFIG + "=100"
})
```

### 6、获取Consumer group.id

当在多个容器中运行相同的侦听器代码时，能够确定记录来自哪个容器（由其`group.id`消费者属性标识）可能会很有用。

您可以使用 `KafkaUtils.getConsumerGroupId()` 在侦听器线程上执行此操作。或者，您可以在方法参数中访问组 ID。

```java
@KafkaListener(id = "id", topicPattern = "someTopic")
public void listener(@Payload String payload, @Header(KafkaHeaders.GROUP_ID) String groupId) {
    ...
}
```

