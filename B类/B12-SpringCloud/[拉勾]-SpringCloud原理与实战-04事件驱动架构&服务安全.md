# 事件驱动架构

# 20 | 消息驱动：Spring 中对消息处理机制的抽象过程

Spring Cloud 专门提供了一个 Spring Cloud Stream 框架来实现事件驱动架构，并完成与主流消息中间件的集成。

**事件驱动架构**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210316151433.png" alt="image-20210316151433557" style="zoom: 33%;" />

在上图中，事件生产者和消费者之间的虚线代表的是一种相互松散、没有直接调用的关联关系。满足以上特性的系统代表着一种松耦合的架构，通常被称为事件驱动架构，而这里的事件也可以被理解是服务与服务之间发送的一种消息。

事件驱动架构本质上是一种架构设计风格，实现方法和工具有很多。在 Spring Cloud 家族中这个工具就是 Spring Cloud Stream。

**Spring 家族中的消息处理机制**

在 Spring 家族中，与消息处理机制相关的框架有三个。Spring Cloud Stream 是基于 Spring Integration 实现了消息发布和消费机制并提供了一层封装，而在 Spring Integration 的背后，则依赖于 Spring Messaging 组件来实现消息处理机制的基础设施。

这三个框架之间的依赖关系如下图所示：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210316152133.png" alt="image-20210316152132946" style="zoom: 33%;" />

接下来的内容，我们先来对位于底层的 Spring Messaging 和 Spring Integration 框架做一些展开。

1. Spring Messaging

Spring Messaging 是 Spring 框架中的一个底层模块，用于提供统一的消息编程模型。例如，消息这个数据单元在 Spring Messaging 中统一定义为如下所示的 Message 接口：

```java
public interface Message<T> {
    T getPayload();
    MessageHeaders getHeaders();
}
```

消息通道 MessageChannel 的定义也比较简单：

```java
public interface MessageChannel {
    long INDEFINITE_TIMEOUT = -1;
    default boolean send(Message<?> message) {
        return send(message, INDEFINITE_TIMEOUT);
    }
    boolean send(Message<?> message, long timeout);
}
```

通道的名称对应的就是队列的名称，但是作为一种抽象和封装，各个消息传递系统所特有的队列概念并不会直接暴露在业务代码中，而是通过通道来对队列进行配置。

Spring Messaging 在基础消息模型之上还提供了很多方便在业务系统中使用消息传递机制的辅助功能，例如各种消息体内容转换器 MessageConverter 以及消息通道拦截器 ChannelInterceptor 等。

2. Spring Integration

Spring Integration 是对 Spring Messaging 的扩展，提供了对系统集成领域的经典著作《企业集成模式：设计构建及部署消息传递解决方案》中所描述的各种企业集成模式的支持，通常被认为是一种企业服务总线 ESB 框架。

Spring Integration 的设计目的是系统集成，因此内部提供了大量的集成化端点方便应用程序直接使用。当各个异构系统之间进行集成时，如何屏蔽各种技术体系所带来的差异性，Spring Integration 为我们提供了解决方案。通过通道之间的消息传递，在消息的入口和出口我们可以使用通道适配器和消息网关这两种典型的端点对消息进行同构化处理。

# 21 | 消息架构：Spring Cloud Stream 的基本架构

**Spring Cloud Stream 基本架构**

Spring Cloud Stream 在消息生产者和消费者之间添加了一种桥梁机制，所有的消息都将通过 Spring Cloud Stream 进行发送和接收，如下图所示：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210316215557.png" alt="image-20210316215557193" style="zoom:50%;" />

Spring Cloud Stream 具备四个核心组件，分别是 Binder、Channel、Source 和 Sink，其中 Binder 和 Channel 成对出现，而 Source 和 Sink 分别面向消息的发布者和消费者。

- Source 和 Sink

Source 组件是真正生成消息的组件，相当于是一个输出（Output）组件。而 Sink 则是真正消费消息的组件，相当于是一个输入（Input）组件。

Source 组件使用一个普通的 POJO 对象来充当需要发布的消息，通过将该对象进行序列化（默认的序列化方式是 JSON）然后发布到 Channel 中。另一方面，Sink 组件监听 Channel 并等待消息的到来，一旦有可用消息，Sink 将该消息反序列化为一个 POJO 对象并用于处理业务逻辑。

- Channel

在消息传递系统中，队列的作用就是实现存储转发的媒介，消息生产者所生成的消息都将保存在队列中并由消息消费者进行消费。通道的名称对应的往往就是队列的名称。

- Binder

Spring Cloud Stream 中最重要的概念就是 Binder。所谓 Binder，顾名思义就是一种黏合剂，将业务服务与消息传递系统黏合在一起。通过 Binder，我们可以很方便地连接消息中间件，可以动态的改变消息的目标地址、发送方式而不需要了解其背后的各种消息中间件在实现上的差异。

**Spring Cloud Stream 集成 Spring 消息处理机制**

在如下所示的代码中，我们定义了 SpringHealthChannel 接口并声明了一个 Input 通道和两个 Output 通道，说明使用该通道的服务会从外部的一个通道中获取消息并向外部的两个通道发送消息：

```java
public interface SpringHealthChannel {
    @Input
    SubscribableChannel input1();

    @Output
    MessageChannel output1();
  
    @Output
    MessageChannel output2();
}
```

上述接口定义中同时使用到了 Spring Messaging 中的 SubscribableChannel 和 MessageChannel。Spring Cloud Stream 对 Spring Messaging 和 Spring Integration 提供了原生支持。

**Spring Cloud Stream 集成消息中间件**

在接下来的内容中，我们将梳理 Spring Cloud Stream 中的消息传递模型，并给出 Binder 与消息中间件如何进行整合的过程。

1. Spring Cloud Stream 中的消息传递模型

- 发布-订阅模型

在 Spring Cloud Stream 中，统一通过发布-订阅模型完成消息的发布和消费，如下所示：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210316221701.png" alt="image-20210316221701734" style="zoom:50%;" />

- 消费者组

一条消息就只能被同一个组中的某一个服务实例所消费。消费者的基本结构如下图所示（其中虚线表示不会发生的消费场景）：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210316221822.png" alt="image-20210316221822025" style="zoom:50%;" />

- 消息分区

同一分区中的消息能够确保始终是由同一个消费者实例进行消费。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210316222006.png" alt="image-20210316222006133" style="zoom: 33%;" />

# 22 | 消息发布：如何使用 Spring Cloud Stream 实现消息发布者和消费者？（上）

**设计 SpringHealth 中的消息发布场景**

类似 SpringHealth 这样的系统中的用户信息变动并不会太频繁，所以很多时候我们会想到通过缓存系统来存放用户信息。而一旦用户信息发生变化，user-service 可以发送一个事件，给到相关的订阅者并更新缓存信息，如下图所示：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210316224022.png" alt="image-20210316224022503" style="zoom:50%;" />

接下来我们关注于上图中的事件发布者 user-service。在 user-service 中需要设计并实现使用 Spring Cloud Stream 发布消息的各个组件，包括 Source、Channel 和 Binder。我们围绕 UserInfoChangedEvent 事件给出 user-service 内部的整个实现流程，如下图所示：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210316224120.png" alt="image-20210316224120602" style="zoom:50%;" />

**实现消息发布者**

1. 使用 @EnableBinding 注解

引入依赖：

```xml
<dependency>
  <groupId>org.springframework.cloud</groupId>
  <artifactId>spring-cloud-stream</artifactId>
</dependency>

<dependency>
  <groupId>org.springframework.cloud</groupId>
  <artifactId>spring-cloud-starter-stream-kafka</artifactId>
</dependency>
```

启动类：

```java
@SpringCloudApplication
@EnableBinding(Source.class)
public class UserApplication {
    public static void main(String[] args) {
        SpringApplication.run(UserApplication.class, args);
    }
}
```

2. 定义 Event

```java
public class UserInfoChangedEvent{
    //事件类型
    private String type;
    //事件所对应的操作
    private String operation;
    //事件对应的领域模型
    private User user;
}
```

3. 创建 Source

```java
@Component
public class UserInfoChangedSource {
    private Source source;
 
    private static final Logger logger = LoggerFactory.getLogger(UserInfoChangedSource.class);
  
    @Autowired
    public UserInfoChangedSource(Source source) {
        this.source = source;
    }
 
    private void publishUserInfoChangedEvent(UserInfoOperation operation, User user) {
      
        logger.debug("Sending message for UserId: {}", user.getId());
     
        UserInfoChangedEvent change =  new UserInfoChangedEvent(
            UserInfoChangedEvent.class.getTypeName(),
            operation.toString(),
            user);
 
        source.output().send(MessageBuilder.withPayload(change).build());
    }

    public void publishUserInfoUpdatedEvent(User user) {
         publishUserInfoChangedEvent(UserInfoOperation.UPDATE, user);
    }

}
```

4. 配置 Binder

```yaml
spring:
  cloud:
    stream:
      bindings:
        output:
          destination: userInfoChangedTopic
          content-type: application/json
      kafka:
        binder:
          zk-nodes: localhost
        brokers: localhost
```

5. 集成服务

```java
@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
 
    @Autowired
    private UserInfoChangedSource userInfoChangedSource;
 
    public void updateUser(User user){
        userRepository.save(user);
        userInfoChangedSource.publishUserInfoUpdatedEvent(user);
    }
 
}
```

**设计 SpringHealth 中的消息消费场景**

负责消费消息的是 Sink 组件，因此，我们同样围绕 UserInfoChangedEvent 事件给出 intervention-service 内部的整个实现流程，如下图所示：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210316225158.png" alt="image-20210316225158301" style="zoom:50%;" />

Spring Cloud Stream 通过 Sink 获取消息并交由 UserInfoChangedSink 实现具体的消费逻辑。

![image-20210316225547206](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210316225547.png)

# 23 | 消息消费：如何使用 Spring Cloud Stream 实现消息发布者和消费者？（下）

今天我们将延续上一课时的内容，来具体讲解如何在服务中添加消息消费者，以及使用各项消息消费的高级主题。

**在服务中添加消息消费者**

1. 使用 @EnableBinding 注解

引入 spring-cloud-stream、spring-cloud-starter-stream-kafka 依赖后，构建 Bootstrap 类：

```java
@SpringCloudApplication
@EnableBinding(Sink.class)
public class InterventionApplication{
    public static void main(String[] args) {
        SpringApplication.run(InterventionApplication.class, args);
    }
}
```

2. 创建 Sink

UserInfoChangedSink 负责处理具体的消息消费逻辑，代码如下所示：

```java
public class UserInfoChangedSink {
 
    @Autowired
    private UserInfoRedisRepository userInfoRedisRepository;
 
    private static final Logger logger = LoggerFactory.getLogger(UserInfoChangedSink.class);
 
    @StreamListener("input")
    public void handleChangedUserInfo(UserInfoChangedEventMapper userInfoChangedEventMapper) {
     
        logger.debug("Received a message of type " + userInfoChangedEventMapper.getType()); 
        logger.debug("Received a {} event from the user-service for user name {}",
                     userInfoChangedEventMapper.getOperation(), 
                     userInfoChangedEventMapper.getUser().getUserName());
        
        if(userInfoChangedEventMapper.getOperation().equals("ADD")) {
            userInfoRedisRepository.saveUser(userInfoChangedEventMapper.getUser());
        } else if(userInfoChangedEventMapper.getOperation().equals("UPDATE")) {
            userInfoRedisRepository.updateUser(userInfoChangedEventMapper.getUser());            
        } else if(userInfoChangedEventMapper.getOperation().equals("DELETE")) {
            userInfoRedisRepository.deleteUser(userInfoChangedEventMapper.getUser().getUserName());
        } else {            
            logger.error("Received an UNKNOWN event from the user-service of type {}",
                         userInfoChangedEventMapper.getType());
        }
    }
}
```

3. 配置 Binder

```yaml
spring:
  cloud:
    stream:
      bindings:
        input:
          destination:  userInfoChangedTopic
          content-type: application/json
      kafka:
        binder:
          zk-nodes: localhost
	      brokers: localhost
```

**Spring Cloud Stream 高级主题**

1. 自定义消息通道

```java
public interface UserInfoChangedChannel{ 
    String USER_INFO = "userInfoChangedChannel";
    
    @Input(UserInfoChangedChannel.USER_INFO)
    SubscribableChannel userInfoChangedChannel();
}
```

一旦我们完成了自定义的消息通信，就可以在 @StreamListener 注解中设置这个通道。

```java
@EnableBinding(UserInfoChangedChannel.class)
public class UserInfoChangedSink {
    @StreamListener(UserInfoChangedChannel.USER_INFO)
    public void handleChangedUserInfo(UserInfoChangedEventMapper userInfoChangedEventMapper) {
	      …
    }
}
```

对于 Binder 的配置而言，我们要做的也只是调整通道的名称。

```yaml
spring:
  cloud:
    stream:
      bindings:
        userInfoChangedChannel:
          destination:  userInfoChangedTopic
          content-type: application/json
      kafka:
        binder:
          zk-nodes: localhost
	      brokers: localhost
```

2. 使用消费者分组

在集群环境下，我们希望服务的不同实例被放置在竞争的消费者关系中，同一服务集群中只有一个实例能够处理给定消息。Spring Cloud Stream 提供的消费者分组可以很方便地实现这一需求，效果图如下所示：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210317231101.png" alt="image-20210317231101428" style="zoom: 50%;" />

要想实现上图所示的消息消费效果，在配置Binder时指定消费者分组信息即可，如下所示：

```yaml
spring:
  cloud:
    stream:
      bindings:
        userInfoChangedChannel:
          destination:  userInfoChangedTopic
          content-type: application/json
        group: interventionGroup
      kafka:
        binder:
          zk-nodes: localhost
	      brokers: localhost
```

3. 使用消息分区

我们希望用户信息中 id 为单号的 UserInfoChangedEvent 始终由第一个 intervention-service 实例进行消费，而id为双号的 UserInfoChangedEvent 则始终由第二个 intervention-service 实例进行消费。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210317231440.png" alt="image-20210317231440858" style="zoom:50%;" />

Binder 配置如下。

```yaml
spring:
  cloud:
    stream:
      bindings:
        default:
          content-type: application/json
          binder: rabbitmq
        output:
            destination: userInfoChangedExchange
          group: interventionGroup
          producer:
            partitionKeyExpression: payload.user.id % 2
            partitionCount: 2
```

****

# 服务安全

# 25 | 微服务访问安全需求和实现方案

**微服务架构中的安全性设计**

对于微服务架构而言，安全性设计的最核心考虑点是认证（Authentication）和授权（Authorization）。

1. 认证与授权

所谓认证，解决的是“你是谁”这一个问题。一旦明确 “你是谁”之后，下一步就可以判断“你能做什么”，这个步骤就是授权。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210317232529.png" alt="image-20210317232529450" style="zoom:50%;" />

上图代表的是一种通用方案。微服务架构中的认证和授权模型与上图中的类似，但在具体设计和实现过程中也有其特殊性。

2. 微服务架构中的认证与授权

微服务架构中存在一个授权中心，授权中心首先会获取客户端请求中所带有的身份凭证信息，然后基于这个身份凭证信息生成一个 Token。客户端获取 Token 之后就可以基于这个 Token 发起对微服务的访问。这时候，我们需要对这个 Token 进行认证，并通过授权中心获取该请求所能访问的特定资源。

针对授权，业界最具代表性的就是 OAuth2 协议。而针对授权，采用JWT是目前非常主流的做法。

**授权：OAuth2 协议**

OAuth 2.0 定义了四种授权方式，即密码模式、授权码模式、简化模式和客户端模式。

**认证：JWT 机制**

JWT 是一种表示数据的标准，在安全领域，我们通常用它来传递被认证的用户身份信息，以便从资源服务器获取资源。

# 26 | 服务授权：Spring Cloud Security 集成 OAuth2 协议

**构建 OAuth2 授权服务器**

我们将在整个系统中创建一个新的代码工程并取名为 auth-server，同时引入与 OAuth2 协议相关的依赖，如下所示：

```xml
<dependency>
  <groupId>org.springframework.cloud</groupId>
  <artifactId>spring-cloud-security</artifactId>
</dependency>
 
<dependency>
  <groupId>org.springframework.security.oauth</groupId>
  <artifactId>spring-security-oauth2</artifactId>
</dependency>
```

构建 Bootstrap 类：

```java
@SpringCloudApplication
@RestController
@EnableResourceServer
@EnableAuthorizationServer
public class AuthApplication {
    public static void main(String[] args) {
        SpringApplication.run(AuthApplication.class, args);
    }
}
```

@EnableAuthorizationServer 注解的作用在于为微服务运行环境提供一个基于 OAuth2 协议的授权服务，该授权服务会暴露一系列基于 RESTful 风格的端点（例如 /oauth/authorize 和 /oauth/token）供 OAuth2 授权流程进行使用。

**基于密码模式生成 Token**

在密码模式下，用户向客户端提供用户名和密码，并将用户名和密码发给授权服务器从而请求 Token。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210318215633.png" alt="image-20210318215633452" style="zoom:50%;" />

**设置客户端信息**

用于描述客户端详情的 ClientDetails 接口如下：

```java
public interface ClientDetails extends Serializable {
    //客户端唯一性 Id
    String getClientId();
    Set<String> getResourceIds();
    boolean isSecretRequired();
    //客户端安全码
    String getClientSecret();
    boolean isScoped();
    //客户端的访问范围
    Set<String> getScope();
    //客户端可以使用的授权模式
    Set<String> getAuthorizedGrantTypes();
    …
}
```

Spring Security 提供了 **[1]AuthorizationServerConfigurerAdapter** 类来简化客户端信息配置，我们可以通过继承该类并覆写其中的 configure() 方法来进行配置。

```java
@Configuration
public class SpringHealthAuthorizationServerConfigurer extends AuthorizationServerConfigurerAdapter {
 
    @Autowired
    private AuthenticationManager authenticationManager;
 
    @Autowired
    private UserDetailsService userDetailsService;
 
    @Override
    public void configure(AuthorizationServerEndpointsConfigurer endpoints) throws Exception {
        endpoints.authenticationManager(authenticationManager).userDetailsService(userDetailsService);
    }
 
    @Override
    public void configure(ClientDetailsServiceConfigurer clients) throws Exception {
      
        clients.inMemory().withClient("springhealth").secret("{noop}springhealth_secret")
                .authorizedGrantTypes("refresh_token", "password", "client_credentials")
                .scopes("webclient", "mobileclient");
    }
}
```

> Spring Security5 中统一使用 PasswordEncoder 来对密码进行编码，在设置密码时要求格式为“{id}password”。而这里的前缀“{noop}”就是代表具体 PasswordEncoder 的 id，表示我们使用的是 NoOpPasswordEncoder。

在前面的内容中提到，@EnableAuthorizationServer 注解会暴露一系列的端点，而授权是使用 AuthorizationEndpoint 这个端点来进行控制的。要想对该端点的行为进行配置，可以使用 **[2]AuthorizationServerEndpointsConfigurer** 这个配置类。和ClientDetailsServiceConfigurer 配置类一样，我们也通过继承 AuthorizationServerConfigurerAdapter 并且覆写其中的 configure() 方法来进行配置。

```java
@Autowired
private AuthenticationManager authenticationManager;
 
@Autowired
private UserDetailsService userDetailsService;
	 
@Override
public void configure(AuthorizationServerEndpointsConfigurer endpoints) throws Exception {
 
    endpoints.authenticationManager(authenticationManager)
      .userDetailsService(userDetailsService);
}
```

至此，客户端设置工作全部完成，我们所做的事情就是实现了一个自定义的 SpringHealthAuthorizationServerConfigurer 配置类。

> 配置了客户端信息、配置了授权端点。

**设置用户认证信息**

设置用户认证信息所依赖的配置类是 WebSecurityConfigurer 类， Spring Security 同样提供了 **[3]WebSecurityConfigurerAdapter** 类来简化该配置类的使用方式，我们可以继承 WebSecurityConfigurerAdapter 类并且覆写其中的 configure() 的方法来完成配置工作。

设置用户信息非常简单，只需要指定用户名（User）、密码（Password）和角色（Role）这三项数据即可。这部分工作就是通过前文中提到的认证管理器 AuthenticationManager 来完成的，该接口非常简单，只包含一个用于认证的 authenticate 方法，如下所示：

```java
public interface AuthenticationManager {

    Authentication authenticate(Authentication authentication)
            throws AuthenticationException;
}
```

在 Spring Security 中，我们可以使用 AuthenticationManagerBuilder 类轻松实现基于内存、LADP 和 JDBC 的认证机制。

```java
@Configuration
public class SpringHealthWebSecurityConfigurer extends WebSecurityConfigurerAdapter {
 
    @Override
    @Bean
    public AuthenticationManager authenticationManagerBean() throws Exception {
        return super.authenticationManagerBean();
    }
 
    @Override
    @Bean
    public UserDetailsService userDetailsServiceBean() throws Exception {
        return super.userDetailsServiceBean();
    }
 
    @Override
    protected void configure(AuthenticationManagerBuilder builder) throws Exception {
        builder.inMemoryAuthentication()
          .withUser("springhealth_user").password("{noop}password1").roles("USER")
          .and()
          .withUser("springhealth_admin").password("{noop}password2").roles("USER", "ADMIN");
    }
}
```

**生成 Token**

授权服务器中会暴露一批端点供HTTP请求进行访问。获取 Token 的端点就是http://localhost:8080/oauth/token，在使用该端点时，我们需要提供前面所配置的客户端信息和用户信息。

![image-20210318223410970](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/20210318223617.png)

接下来我们指定针对授权模式的专用配置信息：

![image-20210318223617642](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/20210318223617.png)

会得到如下所示的返回结果：

```json
{
    "access_token": "868adf52-f524-4be8-a9e7-24c1c41aa7d6",
    "token_type": "bearer",
    "refresh_token": "96de5815-7935-4ca7-a24e-0d7441345696",
    "expires_in": 43199,
    "scope": "webclient"
}
```

# 27 | 服务授权：使用 OAuth2 协议对服务访问进行授权？

**在微服务中集成 OAuth2 授权机制**

定义受保护资源：

```java
@SpringCloudApplication
@EnableResourceServer
public class UserApplication {
    public static void main(String[] args) {
        SpringApplication.run(UserApplication.class, args);
    }
}
```

一旦我们在 user-service 中添加了 @EnableResourceServer 注解之后，user-service 会对所有的 HTTP 请求进行验证以确定 Header 部分中是否包含 Token 信息，如果没有 Token 信息，则会直接限制访问。如果有 Token 信息，就会通过访问 OAuth2 服务器并进行 Token 的验证。

那么 user-service 是如何与 OAuth2 服务器进行通信并获取所传入 Token 的验证结果呢？

要想回答这个问题，我们要明确将 Token 传递给 OAuth2 授权服务器的目的就是获取该 Token 中包含的用户和授权信息。这样，势必需要在 user-service 和 OAuth2 授权服务器之间建立起一种交互关系，我们可以在 user-service 中添加如下所示的 security.oauth2.resource.userInfoUri 配置项来实现这一目标：

```yaml
security:
  oauth2:
    resource:
	    userInfoUri: http://localhost:8080/userinfo
```

这里的http://localhost:8080/userinfo 指向 OAuth2服务中的一个端点，我们需要进行构建。相关代码如下所示：

```java
@RequestMapping(value = "/userinfo", produces = "application/json")
public Map<String, Object> user(OAuth2Authentication user) {
    Map<String, Object> userInfo = new HashMap<>();
    userInfo.put("user", user.getUserAuthentication().getPrincipal());
    userInfo.put("authorities", AuthorityUtils.authorityListToSet(
      user.getUserAuthentication().getAuthorities()
    ));
    return userInfo;
}
```

这个端点的作用就是为了获取可访问那些受保护服务的用户信息。这里用到了 OAuth2Authentication 类，该类保存着用户的身份（Principal）和权限（Authority）信息。

**在微服务中嵌入访问授权控制**

在 Spring Cloud Security 中对访问的不同控制层级进行了抽象，形成了用户、角色和请求方法这三种粒度。这三种层级所能访问的资源范围逐一递减。

所谓的用户层级是指只要是认证用户就可能访问服务内的各种资源。而用户+角色层级在用户层级的基础上，还要求用户属于某一个或多个特定角色。最后的用户+角色+请求方法层级要求最高，能够对某些HTTP操作进行访问限制。接下来我们分别对这三种层级展开讨论。

1. 用户层级的权限访问控制

```java
@Configuration
public class SpringHealthResourceServerConfiguration extends ResourceServerConfigurerAdapter {
    @Override
    public void configure(HttpSecurity httpSecurity) throws Exception {
        httpSecurity.authorizeRequests()
             .anyRequest()
             .authenticated();
    }
}
```

当我们使用普通的 HTTP 请求来访问 user-service 中的任何 URL 时，将会得到一个“unauthorized”的 401 错误信息。

2. 用户+角色层级的权限访问控制

```java
@Configuration
public class SpringHealthResourceServerConfiguration extends ResourceServerConfigurerAdapter {
 
    @Override
	  public void configure(HttpSecurity httpSecurity) throws Exception {
        httpSecurity.authorizeRequests()
                .antMatchers("/interventions/**")
                .hasRole("ADMIN")
                .anyRequest()
                .authenticated();
    }
}
```

现在，如果我们使用角色为“User”的 Token 访问 invervention-service，就会得到一个“access_denied”的错误信息。

3. 用户+角色+操作层级的权限访问控制

```java
@Configuration
public class SpringHealthResourceServerConfiguration extends ResourceServerConfigurerAdapter {
    @Override
    public void configure(HttpSecurity httpSecurity) throws Exception{
        httpSecurity.authorizeRequests()
                .antMatchers(HttpMethod.PUT, "/devices/**")
                .hasRole("ADMIN")
                .anyRequest()
                .authenticated();
    }
}
```

我们使用普通“USER”角色生成的 Token，并调用 device-service 中"/devices/"端点中的 Update 操作，同样会得到“access_denied”错误信息。

**在微服务中传播 Token**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210320231755.png" alt="image-20210320231755420" style="zoom:50%;" />

持有 Token 的客户端访问 intervention-service 提供的 HTTP 端点进行下单操作，该服务会验证所传入 Token 的有效性。intervention-service 会再通过网关访问 user-service 和 device-service，这两个服务同样分别对所传入 Token 进行验证并返回相应的结果。

如何实现上图中的 Token 传播效果？Spring Security 基于 RestTemplate 进行了封装，专门提供了一个用于在 HTTP 请求中传播 Token 的 OAuth2RestTemplate 工具类。想要在业务代码中构建一个 OAuth2RestTemplate 对象，可以使用如下所示的示例代码：

```java
@Bean
public OAuth2RestTemplate oauth2RestTemplate(
  OAuth2ClientContext oauth2ClientContext, 
  OAuth2ProtectedResourceDetails details) {
        return new OAuth2RestTemplate(details, oauth2ClientContext);
}
```

OAuth2RestTemplate 会把从 HTTP 请求头中获取的 Token 保存到一个 OAuth2ClientContext 上下文对象中，而 OAuth2ClientContext 会把每个用户的请求信息控制在会话范围内，以确保不同用户的状态分离。另一方面，OAuth2RestTemplate 还依赖于 OAuth2ProtectedResourceDetails 类，该类封装了 clientId、客户端安全码 clientSecret、访问范围 scope 等属性。

# 28 | 服务认证：如何使用 JWT 实现定制化 Token？

在 OAuth2 协议中，并没有对 Token 具体的组成结构有明确的规定。为了解决 Token 的标准化问题，就诞生了今天我们要介绍的 JWT。

**什么是 JWT？**

JWT 的全称是 JSON Web Token，所以它本质上就是一种基于 JSON 表示的 Token。

从结构上讲，JWT 本身是由三段信息构成的，第一段为头部（Header），第二段为有效负载（Payload），第三段为签名（Signature），如下所示：

```
header.payload.signature
```

在JWT中，每一段 JSON 对象都被 Base64 进行编码，然后编码后的内容用“.”号链接一起。所以本质上 JWT 就是一个字符串，如下所示的就是一个 JWT 字符串的示例：

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3NwcmluZ2hlYWx0aC5leGFtcGxlLmNvbSIsInN1YiI6Im1haWx0bzpzcHJpbmdoZWFsdGhAZXhhbXBsZS5jb20iLCJuYmYiOjE1OTkwNTY4NjIsImV4cCI6MTU5OTA2MDQ2MiwiaWF0IjoxNTk5MDU2ODYyLCJqdGkiOiJpZDEyMzQ1NiIsInR5cCI6Imh0dHBzOi8vc3ByaW5naGVhbHRoLmV4YW1wbGUuY29tL3JlZ2lzdGVyIn0.rlg2i8mWwV-gFjHUSCutX-UBMYrqxL0th1xtyGq7UdE
```

我们可以使用http://jwt.calebb.net/所提供的反向转换原始数据的功能。针对前面的 JWT 字符串，我们可以看到其中所包含的原始 JSON 数据，如下所示：

```json
{
 alg: "HS256",
 typ: "JWT"
}.
{
 iss: "https://springhealth.example.com",
 sub: "mailto:springhealth@example.com",
 nbf: 1599056862,
 exp: 1599060462,
 iat: 1599056862,
 jti: "id123456",
 typ: "https://springhealth.example.com/register"
}.
[signature]
```

**如何集成 OAuth2 与 JWT？**

首先需要在 Maven 的 pom 文件中添加对应的依赖包：

```xml
<dependency>
  <groupId>org.springframework.security</groupId>
  <artifactId>spring-security-jwt</artifactId>
</dependency>
```

创建一个用于配置 JwtTokenStore 的配置类：

```java
@Configuration
public class SpringHealthJWTTokenStoreConfig {
 
    @Bean
    public TokenStore tokenStore() {
        return new JwtTokenStore(jwtAccessTokenConverter());
    }
 
    @Bean
    public JwtAccessTokenConverter jwtAccessTokenConverter() {
        JwtAccessTokenConverter converter = new JwtAccessTokenConverter();
        converter.setSigningKey("123456");
        return converter;
	  }
 
    @Bean
    public DefaultTokenServices tokenServices() {
        DefaultTokenServices defaultTokenServices = new DefaultTokenServices();
        defaultTokenServices.setTokenStore(tokenStore());
        defaultTokenServices.setSupportRefreshToken(true);
        return defaultTokenServices;
    }
}
```

构建一个 SpringHealthAuthorizationServerConfigurer 类来覆写 AuthorizationServerConfigurerAdapter 中的 configure 方法。原先的这个 configure 方法实现如下：

```java
@Override
public void configure(AuthorizationServerEndpointsConfigurer endpoints) throws Exception {
    endpoints.authenticationManager(authenticationManager)
      .userDetailsService(userDetailsService);
}
```

而集成了 JWT 之后，该方法的实现过程如下所示：

```java
@Override
public void configure(AuthorizationServerEndpointsConfigurer endpoints) throws Exception {
    TokenEnhancerChain tokenEnhancerChain = new TokenEnhancerChain();
    tokenEnhancerChain.setTokenEnhancers(Arrays.asList(jwtTokenEnhancer, jwtAccessTokenConverter));
    endpoints.tokenStore(tokenStore).accessTokenConverter(jwtAccessTokenConverter)
      .tokenEnhancer(tokenEnhancerChain) 
      .authenticationManager(authenticationManager)
      .userDetailsService(userDetailsService);
}
```

这里构建了一个对 Token 的增强链 TokenEnhancerChain。

**如何在微服务中使用 JWT？**

在服务调用链中传播 JWT Token 有三个实现步骤。第一步，从 HTTP 请求中获取 JWT Token；第二步，以线程安全的方式存储 JWT Token 以便在后续的服务链中进行使用；第三步，将 JWT Token 嵌入 RestTemplate 请求中。

实现第一第二步，我们可以通过过滤器 Filter 对所有请求进行过滤。

```java
@Component
public class AuthorizationHeaderFilter implements Filter {

    @Override
    public void doFilter(ServletRequest servletRequest, 
                         ServletResponse servletResponse, 
                         FilterChain filterChain) throws IOException, ServletException {
        HttpServletRequest httpServletRequest = (HttpServletRequest) servletRequest;
        AuthorizationHeaderHolder.getAuthorizationHeader()
          .setAuthorizationHeader(
            httpServletRequest.getHeader(AuthorizationHeader.AUTHORIZATION_HEADER));
        filterChain.doFilter(httpServletRequest, servletResponse);
    }
 
    @Override
    public void init(FilterConfig filterConfig) throws ServletException {}
 
    @Override
    public void destroy() {}
}
```

这里的 AuthorizationHeaderHolder 如下所示：

```java
public class AuthorizationHeaderHolder {
    private static final ThreadLocal<AuthorizationHeader> 
      authorizationHeaderContext = new ThreadLocal<AuthorizationHeader>();
 
    public static final AuthorizationHeader getAuthorizationHeader() {
        AuthorizationHeader header = authorizationHeaderContext.get();
 
        if (header == null) {
            header = new AuthorizationHeader();
            authorizationHeaderContext.set(header);
        }
        return authorizationHeaderContext.get();
    }
 
    public static final void setAuthorizationHeader(AuthorizationHeader header) {
        authorizationHeaderContext.set(header);
    }
}
```

这里使用了 ThreadLocal 来确保对 AuthorizationHeader 对象访问的线程安全性。

AuthorizationHeader 定义如下，用于保存来自 HTTP 请求头的 JWT Token：

```java
@Component
public class AuthorizationHeader {
    public static final String AUTHORIZATION_HEADER = "Authorization";

    private String authorizationHeader = new String();
 
    public String getAuthorizationHeader() {
        return authorizationHeader;
    }
 
    public void setAuthorizationHeader(String authorizationHeader) {
        this.authorizationHeader = authorizationHeader;
    }
}
```

实现第三步，我们需要对 RestTemplate 进行一些设置，如下所示：

```java
@Bean
public RestTemplate getCustomRestTemplate() {
    RestTemplate template = new RestTemplate();
    List<ClientHttpRequestInterceptor> interceptors = template.getInterceptors();
    if (interceptors == null) {
        template.setInterceptors(Collections.singletonList(new AuthorizationHeaderInterceptor()));
    } else {
        interceptors.add(new AuthorizationHeaderInterceptor());
        template.setInterceptors(interceptors);
    } 
    return template;
}
```

AuthorizationHeaderInterceptor 的作用就是在 HTTP 请求的消息头中嵌入保存在 AuthorizationHeaderHolder 中的 JWT Token，如下所示：

```java
public class AuthorizationHeaderInterceptor implements ClientHttpRequestInterceptor {
 
    @Override
    public ClientHttpResponse intercept(
            HttpRequest request, byte[] body, ClientHttpRequestExecution execution)
            throws IOException {
 
        HttpHeaders headers = request.getHeaders();
        headers.add(
            AuthorizationHeader.AUTHORIZATION_HEADER, 
            AuthorizationHeaderHolder.getAuthorizationHeader().getAuthorizationHeader()
        );
        return execution.execute(request, body);
    }
}
```

**如何扩展 JWT？**

JWT具有良好的可扩展性，开发人员可以根据需要在 JWT Token 中添加自己想要添加的各种附加信息。

针对 JWT 的扩展性场景，Spring Security 专门提供了一个 TokenEnhancer 接口来对 Token 进行增强（Enhance），该接口定义如下：

```java
public interface TokenEnhancer {
    OAuth2AccessToken enhance(OAuth2AccessToken accessToken, OAuth2Authentication authentication);
}
```

可以看到这里处理的是一个 OAuth2AccessToken 接口，而该接口有一个默认的实现类 DefaultOAuth2AccessToken。我们可以通过该实现类的 setAdditionalInformation 方法以键值对的方式将附加信息添加到 OAuth2AccessToken 中，示例代码如下所示：

```java
public class SpringHealthJWTTokenEnhancer implements TokenEnhancer {

    @Override
    public OAuth2AccessToken enhance(OAuth2AccessToken accessToken, OAuth2Authentication authentication) {
        Map<String, Object> systemInfo= new HashMap<>();
 
        systemInfo.put("system", "springhealth");
 
        ((DefaultOAuth2AccessToken) accessToken).setAdditionalInformation(systemInfo);
        return accessToken;
    }
}
```

这里我们以硬编码的方式添加了一个“system”属性。

要想使得上述 SpringHealthJWTTokenEnhancer 类能够生效，我们需要对 SpringHealthAuthorizationServerConfigurer 类中的 configure 方法进行重新配置，并将 SpringHealthJWTTokenEnhancer 嵌入到 TokenEnhancerChain 中。事实上，我们在前面的代码中已经演示了这部分内容。

现在，我们已经扩展了 JWT Token。那么，如何从这个 JWT Token 中获取所扩展的属性呢？方法也比较简单和固定，如下所示：

```java
//获取 JWTToken
RequestContext ctx = RequestContext.getCurrentContext();
String authorizationHeader = ctx.getRequest().getHeader(AUTHORIZATION_HEADER);
String jwtToken = authorizationHeader.replace("Bearer ","");

//解析 JWTToken
String[] split_string = jwtToken.split("\\.");
String base64EncodedBody = split_string[1];
Base64 base64Url = new Base64(true);
String body = new String(base64Url.decode(base64EncodedBody));
JSONObject jsonObj = new JSONObject(body);

//获取定制化属性值
String systemName = jsonObj.getString("system");
```

我们可以把这段代码嵌入到需要使用到自定义“system”属性的任何场景中。



