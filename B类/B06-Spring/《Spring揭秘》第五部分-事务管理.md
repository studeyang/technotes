# 目录



# 第17章 有关事务的楔子

> 本章内容
>
> - 认识事务本身
> - 初识事务家族成员

**17.1 认识事务本身**

事务就是以可控的方式对数据资源进行访问的一组操作。事务有 4 个限定属性，即原子性（Atomicity）、一致性（Consistency）、隔离性（Isolation）和持久性（Durability）。

**17.2 初识事务家族成员**

- Resource Manager。负责存储并管理系统数据资源的状态，比如数据库服务器、JMS 消息服务器；
- Transaction Processing Monitor。职责是在分布式事务场景中协调包含多个 RM 的事务处理；
- Transaction Manager。TP Monitor 中的核心模块，直接负责多 RM 之间事务处理的协调工作，并提供事务界定（Transaction Demarcation）、事务上下文传播（Transaction Context Propagation）等功能接口；
- Application。事务边界的触发点。

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/全局事务示意图.jpg)

# 第18章 群雄逐鹿下的 Java 事务管理

> 本章内容
>
> - Java 平台的局部事务支持
> - Java 平台的分布式事务支持
> - 继续前行之前的反思

**18.1 Java 平台的局部事务支持**

数据库资源的局部事务管理。可以将数据库连接（java.sql.Connection）的自动提交（AutoCommit）功能设置为 false，改为手动提交来控制事务的提交或回滚。

消息服务资源的局部事务管理。可以通过 JMS 的 java.jms.Session 来控制整个处理过程的事务。

**18.2 Java 平台的分布式事务支持**

Java 平台上的分布式事务管理，主要是通过 JTA（Java Transaction API）或者 JCA（Java Connector Architecture）提供支持的。

- 18.2.1 基于 JTA 的分布式事务管理

  JTA 编程事务管理。通过使用 javax.transaction.UserTransaction 接口进行，各应用服务器都提供了针对它的 JNDI 查找服务。

  JTA 声明性事务管理。如果使用 EJB 进行声明性的分布式事务管理的话，JTA 的使用则只限于 EJB 容器内部，对于应用程序来说则完全就是透明的。

- 18.2.2 基于 JCA 的分布式事务管理

  JCA 规范主要面向 EIS（Enterprise Information System）的集成，通过为遗留的 EIS 系统和 Java EE 应用服务器指定统一的通信标准，二者就可以实现各种服务上的互通。

**18.3 继续前行之前的反思**

1. 局部事务的管理绑定到了具体的数据访问方式；
2. 事务的异常处理；
3. 事务处理 API 的多样性；
4. CMT 声明式事务的局限；

# 第19章 Spring 事务王国的架构

> 本章内容
>
> - 统一中原的过程
> - 和平年代

Spring 的事务框架设计理念的基本原则是：让事务管理的关注点与数据访问关注点相分离。

**19.1 统一中原的过程**













# 第20章 使用 Spring 进行事务管理





# 第21章 Spring 事务管理之扩展篇









