# 服务治理为何选择Spring Cloud

这门课，我将从技术原理、工程实践、进阶提升3个维度详细讲解Spring Cloud。

如何才能快速掌握 Spring Cloud 呢？

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120093130.png"  />

包括：

- Eureka 主要用于服务治理；
- Ribbon 用于负载均衡；
- Hystrix 用于服务之间远程调用时的容错保护；
- Feign 可以让我们通过定义接口的方式直接调用其他服务的API；
- Zuul是API网关，是客户端请求的入口，负责鉴权，路由等功能；
- Gateway是新推出的基于Spring 5的响应式网关；
- Config用于统一的配置管理；
- Sleuth用于请求链路跟踪；
- Stream用来为微服务应用构建消息驱动能力。

# 第01讲：夯实基础-Spring Boot

> 本讲内容
>
> - Spring Boot 的基本介绍；
> - Spring Boot 的使用；
> - Spring Boot 配置管理；
> - Spring Boot Starter 自定义；
> - Spring Boot 监控等多个方面的内容。

**Spring Boot 介绍**

自动装配：Spring Boot 会根据某些规则对所有配置的 Bean 进行初始化。

内嵌容器：Spring Boot 应用程序可以不用部署到外部容器中，比如 Tomcat。

应用监控：Spring Boot 中自带监控功能 Actuator，可以实现对程序内部运行情况进行监控，比如 Bean 加载情况、环境变量、日志信息、线程信息等。

Starter 包简化框架集成难度：将 Bean 的自动装配逻辑封装在 Starter 包内部。

Spring Boot 常用 Starter 包：

- spring-boot-starter-web：用于快速构建基于 Spring MVC 的 Web 项目。
- spring-boot-starter-data-redis：用于快速整合并操作 Redis。
- spring-boot-starter-data-mongodb：用于对 MongoDB 的集成。
- spring-boot-starter-data-jpa：用于操作 MySQL。
- spring-boot-starter-activemq：用于操作 ActiveMQ。

**Spring Boot Starter 自定义**

这里总结了自定义一个 Starter 需要的6个步骤：

1. 创建 Starter 项目；
2. 项目创建完后定义 Starter 需要的配置（Properties）类，比如数据库的连接信息；
3. 编写自动配置类，自动配置类就是获取配置，根据配置来自动装配 Bean；
4. 编写 spring.factories 文件加载自动配置类，Spring 启动的时候会扫描 spring.factories 文件，指定文件中配置的类；
5. 编写配置提示文件 spring-configuration-metadata.json（不是必须的），在添加配置的时候，我们想要知道具体的配置项是什么作用，可以通过编写提示文件来提示；
6. 最后就是使用，在项目中引入自定义 Starter 的 Maven 依赖，增加配置值后即可使用。

# 第02讲：服务治理-Eureka

> 预备知识：
>
> - 服务注册
>
>   服务注册指的是服务在启动时将自身的信息注册到注册中心，方便信息进行统一管理。
>
> - 服务发现
>
>   服务发现指的是客户端从注册中心获取对应服务的信息。
>
> - 服务注册与服务发现相关的动作
>
>   注册、拉取、心跳、剔除。
>
>   心跳。心跳就是健康汇报，定时跟注册中心汇报服务健康状态。
>
> - 服务注册与服务发现解决的问题
>
>   服务数量多时，修改 Nginx 的配置文件变得困难。

Netflix Eureka 是一款由 Netflix 开源的基于 REST 服务的注册中心，用于提供服务发现功能。

Spring Cloud Eureka 基于 Netflix Eureka 进行了二次封装，主要负责完成微服务架构中的服务治理功能。

**架构剖析**

Eureka 的架构主要分为 Eureka Server 和 Eureka Client 两部分。

Eureka Client 又分为 Applicaton Service（服务提供者）和 Application Client（服务消费者）。

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120093137.png)

**Eureka 部署**

开启 EurekaServer 的自动装配功能：

```java
@EnableEurekaServer
```

是否将自己的实例注册到 Eureka Server 中：

```properties
eureka.client.register-with-eureka=false
```

是否应从 Eureka Server 中获取 Eureka 的注册表信息：

```properties
eureka.client.fetch-registry=false
```

**Eureka 使用**

如何使用 Eureka Client 进行注册呢？

启用服务注册与服务发现：

```java
@EnableDiscoveryClient
```

这步操作不是必需的，因为在 spring-cloud-starter-netflix-eureka-client 的 spring.factories 文件中已经指定了所有的自动装配类。

配置服务地址：

```properties
eureka.client.serviceUrl.defaultZone=http://localhost:8761/eureka/
```

**Eureka 集群部署**

假设我们需要搭建一个由两个节点组成的集群，核心思想就是 A 节点会将自己的信息复制到 B 节点，B 节点会将自己的信息复制到 A 节点。

创建一个 master 配置文件，defaultZone 指向 8762 端口，随后创建一个 slave 配置文件，defaultZone 指向 8761 的端口。

**Eureka 注册表**

Eureka 管理的信息不是存储在数据库中的，是存储在 ConcurrentHashMap 中的。

注册表定义在 AbstractInstanceRegistry 类中，Map 的 key 是服务名称，value 是一个 Map。

value 的 Map 的 key 是服务实例的 ID, 比如这里的 monkey-article-service:192.168.31.244:2012 。value 的 Map 里的 value 是 Lease 类，Lease 中存储了实例的注册时间、上线时间等信息，还有具体的实例信息，比如 IP、端口、健康检查的地址等信息，对应的是 InstanceInfo。

Eureka 将注册的服务信息存储在内存中原因是什么呢?

- 优势在于性能高，部署简单。

- 劣势在于对存储容量的扩容难度高。

Eureka 核心操作主要有注册、续约、下线、移除，接口是 com.netflix.eureka.lease.LeaseManager。

**Eureka 集群各节点的数据同步**

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120093141.png)

通过 peerEurekaNodes.getPeerEurekaNodes() 得到 Eureka Server 的所有节点信息，在当前节点中循环进行复制操作，需要排除自己，不需要将信息同步给自己。

**Eureka 自我保护机制**

当网络故障后，所有的服务与 Eureka Server 之间无法进行正常通信，一定时间后，Eureka Server 没有收到续约的信息，将会移除没有续约的实例，这个时候正常的服务也会被移除掉，所以需要引入自我保护机制来解决这种问题。

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120093145.png)

已开启自我保护，当服务提供者 A 出现网络故障，无法与 Eureka Server 进行续约时，虽然 Eureka Server 开启了自我保护模式，但没有将该实例移除，服务消费者还是可以正常拉取服务提供者的信息，正常发起调用。

自我保护不是某个实例没正常续约就会开启，它需要满足一定的条件才会开启，我们来详细的分析自我保护开启的条件。在 AbstractInstanceRegistry 中有两个字段。

- numberOfRenewsPerMinThreshold：期望最小每分钟能够续租的次数；

- expectedNumberOfClientsSendingRenews：期望的服务实例数量。

**Eureka 健康检查**

Eureka Client 会定时发送心跳给 Eureka Server 来证明自己处于健康的状态，如下图所示。

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120093148.png)

# 第06讲：API网关服务-Zuul

本课时我们主要讲解：网关的必要性，Zuul 简介及如何自定义过滤器，Zuul 容错与回退，Zuul 使用经验分享，以及 Zuul 控制路由实例选择等内容。

**网关的必要性**

网关是所有请求的入口，承载了所有的流量，始终战斗在最前线，高并发、高可用都是网关需要面对的难题，网关的重要性可想而知。

- 动态路由

  使用网关后，客户端只需要关注网关的地址，也就是 gateway.com。不再需要关注多个 API 提供方，由网关统一路由到后端的具体服务中。

- 请求监控

  请求监控可以对整个系统的请求进行监控，详细地记录请求响应日志，可以实时统计当前系统的访问量及监控状态。

- 认证鉴权

  认证鉴权可以对每一个访问请求做认证，拒绝非法请求，保护后端的服务。

- 压力测试

  通过 Zuul 可以动态地将测试请求转发到后端服务的集群中，还可以识别测试流量和真实流量，用来做一些特殊处理。

- 灰度发布

  当需要发布新版本的时候，不会立即将老的服务停止，去发布新的服务。

**Zuul 简介**

- 过滤器

  pre 过滤器：可以在请求被路由之前调用。

  route 过滤器：在路由请求时被调用。

  post 过滤器：在 route 和 error 过滤器之后被调用。

  error 过滤器：处理请求发生错误时被调用。

- 请求生命周期

  当一个请求进来时，会先进入 pre 过滤器，在 pre 过滤器执行完后，接着就到了 routing 过滤器中，开始路由到具体的服务中，路由完成后，接着就到了 post 过滤器中，然后将请求结果返回给客户端。如果在这个过程中出现异常，则会进入 error 过滤器中，这就是请求在整个 Zuul 中的生命周期。

  ![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120093154.png)

# 第07讲：分布式配置中心-Apollo


