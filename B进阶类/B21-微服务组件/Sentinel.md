> 来自：https://sentinelguard.io/zh-cn/docs/introduction.html
>
> Demo: https://github.com/alibaba/Sentinel/tree/master/sentinel-demo

# 一、基本原理

## 1.1 Sentinel 工作主流程

在 Sentinel 里面，所有的资源都对应一个资源名称以及一个 Entry。每一个 Entry 创建的时候，同时也会创建一系列功能插槽（slot chain）。这些插槽有不同的职责。

总体的框架如下:

![image-20250306230600969](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503062306013.png)

**1、NodeSelectorSlot**

负责收集资源的路径，并将这些资源的调用路径，以树状结构存储起来，用于根据调用路径来限流降级；

```java
  ContextUtil.enter("entrance1", "appA");
  Entry nodeA = SphU.entry("nodeA");
  if (nodeA != null) {
    nodeA.exit();
  }
  ContextUtil.exit();

  ContextUtil.enter("entrance2", "appA");
  nodeA = SphU.entry("nodeA");
  if (nodeA != null) {
    nodeA.exit();
  }
  ContextUtil.exit();
```

以上代码将在内存中生成以下结构：

```
                   machine-root
                   /         \
                  /           \
          EntranceNode1   EntranceNode2
                /               \
               /                 \
       DefaultNode(nodeA)   DefaultNode(nodeA)
```

上面的结构可以通过调用 `curl http://localhost:8719/tree?type=root` 来显示：

```
EntranceNode: machine-root(t:0 pq:1 bq:0 tq:1 rt:0 prq:1 1mp:0 1mb:0 1mt:0)
-EntranceNode1: Entrance1(t:0 pq:1 bq:0 tq:1 rt:0 prq:1 1mp:0 1mb:0 1mt:0)
--nodeA(t:0 pq:1 bq:0 tq:1 rt:0 prq:1 1mp:0 1mb:0 1mt:0)
-EntranceNode2: Entrance1(t:0 pq:1 bq:0 tq:1 rt:0 prq:1 1mp:0 1mb:0 1mt:0)
--nodeA(t:0 pq:1 bq:0 tq:1 rt:0 prq:1 1mp:0 1mb:0 1mt:0)

t:threadNum  pq:passQps  bq:blockedQps  tq:totalQps  rt:averageRt  prq: passRequestQps 1mp:1m-passed 1mb:1m-blocked 1mt:1m-total
```

**2、ClusterBuilderSlot**

用于存储资源的统计信息以及调用者信息，例如该资源的 RT, QPS, thread count 等等，这些信息将用作为多维度限流，降级的依据；

来源调用者的名字由 `ContextUtil.enter(contextName，origin)` 中的 `origin` 标记。可通过如下命令查看某个资源不同调用者的访问情况：`curl http://localhost:8719/origin?id=caller`：

```
id: nodeA
idx origin  threadNum passedQps blockedQps totalQps aRt   1m-passed 1m-blocked 1m-total 
1   caller1 0         0         0          0        0     0         0          0        
2   caller2 0         0         0          0        0     0         0          0        
```

**3、StatisticSlot**

用于记录、统计不同纬度的 runtime 指标监控信息；

**4、FlowSlot**

`FlowSlot` 则用于根据预设的限流规则以及前面 slot 统计的状态，来进行流量控制；

**5、AuthoritySlot**

根据配置的黑白名单和调用来源信息，来做黑白名单控制；

**6、DegradeSlot**

通过统计信息以及预设的规则，来做熔断降级；

**7、SystemSlot**

通过系统的状态，例如 load1 等，来控制总的入口流量；

# 二、使用文档

## 2.1 基本使用 - 资源与规则



## 2.2 流量控制



## 2.3 熔断降级

**熔断器事件监听**

Sentinel 支持注册自定义的事件监听器监听熔断器状态变换事件（state change event）。示例：

```java
EventObserverRegistry.getInstance().addStateChangeObserver("logging",
    (prevState, newState, rule, snapshotValue) -> {
        if (newState == State.OPEN) {
            // 变换至 OPEN state 时会携带触发时的值
            System.err.println(String.format("%s -> OPEN at %d, snapshotValue=%.2f", prevState.name(),
                TimeUtil.currentTimeMillis(), snapshotValue));
        } else {
            System.err.println(String.format("%s -> %s at %d", prevState.name(), newState.name(),
                TimeUtil.currentTimeMillis()));
        }
    });
```

## 2.4 网关流量控制



## 2.5 注解埋点支持

Sentinel 提供了 `@SentinelResource` 注解用于定义资源，并提供了 AspectJ 的扩展用于自动定义资源、处理 `BlockException` 等。使用 [Sentinel Annotation AspectJ Extension](https://github.com/alibaba/Sentinel/tree/master/sentinel-extension/sentinel-annotation-aspectj) 的时候需要引入以下依赖：

```xml
<dependency>
    <groupId>com.alibaba.csp</groupId>
    <artifactId>sentinel-annotation-aspectj</artifactId>
    <version>x.y.z</version>
</dependency>
```

**@SentinelResource 注解**

> 注意：注解方式埋点不支持 private 方法。

`@SentinelResource` 用于定义资源，并提供可选的异常处理和 fallback 配置项。 包含以下属性：

- `value`：资源名称，必需项（不能为空）
- `entryType`：entry 类型，可选项（默认为 `EntryType.OUT`）
- `blockHandler` / `blockHandlerClass`: `blockHandler` 对应处理 `BlockException` 的函数名称，可选项。
- `fallback`：fallback 函数名称，可选项，用于在抛出异常的时候提供 fallback 处理逻辑。
- `defaultFallback`:（since 1.6.0）：默认的 fallback 函数名称，可选项，通常用于通用的 fallback 逻辑（即可以用于很多服务或方法）。
- `exceptionsToIgnore`（since 1.6.0）：用于指定哪些异常被排除掉，不会计入异常统计中，也不会进入 fallback 逻辑中，而是会原样抛出。

示例：

```java
public class TestService {

    // 对应的 `handleException` 函数需要位于 `ExceptionUtil` 类中，并且必须为 static 函数.
    @SentinelResource(value = "test", blockHandler = "handleException", blockHandlerClass = {ExceptionUtil.class})
    public void test() {
        System.out.println("Test");
    }

    // 原函数
    @SentinelResource(value = "hello", blockHandler = "exceptionHandler", fallback = "helloFallback")
    public String hello(long s) {
        return String.format("Hello at %d", s);
    }
    
    // Fallback 函数，函数签名与原函数一致或加一个 Throwable 类型的参数.
    public String helloFallback(long s) {
        return String.format("Halooooo %d", s);
    }

    // Block 异常处理函数，参数最后多一个 BlockException，其余与原函数一致.
    public String exceptionHandler(long s, BlockException ex) {
        // Do some log here.
        ex.printStackTrace();
        return "Oops, error occurred at " + s;
    }
}
```

# 三、Sentinel 控制台



# 四、开源框架适配

- 云原生微服务体系
  - Spring Boot/Spring Cloud
  - Quarkus
- Web 适配
  - Web Servlet
  - Spring Web
  - Spring WebFlux
  - JAX-RS (Java EE)
- RPC 适配
  - Apache Dubbo
  - gRPC
  - Feign
  - SOFARPC
- HTTP client 适配
  - Apache HttpClient
  - OkHttp
- Reactive 适配
  - Reactor
- API Gateway 适配
  - Spring Cloud Gateway
  - Netflix Zuul 1.x
  - Netflix Zuul 2.x
- Apache RocketMQ





