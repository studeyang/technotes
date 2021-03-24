# 服务容错

# 12 | 服务容错：服务容错的思想和模式

今天的内容关注服务容错的设计理念和与其相关的架构模式。

**为什么要实现服务容错？**

当访问服务 A 得不到正常的响应时，服务 B 的常见处理方式是通过重试机制来进一步加大对服务 A 的访问流量。这样，服务 B 每进行一次重试就会启动一批线程。

线程的不断创建是需要消耗系统资源的，一旦系统资源被耗尽，服务 B 本身也将变得不可用，这就是事故的第二个阶段：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210309225911.png" alt="image-20210309225911832" style="zoom:50%;" />

类似的，如果系统中存在服务 C 等其他服务依赖服务 B......以此类推，最终在以服务 A 为起点的整个调用链路上的所有服务都会变得不可用。这种扩散效应就是所谓的服务雪崩效应。

**服务容错的模式**

消费者容错的常见实现模式包括集群容错、服务隔离、服务熔断和服务回退。

1. 集群容错

从设计思想上讲，容错机制的基本要素就是要做到冗余，即某一个服务应该构建多个实例，这样当一个服务实例出现问题时可以重试其他实例。

一个集群中的服务本身就是冗余的。而针对不同的重试方式就诞生了一批集群容错策略，常见的包括 Failover（失效转移）、Failback（失败通知）、Failsafe（失败安全）和 Failfast（快速失败）等。

失效转移指当服务调用发生异常时，请求会重新在集群中查找下一个可用的服务提供者实例。但为了防止无限重试，通常会对失败重试最大次数进行限制。

2. 服务隔离

所谓隔离，就是指对资源进行有效的管理，从而避免因为资源不可用、发生失败等情况导致系统中的其他资源也变得不可用。

日常开发过程中，主要还是使用线程级别的隔离。简单而主流的做法是使用线程池（Thread Pool）。针对不同的业务场景设计不同的线程池。

这样当某个线程池因为业务异常导致资源消耗时，不会将这种资源消耗扩散到其他线程池，从而保证其他服务持续可用。

3. 服务熔断

当系统中出现某一个异常情况时，能够直接熔断整个服务的请求处理过程。这样可以避免一直等到请求处理完毕或超时，从而避免浪费。

从设计理念上讲，服务熔断也是快速失败的一种具体表现。服务熔断器的基本结构，如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210309225026.png" alt="image-20210309225020619" style="zoom:50%;" />

4. 服务回退

服务回退（Fallback）的概念类似一种被动的、临时的处理机制。当远程调用发生异常时，服务回退并不是直接抛出异常，而是产生一个另外的处理机制来应对该异常。

服务回退不能解决由异常引起的实际问题，而是一种权宜之计。这种权宜之计在处理因为服务依赖而导致的异常时也是一种有效的容错机制。

**Spring Cloud 中的服务容错解决方案**

Spring Cloud 中专门用于提供服务容错功能的 Spring Cloud Circuit Breaker 框架，内置了四种熔断器：

- Netflix Hystrix
- Resilience4J
- Sentinel
- Spring Retry

针对以上四种熔断器，Spring Cloud Circuit Breaker 提供了统一的 API。

其中 Netflix Hystrix 显然来自 Netflix OSS；Resilience4j 是受 Hystrix 项目启发所诞生的一款新型的容错库；Sentinel 从定位上讲是一款包含了熔断降级功能的高可用流量防护组件；而最后的 Spring Retry 是 Spring 自研的重试和熔断框架。

# 13 | 熔断之器：如何使用 Spring Cloud Circuit Breaker 实现服务容错？（上）

Spring Cloud Circuit Breaker 是一个集成性的框架，内部整合了 Netflix Hystrix、Resilience4j、Sentinel 和 Spring Retry 这四款独立的熔断器组件。

我们先来讨论 Netflix Hystrix。

**引入 Hystrix**

添加依赖：

```xml
<dependency>
  <groupId>org.springframework.cloud</groupId>
  <artifactId>spring-cloud-starter-netflix-hystrix</artifactId>
</dependency>
```

定义 Bootstrap 类：

```java
@SpringCloudApplication
public class InterventionApplication {
}
```

@SpringCloudApplication 是一个组合注解，整合了 @SpringBootApplication、@EnableDiscoveryClient 和 @EnableCircuitBreaker 这三个注解。

**使用 Hystrix 实现服务隔离**

我们可以提供一个 HystrixCommand 类的子类来实现服务隔离。我们基于最常用的线程池隔离来进行介绍。典型的 HystrixCommand 子类代码风格如下所示：

```java
public class GetUserCommand extends HystrixCommand<UserMapper> {

    //远程调用 user-service 的客户端工具类
    private UserServiceClient userServiceClient;
 
    protected GetUserCommand(String name) {
        super(
            //设置命令组
            Setter.withGroupKey(HystrixCommandGroupKey.Factory.asKey("springHealthGroup"))
            //设置命令键
            .andCommandKey(HystrixCommandKey.Factory.asKey("interventionKey"))
            //设置线程池键
            .andThreadPoolKey(HystrixThreadPoolKey.Factory.asKey(name))
            //设置命令属性
            .andCommandPropertiesDefaults(
                    HystrixCommandProperties.Setter()
                        .withExecutionTimeoutInMilliseconds(5000))
            //设置线程池属性
            .andThreadPoolPropertiesDefaults(
                    HystrixThreadPoolProperties.Setter()
                        .withMaxQueueSize(10)
                        .withCoreSize(2))
        );
    }
    @Override
    protected UserMapper run() throws Exception {
        return userServiceClient.getUserByUserName("springhealth_user1");
    }
 
    @Override
    protected UserMapper getFallback() {
        return new UserMapper(1L, "user1", "springhealth_user1");
    }
}
```

在日常开发过程中，一般不建议你通过创建一个 HystrixCommand 子类的方式来实现服务隔离，而是推荐你使用更为简单的 @HystrixCommand 注解。@HystrixCommand 是 Hystrix 为简化开发过程而专门提供的一个注解，定义如下：

```java
public @interface HystrixCommand {
    String groupKey() default "";
    String commandKey() default "";
    String threadPoolKey() default "";
    String fallbackMethod() default "";
    HystrixProperty[] commandProperties() default {};
    HystrixProperty[] threadPoolProperties() default {};
    Class<? extends Throwable>[] ignoreExceptions() default {};
    ObservableExecutionMode observableExecutionMode() default ObservableExecutionMode.EAGER;
    HystrixException[] raiseHystrixExceptions() default {};
    String defaultFallback() default "";
}
```

我们回到案例，并使用 @HystrixCommand 注解进行重构，效果如下：

```java
@HystrixCommand(threadPoolKey = "springHealthGroup",
    threadPoolProperties =
     {
         @HystrixProperty(name="coreSize",value="2"),
         @HystrixProperty(name="maxQueueSize",value="10")
     }
)
private UserMapper getUser(String userName) {
    return userClient.getUserByUserName(userName);
}
```

**使用 Hystrix 实现服务熔断**

在 SpringHealth 案例中，我们知道 intervention-service 需要调用 user-service 和 device-service 来生成健康干预记录，该操作调用的代码如下所示：

```java
@Autowired
private UserServiceClient userClient;
 
@Autowired
private DeviceServiceClient deviceClient;
 
@HystrixCommand
private UserMapper getUser(String userName) {
    return userClient.getUserByUserName(userName);
}
 
@HystrixCommand
private DeviceMapper getDevice(String deviceCode) {
    return deviceClient.getDevice(deviceCode);
}
```

Hystrix 还提供了一系列的配置项来细化对熔断器的控制。常见的配置项如下所示：

```java
@HystrixCommand(commandProperties = {
            //超时时间
            @HystrixProperty(name = "execution.isolation.thread.timeoutInMilliseconds", value = "12000"),
            //一个滑动窗口内最小的请求数
            @HystrixProperty(name = "circuitBreaker.requestVolumeThreshold", value = "10"),
            //错误比率阈值
            @HystrixProperty(name = "circuitBreaker.errorThresholdPercentage", value = "75"),
            //触发熔断的时间值
            @HystrixProperty(name = "circuitBreaker.sleepWindowInMilliseconds", value = "7000"),
            //一个滑动窗口的时间长度
            @HystrixProperty(name = "metrics.rollingStats.timeInMilliseconds", value = "15000"),
            //一个滑动窗口被划分的数量
            @HystrixProperty(name = "metrics.rollingStats.numBuckets", value = "5") })
```

**使用 Hystrix 实现服务回退**

Hystrix 在服务调用失败时都可以执行服务回退逻辑。在开发过程上，我们只需要提供一个 Fallback 方法实现并进行配置即可。

如下所示的就是 Fallback 方法的一个示例：

```java
private UserMapper getUserFallback(String userName) {
    UserMapper fallbackUser = new UserMapper(0L,"no_user","not_existed_user");
    return fallbackUser;
}
```

我们通过构建一个不存在的 User 信息来返回 Fallback 结果。有了这个 Fallback 方法，剩下来要做的就是在 @HystrixCommand 注解中设置“fallbackMethod”配置项。重构后的 getUser 方法如下所示：

```java
@HystrixCommand(threadPoolKey = "springHealthGroup",
    threadPoolProperties =
        {
            @HystrixProperty(name="coreSize", value="2"),
            @HystrixProperty(name="maxQueueSize", value="10")
        },
    fallbackMethod = "getUserFallback")
private UserMapper getUser(String userName) {
    return userClient.getUserByUserName(userName);
}
```

# 14 | 熔断之器：如何使用 Spring Cloud Circuit Breaker 实现服务容错？（下）

**理解 Spring Cloud Circuit Breaker 中的熔断器抽象**

Spring Cloud Circuit Breaker 是对熔断器抽象，内部集成了多款不同的熔断器实现工具，并基于这些工具提取了统一的 API 供应用程序进行调用。

为了在应用程序中创建一个熔断器，我们可以使用 Spring Cloud Circuit Breaker 中的工厂类 CircuitBreakerFactory，该工厂类的定义如下所示：

```java
public abstract class CircuitBreakerFactory<CONF, CONFB extends ConfigBuilder<CONF>> extends AbstractCircuitBreakerFactory<CONF, CONFB> {
    public abstract CircuitBreaker create(String id);
}
```

CircuitBreaker 是一个接口，约定了熔断器应该具有的功能，该接口定义如下所示：

```java
public interface CircuitBreaker {
    default <T> T run(Supplier<T> toRun) {
        return run(toRun, throwable -> {
            throw new NoFallbackAvailableException("No fallback available.", throwable);
        });
    };
    <T> T run(Supplier<T> toRun, Function<Throwable, T> fallback);
}
```

Supplier 包含了你希望运行在熔断器中的业务代码，而 Function 则代表着回退方法。

使用 Resilience4j 步骤如下，首先引入 Maven 依赖：

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-circuitbreaker-resilience4j</artifactId>
</dependency>
```

一旦在代码工程的类路径中添加了 starter，系统就会自动创建 CircuitBreaker。

在引入具体的开发框架之后，下一步工作就是对它们进行配置。在 CircuitBreakerFactory 的父类 AbstractCircuitBreakerFactory 中，我们发现了如下两个抽象方法：

```java
//针对某一个 id 创建配置构造器
protected abstract CONFB configBuilder(String id);
 
//为熔断器配置默认属性
public abstract void configureDefault(Function<String, CONF> defaultConfiguration);
```

在这两个抽象方法的背后，Spring Cloud Circuit Breaker 会针对不同的第三方框架提供不同的配置实现过程。

**使用 Spring Cloud Circuit Breaker 集成 Hystrix**

1. 理解 HystrixCircuitBreakerFactory 和 HystrixCircuitBreaker

HystrixCircuitBreaker 类，如下所示：

```java
public class HystrixCircuitBreaker implements CircuitBreaker {
    private HystrixCommand.Setter setter;
  
    public HystrixCircuitBreaker(HystrixCommand.Setter setter) {
        this.setter = setter;
    }
  
    @Override
    public <T> T run(Supplier<T> toRun, Function<Throwable, T> fallback) {
        HystrixCommand<T> command = new HystrixCommand<T>(setter) {
            @Override
            protected T run() throws Exception {
                return toRun.get();
            }

            @Override
            protected T getFallback() {
                return fallback.apply(getExecutionException());
            }
        };
        return command.execute();
    }
}
```

最终实现熔断操作的还是 Hystrix 原生的 HystrixCommand。

我们接着来看 HystrixCircuitBreakerFactory，如下所示：

```java
public class HystrixCircuitBreakerFactory extends
        CircuitBreakerFactory<HystrixCommand.Setter, HystrixCircuitBreakerFactory.HystrixConfigBuilder> {
 
    //实现默认配置
    private Function<String, HystrixCommand.Setter> defaultConfiguration = id -> HystrixCommand.Setter
            .withGroupKey(
                    HystrixCommandGroupKey.Factory.asKey(getClass().getSimpleName()))
            .andCommandKey(HystrixCommandKey.Factory.asKey(id));
 
    public void configureDefault(
            Function<String, HystrixCommand.Setter> defaultConfiguration) {
        this.defaultConfiguration = defaultConfiguration;
    }
 
    public HystrixConfigBuilder configBuilder(String id) {
        return new HystrixConfigBuilder(id);
    }
 
    //创建熔断器
    public HystrixCircuitBreaker create(String id) {
        Assert.hasText(id, "A CircuitBreaker must have an id.");
        HystrixCommand.Setter setter = getConfigurations().computeIfAbsent(id,
                defaultConfiguration);
        return new HystrixCircuitBreaker(setter);
    }
 
    //
    public static class HystrixConfigBuilder
            extends AbstractHystrixConfigBuilder<HystrixCommand.Setter> {
 
        public HystrixConfigBuilder(String id) {
            super(id);
        }
 
        @Override
        public HystrixCommand.Setter build() {
            return HystrixCommand.Setter.withGroupKey(getGroupKey())
                    .andCommandKey(getCommandKey())
                    .andCommandPropertiesDefaults(getCommandPropertiesSetter());
        } 
    }
}
```

上述代码基本就是对原有 HystrixCommand 中关于服务分组等属性的简单封装。

2. 使用 HystrixCircuitBreakerFactory 设置默认属性

在应用程序中为熔断器创建默认配置，我们可以使用 Spring Cloud Circuit Breaker 提供的 Customizer工具类。

```java
Bean
public Customizer<HystrixCircuitBreakerFactory> defaultConfig() {
    return factory -> factory.configureDefault(id -> HystrixCommand.Setter
            .withGroupKey(HystrixCommandGroupKey.Factory.asKey(id))
            .andCommandPropertiesDefaults(
                HystrixCommandProperties.Setter().withExecutionTimeoutInMilliseconds(3000))
            );
}
```

这里通过 HystrixCommandProperties 的 withExecutionTimeoutInMilliseconds 方法将默认超时时间设置为 3000 毫秒。

3. 使用 Hystrix 实现服务熔断

首先，我们需要通过 HystrixCircuitBreakerFactory 创建一个runCircuitBreaker 实例，然后实现具体的业务逻辑并提供一个回退函数，最后执行 CircuitBreaker 的 run 方法。示例代码如下：

```java
//创建 CircuitBreaker
CircuitBreaker hystrixCircuitBreaker = circuitBreakerFactory.create("springhealth");

//封装业务逻辑
Supplier<UserMapper> supplier = () -> {
    return userClient.getUserByUserName(userName);
};
 
//初始化回退函数
Function<Throwable, UserMapper> fallback = t -> {
    UserMapper fallbackUser = new UserMapper(0L,"no_user","not_existed_user");

    return fallbackUser;
};

//执行业务逻辑
hystrixCircuitBreaker.run(supplier, fallback);
```

**使用 Spring Cloud Circuit Breaker 集成 Resilience4j**

1. Resilience4j 基础

我们先来看一下 Resilience4j 中定义的几个核心组件。

当使用 Resilience4j 时，同样需要对熔断器进行配置。而这样配置信息同样分为两部分，一部分是默认配置，一部分是专属于某一个服务的特定配置。典型的 Resilience4j 配置项如下所示：

```yaml
resilience4j:
  circuitbreaker:
    configs:
      default:
        ringBufferSizeInClosedState: 5 # 熔断器关闭时的缓冲区大小
        ringBufferSizeInHalfOpenState: 2 # 熔断器半开时的缓冲区大小
        waitDurationInOpenState: 10000 # 熔断器从打开到半开需要的时间
        failureRateThreshold: 60 # 熔断器打开的失败阈值
        eventConsumerBufferSize: 10 # 事件缓冲区大小
        recordExceptions: # 记录的异常
          - com.example.resilience4j.exceptions.BusinessBException
          - com.example.resilience4j.exceptions.BusinessAException
        ignoreExceptions: # 忽略的异常
          - com.example.resilience4j.exceptions.BusinessAException
    instances:
      userCircuitBreaker:
        baseConfig: default
      deviceCircuitBreaker:
        baseConfig: default
        waitDurationInOpenState: 5000
        failureRateThreshold: 20
```

在上述配置项中，我们初始化了两个服务级的 Circuit Breaker 实例 userCircuitBreaker 和 deviceCircuitBreaker，分别作用于 user-service 和 device-service。其中，userCircuitBreaker 完全使用的是默认配置，而 deviceCircuitBreaker 对 waitDurationInOpenState 和 failureRateThreshold 这两个配置项做了覆盖。

在 Resilience4j 中，存在一个熔断器注册器 CircuitBreakerRegistry。上述配置项会帮我们把 userCircuitBreaker 和 deviceCircuitBreaker 自动注册到这个 CircuitBreakerRegistry 中。而在应用程序中，通过指定熔断器名称就可以从 CircuitBreakerRegistry 中获取熔断器，如下所示：

```java
CircuitBreaker circuitBreaker = circuitBreakerRegistry.circuitBreaker("userCircuitBreaker");
```

一旦获取了 CircuitBreaker 对象，接下来就是通过该对象所提供的 executeSupplier 方法或 executeCheckedSupplier 方法来执行业务代码，如下所示：

```java
circuitBreaker.executeCheckedSupplier(userClient::getUser);
```

如果需要对业务代码执行回退，在 Resilience4j 中的实现过程会相对复杂一点。我们需要使用包装器方法 decorateCheckedSupplier，然后再使用 Try.of().recover() 方法进行降级处理，代码示例如下所示：

```java
CircuitBreaker circuitBreaker = circuitBreakerRegistry.circuitBreaker("userCircuitBreaker");
 
CheckedFunction0<UserMapper> checkedSupplier = CircuitBreaker.
decorateCheckedSupplier(circuitBreaker, userClient::getUser);
 
Try<UserMapper> result = Try.of(checkedSupplier).
.recover(throwable -> {
    UserMapper fallbackUser = new UserMapper(0L,"no_user","not_existed_user");
    return fallbackUser;
});
return result.get();
```

至此我们演示了基于 Java 代码的方式来使用 Resilience4j，但 Resilience4j 也提供了 @CircuitBreaker 注解。该注解类似 Hystrix 中的 @HystrixCommand 注解。使用方式上也比较类似，一般只需要指定熔断器的名称以及回退方法即可，如下所示：

```java
@CircuitBreaker(name = "userCircuitBreaker", fallbackMethod = "getUserFallback")
```

2. 使用 Resilience4j 实现服务熔断

首先，我们同样需要构建一个 Customizer 实例，来初始化对 Resilience4j 的配置，如下所示：

```java
@Bean
public Customizer<Resilience4JCircuitBreakerFactory> defaultCustomizer() {
        return factory -> factory.configureDefault(id -> new Resilience4JConfigBuilder(id)
                .circuitBreakerConfig(CircuitBreakerConfig.ofDefaults())
                .build());
}
```

**服务容错集成 API 网关**

Netflix Zuul 和 Spring Cloud Gateway 这两款 API 网关实现工具，都可以完成与 Hystrix 的无缝集成。

事实上，Hystrix 集成 API 网关唯一所要做的事情就是在网关的配置文件中添加与 Hystrix 相关的配置项即可。这里以常见的设置服务访问超时时间的场景为例：

```yaml
hystrix:
  command:
    default:
      execution:
        isolation:
          thread:
	          timeoutInMilliseconds: 5000
```

上述配置信息的效果就是覆写 Hystrix 的默认超时时间为 5000 毫秒。请注意，以上配置项对经由 API 网关中的所有服务均生效。如果我们想要设置具体某一个服务（例如 userservice）的 Hystrix 超时时间，把“hystrix.command.default”段改为“hystrix.command.userservice”即可。

# 15 | 熔断原理：Hystrix Circuit Breaker 的底层实现机制

**Hystrix Circuit Breaker**

使用 Hystrix 熔断器的最简单方法就是在 Spring Boot 应用程序中添加 @EnableCircuitBreaker 注解。让我们先来分析一下这个注解背后的实现原理。

1. @EnableCircuitBreaker 注解

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@Import(EnableCircuitBreakerImportSelector.class)
public @interface EnableCircuitBreaker { 
}
```

 EnableCircuitBreakerImportSelector 类定义如下：

```java
public class EnableCircuitBreakerImportSelector extends SpringFactoryImportSelector<EnableCircuitBreaker> {
    @Override
    protected boolean isEnabled() {
        return getEnvironment().getProperty(
          "spring.cloud.circuit.breaker.enabled", Boolean.class, Boolean.TRUE);
    }
}
```

EnableCircuitBreakerImportSelector 类会加载 spring.factories 中标明为 EnableCircuitBreaker 的配置类，如下所示：

```properties
org.springframework.cloud.client.circuitbreaker.EnableCircuitBreaker=\
	org.springframework.cloud.netflix.hystrix.HystrixCircuitBreakerConfiguration
```

HystrixCircuitBreakerConfiguration 配置类内部构造了一个切面：

```java
@Pointcut("@annotation(com.netflix.hystrix.contrib.javanica.annotation.HystrixCommand)")
public void hystrixCommandAnnotationPointcut() {
}

@Pointcut("@annotation(com.netflix.hystrix.contrib.javanica.annotation.HystrixCollapser)")
public void hystrixCollapserAnnotationPointcut() {
}

@Around("hystrixCommandAnnotationPointcut() || hystrixCollapserAnnotationPointcut()")
public Object methodsAnnotatedWithHystrixCommand(final ProceedingJoinPoint joinPoint) throws Throwable {
}
```

2. HystrixCircuitBreaker 实现原理

HystrixCircuitBreaker 接口定义如下所示：

```java
public interface HystrixCircuitBreaker {
  //请求是否可被执行
  public boolean allowRequest(); 
  //返回当前熔断器是否打开
  public boolean isOpen(); 
  //关闭熔断器
  void markSuccess();
}
```

**Hystrix 滑动窗口机制**

1. 滑动窗口和数据流处理

通常，我们想要对一些数据做分析和统计时，会首先采集一定的样本，然后进行一定的分组。在采集策略上可以使用时间维度或数量维度。

滑动窗口显然属于时间维度的采集方式，即采集过程基于一定的时间窗口，而这个时间窗口随着时间的演进而逐步向前滑动。

在 Hystrix 中，采用滑动窗口来采集的系统运行时健康数据包括成功请求数量、失败请求数、超时请求数、被拒绝的请求数等。然后每次取最近 10 秒的数据来进行计算，如果这 10 秒中请求的失败率计算下来超过了 50%，就会触发熔断器的熔断机制。这里的 10 秒就是一个滑动窗口，参考其官网的一幅图：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210315221231.png" alt="image-20210315221231343" style="zoom:50%;" />

那么如何来实现这个滑动窗口呢？

2. 响应式编程和 RxJava 基础

在响应式编程中，我们把源源不断的事件看成是一个流（Stream）。RxJava 中用于健康信息采集的操作符包括 window、flatMap 和 reduce 等。

- window 操作符。

  window 操作符用于开窗操作，也就是把当前流中的元素采集并合并到另外的流中，该操作符示意图如下图所示：

  <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210315221604.png" alt="image-20210315221604543" style="zoom:50%;" />

- flatMap 操作符。

  flatMap 操作符把输入流中的每个元素转换成另一个流，再把这些转换之后得到的流元素进行合并。flapMap 操作符示意图如下图所示：

  <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210315221825.png" alt="image-20210315221825625" style="zoom:50%;" />

- reduce 操作符。

  reduce 操作符对流中包含的所有元素进行累积计算，该操作符示意图见下图所示：

  <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210315221922.png" alt="image-20210315221922324" style="zoom:50%;" />

3. HealthCountsStream

HealthCountsStream 类的类层结构，如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210315222144.png" alt="image-20210315222144458" style="zoom: 50%;" />

****

# 配置中心

# 16 | 配置方案：分布式环境下的配置中心解决方案

**配置中心基本模型**

在一个微服务系统中，势必存在多个服务，而这些服务一般都会存在开发环境、测试环境、预发布环境、生产环境等多套环境。

那么如何保证多个环境中这些配置信息都能在各个服务实例中进行实时的同步更新呢？这就需要引入集中式配置管理的设计思想，如下图所示：

![image-20210315223004012](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210315223004.png)

**Spring Boot 中的配置体系**

在 Spring Boot 中，对配置文件的命名是有一定规范的，引入了 Label 和 Profile 概念指定配置信息的版本以及运行环境。其中 Label 表示配置版本控制信息，而 Profile 则用来指定该配置文件所对应的环境。

Spring Boot 中配置文件的格式有两种，分别是 .properties 格式和 .yml 格式。

```tex
/{application}.yml
/{application}-{profile}.yml
/{label}/{application}-{profile}.yml
/{application}-{profile}.properties
/{label}/{application}-{profile}.properties
```

如何指定当前使用具体哪一套配置信息呢？

在 Spring Boot 中，我们可以在主 application.properties 中使用如下的配置方式来激活当前所使用的 Profile：

```properties
spring.profiles.active = test
```

我们也可以同时激活几个 Profile。

```yaml
spring.profiles.active: test, myprofile1, myprofile2
```



