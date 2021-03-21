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



