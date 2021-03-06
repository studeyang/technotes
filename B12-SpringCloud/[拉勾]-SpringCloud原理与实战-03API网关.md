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



