> 参考资料：
>
> - https://disconf.readthedocs.io/zh-cn/latest/
> - https://github.com/knightliao/disconf/tree/master/docs

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

### 2.2 配置更新回调

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

### 2.3 支持配置项

```java
@Service
public class BaoBaoService {

    /**
     * 投资的钱，分布式配置 <br/>
     * 这里切面无法生效，因为SpringAOP不支持。<br/>
     * 但是这里还是正确的，因为我们会将值注入到Bean的值里.
     */
    @DisconfItem(key = key)
    public Double getMoneyInvest() {
        return moneyInvest;
    }
}
```

### 2.4 支持静态配置

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

### 2.5 过滤要进行托管的配置

有时候你不想托管所有的配置文件，可以：

resources/disconf.properties

```properties
# 忽略哪些分布式配置，用逗号分隔
disconf.ignore=jdbc-mysql.properties
```

### 2.6 强大的WEB配置平台控制

在WEB配置平台上，您可以

- 上传、更新 您的配置文件、配置项（有邮件通知），并且实现动态推送。
- 批量下载配置文件，查看ZK上部署情况
- 查看 此配置的影响范围： 哪些机器在使用，各机器上的配置内容各是什么，并且自动校验 一致性。
- 支持 自动化校验配置一致性。
- 简单权限控制

## 三、配置项

配置文件 disconf.properties 说明：

| 配置项                                          | 说明                                                         | 是否必填 | 默认值                                                       |
| ----------------------------------------------- | ------------------------------------------------------------ | -------- | ------------------------------------------------------------ |
| disconf.conf_server_host                        | 配置服务器的 HOST,用逗号分隔 ，示例：127.0.0.1:8000,127.0.0.1:8000 | 是       | 必填                                                         |
| disconf.app                                     | APP 请采用 产品线_服务名 格式                                | 否       | 优先读取命令行参数，然后再读取此文件的值                     |
| disconf.version                                 | 版本号, 请采用 X_X_X_X 格式                                  | 否       | 默认为 DEFAULT_VERSION。优先读取命令行参数，然后再读取此文件的值，最后才读取默认值。 |
| disconf.enable.remote.conf                      | 是否使用远程配置文件，true(默认)会从远程获取配置， false则直接获取本地配置 | 否       | false                                                        |
| disconf.env                                     | 环境                                                         | 否       | 默认为 DEFAULT_ENV。优先读取命令行参数，然后再读取此文件的值，最后才读取默认值 |
| disconf.ignore                                  | 忽略的分布式配置，用空格分隔                                 | 否       | 空                                                           |
| disconf.debug                                   | 调试模式。调试模式下，ZK超时或断开连接后不会重新连接（常用于client单步debug）。非调试模式下，ZK超时或断开连接会自动重新连接。 | 否       | false                                                        |
| disconf.conf_server_url_retry_times             | 获取远程配置 重试次数，默认是3次                             | 否       | 3                                                            |
| disconf.conf_server_url_retry_sleep_seconds     | 获取远程配置 重试时休眠时间，默认是5秒                       | 否       | 5                                                            |
| disconf.user_define_download_dir                | 用户定义的下载文件夹, 远程文件下载后会放在这里。注意，此文件夹必须有有权限，否则无法下载到这里 | 否       | ./disconf/download                                           |
| disconf.enable_local_download_dir_in_class_path | 下载的文件会被迁移到classpath根路径下，强烈建议将此选项置为 true(默认是true) | 否       | true                                                         |

所有配置均可以通过 命令行 `-Dname=value` 参数传入。

如何自定义 disconf.properties 文件的路径？

一般情况下，disconf.properties 应该放在应用程序的根目录下，如果想自定义路径可以使用：

```
-Ddisconf.conf=/tmp/disconf.properties
```

## 四、Disconf设计

### 4.1 架构设计

disconf服务集群模式：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406122321715.jpeg)

disconf的模块架构图：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406122322434.jpeg)

### 4.2 Disconfi-client

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406122311252.jpeg)

**运行流程详细介绍：**

启动事件A：以下按顺序发生。

- A1：扫描静态注解类数据，并注入到配置仓库里。
- A2：根据仓库里的配置文件、配置项，到 disconf-web 平台里下载配置数据。
- A3：将下载得到的配置数据值注入到仓库里。
- A4：根据仓库里的配置文件、配置项，去ZK上监控节点。
- A5：根据XML配置定义，到 disconf-web 平台里下载配置文件，放在仓库里，并监控ZK结点。
- A6：A1-A5均是处理静态类数据。A6是处理动态类数据，包括：实例化配置的回调函数类；将配置的值注入到配置实体里。

更新配置事件B：以下按顺序发生。

- B1：管理员在 Disconf-web 平台上更新配置。
- B2：Disconf-web 平台发送配置更新消息给ZK指定的结点。
- B3：ZK通知 Disconf-cient 模块。
- B4：与A2一样。唯一不同的是它只处理一个配置文件或者一个配置项，而事件A2则是处理所有配置文件和配置项。下同。
- B5：与A3一样。
- B6：基本与A4一样，区别是，这里还会将配置的新值注入到配置实体里。

### 4.3 Disconf-web

Nginx(处理静态请求) + Tomcat(处理动态请求）

后端

- SpringMvc（3.1.2+)
- Jdbc-Template
- Mysql
- RestFul API
- Redis for user login/logout
- H2内存数据库测试方案/Junit/SpringTest

前端

- HTML
- Jquery(1.10.4)：JS工具集合
- Bootstrap(2.3.2)：界面UI
- Node(ejs/fs/eventproxy): 用于前端的HTML的模板化管理

前后端接口(前后端分离)

- 完全Ajax接口
- JSON
- RestFul API





