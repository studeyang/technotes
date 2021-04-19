# 构建系统安全层

# 17 | Spring Security 架构及核心类

**Spring Security 中的过滤器链**

Spring Security 中采用的是管道-过滤器（Pipe-Filter）架构模式，这些过滤器链，构成了 Spring Security 的核心。如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210416230843.png" alt="image-20210416230843195" style="zoom:50%;" />

项目一旦启动，过滤器链将会实现自动配置，如下图所示：

![image-20210416231208007](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210416231208.png)

UsernamePasswordAuthenticationFilter 用来检查输入的用户名和密码，代码如下：

```java
public class UsernamePasswordAuthenticationFilter extends AbstractAuthenticationProcessingFilter {

    public Authentication attemptAuthentication(HttpServletRequest request,
                                                HttpServletResponse response) 
        throws AuthenticationException {
        if (postOnly && !request.getMethod().equals("POST")) {
            throw new AuthenticationServiceException(
                "Authentication method not supported: " + request.getMethod());
        }
 
        String username = obtainUsername(request);
        String password = obtainPassword(request);
 
        if (username == null) {
            username = "";
        }
 
        if (password == null) {
            password = "";
        }
 
        username = username.trim();
 
        UsernamePasswordAuthenticationToken authRequest = 
            new UsernamePasswordAuthenticationToken(username, password);

        // Allow subclasses to set the "details" property
        setDetails(request, authRequest);

        return this.getAuthenticationManager().authenticate(authRequest);
    }
    …
}
```

BasicAuthenticationFilter 用来认证用户的身份。

FilterSecurityInterceptor 用来判定该请求是否能够访问目标 HTTP 端点。

**Spring Security 中的核心类**

![image-20210416230408984](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210416230409.png)

SecurityContextHolder 存储了应用的安全上下文对象 SecurityContext，包含系统请求中最近使用的认证信息。

一个 HTTP 请求到达系统后，将通过一系列的 Filter 完成用户认证，然后具体的工作交由 AuthenticationManager 完成，AuthenticationManager 成功验证后会返回填充好的 Authentication 实例。

AuthenticationManager 是一个接口，其实现类 ProviderManager 会进一步依赖 AuthenticationProvider 接口完成具体的认证工作。

在 Spring Security 中存在一大批 AuthenticationProvider 接口的实现类，分别完成各种认证操作。在执行具体的认证工作时，Spring Security 势必会使用用户详细信息，UserDetailsService 服务就是用来对用户详细信息实现管理。

# 18 | 基于 Spring Security 构建用户认证体系

在 Spring Boot 中整合 Spring Security 框架首先需要引入依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
```

只要我们在代码工程中添加了上述依赖，包含在该工程中的所有 HTTP 端点都将被保护起来。

在引入 spring-boot-starter-security 依赖之后，Spring Security 会默认创建一个用户名为“user”的账号。当我们访问 AccountController 的 “accounts/{accountId}” 端点时，弹出如下界面：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210418223041.png" alt="image-20210418223041403" style="zoom: 50%;" />

同时，控制台日志打印如下：

```txt
Using generated security password: 17bbf7c4-456a-48f5-a12e-a680066c8f80
```

因此，访问该接口需要设置如下信息：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210418223233.png" alt="image-20210418223233304" style="zoom:50%;" />

每次启动应用时，通过 Spring Security 自动生成的密码都会有所变化。如果我们想设置登录账号和密码，可以在 application.yml 中配置如下：

```yml
spring:
  security:
    user:
      name: springcss
      password: springcss_password
```

**配置 Spring Security**

初始化用户信息所依赖的配置类是 WebSecurityConfigurer 接口，在日常开发中，我们往往是使用 WebSecurityConfigurerAdapter 类并覆写其中的 configure(AuthenticationManagerBuilder auth) 的方法完成配置工作。

使用 AuthenticationManagerBuilder 类创建一个 AuthenticationManager 就能够轻松实现基于内存、LADP 和 JDBC 的验证。初始化所使用的用户信息只需要指定用户名（Username）、密码（Password）和角色（Role）这三项数据即可。

- 使用基于内存的用户信息存储方案

```java
@Override
protected void configure(AuthenticationManagerBuilder builder) throws Exception {
    builder.inMemoryAuthentication()
        .withUser("springcss_user")
        .password("password1")
        // 或者使用.authorities("ROLE_USER")
        .roles("USER")
        .and()
        .withUser("springcss_admin")
        .password("password2")
        .roles("USER", "ADMIN");
}
```

- 使用基于数据库的用户信息存储方案

表结构如下：

```sql
create table users(
  username varchar_ignorecase(50) not null primary key,
  password varchar_ignorecase(500) not null,
  enabled boolean not null
);
 
create table authorities (
  username varchar_ignorecase(50) not null,
  authority varchar_ignorecase(50) not null,
  constraint fk_authorities_users foreign key(username) references users(username)
);
 
create unique index ix_auth_username on authorities (username,authority);
```

Spring Security 的配置代码如下：

```java
@Autowired
DataSource dataSource;
 
@Override
protected void configure(AuthenticationManagerBuilder auth) throws Exception {
    auth.jdbcAuthentication()
        .dataSource(dataSource)
        .usersByUsernameQuery("select username, password, enabled from Users where username=?")
        .authoritiesByUsernameQuery("select username, authority from UserAuthorities where username=?")
        .passwordEncoder(new BCryptPasswordEncoder());
}
```

**实现定制化用户认证方案**

- 扩展 UserDetails

```java
public class SpringCssUser implements UserDetails {

    private static final long serialVersionUID = 1L;
    private Long id;
    private final String username;
    private final String password;
    private final String phoneNumber;
    // 省略getter/setter
    // 省略重写方法
}
```

- 扩展 UserDetailsService

```java
@Service
public class SpringCssUserDetailsService implements UserDetailsService {
	 
    @Autowired
    private SpringCssUserRepository repository;

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        SpringCssUser user = repository.findByUsername(username);
        if (user != null) {
            return user;
        }
        throw new UsernameNotFoundException("SpringCSS User '" + username + "' not found");
    }
}
```

- 整合定制化配置

```java
@Configuration
public class SpringCssSecurityConfig extends WebSecurityConfigurerAdapter {

    @Autowired
    SpringCssUserDetailsService springCssUserDetailsService;

    @Override
    protected void configure(AuthenticationManagerBuilder auth) throws Exception {
        auth.userDetailsService(springCssUserDetailsService);
    }
}
```

# 19 | 基于 Spring Security 实现安全访问

在日常开发过程中，我们需要对 Web 应用中的不同 HTTP 端点进行不同粒度的权限控制。

**对 HTTP 端点进行访问授权管理**

- 使用配置方法

配置方法也是位于 WebSecurityConfigurerAdapter 类中，但使用的是 configure(HttpSecurity http) 方法，如下代码所示：

```java
protected void configure(HttpSecurity http) throws Exception {
    http.authorizeRequests()
        // 所有请求都需要认证
        .anyRequest()
        // 允许认证用户访问
        .authenticated()
        .and()
        // 需要使用表单进行登录
        .formLogin()
        .and()
        // 使用 HTTP Basic Authentication 方法完成认证
        .httpBasic();
}
```

Spring Security 还提供了一个 access() 方法，允许开发人员传入一个表达式进行更细粒度的权限控制，这里，我们将引入Spring 框架提供的一种动态表达式语言—— SpEL（Spring Expression Language 的简称）。

只要 SpEL 表达式的返回值为 true，access() 方法就允许用户访问，如下代码所示：

```java
@Override
public void configure(HttpSecurity http) throws Exception {
 
    http.authorizeRequests()
        .antMatchers("/orders")
        .access("hasRole('ROLE_USER')");
}
```

- 使用注解

Spring Security 提供了 @PreAuthorize 注解也可以实现类似的效果，使用该注解代码如下所示：

```java
@RestController
@RequestMapping(value="orders")
public class OrderController {
 
    @PostMapping(value = "/")
    @PreAuthorize("hasRole(ROLE_ADMIN)")
    public void addOrder(@RequestBody Order order) {
        …
    }
}
```

@PostAuthorize 主要用于请求结束之后检查权限。

**实现多维度访问授权方案**

- 使用用户级别保护服务访问

该级别是最基本的资源保护级别，只要是认证用户就可能访问服务内的各种资源。

```java
@Configuration
public class SpringCssSecurityConfig extends WebSecurityConfigurerAdapter {

    protected void configure(HttpSecurity http) throws Exception {
        http.authorizeRequests()
            .anyRequest()
            .authenticated();
    }
}
```

- 使用用户+角色级别保护服务访问

该级别在认证用户级别的基础上，还要求用户属于某一个或多个特定角色。

```java
@Configuration
public class SpringCssSecurityConfig extends WebSecurityConfigurerAdapter {
 
    @Override
    public void configure(HttpSecurity http) throws Exception {
 
        http.authorizeRequests()
            .antMatchers("/customers/**")
            .hasRole("ADMIN")
            .anyRequest()
            .authenticated();
    }
}
```

上述代码表示只有"ADMIN"角色的认证用户才能访问以"/customers/"为根地址的所有 URL。

- 使用用户+角色+操作级别保护服务访问

该级别在认证用户+角色级别的基础上，对某些 HTTP 操作方法做了访问限制。

```java
@Configuration
public class SpringCssSecurityConfig extends WebSecurityConfigurerAdapter {
 
    @Override
    public void configure(HttpSecurity http) throws Exception{
        http.authorizeRequests()
                .antMatchers(HttpMethod.DELETE, "/customers/**")
                .hasRole("ADMIN")
                .anyRequest()
                .authenticated();
    }
}
```

上述代码的效果在于对“/customers”端点执行删除操作时，我们需要使用具有“ADMIN”角色的“springcss_admin”用户，否则会出现“access_denied”错误信息。。

# 构建系统监控层

# 20 | 使用 Actuator 组件实现系统监控

**引入 Spring Boot Actuator 组件**

引入依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

服务启动后，访问 http://localhost:8080/actuator 可以看到如下结果：

```json
{
  "_links":{
    "self":{
      "href":"http://localhost:8080/actuator",
      "templated":false
    },
    "health-path":{
      "href":"http://localhost:8080/actuator/health/{*path}",
      "templated":true
    },
    "health":{
      "href":"http://localhost:8080/actuator/health",
      "templated":false
    },
    "info":{
      "href":"http://localhost:8080/actuator/info",
      "templated":false
    },
    
    // 上面是默认暴露信息，加上下面就是所有的信息
    
    "beans":{
      "href":"http://localhost:8080/actuator/beans",
      "templated":false
    },
    "conditions":{
      "href":"http://localhost:8080/actuator/conditions",
      "templated":false
    },
    "configprops":{
      "href":"http://localhost:8080/actuator/configprops",
      "templated":false
    },
    "env":{
      "href":"http://localhost:8080/actuator/env",
      "templated":false
    },
    "env-toMatch":{
      "href":"http://localhost:8080/actuator/env/{toMatch}",
      "templated":true
    },
    "loggers":{
      "href":"http://localhost:8080/actuator/loggers",
      "templated":false
    },
    "loggers-name":{
      "href":"http://localhost:8080/actuator/loggers/{name}",
      "templated":true
    },
    "heapdump":{
      "href":"http://localhost:8080/actuator/heapdump",
      "templated":false
    },
    "threaddump":{
      "href":"http://localhost:8080/actuator/threaddump",
      "templated":false
    },
    "metrics-requiredMetricName":{
      "href":"http://localhost:8080/actuator/metrics/{requiredMetricName}",
      "templated":true
    },
    "metrics":{
      "href":"http://localhost:8080/actuator/metrics",
      "templated":false
    },
    "scheduledtasks":{
      "href":"http://localhost:8080/actuator/scheduledtasks",
      "templated":false
    },
    "mappings":{
      "href":"http://localhost:8080/actuator/mappings",
      "templated":false
    }
  }
}
```

如果我们想看到所有端点，可以在配置文件中配置：

```yaml
management:
  endpoints:
    web:
      exposure:
        include: "*"
```

常见端点梳理如下：

![image-20210419231958588](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210419231958.png)

通过访问上表中的各个端点，我们就可以获取自己感兴趣的监控信息了。

**health 端点**

访问 http://localhost:8082/actuator/health 端点，就可以得到服务的基本状态：

```json
{
  "status":"UP",
  // 下面是更详细的信息
  "components":{
    "diskSpace":{
      "status":"UP",
      "details":{
        "total":201649549312,
        "free":3434250240,
        "threshold":10485760
      }
    },
    "ping":{
      "status":"UP"
    }
  }
}
```

如果想获取更详细的状态信息，可在配置文件中配置：

```yaml
management: 
  endpoint:
    health:
      show-details: always
```

**扩展 Actuator 端点**

Spring Boot 默认暴露了日常开发中最常见的两个端点：Info 端点和 Health 端点。接下来，我们讨论下如何对这两个端点进行扩展。

- 扩展 Info 端点

Info 端点用于暴露 Spring Boot 应用的自身信息。Spring Boot 中常见的 InfoContributor 如下表所示：

| InfoContributor名称        | 描述                                                       |
| -------------------------- | ---------------------------------------------------------- |
| EnvironmentInfoContributor | 暴露 Environment 中 key 为 info 的所有 key                 |
| GitInfoContributor         | 暴露 git 信息，如果存在 git.properties 文件                |
| BuildInfoContributor       | 暴露构建信息，如果存在 META-INF/build-info.properties 文件 |

EnvironmentInfoContributor 会收集 info 下的所有key，例如在 application.yml 中：

```
info:
  app:
	  encoding: UTF-8
	  java:
	    source: 1.8.0_31
	    target: 1.8.0_31
```

我们也可以扩展 info 端点的信息：

```java
@Component
public class CustomBuildInfoContributor implements InfoContributor {

    @Override
    public void contribute(Builder builder) {
        builder.withDetail("build", Collections.singletonMap("timestamp", new Date())); 
    }
}
```

最终效果如下：

```json
{
  "app":{
    "encoding":"UTF-8",
    "java":{
      "source":"1.8.0_31",
      "target":"1.8.0_31"
    }
  },
  "build":{
    "timestamp":1604307503710
  }
}
```

- 扩展 Health 端点

Health 端点用于检查正在运行的应用程序健康状态，健康状态信息由 HealthIndicator 对象从 Spring 的 ApplicationContext 中获取。

常见的 HealthIndicator 如下表所示：

| HealthIndicator 名称         | 描述                            |
| ---------------------------- | ------------------------------- |
| DiskSpaceHealthIndicator     | 检查磁盘空间是否足够            |
| DataSourceHealthIndicator    | 检查是否可以获得连接 DataSource |
| ElasticsearchHealthIndicator | 检查 Elasticsearch 集群是否启动 |
| JmsHealthIndicator           | 检查 JMS 代理是否启动           |
| MailHealthIndicator          | 检查邮件服务器是否启动          |
| MongoHealthIndicator         | 检查 Mongo 数据库是否启动       |
| RabbitHealthIndicator        | 检查 RabbitMQ 服务器是否启动    |
| RedisHealthIndicator         | 检查 Redis 服务器是否启动       |
| SolrHealthIndicator          | 检查 Solr 服务器是否已启动      |

为了明确某个服务的状态，我们可以自定义一个端点来展示这个服务的状态信息：

```java
@Component
public class CustomerServiceHealthIndicator implements HealthIndicator {

    @Override
    public Health health() {
        try {
            URL url = new URL("http://localhost:8083/health/");
            HttpURLConnection conn = (HttpURLConnection) 
            url.openConnection();
            int statusCode = conn.getResponseCode();
            if (statusCode >= 200 && statusCode < 300) {
                return Health.up().build();
            } else {
                return Health.down().withDetail("HTTP Status Code", statusCode).build();
            }
        } catch (IOException e) {
            return Health.down(e).build();
        }
    }
}
```

效果如下：

```json
{
  "status": "UP",
  "details": {
    "customerservice": {
      "status": "UP"
    }
    …
  }
}
```

```json
{
  "status": "DOWN",
  "details": {
    "customerservice": {
      "status": "DOWN",
      "details": {
        "HTTP Status Code": "404"
      }
    },
    …
  }
}
```

```json
{
  "status": "DOWN",
  "details": {
    "customerservice": {
      "status": "DOWN",
      "details": {
        "error": "java.net.ConnectException: Connection refused: connect"
      }
    },
    …
  }
}
```



