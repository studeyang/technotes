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

![Drawing 1.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211211223350.png)

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

![Drawing 3.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211211223550.png)

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

![Drawing 5.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211211223958.png)

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

![Drawing 7.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211211224757.png)

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

![Drawing 9.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211211225124.png)

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

![图片9.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211211225842.png)

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

![Drawing 1.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211212222358.png)

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

![Drawing 3.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211212222950.png)

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

![Drawing 5.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211212225103.png)

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

![Drawing 7.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211212230050.png)

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

![Drawing 1.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211213230549.png)

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

