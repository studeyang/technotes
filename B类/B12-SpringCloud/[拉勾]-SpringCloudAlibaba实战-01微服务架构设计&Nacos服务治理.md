> 来源：拉勾教育《Spring Cloud Alibaba实战》

# 开篇词 | Spring Cloud Alibaba 未来的微服务生态标准

**为什么要掌握微服务架构？**

分布式架构演进的几十年过程中出现了几十种架构模式，但目标只有一个，解决上一代架构遗留的各种问题，微服务架构也不例外。

而微服务架构解决的，则是基于重量级 ESB 的 SOA 架构的扩展与维护的问题。

**为什么 Spring Cloud Alibaba 会迅速崛起**

这几年以 Netfilix Eureka 为代表的 Spring Cloud 核心中间件纷纷停止更新，再加上许多组件设计老旧，在性能上已无法满足互联网大厂的要求，我们迫切需要一套符合中国特色的微服务架构解决方案。

Spring Cloud Alibaba 就是在这种背景下诞生的，Spring Cloud Alibaba 是国产的微服务开发一站式解决方案，与原有 Spring Cloud 兼容的同时对微服务生态进行扩展，通过添加少量的配置注解，便可实现更符合国情的微服务架构。

![image-20210803232355361](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210803232355.png)

**课程设计**

- 模块一 微服务架构设计

  主要介绍什么是微服务架构，以及微服务架构设计时一些常见问题。

- 模块二 Nacos 服务治理

  Nacos 注册中心是整个微服务架构的核心，我将详细介绍 Nacos的安装、使用与集群搭建过程，同时结合图文介绍 Nacos 服务发现的底层原理。

- 模块三 微服务通信

  当服务间要产生彼此通信，在 Spring Cloud Alibaba 中支持 RPC 与 RESTful 两种方案，对应产品为 Dubbo 与 OpenFeign ，本阶段我将给出这些组件的最佳实践以及原理分析。

- 模块四 系统保护

  Sentinel 是 Alibaba 提供的服务保护中间件，利用 Sentinel 可以有效预防分布式架构的系统性崩溃，本阶段我们将讲解 Sentinel 的限流、熔断、代码控制等最佳实践。

- 模块五 高级特性

  本阶段我们要讲解 Spring Cloud Alibaba 提供的众多高级特性。例如：配置中心、链路追踪、性能监控、分布式事务、消息队列等，这些技术我们都将从应用入门到原理分析逐一进行讲解。

- 模块六 微服务架构最佳实践

  在这个阶段我将拿出自己的私货，为你讲解微服务架构的综合运用与项目实践。在这里我们会接触到 Seata 分布式事务架构、多级缓存设计、老项目升级改造策略、微服务认证与授权体系、数据一致性解决方案以及基于容器化的 DevOps 运维架构。

**学习门槛**

只要是会用 Java，了解过 Spring Boot 框架，就不存在门槛可以放心“食用”。

# 模块一：微服务架构设计

# 01 | 一探究竟：从架构的演变看微服务化架构

**什么是微服务架构**

所谓微服务架构风格是一种将单机应用程序开发为一组小型服务的方法，每个小服务运行在自己的进程中，并以轻量级的机制来进行通信。

这些服务围绕着业务能力所建立，并且由完全自动化的部署机构独立部署，这些服务的集中管理只有最低限度，可以用不同的编程语言编写并使用不同的数据库存储技术。

**垂直划分的分布式应用具有哪些问题？**

要弄清楚微服务架构，首先我们要看以往的分布式架构到底有哪些问题。下面是一个借款服务项目。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210803232843.png" alt="image-20210803232843136" style="zoom:50%;" />

具体的业务流程是：

1. 借款人门户负责收集借款人的需求；
2. 将借款人的信息送入信审和风控系统，风控进行评估；
3. 如果满足借款要求，则将这些信息发给贷后系统来进行实际的放款操作；
4. 最后在实际的分期还款过程中，通知借款人定期还款。

这样的系统架构会有什么问题呢？

- 问题一：系统间通信困难

WebService 跨进程调用时，需要双方持有相同的传输对象才可以完成数据的交互。但如果服务的提供者，他将接口以及传输对象进行升级后，而客户端没有及时更新的话，此时便会因为对象的状态不一致导致传输失败的情况。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210803234627.png" alt="image-20210803234627878" style="zoom:50%;" />

- 问题二：缺少动态发现机制

贷后系统为了高可用的要求，提供了 IP 为 10 和 11 的两个节点。但随着业务的发展，贷后系统加入了额外的两个节点，它们分别是 12 和 13。我们必须手动添加信审系统的 IP 列表，以及重启应用才可以做到。增加了两个系统之间的耦合，提高了项目维护的难度。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210803235043.png" alt="image-20210803235043421" style="zoom:50%;" />

- 问题三：系统间的调用关系复杂

难以梳理的调用关系：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210803235211.png" alt="image-20210803235211465" style="zoom:50%;" />

- 问题四：过度的重复建设

在公司进行项目开发时，每一个团队负责独立的系统，而这些系统往往需要一些通用的底层设施。例如：用户认证与权限控制、黑名单白名单、流量控制与系统异常的处理以及系统参数的配置管理等模块。而这些模块在每一个子系统中都要重复的进行开发，这显然是一件费时费力的事情，不利于数据的集中管理。

**微服务架构又是如何解决这些问题的**

![image-20210803233427544](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210803233427.png)

- 问题一：系统间通信困难

微服务使用 RESTful 通信，RESTful 是基于 HTTP 协议的轻量级通信方式。通信时是并不强制要求调用端必须对代码进行升级，服务端与调用端是彼此兼容的。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210804215334.png" alt="image-20210804215334194" style="zoom: 67%;" />

- 问题二：缺少动态发现机制

微服务架构有一个关键组件名为注册中心，所有的 IP 地址以及节点的状态都是由注册中心来维护的。

![image-20210804215459904](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210804215459.png)

- 问题三：系统间的调用关系复杂

微服务内建链路跟踪体系，通过可视化的形式，可以直观了解服务间的通信过程以及通信的状态。

![image-20210804215615229](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210804215615.png)

- 问题四：过度的重复建设

微服务体系中，有一个用户认证中心的服务，在前端应用实际发起请求前，对用户的身份和权限来进行判断。

# 02 | 经验教训：微服务设计时的五条宝贵经验

**微服务架构的新挑战**

下面我从网络、性能、运维成本、组织架构与集成测试五个方面分别进行阐述。

- 第一点，跨进程通信带来的新问题

架构师在设计时必须考虑上下游系统因为网络因素无法通信的情况，要假设网络是不可靠的，并设计微服务在网络异常时也能进行符合预期的异常处理。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210804221641.png" alt="image-20210804221641239" style="zoom: 67%;" />

- 第二点，较高的响应延迟

跨进程、跨网络的微服务通信在网络传输与消息序列化带来的延迟是不可被忽略的，尤其是在五个以上微服务间消息调用时，网络延迟对于实时系统的影响是很大的。

- 第三点，运维成本会直线上升

对于微服务架构而言，每一个服务都是可独立运行、独立部署、独立维护的业务单元，运维人员每天面对成百上千台服务器发布几十次已是家常便饭，传统手动部署显然已经无法满足互联网的快速变化。

- 第四点，组织架构层面的调整

在微服务的实施过程中，是以业务模块进行团队划分，每一个团队是内聚的，要求可以独立完成从调研到发版的全流程，尽量减少对外界的依赖。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210804222009.png" alt="image-20210804222008988" style="zoom: 50%;" />

- 第五点，服务间的集成测试举步维艰

要获取准确的测试结果，必须搭建完整的微服务环境，光这一项就需要花费大量的人力物力。同时，因为微服务是跨网络通信，网络延迟、超时、带宽、数据量等因素都将影响最终结果，测试结果易产生偏差。

**微服务最佳实践**

在微服务拆分过程中，通常会从业务场景、团队能力、组织架构等多种因素综合考虑，这特别考验架构师的业务能力。一般来说，我们总结出几点通用原则：

- 第一点，微服务的划分原则

单一职责原则：每一个微服务只做好一件事，体现出“高内聚、低耦合”，尽量减少对外界环境的依赖。

服务依赖原则：避免服务间的循环引用，在设计时就要对服务进行分级，区分核心服务与非核心服务。

Two Pizza Team原则：团队要小到让每个成员都能做出显著的贡献，并且相互依赖，有共同目标，以及统一的成功标准。通常 4~6 人是比较理想的规模。

- 第二点，为每一个微服务模块明确使命

```
模板
XX 微服务用来
在出现痛点场景的情况下
解决现有的 XX 问题
从而达到了 XXX 的效果
体现了微服务的价值
```

```
示例
商品检索微服务用来
在商品数据全量多维度组合查询的情况下
解决了 MySQL 数据库全表扫描查询慢的问题
从而让查询响应降低到 50ms 以下
有效提升了用户体验
```

拆与合是伴随着公司业务的演进而变化的，一切以解决问题为准。

- 第三点，微服务确保独立的数据存储

为每一个微服务提供符合自身业务特性的数据库。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210804222615.png" alt="image-20210804222615688" style="zoom: 50%;" />

- 第四点，服务间通信优先采用聚合器模式

在微服务间通信时存在两种消息传递模式：链式模式与聚合器模式。

下图所展示的是链式模式，请求按业务流程在各个服务间流转，最终处理完成返回客户端。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210804222725.png" alt="image-20210804222725637" style="zoom:50%;" />

链式模式调用的整体成功率等于单个服务成功率的乘积，假设每个服务可靠性为 90%，一个业务在 4 个服务执行后的最终成功率只有 90%\*90%\*90%\*90%≈66%，有将近一半的请求会处理失败，这是无法接受的。

聚合器模式则是通过服务作为入口，组装其他服务的调用。以“订单流程服务”为例，将“订单”“支付”“库存”服务进行聚合，一个服务实现了下单、支付、减库存的完整流程。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210804223030.png" alt="image-20210804223030574" style="zoom:50%;" />

采用聚合器模式后，业务流程与编排集中在“订单流程服务”中，可对整体业务进行有效编排，支付与扣库存可以并行调用，可以有效提高系统的性能。

- 第五点，不要强行“微服务”化

架构是解决当前需求和痛点而演进的。在满足需要的前提下，选择合适的而不是选择最好的，合理降低成本才是好架构师该考虑的事情。

**微服务架构的适用场景**

- 新规划的大型业务系统

微服务强调“高内聚，低耦合”，每一个团队负责一个服务，这就意味着从根本上和传统的单体应用有本质不同，从规划阶段采用微服务架构是再好不过的。

- 敏捷的小团队系统

公司在大型项目微服务实践前，往往这类边缘化的小项目会起到“试验田”的作用， 引入快速迭代、持续交付等模式，积累适合本公司特点的微服务实践经验，再将这些经验扩大到其他大型项目中。

- 历史的大型留存业务系统

重构时可以将某一个部分剥离为微服务独立运行，确保无误后再继续剥离出下一个服务，通过抽丝剥茧一般的剥离，逐步将原有大系统剥离为若干子服务，虽然过程十分痛苦，但这是必须做的事情。

**不适合引入微服务的场景**

- 微型项目

系统压力很小，需求变化也不大，利用单体架构便可以很好解决，使用分布式架构反而增加了架构复杂度，让系统更容易不稳定。

- 对数据响应要求高的系统

# 模块二：Nacos 服务治理

# 03 | 顶层设计：微服务生态与 Spring Cloud Alibaba

Java 领域微服务是如何实现的？

**通用的微服务架构应包含哪些组件？**

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210804224347.png" alt="image-20210804224347031" style="zoom: 50%;" />

- 组件1：注册中心（Service Registry）

如何发现新服务节点以及检查服务节点的状态？微服务节点在启动时会将自身的服务名称、IP、端口等信息在注册中心中进行登记，注册中心会定时检查该节点的运行状态。注册中心通常会采用心跳机制最大程度保证其持有的服务节点列表都是可用的。

![image-20210804225444075](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210804225444.png)

- 组件2：负载均衡（Load Balance）

如何发现服务及负载均衡如何实现？微服务彼此调用首先通过服务名在注册中心查询该服务拥有哪些可用节点，通过负载均衡策略选择适合的节点发起实质的通信请求。

![image-20210804225659184](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210804225659.png)

- 组件3：服务通信（Communication）

服务间如何进行消息通信？通常是 HTTP RESTful 风格。在 Spring Cloud 中提供了 Feign 和 RestTemplate 两种技术屏蔽底层实现 RESTful 通信细节，所有开发者都是基于封装后统一的SDK进行开发，这有利于团队间协作。

- 组件4：API 服务网关（API Gateway）

如何对使用者暴露服务 API？微服务架构引入服务网关控制用户的访问权限，是外部环境访问内部微服务的唯一途径。

- 组件5：配置中心（Config Management）

如何集中管理众多服务节点的配置文件？通过部署配置中心服务器，将原本分散的配置文件从应用中剥离，集中转存到配置中心。

![image-20210804230129721](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210804230129.png)

- 组件6：集中式日志管理（Centralized Logging）

如何收集服务节点的日志并统一管理？业内常见的方案有 ELK、EFK，通过搭建独立的日志收集系统，定时抓取增量日志形成有效的统计报表，为决策提供数据支撑。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210804230310.png" alt="image-20210804230310522" style="zoom:50%;" />

- 组件7：分布式链路追踪（Distributed Tracing）

如何实现服务间调用链路追踪？Zipkin 可以记录一个完整业务逻辑涉及的每一个微服务的运行状态，再通过可视化链路图展现。

![image-20210804230416461](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210804230416.png)

- 组件8：服务保护（Service Protection）

如何对系统进行链路保护，避免微服务雪崩？在服务间通信过程中，如果某个微服务出现响应高延迟可能会导致线程池满载，严重时会引起系统崩溃。

**Spring Cloud 是如何支撑微服务架构的？**

![image-20210804230610887](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210804230610.png)

**Spring Cloud Alibaba**

Spring Cloud Alibaba 是直接隶属于 Spring Cloud 的子项目。是国产的微服务开发一站式解决方案，与原有 Spring Cloud 兼容的同时对微服务生态进行扩展，通过添加少量的配置注解，便可实现更符合国情的微服务架构。

![image-20210804231050448](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210804231050.png)

相比 Spring Cloud，Spring Cloud Alibaba 对服务注册、配置中心与负载均衡功能都整合进 Nacos，这样简化了微服务架构的复杂度，出问题的概率也会降低。

原有的服务保护组件也调整为 Sentinel，相较Hystrix功能更强大，使用也更加友好。

# 04 | 服务治理：Nacos 如何实现微服务服务治理

**Nacos 注册中心的特性**

“一个更易于构建云原生应用的动态服务发现、配置管理和服务管理平台”。Nacos 具备以下职能：

- 服务发现及管理；
- 动态配置服务；
- 动态 DNS 服务。

**Nacos 的快速部署**

- 获取安装包

访问 Nacos GitHub：https://github.com/alibaba/nacos/releases/获取 Nacos 最新版安装包 nacos-server-1.4.0.tar.gz。

```shell
[root@server-1 local]# tar -xvf nacos-server-1.4.0.tar.gz
```

- 以单点方式启动

```shell
[root@server-1 local]# cd nacos/bin
[root@server-1 bin]# sh startup.sh -m standalone
```

- 开放防火墙端口

默认 CentOS 系统并没有对外开放 7848/8848 端口，需要设置防火墙对 7848/8848 端口放行。

```shell
[root@server-1 bin]# firewall-cmd --zone=public --add-port=8848/tcp --permanent
success
[root@server-1 bin]# firewall-cmd --zone=public --add-port=7848/tcp --permanent
success
[root@server-1 bin]# firewall-cmd  --reload
success
```

最后，就可以访问了：http://192.168.31.102:8848/nacos。

**微服务如何接入 Nacos**

- 引入 pom.xml 依赖

```xml
<dependency>
    <groupId>com.allibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
</dependency>
```

- 配置 Nacos 地址

```properties
# 应用名称，默认也是在微服务中注册的微服务 ID
spring.application.name=sample-service
# 配置 Nacos 服务器的IP地址
spring.cloud.nacos.discovery.server-addr=192.168.31.102:8848
#连接 Nacos 服务器使用的用户名、密码，默认为 nacos
spring.cloud.nacos.discovery.username=nacos
spring.cloud.nacos.discvery.password=nacos
#微服务提供Web服务的端口号
server.port=9000
```

启动服务后，打开：http://192.168.31.102:8848/nacos。

![image-20210805232918709](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210805232918.png)

**Nacos 注册中心的心跳机制**

下图阐述了微服务与 Nacos 服务器之间的通信过程。在微服务启动后每过5秒，会由微服务内置的 Nacos 客户端主动向 Nacos 服务器发起心跳包（HeartBeat）。

![image-20210805233326517](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210805233326.png)

心跳包会包含当前服务实例的名称、IP、端口、集群名、权重等信息。

naming 模块在接收到心跳包后，首先根据 IP 与端口判断 Nacos 是否存在该服务实例？如果实例信息不存在，在 Nacos 中注册登记该实例。

Nacos Server 每过 20 秒对“实例 Map”中的所有“非健康”实例进行扫描，如发现“非健康”实例，随即从“实例 Map”中将该实例删除。

> 实例地址变化后，这 20 秒内如何容错？

# 05 | 高可用保证：Nacos 如何有效构建注册中心集群

**如何在生产环境部署 Nacos 集群**

![image-20210806230205479](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210806230210.png)

Nacos 集群架构的设计要点：

1. 通过域名方式屏蔽后端容易产生变化的 IP 地址；
2. Nacos 节点对外暴露 8848 与 7848 端口；
3. Nacos 在集群环境下需要持久化应用配置、用户权限、历史信息等内置数据；
4. 不建议直接将服务器物理 IP 对外暴露，而是额外增加 VIP（虚拟 IP），通过 DNS 服务绑定 VIP；

**Nacos 集群的部署过程**

- 第一步，环境准备

Nacos 因为选举算法的特殊性，要求最少三个节点才能组成一个有效的集群。

> 运行最低配置：CPU 1核 / 内存 2G / 硬盘 2G 以上
>
> 生产环境配置：CPU 4核 / 内存 8G / 硬盘 10G 以上

- 第二步，下载安装 Nacos

- 第三步，配置数据库

- 第四步，Nacos 集群节点配置

在 /nacos/config 目录下提供了集群示例文件 cluster.conf.example，根据样例配置 cluster.conf

```properties
192.168.163.131:8848
192.168.163.132:8848
192.168.163.133:8848
```

- 第五步，启动 Nacos 服务器

```shell
sh /usr/local/nacos/bin/startup.sh
```

- 第六步，微服务接入

在 application.properties 配置 Nacos 集群的任意节点：

```properties
# 应用名称，默认也是在微服务中注册的微服务 ID
spring.application.name=sample-service
# 配置 192.168.163.131/132/133 都可以接入 Nacos
spring.cloud.nacos.discovery.server-addr=192.168.163.131:8848,192.168.163.132:8848,192.168.163.133:8848
#连接 Nacos 服务器使用的用户名、密码，默认为 nacos
spring.cloud.nacos.discovery.username=nacos
spring.cloud.nacos.discvery.password=nacos
#微服务提供 Web 服务的端口号
server.port=9000
```

**Nacos 节点间的数据同步过程**

![image-20210807221034759](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210807221040.png)

在 Raft 算法中，只有 Leader 才拥有数据处理与信息分发的权利。因此当微服务启动时，假如注册中心指定为 Follower 节点，则步骤如下：

第一步，Follower 会自动将注册心跳包转给 Leader 节点；

第二步，Leader 节点完成实质的注册登记工作；

第三步，完成注册后向其他 Follower 节点发起“同步注册日志”的指令；

第四步，所有可用的 Follower 在收到指令后进行“ack应答”，通知 Leader 消息已收到；

第五步，当 Leader 接收过半数 Follower 节点的 “ack 应答”后，返回给微服务“注册成功”的响应信息。


