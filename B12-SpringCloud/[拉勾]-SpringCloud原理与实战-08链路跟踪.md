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









