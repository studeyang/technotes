# 开篇词 | 为什么你要学习微服务架构？

微服务架构中，经常会遇到下面问题。

- 服务实例太多怎么办？

当系统中存在大量独立服务时，如何有效识别和管理这些服务的实例？这将成为一大挑战！分布式系统，一定要能够实时对这些服务实例进行治理。

- 服务调用关系太杂乱怎么办？

服务数量所衍生的另一个问题，是服务调用之间的关系会变得混乱，客户端与各个服务之间也会存在较高的耦合度，分布式系统需要提供简洁而明确的入口供客户端访问。

- 服务访问出错了怎么办？

分布式环境下的调用，与单体系统中的方法级调用不同。服务间的跨进程调用可能出现各种意想不到的问题，这就需要在服务访问出错时进行合理的容错处理。

- 配置信息散落在各个服务中怎么办？

一旦系统被拆分成多个独立服务，分布式系统就需要确保分散在每个服务中的配置信息，以及所有服务在开发、测试和生产等环境中的配置信息得到统一管理。

- 服务调用链路太长怎么办？

服务远程调用的另一个问题是调用链路可能会很长，需要对整个调用链路进行监控和跟踪，从而高效发现服务调用过程中的异常场景和性能问题。

针对以上问题，解决方案如下。

- 服务治理：为了有效管理分布式系统中存在的大量服务实例，微服务架构引入了服务发现和服务注册机制，使得服务实例的管理变得自动化、透明化。

- API 网关：为了降低服务客户端与服务提供者之间的耦合度，更好地简化调用过程，微服务架构专门提供了一个 API 网关，用来优化面向客户端的 API 设计。

- 服务容错：为了解决服务访问出错问题，微服务架构中提供了服务隔离、服务熔断和服务回退等面向服务调用端的有效容错机制。

- 配置中心：为了更好地组织和管理散落在各个服务中的配置信息，微服务架构提供了一个配置中心来集中化管理。

- 链路跟踪：为了高效监控服务调用的健康状态以及全链路的数据流转，微服务架构提供了链路跟踪机制，来对各个服务之间的调用过程进行统一管理。

**课程设计**

基础篇（1~3）：这部分介绍微服务架构的基本要素和技术体系。

实践篇（4~34）：

- 服务治理（4~8）
- API 网关（9~11）
- 服务容错（12~15）
- 配置中心（16~19）
- 事件驱动架构（20~24）
- 服务访问安全（25~28）
- 链路跟踪（29~31）
- 微服务测试（32~34）

# 基础篇（1~3）

# 01 | 追本溯源：究竟什么样的架构才是微服务架构？

微服务架构的提出者 Martin Fowler 在其文章Microservices中定义了包括服务组件化、去中心化、基础设施自动化在内的多个微服务架构特点。基于这些特点提炼出构建微服务架构三大要素，即业务建模、技术体系和研发过程。

**微服务架构的第一要素：业务建模**

对于领域的划分，业界主流的分类方法认为，系统中的各个子域可以分成核心子域、支撑子域和通用子域三种类型，其中系统中的核心业务属于核心子域，专注于业务某一方面的子域称为支撑子域，可以作为某种基础设施的功能可以归到通用子域。下图就是一个典型的领域划分示例，来自电商系统：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210226231615.png" alt="image-20210226231615835" style="zoom:50%;" />

服务建模本质上是一个为了满足业务需求，并通过技术手段将这些业务需求转换为可实现服务的过程。我们可以把业务体系中的服务分成如下几种类型：基础服务、通用服务、定制服务和其他服务等。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210226231923.png" alt="image-20210226231923650" style="zoom:50%;" />

**微服务架构的第二要素：技术体系**

本课程基于目前业界主流的微服务实现技术提炼了八大技术体系，包括服务通信、服务治理、服务路由、服务容错、服务网关、服务配置、服务安全和服务监控。

1. 服务通信

微服务架构而言，我们关注的是网络连接模式、I/O 模型和服务调用方式。

基于TCP 协议的网络连接有两种基本方式，也就是通常所说的长连接和短连接。

服务之间通信的另一个关注点是 I/O 模型。I/O 模型也有阻塞式 I/O 和非阻塞式 I/O 等多种实现方式。

服务通信的另一个主题是调用方式，这方面同样存在同步调用和异步调用两大类实现机制，这两大类机制对于开发人员使用开发框架的方式有很大影响。

2. 服务治理

当服务数量达到一定量级时，就需要引入独立的媒介来管理服务的实例，这个媒介一般被称为服务注册中心。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210226232434.png" alt="image-20210226232434052" style="zoom:50%;" />

服务注册中心是保存服务调用所需的路由信息的存储仓库，也是服务提供者和服务消费者进行交互的媒介，充当着服务注册和发现服务器的作用。

3. 服务路由

当客户端请求到达集群，如何确定由哪一台服务器进行请求响应呢？这就是服务路由问题。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210226232616.png" alt="image-20210226232616544" style="zoom:50%;" />

为实现精细化的路由管理，这时候我们就可以采用路由规则。路由规则常见的实现方案是白名单或黑名单，即把需要路由的服务地址信息（如服务 IP）放入可以控制是否可见的路由池中进行路由。同样，路由规则也是微服务开发框架的一项常见功能。

4. 服务容错

对于分布式环境中的服务而言，服务在自身失败引发生错误的同时，还会因为依赖其他服务而导致失败。除了比较容易想到和实现的超时、重试和异步解耦等手段之外，我们需要考虑针对各种场景的容错机制。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210226232908.png" alt="image-20210226232907988" style="zoom:50%;" />

5. 服务网关

服务网关也叫 API 网关，封装了系统内部架构，为每个客户端提供一个定制的 API。在微服务架构中，服务网关的核心要点是，所有的客户端和消费端都通过统一的网关接入微服务，在网关层处理所有的非业务功能。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210226232952.png" alt="image-20210226232952324" style="zoom:50%;" />

6. 服务配置

在微服务架构中，考虑到服务数量和配置信息的分散性，一般都需要引入配置中心的设计思想和相关工具。与注册中心一样，配置中心也是微服务架构中的基础组件，其目的也是对服务进行统一管理，区别在于配置中心管理的对象是配置信息而不是服务的实例信息。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210226233013.png" alt="image-20210226233013130" style="zoom:50%;" />

7. 服务安全

在对微服务架构的学习过程中，服务安全是一块非常重要但又容易被忽视的内容。一般意义上的访问安全性，都是围绕认证和授权这两个核心概念来展开的。也就是说我们首先需要确定用户身份，然后再确定这个用户是否有访问指定资源的权限。站在单个微服务的角度讲，我们系统每次服务访问都能与授权服务器进行集成以便获取访问 Token。站在多个服务交互的角度讲，我们需要确保 Token 在各个微服务之间的有效传播。另一方面，服务内部，我们可以使用不同的访问策略限制服务资源的访问。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210226233029.png" alt="image-20210226233029545" style="zoom:50%;" />

8. 服务监控

在微服务架构中，当服务数量达到一定量级时，我们难免会遇到两个核心问题。一个是如何管理服务之间的调用关系？另一个是如何跟踪业务流的处理过程和结果？这就需要构建分布式服务跟踪机制。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210226233110.png" alt="image-20210226233110180" style="zoom:50%;" />

**微服务架构的第三要素：研发过程**

当寻找把一个大的应用程序进行拆分的方法时，研发过程通常都会围绕产品团队、项目管理、大前端和服务器端团队而展开，这些团队也就是通常所说的职能团队。任何一个需求，无论大小，都将导致跨团队协作，从而增加沟通和协作成本。而微服务架构则倾向围绕业务功能的组织来分割服务，而不是面向某项技术能力。因此，团队是跨职能的特征团队，每个服务都围绕着业务进行构建，并且能够被独立部署到生产环境。

# 02 | 顶级框架：Spring Cloud 是一款什么样的微服务开发框架？

**从 Spring Boot 到 Spring Cloud**

Spring Boot 特性主要体现在开发过程的简单化，包括支持快速构建项目、不依赖外部容器独立运行、开发部署效率高，以及与云平台天然集成等。

在微服务架构中，Spring Cloud 构建在 Spring Boot 之上，继承了 Spring Boot 的多项功能特性，使得开发微服务变得简单而高效。

**Spring Cloud 中的核心组件**

Spring Cloud 中包含了开发一个完整的微服务系统所需的几乎所有技术组件，包括服务注册和发现、API 网关、配置中心、消息处理、负载均衡、熔断器、数据监控等。

1. Spring Cloud Netflix Eureka 与服务治理

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210301220113.png" alt="image-20210301220009494" style="zoom:50%;" />

在服务治理场景下，这些组件构成了一个完整的从服务注册、服务发现到服务调用的流程。

2. Spring Cloud Gateway 与服务网关

Spring Cloud Gateway 构建在最新版本的 Spring 5 和响应式编程框架 Project Reactor 之上，提供了非阻塞的 I/O 通信机制。

<img src="/Users/yanglulu/Library/Application Support/typora-user-images/image-20210301220252298.png" alt="image-20210301220252298" style="zoom:50%;" />

3. Spring Cloud Circuit Breaker 与服务容错

Spring Cloud Circuit Breaker 是对熔断器实现方案的一种抽象。在该组件的内部，Spring Cloud Circuit Breaker 集成了Netfix Hystrix、Resilience4J、Sentinel、Spring Retry这四种熔断器实现工具。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210301220454.png" alt="image-20210301220454935" style="zoom:50%;" />

4. Spring Cloud Config 与配置中心

在 Spring Cloud 中，集中化配置中心服务器的实现依赖于 Spring Cloud Config，而配置仓库的实现方案除了本地文件系统之外，还支持Git、SVN等常见的版本控制工具。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210301220555.png" alt="image-20210301220555221" style="zoom: 50%;" />

5. Spring Cloud Stream 与事件驱动

Spring Cloud Stream 中的 Source 组件是真正生成消息的组件，然后消息通过 Channel 传送到 Binder。这里的 Binder 是一个中间层组件，通过 Binder 可以与特定的消息中间件进行通信。

在 Spring Cloud Stream 中，目前已经内置集成的消息中间件包括 RabbitMQ 和 Kafka。消息消费者则同样通过 Binder 从消息传递系统中获取消息，消息通过 Channel 将流转到 Sink 组件。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210301220850.png" alt="image-20210301220850022" style="zoom:50%;" />

6. Spring Cloud Security 与服务安全

Spring Cloud Security 具备众多特点，包括基于流行的OAuth2 协议的授权机制，以及基于 Token的资源访问保护机制。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210301220958.png" alt="image-20210301220958206" style="zoom:50%;" />

7. Spring Cloud Sleuth 与链路跟踪

我们可以通过Spring Cloud Sleuth自动完成服务调用链路的构建。

任何通过 HTTP 端点接收到的请求或使用 RestTemplate 发出的请求都可以被 Spring Cloud Sleuth 自动收集日志。

同时它也能无缝支持通过由 API 网关 Zuul 发送的请求，以及基于 Spring Cloud Stream 等消息传递技术发送的请求。

并且，Spring Cloud Sleuth 也兼容了 Zipkin、HTrace 等第三方工具的应用和集成，从而实现对服务依赖关系、服务调用时序，以及服务调用数据的可视化，如下图所示。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210301221343.png" alt="image-20210301221343106" style="zoom:50%;" />

8. Spring Cloud Contracts 与服务测试

在微服务架构中，当不同服务之间进行交互和集成时，测试的关注点就变成如何确保服务定义和协议级别的正确性和稳定性，也就是所谓的端到端测试。

Spring Cloud Contract 框架采用了服务桩（Stub） 实现机制来确保特定服务版本的各个服务之间交互过程的正确性，如下所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210301221612.png" alt="image-20210301221612195" style="zoom:50%;" />

# 03 | 案例驱动：如何通过实战案例来学习 Spring Cloud 框架？

在物联网和智能穿戴式设备日益发达的当下，试想一下这样的日常场景。

患者通过智能手环、便携式脉诊仪等一些智能穿戴式设备检测自身的各项健康信息，然后把这些健康信息实时上报到云平台，云平台检测到用户健康信息中的异常情况时会通过人工或自动的方式进行一定的健康干预，从而确保用户健康得到保证。

这是大健康领域非常典型的一个业务场景，也是我们案例的来源。

**SpringHealth：案例驱动**

服务建模是案例分析的第一步。服务建模包括 子域与界限上下文的划分 以及 服务拆分和集成策略的确定。

SpringHealth 包含的业务场景比较简单，用户佩戴着各种穿戴式设备，云平台中的医护人员可以根据这些设备上报的健康信息生成健康干预。而在生成健康干预的过程中，我们需要对设备本身以及用户信息进行验证。从领域建模的角度进行分析，我们可以把该系统分成三个子域，即：

- 用户（User）子域，用于用户管理，用户可以通过注册成为系统用户，同时也可以修改或删除用户信息，并提供用户信息有效性验证的入口。

- 设备（Device）子域，用于设备管理，医护人员可以查询某个用户的某款穿戴式设备以便获取设备的详细信息，同时基于设备获取当前的健康信息。

- 健康干预（Intervention）子域，用于健康干预管理，医护人员可以根据用户当前的健康信息生成对应的健康干预。当然，也可以查询自己所提交健康干预的当前状态。

从子域的分类上讲，用户子域比较明确，显然应该作为一种通用子域。而健康干预是 SpringHealth 的核心业务，所以应该是核心子域。至于设备子域，在这里比较倾向于归为支撑子域。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210301224022.png" alt="image-20210301224022434" style="zoom: 33%;" />

基于以上分析，我们可以把 SpringHealth 划分成三个微服务，即 user-service、device-service 和 intervention-service。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210301224241.png" alt="image-20210301224241826" style="zoom: 33%;" />

以上述三个服务构成了 SpringHealth 的业务主体，属于业务微服务。

**SpringHealth：服务设计**

纵观整个 SpringHealth 系统，除了前面介绍的三个业务微服务之外，实际上更多的服务来自非业务性的基础设施类服务。

1. 服务列表

整个 SpringHealth 的所有服务如下表所示。对于基础设施类服务，命名上我们统一以 -server 来结尾，而对于业务服务，则使用的是 -service 后缀。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210301224814.png" alt="image-20210301224814453" style="zoom:50%;" />

2. 服务数据

我们针对三个业务服务，建立独立的三个数据库，数据库的访问信息通过配置中心进行集中管理，如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210301225020.png" alt="image-20210301225019975" style="zoom:50%;" />

**SpringHealth：代码工程**

服务运行时上存在一定的依赖性。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210301225221.png" alt="image-20210301225221324" style="zoom:50%;" />

**案例之外：从案例实战到原理剖析**

我们将通过源码解析来剖析 Spring Cloud 中核心组件的工作原理，典型的场景包括以下几点：

- 服务治理原理剖析。服务治理的原理剖析涉及两大块内容，一块是构建 Eureka 服务器以及使用 Eureka 客户端的实现机制，另一块则是客户端负载均衡组件 Ribbon 的基本架构和实现原理。
- 服务网关原理剖析。服务网关中，我们选择基于 Zuul 网关的设计思想、功能组件以及路由机制来对它的实现原理进行详细的展开。
- 服务容错原理剖析。针对服务容错，我们选择以 Hystrix 为基础，来分析 HystrixCircuitBreaker 核心类的底层实现原理以及基于滑动窗口实现数据采集的运行机制。
- 服务配置原理剖析。在掌握 Spring Cloud Config 的配置中心应用方式的基础上，我们将重点关注服务器端和客户端的底层交互机制，以及配置信息自动更新的工作原理。
- 事件通信原理剖析。作为集成了 RabbitMQ 和 Kafka 这两款主流消息中间件的 Spring Cloud Stream 框架，我们的关注点在于它对消息集成过程的抽象以及集成过程的实现原理。

# 服务治理（4~8）

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

<img src="/Users/yanglulu/Library/Application Support/typora-user-images/image-20210302225006561.png" alt="image-20210302225006561" style="zoom:33%;" />

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

我们在 intervention-service 的启动类 InterventionApplication中，通过 @LoadBalanced 注解创建 RestTemplate。

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

