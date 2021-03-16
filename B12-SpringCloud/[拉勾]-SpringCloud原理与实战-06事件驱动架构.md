# 20 | 消息驱动：Spring 中对消息处理机制的抽象过程

Spring Cloud 专门提供了一个 Spring Cloud Stream 框架来实现事件驱动架构，并完成与主流消息中间件的集成。

**事件驱动架构**

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210316151433.png" alt="image-20210316151433557" style="zoom: 33%;" />

在上图中，事件生产者和消费者之间的虚线代表的是一种相互松散、没有直接调用的关联关系。满足以上特性的系统代表着一种松耦合的架构，通常被称为事件驱动架构，而这里的事件也可以被理解是服务与服务之间发送的一种消息。

事件驱动架构本质上是一种架构设计风格，实现方法和工具有很多。在 Spring Cloud 家族中这个工具就是 Spring Cloud Stream。

**Spring 家族中的消息处理机制**

在 Spring 家族中，与消息处理机制相关的框架有三个。Spring Cloud Stream 是基于 Spring Integration 实现了消息发布和消费机制并提供了一层封装，而在 Spring Integration 的背后，则依赖于 Spring Messaging 组件来实现消息处理机制的基础设施。

这三个框架之间的依赖关系如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210316152133.png" alt="image-20210316152132946" style="zoom: 33%;" />

接下来的内容，我们先来对位于底层的 Spring Messaging 和 Spring Integration 框架做一些展开。

1. Spring Messaging

Spring Messaging 是 Spring 框架中的一个底层模块，用于提供统一的消息编程模型。例如，消息这个数据单元在 Spring Messaging 中统一定义为如下所示的 Message 接口：

```java
public interface Message<T> {
    T getPayload();
    MessageHeaders getHeaders();
}
```

消息通道 MessageChannel 的定义也比较简单：

```java
public interface MessageChannel {
    long INDEFINITE_TIMEOUT = -1;
    default boolean send(Message<?> message) {
        return send(message, INDEFINITE_TIMEOUT);
    }
    boolean send(Message<?> message, long timeout);
}
```

通道的名称对应的就是队列的名称，但是作为一种抽象和封装，各个消息传递系统所特有的队列概念并不会直接暴露在业务代码中，而是通过通道来对队列进行配置。

Spring Messaging 在基础消息模型之上还提供了很多方便在业务系统中使用消息传递机制的辅助功能，例如各种消息体内容转换器 MessageConverter 以及消息通道拦截器 ChannelInterceptor 等。

2. Spring Integration

Spring Integration 是对 Spring Messaging 的扩展，提供了对系统集成领域的经典著作《企业集成模式：设计构建及部署消息传递解决方案》中所描述的各种企业集成模式的支持，通常被认为是一种企业服务总线 ESB 框架。

Spring Integration 的设计目的是系统集成，因此内部提供了大量的集成化端点方便应用程序直接使用。当各个异构系统之间进行集成时，如何屏蔽各种技术体系所带来的差异性，Spring Integration 为我们提供了解决方案。通过通道之间的消息传递，在消息的入口和出口我们可以使用通道适配器和消息网关这两种典型的端点对消息进行同构化处理。

# 21 | 消息架构：Spring Cloud Stream 的基本架构

**Spring Cloud Stream 基本架构**

Spring Cloud Stream 在消息生产者和消费者之间添加了一种桥梁机制，所有的消息都将通过 Spring Cloud Stream 进行发送和接收，如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210316215557.png" alt="image-20210316215557193" style="zoom:50%;" />

Spring Cloud Stream 具备四个核心组件，分别是 Binder、Channel、Source 和 Sink，其中 Binder 和 Channel 成对出现，而 Source 和 Sink 分别面向消息的发布者和消费者。

- Source 和 Sink

Source 组件是真正生成消息的组件，相当于是一个输出（Output）组件。而 Sink 则是真正消费消息的组件，相当于是一个输入（Input）组件。

Source 组件使用一个普通的 POJO 对象来充当需要发布的消息，通过将该对象进行序列化（默认的序列化方式是 JSON）然后发布到 Channel 中。另一方面，Sink 组件监听 Channel 并等待消息的到来，一旦有可用消息，Sink 将该消息反序列化为一个 POJO 对象并用于处理业务逻辑。

- Channel

在消息传递系统中，队列的作用就是实现存储转发的媒介，消息生产者所生成的消息都将保存在队列中并由消息消费者进行消费。通道的名称对应的往往就是队列的名称。

- Binder

Spring Cloud Stream 中最重要的概念就是 Binder。所谓 Binder，顾名思义就是一种黏合剂，将业务服务与消息传递系统黏合在一起。通过 Binder，我们可以很方便地连接消息中间件，可以动态的改变消息的目标地址、发送方式而不需要了解其背后的各种消息中间件在实现上的差异。

**Spring Cloud Stream 集成 Spring 消息处理机制**

在如下所示的代码中，我们定义了 SpringHealthChannel 接口并声明了一个 Input 通道和两个 Output 通道，说明使用该通道的服务会从外部的一个通道中获取消息并向外部的两个通道发送消息：

```java
public interface SpringHealthChannel {
    @Input
    SubscribableChannel input1();

    @Output
    MessageChannel output1();
  
    @Output
    MessageChannel output2();
}
```

上述接口定义中同时使用到了 Spring Messaging 中的 SubscribableChannel 和 MessageChannel。Spring Cloud Stream 对 Spring Messaging 和 Spring Integration 提供了原生支持。

**Spring Cloud Stream 集成消息中间件**

在接下来的内容中，我们将梳理 Spring Cloud Stream 中的消息传递模型，并给出 Binder 与消息中间件如何进行整合的过程。

1. Spring Cloud Stream 中的消息传递模型

- 发布-订阅模型

在 Spring Cloud Stream 中，统一通过发布-订阅模型完成消息的发布和消费，如下所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210316221701.png" alt="image-20210316221701734" style="zoom:50%;" />

- 消费者组

一条消息就只能被同一个组中的某一个服务实例所消费。消费者的基本结构如下图所示（其中虚线表示不会发生的消费场景）：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210316221822.png" alt="image-20210316221822025" style="zoom:50%;" />

- 消息分区

同一分区中的消息能够确保始终是由同一个消费者实例进行消费。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210316222006.png" alt="image-20210316222006133" style="zoom: 33%;" />

# 22 | 消息发布：如何使用 Spring Cloud Stream 实现消息发布者和消费者？（上）

**设计 SpringHealth 中的消息发布场景**

类似 SpringHealth 这样的系统中的用户信息变动并不会太频繁，所以很多时候我们会想到通过缓存系统来存放用户信息。而一旦用户信息发生变化，user-service 可以发送一个事件，给到相关的订阅者并更新缓存信息，如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210316224022.png" alt="image-20210316224022503" style="zoom:50%;" />

接下来我们关注于上图中的事件发布者 user-service。在 user-service 中需要设计并实现使用 Spring Cloud Stream 发布消息的各个组件，包括 Source、Channel 和 Binder。我们围绕 UserInfoChangedEvent 事件给出 user-service 内部的整个实现流程，如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210316224120.png" alt="image-20210316224120602" style="zoom:50%;" />

**实现消息发布者**

1. 使用 @EnableBinding 注解

引入依赖：

```xml
<dependency>
  <groupId>org.springframework.cloud</groupId>
  <artifactId>spring-cloud-stream</artifactId>
</dependency>

<dependency>
  <groupId>org.springframework.cloud</groupId>
  <artifactId>spring-cloud-starter-stream-kafka</artifactId>
</dependency>
```

启动类：

```java
@SpringCloudApplication
@EnableBinding(Source.class)
public class UserApplication {
    public static void main(String[] args) {
        SpringApplication.run(UserApplication.class, args);
    }
}
```

2. 定义 Event

```java
public class UserInfoChangedEvent{
    //事件类型
    private String type;
    //事件所对应的操作
    private String operation;
    //事件对应的领域模型
    private User user;
}
```

3. 创建 Source

```java
@Component
public class UserInfoChangedSource {
    private Source source;
 
    private static final Logger logger = LoggerFactory.getLogger(UserInfoChangedSource.class);
  
    @Autowired
    public UserInfoChangedSource(Source source) {
        this.source = source;
    }
 
    private void publishUserInfoChangedEvent(UserInfoOperation operation, User user) {
      
        logger.debug("Sending message for UserId: {}", user.getId());
     
        UserInfoChangedEvent change =  new UserInfoChangedEvent(
            UserInfoChangedEvent.class.getTypeName(),
            operation.toString(),
            user);
 
        source.output().send(MessageBuilder.withPayload(change).build());
    }

    public void publishUserInfoUpdatedEvent(User user) {
         publishUserInfoChangedEvent(UserInfoOperation.UPDATE, user);
    }

}
```

4. 配置 Binder

```yaml
spring:
  cloud:
    stream:
      bindings:
        output:
          destination: userInfoChangedTopic
          content-type: application/json
      kafka:
        binder:
          zk-nodes: localhost
        brokers: localhost
```

5. 集成服务

```java
@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
 
    @Autowired
    private UserInfoChangedSource userInfoChangedSource;
 
    public void updateUser(User user){
        userRepository.save(user);
        userInfoChangedSource.publishUserInfoUpdatedEvent(user);
    }
 
}
```

**设计 SpringHealth 中的消息消费场景**

负责消费消息的是 Sink 组件，因此，我们同样围绕 UserInfoChangedEvent 事件给出 intervention-service 内部的整个实现流程，如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210316225158.png" alt="image-20210316225158301" style="zoom:50%;" />

Spring Cloud Stream 通过 Sink 获取消息并交由 UserInfoChangedSink 实现具体的消费逻辑。

![image-20210316225547206](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210316225547.png)





