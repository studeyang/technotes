# 第一章 课程介绍和案例需求

## 01 课程介绍

课程亮点：案例项目驱动，全研发流程覆盖，原理+编程技术+工具结合。

## 02 背景说明

- [eShopOnContainers](https://github.com/dotnet-architecture/eShopOnContainers)
- [microservices-demo](https://github.com/GoogleCloudPlatform/microservices-demo)
- [piggymetrics](https://github.com/sqshq/piggymetrics)
- [Staffjoy 项目代码（原版）](https://github.com/staffjoy/v2)
- [Staffjoy 项目代码（本课程所用的教学版）](https://gitee.com/geektime-geekbang/staffjoy)
- 代码：https://gitee.com/geektime-geekbang/staffjoy
- https://github.com/spring2go/staffjoy
- 课件：https://pan.baidu.com/s/1Q7eP3yZ1Vm8J2nhle5RzTQ 提取码: 1aeh

## 03 课程目标和主要内容

开发层面：

1. 掌握微服务架构和前后端分离架构设计
2. 能够基于 Spring Boot 搭建微服务基础框架
3. 进一步提升 Java/Spring 微服务开发技能
4. 掌握 Spring Boot 微服务测试和相关实践
5. 理解 SaaS 多租户应用的架构和设计

运维层面：

1. 理解可运维架构理念和相关实践
2. 掌握服务容器化和容器云部署相关实践
3. 理解云时代的软件工程流程和实践

## 04 课程案例需求

**Staffjoy**

https://github.com/staffjoy/v2

## 05 课程补充说明

**教学版 Staffjoy 改造**

- Golang -> Java/Spring
- 去掉 gRPC API Gateway
- 默认采用邮件通知

# 第二章 系统架构设计和技术栈选型

## 07 架构设计和技术栈选型

**总体架构**

![image-20220509221355010](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205092213054.png)

**SaaS多租户设计**

![image-20220509221604474](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205092216521.png)

## 08 数据和接口模型设计：账户服务

**账户数据模型**

![image-20220509221751339](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205092217373.png)

**账户接口**

![image-20220509221819213](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205092218259.png)

## 09 数据和接口模型设计：公司服务

**公司数据模型**

![image-20220509222302079](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205092223120.png)

**实体关系ER图**

![image-20220509222331558](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205092223597.png)

**接口模型**

- 公司

![image-20220509222404538](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205092224597.png)

- 公司管理员

![image-20220509222433289](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205092224342.png)

- 员工目录

![image-20220509222500698](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205092225753.png)

- 团队

![image-20220509222520625](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205092225671.png)

- 雇员

![image-20220509222538497](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205092225537.png)

- 任务

![image-20220509222554003](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205092225058.png)

- 班次

![image-20220509222616602](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205092226690.png)

## 10 Dubbo、SpringCloud和Kubernetes该如何选型

**横向比对**

![image-20220509224022199](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205092240261.png)

![image-20220509224431409](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205092244460.png)

> 流量治理：蓝绿部署相关。

![image-20220509224715274](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205092247340.png)

# 第三章：服务开发框架设计和实现 

## 14 Staffjoy项目结构组织

**项目组织代码**

![image-20220510215113896](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205102151986.png)

## 16 微服务接口参数校验为何重要？

**控制器接口参数校验**

![image-20220510220234677](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205102202729.png)

**DTO 参数校验**

![image-20220510220300725](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205102203780.png)

**自定义标注**

![image-20220510220328325](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205102203368.png)

## 17 如何实现统一异常处理

**统一异常处理**

![image-20220510221137429](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205102211479.png)

**统一异常捕获**

![image-20220510221214054](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205102212098.png)

![image-20220510221300992](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205102213044.png)

![image-20220510221332679](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205102213739.png)

**Web MVC ErrorController**

Web 层的接口，根据错误码返回相应的页面。

![image-20220510221425317](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205102214366.png)

## 18 DTO和DMO为什么要互转？

**DTO 和 DMO**

DTO 表示数据传输对象；DMO 表示数据模型对象。

![image-20220510222138452](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205102221497.png)

**DTO 和 DMO互转**

![image-20220510222205233](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205102222281.png)

> https://github.com/modelmapper/modelmapper

## 19 如何实现基于Feign的强类型接口？

**Spring Feign**

![image-20220510223830268](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205102238328.png)

**强类型接口设计**

![image-20220510223855508](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205102238576.png)

ListAccountResponse 定义了额外的字段。当正常响应时，会返回一个 ListAccountResponse 对象；而当异常响应时，会返回父对象 BaseResponse，此时额外字段数据也肯定是空的。

![image-20220510224345859](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205102243912.png)

![image-20220510224105680](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205102241749.png)

**客户端调用范例**

![image-20220510224423909](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205102244977.png)

## 21 异步处理为何要复制线程上下文信息？

AsyncExecutor 配置。

![image-20220511223413065](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205112234192.png)

Async 标注。

![image-20220511223448565](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205112234616.png)

线程上下文拷贝。

![image-20220511223521574](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205112235640.png)

## 23 主流微服务框架概览

![image-20220511224549761](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205112245827.png)

使用 gRpc 的话，需要引入 gRpc Gateway api。

# 第四章：可编程网关设计和实践 

## 24 网关和BFF是如何演化出来的

BFF：Backend For Frontend

**MyShop SOA V1**

2011年的 MyShop 构架。

![image-20220511225714081](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205112257152.png)

此时还没有无线应用。

**MyShop SOA V2**

2012年上线了无线应用。

![image-20220511225807386](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205112258444.png)

问题：

- 调用者与微服务耦合严重
- 每个服务都需要域名
- 无线应用展示裁剪逻辑越来越复杂

**MyShop SOA V2.5**

![image-20220511225837214](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205112258285.png)

问题：

- 随着业务线增加，无线BFF变得臃肿
- 无线BFF增加安全认证，日志监控，限流熔断等
- 无线BFF单点问题

**MyShop SOA V3**

![image-20220513215309229](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205132153393.png)

**MyShop SOA V4**

![image-20220513215327795](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205132153854.png)

## 28 如何设计一个最简网关

**Faraday 网关内核设计**

![image-20220513221829682](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205132218741.png)

**静态路由配置**

![image-20220513221904951](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205132219045.png)

## 31 生产级网关需要考虑哪些环节

- 限流熔断
- 动态路由和负载均衡
- 基于 Path 的路由
  - api.xxx.com/pathx
- 截获器链
- 日志采集和 Metrics 埋点
- 响应流优化

## 32 主流开源网关概览

![image-20220515224937416](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205152249574.png)

# 第五章：安全框架设计和实践 

## 35 安全认证架构演进：微服务阶段

**Auth3.0：Auth Service + Token**

![image-20220516220102095](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205162201227.png)

**Auth3.5 Token + Gateway**

![image-20220516220202079](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205162202151.png)

## 36 基于JWT令牌的安全认证架构

![image-20220516220259620](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205162202681.png)

## 37 JWT的原理是什么？

**JWT令牌结构**

![image-20220516224622717](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205162246821.png)

https://blog.51cto.com/u_15281317/3009218

## 38 JWT有哪两种主要流程？

**HMAC 流程**

![image-20220517221653262](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205172216398.png)

**RSA 流程**

![image-20220517221716794](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205172217908.png)

**JWT 优劣**

![image-20220517221809040](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205172218134.png)

## 39 Staffjoy安全认证架构和SSO

**Staffjoy Auth ~ 登录认证阶段**

![image-20220517222312844](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205172223911.png)

![image-20220517222348751](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205172223820.png)

**Staffjoy Auth ~ 后续访问阶段**

![image-20220517222437976](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205172224043.png)

## 40 用户认证代码剖析

**引入JWT生成和校验库**

```xml
<dependency>
    <groupId>com.auth0</groupId>
    <artifactId>java-jwt</artifactId>
    <version>3.6.0</version>
</dependency>
```

**JWT生成算法**

![image-20220517224417726](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205172244820.png)

**JWT校验算法**

![image-20220517224442523](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205172244584.png)

**登录login种Cookie**

![image-20220517224755725](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205172247787.png)

![image-20220517224811506](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205172248566.png)

**Cookie中取出JWT令牌**

![image-20220517224839177](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205172248267.png)

**JWT校验和取出用户会话数据**

![image-20220517224959063](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205172249128.png)

**网关传递认证授权信息**

![image-20220517224942280](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205172249341.png)

faraday / AuthRequestInterceptor

![image-20220517225738157](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205172257233.png)

Feign客户端传递用户认证信息，common / FeignRequestHeaderInterceptor

![image-20220517225935819](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205172259900.png)

![image-20220517230011574](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205172300663.png)

**登出logout**

![image-20220517225811395](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205172258465.png)

# 第六章：服务测试设计和实践

## 43 SpringBoot微服务测试该如何分类？

![image-20220518224504523](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205182245677.png)

# 第七章：可运维架构设计和实践

## 50 何谓生产就绪（ProductionReady）?

![image-20220519230620393](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205192306553.png)

## 52 Apollo vs SpringCloudConfig vs K8sConfigMap

![image-20220519232449039](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205192324119.png)

## 53 CAT vs Zipkin vs Skywalking

![image-20220523214244528](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205232142679.png)

![image-20220523214638056](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205232146151.png)

## 55 结构化日志和业务审计日志

> https://github.com/jacek99/structlog4j

![image-20220523221046059](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205232210159.png)

## 56 集中异常监控和Sentry

> https://sentry.io
>
> https://github.com/getsentry/sentry

## 57 EFK & Prometheus & Skywalking+K8s集成架构

**EFK+K8s**

![image-20220523222709075](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205232227183.png)

**Prometheus+K8s**

![image-20220523222724794](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205232227899.png)

**Skywalking+K8s**

![image-20220523222745282](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205232227398.png)

# 第八章：服务容器化和Docker Compose部署 

## 58 本地开发部署架构和软件需求

![image-20220523223433542](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205232234619.png)

## 64 容器镜像构建Dockerfile解析

**Account 服务 Dockerfile**

![image-20220525221430714](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205252214883.png)

**MyAccount 单页应用 Dockerfile**

![image-20220525221456350](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205252214469.png)

# 第九章：云原生架构和Kubernetes容器云部署 (17讲)

## 68 到底什么是云原生架构？

**云原生（Cloud Native）应用定义**

应用开发采用持续交付和 DevOps 实践。基于微服务原理而开发的应用，以容器方式打包。

在运行时，容器由运行于云基础设施之上的平台进行调度。

**CNCF**

cncf.io
landscape.cncf.io

## 69 Kubernetes架构

![image-20220526220137400](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205262201559.png)

## 70 Kubernetes的基本概念

**Kubernetes 集群（Cluster）**

![image-20220526221305569](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205262213671.png)

**容器 Container**

![image-20220526221355177](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205262213261.png)

**POD**

![image-20220526221428364](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205262214465.png)

**副本集 ReplicaSet**

![image-20220526221446498](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205262214604.png)

**服务 Service**

![image-20220526221508793](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205262215876.png)

**发布Deployment**

![image-20220526221526300](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205262215417.png)

**滚动发布 Rolling Update**

![image-20220526221557521](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205262215630.png)

**ConfigMap/Secret**

![image-20220526221625225](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205262216341.png)

**DaemonSet**

![image-20220526221650191](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205262216295.png)

**其它概念**

![image-20220526221732775](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205262217857.png)

![image-20220526221918293](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205262219408.png)

**概念总结**

![image-20220526222149227](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205262221299.png)

![image-20220526222218087](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205262222199.png)

## 72 理解Kubernetes节点网络和Pod网络

![image-20220526223202350](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205262232480.png)

## 76 本地测试Kubernetes环境搭建

https://github.com/AliyunContainerService/k8s-for-docker-desktop

## 80 阿里云Kubernetes环境创建

申请专有网络vpc

-> MySQL RDS

-> 创建Kubernetes





























# 第十章：项⽬复盘、应用和扩展环节 (2讲)

# 第十一章：附录 Staffjoy 项目源代码解析 (8讲)



