> 翻译自：https://github.com/Netflix/Hystrix/wiki

## 一、简述

### 1.1 什么是 Hystrix？

在分布式环境中，不可避免地会遇到所依赖的服务挂掉的情况，Hystrix 可以通过增加 **延迟容忍度** 与 **错误容忍度**，来控制这些分布式系统的交互。Hystrix 在服务与服务之间建立了一个中间层，防止服务之间出现故障，并提供了失败时的 **fallback** 策略，来增加你系统的整体可靠性和弹性。

History of Hystrix

Hystrix evolved out of resilience engineering work that the Netflix API team began in 2011. In 2012, Hystrix continued to evolve and mature, and many teams within Netflix adopted it. Today tens of billions of thread-isolated, and hundreds of billions of semaphore-isolated calls are executed via Hystrix every day at Netflix. This has resulted in a dramatic improvement in uptime and resilience.

The following links provide more context around Hystrix and the challenges that it attempts to address:

- [“Making Netflix API More Resilient”](http://techblog.netflix.com/2011/12/making-netflix-api-more-resilient.html)
- [“Fault Tolerance in a High Volume, Distributed System”](http://techblog.netflix.com/2012/02/fault-tolerance-in-high-volume.html)
- [“Performance and Fault Tolerance for the Netflix API”](https://speakerdeck.com/benjchristensen/performance-and-fault-tolerance-for-the-netflix-api-august-2012)
- [“Application Resilience in a Service-oriented Architecture”](http://programming.oreilly.com/2013/06/application-resilience-in-a-service-oriented-architecture.html)
- [“Application Resilience Engineering & Operations at Netflix”](https://speakerdeck.com/benjchristensen/application-resilience-engineering-and-operations-at-netflix)

### 1.2 Hystrix 做了那些事情？

Hystrix 提供了以下服务

- **延迟与失败检测。**引入第三方的 client 类库，通过延迟与失败的检测，来保护服务与服务之间的调用（网络间调用最为典型）
- **阻止级联故障。**阻止复杂的分布式系统中出现级联故障
- **快速失败与快速恢复机制**
- **降级。**提供兜底方案（fallback）并在适当的时机优雅降级
- **监控告警。**提供实时监控、告警与操作控制

### 1.3 Hystrix 解决了什么问题？

在复杂的分布式架构中，服务之间都是相互依赖的，任何一个节点都不可避免会宕机。如果主节点不能从这些宕机节点中独立出来，那主节点将会面临被这些宕机的节点拖垮的风险。

举个例子，如果一个应用依赖了 30 个服务，每个服务保证 99.99% 的时间是正常的，那可以计算出：

> 99.9930 = 99.7% uptime
> 0.3% of 1 billion requests = 3,000,000 failures
> 2+ hours downtime/month even if all dependencies have excellent uptime.

实际情况往往更糟糕。

Even when all dependencies perform well the aggregate impact of even 0.01% downtime on each of dozens of services equates to potentially hours a month of downtime **if you do not engineer the whole system for resilience**.

完好情况下，请求流如下：

![img](https://github.com/Netflix/Hystrix/wiki/images/soa-1-640.png)

　　当一个依赖的节点坏掉时，将阻塞整个的用户请求：

![img](https://github.com/Netflix/Hystrix/wiki/images/soa-2-640.png)

流量高峰时，一个单节点的宕机或延迟，会迅速导致所有服务负载达到饱和。

应用中任何一个可能通过网络访问其他服务的节点，都有可能成为造成潜在故障的来源。更严重的是，还可能导致服务之间的延迟增加，占用队列、线程等系统资源，从而导致多系统之间的级联故障。

![img](https://github.com/Netflix/Hystrix/wiki/images/soa-3-640.png)

更严重的是，当网络请求是通过第三方的一个黑盒客户端来发起时，实现细节都被隐藏起来了，而且还可能频繁变动，这样发生问题时就很难监控和改动。

如果这个第三方还是通过传递依赖的，主应用程序中根本没有显示地写出调用的代码，那就更难了。

网络连接失败或者有延迟，服务将会产生故障或者响应变慢，最终反应成为一个 bug。

所有上述表现出来的故障或延迟，都需要一套管理机制，将节点变得相对独立，这样任何一个单节点故障，都至少不会拖垮整个系统的可用性。

### 1.4 Hystrix 的设计原则是什么？

Hystrix 通过以下设计原则来运作:

- 防止任何一个单节点将容器中的所有线程都占满
- 通过快速失败，取代放在队列中等待
- 提供在故障时的应急方法（fallback）
- 使用隔离技术 (如 bulkhead, swimlane, 和 circuit breaker patterns) 来限制任何一个依赖项的影响面
- 提供实时监控、报警等手段
- 提供低延迟的配置变更
- 防止客户端执行失败，不仅仅是执行网络请求的客户端

### 1.5 Hystrix 如何实现它的目标？

如下：

- 将远程请求或简单的方法调用包装成 `HystrixCommand` 或者 `HystrixObservableCommand` 对象，启动一个单独的线程来运行。(示例：[命令模式](http://en.wikipedia.org/wiki/Command_pattern))
- 你可以为服务调用定义一个超时时间，可以为默认值，或者你自定义设置该属性，使得99.5%的请求时间都在该时间以下。
- 为每一个依赖的服务都分配一个线程池，当该线程池满了之后，直接拒绝，这样就防止某一个依赖的服务出问题阻塞了整个系统的其他服务。
- 记录成功数、失败数、超时数以及拒绝数等指标。
- 设置一个熔断器，将所有请求在一段时间内打到这个熔断器提供的方法上，触发条件可以是手动的，也可以根据失败率自动调整。
- 实时监控配置与属性的变更。

当你启用 Hystrix 封装了原有的远程调用请求后，整个流程图变为下图所示。

![img](https://github.com/Netflix/Hystrix/wiki/images/soa-4-isolation-640.png)

接下来让我们学习如何使用它吧。

## 二、快速入门

### 2.1 获取源码

Maven

```xml
<dependency>
    <groupId>com.netflix.hystrix</groupId>
    <artifactId>hystrix-core</artifactId>
    <version>x.y.z</version>
</dependency>
```

lvy

```
<dependency org="com.netflix.hystrix" name="hystrix-core" rev="x.y.z" />
```

如果你想下载 Jar 包而不是构建在一个工程里，如下：

```xml
<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
	<modelVersion>4.0.0</modelVersion>
	<groupId>com.netflix.hystrix.download</groupId>
	<artifactId>hystrix-download</artifactId>
	<version>1.0-SNAPSHOT</version>
	<name>Simple POM to download hystrix-core and dependencies</name>
	<url>http://github.com/Netflix/Hystrix</url>
	<dependencies>
		<dependency>
			<groupId>com.netflix.hystrix</groupId>
			<artifactId>hystrix-core</artifactId>
			<version>x.y.z</version>
			<scope/>
		</dependency>
	</dependencies>
</project>
```

然后执行

```
mvn -f download-hystrix-pom.xml dependency:copy-dependencies
```

It will download hystrix-core-*.jar and its dependencies into ./target/dependency/.

You need Java 6 or later.

### 2.2 Hello World!

最简单的示例：

```java
public class CommandHelloWorld extends HystrixCommand<String> {

    private final String name;

    public CommandHelloWorld(String name) {
        super(HystrixCommandGroupKey.Factory.asKey("ExampleGroup"));
        this.name = name;
    }

    @Override
    protected String run() {
        // a real example would do work like a network call here
        return "Hello " + name + "!";
    }
}
```

[View Source](https://github.com/Netflix/Hystrix/blob/master/hystrix-examples/src/main/java/com/netflix/hystrix/examples/basic/CommandHelloWorld.java)

该 commond 类可以用以下方法使用：

```java
// 1
String s = new CommandHelloWorld("Bob").execute();
// 2
Future<String> s = new CommandHelloWorld("Bob").queue();
// 3
Observable<String> s = new CommandHelloWorld("Bob").observe();
```

更多具体的用法详见 **如何使用** 模块。

Example source code can be found in the [hystrix-examples](https://github.com/Netflix/Hystrix/tree/master/hystrix-examples/src/main/java/com/netflix/hystrix/examples) module.

### 2.3 构建

下载源码并构建：

```
$ git clone git@github.com:Netflix/Hystrix.git
$ cd Hystrix/
$ ./gradlew build
```

或者像这样构建

```
$ ./gradlew clean build
```

构建的输出大概是这样的

```
$ ./gradlew build
:hystrix-core:compileJava
:hystrix-core:processResources UP-TO-DATE
:hystrix-core:classes
:hystrix-core:jar
:hystrix-core:sourcesJar
:hystrix-core:signArchives SKIPPED
:hystrix-core:assemble
:hystrix-core:licenseMain UP-TO-DATE
:hystrix-core:licenseTest UP-TO-DATE
:hystrix-core:compileTestJava
:hystrix-core:processTestResources UP-TO-DATE
:hystrix-core:testClasses
:hystrix-core:test
:hystrix-core:check
:hystrix-core:build
:hystrix-examples:compileJava
:hystrix-examples:processResources UP-TO-DATE
:hystrix-examples:classes
:hystrix-examples:jar
:hystrix-examples:sourcesJar
:hystrix-examples:signArchives SKIPPED
:hystrix-examples:assemble
:hystrix-examples:licenseMain UP-TO-DATE
:hystrix-examples:licenseTest UP-TO-DATE
:hystrix-examples:compileTestJava
:hystrix-examples:processTestResources UP-TO-DATE
:hystrix-examples:testClasses
:hystrix-examples:test
:hystrix-examples:check
:hystrix-examples:build

BUILD SUCCESSFUL

Total time: 30.758 secs
```

clean build 方式的输出如下

```
> Building > :hystrix-core:test > 147 tests completed
```

## 三、工作原理

### 3.1 流程图

下图展示了当你用使用 Hystrix 封装后的客户端请求一个服务时的流程：

![img](https://github.com/Netflix/Hystrix/wiki/images/hystrix-command-flow-chart.png)

The following sections will explain this flow in greater detail:

1. [Construct a `HystrixCommand` or `HystrixObservableCommand` Object](https://github.com/Netflix/Hystrix/wiki/How-it-Works#flow1)
2. [Execute the Command](https://github.com/Netflix/Hystrix/wiki/How-it-Works#flow2)
3. [Is the Response Cached?](https://github.com/Netflix/Hystrix/wiki/How-it-Works#flow3)
4. [Is the Circuit Open?](https://github.com/Netflix/Hystrix/wiki/How-it-Works#flow4)
5. [Is the Thread Pool/Queue/Semaphore Full?](https://github.com/Netflix/Hystrix/wiki/How-it-Works#flow5)
6. [`HystrixObservableCommand.construct()` or `HystrixCommand.run()`](https://github.com/Netflix/Hystrix/wiki/How-it-Works#flow6)
7. [Calculate Circuit Health](https://github.com/Netflix/Hystrix/wiki/How-it-Works#flow7)
8. [Get the Fallback](https://github.com/Netflix/Hystrix/wiki/How-it-Works#flow8)
9. [Return the Successful Response](https://github.com/Netflix/Hystrix/wiki/How-it-Works#flow9)



1. 创建 HystrixCommand 或 HystrixObservableCommand 对象

通过构建这两个对象来发起请求，构造函数中可以传入你发起请求时需要的参数。

如果你需要的是返回一个单独的响应，那你就用 [`HystrixCommand`](http://netflix.github.com/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixCommand.html) 对象。

```java
HystrixCommand command = new HystrixCommand(arg1, arg2);
```

Construct a [`HystrixObservableCommand`](http://netflix.github.com/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixObservableCommand.html) object if the dependency is expected to return an Observable that emits responses. For example:

```java
HystrixObservableCommand command = new HystrixObservableCommand(arg1, arg2);
```



2. 执行 command

一共有四种方式可以执行 command，其中前两种方式都只适用于简单的 HystrixCommand 对象。

- [`execute()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommand.html#execute()) — 以阻塞方式运行，并返回返回其包装对象的响应值，或者抛出异常
- [`queue()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommand.html#queue()) — 返回一个 Future 对象，你可以选择在适当时机 get
- [`observe()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixObservableCommand.html#observe()) — subscribes to the `Observable` that represents the response(s) from the dependency and returns an `Observable` that replicates that source `Observable`
- [`toObservable()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixObservableCommand.html#toObservable()) — returns an `Observable` that, when you subscribe to it, will execute the Hystrix command and emit its responses

```java
K             value   = command.execute();
Future<K>     fValue  = command.queue();
Observable<K> ohValue = command.observe();         //hot observable
Observable<K> ocValue = command.toObservable();    //cold observable
```

实际上，同步方法 execute() 底层逻辑是调用 queue().get()，然后 queue() 实际上是调用了 toObservable().toBlocking().toFuture()，也就是说所有 HystrixCommand 的逻辑都是走 [`Observable`](http://reactivex.io/documentation/observable.html) 实现。



3. 是否请求缓存?

如果开启了请求缓存，并且该响应可以在缓存中找到，那就立刻返回缓存的响应值，而不会再走远程调用逻辑。(See [“Request Caching”](https://github.com/Netflix/Hystrix/wiki/How-it-Works#RequestCaching) below.)



4. 是否开启熔断?

当执行 command 时，Hystrix 会判断熔断是否开启，如果是开启状态则走 (8) 进行 Fallback 降级策略，如果未开启则走 (5) ，继续下一步判断是否可以执行 command。



5. 线程池\队列\信号量 是否已满?

如果上述三者已达到阈值，Hystrix 就会直接走 (8) 进行 Fallback 降级策略。



6. `HystrixObservableCommand.construct()` or `HystrixCommand.run()`

Here, Hystrix invokes the request to the dependency by means of the method you have written for this purpose, one of the following:

- [`HystrixCommand.run()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommand.html#run()) — 返回单个响应或者引发异常
- [`HystrixObservableCommand.construct()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixObservableCommand.html#construct()) — returns an Observable that emits the response(s) or sends an `onError` notification

If the `run()` or `construct()` method exceeds the command’s timeout value, the thread will throw a `TimeoutException` (or a separate timer thread will, if the command itself is not running in its own thread). In that case Hystrix routes the response through 8. Get the Fallback, and it discards the eventual return value `run()` or `construct()` method if that method does not cancel/interrupt.

Please note that there's no way to force the latent thread to stop work - the best Hystrix can do on the JVM is to throw it an InterruptedException. If the work wrapped by Hystrix does not respect InterruptedExceptions, the thread in the Hystrix thread pool will continue its work, though the client already received a TimeoutException. This behavior can saturate the Hystrix thread pool, though the load is 'correctly shed'. Most Java HTTP client libraries do not interpret InterruptedExceptions. So make sure to correctly configure connection and read/write timeouts on the HTTP clients.

If the command did not throw any exceptions and it returned a response, Hystrix returns this response after it performs some some logging and metrics reporting. In the case of `run()`, Hystrix returns an `Observable` that emits the single response and then makes an `onCompleted` notification; in the case of `construct()` Hystrix returns the same `Observable` returned by `construct()`.



7. Calculate Circuit Health

Hystrix reports successes, failures, rejections, and timeouts to the circuit breaker, which maintains a rolling set of counters that calculate statistics.

It uses these stats to determine when the circuit should “trip,” at which point it short-circuits any subsequent requests until a recovery period elapses, upon which it closes the circuit again after first checking certain health checks.



8. Get the Fallback

Hystrix tried to revert to your fallback whenever a command execution fails: when an exception is thrown by `construct()` or `run()` (6.), when the command is short-circuited because the circuit is open (4.), when the command’s thread pool and queue or semaphore are at capacity (5.), or when the command has exceeded its timeout length.

Write your fallback to provide a generic response, without any network dependency, from an in-memory cache or by means of other static logic. *If you must use a network call in the fallback, you should do so by means of another `HystrixCommand` or `HystrixObservableCommand`.*

In the case of a `HystrixCommand`, to provide fallback logic you implement [`HystrixCommand.getFallback()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommand.html#getFallback()) which returns a single fallback value.

In the case of a `HystrixObservableCommand`, to provide fallback logic you implement [`HystrixObservableCommand.resumeWithFallback()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixObservableCommand.html#resumeWithFallback()) which returns an Observable that may emit a fallback value or values.

If the fallback method returns a response then Hystrix will return this response to the caller. In the case of a `HystrixCommand.getFallback()`, it will return an Observable that emits the value returned from the method. In the case of `HystrixObservableCommand.resumeWithFallback()` it will return the same Observable returned from the method.

If you have not implemented a fallback method for your Hystrix command, or if the fallback itself throws an exception, Hystrix still returns an Observable, but one that emits nothing and immediately terminates with an `onError` notification. It is through this `onError` notification that the exception that caused the command to fail is transmitted back to the caller. (It is a poor practice to implement a fallback implementation that can fail. You should implement your fallback such that it is not performing any logic that could fail.)

The result of a failed or nonexistent fallback will differ depending on how you invoked the Hystrix command:

- `execute()` — throws an exception
- `queue()` — successfully returns a `Future`, but this `Future` will throw an exception if its `get()` method is called
- `observe()` — returns an `Observable` that, when you subscribe to it, will immediately terminate by calling the subscriber’s `onError` method
- `toObservable()` — returns an `Observable` that, when you subscribe to it, will terminate by calling the subscriber’s `onError` method



9. Return the Successful Response

If the Hystrix command succeeds, it will return the response or responses to the caller in the form of an `Observable`. Depending on how you have invoked the command in step 2, above, this `Observable` may be transformed before it is returned to you:

![](https://github.com/Netflix/Hystrix/wiki/images/hystrix-return-flow.png)

- `execute()` — obtains a `Future` in the same manner as does `.queue()` and then calls `get()` on this `Future` to obtain the single value emitted by the `Observable`
- `queue()` — converts the `Observable` into a `BlockingObservable` so that it can be converted into a `Future`, then returns this `Future`
- `observe()` — subscribes to the `Observable` immediately and begins the flow that executes the command; returns an `Observable` that, when you `subscribe` to it, replays the emissions and notifications
- `toObservable()` — returns the `Observable` unchanged; you must `subscribe` to it in order to actually begin the flow that leads to the execution of the command



### 3.2 时序图

@adrianb11 has kindly provided a [sequence diagram](https://design.codelytics.io/hystrix/how-it-works) demonstrating the above flows



### 3.3 熔断器

The following diagram shows how a `HystrixCommand` or `HystrixObservableCommand` interacts with a [`HystrixCircuitBreaker`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixCircuitBreaker.html) and its flow of logic and decision-making, including how the counters behave in the circuit breaker.

![img](https://github.com/Netflix/Hystrix/wiki/images/circuit-breaker-640.png)

[*(Click for larger view)*](https://github.com/Netflix/Hystrix/wiki/images/circuit-breaker-1280.png)

The precise way that the circuit opening and closing occurs is as follows:

1. Assuming the volume across a circuit meets a certain threshold (`HystrixCommandProperties.circuitBreakerRequestVolumeThreshold()`)...
2. And assuming that the error percentage exceeds the threshold error percentage (`HystrixCommandProperties.circuitBreakerErrorThresholdPercentage()`)...
3. Then the circuit-breaker transitions from `CLOSED` to `OPEN`.
4. While it is open, it short-circuits all requests made against that circuit-breaker.
5. After some amount of time (`HystrixCommandProperties.circuitBreakerSleepWindowInMilliseconds()`), the next single request is let through (this is the `HALF-OPEN` state). If the request fails, the circuit-breaker returns to the `OPEN` state for the duration of the sleep window. If the request succeeds, the circuit-breaker transitions to `CLOSED` and the logic in **1.** takes over again.



### 3.4 隔离机制

Hystrix employs the bulkhead pattern to isolate dependencies from each other and to limit concurrent access to any one of them.

![img](https://github.com/Netflix/Hystrix/wiki/images/soa-5-isolation-focused-640.png)



### 3.5 线程与线程池

Clients (libraries, network calls, etc) execute on separate threads. This isolates them from the calling thread (Tomcat thread pool) so that the caller may “walk away” from a dependency call that is taking too long.

Hystrix uses separate, per-dependency thread pools as a way of constraining any given dependency so latency on the underlying executions will saturate the available threads only in that pool.

![img](https://github.com/Netflix/Hystrix/wiki/images/request-example-with-latency-1280.png)

[*(Click for larger view)*](https://github.com/Netflix/Hystrix/wiki/images/request-example-with-latency-1280.png)

It is possible for you to protect against failure without the use of thread pools, but this requires the client being trusted to fail very quickly (network connect/read timeouts and retry configuration) and to always behave well.

Netflix, in its design of Hystrix, chose the use of threads and thread-pools to achieve isolation for many reasons including:

- Many applications execute dozens (and sometimes well over 100) different back-end service calls against dozens of different services developed by as many different teams.
- Each service provides its own client library.
- Client libraries are changing all the time.
- Client library logic can change to add new network calls.
- Client libraries can contain logic such as retries, data parsing, caching (in-memory or across network), and other such behavior.
- Client libraries tend to be “black boxes” — opaque to their users about implementation details, network access patterns, configuration defaults, etc.
- In several real-world production outages the determination was “oh, something changed and properties should be adjusted” or “the client library changed its behavior.”
- Even if a client itself doesn’t change, the service itself can change, which can then impact performance characteristics which can then cause the client configuration to be invalid.
- Transitive dependencies can pull in other client libraries that are not expected and perhaps not correctly configured.
- Most network access is performed synchronously.
- Failure and latency can occur in the client-side code as well, not just in the network call.

![img](https://github.com/Netflix/Hystrix/wiki/images/isolation-options-640.png)

[*(Click for larger view)*](https://github.com/Netflix/Hystrix/wiki/images/isolation-options-1280.png)



**Benefits of Thread Pools**

The benefits of isolation via threads in their own thread pools are:

- The application is fully protected from runaway client libraries. The pool for a given dependency library can fill up without impacting the rest of the application.
- The application can accept new client libraries with far lower risk. If an issue occurs, it is isolated to the library and doesn’t affect everything else.
- When a failed client becomes healthy again, the thread pool will clear up and the application immediately resumes healthy performance, as opposed to a long recovery when the entire Tomcat container is overwhelmed.
- If a client library is misconfigured, the health of a thread pool will quickly demonstrate this (via increased errors, latency, timeouts, rejections, etc.) and you can handle it (typically in real-time via dynamic properties) without affecting application functionality.
- If a client service changes performance characteristics (which happens often enough to be an issue) which in turn cause a need to tune properties (increasing/decreasing timeouts, changing retries, etc.) this again becomes visible through thread pool metrics (errors, latency, timeouts, rejections) and can be handled without impacting other clients, requests, or users.
- Beyond the isolation benefits, having dedicated thread pools provides built-in concurrency which can be leveraged to build asynchronous facades on top of synchronous client libraries (similar to how the Netflix API built a reactive, fully-asynchronous Java API on top of Hystrix commands).

In short, the isolation provided by thread pools allows for the always-changing and dynamic combination of client libraries and subsystem performance characteristics to be handled gracefully without causing outages.

**Note:** Despite the isolation a separate thread provides, your underlying client code should also have timeouts and/or respond to Thread interrupts so it can not block indefinitely and saturate the Hystrix thread pool.



**Drawbacks of Thread Pools**

The primary drawback of thread pools is that they add computational overhead. Each command execution involves the queueing, scheduling, and context switching involved in running a command on a separate thread.

Netflix, in designing this system, decided to accept the cost of this overhead in exchange for the benefits it provides and deemed it minor enough to not have major cost or performance impact.



**Cost of Threads**

Hystrix measures the latency when it executes the `construct()` or `run()` method on the child thread as well as the total end-to-end time on the parent thread. This way you can see the cost of Hystrix overhead (threading, metrics, logging, circuit breaker, etc.).

The Netflix API processes 10+ billion Hystrix Command executions per day using thread isolation. Each API instance has 40+ thread-pools with 5–20 threads in each (most are set to 10).

The following diagram represents one `HystrixCommand` being executed at 60 requests-per-second on a single API instance (of about 350 total threaded executions per second per server):

![img](https://github.com/Netflix/Hystrix/wiki/images/thread-cost-60rps-original.png)

At the median (and lower) there is no cost to having a separate thread.

At the 90th percentile there is a cost of 3ms for having a separate thread.

At the 99th percentile there is a cost of 9ms for having a separate thread. Note however that the increase in cost is far smaller than the increase in execution time of the separate thread (network request) which jumped from 2 to 28 whereas the cost jumped from 0 to 9.

This overhead at the 90th percentile and higher for circuits such as these has been deemed acceptable for most Netflix use cases for the benefits of resilience achieved.

For circuits that wrap very low-latency requests (such as those that primarily hit in-memory caches) the overhead can be too high and in those cases you can use another method such as tryable semaphores which, while they do not allow for timeouts, provide most of the resilience benefits without the overhead. The overhead in general, however, is small enough that Netflix in practice usually prefers the isolation benefits of a separate thread over such techniques.



**Semaphores**

You can use semaphores (or counters) to limit the number of concurrent calls to any given dependency, instead of using thread pool/queue sizes. This allows Hystrix to shed load without using thread pools but it does not allow for timing out and walking away. If you trust the client and you only want load shedding, you could use this approach.

`HystrixCommand` and `HystrixObservableCommand` support semaphores in 2 places:

- **Fallback:** When Hystrix retrieves fallbacks it always does so on the calling Tomcat thread.
- **Execution:** If you set the property `execution.isolation.strategy` to `SEMAPHORE` then Hystrix will use semaphores instead of threads to limit the number of concurrent parent threads that invoke the command.

You can configure both of these uses of semaphores by means of dynamic properties that define how many concurrent threads can execute. You should size them by using similar calculations as you use when sizing a threadpool (an in-memory call that returns in sub-millisecond times can perform well over 5000rps with a semaphore of only 1 or 2 … but the default is 10).

**Note:** if a dependency is isolated with a semaphore and then becomes latent, the parent threads will remain blocked until the underlying network calls timeout.

Semaphore rejection will start once the limit is hit but the threads filling the semaphore can not walk away.



### 3.6 请求合并

You can front a `HystrixCommand` with a request collapser ([`HystrixCollapser`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixCollapser.html) is the abstract parent) with which you can collapse multiple requests into a single back-end dependency call.

The following diagram shows the number of threads and network connections in two scenarios: first without and then with request collapsing (assuming all connections are “concurrent” within a short time window, in this case 10ms).

![img](https://github.com/Netflix/Hystrix/wiki/images/collapser-1280.png)

**Sequence Diagram**

@adrianb11 has kindly provided a [sequence diagram](https://design.codelytics.io/hystrix/request-collapsing) of request-collapsing.

**Why Use Request Collapsing?**

Use request collapsing to reduce the number of threads and network connections needed to perform concurrent `HystrixCommand` executions. Request collapsing does this in an automated manner that does not force all developers of a codebase to coordinate the manual batching of requests.

**Global Context (Across All Tomcat Threads)**

The ideal type of collapsing is done at the global application level, so that requests from *any user* on any Tomcat thread can be collapsed together.

For example, if you configure a `HystrixCommand` to support batching for any user on requests to a dependency that retrieves movie ratings, then when any user thread in the same JVM makes such a request, Hystrix will add its request along with any others into the same collapsed network call.

Note that the collapser will pass a single HystrixRequestContext object to the collapsed network call, so downstream systems must need to handle this case for this to be an effective option.

**User Request Context (Single Tomcat Thread)**

If you configure a `HystrixCommand` to only handle batch requests for *a single user*, then Hystrix can collapse requests from within a single Tomcat thread (request).

For example, if a user wants to load bookmarks for 300 video objects, instead of executing 300 network calls, Hystrix can combine them all into one.

**Object Modeling and Code Complexity**

Sometimes when you create an object model that makes logical sense to the consumers of the object, this does not match up well with efficient resource utilization for the producers of the object.

For example, given a list of 300 video objects, iterating over them and calling `getSomeAttribute()` on each is an obvious object model, but if implemented naively can result in 300 network calls all being made within milliseconds of each other (and very likely saturating resources).

There are manual ways with which you can handle this, such as before allowing the user to call `getSomeAttribute()`, require them to declare what video objects they want to get attributes for so that they can all be pre-fetched.

Or, you could divide the object model so a user has to get a list of videos from one place, then ask for the attributes for that list of videos from somewhere else.

These approaches can lead to awkward APIs and object models that don’t match mental models and usage patterns. They can also lead to simple mistakes and inefficiencies as multiple developers work on a codebase, since an optimization done for one use case can be broken by the implementation of another use case and a new path through the code.

By pushing the collapsing logic down to the Hystrix layer, it doesn’t matter how you create the object model, in what order the calls are made, or whether different developers know about optimizations being done or even needing to be done.

The `getSomeAttribute()` method can be put wherever it fits best and be called in whatever manner suits the usage pattern and the collapser will automatically batch calls into time windows.

**What Is the Cost of Request Collapsing?**

The cost of enabling request collapsing is an increased latency before the actual command is executed. The maximum cost is the size of the batch window.

If you have a command that takes 5ms on median to execute, and a 10ms batch window, the execution time could become 15ms in a worst case. Typically a request will not happen to be submitted to the window just as it opens, and so the median penalty is half the window time, in this case 5ms.

The determination of whether this cost is worth it depends on the command being executed. A high-latency command won’t suffer as much from a small amount of additional average latency. Also, the amount of concurrency on a given command is key: There is no point in paying the penalty if there are rarely more than 1 or 2 requests to be batched together. In fact, in a single-threaded sequential iteration collapsing would be a major performance bottleneck as each iteration will wait the 10ms batch window time.

If, however, a particular command is heavily utilized concurrently and can batch dozens or even hundreds of calls together, then the cost is typically far outweighed by the increased throughput achieved as Hystrix reduces the number of threads it requires and the number of network connections to dependencies.

**Collapser Flow**

![img](https://github.com/Netflix/Hystrix/wiki/images/collapser-flow-1280.png)



### 3.7 请求缓存

`HystrixCommand` and `HystrixObservableCommand` implementations can define a cache key which is then used to de-dupe calls within a request context in a concurrent-aware manner.

Here is an example flow involving an HTTP request lifecycle and two threads doing work within that request:

![img](https://github.com/Netflix/Hystrix/wiki/images/request-cache-1280.png)

The benefits of request caching are:

- Different code paths can execute Hystrix Commands without concern of duplicate work.

This is particularly beneficial in large codebases where many developers are implementing different pieces of functionality.

For example, multiple paths through code that all need to get a user’s `Account` object can each request it like this:

```java
Account account = new UserGetAccount(accountId).execute();

//or

Observable<Account> accountObservable = new UserGetAccount(accountId).observe();
```

The Hystrix `RequestCache` will execute the underlying `run()` method once and only once, and both threads executing the `HystrixCommand` will receive the same data despite having instantiated different instances.

- Data retrieval is consistent throughout a request.

Instead of potentially returning a different value (or fallback) each time the command is executed, the first response is cached and returned for all subsequent calls within the same request.

- Eliminates duplicate thread executions.

Since the request cache sits in front of the `construct()` or `run()` method invocation, Hystrix can de-dupe calls before they result in thread execution.

If Hystrix didn’t implement the request cache functionality then each command would need to implement it themselves inside the `construct` or `run` method, which would put it after a thread is queued and executed.



## 四、如何使用

### 4.1 Hello World!

[`HystrixCommand`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixCommand.html) 实现：

```java
public class CommandHelloWorld extends HystrixCommand<String> {

    private final String name;

    public CommandHelloWorld(String name) {
        super(HystrixCommandGroupKey.Factory.asKey("ExampleGroup"));
        this.name = name;
    }

    @Override
    protected String run() {
        // a real example would do work like a network call here
        return "Hello " + name + "!";
    }
}
```

[View Source](https://github.com/Netflix/Hystrix/blob/master/hystrix-examples/src/main/java/com/netflix/hystrix/examples/basic/CommandHelloWorld.java)

[`HystrixObservableCommand`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixObservableCommand.html) 实现：

```java
public class CommandHelloWorld extends HystrixObservableCommand<String> {

    private final String name;

    public CommandHelloWorld(String name) {
        super(HystrixCommandGroupKey.Factory.asKey("ExampleGroup"));
        this.name = name;
    }

    @Override
    protected Observable<String> construct() {
        return Observable.create(new Observable.OnSubscribe<String>() {
            @Override
            public void call(Subscriber<? super String> observer) {
                try {
                    if (!observer.isUnsubscribed()) {
                        // a real example would do work like a network call here
                        observer.onNext("Hello");
                        observer.onNext(name + "!");
                        observer.onCompleted();
                    }
                } catch (Exception e) {
                    observer.onError(e);
                }
            }
         } ).subscribeOn(Schedulers.io());
    }
}
```



### 4.2 同步执行

调用 [`execute()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommand.html#execute()) 方法即可。

```java
String s = new CommandHelloWorld("World").execute();
```

测试用例如下：

```java
@Test
public void testSynchronous() {
    assertEquals("Hello World!", new CommandHelloWorld("World").execute());
    assertEquals("Hello Bob!", new CommandHelloWorld("Bob").execute());
}
```

对于 HystrixObservableCommand 可以用 `.toBlocking().toFuture().get()`

### 4.3 异步执行

调用 [`queue()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommand.html#queue()) 方法即可。

```java
Future<String> fs = new CommandHelloWorld("World").queue();
```

返回值可以这样拿到：

```java
String s = fs.get();
```

测试用例如下：

```java
@Test
public void testAsynchronous1() throws Exception {
    assertEquals("Hello World!", new CommandHelloWorld("World").queue().get());
    assertEquals("Hello Bob!", new CommandHelloWorld("Bob").queue().get());
}

@Test
public void testAsynchronous2() throws Exception {
    Future<String> fWorld = new CommandHelloWorld("World").queue();
    Future<String> fBob = new CommandHelloWorld("Bob").queue();

    assertEquals("Hello World!", fWorld.get());
    assertEquals("Hello Bob!", fBob.get());
}
```

以下两种写法是等价的：

```java
String s1 = new CommandHelloWorld("World").execute();
String s2 = new CommandHelloWorld("World").queue().get();
```

对于 HystrixObservableCommand 可以用 `.toBlocking().toFuture()`

### 4.4 Reactive Execution

You can also observe the results of a `HystrixCommand` as an `Observable` by using one of the following methods:

- [`observe()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommand.html#observe()) — returns a “hot” Observable that executes the command immediately, though because the Observable is filtered through a `ReplaySubject` you are not in danger of losing any items that it emits before you have a chance to subscribe
- [`toObservable()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommand.html#toObservable()) — returns a “cold” Observable that won’t execute the command and begin emitting its results until you subscribe to the Observable

```java
Observable<String> ho = new CommandHelloWorld("World").observe();
// or Observable<String> co = new CommandHelloWorld("World").toObservable();
```

You then retrieve the value of the command by subscribing to the Observable:

```java
ho.subscribe(new Action1<String>() {

    @Override
    public void call(String s) {
         // value emitted here
    }

});
```

The following unit tests demonstrate the behavior:

```java
@Test
public void testObservable() throws Exception {

    Observable<String> fWorld = new CommandHelloWorld("World").observe();
    Observable<String> fBob = new CommandHelloWorld("Bob").observe();

    // blocking
    assertEquals("Hello World!", fWorld.toBlockingObservable().single());
    assertEquals("Hello Bob!", fBob.toBlockingObservable().single());

    // non-blocking 
    // - this is a verbose anonymous inner-class approach and doesn't do assertions
    fWorld.subscribe(new Observer<String>() {

        @Override
        public void onCompleted() {
            // nothing needed here
        }

        @Override
        public void onError(Throwable e) {
            e.printStackTrace();
        }

        @Override
        public void onNext(String v) {
            System.out.println("onNext: " + v);
        }

    });

    // non-blocking
    // - also verbose anonymous inner-class
    // - ignore errors and onCompleted signal
    fBob.subscribe(new Action1<String>() {

        @Override
        public void call(String v) {
            System.out.println("onNext: " + v);
        }

    });
}
```

Using Java 8 lambdas/closures is more compact; it would look like this:

```java
    fWorld.subscribe((v) -> {
        System.out.println("onNext: " + v);
    })
    
    // - or while also including error handling
    
    fWorld.subscribe((v) -> {
        System.out.println("onNext: " + v);
    }, (exception) -> {
        exception.printStackTrace();
    })
```

More information about Observable can be found at http://reactivex.io/documentation/observable.html



### 4.5 Reactive Commands

Rather than converting a `HystrixCommand` into an `Observable` using the methods described above, you can also create a `HystrixObservableCommand` that is a specialized version of `HystrixCommand` meant to wrap Observables. A `HystrixObservableCommand` is capable of wrapping Observables that emit multiple items, whereas ordinary `HystrixCommands`, even when converted into Observables, will never emit more than one item.

In such a case, instead of overriding the `run` method with your command logic (as you would with an ordinary `HystrixCommand`), you would override the `construct` method so that it returns the Observable you intend to wrap.

To obtain an Observable representation of the `HystrixObservableCommand`, use one of the following two methods:

- [`observe()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixObservableCommand.html#observe()) — returns a “hot” Observable that subscribes to the underlying Observable immediately, though because it is filtered through a `ReplaySubject` you are not in danger of losing any items that it emits before you have a chance to subscribe to the resulting Observable
- [`toObservable()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixObservableCommand.html#toObservable()) — returns a “cold” Observable that won’t subscribe to the underlying Observable until you subscribe to the resulting Observable



### 4.6 Fallback

你可以为 Hystrix 提供一个降级策略并提供相应的降级方法 Fallback，这样当调用出错时，Hystrix 会选择执行你的 Fallback 方法并返回。你可以为大多数的 command 都设置降级策略，但以下几种情况除外：

1. 写操作：如果一个方法只是写操作，而不需要返回一个值，其实就是返回值为 void 的方法。这时候你就不需要再设置 fallback 了。如果写失败了你反而希望错误信息传递过来
2. 离线计算：如果一个方法的使命是写缓存、生成报告、或者大量的离线计算，这时最好不要设置 fallback，让错误信息返回以便重试，而不是毫无察觉地替换为降级方法

启用 fallback 你只需要实现 HystrixCommand 的 [`getFallback()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommand.html#getFallback()) 方法即可，Hystrix 将会在错误发生时执行该方法，所谓的错误包括：抛出异常、超时、线程池或信号量触发拒绝、熔断器打开。

```java
public class CommandHelloFailure extends HystrixCommand<String> {

    private final String name;

    public CommandHelloFailure(String name) {
        super(HystrixCommandGroupKey.Factory.asKey("ExampleGroup"));
        this.name = name;
    }

    @Override
    protected String run() {
        throw new RuntimeException("this command always fails");
    }

    @Override
    protected String getFallback() {
        return "Hello Failure " + name + "!";
    }
}
```

[View Source](https://github.com/Netflix/Hystrix/blob/master/hystrix-examples/src/main/java/com/netflix/hystrix/examples/basic/CommandHelloFailure.java)

该 run 方法每次都必然抛出异常，然后执行降级方法，以下为测试用例：

```java
@Test
public void testSynchronous() {
    assertEquals("Hello Failure World!", new CommandHelloFailure("World").execute());
    assertEquals("Hello Failure Bob!", new CommandHelloFailure("Bob").execute());
}
```

**`HystrixObservableCommand` Equivalent**

For a `HystrixObservableCommand` you instead may override the `resumeWithFallback` method so that it returns a second `Observable` that will take over from the primary `Observable` if it fails. Note that because an `Observable` may fail after having already emitted one or more items, your fallback should not assume that it will be emitting the only values that the observer will see.

Internally, Hystrix uses the RxJava [`onErrorResumeNext`](http://reactivex.io/documentation/operators/catch.html) operator to seamlessly transition between the primary and fallback `Observable` in case of an error.

**Sequence Diagram**

@adrianb11 has kindly provided a [sequence diagram](https://design.codelytics.io/hystrix/fallback) demonstrating how a timeout then fallback works.



### 4.7 Error Propagation

 run() 方法抛出的所有异常，除了 [`HystrixBadRequestException`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/exception/HystrixBadRequestException.html) 以外，都会记为失败数，并触发 fallback 和熔断器的相关逻辑。

**`HystrixObservableCommand` Equivalent**

In the case of a `HystrixObservableCommand`, non-recoverable errors are returned via `onError` notifications from the resulting `Observable`, and fallbacks are accomplished by falling back to a second Observable that Hystrix obtains through the `resumeWithFallback` method that you implement.

**Execution Exception types**

| Failure Type         | Exception class              | Exception.cause                        | subject to fallback |
| -------------------- | ---------------------------- | -------------------------------------- | ------------------- |
| FAILURE              | `HystrixRuntimeException`    | underlying exception (user-controlled) | YES                 |
| TIMEOUT              | `HystrixRuntimeException`    | `j.u.c.TimeoutException`               | YES                 |
| SHORT_CIRCUITED      | `HystrixRuntimeException`    | `j.l.RuntimeException`                 | YES                 |
| THREAD_POOL_REJECTED | `HystrixRuntimeException`    | `j.u.c.RejectedExecutionException`     | YES                 |
| SEMAPHORE_REJECTED   | `HystrixRuntimeException`    | `j.l.RuntimeException`                 | YES                 |
| BAD_REQUEST          | `HystrixBadRequestException` | underlying exception (user-controlled) | NO                  |



### 4.8 Command Name

一个 command 的名字，默认根据类名来定义：

```java
getClass().getSimpleName();
```

明确定义 command 的名称，需要通过构造方法传入：

```java
public CommandHelloWorld(String name) {
    super(Setter.withGroupKey(HystrixCommandGroupKey.Factory.asKey("ExampleGroup"))
          .andCommandKey(HystrixCommandKey.Factory.asKey("HelloWorld")));
    this.name = name;
}
```

你也可以把固定的 Setter 保存起来，以便每次都传入一样的值：

```java
private static final Setter cachedSetter = 
    Setter.withGroupKey(HystrixCommandGroupKey.Factory.asKey("ExampleGroup"))
    .andCommandKey(HystrixCommandKey.Factory.asKey("HelloWorld"));    

public CommandHelloWorld(String name) {
    super(cachedSetter);
    this.name = name;
}
```

[`HystrixCommandKey`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixCommandKey.html) is an interface and can be implemented as an enum or regular class, but it also has the helper [`Factory`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixCommandKey.Factory.html) class to construct and intern instances such as:

```
HystrixCommandKey.Factory.asKey("HelloWorld")
```



### 4.9 Command Group

Hystrix 用这个分组的 key 去做统一的报表、监控、仪表盘等数据统计。上面代码中已经包含。

By default Hystrix uses this to define the command thread-pool unless a separate one is defined.

[`HystrixCommandGroupKey`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixCommandGroupKey.html) is an interface and can be implemented as an enum or regular class, but it also has the helper [`Factory`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixCommandGroupKey.Factory.html) class to construct and intern instances such as:

```
HystrixCommandGroupKey.Factory.asKey("ExampleGroup")
```



### 4.10 Command Thread-Pool

thread-pool key 对应着 [`HystrixThreadPool`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixThreadPool.html)，每一个 command 都属于一个 HystrixTreadPool，也即对应着一个 [`HystrixThreadPoolKey`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixThreadPoolKey.html)。如果不指定，那就默认同 HystrixGroupKey 相同。

To explicitly define the name pass it in via the `HystrixCommand` or `HystrixObservableCommand` constructor:

```java
public CommandHelloWorld(String name) {
    super(Setter.withGroupKey(HystrixCommandGroupKey.Factory.asKey("ExampleGroup"))
          .andCommandKey(HystrixCommandKey.Factory.asKey("HelloWorld"))
          .andThreadPoolKey(HystrixThreadPoolKey.Factory.asKey("HelloWorldPool")));
    this.name = name;
}
```

[`HystrixThreadPoolKey`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixThreadPoolKey.html) is an interface and can be implemented as an enum or regular class, but it also has the helper [`Factory`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixThreadPoolKey.Factory.html) class to construct and intern instances such as:

```
HystrixThreadPoolKey.Factory.asKey("HelloWorldPool")
```

The reason why you might use `HystrixThreadPoolKey` instead of just a different `HystrixCommandGroupKey` is that multiple commands may belong to the same “group” of ownership or logical functionality, but certain commands may need to be isolated from each other.

Here is a simple example:

- two commands used to access Video metadata
- group name is “VideoMetadata”
- command A goes against resource #1
- command B goes against resource #2

If command A becomes latent and saturates its thread-pool it should not prevent command B from executing requests since they each hit different back-end resources.

Thus, we logically want these commands grouped together but want them isolated differently and would use `HystrixThreadPoolKey` to give each of them a different thread-pool.



### 4.11 Request Cache

请求缓存可以通过实现 [`getCacheKey()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommand.html#getCacheKey()) 方法：

```java
public class CommandUsingRequestCache extends HystrixCommand<Boolean> {

    private final int value;

    protected CommandUsingRequestCache(int value) {
        super(HystrixCommandGroupKey.Factory.asKey("ExampleGroup"));
        this.value = value;
    }

    @Override
    protected Boolean run() {
        return value == 0 || value % 2 == 0;
    }

    @Override
    protected String getCacheKey() {
        return String.valueOf(value);
    }
}
```

[View Source](https://github.com/Netflix/Hystrix/blob/master/hystrix-examples/src/main/java/com/netflix/hystrix/examples/basic/CommandUsingRequestCache.java)

由于这个依赖请求的上下文，所以我们必须先初始化 [`HystrixRequestContext`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/strategy/concurrency/HystrixRequestContext.html)，测试代码如下：

```java
@Test
public void testWithoutCacheHits() {
    HystrixRequestContext context = HystrixRequestContext.initializeContext();
    try {
        assertTrue(new CommandUsingRequestCache(2).execute());
        assertFalse(new CommandUsingRequestCache(1).execute());
        assertTrue(new CommandUsingRequestCache(0).execute());
        assertTrue(new CommandUsingRequestCache(58672).execute());
    } finally {
        context.shutdown();
    }
}
```

一般来说这个 context 对象的初始化和销毁应该通过 ServletFilter 来控制。下面的例子展示了 context 对象对缓存的影响（包括获取的值以及是否是从缓存中获取的这个判断）

```java
@Test
public void testWithCacheHits() {
    HystrixRequestContext context = HystrixRequestContext.initializeContext();
    try {
        CommandUsingRequestCache command2a = new CommandUsingRequestCache(2);
        CommandUsingRequestCache command2b = new CommandUsingRequestCache(2);

        assertTrue(command2a.execute());
        // this is the first time we've executed this command with
        // the value of "2" so it should not be from cache
        assertFalse(command2a.isResponseFromCache());

        assertTrue(command2b.execute());
        // this is the second time we've executed this command with
        // the same value so it should return from cache
        assertTrue(command2b.isResponseFromCache());
    } finally {
        context.shutdown();
    }

    // start a new request context
    context = HystrixRequestContext.initializeContext();
    try {
        CommandUsingRequestCache command3b = new CommandUsingRequestCache(2);
        assertTrue(command3b.execute());
        // this is a new request context so this 
        // should not come from cache
        assertFalse(command3b.isResponseFromCache());
    } finally {
        context.shutdown();
    }
}
```



### 4.12 Request Collapsing

这个技术允许多个请求被压缩在一个单独的 `HystrixCommand` 里面发出请求。

A collapser can use the batch size and the elapsed time since the creation of the batch as triggers for executing a batch.

There are 2 styles of request-collapsing supported by Hystrix: request-scoped and globally-scoped. This is configured at collapser construction, and defaulted to request-scoped.

A request-scoped collapser collects a batch per `HystrixRequestContext`, while a globally-scoped collapser collects a batch across multiple `HystrixRequestContext`s. As a result, if your downstream dependencies cannot handle multiple `HystrixRequestContext`s in a single command invocation, request-scoped collapsing is the proper choice.

At Netflix, we exclusively use request-scoped collapsers because all current systems have been built on the assumption that a single `HystrixRequestContext` will be used in each command. Since the batches are per-request only, collapsing is effective when commands occur in parallel with different arguments in the same request.

Following is a simple example of how to implement a request-scoped [`HystrixCollapser`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixCollapser.html):

```java
public class CommandCollapserGetValueForKey extends HystrixCollapser<List<String>, String, Integer> {

    private final Integer key;

    public CommandCollapserGetValueForKey(Integer key) {
        this.key = key;
    }

    @Override
    public Integer getRequestArgument() {
        return key;
    }

    @Override
    protected HystrixCommand<List<String>> createCommand(final Collection<CollapsedRequest<String, Integer>> requests) {
        return new BatchCommand(requests);
    }

    @Override
    protected void mapResponseToRequests(List<String> batchResponse, Collection<CollapsedRequest<String, Integer>> requests) {
        int count = 0;
        for (CollapsedRequest<String, Integer> request : requests) {
            request.setResponse(batchResponse.get(count++));
        }
    }

    private static final class BatchCommand extends HystrixCommand<List<String>> {
        private final Collection<CollapsedRequest<String, Integer>> requests;

        private BatchCommand(Collection<CollapsedRequest<String, Integer>> requests) {
                super(Setter.withGroupKey(HystrixCommandGroupKey.Factory.asKey("ExampleGroup"))
                    .andCommandKey(HystrixCommandKey.Factory.asKey("GetValueForKey")));
            this.requests = requests;
        }

        @Override
        protected List<String> run() {
            ArrayList<String> response = new ArrayList<String>();
            for (CollapsedRequest<String, Integer> request : requests) {
                // artificial response for each argument received in the batch
                response.add("ValueForKey: " + request.getArgument());
            }
            return response;
        }
    }
}
```

[View Source](https://github.com/Netflix/Hystrix/blob/master/hystrix-examples/src/main/java/com/netflix/hystrix/examples/basic/CommandCollapserGetValueForKey.java)

The following unit test shows how to use a collapser to automatically batch four executions of `CommandCollapserGetValueForKey` into a single `HystrixCommand` execution:

```java
@Test
public void testCollapser() throws Exception {
    HystrixRequestContext context = HystrixRequestContext.initializeContext();
    try {
        Future<String> f1 = new CommandCollapserGetValueForKey(1).queue();
        Future<String> f2 = new CommandCollapserGetValueForKey(2).queue();
        Future<String> f3 = new CommandCollapserGetValueForKey(3).queue();
        Future<String> f4 = new CommandCollapserGetValueForKey(4).queue();

        assertEquals("ValueForKey: 1", f1.get());
        assertEquals("ValueForKey: 2", f2.get());
        assertEquals("ValueForKey: 3", f3.get());
        assertEquals("ValueForKey: 4", f4.get());

        // assert that the batch command 'GetValueForKey' was in fact
        // executed and that it executed only once
        assertEquals(1, HystrixRequestLog.getCurrentRequest().getExecutedCommands().size());
        HystrixCommand<?> command = HystrixRequestLog.getCurrentRequest().getExecutedCommands().toArray(new HystrixCommand<?>[1])[0];
        // assert the command is the one we're expecting
        assertEquals("GetValueForKey", command.getCommandKey().name());
        // confirm that it was a COLLAPSED command execution
        assertTrue(command.getExecutionEvents().contains(HystrixEventType.COLLAPSED));
        // and that it was successful
        assertTrue(command.getExecutionEvents().contains(HystrixEventType.SUCCESS));
    } finally {
        context.shutdown();
    }
}
```



### 4.13 Request Context Setup

To use request-scoped features (request caching, request collapsing, request log) you must manage the [`HystrixRequestContext`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/strategy/concurrency/HystrixRequestContext.html) lifecycle (or implement an alternative [`HystrixConcurrencyStrategy`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/strategy/concurrency/HystrixConcurrencyStrategy.html)).

This means that you must execute the following before a request:

```
HystrixRequestContext context = HystrixRequestContext.initializeContext();
```

and then this at the end of the request:

```
context.shutdown();
```

In a standard Java web application, you can use a Servlet Filter to initialize this lifecycle by implementing a filter similar to this:

```java
public class HystrixRequestContextServletFilter implements Filter {

    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) 
     throws IOException, ServletException {
        HystrixRequestContext context = HystrixRequestContext.initializeContext();
        try {
            chain.doFilter(request, response);
        } finally {
            context.shutdown();
        }
    }
}
```

You could enable the filter for all incoming traffic by adding a section to the `web.xml` as follows:

```xml
<filter>
    <display-name>HystrixRequestContextServletFilter</display-name>
    <filter-name>HystrixRequestContextServletFilter</filter-name>
    <filter-class>com.netflix.hystrix.contrib.requestservlet.HystrixRequestContextServletFilter</filter-class>
</filter>
<filter-mapping>
    <filter-name>HystrixRequestContextServletFilter</filter-name>
    <url-pattern>/*</url-pattern>
</filter-mapping>
```



### 4.14 Common Patterns

In the following sections are common uses and patterns of use for `HystrixCommand` and `HystrixObservableCommand`.



### 4.15 Fail Fast

The most basic execution is one that does a single thing and has no fallback behavior. It will throw an exception if any type of failure occurs.

```java
public class CommandThatFailsFast extends HystrixCommand<String> {

    private final boolean throwException;

    public CommandThatFailsFast(boolean throwException) {
        super(HystrixCommandGroupKey.Factory.asKey("ExampleGroup"));
        this.throwException = throwException;
    }

    @Override
    protected String run() {
        if (throwException) {
            throw new RuntimeException("failure from CommandThatFailsFast");
        } else {
            return "success";
        }
}
```

[View Source](https://github.com/Netflix/Hystrix/blob/master/hystrix-examples/src/main/java/com/netflix/hystrix/examples/basic/CommandThatFailsFast.java)

These unit tests show how it behaves:

```java
@Test
public void testSuccess() {
    assertEquals("success", new CommandThatFailsFast(false).execute());
}

@Test
public void testFailure() {
    try {
        new CommandThatFailsFast(true).execute();
        fail("we should have thrown an exception");
    } catch (HystrixRuntimeException e) {
        assertEquals("failure from CommandThatFailsFast", e.getCause().getMessage());
        e.printStackTrace();
    }
}
```

**`HystrixObservableCommand` Equivalent**

The equivalent Fail-Fast solution for a `HystrixObservableCommand` would involve overriding the `resumeWithFallback` method as follows:

```java
@Override
protected Observable<String> resumeWithFallback() {
    if (throwException) {
        return Observable.error(new Throwable("failure from CommandThatFailsFast"));
    } else {
        return Observable.just("success");
    }
}
```



### 4.16 Fail Silent

Failing silently is the equivalent of returning an empty response or removing functionality. It can be done by returning `null`, an empty Map, empty List, or other such responses.

You do this by implementing a [`getFallback()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommand.html#getFallback()) method on the `HystrixCommand` instance:

![img](https://github.com/Netflix/Hystrix/wiki/images/fallback-640.png)

```java
public class CommandThatFailsSilently extends HystrixCommand<String> {

    private final boolean throwException;

    public CommandThatFailsSilently(boolean throwException) {
        super(HystrixCommandGroupKey.Factory.asKey("ExampleGroup"));
        this.throwException = throwException;
    }

    @Override
    protected String run() {
        if (throwException) {
            throw new RuntimeException("failure from CommandThatFailsFast");
        } else {
            return "success";
        }
    }

    @Override
    protected String getFallback() {
        return null;
    }
}
```

[View Source](https://github.com/Netflix/Hystrix/blob/master/hystrix-examples/src/main/java/com/netflix/hystrix/examples/basic/CommandThatFailsSilently.java)

```java
@Test
public void testSuccess() {
    assertEquals("success", new CommandThatFailsSilently(false).execute());
}

@Test
public void testFailure() {
    try {
        assertEquals(null, new CommandThatFailsSilently(true).execute());
    } catch (HystrixRuntimeException e) {
        fail("we should not get an exception as we fail silently with a fallback");
    }
}
```

Another implementation that returns an empty list would look like:

```java
@Override
protected List<String> getFallback() {
    return Collections.emptyList();
}
```

**`HystrixObservableCommand` Equivalent**

The equivalent Fail-Silently solution for a `HystrixObservableCommand` would involve overriding the [`resumeWithFallback()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixObservableCommand.html#resumeWithFallback()) method as follows:

```java
@Override
protected Observable<String> resumeWithFallback() {
    return Observable.empty();
}
```



### 4.17 Fallback: Static

Fallbacks can return default values statically embedded in code. This doesn’t cause the feature or service to be removed in the way that “fail silent” often does, but instead causes default behavior to occur.

For example, if a command returns a true/false based on user credentials but the command execution fails, it can default to true:

```java
@Override
protected Boolean getFallback() {
    return true;
}
```

**`HystrixObservableCommand` Equivalent**

The equivalent Static solution for a `HystrixObservableCommand` would involve overriding the `resumeWithFallback` method as follows:

```java
@Override
protected Observable<Boolean> resumeWithFallback() {
    return Observable.just( true );
}
```



### 4.18 Fallback: Stubbed

You typically use a stubbed fallback when your command returns a compound object containing multiple fields, some of which can be determined from other request state while other fields are set to default values.

Examples of places where you might find state appropriate to use in these stubbed values are:

- cookies
- request arguments and headers
- responses from previous service requests prior to the current one failing

Your fallback can retrieve stubbed values statically from the request scope, but typically it is recommended that they be injected at command instantiation time for use if they are needed such as this following example demonstrates in the way it treats the `countryCodeFromGeoLookup` field:

```java
public class CommandWithStubbedFallback extends HystrixCommand<UserAccount> {

    private final int customerId;
    private final String countryCodeFromGeoLookup;

    /**
     * @param customerId
     *            The customerID to retrieve UserAccount for
     * @param countryCodeFromGeoLookup
     *            The default country code from the HTTP request geo code lookup used for fallback.
     */
    protected CommandWithStubbedFallback(int customerId, String countryCodeFromGeoLookup) {
        super(HystrixCommandGroupKey.Factory.asKey("ExampleGroup"));
        this.customerId = customerId;
        this.countryCodeFromGeoLookup = countryCodeFromGeoLookup;
    }

    @Override
    protected UserAccount run() {
        // fetch UserAccount from remote service
        //        return UserAccountClient.getAccount(customerId);
        throw new RuntimeException("forcing failure for example");
    }

    @Override
    protected UserAccount getFallback() {
        /**
         * Return stubbed fallback with some static defaults, placeholders,
         * and an injected value 'countryCodeFromGeoLookup' that we'll use
         * instead of what we would have retrieved from the remote service.
         */
        return new UserAccount(customerId, "Unknown Name",
                countryCodeFromGeoLookup, true, true, false);
    }

    public static class UserAccount {
        private final int customerId;
        private final String name;
        private final String countryCode;
        private final boolean isFeatureXPermitted;
        private final boolean isFeatureYPermitted;
        private final boolean isFeatureZPermitted;

        UserAccount(int customerId, String name, String countryCode,
                boolean isFeatureXPermitted,
                boolean isFeatureYPermitted,
                boolean isFeatureZPermitted) {
            this.customerId = customerId;
            this.name = name;
            this.countryCode = countryCode;
            this.isFeatureXPermitted = isFeatureXPermitted;
            this.isFeatureYPermitted = isFeatureYPermitted;
            this.isFeatureZPermitted = isFeatureZPermitted;
        }
    }
}
```

[View Source](https://github.com/Netflix/Hystrix/blob/master/hystrix-examples/src/main/java/com/netflix/hystrix/examples/basic/CommandWithStubbedFallback.java)

The following unit test demonstrates its behavior:

```java
@Test
public void test() {
    CommandWithStubbedFallback command = new CommandWithStubbedFallback(1234, "ca");
    UserAccount account = command.execute();
    assertTrue(command.isFailedExecution());
    assertTrue(command.isResponseFromFallback());
    assertEquals(1234, account.customerId);
    assertEquals("ca", account.countryCode);
    assertEquals(true, account.isFeatureXPermitted);
    assertEquals(true, account.isFeatureYPermitted);
    assertEquals(false, account.isFeatureZPermitted);
}
```

**`HystrixObservableCommand` Equivalent**

The equivalent Stubbed solution for a `HystrixObservableCommand` would involve overriding the `resumeWithFallback` method to return an `Observable` that emits the stub responses. A version equivalent to the previous example would look like this:

```java
@Override
protected Observable<Boolean> resumeWithFallback() {
    return Observable.just( new UserAccount(customerId, "Unknown Name",
                                            countryCodeFromGeoLookup, true, true, false) );
}
```

But if you are expecting to emit multiple items from your `Observable`, you may be more interested in generating stubs for only those items that the original `Observable` had not yet emitted before it failed. Here is a simple example to show how you might accomplish this — it keeps track of the last item emitted from the main `Observable` so that the fallback knows where to pick up to continue the sequence:

```java
@Override
protected Observable<Integer> construct() {
    return Observable.just(1, 2, 3)
            .concatWith(Observable.<Integer> error(new RuntimeException("forced error")))
            .doOnNext(new Action1<Integer>() {
                @Override
                public void call(Integer t1) {
                    lastSeen = t1;
                }
                
            })
            .subscribeOn(Schedulers.computation());
}

@Override
protected Observable<Integer> resumeWithFallback() {
    if (lastSeen < 4) {
        return Observable.range(lastSeen + 1, 4 - lastSeen);
    } else {
        return Observable.empty();
    }
}
```



### 4.19 Fallback: Cache via Network

Sometimes if a back-end service fails, a stale version of data can be retrieved from a cache service such as memcached.

Since the fallback will go over the network it is another possible point of failure and so it also needs to be wrapped by a `HystrixCommand` or `HystrixObservableCommand`.

![img](https://github.com/Netflix/Hystrix/wiki/images/fallback-via-command-640.png)

It is important to execute the fallback command on a separate thread-pool, otherwise if the main command were to become latent and fill the thread-pool, this would prevent the fallback from running if the two commands share the same pool.

The following code shows how `CommandWithFallbackViaNetwork` executes `FallbackViaNetwork` in its `getFallback()` method.

Note how if the fallback fails, it *also* has a fallback which does the “fail silent” approach of returning `null`.

To configure the `FallbackViaNetwork` command to run on a different threadpool than the default `RemoteServiceX` derived from the [`HystrixCommandGroupKey`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixCommandGroupKey.html), it injects `HystrixThreadPoolKey.Factory.asKey("RemoteServiceXFallback")` into the constructor.

This means `CommandWithFallbackViaNetwork` will run on a thread-pool named `RemoteServiceX` and `FallbackViaNetwork` will run on a thread-pool named `RemoteServiceXFallback`.

```java
public class CommandWithFallbackViaNetwork extends HystrixCommand<String> {
    private final int id;

    protected CommandWithFallbackViaNetwork(int id) {
        super(Setter.withGroupKey(HystrixCommandGroupKey.Factory.asKey("RemoteServiceX"))
                .andCommandKey(HystrixCommandKey.Factory.asKey("GetValueCommand")));
        this.id = id;
    }

    @Override
    protected String run() {
        //        RemoteServiceXClient.getValue(id);
        throw new RuntimeException("force failure for example");
    }

    @Override
    protected String getFallback() {
        return new FallbackViaNetwork(id).execute();
    }

    private static class FallbackViaNetwork extends HystrixCommand<String> {
        private final int id;

        public FallbackViaNetwork(int id) {
            super(Setter.withGroupKey(HystrixCommandGroupKey.Factory.asKey("RemoteServiceX"))
                    .andCommandKey(HystrixCommandKey.Factory.asKey("GetValueFallbackCommand"))
                    // use a different threadpool for the fallback command
                    // so saturating the RemoteServiceX pool won't prevent
                    // fallbacks from executing
                    .andThreadPoolKey(HystrixThreadPoolKey.Factory.asKey("RemoteServiceXFallback")));
            this.id = id;
        }

        @Override
        protected String run() {
            MemCacheClient.getValue(id);
        }

        @Override
        protected String getFallback() {
            // the fallback also failed
            // so this fallback-of-a-fallback will 
            // fail silently and return null
            return null;
        }
    }
}
```

[View Source](https://github.com/Netflix/Hystrix/blob/master/hystrix-examples/src/main/java/com/netflix/hystrix/examples/basic/CommandWithFallbackViaNetwork.java)



### 4.20 Primary + Secondary with Fallback

Some systems have dual-mode behavior — primary and secondary, or primary and failover.

Sometimes the secondary or failover is considered a failure state and it is intended only for fallback; in those scenarios it would fit in the same pattern as “Cache via Network” described above.

However, if flipping to the secondary system is common, such as a normal part of rolling out new code (sometimes this is part of how stateful systems handle code pushes) then every time the secondary system is used the primary will be in a failure state, tripping circuit breakers and firing alerts.

This is not the desired behavior, if for no other reason than to avoid the “cry wolf” fatigue that will cause alerts to be ignored when a real issue is occurring.

So in such a case the strategy is instead to treat the switching between primary and secondary as normal, healthy patterns and put a façade in front of them.

![img](https://github.com/Netflix/Hystrix/wiki/images/primary-secondary-example-640.png)

The primary and secondary `HystrixCommand` implementations are thread-isolated since they are doing network traffic and business logic. They may each have very different performance characteristics (often the secondary system is a static cache) so another benefit of separate commands for each is that they can be individually tuned.

You do not expose these two commands publicly but you instead hide them behind another `HystrixCommand` that is semaphore-isolated and that implements the conditional logic as to whether to invoke the primary or secondary command. If both primary and secondary fail then control switches to the fallback of the façade command itself.

The façade `HystrixCommand` can use semaphore-isolation since all of the work it is doing is going through two other `HystrixCommand`s that are already thread-isolated. It is unnecessary to have yet another layer of threading as long as the [`run()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommand.html#run()) method of the façade is not doing any other network calls, retry logic, or other “error prone” things.

```java
public class CommandFacadeWithPrimarySecondary extends HystrixCommand<String> {

    private final static DynamicBooleanProperty usePrimary = DynamicPropertyFactory.getInstance().getBooleanProperty("primarySecondary.usePrimary", true);

    private final int id;

    public CommandFacadeWithPrimarySecondary(int id) {
        super(Setter
                .withGroupKey(HystrixCommandGroupKey.Factory.asKey("SystemX"))
                .andCommandKey(HystrixCommandKey.Factory.asKey("PrimarySecondaryCommand"))
                .andCommandPropertiesDefaults(
                        // we want to default to semaphore-isolation since this wraps
                        // 2 others commands that are already thread isolated
                        HystrixCommandProperties.Setter()
                                .withExecutionIsolationStrategy(ExecutionIsolationStrategy.SEMAPHORE)));
        this.id = id;
    }

    @Override
    protected String run() {
        if (usePrimary.get()) {
            return new PrimaryCommand(id).execute();
        } else {
            return new SecondaryCommand(id).execute();
        }
    }

    @Override
    protected String getFallback() {
        return "static-fallback-" + id;
    }

    @Override
    protected String getCacheKey() {
        return String.valueOf(id);
    }

    private static class PrimaryCommand extends HystrixCommand<String> {

        private final int id;

        private PrimaryCommand(int id) {
            super(Setter
                    .withGroupKey(HystrixCommandGroupKey.Factory.asKey("SystemX"))
                    .andCommandKey(HystrixCommandKey.Factory.asKey("PrimaryCommand"))
                    .andThreadPoolKey(HystrixThreadPoolKey.Factory.asKey("PrimaryCommand"))
                    .andCommandPropertiesDefaults(
                            // we default to a 600ms timeout for primary
                            HystrixCommandProperties.Setter().withExecutionTimeoutInMilliseconds(600)));
            this.id = id;
        }

        @Override
        protected String run() {
            // perform expensive 'primary' service call
            return "responseFromPrimary-" + id;
        }

    }

    private static class SecondaryCommand extends HystrixCommand<String> {

        private final int id;

        private SecondaryCommand(int id) {
            super(Setter
                    .withGroupKey(HystrixCommandGroupKey.Factory.asKey("SystemX"))
                    .andCommandKey(HystrixCommandKey.Factory.asKey("SecondaryCommand"))
                    .andThreadPoolKey(HystrixThreadPoolKey.Factory.asKey("SecondaryCommand"))
                    .andCommandPropertiesDefaults(
                            // we default to a 100ms timeout for secondary
                            HystrixCommandProperties.Setter().withExecutionTimeoutInMilliseconds(100)));
            this.id = id;
        }

        @Override
        protected String run() {
            // perform fast 'secondary' service call
            return "responseFromSecondary-" + id;
        }

    }

    public static class UnitTest {

        @Test
        public void testPrimary() {
            HystrixRequestContext context = HystrixRequestContext.initializeContext();
            try {
                ConfigurationManager.getConfigInstance().setProperty("primarySecondary.usePrimary", true);
                assertEquals("responseFromPrimary-20", new CommandFacadeWithPrimarySecondary(20).execute());
            } finally {
                context.shutdown();
                ConfigurationManager.getConfigInstance().clear();
            }
        }

        @Test
        public void testSecondary() {
            HystrixRequestContext context = HystrixRequestContext.initializeContext();
            try {
                ConfigurationManager.getConfigInstance().setProperty("primarySecondary.usePrimary", false);
                assertEquals("responseFromSecondary-20", new CommandFacadeWithPrimarySecondary(20).execute());
            } finally {
                context.shutdown();
                ConfigurationManager.getConfigInstance().clear();
            }
        }
    }
}
```

[View Source](https://github.com/Netflix/Hystrix/blob/master/hystrix-examples/src/main/java/com/netflix/hystrix/examples/basic/CommandFacadeWithPrimarySecondary.java)



### 4.21 Client Doesn't Perform Network Access

When you wrap behavior that does not perform network access, but where latency is a concern or the threading overhead is unacceptable, you can set the [`executionIsolationStrategy`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommandProperties.html#executionIsolationStrategy()) property to [`ExecutionIsolationStrategy`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommandProperties.ExecutionIsolationStrategy.html)`.SEMAPHORE` and Hystrix will use semaphore isolation instead.

The following shows how to set this property as the default for a command via code (you can also override it via dynamic properties at runtime).

```java
public class CommandUsingSemaphoreIsolation extends HystrixCommand<String> {

    private final int id;

    public CommandUsingSemaphoreIsolation(int id) {
        super(Setter.withGroupKey(HystrixCommandGroupKey.Factory.asKey("ExampleGroup"))
                // since we're doing an in-memory cache lookup we choose SEMAPHORE isolation
                .andCommandPropertiesDefaults(HystrixCommandProperties.Setter()
                        .withExecutionIsolationStrategy(ExecutionIsolationStrategy.SEMAPHORE)));
        this.id = id;
    }

    @Override
    protected String run() {
        // a real implementation would retrieve data from in memory data structure
        return "ValueFromHashMap_" + id;
    }

}
```

[View Source](https://github.com/Netflix/Hystrix/blob/master/hystrix-examples/src/main/java/com/netflix/hystrix/examples/basic/CommandUsingSemaphoreIsolation.java)



### 4.22 Get-Set-Get with Request Cache Invalidation

If you are implementing a Get-Set-Get use case where the Get receives enough traffic that request caching is desired but sometimes a Set occurs on another command that should invalidate the cache within the same request, you can invalidate the cache by calling [`HystrixRequestCache.clear()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixRequestCache.html#clear(java.lang.String)).

Here is an example implementation:

```java
public class CommandUsingRequestCacheInvalidation {

    /* represents a remote data store */
    private static volatile String prefixStoredOnRemoteDataStore = "ValueBeforeSet_";

    public static class GetterCommand extends HystrixCommand<String> {

        private static final HystrixCommandKey GETTER_KEY = HystrixCommandKey.Factory.asKey("GetterCommand");
        private final int id;

        public GetterCommand(int id) {
            super(Setter.withGroupKey(HystrixCommandGroupKey.Factory.asKey("GetSetGet"))
                    .andCommandKey(GETTER_KEY));
            this.id = id;
        }

        @Override
        protected String run() {
            return prefixStoredOnRemoteDataStore + id;
        }

        @Override
        protected String getCacheKey() {
            return String.valueOf(id);
        }

        /**
         * Allow the cache to be flushed for this object.
         * 
         * @param id
         *            argument that would normally be passed to the command
         */
        public static void flushCache(int id) {
            HystrixRequestCache.getInstance(GETTER_KEY,
                    HystrixConcurrencyStrategyDefault.getInstance()).clear(String.valueOf(id));
        }

    }

    public static class SetterCommand extends HystrixCommand<Void> {

        private final int id;
        private final String prefix;

        public SetterCommand(int id, String prefix) {
            super(HystrixCommandGroupKey.Factory.asKey("GetSetGet"));
            this.id = id;
            this.prefix = prefix;
        }

        @Override
        protected Void run() {
            // persist the value against the datastore
            prefixStoredOnRemoteDataStore = prefix;
            // flush the cache
            GetterCommand.flushCache(id);
            // no return value
            return null;
        }
    }
}
```

[View Source](https://github.com/Netflix/Hystrix/blob/master/hystrix-examples/src/main/java/com/netflix/hystrix/examples/basic/CommandUsingRequestCacheInvalidation.java)

The unit test that confirms the behavior is:

```java
@Test
public void getGetSetGet() {
    HystrixRequestContext context = HystrixRequestContext.initializeContext();
    try {
        assertEquals("ValueBeforeSet_1", new GetterCommand(1).execute());
        GetterCommand commandAgainstCache = new GetterCommand(1);
        assertEquals("ValueBeforeSet_1", commandAgainstCache.execute());
        // confirm it executed against cache the second time
        assertTrue(commandAgainstCache.isResponseFromCache());
        // set the new value
        new SetterCommand(1, "ValueAfterSet_").execute();
        // fetch it again
        GetterCommand commandAfterSet = new GetterCommand(1);
        // the getter should return with the new prefix, not the value from cache
        assertFalse(commandAfterSet.isResponseFromCache());
        assertEquals("ValueAfterSet_1", commandAfterSet.execute());
    } finally {
        context.shutdown();
    }
}
}
```



### 4.23 Migrating a Library to Hystrix

When you are migrating an existing client library to use Hystrix, you should replace each of the “service methods” with a `HystrixCommand`.

The service methods should then forward calls to the `HystrixCommand` and not have any additional business logic in them.

Thus, before migration a service library may look like this:

![img](https://github.com/Netflix/Hystrix/wiki/images/library-migration-to-hystrix-without-640.png)

After migrating, users of a library will be able to access the `HystrixCommand`s directly or indirectly via the service facade that delegates to the `HystrixCommand`s.

![img](https://github.com/Netflix/Hystrix/wiki/images/library-migration-to-hystrix-with-640.png)

## 五、Operations

Hystrix is not only a tool for resilience engineering but also for operations.

This page attempts to share some of what has been learned in operating a system with 100+ Hystrix Command types, 40+ thread pools, and 10+ billion thread-isolated and 200+ billion semaphore-isolated command executions per day.

The screenshots and incidents described on this page come from the Netflix API system and represent either real production issues or [Latency Monkey](http://techblog.netflix.com/2011/07/netflix-simian-army.html) simulations against production.

### 5.1 How to Configure and Tune a Circuit

The typical approach to deploying a new circuit has been to release it into production with liberal configuration (timeouts/threads/semaphores) and then tune it down to a more strict configuration after seeing it run through a peak production cycle.

In practice what this typically looks like is:

1. Leave at default the 1000ms timeout unless it’s known that more time is needed.
2. Leave the threadpool at its default of 10 threads unless it’s known that more threads are needed.
3. Deploy to canary; if all is well, proceed.
4. Run in production for 24 hours on the entire fleet.
5. Rely on standard alerting and monitoring to catch issues if any.
6. After 24 hours, use latency percentiles and traffic volume to calculate what are the lowest configuration values that make sense for the circuit.
7. Change the values on-the-fly in production and monitor them using the real-time dashboards until you are confident.
8. Only ever look at the configuration for this circuit again if the behavior or performance characteristics of the circuit change and are brought to your attention via alerts and/or dashboard monitoring.

The following diagram represents a typical thought process showing how to choose the size of a thread-pool, queue, and execution timeout (or semaphore sizing):

![img](https://github.com/Netflix/Hystrix/wiki/images/thread-configuration-640.png)

For most circuits, you should try to set their timeout values close to the 99.5th percentile of a normal healthy system so they will cut off bad requests and not let them take up system resources or affect user behavior.

You must size thread-pools and queues so they are a small percentage of overall application resources, otherwise they will fail to prevent a dependency from saturating available resources.

The important things about configuring and tuning circuits are:

- you should do tuning in production and based on real traffic patterns
- you can easily adjust settings in real time while monitoring to see impact of different settings

### 5.2 Expect Jitter and Failure

Hystrix measures and reports metrics with millisecond granularity. This reveals “jitter” — seen as bursts of timeouts, thread-pool rejections, slow downs, and other such things. In a large cluster there are generally some of these things occurring at any particular time for a high-volume circuit.

This granularity at which metrics are captured by Hystrix is something many software systems don’t have, so these reports can cause undue worry.

In this screenshot from the Netflix API dashboard that monitors Hystrix Commands in production you can see the orange and purple numbers that show timeouts and threadpool rejections occurring for a small number of requests in a 10-second statistical window representing 243 servers.

![img](https://github.com/Netflix/Hystrix/wiki/images/circuit-identity-jitter-640.png)

Most systems are measured at a fairly high-level — even if broken into percentile latencies it’s done per minute. Also, often it’s done for an entire application request loop, not each individual dependency that is interacted with. In Hystrix you get a much finer-tuned view of what is going on. Once you have the magnifying glass showing you what’s going on with each dependency, don’t be surprised to see jitter that may have been invisible to you before.

Some of the causes:

- client machine garbage collection (your machine does a garbage collection in the middle of a request)
- service machine garbage collection (the remote server does a garbage collection in the middle of a request to it)
- network issues
- different payload sizes for different request arguments
- cache misses
- bursty call patterns
- new machines starting up (deployments, auto-scale events) and “warming up”

### 5.3 When Things Are Latent

If you notice latancy, don’t react by jumping to reconfigure things. If a Hystrix Command is shedding load it’s doing what it’s supposed to *(assuming you configured it correctly when it was healthy, of course — see above)*.

In the early days as Hystrix was being adopted at Netflix it was a common reaction when a circuit (what we internally call a `Hystrix[Observable]Command`/`CircuitBreaker` pairing) became latent to dynamically change properties to increase thread-pools, queues, timeouts, and so forth to “try and give it some breathing room” and get it working again. But that is the opposite of what you should do. If you configured the command correctly for a healthy system and it is now rejecting, timing out, and/or short-circuiting then you should concentrate on fixing the underlying root cause.

Don’t make the mistake of responding by giving the command more resources that it can use up (at an extreme if you behave that way, you DDOS yourself by increasing the size of thread-pools, queues, timeouts, semaphores, and the like.)

For example, imagine that you have a cluster of 100 servers each with 10 concurrent connections to a service allowed, that is: 1000 possible concurrent connections. When healthy it normally uses 200–300 of them at any given time. If latency occurs and backs them all up, you are now using 1000 connections. 10 per box may not seem much for the client so let’s try increasing it to 20, right? Most likely if 10 were saturated, 20 will become saturated as well. Now you have 2000 connections held open against the back end making things even worse.

This is one of the reasons why the circuit breaker exists — to “release the pressure” on underlying systems to let them recover instead of pounding them with more requests in retry loops, hung connections, and the like.

For example, here is an example of a single dependency experiencing latency resulting in timeouts high enough to cause the circuit-breaker to trip on about one-third of the cluster. It is the only circuit in the system having health issues and Hystrix is preventing it from taking other resources while it has latency problems.

![img](https://github.com/Netflix/Hystrix/wiki/images/ops-social-640.png)

In short, let the system shed load, short-circuit, timeout, and reject until the underlying system is healthy again and it will take care of itself and come back to health at the Hystrix layer. Hystrix is designed for exactly this scenario and the point is to reduce resource utilization by latent systems so that recovery can occur quickly by keeping most resources isolated and away from those that are hung up on a latent connection.

### 5.4 What Dependency Failure Looks Like

The most typical type of failure in a distributed system is for a single dependency to fail or become latent while all others remain healthy. In these cases the metrics and dashboards are very obvious in showing what is happening:

![img](https://github.com/Netflix/Hystrix/wiki/images/ops-cinematch-1-640.png)

The above screenshot shows a single circuit with a 20% error rate: High enough to have impact but not enough to start tripping the circuit breakers. The other three circuits are unaffected.

In this particular example it is actual errors, not latency, that is causing the problem — as shown by the red numbers instead of orange.

The following charts were captured during the same incident to show the historical trend of this circuit and how it spiked in failures and fallbacks.

![img](https://github.com/Netflix/Hystrix/wiki/images/ops-cinematch-2-640.png)

### 5.5 Dependency Failure with Fallback

Here is a screenshot of another incident affecting a single circuit. Note that the 99.5th percentile latency is very high. That’s how long the underlying worker threads were taking to complete, which would in turn saturate the thread pools and lead to time-outs from the calling thread.

All but one machine in the cluster has the circuit breaker tripped, which accounts for most traffic being short-circuited (blue), and on the one machine still trying most requests are being timed out (orange).

![img](https://github.com/Netflix/Hystrix/wiki/images/ops-getbookmarks-640.png)

Note that the other circuits are healthy and the line graph on the left shows no increase in 500s being returned since this circuit is returning a fallback so users are receiving a degraded but still functional experience.

### 5.6 Cascading Dependency Failures

This screenshot represents a failure (in this case high latency) of a single system that is heavily depended upon by many other systems and so the failure cascaded across them as well. The Netflix API system had to be resilient against latency and failure not from just the single root cause but all of the systems impacted by it as well.

The following screenshot shows six circuits representing three different systems:

![img](https://github.com/Netflix/Hystrix/wiki/images/ops-ab-640.png)

At the time of this incident Hystrix was still mostly a “Netflix-API-only” thing. As Hystrix rolls across more and more Netflix teams, this further limits the impact of cascading failure, as this next diagram illustrates:

![img](https://github.com/Netflix/Hystrix/wiki/images/cascading-failure-preventing-640.png)

### 5.7 When It’s You, Not The Dependency

If all of the circuits seem bad (the dashboard is all lit up) then there’s a good chance the problem is your system, not all of your dependencies at the same time.

![img](https://github.com/Netflix/Hystrix/wiki/images/ops-complete-system-640.png)

Two examples of system problems that can cause this are:

- system is overloaded (high load average, CPU usage, etc.)
  - An example of when this can occur is if autoscaling policies fail or don’t scale fast enough with traffic surges, and machines are receiving more traffic than they can handle.
- memory leak that eventually causes GC thrashing which steals CPU and causes pauses which in turn causes circuits to timeout, backup and reject

## 六、配置

### 6.1 Introduction

Hystrix uses [Archaius](https://github.com/Netflix/archaius) for the default implementation of properties for configuration.

The documentation below describes the default [`HystrixPropertiesStrategy`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/strategy/properties/HystrixPropertiesStrategy.html) implementation that is used unless you override it by using a [plugin](https://github.com/Netflix/Hystrix/wiki/Plugins).

Each property has four levels of precedence:

**1. Global default from code**

This is the default if none of the following 3 are set.

The global default is shown as “**Default Value**” in the tables below.

**2. Dynamic global default property**

You can change a global default value by using properties.

The global default property name is shown as “**Default Property**” in the tables below.

**3. Instance default from code**

You can define an instance-specific default. Example:

```
HystrixCommandProperties.Setter()
   .withExecutionTimeoutInMilliseconds(int value)
```

You would insert a command of this sort into a `HystrixCommand` constructor in a manner similar to this:

```
public HystrixCommandInstance(int id) {
    super(Setter.withGroupKey(HystrixCommandGroupKey.Factory.asKey("ExampleGroup"))
        .andCommandPropertiesDefaults(HystrixCommandProperties.Setter()
               .withExecutionTimeoutInMilliseconds(500)));
    this.id = id;
}
```

There are convenience constructors for commonly-set initial values. Here's an example:

```
public HystrixCommandInstance(int id) {
    super(HystrixCommandGroupKey.Factory.asKey("ExampleGroup"), 500);
    this.id = id;
}
```

**4. Dynamic instance property**

You can set instance-specific values dynamically which override the preceding three levels of defaults.

The dynamic instance property name is shown as “**Instance Property**” in the tables below.

Example:

| Instance Property | `hystrix.command.*HystrixCommandKey*.execution.isolation.thread.timeoutInMilliseconds` |
| ----------------- | ------------------------------------------------------------ |
|                   |                                                              |

Replace the [*`HystrixCommandKey`*](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixCommandKey.html) portion of the property with the [`HystrixCommandKey.name()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommandKey.html#name()) value of whichever `HystrixCommand` you are targeting.

For example, if the key was named “`SubscriberGetAccount`” then the property name would be:

> ```
> hystrix.command.SubscriberGetAccount.execution.isolation.thread.timeoutInMilliseconds
> ```



### 6.2 Command Properties

下面的配置 [Properties](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixCommandProperties.html) 决定了 `HystrixCommand` 如何被执行。

#### 6.2.1 Execution

下面的配置决定了 [`HystrixCommand.run()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommand.html#run()) 如何被执行。

**execution.isolation.strategy**

`HystrixCommand.run()` 以哪种隔离策略执行，分为 THREAD 和 SEMAPHORE 两种。

- `THREAD` — 它在单独的线程上执行，同时请求受线程池中线程数量的限制。
- `SEMAPHORE` — 它在调用线程上执行，并且并发请求受信号量计数限制。

Thread 还是 Semaphore，该如何选择？

HystrixCommand 默认使用的是 THREAD，这也是推荐的方式，HystrixObservableCommand 用的是 SEMAPHORE 方式。

Commands executed in threads have an extra layer of protection against latencies beyond what network timeouts can offer.

<!-- 在线程中执行的命令具有比网络超时更多的保护层，以防止延迟。-->

通常情况下，只有在调用非网络请求且高并发（每秒数百次，每个实例）时，使用 SEMAPHORE 隔离才是适当的，因为单独线程的开销太高了。

> Netflix API has 100+ commands running in 40+ thread pools and only a handful of those commands are not running in a thread - those that fetch metadata from an in-memory cache or that are façades to thread-isolated commands (see [“Primary + Secondary with Fallback” pattern](https://github.com/Netflix/Hystrix/wiki/How-To-Use#common-patterns) for more information on this).

![img](https://github.com/Netflix/Hystrix/wiki/images/isolation-options-640.png)

[(Click for larger view)](https://github.com/Netflix/Hystrix/wiki/images/isolation-options-1280.png)

See [how isolation works](https://github.com/Netflix/Hystrix/wiki/How-it-Works#isolation) for more information about this decision.

| Default Value                | `THREAD` (see `ExecutionIsolationStrategy.THREAD`)           |
| ---------------------------- | ------------------------------------------------------------ |
| Possible Values              | `THREAD`, `SEMAPHORE`                                        |
| Default Property             | `hystrix.command.default.execution.isolation.strategy`       |
| Instance Property            | `hystrix.command.*HystrixCommandKey*.execution.isolation.strategy` |
| How to Set Instance Default: | `// to use thread isolation HystrixCommandProperties.Setter()   .withExecutionIsolationStrategy(ExecutionIsolationStrategy.THREAD) // to use semaphore isolation HystrixCommandProperties.Setter()   .withExecutionIsolationStrategy(ExecutionIsolationStrategy.SEMAPHORE)` |



**execution.isolation.thread.timeoutInMilliseconds**

HystrixCommand 默认是由超时时间控制（execution.timeout.enabled = true）并且分配降级策略的，这个参数就设定了超时时间，默认为 1000 ms

This property sets the time in milliseconds after which the caller will observe a timeout and walk away from the command execution. Hystrix marks the `HystrixCommand` as a TIMEOUT, and performs fallback logic. Note that there is configuration for turning off timeouts per-command, if that is desired (see command.timeout.enabled).

**Note:** Timeouts will fire on `HystrixCommand.queue()`, even if the caller never calls `get()` on the resulting Future. Before Hystrix 1.4.0, only calls to `get()` triggered the timeout mechanism to take effect in such a case.

| Default Value               | `1000`                                                       |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.command.default.execution.isolation.thread.timeoutInMilliseconds` |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.execution.isolation.thread.timeoutInMilliseconds` |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withExecutionTimeoutInMilliseconds(int value)` |



**execution.timeout.enabled**

如上所述，是否开启超时控制，默认为 true

This property indicates whether the `HystrixCommand.run()` execution should have a timeout.

| Default Value               | `true`                                                       |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.command.default.execution.timeout.enabled`          |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.execution.timeout.enabled` |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withExecutionTimeoutEnabled(boolean value)` |



**execution.isolation.thread.interruptOnTimeout**

超时后是否允许 interrupt，默认为 true

This property indicates whether the `HystrixCommand.run()` execution should be interrupted when a timeout occurs.

| Default Value               | `true`                                                       |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.command.default.execution.isolation.thread.interruptOnTimeout` |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.execution.isolation.thread.interruptOnTimeout` |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withExecutionIsolationThreadInterruptOnTimeout(boolean value)` |



**execution.isolation.thread.interruptOnCancel**

cancel 后是否 interrupt，默认为 false

This property indicates whether the `HystrixCommand.run()` execution should be interrupted when a cancellation occurs.

| Default Value               | `false`                                                      |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.command.default.execution.isolation.thread.interruptOnCancel` |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.execution.isolation.thread.interruptOnCancel` |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withExecutionIsolationThreadInterruptOnCancel(boolean value)` |



**execution.isolation.semaphore.maxConcurrentRequests**

如果你的隔离策略配置的是 ExecutionIsolationStrategy.SEMAPHORE，那这个参数就是表明信号量的值，也就是最大的并发请求数。如果达到了这个值，随后的请求将会被拒绝。默认为 10。这个信号量值设置为多少，等同于你往线程池里放多少个线程，不过信号量的开销要小得多，而且方法的执行速度也要快得多，如果不是这样的情况，最好还是选择线程池方式，也就是 THREAD

This property sets the maximum number of requests allowed to a `HystrixCommand.run()` method when you are using `ExecutionIsolationStrategy.SEMAPHORE`.

If this maximum concurrent limit is hit then subsequent requests will be rejected.

The logic that you use when you size a semaphore is basically the same as when you choose how many threads to add to a thread-pool, but the overhead for a semaphore is far smaller and typically the executions are far faster (sub-millisecond), otherwise you would be using threads.

> For example, 5000rps on a single instance for in-memory lookups with metrics being gathered has been seen to work with a semaphore of only 2.

The isolation principle is still the same so the semaphore should still be a small percentage of the overall container (i.e. Tomcat) thread pool, not all of or most of it, otherwise it provides no protection.

| Default Value               | `10`                                                         |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.command.default.execution.isolation.semaphore.maxConcurrentRequests` |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.execution.isolation.semaphore.maxConcurrentRequests` |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withExecutionIsolationSemaphoreMaxConcurrentRequests(int value)` |



#### 6.2.2 Fallback

以下配置决定了 HystrixCommand.getFallback 的逻辑，这些配置同时适用于 THREAD 和 SEMAPHORE

The following properties control how [`HystrixCommand.getFallback()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommand.html#getFallback()) executes. These properties apply to both `ExecutionIsolationStrategy.THREAD` and `ExecutionIsolationStrategy.SEMAPHORE`.



**fallback.isolation.semaphore.maxConcurrentRequests**

该值为请求 Fallback 的最大并发请求数，默认为 10，如果达到了这个值，随后的请求将会抛出异常

This property sets the maximum number of requests a `HystrixCommand.getFallback()` method is allowed to make from the calling thread.

If the maximum concurrent limit is hit then subsequent requests will be rejected and an exception thrown since no fallback could be retrieved.

| Default Value               | `10`                                                         |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.command.default.fallback.isolation.semaphore.maxConcurrentRequests` |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.fallback.isolation.semaphore.maxConcurrentRequests` |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withFallbackIsolationSemaphoreMaxConcurrentRequests(int value)` |



**fallback.enabled**

当错误或超时发生时，是否走降级策略，默认为 true

Since: 1.2

This property determines whether a call to `HystrixCommand.getFallback()` will be attempted when failure or rejection occurs.

| Default Value               | `true`                                                       |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.command.default.fallback.enabled`                   |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.fallback.enabled`       |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withFallbackEnabled(boolean value)` |



#### 6.2.3 Circuit Breaker

The circuit breaker properties control behavior of the [`HystrixCircuitBreaker`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixCircuitBreaker.html).



**circuitBreaker.enabled**

是否开启熔断器，默认为 true

This property determines whether a circuit breaker will be used to track health and to short-circuit requests if it trips.

| Default Value               | `true`                                                       |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.command.default.circuitBreaker.enabled`             |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.circuitBreaker.enabled` |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withCircuitBreakerEnabled(boolean value)` |



**circuitBreaker.requestVolumeThreshold**

滑动窗口大小，即触发熔断的最小请求数量，默认为 20。举个例子，一共只有 19 个请求落在窗口内，就算全都失败了，也不会触发熔断

This property sets the minimum number of requests in a rolling window that will trip the circuit.

For example, if the value is 20, then if only 19 requests are received in the rolling window (say a window of 10 seconds) the circuit will not trip open even if all 19 failed.

| Default Value               | `20`                                                         |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.command.default.circuitBreaker.requestVolumeThreshold` |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.circuitBreaker.requestVolumeThreshold` |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withCircuitBreakerRequestVolumeThreshold(int value)` |



**circuitBreaker.sleepWindowInMilliseconds**

设置一个时间，当触发熔断后，多少秒之后再次进行访问尝试，看是否仍然要保持熔断状态，默认为 5000ms

This property sets the amount of time, after tripping the circuit, to reject requests before allowing attempts again to determine if the circuit should again be closed.

| Default Value               | `5000`                                                       |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.command.default.circuitBreaker.sleepWindowInMilliseconds` |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.circuitBreaker.sleepWindowInMilliseconds` |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withCircuitBreakerSleepWindowInMilliseconds(int value)` |



**circuitBreaker.errorThresholdPercentage**

设置一个失败率，失败的请求达到这个值时，就触发熔断，默认为 50%

This property sets the error percentage at or above which the circuit should trip open and start short-circuiting requests to fallback logic.

| Default Value               | `50`                                                         |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.command.default.circuitBreaker.errorThresholdPercentage` |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.circuitBreaker.errorThresholdPercentage` |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withCircuitBreakerErrorThresholdPercentage(int value)` |



**circuitBreaker.forceOpen**

This property, if `true`, forces the circuit breaker into an open (tripped) state in which it will reject all requests.

This property takes precedence over `circuitBreaker.forceClosed`.

| Default Value               | `false`                                                      |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.command.default.circuitBreaker.forceOpen`           |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.circuitBreaker.forceOpen` |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withCircuitBreakerForceOpen(boolean value)` |



**circuitBreaker.forceClosed**

This property, if `true`, forces the circuit breaker into a closed state in which it will allow requests regardless of the error percentage.

The `circuitBreaker.forceOpen` property takes precedence so if it is set to `true` this property does nothing.

| Default Value               | `false`                                                      |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.command.default.circuitBreaker.forceClosed`         |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.circuitBreaker.forceClosed` |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withCircuitBreakerForceClosed(boolean value)` |



#### 6.2.4 Metrics

该配置指定了如何在运行过程中收集 metrics

The following properties are related to capturing metrics from `HystrixCommand` and `HystrixObservableCommand` execution.



**metrics.rollingStats.timeInMilliseconds**

指标收集的滑动窗口时间，也就是 Hystrix 保持多久的一个指标收集，为之后的使用和上报做准备，默认为 10000 ms。下图为具体图示

This property sets the duration of the statistical rolling window, in milliseconds. This is how long Hystrix keeps metrics for the circuit breaker to use and for publishing.

As of 1.4.12, this property affects the initial metrics creation only, and adjustments made to this property after startup will not take effect. This avoids metrics data loss, and allows optimizations to metrics gathering.

The window is divided into buckets and “rolls” by these increments.

For example, if this property is set to 10 seconds (`10000`) with ten 1-second buckets, the following diagram represents how it rolls new buckets on and old ones off:

![img](https://github.com/Netflix/Hystrix/wiki/images/rolling-stats-640.png)

| Default Value               | `10000`                                                      |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.command.default.metrics.rollingStats.timeInMilliseconds` |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.metrics.rollingStats.timeInMilliseconds` |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withMetricsRollingStatisticalWindowInMilliseconds(int value)` |



**metrics.rollingStats.numBuckets**

配合上面的参数使用，表示一个滑动窗口时间被分割为多少个 buckets 来进行细粒度指标收集，默认为 10

This property sets the number of buckets the rolling statistical window is divided into.

**Note:** The following must be true — “`metrics.rollingStats.timeInMilliseconds % metrics.rollingStats.numBuckets == 0`” — otherwise it will throw an exception.

In other words, 10000/10 is okay, so is 10000/20 but 10000/7 is not.

As of 1.4.12, this property affects the initial metrics creation only, and adjustments made to this property after startup will not take effect. This avoids metrics data loss, and allows optimizations to metrics gathering.

| Default Value               | `10`                                                         |
| --------------------------- | ------------------------------------------------------------ |
| Possible Values             | Any value that `metrics.rollingStats.timeInMilliseconds` can be evenly divided by. The result however should be buckets measuring hundreds or thousands of milliseconds. Performance at high volume has not been tested with buckets <100ms. |
| Default Property            | `hystrix.command.default.metrics.rollingStats.numBuckets`    |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.metrics.rollingStats.numBuckets` |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withMetricsRollingStatisticalWindowBuckets(int value)` |



**metrics.rollingPercentile.enabled**

进行百分比、均值等指标的收集，默认为 true，如果不选，则所有这类的指标返回 -1

This property indicates whether execution latencies should be tracked and calculated as percentiles. If they are disabled, all summary statistics (mean, percentiles) are returned as -1.

| Default Value               | `true`                                                       |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.command.default.metrics.rollingPercentile.enabled`  |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.metrics.rollingPercentile.enabled` |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withMetricsRollingPercentileEnabled(boolean value)` |



**metrics.rollingPercentile.timeInMilliseconds**

进行百分比均值等指标收集的窗口时间，默认为 60000 ms

This property sets the duration of the rolling window in which execution times are kept to allow for percentile calculations, in milliseconds.

The window is divided into buckets and “rolls” by those increments.

As of 1.4.12, this property affects the initial metrics creation only, and adjustments made to this property after startup will not take effect. This avoids metrics data loss, and allows optimizations to metrics gathering.

| Default Value               | `60000`                                                      |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.command.default.metrics.rollingPercentile.timeInMilliseconds` |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.metrics.rollingPercentile.timeInMilliseconds` |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withMetricsRollingPercentileWindowInMilliseconds(int value)` |



**metrics.rollingPercentile.numBuckets**

同理，上述百分比指标将被分为多少个 buckets 来进行收集，必须整除

This property sets the number of buckets the `rollingPercentile` window will be divided into.

Note: The following must be true — “`metrics.rollingPercentile.timeInMilliseconds % metrics.rollingPercentile.numBuckets == 0`” — otherwise it will throw an exception.

In other words, 60000/6 is okay, so is 60000/60 but 10000/7 is not.

As of 1.4.12, this property affects the initial metrics creation only, and adjustments made to this property after startup will not take effect. This avoids metrics data loss, and allows optimizations to metrics gathering.

| Default Value               | `6`                                                          |
| --------------------------- | ------------------------------------------------------------ |
| Possible Values             | Any value that `metrics.rollingPercentile.timeInMilliseconds` can be evenly divided by. The result however should be buckets measuring thousands of milliseconds. Performance at high volume has not been tested with buckets <1000ms. |
| Default Property            | `hystrix.command.default.metrics.rollingPercentile.numBuckets` |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.metrics.rollingPercentile.numBuckets` |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withMetricsRollingPercentileWindowBuckets(int value)` |



**metrics.rollingPercentile.bucketSize**

收集百分比指标时，每一个 buckets 最大收集的请求数，默认为 100。举个例子，如果该值设置为 100，那一个 bucket 有 500 个请求过来时，只会用后 100 个请求做指标计算。

This property sets the maximum number of execution times that are kept per bucket. If more executions occur during the time they will wrap around and start over-writing at the beginning of the bucket.

For example, if bucket size is set to 100 and represents a bucket window of 10 seconds, but 500 executions occur during this time, only the last 100 executions will be kept in that 10 second bucket.

If you increase this size, this also increases the amount of memory needed to store values and increases the time needed for sorting the lists to do percentile calculations.

As of 1.4.12, this property affects the initial metrics creation only, and adjustments made to this property after startup will not take effect. This avoids metrics data loss, and allows optimizations to metrics gathering.

| Default Value               | `100`                                                        |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.command.default.metrics.rollingPercentile.bucketSize` |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.metrics.rollingPercentile.bucketSize` |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withMetricsRollingPercentileBucketSize(int value)` |



**metrics.healthSnapshot.intervalInMilliseconds**

设置一个时间，来指定收集健康指标的时间间隔（比如计算成功数、错误率等），默认为 500ms。该指标的意义是如果你的系统 CPU 负载很高，该指标计算同样也是 CPU 密集型运算，这个值可以让你控制多久进行一次健康统计。

This property sets the time to wait, in milliseconds, between allowing health snapshots to be taken that calculate success and error percentages and affect circuit breaker status.

On high-volume circuits the continual calculation of error percentages can become CPU intensive thus this property allows you to control how often it is calculated.

| Default Value               | `500`                                                        |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.command.default.metrics.healthSnapshot.intervalInMilliseconds` |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.metrics.healthSnapshot.intervalInMilliseconds` |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withMetricsHealthSnapshotIntervalInMilliseconds(int value)` |



#### 6.2.5 Request Context

以下参数会影响 HystrixRequestContex

These properties concern [`HystrixRequestContext`](http://netflix.github.com/Hystrix/javadoc/index.html?com/netflix/hystrix/strategy/concurrency/HystrixRequestContext.html) functionality used by `HystrixCommand`.



**requestCache.enabled**

该参数决定了 HystrixCommand.getCacheKey 是否被启用，默认为 true

This property indicates whether [`HystrixCommand.getCacheKey()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommand.html#getCacheKey()) should be used with [`HystrixRequestCache`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixRequestCache.html) to provide de-duplication functionality via request-scoped caching.

| Default Value               | `true`                                                       |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.command.default.requestCache.enabled`               |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.requestCache.enabled`   |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withRequestCacheEnabled(boolean value)` |



**requestLog.enabled**

该参数决定了执行过程中的日志，是否会输出到 HystrixRequestLog

This property indicates whether `HystrixCommand` execution and events should be logged to [`HystrixRequestLog`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixRequestLog.html).

| Default Value               | `true`                                                       |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.command.default.requestLog.enabled`                 |
| Instance Property           | `hystrix.command.*HystrixCommandKey*.requestLog.enabled`     |
| How to Set Instance Default | `HystrixCommandProperties.Setter()   .withRequestLogEnabled(boolean value)` |



### 6.3 Collapser Properties

The following properties control [`HystrixCollapser`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixCollapser.html) behavior.



**maxRequestsInBatch**

This property sets the maximum number of requests allowed in a batch before this triggers a batch execution.

| Default Value               | `Integer.MAX_VALUE`                                          |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.collapser.default.maxRequestsInBatch`               |
| Instance Property           | `hystrix.collapser.*HystrixCollapserKey*.maxRequestsInBatch` |
| How to Set Instance Default | `HystrixCollapserProperties.Setter()   .withMaxRequestsInBatch(int value)` |



**timerDelayInMilliseconds**

This property sets the number of milliseconds after the creation of the batch that its execution is triggered.

| Default Value               | `10`                                                         |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.collapser.default.timerDelayInMilliseconds`         |
| Instance Property           | `hystrix.collapser.*HystrixCollapserKey*.timerDelayInMilliseconds` |
| How to Set Instance Default | `HystrixCollapserProperties.Setter()   .withTimerDelayInMilliseconds(int value)` |



**requestCache.enabled**

This property indicates whether request caching is enabled for [`HystrixCollapser.execute()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCollapser.html#execute()) and [`HystrixCollapser.queue()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCollapser.html#queue()) invocations.

| Default Value               | `true`                                                       |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.collapser.default.requestCache.enabled`             |
| Instance Property           | `hystrix.collapser.*HystrixCollapserKey*.requestCache.enabled` |
| How to Set Instance Default | `HystrixCollapserProperties.Setter()   .withRequestCacheEnabled(boolean value)` |



### 6.4 ThreadPool Properties

以下参数控制 command 在执行时所需的线程池参数，与 Java 中的 ThreadPoolExecutor 的参数是对应的。大多数情况下 10 个线程足够了（甚至更小）。要想判断到底多少个线程合适，有以下的经验计算公式。

流量顶峰时的 QPS * 99%请求时延 + 一些用来缓冲的空间

The following properties control the behavior of the thread-pools that Hystrix Commands execute on. Please note that these names match those in [the ThreadPoolExecutor Javadoc](https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/ThreadPoolExecutor.html)

Most of the time the default value of 10 threads will be fine (often it could be made smaller).

To determine if it needs to be larger, a basic formula for calculating the size is:

*requests per second at peak when healthy × 99th percentile latency in seconds + some breathing room*

See the example below to see how this formula is put into practice.

The general principle is keep the pool as small as possible, as it is the primary tool to shed load and prevent resources from becoming blocked if latency occurs.

> Netflix API has 30+ of its threadpools set at 10, two at 20, and one at 25.

![img](https://github.com/Netflix/Hystrix/wiki/images/thread-configuration-640.png)

[*(Click for larger view)*](https://github.com/Netflix/Hystrix/wiki/images/thread-configuration-1280.png)

The above diagram shows an example configuration in which the dependency has no reason to hit the 99.5th percentile and therefore it cuts it short at the network timeout layer and immediately retries with the expectation that it will get median latency most of the time, and will be able to accomplish this all within the 300ms thread timeout.

If the dependency has legitimate reasons to sometimes hit the 99.5th percentile (such as cache miss with lazy generation) then the network timeout will be set higher than it, such as at 325ms with 0 or 1 retries and the thread timeout set higher (350ms+).

The thread-pool is sized at 10 to handle a burst of 99th percentile requests, but when everything is healthy this threadpool will typically only have 1 or 2 threads active at any given time to serve mostly 40ms median calls.

When you configure it correctly a timeout at the `HystrixCommand` layer should be rare, but the protection is there in case something other than network latency affects the time, or the combination of connect+read+retry+connect+read in a worst case scenario still exceeds the configured overall timeout.

The aggressiveness of configurations and tradeoffs in each direction are different for each dependency.

You can change configurations in real-time as needed as performance characteristics change or when problems are found, all without the risk of taking down the entire app if problems or misconfigurations occur.



**coreSize**

核心线程数，默认为 10

This property sets the core thread-pool size.

| Default Value               | `10`                                                         |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.threadpool.default.coreSize`                        |
| Instance Property           | `hystrix.threadpool.*HystrixThreadPoolKey*.coreSize`         |
| How to Set Instance Default | `HystrixThreadPoolProperties.Setter()   .withCoreSize(int value)` |



**maximumSize**

最大线程数，该参数在 `allowMaximumSizeToDivergeFromCoreSize` 为 true 时才生效，默认与核心线程数一样，都是 10

Added in 1.5.9. This property sets the maximum thread-pool size. This is the maximum amount of concurrency that can be supported without starting to reject `HystrixCommand`s. Please note that this setting only takes effect if you also set `allowMaximumSizeToDivergeFromCoreSize`. Prior to 1.5.9, core and maximum sizes were always equal.

| Default Value               | `10`                                                         |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.threadpool.default.maximumSize`                     |
| Instance Property           | `hystrix.threadpool.*HystrixThreadPoolKey*.maximumSize`      |
| How to Set Instance Default | `HystrixThreadPoolProperties.Setter()   .withMaximumSize(int value)` |



**maxQueueSize**

设置 BlockingQueue 所实现队列的最大队列大小，默认为 -1。为 -1 代表用的是 SynchronousQueue，否则就是固定大小的 LinkedBlockingQueue。当核心线程池的线程都在忙碌时，新请求将会落在这个队列里，但超出队列部分将会被拒绝

This property sets the maximum queue size of the `BlockingQueue` implementation.

If you set this to `-1` then [`SynchronousQueue`](http://docs.oracle.com/javase/6/docs/api/java/util/concurrent/SynchronousQueue.html) will be used, otherwise a positive value will be used with [`LinkedBlockingQueue`](http://docs.oracle.com/javase/6/docs/api/java/util/concurrent/LinkedBlockingQueue.html).

**Note:** This property only applies at initialization time since queue implementations cannot be resized or changed without re-initializing the thread executor which is not supported.

If you need to overcome this limitation and to allow dynamic changes in the queue, see the `queueSizeRejectionThreshold` property.

To change between `SynchronousQueue` and `LinkedBlockingQueue` requires a restart.

| Default Value               | `−1`                                                         |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.threadpool.default.maxQueueSize`                    |
| Instance Property           | `hystrix.threadpool.*HystrixThreadPoolKey*.maxQueueSize`     |
| How to Set Instance Default | `HystrixThreadPoolProperties.Setter()   .withMaxQueueSize(int value)` |



**queueSizeRejectionThreshold**

当队列里的等待线程数达到该值时，随后的请求将会被拒绝，即使还没达到 maxQueueSize。该参数的意义是因为 maxQueueSize 在线程刚创建时就固定了大小，无法改变，该值可以弥补这个缺憾，所以有时候 maxQueueSize 不起作用就是因为这个。默认为 5

This property sets the queue size rejection threshold — an artificial maximum queue size at which rejections will occur even if `maxQueueSize` has not been reached. This property exists because the `maxQueueSize` of a [`BlockingQueue`](http://docs.oracle.com/javase/6/docs/api/java/util/concurrent/BlockingQueue.html) cannot be dynamically changed and we want to allow you to dynamically change the queue size that affects rejections.

This is used by `HystrixCommand` when queuing a thread for execution.

**Note:** This property is not applicable if `maxQueueSize == -1`.

| Default Value               | `5`                                                          |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.threadpool.default.queueSizeRejectionThreshold`     |
| Instance Property           | `hystrix.threadpool.*HystrixThreadPoolKey*.queueSizeRejectionThreshold` |
| How to Set Instance Default | `HystrixThreadPoolProperties.Setter()   .withQueueSizeRejectionThreshold(int value)` |



**keepAliveTimeMinutes**

1.5.9版本之前，线程池是固定大小的（相当于 coreSize == maximumSize），而之后的版本这两个值可能不同，线程池可能会创建或销毁线程以动态调整。该参数指定了线程多久不使用就被释放掉，默认值是 1min

This property sets the keep-alive time, in minutes.

Prior to 1.5.9, all thread pools were fixed-size, as `coreSize == maximumSize`. In 1.5.9 and after, setting `allowMaximumSizeToDivergeFromCoreSize` to `true` allows those 2 values to diverge, such that the pool may acquire/release threads. If `coreSize < maximumSize`, then this property controls how long a thread will go unused before being released.

| Default Value               | `1`                                                          |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.threadpool.default.keepAliveTimeMinutes`            |
| Instance Property           | `hystrix.threadpool.*HystrixThreadPoolKey*.keepAliveTimeMinutes` |
| How to Set Instance Default | `HystrixThreadPoolProperties.Setter()   .withKeepAliveTimeMinutes(int value)` |



**allowMaximumSizeToDivergeFromCoreSize**

是否允许线程池的大小扩大到 maximumSize，默认为 false

Added in 1.5.9. This property allows the configuration for `maximumSize` to take effect. That value can then be equal to, or higher, than `coreSize`. Setting `coreSize < maximumSize` creates a thread pool which can sustain `maximumSize` concurrency, but will return threads to the system during periods of relative inactivity. (subject to `keepAliveTimeInMinutes`)

| Default Value               | `false`                                                      |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.threadpool.default.allowMaximumSizeToDivergeFromCoreSize` |
| Instance Property           | `hystrix.threadpool.*HystrixThreadPoolKey*.allowMaximumSizeToDivergeFromCoreSize` |
| How to Set Instance Default | `HystrixThreadPoolProperties.Setter()   .withAllowMaximumSizeToDivergeFromCoreSize(boolean value)` |



**metrics.rollingStats.timeInMilliseconds**

监控线程池指标的滑动窗口时间，默认 10000 ms

This property sets the duration of the statistical rolling window, in milliseconds. This is how long metrics are kept for the thread pool.

The window is divided into buckets and “rolls” by those increments.

| Default Value               | `10000`                                                      |
| --------------------------- | ------------------------------------------------------------ |
| Default Property            | `hystrix.threadpool.default.metrics.rollingStats.timeInMilliseconds` |
| Instance Property           | `hystrix.threadpool.*HystrixThreadPoolKey*.metrics.rollingStats.timeInMilliseconds` |
| How to Set Instance Default | `HystrixThreadPoolProperties.Setter()   .withMetricsRollingStatisticalWindowInMilliseconds(int value)` |



**metrics.rollingStats.numBuckets**

监控线程池指标的 buckets 数量，默认为 10，必须能被上一个指标整除

This property sets the number of buckets the rolling statistical window is divided into.

**Note:** The following must be true — “`metrics.rollingStats.timeInMilliseconds % metrics.rollingStats.numBuckets == 0`” — otherwise it will throw an exception.

In other words, 10000/10 is okay, so is 10000/20 but 10000/7 is not.

| Default Value               | `10`                                                         |
| --------------------------- | ------------------------------------------------------------ |
| Possible Values             | Any value that `metrics.rollingStats.timeInMilliseconds` can be evenly divided by. The result however should be buckets measuring hundreds or thousands of milliseconds. Performance at high volume has not been tested with buckets <100ms. |
| Default Property            | `hystrix.threadpool.default.metrics.rollingStats.numBuckets` |
| Instance Property           | `hystrix.threadpool.*HystrixThreadPoolProperties*.metrics.rollingStats.numBuckets` |
| How to Set Instance Default | `HystrixThreadPoolProperties.Setter()   .withMetricsRollingStatisticalWindowBuckets(int value)` |



## 七、Metrics and Monitoring

### 7.1 Motivation

As HystrixCommands and HystrixObservableCommands execute, they generate metrics on execution outcomes and latency. These are very useful to operators of the system, as they give a great deal of insight into how the system is behaving. Hystrix offers metrics per command key and to very fine granularities (on the order of seconds).

These metrics are useful both individually, and in aggregate. Getting the set of commands that executed in a request, along with outcomes and latency information, is often helpful in debugging. Aggregate metrics are useful in understanding overall system-level behavior, and are appropriate for alerting or reporting. The [Hystrix Dashboard](https://github.com/Netflix/Hystrix/wiki/Dashboard) is one such consumer.

Here's an illustration of commands executing and writing metrics :

![img](https://github.com/Netflix/Hystrix/wiki/images/metrics-generation.png) 

[*(Click for larger view.)*](https://github.com/Netflix/Hystrix/wiki/images/metrics-generation.png)



### 7.2 Hystrix Event Types

The complete set of Hystrix command event types is specified in the table below. These correspond to the enum `com.netflix.hystrix.HystrixEventType`. These types are shared between `HystrixCommand` and `HystrixObservableCommand`.

In a `HystrixCommand`, only single values are returned, so there is 1 event types for execution, and, if necessary, 1 event type for fallback. So a **SUCCESS** implies a value return and the completion of the command.

In a `HystrixObservableCommand`, [0..n] values may be returned, so the **EMIT** event corresponds to a value returned, and the other execution events correspond to the command terminating. If you're familiar with [RxJava](https://github.com/ReactiveX/RxJava), **EMIT** is equivalent to `OnNext`, **SUCCESS** is equivalent to `OnCompleted`, and **FAILURE** is equivalent to `OnError`.



**Command Execution Event Types (`com.netflix.hystrix.HystrixEventType`)**

| Name                     | Description                                                 | Triggers Fallback? |
| ------------------------ | ----------------------------------------------------------- | ------------------ |
| **EMIT**                 | value delivered (`HystrixObservableCommand` only)           | NO                 |
| **SUCCESS**              | execution complete with no errors                           | NO                 |
| **FAILURE**              | execution threw an Exception                                | YES                |
| **TIMEOUT**              | execution started, but did not complete in the allowed time | YES                |
| **BAD_REQUEST**          | execution threw a `HystrixBadRequestException`              | NO                 |
| **SHORT_CIRCUITED**      | circuit breaker **OPEN**, execution not attempted           | YES                |
| **THREAD_POOL_REJECTED** | thread pool at capacity, execution not attempted            | YES                |
| **SEMAPHORE_REJECTED**   | semaphore at capacity, execution not attempted              | YES                |



**Command Fallback Event Types (`com.netflix.hystrix.HystrixEventType`)**

| Name                   | Description                                                | Throws Exception? |
| ---------------------- | ---------------------------------------------------------- | ----------------- |
| **FALLBACK_EMIT**      | fallback value delivered (`HystrixObservableCommand` only) | NO                |
| **FALLBACK_SUCCESS**   | fallback execution complete with no errors                 | NO                |
| **FALLBACK_FAILURE**   | fallback execution threw an error                          | YES               |
| **FALLBACK_REJECTION** | fallback semaphore at capacity, fallback not attempted     | YES               |
| **FALLBACK_MISSING**   | no fallback implemented                                    | YES               |



**Other Command Event Types (`com.netflix.hystrix.HystrixEventType`)**

| Name                    | Description                                                  |
| ----------------------- | ------------------------------------------------------------ |
| **EXCEPTION_THROWN**    | was an exception thrown by the overall command execution?    |
| **RESPONSE_FROM_CACHE** | was the command able to be looked up in cache? If so, execution did not occur |
| **COLLAPSED**           | was the command a result of a collapser batch?               |



**Thread Pool Event Types (`com.netflix.hystrix.HystrixEventType.ThreadPool`)**

| Name         | Description                                          |
| ------------ | ---------------------------------------------------- |
| **EXECUTED** | thread pool has space and allowed the command to run |
| **REJECTED** | thread pool had no room, and rejected the command    |



**Collapser Event Types (`com.netflix.hystrix.HystrixEventType.Collapser`)**

| Name                    | Description                                                  |
| ----------------------- | ------------------------------------------------------------ |
| **BATCH_EXECUTED**      | batch generated by collapser and batch command invoked       |
| **ADDED_TO_BATCH**      | argument added to collapser batch                            |
| **RESPONSE_FROM_CACHE** | argument not added to collapser batch, because it was found in request cache |



### 7.3 Metrics storage

When the metrics get generated, they need to get stored for some period of time before they get pushed off-box and into a different system. The alternative is to always stream metrics directly off-box, and this is unlikely to perform well unless the volume is very low. Instead, the approach Hystrix chooses is to write the metrics to in-memory data structures. These store metrics and allow for querying at some later point.

The specific data structures that store metrics changed in Hystrix 1.5.0.

#### 7.3.1 Up to 1.4.x

In Hystrix versions up to 1.4.x, metrics are written to aggregating data structures. A `HystrixRollingNumber` captures counts of events and a `HystrixRollingPercentile` captures observations of quantities that have interesting distributions. For example, command latency and collapser batch size are tracked using a `HystrixRollingPercentile`. Metrics are written to these data structures synchronously as the command executes. These data structures support a rolling model, where only the most recent metrics are kept.

**HystrixRollingNumber**

As commands start executing, these data structures get initialized. HystrixRollingNumbers take 2 pieces of config: number of buckets, and overall window of metrics to track. Call the number of buckets `n` and the overall window `w` (in milliseconds). Then call `t` (`= w/n`) the bucket size (in milliseconds). Given that config, writes always go into the newest bucket, and reads go against this "hot" bucket and the previous `n-1` buckets. Since only `n` buckets are needed at a time, the data structure re-uses old buckets to save on memory allocation. Because all of the writes are synchronous, there's no background work that does this "bucket rolling". Instead, one unlucky write per bucket pays the cost of doing the work of updating pointers and getting a new bucket ready for writing. This data structure permits any threads to write, so has internal synchronization logic to allow this to occur safely, without external synchronization.

Configuration of `n` and `w` are exposed at [Number of Buckets Config](https://github.com/Netflix/Hystrix/wiki/Configuration#metricsrollingstatsnumbuckets) and [Overall window config](https://github.com/Netflix/Hystrix/wiki/Configuration#metricsrollingstatstimeinmilliseconds)

Please also see those config links for an illustration of how the rolling number does bucketing.

**HystrixRollingPercentile**

The HystrixRollingPercentile is similar. It shares the bucketing semantics of HystrixRollingNumber, and has the additional configuration of the maximum number of observations in a bucket. Reads of this data structure can be a mean or arbitrary percentile of the distribution. In this case, the distribution is calculated over the "hot" bucket and the previous `n-1` buckets.

Configuration of `n` and `w` are exposed at [Number of Buckets Config](https://github.com/Netflix/Hystrix/wiki/Configuration#metrics.rollingPercentile.numBuckets) and [Overall window config](https://github.com/Netflix/Hystrix/wiki/Configuration#metrics.rollingPercentile.timeInMilliseconds). The maximum count per bucket is exposed at [Maximum count config](https://github.com/Netflix/Hystrix/wiki/Configuration#metrics.rollingPercentile.bucketSize)

### 7.4 Metric reads

With these data structures, it's straightforward to ask for aggregate values. You may ask a `HystrixRollingNumber` for a rolling count of SUCCESS, or a `HystrixRollingPercentile` for a rolling mean, for example. The [Hystrix Circuit Breaker](https://github.com/Netflix/Hystrix/wiki/How-it-Works#circuit-breaker) is based on the rolling count of successes vs failures, for instance. All of the metrics publishers and streams in `hystrix-contrib` read these rolling counts and publish aggregate info off-box.

However, the story is more complicated with any level of detail past this. Because reads only return these aggregated values, we have no ability to do any faceting. For example, knowing that FooCommand is failing at 50% in aggregate is interesting, but I'd also like the ability to know that it's failing at 0% in Mexico and Brazil, and 98% in the United States. That level of detail is lost when we strictly do aggregates.

As a result, internally at Netflix, we've started to parse the `HystrixRequestLog`, and then use this for further analysis. The `HystrixRequestLog` tracks all events in a request, and makes them available as a string. This is not optimal, but makes a few things possible. We can take a peek at this value at the end of every HTTP request, and then push out this data along with all other contextual information in the HTTP request. This makes it possible to do things like partition the Hystrix outcomes/latency by HTTP path, which we've found to be valuable.

#### 7.4.1 1.5.x (and beyond)

As a result of this insight, we've redesigned how metrics can get consumed to allow for more flexibility. If metrics are modeled as a first-class stream, they may be consumed in any arbitrary way. To do this, we build streams for each metric. Each `HystrixCommandKey` has a start-event and completion-event stream that may be subscribed to, as does each `HystrixThreadPoolKey`. Each `HystrixCollapserKey` has a stream dedicated to collapser actions.

To maintain backward compatibility (and verify that this abstraction holds water), `hystrix-core` provides implementations of all of the aggregated queries possible against `HystrixRollingNumber`/`HystrixRollingPercentile`, except calculated against these streams. This has a few benefits. Instead of maintaining complex code within Hystrix, we depend on [RxJava](https://github.com/ReactiveX/RxJava) for thread-safe implementations of aggregating operations. As an example, bucketing by time is implementing using [Observable.window](http://reactivex.io/documentation/operators/window.html). This operates on a background thread, so we now get "bucket-rolling" behavior on a background thread for free without having to implement it ourselves.

To create this abstraction, each command no longer emits into a Command-scoped `HystrixRollingNumber`. Instead, it emits into a thread-local [rx.Subject](https://github.com/ReactiveX/RxJava/wiki/subject). This is done to allow writes to occur without any synchronization. From there, each event gets written to a command-specific, threadpool-specific or collapser-specific [rx.Subject](https://github.com/ReactiveX/RxJava/wiki/subject). These Subjects then are exposed as Observables in the Hystrix public API as follows:

| Class                               | Method      | Return Type                                  |
| ----------------------------------- | ----------- | -------------------------------------------- |
| `HystrixCommandStartStream`         | `observe()` | `Observable<HystrixCommandExecutionStarted>` |
| `HystrixCommandCompletionStream`    | `observe()` | `Observable<HystrixCommandCompletion>`       |
| `HystrixThreadPoolStartStream`      | `observe()` | `Observable<HystrixCommandExecutionStarted>` |
| `HystrixThreadPoolCompletionStream` | `observe()` | `Observable<HystrixCommandCompletion>`       |
| `HystrixCollapserEventStream`       | `observe()` | `Observable<HystrixCollapserEvent>`          |
| `HystrixRequestEventsStream`        | `observe()` | `Observable<HystrixRequestEvents>`           |

Hystrix users may create any metrics strategy that's most appropriate for their domain. A few default implementation are provided. An example is RollingCommandEventCounterStream. Any thread may synchronously read the latest rolling value from this stream, which is getting written to in the background as buckets roll by.

Here are the provided metrics consumers, and how they may be invoked:

**Bucketed Event Counters**

These count events by type. Commands, threadpools, and collapsers each have different types: [#hystrix-event-types](`HystrixEventType`, `HystrixEventType.ThreadPool`, and `HystrixEventType.Collapser`, respectively)

Rolling counters only consider the last `n` buckets, just like the `HystrixRollingNumber`/`Percentile` above. Cumulative counters consider all events since the start of the JVM.

These counters may be treated as a stream by invoking `Observable<long[]> observe()`. This returns a long array on every bucket roll. By using the appropriate event type enum's ordinal as an index into the long array, you can find the count of any event type.

They may be also read synchronously. In this case, you're guaranteed to read the most-recently calculated value. This doesn't include the bucket being currently written to. In this case, you can invoke `long[] getLatest()` for the entire set of counts, or `long getLatest(HystrixEventType)` for a specific event type.

**Bucketed Max-Concurrency Counters**

These keep track of the high-water mark of concurrency in a given time period. This has only a rolling version, as a cumulative counter would provide very little information. This is tracked for commands and threadpools.

These counters may be treated as a stream by invoking `Observable<Integer> observe()`. This returns the maximum concurrency witnessed in the last `n` buckets of observations and is emitted on every bucket roll.

They may also be read synchronously, using `int getLatest()` for the most recently calculated value.

**Bucketed Distributions**

These keep track of a set of observations and allow queries on the aggregated distribution over a rolling window. This is tracked for command latency, command user latency, and collapser batch size.

These counters may be treated as a stream by invoking `Observable<CachedValuesHistogram> observe()` This returns the latest aggregate histogram, which you can then further query.

They may also be read synchronously, using `CachedValuesHistogram getLatest` for the most recent histogram, `int getLatestMean()` for the latest mean, and `int getLatestPercentile(long percentile)` for the most recent percentile.

**Other streams**

This is an area where we think the community will have a lot of great ideas that we haven't thought of yet. Please let us know if you're using metrics in a specific way for your domain - we'd love to hear your experience. Even better, feel free to submit your work as an example or a `hystrix-contrib` module.

### 7.5 Sample streams

In addition to event streams, there are metrics that live outside of any given event that are useful in understanding the system. All of these are new, as of 1.5.0

**Configuration stream**

Configuration has a different lifecycle than any command or request. It's often useful to understand the global configuration picture, so 1.5.0 has introduced a dedicated configuration stream (`com.netflix.hystrix.config.HystrixConfigurationStream`). This class knows how to look up all current configuration values, then attaches them to a timer, to make it into a stream

Hystrix provides a mapping of these object into JSON at `com.netflix.hystrix.contrib.sample.stream.HystrixConfigurationJsonStream` and an embedding of this stream into an SSE servlet at `com.netflix.hystrix.contrib.sample.stream.HystrixConfigSseServlet` (both in `hystrix-metrics-event-stream` contrib module. You're free to consume the stream using these models, or invent your own. [#1062](https://github.com/Netflix/Hystrix/issues/1062) and [#1063](https://github.com/Netflix/Hystrix/issues/1063) provide some future directions that we believe will be better, performance-wise.

Here's what output of this SSE stream looks like for the [`hystrix-examples-webapp`](https://github.com/Netflix/Hystrix/tree/master/hystrix-examples-webapp):

> data: {"type":"HystrixConfig","commands":{"CreditCardCommand":{"threadPoolKey":"CreditCard","groupKey":"CreditCard","execution":{"isolationStrategy":"THREAD","threadPoolKeyOverride":null,"requestCacheEnabled":true,"requestLogEnabled":true,"timeoutEnabled":true,"fallbackEnabled":true,"timeoutInMilliseconds":3000,"semaphoreSize":10,"fallbackSemaphoreSize":10,"threadInterruptOnTimeout":true},"metrics":{"healthBucketSizeInMs":500,"percentileBucketSizeInMilliseconds":60000,"percentileBucketCount":10,"percentileEnabled":true,"counterBucketSizeInMilliseconds":10000,"counterBucketCount":10},"circuitBreaker":{"enabled":true,"isForcedOpen":false,"isForcedClosed":false,"requestVolumeThreshold":20,"errorPercentageThreshold":50,"sleepInMilliseconds":5000}},"GetUserAccountCommand":{"threadPoolKey":"User","groupKey":"User","execution":{"isolationStrategy":"THREAD","threadPoolKeyOverride":null,"requestCacheEnabled":true,"requestLogEnabled":true,"timeoutEnabled":true,"fallbackEnabled":true,"timeoutInMilliseconds":50,"semaphoreSize":10,"fallbackSemaphoreSize":10,"threadInterruptOnTimeout":true},"metrics":{"healthBucketSizeInMs":500,"percentileBucketSizeInMilliseconds":60000,"percentileBucketCount":10,"percentileEnabled":true,"counterBucketSizeInMilliseconds":10000,"counterBucketCount":10},"circuitBreaker":{"enabled":true,"isForcedOpen":false,"isForcedClosed":false,"requestVolumeThreshold":20,"errorPercentageThreshold":50,"sleepInMilliseconds":5000}},"GetOrderCommand":{"threadPoolKey":"Order","groupKey":"Order","execution":{"isolationStrategy":"THREAD","threadPoolKeyOverride":null,"requestCacheEnabled":true,"requestLogEnabled":true,"timeoutEnabled":true,"fallbackEnabled":true,"timeoutInMilliseconds":1000,"semaphoreSize":10,"fallbackSemaphoreSize":10,"threadInterruptOnTimeout":true},"metrics":{"healthBucketSizeInMs":500,"percentileBucketSizeInMilliseconds":60000,"percentileBucketCount":10,"percentileEnabled":true,"counterBucketSizeInMilliseconds":10000,"counterBucketCount":10},"circuitBreaker":{"enabled":true,"isForcedOpen":false,"isForcedClosed":false,"requestVolumeThreshold":20,"errorPercentageThreshold":50,"sleepInMilliseconds":5000}},"GetPaymentInformationCommand":{"threadPoolKey":"PaymentInformation","groupKey":"PaymentInformation","execution":{"isolationStrategy":"THREAD","threadPoolKeyOverride":null,"requestCacheEnabled":true,"requestLogEnabled":true,"timeoutEnabled":true,"fallbackEnabled":true,"timeoutInMilliseconds":1000,"semaphoreSize":10,"fallbackSemaphoreSize":10,"threadInterruptOnTimeout":true},"metrics":{"healthBucketSizeInMs":500,"percentileBucketSizeInMilliseconds":60000,"percentileBucketCount":10,"percentileEnabled":true,"counterBucketSizeInMilliseconds":10000,"counterBucketCount":10},"circuitBreaker":{"enabled":true,"isForcedOpen":false,"isForcedClosed":false,"requestVolumeThreshold":20,"errorPercentageThreshold":50,"sleepInMilliseconds":5000}}},"threadpools":{"User":{"coreSize":8,"maxQueueSize":-1,"queueRejectionThreshold":5,"keepAliveTimeInMinutes":1,"counterBucketSizeInMilliseconds":10000,"counterBucketCount":10},"CreditCard":{"coreSize":8,"maxQueueSize":-1,"queueRejectionThreshold":5,"keepAliveTimeInMinutes":1,"counterBucketSizeInMilliseconds":10000,"counterBucketCount":10},"Order":{"coreSize":8,"maxQueueSize":-1,"queueRejectionThreshold":5,"keepAliveTimeInMinutes":1,"counterBucketSizeInMilliseconds":10000,"counterBucketCount":10},"PaymentInformation":{"coreSize":8,"maxQueueSize":-1,"queueRejectionThreshold":5,"keepAliveTimeInMinutes":1,"counterBucketSizeInMilliseconds":10000,"counterBucketCount":10}},"collapsers":{}}

**Utilization stream**

Likewise, utilization of shared resources like semaphores and threadpools is often important to reason about. 1.5.0 introduces a stream which samples utilization values. By sampling these values, you can gain insight into the utilization distribution, which should help influence configuration decisions. I'd like to eventually consider this as part of a feedback loop which can directly affect configuration, but that work has not started yet. See [#131](https://github.com/Netflix/Hystrix/issues/131)

The utilization stream is modeled at `com.netflix.hystrix.metric.sample.HystrixUtilizationStream`. It is mapped into JSON at `com.netflix.hystrix.contrib.sample.stream.HystrixUtilizationJsonStream` and embedded in an SSE servlet at `com.netflix.hystrix.contrib.sample.stream.HystrixUtilizationSseServlet`.

Here's what output of this SSE stream looks like for the [`hystrix-examples-webapp`](https://github.com/Netflix/Hystrix/tree/master/hystrix-examples-webapp) :

> data: {"type":"HystrixUtilization","commands":{"CreditCardCommand":{"activeCount":0},"GetUserAccountCommand":{"activeCount":0},"GetOrderCommand":{"activeCount":1},"GetPaymentInformationCommand":{"activeCount":0}},"threadpools":{"User":{"activeCount":0,"queueSize":0,"corePoolSize":8,"poolSize":2},"CreditCard":{"activeCount":0,"queueSize":0,"corePoolSize":8,"poolSize":1},"Order":{"activeCount":1,"queueSize":0,"corePoolSize":8,"poolSize":2},"PaymentInformation":{"activeCount":0,"queueSize":0,"corePoolSize":8,"poolSize":2}}}

**Request streams**

Scoping commands to a request is often useful for analysis purposes. It allows other request-level data to be associated to Hystrix data and analyzed together. In 1.5.0, a dedicated request stream was added. This is similar in spirit to the idea of inspecting the HystrixRequestLog-produced string at the end of every request, but modeled directly, rather than relying on string parsing.

This stream is produced by `com.netflix.hystrix.metrics.HystrixRequestEventsStream`. It has a conversion to JSON at `com.netflix.hystrix.contrib.requests.stream.HystrixRequestEventsJsonStream` and an embedding in an SSE servlet at: `com.netflix.hystrix.contrib.requests.stream.HystrixRequestEventsSseServlet`.

Here's an example output for the [`hystrix-examples-webapp`](https://github.com/Netflix/Hystrix/tree/master/hystrix-examples-webapp) :

> data: [{"name":"GetOrderCommand","events":["SUCCESS"\],"latencies":[111]},{"name":"GetPaymentInformationCommand","events":["SUCCESS"],"latencies":[15]},{"name":"GetUserAccountCommand","events":["TIMEOUT","FALLBACK_SUCCESS"],"latencies":[59],"cached":2},{"name":"CreditCardCommand","events":["SUCCESS"],"latencies":[957]}],[{"name":"GetUserAccountCommand","events":["SUCCESS"],"latencies":[3],"cached":2},{"name":"GetOrderCommand","events":["SUCCESS"],"latencies":[77]},{"name":"GetPaymentInformationCommand","events":["SUCCESS"],"latencies":[21]},{"name":"CreditCardCommand","events":["SUCCESS"],"latencies":[1199]}](https://github.com/Netflix/Hystrix/wiki/{"name"%3A"GetOrderCommand"%2C"events"%3A["SUCCESS"]%2C"latencies"%3A[111]}%2C{"name"%3A"GetPaymentInformationCommand"%2C"events"%3A["SUCCESS"]%2C"latencies"%3A[15]}%2C{"name"%3A"GetUserAccountCommand"%2C"events"%3A["TIMEOUT"%2C"FALLBACK_SUCCESS"]%2C"latencies"%3A[59]%2C"cached"%3A2}%2C{"name"%3A"CreditCardCommand"%2C"events"%3A["SUCCESS"]%2C"latencies"%3A[957]}]%2C[{"name"%3A"GetUserAccountCommand"%2C"events"%3A["SUCCESS"]%2C"latencies"%3A[3]%2C"cached"%3A2}%2C{"name"%3A"GetOrderCommand"%2C"events"%3A["SUCCESS"]%2C"latencies"%3A[77]}%2C{"name"%3A"GetPaymentInformationCommand"%2C"events"%3A["SUCCESS"]%2C"latencies"%3A[21]}%2C{"name"%3A"CreditCardCommand"%2C"events"%3A["SUCCESS"]%2C"latencies"%3A[1199]})

### 7.6 Metrics Event Stream

You can use the [`hystrix-metrics-event-stream`](https://github.com/Netflix/Hystrix/tree/master/hystrix-contrib/hystrix-metrics-event-stream) to power the [dashboard](https://github.com/Netflix/Hystrix/wiki/Dashboard), real-time alerting, and other such use cases.

### 7.7 Metrics Publisher

You can publish metrics by using an implementation of [`HystrixMetricsPublisher`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/strategy/metrics/HystrixMetricsPublisher.html).

Register your `HystrixMetricsPublisher` implementations by calling [`HystrixPlugins.registerMetricsPublisher(HystrixMetricsPublisher impl)`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/strategy/HystrixPlugins.html#registerMetricsPublisher(com.netflix.hystrix.strategy.metrics.HystrixMetricsPublisher)).

Hystrix includes the following implementations as `hystrix-contrib` modules:

- Netflix Servo: [`hystrix-servo-metrics-publisher`](https://github.com/Netflix/Hystrix/tree/master/hystrix-contrib/hystrix-servo-metrics-publisher)
- Yammer Metrics: [`hystrix-yammer-metrics-publisher`](https://github.com/Netflix/Hystrix/tree/master/hystrix-contrib/hystrix-yammer-metrics-publisher)

The following sections explain the metrics published with those implementations:

#### 7.7.1 Command Metrics

Each [`HystrixCommand`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixCommand.html) publishes metrics with the following tags:

- Servo Tag: `"instance"`, Value: `HystrixCommandKey.name()`
- Servo Tag: `"type"`, Value: `"HystrixCommand"`

Informational and Status

- *Boolean* `isCircuitBreakerOpen`
- *Number* `errorPercentage`
- *Number* `executionSemaphorePermitsInUse`
- *String* `commandGroup`
- *Number* `currentTime`

**Cumulative and Rolling Event Counts**

Cumulative counts ([`Counter`](https://github.com/Netflix/servo/blob/master/servo-core/src/main/java/com/netflix/servo/monitor/Counter.java)) represent the number of events since the start of the application.

Rolling counts ([`Gauge`](https://github.com/Netflix/servo/blob/master/servo-core/src/main/java/com/netflix/servo/monitor/Gauge.java)) are configured by [metrics.rollingStats.* properties](https://github.com/Netflix/Hystrix/wiki/Configuration). They are “point in time” counts representing the last *x* seconds (for example 10 seconds).

| Event                  | Cumulative Count (Long)   | Rolling Count (Number)           |
| ---------------------- | ------------------------- | -------------------------------- |
| `BAD_REQUEST`          | `countBadRequests`        | `rollingCountBadRequests`        |
| `COLLAPSED`            | `countCollapsedRequests`  | `rollingCountCollapsedRequests`  |
| `EMIT`                 | `countEmit`               | `rollingCountEmit`               |
| `EXCEPTION_THROWN`     | `countExceptionsThrown`   | `rollingCountExceptionsThrown`   |
| `FAILURE`              | `countFailure`            | `rollingCountFailure`            |
| `FALLBACK_EMIT`        | `countFallbackEmit`       | `rollingCountFallbackEmit`       |
| `FALLBACK_FAILURE`     | `countFallbackFailure`    | `rollingCountFallbackFailure`    |
| `FALLBACK_REJECTION`   | `countFallbackRejection`  | `rollingCountFallbackRejection`  |
| `FALLBACK_SUCCESS`     | `countFallbackSuccess`    | `rollingCountFallbackSuccess`    |
| `RESPONSE_FROM_CACHE`  | `countResponsesFromCache` | `rollingCountResponsesFromCache` |
| `SEMAPHORE_REJECTED`   | `countSemaphoreRejected`  | `rollingCountSemaphoreRejected`  |
| `SHORT_CIRCUITED`      | `countShortCircuited`     | `rollingCountShortCircuited`     |
| `SUCCESS`              | `countSuccess`            | `rollingCountSuccess`            |
| `THREAD_POOL_REJECTED` | `countThreadPoolRejected` | `rollingCountThreadPoolRejected` |
| `TIMEOUT`              | `countTimeout`            | `rollingCountTimeout`            |

**Latency Percentiles: `HystrixCommand.run()` Execution ([Gauge](https://github.com/Netflix/servo/blob/master/servo-core/src/main/java/com/netflix/servo/monitor/Gauge.java))**

These metrics represent percentiles of execution times for the [`HystrixCommand.run()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommand.html#run()) method (on the child thread if using thread isolation).

These are rolling percentiles as configured by [metrics.rollingPercentile.* properties](https://github.com/Netflix/Hystrix/wiki/Configuration).

- *Number* `latencyExecute_mean`
- *Number* `latencyExecute_percentile_5`
- *Number* `latencyExecute_percentile_25`
- *Number* `latencyExecute_percentile_50`
- *Number* `latencyExecute_percentile_75`
- *Number* `latencyExecute_percentile_90`
- *Number* `latencyExecute_percentile_99`
- *Number* `latencyExecute_percentile_995`

**Latency Percentiles: End-to-End Execution ([Gauge](https://github.com/Netflix/servo/blob/master/servo-core/src/main/java/com/netflix/servo/monitor/Gauge.java))**

These metrics represent percentiles of execution times for the end-to-end execution of [`HystrixCommand.execute()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommand.html#execute()) or [`HystrixCommand.queue()`](http://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/HystrixCommand.html#queue()) until a response is returned (or is ready to return in case of `queue()`).

The purpose of this compared with the `latencyExecute*` percentiles is to measure the cost of thread queuing/scheduling/execution, semaphores, circuit breaker logic, and other aspects of overhead (including metrics capture itself).

These are rolling percentiles as configured by [metrics.rollingPercentile.* properties](https://github.com/Netflix/Hystrix/wiki/Configuration).

- *Number* `latencyTotal_mean`
- *Number* `latencyTotal_percentile_5`
- *Number* `latencyTotal_percentile_25`
- *Number* `latencyTotal_percentile_50`
- *Number* `latencyTotal_percentile_75`
- *Number* `latencyTotal_percentile_90`
- *Number* `latencyTotal_percentile_99`
- *Number* `latencyTotal_percentile_995`

**Property Values ([Informational](https://github.com/Netflix/servo/blob/master/servo-core/src/main/java/com/netflix/servo/monitor/Informational.java))**

These informational metrics report the actual property values being used by the `HystrixCommand`. This enables you to see when a dynamic property takes effect and to confirm a property is set as expected.

- *Number* `propertyValue_rollingStatisticalWindowInMilliseconds`
- *Number* `propertyValue_circuitBreakerRequestVolumeThreshold`
- *Number* `propertyValue_circuitBreakerSleepWindowInMilliseconds`
- *Number* `propertyValue_circuitBreakerErrorThresholdPercentage`
- *Boolean* `propertyValue_circuitBreakerForceOpen`
- *Boolean* `propertyValue_circuitBreakerForceClosed`
- *Number* `propertyValue_executionIsolationThreadTimeoutInMilliseconds`
- *String* `propertyValue_executionIsolationStrategy`
- *Boolean* `propertyValue_metricsRollingPercentileEnabled`
- *Boolean* `propertyValue_requestCacheEnabled`
- *Boolean* `propertyValue_requestLogEnabled`
- *Number* `propertyValue_executionIsolationSemaphoreMaxConcurrentRequests`
- *Number* `propertyValue_fallbackIsolationSemaphoreMaxConcurrentRequests`

#### 7.7.2 ThreadPool Metrics

Each [`HystrixThreadPool`](http://netflix.github.io/Hystrix/javadoc/index.html?com/netflix/hystrix/HystrixThreadPool.html) publishes metrics with the following tags:

- Servo Tag: `"instance"`, Value: `HystrixThreadPoolKey.name()`
- Servo Tag: `"type"`, Value: `"HystrixThreadPool"`

**Informational and Status**

- *String* `name`
- *Number* `currentTime`

**Rolling Counts ([Gauge](https://github.com/Netflix/servo/blob/master/servo-core/src/main/java/com/netflix/servo/monitor/Gauge.java))**

- *Number* `rollingMaxActiveThreads`
- *Number* `rollingCountThreadsExecuted`

**Cumulative Counts ([Counter](https://github.com/Netflix/servo/blob/master/servo-core/src/main/java/com/netflix/servo/monitor/Counter.java))**

- *Long* `countThreadsExecuted`

**ThreadPool State ([Gauge](https://github.com/Netflix/servo/blob/master/servo-core/src/main/java/com/netflix/servo/monitor/Gauge.java))**

- *Number* `threadActiveCount`
- *Number* `completedTaskCount`
- *Number* `largestPoolSize`
- *Number* `totalTaskCount`
- *Number* `queueSize`

**Property Values ([Informational](https://github.com/Netflix/servo/blob/master/servo-core/src/main/java/com/netflix/servo/monitor/Informational.java))**

- *Number* `propertyValue_corePoolSize`
- *Number* `propertyValue_keepAliveTimeInMinutes`
- *Number* `propertyValue_queueSizeRejectionThreshold`
- *Number* `propertyValue_maxQueueSize`

## 八、Plugins



