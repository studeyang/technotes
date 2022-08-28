# 18 | Spring Data 常见错误

众所周知，基本上所有的项目都会用到数据库，所以 Spring 提供了对市场上主流数据库的贴心支持，我们不妨通过下面的列表快速浏览下：

```
Spring Data Commons
Spring Data JPA
Spring Data KeyValue
Spring Data LDAP
Spring Data MongoDB
Spring Data Redis
Spring Data REST
Spring Data for Apache Cassandra
Spring Data for Apache Geode
Spring Data for Apache Solr
Spring Data for Pivotal GemFire
Spring Data Couchbase (community module)
Spring Data Elasticsearch (community module)
Spring Data Neo4j (community module)
```

**案例 1：注意读与取的一致性**

当使用 Spring Data Redis 时，我们有时候会在项目升级的过程中，发现存储后的数据有读取不到的情况。这里我们不妨直接写出一个错误案例来模拟下：

```java
@SpringBootApplication
public class SpringdataApplication {
    SpringdataApplication(RedisTemplate redisTemplate, 
                          StringRedisTemplate stringRedisTemplate) {
        String key = "mykey";
        stringRedisTemplate.opsForValue().set(key, "myvalue");
        Object valueGotFromStringRedisTemplate = stringRedisTemplate.opsForValue().get(key);
        System.out.println(valueGotFromStringRedisTemplate);
        Object valueGotFromRedisTemplate = redisTemplate.opsForValue().get(key);
        System.out.println(valueGotFromRedisTemplate);
    }
    public static void main(String[] args) {
        SpringApplication.run(SpringdataApplication.class, args);
    }
}
```

在上述代码中，我们使用了 Redis 提供的两种 Template，一种 RedisTemplate，一种 StringRedisTemplate。但是当我们使用 StringRedisTemplate 去存一个数据后，你会发现使用 RedisTemplate 是取不到对应的数据的。输出结果如下：

```
myvalue
null
```

如果我们是不同的开发者开发不同的项目呢？一个项目只负责存储，另外一个项目只负责读取，两个项目之间缺乏沟通和协调。这种问题在实际工作中并不稀奇。

- 案例解析

首先，我们需要认清一个现实：我们不可能直接将数据存取到 Redis 中，毕竟一些数据是一个对象型，例如 String，甚至是一些自定义对象。我们需要在存取前对数据进行序列化或者反序列化操作。

当带着 key 去存取数据时，它会执行 AbstractOperations#rawKey。

```java
byte[] rawKey(Object key) {
    Assert.notNull(key, "non null key required");
    if (keySerializer() == null && key instanceof byte[]) {
        return (byte[]) key;
    }
    return keySerializer().serialize(key);
}
```

从上述代码可以看出，假设存在 keySerializer，则利用它将 key 序列化。而对于 StringRedisTemplate 来说，它指定的其实是 StringRedisSerializer。具体实现如下：

```java
public class StringRedisSerializer implements RedisSerializer<String> {
    private final Charset charset;
    @Override
    public byte[] serialize(@Nullable String string) {
        return (string == null ? null : string.getBytes(charset));
    }
}
```

而如果我们使用的是 RedisTemplate，则使用的是 JDK 序列化，具体序列化操作参考下面的实现：

```java
public class JdkSerializationRedisSerializer implements RedisSerializer<Object> {
    @Override
    public byte[] serialize(@Nullable Object object) {
        if (object == null) {
            return SerializationUtils.EMPTY_ARRAY;
        }
        try {
            return serializer.convert(object);
        } catch (Exception ex) {
            throw new SerializationException("Cannot serialize", ex);
        }
    }
}
```

上面对 key 的处理，采用的是 JDK 的序列化，最终它调用的方法如下：

```java
public interface Serializer<T> {
    void serialize(T var1, OutputStream var2) throws IOException;
    default byte[] serializeToByteArray(T object) throws IOException {
        ByteArrayOutputStream out = new ByteArrayOutputStream(1024);
        this.serialize(object, out);
        return out.toByteArray();
    }
}
```

你可以直接将"mykey"这个字符串分别用上面提到的两种序列化器进行序列化，你会发现它们的结果确实不同。

- 案例修正

要解决这个问题，非常简单，就是检查自己所有的数据操作，是否使用了相同的 RedisTemplate，就是相同，也要检查所指定的各种 Serializer 是否完全一致，否则就会出现各式各样的错误。

**案例 2：默认值的错误**

当我们使用 Spring Data 时，就像其他 Spring 模块一样，为了应对大多数场景或者方便用户使用，Spring Data 都有很多默认值，但是不见得所有的默认值都是最合适的。

例如在一个依赖 Cassandra 的项目中，有时候我们在写入数据之后，并不能立马读到写入的数据。这里面可能是什么原因呢？这种错误并没有什么报错，一切都是正常的，只是读取不到数据而已。

- 案例解析

当我们什么都不去配置，而是直接使用 Spring Data Cassandra 来操作时，我们实际依赖了 Cassandra driver 内部的配置文件，具体目录如下：

```
.m2\repository\com\datastax\oss\java-driver-core\4.6.1\java-driver-core-4.6.1.jar!\reference.conf
```

我们可以看下它存在很多默认的配置，其中一项很重要的配置是 Consistency，在 driver 中默认为 LOCAL_ONE，具体如下：

```
basic.request {
  # The consistency level.
  # 
  # Required: yes
  # Modifiable at runtime: yes, the new value will be used for requests issued after the change.
  # Overridable in a profile: yes
  consistency = LOCAL_ONE
  //省略其他非关键配置
}
```

所以当我们去执行读写操作时，我们都会使用 LOCAL_ONE。

如果你稍微了解下 Cassandra 的话，你就知道 Cassandra 使用的一个核心原则，就是要使得 R（读）+W（写）>N，即读和写的节点数之和需要大于备份数。

例如，假设我们的数据备份是 3 份，待写入的数据分别存储在 A、B、C 三个节点上。那么常见的搭配是 R（读）和 W（写）的一致性都是 LOCAL_QURAM，这样可以保证能及时读到写入的数据；而假设在这种情况下，我们读写都是用 LOCAL_ONE，那么则可能发生这样的情况，即用户写入一个节点 A 就返回了，但是用户 B 立马读的节点是 C，且由于是 LOCAL_ONE 一致性，则读完 C 就可以立马返回。此时，就会出现数据读取可能落空的情况。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208262219855.png" alt="image-20220826221957720" style="zoom:50%;" />

那么考虑一个问题，为什么 Cassandra driver 默认是使用 LOCAL_ONE 呢？

实际上，当你第一次学习和应用 Cassandra 时，你一定会先只装一台机器玩玩。此时，设置为 LOCAL_ONE 其实是最合适的，也正因为只有一台机器，你的读写都只能命中一台。这样的话，读写是完全没有问题的。但是产线上的 Cassandra 大多都是多数据中心多节点的，备份数大于 1。所以读写都用 LOCAL_ONE 就会出现问题。

- 案例修正

通过这个案例的分析，我们知道 Spring Data Cassandra 的默认值不见得适应于所有情况，甚至说，不一定适合于产线环境，所以这里我们不妨修改下默认值，还是以 consistency 为例。

我们看下如何修改它：

```java
@Override
protected SessionBuilderConfigurer getSessionBuilderConfigurer() {
    return cqlSessionBuilder -> {
        DefaultProgrammaticDriverConfigLoaderBuilder defaultProgrammaticDriverConfigLoaderBuilder = 
            new DefaultProgrammaticDriverConfigLoaderBuilder();
        driverConfigLoaderBuilderCustomizer().customize(defaultProgrammaticDriverConfigLoaderBuilder);
        cqlSessionBuilder.withConfigLoader(defaultProgrammaticDriverConfigLoaderBuilder.build());
        return cqlSessionBuilder;
    }
}

@Bean
public DriverConfigLoaderBuilderCustomizer driverConfigLoaderBuilderCustomizer() {
    return loaderBuilder -> loaderBuilder
        .withString(REQUEST_CONSISTENCY, ConsistencyLevel.LOCAL_QUORUM.name());
}
```

这里我们将一致性级别从 LOCAL_ONE 改成了 LOCAL_QUARM，更符合我们的实际产品部署和应用情况。

**案例 3：冗余的 Session**

有时候，我们使用 Spring Data 做连接时，会比较在意我们的内存占用。例如我们使用 Spring Data Cassandra 操作 Cassandra 时，可能会发现类似这样的问题：

![image-20220827211645980](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208272116147.png)

Spring Data Cassandra 在连接 Cassandra 之后，会获取 Cassandra 的 Metadata 信息，这个内存占用量是比较大的，因为它存储了数据的 Token Range 等信息。如上图所示，在我们的应用中，占用 40M 以上已经不少了，但问题是为什么有 4 个占用 40 多 M 呢？难道不是只建立一个连接么？

- 案例解析

这里我们可以先写一个例子，直接展示下问题的原因，然后再来看看我们的问题到底出现在什么地方！现在我们定义一个 MyService 类，当它构造时，会输出它的名称信息：

```java
public class MyService {
    public MyService(String name) {
        System.err.println(name);
    }
}
```

然后我们定义两个 Configuration 类，同时让它们是继承关系，其中父 Configuration 命名如下：

```java
@Configuration
public class BaseConfig {
    @Bean
    public MyService service() {
        return new MyService("myservice defined from base config");
    }
}
```

子 Configuration 命名如下：

```java
@Configuration
public class Config extends BaseConfig {
    @Bean
    public MyService service(){
        return new MyService("myservice defined from config");
    }
}
```

子类的 service() 实现覆盖了父类对应的方法。最后，我们书写一个启动程序：

```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

为了让程序启动，我们不能将 BaseConfig 和 Config 都放到 Application 的扫描范围。我们可以按如下结构组织代码：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208272121708.png" alt="image-20220827212137637" style="zoom:50%;" />

最终我们会发现，当程序启动时，我们只有一个 MyService 的 Bean 产生，输出日志如下：

```
myservice defined from config
```

这里可以看出，如果我们的子类标识 Bean 的方法正好覆盖了对应的父类，那么只能利用子类的方法产生一个 Bean。但是假设我们不小心在子类实现时，没有意识到父类方法的存在，定义如下呢？

```java
@Configuration
public class Config extends BaseConfig {
    @Bean
    public MyService service2() {
        return new MyService("myservice defined from config");
    }
}
```

经过上述的不小心修改，再次运行程序，你会发现有 2 个 MyService 的 Bean 产生：

```
myservice defined from config
myservice defined from base config
```

说到这里你可能想到一个造成内存翻倍的原因。我们去查看案例程序的代码，可能会发现存在这样的问题：

```java
@Configuration
@EnableCassandraRepositories
public class CassandraConfig extends AbstractCassandraConfiguration {
    @Bean
    @Primary
    public CqlSessionFactoryBean session() {
        log.info("init session");
        CqlSessionFactoryBean cqlSessionFactoryBean = new CqlSessionFactoryBean();
        //省略其他非关键代码
        return cqlSessionFactoryBean;
    }
    //省略其他非关键代码
}
```

CassandraConfig 继承于 AbstractSessionConfiguration，它已经定义了一个CqlSessionFactoryBean，代码如下：

```java
@Configuration
public abstract class AbstractSessionConfiguration implements BeanFactoryAware {
    @Bean
    public CqlSessionFactoryBean cassandraSession() {
        CqlSessionFactoryBean bean = new CqlSessionFactoryBean();
        bean.setContactPoints(getContactPoints());
        //省略其他非关键代码
        return bean;
    }
    //省略其他非关键代码
}
```

而比较这两段的 CqlSessionFactoryBean 的定义方法，你会发现它们的方法名是不同的：

```
cassandraSession()
session()
```

- 案例修正

我们可以把原始案例代码修改如下：

```java
@Configuration
@EnableCassandraRepositories
public class CassandraConfig extends AbstractCassandraConfiguration {
    @Bean
    @Primary
    public CqlSessionFactoryBean cassandraSession() {
        //省略其他非关键代码
    }
    //省略其他非关键代码
}
```

不过你可能会有一个疑问，这里不就是翻倍了么？但也不至于四倍啊。

实际上，这是因为使用 Spring Data Redis 会创建两个 Session （systemSession 和 session），它们都会获取 metadata。具体可参考代码 CqlSessionFactoryBean#afterPropertiesSet：

```java
@Override
public void afterPropertiesSet() {
    CqlSessionBuilder sessionBuilder = buildBuilder();
    // system session 的创建
    this.systemSession = buildSystemSession(sessionBuilder);
    initializeCluster(this.systemSession);
    // normal session 的创建
    this.session = buildSession(sessionBuilder);
    executeCql(getStartupScripts().stream(), this.session);
    performSchemaAction();
    this.systemSession.refreshSchema();
    this.session.refreshSchema();
}
```

# 19 | Spring 事务常见错误（上）

Spring 事务管理包含两种配置方式，第一种是使用 XML 进行模糊匹配，绑定事务管理；第二种是使用注解，这种方式可以对每个需要进行事务处理的方法进行单独配置，你只需要添加上 @Transactional，然后在注解内添加属性配置即可。

在正式开始讲解事务之前，我们先搭建一个简单的 Spring 数据库的环境。

1. 数据库配置文件 jdbc.properties

```properties
jdbc.driver=com.mysql.cj.jdbc.Driver
jdbc.url=jdbc:mysql://localhost:3306/spring?useUnicode=true&characterEncoding=UTF-8&serverTimezone=UTC&useSSL=false
jdbc.username=root
jdbc.password=pass
```

2. JDBC 的配置类

```java
public class JdbcConfig {
    @Value("${jdbc.driver}")
    private String driver;
    @Value("${jdbc.url}")
    private String url;
    @Value("${jdbc.username}")
    private String username;
    @Value("${jdbc.password}")
    private String password;
    @Bean(name = "jdbcTemplate")
    public JdbcTemplate createJdbcTemplate(DataSource dataSource) {
        return new JdbcTemplate(dataSource);
    }
    @Bean(name = "dataSource")
    public DataSource createDataSource() {
        DriverManagerDataSource ds = new DriverManagerDataSource();
        ds.setDriverClassName(driver);
        ds.setUrl(url);
        ds.setUsername(username);
        ds.setPassword(password);
        return ds;
    }
    @Bean(name = "transactionManager")
    public PlatformTransactionManager createTransactionManager(DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }
}
```

3. 应用配置类

```java
@Configuration
@ComponentScan
@Import({JdbcConfig.class})
@PropertySource("classpath:jdbc.properties")
@MapperScan("com.spring.puzzle.others.transaction.example1")
@EnableTransactionManagement
@EnableAutoConfiguration(exclude={DataSourceAutoConfiguration.class})
@EnableAspectJAutoProxy(proxyTargetClass = true, exposeProxy = true)
public class AppConfig {
    public static void main(String[] args) throws Exception {
        ApplicationContext context = new AnnotationConfigApplicationContext(AppConfig.class);
    }
}
```

完成了上述基础配置和代码后，我们开始进行案例的讲解。

**案例 1：unchecked 异常与事务回滚**

在系统中，我们需要增加一个学生管理的功能，每一位新生入学后，都会往数据库里存入学生的信息。我们引入了一个学生类 Student 和与之相关的 Mapper。

```java
public class Student implements Serializable {
    private Integer id;
    private String realname;
}
```

对应的 Mapper 类定义如下：

```java
@Mapper
public interface StudentMapper {
    @Insert("INSERT INTO `student`(`realname`) VALUES (#{realname})")
    void saveStudent(Student student);
}
```

对应数据库表的 Schema 如下：

```sql
CREATE TABLE `student` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `realname` varchar(255) DEFAULT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

业务类 StudentService，其中包括一个保存的方法 saveStudent。

```java
@Service
public class StudentService {
    @Autowired
    private StudentMapper studentMapper;
    @Transactional
    public void saveStudent(String realname) throws Exception {
        Student student = new Student();
        student.setRealname(realname);
        studentMapper.saveStudent(student);
        if (student.getRealname().equals("小明")) {
            throw new Exception("该学生已存在");
        }
    }
}
```

然后使用下面的代码来测试一下，保存一个叫小明的学生，看会不会触发事务的回滚。

```java
public class AppConfig {
    public static void main(String[] args) throws Exception {
        ApplicationContext context = new AnnotationConfigApplicationContext(AppConfig.class);
        StudentService studentService = (StudentService) context.getBean("studentService");
        studentService.saveStudent("小明");
    }
}
```

执行结果中，异常被抛出，但是检查数据库，你会发现数据库里插入了一条新的记录。

- 案例解析

我们通过 debug 沿着 saveStudent 继续往下跟，得到了一个这样的调用栈：

![image-20220828214520385](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208282145613.png)

从这个调用栈中我们看到了熟悉的 CglibAopProxy，另外事务本质上也是一种特殊的切面，在创建的过程中，被 CglibAopProxy 代理。事务处理的拦截器是 TransactionInterceptor，它支撑着整个事务功能的架构，我们来分析下这个拦截器是如何实现事务特性的。

首先，TransactionInterceptor 继承类 TransactionAspectSupport，实现了接口 MethodInterceptor。

```java
protected Object invokeWithinTransaction(
    Method method, @Nullable Class<?> targetClass,
    final InvocationCallback invocation) throws Throwable {
    //省略非关键代码
    Object retVal;
    try {
        retVal = invocation.proceedWithInvocation();
    } catch (Throwable ex) {
        completeTransactionAfterThrowing(txInfo, ex);
        throw ex;
    } finally {
        cleanupTransactionInfo(txInfo);
    }
    //省略非关键代码
}
```

在 completeTransactionAfterThrowing 的代码中，有这样一个方法 rollbackOn()，这是事务的回滚的关键判断条件。当这个条件满足时，会触发 rollback 操作，事务回滚。

```java
protected void completeTransactionAfterThrowing(
    @Nullable TransactionInfo txInfo, Throwable ex) {
    //省略非关键代码
    //判断是否需要回滚
    if (txInfo.transactionAttribute != null 
        && txInfo.transactionAttribute.rollbackOn(ex)) {
        try {
            //执行回滚
            txInfo.getTransactionManager().rollback(txInfo.getTransactionStatus());
        } catch (TransactionSystemException ex2) {
            ex2.initApplicationException(ex);
            throw ex2;
        } catch (RuntimeException | Error ex2) {
            throw ex2;
        }
    }
    //省略非关键代码
}
```

rollbackOn() 其实包括了两个层级，具体可参考如下代码：

```java
public boolean rollbackOn(Throwable ex) {
    // 层级 1：根据"rollbackRules"及当前捕获异常来判断是否需要回滚
    RollbackRuleAttribute winner = null;
    int deepest = Integer.MAX_VALUE;
    if (this.rollbackRules != null) {
        for (RollbackRuleAttribute rule : this.rollbackRules) {
            // 当前捕获的异常可能是回滚“异常”的继承体系中的“一员”
            int depth = rule.getDepth(ex);
            if (depth >= 0 && depth < deepest) {
                deepest = depth;
                winner = rule;
            }
        }
    }
    // 层级 2：调用父类的 rollbackOn 方法来决策是否需要 rollback
    if (winner == null) {
        return super.rollbackOn(ex);
    }
    return !(winner instanceof NoRollbackRuleAttribute);
}
```

在父类的 rollbackOn() 中，我们发现了一个重要的线索，只有在异常类型为 RuntimeException 或者 Error 的时候才会返回 true。

```java
public boolean rollbackOn(Throwable ex) {
    return (ex instanceof RuntimeException || ex instanceof Error);
}
```

- 问题修正

只需要把抛出的异常类型改成 RuntimeException 就可以了。于是这部分代码就可以修改如下：

```java
@Service
public class StudentService {
    @Autowired
    private StudentMapper studentMapper;
    @Transactional
    public void saveStudent(String realname) throws Exception {
        Student student = new Student();
        student.setRealname(realname);
        studentMapper.saveStudent(student);
        if (student.getRealname().equals("小明")) {
            throw new RuntimeException("该用户已存在");
        }
    }
}
```

但是这种修改方法看起来不够优美，毕竟我们的异常有时候是固定死不能随意修改的。所以结合前面的案例分析，我们还有一个更好的修改方式。

```java
@Transactional(rollbackFor = Exception.class)
```

**案例 2：试图给 private 方法添加事务**























