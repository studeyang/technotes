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

# 04｜Spring Bean生命周期常见错误

这节课我们来聊一聊 Spring Bean 的初始化过程及销毁过程中的一些问题。

**案例 1：构造器内抛空指针异常**

在构建宿舍管理系统时，有 LightMgrService 来管理 LightService，从而控制宿舍灯的开启和关闭。我们希望在 LightMgrService 初始化时能够自动调用 LightService 的 check 方法来检查所有宿舍灯的电路是否正常，代码如下：

```java
@Component
public class LightMgrService {
    
  @Autowired
  private LightService lightService;
    
  public LightMgrService() {
    lightService.check();
  }
    
}
```

我们在 LightMgrService 的默认构造器中调用了通过 @Autoware 注入的成员变量 LightService 的 check 方法：

```java
@Service
public class LightService {
    
  public void start() {
    System.out.println("turn on all lights");
  }
    
  public void shutdown() {
    System.out.println("turn off all lights");
  }
    
  public void check() {
    System.out.println("check all lights");
  }
    
}
```

然而，程序启动后报出 NullPointerException，错误示例如下：

![image-20220721213349700](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207212133941.png)

- 案例解析

上面出错的原因是我们对 Spring 类初始化过程没有足够的了解。下面这张时序图描述了 Spring 启动时的一些关键结点：

![下载](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207212124231.png)

这个图可以分为三部分：

第一部分，将一些必要的系统类，比如 Bean 的后置处理器类，注册到 Spring 容器，其中就包括我们这节课关注的 CommonAnnotationBeanPostProcessor 类；

第二部分，将这些后置处理器实例化，并注册到 Spring 的容器中；

第三部分，实例化所有用户定制类，调用后置处理器进行辅助装配、类初始化等等。

我们重点看下第三部分，即 Spring 初始化单例类的一般过程，基本都是 getBean() -> doGetBean() -> getSingleton()，如果发现 Bean 不存在，则调用 createBean() -> doCreateBean() 进行实例化。

doCreateBean() 的源代码如下：

```java
protected Object doCreateBean(final String beanName, 
                              final RootBeanDefinition mbd, 
                              final @Nullable Object[] args) 
    throws BeanCreationException {
  //省略非关键代码
  if (instanceWrapper == null) {
    instanceWrapper = createBeanInstance(beanName, mbd, args);
  }
  final Object bean = instanceWrapper.getWrappedInstance();
  //省略非关键代码
  Object exposedObject = bean;
  try {
    populateBean(beanName, mbd, instanceWrapper);
    exposedObject = initializeBean(beanName, exposedObject, mbd);
  }
  catch (Throwable ex) {
    //省略非关键代码
  }
}
```

上述代码完整地展示了 Bean 初始化的三个关键步骤：createBeanInstance、populateBean、initializeBean，分别对应实例化 Bean，注入 Bean 依赖，以及初始化 Bean。

- 问题修正

通过源码分析，现在我们知道了问题的根源，就是在于使用 @Autowired 直接标记在成员属性上而引发的装配行为是发生在构造器执行之后的。所以这里我们可以通过下面这种修订方法来纠正这个问题：

```java
@Component
public class LightMgrService {
 
    private LightService lightService;
    
    public LightMgrService(LightService lightService) {
        this.lightService = lightService;
        lightService.check();
    }
    
}
```

当使用上面的代码时，构造器参数 LightService 会被自动注入 LightService 的 Bean，从而在构造器执行时，不会出现空指针。可以说，使用构造器参数来隐式注入是一种 Spring 最佳实践，因为它成功地规避了案例 1 中的问题。

**案例 2：意外触发 shutdown 方法**

LightService 的实现，它包含了 shutdown 方法，负责关闭所有的灯，关键代码如下：

```java
@Service
public class LightService {
    //省略其他非关键代码
    public void shutdown() {
        System.out.println("shutting down all lights");
    }
    //省略其他非关键代码
}
```

随着业务的需求变化，我们可能会去掉 @Service 注解，使用另外一种产生 Bean 的方式：

```java
@Configuration
public class BeanConfiguration {
    @Bean
    public LightService getTransmission() {
        return new LightService();
    }
}
```

我们现在让 Spring 启动完成后立马关闭当前 Spring 上下文。这样等同于模拟宿舍管理系统的启停：

```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        ConfigurableApplicationContext context = SpringApplication.run(Application.class);
        context.close();
    }
}
```

运行这段代码后，我们可以看到控制台上打印了 shutting down all lights。显然 shutdown 方法未按照预期被执行了。

- 案例解析

通过调试，我们发现只有通过使用 Bean 注解注册到 Spring 容器的对象，才会在 Spring 容器被关闭的时候自动调用 shutdown 方法，而使用 @Component 将当前类自动注入到 Spring 容器时，shutdown 方法则不会被自动执行。

我们可以尝试到 Bean 注解类的代码中去寻找一些线索，可以看到属性 destroyMethod 有非常大段的注释，基本上解答了我们对于这个问题的大部分疑惑。

使用 Bean 注解的方法所注册的 Bean 对象，如果用户不设置 destroyMethod 属性，则其属性值为 AbstractBeanDefinition.INFER_METHOD。此时 Spring 会检查当前 Bean 对象的原始类中是否有名为 shutdown 或者 close 的方法，如果有，此方法会被 Spring 记录下来，并在容器被销毁时自动执行。

- 问题修正

如果一定要定义名为 close 或者 shutdown 方法，也可以通过将 Bean 注解内 destroyMethod 属性设置为空的方式来解决这个问题。

```java
@Configuration
public class BeanConfiguration {
    @Bean(destroyMethod="")
    public LightService getTransmission(){
        return new LightService();
    }
}
```

# 05｜Spring AOP 常见错误（上）

AOP 是日志记录、监控管理、性能统计、异常处理、权限管理、统一认证等各个方面被广泛使用的技术。

我们之所以能无感知地在容器对象方法前后任意添加代码片段，那是由于 Spring 在运行期帮我们把切面中的代码逻辑动态“织入”到了容器对象方法内，所以说 AOP 本质上就是一个代理模式。然而在使用这种代理模式时，我们常常会用不好，那么这节课我们就来解析下有哪些常见的问题，以及背后的原理是什么。

**案例 1：this 调用的当前类方法无法被拦截**

假设我们正在开发一个宿舍管理系统，这个模块包含一个负责电费充值的类 ElectricService，它含有一个充电方法 charge()：

```java
@Service
public class ElectricService {
    public void charge() throws Exception {
        System.out.println("Electric charging ...");
        this.pay();
    }
    public void pay() throws Exception {
        System.out.println("Pay with alipay ...");
        Thread.sleep(1000);
    }
}
```

因为支付宝支付 pay() 是第三方接口，我们需要记录下接口调用时间。这时候我们就引入了一个 @Around 的增强 ，分别记录在 pay() 方法执行前后的时间，并计算出执行 pay() 方法的耗时。

```java
@Aspect
@Service
@Slf4j
public class AopConfig {
@Around("execution(* com.spring.puzzle.class5.example1.ElectricService.pay())")
    public void recordPayPerformance(ProceedingJoinPoint joinPoint) throws Throwable {
        long start = System.currentTimeMillis();
        joinPoint.proceed();
        long end = System.currentTimeMillis();
        System.out.println("Pay method time cost（ms）: " + (end - start));
    }
}
```

最后我们再通过定义一个 Controller 来提供电费充值接口，定义如下：

```java
@RestController
public class HelloWorldController {
    @Autowired
    ElectricService electricService;
    
    @RequestMapping(path = "charge", method = RequestMethod.GET)
    public void charge() throws Exception {
        electricService.charge();
    }
}
```

完成代码后，我们访问上述接口，会发现这段计算时间的切面并没有执行到，输出日志如下：

```
Electric charging ...
Pay with alipay ...
```

- 案例解析

我们可以从源码中找到真相。首先来设置个断点，调试看看 this 对应的对象是什么样的：

![image-20220722220732765](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207222207979.png)

可以看到，this 对应的就是一个普通的 ElectricService 对象，并没有什么特别的地方。再看看在 Controller 层中自动装配的 ElectricService 对象是什么样：

![image-20220722220804301](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207222208453.png)

可以看到，这是一个被 Spring 增强过的 Bean。而 this 对应的对象只是一个普通的对象，并没有做任何额外的增强。

为什么 this 引用的对象只是一个普通对象呢？这还要从 Spring AOP 增强对象的过程来看。我们具体看下创建代理对象的过程。先来看下调用栈：

![image-20220722221230436](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207222212593.png)

创建代理对象的时机就是创建一个 Bean 的时候，而创建的的关键工作其实是由 AnnotationAwareAspectJAutoProxyCreator 完成的。它本质上是一种 BeanPostProcessor。所以它的执行是在完成原始 Bean 构建后的初始化 Bean（initializeBean）过程中。

- 问题修正

从上述案例解析中，我们知道，只有引用的是被动态代理创建出来的对象，才会被 Spring 增强，具备 AOP 该有的功能。那什么样的对象具备这样的条件呢？

有两种。一种是被 @Autowired 注解的，于是我们的代码可以改成这样，即通过 @Autowired 的方式，在类的内部，自己引用自己：

```java
@Service
public class ElectricService {
    @Autowired
    ElectricService electricService;
    
    public void charge() throws Exception {
        System.out.println("Electric charging ...");
        //this.pay();
        electricService.pay();
    }
    
    public void pay() throws Exception {
        System.out.println("Pay with alipay ...");
        Thread.sleep(1000);
    }
}
```

另一种方法就是直接从 AopContext 获取当前的 Proxy。那你可能会问了，AopContext 是什么？简单说，它的核心就是通过一个 ThreadLocal 来将 Proxy 和线程绑定起来，这样就可以随时拿出当前线程绑定的 Proxy。

不过使用这种方法有个小前提，就是需要在 @EnableAspectJAutoProxy 里加一个配置项 exposeProxy = true，表示将代理对象放入到 ThreadLocal，这样才可以直接通过 AopContext.currentProxy() 的方式获取到，否则会报错如下：

![image-20220722221901639](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207222219794.png)

按这个思路，我们修改下相关代码：

```java
@SpringBootApplication
@EnableAspectJAutoProxy(exposeProxy = true)
public class Application {
    // 省略非关键代码
}
```

业务代码如下：

```java
@Service
public class ElectricService {
    public void charge() throws Exception {
        System.out.println("Electric charging ...");
        ElectricService electric = ((ElectricService) AopContext.currentProxy());
        electric.pay();
    }
    public void pay() throws Exception {
        System.out.println("Pay with alipay ...");
        Thread.sleep(1000);
    }
}
```

**案例 2：直接访问被拦截类的属性抛空指针异常**

接上一个案例，在宿舍管理系统中，我们使用了 charge() 方法进行支付。在统一结算的时候我们会用到一个管理员用户付款编号。

```java
@Service
public class AdminUserService {
    public final User adminUser = new User("202101166");
    
    public void login() {
        System.out.println("admin user login...");
    }
}
```

ElectricService 类在电费充值时，需要管理员登录并使用其编号进行结算。完整代码如下：

```java
@Service
public class ElectricService {
    
    @Autowired
    private AdminUserService adminUserService;
    
    public void charge() throws Exception {
        System.out.println("Electric charging ...");
        this.pay();
    }
    
    public void pay() throws Exception {
        adminUserService.login();
        String payNum = adminUserService.adminUser.getPayNum();
        System.out.println("User pay num : " + payNum);
        System.out.println("Pay with alipay ...");
        Thread.sleep(1000);
    }
}
```

代码完成后，执行 charge() 操作，一切正常。

```
Electric charging ...
admin user login...
User pay num : 202101166
Pay with alipay ...
```

由于安全需要，管理员在登录时，需要记录一行日志以便于以后审计管理员操作。所以我们添加一个 AOP 相关配置类，具体如下：

```java
@Aspect
@Service
@Slf4j
public class AopConfig {
    @Before("execution(* com.spring.puzzle.class5.example2.AdminUserService.login(..))")
    public void logAdminLogin(JoinPoint pjp) throws Throwable {
        System.out.println("! admin login ...");
    }
}
```

添加这段代码后，我们执行 charge() 操作，发现不仅没有相关日志，而且在执行下面这一行代码的时候直接抛出了 NullPointerException：

```java
String payNum = dminUserService.user.getPayNum();
```

- 案例解析

我们先 debug 一下，来看看加入 AOP 后调用的对象是什么样子。

![image-20220725213318634](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207252133846.png)

可以看出，加入 AOP 后，我们的对象已经是一个代理对象了，并且属性 adminUser 确实为 null。

为什么会这样？

正常情况下，AdminUserService 只是一个普通的对象，而 AOP 增强过的则是一个 AdminUserService$$EnhancerBySpringCGLIB$$xxxx。这个类实际上是 AdminUserService 的一个子类。它会 overwrite 所有 public 和 protected 方法，并在内部将调用委托给原始的 AdminUserService 实例。

从具体实现角度看，CGLIB 中 AOP 的实现是基于 org.springframework.cglib.proxy 包中 Enhancer 和 MethodInterceptor 两个接口来实现的。整个过程，可以概括为三个步骤：

1. 定义自定义的 MethodInterceptor 负责委托方法执行；
2. 创建 Enhancer 并设置 Callback 为上述 MethodInterceptor；
3. enhancer.create() 创建代理。

以 CGLIB 的 Proxy 的实现类 CglibAopProxy 为例，来看看具体的流程：

```java
public Object getProxy(@Nullable ClassLoader classLoader) {
    // 省略非关键代码
    // 创建及配置 Enhancer
    Enhancer enhancer = createEnhancer();
    // 省略非关键代码
    // 获取Callback：包含DynamicAdvisedInterceptor，亦是MethodInterceptor
    Callback[] callbacks = getCallbacks(rootClass);
    // 省略非关键代码
    // 生成代理对象并创建代理（设置 enhancer 的 callback 值）
    return createProxyClassAndInstance(enhancer, callbacks);
    // 省略非关键代码
}
```

上述代码中的几个关键步骤大体符合之前提及的三个步骤，其中最后一步一般都会执行到 CglibAopProxy 子类 ObjenesisCglibAopProxy 的 createProxyClassAndInstance() 方法：

```java
protected Object createProxyClassAndInstance(Enhancer enhancer, Callback[] callbacks) {
    //创建代理类Class
    Class<?> proxyClass = enhancer.createClass();
    Object proxyInstance = null;
    //spring.objenesis.ignore默认为false
    //所以objenesis.isWorthTrying()一般为true
    if (objenesis.isWorthTrying()) {
        try {
            // 创建实例
            proxyInstance = objenesis.newInstance(proxyClass, enhancer.getUseCache());
        }
        catch (Throwable ex) {
            // 省略非关键代码
        }
    }
    if (proxyInstance == null) {
        // 尝试普通反射方式创建实例
        try {
            Constructor<?> ctor = (this.constructorArgs != null ?
                                   proxyClass.getDeclaredConstructor(this.constructorArgTypes) :
                                   proxyClass.getDeclaredConstructor());
            ReflectionUtils.makeAccessible(ctor);
            proxyInstance = (this.constructorArgs != null ?
                             ctor.newInstance(this.constructorArgs) : ctor.newInstance());
            //省略非关键代码
        }
    }
    // 省略非关键代码
    ((Factory) proxyInstance).setCallbacks(callbacks);
    return proxyInstance;
}
```

这里我们可以了解到，Spring 会默认尝试使用 objenesis 方式实例化对象，如果失败则再次尝试使用常规方式实例化对象。现在，我们可以进一步查看 objenesis 方式实例化对象的流程。

![image-20220725215756940](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207252157098.png)

参照上述截图所示调用栈，objenesis 方式最后使用了 JDK 的 ReflectionFactory.newConstructorForSerialization() 完成了代理对象的实例化。这种方式创建出来的对象是不会初始化类成员变量的。

- 问题修正

既然是无法直接访问被拦截类的成员变量，那我们就换个方式，在 AdminUserService 里写个 getUser() 方法，从内部访问获取变量。

```java
public User getUser() {
    return user;
}
```

在 ElectricService 里通过 getUser() 获取 User 对象：

```java
String payNum = adminUserService.getAdminUser().getPayNum();
```

运行下来，一切正常，可以看到管理员登录日志了：

```
Electric charging ...
! admin login ...
admin user login...
User pay num : 202101166
Pay with alipay ...
```

你有没有产生另一个困惑呢？既然代理类的类属性不会被初始化，那为什么可以通过在 AdminUserService 里写个 getUser() 方法来获取代理类实例的属性呢？

我们再次回顾 createProxyClassAndInstance 的代码逻辑，创建代理类后，我们会调用 setCallbacks 来设置拦截后需要注入的代码：

```java
protected Object createProxyClassAndInstance(Enhancer enhancer, Callback[] callbacks) {
    Class<?> proxyClass = enhancer.createClass();
    Object proxyInstance = null;
    if (objenesis.isWorthTrying()) {
        try {
            roxyInstance = objenesis.newInstance(proxyClass, enhancer.getUseCache());
        }
        // 省略非关键代码
        ((Factory) proxyInstance).setCallbacks(callbacks);
        return proxyInstance;
}
```

通过代码调试和分析，我们可以得知上述的 callbacks 中会存在一种服务于 AOP 的 DynamicAdvisedInterceptor，它的接口是 MethodInterceptor（callback 的子接口），实现了拦截方法 intercept()。

说到这里，我们已经解决了问题。但其实你改变一个属性，也可以让产生的代理对象的属性值不为 null。例如修改启动参数 spring.objenesis.ignore 如下：

![image-20220725220616162](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207252206387.png)

此时再调试程序，你会发现 adminUser 已经不为 null 了：

![image-20220725220635292](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207252206494.png)

# 06｜Spring AOP常见错误（下）

当一个系统采用的切面越来越多时，因为执行顺序而导致的问题便会逐步暴露出来，下面我们就重点看一下。

**案例 1：错乱混合不同类型的增强**

这个宿舍管理系统维护了一个电费充值模块，它包含了一个负责电费充值的类 ElectricService，还有一个充电方法 charge()：

```java
@Service
public class ElectricService {
    public void charge() throws Exception {
        System.out.println("Electric charging ...");
    }
}
```

为了在执行 charge() 之前，鉴定下调用者的权限，我们增加了针对于 Electric 的切面类 AopConfig，其中包含一个 @Before 增强。

```java
@Aspect
@Service
@Slf4j
public class AspectService {
    @Before("execution(* com.spring.puzzle.class6.example1.ElectricService.charge())");
    public void checkAuthority(JoinPoint pjp) throws Throwable {
        System.out.println("validating user authority");
        Thread.sleep(1000);
    }
}
```

执行后，得到以下 log：

```
validating user authority
Electric charging ...
```

一段时间后，由于业务发展，ElectricService 中的 charge() 逻辑变得更加复杂了，我们需要仅仅针对 ElectricService 的 charge() 做性能统计。

```java
@Aspect
@Service
public class AopConfig {
    
    @Before("execution(* com.spring.puzzle.class6.example1.ElectricService.charge())");
    public void checkAuthority(JoinPoint pjp) throws Throwable {
        System.out.println("validating user authority");
        Thread.sleep(1000);
    }
    
    @Around("execution(* com.spring.puzzle.class6.example1.ElectricService.charge())");
    public void recordPerformance(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        pjp.proceed();
        long end = System.currentTimeMillis();
        System.out.println("charge method time cost: " + (end - start));
    }
}
```

执行后得到日志如下：

```
validating user authority
Electric charging ...
charge method time cost 1022 (ms)
```

通过性能统计打印出的日志，我们可以得知 charge() 执行时间超过了 1 秒钟。然而，该方法仅打印了一行日志，它的执行不可能需要这么长时间。

- 案例解析

针对这个案例而言，当同一个切面（Aspect）中同时包含多个不同类型的增强时（Around、Before、After、AfterReturning、AfterThrowing 等），它们的执行是有顺序的。那么顺序如何？我们不妨来解析下。

Spring 初始化单例类的一般过程，基本都是 getBean()->doGetBean()->getSingleton()，如果发现 Bean 不存在，则调用 createBean()->doCreateBean() 进行实例化。

而如果我们的代码里使用了 Spring AOP，doCreateBean() 最终会返回一个代理对象。（参考 AbstractAutoProxyCreator#createProxy）

最终的排序结果依次是 Around.class, Before.class, After.class, AfterReturning.class, AfterThrowing.class。（ReflectiveAspectJAdvisorFactory  类中的静态方法块）

```java
static {
    //第一个比较器，用来按照增强类型排序
    Comparator<Method> adviceKindComparator = new ConvertingComparator<>(
        new InstanceComparator<>(
            Around.class, Before.class, After.class, AfterReturning.class, 
            AfterThrowing.class),
        (Converter<Method, Annotation>) method -> {
            AspectJAnnotation<?> annotation =
                AbstractAspectJAdvisorFactory.findAspectJAnnotationOnMethod(method);
            return (annotation != null ? annotation.getAnnotation() : null);
        });
       
    //第二个比较器，用来按照方法名排序
    Comparator<Method> methodNameComparator = new ConvertingComparator<>(Method::getName);
    METHOD_COMPARATOR = adviceKindComparator.thenComparing(methodNameComparator
}
```

- 问题修正

从上述案例解析中，我们知道 Around 类型的增强被调用的优先级高于 Before 类型的增强，所以上述案例中性能统计所花费的时间，包含权限验证的时间。

我们可以按照下面的思路来修改：

1. 将 ElectricService.charge() 的业务逻辑全部移动到 doCharge()，在 charge() 中调用 doCharge()；
2. 性能统计只需要拦截 doCharge()；
3. 权限统计增强保持不变，依然拦截 charge()。

ElectricService 类代码更改如下：

```java
@Service
public class ElectricService {
    public void charge() {
        doCharge();
    }
    public void doCharge() {
        System.out.println("Electric charging ...");
    }
}
```

切面代码更改如下：

```java
@Aspect
@Service
public class AopConfig {
    
    @Before("execution(* com.spring.puzzle.class6.example1.ElectricService.charge())")
    public void checkAuthority(JoinPoint pjp) throws Throwable {
        System.out.println("validating user authority");
        Thread.sleep(1000);
    }
    
    @Around("execution(* com.spring.puzzle.class6.example1.ElectricService.doCharge())")
    public void recordPerformance(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        pjp.proceed();
        long end = System.currentTimeMillis();
        System.out.println("charge method time cost: " + (end - start));
    }
}
```

**案例 2：错乱混合同类型增强**

那如果同一个切面里的多个增强方法其增强都一样，那调用顺序又如何呢？我们继续看下一个案例。

业务逻辑类 ElectricService 不变：

```java
@Service
public class ElectricService {
    public void charge() {
        System.out.println("Electric charging ...");
    }
}
```

切面类 AspectService 包含两个方法，都是 Before 类型增强。

```java
@Aspect
@Service
public class AopConfig {
    @Before("execution(* com.spring.puzzle.class5.example2.ElectricService.charge())")
    public void logBeforeMethod(JoinPoint pjp) throws Throwable {
        System.out.println("step into ->"+pjp.getSignature());
    }
    
    @Before("execution(* com.spring.puzzle.class5.example2.ElectricService.charge())")
    public void validateAuthority(JoinPoint pjp) throws Throwable {
        throw new RuntimeException("authority check failed");
    }
}
```

我们对代码的执行预期为：当鉴权失败时，由于 ElectricService.charge() 没有被调用，那么 logBeforeMethod() 不应该被调用。

但是，执行结果却如下：

```
step into ->void com.spring.puzzle.class6.example2.Electric.charge()
Exception in thread "main" java.lang.RuntimeException: authority check failed
```

这里我们就需要搞清楚一个问题：当同一个切面包含多个同一种类型的多个增强，且修饰的都是同一个方法时，这多个增强的执行顺序是怎样的？

- 案例解析

```java
static {
    //第一个比较器，用来按照增强类型排序
    ......
    //第二个比较器，用来按照方法名排序
    Comparator<Method> methodNameComparator = new ConvertingComparator<>(Method::getName);
    METHOD_COMPARATOR = adviceKindComparator.thenComparing(methodNameComparator
}
```

如果两个方法名长度相同，则依次比较每一个字母的 ASCII 码，ASCII 码越小，排序越靠前；若长度不同，且短的方法名字符串是长的子集时，短的排序靠前。

- 问题修正

在同一个切面配置类中，针对同一个方法存在多个同类型增强时，其执行顺序仅和当前增强方法的名称有关。

```java
@Aspect
@Service
public class AopConfig {
    
    @Before("execution(* com.spring.puzzle.class6.example2.ElectricService.charge())")
    public void logBeforeMethod(JoinPoint pjp) throws Throwable {
        System.out.println("step into ->"+pjp.getSignature());
    }
    
    @Before("execution(* com.spring.puzzle.class6.example2.ElectricService.charge())")
    public void checkAuthority(JoinPoint pjp) throws Throwable {
        throw new RuntimeException("authority check failed");
    }
}
```

我们可以将原来的 validateAuthority() 改为 checkAuthority()，这种情况下，对增强 （Advisor）的排序，其实最后就是在比较字符 l 和 字符 c。显然易见，checkAuthority() 的排序会靠前，从而被优先执行，最终问题得以解决。

# 07｜Spring事件常见错误

Spring 事件的设计比较简单。说白了，就是监听器设计模式在 Spring 中的一种实现，参考下图：

![image-20220727220050768](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207272200105.png)

从图中我们可以看出，Spring 事件包含以下三大组件。

1. 事件（Event）：用来区分和定义不同的事件，在 Spring 中，常见的如 ApplicationEvent 和 AutoConfigurationImportEvent，它们都继承于 java.util.EventObject。

2. 事件广播器（Multicaster）：负责发布上述定义的事件。例如，负责发布 ApplicationEvent 的 ApplicationEventMulticaster 就是 Spring 中一种常见的广播器。

3. 事件监听器（Listener）：负责监听和处理广播器发出的事件，例如 ApplicationListener 就是用来处理 ApplicationEventMulticaster 发布的 ApplicationEvent，它继承于 JDK 的 EventListener。

   > 我们可以看下它的定义来验证这个结论：
   >
   > ```java
   > public interface ApplicationListener<E extends ApplicationEvent> extends EventListener {
   >     void onApplicationEvent(E event);
   > }
   > ```

**案例 1：试图处理并不会抛出的事件**

在很多 Spring 初级开发者眼中，Spring 运转的核心就是一个 Context 的维护，那么启动 Spring 自然会启动 Context。

```java
@Slf4j
@Component
public class MyContextStartedEventListener implements ApplicationListener<ContextStartedEvent> {
    public void onApplicationEvent(final ContextStartedEvent event) {
        log.info("{} received: {}", this.toString(), event);
    }
}
```

但是当我们启动 Spring Boot 后，会发现并不会拦截到这个事件，如何理解这个错误呢？

- 案例解析

在 Spring Boot 中，这个事件的抛出只发生在一处，即位于方法 AbstractApplicationContext#start 中。

```java
@Override
public void start() {
    getLifecycleProcessor().start();
    publishEvent(new ContextStartedEvent(this));
}
```

只有上述方法被调用，才会抛出 ContextStartedEvent，但是这个方法在 Spring Boot 启动时会被调用么？我们可以查看 Spring 启动方法中围绕 Context 的关键方法调用，代码如下：

```java
public ConfigurableApplicationContext run(String... args) {
    //省略非关键代码
    context = createApplicationContext();
    //省略非关键代码
    prepareContext(context, environment, listeners, applicationArguments, printBanner);
    refreshContext(context);
    //省略非关键代码
    return context;
}
```

我们发现围绕 Context、Spring Boot 的启动只做了两个关键工作：创建 Context 和 Refresh Context。其中 Refresh 的关键代码如下：

```java
protected void refresh(ApplicationContext applicationContext) {
    Assert.isInstanceOf(AbstractApplicationContext.class, applicationContext);
    ((AbstractApplicationContext) applicationContext).refresh();
}
```

很明显，Spring 启动最终调用的是 AbstractApplicationContext#refresh，并不是 AbstractApplicationContext#start，ContextStartedEvent 自然不会被抛出。

- 问题修正

如果我们确实想在 Spring Boot 启动时拦截一个启动事件，可以把监听事件的类型修改成真正发生的事件即可：

```java
@Component
public class MyContextRefreshedEventListener implements ApplicationListener<ontextRefreshedEvent> {
    public void onApplicationEvent(final ContextRefreshedEvent event) {
        log.info("{} received: {}", this.toString(), event);
    }
}
```

ContextRefreshedEvent 的抛出可以参考方法 AbstractApplicationContext#finishRefresh。

**案例 2：监听事件的体系不对**

```java
@Slf4j
@Component
public class MyApplicationEnvironmentPreparedEventListener implements 
    ApplicationContext<ApplicationEnvironmentPreparedEvent> {
    public void onApplicationEvent(final ApplicationEnvironmentPreparedEvent event) {
        log.info("{} received: {}", this.toString(), event);
    }
}
```

这里我们试图处理 ApplicationEnvironmentPreparedEvent。这个事件在 Spring 中是由 EventPublishingRunListener#environmentPrepared 方法抛出，代码如下：

```java
@Override
public void environmentPrepared(ConfigurableEnvironment environment) {
    this.initialMulticaster
        .multicastEvent(new ApplicationEnvironmentPreparedEvent(this.application));
}
```

但是我们真正去运行程序时会发现，监听器的处理并不执行，这又是为何？

- 案例解析

这是在 Spring 事件处理上非常容易犯的一个错误，即监听的体系不一致。

我们首先来看下关于 ApplicationEnvironmentPreparedEvent 的处理相关的两大组件。

1. 广播器：这个事件的广播器是 EventPublishingRunListener 的 initialMulticaster，代码参考如下：

```java
public class EventPublishingRunListener implements SpringApplicationRunListener, Orderd {
    //省略非关键代码
    private final SimpleApplicationEventMulticaster initialMulticaster;
    public EventPublishingRunListener(SpringApplication application, String[] args) {
        //省略非关键代码
        this.initialMulticaster = new SimpleApplicationEventMulticaster();
        for (ApplicationListener<?> listener : application.getListeners()) {
            this.initialMulticaster.addApplicationListener(listener);
        }
    }
}
```

2. 监听器：这个事件的监听器同样位于 EventPublishingRunListener 中，获取方式参考关键代码行：

```java
this.initialMulticaster.addApplicationListener(listener);
```

继续查看代码，我们会发现这个事件的监听器就存储在 SpringApplication#Listeners 中，调试下就可以找出所有的监听器，截图如下：

![image-20220727224007359](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207272240582.png)

从中我们可以发现并不存在我们定义的 MyApplicationEnvironmentPreparedEventListener，这是为何？

当 Spring Boot 被构建时，会使用下面的方法去寻找上述监听器：

```java
setListeners((Collection) getSpringFactoriesInstances(ApplicationListener.class));
```

最终是从 META-INF/spring.factories 文件中获取 listener 的：

```
org.springframework.context.ApplicationListener=\
org.springframework.boot.ClearCachesApplicationListener,\
org.springframework.boot.builder.ParentContextCloserApplicationListener,\
org.springframework.boot.cloud.CloudFoundryVcapEnvironmentPostProcessor,\
//省略其他监听器
```

我们定义的监听器并没有被放置在 META-INF/spring.factories 中，实际上，我们的监听器监听的体系是另外一套，其关键组件如下：

1. 广播器：即 AbstractApplicationContext#applicationEventMulticaster；
2. 监听器：由上述提及的 META-INF/spring.factories 中加载的监听器以及扫描到的 ApplicationListener 类型的 Bean 共同组成。

> “另一套监听体系”这里有点逻辑跳跃。

这样比较后，我们可以得出一个结论：我们定义的监听器并不能监听到 initialMulticaster 广播出的 ApplicationEnvironmentPreparedEvent。

- 问题修正

1. 在构建 Spring Boot 时，添加 MyApplicationEnvironmentPreparedEventListener：

```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        MyApplicationEnvironmentPreparedEventListener listener 
            = new MyApplicationEnvironmentPreparedEventListener();
        SpringApplication springApplication = new SpringApplicationBuilder(Application.class)
            .listeners(listener).build();
        springApplication.run(args);
    }
}
```

2. 使用 META-INF/spring.factories，即在 /src/main/resources 下面新建目录 META-INF，然后新建一个对应的 spring.factories 文件：

```
org.springframework.context.ApplicationListener=\
com.spring.puzzle.listener.example2.MyApplicationEnvironmentPreparedEventListener
```

**案例 3：部分事件监听器失效**

有些时候，我们可能还会发现部分事件监听器一直失效或偶尔失效。这里我们可以写一段代码来模拟偶尔失效的场景：

```java
public class MyEvent extends ApplicationEvent {
    public MyEvent(Object source) {
        super(source);
    }
}

@Component
@Order(1)
public class MyFirstEventListener implements ApplicationListener<MyEvent> {
    Random random = new Random();
    @Override
    public void onApplicationEvent(MyEvent event) {
        log.info("{} received: {}", this.toString(), event);
        //模拟部分失效
        if(random.nextInt(10) % 2 == 1)
            throw new RuntimeException("exception happen on first listener");
    }
}

@Component
@Order(2)
public class MySecondEventListener implements ApplicationListener<MyEvent> {
    @Override
    public void onApplicationEvent(MyEvent event) {
        log.info("{} received: {}", this.toString(), event);
    }
}
```

这里监听器 MyFirstEventListener 的优先级稍高，且执行过程中会有 50% 的概率抛出异常。然后我们再写一个 Controller 来触发事件的发送：

```java
@RestController
@Slf4j
public class HelloWorldController {
    @Autowired
    private AbstractApplicationContext applicationContext;
    
    @RequestMapping(path = "publishEvent", method = RequestMethod.GET)
    public String notifyEvent() {
        log.info("start to publish event");
        applicationContext.publishEvent(new MyEvent(UUID.randomUUID()));
        return "ok";
    }
}
```

完成这些代码后，我们使用 http://localhost:8080/publishEvent 来测试监听器的接收和执行。观察测试结果，我们会发现监听器 MySecondEventListener 有一半的概率并没有接收到任何事件。

- 案例解析

处理器的执行是顺序执行的，在执行过程中，如果一个监听器执行抛出了异常，则后续监听器就得不到被执行的机会了。

这里我们可以通过 Spring 源码看下事件是如何被执行的。当广播一个事件，执行的方法参考 SimpleApplicationEventMulticaster#multicastEvent(ApplicationEvent)：

```java
@Override
public void multicastEvent(final ApplicationEvent event, @Nullable ResolvableType eventType) {
    ResolvableType type = (eventType != null ? eventType : resolveDefaultEventType(event));
    Executor executor = getTaskExecutor();
    for (ApplicationListener<?> listener : getApplicationListeners(event, type) {
         if (executor != null) {
             executor.execute(() -> invokeListener(listener, event));
         } else {
             invokeListener(listener, event);
         }
    }
}
```

每个监听器的执行是通过 invokeListener() 来触发的，调用的是接口方法 ApplicationListener#onApplicationEvent。执行逻辑可参考如下代码：

```java
protected void invokeListener(ApplicationListener<?> listener, ApplicationEvent event) {
    ErrorHandler errorHandler = getErrorHandler();
    if (errorHandler != null) {
        try {
            doInvokeListener(listener, event);
        } catch (Throwable err) {
            errorHandler.handleError(err);
        }
    } else {
        doInvokeListener(listener, event);
    }
}

private void doInvokeListener(ApplicationListener listener, ApplicationEvent event) {
    try {
        listener.onApplicationEvent(event);
    } catch (ClassCastException ex) {
        //省略非关键代码
        else {
            throw ex;
        }
    }
}
```

这里我们并没有去设置什么 org.springframework.util.ErrorHandler，也没有绑定什么 Executor 来执行任务，所以针对本案例的情况，我们可以看出：最终事件的执行是由同一个线程按顺序来完成的，任何一个报错，都会导致后续的监听器执行不了。

- 问题修正

1. 确保监听器的执行不会抛出异常。

```java
@Component
@Order(1)
public class MyFirstEventListener implements ApplicationListener<MyEvent> {
    @Override
    public void onApplicationEvent(MyEvent event) {
        try {
            // 省略事件处理相关代码
        } catch(Throwable throwable) {
            //write error/metric to alert
        }
    }
}
```

2. 使用 org.springframework.util.ErrorHandler。

假设我们设置了一个 ErrorHandler，那么就可以用这个 ErrorHandler 去处理掉异常，从而保证后续事件监听器处理不受影响。我们可以使用下面的代码来修正问题：

```java
SimpleApplicationEventMulticaster simpleApplicationEventMulticaster = 
    applicationContext.getBean(APPLICATION_EVENT_MULTICASTER_BEAN_NAME,                            
                               SimpleApplicationEventMulticaster.class);
simpleApplicationEventMulticaster.setErrorHandler(TaskUtils.LOG_AND_SUPPRESS_ERROR_HANDLER);
```

其中 LOG_AND_SUPPRESS_ERROR_HANDLER 的实现如下：

```java
public static final ErrorHandler LOG_AND_SUPPRESS_ERROR_HANDLER = new LoggingErrorHandler();
private static class LoggingErrorHandler implements ErrorHandler {
    private final Log logger = LogFactory.getLog(LoggingErrorHandler.class);
    @Override
    public void handleError(Throwable t) {
        logger.error("Unexpected error occurred in scheduled task", t);
    }
}
```

