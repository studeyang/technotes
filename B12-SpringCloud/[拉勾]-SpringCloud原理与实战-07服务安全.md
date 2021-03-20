# 25 | 服务安全：微服务访问安全需求和实现方案？

**微服务架构中的安全性设计**

对于微服务架构而言，安全性设计的最核心考虑点还是认证（Authentication）和授权（Authorization）。

1. 认证与授权

所谓认证，解决的是“你是谁”这一个问题。一旦明确 “你是谁”之后，下一步就可以判断“你能做什么”，这个步骤就是授权。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210317232529.png" alt="image-20210317232529450" style="zoom:50%;" />

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

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210318215633.png" alt="image-20210318215633452" style="zoom:50%;" />

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

![image-20210318223410970](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210318223411.png)

接下来我们指定针对授权模式的专用配置信息：

![image-20210318223617642](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210318223617.png)

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

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210320231755.png" alt="image-20210320231755420" style="zoom:50%;" />

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

