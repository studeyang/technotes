> 来源：拉勾教育《Spring Cloud Alibaba实战》

# ==模块三 微服务通信==

# 06 | 负载均衡：Ribbon 如何保证微服务的高可用

> 内容合并至《[拉勾]-SpringCloud原理与实战-02服务治理&API网关》07 | 负载均衡：如何使用 Ribbon 实现客户端负载均衡？

# 07 | REST消息通信：如何使用 OpenFeign 简化服务间通信

**Feign 与 OpenFeign**

Netflix Feign 采用“接口+注解”的方式开发，通过模仿 RPC 的客户端与服务器模式（CS），采用接口方式开发来屏蔽网络通信的细节。

OpenFeign 则是在 Netflix Feign 的基础上进行封装，结合原有 Spring MVC 的注解，对 Spring Cloud 微服务通信提供了良好的支持。

**OpenFeign 的使用办法**

假设某电商平台日常订单业务中，为保证每一笔订单不会超卖，在创建订单前订单服务（order-service）首先去仓储服务（warehouse-service）检查对应商品 skuId（品类编号）的库存数量是否足够，库存充足创建订单，不足 App 前端提示“库存不足”。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210808220423.png" alt="image-20210808220417309" style="zoom:67%;" />

第一步，order-service 工程引入 pom.xml。

```xml
<dependency>
  <groupId>org.springframework.cloud</groupId>
  <artifactId>spring-cloud-starter-openfeign</artifactId>
  <version>2.2.5.RELEASE</version>
</dependency>
```

> 当我们引入 OpenFeign 的时候，在 Maven 依赖中会出现 netflix-ribbon 负载均衡器的身影。
>
> OpenFeign 为了保证通信高可用，底层也是采用 Ribbon 实现负载均衡，其原理与 Ribbon+RestTemplate 完全相同，只不过相较 RestTemplate，OpenFeign 封装度更高罢了。

第二步，启动类增加 @EnableFeignClients 注解。

```java
@SpringBootApplication
@EnableFeignClients //启用OpenFeign
public class OrderServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(OrderServiceApplication.class, args);
    }
}
```

第三步，创建OpenFeign的通信接口与响应对象。

```java
@FeignClient("warehouse-service")
public interface WarehouseServiceFeignClient {
    @GetMapping("/stock")
    public Stock getStock(@RequestParam("skuId") Long skuId);
}
```

**生产环境 OpenFeign 的配置事项**

- 如何更改 OpenFeign 默认的负载均衡策略

application.yml：

```yaml
warehouse-service: #服务提供者的微服务ID
  ribbon:
    #设置对应的负载均衡类
    NFLoadBalancerRuleClassName: com.netflix.loadbalancer.RandomRule
```

- 开启默认的 OpenFeign 数据压缩功能

在 OpenFeign 中，默认并没有开启数据压缩功能。但如果你在服务间单次传递数据超过 1K 字节，强烈推荐开启数据压缩功能。

> 默认 OpenFeign 使用 Gzip 方式压缩数据，对于大文本通常压缩后尺寸只相当于原始数据的 10%~30%。

```yaml
feign:
  compression:
    request:
      # 开启请求数据的压缩功能
      enabled: true
      # 压缩支持的MIME类型
      mime-types: text/xml,application/xml, application/json
      # 数据压缩下限 1024表示传输数据大于1024 才会进行数据压缩(最小压缩值标准)
      min-request-size: 1024
    # 开启响应数据的压缩功能
    response:
      enabled: true
```

- 替换默认通信组件

OpenFeign 默认使用 Java 自带的 URLConnection 对象创建 HTTP 请求。生产环境如果能换成 Apache HttpClient、OKHttp 这样的专用通信组件，可以更好地对 HTTP 连接对象进行重用与管理。以OKHttp配置方式为例：

引入 pom.xml 依赖：

```xml
<dependency>
    <groupId>io.github.openfeign</groupId>
    <artifactId>feign-okhttp</artifactId>
    <version>11.0</version>
</dependency>
```

定义 OkHttpClient Bean 对象：

```java
@Bean
public okhttp3.OkHttpClient okHttpClient(){
    return new okhttp3.OkHttpClient.Builder()
        //读取超时时间
        .readTimeout(10, TimeUnit.SECONDS)
        //连接超时时间
        .connectTimeout(10, TimeUnit.SECONDS)
        //写超时时间
        .writeTimeout(10, TimeUnit.SECONDS)
        //设置连接池
        .connectionPool(new ConnectionPool())
        .build();
}
```

application.yml 中启用 OkHttp：

```yaml
feign:
  okhttp:
    enabled: true
```

# 08 | RPC 消息：Dubbo 与 Nacos 体系如何协同作业

**RESTful 与 RPC 的区别**

RPC 采用客户端（Client) - 服务端（Server） 的架构方式实现跨进程通信，实现的通信协议也没有统一的标准，具体实现依托于研发厂商的设计。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210808223857.png" alt="image-20210808223857154" style="zoom:50%;" />

那 RESTful 与 RPC 孰优孰劣呢？我们通过一个表格进行说明：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210808223948.png" alt="image-20210808223948543" style="zoom:50%;" />

在微服务架构场景下，因为大多数服务都是轻量级的，同时 90%的任务通过短连接就能实现，因此更推荐使用 RESTful 通信。

**Apache Dubbo**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210808223135.png" alt="image-20210808223135525" style="zoom: 50%;" />

Dubbo 架构中，包含 5 种角色。

- Provider：RPC 服务提供者。
- Container：容器，用于启动、停止 Provider 服务。
- Consumer：消费者，调用的发起者。
- Registry：注册中心，与微服务注册中心职责类似。
- Monitor：监控器，监控器提供了 Dubbo 的监控职责。在 Dubbo 产生通信时，Monitor 进行收集、统计，并通过可视化 UI 界面帮助运维人员了解系统进程间的通信状况。

**Dubbo与 Nacos 协同作业：开发 Provider 仓储服务**

还是以“订单与库存服务”案例为例。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210808223251.png" alt="image-20210808223251858" style="zoom:67%;" />

第一步：引入 pom.xml 依赖。

```xml
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
</dependency>
<dependency>
    <groupId>org.apache.dubbo</groupId>
    <artifactId>dubbo-spring-boot-starter</artifactId>
    <version>2.7.8</version>
</dependency>
```

第二步：配置 application.yml 文件。

```yaml
spring:
  application:
    name: warehouse-service #微服务id
  cloud:
    nacos: #nacos注册地址
      discovery:
        server-addr: 192.168.31.101:8848
        username: nacos
        password: nacos

dubbo: #dubbo与nacos的通信配置
  application:
    name: warehouse-dubbo #provider在Nacos中的应用id
  registry: #Provider与Nacos通信地址，与spring.cloud.nacos地址一致
    address: nacos://192.168.31.101:8848
  protocol: 
    name: dubbo #通信协议名
    port: 20880 #配置通信端口，默认为20880
  scan: 
    base-packages: com.lagou.warehouseservice.dubbo
```

注册示意图如下：

![image-20210808225440206](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210808225440.png)

第三步：开发接口与实现类。

```java
// Dubbo 在对象传输过程中使用了 JDK 序列化，对象必须实现 Serializable 接口。
public class Stock implements Serializable {
    private Long skuId; //商品品类编号
    private String title; //商品与品类名称
    private Integer quantity; //库存数量
    private String unit; //单位
    private String description; //描述信息
}

//Provider接口
public interface WarehouseService {
    //查询库存
    public Stock getStock(Long skuId);
}

@DubboService
public class WarehouseServiceImpl implements WarehouseService {
    public Stock getStock(Long skuId){
        //...
    }
}
```

第四步：启动微服务。

可以看到下图效果：

![image-20210808225924093](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210808225924.png)

**Dubbo与 Nacos 协同作业：开发 Consumer 订单服务**

第一步：引入 pom.xml 依赖。

```xml
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
</dependency>
<dependency>
    <groupId>org.apache.dubbo</groupId>
    <artifactId>dubbo-spring-boot-starter</artifactId>
    <version>2.7.8</version>
</dependency>
```

第二步，设置微服务、Dubbo 与 Nacos通信选项。

```yaml
spring:
  application:
    name: order-service
  cloud:
    nacos:
      discovery:
        server-addr: 192.168.31.101:8848
        username: nacos
        password: nacos
server:
  port: 9000
dubbo:
  application:
    name: order-service-dubbo
  registry:
    address: nacos://192.168.31.101:8848
```

第三步，将 Provider 端接口 WarehouseService 以及依赖的 Stock类复制到 order-service 工程，注意要求包名、类名及代码保持完全一致。

第四步，Consumer 调用接口实现业务逻辑。

```java
@RestController
public class OrderController {
    
    @DubboReference
    private WarehouseService warehouseService;
    
    @GetMapping("/create_order")
    public Map createOrder(Long skuId , Long salesQuantity){
        // ...
        //查询商品库存，像调用本地方法一样完成业务逻辑。
        Stock stock = warehouseService.getStock(skuId);
        // ...
    }
}
```

业务逻辑如下图所示：

![image-20210808230506545](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210808230506.png)

第五步，启动微服务，验证 Nacos 注册信息。

![image-20210808230529484](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210808230529.png)

此时 Consumer 已在服务列表中出现，说明消费者已注册成功。

# 09 | 服务门户：Spring Cloud Gateway 如何把好微服务的大门

**API 网关的作用**

- 针对所有请求进行统一鉴权、熔断、限流、日志等前置处理，让微服务专注自己的业务。
- 统一调用风格，大幅度简化用户的接入难度。
- 更好的安全性，在通过 API 网关鉴权后，可以控制不同角色用户访问后端服务的权利，实现了服务更细粒度的权限控制。
- 微服务架构通过引入 API 网关，将用户端与微服务的具体实现进行了解耦。

**API 网关主流产品**

- OpenResty

OpenResty 是一个强大的 Web 应用服务器，可以快速构造出足以胜任 10K 以上并发连接响应的超高性能 Web 应用系统。

但 OpenResty 是一款独立的产品，与主流的注册中心存在一定兼容问题，需要架构师独立实现其服务注册、发现的功能。

- Spring Cloud Zuul

Zuul 是 Netflix 开源的微服务网关，它的主要职责是对用户请求进行路由转发与过滤。

后来 Netflix 内部产生分歧，Netflix 官方宣布 Zuul 停止维护，这让 Spring 机构也必须转型。于是 Spring Cloud 团队决定开发自己的第二代 API 网关产品：Spring Cloud Gateway。

- Spring Cloud Gateway

Spring Cloud Gateway 是 Spring 自己开发的新一代 API 网关产品。它基于 NIO 异步处理，摒弃了 Zuul 基于 Servlet 同步通信的设计，因此拥有更好的性能。

**Spring Cloud Gateway使用入门**

示例说明：

假设“service-a”微服务提供了三个 RESTful 接口。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210809224559.png" alt="image-20210809224559049" style="zoom:50%;" />

假设 “service-b” 微服务提供了三个 RESTful 接口。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210809224624.png" style="zoom:50%;" />

如何通过部署 Spring Cloud Gateway 实现 API 路由功能来屏蔽后端细节呢？

第一步：引入 pom.xml 依赖。

```xml
<dependency>
  <groupId>org.springframework.cloud</groupId>
  <artifactId>spring-cloud-starter-gateway</artifactId>
</dependency>
```

第二步，在 application.yml 增加如下配置。

```yaml
spring:
  application:
    name: gateway #配置微服务id
  cloud:
    nacos:
      discovery:
        #nacos通信地址
        server-addr: 192.168.31.101:8848 
        username: nacos
        password: nacos
    gateway: #让gateway通过nacos实现自动路由转发
      discovery:
        locator:
          #locator.enabled是自动根据URL规则实现路由转发
          enabled: true
```

`spring.cloud.gateway.discovery.locator.enabled=true`这项配置允许 Gateway 自动实现后端微服务路由转发，例如，网关 IP 为：192.168.31.103，我们需要通过网关执行 service-a 的 list 方法，具体写法为：

```http
http://192.168.31.103:80/service-a/list
```

访问后 Gateway 按下图流程进行请求路由转发。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210809223117.png" alt="image-20210809223117733" style="zoom:67%;" />

**谓词（Predicate）与过滤器（Filter）**

路由（Route）是指一个完整的网关地址映射与处理过程。一个完整的路由包含两部分配置：谓词（Predicate）与过滤器（Filter）。

前端应用发来的请求要被转发到哪个微服务上，是由谓词决定的；而转发过程中请求、响应数据被网关如何加工处理是由过滤器决定的。

- 谓词（Predicate）

这里我们给出一个实例，将原有 Gateway 工程的 application.yml 文件修改为下面的设置：

```yaml
spring:
  application:
    name: gateway
  cloud:
    nacos:
      discovery:
        server-addr: 192.168.31.10:8848
        username: nacos
        password: nacos
    gateway: 
      discovery:
        locator:
          #不再需要Gateway路由转发
          enabled: false 
      routes:  #路由规则配置
        #第一个路由配置，service-a路由规则
        - id: service_a_route #路由唯一标识
          #lb开头代表基于gateway的负载均衡策略选择实例
          uri: lb://service-a 
          #谓词配置
          predicates:
            #Path路径谓词，代表用户端URI如果以/a开头便会转发到service-a实例
            - Path=/a/** 
            #After生效时间谓词，2020年10月15日后该路由才能在网关对外暴露
            - After=2020-10-05T00:00:00.000+08:00[Asia/Shanghai]
          #过滤器配置
          filters:
            #忽略掉第一层前缀进行转发
            - StripPrefix=1 
            #为响应头附加X-Response=Blue
            - AddResponseHeader=X-Response,Blue 
        #第二个路由配置，service-b路由规则
        - id: service_b_route
          uri: lb://service-b
          predicates:
            - Path=/b/**
          filters:
            - StripPrefix=1
```

在 2020 年 10 月 15 日后，当用户端发来/a/...开头的请求时，Spring Cloud Gateway 会自动获取 service-a 可用实例，默认采用轮询方式将URI附加至实例地址后，形成新地址，service-a处理后 Gateway 网关自动在响应头附加 X-Response=Blue。

第二个 service_b_route，说明当用户访问/b开头 URL 时，转发到 service-b 可用实例。

- 过滤器（Filter）

过滤器（Filter）可以对请求或响应的数据进行额外处理，这里我们列出三个最常用的内置过滤器进行说明。

AddRequestParameter 是对所有匹配的请求添加一个查询参数。

```yaml
filters:
  #在请求参数中追加foo=bar
  - AddRequestParameter=foo,bar
```

AddResponseHeader 会对所有匹配的请求，在返回结果给客户端之前，在 Header 中添加响应的数据。

```yaml
#在Response中添加Header头，key=X-Response-Foo，Value=Bar。
filters:
  - AddResponseHeader=X-Response,Blue
```

Retry 为重试过滤器，当后端服务不可用时，网关会根据配置参数来发起重试请求。

```yaml
filters:
  #涉及过滤器参数时，采用name-args的完整写法
  - name: Retry #name是内置的过滤器名
    args: #参数部分使用args说明
      retries: 3
      status: 503
```

**Spring Cloud Gateway 的执行原理**

下图是 Spring Cloud Gateway 的执行流程。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210809223635.png" alt="img" style="zoom: 67%;" />

在整个处理过程中谓词（Predicate）与过滤器（Filter）起到了重要作用，谓词决定了路径的匹配规则，让 Gateway 确定应用哪个微服务，而 Filter 则是对请求或响应作出实质的前置、后置处理。

在项目中功能场景多种多样，像日常的用户身份鉴权、日志记录、黑白名单、反爬虫等基础功能都可以通过自定义 Filter 为 Gateway 进行功能扩展。

下面我们通过“计时过滤器”为例，讲解如何为 Gateway 绑定自定义全局过滤器。

**自定义全局过滤器**

在 Spring Cloud Gateway 中，自定义过滤器分为两种，全局过滤器与局部过滤器。两者唯一的区别是：全局过滤器默认应用在所有路由（Route）上，而局部过滤器可以为指定的路由绑定。

下面通过“计时过滤器”这个案例讲解全局过滤器的配置。所谓计时过滤器是指任何从网关访问的请求，都要在日志中记录下从请求进入到响应退出的执行时间，通过这个时间运维人员便可以收集并分析哪些功能进行了慢处理，以此为依据进行进一步优化。

下面是计时过滤器的代码，重要的部分我通过注释进行了说明。

```java
@Component //自动实例化并被Spring IOC容器管理
//全局过滤器必须实现两个接口：GlobalFilter、Ordered
//GlobalFilter是全局过滤器接口，实现类要实现filter()方法进行功能扩展
//Ordered接口用于排序，通过实现getOrder()方法返回整数代表执行当前过滤器的前后顺序
public class ElapsedFilter implements GlobalFilter, Ordered {
    //基于slf4j.Logger实现日志输出
    private static final Logger logger = LoggerFactory.getLogger(ElapsedFilter.class);
    //起始时间属性名
    private static final String ELAPSED_TIME_BEGIN = "elapsedTimeBegin";
    /**
     * 实现filter()方法记录处理时间
     
     * @param exchange 用于获取与当前请求、响应相关的数据，以及设置过滤器间传递的上下文数据
     * @param chain Gateway过滤器链对象
     * @return Mono对应一个异步任务，因为Gateway是基于Netty Server异步处理的,Mono对就代表异步处理完毕的情况。
     */
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        //Pre前置处理部分
        //在请求到达时，往ServerWebExchange上下文环境中放入了一个属性elapsedTimeBegin，保存请求执行前的时间戳
        exchange.getAttributes().put(ELAPSED_TIME_BEGIN, System.currentTimeMillis());

        //chain.filter(exchange).then()对应Post后置处理部分
        //当响应产生后，记录结束与elapsedTimeBegin起始时间比对，获取RESTful API的实际执行时间
        return chain.filter(exchange).then(
                Mono.fromRunnable(() -> { //当前过滤器得到响应时，计算并打印时间
                    Long startTime = exchange.getAttribute(ELAPSED_TIME_BEGIN);
                    if (startTime != null) {
                        logger.info(exchange.getRequest().getRemoteAddress() //远程访问的用户地址
                                + " | " +  exchange.getRequest().getPath()  //Gateway URI
                                + " | cost " + (System.currentTimeMillis() - startTime) + "ms"); //处理时间
                    }
                })
        );
    }
    //设置为最高优先级，最先执行ElapsedFilter过滤器
    //return Ordered.LOWEST_PRECEDENCE; 代表设置为最低优先级
    @Override
    public int getOrder() {
        return Ordered.HIGHEST_PRECEDENCE;
    }
}
```

运行后通过 Gateway 访问任意微服务便会输出日志：

```shell
2021-01-10 12:36:01.765  INFO 14052 --- [ctor-http-nio-4] com.lagou.gateway.filter.ElapsedFilter   : /0:0:0:0:0:0:0:1:57873 | /test-service/test | cost 821ms
```

# ==模块四 系统保护==

# 10 | 系统保护：微服务架构雪崩效应与服务限流

**微服务的雪崩效应**

“雪崩”一词指的是山地积雪由于底部溶解等原因造成的突然大块塌落的现象，具有很强的破坏力。

在微服务项目中指由于突发流量导致某个服务不可用，从而导致上游服务不可用，并产生级联效应，最终导致整个系统不可用。

为什么微服务会产生雪崩效应？

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210810231240.png" alt="image-20210810231240612" style="zoom:50%;" />

假如服务 I 因为优化问题，导致需要 20 秒才能返回响应，这就必然会导致 20 秒内该请求线程会一直处于阻塞状态。

假如在 20 秒内有 10 万个请求通过应用访问到后端微服务。容器会因为大量请求阻塞积压导致连接池爆满，而这种情况后果极其严重！轻则“服务无响应”，重则前端应用直接崩溃。

如何有效避免雪崩效应？

- 采用限流方式进行预防：控制请求的流入，让流量有序的进入应用，保证流量在一个可控的范围内。
- 采用服务降级进行补救：服务降级是指当应用处理时间超过规定上限后，无论服务是否处理完成，便立即触发服务降级，响应返回预先设置的异常信息。

**Alibaba Sentinel**

Sentinel 以流量为切入点，从流量控制、熔断降级、系统负载保护等多个维度保护服务的稳定性。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210810231651.png" alt="image-20210810231651809" style="zoom:67%;" />

Sentinel 分为两个部分：Sentinel Dashboard 和 Sentinel 客户端。

如何部署 Sentinel Dashboard（仪表盘）？

- 下载最新版 Sentinel Dashboard

访问：https://github.com/alibaba/Sentinel/releases。

- 启动 Dashboard

```shell
java -jar -Dserver.port=9100 sentinel-dashboard-1.8.0.jar
```

- 登录控制台

输入 sentinel/sentinel，便可进入 Dashboard。

![image-20210810232105397](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210810232105.png)

**微服务内置 Sentinel 客户端**

- 第一步：引入 pom.xml 依赖。

```xml
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-sentinel</artifactId>
</dependency>
```

- 第二步：配置 application.yml。

```yaml
spring:
  application:
    name: sentinel-sample #应用名&微服务id
  cloud:
    sentinel: #Sentinel Dashboard通信地址
      transport:
        dashboard: 192.168.31.10:9100
      eager: true #取消控制台懒加载
    nacos: #Nacos通信地址
      server-addr: 192.168.31.10:8848
      username: nacos
      password: nacos
```

- 第三步，验证配置。

在 Sentinel Dashboard 左侧看到 sentinel-sample 服务出现，则代表 Sentinel 客户端与 Dashboard 已经完成通信。

![image-20210810232335630](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210810232335.png)

如何配置限流规则？

- 第一步：编写模拟接口。

```java
@RestController
public class SentinelSampleController {
    @GetMapping("/test_flow_rule")
    public String testFlowRule(){
        return "SUCCESS";
    }
}
```

访问http://localhost/test_flow_rule，无论刷新多少次，都会看到“SUCCESS”。

- 第二步，访问 Sentinel Dashboard 配置限流规则。

在左侧找到簇点链路，右侧定位到 /test_flow_rule，点击后面的“流控”按钮。

![image-20210810232618999](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210810232619.png)

为 /test_flow_rule 接口配置每秒钟只允许 1QPS 访问。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210810232706.png" alt="image-20210810232706581" style="zoom: 50%;" />

此时针对 /test_flow_rule 接口的流控规则已生效，可以在“流控规则”面板看到。

![image-20210810232739728](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210810232739.png)

- 第三步，验证流控效果。

重新访问http://localhost/test_flow_rule，第一次刷新时会出现“SUCCESS”文本代表处理成功。

同一秒内再次刷新便会出现 “Blocked by Sentinel (flow limiting)”，代表服务已被限流降级。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210810232823.png" alt="image-20210810232823597" style="zoom:50%;" />

# 11 | 限流与熔断：Sentinel 在项目中的最佳实践

**Sentinel 的执行流程**

Sentinel 的执行流程分为三个阶段：

- Sentinel Core 与 Sentinel Dashboard 建立连接；
- Sentinel Dashboard 向 Sentinel Core 下发新的保护规则；
- Sentinel Core 应用新的保护规则，实施限流、熔断等动作。

第一步，建立连接。

请求是以心跳包的方式定时向 Dashboard 发送，包含 Sentinel Core 的 AppName、IP、端口信息。

> 这里有个重要细节：Sentinel Core 为了能够持续接收到来自 Dashboard 的数据，会在微服务实例设备上监听 8719 端口，在心跳包上报时也是上报这个 8719 端口，而非微服务本身的 80 端口。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210811225452.png" alt="image-20210811225452372" style="zoom:50%;" />

在 Sentinel Dashboard 接收到心跳包后，来自 Sentinel Core 的 AppName、IP、端口信息会被封装为 MachineInfo 对象放入 ConcurrentHashMap 保存在 JVM 的内存中，以备后续使用。

第二步，推送新规则。

如果在 Dashboard 页面中设置了新的保护规则，会（第一）先从当前的 MachineInfo 中提取符合要求的微服务实例信息，（第二）之后通过 Dashboard 内置的 transport 模块将新规则打包推送到微服务实例的 Sentinel Core，（第三）Sentinel Core 收到新规则在微服务应用中对本地规则进行更新，这些新规则会保存在微服务实例的 JVM 内存中。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210811230108.png" alt="image-20210811230108150" style="zoom:50%;" />

第三步，处理请求。

Sentinel Core 为服务限流、熔断提供了核心拦截器 SentinelWebInterceptor，这个拦截器默认对所有请求 /** 进行拦截，然后开始请求的链式处理流程。

在对于每一个处理请求的节点被称为 Slot（槽），通过多个槽的连接形成处理链，在请求的流转过程中，如果有任何一个 Slot 验证未通过，都会产生 BlockException，请求处理链便会中断，并返回 “Blocked by sentinel" 异常信息。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210811230332.png" alt="img" style="zoom:67%;" />

前 3 个 Slot为前置处理，用于收集、统计、分析必要的数据；后 4 个为规则校验 Slot，从 Dashboard 推送的新规则保存在“规则池”中，然后对应 Slot 进行读取并校验当前请求是否允许放行，允许放行则送入下一个 Slot 直到最终被 RestController 进行业务处理，不允许放行则直接抛出 BlockException 返回响应。

**Sentinel 限流降级算法：滑动窗口算法**

实现限流降级的核心是如何统计单位时间某个接口的访问量，常见的算法有计数器算法、令牌桶算法、漏桶算法、滑动窗口算法。Sentinel 采用滑动窗口算法来统计访问量。

假设某应用限流控制 1 分钟最多允许 600 次访问。采用滑动窗口算法是将每 1 分钟拆分为 6（变量）个等份时间段，每个时间段为 10 秒，6 个时间段为 1 组在下图用红色边框区域标出，而这个红色边框区域就是滑动窗口。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210811231230.png" alt="image-20210811231230786" style="zoom:50%;" />

每当产生 1 个访问则在对应时间段的计数器自增加 1，当滑动窗口内所有时间段的计数器总和超过 600，后面新的访问将被限流直接拒绝。同时每过 10 秒，滑动窗口向右移动，前面的过期时间段计数器将被作废。

**使用 Sentinel Dashboard 进行限流设置**

第一，在 Sentinel Dashboard 中“簇点链路”，找到需要限流的 URI，点击“+流控”进入流控设置。

![image-20210811231550033](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210811231550.png)

> 小提示，sentinel-dashboard 基于懒加载模式，如果在簇点链路没有找到对应的 URI，需要先访问下这个功能，对应的 URI 便会出现。

第二，点击后，弹出下框：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210811231704.png" alt="image-20210811231704413" style="zoom:50%;" />

- 资源名：要流控的 URI，在 Sentinel 中 URI 被称为“资源”；
- 针对来源：默认 default 代表所有来源，可以针对某个微服务或者调用者单独设置；
- 阈值类型：是按每秒访问数量（QPS）还是并发数（线程数）进行流控；
- 单机阈值：具体限流的数值是多少。

第三，点击对话框中的“高级选项”，就会出现更为详细的设置项。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210811232050.png" alt="image-20210811232050554" style="zoom:50%;" />

流控模式是指采用什么方式进行流量控制。Sentinel支持三种模式：直接、关联、链路。

- 直接模式：以上图为例，当 List 接口 QPS 超过 1，浏览器会出现“Blocked by Sentinel”。

- 关联模式：

  当 List 接口关联的 update 接口 QPS 超过 1 时，再次访问List 接口便会响应“Blocked by Sentinel”。

  <img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210811232422.png" alt="image-20210811232422736" style="zoom:50%;" />

- 链路模式：

  以下图为例，在某个微服务中 List 接口，会被 Check 接口调用。在另一个业务，List 接口也会被 Scan 接口调用。

  <img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210811224358.png" alt="image-20210811224358399" style="zoom: 33%;" />

  如果按下图配置，将入口资源设为“/check”，则只会针对 check 接口的调用链路生效。

  <img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210811232921.png" alt="image-20210811232921202" style="zoom: 67%;" />

  当访问 check 接口的 QPS 超过 1 时，List 接口就会被限流。而另一条链路从 scan 接口到 List 接口的链路则不会受到任何影响。

流控效果是指在达到流控条件后，对当前请求如何处理。流控效果有三种：快速失败、Warm UP（预热）、排队等待。

- 快速失败：指流量超过限流阈值后，直接返回响应并抛出 BlockException，快速失败是最常用的处理形式。

- Warm Up（预热）：用于应对瞬时大并发流量冲击。当遇到突发大流量时，Warm Up 会缓慢拉升阈值限制，预防系统瞬时崩溃，这期间超出阈值的访问处于队列等待状态，并不会立即抛出 BlockException。

  如下图所示，List 接口平时单机阈值 QPS 处于低水位：默认为 1000/3 (冷加载因子)≈333，当瞬时大流量进来，10 秒钟内将 QPS 阈值逐渐拉升至 1000，为系统留出缓冲时间，预防突发性系统崩溃。

  ![image-20210811233406680](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210811233406.png)

- 排队等待：排队等待是采用匀速放行的方式对请求进行处理。如下所示，假设现在有 100 个请求瞬间进入，那么会出现以下几种情况：

  单机 QPS 阈值=1，代表每 1 秒只能放行 1 个请求，其他请求队列等待，共需 100 秒处理完毕；

  单机 QPS 阈值=4，代表 250 毫秒匀速放行 1 个请求，其他请求队列等待，共需 25 秒处理完毕；

  <img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210811233847.png" alt="image-20210811233847710" style="zoom:67%;" />

  如果某一个请求在队列中处于等待状态超过 2000 毫秒，则直接抛出 BlockException。

**使用 Sentinel Dashboard 进行熔断降级设置**

在股市中，熔断条件就是大盘跌幅超过 5%，而熔断的措施便是强制停止交易 15 分钟，之后尝试恢复交易，如仍出现继续下跌，便会再次触发熔断直接闭市。但假设 15 分钟后，大盘出现回涨，便认为事故解除继续正常交易。这是现实生活中的熔断。

下图清晰的说明了 Sentinel 的熔断过程：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210811224812.png" alt="image-20210811224812688" style="zoom: 50%;" />

Sentinel Dashboard 可以设置三种不同的熔断模式：慢调用比例、异常比例、异常数。

- 慢调用比例是指当接口在 1 秒内“慢处理”数量超过一定比例，则触发熔断。

  <img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210811234457.png" alt="image-20210811234457180" style="zoom:50%;" />

  <img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210811234712.png" alt="image-20210811234712010" style="zoom: 67%;" />

- 异常比例是指 1 秒内按接口调用产生异常的比例（异常调用数/总数量）触发熔断。

  <img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210811234529.png" alt="image-20210811234529852" style="zoom:50%;" />

  <img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210811234738.png" alt="image-20210811234738056" style="zoom:67%;" />

- 异常数是指在 1 分钟内异常的数量超过阈值则触发熔断。

  <img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210811234809.png" alt="image-20210811234809488" style="zoom:50%;" />

  <img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210811234826.png" alt="image-20210811234826401" style="zoom:67%;" />

# 12 | 配置中心：基于 Nacos 集中管理应用配置

配置中心的职责是集中管理微服务架构中每一个服务实例的配置数据。当微服务架构引入配置中心后，微服务应用只需持有应用启动的最小化配置。

当引入配置中心后，微服务的架构会产生如下变化。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210812223749.png" alt="image-20210812223749823" style="zoom:67%;" />

**微服务接入 Nacos 配置中心**

第一步，创建工程引入依赖。

```xml
<!-- Nacos注册中心starter -->
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
</dependency>
<!-- Nacos配置中心starter -->
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-config</artifactId>
</dependency>
```

第二步，在 resources 目录下创建 bootstrap.yml 引导文件。

> 注意，bootstrap.yml 文件名是固定的，不能随意改变。

```yaml
spring:
  application:
    name: order-service #微服务id
  profiles:
    active: dev #环境名
  cloud:
    nacos:
      config: #Nacos配置中心配置
        file-extension: yml #文件扩展名
        server-addr: 192.168.31.10:8848
        username: nacos
        password: nacos
logging: #开启debug日志，仅为学习时使用
  level:
    root: debug
```

通过文件中的 “微服务 id”-“环境名”.“文件扩展名” 三部分组合为有效的 data id，即 order-service-dev.yml。

第三步，打开 Nacos 配置中心页面，点击右上角“+”号新建配置。

![image-20210812224424868](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210812224424.png)

![image-20210812224508963](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210812224509.png)

- Data ID：配置的唯一标识，格式固定为：{微服务id}-{环境名}.yml，例如 order-service-dev.yml。
- Group：指定配置文件的分组，这里设置默认分组 DEFAULT_GROUP 即可。

配置完成后在 nacos_config 数据库的 config_info 表中也出现了对应配置数据。

**Nacos 生产环境中的配置技巧**

- 配置热加载技术

Nacos 采用的是一种长轮询机制以支持配置的热加载。当客户端发起 Pull 请求后，服务端先检查配置是否发生了变更，如果有变更，则立即返回最新的配置；如果没有，则设置一个定时任务，延迟 29.5s 执行，并且把当前的客户端长轮询连接加入 allSubs 队列。如图所示：

![image-20210812230219145](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210812230219.png)

这时候有两种方式触发该连接结果的返回：

第一种是在等待 29.5s 后触发自动检查机制，这时候不管配置有没有发生变化，都会把结果返回客户端。而 29.5s 就是这个长连接保持的时间。

第二种是在 29.5s 内任意一个时刻，通过 Nacos Dashboard 或者 API 的方式对配置进行了修改，这会触发一个事件机制，监听到该事件的任务会遍历 allSubs 队列，找到发生变更的配置项对应的 ClientLongPolling 任务，将变更的数据通过该任务中的连接进行返回，就完成了一次“推送”操作。

> 服务端“Hold”住请求的这个动作，有无必要？

为了支持热加载，服务 A 需要满足如下要求：

第一，配置数据必须被封装到单独的 Bean 中；

第二，这个配置 Bean 需要被 @Configuration 与 @RefreshScope 两个注解描述。

```java
@Configuration
@RefreshScope
public class CustomConfig {
    @Value("${custom.flag}")
    private String flag;
    @Value("${custom.database}")
    private String database;
}
```

- 切换环境配置文件

假如产品开发完成准备上线，可利用 Nacos 迅速完成从开发到生产环境的切换。

第一步，在 Nacos 中设置生产环境的配置，Data Id 为 order-service-prod.yml。

第二步，调整 order-service 的 bootstrap.yml 引导文件，修改`spring.profiles.active`为 prod，同时更换生产环境 Nacos 地址。

- 管理基础配置数据

对于基础的全局配置，我们可以将其存放到单独的 order-service.yml 配置中，在 order-service 服务启动时，这个不带环境名的配置文件必然会被加载。

# 13 | 生产实践：Sentinel 进阶应用场景

本讲咱们学习如何在生产环境下通过 Nacos 实现 Sentinel 规则持久化。本讲咱们将介绍三方面内容：

- Sentinel 与 Nacos 整合实现规则持久化；
- 自定义资源点进行熔断保护；
- 开发友好的异常处理程序。

**Sentinel 与 Nacos 整合实现规则持久化**

在前面 Sentinel 的使用过程中，当微服务重启以后所有的配置规则都会丢失，其中的根源是默认微服务将 Sentinel 的规则保存在 JVM 内存中，当应用重启后 JVM 内存销毁，规则就会丢失。为了解决这个问题，我们就需要通过某种机制将配置好的规则进行持久化保存，同时这些规则变更后还能及时通知微服务进行变更。

无论是配置数据的持久化特性还是配置中心主动推送的特性都是我们需要的，因此 Nacos 自然就成了 Sentinel 规则持久化的首选。

首先，咱们快速构建演示工程 sentinel-sample。

第一步，pom.xml 增加以下三项依赖。

```xml
<!-- Nacos 客户端 Starter-->
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
</dependency>
<!-- Sentinel 客户端 Starter-->
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-sentinel</artifactId>
</dependency>
<!-- 对外暴露 Spring Boot 监控指标-->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

第二步，配置 Nacos 与 Sentinel 客户端。

```yaml
spring:
  application:
    name: sentinel-sample #应用名&微服务 id
  cloud:
    sentinel: #Sentinel Dashboard 通信地址
      transport:
        dashboard: 192.168.31.10:9100
      eager: true #取消控制台懒加载
    nacos: #Nacos 通信地址
      server-addr: 192.168.31.10:8848
      username: nacos
      password: nacos
  jackson:
    default-property-inclusion: non_null
server:
  port: 80
management:
  endpoints:
    web: #将所有可用的监控指标项对外暴露
      exposure: #可以访问 /actuator/sentinel进行查看Sentinel监控项
        include: '*'
logging:
  level:
    root: debug #开启 debug 是学习需要，生产改为 info 即可
```

第三步，在 sentinel-sample 服务中，增加 SentinelSampleController 类，用于演示运行效果。

```java
@RestController
public class SentinelSampleController {
    //演示用的业务逻辑类
    @Resource
    private SampleService sampleService;
    /**
     * 流控测试接口
     * @return
     */
    @GetMapping("/test_flow_rule")
    public ResponseObject testFlowRule(){
        //code=0 代表服务器处理成功
        return new ResponseObject("0","success!");
    }

    /**
     * 熔断测试接口
     * @return
     */
    @GetMapping("/test_degrade_rule")
    public ResponseObject testDegradeRule(){
        try {
            sampleService.createOrder();
        } catch (IllegalStateException e){
            //当 createOrder 业务处理过程中产生错误时会抛出IllegalStateException
            //IllegalStateException 是 JAVA 内置状态异常，在项目开发时可以更换为自己项目的自定义异常
            //出现错误后将异常封装为响应对象后JSON输出
            return new ResponseObject(e.getClass().getSimpleName(),e.getMessage());
        }
        return new ResponseObject("0","order created!");
    }
}
```

ResponseObject 对象封装了响应的数据。

```java
/**
 * 封装响应数据的对象
 */
public class ResponseObject {
    private String code; //结果编码，0-固定代表处理成功
    private String message;//响应消息
    private Object data;//响应附加数据（可选）
 
    public ResponseObject(String code, String message) {
        this.code = code;
        this.message = message;
    }
    //Getter/Setter省略
}
```

第四步，额外增加 SampleService 用于模拟业务逻辑，等下我们将用它讲解自定义资源点与熔断设置。

```java
/**
 * 演示用的业务逻辑类
 */
@Service
public class SampleService {
    //模拟创建订单业务
    public void createOrder(){
        try {
            //模拟处理业务逻辑需要101毫秒
            Thread.sleep(101);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println("订单已创建");
    }
}
```

工程创建完成，下面咱们将 Sentinel 接入 Nacos 配置中心。

第一步，pom.xml 新增 sentinel-datasource-nacos 依赖。

```xml
<dependency>
    <groupId>com.alibaba.csp</groupId>
    <artifactId>sentinel-datasource-nacos</artifactId>
</dependency>
```

sentinel-datasource-nacos 是 Sentinel 为 Nacos 扩展的数据源模块，允许将规则数据存储在 Nacos 配置中心，在微服务启动时利用该模块 Sentinel 会自动在 Nacos 下载对应的规则数据。

第二步，在 application.yml 文件中增加 Nacos 下载规则，在原有的 sentinel 配置下新增 datasource 选项。

```yaml
spring:
  application:
    name: sentinel-sample #应用名&微服务id
  cloud:
    sentinel: #Sentinel Dashboard通信地址
      transport:
        dashboard: 192.168.31.10:9100
      eager: true #取消控制台懒加载
      datasource:
        flow: #数据源名称，可以自定义
          nacos: #nacos配置中心
            #Nacos内置配置中心，因此重用即可
            server-addr: ${spring.cloud.nacos.server-addr}
            #定义流控规则data-id，完整名称为:sentinel-sample-flow-rules，在配置中心设置时data-id必须对应。
            dataId: ${spring.application.name}-flow-rules
            #gourpId对应配置文件分组，对应配置中心groups项
            groupId: SAMPLE_GROUP
            #flow固定写死，说明这个配置是流控规则
            rule-type: flow
            #nacos通信的用户名与密码
            username: nacos
            password: nacos
    nacos: #Nacos通信地址
      server-addr: 192.168.31.10:8848
      username: nacos
      password: nacos
    ...
```

通过这一份配置，微服务在启动时就会自动从 Nacos 配置中心 SAMPLE_GROUP 分组下载 data-id 为 sentinel-sample-flow-rules 的配置信息并将其作为流控规则生效。

第三步，在 Nacos 配置中心页面，新增 data-id 为sentinel-sample-flow-rules 的配置项。

```json
[
    {
        "resource":"/test_flow_rule", #资源名，说明对那个URI进行流控
        "limitApp":"default",  #命名空间，默认default
        "grade":1, #类型 0-线程 1-QPS
        "count":2, #超过2个QPS限流将被限流
        "strategy":0, #限流策略: 0-直接 1-关联 2-链路
        "controlBehavior":0, #控制行为: 0-快速失败 1-WarmUp 2-排队等待
        "clusterMode":false #是否集群模式
    }
]
```

这些配置项与 Dashboard UI 中的选项是对应的。更多细节可参考：[流量控制](https://github.com/alibaba/Sentinel/wiki/%E6%B5%81%E9%87%8F%E6%8E%A7%E5%88%B6?fileGuid=xxQTRXtVcqtHK6j8)

最后，我们启动应用来验证流控效果。

咱们在浏览器反复刷新，当 test_flow_rule 接口每秒超过 2 次访问，就会出现“Blocked by Sentinel (flow limiting)”的错误信息，说明流控规则已生效。

之后我们再来验证能否自动推送新规则，将 Nacos 配置中心中流控规则 count 选项改为 1。我们可以通过 Spring Boot Actuator 提供的监控指标确认流控规则已生效。访问 http://localhost/actuator/sentinel。

![image-20240606233839578](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406062338832.png)

**自定义资源点进行熔断保护**

在前面一系列 Sentinel 的讲解中我们都是针对 RESTful 的接口进行限流熔断设置，但是在项目中有的时候是要针对某一个 Service 业务逻辑方法进行限流熔断等规则设置，这要怎么办呢？

在 sentinel-core 客户端中为开发者提供了 @SentinelResource 注解，该注解允许在程序代码中自定义 Sentinel 资源点来实现对特定方法的保护，下面我们以熔断降级规则为例来进行讲解。

第一步，声明切面类。

```java
@SpringBootApplication
public class SentinelSampleApplication {
    // 注解支持的配置Bean
    @Bean
    public SentinelResourceAspect sentinelResourceAspect() {
        return new SentinelResourceAspect();
    }
    public static void main(String[] args) {
        SpringApplication.run(SentinelSampleApplication.class, args);
    }
}
```

sentinel-core 是基于 Spring AOP 在目标 Service 方法执行前按熔断规则进行检查，只允许有效的数据被送入目标方法进行处理。SentinelResourceAspect 就是 Sentinel 提供的切面类，用于进行熔断的前置检查。

第二步，声明资源点。

在 SampleService.createOrder 方法上增加 @SentinelResource 注解用于声明 Sentinel 资源点，只有声明了资源点，Sentinel 才能实施限流熔断等保护措施。

```java
/**
 * 演示用的业务逻辑类
 */
@Service
public class SampleService {
    //资源点名称为createOrder
    @SentinelResource("createOrder")
    /**
     * 模拟创建订单业务
     * 抛出IllegalStateException异常用于模拟业务逻辑执行失败的情况
     */
    public void createOrder() throws IllegalStateException{
        try {
            //模拟处理业务逻辑需要101毫秒
            Thread.sleep(101);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println("订单已创建");
    }
}
```

修改完毕，启动服务。然后打开访问 Sentinel Dashboard，在簇点链路中要确认 createOrder资源点已存在。

![Drawing 3.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406062346098.png)

第三步，获取熔断规则。

打开sentinel-sample 工程的 application.yml 文件，将服务接入 Nacos 配置中心的参数以获取熔断规则。

```yaml
datasource:
  flow: #之前的流控规则，直接忽略
    ...
  degrade: #熔断规则
    nacos:
      server-addr: ${spring.cloud.nacos.server-addr}
      dataId: ${spring.application.name}-degrade-rules
      groupId: SAMPLE_GROUP
      rule-type: degrade #代表熔断
     username: nacos
     password: nacos
```

熔断规则的获取过程和前面流控规则类似，只不过 data-id 改为sentinel-sample-degrade-rules，以及 rule-type 更改为 degrade。

第四步，在 Nacos 配置熔断规则。

设置 data-id 为 sentinel-sample-degrade-rules，Groups 为 SAMPLE_GROUP 与微服务的设置保持一致。

```json
[{
    "resource": "createOrder", #自定义资源名
    "limitApp": "default", #命名空间
    "grade": 0, #0-慢调用比例 1-异常比例 2-异常数
    "count": 100, #最大RT 100毫秒执行时间
    "timeWindow": 5, #时间窗口5秒
    "minRequestAmount": 1, #最小请求数
    "slowRatioThreshold": 0.1 #比例阈值
}]
```

上面这段 JSON 完整的含义是：

![图片1-.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406062348452.png)

设置成功，访问 Spring Boot Actuator：http://localhost/actuator/sentinel，可以看到此时 gradeRules 数组下 createOrder 资源点的熔断规则已被 Nacos推送并立即生效。

![Drawing 6.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406062349244.png)

咱们来验证下，因为规则允许最大时长为 100 毫秒，而在 createOrder 方法中模拟业务处理需要 101 毫秒，显然会触发熔断。

```java
@SentinelResource("createOrder")
//模拟创建订单业务
public void createOrder(){
    try {
        //模拟处理业务逻辑需要101毫秒
        Thread.sleep(101);
    } catch (InterruptedException e) {
        e.printStackTrace();
    }
    System.out.println("订单已创建");
}
```

连续访问 http://localhost/test_degrade_rule，当第二次访问时便会出现 500 错误。

![Drawing 7.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406062350691.png)

在触发流控或熔断后默认的错误提示不是很友好。

**开发友好的异常处理程序**

第一，针对 RESTful 接口的异常处理。

默认情况下如果访问触发了流控规则，则会直接响应异常信息“BlockedbySentinel (flow limiting)”。

![Drawing 8.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202406062352314.png)

针对 RESTful 接口的统一异常处理需要实现 BlockExceptionHandler，我们先给出完整代码。

```java
@Component //Spring IOC实例化并管理该对象
public class UrlBlockHandler implements BlockExceptionHandler {
    /**
     * RESTFul异常信息处理器
     * @param httpServletRequest
     * @param httpServletResponse
     * @param e
     * @throws Exception
     */
    @Override
    public void handle(HttpServletRequest httpServletRequest, HttpServletResponse httpServletResponse, BlockException e) throws Exception {
        String msg = null;
        if(e instanceof FlowException){//限流异常
            msg = "接口已被限流";
        }else if(e instanceof DegradeException){//熔断异常
            msg = "接口已被熔断,请稍后再试";
        }else if(e instanceof ParamFlowException){ //热点参数限流
            msg = "热点参数限流"; 
        }else if(e instanceof SystemBlockException){ //系统规则异常
            msg = "系统规则(负载/....不满足要求)";
        }else if(e instanceof AuthorityException){ //授权规则异常
            msg = "授权规则不通过"; 
        }
        httpServletResponse.setStatus(500);
        httpServletResponse.setCharacterEncoding("UTF-8");
        httpServletResponse.setContentType("application/json;charset=utf-8");
        //ObjectMapper是内置Jackson的序列化工具类,这用于将对象转为JSON字符串
        ObjectMapper mapper = new ObjectMapper();
        //某个对象属性为null时不进行序列化输出
        mapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
        mapper.writeValue(httpServletResponse.getWriter(),
                new ResponseObject(e.getClass().getSimpleName(), msg)
        );
    }
}
```

当 RESTful触发流控规则后，前端响应如下：

```json
{
    code: "FlowException",
    message: "接口已被限流"
}
```

当触发熔断规则后，前端响应如下：

```json
{
    code: "DegradeException",
    message: "接口已被熔断,请稍后再试"
}
```

通过这种统一而通用的异常处理机制，对RESTful 屏蔽了sentinel-core默认的错误文本，让项目采用统一的 JSON 规范进行输出。

第二，自定义资源点的异常处理。

自定义资源点的异常处理与 RESTful 接口处理略有不同，我们需要在 @SentinelResource 注解上额外附加 blockHandler属性进行异常处理，这里先给出完整代码。

```java
/**
 * 演示用的业务逻辑类
 */
@Service
public class SampleService {
    @SentinelResource(value = "createOrder",blockHandler = "createOrderBlockHandler")
    /**
     * 模拟创建订单业务
     * 抛出 IllegalStateException 异常用于模拟业务逻辑执行失败的情况
     */
    public void createOrder() throws IllegalStateException{
        try {
            //模拟处理业务逻辑需要 101 毫秒
            Thread.sleep(101);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println("订单已创建");
    }
    public void createOrderBlockHandler(BlockException e) throws IllegalStateException{
        String msg = null;
        if(e instanceof FlowException){//限流异常
            msg = "资源已被限流";
        }else if(e instanceof DegradeException){//熔断异常
            msg = "资源已被熔断,请稍后再试";
        }else if(e instanceof ParamFlowException){ //热点参数限流
            msg = "热点参数限流";
        }else if(e instanceof SystemBlockException){ //系统规则异常
            msg = "系统规则(负载/....不满足要求)";
        }else if(e instanceof AuthorityException){ //授权规则异常
            msg = "授权规则不通过";
        }
        throw new IllegalStateException(msg);
    }
}
```

createOrderBlockHandler 方法的书写有两个要求：

- 方法返回值、访问修饰符、抛出异常要与原始的 createOrder 方法完全相同。
- createOrderBlockHandler 方法名允许自定义，但最后一个参数必须是 BlockException 对象，这是所有规则异常的父类，通过判断 BlockException 我们就知道触发了哪种规则异常。

当程序运行后，咱们看一下结果。访问 http://localhost/test_degrade_rule 当触发流控规则后，响应如下：

```json
{
    code: "IllegalStateException",
    message: "资源已被限流"
}
```

当触发熔断规则后，响应如下：

```json
{
    code: "IllegalStateException",
    message: "资源已被熔断,请稍后再试"
}
```









