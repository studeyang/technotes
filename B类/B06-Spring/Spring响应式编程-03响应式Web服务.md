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

# 12 | WebClient：如何实现非阻塞式的跨服务远程调用？

**创建并配置 WebClient**

创建 WebClient 有两种方法，一种是通过它所提供的 create() 工厂方法。

```java
WebClient webClient = WebClient.create();
// 或者初始化时指定 baseUrl
WebClient webClient = WebClient.create("https://localhost:8081/accounts");
```

另一种是使用 WebClient Builder 构造器工具类。

```java
WebClient webClient = WebClient.builder().build();
```

创建完 WebClient 实例之后，就可以添加相关的配置项。

```java
WebClient webClient = WebClient.builder()
	.baseUrl("https://localhost:8081/accounts")
    .defaultHeader(HttpHeaders.CONTENT_TYPE, "application/json")
	.defaultHeader(HttpHeaders.USER_AGENT, "Reactive WebClient")
	.build();
```

**使用 WebClient 访问服务**

- 构造 URL

使用 WebClient 时可以在它提供的 uri() 方法中添加路径变量和参数值。

```java
webClient.get().uri("http://localhost:8081/accounts/{id}", 100);
```

我们也可以事先把这些路径变量和参数值拼装成一个 Map 对象。

```java
Map<String, Object> uriVariables = new HashMap<>();
uriVariables.put("param1", "value1");
uriVariables.put("param2", "value2");
webClient.get().uri("http://localhost:8081/accounts/{param1}/{param2}", variables);
```

一旦我们准备好请求信息，就可以使用 WebClient 提供的一系列工具方法完成远程服务的访问，例如 retrieve() 方法。

- retrieve() 方法

retrieve() 方法是获取响应主体并对其进行解码的最简单方法。

```java
WebClient webClient = WebClient.create("http://localhost:8081");
 
Mono<Account> result = webClient.get()
        .uri("/accounts/{id}", id)
	    .accept(MediaType.APPLICATION_JSON)
        .retrieve()
        .bodyToMono(Account.class);
```

- exchange() 方法

如果希望对响应拥有更多的控制权，这时候我们可以使用 exchange() 方法来访问整个响应结果，该响应结果是一个 ClientResponse 对象，包含了响应的状态码、Cookie 等信息，示例代码如下所示。

```java
Mono<Account> result = webClient.get()
    .uri("/accounts/{id}", id)
    .accept(MediaType.APPLICATION_JSON)
    .exchange() 
    .flatMap(response -> response.bodyToMono(Account.class));
```

- 使用 RequestBody

如果你有一个 Mono 或 Flux 类型的请求体，那么可以使用 WebClient 的 body() 方法来进行编码，使用示例如下所示。

```java
Mono<Account> accountMono = ... ;
 
Mono<Void> result = webClient.post()
            .uri("/accounts")
            .contentType(MediaType.APPLICATION_JSON)
            .body(accountMono, Account.class)
            .retrieve()
            .bodyToMono(Void.class);
```

如果请求对象是一个普通的 POJO 而不是 Flux/Mono，则可以使用 syncBody() 方法作为一种快捷方式来传递请求，示例代码如下所示。

```java
Account account = ... ;
 
Mono<Void> result = webClient.post()
            .uri("/accounts")
            .contentType(MediaType.APPLICATION_JSON)
            .syncBody(account)
            .retrieve()
            .bodyToMono(Void.class);
```

- 表单和文件提交

当传递的请求体是一个 MultiValueMap 对象时，WebClient 默认发起的是表单提交。

```java
String baseUrl = "http://localhost:8081";
WebClient webClient = WebClient.create(baseUrl);
 
MultiValueMap<String, String> map = new LinkedMultiValueMap<>();
map.add("username", "jianxiang");
map.add("password", "password");
 
Mono<String> mono = webClient.post()
	.uri("/login")
	.syncBody(map)
	.retrieve()
	.bodyToMono(String.class);
```

如果想提交 Multipart Data，我们可以使用 MultipartBodyBuilder 工具类来简化请求的构建过程，最终得到一个 MultiValueMap 对象。

```java
MultipartBodyBuilder builder = new MultipartBodyBuilder();
builder.part("paramPart", "value");
builder.part("filePart", new FileSystemResource("jianxiang.png"));
builder.part("accountPart", new Account("jianxiang"));
 
MultiValueMap<String, HttpEntity<?>> parts = builder.build();
```

再通过 WebClient 的 syncBody() 方法就可以实现请求提交。

**WebClient 的其他使用技巧**

- 请求拦截

我们编写一个自定义的过滤器函数 logFilter()，代码如下所示。

```java
private ExchangeFilterFunction logFilter() {
    return (clientRequest, next) -> {
        logger.info("Request: {} {}", clientRequest.method(), clientRequest.url());
        clientRequest.headers().forEach(
            (name, values) -> values.forEach(value -> logger.info("{}={}", name, value))
        );
        return next.exchange(clientRequest);
    };
}
```

把该过滤器添加到请求链路中，代码如下所示。

```java
WebClient webClient = WebClient.builder()
    .filter(logFilter())
    .build();
```

- 异常处理

当发起一个请求所得到的响应状态码为 4XX 或 5XX 时，WebClient 就会抛出一个 WebClientResponseException 异常，我们可以使用 onStatus() 方法来自定义对异常的处理方式，示例代码如下所示。

```java
public Flux<Account> listAccounts() {
    return webClient.get()
        .uri("/accounts)
        .retrieve()
        .onStatus(HttpStatus::is4xxClientError, clientResponse ->
             Mono.error(new MyCustomClientException())
         )
        .onStatus(HttpStatus::is5xxServerError, clientResponse ->
             Mono.error(new MyCustomServerException())
         )
        .bodyToFlux(Account.class);
}
```

需要注意的是，这种处理方式只适用于使用 retrieve() 方法进行远程请求的场景，exchange() 方法在获取 4XX 或 5XX 响应的情况下不会引发异常。

因此，当使用 exchange() 方法时，我们需要自行检查状态码并以合适的方式处理它们。

# 13 | RSocket：一种新的高性能网络通信协议

RSocket 是一款全新的协议，它基于响应式数据流，为我们提供了高性能的网络通信机制。

**请求-响应模式的问题**

HTTP 协议本身比较简单，只支持请求-响应模式。而这种模式对于很多应用场景来说是不合适的。典型的例子就是消息推送，以 HTTP 协议为例，如果客户端需要获取最新的推送消息，就必须使用轮询。客户端不停地发送请求到服务器来检查更新，这无疑造成了大量的资源浪费。

请求-响应模式的另外一个问题是，如果某个请求的响应时间过长，会阻塞之后的其他请求的处理。

**RSocket 协议与交互模式**

RSocket 是一个二进制的协议，以异步消息的方式提供 4 种交互模式。

- 请求-响应（request/response）模式：发送方在发送消息给接收方之后，等待与之对应的响应消息。
- 请求-响应流（request/stream）模式：发送方的每个请求消息，都对应于接收方的一个消息流作为响应。
- 即发-即忘（fire-and-forget）模式：发送方的请求消息没有与之对应的响应。
- 通道（channel）模式：在发送方和接收方之间建立一个双向传输的通道。

RSocket 采用的是自定义二进制协议，其本身的定位就是高性能通信协议，性能上比 HTTP 高出一个数量级。

在交互模式上，与 HTTP 的请求-响应这种单向的交互模式不同，RSocket 倡导的是对等通信，不再使用传统的客户端-服务器端单向通信模式，而是在两端之间可以自由地相互发送和处理请求。RSocket 协议在交互方式上可以参考下图。

![图片1.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211221225704.png)

**使用 RSocket 实现远程交互**

首先需要引入如下依赖。

```xml
<dependency>
    <groupId>io.rsocket</groupId>
    <artifactId>rsocket-core</artifactId>
</dependency>
<dependency>
    <groupId>io.rsocket</groupId>
    <artifactId>rsocket-transport-netty</artifactId>
</dependency>
```

RSocket 接口的定义如下所示。

```java
public interface RSocket extends Availability, Closeable {

    //推送元信息，数据可以自定义
    Mono<Void> metadataPush(Payload payload);

    //请求-响应模式，发送一个请求并接收一个响应。该协议也比 HTTP 更具优势，因为它是异步且多路复用的
    Mono<Payload> requestResponse(Payload payload);

    //即发-即忘模式，请求-响应的优化，在不需要响应时非常有用
    Mono<Void> fireAndForget(Payload payload);

    //请求-响应流模式，类似返回集合的请求/响应，集合将以流的方式返回，而不是等到查询完成
    Flux<Payload> requestStream(Payload payload);

    //通道模式，允许任意交互模型的双向消息流
    Flux<Payload> requestChannel(Publisher<Payload> payloads);
}
```

意到这几个方法的输入都是一个 Payload 消息对象，而不是一个响应式流对象。但 requestChannel 方法就不一样了，它的输入同样是一个代表响应式流的 Publisher 对象，这意味着此种模式下的输入输出都是响应式流，也就是说可以进行客户端和服务器端之间的双向交互。

我们先来看如何构建 RSocket 服务器端，示例代码如下所示。

```java
RSocketFactory.receive()
        .acceptor(((setup, sendingSocket) -> Mono.just(
            new AbstractRSocket() {
              @Override
              public Mono<Payload> requestResponse(Payload payload) {
                return Mono.just(DefaultPayload.create("Hello: " + payload.getDataUtf8()));
              }
            }
        )))
        .transport(TcpServerTransport.create("localhost", 7000))
        .start()
        .subscribe();
```

构建完服务器端，我们来构建客户端组件，如下所示。

```java
RSocket socket = RSocketFactory.connect()
        .transport(TcpClientTransport.create("localhost", 7000))
        .start()
        .block();
```

现在，我们就可以使用 RSocket 的 requestResponse() 方法来发送请求并获取响应了，如下所示。

```java
socket.requestResponse(DefaultPayload.create("World"))
        .map(Payload::getDataUtf8)
        .doOnNext(System.out::println)
        .doFinally(signalType -> socket.dispose())
        .then()
        .block();
```

执行这次请求，我们会在控制台上获取“Hello: World”。

**集成 RSocket 与 Spring 框架**

我们需要引入如下依赖。

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-rsocket</artifactId>
</dependency>
```

构建如下所示一个简单 Controller。

```java
@Controller
public class HelloController {

    @MessageMapping("hello")
    public Mono<String> hello(String input) {
        return Mono.just("Hello: " + input);
  }
}
```

@MessageMapping 是 Spring 提供的一个注解，用来指定 WebSocket、RSocket 等协议中消息处理的目的地。

为了访问这个 RSocket 端点，我们需要构建一个 RSocketRequester 对象，构建方式如下所示。

```java
@Autowired
RSocketRequester.Builder builder;

RSocketRequester requester = builder.dataMimeType(MimeTypeUtils.TEXT_PLAIN)
            .connect(TcpClientTransport.create(7000)).block();
```

基于这个 RSocketRequester 对象，我们就可以通过它的 route 方法路由到前面通过 @MessageMapping 注解构建的 "hello" 端点，如下所示。

```java
Mono<String> response = requester.route("hello")
        .data("World")
        .retrieveMono(String.class);
```

