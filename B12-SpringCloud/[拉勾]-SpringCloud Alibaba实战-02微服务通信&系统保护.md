> 来源：拉勾教育《Spring Cloud Alibaba实战》

# 06 | 负载均衡：Ribbon 如何保证微服务的高可用

> 内容合并至《[拉勾]-SpringCloud原理与实战-02服务治理&API网关》07 | 负载均衡：如何使用 Ribbon 实现客户端负载均衡？

# 07 | REST消息通信：如何使用 OpenFeign 简化服务间通信

**Feign 与 OpenFeign**

Netflix Feign 采用“接口+注解”的方式开发，通过模仿 RPC 的客户端与服务器模式（CS），采用接口方式开发来屏蔽网络通信的细节。

OpenFeign 则是在 Netflix Feign 的基础上进行封装，结合原有 Spring MVC 的注解，对 Spring Cloud 微服务通信提供了良好的支持。

**OpenFeign 的使用办法**

假设某电商平台日常订单业务中，为保证每一笔订单不会超卖，在创建订单前订单服务（order-service）首先去仓储服务（warehouse-service）检查对应商品 skuId（品类编号）的库存数量是否足够，库存充足创建订单，不足 App 前端提示“库存不足”。

![image-20210808220417309](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210808220423.png)

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

![image-20210808223857154](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210808223857.png)

那 RESTful 与 RPC 孰优孰劣呢？我们通过一个表格进行说明：

![image-20210808223948543](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210808223948.png)

在微服务架构场景下，因为大多数服务都是轻量级的，同时 90%的任务通过短连接就能实现，因此更推荐使用 RESTful 通信。

**Apache Dubbo**

![image-20210808223135525](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210808223135.png)

Dubbo 架构中，包含 5 种角色。

- Provider：RPC 服务提供者。
- Container：容器，用于启动、停止 Provider 服务。
- Consumer：消费者，调用的发起者。
- Registry：注册中心，与微服务注册中心职责类似。
- Monitor：监控器，监控器提供了 Dubbo 的监控职责。在 Dubbo 产生通信时，Monitor 进行收集、统计，并通过可视化 UI 界面帮助运维人员了解系统进程间的通信状况。

**Dubbo与 Nacos 协同作业：开发 Provider 仓储服务**

还是以“订单与库存服务”案例为例。

![image-20210808223251858](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210808223251.png)

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

![image-20210808225440206](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210808225440.png)

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

![image-20210808225924093](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210808225924.png)

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

![image-20210808230506545](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210808230506.png)

第五步，启动微服务，验证 Nacos 注册信息。

![image-20210808230529484](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210808230529.png)

此时 Consumer 已在服务列表中出现，说明消费者已注册成功。







