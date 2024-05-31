# 一、快速开始

> 示例代码: https://github.com/apache/dubbo-samples/tree/master/2-advanced/dubbo-samples-dubbo

以下示例使用 Spring Boot 快速开始 dubbo 的入门级使用。

在本任务中，将分为 3 个子模块，其中 `interface` 模块被 `consumer` 和 `provider` 两个模块共同依赖，存储 RPC 通信使用的 API 接口。

## 1.1 定义接口

工程结构如下：

```
// 共享 API 模块
dubbo-samples-spring-boot-interface
|-- pom.xml
|-- src/main/java/org/apache/dubbo/springboot/demo
  |-- DemoService.java    // API 接口
```

在 `dubbo-spring-boot-demo-interface`模块下建立 `DemoService` 接口，定义如下：

```java
package org.apache.dubbo.springboot.demo;

public interface DemoService {
    String sayHello(String name);
}
```

## 1.2 服务提供者

工程结构如下：

```
// 服务端模块
dubbo-samples-spring-boot-consumer
|-- pom.xml
|-- src/main/java/org/apache/dubbo/springboot/demo/provider
  |-- DemoServiceImpl.java    // 服务端实现类
  |-- ProviderApplication.java    // 服务端启动类
|-- src/main/resources
  |-- application.yml    // Spring Boot 配置文件
```

在 pom.xml 文件里添加依赖：

```xml
<!-- dubbo -->
<dependency>
    <groupId>org.apache.dubbo</groupId>
    <artifactId>dubbo-spring-boot-starter</artifactId>
</dependency>
<dependency>
    <groupId>org.apache.dubbo</groupId>
    <artifactId>dubbo-dependencies-zookeeper-curator5</artifactId>
    <type>pom</type>
    <exclusions>
        <exclusion>
            <artifactId>slf4j-reload4j</artifactId>
            <groupId>org.slf4j</groupId>
        </exclusion>
    </exclusions>
</dependency>
```

在`dubbo-spring-boot-demo-provider` 模块下建立 `DemoServiceImpl` 类，定义如下：

```java
package org.apache.dubbo.springboot.demo.provider;

import org.apache.dubbo.config.annotation.DubboService;
import org.apache.dubbo.springboot.demo.DemoService;

@DubboService
public class DemoServiceImpl implements DemoService {

    @Override
    public String sayHello(String name) {
        return "Hello " + name;
    }
}
```

在 application.yml 文件中添加以下内容：

```yml
dubbo:
  application:
    name: dubbo-springboot-demo-provider
  protocol:
    name: dubbo
    port: -1
  registry:
    address: zookeeper://${zookeeper.address:127.0.0.1}:2181
```

启动类如下：

```java
@SpringBootApplication
@EnableDubbo
public class ProviderApplication {
    public static void main(String[] args) {
        SpringApplication.run(ProviderApplication.class, args);
    }
}
```

## 1.3 服务消费者

工程结构如下：

```
// 消费端模块
dubbo-samples-spring-boot-consumer
|-- pom.xml
|-- src/main/java/org/apache/dubbo/springboot/demo/consumer
  |-- ConsumerApplication.java    // 消费端启动类
  |-- Task.java    // 消费端模拟调用任务
|-- src/main/resources
  |-- application.yml    // Spring Boot 配置文件
```

在 pom.xml 文件里添加依赖：

```xml
<!-- dubbo -->
<dependency>
    <groupId>org.apache.dubbo</groupId>
    <artifactId>dubbo-spring-boot-starter</artifactId>
</dependency>
<dependency>
    <groupId>org.apache.dubbo</groupId>
    <artifactId>dubbo-dependencies-zookeeper-curator5</artifactId>
    <type>pom</type>
    <exclusions>
        <exclusion>
            <artifactId>slf4j-reload4j</artifactId>
            <groupId>org.slf4j</groupId>
        </exclusion>
    </exclusions>
</dependency>
```

在 application.yml 文件中添加以下内容：

```yaml
dubbo:
  application:
    name: dubbo-springboot-demo-consumer
  protocol:
    name: dubbo
    port: -1
  registry:
    address: zookeeper://${zookeeper.address:127.0.0.1}:2181
```

消费逻辑代码 Task 类如下：

```javascript
@Component
public class Task implements CommandLineRunner {
    @DubboReference
    private DemoService demoService;

    @Override
    public void run(String... args) throws Exception {
        String result = demoService.sayHello("world");
        System.out.println("Receive result ======> " + result);

        new Thread(()-> {
            while (true) {
                try {
                    Thread.sleep(1000);
                    System.out.println(new Date() + " Receive result ======> " + demoService.sayHello("world"));
                } catch (InterruptedException e) {
                    e.printStackTrace();
                    Thread.currentThread().interrupt();
                }
            }
        }).start();
    }
}
```

启动类如下：

```java
@SpringBootApplication
@EnableDubbo
public class ConsumerApplication {
    public static void main(String[] args) {
        SpringApplication.run(ConsumerApplication.class, args);
    }
}
```

## 1.4 启动应用

可以看到 dubbo-samples-spring-boot-consumer 控制台打印如下：

```
Receive result ======> Hello world
```

# 二、介绍

## 2.1 为什么需要 Dubbo？

使用它能够很好的提高业务迭代效率与系统稳定性，要做到这一点就需要解决服务拆分与定义、数据通信、地址发现、流量管理、数据一致性、系统容错能力等一系列问题。

Dubbo 可以帮助解决如下微服务实践问题：

- 服务定义

Dubbo 支持通过 IDL 定义服务，也支持编程语言特有的服务开发定义方式，如通过 Java Interface 定义服务。

- 服务发布与调用

Dubbo 支持同步、异步、Reactive Streaming 等服务调用编程模式，还支持请求上下文 API、设置超时时间等。

- 服务治理与监控

作为服务框架数据面，Dubbo 定义了服务地址发现、负载均衡策略、基于规则的流量路由、Metrics 指标采集等服务治理抽象，并适配到特定的产品实现。

## 2.2 Dubbo 核心概念

![architecture](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202405311039546.png)

以上是 Dubbo 的工作原理图，从抽象架构上分为两层：服务治理抽象控制面 和 Dubbo 数据面。

**服务治理控制面**

服务开发框架解决了开发与通信的问题，但在微服务集群环境下，我们仍需要解决无状态服务节点动态变化、外部化配置、日志跟踪、可观测性、流量管理、高可用性、数据一致性等一系列问题，我们将这些问题统称为服务治理。

以下展示了 Dubbo 核心的服务治理功能定义：

![governance](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202405311040160.png)

**Dubbo 数据面**

代表的是集群中所有的 Dubbo 进程，进程之间通过 RPC 协议实现数据交换，Dubbo 定义了微服务应用开发与调用规范并负责完成数据传输的编解码工作。

# 三、功能

## 3.1 服务发现

Dubbo 服务发现具备高性能、支持大规模集群、服务级元数据配置等优势，提供 Nacos、Zookeeper、Consul、Redis、kubernetes 等多种注册中心适配，与 Spring Cloud、Kubernetes Service 模型打通，支持自定义扩展。

**面向百万实例集群的服务发现机制**

![service-discovery](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202405311040452.png)

**高效地址推送实现**

Dubbo 实现了按需精准订阅地址信息。比如一个消费者应用依赖 app1、app2，则只会订阅 app1、app2 的地址列表更新，大幅减轻了冗余数据推送和解析的负担。

![service-discovery](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202405311040822.png)

**丰富元数据配置**

首先，消费者从注册中心接收到地址 (ip:port) 信息，然后与提供者建立连接并读取到对端的元数据配置信息，两部分信息共同组装成消费端有效的地址列表。

![service-discovery](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202405311040518.png)

## 3.2 负载均衡

目前 Dubbo 内置了如下负载均衡算法，可通过调整配置项启用。

| 算法                          | 特性                    | 备注                                                 |
| :---------------------------- | :---------------------- | :--------------------------------------------------- |
| Weighted Random LoadBalance   | 加权随机                | 默认算法，默认权重相同                               |
| RoundRobin LoadBalance        | 加权轮询                | 借鉴于 Nginx 的平滑加权轮询算法，默认权重相同，      |
| LeastActive LoadBalance       | 最少活跃优先 + 加权随机 | 背后是能者多劳的思想                                 |
| Shortest-Response LoadBalance | 最短响应优先 + 加权随机 | 更加关注响应速度                                     |
| ConsistentHash LoadBalance    | 一致性哈希              | 确定的入参，确定的提供者，适用于有状态请求           |
| P2C LoadBalance               | Power of Two Choice     | 随机选择两个节点后，继续选择“连接数”较小的那个节点。 |
| Adaptive LoadBalance          | 自适应负载均衡          | 在 P2C 算法基础上，选择二者中 load 最小的那个节点    |

## 3.3 流量管控

在 Dubbo 中，多个路由器组成一条路由链共同协作。

![Router](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202405311040740.png)

Dubbo 中的每个服务都有一条完全独立的路由链，每个服务的路由链组成可能不同，处理的规则各异，各个服务间互不影响。

对单条路由链而言，即使每次输入的地址集合相同，根据每次请求上下文的不同，生成的地址子集结果也可能不同。

## 3.4 观测服务

**Admin**

Admin 控制台可视化展示了集群中的应用、服务、实例及依赖关系，支持流量治理规则下发，同时还提供如服务测试、mock、文档管理等提升研发测试效率的工具。

![Admin 效果图](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202405311040035.jpg)

**Metrics**

Dubbo 运行时统计了包括 qps、rt、调用总数、成功数、失败数，失败原因统计等在内的核心服务指标，同时，为了更好的监测服务运行状态，Dubbo 还提供了对核心组件状态的监控，如线程池数量、服务健康状态等。

可以通过 Grafana 可视化的查看 Metrics 指标：

![Grafana 效果图](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202405311040630.png)

**Tracing**

Dubbo 通过 Filter 拦截器实现了请求运行时的埋点跟踪，通过将跟踪数据导出到一些主流实现如 Zipkin、Skywalking、Jaeger 等，可以实现全链路跟踪数据的分析与可视化展示。

![Tracing 效果图](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202405311040911.png)

**Logging**

访问日志可以帮助分析系统的流量情况，在有些场景下，开启访问日志对于排查问题也非常有帮助。



# 四、任务



# 五、SDK用户手册



# 六、其他



# 七、安全公告















