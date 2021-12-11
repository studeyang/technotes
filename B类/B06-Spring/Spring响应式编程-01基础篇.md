> 来源拉勾教育《Spring响应式编程实战》--鉴湘
>
> 代码：https://github.com/lagoueduCol/ReactiveProgramming-jianxiang.git

# 开篇词 | 响应式编程：紧跟技术趋势，提升系统弹性

课程旨在弥补此前基于 Spring 5 的响应式编程系统化学习的空白。

在响应式编程领域存在一个核心的理念，即全栈式响应式编程，也就是响应式开发方式的有效性取决于在整个请求链路的各个环节是否都采用了响应式编程模型。基于这一理念，我结合常见的分布式服务架构中的完整请求链路来设计了课程体系。

![Drawing 5.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211208223049.png)

- 基本概念篇：介绍响应式编程的核心组件与技术体系。
- 编程框架篇：介绍 Spring 5 中内置的响应式编程框架 Project Reactor。
- 技术组件之响应式 Web 服务篇：介绍基于 Spring 构建响应式 Web 服务的系统方法。
- 技术组件之响应式数据访问篇：针对 MongoDB 和 Redis，讨论实现响应式数据访问的系统方法。
- 技术组件之响应式消息通信篇：介绍消息通信的基本概念，以及基于 Spring Cloud Stream 所提供的响应式编程组件来完成与 RabbitMQ 等主流消息中间件之间的集成。
- 技术组件之响应式测试篇：介绍针对案例系统中各层响应式组件进行有效测试的解决方案。

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

![Drawing 1.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211208225347.png)

服务 B 的线程 B 在整个过程的 CPU 利用效率是很低的，很多时间线程被浪费在了 I/O 阻塞上，无法执行其他的处理过程。

继续分析服务 A 中的处理过程，可以得到以下的时序图。

![Drawing 3.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211208225611.png)

上面所展示的整个过程中，每一个环节都可能是同步阻塞的。针对同步阻塞问题，在技术上也可以引入一些实现技术来将同步调用转化为异步调用。

- 异步调用的实现技术

在 Java 世界中，为了实现异步非阻塞，一般会采用回调和 Future 这两种机制，但这两种机制都存在一定局限性。

回调的含义如下图所示。

![Drawing 5.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211208225735.png)

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

![Drawing 9.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211208230127.png)

我们可以基于同一套事件发布机制和事件处理平台来应对多种业务场景，不同的场景只需要发送不同的事件即可。

如果我们聚焦于服务 A 的内部，采用发布-订阅模式进行重构如下。

![Drawing 11.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211208230307.png)

如果我们在这些层上都对某个事件进行了订阅，那么就可以对其分别进行处理，并最终将处理结果从服务 A 传播到服务 B 中。

- 数据流与响应式

想象下系统中可能会存在着很多事件，每一种事件会基于用户的操作或者系统自身的行为而被触发，并形成了一个事件的集合。针对事件的集合，我们可以把它们看成是一串串联起来的数据流。

无论是从底层数据库，向上到达服务层，最后到 Web 服务层，抑或是在这个流程中所包含的任意中间层组件，整个数据传递链路都应该是采用事件驱动的方式来进行运作的。

这样，我们就可以不采用传统的同步调用方式来处理数据，而是由处于数据库上游的各层组件自动来执行事件。**这就是响应式编程的核心特点**。这种工作方式的优势就在于，生成事件和消费事件的过程是异步执行的，所以线程的生命周期都很短，也就意味着资源之间的竞争关系较少，服务器的响应能力也就越高。

- 响应式宣言和响应式系统

关于响应式，业界也存在一个著名的响应式宣言，下图就是响应式宣言的官方网站给出的，对于这一宣言的图形化描述。

![Drawing 13.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211208224400.png)

可以看到，即时响应性（Responsive）、回弹性（Resilient）、弹性（Elastic）以及消息驱动（Message Driven）构成了响应式宣言的主体内容。响应式宣言认为，具备上图中各个特性的系统，就可以称为响应式系统。

而这些特性又可以分为三个层次，其中即时响应性、可维护性（Maintainable）和扩展性（Extensible）体现的是价值，回弹性和弹性是表现形式，而消息驱动则是实现手段。

> 所谓回弹性指的是系统在出现失败时，依然能够保持即时响应性；而弹性则是指的系统在各种请求压力之下，都能保持即时响应性。

# 02 | 背压机制：响应式流为什么能够提高系统的弹性？

我们知道响应式系统都是通过对数据流中每个事件进行处理，来提高系统的即时响应性的。

**流的概念**

简单来讲，所谓的流就是由生产者生产并由一个或多个消费者消费的元素序列。

- 流的处理模型：存在两种基本的实现机制--推和拉。
- 流量控制：使用有界阻塞队列。

![Drawing 9.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211209224847.png)

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

![Drawing 11.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211209230532.png)

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

![图片0.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211210220934.png)

上图演示了 Hystrix 滑动窗口策略，把 10 秒时间拆分成了 10 个格子，我们把这种格子称为桶 Bucket。每个桶中的数据就是这一秒中所处理的请求数量，并针对处理结果的状态做了分类。然后每当收集好一个新的桶后，就会丢弃掉最旧的一个桶，所以窗口是滑动的。

那么如何来实现这个滑动窗口呢？我们转换一下思路，可以把系统运行时所产生的所有数据都视为一个个的事件，这样滑动窗口中每个桶的数据都来自源源不断的事件。同时，对于这些生成的事件，我们通常需要对其进行转换以便进行后续的操作。这两点构成了实现滑动窗口的设计目标和方法。

在技术实现的选型上，Hystrix 采用了基于响应式编程思想的 RxJava。使用 RxJava 的一大好处是可以通过 RxJava 的一系列操作符来实现滑动窗口，包括 window、flatMap 和 reduce 等。

**应用二：Spring Cloud Gateway 中的过滤器**

Spring Cloud Gateway 中的核心概念就是过滤器（Filter），围绕过滤器的请求处理流程如下图所示。

![图片1.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211210221331.png)

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

![图片3.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211210223401.png)

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

![Drawing 1.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211210224812.png)

上图针对传统 spring-webmvc 技术栈和新型的 spring-webflux 技术栈做了一个对比。

最上层所提供的实际上是面向开发人员的开发模式，Spring WebFlux 既支持基于 @Controller、@RequestMapping 等注解的传统开发模式，又支持基于 Router Functions 的函数式开发模式。

关于框架背后的实现原理，传统的 Spring MVC 构建在 Java EE 的 Servlet 标准之上，该标准本身就是阻塞和同步的。而 Spring WebFlux 则是构建在响应式流以及它的实现框架 Reactor 的基础之上的一个开发框架，因此可以基于 HTTP 协议用来构建异步非阻塞的 Web 服务。

位于底部的容器。Spring MVC 是运行在传统的 Servlet 容器之上，而 Spring WebFlux 则需要支持异步的运行环境。

> 由于 WebFlux 提供了异步非阻塞的 I/O 特性，因此非常适合用来开发 I/O 密集型服务。而在使用 Spring MVC 就能满足的场景下，就不需要更改为 WebFlux。通常，我也不大建议你将 WebFlux 和 Spring MVC 混合使用，因为这种开发方式显然无法保证全栈式的响应式流。

**Spring Data Reactive**

在 Spring Data 的基础上，Spring 5 也全面提供了一组响应式数据访问模型。

![Drawing 2.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211210230046.png)

可以看到，上图底部明确把 Spring Data 划分为两大类型，一类是支持 JDBC、JPA 和部分 NoSQL 的传统 Spring Data Repository，而另一类则是支持 Mongo、Cassandra、Redis、Couchbase 等的响应式 Spring Data Reactive Repository。

**案例驱动：ReactiveSpringCSS**

这里的 CSS 是对客户服务系统 Customer Service System 的简称。客户服务是电商、健康类业务场景中非常常见的一种业务场景，我们将通过构建一个精简但又完整的系统来展示 Spring 5 中响应式编程相关的设计理念和各项技术组件。ReactiveSpringCSS 整体架构。

![Drawing 3.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211210225139.png)

customer-service 一般会与用户账户服务 account-service 进行交互以获取生成工单所需的用户账户信息。针对 order-service，其定位是订单服务，customer-service 也需要从该服务中查询订单信息。

在 ReactiveSpringCSS 的整体架构图中，引出了构建一个响应式系统所需的多项技术组件。

- Web 层：使用 Spring WebFlux 组件来为三个服务构建响应式 RESTful 端点，并通过支持响应式请求的 WebClient 客户端组件来消费这些端点。
- Service 层：完成事件处理和消息通信相关的业务场景。
- 消息中间件：使用 Spring Cloud Stream 组件。
- Repository 层：将引入 MongoDB 和 Redis 这两款支持响应式流的 NoSQL 数据库。MongoDB 用于存储业务数据，Redis 用于消息数据缓存。







