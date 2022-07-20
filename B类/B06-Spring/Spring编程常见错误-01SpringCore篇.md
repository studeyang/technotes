# 开篇词

本专栏共分为以下三个部分，你可以对照着下面这张图去理解我的设计思路：

![image-20220714222215589](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207142222708.png)

Spring Core 篇：Spring Core 包括 Bean 定义、注入、AOP 等核心功能，可以说它们是 Spring 的基石。不管未来你是做 Spring Web 开发，还是使用 Spring Cloud 技术栈，你都绕不开这些功能。所以这里我会重点介绍在这些功能使用上的常见问题。

Spring Web 篇：大多项目使用 Spring 还是为了进行 Web 开发，所以我也梳理了从请求 URL 解析、Header 解析、Body 转化到授权等 Web 开发中绕不开的问题。不难发现，它们正好涵盖了从一个请求到来，到响应回去这一完整流程。

Spring 补充篇：作为补充，这部分我会重点介绍 Spring 测试、Spring 事务、Spring Data 相关问题。最后，我还会为你系统总结下 Spring 使用中发生问题的根本原因。

# 01｜Spring Bean定义常见错误

**案例 1：隐式扫描不到 Bean 的定义**

我们使用下面的包结构和
相关代码来完成一个简易的 Web 版 HelloWorld：

![image-20220714223154397](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207142231438.png)

假设有一天，当我们需要添加多个类似的 Controller，同时又希望用更清晰的包层
次和结构来管理时，我们可能会去单独建立一个独立于 application 包之外的 Controller
包，并调整类的位置。调整后结构示意如下：

![image-20220714223245190](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207142232226.png)

我们会发现这个 Web 应用失
效了，即不能识别出 HelloWorldController 了。

- 案例解析

在我们的案例中，我们直接使用的是 SpringBootApplication 注解定义的
ComponentScan，它的 basePackages 没有指定，所以默认为空。此时扫描的是什么包？这里不妨带着这个问题去调试下（调试位置参考 ComponentScanAnnotationParser#parse 方法），调试视图如下：

![image-20220714223643124](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207142236157.png)

从上图可以看出，当 basePackages 为空时，扫描的包会是 declaringClass 所在的包，在本案例中，declaringClass 就是 Application.class，所以扫描的包其实就是它所在的包，即 com.spring.puzzle.class1.example1.application。

- 问题修正

```java
@SpringBootApplication
@ComponentScan("com.spring.puzzle.class1.example1.controller")
public class Application {
  public static void main(String[] args) {
    SpringApplication.run(Application.class, args);
  }
}
```

一旦显式指定其它包，原来的默认扫描包就被忽略了。

**案例 2：定义的 Bean 缺少隐式依赖**

例如我们会写出下面这样的代码：

```java
@Service
public class ServiceImpl {
    private String serviceName;
    public ServiceImpl(String serviceName) {
        this.serviceName = serviceName;
    }
}
```

在启动项目的时候会报如下错误：

```text
Parameter 0 of constructor in com.spring.puzzle.class1.example2.ServiceImpl required a bean of type 'java.lang.String' that could not be found.
```

那这种错误是怎么发生的呢？下面我们来分析一下。

- 案例解析

当创建一个 Bean 时，调用的方法是
AbstractAutowireCapableBeanFactory#createBeanInstance。它主要包含两大基本步骤：寻找构造器和通过反射调用构造器创建实例。

对于这个案例，最核心的代码执行，你可以参考下面的代码片段：

```java
// Candidate constructors for autowiring?
Constructor<?>[] ctors = determineConstructorsFromBeanPostProcessors(beanClass, beanName);
if (ctors != null || mbd.getResolvedAutowireMode() == AUTOWIRE_CONSTRUCTOR ||
    mbd.hasConstructorArgumentValues() || !ObjectUtils.isEmpty(args)) {
    return autowireConstructor(beanName, mbd, ctors, args);
}
```

Spring 会先执行 determineConstructorsFromBeanPostProcessors 方法来获取构造器，然后通过 autowireConstructor 方法带着构造器去创建实例。很明显，在本案例中只有一个构造器，所以非常容易跟踪这个问题。

- 问题修正

我们定义一个类为 Bean，如果再显式定义了构造器，那么这个 Bean 在构建时，会自动根据构造器参数定义寻找对应的 Bean，然后反射创建出这个 Bean。

我们可以直接定义一个能让 Spring 装配给 ServiceImpl 构造器参数的 Bean，例如定义如下：

```java
//这个bean装配给ServiceImpl的构造器参数“serviceName”
@Bean
public String serviceName(){
    return "MyServiceName";
}
```

**案例 3：原型 Bean 被固定**

在定义 Bean 时，有时候我们会使用原型 Bean，例如定义如下：

```java
@Service
@Scope(ConfigurableBeanFactory.SCOPE_PROTOTYPE)
public class ServiceImpl {
}
```

然后我们按照下面的方式去使用它：

```java
@RestController
public class HelloWorldController {
    
    @Autowired
    private ServiceImpl serviceImpl;
    
    @RequestMapping(path = "hi", method = RequestMethod.GET)
    public String hi() {
        return "helloworld, service is : " + serviceImpl;
    };
}
```

结果，我们会发现，不管我们访问多少次http://localhost:8080/hi，访问的结果都是不变的，如下：

```
helloworld, service is :
com.spring.puzzle.class1.example3.error.ServiceImpl@4908af
```

- 案例解析

当一个属性成员 serviceImpl 声明为 @Autowired 后，那么在创建 HelloWorldController 这个 Bean 时，会先使用构造器反射出实例，然后来装配各个标记为 @Autowired 的属性成员（装配方法参考 AbstractAutowireCapableBeanFactory#populateBean）。

具体到执行过程，它会使用很多 BeanPostProcessor 来做完成工作，其中一种是
AutowiredAnnotationBeanPostProcessor，它会通过 DefaultListableBeanFactory#findAutowireCandidates 寻找到 ServiceImpl 类型的 Bean，然后设置给对应的属性（即 serviceImpl 成员）。

待我们寻找到要自动注入的 Bean 后，即可通过反射设置给对应的 field。这个 field 的执行只发生了一次，所以后续就固定起来了，它并不会因为 ServiceImpl 标记了 SCOPE_PROTOTYPE 而改变。

- 问题修正

通过上述源码分析，我们可以知道要修正这个问题，肯定是不能将 ServiceImpl 的 Bean 固定到属性上的，而应该是每次使用时都会重新获取一次。所以这里我提供了两种修正方式：

1. 自动注入 Context

```java
@RestController
public class HelloWorldController {
    
    @Autowired
    private ApplicationContext applicationContext;
    
    @RequestMapping(path = "hi", method = RequestMethod.GET)
    public String hi() {
        return "helloworld, service is : " + getServiceImpl();
    }
    
    public ServiceImpl getServiceImpl() {
        return applicationContext.getBean(ServiceImpl.class);
    }
}
```

2. 使用 Lookup 注解

```java
@RestController
public class HelloWorldController {

    @RequestMapping(path = "hi", method = RequestMethod.GET)
    public String hi(){
        return "helloworld, service is : " + getServiceImpl();
    }

    @Lookup
    public ServiceImpl getServiceImpl(){
        return null;
    }
}
```

首先，我们可以通过调试方式看下方法的执行，参考下图：

![image-20220715224641052](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207152246205.png)

从上图我们可以看出，我们最终的执行因为标记了 Lookup 而走入了 CglibSubclassingInstantiationStrategy.LookupOverrideMethodInterceptor，这个方法的关键实现参考 LookupOverrideMethodInterceptor#intercept。

我们的方法调用最终并没有走入案例代码实现的 return null 语句，而是通过 BeanFactory 来获取 Bean。所以从这点也可以看出，其实在我们的 getServiceImpl 方法实现中，随便怎么写都行，这不太重要。

# 02｜Spring Bean依赖注入常见错误（上）

这节课我们来聊聊 Spring @Autowired。

**案例 1：过多赠予，无所适从**

在使用 @Autowired 时，你或多或少都会遇过类似的错误：

```
required a single bean, but 2 were found
```

为了重现这个错误，我们可以先写一个案例来模拟下。

```java
@RestController
@Slf4j
@Validated
public class StudentController {
    @Autowired
    DataService dataService;
    
    @RequestMapping(path = "students/{id}", method = RequestMethod.DELETE)
    public void deleteStudent(@PathVariable("id") @Range(min = 1,max = 100) int id) {
        dataService.deleteStudent(id);
    }
}
```

其中 DataService 是一个接口，其实现依托于 Oracle，代码示意如下：

```java
public interface DataService {
    void deleteStudent(int id);
} 

@Repository
@Slf4j
public class OracleDataService implements DataService {
    @Override
    public void deleteStudent(int id) {
        log.info("delete student info maintained by oracle");
    }
}
```

截止目前，运行并测试程序是毫无问题的。直到某天，我们接到节约成本的需求，希望把一些部分非核心的业务从 Oracle 迁移到社区版 Cassandra，所以我们自然会先添加上一个新的 DataService 实现，代码如下：

```java
@Repository
@Slf4j
public class CassandraDataService implements DataService{
    @Override
    public void deleteStudent(int id) {
        log.info("delete student info maintained by cassandra");
    }
}
```

此时，程序就已经无法启动了，报错如下：

![image-20220719210803377](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207192108552.png)

- 案例解析

首先，我们先来了解下 @Autowired 发生的位置和核心过程。当一个 Bean 被构建时，核心包括两个基本步骤：

1. 执行 AbstractAutowireCapableBeanFactory#createBeanInstance 方法：通过构造器反射构造出这个 Bean，在此案例中相当于构建出 StudentController 的实例；
2. 执行 AbstractAutowireCapableBeanFactory#populate 方法：填充（即设置）这个 Bean，在本案例中，相当于设置 StudentController 实例中被 @Autowired 标记的 dataService 属性成员。

在步骤 2 中，“填充”过程的关键就是执行各种 BeanPostProcessor 处理器，关键代码如下：

```java
protected void populateBean(String beanName, RootBeanDefinition mbd, @Nullable BeanWrapper bw) {
  //省略非关键代码
  for (BeanPostProcessor bp : getBeanPostProcessors()) {
    if (bp instanceof InstantiationAwareBeanPostProcessor) {
      InstantiationAwareBeanPostProcessor ibp = (InstantiationAwareBeanPostProcessor) bp;
      PropertyValues pvsToUse = ibp.postProcessProperties(pvs, bw.getWrappedInstance(), beanName);
      //省略非关键代码
    }
  }
}
```

在上述代码执行过程中，因为 StudentController 含有标记为 Autowired 的成员属性 dataService，所以会使用到 AutowiredAnnotationBeanPostProcessor（BeanPostProcessor 中的一种）来完成“装配”过程：找出合适的 DataService 的 bean 并设置给
StudentController#dataService。如果深究这个装配过程，又可以细分为两个步骤：

1. 寻找出所有需要依赖注入的字段和方法，参考 AutowiredAnnotationBeanPostProcessor#postProcessProperties 中的代码行：

```java
InjectionMetadata metadata = findAutowiringMetadata(beanName, bean.getClass(), pvs);
```

2. 根据依赖信息寻找出依赖并完成注入，以字段注入为例，参考 AutowiredFieldElement#inject 方法：

```java
@Override
protected void inject(Object bean, @Nullable String beanName, @Nullable PropertyValues pvs)
    throws Throwable {
  Field field = (Field) this.member;
  Object value;
  //省略非关键代码
  try {
    DependencyDescriptor desc = new DependencyDescriptor(field, this.required);
    //寻找“依赖”，desc为"dataService"的DependencyDescriptor
    value = beanFactory.resolveDependency(desc, beanName, autowiredBeanNames, typeConverter);
  }
  //省略非关键代码
  if (value != null) {
    ReflectionUtils.makeAccessible(field);
    //装配“依赖”
    field.set(bean, value);
  }
}    
```

当我们根据 DataService 这个类型来找出依赖时，我们会找出 2 个依赖，分别为 CassandraDataService 和 OracleDataService。在这样的情况下，如果同时满足以下两个条件则会抛出本案例的错误：

1. 调用 determineAutowireCandidate 方法来选出优先级最高的依赖，但是发现并没有优先级可依据。具体选择过程可参考
   DefaultListableBeanFactory#determineAutowireCandidate。

   > 优先级的决策是先根据 @Primary 来决策，其次是 @Priority 决策，最后是根据 Bean 名字的严格匹配来决策。如果这些帮助决策优先级的注解都没有被使用，名字也不精确匹配，则返回 null，告知无法决策出哪种最合适。

2. @Autowired 要求是必须注入的（即 required 保持默认值为 true），或者注解的属性类型并不是可以接受多个 Bean 的类型，例如数组、Map、集合。这点可以参考
   DefaultListableBeanFactory#indicatesMultipleBeans 的实现。

- 问题修正

第一，我们可以通过使用标记 @Primary 的方式来让被标记的候选者有更高优先级，从而避免报错。

```java
@Repository
@Primary
@Slf4j
public class OracleDataService implements DataService{
  //省略非关键代码
}
```

但是这种方式并不一定符合业务需求。

第二，我们可以使用下面的方式去修改：

```java
@Autowired
DataService oracleDataService;
```

将属性名和 Bean 名字精确匹配，这样就可以让注入选择不犯难：需要 Oracle 时指定属性名为 oracleDataService，需要 Cassandra 时则指定属性名为 cassandraDataService。

第三，还可以采用 @Qualifier 来显式指定引用的是那种服务，例如采用下面的方式：

```java
@Autowired()
@Qualifier("cassandraDataService")
DataService dataService;
```

这种方式之所以能解决问题，在于它能让寻找出的 Bean 只有一个（即精确匹配），所以压根不会出现后面的决策过程，可以参考
DefaultListableBeanFactory#doResolveDependency。

**案例 2：显式引用 Bean 时首字母忽略大小写**

在使用 @Qualifier 时，我们有时候会犯另一个经典的小错误，就是我们可能会忽略 Bean 的名称首字母大小写。这里我们把校正后的案例稍稍变形如下：

```java
@Autowired
@Qualifier("CassandraDataService")
DataService dataService;
```

运行程序，我们会报错如下：

```
Exception encountered during context initialization - cancelling refresh attempt: 
org.springframework.beans.factory.UnsatisfiedDependencyException: Error
creating bean with name 'studentController': Unsatisfied dependency expressed
through field 'dataService'; nested exception is
org.springframework.beans.factory.NoSuchBeanDefinitionException: No
qualifying bean of type 'com.spring.puzzle.class2.example2.DataService'
available: expected at least 1 bean which qualifies as autowire candidate.
Dependency annotations:
{@org.springframework.beans.factory.annotation.Autowired(required=true),
@org.springframework.beans.factory.annotation.Qualifier(value=CassandraData
Service)}
```

这里我们很容易得出一个结论：对于 Bean 的名字，如果没有显式指明，就应该是类名，不过首字母应该小写。但是这个轻松得出的结论成立么？

不妨再测试下，假设我们需要支持 SQLite 这种数据库，我们定义了一个命名为 SQLiteDataService 的实现，然后借鉴之前的经验，我们很容易使用下面的代码来引用这个实现：

```java
@Autowired
@Qualifier("sQLiteDataService")
DataService dataService;
```

运行程序后，依然会出现之前的错误，而如果改成 SQLiteDataService，则运行通过了。这和之前的结论又矛盾了。所以，显式引用 Bean 时，首字母到底是大写还是小写呢？

- 案例解析

在这里，我们真正需要关心的问题是：不显式设置名字的 Bean，其默认名称首字母到底是大写还是小写呢？

BeanNameGenerator#generateBeanName 即用来产生 Bean 的名字。因为 DataService 的实现都是使用注解标记的，所以 Bean 名称的生成逻辑最终调用的其实是 AnnotationBeanNameGenerator#generateBeanName 这种实现方式，我们可以看下它的具体实现，代码如下：

```java
@Override
public String generateBeanName(BeanDefinition definition, BeanDefinitionRegistry registry) {
  if (definition instanceof AnnotatedBeanDefinition) {
    String beanName = determineBeanNameFromAnnotation((AnnotatedBeanDefiniti
    if (StringUtils.hasText(beanName)) {
    // Explicit bean name found.
      return beanName;
    }
  }
  // Fallback: generate a unique default bean name.
  return buildDefaultBeanName(definition, registry);
}
```

大体流程只有两步：看 Bean 有没有显式指明名称，如果有则用显式名称，如果没有则产生一个默认名称。在我们的案例中，是没有给 Bean 指定名字的，所以产生的 Bean 的名称就是生成的默认名称，查看默认名的产生方法 buildDefaultBeanName，其实现如下：

```java
protected String buildDefaultBeanName(BeanDefinition definition) {
  String beanClassName = definition.getBeanClassName();
  Assert.state(beanClassName != null, "No bean class name set");
  String shortClassName = ClassUtils.getShortName(beanClassName);
  return Introspector.decapitalize(shortClassName);
}
```

首先，获取一个简短的 ClassName，然后调用 Introspector#decapitalize 方法，设置首字母大写或小写，具体参考下面的代码实现：

```java
public static String decapitalize(String name) {
  if (name == null || name.length() == 0) {
    return name;
  }
  if (name.length() > 1 && Character.isUpperCase(name.charAt(1)) &&
      Character.isUpperCase(name.charAt(0))) {
    return name;
  }
  char chars[] = name.toCharArray();
  chars[0] = Character.toLowerCase(chars[0]);
  return new String(chars);
}
```

到这，我们很轻松地明白了前面两个问题出现的原因：如果一个类名是以两个大写字母开头的，则首字母不变，其它情况下默认首字母变成小写。

- 问题修正

如果 Bean 定义代码为：

```java
@Repository
@Slf4j
public class CassandraDataService implements DataService {
}
```

可以在引用处纠正首字母大小写问题：

```java
@Autowired
@Qualifier("cassandraDataService")
DataService dataService;
```

如果 Bean 引用代码为：

```java
@Autowired
@Qualifier("CassandraDataService")
DataService dataService;
```

可以通过显式指明 CassandraDataService 的 Bean 名称为 CassandraDataService 来纠正这个问题。

```java
@Repository("CassandraDataService")
@Slf4j
public class CassandraDataService implements DataService {
  //省略实现
}
```

**案例 3：引用内部类的 Bean 遗忘类名**

我们沿用上面的案例，稍微再添加点别的需求，例如我们需要定义一个内部类来实现一种新的 DataService，代码如下：

```java
public class StudentController {
  @Repository
  public static class InnerClassDataService implements DataService {
    @Override
    public void deleteStudent(int id) {
    //空实现
    }
  }
  //省略其他非关键代码
}
```

遇到这种情况，我们一般都会很自然地用下面的方式直接去显式引用这个 Bean：

```java
@Autowired
@Qualifier("innerClassDataService")
DataService innerClassDataService;
```

实际上这样仍然会报错“找不到 Bean”，这是为什么？

- 案例解析

实际上，我们遭遇的情况是“如何引用内部类的 Bean”。

在代码 AnnotationBeanNameGenerator#buildDefaultBeanName 中，有一行语句是对 class 名字的处理，代码如下：

```java
String shortClassName = ClassUtils.getShortName(beanClassName);
```

我们可以看下它的实现，参考 ClassUtils#getShortName 方法：

```java
public static String getShortName(String className) {
  Assert.hasLength(className, "Class name must not be empty");
  int lastDotIndex = className.lastIndexOf(PACKAGE_SEPARATOR);
  int nameEndIndex = className.indexOf(CGLIB_CLASS_SEPARATOR);
  if (nameEndIndex == -1) {
    nameEndIndex = className.length();
  }
  String shortName = className.substring(lastDotIndex + 1, nameEndIndex);
  shortName = shortName.replace(INNER_CLASS_SEPARATOR, PACKAGE_SEPARATOR);
  return shortName;
}
```

假设我们是一个内部类，例如下面的类名：

```java
com.spring.puzzle.class2.example3.StudentController.InnerClassDataService
```

在经过这个方法的处理后，我们得到的其实是下面这个名称：

```
StudentController.InnerClassDataService
```

最后经过 Introspector.decapitalize 的首字母变换，最终获取的 Bean 名称如下：

```
studentController.InnerClassDataService
```

所以我们在案例程序中，直接使用 innerClassDataService 自然找不到想要的 Bean。

- 问题修正

```java
@Autowired
@Qualifier("studentController.InnerClassDataService")
DataService innerClassDataService;
```

这个引用看起来有些许奇怪，但实际上是可以工作的，反而直接使用 innerClassDataService 来引用倒是真的不可行。

# 03｜Spring Bean 依赖注入常见错误（下）

在实际应用中，我们也会使用 @Value 等不太常见的注解来完成自动注入，同时也存在注入到集合、数组等复杂类型的场景。这些情况下，我们也会遇到一些问题。所以这一讲我们不妨来梳理下。

**@Value 和 @Autowired**

我们一般都会因为 @Value 常用于 String 类型的装配而误以为 @Value 不能用于非内置对象的装配，实际上这是一个常见的误区。例如，我们可以使用下面这种方式来 Autowired 一个属性成员：

```java
@Value("#{student}")
private Student student;

@Bean
public Student student(){
  Student student = createStudent(1, "xie");
  return student;
}
```

我们使用 @Value 更多是用来装配 String，而且它支持多种强大的装配方式，典型的方式参考下面的示例：

```java
//注册正常字符串
@Value("我是字符串")
private String text;

//注入系统参数、环境变量或者配置文件中的值
@Value("${ip}")
private String ip

//注入其他Bean属性，其中student为bean的ID，name为其属性
@Value("#{student.name}")
private String name;
```

**案例 1：@Value 没有注入预期的值**

那么在使用 @Value 时可能会遇到那些错误呢？这里分享一个最为典型的错误，即使用 @Value 可能会注入一个不是预期的值。

我们可以模拟一个场景，我们在配置文件 application.properties 配置了这样一个属性：

```properties
username=admin
password=pass
```

然后我们在一个 Bean 中，分别定义两个属性来引用它们：

```java
@RestController
@Slf4j
public class ValueTestController {
  @Value("${username}")
  private String username;
  @Value("${password}")
  private String password;
    
  @RequestMapping(path = "user", method = RequestMethod.GET)
  public String getUser(){
    return username + ":" + password;
  }
}
```

当我们去打印上述代码中的 username 和 password 时，我们会发现 password 正确返回了，但是 username 返回的并不是配置文件中指明的 admin，而是运行这段程序的计算机用户名。很明显，使用 @Value 装配的值没有完全符合我们的预期。

- 案例解析

对于 @Value，Spring 是如何根据 @Value 来查询“值”的。我们可以先通过方法 DefaultListableBeanFactory#doResolveDependency 来了解 @Value 的核心工作流程，代码如下：

```java
@Nullable
public Object doResolveDependency(DependencyDescriptor descriptor, @Nullable String beanName,
    @Nullable Set<String> autowiredBeanNames, @Nullable TypeConverter typeConverter) throw BeansException {
  //省略其他非关键代码
  Class<?> type = descriptor.getDependencyType();
  //寻找@Value
  Object value = getAutowireCandidateResolver().getSuggestedValue(descriptor);
  if (value != null) {
    if (value instanceof String) {
      //解析Value值
      String strVal = resolveEmbeddedValue((String) value);
      BeanDefinition bd = (beanName != null && containsBean(beanName) ? 
                           getMergedBeanDefinition(beanName) : null);
      value = evaluateBeanDefinitionString(strVal, bd);
    }
    //转化Value解析的结果到装配的类型
    TypeConverter converter = (typeConverter != null ? typeConverter : getTypeConvertor());
    try {
      return converter.convertIfNecessary(value, type, descriptor.getTypeConvertor());
    } catch (UnsupportedOperationException ex) {
      //异常处理
    }
  }
//省略其他非关键代码
}
```

结合我们的案例，很明显问题应该发生在解析 Value 指定字符串过程，执行过程参考下面的关键代码行：

```java
String strVal = resolveEmbeddedValue((String) value);
```

这里其实是在解析嵌入的值，实际上就是“替换占位符”工作。具体而言，它采用的是 PropertySourcesPlaceholderConfigurer 根据 PropertySources 来替换。不过当使用 ${username} 来获取替换值时，其最终执行的查找并不是局限在 application.property 文件中的。

![image-20220720213223561](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207202132912.png)

而具体的查找执行，我们可以通过下面的代码 （PropertySourcesPropertyResolver#getProperty）来获取它的执行方式：

```java
@Nullable
protected <T> T getProperty(String key, Class<T> targetValueType, boolean resolveNestedPlaceholders) {
  if (this.propertySources != null) {
    for (PropertySource<?> propertySource : this.propertySources) {
      Object value = propertySource.getProperty(key);
      if (value != null) {
        //查到value即退出
        return convertValueIfNecessary(value, targetValueType);
      }
    }
  }
  return null;
}
```

我们查看 systemEnvironment 这个源，会发现刚好有一个 username 和我们是重合的。

![image-20220720213543389](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207202135551.png)

- 问题修正

```java
user.name=admin
user.password=pass
```

**案例 2：错乱的注入集合**

假设我们存在这样一个需求：存在多个学生 Bean，我们需要找出来，并存储到一个 List 里面去。多个学生 Bean 的定义如下：

```java
@Bean
public Student student1() {
  return createStudent(1, "xie");
}

@Bean
public Student student2(){
  return createStudent(2, "fang");
}

private Student createStudent(int id, String name) {
  Student student = new Student();
  student.setId(id);
  student.setName(name);
  return student;
}
```

有了集合类型的自动注入后，我们就可以把零散的学生 Bean 收集起来了，代码示例如下：

```java
@RestController
@Slf4j
public class StudentController {
    
  private List<Student> students;

  public StudentController(List<Student> students) {
    this.students = students;
  }
  
  @RequestMapping(path = "students", method = RequestMethod.GET)
  public String listStudents() {
    return students.toString();
  }
}
```

通过上述代码，我们就可以完成集合类型的注入工作，输出结果如下：

```
[Student(id=1, name=xie), Student(id=2, name=fang)]
```

然而，当我们持续增加一些 student 时，可能就不喜欢用这种方式来注入集合类型了，而是倾向于用下面的方式去完成注入工作：

```java
@Bean
public List<Student> students(){
  Student student3 = createStudent(3, "liu");
  Student student4 = createStudent(4, "fu");
  return Arrays.asList(student3, student4);
}
```

为了好记，这里我们不妨将上面这种方式命名为“直接装配方式”，而将之前的那种命名为“收集方式”。实际上，如果这两种方式是非此即彼的存在，自然没有任何问题，都能玩转。但是如果我们不小心让这 2 种方式同时存在了，结果会怎样？

- 案例解析

对于收集装配风格，Spring 使用的是 DefaultListableBeanFactory#resolveMultipleBeans 来完成装配工作。大体过程如下：

1. 获取集合类型的元素类型

针对本案例，目标类型定义为 List<Student> students，所以元素类型为 Student，获取
的具体方法参考代码行：

```java
Class<?> elementType = descriptor.getResolvableType().asCollection().resolveGeneric();
```

2. 根据元素类型，找出所有的 Bean

有了上面的元素类型，即可根据元素类型来找出所有的 Bean，关键代码行如下：

```java
Map<String, Object> matchingBeans = findAutowireCandidates(beanName, elementType, new MultiElementDescriptor(descriptor));
```

3. 将匹配的所有的 Bean 按目标类型进行转化

在本案例中，我们就需要把它转化为 List，转化的关键代码如下：

```java
Object result = converter.convertIfNecessary(matchingBeans.values(), type);
```

如果我们继续深究执行细节，就可以知道最终是转化器 CollectionToCollectionConverter 来完成这个转化过程。

我们再来看下直接装配方式的执行过程，实际上这步在前面的课程中我们就提到过（即 DefaultListableBeanFactory#findAutowireCandidates 方法执行）。

了解了这两种方式，我们再来思考这两种方式的关系：当同时满足这两种装配方式时，Spring 是如何处理的？这里我们可以参考方法 DefaultListableBeanFactory#doResolveDependency 的几行关键代码，代码如下：

```java
Object multipleBeans = resolveMultipleBeans(descriptor, beanName, autowiredBeanNames, typeConverter);
if (multipleBeans != null) {
  return multipleBeans;
}
Map<String, Object> matchingBeans = findAutowireCandidates(beanName, type, descriptor);
```

当使用收集装配方式来装配时，能找到任何一个对应的 Bean，则返回，如果一个都没有找到，才会采用直接装配的方式。

- 问题修正

我们可以使用直接装配的方式去修正问题，代码如下：

```java
@Bean
public List<Student> students() {
  Student student1 = createStudent(1, "xie");
  Student student2 = createStudent(2, "fang");
  Student student3 = createStudent(3, "liu");
  Student student4 = createStudent(4, "fu");
  return Arrays.asList(student1，student2，student3, student4);
}
```

也可以使用收集方式来修正问题时，代码如下：

```java
@Bean
public Student student1() {
  return createStudent(1, "xie");
}

@Bean
public Student student2() {
  return createStudent(2, "fang");
}

@Bean
public Student student3() {
  return createStudent(3, "liu");
}

@Bean
public Student student4() {
  return createStudent(4, "fu");
}
```











