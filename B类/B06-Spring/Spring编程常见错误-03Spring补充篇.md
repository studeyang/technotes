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

```java
@Service
public class StudentService {
    @Autowired
    private StudentMapper studentMapper;
    @Autowired
    private StudentService studentService;
    
    public void saveStudent(String realname) throws Exception {
        Student student = new Student();
        student.setRealname(realname);
        studentService.doSaveStudent(student);
    }
    @Transactional
    private void doSaveStudent(Student student) throws Exception {
        studentMapper.saveStudent(student);
        if (student.getRealname().equals("小明")) {
            throw new RuntimeException("该用户已存在");
        }
    }
}
```

执行的时候，传入参数“小明”，结果是异常正常抛出，事务却没有回滚。

- 案例解析

当 Bean 初始化之后，会开始尝试代理操作，这个过程是从 AbstractAutoProxyCreator 里的 postProcessAfterInitialization 方法开始处理的。

我们一路往下找，直到到了 AopUtils 的 canApply 方法。这个方法就是针对切面定义里的条件，确定这个方法是否可以被应用创建成代理。其中有一段 methodMatcher.matches(method, targetClass) 是用来判断这个方法是否符合这样的条件。

从 matches() 调用到了 AbstractFallbackTransactionAttributeSource 的 getTransactionAttribute：

```java
public boolean matches(Method method, Class<?> targetClass) {
    //省略非关键代码
    TransactionAttributeSource tas = getTransactionAttributeSource();
    return (tas == null || tas.getTransactionAttribute(method, targetClass) != null);
}
```

其中，getTransactionAttribute 这个方法是用来获取注解中的事务属性，根据属性确定事务采用什么样的策略。

接着调用到 computeTransactionAttribute 这个方法，其主要功能是根据方法和类的类型确定是否返回事务属性，执行代码如下：

```java
protected TransactionAttribute computeTransactionAttribute(
    Method method, @Nullable Class<?> targetClass) {
    //省略非关键代码
    if (allowPublicMethodsOnly() && !Modifier.isPublic(method.getModifiers())) {
        return null;
    }
    //省略非关键代码
}
```

这里有这样一个判断 allowPublicMethodsOnly() && !Modifier.isPublic(method.getModifiers()) ，当这个判断结果为 true 的时候返回 null，也就意味着这个方法不会被代理，从而导致事务的注解不会生效。我们可以分别看一下这两个条件。

条件 1：allowPublicMethodsOnly()

```java
protected boolean allowPublicMethodsOnly() {
    return this.publicMethodsOnly;
}
```

publicMethodsOnly 属性默认为 true。

条件 2：Modifier.isPublic()

```java
// PUBLIC:1，PRIVATE:2，PROTECTED:4
public static boolean isPublic(int mod) {
    return (mod & PUBLIC) != 0;
}
```

综合上述两个条件，只有当注解为事务的方法被声明为 public 的时候，才会被 Spring 处理。

- 问题修正

案例中的 StudentService，它含有一个自动装配（Autowired）了自身（StudentService）的实例来完成代理方法的调用。这个问题我们在之前 Spring AOP 的代码解析中重点强调过。

```java
@Service
public class StudentService {
    @Autowired
    private StudentMapper studentMapper;
    @Autowired
    private StudentService studentService;
    
    public void saveStudent(String realname) throws Exception {
        Student student = new Student();
        student.setRealname(realname);
        studentService.doSaveStudent(student);
    }
    @Transactional
    public void doSaveStudent(Student student) throws Exception {
        studentMapper.saveStudent(student);
        if (student.getRealname().equals("小明")) {
            throw new RuntimeException("该用户已存在");
        }
    }
}
```

# 20 | Spring 事务常见错误（下）

我们继续讨论事务中的另外两个问题，一个是关于事务的传播机制，另一个是关于多数据源的切换问题。

**案例 1：嵌套事务回滚错误**

我们增加了一个新的业务类 CourseService，用于实现相关业务逻辑。分别调用了保存学生与课程的关联关系，并给课程注册人数 +1。

```java
@Service
public class CourseService {
    @Autowired
    private CourseMapper courseMapper;
    @Autowired
    private StudentCourseMapper studentCourseMapper;
    //注意这个方法标记了“Transactional”
    @Transactional(rollbackFor = Exception.class)
    public void regCourse(int studentId) throws Exception {
        studentCourseMapper.saveStudentCourse(studentId, 1);
        courseMapper.addCourseNumber(1);
    }
}
```

我们在之前的 StudentService.saveStudent() 中调用了 regCourse()，实现了完整的业务逻辑。我们希望的结果是，当注册课程发生错误时，只回滚注册课程部分，保证学生信息依然正常。

```java
@Service
public class StudentService {
    //省略非关键代码
    @Transactional(rollbackFor = Exception.class)
    public void saveStudent(String realname) throws Exception {
        Student student = new Student();
        student.setRealname(realname);
        studentService.doSaveStudent(student);
        try {
            courseService.regCourse(student.getId());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    //省略非关键代码
}
```

为了验证异常是否符合预期，我们在 regCourse() 里抛出了一个注册失败的异常：

```java
@Transactional(rollbackFor = Exception.class)
public void regCourse(int studentId) throws Exception {
    studentCourseMapper.saveStudentCourse(studentId, 1);
    courseMapper.addCourseNumber(1);
    throw new Exception("注册失败");
}
```

最后的结果是，学生和选课的信息都被回滚了，显然这并不符合我们的预期。

- 案例解析

我们先把整个事务的结构梳理一下，整个业务是包含了 2 层事务，外层的 saveStudent() 的事务和内层的 regCourse() 事务。

在 Spring 声明式的事务处理中，有一个属性 propagation，表示一个带事务的方法调用了另一个带事务的方法，被调用的方法它怎么处理自己事务和调用方法事务之间的关系。

propagation 有 7 种配置：REQUIRED、SUPPORTS、MANDATORY、REQUIRES_NEW、NOT_SUPPORTED、NEVER、NESTED。默认是 REQUIRED，它的含义是：如果本来有事务，则加入该事务，如果没有事务，则创建新的事务。

我们再来看下 Spring 事务处理的核心，其关键实现参考 TransactionAspectSupport.invokeWithinTransaction()：

```java
protected Object invokeWithinTransaction(Method method, @Nullable Class<?> targetClass,
                                         final InvocationCallback invocation) throws Throwable {
    TransactionAttributeSource tas = getTransactionAttributeSource();
    final TransactionAttribute txAttr = 
        (tas != null ? tas.getTransactionAttribute(method, targetClass) : null);
    final PlatformTransactionManager tm = determineTransactionManager(txAttr);
    final String joinpointIdentification = methodIdentification(method, targetClass, txAttr);
    if (txAttr == null || !(tm instanceof CallbackPreferringPlatformTransactionManager)) {
        // 是否需要创建一个事务
        TransactionInfo txInfo = createTransactionIfNecessary(tm, txAttr, joinpointIndentification);
        Object retVal = null;
        try {
            // 调用具体的业务方法
            retVal = invocation.proceedWithInvocation();
        } catch (Throwable ex) {
            // 当发生异常时进行处理
            completeTransactionAfterThrowing(txInfo, ex);
            throw ex;
        } finally {
            cleanupTransactionInfo(txInfo);
        }
        // 正常返回时提交事务
        commitTransactionAfterReturning(txInfo);
        return retVal;
    }
    //......省略非关键代码.....
}
```

整个方法完成了事务的一整套处理逻辑，如下：

1. 检查是否需要创建事务；
2. 调用具体的业务方法进行处理；
3. 提交事务；
4. 处理异常。

当前案例是两个事务嵌套的场景，外层事务 doSaveStudent() 和内层事务 regCourse()，每个事务都会调用到这个方法。所以，这个方法会被调用两次。下面我们来具体来看下内层事务对异常的处理。

当捕获了异常，会调用 TransactionAspectSupport.completeTransactionAfterThrowing() 进行异常处理：

```java
protected void completeTransactionAfterThrowing(@Nullable TransactionInfo txInfo, Throwable ex) {
    if (txInfo != null && txInfo.getTransactionStatus() != null) {
        if (txInfo.transactionAttribute != null && txInfo.transactionAttribute.rollbackOn(ex)) {
            try {
                txInfo.getTransactionManager().rollback(txInfo.getTransactionStatus());
            } catch (TransactionSystemException ex2) {
                logger.error("Application exception overridden by rollback exception", ex);
                ex2.initApplicationException(ex);
                throw ex2;
            } catch (RuntimeException | Error ex2) {
                logger.error("Application exception overridden by rollback exception", ex);
                throw ex2;
            }
        }
        //......省略非关键代码.....
    }
}
```

在这个方法里，我们对异常类型做了一些检查，当符合声明中的定义后，执行了具体的 rollback 操作，这个操作是通过 TransactionManager.rollback() 完成的：

```java
public final void rollback(TransactionStatus status) throws TransactionException {
    if (status.isCompleted()) {
        throw new IllegalTransactionStateException(
            "Transaction is already completed - do not call commit or rollback more than once per transaction");
    }
    DefaultTransactionStatus defStatus = (DefaultTransactionStatus) status;
    processRollback(defStatus, false);
}
```

而 rollback() 是在 AbstractPlatformTransactionManager 中实现的，继续调用了 processRollback()：

```java
private void processRollback(DefaultTransactionStatus status, boolean unexpected) {
    try {
        boolean unexpectedRollback = unexpected;
        if (status.hasSavepoint()) { // 有保存点
            status.rollbackToHeldSavepoint();
        } else if (status.isNewTransaction()) { // 是否为一个新的事务
            doRollback(status);
        } else { // 处于一个更大的事务中
            if (status.hasTransaction()) { // 分支1
                if (status.isLocalRollbackOnly() || isGlobalRollbackOnParticipationFailure()) {
                    doSetRollbackOnly(status);
                }
            }
            if (!isFailEarlyOnGlobalRollbackOnly()) {
                unexpectedRollback = false;
            }
        }
        // 省略非关键代码
        if (unexpectedRollback) {
            throw new UnexpectedRollbackException(
                "Transaction rolled back because it has been marked as rollback-only");
        }
    } finally {
        cleanupAfterCompletion(status);
    }
}
```

这个方法里区分了三种不同类型的情况：

1. 是否有保存点；
2. 是否为一个新的事务；
3. 是否处于一个更大的事务中。

在这里，因为我们用的是默认的传播类型 REQUIRED，嵌套的事务并没有开启一个新的事务，所以在这种情况下，当前事务是处于一个更大的事务中，所以会走到情况 3 分支 1 的代码块下。

这里有两个判断条件来确定是否设置为仅回滚：

```java
if (status.isLocalRollbackOnly() || isGlobalRollbackOnParticipationFailure())
```

isLocalRollbackOnly 在当前的情况下是 false，所以是否分设置为仅回滚就由 isGlobalRollbackOnParticipationFailure() 这个方法来决定了，其默认值为 true， 即是否回滚交由外层事务统一决定 。

显然这里的条件得到了满足，从而执行 doSetRollbackOnly：

```java
protected void doSetRollbackOnly(DefaultTransactionStatus status) {
    DataSourceTransactionObject txObject = (DataSourceTransactionObject) status.getTransaction();
    txObject.setRollbackOnly();
}
```

以及最终调用到的 DataSourceTransactionObject 中的 setRollbackOnly()：

```java
public void setRollbackOnly() {
    getConnectionHolder().setRollbackOnly();
}
```

接下来，我们来看外层事务。因为在外层事务中，我们自己的代码捕获了内层抛出来的异常，所以这个异常不会继续往上抛，最后的事务会在 TransactionAspectSupport.invokeWithinTransaction() 中的 commitTransactionAfterReturning() 中进行处理：

```java
protected void commitTransactionAfterReturning(@Nullable TransactionInfo txInfo) {
    if (txInfo != null && txInfo.getTransactionStatus() != null) {
        txInfo.getTransactionManager().commit(txInfo.getTransactionStatus());
    }
}
```

在这个方法里我们执行了 commit 操作，代码如下：

```java
public final void commit(TransactionStatus status) throws TransactionException {
    //......省略非关键代码.....
    if (!shouldCommitOnGlobalRollbackOnly() && defStatus.isGlobalRollbackOnly()) {
        processRollback(defStatus, true);
        return;
    }
    processCommit(defStatus);
}
```

当满足了 shouldCommitOnGlobalRollbackOnly() 和 defStatus.isGlobalRollbackOnly()，就会回滚，否则会继续提交事务。其中 shouldCommitOnGlobalRollbackOnly() 的作用为，如果发现了事务被标记了全局回滚，并且在发生了全局回滚的情况下，判断是否应该提交事务，这个方法的默认实现是返回了 false，这里我们不需要关注它，继续查看 isGlobalRollbackOnly() 的实现：

```java
public boolean isGlobalRollbackOnly() {
    return ((this.transaction instanceof SmartTransactionObject) && 
            ((SmartTransactionObject) this.transaction).isRollbackOnly());
}
```

这个方法最终进入了 DataSourceTransactionObject 类中的 isRollbackOnly()：

```java
public boolean isRollbackOnly() {
    return getConnectionHolder().isRollbackOnly();
}
```

我们再次回顾一下之前的内部事务处理结果，其最终调用到的是 DataSourceTransactionObject 中的 setRollbackOnly()：

```java
public void setRollbackOnly() {
    getConnectionHolder().setRollbackOnly();
}
```

isRollbackOnly() 和 setRollbackOnly() 这两个方法的执行本质都是对 ConnectionHolder 中 rollbackOnly 属性标志位的存取，而 ConnectionHolder 则存在于 DefaultTransactionStatus 类实例的 transaction 属性之中。

至此，答案基本浮出水面了：外层事务是否回滚的关键，最终取决于 DataSourceTransactionObject 类中的 isRollbackOnly()，而该方法的返回值，正是我们在内层异常的时候设置的。

- 问题修正

我们只需要对传播属性进行修改，把类型改成 REQUIRES_NEW 就可以了。

```java
@Transactional(rollbackFor = Exception.class, propagation = Propagation.REQUIRES_NEW)
public void regCourse(int studentId) throws Exception {
    studentCourseMapper.saveStudentCourse(studentId, 1);
    courseMapper.addCourseNumber(1);
    throw new Exception("注册失败");
}
```

简单解释下这个过程：

当子事务声明为 Propagation.REQUIRES_NEW 时，在 TransactionAspectSupport.invokeWithinTransaction() 中调用 createTransactionIfNecessary() 就会创建一个新的事务，独立于外层事务。

而在 AbstractPlatformTransactionManager.processRollback() 进行 rollback 处理时，因为 status.isNewTransaction() 会因为它处于一个新的事务中而返回 true，所以它走入到了另一个分支，执行了 doRollback() 操作，让这个子事务单独回滚，不会影响到主事务。

**案例 2：多数据源间切换之谜**

假设现在每个学生在注册的时候，需要给他们发一张校园卡，并给校园卡里充入 50 元钱。但是这个校园卡管理系统是一个第三方系统，使用的是另一套数据库，这样我们就需要在一个事务中同时操作两个数据库。

Card 的业务类如下，里面实现了卡与学生 ID 关联，以及充入 50 元的操作：

```java
@Service
public class CardService {
    @Autowired
    private CardMapper cardMapper;
    
    @Transactional
    public void createCard(int studentId) throws Exception {
        Card card = new Card();
        card.setStudentId(studentId);
        card.setBalance(50);
        cardMapper.saveCard(card);
    }
}
```

- 案例解析

学生注册和发卡都要在一个事务里完成，但是我们都默认只会连一个数据源，之前我们一直连的都是学生信息这个数据源，在这里，我们还需要对校园卡的数据源进行操作。于是，我们需要在一个事务里完成对两个数据源的操作，该如何实现这样的功能呢？

在 Spring 里有这样一个抽象类 AbstractRoutingDataSource，这个类相当于 DataSource 的路由中介，在运行时根据某种 key 值来动态切换到所需的 DataSource 上。通过实现这个类就可以实现我们期望的动态数据源切换。

```java
public abstract class AbstractRoutingDataSource 
    extends AbstractDataSource implements InitializingBean {
    
    @Nullable
    private Map<Object, Object> targetDataSources;
    
    @Nullable
    private Object defaultTargetDataSource;
    
    private boolean lenientFallback = true;
    
    private DataSourceLookup dataSourceLookup = new JndiDataSourceLookup();
    
    @Nullable
    private Map<Object, DataSource> resolvedDataSources;
    
    @Nullable
    private DataSource resolvedDefaultDataSource;
    
    //省略非关键代码
}
```

这里强调一下，这个类里有这么几个关键属性：

1. targetDataSources 保存了 key 和数据库连接的映射关系；
2. defaultTargetDataSource 标识默认的连接；
3. resolvedDataSources 存储数据库标识和数据源的映射关系。

获取数据库连接的是 getConnection()，它调用了 determineTargetDataSource() 来创建连接：

```java
protected DataSource determineTargetDataSource() {
    Assert.notNull(this.resolvedDataSources, "DataSource router not initialized");
    Object lookupKey = determineCurrentLookupKey();
    DataSource dataSource = this.resolvedDataSources.get(lookupKey);
    if (dataSource == null && (this.lenientFallback || lookupKey == null)) {
        dataSource = this.resolvedDefaultDataSource;
    }
    if (dataSource == null) {
        throw new IllegalStateException(
            "Cannot determine target DataSource for lookup key [" + lookupKey + "]");
    }
    return dataSource;
}
```

determineTargetDataSource() 是整个部分的核心，它的作用就是动态切换数据源。有多少个数据源，就存多少个数据源在 targetDataSources 中。

而选择哪个数据源又是由 determineCurrentLookupKey() 来决定的，此方法是抽象方法，需要我们继承 AbstractRoutingDataSource 抽象类来重写此方法。

```java
protected abstract Object determineCurrentLookupKey();
```

这样看来，这个方法的实现就得由我们完成了。接下来我们将会完成一系列相关的代码，解决这个问题。

- 问题修正

首先，我们创建一个 MyDataSource 类，继承了 AbstractRoutingDataSource，并覆写了 determineCurrentLookupKey()：

```java
public class MyDataSource extends AbstractRoutingDataSource {
    private static final ThreadLocal<String> key = new ThreadLocal<String>();
    
    @Override
    protected Object determineCurrentLookupKey() {
        return key.get();
    }
    
    public static void setDataSource(String dataSource) {
        key.set(dataSource);
    }
    
    public static String getDatasource() {
        return key.get();
    }
    
    public static void clearDataSource() {
        key.remove();
    }
}
```

其次，我们需要修改 JdbcConfig。这里定义了  dataSourceCore 和 dataSourceCard 两个数据源。

```java
public class JdbcConfig {
    //省略非关键代码
    @Value("${card.driver}")
    private String cardDriver;
    
    @Value("${card.url}")
    private String cardUrl;
    
    @Value("${card.username}")
    private String cardUsername;
    
    @Value("${card.password}")
    private String cardPassword;
    
    @Autowired
    @Qualifier("dataSourceCard")
    private DataSource dataSourceCard;
    
    @Autowired
    @Qualifier("dataSourceCore")
    private DataSource dataSourceCore;
    
    //省略非关键代码
    @Bean(name = "dataSourceCore")
    public DataSource createCoreDataSource() {
        DriverManagerDataSource ds = new DriverManagerDataSource();
        ds.setDriverClassName(driver);
        ds.setUrl(url);
        ds.setUsername(username);
        ds.setPassword(password);
        return ds;
    }
    
    @Bean(name = "dataSourceCard")
    public DataSource createCardDataSource() {
        DriverManagerDataSource ds = new DriverManagerDataSource();
        ds.setDriverClassName(cardDriver);
        ds.setUrl(cardUrl);
        ds.setUsername(cardUsername);
        ds.setPassword(cardPassword);
        return ds;
    }
    
    @Bean(name = "dataSource")
    public MyDataSource createDataSource() {
        MyDataSource myDataSource = new MyDataSource();
        Map<Object, Object> map = new HashMap<>();
        map.put("core", dataSourceCore);
        map.put("card", dataSourceCard);
        myDataSource.setTargetDataSources(map);
        myDataSource.setDefaultTargetDataSource(dataSourceCore);
        return myDataSource;
    }
    //省略非关键代码
}
```

最后还剩下一个问题，setDataSource 这个方法什么时候执行呢？

我们可以用 Spring AOP 来设置，把配置的数据源类型都设置成注解标签。我们定义了一个新的注解 @DataSource，，可以直接加在 Service() 上，实现数据库切换：

```java
@Documented
@Target({ElementType.TYPE, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
public @interface DataSource {
    String value();
    String core = "core";
    String card = "card";
}
```

另外，我们还需要写一个 Spring AOP 来对相应的服务方法进行拦截，完成数据源的切换操作。特别要注意的是，这里要加上一个 @Order(1) 标记它的初始化顺序。这个 Order 值一定要比事务的 AOP 切面的值小，这样可以获得更高的优先级，否则自动切换数据源将会失效。

```java
@Aspect
@Service
@Order(1)
public class DataSourceSwitch {
    @Around("execution(* com.spring.puzzle.others.transaction.example3.CardService.*(..))")
    public void around(ProceedingJoinPoint point) throws Throwable {
        Signature signature = point.getSignature();
        MethodSignature methodSignature = (MethodSignature) signature;
        Method method = methodSignature.getMethod();
        if (method.isAnnotationPresent(DataSource.class)) {
            DataSource dataSource = method.getAnnotation(DataSource.class);
            MyDataSource.setDataSource(dataSource.value());
            System.out.println("数据源切换至：" + MyDataSource.getDatasource());
        }
        point.proceed();
        MyDataSource.clearDataSource();
        System.out.println("数据源已移除！");
    }
}
```

最后，我们实现了 Card 的发卡逻辑，在方法前声明了切换数据库：

```java
@Service
public class CardService {
    @Autowired
    private CardMapper cardMapper;
    
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    @DataSource(DataSource.card)
    public void createCard(int studentId) throws Exception {
        Card card = new Card();
        card.setStudentId(studentId);
        card.setBalance(50);
        cardMapper.saveCard(card);
    }
}
```

并在 saveStudent() 里调用了发卡逻辑：

```java
@Transactional(rollbackFor = Exception.class)
public void saveStudent(String realname) throws Exception {
    Student student = new Student();
    student.setRealname(realname);
    studentService.doSaveStudent(student);
    try {
        courseService.regCourse(student.getId());
        cardService.createCard(student.getId());
    } catch (Exception e) {
        e.printStackTrace();
    }
}
```

执行一下，一切正常，两个库的数据都可以正常保存了。

最后我们重新过一遍流程。在创建了事务以后，会通过 DataSourceTransactionManager.doBegin() 获取相应的数据库连接：

```java
protected void doBegin(Object transaction, TransactionDefinition definition) {
    DataSourceTransactionObject txObject = (DataSourceTransactionObject) transaction;
    Connection con = null;
    try {
        if (!txObject.hasConnectionHolder() ||
            txObject.getConnectionHolder().isSynchronizedWithTransaction()) {
            Connection newCon = obtainDataSource().getConnection();
            txObject.setConnectionHolder(new ConnectionHolder(newCon), true);
        }
        //省略非关键代码
}
```

这里的 obtainDataSource().getConnection() 调用到了 AbstractRoutingDataSource.getConnection()，这就与我们实现的功能顺利会师了。

```java
public Connection getConnection() throws SQLException {
    return determineTargetDataSource().getConnection();
}
```



