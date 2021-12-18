# 09 | 框架升级：WebFlux 比 Web MVC 到底好在哪里？

从本讲开始，我们将围绕一个典型的多层架构，从每一层出发构建响应式应用程序。首先关注的是 Web 服务层。

**Spring WebFlux 的应用场景**

微服务架构的兴起为 WebFlux 的应用提供了一个很好的场景。在一个微服务系统中，数百个独立的微服务相互通信势必会涉及大量的 I/O 操作，尤其是阻塞式 I/O 操作会整体增加系统的延迟并降低吞吐量。如果能够在复杂的流程中集成非阻塞、异步通信机制，我们就可以高效处理跨服务之间的网络请求。针对这种场景，WebFlux 是一种非常有效的解决方案。

**从 WebMVC 到 WebFlux**

让我们先从传统的 Spring WebMVC 技术栈开始说起。

**Spring WebMVC技术栈**

Spring WebMVC 使用了“管道-过滤器（Pipe-Filter）”架构模式，使用了 Servlet 中的过滤器链（FilterChain）来对请求进行拦截，如下图所示。

![Drawing 0.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211214225534.png)

我们知道 WebMVC 运行在 Servlet 容器上，当 HTTP 请求通过 Servlet 容器时就会被转换为一个 ServletRequest 对象，而最终返回一个 ServletResponse 对象，一次请求的详细流程如下图所示。





![img](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211214222446.jpg)

在执行过程中，DispatcherServlet 会在应用上下文中搜索所有 HandlerMapping。如果我们使用了 @RequestMapping，那么会找到 RequestMappingHandlerMapping，对应的 HandlerAdapter 就是 RequestMappingHandlerAdapter

> 常用的 HandlerMapping 包含：
>
> - BeanNameUrlHandlerMapping：负责检测所有 Controller 并根据请求 URL 的匹配规则映射到具体的 Controller 实例上。
> - RequestMappingHandlerMapping：基于 @RequestMapping 注解来找到目标 Controller。

关键的类定义如下：

```java
public interface FilterChain {
    public void doFilter (ServletRequest request, ServletResponse response ) throws IOException, ServletException;
}
```

```java
public interface HandlerMapping {
    //找到与请求对应的 Handler，封装为一个 HandlerExecutionChain 返回
    HandlerExecutionChain getHandler(HttpServletRequest request) throws Exception;
}
```

```java
public interface HandlerAdapter {
    //针对给定的请求/响应对象调用目标 Handler
    ModelAndView handle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception;
}
```

Spring WebMVC 的整体架构，如下图所示。

![Drawing 1.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211214230501.png)

**Spring WebFlux 技术栈**

前面介绍的 HandlerMapping、HandlerAdapter 等组件在 WebFlux 里都有同名的响应式版本。在 WebFlux 中，代表请求和响应的是全新的 ServerHttpRequest 和 ServerHttpResponse 对象。

和 WebMVC 中的 DispatcherServlet 相对应的组件是 DispatcherHandler。与 DispatcherServlet 类似，DispatcherHandler 同样使用了一套响应式版本的 HandlerMapping 和 HandlerAdapter 完成对请求的处理。

> 请注意，HandlerMapping 和 HandlerAdapter 是定义在 org.springframework.web.reactive 包中的。

关键的类定义如下：

```java
public interface WebFilterChain {
    //ServerWebExchange 相当于一个上下文容器
    //保存了 ServerHttpRequest、ServerHttpResponse 以及一些框架运行时状态信息
    Mono<Void> filter(ServerWebExchange exchange);
}
```

```java
public interface HandlerMapping {
    //ServerWebExchange 中包含了 ServerHttpRequest 和 ServerHttpResponse 对象
    Mono<Object> getHandler(ServerWebExchange exchange);
}
```

```java
public interface HandlerAdapter {
    //HandlerResult 代表处理结果
    Mono<HandlerResult> handle(ServerWebExchange exchange, Object handler);
}
```

在 WebFlux 中，同样实现了响应式版本的 RequestMappingHandlerMapping 和 RequestMappingHandlerAdapter，因此我们仍然可以采用注解的方法来构建 Controller。

另一方面，WebFlux 中还提供了 RouterFunctionMapping 和 HandlerFunctionAdapter 组合，专门用来提供基于函数式编程的开发模式。这样 Spring WebFlux 的整体架构图就演变成这样。

![Drawing 2.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211214231324.png)

**对比 WebFlux 和 WebMVC 的处理模型**

WebMVC 建立在阻塞 I/O 之上，我们来分析这种模型下线程处理请求的过程。

假设有一个工作线程会处理来自客户端的请求，所有请求构成一个请求队列，并由一个线程按顺序进行处理。针对一个请求，线程需要执行两部分工作，首先是接受请求，然后再对其进行处理，如下图所示。

![Drawing 3.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211214231434.png)

从这个简单的图中，我们可以得出结论，线程效率低下。

相比之下，WebFlux 构建在非阻塞 API 之上，这意味着没有操作需要与 I/O 阻塞线程进行交互。接受和处理请求的效率很高，如下图所示。

![Drawing 4.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211214231507.png)

如果是在多线程的场景下会发生什么呢？

![Drawing 5.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211214231544.png)

当处理用户请求涉及太多的线程实例时，相互之间就需要协调资源，这是由于它们之间的不一致性会导致性能下降。

**处理模型对性能的影响**

在 Biju Kunjummen 的测试用例中，他分别基于 WebMVC 所提供的阻塞式 RestTemplate 以及 WebFlux 所提供的非阻塞式 WebClient 工具类对远程 Web 服务发起请求。对于不同组的并发用户（300、1000、1500、3000、5000），他分别发送了一个 delay 属性设置为 300 ms 的请求，每个用户重复该场景 30 次，请求之间的延迟为 1 到 2 秒。测试用例中使用了 Gatling 这款工具来执行压测。

这里我们截取 300 和 3000 并发用户场景下的结果进行对比，如下面两张图所示。

![Drawing 6.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211214231912.png)

![Drawing 7.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211214231919.png)

可以看到，在 300 并发用户的测试用例下，WebMVC 和 WebFlux 的表现比较接近，意味着在并发量不高的情况下，非阻塞式的请求处理过程并没有太多优势；

而在 3000 并发用户下，情况就完全不一样了。无论是吞吐量还是响应时间，WebFlux 都具有压倒性的性能优势。

> 完整版的测试结果和数据，你可以参考 Biju Kunjummen 的这篇文章进行获取：https://dzone.com/articles/raw-performance-numbers-spring-boot-2-webflux-vs-s

# 10 | WebFlux：如何构建异步非阻塞服务？

**引入 Spring WebFlux**

```xml
<dependencies>      
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-webflux</artifactId>
    </dependency>
</dependencies>
```

**使用注解编程模型创建响应式 RESTful 服务**

```java
@RestController
public class HelloController {
 
    @GetMapping("/")
    public Mono<String> hello() {
        return Mono.just("Hello World!");
    }
}
```

使用 Spring WebFlux 与 Spring MVC 的不同之处在于，前者使用的类型都是 Reactor 中提供的 Flux 和 Mono 对象，而不是普通的 POJO。

**使用函数式编程模型创建响应式 RESTful 服务**

当我发起一个远程调用，传入的 HTTP 请求由 HandlerFunction 处理， HandlerFunction 本质上是一个接收 ServerRequest 并返回 Mono 的函数。ServerRequest 和 ServerResponse 是一对不可变接口，用来提供对底层 HTTP 消息的友好访问。

- ServerRequest

ServerRequest 代表请求对象，可以访问各种 HTTP 请求元素。例如，如果我们希望将请求消息体提取为 Mono 类型的对象，可以使用如下方法。

```java
Mono<String> string = request.bodyToMono(String.class);
```

或者使用 BodyExtractors：

```java
Mono<String> string = 
    request.body(BodyExtractors.toMono(String.class);
```

- ServerResponse

通过 body() 方法来加载响应内容是构建 ServerResponse 最常见的方法。

```java
Mono<Order> order = …;
ServerResponse.ok().contentType(MediaType.APPLICATION_JSON)
    .body(order);
```

或者使用 BodyInserters：

```java
ServerResponse.ok().body(BodyInserters.fromObject("Hello World"));
```

- HandlerFunction

我们可以通过实现 HandlerFunction 接口中的 handle() 方法来创建定制化的请求响应处理机制。

```java
public class HelloWorldHandlerFunction implements HandlerFunction<ServerResponse> {

    @Override
    public Mono<ServerResponse> handle(ServerRequest request) {
        return ServerResponse.ok().body(
	        BodyInserters.fromObject("Hello World"));
    }
};
```

- RouterFunction

RouterFunction 与传统 SpringMVC 中的 @RequestMapping 注解功能类似。

```java
RouterFunction<ServerResponse> helloWorldRoute = RouterFunctions.route(
        RequestPredicates.path("/hello-world"),
        new HelloWorldHandlerFunction());
```

RouterFunctions 的 route 方法如下：

```java
public static <T extends ServerResponse> RouterFunction<T> route(
            RequestPredicate predicate, HandlerFunction<T> handlerFunction) { 
    return new DefaultRouterFunction<>(predicate, handlerFunction);
}
```

RouterFunction 的核心逻辑位于这里的 DefaultRouterFunction 类中，该类的 route() 方法如下所示。

```java
public Mono<HandlerFunction<T>> route(ServerRequest request) {
    if (this.predicate.test(request)) {
        if (logger.isTraceEnabled()) {
            String logPrefix = request.exchange().getLogPrefix();
            logger.trace(logPrefix + String.format("Matched %s", this.predicate));
        }
        return Mono.just(this.handlerFunction);
    } else {
        return Mono.empty();
    }
}
```

路由机制的优势在于它的组合型。两个路由功能可以组合成一个新的路由功能，并通过一定的评估方法路由到其中任何一个处理函数。如果第一个路由的谓词不匹配，则第二个谓词会被评估。

```java
RouterFunction<ServerResponse> personRoute =
        route(GET("/orders/{id}").and(accept(APPLICATION_JSON)), personHandler::getOrderById)
        .andRoute(GET("/orders").and(accept(APPLICATION_JSON)), personHandler::getOrders)
        .andRoute(POST("/orders").and(contentType(APPLICATION_JSON)), personHandler::createOrder);
```







