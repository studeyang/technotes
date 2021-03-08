# 09 | 同步网关：基于 Zuul 构建 API 网关

**什么是 API 网关？**

在服务调用过程中添加了一个网关层，所有的客户端都通过这个统一的网关接入微服务。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210306171411.png" alt="image-20210306171357483" style="zoom: 50%;" />

这样一些非业务功能性需求就可以在网关层进行集中处理。包括请求监控、安全管理、路由规则、日志记录、访问控制、服务适配等功能：

**如何使用 Zuul 构建 API 网关？**

引入 spring-cloud-starter-netflix-zuul 依赖，如下所示：

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-netflix-zuul</artifactId>
</dependency>
```

创建 Bootstrap 类，代码如下：

```java
@SpringBootApplication
@EnableZuulProxy
public class ZuulServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(ZuulServerApplication.class, args);
    }
}
```

API 网关与注册中心关系密切，注册中心为服务路由提供了服务定义信息，这是能够实现服务路由的基础。我们需要向 application.yml 配置文件中添加对 Eureka 的集成。配置内容如下所示：

```yaml
server:
  port: 5555
	 
eureka:
  instance:
    preferIpAddress: true
  client:
    registerWithEureka: true
    fetchRegistry: true
    serviceUrl:
	    defaultZone: http://localhost:8761/eureka/
```

另一方面，API 网关在其服务的消费者和提供者之间提供了一层反向代理，充当着前置负载均衡器的角色。所以，API 网关的定位决定了 Zuul 需要依赖 Ribbon。

**如何使用 Zuul 实现服务路由？**

对于 API 网关而言，最重要的功能就是服务路由，即通过 Zuul 访问的请求会路由并转发到对应的后端服务中。通过 Zuul 进行服务访问的 URL 通用格式如下所示：

```http
http://zuulservice:5555/service
```

在 Zuul 中，服务路由信息的设置可以使用以下几种常见做法。

1. 基于服务发现映射服务路由

Zuul 可以基于注册中心的服务发现机制实现自动化服务路由功能。这是最常见的、也最推荐的做法。网关不需要做任何事情，因为在 Eureka 中已经保存了各种服务定义信息。

例如，我们在 user-service 的配置文件中通过以下配置项指定了该服务的名称为 userservice：

```yaml
spring:
  application:
    name: userservice
```

这样我们就可以通过http://zuulservice:5555/userservice访问到该服务。

访问 zuul-service 的以下地址：

```http
http://zuulservice:5555/actuator/routes
```

可以看到如下路由映射信息：

```json
{
  "/userservice/**":"userservice"
}
```

"/userservice/**" 代表所有以`/userservice`开头的路径请求都将被自动路由到注册在 Eureka 中的名为 userservice 的某一个服务实例中。

2. 基于动态配置映射服务路由

基于服务发现机制的系统自动映射非常方便，但也有明显的局限性。在日常开发过程中，我们往往对服务映射关系有更多的定制化需求，比方说不使用默认的服务名称来命名目标服务。

可以在 zuul-server 工程下的 application.yml 配置如下：

```yaml
zuul:
  prefix: /springhealth
  routes:
    ignored-services: 'userservice'
    userservice: /user/**
```

现在访问 http://zuulservice:5555/actuator/routes 端点，如下所示：

```json
{
  "/springhealth/user/**":"userservice" 
}
```

3. 基于静态配置映射服务路由

让我们考虑这样一个场景，如果系统中存在一个第三方服务，该服务无法注册到我们的 Eureka 注册中心，且提供了一个 HTTP 接口供 SpringHealth 系统调用。

针对这一场景，我们可以在配置文件中添加如下的静态路由配置，这样访问“/thirdpartyservice/**”时，Zuul 会将该请求转发到外部的第三方服务http://thirdparty.com/thirdpartyservice中。

```yaml
zuul:
  routes:
    thirdpartyservice:
      path: /thirdpartyservice/**
      url: http://thirdparty.com/thirdpartyservice
```

现在的服务路由信息就会变成如下结果：

```json
{
  "/springhealth/thirdpartyservice/**":"http://thirdparty.com/thirdpartyservice",
  "/springhealth/user/**":"userservice"
}
```

**Zuul 整合 Ribbon**

Zuul 能够与 Ribbon 进行整合，这种整合也来自手工设置静态服务路由的方式，具体实现方式如下所示：

```yaml
zuul:
  routes:
    thirdpartyservice:
      path: /thirdpartyservice/**
      serviceId: thirdpartyservice

ribbon:
  eureka:
    enabled: false

thirdpartyservice:
  ribbon:
    listOfServers: http://thirdpartyservice1:8080,http://thirdpartyservice2:8080
```

这里，我们配置了一个 thirdpartyservice 路由信息，通过“/ thirdpartyservice /**”映射到 serviceId 为“thirdpartyservice”的服务中。

然后我们希望通过自定义 Ribbon 的方式来实现客户端负载均衡，这时候就需要关闭 Ribbon 与 Eureka 之间的关联。可以通过“ribbon.eureka.enabled: false”配置项完成这一目标。

在不使用 Eureka 的情况下，我们需要手工指定 Ribbon 的服务列表。“users.ribbon.listOfServers”配置项为我们提供了这方面的支持，如在上面的示例中“http://thirdpartyservice1:8080，http://thirdpartyservice2:8080”就为 Ribbon 提供了两个服务定义作为实现负载均衡的服务列表。

# 10 | 同步网关：剖析 Zuul 网关的工作原理

**ZuulFilter 组件架构**

Zuul 响应 HTTP 请求的过程是一种典型的过滤器结构，内部提供了 ZuulFilter 组件来实现这一机制。作为切入点，我们先从 ZuulFilter 展开讨论。

1. ZuulFilter 的定义与 ZuulRegistry

在 Zuul 中，ZuulFilter 是 Zuul 中的关键组件。IZuulFilter 接口定义如下：

```java
public interface IZuulFilter {
  // 是否需要执行该过滤器
  boolean shouldFilter();
  // 具体需要实现的业务逻辑
  Object run() throws ZuulException;
}
```

IZuulFilter的直接实现类是 ZuulFilter，ZuulFilter 是一个抽象类，额外提供了如下所示的两个抽象方法：

```java
//过滤器类型
//分为 PRE、ROUTING、POST 和 ERROR 四种
abstract public String filterType();
//过滤器执行顺序，数字越小则越先执行
abstract public int filterOrder();
```

既然有了过滤器，系统中就应该存在一个管理过滤器的组件，称为过滤器注册表 FilterRegistry。定义如下：

```java
public class FilterRegistry {

  private static final FilterRegistry INSTANCE = new FilterRegistry();

  public static final FilterRegistry instance() {
    return INSTANCE;
  }

  private final ConcurrentHashMap<String, ZuulFilter> filters = new ConcurrentHashMap<String, ZuulFilter>();
  
  private FilterRegistry() {}
  
}
```

2. ZuulFilter 的加载与 FilterLoader

FilterLoader 负责 ZuulFilter 的加载。它用来在源码变化时编译、载入和校验过滤器。针对这个核心类，我们将从它的变量入手，对它进行分析。

```java
//Filter 文件名与修改时间的映射
private final ConcurrentHashMap<String, Long> filterClassLastModified = new ConcurrentHashMap<>();
//Filter 名称与代码的映射
private final ConcurrentHashMap<String, String> filterClassCode = new ConcurrentHashMap<>();
//Filter 名称与名称的映射，作用是判断该 Filter 是否存在
private final ConcurrentHashMap<String, String> filterCheck = new ConcurrentHashMap<>();
//Filter 类型与 List<ZuulFilter> 的映射
private final ConcurrentHashMap<String, List<ZuulFilter>> hashFiltersByType = new ConcurrentHashMap<>();
//前面提到的 FilterRegistry 单例
private FilterRegistry filterRegistry = FilterRegistry.instance();
//动态代码编译器实例，Zuul 提供的默认实现是 GroovyCompiler
static DynamicCodeCompiler COMPILER;
//ZuulFilter 工厂类
static FilterFactory FILTER_FACTORY = new DefaultFilterFactory();
```

DynamicCodeCompiler 是一种动态代码编译器。DynamicCodeCompiler 接口定义如下：

```java
public interface DynamicCodeCompiler {
  //从代码编译到类
  Class compile(String sCode, String sName) throws Exception;
  //从文件编译到类
  Class compile(File file) throws Exception;
}
```

Zuul 通过文件来存储各种 ZuulFilter 的定义和实现逻辑，然后启动一个守护线程（FilterFileManager）定时轮询这些文件，确保变更之后的文件能够动态加载到 FilterRegistry 中。

3. RequestContext 与上下文

我们可以通过 RequestContext 对象将业务信息放到请求上下文（Context）中，并使其在各个 ZuulFilter 中进行传递。

HTTP 请求的所有参数总是绑定在处理请求的线程中，每个新的请求都是由一个独立的线程进行处理，诸如 Tomcat 之类的服务器会为我们启动了这个线程。

因此，RequestContext 的访问必须设计成线程安全，Zuul 使用了非常常见和实用的 ThreadLocal，如下所示：

```java
protected static final ThreadLocal<? extends RequestContext> threadLocal = 
  new ThreadLocal<RequestContext>() {
        @Override
        protected RequestContext initialValue() {
            try {
                return contextClass.newInstance();
            } catch (Throwable e) {
                throw new RuntimeException(e);
            }
        }
};
```

用于获取 RequestContext 的 getCurrentContext 方法如下所示：

```java
public static RequestContext getCurrentContext() {
  RequestContext context = threadLocal.get();
  return context;
}
```

4. HTTP 请求与过滤器执行

接下去我们分析如何使用加载好的 ZuulFilter。Zuul 提供了 FilterProcessor 类来执行 Filter，FilterProcessor 基于 runFilters 方法衍生出 postRoute()、preRoute()、error() 和 route() 这四个方法，分别对应 Zuul 中的四种过滤器类型。

其中 PRE 过滤器在请求到达目标服务器之前调用，ROUTING 过滤器把请求发送给目标服务，POST 过滤器在请求从目标服务返回之后执行，而 ERROR 过滤器则在发生错误时执行。同时，这四种过滤器有一定的执行顺序，如下所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210307232307.png" alt="image-20210307232307246" style="zoom:50%;" />

在 Spring Cloud 中所有请求都是 HTTP 请求，Zuul 作为一个服务网关同样也需要完成对 HTTP 请求的响应。ZuulServlet 是 Zuul 中对 HttpServlet 接口的一个实现类。

**Spring Cloud 集成 ZuulFilter**

Spring Cloud 的 ZuulFilter 是如何实现加载的呢？

在 ZuulFilterInitializer 中发现了如下所示的 contextInitialized 方法：

```java
@PostConstruct
public void contextInitialized() {
  log.info("Starting filter initializer");
 
  TracerFactory.initialize(tracerFactory);
  CounterFactory.initialize(counterFactory);
 
  for (Map.Entry<String, ZuulFilter> entry : this.filters.entrySet()) {
    filterRegistry.put(entry.getKey(), entry.getValue());
  }
}
```

至此，Spring Cloud 通过 Netflix Zuul 提供的 FilterLoader 和 FilterRegistry 等工具类完成了两者之间的集成。

# 11 | 异步网关：基于 Spring Cloud Gateway 构建 API 网关

**Spring Cloud Gateway 简介**

在性能上，Spring Cloud Gateway 基于最新的 Spring 5 和 Spring Boot 2，以及用于响应式编程的 Project Reactor 框架，提供的是响应式、非阻塞式 I/O 模型。

而 Zuul 的实现原理是对 Servlet 的一层封装，通信模式上采用的是阻塞式 I/O。

所以 Spring Cloud Gateway 性能更高。

功能上，Spring Cloud Gateway 也比 Zuul 更为丰富。除了通用的服务路由机制之外，Spring Cloud Gateway 还支持请求限流等面向服务容错方面的功能，同样也能与 Hystrix 等框架进行良好的集成。

但是，Spring Cloud Gateway 的源码非常复杂，出现问题不容易排查和解决。而 Zuul 的编程模型和底层原理都非常简单，开发调试上也容易把握。

如何使用 Spring Cloud Gateway 呢？

添加依赖：

```xml
<dependency>
  <groupId>org.springframework.cloud</groupId>
  <artifactId>spring-cloud-starter-gateway</artifactId>
</dependency>
```

Bootstrap 类上添加 @EnableDiscoveryClient 注解。

```java
@SpringBootApplication
@EnableDiscoveryClient
public class GatewayApplication {
    public static void main(String[] args) {
        SpringApplication.run(GatewayApplication.class, args);
    }
}
```

**Spring Cloud Gateway 与服务路由**

1. Spring Cloud Gateway 基本架构

Spring Cloud Gateway 中的核心概念有两个，一个是过滤器（Filter），一个是谓词（Predicate）。Spring Cloud Gateway 的整体架构图如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210308233201.png" alt="image-20210308233200967" style="zoom: 67%;" />

Spring Cloud Gateway 中的过滤器和 Zuul 中的过滤器是同一个概念。它们都可以用于在处理 HTTP 请求之前或之后修改请求本身，及对应响应结果。区别在于两者的类型和实现方式不同。

而所谓谓词，本质上是一种判断条件，用于将 HTTP 请求与路由进行匹配。Spring Cloud Gateway 内置了大量的谓词组件，可以分别对 HTTP 请求的消息头、请求路径等常见的路由媒介进行自动匹配以便决定路由结果。

2. 使用 Spring Cloud Gateway 实现路由

一条完整路由配置的基本结构，如下所示。

```yaml
spring:
  cloud:
	  gateway:
	    discovery:
        locator:
          enabled: true
      routes:
      #路由信息编号
      - id: testroute
        #集成负载均衡机制
        uri: lb://testservice
        #匹配以“/test”开头的请求
        predicates:
        - Path=/test/**
        #为路径添加前缀
        filters:
        - PrefixPath=/prefix
```

spring.cloud.gateway.discovery.locator.enabled 表示设置 Spring Cloud Gateway 对 HTTP 请求的路由行为。

SpringHealth 案例系统，Spring Cloud Gateway 网关服务中完整版的配置信息如下所示：

```yaml
server:
  port: 5555

eureka:
  instance:
    preferIpAddress: true
  client:
    registerWithEureka: true
    fetchRegistry: true
    serviceUrl:
        defaultZone: http://localhost:8761/eureka/

spring:
  cloud:
    gateway:
      discovery:
        locator:
          enabled: true
      routes:
      - id: userroute
        uri: lb://userservice
        predicates:
        - Path=/user/**
        filters:
        - RewritePath=/user/(?<path>.*), /$\{path}
      - id: deviceroute
        uri: lb://deviceservice
        predicates:
        - Path=/device/**
        filters:
        - RewritePath=/device/(?<path>.*), /$\{path}
      - id: interventionroute
        uri: lb://interventionservice
        predicates:
        - Path=/intervention/**
        filters:
        - RewritePath=/intervention/(?<path>.*), /$\{path}
```

以上配置添加了一个对请求路径进行重写（Rewrite）的过滤器。分别在路径上添加了“/user”“/device”和“/intervention”前缀。这种重写过滤器的效果实际上和前面介绍的前缀过滤器有相同的效果。

与 Zuul 一样，Spring Cloud Gateway 的扩展性也主要体现在过滤器组件中。

**剖析 Spring Cloud Gateway 中的过滤器**

针对过滤器，Spring Cloud Gateway 提供了一个全局过滤器（GlobalFilter）的概念。

我们首先想到了可以使用全局过滤器来对所有 HTTP 请求进行拦截，具体做法是实现 GlobalFilter 接口，示例代码如下所示。

```java
@Configuration
public class JWTAuthFilter implements GlobalFilter {
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest.Builder builder = exchange.getRequest().mutate();
        builder.header("Authorization","JWTToken");
        
        return chain.filter(exchange.mutate().request(builder.build()).build());
    }
}
```

在这个示例中，我们给所有经过 API 网关的 HTTP 请求添加了一个消息头，用来设置与 JWT Token 相关的安全认证信息。

Spring Cloud Gateway 也提供了可用于 pre 和 post 两种阶段的过滤器。以下代码展示了一个 PostGatewayFilter 的实现方式。

首先继承一个 AbstractGatewayFilterFactory 类，然后可以通过覆写 apply 方法来提供针对 ServerHttpResponse 对象的任何操作：

```java
public class PostGatewayFilterFactory extends AbstractGatewayFilterFactory {
    @Override
    public GatewayFilter apply(Config config) {
        return (exchange, chain) -> {
          return chain.filter(exchange).then(Mono.fromRunnable(() -> {
              ServerHttpResponse response = exchange.getResponse();
              //针对Response的各种处理
            }));
          };
    }
}
```

PreGatewayFilter 的实现方式也类似，只不过处理的目标一般是 ServerHttpRequest 对象。

