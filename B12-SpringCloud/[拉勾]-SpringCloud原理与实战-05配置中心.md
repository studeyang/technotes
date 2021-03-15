# 16 | 配置方案：分布式环境下的配置中心解决方案

**配置中心基本模型**

在一个微服务系统中，势必存在多个服务，而这些服务一般都会存在开发环境、测试环境、预发布环境、生产环境等多套环境。

那么如何保证多个环境中这些配置信息都能在各个服务实例中进行实时的同步更新呢？这就需要引入集中式配置管理的设计思想，如下图所示：

![image-20210315223004012](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210315223004.png)

**Spring Boot 中的配置体系**

在 Spring Boot 中，对配置文件的命名是有一定规范的，引入了 Label 和 Profile 概念指定配置信息的版本以及运行环境。其中 Label 表示配置版本控制信息，而 Profile 则用来指定该配置文件所对应的环境。

Spring Boot 中配置文件的格式有两种，分别是 .properties 格式和 .yml 格式。

```tex
/{application}.yml
/{application}-{profile}.yml
/{label}/{application}-{profile}.yml
/{application}-{profile}.properties
/{label}/{application}-{profile}.properties
```

如何指定当前使用具体哪一套配置信息呢？

在 Spring Boot 中，我们可以在主 application.properties 中使用如下的配置方式来激活当前所使用的 Profile：

```properties
spring.profiles.active = test
```

我们也可以同时激活几个 Profile。

```yaml
spring.profiles.active: test, myprofile1, myprofile2
```



