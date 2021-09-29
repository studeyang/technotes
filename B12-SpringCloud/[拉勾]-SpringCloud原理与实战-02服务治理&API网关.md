# 服务治理

# 04 | 服务治理：服务治理解决方案？

为了更好地理解服务治理背后的基本需求、设计模型以及相应的实现策略和工具，做到触类旁通，我们需要首先对服务治理的解决方案做全面阐述。

**服务治理的基本需求**

对于服务治理而言，可以说支持服务注册和服务发现就是它最基本也最重要的功能需求。

首当其冲面临的一大挑战就是服务实例的数量较多。而且，由于自动扩容、服务的失败和更新等因素，服务实例的运行时状态也经常变化，如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210302221958.png" alt="image-20210302221958514" style="zoom: 33%;" />

对于服务提供者而言，需要一个自动化机制将自己的服务实例注册到服务注册中心；对于服务消费者而言，需要它能自动发现这些服务实例并进行远程调用。

此外，注册中心还需要具备高可用。同时，考虑到异构系统之间的交互需求，注册中心作为一种平台化解决方案也应该提供多种客户端技术的集成支持。

**服务治理的设计模型**

在服务启动时，服务提供者通过内部的注册中心客户端程序自动将自身注册到注册中心，而服务消费者的注册中心客户端程序则可以从注册中心中获取那些已经注册的服务实例信息。

注册中心的基本模型参考下图：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210302222626.png" alt="image-20210302222626694" style="zoom: 50%;" />

为了提高服务路由的效率和容错性，服务消费者可以配备缓存机制以加速服务路由。

**服务治理的实现策略**

对于服务治理工具而言，在实现上的主要难度在于在服务提供者实例状态发生变更时如何同步到服务的消费者。

从架构设计上讲，状态变更管理可以采用发布-订阅模式。基于这种思想，就诞生了一种服务监听机制。通常采用监听器以及回调机制，如下图所示。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210302223902.png" alt="image-20210302223902680" style="zoom:50%;" />

另外一种确保状态信息同步的方式是采用轮询机制。即服务的消费者定期调用注册中心提供的服务获取接口获取最新的服务列表并更新本地缓存，如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210302224045.png" alt="image-20210302224045406" style="zoom:50%;" />

轮询机制实现上就是一个定时程序，需要考虑定时的频率以确保数据同步的时效性。

**服务治理的实现工具**

目前市面上存在一批主流的服务治理实现工具，包括常见的 Consul 、ZooKeeper、Netflix Eureka 等。

以 ZooKeeper 为例，它就是“服务监听机制”实现策略的典型代表性工具。

ZooKeeper本质上是一个树形结构，可以在树上创建临时节点，并对节点添加监听器。临时节点的客户端关注该节点的状态，一旦发生变化则通过监听器回传消息到客户端，然后客户端的回调函数就会得到调用。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210302224434.png" alt="image-20210302224434432" style="zoom:50%;" />

对于 Netflix Eureka 而言，采用的就是典型的“轮询机制”来实现服务实例状态的同步，默认的同步频率是 30 秒。

**服务治理与负载均衡**

关于服务发现环节，业界也有两种不同的实现方式，一种是客户端发现机制，一种则是服务器端发现机制。在微服务架构中，主流的是采用客户端发现机制，即在每个服务消费者内部保存着一个服务列表：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210302224817.png" alt="image-20210302224817683" style="zoom: 33%;" />

当服务消费者真正对某一个服务提供者发起远程调用时，这时候就需要集成负载均衡机制。这时候的负载均衡也是一种客户端行为，被称为客户端负载均衡：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210308151740.png" alt="image-20210302225006561" style="zoom:33%;" />

**Spring Cloud中的服务治理解决方案**

Spring Cloud 整体服务治理方案如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210302225254.png" alt="image-20210302225254781" style="zoom: 50%;" />

Spring Cloud Netflix 中也集成了Netflix Ribbon 组件来实现客户端负载均衡。

# 05 | 服务注册：构建 Eureka 服务器及其实现原理？

**基于 Eureka 构建注册中心**

1. 构建单点 Eureka 服务器

引入依赖：

```xml
<dependency>
     <groupId>org.springframework.cloud</groupId>
     <artifactId>spring-cloud-starter-netflix-eureka-server</artifactId>
</dependency>
```

创建 Spring Boot 的启动类：

```java
@SpringBootApplication
@EnableEurekaServer
public class EurekaServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(EurekaServerApplication.class, args);
    }
}
```

Eureka 配置项可以分成三大类。

一类用于控制 Eureka 服务器端行为，以 eureka.server 开头；一类则是从客户端角度出发考虑配置需求，以 eureka.client 开头；而最后一类则关注于注册到 Eureka 的服务实例本身，以 eureka.instance 开头。

在 eureka-server 工程的 application.yml 文件中添加了如下配置信息。

```yaml
server:
  port: 8761
  
eureka:
  client:
    # 是否把当前的客户端实例注册到 Eureka 服务器
    registerWithEureka: false
    # 是否从 Eureka 服务器上拉取已注册的服务信息
    fetchRegistry: false
    serviceUrl:
      defaultZone: http://localhost:8761
```

2. 构建 Eureka 服务器集群

我们准备两个 Eureka 服务实例 eureka1 和 eureka2。

在 Spring Boot 中，我们分别提供 application-eureka1.yml 和 application-eureka2.yml 这两个配置文件来设置相关的配置项。其中 application-eureka1.yml 配置文件的内容如下：

```yaml
server:
  port: 8761

eureka:
  instance:
    # 指定当前 Eureka 服务的主机名称
    hostname: eureka1
  client:
    serviceUrl:
      # 指向集群中的其他 Eureka 服务器
      defaultZone: http://eureka2:8762/eureka/
```

对应的，application-eureka2.yml 配置文件的内容如下：

```yaml
server:
  port: 8762

eureka:
  instance:
    hostname: eureka2
  client:
    serviceUrl:
      defaultZone: http://eureka1:8761/eureka/
```

Eureka 集群的构建方式实际上就是将自己作为服务并向其他注册中心注册自己，这样就形成了一组互相注册的服务注册中心以实现服务列表的同步。

显然，这个场景下 registerWithEureka 和 fetchRegistry配置项应该都使用其默认的 true 值。

eureka.instance.hostname 配置项中的 eureka1 和 eureka2 是无法访问的，所以需要在本机hosts 文件中添加以下信息。

```reStructuredText
127.0.0.1 eureka1
127.0.0.1 eureka2
```

**理解 Eureka 服务器实现原理**

1. Eureka 核心概念

我们在对 Eureka 的内部结构做进一步展开，可以得到如下所示的注册中心细化模型图。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210303224426.png" alt="image-20210303224426138" style="zoom: 50%;" />

服务注册（Register）：各个微服务通过向 Eureka 服务器提供 IP 地址、端点等各项与服务发现相关的基本信息完成服务注册操作。

服务续约（Register）：Eureka 客户端需要每隔一定时间主动上报自己的运行时状态。

服务取消（Cancel）：Eureka 客户端主动告知 Eureka 服务器自己不想再注册到 Eureka 中。

服务剔除（Evict）：当 Eureka 客户端连续一段时间没有向 Eureka 服务器发送服务续约信息时，Eureka 服务器就会认为该服务实例已经不再运行，从而将其从服务列表中进行剔除。

2. Eureka 服务存储源码解析

对于一个注册中心而言，我们首先需要关注它的数据存储方法。InstanceRegistry 接口及其实现类承接了这部分职能。类层结构如下所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210303225111.png" alt="image-20210303225111370" style="zoom:50%;" />

在 AbstractInstanceRegistry 中发现了 Eureka 用于保存注册信息的数据结构，如下所示：

```java
private final ConcurrentHashMap<String, Map<String, Lease<InstanceInfo>>> registry = new ConcurrentHashMap<String, Map<String, Lease<InstanceInfo>>>();
```

其中第一层的 ConcurrentHashMap 的 Key 为 spring.application.name，也就是服务名；而第二层的 Map 的 Key 为 instanceId，也就是服务的唯一实例 ID，Value 为 Lease 对象。

Eureka 采用 Lease（租约）这个词来表示对服务注册信息的抽象，Lease 对象保存了服务实例信息以及一些实例服务注册相关的时间，如注册时间 registrationTimestamp、最新的续约时间 lastUpdateTimestamp 等。如果用图形化的表达方式来展示这种数据结构，可以参考下图：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210303225905.png" alt="image-20210303225905311" style="zoom:50%;" />

3. Eureka 服务缓存源码解析

Eureka 服务器端组件的另一个核心功能是提供服务列表。为了提高性能，Eureka 服务器会缓存一份所有已注册的服务列表，并通过一定的定时机制对缓存数据进行更新。

为了获取注册到 Eureka 服务器上具体某一个服务实例的详细信息，可以访问如下地址：

```http
http://<eureka-server-ip>:8761/eureka/apps/<APPID>
```

ApplicationResource 类（位于com.netflix.eureka.resources 包中）提供了根据应用获取注册信息的入口。我们来看该类的 getApplication 方法，核心代码如下所示：

```java
Key cacheKey = new Key(
    Key.EntityType.Application,
    appName,
    keyType,
    CurrentRequestVersion.get(),
    EurekaAccept.fromString(eurekaAccept)
);

String payLoad = responseCache.get(cacheKey);

if (payLoad != null) {
    logger.debug("Found: {}", appName);
    return Response.ok(payLoad).build();
} else {
    logger.debug("Not Found: {}", appName);
    return Response.status(Status.NOT_FOUND).build();
}
```

4. Eureka 高可用源码解析

Eureka 的高可用部署方式被称为 Peer Awareness 模式。我们在 InstanceRegistry 的类层结构中也已经看到了它的一个扩展接口 PeerAwareInstanceRegistry 以及该接口的实现类 PeerAwareInstanceRegistryImpl，它的 register 方法如下所示：

```java
@Override
public void register(final InstanceInfo info, final boolean isReplication) {
    int leaseDuration = Lease.DEFAULT_DURATION_IN_SECS;
    if (info.getLeaseInfo() != null && info.getLeaseInfo().getDurationInSecs() > 0) {
        leaseDuration = info.getLeaseInfo().getDurationInSecs();
    }
    super.register(info, leaseDuration, isReplication);
    replicateToPeers(Action.Register, info.getAppName(), info.getId(), info, null, isReplication);
}
```

replicateToPeers 方法就是用来实现服务器节点之间的状态同步。replicateToPeers 方法的核心代码如下所示：

```java
for (final PeerEurekaNode node : peerEurekaNodes.getPeerEurekaNodes()) {
    //如果该 URL 代表主机自身，则不用进行注册
    if (peerEurekaNodes.isThisMyUrl(node.getServiceUrl())) {
        continue;
    }
    replicateInstanceActionsToPeers(action, appName, id, info, newStatus, node);
}
```

# 06 | 服务发现：构建 Eureka 客户端及其实现原理？

**使用 Eureka 注册和发现服务**

今天我们将先以 user-service 为例来演示如何完成服务的注册和发现。

1. 实现服务注册

添加依赖：

```xml
<dependency>
     <groupId>org.springframework.cloud</groupId>
     <artifactId>spring-cloud-starter-netflix-eureka-client</artifactId>
</dependency>
```

user-service 的 Bootstrap 类：

```java
@SpringBootApplication
@EnableEurekaClient
public class UserApplication {
  	public static void main(String[] args) {
        SpringApplication.run(UserApplication.class, args);
    }
}
```

可以使用统一的 @SpringCloudApplication 注解，来实现 @SpringBootApplication 和 @EnableEurekaClient 这两个注解整合在一起的效果。

user-service 中的配置内容如下所示：

```yaml
spring:
  application:
    name: userservice 
server:
  port: 8081

eureka:
  client:
    serviceUrl:
      defaultZone: http://localhost:8761/eureka/
```

如果使用的是 Eureka 服务器集群，那么 eureka.client.serviceUrl.defaultZone 配置项的内容就应该是“http://eureka1:8761/eureka/,http://eureka2:8762/eureka/”，用于指向当前的集群环境。

2. 实现服务发现

为了获取注册到 Eureka 服务器上具体某一个服务实例的详细信息，我们可以访问如下地址：

```http
http://<eureka-ip-port>:8761/eureka/apps/<APPID>
```

例如：

```http
http://localhost:8761/eureka/apps/userservice
```

**理解 Eureka 客户端基本原理**

在 Netflix Eureka 中，专门提供了一个客户端包，并抽象了一个客户端接口 EurekaClient。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210304222710.png" alt="image-20210304222710360" style="zoom: 67%;" />

# 07 | 负载均衡：如何使用 Ribbon 实现客户端负载均衡？

Spring Cloud 中同样存在着与 Eureka 配套的负载均衡器，这就是 Ribbon 组件。Eureka 和 Ribbon 的交互方式如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210304223949.png" alt="image-20210304223949098" style="zoom: 50%;" />

**理解 Ribbon 与 DiscoveryClient**

1. Ribbon 的核心功能

Spring Cloud Netflix Ribbon 通过注解就能简单实现在面向服务的接口调用中，自动集成负载均衡功能，使用方式主要包括以下两种：

- 使用 @LoadBalanced 注解。

@LoadBalanced 注解用于修饰发起 HTTP 请求的 RestTemplate 工具类，并在该工具类中自动嵌入客户端负载均衡功能。开发人员不需要针对负载均衡做任何特殊的开发或配置。

- 使用 @RibbonClient 注解。

可以使用 @RibbonClient 注解来完全控制客户端负载均衡行为。这在需要定制化负载均衡算法等某些特定场景下非常有用，我们可以使用这个功能实现更细粒度的负载均衡配置。

2. 使用 DiscoveryClient 获取服务实例信息

首先，我们获取当前注册到 Eureka 中的服务名称全量列表，如下所示：

```java
List<String> serviceNames = discoveryClient.getServices();
```

基于这个服务名称列表可以获取所有自己感兴趣的服务，并进一步获取这些服务的实例信息：

```java
List<ServiceInstance> serviceInstances = discoveryClient.getInstances(serviceName);
```

3. 通过 @Loadbalanced 注解调用服务

我们在 intervention-service 的启动类 InterventionApplication 中，通过 @LoadBalanced 注解创建 RestTemplate。

```java
@SpringBootApplication
@EnableEurekaClient
public class InterventionApplication {

    @LoadBalanced
    @Bean
    public RestTemplate getRestTemplate(){
        return new RestTemplate();
    }

    public static void main(String[] args) {
        SpringApplication.run(InterventionApplication.class, args);
    }
}
```

我们在 intervention-service 工程中添加一个新的 UserServiceClient 类并添加以下代码：

```java
@Component
public class UserServiceClient {

    @Autowired
    RestTemplate restTemplate;

    public UserMapper getUserByUserName(String userName){
        ResponseEntity<UserMapper> restExchange =
            restTemplate.exchange(
                "http://userservice/users/{userName}",
                HttpMethod.GET,
                null, UserMapper.class, userName);

        UserMapper user = restExchange.getBody();
        return user;
    }
}
```

这里的 RestTemplate 已经具备了客户端负载均衡功能，因为我们在 InterventionApplication 类中创建该 RestTemplate 时添加了 @LoadBalanced 注解。

同样请注意，URL“http://userservice/users/{userName}”中的”userservice”是在 user-service 中配置的服务名称，也就是在注册中心中存在的名称。

4. 通过 @RibbonClient 注解自定义负载均衡策略

默认情况下，Ribbon 使用的是轮询策略，我们无法控制具体生效的是哪种负载均衡算法。但在有些场景下，我们就需要对负载均衡这一过程进行更加精细化的控制，这时候就可以用到 @RibbonClient 注解。

为了使用 @RibbonClient 注解，我们需要创建一个独立的配置类，用来指定具体的负载均衡规则。

```java
@Configuration
public class SpringHealthLoadBalanceConfig {

    @Autowired
    IClientConfig config;

    @Bean
    @ConditionalOnMissingBean
    public IRule springHealthRule(IClientConfig config) {
        return new RandomRule();
    }
}
```

该配置类的作用是使用 RandomRule 替换 Ribbon 中的默认负载均衡策略 RoundRobin。我们可以在调用特定服务时使用该配置类。

```java
@SpringBootApplication
@EnableEurekaClient
@RibbonClient(name = "userservice", configuration = SpringHealthLoadBalanceConfig.class)
public class InterventionApplication{

    @Bean
    @LoadBalanced
    public RestTemplate restTemplate(){
        return new RestTemplate();
    }

    public static void main(String[] args) {
        SpringApplication.run(InterventionApplication.class, args);
    }
}
```

现在每次访问 user-service 时将使用 RandomRule 这一随机负载均衡策略。

**Ribbon+RestTemplate 实现服务间高可用通信**

- 代码模式

pom.xml 引入依赖：

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-web</artifactId>
</dependency>
<dependency>
  <groupId>com.alibaba.cloud</groupId>
  <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
</dependency>
<dependency>
  <groupId>org.springframework.cloud</groupId>
  <artifactId>spring-cloud-starter-netflix-ribbon</artifactId>
  <version>${spring-cloud-alibaba.version}</version>
</dependency>
```

配置 application.yml：

```yaml
spring:
  application:
    name: provider-service #应用/微服务名字
  cloud:
    nacos:
      discovery:
        #nacos服务器地址
        server-addr: 192.168.31.102:8848 
        username: nacos #用户名密码
        password: nacos
server:
  port: 80
```

使用代码：

```java
@RestController
public class ConsumerController {
    @Resource
    private LoadBalancerClient loadBalancerClient;
    @Resource
    private RestTemplate restTemplate;
    @GetMapping("/consumer/msg")
    public String getProviderMessage() {
        ServiceInstance serviceInstance = loadBalancerClient.choose("provider-service");
        //获取服务实例的 IP 地址
        String host = serviceInstance.getHost();
        //获取服务实例的端口
        int port = serviceInstance.getPort();
        String result = restTemplate.getForObject("http://" + host + ":" + port + "/provider/msg", String.class);
        //向浏览器返回响应
        return "consumer-service 响应数据:" + result;
    }
}
```

- 注解模式

初始化 RestTemplate：

```java
@SpringBootApplication
public class ConsumerServiceApplication {
    @Bean
    @LoadBalanced 
    public RestTemplate restTemplate(){
        return new RestTemplate();
    }
    public static void main(String[] args) {
        SpringApplication.run(ConsumerServiceApplication.class, args);
    }
}
```

使用代码：

```java
@RestController
public class ConsumerController {
    @Resource
    private RestTemplate restTemplate;
    @GetMapping("/consumer/msg")
    public String getProviderMessage() {
        //将原有IP:端口替换为服务名，RestTemplate便会在通信前自动利用Ribbon查询可用provider-service实例列表
        //再根据负载均衡策略选择节点实例
        String result = restTemplate.getForObject("http://provider-service/provider/msg", String.class);
        return "consumer-service获得数据:" + result;
    }
}
```

**如何配置 Ribbon 负载均衡策略**

Ribbon 内置多种负载均衡策略，常用的分为以下几种：

- RoundRobinRule

  轮询策略，Ribbon 默认策略。默认超过 10 次获取到的 server 都不可用，会返回⼀个空的 server。

- RandomRule

  随机策略，如果随机到的 server 为 null 或者不可用的话。会不停地循环选取。

- RetryRule

  重试策略，⼀定时限内循环重试。RetryRule 会在每次选取之后，对选举的 server 进⾏判断，是否为 null，是否 alive，并且在 500ms 内会不停地选取判断。

- BestAvailableRule

  最小连接数策略，遍历 serverList，选取出可⽤的且连接数最小的⼀个 server。那么会调用 RoundRobinRule 重新选取。

- AvailabilityFilteringRule

  可用过滤策略。扩展了轮询策略，会先通过默认的轮询选取⼀个 server，再去判断该 server 是否超时可用、当前连接数是否超限，都成功再返回。

- ZoneAvoidanceRule

  区域权衡策略。扩展了轮询策略，除了过滤超时和链接数过多的 server，还会过滤掉不符合要求的 zone 区域⾥⾯的所有节点，始终保证在⼀个区域/机房内的服务实例进行轮询。

要更改微服务通信时采用的负载均衡策略，在 application.yml 中采用下面格式书写即可。

```yaml
provider-service: #服务提供者的微服务id
  ribbon:
    #设置对应的负载均衡类
    NFLoadBalancerRuleClassName: com.netflix.loadbalancer.RandomRule 
```

# 08 | 负载均衡：Ribbon 的基本架构和实现原理？

**Netflix Ribbon 基本架构**

作为一款客户端负载均衡工具，要做的事情无非就是两件：第一件事情是获取注册中心中的服务器列表；第二件事情是在这个服务列表中选择一个服务进行调用。

针对这两个问题，Netflix Ribbon 提供了自身的一套基本架构，并抽象了一批核心类，让我们来一起看一下核心类。

1. Netflix Ribbon 中的核心类

Netflix Ribbon 的核心接口 ILoadBalancer 就是围绕着上述两个问题来设计的，该接口位于 com.netflix.loadbalancer 包下，定义如下：

```java
public interface ILoadBalancer {
    //添加后端服务
    public void addServers(List<Server> newServers);

    //选择一个后端服务
    public Server chooseServer(Object key); 

    //标记一个服务不可用
    public void markServerDown(Server server);

    //获取当前可用的服务列表
    public List<Server> getReachableServers();

    //获取所有后端服务列表
    public List<Server> getAllServers();
}
```

ILoadBalancer 接口的类层结构如下所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210305224753.png" alt="image-20210305224753270" style="zoom:50%;" />

我们先来梳理 BaseLoadBalancer 包含的作为一个负载均衡器应该具备的一些核心组件，比较重要的有以下三个。

- IRule

IRule 接口是对负载均衡策略的一种抽象，可以通过实现这个接口来提供各种适用的负载均衡算法。

```java
public interface IRule {
    public Server choose(Object key);
    public void setLoadBalancer(ILoadBalancer lb);
    public ILoadBalancer getLoadBalancer();
}
```

- IPing

IPing 接口判断目标服务是否存活，定义如下：

```java
public interface IPing {
    public boolean isAlive(Server server);
}
```

- LoadBalancerStats

LoadBalancerStats 类记录负载均衡的实时运行信息，用来作为负载均衡策略的运行时输入。

2. Netflix Ribbon 中的负载均衡策略

IRule 接口的类层结构如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210305225852.png" alt="image-20210305225852543" style="zoom:50%;" />

静态的几种策略相对都比较简单，而像 RetryRule 实际上不算是严格意义上的负载均衡策略，所以这里重点关注 Ribbon 所实现的几种不同的动态策略。

- BestAvailableRule 策略

选择一个并发请求量最小的服务器，逐个考察服务器然后选择其中活跃请求数最小的服务器。

- WeightedResponseTimeRule 策略

该策略与请求的响应时间有关，显然，如果响应时间越长，就代表这个服务的响应能力越有限，那么分配给该服务的权重就应该越小。

- AvailabilityFilteringRule 策略

通过检查 LoadBalancerStats 中记录的各个服务器的运行状态，过滤掉那些处于一直连接失败或处于高并发状态的后端服务器。

**Spring Cloud Netflix Ribbon**

Spring Cloud Netflix Ribbon 专门针对 Netflix Ribbon 提供了一个独立的集成实现。

Spring Cloud Netflix Ribbon 相当于 Netflix Ribbon 的客户端。而对于 Spring Cloud Netflix Ribbon 而言，我们的应用服务相当于它的客户端。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210305230331.png" alt="image-20210305230331728" style="zoom:50%;" />

这次，我们打算从应用服务层的 @LoadBalanced 注解入手，切入 Spring Cloud Netflix Ribbon，然后再从 Spring Cloud Netflix Ribbon 串联到 Netflix Ribbon，从而形成整个负载均衡闭环管理。

1. @LoadBalanced 注解

为什么通过 @LoadBalanced 注解创建的 RestTemplate 就能自动具备客户端负载均衡的能力？

在 Spring Cloud Netflix Ribbon 中存在一个自动配置类——LoadBalancerAutoConfiguration 类。

而在该类中，维护着一个被 @LoadBalanced 修饰的 RestTemplate 对象的列表。在初始化的过程中，对于所有被 @LoadBalanced 注解修饰的 RestTemplate，调用 RestTemplateCustomizer 的 customize 方法进行定制化，该定制化的过程就是对目标 RestTemplate 增加拦截器 LoadBalancerInterceptor，如下所示：

```java
@Configuration
@ConditionalOnMissingClass("org.springframework.retry.support.RetryTemplate")
static class LoadBalancerInterceptorConfig {
    @Bean
    public LoadBalancerInterceptor ribbonInterceptor(
                            LoadBalancerClient loadBalancerClient, 
                            LoadBalancerRequestFactory requestFactory) {
        return new LoadBalancerInterceptor(loadBalancerClient, requestFactory);
    }

    @Bean
    @ConditionalOnMissingBean
    public RestTemplateCustomizer restTemplateCustomizer(
                final LoadBalancerInterceptor loadBalancerInterceptor) {
        return restTemplate -> {
                List<ClientHttpRequestInterceptor> list = new ArrayList<>(
                    restTemplate.getInterceptors());
                list.add(loadBalancerInterceptor);
                restTemplate.setInterceptors(list);
            };
    }
}
```

这个 LoadBalancerInterceptor 用于实时拦截，可以看到它的构造函数中传入了一个对象 LoadBalancerClient，而在它的拦截方法本质上就是使用 LoadBalanceClient 来执行真正的负载均衡。LoadBalancerInterceptor 类代码如下所示：

```java
public class LoadBalancerInterceptor implements ClientHttpRequestInterceptor {
 
    private LoadBalancerClient loadBalancer;
    private LoadBalancerRequestFactory requestFactory;
 
    public LoadBalancerInterceptor(LoadBalancerClient loadBalancer, LoadBalancerRequestFactory requestFactory) {
        this.loadBalancer = loadBalancer;
        this.requestFactory = requestFactory;
    }
 
    public LoadBalancerInterceptor(LoadBalancerClient loadBalancer) {
        this(loadBalancer, new LoadBalancerRequestFactory(loadBalancer));
    }
 
    @Override
    public ClientHttpResponse intercept(final HttpRequest request, final byte[] body,
            final ClientHttpRequestExecution execution) throws IOException {
        final URI originalUri = request.getURI();
        String serviceName = originalUri.getHost();
        Assert.state(serviceName != null, "Request URI does not contain a valid hostname: " + originalUri);
        return this.loadBalancer.execute(serviceName, requestFactory.createRequest(request, body, execution));
    }
}
```

可以看到这里的拦截方法 intercept 直接调用了 LoadBalancerClient 的 execute 方法完成对请求的负载均衡执行。

2. LoadBalanceClient 接口

LoadBalancerClient 是一个非常重要的接口，定义如下：

```java
public interface LoadBalancerClient extends ServiceInstanceChooser {
 
    <T> T execute(String serviceId, LoadBalancerRequest<T> request) throws IOException;
 
    <T> T execute(String serviceId, ServiceInstance serviceInstance,
           LoadBalancerRequest<T> request) throws IOException;
 
    URI reconstructURI(ServiceInstance instance, URI original);
}
```

LoadBalancerClient 继承自 ServiceInstanceChooser 接口，该接口定义如下：

```java
public interface ServiceInstanceChooser {
    ServiceInstance choose(String serviceId);
}
```

提供具体实现的是实现了 LoadBalancerClient 接口的 RibbonLoadBalancerClient，而 RibbonLoadBalancerClient 位于 spring-cloud-netflix-ribbon 工程中。这样我们的代码流程就从应用程序转入到了 Spring Cloud Netflix Ribbon 中。

RibbonLoadBalancerClient 中，choose 方法最终调用了如下所示的 getServer 方法：

```java
protected Server getServer(ILoadBalancer loadBalancer) {
    if (loadBalancer == null) {
        return null;
    }
    return loadBalancer.chooseServer("default"); 
}
```

这里的 loadBalancer 对象就是前面介绍的 Netflix Ribbon 中的 ILoadBalancer 接口的实现类。这样，我们就把 Spring Cloud Netflix Ribbon 与 Netflix Ribbon 的整体协作流程串联起来。

****

# API 网关

# 09 | 同步网关：基于 Zuul 构建 API 网关

**什么是 API 网关？**

在服务调用过程中添加了一个网关层，所有的客户端都通过这个统一的网关接入微服务。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210306171411.png" alt="image-20210306171357483" style="zoom: 50%;" />

这样一些非业务功能性需求就可以在网关层进行集中处理。包括请求监控、安全管理、路由规则、日志记录、访问控制、服务适配等功能：

**如何使用 Zuul 构建 API 网关？**

引入 spring-cloud-starter-netflix-zuul 依赖，如下所示：

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-netflix-zuul</artifactId>
</dependency>
```

创建 Bootstrap 类，代码如下：

```java
@SpringBootApplication
@EnableZuulProxy
public class ZuulServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(ZuulServerApplication.class, args);
    }
}
```

API 网关与注册中心关系密切，注册中心为服务路由提供了服务定义信息，这是能够实现服务路由的基础。我们需要向 application.yml 配置文件中添加对 Eureka 的集成。配置内容如下所示：

```yaml
server:
  port: 5555
eureka:
  instance:
    preferIpAddress: true
  client:
    registerWithEureka: true
    fetchRegistry: true
    serviceUrl:
      defaultZone: http://localhost:8761/eureka/
```

另一方面，API 网关在其服务的消费者和提供者之间提供了一层反向代理，充当着前置负载均衡器的角色。所以，API 网关的定位决定了 Zuul 需要依赖 Ribbon。

**如何使用 Zuul 实现服务路由？**

对于 API 网关而言，最重要的功能就是服务路由，即通过 Zuul 访问的请求会路由并转发到对应的后端服务中。通过 Zuul 进行服务访问的 URL 通用格式如下所示：

```http
http://zuulservice:5555/service
```

在 Zuul 中，服务路由信息的设置可以使用以下几种常见做法。

1. 基于服务发现映射服务路由

Zuul 可以基于注册中心的服务发现机制实现自动化服务路由功能。这是最常见的、也最推荐的做法。网关不需要做任何事情，因为在 Eureka 中已经保存了各种服务定义信息。

例如，我们在 user-service 的配置文件中通过以下配置项指定了该服务的名称为 userservice：

```yaml
spring:
  application:
    name: userservice
```

这样我们就可以通过http://zuulservice:5555/userservice访问到该服务。

访问 zuul-service 的以下地址：

```http
http://zuulservice:5555/actuator/routes
```

可以看到如下路由映射信息：

```json
{
  "/userservice/**":"userservice"
}
```

"/userservice/**" 代表所有以`/userservice`开头的路径请求都将被自动路由到注册在 Eureka 中的名为 userservice 的某一个服务实例中。

2. 基于动态配置映射服务路由

基于服务发现机制的系统自动映射非常方便，但也有明显的局限性。在日常开发过程中，我们往往对服务映射关系有更多的定制化需求，比方说不使用默认的服务名称来命名目标服务。

可以在 zuul-server 工程下的 application.yml 配置如下：

```yaml
zuul:
  prefix: /springhealth
  routes:
    ignored-services: 'userservice'
    userservice: /user/**
```

现在访问 http://zuulservice:5555/actuator/routes 端点，如下所示：

```json
{
  "/springhealth/user/**":"userservice" 
}
```

3. 基于静态配置映射服务路由

让我们考虑这样一个场景，如果系统中存在一个第三方服务，该服务无法注册到我们的 Eureka 注册中心，且提供了一个 HTTP 接口供 SpringHealth 系统调用。

针对这一场景，我们可以在配置文件中添加如下的静态路由配置，这样访问“/thirdpartyservice/**”时，Zuul 会将该请求转发到外部的第三方服务http://thirdparty.com/thirdpartyservice中。

```yaml
zuul:
  routes:
    thirdpartyservice:
      path: /thirdpartyservice/**
      url: http://thirdparty.com/thirdpartyservice
```

现在的服务路由信息就会变成如下结果：

```json
{
  "/springhealth/thirdpartyservice/**":"http://thirdparty.com/thirdpartyservice",
  "/springhealth/user/**":"userservice"
}
```

**Zuul 整合 Ribbon**

Zuul 能够与 Ribbon 进行整合，这种整合也来自手工设置静态服务路由的方式，具体实现方式如下所示：

```yaml
zuul:
  routes:
    thirdpartyservice:
      path: /thirdpartyservice/**
      serviceId: thirdpartyservice

ribbon:
  eureka:
    enabled: false

thirdpartyservice:
  ribbon:
    listOfServers: http://thirdpartyservice1:8080,http://thirdpartyservice2:8080
```

这里，我们配置了一个 thirdpartyservice 路由信息，通过“/ thirdpartyservice /**”映射到 serviceId 为“thirdpartyservice”的服务中。

然后我们希望通过自定义 Ribbon 的方式来实现客户端负载均衡，这时候就需要关闭 Ribbon 与 Eureka 之间的关联。可以通过“ribbon.eureka.enabled: false”配置项完成这一目标。

在不使用 Eureka 的情况下，我们需要手工指定 Ribbon 的服务列表。“users.ribbon.listOfServers”配置项为我们提供了这方面的支持，如在上面的示例中“http://thirdpartyservice1:8080，http://thirdpartyservice2:8080”就为 Ribbon 提供了两个服务定义作为实现负载均衡的服务列表。

# 10 | 同步网关：剖析 Zuul 网关的工作原理

**ZuulFilter 组件架构**

Zuul 响应 HTTP 请求的过程是一种典型的过滤器结构，内部提供了 ZuulFilter 组件来实现这一机制。作为切入点，我们先从 ZuulFilter 展开讨论。

1. ZuulFilter 的定义与 ZuulRegistry

在 Zuul 中，ZuulFilter 是 Zuul 中的关键组件。IZuulFilter 接口定义如下：

```java
public interface IZuulFilter {
  // 是否需要执行该过滤器
  boolean shouldFilter();
  // 具体需要实现的业务逻辑
  Object run() throws ZuulException;
}
```

IZuulFilter的直接实现类是 ZuulFilter，ZuulFilter 是一个抽象类，额外提供了如下所示的两个抽象方法：

```java
//过滤器类型
//分为 PRE、ROUTING、POST 和 ERROR 四种
abstract public String filterType();
//过滤器执行顺序，数字越小则越先执行
abstract public int filterOrder();
```

既然有了过滤器，系统中就应该存在一个管理过滤器的组件，称为过滤器注册表 FilterRegistry。定义如下：

```java
public class FilterRegistry {

  private static final FilterRegistry INSTANCE = new FilterRegistry();

  public static final FilterRegistry instance() {
    return INSTANCE;
  }

  private final ConcurrentHashMap<String, ZuulFilter> filters = new ConcurrentHashMap<String, ZuulFilter>();
  
  private FilterRegistry() {}
  
}
```

2. ZuulFilter 的加载与 FilterLoader

FilterLoader 负责 ZuulFilter 的加载。它用来在源码变化时编译、载入和校验过滤器。针对这个核心类，我们将从它的变量入手，对它进行分析。

```java
//Filter 文件名与修改时间的映射
private final ConcurrentHashMap<String, Long> filterClassLastModified = new ConcurrentHashMap<>();
//Filter 名称与代码的映射
private final ConcurrentHashMap<String, String> filterClassCode = new ConcurrentHashMap<>();
//Filter 名称与名称的映射，作用是判断该 Filter 是否存在
private final ConcurrentHashMap<String, String> filterCheck = new ConcurrentHashMap<>();
//Filter 类型与 List<ZuulFilter> 的映射
private final ConcurrentHashMap<String, List<ZuulFilter>> hashFiltersByType = new ConcurrentHashMap<>();
//前面提到的 FilterRegistry 单例
private FilterRegistry filterRegistry = FilterRegistry.instance();
//动态代码编译器实例，Zuul 提供的默认实现是 GroovyCompiler
static DynamicCodeCompiler COMPILER;
//ZuulFilter 工厂类
static FilterFactory FILTER_FACTORY = new DefaultFilterFactory();
```

DynamicCodeCompiler 是一种动态代码编译器。DynamicCodeCompiler 接口定义如下：

```java
public interface DynamicCodeCompiler {
  //从代码编译到类
  Class compile(String sCode, String sName) throws Exception;
  //从文件编译到类
  Class compile(File file) throws Exception;
}
```

Zuul 通过文件来存储各种 ZuulFilter 的定义和实现逻辑，然后启动一个守护线程（FilterFileManager）定时轮询这些文件，确保变更之后的文件能够动态加载到 FilterRegistry 中。

3. RequestContext 与上下文

我们可以通过 RequestContext 对象将业务信息放到请求上下文（Context）中，并使其在各个 ZuulFilter 中进行传递。

HTTP 请求的所有参数总是绑定在处理请求的线程中，每个新的请求都是由一个独立的线程进行处理，诸如 Tomcat 之类的服务器会为我们启动了这个线程。

因此，RequestContext 的访问必须设计成线程安全，Zuul 使用了非常常见和实用的 ThreadLocal，如下所示：

```java
protected static final ThreadLocal<? extends RequestContext> threadLocal = 
  new ThreadLocal<RequestContext>() {
        @Override
        protected RequestContext initialValue() {
            try {
                return contextClass.newInstance();
            } catch (Throwable e) {
                throw new RuntimeException(e);
            }
        }
};
```

用于获取 RequestContext 的 getCurrentContext 方法如下所示：

```java
public static RequestContext getCurrentContext() {
  RequestContext context = threadLocal.get();
  return context;
}
```

4. HTTP 请求与过滤器执行

接下去我们分析如何使用加载好的 ZuulFilter。Zuul 提供了 FilterProcessor 类来执行 Filter，FilterProcessor 基于 runFilters 方法衍生出 postRoute()、preRoute()、error() 和 route() 这四个方法，分别对应 Zuul 中的四种过滤器类型。

其中 PRE 过滤器在请求到达目标服务器之前调用，ROUTING 过滤器把请求发送给目标服务，POST 过滤器在请求从目标服务返回之后执行，而 ERROR 过滤器则在发生错误时执行。同时，这四种过滤器有一定的执行顺序，如下所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210307232307.png" alt="image-20210307232307246" style="zoom:50%;" />

在 Spring Cloud 中所有请求都是 HTTP 请求，Zuul 作为一个服务网关同样也需要完成对 HTTP 请求的响应。ZuulServlet 是 Zuul 中对 HttpServlet 接口的一个实现类。

**Spring Cloud 集成 ZuulFilter**

Spring Cloud 的 ZuulFilter 是如何实现加载的呢？

在 ZuulFilterInitializer 中发现了如下所示的 contextInitialized 方法：

```java
@PostConstruct
public void contextInitialized() {
  log.info("Starting filter initializer");
 
  TracerFactory.initialize(tracerFactory);
  CounterFactory.initialize(counterFactory);
 
  for (Map.Entry<String, ZuulFilter> entry : this.filters.entrySet()) {
    filterRegistry.put(entry.getKey(), entry.getValue());
  }
}
```

至此，Spring Cloud 通过 Netflix Zuul 提供的 FilterLoader 和 FilterRegistry 等工具类完成了两者之间的集成。

# 11 | 异步网关：基于 Spring Cloud Gateway 构建 API 网关

**Spring Cloud Gateway 简介**

在性能上，Spring Cloud Gateway 基于最新的 Spring 5 和 Spring Boot 2，以及用于响应式编程的 Project Reactor 框架，提供的是响应式、非阻塞式 I/O 模型。

而 Zuul 的实现原理是对 Servlet 的一层封装，通信模式上采用的是阻塞式 I/O。

所以 Spring Cloud Gateway 性能更高。

功能上，Spring Cloud Gateway 也比 Zuul 更为丰富。除了通用的服务路由机制之外，Spring Cloud Gateway 还支持请求限流等面向服务容错方面的功能，同样也能与 Hystrix 等框架进行良好的集成。

但是，Spring Cloud Gateway 的源码非常复杂，出现问题不容易排查和解决。而 Zuul 的编程模型和底层原理都非常简单，开发调试上也容易把握。

如何使用 Spring Cloud Gateway 呢？

添加依赖：

```xml
<dependency>
  <groupId>org.springframework.cloud</groupId>
  <artifactId>spring-cloud-starter-gateway</artifactId>
</dependency>
```

Bootstrap 类上添加 @EnableDiscoveryClient 注解。

```java
@SpringBootApplication
@EnableDiscoveryClient
public class GatewayApplication {
    public static void main(String[] args) {
        SpringApplication.run(GatewayApplication.class, args);
    }
}
```

**Spring Cloud Gateway 与服务路由**

1. Spring Cloud Gateway 基本架构

Spring Cloud Gateway 中的核心概念有两个，一个是过滤器（Filter），一个是谓词（Predicate）。Spring Cloud Gateway 的整体架构图如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210308233201.png" alt="image-20210308233200967" style="zoom: 67%;" />

Spring Cloud Gateway 中的过滤器和 Zuul 中的过滤器是同一个概念。它们都可以用于在处理 HTTP 请求之前或之后修改请求本身，及对应响应结果。区别在于两者的类型和实现方式不同。

而所谓谓词，本质上是一种判断条件，用于将 HTTP 请求与路由进行匹配。Spring Cloud Gateway 内置了大量的谓词组件，可以分别对 HTTP 请求的消息头、请求路径等常见的路由媒介进行自动匹配以便决定路由结果。

2. 使用 Spring Cloud Gateway 实现路由

一条完整路由配置的基本结构，如下所示。

```yaml
spring:
  cloud:
    gateway:
      discovery:
        locator:
          enabled: true
      routes:
      #路由信息编号
      - id: testroute
        #集成负载均衡机制
        uri: lb://testservice
        #匹配以“/test”开头的请求
        predicates:
        - Path=/test/**
        #为路径添加前缀
        filters:
        - PrefixPath=/prefix
```

spring.cloud.gateway.discovery.locator.enabled 表示设置 Spring Cloud Gateway 对 HTTP 请求的路由行为。

SpringHealth 案例系统，Spring Cloud Gateway 网关服务中完整版的配置信息如下所示：

```yaml
server:
  port: 5555

eureka:
  instance:
    preferIpAddress: true
  client:
    registerWithEureka: true
    fetchRegistry: true
    serviceUrl:
        defaultZone: http://localhost:8761/eureka/

spring:
  cloud:
    gateway:
      discovery:
        locator:
          enabled: true
      routes:
      - id: userroute
        uri: lb://userservice
        predicates:
        - Path=/user/**
        filters:
        - RewritePath=/user/(?<path>.*), /$\{path}
      - id: deviceroute
        uri: lb://deviceservice
        predicates:
        - Path=/device/**
        filters:
        - RewritePath=/device/(?<path>.*), /$\{path}
      - id: interventionroute
        uri: lb://interventionservice
        predicates:
        - Path=/intervention/**
        filters:
        - RewritePath=/intervention/(?<path>.*), /$\{path}
```

以上配置添加了一个对请求路径进行重写（Rewrite）的过滤器。分别在路径上添加了“/user”“/device”和“/intervention”前缀。这种重写过滤器的效果实际上和前面介绍的前缀过滤器有相同的效果。

与 Zuul 一样，Spring Cloud Gateway 的扩展性也主要体现在过滤器组件中。

**剖析 Spring Cloud Gateway 中的过滤器**

针对过滤器，Spring Cloud Gateway 提供了一个全局过滤器（GlobalFilter）的概念。

我们首先想到了可以使用全局过滤器来对所有 HTTP 请求进行拦截，具体做法是实现 GlobalFilter 接口，示例代码如下所示。

```java
@Configuration
public class JWTAuthFilter implements GlobalFilter {
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest.Builder builder = exchange.getRequest().mutate();
        builder.header("Authorization","JWTToken");
        
        return chain.filter(exchange.mutate().request(builder.build()).build());
    }
}
```

在这个示例中，我们给所有经过 API 网关的 HTTP 请求添加了一个消息头，用来设置与 JWT Token 相关的安全认证信息。

Spring Cloud Gateway 也提供了可用于 pre 和 post 两种阶段的过滤器。以下代码展示了一个 PostGatewayFilter 的实现方式。

首先继承一个 AbstractGatewayFilterFactory 类，然后可以通过覆写 apply 方法来提供针对 ServerHttpResponse 对象的任何操作：

```java
public class PostGatewayFilterFactory extends AbstractGatewayFilterFactory {
    @Override
    public GatewayFilter apply(Config config) {
        return (exchange, chain) -> {
          return chain.filter(exchange).then(Mono.fromRunnable(() -> {
              ServerHttpResponse response = exchange.getResponse();
              //针对Response的各种处理
            }));
          };
    }
}
```

PreGatewayFilter 的实现方式也类似，只不过处理的目标一般是 ServerHttpRequest 对象。

