> 参考资料：https://cn.dubbo.apache.org/zh-cn/overview/what/

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

### 场景一：超时时间

**场景描述**

支持动态调整服务超时时间的能力，在无需重启应用的情况下调整服务的超时时间，这对于临时解决一些服务上下游依赖不稳定而导致的调用失败问题非常有效。

**场景举例**

商城项目通过 `org.apache.dubbo.samples.UserService` 提供用户信息管理服务，访问 `http://localhost:8080/` 打开商城并输入任意账号密码，点击 `Login` 即可以正常登录到系统。

![timeout1.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406012230131.png)

有些场景下，User 服务的运行速度会变慢，比如存储用户数据的数据库负载过高导致查询变慢，这时就会出现 `UserService` 访问超时的情况，导致登录失败。

![timeout2.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406012230005.png)

**配置详情**

为了解决突发的登录超时问题，我们只需要适当增加 `UserService` 服务调用的等待时间即可。

规则 key：`org.apache.dubbo.samples.UserService`

规则体：

```yaml
configVersion: v3.0
enabled: true
configs:
  - side: provider
    parameters:
      timeout: 2000
```

`side: provider` 配置会将规则发送到服务提供方实例，所有 `UserService` 服务实例会基于新的 timeout 值进行重新发布，并通过注册中心通知给所有消费方。

### 场景二：服务重试

**场景描述**

在服务初次调用失败后，通过重试能有效的提升总体调用成功率。

> 但也要注意重试可能带来的响应时间增长，系统负载升高等，另外，重试一般适用于只读服务，或者具有幂等性保证的写服务。

**场景举例**

成功登录商城项目后，商城会默认在首页展示当前登录用户的详细信息。

![retry1.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406012238001.png)

但有些时候，提供用户详情的 Dubbo 服务也会由于网络不稳定等各种原因变的不稳定，比如我们提供用户详情的 User 服务就很大概率会调用失败，导致用户无法看到账户的详细信息。

![retry2.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406012239001.png)

**配置详情**

访问用户详情的过程可以设置成异步的，只要最终数据能加载出来，适当的增加等待时间并不是大的问题。因此，我们可以考虑通过对每次用户访问增加重试次数的方式，提高服务详情服务的整体访问成功率。

![retry3.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406012241399.png)

规则 key：`org.apache.dubbo.samples.UserService`

规则体：

```yaml
configVersion: v3.0
enabled: true
configs:
  - side: consumer
    parameters:
      retries: 5
```

`side: consumer` 配置会将规则发送到服务消费方实例，所有 `UserService` 服务实例会基于新的 timeout 值进行重新发布，并通过注册中心通知给所有消费方。

### 场景三：访问日志

**场景描述**

访问日志可以很好的记录某台机器在某段时间内处理的所有服务请求信息，包括请求接收时间、远端 IP、请求参数、响应结果等，运行态动态的开启访问日志对于排查问题非常有帮助。

**场景举例**

商城的所有用户服务都由 `User` 应用的 UserService 提供，通过这个任务，我们为 `User` 应用的某一台或几台机器开启访问日志，以便观察用户服务的整体访问情况。

Dubbo 通过 `accesslog` 标记识别访问日志的开启状态，我们可以指定日志文件的输出位置，也可以单独打开某台机器的访问日志。

**配置详情**

规则 key：shop-user

规则体：

```yaml
configVersion: v3.0
enabled: true
configs:
  - side: provider
    parameters:
      accesslog: true
```

accesslog 的有效值如下：

- `true` 或 `default` 时，访问日志将随业务 logger 一同输出，此时可以在应用内提前配置 `dubbo.accesslog` appender 调整日志的输出位置和格式
- 具体的文件路径如 `/home/admin/demo/dubbo-access.log`，这样访问日志将打印到指定的文件内

在 Admin 界面，还可以单独指定开启某一台机器的访问日志：

```yaml
configVersion: v3.0
enabled: true
configs:
  - match
     address:
       oneof:
        - wildcard: "{ip}:*"
    side: provider
    parameters:
      accesslog: true
```

其中，`{ip}` 替换为具体的机器地址即可。

### 场景四：区域调用

**场景描述**

当应用部署在多个不同机房/区域的时候，应用之间相互调用就会出现跨区域的情况，而跨区域调用会增加响应时间，影响用户体验。

同机房/区域优先是指应用调用服务时，优先调用同机房/区域的服务提供者，避免了跨区域带来的网络延时，从而减少了调用的响应时间。

**场景举例**

Detail 应用和 Comment 应用都有双区域部署，其中 Detail v1 与 Comment v1 部署在区域 Beijing，Detail v2 与 Comment v2 部署在区域 Hangzhou 区域。

为了保证服务调用的响应速度，我们需要增加同区域优先的调用规则，确保 Beijing 区域内的 Detail v1 始终默认调用 Comment v1，Hangzhou 区域内的 Detail v2 始终调用 Comment v2。

![region1](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406012252388.png)

当同区域内的服务出现故障或不可用时，则允许跨区域调用。

![region2](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406012252153.png)

**配置详情**

规则 key：`org.apache.dubbo.samples.CommentService`

规则体：

```yaml
configVersion: v3.0
enabled: true
force: false
key: org.apache.dubbo.samples.CommentService
conditions:
  - '=> region = $region'
```

这里使用的是条件路由，`region` 为我们示例中的区域标识，会自动的识别当前发起调用的一方所在的区域值，当请求到达 `hangzhou` 区域部署的 Detail 后，从 Detail 发出的请求自动筛选 URL 地址中带有 `region=hangzhou` 标识的 Comment 地址，如果发现有可用的地址子集则将请求发出，如果没有匹配条件的地址，则随机发往任意可用区地址。

`force: false` 也是关键，这允许在同区域无有效地址时，可以跨区域调用服务。

### 场景五：环境隔离

**场景描述**

在生产发布过程中，为了保障新版本得到充分的验证，我们需要搭建一套完全隔离的线上灰度环境用来部署新版本服务，线上灰度环境能完全模拟生产运行情况，但只有固定的带有特定标记的线上流量会被导流到灰度环境，充分验证新版本的同时将线上变更风险降到最低。

利用 Dubbo 提供的标签路由能力，可以非常灵活的实现流量隔离能力。

**场景举例**

我们决定为商城系统建立一套完整的线上灰度验证环境，灰度环境和线上环境共享一套物理集群，需要我们通过 Dubbo 标签路由从逻辑上完全隔离出一套环境，做到灰度流量和线上流量互不干扰。

![gray1](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406012302094.png)

首先，为 User、Detail、Comment、Order 几个应用都部署灰度环境实例，我们为这部分实例都带有 `env=gray` 的环境标。

**配置详情**

我们需要通过 Admin 为 `shop-detail`、`shop-comment`、`shop-order`、`shop-user` 四个应用分别设置标签归组规则，以 `shop-detail` 为例：

规则 key：`shop-detail`

规则体：

```yaml
configVersion: v3.0
force: true
enabled: true
key: shop-detail
tags:
  - name: gray
    match:
      - key: env
        value:
          exact: gray
```

其中，`name` 为灰度环境的流量匹配条件，只有请求上下文中带有 `dubbo.tag=gray` 的流量才会被转发到隔离环境地址子集。请求上下文可通过 `RpcContext.getClientAttachment().setAttachment("dubbo.tag", "gray")` 传递。

`match` 指定了地址子集筛选条件，示例中我们匹配了所有地址 URL 中带有 `env=gray` 标签的地址列表（商城示例中 v2 版本部署的实例都带已经被打上这个标签）。

`force` 指定了是否允许流量跳出灰度隔离环境，这决定了某个服务发现灰度隔离环境没有可用地址时的行为，默认值为 `false` 表示会 fallback 到不属于任何隔离环境 (不带标签) 的普通地址集（不会 fallback 到任何已经归属其他隔离环境的 ip 地址）。示例中设置 `froce: true` 表示当灰度环境地址子集为空时，服务调用失败（No provider exception）。

### 场景六：参数路由

**场景描述**



**场景举例**



**配置详情**

规则 key：`xxx`

规则体：

```yaml

```

### 场景七：权重比例

**场景描述**



**场景举例**



**配置详情**

规则 key：`xxx`

规则体：

```yaml

```

### 场景八：服务降级

**场景描述**



**场景举例**



**配置详情**

规则 key：`xxx`

规则体：

```yaml

```

### 场景九：机器导流

**场景描述**



**场景举例**



**配置详情**

规则 key：`xxx`

规则体：

```yaml

```




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















