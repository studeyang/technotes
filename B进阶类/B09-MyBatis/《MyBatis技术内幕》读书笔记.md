# 第1章 MyBatis快速入门

整体架构

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201120091440.png)

一条SQL语句的大致过程

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201120091445.png)

# 第2章 基础支持层

基础支持层包括：数据源模块、事务管理模块、缓存模块、Binding模块、反射模块、类型转换、日志模块、资源加载、解析器模块。

**2.1 解析器模块**

对XML配置文件进行解析。

**2.2 反射工具箱**

MyBatis在进行参数处理、结果映射等操作时，会涉及大量的反射操作。

**2.3 类型转换**

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201120091454.png)

**2.4 日志模块**

统一日志接口。

**2.5 资源加载**

`ClassLoaderWrapper`包装了多个`ClassLoader`对象，通过调整多个类加载器的使用有顺序，`ClassLoaderWrapper`可以确保返回给系统使用的是正确的类加载器。

**2.6 DataSource**

MyBatis 不仅可以集成第三方数据源组件，还提供了自己的数据源实现，`PooledDataSource`和`UnpooledDataSource`。

**2.7 Transaction**

MyBatis 使用`Transaction`接口对数据库事务进行了抽象，有`JdbcTransaction`和`ManagedTransaction`两个实现。

**2.8 binding 模块**

`Mapper`接口中定义的方法在 MyBatis 初始化过程中会与映射配置文件中定义的 SQL 语句相关联。如果存在无法关联的 SQL 语句，在 MyBatis 的初始化阶段就会抛出异常。

**2.9 缓存模块**

MyBatis 中的缓存分为一级缓存、二级缓存，它们都是`Cache`接口的实现。

# 第3章 核心处理层

核心处理层包括：配置解析、参数映射、SQL解析、SQL执行、结果集映射、插件。

**3.1 MyBatis 初始化**

类似于 Spring、MyBatis 等灵活性和可扩展性都很高的开源框架都提供了很多配置项，开发人员需要在使用时提供相应的配置信息，实现相应的需求。

**3.2 SqlNode & SqlSource**


