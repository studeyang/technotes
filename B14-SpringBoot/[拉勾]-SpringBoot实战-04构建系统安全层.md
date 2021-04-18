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

# 18 | 如何基于 Spring Security 构建用户认证体系？

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











