# 开篇词

Spring Boot 框架使配置变简单、使编程变简单、使部署变简单、使监控变简单。总结来说有如下特点。

- 看上去简单，实则复杂

Spring Boot 提供了很多隐式的功能，比如自动配置，它将系统开发的复杂度隐藏得很深。

- 技术体系和组件众多

Spring Boot 提供了一大批功能组件，这些功能组件构成了庞大的技术体系。

- 框架集成的“坑”不少

Spring Boot 是一个集成性的框架，内部整合了市面上很多开源框架。

Web 应用程序总体可以拆分为下图的维度。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210330224842.png" alt="image-20210330224841931" style="zoom:50%;" />

可以从下面8个部分进行学习。

- 第 1 部分（01~02），开启 Spring Boot 框架的学习之旅
- 第 2 部分（03~05），使用 Spring Boot 构建多维度配置层
- 第 3 部分（06~10），使用 Spring Boot 构建数据访问层
- 第 4 部分（11~13），使用 Spring Boot 构建 Web 服务层
- 第 5 部分（14~16），使用 Spring Boot 构建消息通信层
- 第 6 部分（17~19），使用 Spring Boot 构建系统安全层
- 第 7 部分（20~22），使用 Spring Boot 构建系统监控层
- 第 8 部分（23~24），测试 Spring Boot 应用程序

# 第1部分

# 01 | 家族生态：Spring 家族的技术体系

**Spring 家族技术生态全景图**

我们访问 Spring 的官方网站（https://spring.io/）来对这个框架做宏观的了解。在 Spring 的主页中，展示了下面这张图：

![image-20210330230706127](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210330230706.png)

这里罗列了 Spring 框架的七大核心技术体系，分别是微服务架构、响应式编程、云原生、Web 应用、Serverless 架构、事件驱动以及批处理。

这些技术体系各有其应用场景。

例如，如果我们想要实现日常报表等轻量级的批处理任务，而又不想引入 Hadoop 这套庞大的离线处理平台时，使用基于 Spring Batch 的批处理框架是一个不错的选择。

再比方说，如果想要实现与 Kafka、RabbitMQ 等各种主流消息中间件之间的集成，但又希望开发人员不需要了解这些中间件在使用上的差别，那么使用基于 Spring Cloud Stream 的事件驱动架构是你的首选。

**Spring Framework 的整体架构**

我们现在能看到的 Spring 家族技术体系都是在 Spring Framework 基础上逐步演进而来的。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210330231153.png" alt="image-20210330231153856" style="zoom:50%;" />

Spring 从诞生之初就被认为是一种容器，上图中的“核心容器”部分就包含了一个容器所应该具备的核心功能。

最上面的两个框就是构建应用程序所需要的最核心的两大功能组件，也是我们日常开发中最常用的组件，即数据访问和 Web 服务。这两大部分功能组件中包含的内容非常多，而且充分体现了 Spring Framework 的集成性，也就是说，框架内部整合了业界主流的数据库驱动、消息中间件、ORM 框架等各种工具，开发人员可以根据需要灵活地替换和调整自己想要使用的工具。

从开发语言上讲，虽然 Spring 应用最广泛的是在 Java EE 领域，但在当前的版本中，也支持 Kotlin、Groovy 以及各种动态开发语言。

# 02 | 案例驱动：一个 Spring Web 应用程序

















