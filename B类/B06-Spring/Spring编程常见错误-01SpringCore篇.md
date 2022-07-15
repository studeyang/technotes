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







