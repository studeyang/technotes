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





