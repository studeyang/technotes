> 参考资料：https://disconf.readthedocs.io/zh-cn/latest/

## 一、功能概述

### 1.1 主要目标

- 部署极其简单：同一个上线包，无须改动配置，即可在 多个环境中(RD/QA/PRODUCTION) 上线
- 部署动态化：更改配置，无需重新打包或重启，即可 实时生效
- 统一管理：提供web平台，统一管理 多个环境(RD/QA/PRODUCTION)、多个产品 的所有配置
- 核心目标：一个jar包，到处运行

### 1.2 功能特点

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406092331507.jpeg)

1、支持配置项+配置文件的管理（配置项是指某个类里的某个Field字段）；

2、配置发布统一化：配置存储在云端系统，用户统一管理 多个环境(RD/QA/PRODUCTION)、多个平台 的所有配置；

3、配置更新自动化：用户在平台更新配置，使用该配置的系统会自动发现该情况，并应用新配置。特殊地，如果用户为此配置定义了回调函数类，则此函数类会被自动调用；

4、极简的使用方式：基于XML配置或者基于注解，即可完成复杂的配置分布式化。

## 二、Quick Start

Demo: https://github.com/knightliao/disconf-demos-java/

### 2.1 托管配置

通过简单的注解类方式 托管配置。当配置被更新后，注解类的数据自动同步。

```java
@Service
@DisconfFile(filename = "redis.properties")
public class JedisConfig {

    // 代表连接地址
    private String host;

    // 代表连接port
    private int port;

    /**
     * 地址, 分布式文件配置
     */
    @DisconfFileItem(name = "redis.host", associateField = "host")
    public String getHost() {
        return host;
    }

    public void setHost(String host) {
        this.host = host;
    }

    /**
     * 端口, 分布式文件配置
     */
    @DisconfFileItem(name = "redis.port", associateField = "port")
    public int getPort() {
        return port;
    }

    public void setPort(int port) {
        this.port = port;
    }
}
```

### 1.2 配置更新回调

如果配置更新时，您需要的是 **不仅注解类自动同步，并且其它类也需要做些变化**，那么您需要一个回调来帮忙。

[一个简单的Redis服务](https://github.com/knightliao/disconf-demos-java/blob/master/disconf-standalone-dubbo-demo/src/main/java/com/example/disconf/demo/service/SimpleRedisServiceUpdateCallback.java)。

```java
@Service
public class SimpleRedisService implements InitializingBean, DisposableBean {

    // jedis 实例
    private Jedis jedis = null;

    @Autowired
    private JedisConfig jedisConfig;

    /**
     * 更改Jedis
     */
    public void changeJedis() {
        log.info("start to change jedis hosts to: " + jedisConfig.getHost() + " : " + jedisConfig.getPort());
        jedis = JedisUtil.createJedis(jedisConfig.getHost(), jedisConfig.getPort());
        log.info("change ok.");
    }
}
```

```java
@Service
@DisconfUpdateService(classes = { JedisConfig.class })
// 或者写成 @DisconfUpdateService(confFileKeys = { "redis.properties" })
public class SimpleRedisServiceUpdateCallback implements IDisconfUpdate {

    @Autowired
    private SimpleRedisService simpleRedisService;

    public void reload() throws Exception {
        simpleRedisService.changeJedis();
    }

}
```

### 1.3 支持基于XML的配置文件托管

除了支持基于注解式的配置文件，我们还支持 基于XML无代码侵入式的。

### 1.4 支持配置项

```java
@DisconfItem(key = key)
public Double getMoneyInvest() {
    return moneyInvest;
}
```

### 1.5 支持静态配置

```java
@DisconfFile(filename = "static.properties")
public class StaticConfig {

    private static int staticVar;

    @DisconfFileItem(name = "staticVar", associateField = "staticVar")
    public static int getStaticVar() {
        return staticVar;
    }
}
```

### 1.6 支持基于XML的配置文件托管：不会自动reload



### 1.7 过滤要进行托管的配置

有时候你不想托管所有的配置文件，可以：

```java
# 忽略哪些分布式配置，用逗号分隔
ignore=jdbc-mysql.properties
```

### 1.8 强大的WEB配置平台控制

在WEB配置平台上，您可以

- 上传、更新 您的配置文件、配置项（有邮件通知），并且实现动态推送。
- 批量下载配置文件，查看ZK上部署情况
- 查看 此配置的影响范围： 哪些机器在使用，各机器上的配置内容各是什么，并且自动校验 一致性。
- 支持 自动化校验配置一致性。
- 简单权限控制

