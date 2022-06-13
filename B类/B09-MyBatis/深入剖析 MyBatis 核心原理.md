> 来自拉勾教育《深入剖析 MyBatis 核心原理》--杨四正
>
> https://github.com/xxxlxy2008/mybatis

# 模块一：快速入门

## 01 | 常见持久层框架赏析，到底是什么让你选择 MyBatis？

从性能角度来看，Hibernate、Spring Data JPA 在对 SQL 语句的掌控、SQL 手工调优、多表连接查询等方面，不及 MyBatis 直接使用原生 SQL 语句方便、高效；

从可移植性角度来看，Hibernate 帮助我们屏蔽了底层数据库方言，Spring Data JPA 帮我们屏蔽了 ORM 的差异，而 MyBatis 因为直接编写原生 SQL，会与具体的数据库完全绑定（但实践中很少有项目会来回切换底层使用的数据库产品或 ORM 框架，所以这点并不是特别重要）；

从开发效率角度来看，Hibernate、Spring Data JPA 处理中小型项目的效率会略高于 MyBatis（这主要还是看需求和开发者技术栈）。





# 模块二：基础支撑层





# 模块三：核心处理层





# 模块四：扩展延伸















