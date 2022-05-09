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

# 第二章 系统架构设计和技术栈选型（6~13）

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

## 10丨Dubbo、SpringCloud和Kubernetes该如何选型

**横向比对**

![image-20220509224022199](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205092240261.png)

![image-20220509224431409](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205092244460.png)

> 流量治理：蓝绿部署相关。

![image-20220509224715274](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205092247340.png)









# 第三章：服务开发框架设计和实现 (10讲)

第四章：可编程网关设计和实践 (9讲)

第五章：安全框架设计和实践 (10讲)

第六章：服务测试设计和实践 (7讲)

第七章：可运维架构设计和实践 (8讲)

第八章：服务容器化和Docker Compose部署 (10讲)

第九章：云原生架构和Kubernetes容器云部署 (17讲)

第十章：项⽬复盘、应用和扩展环节 (2讲)

# 第十一章：附录 Staffjoy 项目源代码解析 (8讲)



