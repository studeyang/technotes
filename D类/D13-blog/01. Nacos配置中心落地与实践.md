# Nacos配置中心落地与实践

# 一、背景

目前，我们公司各团队配置中心使用各异，电商使用的是 Spring Cloud Config，支付使用的是 Apollo，APP 团队使用的是 Apollo+Nacos。为了更好地应对公司业务的发展，统一基础设施技术栈必不可少。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220222140242719.png" alt="image-20220222140242719"  />

> 图片来源：[直播《如何做好微服务基础设施选型》](https://www.bilibili.com/video/BV1GR4y137RS?spm_id_from=333.999.0.0)--李运华

此外，电商团队使用的 Spring Cloud Config 面临以下技术痛点：

- 修改配置需要重启服务
- 配置管理不友好（通过gitlab修改）
- 缺少权限管控、格式检验、安全配置等特性

# 二、配置中心选型

## 开源产品分析

- Spring Cloud Config

2014年9月开源，Spring Cloud 生态组件，可以和 Spring Cloud 体系无缝整合。

- Apollo

2016年5月，携程开源的一款可靠的分布式配置管理中心。能够集中化管理应用不同环境、不同集群的配置，配置修改后能够实时推送到应用端，并且具备规范的权限、流程治理等特性，适用于微服务配置管理场景。

- Nacos

2018年6月，阿里开源的一个更易于构建云原生应用的动态服务发现、配置管理和服务管理平台。它孵化于阿里巴巴，成长于十年双十一的洪峰考验，沉淀了简单易用、稳定可靠、性能卓越的核心竞争力。

|            | 比较项               | Nacos                                                        | Apollo                                               | Spring Cloud Config                                          |
| :--------: | -------------------- | ------------------------------------------------------------ | ---------------------------------------------------- | ------------------------------------------------------------ |
| 社区活跃度 | 开源时间             | 2018.6                                                       | 2016.5                                               | 2014.9                                                       |
|            | github关注           | 20.5k                                                        | 26K                                                  | 1.7K                                                         |
|            | 文档                 | [完善](https://nacos.io/zh-cn/docs/system-configurations.html) | [完善](https://www.apolloconfig.com/#/)              | [完善](https://spring.io/projects/spring-cloud-config#overview) |
|    性能    | 单机读（QPS）        | 15000                                                        | 9000                                                 | 7(限流所致)                                                  |
|            | 单机写（QPS）        | 1800                                                         | 1100                                                 | 5(限流所致)                                                  |
|   可用性   | 停服影响（配置服务） | 已启动的客户端不影响                                         | 已启动的客户端不影响                                 | 已启动的客户端不影响                                         |
|            | 部署模式             | 集群                                                         | 集群                                                 | 集群                                                         |
|   易用性   | 配置生效时间         | 实时                                                         | 实时                                                 | 重启生效，或手动refresh生效                                  |
|            | 数据一致性           | HTTP异步通知                                                 | 数据库模拟消息队列，Apollo定时读消息 一分钟实时生效  | Git保证数据一致性，Config-server从Git读数据                  |
|            | 配置界面             | 支持                                                         | 支持                                                 | 不支持                                                       |
|            | 配置格式校验         | 支持                                                         | 支持                                                 | 不支持                                                       |
|            | 配置回滚             | 支持                                                         | 支持                                                 | 支持（基于git的回滚）                                        |
|            | 版本管理             | 支持                                                         | 支持                                                 | 支持（基于git的版本管理）                                    |
|            | 客户端支持语言       | 官方java 非官方 Go、Python、NodeJS、C++                      | 官方java .net 非官方 Go、Python、NodeJS、PHP、C++    |                                                              |
|            | 客户端使用           | nacos client                                                 | apollo client                                        | cloud config client                                          |
|   安全性   | 权限管理             | 支持                                                         | 完善 数据权限都比较完善                              | 支持（git）                                                  |
|            | 授权/审计/审核       | 支持                                                         | 界面上直接操作且支持修改和发布权限分离               | 依赖git权限管理                                              |
|            | 数据加密             | 不支持                                                       | 不支持                                               | 加密和解密属性值                                             |
| 架构复杂度 | 运维成本             | Nacos+MySQL（部署简单）                                      | Config+Admin+Portal+MySQL（部署复杂）                | Config-server+Git+MQ（部署复杂）                             |
|            | 服务依赖             | 自身就是注册发现中心 阿里云两个功能隔开了                    | 分布式 需要注册中心 内置了eureka                     | 需要注册中心                                                 |
|            | 灰度发布             | 支持 客户端配置 且路由规则客户端计算 耦合高 繁琐             | 支持 服务端配置 且路由规则服务端计算 客户端透明 简单 | 支持                                                         |
|            | 邮件服务             | 不支持                                                       | 支持                                                 | 不支持                                                       |
|            | 查询配置监听         | 支持                                                         | 支持                                                 | 支持                                                         |

1. 从性能方面看：读写性能 Nacos > Apollo > Spring Cloud Config。
2. 从功能方面看：功能完善度 Apollo > Nacos > Spring Cloud Config。
3. 从社区活跃性看：原来Spring Cloud 那一套生态Netflix基本上不怎么维护了，因为不赚钱；但是 Spring Alibaba 这套微服务生态会一直开源且有维护，因为阿里将这一块 SaaS 化后赚钱。
4. Nacos的优势：简单。它整合了注册中心、配置中心功能，部署和操作相比Apollo都要直观简单，因此它简化了架构复杂度，并减轻运维及部署工作。

## 性能对比

- 压力机信息

处理器：Intel(R) Core(TM) i5-9500 CPU @ 3.00GHz 3.00 GHz

系统：window 10

内测：16G

- 压测工具：JMeter
- 压测策略：100用户请求线程 10内递增开启，持续时间100s

### 场景一：调用服务端

![image-20220222142033442](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220222142033442.png)

测试结果如下：

![image-20220222142102625](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220222142102625.png)

通过压测发现，Nacos读配置的TPS大约是11000左右 ，写配置TPS大约是1800左右，而Apollo读配置TPS大约是1100，写配置TPS大约310，Nacos读写性能优势非常明显。

### 场景二：调用客户端

![image-20220222142123826](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220222142123826.png)

测试结果如下：

![image-20220222142232508](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220222142232508.png)

可见，读性能相差不大。

## 结论

|                     | 选择的原因                             | 不选择的原因 |
| ------------------- | -------------------------------------- | ------------ |
| Nacos               | 统一技术栈能解决现有技术痛点运维成本低 |              |
| Apollo              |                                        | 依赖 Eureka  |
| Spring Cloud Config |                                        |              |

> 参考文档：
>
> - [深度对比三种主流微服务配置中心](https://zhuanlan.zhihu.com/p/62191330)
> - [Nacos服务配置性能测试报告](https://nacos.io/zh-cn/docs/nacos-config-benchmark.html)
> - [Apollo性能测试报告](https://www.bookstack.cn/read/ctripcorp-apollo/24aec7d3cf41ff30.md)
> - [凉凉了，Eureka 宣布闭源，Spring Cloud 何去何从？](https://blog.csdn.net/csdnsevenn/article/details/81025178)

# 三、快速使用

> 参考文档：https://nacos.io/en-us/docs/quick-start-spring-boot.html

## 升级依赖

去除 spring-cloud-config 依赖：

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-config</artifactId>
</dependency>
```

添加 Nacos 依赖:

```xaml
<dependency>
    <groupId>com.alibaba.boot</groupId>
    <artifactId>nacos-config-spring-boot-starter</artifactId>
    <version>0.1.8</version>
</dependency>
```

## 替换 Nacos 配置

将原 bootstrap.yml 文件中的 config 配置替换成 nacos 的配置。

```yaml
spring:
  application:
    name: {应用名}
  cloud:                                                      # 移除
    config:                                                   # 移除
      uri: http://config-center.alpha-intra.dbses.com/conf    # 移除
      label: alpha                                            # 移除
```

替换结果如下：

```yaml
spring:
  application:
    name: {应用名}
nacos:
  config:
    server-addr: http://ec-nacos.dbses.com
    namespace: alpha
    group: {组名}
```

## 启动类添加注解

```java
// dataId 对应服务的配置
@NacosPropertySource(groupId = "${nacos.config.group}", dataId = "${spring.application.name}.yml", first = true)
public class WebApplication {
 
    public static void main(String[] args) {
        SpringApplication.run(WebApplication.class, args);
    }
 
}
```

# 四、实践

## 配置动态刷新

**方式一：使用@NacosValue**

使用此种方法需要在@NacosPropertySource 需加上 autoRefreshed=true。示例代码如下：

```java
@NacosPropertySource(groupId = "infra", dataId = "zebra-service.yml", first = true, autoRefreshed = true)
public class WebApplication {
 
    public static void main(String[] args) {
        SpringApplication.run(WebApplication.class, args);
    }
 
}
```

nacos 配置如下：

```
test1:
  config: 2
```

接口代码如下：

```java
@RestController
public class TestController {
 
    @NacosValue(value = "${test1.config}", autoRefreshed = true)
    private String config;
 
    @GetMapping("/config")
    public String getConfig() {
        return config;
    }
 
}
```

**方式二：使用@NacosConfigurationProperties**

示例代码如下：

```java
@Configuration
@Data
@NacosConfigurationProperties(prefix = "test2", dataId = "zebra-service.yml", groupId = "infra", autoRefreshed = true)
public class TestConfig {
 
    private List<String> config;
 
    private Map<String, String> map;
 
    @Override
    public String toString() {
        return "TestConfig{" + "config=" + config + ", map=" + map + '}';
    }
 
}
```

nacos 配置如下：

```yaml
test2:
  config:
    - yang
    - wang
  map:
    courier: yang
    zebra: wang
```

接口代码如下：

```java
@RestController
public class TestController {
 
    @Autowired
    private TestConfig testConfig;
 
    @GetMapping("/config2")
    public String getConfig2() {
        return testConfig.toString();
    }
 
}
```

> **注意**
>
> 动态刷新map，修改了key会累加，不会删除原来的key。例如将 zebra-service.yml 配置中的 test2.map.zebra 改为 test2.map.zebr 后，获取的结果如下：
>
> TestConfig{config=[yang, wang], map={courier=yang, zebra=wang, zebr=wang}}

**方式三：使用@NacosConfigListener**

nacos 配置如下：

```yaml
test1:
  config: 2
```

示例代码如下：

```java
@RestController
public class TestController {
 
    @Value(value = "${test1.config}")
    private String config;
 
    @GetMapping("/config")
    public String getConfig() {
        return config;
    }
 
    @NacosConfigListener(dataId = "zebra-service.yml", groupId = "infra")
    public void testConfigChange(String newContent) {
        YamlPropertiesFactoryBean yamlFactory = new YamlPropertiesFactoryBean();
        yamlFactory.setResources(new ByteArrayResource(newContent.getBytes()));
        Properties commonsProperties = yamlFactory.getObject();
        this.config = commonsProperties.getProperty("test1.config"));
    }
 
}
```

## 多配置引入

**问题描述**

我们的项目之前读取了许多公共配置，现想要读取公共配置，该怎么办？

**问题解决**

使用 @NacosPropertySources 注解即可加入多个配置文件。

样例代码：

```java
@NacosPropertySources({
        @NacosPropertySource(groupId = "infra", dataId = "captcha-service.yml", first = true),
        @NacosPropertySource(groupId = "commons", dataId = "__common_eureka_.yml")
})
public class WebApplication {
 
    public static void main(String[] args) {
        SpringApplication.run(WebApplication.class, args);
    }
 
}
```

> 这里的 first = true 表示这个文件的配置优先级是最高的。

## 本地配置覆盖

**问题描述**

作为开发人员，我们可能需要本地启动程序来进行调试，但此时本地启动的程序连接的是 alpha 环境的配置。如果修改 alpha 环境的配置，又可能影响 alpha 及其他人的程序运行。

面对这种情况，我们怎么管理配置的优先级？

下面以 test1.config 配置为例。nacos 配置文件如下：

![image-20220222143101832](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220222143101832.png)

启动配置如下：

![image-20220222143133401](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220222143133401.png)

测试代码如下：

```java
@RestController
public class TestController {
 
    @NacosValue(value = "${test1.config}", autoRefreshed = true)
    private String config1;
 
    @GetMapping("/config1")
    public String getConfig1() {
        return config1;
    }
}
```

执行结果为：

![image-20220222143208909](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220222143208909.png)

本地的配置并没有达到覆盖的效果。

**问题分析**

我们不妨先改造一下程序启动类。

![image-20220222143652521](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220222143652521.png)

通过断点可以看到，应用配置（这里指 nacos 中的 zebra-service.yml，下同）的优先级是在公共配置之前的，这点是必要的。

> 应用配置必须在公共配置之前。

但是应用配置也在系统变量（systemProperties）、系统环境（systemEnvironment）之前。所以我们配置的 test1.config 并没有生效为 local。

稍作修改一下：

![image-20220222143612121](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220222143612121.png)

**问题解决**

再测试一下本地配置是否覆盖。

![image-20220222143742655](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220222143742655.png)

本地的配置已达到覆盖的效果。最终的启动类代码为：

```java
@SpringBootApplication
@EnableDiscoveryClient
@EnableFeignClients
@PrepareConfigurations({"__common_database_", "__common_eureka_"})
@NacosPropertySource(groupId = "infra", dataId = "zebra-service.yml", autoRefreshed = true
        ,after = StandardEnvironment.SYSTEM_PROPERTIES_PROPERTY_SOURCE_NAME
)
public class WebApplication {
 
    public static void main(String[] args) {
        SpringApplication.run(WebApplication.class, args);
    }
 
}
```

