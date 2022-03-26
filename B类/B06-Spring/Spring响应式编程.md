> 来源拉勾教育《Spring响应式编程实战》--鉴湘
>
> 代码：https://github.com/lagoueduCol/ReactiveProgramming-jianxiang.git

# 开篇词 | 响应式编程：紧跟技术趋势，提升系统弹性

课程旨在弥补此前基于 Spring 5 的响应式编程系统化学习的空白。

在响应式编程领域存在一个核心的理念，即全栈式响应式编程，也就是响应式开发方式的有效性取决于在整个请求链路的各个环节是否都采用了响应式编程模型。基于这一理念，我结合常见的分布式服务架构中的完整请求链路来设计了课程体系。

![Drawing 5.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211208223049.png)

- 基本概念篇：介绍响应式编程的核心组件与技术体系。
- 编程框架篇：介绍 Spring 5 中内置的响应式编程框架 Project Reactor。
- 技术组件之响应式 Web 服务篇：介绍基于 Spring 构建响应式 Web 服务的系统方法。
- 技术组件之响应式数据访问篇：针对 MongoDB 和 Redis，讨论实现响应式数据访问的系统方法。
- 技术组件之响应式消息通信篇：介绍消息通信的基本概念，以及基于 Spring Cloud Stream 所提供的响应式编程组件来完成与 RabbitMQ 等主流消息中间件之间的集成。
- 技术组件之响应式测试篇：介绍针对案例系统中各层响应式组件进行有效测试的解决方案。

# 模块一：基础篇

# 01 | 追本溯源：响应式编程究竟是一种什么样的技术体系？

**从传统开发模式到异步执行技术**

现实的开发过程普遍采用的是同步阻塞式的开发模式，以实现业务系统。在这种模式下，开发、调试和维护都很简单。

- Web 请求与 I/O 模型

这是日常开发过程中非常具有代表性的一种场景。

```java
RestTemplate restTemplate = new RestTemplate();
ResponseEntity<User> restExchange = restTemplate.exchange(
        "http://localhost:8080/users/{userName}", HttpMethod.GET, null, User.class, userName);
User result = restExchange.getBody();
process(result);
```

这个实现过程类似于下面的调用。

![Drawing 1.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211208225347.png)

服务 B 的线程 B 在整个过程的 CPU 利用效率是很低的，很多时间线程被浪费在了 I/O 阻塞上，无法执行其他的处理过程。

继续分析服务 A 中的处理过程，可以得到以下的时序图。

![Drawing 3.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211208225611.png)

上面所展示的整个过程中，每一个环节都可能是同步阻塞的。针对同步阻塞问题，在技术上也可以引入一些实现技术来将同步调用转化为异步调用。

- 异步调用的实现技术

在 Java 世界中，为了实现异步非阻塞，一般会采用回调和 Future 这两种机制，但这两种机制都存在一定局限性。

回调的含义如下图所示。

![Drawing 5.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211208225735.png)

回调的最大问题是复杂性，一旦在执行流程中包含了多层的异步执行和回调，那么就会形成一种嵌套结构，给代码的开发和调试带来很大的挑战。所以回调很难大规模地组合起来使用，因为很快就会导致代码难以理解和维护，从而造成所谓的“回调地狱”问题。

Future 模式简单理解为这样一种场景：我们有一个需要处理的任务，然后把这个任务提交到 Future，Future 就会在一定时间内完成这个任务，而在这段时间内我们可以去做其他事情。作为 Future 模式的实现，Java 中的 Future 接口只包含如下 5 个方法。

```java
public interface Future<V> {

    //取消任务的执行
    boolean cancel(boolean mayInterruptIfRunning);

    //判断任务是否已经取消
    boolean isCancelled();

    //判断任务是否已经完成
    boolean isDone();

    //等待任务执行结束并获取结果
    V get() throws InterruptedException, ExecutionException;

    //在一定时间内等待任务执行结束并获取结果
    V get(long timeout, TimeUnit unit)?
            throws InterruptedException,ExecutionException,TimeoutException;
}
```

从本质上讲，Future 以及由 Future 所衍生出来的 CompletableFuture 等各种优化方案就是一种多线程技术。多线程假设一些线程可以共享一个 CPU，而 CPU 时间能在多个线程之间共享，这一点就引入了“上下文切换”的概念。

如果想要恢复线程，就需要涉及加载和保存寄存器等一系列计算密集型的操作。因此，大量线程之间的相互协作同样会导致资源利用效率低下。

**响应式编程实现方法**

- 发布-订阅模式

在这一模式中，发布者和订阅者之间可以没有直接的交互，而是通过发送事件到事件处理平台的方式来完成整合，如下图所示。

![Drawing 9.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211208230127.png)

我们可以基于同一套事件发布机制和事件处理平台来应对多种业务场景，不同的场景只需要发送不同的事件即可。

如果我们聚焦于服务 A 的内部，采用发布-订阅模式进行重构如下。

![Drawing 11.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211208230307.png)

如果我们在这些层上都对某个事件进行了订阅，那么就可以对其分别进行处理，并最终将处理结果从服务 A 传播到服务 B 中。

- 数据流与响应式

想象下系统中可能会存在着很多事件，每一种事件会基于用户的操作或者系统自身的行为而被触发，并形成了一个事件的集合。针对事件的集合，我们可以把它们看成是一串串联起来的数据流。

无论是从底层数据库，向上到达服务层，最后到 Web 服务层，抑或是在这个流程中所包含的任意中间层组件，整个数据传递链路都应该是采用事件驱动的方式来进行运作的。

这样，我们就可以不采用传统的同步调用方式来处理数据，而是由处于数据库上游的各层组件自动来执行事件。**这就是响应式编程的核心特点**。这种工作方式的优势就在于，生成事件和消费事件的过程是异步执行的，所以线程的生命周期都很短，也就意味着资源之间的竞争关系较少，服务器的响应能力也就越高。

- 响应式宣言和响应式系统

关于响应式，业界也存在一个著名的响应式宣言，下图就是响应式宣言的官方网站给出的，对于这一宣言的图形化描述。

![Drawing 13.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211208224400.png)

可以看到，即时响应性（Responsive）、回弹性（Resilient）、弹性（Elastic）以及消息驱动（Message Driven）构成了响应式宣言的主体内容。响应式宣言认为，具备上图中各个特性的系统，就可以称为响应式系统。

而这些特性又可以分为三个层次，其中即时响应性、可维护性（Maintainable）和扩展性（Extensible）体现的是价值，回弹性和弹性是表现形式，而消息驱动则是实现手段。

> 所谓回弹性指的是系统在出现失败时，依然能够保持即时响应性；而弹性则是指的系统在各种请求压力之下，都能保持即时响应性。

# 02 | 背压机制：响应式流为什么能够提高系统的弹性？

我们知道响应式系统都是通过对数据流中每个事件进行处理，来提高系统的即时响应性的。

**流的概念**

简单来讲，所谓的流就是由生产者生产并由一个或多个消费者消费的元素序列。

- 流的处理模型：存在两种基本的实现机制--推和拉。
- 流量控制：使用有界阻塞队列。

![Drawing 9.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211209224847.png)

这种阻塞行为是不可能实现异步操作的，所以结合上一讲中的讨论结果，无论从回弹性、弹性还是即时响应性出发，有界阻塞队列都不是我们想要的解决方案。

讲到这里，我们已经明确，纯“推”模式下的数据流量会有很多不可控制的因素，并不能直接应用，而是需要在“推”模式和“拉”模式之间考虑一定的平衡性，从而优雅地实现流量控制。这就需要引出响应式系统中非常重要的一个概念——背压机制（Backpressure）。

**背压机制**

什么是背压？简单来说就是下游能够向上游反馈流量请求的机制。

如果消费者消费数据的速度赶不上生产者生产数据的速度时，它就会持续消耗系统的资源，直到这些资源被消耗殆尽。

这个时候，就需要采用背压机制，消费者会根据自身的处理能力来请求数据，而生产者也会根据消费者的能力来生产数据，从而在两者之间达成一种动态的平衡，确保系统的即时响应性。

**响应式流的核心接口**

针对流量控制的解决方案以及背压机制都包含在响应式流规范中，其中包含了响应式编程的各个核心组件，让我们一起来看一下。

在 Java 的世界中，响应式流规范只定义了四个核心接口，即 Publisher`<T>`、Subscriber`<T>`、Subscription 和 Processor<T,R>。

- Publisher`<T>`：生产者

Publisher 根据收到的请求向当前订阅者 Subscriber 发送元素。

```java
public interface Publisher<T> {
    public void subscribe(Subscriber<? super T> s);
}
```

- Subscriber `<T>`：订阅者

Subscriber 代表的是一种可以从发布者那里订阅并接收元素的订阅者。

```java
public interface Subscriber<T> {
    public void onSubscribe(Subscription s);
    public void onNext(T t);
    public void onError(Throwable t);
    public void onComplete();
}
```

onSubscribe()：当发布者的 subscribe() 方法被调用时就会触发这个回调。

Subscription：可以把这个 Subscription 看作是一种用于订阅的上下文对象。

onNext()：当订阅关系已经建立，那么发布者就可以调用订阅者的 onNext() 方法向订阅者发送一个数据。

onComplete()：上述这个过程是持续不断的，直到所发送的数据已经达到 Subscription 对象中所请求的数据个数。这时候 onComplete() 方法就会被触发，代表这个数据流已经全部发送结束。

onError()：一旦在这个过程中出现了异常，那么就会触发 onError() 方法，我们可以通过这个方法捕获到具体的异常信息进行处理，而数据流也就自动终止了。

- Subscription

Subscription 代表的就是一种订阅上下文对象。

```java
public interface Subscription {
    public void request(long n);
    public void cancel();
}
```

request()：订阅者用该方法请求 n 个元素，可以通过不断调用该方法来向发布者请求数据。

cancel()：用来取消这次订阅。

请注意，**Subscription 对象是确保生产者和消费者针对数据处理速度达成一种动态平衡的基础，也是流量控制中实现背压机制的关键所在**，我们可以通过下图来进一步理解整个数据请求和处理过程。

![Drawing 11.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211209230532.png)

**响应式流的技术生态圈**

目前，业界主流响应式开发库包括 RxJava、Akka、Vert.x 以及 Project Reactor。在本课程中，我们将重点介绍 Project Reactor，它是 Spring 5 中所默认集成的响应式开发库。

# 03 | 场景应用：响应式编程能够应用于哪些具体场景？

响应式编程能够应用到那些具体的场景呢？目前有哪些框架中使用到了这一新型的技术体系呢？这一讲我将为你解答这些疑问。

**响应式编程的应用场景分析**

- 数据流处理

数据流处理是响应式编程的一大应用场景。流式系统的主要特点是低延迟和高吞吐量，流式系统的表现形式也可以有很多，日常的日志埋点和分析、服务运行时的状态采集等都属于这种类型。

- API 网关

针对高并发流量，通常涉及大量的 I/O 操作。相较于传统的同步阻塞式 I/O 模型，响应式编程所具备的异步非阻塞式 I/O 模型非常适合应对处理高并发流量的业务场景。

**应用一：Netflix Hystrix 中的滑动窗口**

Netflix Hystrix 使用了 HystrixCircuitBreaker 类来实现熔断器。该类通过一个 circuitOpen 状态位控制着整个熔断判断流程，而这个状态位本身的状态值则取决于系统目前的执行数据和健康指标。

那么，HystrixCircuitBreaker 如何动态获取系统运行时的各项数据呢？

这里就使用到了一个 HealthCountsStream 类，这就是一种数据流。HealthCountsStream 在设计上采用了一种特定的机制，即滑动窗口（Rolling Window）机制。

Hystrix 以秒为单位来统计系统中所有请求的处理情况，然后每次取最近 10 秒的数据来进行计算。如果失败率超过一定阈值，就进行熔断。这里的 10 秒就是一个滑动窗口，参考其官网的一幅图，如下所示。

![图片0.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211210220934.png)

上图演示了 Hystrix 滑动窗口策略，把 10 秒时间拆分成了 10 个格子，我们把这种格子称为桶 Bucket。每个桶中的数据就是这一秒中所处理的请求数量，并针对处理结果的状态做了分类。然后每当收集好一个新的桶后，就会丢弃掉最旧的一个桶，所以窗口是滑动的。

那么如何来实现这个滑动窗口呢？我们转换一下思路，可以把系统运行时所产生的所有数据都视为一个个的事件，这样滑动窗口中每个桶的数据都来自源源不断的事件。同时，对于这些生成的事件，我们通常需要对其进行转换以便进行后续的操作。这两点构成了实现滑动窗口的设计目标和方法。

在技术实现的选型上，Hystrix 采用了基于响应式编程思想的 RxJava。使用 RxJava 的一大好处是可以通过 RxJava 的一系列操作符来实现滑动窗口，包括 window、flatMap 和 reduce 等。

**应用二：Spring Cloud Gateway 中的过滤器**

Spring Cloud Gateway 中的核心概念就是过滤器（Filter），围绕过滤器的请求处理流程如下图所示。

![图片1.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211210221331.png)

过滤器用于在响应 HTTP 请求之前或之后修改请求本身及对应的响应结果。Spring Cloud Gateway 中提供了一个全局过滤器（GlobalFilter）的概念，对所有路由都生效。

```java
@Configuration
public class JWTAuthFilter implements GlobalFilter {
 
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest.Builder builder = exchange.getRequest().mutate();
        builder.header("Authorization","Token");
        return chain.filter(exchange.mutate().request(builder.build()).build());
    }
}
```

在上面示例中，我们对所有经过 API 网关的 HTTP 请求添加了一个消息头，用来设置与访问 Token 相关的安全认证信息。

**应用三：Spring WebFlux 中的请求处理流程**

在 WebFlux 中，对 HTTP 请求的处理过程涉及了 HandlerMapping、HandlerAdapter、HandlerResultHandler 类之间的交互，整个流程如下图所示。

![图片3.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211210223401.png)

我们直接来看用于完成上图流程的 Handle 方法定义，该方法实现了流式处理请求机制，如下所示。

```java
public Mono<Void> handle(ServerWebExchange exchange) {
    if (this.handlerMappings == null) {
        return createNotFoundError();
    }

    return Flux.fromIterable(this.handlerMappings)
            //从handlerMapping这个map中获取HandlerMapping
            .concatMap(mapping -> mapping.getHandler(exchange))
            .next()
            //如果没有找到HandlerMapping，则抛出异常
            .switchIfEmpty(createNotFoundError())
            //触发HandlerAdapter的handle方法
            .flatMap(handler -> invokeHandler(exchange, handler))
            //触发HandlerResultHandler 的handleResult方法
            .flatMap(result -> handleResult(exchange, result));
}
```

# 04 | 案例驱动：如何基于 Spring 框架来学习响应式编程？

Spring 5 提供了针对 Web 服务层开发的响应式 Web 框架 WebFlux，以及支持响应式数据访问的 Spring Data Reactive 框架。在今天这一讲中，我将为你梳理 Spring 框架中的响应式编程技术栈，并引出贯穿整个课程的案例系统。

**Spring WebFlux**

WebFlux 功能非常强大，不仅包含了对创建和访问响应式 HTTP 端点的支持，还可以用来实现服务器推送事件以及 WebSocket。

Spring WebFlux 提供了完整的支持响应式开发的服务端技术栈，Spring WebFlux 的整体架构如下图所示。

![Drawing 1.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211210224812.png)

上图针对传统 spring-webmvc 技术栈和新型的 spring-webflux 技术栈做了一个对比。

最上层所提供的实际上是面向开发人员的开发模式，Spring WebFlux 既支持基于 @Controller、@RequestMapping 等注解的传统开发模式，又支持基于 Router Functions 的函数式开发模式。

关于框架背后的实现原理，传统的 Spring MVC 构建在 Java EE 的 Servlet 标准之上，该标准本身就是阻塞和同步的。而 Spring WebFlux 则是构建在响应式流以及它的实现框架 Reactor 的基础之上的一个开发框架，因此可以基于 HTTP 协议用来构建异步非阻塞的 Web 服务。

位于底部的容器。Spring MVC 是运行在传统的 Servlet 容器之上，而 Spring WebFlux 则需要支持异步的运行环境。

> 由于 WebFlux 提供了异步非阻塞的 I/O 特性，因此非常适合用来开发 I/O 密集型服务。而在使用 Spring MVC 就能满足的场景下，就不需要更改为 WebFlux。通常，我也不大建议你将 WebFlux 和 Spring MVC 混合使用，因为这种开发方式显然无法保证全栈式的响应式流。

**Spring Data Reactive**

在 Spring Data 的基础上，Spring 5 也全面提供了一组响应式数据访问模型。

![Drawing 2.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211210230046.png)

可以看到，上图底部明确把 Spring Data 划分为两大类型，一类是支持 JDBC、JPA 和部分 NoSQL 的传统 Spring Data Repository，而另一类则是支持 Mongo、Cassandra、Redis、Couchbase 等的响应式 Spring Data Reactive Repository。

**案例驱动：ReactiveSpringCSS**

这里的 CSS 是对客户服务系统 Customer Service System 的简称。客户服务是电商、健康类业务场景中非常常见的一种业务场景，我们将通过构建一个精简但又完整的系统来展示 Spring 5 中响应式编程相关的设计理念和各项技术组件。ReactiveSpringCSS 整体架构。

![Drawing 3.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211210225139.png)

customer-service 一般会与用户账户服务 account-service 进行交互以获取生成工单所需的用户账户信息。针对 order-service，其定位是订单服务，customer-service 也需要从该服务中查询订单信息。

在 ReactiveSpringCSS 的整体架构图中，引出了构建一个响应式系统所需的多项技术组件。

- Web 层：使用 Spring WebFlux 组件来为三个服务构建响应式 RESTful 端点，并通过支持响应式请求的 WebClient 客户端组件来消费这些端点。
- Service 层：完成事件处理和消息通信相关的业务场景。
- 消息中间件：使用 Spring Cloud Stream 组件。
- Repository 层：将引入 MongoDB 和 Redis 这两款支持响应式流的 NoSQL 数据库。MongoDB 用于存储业务数据，Redis 用于消息数据缓存。

# 模块二：编程框架篇

# 05 | 响应式编程框架 Reactor

在 Java 领域，目前响应式流的开发库包括 RxJava、Akka、Vert.x 和 Project Reactor 等。

**Project Reactor 框架**

Reactor 诞生在响应式流规范制定之后，所以从一开始就是严格按照响应式流规范设计并实现了它的 API，这也是 Spring 选择它作为默认响应式编程框架的核心原因。

Reactor 框架可以单独使用。和集成其他第三方库一样，如果想要在代码中引入 Reactor，要做的事情就是在 Maven 的 pom 文件中添加如下依赖包。

```xml
<dependency>
    <groupId>io.projectreactor</groupId>
    <artifactId>reactor-core</artifactId>
</dependency>
	 
<dependency>
    <groupId>io.projectreactor</groupId>
    <artifactId>reactor-test</artifactId>
    <scope>test</scope>
</dependency>
```

其中 reactor-core 包含了 Reactor 的核心功能，而 reactor-test 则提供了支持测试的相关工具类。

**Reactor 异步数据序列**

响应式流规范的基本组件是一个异步的数据序列，在 Reactor 框架中，我们可以把这个异步数据序列表示成如下形式。

![Drawing 1.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211211223350.png)

上图中的异步序列模型从语义上可以用如下公式表示。

```
onNext x 0..N [onError | onComplete]
```

以上公式中包含了三种消息通知：

- onNext 表示正常的包含元素的消息通知；
- onComplete 表示序列结束的消息通知；
- onError 表示序列出错的消息通知。

> 正常情况下，onNext() 和 onComplete() 方法都应该被调用，用来正常消费数据并结束序列。
>
> 如果没有调用 onComplete() 方法就会生成一个无界数据序列，在业务系统中，这通常是不合理的。
>
> onError() 方法只有序列出现异常时才会被调用。

基于上述异步数据序列，Reactor 框架提供了两个核心组件来发布数据，分别是 Flux 和 Mono 组件。

**Flux 和 Mono 组件**

Flux 代表的是一个包含 0 到 n 个元素的异步序列，Reactor 官网给出了它的示意图，如下所示。

![Drawing 3.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211211223550.png)

> 上图中的“operator”代表的是操作符，红色的叉号代表异常，“|”符号则代表序列正常结束。

序列的三种消息通知都适用于 Flux。我们先通过一段简短的代码来演示使用 Flux 的方法，如下所示。

```java
private Flux<Account> getAccounts() {
    List<Account> accountList = new ArrayList<>();
 
    Account account = new Account();
    account.setId(1L);
    account.setAccountCode("DemoCode");
    account.setAccountName("DemoName");
    accountList.add(account);

    return Flux.fromIterable(accountList);
}
```

 Web 层组件的代码示例，如下所示。

```java
@GetMapping("/accounts")
public Flux<Account> getAccountList() {
    Flux<Account> accounts= accountService.getAccounts();

    return accounts;
}
```

我们再来看 Reactor 所提供的 Mono 组件。Mono 数据序列中只包含 0 个或 1 个元素，如下图所示。

![Drawing 5.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211211223958.png)

我们同样通过一个服务层的方法来演示 Mono 组件的用法，示例代码如下。

```java
private Mono<Account> getAccountById(Long id) { 
    Account account = new Account();
    account.setId(id);
    account.setAccountCode("DemoCode");
    account.setAccountName("DemoName");
    accountList.add(account);

    return Mono.just(account);
}
```

Web 层如下所示。

```java
@GetMapping("/accounts/{id}")
public Mono<Account> getAccountById(@PathVariable Long id) {
    Mono<Account> account = accountService.getAccountById(id);

    return account;
}
```

某种程度上可以把 Mono 看作是 Flux 的一种特例，而两者之间也可以进行相互的转换和融合。Reactor 中提供了一大批非常实用的操作符来简化这些操作的开发过程。

**操作符**

操作符的执行效果如下所示。

![Drawing 7.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211211224757.png)

在 Reactor 中，可以把操作符分成转换、过滤、组合、条件、数学、日志、调试等几大类。

**背压处理**

背压是所有响应式编程框架所必须要考虑的核心机制，Reactor 框架支持所有常见的背压传播模式，包括以下几种。

- 纯推模式：这种模式下，订阅者通过 subscription.request(Long.MAX_VALUE) 请求有效无限数量的元素。
- 纯拉模式：这种模式下，订阅者通过 subscription.request(1) 方法在收到前一个元素后只请求下一个元素。
- 推-拉混合模式：这种模式下，当订阅者有实时控制需求时，发布者可以适应所提出的数据消费速度。

基于这些背压传播模式，在 Reactor 框架中，针对背压有以下四种处理策略。

- BUFFER：代表一种缓存策略，缓存消费者暂时还无法处理的数据并放到队列中，这时候使用的队列相当于是一种无界队列。
- DROP：代表一种丢弃策略，当消费者无法接收新的数据时丢弃这个元素，这时候相当于使用了有界丢弃队列。
- LATEST：类似于 DROP 策略，但让消费者只得到来自上游组件的最新数据。
- ERROR：代表一种错误处理策略，当消费者无法及时处理数据时发出一个错误信号。

Reactor 使用了一个枚举类型 OverflowStrategy 来定义这些背压处理策略，并提供了一组对应的 onBackpressureBuffer、onBackpressureDrop、onBackpressureLatest 和 onBackpressureError 操作符来设置背压，分别对应上述四种处理策略。

Reactor 官网给出的 onBackpressureBuffer 操作符的弹珠图如下所示。

![Drawing 9.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211211225124.png)

onBackpressureBuffer 操作符有很多种可以选择的配置项，我们可以用来灵活控制它的行为。

# 06 | 流式操作：如何使用 Flux 和 Mono 高效构建响应式数据流？

我们知道在响应式流规范中，存在代表发布者的 Publisher 接口，而 Reactor 提供了这一接口的两种实现，即 Flux 和 Mono，它们是我们利用 Reactor 框架进行响应式编程的基础组件。

创建 Flux 的方式非常多，大体可以分成两大类，一类是基于各种工厂模式的静态创建方法，而另一类则采用编程的方式动态创建 Flux。相对而言，静态方法在使用上都比较简单，但不如动态方法来得灵活。我们来一起看一下。

**通过静态方法创建 Flux**

- just() 方法

它可以指定序列中包含的全部元素，创建出来的 Flux 序列在发布这些元素之后会自动结束。使用 just() 方法创建 Flux 对象的示例代码如下所示。

```java
Flux.just("Hello", "World").subscribe(System.out::println);
```

```
Hello
World
```

- fromXXX() 方法组

如果我们已经有了一个数组、一个 Iterable 对象或 Stream 对象，那么就可以通过 Flux 提供的 fromXXX() 方法组来从这些对象中自动创建 Flux，包括 fromArray()、fromIterable() 和 fromStream() 方法。

```java
Flux.fromArray(new Integer[] {1, 2, 3})
	.subscribe(System.out::println);
```

```
1
2
3
```

- range() 方法

如果你快速生成一个整数数据流，那么可以采用 range() 方法，该方法允许我们指定目标整数数据流的起始元素以及所包含的个数。

```java
Flux.range(2020, 5).subscribe(System.out::println);
```

```
2020
2021
2022
2023
2024
```

- interval() 方法

通过 interval() 所具备的一组重载方法，我们可以分别指定这个数据序列中第一个元素发布之前的延迟时间，以及每个元素之间的时间间隔。它的弹珠图，如下所示。

![图片9.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211211225842.png)

可以看到，上图中每个元素发布时相当于添加了一个定时器的效果。使用 interval() 方法的示例代码如下所示。

```java
Flux.interval(Duration.ofSeconds(2), Duration.ofMillis(200)).subscribe(System.out::println);
```

这段代码的执行效果相当于在等待 2 秒钟之后，生成一个从 0 开始逐一递增的无界数据序列，每 200 毫秒推送一次数据。

- empty()、error() 和 never()

> 这几个方法都比较少用，通常只用于调试和测试。
如果你希望创建一个只包含结束消息的空序列，那么可以使用 empty() 方法。

```java
Flux.empty().subscribe(System.out::println);
```

这时候控制台应该没有任何的输出结果。

通过 error() 方法可以创建一个只包含错误消息的序列。如果你不希望所创建的序列不发出任何类似的消息通知，也可以使用 never() 方法实现这一目标。

**通过动态方法创建 Flux**

如果数据序列事先无法确定，或者生成过程中包含复杂的业务逻辑，那么就需要用到动态创建方法。

- generate() 方法

generate() 方法生成 Flux 序列依赖于 Reactor 所提供的 SynchronousSink 组件，定义如下。

```java
public static <T> Flux<T> generate(Consumer<SynchronousSink<T>> generator)
```

SynchronousSink 是一个同步的 Sink 组件，也就是说元素的生成过程是同步执行的。它包括 next()、complete() 和 error() 这三个核心方法。使用 generate() 方法创建 Flux 的示例代码如下。

```java
Flux.generate(sink -> {
    sink.next("Jianxiang");
    sink.complete();
}).subscribe(System.out::println);
```

```
Jianxiang
```

> 这里要注意的是 next() 方法只能最多被调用一次。
>
> 我们在这里调用了一次 next() 方法，并通过 complete() 方法结束了这个数据流。如果不调用 complete() 方法，那么就会生成一个所有元素均为“Jianxiang”的无界数据流。
如果想要在序列生成过程中引入状态，那么可以使用如下所示的 generate() 方法重载。

```java
Flux.generate(() -> 1, (i, sink) -> {
            sink.next(i);
            if (i == 5) {
                sink.complete();
            }
            return ++i;
}).subscribe(System.out::println);
```

```
1
2
3
4
5
```

- create()

create() 方法与 generate() 方法比较类似，但它使用的是一个 FluxSink 组件，定义如下。

```java
public static <T> Flux<T> create(Consumer<? super FluxSink<T>> emitter)
```

FluxSink 除了 next()、complete() 和 error() 这三个核心方法外，还定义了背压策略，并且可以在一次调用中产生多个元素。使用 create() 方法创建 Flux 的示例代码如下。

```java
Flux.create(sink -> {
        for (int i = 0; i < 5; i++) {
            sink.next("jianxiang" + i);
        }
        sink.complete();
}).subscribe(System.out::println);
```

```
jianxiang0
jianxiang1
jianxiang2
jianxiang3
jianxiang4
```

通过 create() 方法创建 Flux 对象的方式非常灵活，在本专栏中会有多种场景用到这个方法。

**通过 Mono 对象创建响应式流**

对于 Mono 而言，可以认为它是 Flux 的一种特例，所以很多创建 Flux 的方法同样适用。

除了 just()、empty()、error() 和 never() 这些方法之外，比较常用的还有 justOrEmpty() 等方法。justOrEmpty() 方法会先判断所传入的对象中是否包含值，只有在传入对象不为空时，Mono 序列才生成对应的元素，该方法示例代码如下。

```java
Mono.justOrEmpty(Optional.of("jianxiang"))
	.subscribe(System.out::println);
```

如果要想动态创建 Mono，我们同样也可以通过 create() 方法并使用 MonoSink 组件，示例代码如下。

```java
Mono.create(sink -> sink.success("jianxiang"))
    .subscribe(System.out::println);
```

**订阅响应式流**

介绍完如何创建响应式流，接下来就需要讨论如何订阅响应式流。Flux 和 Mono 提供了一批非常有用的 subscribe() 方法重载方法。

```java
//订阅流的最简单方法，忽略所有消息通知
subscribe();
//对每个来自 onNext 通知的值调用 dataConsumer，但不处理 onError 和 onComplete 通知
subscribe(Consumer<T> dataConsumer);
//在前一个重载方法的基础上添加对 onError 通知的处理
subscribe(Consumer<T> dataConsumer, Consumer<Throwable> errorConsumer);
//在前一个重载方法的基础上添加对 onComplete 通知的处理
subscribe(Consumer<T> dataConsumer, Consumer<Throwable> errorConsumer,
Runnable completeConsumer);
//这种重载方法允许通过请求足够数量的数据来控制订阅过程
subscribe(Consumer<T> dataConsumer, Consumer<Throwable> errorConsumer,
Runnable completeConsumer, Consumer<Subscription> subscriptionConsumer);
//订阅序列的最通用方式，可以为我们的 Subscriber 实现提供所需的任意行为
subscribe(Subscriber<T> subscriber);
```

通过上述 subscribe() 重载方法，我们可以只处理其中包含的正常消息，也可以同时处理错误消息和完成消息。例如，下面这段代码示例展示了同时处理正常和错误消息的实现方法。

```java
Mono.just(“jianxiang”)
         .concatWith(Mono.error(new IllegalStateException()))
         .subscribe(System.out::println, System.err::println);
```

```
jianxiang 
java.lang.IllegalStateException
```

有时候我们不想直接抛出异常，而是希望采用一种容错策略来返回一个默认值，就可以采用如下方式。

```java
Mono.just(“jianxiang”)
          .concatWith(Mono.error(new IllegalStateException()))
          .onErrorReturn(“default”)
          .subscribe(System.out::println);
```

```
jianxiang 
default
```

另外一种容错策略是通过 switchOnError() 方法使用另外的流来产生元素。

```java
Mono.just(“jianxiang”)
         .concatWith(Mono.error(new IllegalStateException()))
         .switchOnError(Mono.just(“default”))
         .subscribe(System.out::println);
```

```
jianxiang 
default
```

我们可以充分利用 Lambda 表达式来使用 subscribe() 方法，例如下面这段代码。

```java
Flux.just("jianxiang1", "jianxiang2", "jianxiang3")
    .subscribe(
        data -> System.out.println("onNext:" + data), 
        err -> {}, 
        () -> System.out.println("onComplete")
    );
```

```
onNext:jianxiang1
onNext:jianxiang2
onNext:jianxiang3
onComplete
```

# 07 | Reactor 操作符（上）：如何快速转换响应式流？

Reactor 框架为我们提供了大量操作符，用于操作 Flux 和 Mono 对象。

**操作符的分类**

本篇将 Flux 和 Mono 操作符分成如下六大类型：

- 转换（Transforming）操作符，负责将序列中的元素转变成另一种元素；

- 过滤（Filtering）操作符，负责将不需要的数据从序列中剔除出去；

- 组合（Combining）操作符，负责将序列中的元素进行合并、连接和集成；

- 条件（Conditional）操作符，负责根据特定条件对序列中的元素进行处理；

- 裁剪（Reducing）操作符，负责对序列中的元素执行各种自定义的裁剪操作；

- 工具（Utility）操作符，负责一些针对流式处理的辅助性操作。

本篇把前面三种操作符统称为“转换类”操作符，剩余的三大类统称为“裁剪类”操作符。

**转换（Transforming）操作符**

包括 buffer、window、map、flatMap 等。

- buffer

buffer 操作符的作用相当于把当前流中的元素统一收集到一个集合中，并把这个集合对象作为新的数据流。

```java
Flux.range(1, 25)
    .buffer(10)
    .subscribe(System.out::println);
```

```
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
[11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
[21, 22, 23, 24, 25]
```

> buffer 操作符的另一种用法是指定收集的时间间隔，由此演变出了一组 bufferTimeout() 方法，bufferTimeout() 方法可以指定时间间隔为一个 Duration 对象或毫秒数。
- window

window 操作符的作用类似于 buffer，不同的是 window 操作符是把当前流中的元素收集到另外的 Flux 序列中，而不是一个集合，代表的是一种对序列进行开窗的操作。官方给出的弹珠图，如下所示。

![Drawing 1.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211212222358.png)

示例代码如下。

```java
Flux.range(1, 5)
    .window(2)
    .toIterable()
    .forEach(w -> {
        w.subscribe(System.out::println);
        System.out.println("-------");
    });
```

```
1
2
-------
3
4
-------
5
```

- map

map 操作符相当于一种映射操作，它对流中的每个元素应用一个映射函数从而达到转换效果。

```java
Flux.just(1, 2)
    .map(i -> "number-" + i)
    .subscribe(System.out::println);
```

```
number-1
number-2
```

- flatMap 

flatMap 操作符执行的也是一种映射操作，但与 map 不同，该操作符会把流中的每个元素映射成一个流而不是一个元素。弹珠图如下所示。

![Drawing 3.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211212222950.png)

示例代码如下。

```java
Flux.just(1, 5)
     .flatMap(x -> Mono.just(x * x))
     .subscribe(System.out::println);
```

```
1
25
```

**过滤（Filtering）操作符**

包括 filter、first/last、skip/skipLast、take/takeLast 等。

- filter

filter 操作符的含义与普通的过滤器类似，就是对流中包含的元素进行过滤，只留下满足指定过滤条件的元素，而过滤条件的指定一般是通过断言。

示例代码如下：

```java
Flux.range(1, 10)
    .filter(i -> i % 2 == 0)
	.subscribe(System.out::println);
```

这里的“i % 2 == 0”代表的就是一种断言。

- first/last

first 操作符的执行效果为返回流中的第一个元素，而 last 操作符的执行效果即返回流中的最后一个元素。

- skip/skipLast

如果使用 skip 操作符，将会忽略数据流的前 n 个元素。类似的，如果使用 skipLast 操作符，将会忽略流的最后 n 个元素。

- take/takeLast

take 系列操作符用来从当前流中提取元素。我们可以按照指定的数量来提取元素，也可以按照指定的时间间隔来提取元素。

```java
Flux.range(1, 100).take(5).subscribe(System.out::println);
Flux.range(1, 100).takeLast(5).subscribe(System.out::println);
```

```
1
2
3
4
5
```

```
996
997
998
999
1000
```

**组合（Combining）操作符**

包括 then/when、merge、zip 等。

- then/when

then 操作符的含义是等到上一个操作完成再进行下一个。以下代码展示了该操作符的用法。

```java
Flux.just(1, 2, 3)
    .then()
    .subscribe(System.out::println);
```

then 操作符在上游的元素执行完成之后才会触发新的数据流，也就是说会忽略所传入的元素，所以上述代码在控制台上实际并没有任何输出。

和 then 一起的还有一个 thenMany 操作服务，具有同样的含义，但可以初始化一个新的 Flux 流。示例代码如下所示。

```java
Flux.just(1, 2, 3)
    .thenMany(Flux.just(4, 5))
    .subscribe(System.out::println);
```

```
4
5
```

对应的，when 操作符的含义则是等到多个操作一起完成。

```java
public Mono<Void> updateOrders(Flux<Order> orders) {
        return orders
            .flatMap(file -> {
                Mono<Void> saveOrderToDatabase = ...;
                Mono<Void> sendMessage = ...;
                return Mono.when(saveOrderToDatabase, sendMessage);
       });
}
```

在上述代码中，假设我们对订单列表进行批量更新，首先把订单数据持久化到数据库，然后再发送一条通知类的消息。我们需要确保这两个操作都完成之后方法才能返回，所以用到了 when 操作符。

- merge

merge 操作符用来把多个 Flux 流合并成一个 Flux 序列，而合并的规则就是按照流中元素的实际生成的顺序进行，它的弹珠图如下所示。

![Drawing 5.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211212225103.png)

merge 操作符的代码示例如下所示，我们通过 Flux.intervalMillis() 方法分别创建了两个 Flux 序列，然后将它们 merge 之后打印出来。

```java
Flux.merge(Flux.intervalMillis(0, 100).take(2), 
           Flux.intervalMillis(50, 100).take(2))
    .toStream()
    .forEach(System.out::println);
```

```
0
0
1
1
```

第一个 intervalMillis 方法没有延迟，每隔 100 毫秒生成一个元素；第二个 intervalMillis 方法则是延迟 50 毫秒之后才发送第一个元素，时间间隔同样是 100 毫秒。

和 merge 类似的还有一个 mergeSequential 方法。不同于 merge 操作符，mergeSequential 操作符则按照所有流被订阅的顺序，以流为单位进行合并。现在我们来看一下这段代码，这里仅仅将 merge 操作换成了 mergeSequential 操作。

```java
Flux.mergeSequential(Flux.intervalMillis(0, 100).take(2), 
                     Flux.intervalMillis(50, 100).take(2))
    .toStream()
    .forEach(System.out::println);
```

```
0
1
0
1
```

显然从结果来看，mergeSequential 操作是等上一个流结束之后再 merge 新生成的流元素。

- zip

zip 操作符的合并规则比较特别，是将当前流中的元素与另外一个流中的元素按照一对一的方式进行合并，如下所示。

![Drawing 7.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211212230050.png)

使用 zip 操作符在合并时可以不做任何处理，由此得到的是一个元素类型为 Tuple2 的流，示例代码如下所示。

```java
Flux flux1 = Flux.just(1, 2);
Flux flux2 = Flux.just(3, 4);
Flux.zip(flux1, flux2)
    .subscribe(System.out::println);
```

```
[1,3]
[2,4]
```

我们可以使用 zipWith 操作符实现同样的效果，示例代码如下所示。

```java
Flux.just(1, 2)
    .zipWith(Flux.just(3, 4))
	.subscribe(System.out::println);
```

另一方面，我们也可以通过自定义一个 BiFunction 函数来对合并过程做精细化的处理，这时候所得到的流的元素类型即为该函数的返回值类似，示例代码如下所示。

```
Flux.just(1, 2)
    .zipWith(
        Flux.just(3, 4), 
        (s1, s2) -> String.format("%s+%s=%s", s1, s2, s1 + s2)
    )
	.subscribe(System.out::println);
```

```
1+3=4
2+4=6
```

# 08 | Reactor 操作符（下）：如何多样化裁剪响应式流？

本节将继续介绍条件、裁剪、工具类的操作符。

**条件（Conditional）操作符**

所谓条件操作符，本质上就是提供了一个判断的依据来确定是否处理流中的元素。Reactor 中常用的条件操作符有 defaultIfEmpty、takeUntil、takeWhile、skipUntil 和 skipWhile 等。

- defaultIfEmpty

defaultIfEmpty 操作符针对空数据流提供了一个简单而有用的处理方法。

```java
@GetMapping("/orders/{id}")
public Mono<ResponseEntity<Order>> findOrderById(@PathVariable String id) {
     return orderService.findOrderById(id)
        .map(ResponseEntity::ok)
        .defaultIfEmpty(ResponseEntity.status(404).body(null));
}
```

- takeUntil/takeWhile

takeUntil 操作符的基本用法是 takeUntil (Predicate<? super T> predicate)，其中 Predicate 代表一种断言条件，该操作符将从数据流中提取元素直到断言条件返回 true。

```java
Flux.range(1, 100)
    .takeUntil(i -> i == 10)
    .subscribe(System.out::println);
```

输出结果是 1~10 的数字。

```java
Flux.range(1, 100)
    .takeWhile(i -> i <= 10)
    .subscribe(System.out::println);
```

输出结果也是 1~10 的数字。

- skipUntil/skipWhile

与 takeUntil 相对应，skipUntil 操作符的基本用法是 skipUntil (Predicate<? super T> predicate)。skipUntil 将丢弃原始数据流中的元素直到 Predicate 返回 true。

与 takeWhile 相对应，skipWhile 操作符的基本用法是 skipWhile (Predicate<? super T> continuePredicate)，当 continuePredicate 返回 true 时才进行元素的丢弃。

**裁剪（Reducing）操作符**

裁剪操作符通常用于统计流中的元素数量，或者检查元素是否具有一定的属性。在 Reactor 中，常用的裁剪操作符有 any 、concat、count 和 reduce 等。

- any

any 操作符用于检查是否至少有一个元素具有所指定的属性，示例代码如下。

```java
Flux.just(3, 5, 7, 9, 11, 15, 16, 17)
    .any(e -> e % 2 == 0)
    .subscribe(isExisted -> System.out.println(isExisted));
```

```
true
```

all 操作符，用来检查流中元素是否都满足同一属性。

```java
Flux.just("abc", "ela", "ade", "pqa", "kang")
    .all(a -> a.contains("a"))
    .subscribe(isAllContained -> System.out.println(isAllContained));
```

```
true
```

- concat

concat 操作符用来合并来自不同 Flux 的数据。与 merge 操作符不同，这种合并采用的是顺序的方式，所以严格意义上并不是一种合并操作，所以我们把它归到裁剪操作符类别中。

```java
Flux.concat(
        Flux.range(1, 3),
        Flux.range(4, 2),
        Flux.range(6, 5)
    ).subscribe(System.out::println);
```

输出结果是 1~10 的数字。

- reduce

裁剪操作符中最经典的就是这个 reduce 操作符。reduce 操作符对来自 Flux 序列中的所有元素进行累积操作并得到一个 Mono 序列，该 Mono 序列中包含了最终的计算结果。reduce 操作符示意图如下所示。

![Drawing 1.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211213230549.png)

我们也可以通过一个 BiFunction 来实现任何自定义的复杂计算逻辑。

```java
Flux.range(1, 10)
    .reduce((x, y) -> x + y)
    .subscribe(System.out::println);
```

```
55
```

与 reduce 操作符类似的还有一个 reduceWith 操作符，用来在 reduce 操作时指定一个初始值。

```java
Flux.range(1, 10)
    .reduceWith(() -> 5, (x, y) -> x + y)
    .subscribe(System.out::println);
```

```
60
```

**工具（Utility）操作符**

Reactor 中常用的工具操作符有 subscribe、timeout、block、log 和 debug 等。

- subscribe

subscirbe 操作符订阅序列的最通用方式，如下所示。

```java
//订阅序列的最通用方式，可以为我们的Subscriber实现提供所需的任意行为
subscribe(Subscriber<T> subscriber);
```

基于这种方式，如果默认的 subscribe() 方法没有提供所需的功能，我们可以实现自己的 Subscriber。

```java
Subscriber<String> subscriber = new Subscriber<String>() {
    volatile Subscription subscription; 
    public void onSubscribe(Subscription s) {
        subscription = s;
        System.out.println("initialization");
        subscription.request(1);
    }
    public void onNext(String s) {
        System.out.println("onNext:" + s);
        subscription.request(1);
    }
    public void onComplete() { 
        System.out.println("onComplete");
    }
    public void onError(Throwable t) { 
        System.out.println("onError:" + t.getMessage());
    }
};
```

由于订阅和数据处理可能发生在不同的线程中，因此我们使用 volatile 关键字来确保所有线程都具有对 Subscription 实例的正确引用。

当订阅到达时，我们会通过 onSubscribe 回调通知 Subscriber。在 onNext 回调中，我们打印接收到的数据并请求下一个元素。

现在，让我们通过 subscribe() 方法来使用这个 Subscriber，如下所示。

```java
Flux<String> flux = Flux.just("12", "23", "34");
flux.subscribe(subscriber);
```

```
initialization
onNext:12
onNext:23
onNext:34
onComplete
```

前面构建的自定义 Subscriber 虽然能够正常运作，但因为过于偏底层，因此并不推荐你使用。推荐的方法是扩展 Project Reactor 提供的 BaseSubscriber 类。

```java
class MySubscriber<T> extends BaseSubscriber<T> {
    public void hookOnSubscribe(Subscription subscription) {
        System.out.println("initialization");
        request(1);
    }
    public void hookOnNext(T value) {
        System.out.println("onNext:" + value);
        request(1);
    }
}
```

- timeout

timeout 操作符非常简单，保持原始的流发布者，当特定时间段内没有产生任何事件时，将生成一个异常。

- block

block 操作符在接收到下一个元素之前会一直阻塞。block 操作符常用来把响应式数据流转换为传统数据流。

例如，使用如下方法将分别把 Flux 数据流和 Mono 数据流转变成普通的 List\<Order\> 对象和单个的 Order 对象，我们同样可以设置 block 操作的等待时间。

```java
public List<Order> getAllOrders() {
    return orderservice.getAllOrders()
	    .block(Duration.ofSecond(5));
}
 
public Order getOrderById(Long orderId) {
    return orderservice.getOrderById(orderId)
	    .block(Duration.ofSecond(2));
}
```

- log

Reactor 中专门提供了针对日志的工具操作符 log，它会观察所有的数据并使用日志工具进行跟踪。

```java
Flux.just(1, 2)
    .log()
    .subscribe(System.out::println);
```

执行结果如下所示（为了显示简洁，部分内容和格式做了调整）。

```
Info: | onSubscribe([Synchronous Fuseable] FluxArray.ArraySubscription)
Info: | request(unbounded)
Info: | onNext(1)
1
Info: | onNext(2)
2
Info: | onComplete()
```

- debug

debug 的操作符用于启动调试模式，我们需要在程序开始的地方添加如下代码。

```java
Hooks.onOperator(providedHook -> 
    providedHook.operatorStacktrace())
```

现在，所有的操作符在执行时都会保存与执行过程相关的附加信息。而当系统出现异常时，这些附加信息就相当于系统异常堆栈信息的一部分，方便开发人员进行问题的分析和排查。

上述做法是全局性的，如果你只想观察某个特定的流，那么就可以使用检查点（checkpoint）这一调试功能。例如以下代码演示了如何通过检查点来捕获 0 被用作除数的场景，我们在代码中添加了一个名为“debug”的检查点。

```java
Mono.just(0).map(x -> 1 / x)
    .checkpoint("debug")
    .subscribe(System.out::println);
```

```
Exception in thread "main" reactor.core.Exceptions$ErrorCallbackNotImplemented: java.lang.ArithmeticException: / by zero
	Caused by: java.lang.ArithmeticException: / by zero
	…
 
Assembly trace from producer [reactor.core.publisher.MonoMap] :
    reactor.core.publisher.Mono.map(Mono.java:2029)
    com.jianxiang.reactor.demo.Debug.main(Debug.java:10)
Error has been observed by the following operator(s):
    |_  Mono.map(Debug.java:10)
    |_  Mono.checkpoint(Debug.java:10)
 
    Suppressed: reactor.core.publisher.FluxOnAssembly$AssemblySnapshotException: zero
        at reactor.core.publisher.MonoOnAssembly.<init>(MonoOnAssembly.java:55)
        at reactor.core.publisher.Mono.checkpoint(Mono.java:1304)
        ... 1 more
```

可以看到，这个检查点信息会包含在异常堆栈中。根据需要在系统的关键位置上添加自定义的检查点，也是我们日常开发过程中的一种最佳实践。

# 模块三：响应式Web服务

# 09 | 框架升级：WebFlux 比 Web MVC 到底好在哪里？

从本讲开始，我们将围绕一个典型的多层架构，从每一层出发构建响应式应用程序。首先关注的是 Web 服务层。

**Spring WebFlux 的应用场景**

微服务架构的兴起为 WebFlux 的应用提供了一个很好的场景。在一个微服务系统中，数百个独立的微服务相互通信势必会涉及大量的 I/O 操作，尤其是阻塞式 I/O 操作会整体增加系统的延迟并降低吞吐量。如果能够在复杂的流程中集成非阻塞、异步通信机制，我们就可以高效处理跨服务之间的网络请求。针对这种场景，WebFlux 是一种非常有效的解决方案。

**从 WebMVC 到 WebFlux**

让我们先从传统的 Spring WebMVC 技术栈开始说起。

**Spring WebMVC技术栈**

Spring WebMVC 使用了“管道-过滤器（Pipe-Filter）”架构模式，使用了 Servlet 中的过滤器链（FilterChain）来对请求进行拦截，如下图所示。

![Drawing 0.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211214225534.png)

我们知道 WebMVC 运行在 Servlet 容器上，当 HTTP 请求通过 Servlet 容器时就会被转换为一个 ServletRequest 对象，而最终返回一个 ServletResponse 对象，一次请求的详细流程如下图所示。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211214222446.jpg)

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

![Drawing 1.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211214230501.png)

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

![Drawing 2.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211214231324.png)

**对比 WebFlux 和 WebMVC 的处理模型**

WebMVC 建立在阻塞 I/O 之上，我们来分析这种模型下线程处理请求的过程。

假设有一个工作线程会处理来自客户端的请求，所有请求构成一个请求队列，并由一个线程按顺序进行处理。针对一个请求，线程需要执行两部分工作，首先是接受请求，然后再对其进行处理，如下图所示。

![Drawing 3.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211214231434.png)

从这个简单的图中，我们可以得出结论，线程效率低下。

相比之下，WebFlux 构建在非阻塞 API 之上，这意味着没有操作需要与 I/O 阻塞线程进行交互。接受和处理请求的效率很高，如下图所示。

![Drawing 4.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211214231507.png)

如果是在多线程的场景下会发生什么呢？

![Drawing 5.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211214231544.png)

当处理用户请求涉及太多的线程实例时，相互之间就需要协调资源，这是由于它们之间的不一致性会导致性能下降。

**处理模型对性能的影响**

在 Biju Kunjummen 的测试用例中，他分别基于 WebMVC 所提供的阻塞式 RestTemplate 以及 WebFlux 所提供的非阻塞式 WebClient 工具类对远程 Web 服务发起请求。对于不同组的并发用户（300、1000、1500、3000、5000），他分别发送了一个 delay 属性设置为 300 ms 的请求，每个用户重复该场景 30 次，请求之间的延迟为 1 到 2 秒。测试用例中使用了 Gatling 这款工具来执行压测。

这里我们截取 300 和 3000 并发用户场景下的结果进行对比，如下面两张图所示。

![Drawing 6.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211214231912.png)

![Drawing 7.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211214231919.png)

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

![图片1.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211221225704.png)

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
@MessageMapping 是 Spring 提供的一个注解，用来指定 WebSocket、RSocket 等协议中消息处理的目的地。为了访问这个 RSocket 端点，我们需要构建一个 RSocketRequester 对象，构建方式如下所示。
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

# 模块四：响应式数据访问

# 17 | R2DBC：关系型数据库能具备响应式数据访问特性吗？

R2DBC 是 Reactive Relational Database Connectivity 的全称，即响应式关系型数据库连接，该规范允许驱动程序提供与关系型数据库之间的响应式和非阻塞集成。

**Spring Data R2DBC**

R2DBC 是由 Spring Data 团队领导的一项探索响应式数据库访问的尝试。R2DBC 的目标是定义具有背压支持的响应式数据库访问 API，该项目包含了三个核心组件。

- R2DBC SPI：定义了实现驱动程序的简约 API。
- R2DBC 客户端：提供了一个人性化的 API 和帮助类。
- R2DBC 驱动：截至目前，为 PostgreSQL、H2、Microsoft SQL Server、MariaDB 以及 MySQL 提供了 R2DBC 驱动程序。

如何使用？首先需引入依赖。

```xml
<!-- spring data r2dbc -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-r2dbc</artifactId>
</dependency>
 
<!-- r2dbc 连接池 -->
<dependency>
    <groupId>io.r2dbc</groupId>
    <artifactId>r2dbc-pool</artifactId>
</dependency>
 
<!--r2dbc mysql 库 -->
<dependency>
    <groupId>dev.miku</groupId>
    <artifactId>r2dbc-mysql</artifactId>
</dependency>
```

在引入 Spring Data R2DBC 之后，我们来使用该组件完成一个示例应用程序的实现。让我们先使用 MySQL 数据库来定义一张 ACCOUNT 表。

```java
USE `r2dbcs_account`;
 
DROP TABLE IF EXISTS `ACCOUNT`;
CREATE TABLE `ACCOUNT`(
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `ACCOUNT_CODE` varchar(100) NOT NULL,
  `ACCOUNT_NAME` varchar(100) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
 
INSERT INTO `account` VALUES ('1', 'account1', 'name1');
INSERT INTO `account` VALUES ('2', 'account2', 'name2');
```

然后，基于该数据库表定义一个实体对象。

```java
import org.springframework.data.annotation.Id;
import org.springframework.data.relational.core.mapping.Table;
 
@Table("account")
public class Account {
    @Id
    private Long id;
    private String accountCode;
    private String accountName;
    //省略 getter/setter
}
```

基于 Account 对象，我们可以设计如下所示的 Repository。

```java
import org.springframework.data.r2dbc.repository.Query;
import org.springframework.data.r2dbc.repository.R2dbcRepository;
 
public interface ReactiveAccountRepository extends R2dbcRepository<Account, Long> {
 
    @Query("insert into ACCOUNT (ACCOUNT_CODE, ACCOUNT_NAME) values (:accountCode,:accountName)")
    Mono<Boolean> addAccount(String accountCode, String accountName);

    @Query("SELECT * FROM account WHERE id =:id")
    Mono<Account> getAccountById(Long id);
}
```

为了访问数据库，最后要做的一件事情就是指定访问数据库的地址，如下所示。

```yaml
spring:
   r2dbc:
     url: r2dbcs:mysql://127.0.0.1:3306/r2dbcs_account
     username: root
     password: root
```

最后，我们构建一个 AccountController 来对 ReactiveAccountRepository 进行验证。

```java
@RestController
@RequestMapping(value = "accounts")
public class AccountController {
 
    @Autowired
    private ReactiveAccountRepository reactiveAccountRepository;
 
    @GetMapping(value = "/{accountId}")
    public Mono<Account> getAccountById(@PathVariable("accountId") Long accountId) {

        Mono<Account> account = reactiveAccountRepository.getAccountById(accountId);
        return account;
    }
 
    @PostMapping(value = "/")
    public Mono<Boolean> addAccount(@RequestBody Account account) {

        return reactiveAccountRepository.addAccount(account.getAccountCode(), account.getAccountName());
    }
}
```


