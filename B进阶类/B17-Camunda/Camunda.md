> 参考资料：http://camunda-cn.shaochenfeng.com/introduction/downloading-camunda/

# 01 | 介绍

## 1.1 软件架构总览

Camunda 平台是一个基于 Java 的框架。主要组件是用 Java 编写的，我们总体上专注于为 Java 开发者提供他们在 JVM 上设计、实施和运行业务流程和工作流所需的工具。然而，我们也想让非 Java 开发者也能使用流程引擎技术。这就是为什么 Camunda 平台还提供了 REST API，允许你与远程流程引擎应用建立连接。

Camunda 平台既可以作为一个独立的流程引擎服务器使用，也可以嵌入到定制的 Java 应用程序中。

## 1.2 流程引擎架构

![image-20211124140120326](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/image-20211124140120326.png)

- 流程引擎公共 API：面向服务的 API 允许 Java 应用程序与流程引擎交互。
- BPMN 2.0 核心引擎：这是流程引擎的核心。它有一个轻量级的图结构执行引擎（PVM - Process Virtual Machine），一个将 BPMN 2.0 XML 文件转化为 Java 对象的 BPMN 2.0 解析器，以及一套 BPMN 行为实现（为 BPMN 2.0 结构提供实现，如网关或服务任务）。
- Job 执行器：Job 执行者负责处理异步的后台工作，如流程中的定时器或异步延续。
- 持久层：流程引擎有一个持久层，负责将流程实例状态持久化到关系数据库中。我们使用 MyBatis 映射引擎来实现对象的关系映射。

## 1.3 Camunda 部署架构

Camunda 平台是一个灵活的框架，可以部署在不同的场景中。本节对最常见的部署场景进行了概述。

### 嵌入式流程引擎

![image-20211124140837289](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/image-20211124140837289.png)

在这种情况下，流程引擎被作为一个库添加到一个自定义的应用程序中。这样，流程引擎可以很容易地随着应用程序的生命周期启动和停止。也可以在一个共享数据库之上运行多个嵌入式流程引擎。

### 分布式的、由容器管理的流程引擎

![image-20211124140943451](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/image-20211124140943451.png)

在这种情况下，流程引擎在运行时容器（Servlet 容器、应用服务器…）内启动。流程引擎作为容器服务提供的，可以被部署在容器内的所有应用程序共享。这个概念就像 JMS 消息队列，它由运行时提供，可以被所有应用程序使用。流程部署和应用程序之间有一对一的映射：流程引擎跟踪应用程序部署的流程定义，并将执行委托给相对应的应用程序。

### 独立运行的（远程）流程引擎服务

![image-20211124141414276](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/image-20211124141414276.png)

在这种情况下，流程引擎被作为一个网络服务提供。在网络上运行的不同应用程序可以通过一个远程通信与流程引擎进行交互。使流程引擎可以远程访问的最简单方法是使用内置的 REST API。不同的通信渠道，如 SOAP Webservices 或 JMS 也是可以的，但需要由用户自行实现。

## 1.4 集群

为了提供扩展或故障转移能力，流程引擎可以发布到集群中的不同节点。然后每个流程引擎实例必须连接到同一个共享数据库。

![image-20211124141731611](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/image-20211124141731611.png)

各个流程引擎实例不会在事务中维护会话状态。每当流程引擎运行一个事务时，完整的状态被储存到共享数据库。这使得在同一实例中工作的后续请求路由到不同的集群节点成为可能。这个处理方式非常简单，容易理解，在部署集群安装时，它的限制也很有限。就流程引擎而言，用于扩展的设置和用于故障转移的设置之间没有区别（因为流程引擎在事务之中不保留会话状态）。

### 集群环境中的会话状态

Camunda 平台不提供开箱即用的负载均衡功能和会话复制功能。负载均衡功能需要由第三方系统提供，而会话复制则需要由主机应用服务器提供。

在集群设置中，如果用户要登录到网络应用程序，需要采取额外的步骤来确保用户不需要多次登录。有两个方法：

1. 可以在你的负载均衡解决方案中配置和启用 “粘性会话”。这将确保在一个可配置的时间段内，所有来自特定用户的请求都被引导到同一个实例。
2. 会话共享可以在你的应用服务器中启用，这样应用服务器实例就可以共享会话状态。这将允许一个用户连接到集群中的多个实例，而不会被要求多次登录。

如果以上两种方法都没有在集群设置中实现，那么连接到多个节点，无论是故意的或通过负载平衡解决方案的，都将导致多次登录请求。

### 集群环境中的 Job 执行器

流程引擎 [job 执行器](http://camunda-cn.shaochenfeng.com/user-guide/process-engine/the-job-executor/) 也是集群的，在每个节点上都存在。这样，就流程引擎而言，就没有单点故障。job执行器可以同时在[同质和异质集群](http://camunda-cn.shaochenfeng.com/user-guide/process-engine/the-job-executor/#cluster-setups)中运行。

## 1.5 多租户

为了用一个 Camunda 服务于多个独立的应用，流程引擎支持多租户。支持以下多租户模式：

- 通过使用不同的数据库模式或数据库进行表级数据分离
- 通过使用租户标记进行行级数据分离

用户应该选择适合其数据分离需求的模式。Camunda 的 API 提供了对每个流程和相关数据的访问。 

# 02 | 用户指南

## 2.1 流程引擎

### 使用 Java API 启动流程引擎

```java
ProcessEngine processEngine = ProcessEngineConfiguration.createStandaloneInMemProcessEngineConfiguration()
  .setDatabaseSchemaUpdate(ProcessEngineConfiguration.DB_SCHEMA_UPDATE_FALSE)
  .setJdbcUrl("jdbc:h2:mem:my-own-db;DB_CLOSE_DELAY=1000")
  .setJobExecutorActivate(true)
  .buildProcessEngine();
```

### 使用 camunda cfg XML 配置流程引擎

```xml
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd">

  <bean id="processEngineConfiguration" class="org.camunda.bpm.engine.impl.cfg.StandaloneProcessEngineConfiguration">

    <property name="jdbcUrl" value="jdbc:h2:mem:camunda;DB_CLOSE_DELAY=1000" />
    <property name="jdbcDriver" value="org.h2.Driver" />
    <property name="jdbcUsername" value="sa" />
    <property name="jdbcPassword" value="" />

    <property name="databaseSchemaUpdate" value="true" />

    <property name="jobExecutorActivate" value="false" />

    <property name="mailServerHost" value="mail.my-corp.com" />
    <property name="mailServerPort" value="5025" />
  </bean>

</beans>
```

### 在 bpm-platform.xml 中配置流程引擎

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bpm-platform xmlns="http://www.camunda.org/schema/1.0/BpmPlatform"
              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xsi:schemaLocation="http://www.camunda.org/schema/1.0/BpmPlatform http://www.camunda.org/schema/1.0/BpmPlatform">

  <job-executor>
    <job-acquisition name="default" />
  </job-executor>

  <process-engine name="default">
    <job-acquisition>default</job-acquisition>
    <configuration>org.camunda.bpm.engine.impl.cfg.StandaloneProcessEngineConfiguration</configuration>
    <datasource>java:jdbc/ProcessEngine</datasource>

    <properties>
      <property name="history">full</property>
      <property name="databaseSchemaUpdate">true</property>
      <property name="authorizationEnabled">true</property>
    </properties>

  </process-engine>
</bpm-platform>
```

### 在 processes.xml 中配置流程引擎

流程引擎也可以使用`META-INF/processes.xml`文件进行配置和引导。

## 2.2 错误处理

参考资料：http://camunda-cn.shaochenfeng.com/user-guide/process-engine/error-handling/

### 事务回滚

标准的处理策略是向客户端抛出异常，即回滚当前事务。

### Job 异步重试

这意味着用户不会看到错误，而是“一切都成功”的对话框。 异常存储在Job中。重试策略将在稍后（当网络再次可用时）自动重新触发Job。

### 捕获异常并使用排他网关

> 网关分为：
>
> - 复杂网关（Complex Gateway）
> - 并行网关（Parallel Gateway）
> - 包含性网关（Inclusive Gateway）
> - 排他性网关（Exclusive Gateway）

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/error-result-xor.png)

我们触发了“检查数据完整性”任务。 Java 服务可能会抛出“DataIncompleteException”。 但是，如果我们检查完整性，不完整的数据不是异常，而是预期的结果，因此我们更喜欢在评估流程变量的流程中使用 异或网关，例如，“#{dataComplete==false}” 。

### 定义错误事件

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/bpmn.boundary.error.event.png)

可以明确地对错误进行建模，从而解决业务错误的用例。

## 2.3 超时处理

参考资料：https://camunda.com/best-practices/managing-the-task-lifecycle/

可以在定义流程时，设置某段流程的超时时间。

![image-20211207113925292](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/image-20211207113925292.png)













