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



### Factory Listeners

从版本 2.5 开始，可以使用`Listener`配置`DefaultKafkaProducerFactory`和`DefaultKafkaConsumerFactory` ，以便在创建或关闭生产者或消费者时接收通知。

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

### 默认Client ID前缀

从版本 3.2 开始，对于使用`spring.application.name`属性定义应用程序名称的 Spring Boot 应用程序，该名称现在用作这些客户端类型自动生成的客户端 ID 的默认前缀：

- 不使用消费者组的消费者客户端
- 生产者客户端
- admin clients

这使得在服务器端识别这些客户端以进行故障排除或应用配额变得更加容易。

*表 1. 使用*`spring.application.name=myapp` *Spring Boot 应用程序生成的示例客户端 ID*

| 客户端类型                | 没有应用程序名称   | 有应用程序名称     |
| :------------------------ | :----------------- | :----------------- |
| 没有消费者组的消费者      | consumer-null-1    | myapp-consumer-1   |
| 消费者组“mygroup”的消费者 | consumer-mygroup-1 | consumer-mygroup-1 |
| producer                  | producer-1         | myapp-producer-1   |
| admin                     | adminclient-1      | myapp-admin-1      |

## 2.2 配置Topic



## 2.3 发送消息

### 使用`KafkaTemplate`

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

### 使用`RoutingKafkaTemplate`

从版本 2.5 开始，您可以使用`RoutingKafkaTemplate`根据目标`topic`名称在运行时选择生产者。

以下简单的 Spring Boot 应用程序提供了一个示例，说明如何使用相同的模板发送到不同的主题，每个主题使用不同的值序列化器。

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

### 使用`DefaultKafkaProducerFactory`

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

### 使用`ReplyingKafkaTemplate`

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











