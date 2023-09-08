# 开篇词 | Spring Security，为你的应用安全与职业之路保驾护航

**这门课程是如何设计的？**

- 模块一：基础功能篇。这部分我将介绍 Spring Security 的一些基础性功能，包括认证、授权和加密。
- 模块二：高级主题篇。这部分功能面向特定需求，用于构建比较复杂的应用场景，包括过滤器、跨站点请求伪造保护、跨域资源共享，以及针对非 Web 应用程序的全局方法安全机制。
- 模块三：OAuth2 与微服务篇。这部分内容关注微服务开发框架Spring Cloud 与 Spring Security 之间的整合，我们将对 OAuth2 协议和 JWT 全面展开讲解，并使用这些技术体系构建安全的微服务系统，以及单点登录系统。
- 模块四：框架扩展篇。这部分内容是对 Spring Security 框架在应用上的一些扩展，包括在 Spring Security 中引入全新的响应式编程技术，以及如何对应用程序安全性进行测试的系统方法。

课程源码：https://github.com/lagouEdAnna/SpringSecurity-jianxiang

# ==基础功能篇==

# 01 | 顶级框架：Spring Security 是一款什么样的安全性框架？

Spring Security 提供的是一整套完整的安全性解决方案。面向不同的业务需求和应用场景，Spring Security 分别提供了对应的安全性功能，在接下来的内容中，我们将从单体应用、微服务架构以及响应式系统这三个维度对这些功能展开讨论。

**Spring Security 与单体应用**

在安全领域中非常常见但又容易混淆的两个概念，即认证（Authentication）和授权（Authorization）。

所谓认证，解决的是“你是谁”这一个问题，也就是说对于每一次访问请求，系统都能判断出访问者是否具有合法的身份标识。

一旦明确 “你是谁”，下一步就可以判断“你能做什么”，这个步骤就是授权。通用的授权模型大多基于权限管理体系，即对资源、权限、角色和用户的一种组合处理。

如果我们将认证和授权结合起来，就构成了对系统中的资源进行安全性管理的最常见解决方案，即先判断资源访问者的有效身份，再来确定其是否有对这个资源进行访问的合法权限，如下图所示：

![image-20230905233446595](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202309052334742.png)

**Spring Security 与微服务架构**

服务提供者充当的角色就是资源的服务器，而服务消费者就是客户端。所以各个服务本身既可以是客户端，也可以作为资源服务器，或者两者兼之。

接下来，我们把认证和授权结合起来，梳理出微服务访问场景下的安全性实现方案，如下图所示：

![image-20230905233752129](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202309052337170.png)

可以看到，与单体应用相比，在微服务架构中需要把认证和授权的过程进行集中化管理，所以在上图中出现了一个授权中心。 授权中心会获取客户端请求中所带有的身份凭证信息，然后基于凭证信息生成一个 Token，这个 Token 中就包含了权限范围和有效期。

**Spring Security 与响应式系统**

响应式编程是 Spring 5 最核心的新功能，也是 Spring 家族目前重点推广的技术体系。Spring 5 的响应式编程模型以 Project Reactor 库为基础，后者则实现了响应式流规范。

# 02 | 用户认证：如何使用 Spring Security 构建用户认证体系？

**Spring Security 配置体系**

```java
protected void configure(HttpSecurity http) throws Exception {
 
        http
           .authorizeRequests()
               .anyRequest().authenticated()
               .and()
           .formLogin().and()
           .httpBasic();
}
```

- 首先，通过 HttpSecurity 类的 authorizeRequests() 方法对所有访问 HTTP 端点的 HttpServletRequest 进行限制；
- 然后，anyRequest().authenticated() 语句指定了对于所有请求都需要执行认证，也就是说没有通过认证的用户就无法访问任何端点；
- 接着，formLogin() 语句用于指定使用表单登录作为认证方式，也就是会弹出一个登录界面；
- 最后，httpBasic() 语句表示可以使用 HTTP 基础认证（Basic Authentication）方法来完成认证。

**实现 HTTP 基础认证和表单登录认证**

httpBasic() 和 formLogin() 这两种用于控制用户认证的实现手段，分别代表了HTTP 基础认证和表单登录认证。

现在查看 HTTP 请求，可以看到 Request Header 中添加了 Authorization 标头，格式为：Authorization: \<type\> \<credentials\>。这里的 type 就是“Basic”，而 credentials 则是这样一个字符串：

```
dXNlcjo5YjE5MWMwNC1lNWMzLTQ0YzctOGE3ZS0yNWNkMjY3MmVmMzk=
```

这个字符串就是将用户名和密码组合在一起，再经过 Base64 编码得到的结果。而我们知道 Base64 只是一种编码方式，并没有集成加密机制，所以本质上传输的还是明文形式。

HTTP 基础认证比较简单，没有定制的登录页面，所以单独使用的场景比较有限。在使用 Spring Security 时，我们一般会把 HTTP 基础认证和接下来要介绍的表单登录认证结合起来一起使用。

在 WebSecurityConfigurerAdapter 的 configure() 方法中，一旦配置了 HttpSecurity 的 formLogin() 方法，就启动了表单登录认证。

**配置 Spring Security 用户认证体系**

我们已经知道可以通过 WebSecurityConfigurerAdapter 类的 configure(HttpSecurity http) 方法来完成认证。我们可以通过继承 WebSecurityConfigurerAdapter 类并且覆写其中的 configure(AuthenticationManagerBuilder auth) 的方法来完成对用户信息的配置工作。请注意这是两个不同的 configure() 方法。

针对 WebSecurityConfigurer 配置类，我们首先需要明确配置的内容。实际上，初始化用户信息非常简单，只需要指定用户名（Username）、密码（Password）和角色（Role）这三项数据即可。在 Spring Security 中，基于 AuthenticationManagerBuilder 工具类为开发人员提供了基于内存、JDBC、LDAP 等多种验证方案。

- 使用基于内存的用户信息存储方案

```java
@Override
protected void configure(AuthenticationManagerBuilder builder) throws Exception {
 
    builder.inMemoryAuthentication()
        .withUser("spring_user").password("password1").roles("USER")
        .and()
        .withUser("spring_admin").password("password2").roles("USER", "ADMIN");
}
```

可以看到，基于内存的用户信息存储方案实现也比较简单，但同样缺乏灵活性，因为用户信息是写死在代码里的。所以，我们接下来就要引出另一种更为常见的用户信息存储方案——数据库存储。

- 使用基于数据库的用户信息存储方案

既然是将用户信息存储在数据库中，势必需要创建表结构。我们可以在 Spring Security 的源文件（org/springframework/security/core/userdetails/jdbc/users.ddl）中找到对应的 SQL 语句，如下所示：

```sql
create table users(username varchar_ignorecase(50) not null primary key,password varchar_ignorecase(500) not null,enabled boolean not null);
 
create table authorities (username varchar_ignorecase(50) not null,authority varchar_ignorecase(50) not null,constraint fk_authorities_users foreign key(username) references users(username));
 
create unique index ix_auth_username on authorities (username,authority);
```

一旦我们在自己的数据库中创建了这两张表，并添加了相应的数据，就可以直接通过注入一个 DataSource 对象进行用户数据的查询，如下所示：

```java
@Autowired
DataSource dataSource;
 
@Override
protected void configure(AuthenticationManagerBuilder auth) throws Exception {
 
        auth.jdbcAuthentication().dataSource(dataSource)
               .usersByUsernameQuery("select username, password, enabled from Users " + "where username=?")
               .authoritiesByUsernameQuery("select username, authority from UserAuthorities " + "where username=?")
               .passwordEncoder(new BCryptPasswordEncoder());
}
```

请你注意，这里我们用到了一个passwordEncoder() 方法，这是 Spring Security 中提供的一个密码加解密器。

# 03 | 认证体系：如何深入理解 Spring Security 用户认证机制？

**Spring Security 中的用户和认证**

Spring Security 中的认证过程由一组核心对象组成，大致可以分成两大类，一类是**用户对象**，一类是**认证对象**，下面我们来具体了解一下。



- Spring Security 中的用户对象

Spring Security 中的用户对象用来描述用户并完成对用户信息的管理，涉及**UserDetails、GrantedAuthority、UserDetailsService 和 UserDetailsManager**这四个核心对象。

1. UserDetails：描述 Spring Security 中的用户。
2. GrantedAuthority：定义用户的操作权限。
3. UserDetailsService：定义了对 UserDetails 的查询操作。
4. UserDetailsManager：扩展 UserDetailsService，添加了创建用户、修改用户密码等功能。



- Spring Security 中的认证对象

认证对象代表认证请求本身，并保存该请求访问应用程序过程中涉及的各个实体的详细信息。

```java
public interface Authentication extends Principal, Serializable {
    //安全主体具有的权限
    Collection<? extends GrantedAuthority> getAuthorities();
 
	//证明主体有效性的凭证
    Object getCredentials();
 
    //认证请求的明细信息
    Object getDetails();
 
    //主体的标识信息
    Object getPrincipal();
 
    //认证是否通过
    boolean isAuthenticated();
 
    //设置认证结果
    void setAuthenticated(boolean isAuthenticated) throws IllegalArgumentException;
}
```

在安全领域，请求访问该应用程序的用户通常被称为**主体**（Principal），在 JDK 中存在一个同名的接口，而 Authentication 扩展了这个接口。

显然，Authentication 只代表了认证请求本身，而具体执行认证的过程和逻辑需要由专门的组件来负责，这个组件就是 AuthenticationProvider，定义如下：

```java
public interface AuthenticationProvider {
 
    //执行认证，返回认证结果
    Authentication authenticate(Authentication authentication)
             throws AuthenticationException;
 
    //判断是否支持当前的认证对象
    boolean supports(Class<?> authentication);
}
```



**实现定制化用户认证方案**

通过前面的分析，我们明确了用户信息存储的实现过程实际上是可以定制化的。Spring Security 所做的工作只是把常见的、符合一般业务场景的实现方式嵌入到了框架中。如果有特殊的场景，开发人员完全可以实现自定义的用户信息存储方案。

- 扩展 UserDetails

扩展 UserDetails 的方法就是直接实现该接口，例如我们可以构建如下所示的 SpringUser 类：

```java
public class SpringUser implements UserDetails {
 
    private static final long serialVersionUID = 1L;
    private Long id;  
    private final String username;
    private final String password;
    private final String phoneNumber;
}
```

一旦我们构建了这样一个 SpringUser 类，就可以创建对应的表结构存储类中定义的字段。

```java
public interface SpringUserRepository extends CrudRepository<SpringUser, Long> {
    SpringUser findByUsername(String username);  
}
```



- 扩展 UserDetailsService

UserDetailsService 接口只有一个 loadUserByUsername 方法需要实现。因此，我们基于 SpringUserRepository 的 findByUsername 方法，根据用户名从数据库中查询数据。

```java
@Service
public class SpringUserDetailsService 
        implements UserDetailsService {
	 
  @Autowired
  private SpringUserRepository repository;
 
  @Override
  public UserDetails loadUserByUsername(String username)
      throws UsernameNotFoundException {
 
    SpringUser user = repository.findByUsername(username);
    if (user != null) {
      return user;
    }
    throw new UsernameNotFoundException(
                    "SpringUser '" + username + "' not found");
  }
}
```



- 扩展 AuthenticationProvider

扩展 AuthenticationProvider 的过程就是提供一个自定义的 AuthenticationProvider 实现类。这里我们以最常见的用户名密码认证为例，梳理自定义认证过程所需要实现的步骤，如下所示：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202309072202806.png)

首先我们需要通过 UserDetailsService 获取一个 UserDetails 对象，然后根据该对象中的密码与认证请求中的密码进行匹配，如果一致则认证成功，反之抛出一个 BadCredentialsException 异常。示例代码如下所示：

```java
@Component
public class SpringAuthenticationProvider implements AuthenticationProvider {
 
    @Autowired
    private UserDetailsService userDetailsService;
 
    @Autowired
    private PasswordEncoder passwordEncoder;
 
    @Override
    public Authentication authenticate(Authentication authentication) {
        String username = authentication.getName();
        String password = authentication.getCredentials().toString();
 
        UserDetails user = userDetailsService.loadUserByUsername(username);
        if (passwordEncoder.matches(password, user.getPassword())) {
            return new UsernamePasswordAuthenticationToken(username, password, u.getAuthorities());
        } else {
            throw new BadCredentialsException("The username or password is wrong!");
        }
    }
 
    @Override
    public boolean supports(Class<?> authenticationType) {
        return authenticationType.equals(UsernamePasswordAuthenticationToken.class);
    }
}
```



- 整合定制化配置

最后，我们创建一个 SpringSecurityConfig 类，该类继承了 WebSecurityConfigurerAdapter 配置类。

```java
@Configuration
public class SpringSecurityConfig extends WebSecurityConfigurerAdapter {
 
    @Autowired
    private UserDetailsService springUserDetailsService;
 
    @Autowired
    private AuthenticationProvider springAuthenticationProvider;
 
 
    @Override
    protected void configure(AuthenticationManagerBuilder auth) throws Exception {
 
     auth.userDetailsService(springUserDetailsService)
	.authenticationProvider(springAuthenticationProvider);
	}
}
```

# 04 | 密码安全：Spring Security 中包含哪些加解密技术？

用户认证的过程通常涉及密码的校验，因此密码的安全性也是我们需要考虑的一个核心问题。Spring Security 作为一款功能完备的安全性框架，一方面提供了**用于完成认证操作的 PasswordEncoder 组件**，另一方面也包含一个独立而完整的**加密模块**，方便在应用程序中单独使用。

**PasswordEncoder**

我们通过 jdbcAuthentication() 方法验证用户信息时一定要**集成加密机制**，也就是使用 passwordEncoder() 方法嵌入一个 PasswordEncoder 接口的实现类。

```java
@Override
protected void configure(AuthenticationManagerBuilder auth) throws Exception {
 
        auth.jdbcAuthentication().dataSource(dataSource)
               .usersByUsernameQuery("select username, password, enabled from Users " + "where username=?")
               .authoritiesByUsernameQuery("select username, authority from UserAuthorities " + "where username=?")
               .passwordEncoder(new BCryptPasswordEncoder());
}
```



- PasswordEncoder 接口

在 Spring Security 中，PasswordEncoder 接口代表的是一种密码编码器，其核心作用在于**指定密码的具体加密方式**，以及如何将一段给定的加密字符串与明文之间完成匹配校验。

Spring Security 内置了一大批 PasswordEncoder 接口的实现类，如下所示：

1. NoOpPasswordEncoder：以明文形式保留密码，不对密码进行编码。这种 PasswordEncoder 通常只用于演示，不应该用于生产环境。
2. StandardPasswordEncoder：使用 SHA-256 算法对密码执行哈希操作。
3. BCryptPasswordEncoder：使用 bcrypt 强哈希算法对密码执行哈希操作。
4. Pbkdf2PasswordEncoder：使用 PBKDF2 算法对密码执行哈希操作。



- 自定义 PasswordEncoder

如果你想使用某种算法集成 PasswordEncoder，就可以实现类似如下所示的 Sha512PasswordEncoder，这里使用了 SHA-512 作为加解密算法：

```java
public class Sha512PasswordEncoder implements PasswordEncoder {
 
   @Override
   public String encode(CharSequence rawPassword) {
      return hashWithSHA512(rawPassword.toString());
   }

   @Override
   public boolean matches(CharSequence rawPassword, String encodedPassword) {
      String hashedPassword = encode(rawPassword);
  	  return encodedPassword.equals(hashedPassword);
   }

   private String hashWithSHA512(String input) {
     StringBuilder result = new StringBuilder();

     try {
       MessageDigest md = MessageDigest.getInstance("SHA-512");
       byte [] digested = md.digest(input.getBytes());
       for (int i = 0; i < digested.length; i++) {
       result.append(Integer.toHexString(0xFF & digested[i]));
       }
       } catch (NoSuchAlgorithmException e) {
       throw new RuntimeException("Bad algorithm");
     }

     return result.toString();
  }
}
```



- 代理式 DelegatingPasswordEncoder

在对密码进行加解密过程中，只会使用到一个 PasswordEncoder，如果这个 PasswordEncoder 不满足我们的需求，那么就需要替换成另一个 PasswordEncoder。这就引出了一个问题，如何优雅地应对这种变化呢？

虽然 DelegatingPasswordEncoder 也实现了 PasswordEncoder 接口，但事实上，它更多扮演了一种代理组件的角色，这点从命名上也可以看出来。DelegatingPasswordEncoder 将具体编码的实现根据要求代理给不同的算法，以此实现不同编码算法之间的兼容并协调变化。



**Spring Security 加密模块**

使用 Spring Security 时，通常涉及用户认证的部分会用到加解密技术。但就应用场景而言，加解密技术是一种通用的基础设施类技术，不仅可以用于用户认证，也可以用于其他任何涉及敏感数据处理的场景。因此，Spring Security 也充分考虑到了这种需求，专门提供了一个加密模式（Spring Security Crypto Module，SSCM）。

请注意，尽管 PasswordEncoder 也属于这个模块的一部分，但这个模块本身是高度独立的，我们可以脱离于用户认证流程来使用这个模块。

```java
// 创建一个 8 字节的密钥，并将其编码为十六进制字符串
String salt = KeyGenerators.string().generateKey(); 
String password = "secret"; 
String valueToEncrypt = "HELLO"; 
// 使用 256 位 AES 算法对 password 字段进行加密
BytesEncryptor e = Encryptors.standard(password, salt); 
byte [] encrypted = e.encrypt(valueToEncrypt.getBytes()); 
byte [] decrypted = e.decrypt(encrypted);
```

在日常开发过程中，你可以根据需要调整上述代码并嵌入到我们的系统中。

# 05 | 访问授权：如何对请求的安全访问过程进行有效配置？

**Spring Security 中的权限和角色**

- 基于权限进行访问控制

GrantedAuthority 对象代表的就是一种权限对象，而一个 UserDetails 对象具备一个或多个 GrantedAuthority 对象。

如果用代码来表示这种关联关系，可以采用如下所示的实现方法：

```java
UserDetails user = User.withUsername("jianxiang")
     .password("123456")
     .authorities("create", "delete")
     .build();
```

在 Spring Security 中，提供了一组针对 GrantedAuthority 的配置方法。例如：

1. hasAuthority(String)，允许具有**特定权限**的用户进行访问；
1. hasAnyAuthority(String)，允许具有**任一权限**的用户进行访问。

使用方式：

```java
// 特定权限
httpSecurity.authorizeRequests().anyRequest().hasAuthority("CREATE");        
// 任意一种权限
httpSecurity.authorizeRequests().anyRequest().hasAnyAuthority("CREATE", "DELETE");
// 表达式的返回值是 true，access() 方法就会允许用户访问
httpSecurity.authorizeRequests().anyRequest().access("hasAuthority('CREATE')");
// 更为复杂的场景
String expression = "hasAuthority('CREATE') and !hasAuthority('Retrieve')"; 
httpSecurity.authorizeRequests().anyRequest().access(expression);
```



- 基于角色进行访问控制

角色可以看成是拥有多个权限的一种数据载体。我们可以使用如下方式初始化用户的角色：

```java
UserDetails user = User.withUsername("jianxiang")
      .password("123456")
      .authorities("ROLE_ADMIN")
      .build();
// 另一种简化的方法
UserDetails user = User.withUsername("jianxiang")
      .password("123456")
      .roles("ADMIN")
      .build();
```

上述代码相当于为用户“jianxiang”指定了“ADMIN”这个角色。

和权限配置一样，Spring Security 也通过使用对应的 hasRole() 和 hasAnyRole() 方法来判断用户是否具有某个角色或某些角色，使用方法如下所示：

```java
httpSecurity.authorizeRequests().anyRequest().hasRole("ADMIN");
```

下表展示了常见的配置方法及其作用：

| 配置方法                | 作用                               |
| ----------------------- | ---------------------------------- |
| anonymous()             | 允许匿名访问                       |
| authenticated()         | 允许认证用户访问                   |
| denyAll()               | 无条件禁止一切访问                 |
| hasAnyAuthority(String) | 允许具有任一权限的用户进行访问     |
| hasAnyRole(String)      | 允许具有任一角色的用户进行访问     |
| hasAuthority(String)    | 允许具有特定权限的用户进行访问     |
| hasIpAddress(String)    | 允许来自特定 IP 地址的用户进行访问 |
| hasRole(String)         | 允许具有特定角色的用户进行访问     |
| permitAll()             | 无条件允许一切访问                 |



**使用配置方法控制访问权限**

如何让 HTTP 请求与权限控制过程关联起来呢？Spring Security 提供了三种强大的匹配器（Matcher）来实现这一目标，分别是**MVC 匹配器、Ant 匹配器以及正则表达式匹配器**。



- MVC 匹配器

```java
http.authorizeRequests() 
    // zhangsan
    .mvcMatchers("/hello_user").hasRole("USER") 
    // lisi
    .mvcMatchers("/hello_admin").hasRole("ADMIN");
```

如果你使用角色为“USER”的用户“zhangsan”来访问“/hello_admin”端点，那么将会得到如下所示的响应：

```json
{ 
    "status":403, 
    "error":"Forbidden", 
    "message":"Forbidden", 
    "path":"/hello_admin" 
}
```

如果我们想要对某个路径下的所有子路径都指定同样的访问控制，那么只需要在该路径后面添加“*”号即可，示例代码如下所示：

```java
http.authorizeRequests() 
    .mvcMatchers(HttpMethod.GET, "/user/*")
    .authenticated() 
```



- Ant 匹配器

Ant 匹配器的表现形式和使用方法与前面介绍的 MVC 匹配器非常相似，它也提供了如下所示的三个方法来完成请求与 HTTP 端点地址之间的匹配关系：

1. antMatchers(String patterns)
2. antMatchers(HttpMethod method)
3. antMatchers(HttpMethod method, String patterns)



- 正则表达式匹配器

正则表达式匹配器也提供了如下所示的两个配置方法：

1. regexMatchers(HttpMethod method, String regex)
2. regexMatchers(String regex)

使用这一匹配器的主要优势在于它能够**基于复杂的正则表达式**对请求地址进行匹配，这是 MVC 匹配器和 Ant 匹配器无法实现的，你可以看一下如下所示的这段配置代码：

```java
http.authorizeRequests()
   .mvcMatchers("/email/{email:.*(.+@.+\\.com)}")
   .permitAll()
   .anyRequest()
   .denyAll();
```

只有输入的请求是一个合法的邮箱地址才能允许访问。

# 06 | 权限管理：如何剖析 Spring Security 的授权原理？



# 07 | 案例实战：使用 Spring Security 基础功能保护 Web 应用











