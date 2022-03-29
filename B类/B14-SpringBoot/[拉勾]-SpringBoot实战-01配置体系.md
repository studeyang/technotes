# 开篇词

Spring Boot 框架使配置变简单、使编程变简单、使部署变简单、使监控变简单。总结来说有如下特点。

- 看上去简单，实则复杂

Spring Boot 提供了很多隐式的功能，比如自动配置，它将系统开发的复杂度隐藏得很深。

- 技术体系和组件众多

Spring Boot 提供了一大批功能组件，这些功能组件构成了庞大的技术体系。

- 框架集成的“坑”不少

Spring Boot 是一个集成性的框架，内部整合了市面上很多开源框架。

Web 应用程序总体可以拆分为下图的维度。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210330224842.png" alt="image-20210330224841931" style="zoom:50%;" />

可以从下面8个部分进行学习。

- 第 1 部分（01~02），开启 Spring Boot 框架的学习之旅
- 第 2 部分（03~05），使用 Spring Boot 构建多维度配置层
- 第 3 部分（06~10），使用 Spring Boot 构建数据访问层
- 第 4 部分（11~13），使用 Spring Boot 构建 Web 服务层
- 第 5 部分（14~16），使用 Spring Boot 构建消息通信层
- 第 6 部分（17~19），使用 Spring Boot 构建系统安全层
- 第 7 部分（20~22），使用 Spring Boot 构建系统监控层
- 第 8 部分（23~24），测试 Spring Boot 应用程序

# 开启学习之旅

# 01 | Spring 家族的技术体系

**Spring 家族技术生态全景图**

我们访问 Spring 的官方网站（https://spring.io/）来对这个框架做宏观的了解。在 Spring 的主页中，展示了下面这张图：

![image-20210330230706127](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210330230706.png)

这里罗列了 Spring 框架的七大核心技术体系，分别是微服务架构、响应式编程、云原生、Web 应用、Serverless 架构、事件驱动以及批处理。

这些技术体系各有其应用场景。

例如，如果我们想要实现日常报表等轻量级的批处理任务，而又不想引入 Hadoop 这套庞大的离线处理平台时，使用基于 Spring Batch 的批处理框架是一个不错的选择。

再比方说，如果想要实现与 Kafka、RabbitMQ 等各种主流消息中间件之间的集成，但又希望开发人员不需要了解这些中间件在使用上的差别，那么使用基于 Spring Cloud Stream 的事件驱动架构是你的首选。

**Spring Framework 的整体架构**

我们现在能看到的 Spring 家族技术体系都是在 Spring Framework 基础上逐步演进而来的。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210330231153.png" alt="image-20210330231153856" style="zoom:50%;" />

Spring 从诞生之初就被认为是一种容器，上图中的“核心容器”部分就包含了一个容器所应该具备的核心功能。

最上面的两个框就是构建应用程序所需要的最核心的两大功能组件，也是我们日常开发中最常用的组件，即数据访问和 Web 服务。这两大部分功能组件中包含的内容非常多，而且充分体现了 Spring Framework 的集成性，也就是说，框架内部整合了业界主流的数据库驱动、消息中间件、ORM 框架等各种工具，开发人员可以根据需要灵活地替换和调整自己想要使用的工具。

从开发语言上讲，虽然 Spring 应用最广泛的是在 Java EE 领域，但在当前的版本中，也支持 Kotlin、Groovy 以及各种动态开发语言。

# 02 | 一个 Spring Web 应用程序

**一个 Spring Web 应用程序**

一个典型的 Web 应用程序的项目结构如下图所示：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210401222615.png" alt="image-20210401222615599" style="zoom:50%;" />

1. 包依赖

Spring Boot 提供了一系列 starter 工程来简化各种组件之间的依赖关系。以开发 Web 服务为例，我们需要引入 spring-boot-starter-web 这个工程，而这个工程中并没有具体的代码，只是包含了一些 pom 依赖，如下所示：

- org.springframework.boot:spring-boot-starter
- org.springframework.boot:spring-boot-starter-tomcat
- org.springframework.boot:spring-boot-starter-validation
- com.fasterxml.jackson.core:jackson-databind
- org.springframework:spring-web
- org.springframework:spring-webmvc

2. 启动类

```java
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class HelloApplication {

    public static void main(String[] args) {
        SpringApplication.run(HelloApplication.class, args);
    }
}
```

@SpringBootApplication 注解一方面会启动整个 Spring 容器，另一方面也会自动扫描代码包结构下的 @Component、@Service、@Repository、@Controller 等注解并把这些注解对应的类转化为 Bean 对象全部加载到 Spring 容器中。

3. 控制器类

```java
@RestController
@RequestMapping(value = "accounts")
public class AccountController {
 
    @Autowired
    private AccountService accountService;
 
    @GetMapping(value = "/{accountId}")
    public Account getAccountById(@PathVariable("accountId") Long accountId) {
        Account account = accountService.getAccountById(accountId);
        return account;
    }
}
```

@RestController 注解是传统 Spring MVC 中所提供的 @Controller 注解的升级版，相当于就是 @Controller 和 @ResponseEntity 注解的结合体，会自动使用 JSON 实现序列化/反序列化操作。

**案例驱动：SpringCSS**

这里的 CSS 是对客户服务系统 Customer Service System 的简称。客服服务是电商、健康类业务场景中非常常见的一种业务场景，我们将通过构建一个精简但又完整的系统来展示 Spring Boot 相关设计理念和各项技术组件。

在 SpringCSS 中，存在一个 customer-service，这是一个 Spring Boot 应用程序，也是整个案例系统中的主体服务。

customer-service 一般会与用户服务 account-service 进行交互，生成客户工单；也需要从 order-service 服务中查询订单信息。SpringCSS 的整个系统交互过程如下图所示：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210401224346.png" alt="image-20210401224346130" style="zoom:50%;" />

# 构建多维度配置层

# 03 | Spring Boot 中的配置体系

在 Spring Boot 中，其核心设计理念是对配置信息的管理采用约定优于配置。

**配置文件与 Profile**

为了达到集中化管理的目的，Spring Boot 对配置文件的命名也做了一定的约定，分别使用 label 和 profile 概念来指定配置信息的版本以及运行环境，其中 label 表示配置版本控制信息，而 profile 则用来指定该配置文件所对应的环境。

```
/{application}.yml
/{application}-{profile}.yml
/{label}/{application}-{profile}.yml
/{application}-{profile}.properties
/{label}/{application}-{profile}.properties
```

**代码控制与Profile**

先来看一个简单的示例。

```java
@Configuration
public class DataSourceConfig {
 
    @Bean
    @Profile("dev")
    public DataSource devDataSource() {
        //创建 dev 环境下的 DataSource 
    }
 
    @Bean()
    @Profile("prod")
    public DataSource prodDataSource(){
        //创建 prod 环境下的 DataSource 
    }
}
```

这里使用 @Profile 注解来指定具体所需要执行的 DataSource 创建代码，通过这种方式，可以达到与使用配置文件相同的效果。

在日常开发过程中，一个常见的需求是根据不同的运行环境初始化数据。基于 @Profile 注解，我们就可以将这一过程包含在代码中并做到自动化，如下所示：

```java
@Profile("dev")
@Configuration
public class DevDataInitConfig {
 
  @Bean
  public CommandLineRunner dataInit() { 
    return new CommandLineRunner() {
      @Override
      public void run(String... args) throws Exception {
        //执行 Dev 环境的数据初始化
    };  
}
```

这里用到了 Spring Boot 所提供了启动时任务接口 CommandLineRunner，实现了该接口的代码会在 Spring Boot 应用程序启动时自动进行执行。

# 04 | 如何创建和管理自定义的配置信息？

**如何在配置文件中嵌入系统配置信息？**

通过 ${} 占位符可以引用配置文件中的其他配置项内容，如下列配置：

```properties
system.name=springcss
system.domain=health
system.description=The system ${name} is used for ${domain}.
```

最终“system.description”配置项的值就是“The system springcss is used for health”。

再来看一种场景，假设我们使用 Maven 来构建应用程序，那么可以按如下所示的配置项来动态获取与系统构建过程相关的信息：

```yaml
info: 
  app:
    encoding: @project.build.sourceEncoding@
    java:
      source: @java.version@
      target: @java.version@
```

上述配置项的效果与如下所示的静态配置是一样的：

```yaml
info:
  app:
    encoding: UTF-8
    java:
        source: 1.8.0_31
        target: 1.8.0_31
```

**如何创建和使用自定义配置信息？**

例如，对于现在的配置：

```properties
springcss.order.point=10
```

想要获取这个配置项的内容，通常有两种方法。

1. 使用 @Value 注解

我们可以构建一个 SpringCssConfig 类，如下所示：

```java
@Component
public class SpringCssConfig {
 
    @Value("${springcss.order.point}")
    private int point;
}
```

2. 使用 @ConfigurationProperties 注解

在使用该注解时，我们通常会设置一个“prefix”属性用来指定配置项的前缀，如下所示：

```java
@Component
@ConfigurationProperties(prefix = "springcss.order")
public class SpringCsshConfig {
 
    private int point;

    //省略 getter/setter
}
```

考虑一种更常见也更复杂的场景：假设用户根据下单操作获取的积分并不是固定的，而是根据每个不同类型的订单有不同的积分，那么现在的配置项的内容，如果使用 Yaml 格式的话就应该是这样：

```yaml
springcss:
  points:
    orderType[1]: 10
    orderType[2]: 20
    orderType[3]: 30
```

把这些配置项全部加载到业务代码中：

```java
@Component
@ConfigurationProperties(prefix="springcss.points")
public class SpringCssConfig {
 
    private Map<String, Integer> orderType = new HashMap<>();

    //省略 getter/setter
}
```

> 这里的 Map Key 会是什么样的数据？

当我们输入某一个配置项的前缀时，诸如 IDEA、Eclipse 这样的 IDE 就会自动弹出该前缀下的所有配置信息供你进行选择，效果如下：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210402222532.png" alt="image-20210402222532470" style="zoom:50%;" />

如何实现这种效果呢？

我们需要生成配置元数据。通过 IDE 的“Create metadata for 'springcss.order.point'”按钮，就可以选择创建配置元数据文件。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210402222817.png" alt="image-20210402222817447" style="zoom:50%;" />

这个文件的名称为 additional-spring-configuration-metadata.json，文件内容如下所示：

```json
{
  "properties": [
    {
      "name": "springcss.order.point",
      "type": "java.lang.String",
      "description": "A description for 'springcss.order.point'"
      "defaultValue": 10
    }
  ]
}
```

效果如下所示：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210402223055.png" alt="image-20210402223055622" style="zoom:50%;" />

**如何组织和整合配置信息？**

1. 使用 @PropertySources 注解

在使用 @ConfigurationProperties 注解时，我们可以和 @PropertySource 注解一起进行使用，从而指定从哪个具体的配置文件中获取配置信息。

```java
@Component
@ConfigurationProperties(prefix = "springcss.order")
@PropertySources({
        @PropertySource("classpath:application.properties "),
        @PropertySource("classpath:redis.properties"),
        @PropertySource("classpath:mq.properties")
})
public class SpringCssConfig {
}
```

我们也可以通过配置 spring.config.location 来改变配置文件的默认加载位置，从而实现对多个配置文件的同时加载。

```
java -jar customerservice-0.0.1-SNAPSHOT.jar --spring.config.location=file:///D:/application.properties, classpath:/config/
```

通过 spring.config.location 指定多个配置文件路径也是组织和整合配置信息的一种有效的实现方式。

通过前面的示例，我们看到可以把配置文件保存在多个路径，而这些路径在加载配置文件时具有一定的顺序。Spring Boot 在启动时会扫描以下位置的 application.properties 或者 application.yml 文件作为全局配置文件：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210402223922.png" alt="image-20210402223922742" style="zoom:50%;" />

**如何覆写内置的配置类？**

Spring Boot 内置了大量的自动配置，如果我们不想使用这些配置，就需要对它们进行覆写。

在 Spring Security 体系中，设置用户认证信息所依赖的配置类是 WebSecurityConfigurer 类。这是一个设置 Web 安全的配置类。Spring Security 提供了 WebSecurityConfigurerAdapter 这个适配器类来简化该配置类的使用方式，我们可以继承 WebSecurityConfigurerAdapter 类并且覆写其中的 configure() 的方法来完成自定义的用户认证配置工作。

```java
@Configuration
public class SpringHCssWebSecurityConfigurer extends WebSecurityConfigurerAdapter {
 
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
          .withUser("springcss_user")
          .password("{noop}password1")
          .roles("USER")
          .and()
          .withUser("springcss_admin")
          .password("{noop}password2")
          .roles("USER", "ADMIN");
    }
}
```

开发人员可以通过构建诸如上述所示的 SpringCssWebSecurityConfigurer 类来对这些内置配置类进行覆写，从而实现自定义的配置信息。

# 05 | Spring Boot 自动配置的实现原理

我们先从 @SpringBootApplication 注解开始。

**@SpringBootApplication 注解**

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@SpringBootConfiguration
@EnableAutoConfiguration
@ComponentScan(excludeFilters = {
        @Filter(type = FilterType.CUSTOM, classes = TypeExcludeFilter.class),
        @Filter(type = FilterType.CUSTOM, classes = AutoConfigurationExcludeFilter.class) })
public @interface SpringBootApplication {
    @AliasFor(annotation = EnableAutoConfiguration.class)
    Class<?>[] exclude() default {};
 
    @AliasFor(annotation = EnableAutoConfiguration.class)
    String[] excludeName() default {};
 
    @AliasFor(annotation = ComponentScan.class, attribute = "basePackages")
    String[] scanBasePackages() default {};
 
    @AliasFor(annotation = ComponentScan.class, attribute = "basePackageClasses")
    Class<?>[] scanBasePackageClasses() default {};
}
```

我们可以通过 exclude 和 excludeName 属性来配置不需要实现自动装配的类或类名，也可以通过 scanBasePackages 和 scanBasePackageClasses 属性来配置需要进行扫描的包路径和类路径。

@SpringBootApplication 注解实际上是一个组合注解，它由三个注解组合而成，分别是 @SpringBootConfiguration、@EnableAutoConfiguration 和 @ComponentScan。

1. @ComponentScan 注解

扫描基于 @Component 等注解所标注的类所在包下的所有需要注入的类，并把相关 Bean 定义批量加载到容器中。

2. @SpringBootConfiguration 注解

它是一个空注解，只是使用了 Spring 中的 @Configuration 注解。

3. @EnableAutoConfiguration 注解

该注解的定义如下代码所示：

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@AutoConfigurationPackage
@Import(AutoConfigurationImportSelector.class)
public @interface EnableAutoConfiguration {
 
    String ENABLED_OVERRIDE_PROPERTY = "spring.boot.enableautoconfiguration";
 
    Class<?>[] exclude() default {};
 
    String[] excludeName() default {};
}
```

这里我们关注两个新注解，@AutoConfigurationPackage 和 @Import(AutoConfigurationImportSelector.class)。

@AutoConfigurationPackage 对该注解所在包下的类进行自动配置。AutoConfigurationImportSelector 类会执行 selectImports 方法，核心是获取 configurations 集合并进行过滤。

AutoConfigurationImportSelector 类是一种选择器，负责从各种配置项中找到需要导入的具体配置类。该类的结构如下图所示：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210406225204.png" alt="image-20210406225204010" style="zoom: 33%;" />

**SPI 机制**

JDK 提供了用于服务查找的一个工具类 java.util.ServiceLoader 来实现 SPI 机制。可以在 jar 包的 META-INF/services/ 目录下创建一个以服务接口命名的文件。JDK 中 SPI 机制开发流程如下图所示：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210406225433.png" alt="image-20210406225433071" style="zoom:50%;" />

**SpringFactoriesLoader**

SpringFactoriesLoader 类似这种 SPI 机制，只不过以服务接口命名的文件是放在 META-INF/spring.factories 文件夹下。

spring.factories 配置文件片段如下：

```factories
# Auto Configure
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
org.springframework.boot.autoconfigure.admin.SpringApplicationAdminJmxAutoConfiguration,\
org.springframework.boot.autoconfigure.aop.AopAutoConfiguration,\
org.springframework.boot.autoconfigure.amqp.RabbitAutoConfiguration,\
org.springframework.boot.autoconfigure.MessageSourceAutoConfiguration,\
org.springframework.boot.autoconfigure.PropertyPlaceholderAutoConfiguration,\
org.springframework.boot.autoconfigure.batch.BatchAutoConfiguration,\
org.springframework.boot.autoconfigure.cache.CacheAutoConfiguration,\
org.springframework.boot.autoconfigure.cassandra.CassandraAutoConfiguration,\
org.springframework.boot.autoconfigure.cloud.CloudAutoConfiguration,\
org.springframework.boot.autoconfigure.context.ConfigurationPropertiesAutoConfiguration,\
…
```

以上就是 Spring Boot 中基于 @SpringBootApplication 注解实现自动配置的基本过程和原理。

**@ConditionalOn 系列条件注解**

Spring Boot 中提供了一系列的条件注解，常见的包括：

- @ConditionalOnProperty：只有当所提供的属性属于 true 时才会实例化 Bean
- @ConditionalOnBean：只有在当前上下文中存在某个对象时才会实例化 Bean
- @ConditionalOnClass：只有当某个 Class 位于类路径上时才会实例化 Bean
- @ConditionalOnExpression：只有当表达式为 true 的时候才会实例化 Bean
- @ConditionalOnMissingBean：只有在当前上下文中不存在某个对象时才会实例化 Bean
- @ConditionalOnMissingClass：只有当某个 Class 在类路径上不存在的时候才会实例化 Bean
- @ConditionalOnNotWebApplication：只有当不是 Web 应用时才会实例化 Bean

这些注解的实现原理大致相同，我们挑选 @ConditionalOnClass 注解进行展开，该注解定义如下：

```java
@Target({ ElementType.TYPE, ElementType.METHOD })
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Conditional(OnClassCondition.class)
public @interface ConditionalOnClass {
  Class<?>[] value() default {};
  String[] name() default {};
}
```

OnClassCondition 是 SpringBootCondition 的子类，SpringBootCondition 中的 matches 方法实现如下：：

```java
@Override
public final boolean matches(ConditionContext context,
            AnnotatedTypeMetadata metadata) {
    String classOrMethodName = getClassOrMethodName(metadata);
    try {
        ConditionOutcome outcome = getMatchOutcome(context, metadata);
        logOutcome(classOrMethodName, outcome);
        recordEvaluation(context, classOrMethodName, outcome);
        return outcome.isMatch();
    }
    //省略其他方法
}
```











