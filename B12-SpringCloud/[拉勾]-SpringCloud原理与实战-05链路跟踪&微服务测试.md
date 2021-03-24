# 链路跟踪

# 29 | 监控原理：服务监控和 Spring Cloud Sleuth 的基本原理？

**服务监控基本原理**

我们首先需要引入两个基本概念，即 SpanId 和 TraceId。

- SpanId

SpanId 一般被称为跨度 Id。服务 A 位于服务 B 的上游，所以访问服务 A 所生成的 SpanId 应该是访问服务 B 所生成的 SpanId 的父 SpanId。

- TraceId

把请求通过所有服务的 Span 都串联起来，生成一个全局的唯一性 Id，这个唯一性 Id 就是 TraceId。

关于 Span，业界一般使用四种关键事件记录每个服务的客户端请求和服务器响应过程。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210322214404.png" alt="image-20210322214404008" style="zoom:50%;" />

在上图中，cs 表示 Client Send，代表了一个 Span 的开始。sr 代表 Server Receive，表示服务端接收客户端的请求。ss 代表 Server Send，表示服务器返回结果给客户端。cr 表示 Client Receive，表示客户端接收到了服务器端返回的结果，代表着一个 Span 的完成。

> 我们可以通过计算这四个关键时间之前的差值来获取 Span 中的时间信息。
>
> 显然，sr-cs 值等于请求的网络延迟，ss-sr 值表示服务端处理请求的时间，而 cr-sr 值则代表客户端接收服务端数据的时间。

要实现服务跟踪，首先，我们需要对整个调用过程的所有服务进行埋点并生成事件，并对这些事件数据进行采集。然后，我们还需要对采集到的事件数据进行各种指标运算，并将运算结果保存起来，并提供各种排序、阈值设置和警告等功能。

**使用 Spring Cloud Sleuth 实现服务监控**

引入依赖：

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-sleuth</artifactId>
</dependency>
```

日志打印格式如下所示：

```
[服务名称, TraceId, SpanId, Zipkin 标志位]
```

第一段中的 userservice 代表着该服务的名称，使用的就是在 bootstrap.yml 中 spring.application.name 指定的服务名称。

第二段中的 TraceId 代表一次完整请求的唯一编号。在诸如 Zipkin 等可视化工具中，可以通过 TraceId 查看完整的服务调用链路。

第三段的 SpanId 与 TraceId 是多对一的关系，每一个 SpanId 都从属于特定的 TraceId。当然，也可以通过 SpanId 查看某一个服务调用过程的详细信息。

第四段代表 Zipkin 标志位，该标志位用于识别是否将服务跟踪信息同步到 Zipkin。

# 30 | 监控可视：整合 Spring Cloud Sleuth 与 Zipkin 实现可视化监控

**Zipkin 简介**

Zipkin 是一个开源的分布式跟踪系统，每个服务向 Zipkin 报告运行时数据，Zipkin 会根据调用关系通过 Zipkin UI 对整个调用链路中的数据实现可视化。在结构上 Zipkin 包含几个核心的组件，如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210322232931.png" alt="image-20210322232931040" style="zoom:50%;" />

日志的收集组件 Collector，接收来自外部传输（Transport）的数据，将这些数据转换为 Zikpin 内部处理的 Span 格式。这些收集的数据通过存储组件 Storage 进行存储，当前支持 Cassandra、Redis、HBase、MySQL、PostgreSQL、SQLite 等工具，默认存储在内存中。

所存储数据可以通过 RESTful API 对外暴露查询接口。Zipkin 还提供了一套简单的 Web 界面，可以查询和分析跟踪信息。

**集成 Zipkin 服务器**

为了集成 Zipkin 服务器，在各个微服务中，需要确保添加了对 Spring Cloud Sleuth 和 Zipkin 的 Maven 依赖，如下所示。

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-sleuth</artifactId>
</dependency>

<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-sleuth-zipkin</artifactId>
</dependency>
```

然后，在配置文件中添加对 Zipkin 服务器的引用即可，配置内容如下所示。

```yml
spring:
	zipkin:
	  baseUrl: http://localhost:9411
```

至此，Zipkin 环境已经搭建完毕，我们可以通过访问 http://localhost:9411 来获取 Zipkin 所提供的所有可视化结果，接下来将演示如何使用 Zipkin 跟踪服务调用链路。

**使用 Zipkin 可视化服务调用链路**

Zipkin 可视化服务调用链路的构建包含三大维度：可视化服务依赖关系、可视化服务调用时序、可视化服务调用数据。

1. 可视化服务依赖关系

当系统规模越来越大后，各个业务服务之间的直接依赖和间接依赖关系就会变得十分复杂。我们需要通过一个简洁明了的可视化工具来查看当前服务链路中的依赖关系，Zipkin 就提供了这方面的支持。

2. 可视化服务调用时序

![image-20210323210917238](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210323210917.png)

当发起这个 HTTP 请求时，该请求会先到达 Zuul 网关，然后再通过路由转发到 userservice。

> 注意到这里 userservice 出现了两个 Span，原因在于 userservice 在该请求中还访问了 OAuth2 的授权服务器。

3. 可视化服务调用数据

点击“get /users/username/{username}”这个 Span，Zipkin 会跳转到一个新的页面并显示如下图所示的数据：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210323211743.png" alt="image-20210323211743527" style="zoom:50%;" />

# 31 | 监控扩展：使用 Tracer 在访问链路中创建自定义的 Span

今天的内容我们将围绕如何使用 Spring Cloud Sleuth 底层的 Brave 框架在服务访问链路中添加自定义 Span 这一话题展开讨论。

**使用 Brave 创建自定义 Span**

我们首先来关注 Brave 中的 Span 类，该类的方法如下：

```java
public abstract class Span {
  
  /** 设置开始时间 */
  public Span start(long timestamp);
  
  /** 设置结束时间 */
  public void finish(long timestamp);
  
  /** 指定四种监控事件 */
  public Span annotate(long timestamp, String value);
  
  /** 为Span打标签 */
  public Span tag(String key, String value);
}
```

了解了 Span 的定义之后，我们就来讨论在业务代码中创建 Span 的两种方法。一种是使用 Brave 中的 Tracer 类，一种是使用注解。

**通过 Tracer 类创建 Span**

```java
@Service
public class MyService {

    @Autowired
    private Tracer tracer;

    public void perform() {
         Span newSpan = tracer.nextSpan().name("spanName").start();
        //ScopedSpan newSpan = tracer.startScopedSpan("spanName");
        try {
            //执行业务逻辑
        }
        finally{
          newSpan.tag("key", "value");
          newSpan.annotate("myannotation");
          newSpan.finish();
        }
    }
}
```

上述代码创建并启动了一个“spanName”新的 Span。这是在业务代码中嵌入自定义 Span 的一种方法。

另一种方法是使用注释行代码中的 ScopedSpan。

**使用注解创建 Span**

自动创建一个新的 Span：

```java
@NewSpan
void myMethod();
```

@SpanTag 注解自动为通过 @NewSpan 注解所创建的 Span 添加标签：

```java
@NewSpan(name = "myspan")
void myMethod(@SpanTag("mykey") String param);
```

**使用 Zipkin 集成自定义跟踪**

在某些特定场景下，我们希望在这些 Span 的基础上能够实现一些定制化的数据收集和展示方式。

假设在服务调用链路中，某一个方法调用时间比较长。通过方法默认的 Span 通常无法判断响应时间过长的原因。

那么就可以通过添加一系列的自定义 Span 的方式对长时间的服务调用进行拆分，把该请求中所涉及的多种操作分别创建 Span，然后找到最影响性能的 Span 并进行优化，这也是服务监控系统实现过程中的一项最佳实践，如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210323234740.png" alt="image-20210323234740589" style="zoom:50%;" />



****

# 微服务测试

# 32 | 测试方案：微服务的测试解决方案

**微服务测试的系统方法**

在测试微服务架构中需要面对的两个核心问题，即如何验证组件级别的正确性以及如何验证服务级别的正确性。

1. 如何验证组件级别的正确性？

验证组件级别正确性的一大难点在于关于组件与组件之间的依赖关系，常见的技巧就是使用 Mock 对象来替代真实的依赖对象，从而模拟真实的调用场景。

2. 如何验证服务级别的正确性？

服务与服务之间的验证工作一般指的是系统测试，涉及整体应用环境在现实场景中的系统测试也被称为是一种端到端（End-to-End）测试。

端到端测试相对复杂，目前有一种测试策略为我们提供了解决方案，这就是面向契约的消费者驱动测试。

**消费者驱动的契约测试**

1. 什么是消费者驱动契约测试？

对于任何一个服务所暴露的对外接口，我们都可以把它们归为是一种契约（Contract），即接口的调用者希望通过接口获取某种约定的价值。消费者驱动的契约测试就是基于契约思想而诞生的一种端到端测试方法。

那么一个合理的契约应该包括哪些组成部分呢？显然，契约一方面应该定义其他微服务所期望的数据格式、支持的操作方法以及访问的协议。另一方面，也可以约定调用时延或吞吐量等非功能性约束和条件。

2. 如何开展消费者驱动契约测试？

消费者驱动契约测试实施过程如下：契约测试业务场景提取、服务消费者请求契约化、模拟服务消费者发送请求、服务提供者验证契约。

作为一个完整的微服务套件，Spring Cloud 也提供了 Spring Cloud Contract 作为消费者驱动契约测试的开发框架。























