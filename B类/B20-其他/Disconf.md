> 参考资料：
>
> - https://disconf.readthedocs.io/zh-cn/latest/
> - https://github.com/knightliao/disconf/tree/master/docs

# 一、功能概述

## 1.1 主要目标

- 部署极其简单：同一个上线包，无须改动配置，即可在 多个环境中(RD/QA/PRODUCTION) 上线
- 部署动态化：更改配置，无需重新打包或重启，即可 实时生效
- 统一管理：提供web平台，统一管理 多个环境(RD/QA/PRODUCTION)、多个产品 的所有配置
- 核心目标：一个jar包，到处运行

## 1.2 功能特点

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406092331507.jpeg)

1、支持配置项+配置文件的管理（配置项是指某个类里的某个Field字段）；

2、配置发布统一化：配置存储在云端系统，用户统一管理 多个环境(RD/QA/PRODUCTION)、多个平台 的所有配置；

3、配置更新自动化：用户在平台更新配置，使用该配置的系统会自动发现该情况，并应用新配置。特殊地，如果用户为此配置定义了回调函数类，则此函数类会被自动调用；

4、极简的使用方式：基于XML配置或者基于注解，即可完成复杂的配置分布式化。

# 二、Quick Start

Demo: https://github.com/knightliao/disconf-demos-java/

## 2.1 托管配置

通过简单的注解类方式 托管配置。当配置被更新后，注解类的数据自动同步。

> 所谓的托管，就是把配置集中到一个类中，以前（2016年）或许很新颖，现在（2024年）属于常规操作。

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

## 2.2 配置更新回调

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

## 2.3 支持配置项

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

> 切面无法生效，说明更新配置后无法获取最新值。这个注解等效于 Spring 的 @Value。

## 2.4 支持静态配置

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

## 2.5 强大的WEB配置平台控制

在WEB配置平台上，您可以

- 上传、更新 您的配置文件、配置项（有邮件通知），并且实现动态推送。
- 批量下载配置文件，查看ZK上部署情况
- 查看 此配置的影响范围： 哪些机器在使用，各机器上的配置内容各是什么，并且自动校验 一致性。
- 支持 自动化校验配置一致性。
- 简单权限控制

# 三、配置项

配置文件 disconf.properties 说明：

```properties
# 说明：必填。配置服务器的 HOST, 用逗号分隔
disconf.conf_server_host=127.0.0.1:8000,127.0.0.1:8000

# 说明：APP 请采用 产品线_服务名 格式
# 默认值：优先读取命令行参数，然后再读取此文件的值
disconf.app=

# 说明：版本号, 请采用 X_X_X_X 格式
# 默认值：DEFAULT_VERSION。优先读取命令行参数，然后再读取此文件的值，最后才读取默认值。
disconf.version=

# 说明：是否使用远程配置文件，true会从远程获取配置， false则直接获取本地配置
# 默认值：true
disconf.enable.remote.conf=

# 说明：环境
# 默认值：DEFAULT_ENV。优先读取命令行参数，然后再读取此文件的值，最后才读取默认值
disconf.env=

# 说明：忽略的分布式配置，用空格分隔
# 默认值：空
disconf.ignore=

# 说明：调试模式。调试模式下，ZK超时或断开连接后不会重新连接（常用于client单步debug）。非调试模式下，ZK超时或断开连接会自动重新连接。
# 默认值：false
disconf.debug=

# 说明：获取远程配置 重试次数
# 默认值：3
disconf.conf_server_url_retry_times=

# 说明：获取远程配置 重试时休眠时间
# 默认值：5
disconf.conf_server_url_retry_sleep_seconds=

# 说明：用户定义的下载文件夹, 远程文件下载后会放在这里。注意，此文件夹必须有有权限，否则无法下载到这里
# 默认值：./disconf/download
disconf.user_define_download_dir=

# 说明：下载的文件会被迁移到classpath根路径下，强烈建议将此选项置为 true
# 默认值：true
disconf.enable_local_download_dir_in_class_path=
```

所有配置均可以通过 命令行 `-Dname=value` 参数传入。

如何自定义 disconf.properties 文件的路径？

一般情况下，disconf.properties 应该放在应用程序的根目录下，如果想自定义路径可以使用：

```
-Ddisconf.conf=/tmp/disconf.properties
```

# 四、Disconf设计

## 4.1 架构设计

disconf服务集群模式：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406122321715.jpeg)

disconf的模块架构图：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406122322434.jpeg)

## 4.2 Disconfi-client

### 4.2.1 运行流程详细介绍

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406132317699.jpeg)

启动事件A：以下按顺序发生。

（第一次扫描，静态扫描 for annotation config）

- A3：扫描静态注解类数据，并注入到配置仓库里。==（第一次扫描）==
- A4+A2：根据仓库里的配置文件、配置项，到 disconf-web 平台里下载配置数据。==（获取数据）==
- A5：将下载得到的配置数据值注入到仓库里。==（注入）==
- A6：根据仓库里的配置文件、配置项，去ZK上监控节点。==（Watch）==

（第二次扫描，动态扫描 for annotation config）

- A7+A2：根据XML配置定义，到 disconf-web 平台里下载配置文件，放在仓库里，并监控ZK结点。
- A8：A1-A6均是处理静态类数据。A7是处理动态类数据，包括：实例化配置的回调函数类；将配置的值注入到配置实体里。

> 配置仓库指的是什么？
>
> DisconfCenterStore 这个类，可以理解为一个 Map。

更新配置事件B：以下按顺序发生。

- B1：管理员在 Disconf-web 平台上更新配置。
- B2：Disconf-web 平台发送配置更新消息给ZK指定的结点。
- B3：ZK通知 Disconf-cient 模块。
- B4：Disconf-cient 根据仓库里的配置文件、配置项，到 disconf-web 平台里下载配置数据。（与A4一样）
- B5：将下载得到的配置数据值注入到仓库里。（与A5一样）
- B6：根据仓库里的配置文件、配置项，去ZK上监控节点。（基本与A6一样，唯一的区别是，这里还会将配置的新值注入到配置实体里）

主备机切换事件C：以下按顺序发生。

- C1：发生主机挂机事件。
- C2：ZK通知所有被影响到的备机。
- C4：与A2一样。
- C5：与A4一样。
- C6：与A5一样。
- C7：与A6一样。

### 4.2.2 Disconf-client 的启动

应用程序启动时，当Spring容器扫描了所有Java Bean却还未初始化这些Bean时，disconf-client 模块会优先开始初始化（最高优先级）。它会将 配置文件名、配置项名记录在配置仓库里，并去 disconf-web 平台下载配置文件至classpath目录下。并且，还会到ZK上生成相应的节点。

接着Spring开始初始化用户定义的SpringBean。由于配置文件已经被正确下载至Classpath路径下，因此，JavaBean的配置文件使用的是分布式配置文件，而非本地的配置文件。

待SpringBean初始化后，Disconf-client会获取配置更新回调类实例：此时，Spring上的所有Bean均已被init。Disconf-client模块会再次运行，这时它会去获取用户撰写的配置更新回调函数类实例。

配置文件更新时，分布式配置文件会重新被下载：当配置文件更新时，disconf-client便会重新从 disconf-web 平台下载配置文件，并重新将值放在配置仓库里。并按顺序进行调用回调函数类的 reload() 方法。

启动分成两步，由两个Bean来实现：

```xml
<bean id="disconfMgrBean" class="com.baidu.disconf.client.DisconfMgrBean"
    destroy-method="destroy">
    <property name="scanPackage" value="com.baidu.disconf.demo" />
</bean>
<bean id="disconfMgrBean2" class="com.baidu.disconf.client.DisconfMgrBeanSecond"
    init-method="init" destroy-method="destroy">
</bean>
```

这里 com.baidu.disconf.dem 是要扫描的类。

第一步由Bean com.baidu.disconf.client.DisconfMgrBean 来控制。第二步由 com.baidu.disconf.client.DisconfMgrBeanSecond 控制。

**第一步：com.baidu.disconf.client.DisconfMgrBean**

此Bean实现了BeanFactoryPostProcessor和PriorityOrdered接口。它的Bean初始化Order是最高优先级的。

因此，当Spring扫描了所有的Bean信息后，在所有Bean初始化（init）之前，DisconfMgrBean的postProcessBeanFactory方法将被调用，在这里，Disconf-Client会进行第一次扫描。

扫描按顺序做了以下几个事情：

1. 初始化Disconf-client自己的配置模块。
2. 初始化Scan模块。
3. 初始化Core模块，并极联初始化Watch，Fetcher，Restful模块。
4. 扫描用户类，整合分布式配置注解相关的静态类信息至配置仓库里。
5. 执行Core模块，从disconf-web平台上下载配置数据：配置文件下载到本地，配置项直接下载。
6. 配置文件和配置项的数据会注入到配置仓库里。
7. 使用watch模块为所有配置关联ZK上的结点。

其中对配置的处理详细为：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406132340920.jpeg)

**第二步：com.baidu.disconf.client.DisconfMgrBeanSecond**

DisconfMgrBean的扫描主要是静态数据的初始化，并未涉及到动态数据。DisconfMgrBeanSecond Bean则是将一些动态的数据写到仓库里。

本次扫描按顺序做了以下几个事情：

1. 将配置更新回调实例放到配置仓库里
2. 为配置实例注入值。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406132344828.jpeg)

### 4.2.3 动态修改配置的原理

在上面我们说到，配置文件类中的配置项必须有 get 方法，并且必须有 @DisconfFileItem 注解。在 get 上面添加注解的原因就是为了做切面。

disconf-cient使用Spring AOP拦截 系统里所有含有@DisconfFileItem注解的 get 方法，把所有此类请求都定向到用户程序的配置仓库中去获取。

通过这种方式，我们可以实现统一的、集中式的在配置仓库里去获取配置文件数据。这是一种简洁的实现方式。

### 4.2.4 分布式配置项的实现

配置项相对于配置文件，比较灵活。我们可以在任何SpringBean里添加配置项。

如以下是在一个配置文件类里添加配置项：

```java
@Service
@DisconfFile(filename = "coefficients.properties")
public class Coefficients {

    public static final String key = "discountRate";

    @Value(value = "2.0d")
    private Double discount;

    private double baiFaCoe;

    /**
     * 阿里余额宝的系数, 分布式文件配置
     */
    @DisconfFileItem(name = "coe.baiFaCoe")
    public double getBaiFaCoe() {
        return baiFaCoe;
    }

    /**
     * 折扣率，分布式配置
     *
     * @return
     */
    @DisconfItem(key = key)
    public Double getDiscount() {
        return discount;
    }
}
```

我们也可以在一个Service类里添加配置项：

```java
@Service
public class BaoBaoService {

    protected static final Logger LOGGER = LoggerFactory.getLogger(BaoBaoService.class);

    public static final String key = "moneyInvest";

    @Value(value = "2000d")
    private Double moneyInvest;

    @Autowired
    private Coefficients coefficients;

    /**
     * 计算百发一天赚多少钱
     */
    public double calcBaiFa() {
        return coefficients.getBaiFaCoe() * coefficients.getDiscount() * getMoneyInvest();
    }

    /**
     * 投资的钱，分布式配置 <br/>
     * <br/>
     * 这里切面无法生效，因为SpringAOP不支持。<br/>
     * 但是这里还是正确的，因为我们会将值注入到Bean的值里.
     */
    @DisconfItem(key = key)
    public Double getMoneyInvest() {
        return moneyInvest;
    }
}
```

采用哪种方式，由用户选择。

值得注意的是，在第二种实现中，它的方法calcBaiFa() 时调用了 getMoneyInvest() 方法。 getMoneyInvest() 是配置项的get方法，它添加了@DisconfItem注解，表明它是一个配置项，并且会被切面拦截，moneyInvest的值会在配置仓库里获取。但是，可惜的是，SpringAOP是无法拦截"Call myself"方法的。也就是说getMoneyInvest()是无法被切面拦截到的。

为了解决此问题，在实现中，我们不仅将它的值 注入到配置仓库中，而且还注入到配置项所在类的实例里。因此，在上面第二种实现中，虽然 getMoneyInvest() 方法无法被拦截，但是它返回的还是正确的分布式值的。

配置文件也一样，配置值亦会注入到配置文件类实体中。

## 4.3 Disconf-web

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





