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

# 03 | 认证体系：深入理解 Spring Security 用户认证机制？

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

# 06 | 权限管理：剖析 Spring Security 的授权原理？



**Spring Security 授权整体流程**

在 Spring Security 中，实现对所有请求权限控制的配置方法只需要如下所示的一行代码：

```
http.authorizeRequests();
```

在 Spring Security 中，存在一个叫 FilterSecurityInterceptor 的拦截器，它位于整个过滤器链的末端，核心功能是**对权限控制过程进行拦截**，以此判定该请求是否能够访问目标 HTTP 端点。FilterSecurityInterceptor 是整个权限控制的第一个环节，我们把它称为**拦截请求**。

我们对请求进行拦截之后，下一步就要获取该请求的访问资源，以及访问这些资源需要的权限信息。我们把这一步骤称为**获取权限配置**。在 Spring Security 中，存在一个 SecurityMetadataSource 接口，该接口保存着一系列安全元数据的数据源，代表权限配置的抽象。

SecurityMetadataSource 接口定义了一组方法来操作这些权限配置，具体权限配置的表现形式是**ConfigAttribute 接口**。

当我们获取了权限配置信息后，就可以根据这些配置决定 HTTP 请求是否具有访问权限，也就是执行授权决策。Spring Security 专门提供了一个 AccessDecisionManager 接口完成该操作。而在 AccessDecisionManager 接口中，又把具体的决策过程委托给了 AccessDecisionVoter 接口。**AccessDecisionVoter 可以被认为是一种投票器，负责对授权决策进行表决**。

以上三个步骤构成了 Spring Security 的授权整体工作流程，可以用如下所示的时序图表示：

![Drawing 0.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202309092247884.png)

接下来，我们基于这张类图分别对拦截请求、获取权限配置、执行授权决策三个步骤逐一展开讲解。

**拦截请求**

FilterSecurityInterceptor 拦截请求的核心代码在其父类 AbstractSecurityInterceptor 中的 beforeInvocation() 方法中，主流程代码如下：

```java
protected InterceptorStatusToken beforeInvocation(Object object) {
        
	    …
	    //获取 ConfigAttribute 集合
        Collection< ConfigAttribute > attributes = this.obtainSecurityMetadataSource()
                 .getAttributes(object);
 
        …
        //获取认证信息
        Authentication authenticated = authenticateIfRequired();
 
        //执行授权
        try {
             this.accessDecisionManager.decide(authenticated, object, attributes);
        }
        catch (AccessDeniedException accessDeniedException) {
             …
        }
        …
}
```

上述操作从配置好的 SecurityMetadataSource 中获取当前请求所对应的 ConfigAttribute，即权限信息。那么，这个 SecurityMetadataSource 又是怎么来的呢？

**执行授权决策**

执行授权决策的前提是**获取认证信息**，因此，我们在 FilterSecurityInterceptor 的拦截流程中发现了如下一行执行认证操作的代码：

```java
Authentication authenticated = authenticateIfRequired();
```

这里的 authenticateIfRequired() 方法执行认证操作，该方法实现如下：

```java
private Authentication authenticateIfRequired() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        …
 
        authentication = authenticationManager.authenticate(authentication);
	    …
        SecurityContextHolder.getContext().setAuthentication(authentication);
 
        return authentication;
}
```

首先根据上下文对象中是否存在 Authentication 对象来判断当前用户是否已通过认证。如果尚未通过身份认证，则调用 AuthenticationManager 进行认证，并把 Authentication 存储到上下文对象中。

# 07 | 案例实战：使用 Spring Security 基础功能保护 Web 应用

在今天的案例中，我们将构建一个简单但完整的小型 Web 应用程序。当合法用户成功登录系统之后，浏览器会跳转到一个系统主页，并展示一些个人健康档案（HealthRecord）数据。

**案例设计**

本案例的核心功能是**实现自定义的用户认证流程**，所以我们需要构建独立的 UserDetailsService 以及 AuthenticationProvider。

**系统初始化**

这部分工作涉及**领域对象的定义、数据库初始化脚本的整理以及相关依赖组件的引入**。

针对领域对象，我们重点来看如下所示的 User 类定义：

```java
@Entity
public class User {
 
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;
 
    private String username;
    private String password;
 
    @Enumerated(EnumType.STRING)
    private PasswordEncoderType passwordEncoderType;
 
    @OneToMany(mappedBy = "user", fetch = FetchType.EAGER)
	private List<Authority> authorities;
	…
}
```

```java
public enum PasswordEncoderType {
    BCRYPT, SCRYPT
}
```

可以看到，这里除了指定主键 id、用户名 username 和密码 password 之外，还包含了一个**加密算法枚举值 EncryptionAlgorithm**。在案例系统中，我们将提供 BCryptPasswordEncoder 和 SCryptPasswordEncoder 这两种可用的密码解密器，你可以通过该枚举值进行设置。

同时，我们在 User 类中还发现了一个 Authority 列表。显然，这个列表用来指定该 User 所具备的权限信息。Authority 类的定义如下所示：

```java
@Entity
public class Authority {
 
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;
 
    private String name;
 
    @JoinColumn(name = "user")
    @ManyToOne
	private User user;
	…
}
```

通过定义不难看出 User 和 Authority 之间是**一对多**的关系。

基于 User 和 Authority 领域对象，我们也给出创建数据库表的 SQL 定义，如下所示：

```sql
CREATE TABLE IF NOT EXISTS `spring_security`.`user` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(45) NOT NULL,
  `password` TEXT NOT NULL,
  `password_encoder_type` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`));
CREATE TABLE IF NOT EXISTS `spring_security`.`authority` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `user` INT NOT NULL,
  PRIMARY KEY (`id`));
```

在运行系统之前，我们同样也需要初始化数据，对应脚本如下所示：

```sql
INSERT IGNORE INTO `spring_security`.`user` (`id`, `username`, `password`, `password_encoder_type`) VALUES ('1', 'jianxiang', '$2a$10$xn3LI/AjqicFYZFruSwve.681477XaVNaUQbr1gioaWPn4t1KsnmG', 'BCRYPT');
INSERT IGNORE INTO `spring_security`.`authority` (`id`, `name`, `user`) VALUES ('1', 'READ', '1');
INSERT IGNORE INTO `spring_security`.`authority` (`id`, `name`, `user`) VALUES ('2', 'WRITE', '1');
INSERT IGNORE INTO `spring_security`.`health_record` (`id`, `username`, `name`, `value`) VALUES ('1', 'jianxiang', 'weight', '70');
INSERT IGNORE INTO `spring_security`.`health_record` (`id`, `username`, `name`, `value`) VALUES ('2', 'jianxiang', 'height', '177');
INSERT IGNORE INTO `spring_security`.`health_record` (`id`, `username`, `name`, `value`) VALUES ('3', 'jianxiang', 'bloodpressure', '70');
INSERT IGNORE INTO `spring_security`.`health_record` (`id`, `username`, `name`, `value`) VALUES ('4', 'jianxiang', 'pulse', '80');
```

这里初始化了一个用户名为 “jianxiang”的用户，同时指定了它的密码为“12345”，加密算法为“BCRYPT”。

现在，领域对象和数据层面的初始化工作已经完成了，接下来我们需要在代码工程的 pom 文件中添加如下所示的 Maven 依赖：

```xml
<dependencies>	    
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-thymeleaf</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
 
        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.security</groupId>
            <artifactId>spring-security-test</artifactId>
            <scope>test</scope>
        </dependency>
</dependencies>
```

**实现用户管理**

实现自定义用户认证的过程通常涉及两大部分内容，一方面需要使用 User 和 Authority 对象来完成**定制化的用户管理**，另一方面需要把这个定制化的用户管理**嵌入整个用户认证流程中**。

如果你想实现自定义的用户信息，扩展 UserDetails 这个接口即可。实现方式如下所示：

```java
public class CustomUserDetails implements UserDetails {
 
    private final User user;
 
    public CustomUserDetails(User user) {
        this.user = user;
    }
 
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return user.getAuthorities().stream()
                   .map(a -> new SimpleGrantedAuthority(a.getName()))
                   .collect(Collectors.toList());
    }
 
    @Override
    public String getPassword() {
        return user.getPassword();
    }
 
    @Override
    public String getUsername() {
        return user.getUsername();
    }
 
    @Override
    public boolean isAccountNonExpired() {
        return true;
    }
 
    @Override
    public boolean isAccountNonLocked() {
        return true;
    }
 
    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }
 
    @Override
    public boolean isEnabled() {
        return true;
    }
 
    public final User getUser() {
        return user;
    }
}
```

请注意，这里的 getAuthorities() 方法中，我们将 User 对象中的 Authority 列表转换为了 Spring Security 中代表用户权限的 **SimpleGrantedAuthority 列表**。

所有的自定义用户信息和权限信息都是维护在数据库中的，所以为了获取这些信息，我们需要创建数据访问层组件，这个组件就是 UserRepository，定义如下：

```java
public interface UserRepository extends JpaRepository<User, Integer> {
 
    Optional<User> findUserByUsername(String username);
}
```

现在，我们已经能够在数据库中维护自定义用户信息，也能够根据这些用户信息获取到 UserDetails 对象，那么接下来要做的事情就是扩展 UserDetailsService。自定义 CustomUserDetailsService 实现如下所示：

```java
@Service
public class CustomUserDetailsService implements UserDetailsService {
 
    @Autowired
    private UserRepository userRepository;
 
    @Override
    public CustomUserDetails loadUserByUsername(String username) {
        Supplier<UsernameNotFoundException> s =
                () -> new UsernameNotFoundException("Username" + username + "is invalid!");
 
        User u = userRepository.findUserByUsername(username).orElseThrow(s);
 
        return new CustomUserDetails(u);
    }
}
```

这里我们通过 UserRepository 查询数据库来获取 CustomUserDetails 信息。

**实现认证流程**

实现自定义认证流程要做的也是实现 AuthenticationProvider 中的这两个方法，而认证过程势必要借助于前面介绍的 CustomUserDetailsService。

我们先来看一下 AuthenticationProvider 接口的实现类 AuthenticationProviderService，如下所示：

```java
@Service
public class AuthenticationProviderService implements AuthenticationProvider {
 
    @Autowired
    private CustomUserDetailsService userDetailsService;
 
    @Autowired
    private BCryptPasswordEncoder bCryptPasswordEncoder;
 
    @Autowired
    private SCryptPasswordEncoder sCryptPasswordEncoder;
 
    @Override
    public Authentication authenticate(Authentication authentication) throws AuthenticationException {
        String username = authentication.getName();
        String password = authentication.getCredentials().toString();
 
        //根据用户名从数据库中获取 CustomUserDetails
        CustomUserDetails user = userDetailsService.loadUserByUsername(username);
 
        //根据所配置的密码加密算法分别验证用户密码
        switch (user.getUser().getPasswordEncoderType()) {
            case BCRYPT:
                return checkPassword(user, password, bCryptPasswordEncoder);
            case SCRYPT:
                return checkPassword(user, password, sCryptPasswordEncoder);
        }
 
        throw new  BadCredentialsException("Bad credentials");
    }
 
    @Override
    public boolean supports(Class<?> aClass) {
        return UsernamePasswordAuthenticationToken.class.isAssignableFrom(aClass);
    }
 
    private Authentication checkPassword(CustomUserDetails user, String rawPassword, PasswordEncoder encoder) {
        if (encoder.matches(rawPassword, user.getPassword())) {
            return new UsernamePasswordAuthenticationToken(user.getUsername(), user.getPassword(), user.getAuthorities());
        } else {
            throw new BadCredentialsException("Bad credentials");
        }
    }
}
```

我们首先通过 CustomUserDetailsService 从数据库中获取用户信息并构造成 CustomUserDetails 对象。然后，根据指定的密码加密器对用户密码进行验证，如果验证通过则构建一个 UsernamePasswordAuthenticationToken 对象并返回，反之直接抛出 BadCredentialsException 异常。而在 supports() 方法中指定的就是这个目标 UsernamePasswordAuthenticationToken 对象。

**安全配置**

最后，我们要做的就是通过 Spring Security 提供的配置体系将前面介绍的所有内容串联起来，如下所示：

```java
@Configuration
public class SecurityConfig extends WebSecurityConfigurerAdapter {
 
    @Autowired
    private AuthenticationProviderService authenticationProvider;
 
    @Bean
    public BCryptPasswordEncoder bCryptPasswordEncoder() {
        return new BCryptPasswordEncoder();
    }
 
    @Bean
    public SCryptPasswordEncoder sCryptPasswordEncoder() {
        return new SCryptPasswordEncoder();
    }
 
    @Override
    protected void configure(AuthenticationManagerBuilder auth) {
        auth.authenticationProvider(authenticationProvider);
    }
 
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http.formLogin()
            .defaultSuccessUrl("/healthrecord", true);
        http.authorizeRequests().anyRequest().authenticated();
    }
}
```

这里注入了已经构建完成的 AuthenticationProviderService，并初始化了两个密码加密器 BCryptPasswordEncoder 和 SCryptPasswordEncoder。最后，我们覆写了 WebSecurityConfigurerAdapter 配置适配器类中的 configure() 方法，并指定用户登录成功后将跳转到"/healthrecord"路径所指定的页面。

对应的，我们需要构建如下所示的 HealthRecordController 类来指定"/healthrecord"路径，并展示业务数据的获取过程，如下所示：

```java
@Controller
public class HealthRecordController {
    @Autowired
    private HealthRecordService healthRecordService;
    
    @GetMapping("/main")
    public String main(Authentication a, Model model) {
    	String userName = a.getName();
        model.addAttribute("username", userName);
        model.addAttribute("healthRecords", healthRecordService.getHealthRecordsByUsername(userName));
        return "main.html";
    }
}
```

这里所指定的 health_record.html 位于 resources/templates 目录下，该页面基于 thymeleaf 模板引擎构建，如下所示：

```html
<!DOCTYPE html>
<html lang="en" xmlns:th="http://www.thymeleaf.org">
    <head>
        <meta charset="UTF-8">
        <title>健康档案</title>
    </head>
    <body>
        <h2 th:text="'登录用户：' + ${username}" />
        <p><a href="/logout">退出登录</a></p>
        <h2>个人健康档案:</h2>
        <table>
            <thead>
            <tr>
                <th> 健康指标名称 </th>
                <th> 健康指标值 </th>
            </tr>
            </thead>
            <tbody>
            <tr th:if="${healthRecords.empty}">
                <td colspan="2"> 无健康指标 </td>
            </tr>
            <tr th:each="healthRecord : ${healthRecords}">
                <td><span th:text="${healthRecord.name}"> 健康指标名称 </span></td>
                <td><span th:text="${healthRecord.value}"> 健康指标值 </span></td>
            </tr>
            </tbody>
        </table>
    </body>
</html>
```

这里我们从 Model 对象中获取了认证用户信息以及健康档案信息，并渲染在页面上。

**案例演示**

现在，让我们启动 Spring Boot 应用程序，并访问[http://localhost:8080](http://localhost:8080/?fileGuid=xxQTRXtVcqtHK6j8)端点。因为访问系统的任何端点都需要认证，所以 Spring Security 会自动跳转到如下所示的登录界面：

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023image-20230911113950836.png)

我们分别输入用户名“studeyang”和密码“12345”，系统就会跳转到健康档案主页：

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023image-20230911114211416.png)

在这个主页中，我们正确获取了登录用户的用户名，并展示了个人健康档案信息。这个结果也证实了自定义用户认证体系的正确性。

# ==高级主题篇==

# 08 | 管道过滤：基于 Spring Security 的过滤器扩展安全性

**Spring Security 过滤器架构**

Spring Security 中的过滤器架构是**基于 Servlet**构建的，所以我们先从 Servlet 中的过滤器开始说起。



- Servlet 与管道-过滤器模式

在 Servlet 中，代表过滤器的 Filter 接口定义如下：

```java
public interface Filter {
 
    public void init(FilterConfig filterConfig) throws ServletException;

    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException;
 
    public void destroy();
}
```

一个过滤器组件所包含的业务逻辑应该位于 doFilter() 方法中，该方法带有三个参数，分别是**ServletRequest、ServletResponse 和 FilterChain**。

1. ServletRequest：表示 HTTP 请求，我们使用该对象获取有关请求的详细信息。
2. ServletResponse：表示 HTTP 响应，我们使用该对象构建响应结果，然后将其发送回客户端或沿着过滤器链向后传递。
3. FilterChain：表示过滤器链，我们使用该对象将请求转发到链中的下一个过滤器。



- Spring Security 中的过滤器链

在 Spring Security 中，其核心流程的执行也是依赖于一组过滤器，这些过滤器在框架启动后会自动进行初始化，如图所示：

![Drawing 1.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202309102237068.png)

上图中的 BasicAuthenticationFilter 用来验证用户的身份凭证；而 UsernamePasswordAuthenticationFilter 会检查输入的用户名和密码，并根据认证结果决定是否将这一结果传递给下一个过滤器。

**整个 Spring Security 过滤器链的末端是一个 FilterSecurityInterceptor，它本质上也是一个 Filter**。但与其他用于完成认证操作的 Filter 不同，它的核心功能是**实现权限控制**，也就是用来判定该请求是否能够访问目标 HTTP 端点。FilterSecurityInterceptor 对于权限控制的粒度可以到方法级别，能够满足前面提到的精细化访问控制。



**实现自定义过滤器**

- 开发过滤器

我们想象这样一种场景，业务上我们需要根据客户端请求头中是否包含某一个特定的标志位，来决定请求是否有效。如图所示：

![Drawing 2.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202309102242867.png)

这在现实开发过程中也是一种常见的应用场景，可以实现定制化的安全性控制。针对这种应用场景，我们可以实现如下所示的 RequestValidationFilter 过滤器：

```java
public class RequestValidationFilter implements Filter {
 
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain filterChain) throws IOException, ServletException {
        HttpServletRequest httpRequest = (HttpServletRequest) request;
        HttpServletResponse httpResponse = (HttpServletResponse) response;
        String requestId = httpRequest.getHeader("SecurityFlag");
        if (requestId == null || requestId.isBlank()) {
            httpResponse.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }
 
        filterChain.doFilter(request, response);
    }
}
```



- 配置过滤器

如果我们想要实现定制化的安全性控制策略，就可以实现类似前面介绍的 RequestValidationFilter 这样的过滤器，并放置在 BasicAuthenticationFilter 前。这样，在执行用户认证之前，我们就可以排除掉一批无效请求，效果如下所示：

![Drawing 3.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202309102244500.png)

在 Spring Security 中，提供了一组可以往过滤器链中添加过滤器的工具方法，包括 addFilterBefore()、addFilterAfter()、addFilterAt() 以及 addFilter() 等，它们都定义在 HttpSecurity 类中。这些方法的含义都很明确，使用起来也很简单，例如，想要实现如上图所示的效果，我们可以编写这样的代码：

```java
@Override
protected void configure(HttpSecurity http) throws Exception {
        http.addFilterBefore(
                new RequestValidationFilter(),
                BasicAuthenticationFilter.class)
            .authorizeRequests()
                .anyRequest()
                .permitAll();
}
```



**Spring Security 中的过滤器**

下表列举了 Spring Security 中常用的过滤器名称、功能以及它们的顺序关系：

![image.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202309102245242.png)

# 09 | 攻击应对：如何实现 CSRF 保护和跨域 CORS？

今天我们就来讨论在日常开发过程中常见的两个安全性话题，即 CSRF 和 CORS。

**使用 Spring Security 提供 CSRF 保护**

CSRF 的全称是 Cross-Site Request Forgery，翻译成中文就是**跨站请求伪造**。那么，究竟什么是跨站请求伪造？



- 什么是 CSRF？

你可以将 CSRF 理解为一种攻击手段，即攻击者盗用了你的身份，然后以你的名义向第三方网站发送恶意请求。我们可以使用如下所示的流程图来描述 CSRF：

![Drawing 0.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202309122252508.png)

具体流程如下：

1. 用户浏览并登录信任的网站 A，通过用户认证后，会在浏览器中生成针对 A 网站的 Cookie；
2. 用户在没有退出网站 A 的情况下访问网站 B，然后网站 B 向网站 A 发起一个请求；
3. 用户浏览器根据网站 B 的请求，携带 Cookie 访问网站 A；
4. 由于浏览器会自动带上用户的 Cookie，所以网站 A 接收到请求之后会根据用户具备的权限进行访问控制，这样相当于用户本身在访问网站 A，从而网站 B 就达到了模拟用户访问网站 A 的操作过程。

从应用程序开发的角度来讲，CSRF 就是系统的一个安全漏洞，这种安全漏洞也在 Web 开发中广泛存在。

进行 CSRF 保护的基本思想就是**为系统中的每一个连接请求加上一个随机值**，我们称之为 csrf_token。这样，当用户向网站 A 发送请求时，网站 A 在生成的 Cookie 中就会设置一个 csrf_token 值。

在浏览器发送提交的表单数据的请求中也有一个隐藏的 csrf_token 值，这样网站 A 接收到请求后，一方面从 Cookie 中提取出 csrf_token，另一方面也从表单提交的数据中获取隐藏的 csrf_token。将两者进行比对，如果不一致就代表这就是一个伪造的请求。



- 使用 CsrfFilter

在 Spring Security 中，专门提供了一个 CsrfFilter 来实现对 CSRF 的保护。CsrfFilter 拦截请求，并允许使用 GET、HEAD、TRACE 和 OPTIONS 等 HTTP 方法的请求。

而针对 PUT、POST、DELETE 等可能会修改数据的其他请求，CsrfFilter 则希望接**收包含 csrf_token 的消息头**。如果这个消息头不存在或包含不正确的 csrf_token 值，应用程序将拒绝该请求并将响应的状态设置为 403。

```java
@Override
protected void doFilterInternal(HttpServletRequest request,
             HttpServletResponse response, FilterChain filterChain)
                     throws ServletException, IOException {
        request.setAttribute(HttpServletResponse.class.getName(), response);
 
        //从 CsrfTokenRepository 中获取 CsrfToken
        CsrfToken csrfToken = this.tokenRepository.loadToken(request);
        final boolean missingToken = csrfToken == null;
 
        //如果找不到 CsrfToken 就生成一个并保存到 CsrfTokenRepository 中
        if (missingToken) {
             csrfToken = this.tokenRepository.generateToken(request);
             this.tokenRepository.saveToken(csrfToken, request, response);
        }
 
        //在请求中添加 CsrfToken
        request.setAttribute(CsrfToken.class.getName(), csrfToken);
        request.setAttribute(csrfToken.getParameterName(), csrfToken);
 
        if (!this.requireCsrfProtectionMatcher.matches(request)) {
             filterChain.doFilter(request, response);
             return;
        }
 
        //从请求中获取 CsrfToken
        String actualToken = request.getHeader(csrfToken.getHeaderName());
        if (actualToken == null) {
             actualToken = request.getParameter(csrfToken.getParameterName());
        }
 
        //如果请求所携带的 CsrfToken 与从 Repository 中获取的不同，则抛出异常
        if (!csrfToken.getToken().equals(actualToken)) {
             if (this.logger.isDebugEnabled()) {
                 this.logger.debug("Invalid CSRF token found for "
                         + UrlUtils.buildFullRequestUrl(request));
             }
             if (missingToken) {
                 this.accessDeniedHandler.handle(request, response,
                         new MissingCsrfTokenException(actualToken));
             }
             else {
                 this.accessDeniedHandler.handle(request, response,
                         new InvalidCsrfTokenException(csrfToken, actualToken));
             }
             return;
        }
        
        //正常情况下继续执行过滤器链的后续流程
        filterChain.doFilter(request, response);
}
```

在 Spring Security 中，专门定义了一个 CsrfToken 接口来约定它的格式：

```java
public interface CsrfToken extends Serializable {
 
    //获取消息头名称
    String getHeaderName();
 
    //获取应该包含 Token 的参数名称
    String getParameterName();
	 
	//获取具体的 Token 值
    String getToken();
}
```

在 Spring Security 中，CsrfTokenRepository 接口具有一批实现类，除了 CookieCsrfTokenRepository，还有 HttpSessionCsrfTokenRepository 等。CookieCsrfTokenRepository 的 saveToken() 方法也比较简单，就是基于 Cookie 对象进行了 CsrfToken 的设置工作，如下所示：

```java
@Override
public void saveToken(CsrfToken token, HttpServletRequest request,
             HttpServletResponse response) {
        String tokenValue = token == null ? "" : token.getToken();
        Cookie cookie = new Cookie(this.cookieName, tokenValue);
        cookie.setSecure(request.isSecure());
        if (this.cookiePath != null && !this.cookiePath.isEmpty()) {
                 cookie.setPath(this.cookiePath);
        } else {
                 cookie.setPath(this.getRequestContext(request));
        }
        if (token == null) {
             cookie.setMaxAge(0);
        }
        else {
             cookie.setMaxAge(-1);
        }
        cookie.setHttpOnly(cookieHttpOnly);
        if (this.cookieDomain != null && !this.cookieDomain.isEmpty()) {
             cookie.setDomain(this.cookieDomain);
        }
 
        response.addCookie(cookie);
}
```

从 Spring Security 4.0 开始，默认启用 CSRF 保护，以防止 CSRF 攻击应用程序。Spring Security CSRF 会针对 POST、PUT 和 DELETE 方法进行防护。因此，对于开发人员而言，实际上你并不需要做什么额外工作就能使用这个功能了。当然，如果你不想使用这个功能，也可以通过如下配置方法进行关闭：

```java
http.csrf().disable();
```



- 定制化 CSRF 保护

如果你想获取 HTTP 请求中的 CsrfToken，只需要使用如下所示的代码：

```java
CsrfToken token = (CsrfToken)request.getAttribute("_csrf");
```

如果你不想使用 Spring Security 内置的存储方式，而是想基于自身需求把 CsrfToken 存储起来，要做的事情就是**实现 CsrfTokenRepository 接口**。这里我们尝试把 CsrfToken 保存到关系型数据库中，所以可以通过扩展 Spring Data 中的 JpaRepository 来定义一个 JpaTokenRepository，如下所示：

```java
public interface JpaTokenRepository extends JpaRepository<Token, Integer> {
 
    Optional<Token> findTokenByIdentifier(String identifier);
}
```

然后，我们基于 JpaTokenRepository 来构建一个 DatabaseCsrfTokenRepository，如下所示：

```java
public class DatabaseCsrfTokenRepository
        implements CsrfTokenRepository {
 
    @Autowired
    private JpaTokenRepository jpaTokenRepository;
 
    @Override
    public CsrfToken generateToken(HttpServletRequest httpServletRequest) {
        String uuid = UUID.randomUUID().toString();
        return new DefaultCsrfToken("X-CSRF-TOKEN", "_csrf", uuid);
    }
 
    @Override
    public void saveToken(CsrfToken csrfToken, HttpServletRequest httpServletRequest, HttpServletResponse httpServletResponse) {
        String identifier = httpServletRequest.getHeader("X-IDENTIFIER");
        Optional<Token> existingToken = jpaTokenRepository.findTokenByIdentifier(identifier);
 
        if (existingToken.isPresent()) {
            Token token = existingToken.get();
            token.setToken(csrfToken.getToken());
        } else {
            Token token = new Token();
            token.setToken(csrfToken.getToken());
            token.setIdentifier(identifier);
            jpaTokenRepository.save(token);
        }
    }
 
    @Override
    public CsrfToken loadToken(HttpServletRequest httpServletRequest) {
        String identifier = httpServletRequest.getHeader("X-IDENTIFIER");
        Optional<Token> existingToken = jpaTokenRepository.findTokenByIdentifier(identifier);
 
        if (existingToken.isPresent()) {
            Token token = existingToken.get();
            return new DefaultCsrfToken("X-CSRF-TOKEN", "_csrf", token.getToken());
        }
 
        return null;
    }
}
```

这里借助了 HTTP 请求中的“X-IDENTIFIER”请求头来确定请求的唯一标识，从而将这一唯一标识与特定的 CsrfToken 关联起来。然后我们使用 JpaTokenRepository 完成了针对关系型数据库的持久化工作。

最后，想要上述代码生效，我们需要通过配置方法完成对 CSRF 的设置，如下所示，这里直接通过 csrfTokenRepository 方法集成了自定义的 DatabaseCsrfTokenRepository：

```java
@Override
protected void configure(HttpSecurity http) throws Exception {
        http.csrf(c -> {
            c.csrfTokenRepository(databaseCsrfTokenRepository());
        });
        …
}
```



**使用 Spring Security 实现 CORS**

我们继续来看 Web 应用程序开发过程中另一个常见的需求——CORS，即跨域资源共享（Cross-Origin Resource Sharing）。



- 什么是 CORS？

例如，当我们从“test.com”这个域名发起请求时，浏览器为了一定的安全因素考虑，并不会允许请求去访问“api.test.com”这个域名，因为请求已经跨越了两个域名。

从原理上讲，实际就是浏览器在 HTTP 请求的消息头部分新增一些字段，如下所示：

```
//浏览器自己设置的请求域名
Origin     
//浏览器告诉服务器请求需要用到哪些 HTTP 方法
Access-Control-Request-Method
//浏览器告诉服务器请求需要用到哪些 HTTP 消息头
Access-Control-Request-Headers
```

当浏览器进行跨域请求时会和服务器端进行一次的握手协议，从响应结果中可以获取如下信息：

```
//指定哪些客户端的域名允许访问这个资源
Access-Control-Allow-Origin 
//服务器支持的 HTTP 方法
Access-Control-Allow-Methods 
//需要在正式请求中加入的 HTTP 消息头
Access-Control-Allow-Headers 
```

因此，实现 CORS 的关键是**服务器**。只要服务器**合理设置这些响应结果中的消息头**，就相当于实现了对 CORS 的支持，从而支持跨源通信。



- 使用 CorsFilter

在 Spring 中存在一个 CorsFilter 过滤器，不过这个过滤器并不是 Spring Security 提供的，而是来自**Spring Web MVC**。在 CorsFilter 这个过滤器中，首先应该判断来自客户端的请求是不是一个跨域请求，然后根据 CORS 配置来判断该请求是否合法，如下所示：

```java
@Override
protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
             FilterChain filterChain) throws ServletException, IOException {
 
        if (CorsUtils.isCorsRequest(request)) {
             CorsConfiguration corsConfiguration = this.configSource.getCorsConfiguration(request);
             if (corsConfiguration != null) {
                 boolean isValid = this.processor.processRequest(corsConfiguration, request, response);
                 if (!isValid || CorsUtils.isPreFlightRequest(request)) {
                     return;
                 }
             }
        }
 
        filterChain.doFilter(request, response);
}
```

Spring Security 也在 HttpSecurity 工具类通过提供了 cors() 方法来创建 CorsConfiguration，使用方式如下所示：

```java
@Override
protected void configure(HttpSecurity http) throws Exception {
        http.cors(c -> {
            CorsConfigurationSource source = request -> {
                CorsConfiguration config = new CorsConfiguration();
                config.setAllowedOrigins(Arrays.asList("*"));
                config.setAllowedMethods(Arrays.asList("*"));
                return config;
            };
            c.configurationSource(source);
        });
        …
}
```

我们可以通过 setAllowedOrigins() 和 setAllowedMethods() 方法实现对 HTTP 响应消息头的设置。**这里将它们都设置成“\*”，意味着所有请求都可以进行跨域访问**。你也可以根据需要设置特定的域名和 HTTP 方法。



- 使用 @CrossOrigin 注解

通过 CorsFilter，我们实现了全局级别的跨域设置。但有时候，我们可能只需要针对某些请求实现这一功能，通过 Spring Security 也是可以做到这一点的，我们可以在特定的 HTTP 端点上使用如下所示的 @CrossOrigin 注解：

```java
@Controller
public class TestController {
        
    @PostMapping("/hello")
	@CrossOrigin("http://api.test.com:8080")
    public String hello() {
        return "hello";
    }
}
```

# 10 | 全局方法：如何确保方法级别的安全访问？

**全局方法安全机制**

围绕某个业务的实现方法所开展的安全控制，这种安全控制也被称为全局方法安全（Global Method Security）机制。

全局方法安全机制能为我们带来什么价值呢？通常包括两个方面，即方法调用授权和方法调用过滤。

方法调用授权的含义很明确，我们可以用它来确定某个请求是否具有调用方法的权限。如果是在方法调用之前进行授权管理，就是预授权（PreAuthorization）；如果是在方法执行完成后来确定是否可以访问方法返回的结果，一般称之为后授权（PostAuthorization）。

方法调用过滤本质上类似于过滤器机制，也可以分为 PreFilter 和 PostFilter 两大类。其中预过滤（PreFilter）用来对该方法的参数进行过滤，从而获取其参数接收的内容，而后过滤（PostFilter）则用来判断调用者可以在方法执行后从方法返回结果中接收的内容。

默认情况下 Spring Security 并没有启用全局方法安全机制。因此，想要启用这个功能，我们需要使用**@EnableGlobalMethodSecurity 注解**。

```java
@Configuration
@EnableGlobalMethodSecurity(prePostEnabled = true)
public class SecurityConfig {}
```

这里我们设置了“prePostEnabled”为 true，意味着我们启用了 Pre/PostAuthorization 注解。

**使用注解实现方法级别授权**

针对方法级别授权，Spring Security 提供了 @PreAuthorize 和 @PostAuthorize 这两个注解，分别用于预授权和后授权。



- @PreAuthorize 注解

假设在 OrderService 中存在一个 getOrderByUser(String user) 方法，而出于系统安全性的考虑，我们希望用户只能获取自己创建的订单信息，也就是说我们需要校验通过该方法传入的“user”参数是否为当前认证的合法用户。这种场景下，我们就可以使用 @PreAuthorize 注解：

```java
@PreAuthorize("#name == authentication.principal.username")
public List<Order> getOrderByUser(String user) {
    …
}
```

这里我们将输入的“user”参数与通过 SpEL 表达式从安全上下文中获取的“authentication.principal.username”进行比对，如果相同就执行正确的方法逻辑，反之将直接抛出异常。



- @PostAuthorize 注解

有时我们允许调用者正确调用方法，但希望该调用者不接受返回的响应结果。比如在那些访问第三方外部系统的应用中，我们并不能完全相信返回数据的正确性，也有对调用的响应结果进行限制的需求，@PostAuthorize 注解为我们实现这类需求提供了很好的解决方案。

假设我们存在如下所示的一个 Author 对象，保存着该作者的姓名和创作的图书作品：

```java
public class Author {
    private String name;
    private List<String> books;
}
```

我们假设系统中保存着两个 Author 对象，现在，我们有这样一个根据姓名获取 Author 对象的查询方法：

```java
Map<String, Author> authors =
    Map.of(
        "AuthorA", new Author("AuthorA ",List.of("BookA1", “BookA2)),
        "AuthorB", new Author("AuthorB", List.of("BookB1"))
);

@PostAuthorize("returnObject.books.contains('BookA2')")
public Author getAuthorByNames(String name) {
    return authors.get(name);
}
```

在这个示例中，借助于代表返回值的“returnObject”对象，如果我们使用创作了“BookA2”的“AuthorA”来调用这个方法，就能正常返回数据；如果使用“AuthorB”，就会报 403 异常。



**使用注解实现方法级别过滤**

- @PreFilter 注解

使用预过滤，方法调用是一定会执行的，但只有那些符合过滤规则的数据才会正常传递到调用链路的下一层组件。

我们设计一个新的数据模型，并构建如下所示的 Controller 层方法：

```java
@Autowired
private ProductService productService;
 
@GetMapping("/sell")
public List<Product> sellProduct() {
    List<Product> products = new ArrayList<>();
 
    products.add(new Product("p1", "jianxiang1"));
    products.add(new Product("p2", "jianxiang2"));
    products.add(new Product("p3", "jianxiang3"));
 
    return productService.sellProducts(products);
}
```

然后，我们来到 Service 层组件，实现如下所示的方法：

```java
@PreFilter("filterObject.name == authentication.name")
public List<Product> sellProducts(List<Product> products) {
    return products;
}
```

这里通过使用“filterObject”对象，我们可以获取输入的 Product 数据，然后将“filterObject.name”字段与从安全上下文中获取的“authentication.name”进行比对，就能将那些不属于当前认证用户的数据进行过滤。



- @PostFilter 注解

如果使用后过滤，方法调用也是一定会执行的，但只有那些符合过滤规则的数据才会正常返回。

@PostFilter 注解的使用方法也很简单，示例如下：

```java
@PostFilter("filterObject.name == authentication.principal.username")
public List<Product> findProducts() {
    List<Product> products = new ArrayList<>();
 
    products.add(new Product("p1", "jianxiang1"));
    products.add(new Product("p2", "jianxiang2"));
    products.add(new Product("p3", "jianxiang3"));
 
    return products;
}
```

我们指定了过滤的规则为"filterObject.name == authentication.principal.username"，也就是说该方法只会返回那些属于当前认证用户的数据，其他用户的数据会被自动过滤。

# 11 | 案例实战：使用 Spring Security 高级主题保护 Web 应用











# ==OAuth2 与微服务篇==



# ==框架扩展篇==

