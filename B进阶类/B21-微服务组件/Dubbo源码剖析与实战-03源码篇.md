# 12｜源码框架：框架在源码层面如何体现分层？

从今天起我们进入Dubbo源码的学习。

不过在深入研究底层源码之前，我们得先窥其全貌，站在上帝视角来俯视一番，看看框架在代码层面到底是如何分层搭建的。

**模块流程图**

讲到Dubbo框架在代码层面是如何分层搭建的，逃不开官方提供的 [Dubbo 官网的整体设计图](https://dubbo.apache.org/imgs/dev/dubbo-framework.jpg)。

![image-20250320224933167](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503202249814.png)

这10个模块各自的作用是什么，之间又有着怎样的联系？今天，我们将会从消费方发起一次调用开始，尝试把这十个模块串联起来，看看在调用过程中一步步会涉及哪些模块。

**1. Service**

消费方只是引用了 jar 包中的接口来进行调用，就可以拿到想要的结果了，非常简单。

```java
// 消费方通过Spring的上下文对象工具类拿到 CryptoFacade 接口的实例对象
CryptoFacade cryptoFacade = SpringCtxUtils.getBean(CryptoFacade.class);
// 然后调用接口的解密方法，并打印结果
System.out.println(cryptoFacade.decrypt("Geek"));
```

像这些接口（CryptoFacade）和接口实现类（CryptoFacadeImpl），都与实际业务息息相关的，和底层框架没有太多的牵连， **Dubbo 把这样与业务逻辑关联紧密的一层称为服务层，即 Service。**

**2\. Config**

现在有了Service服务层的代码编写，不过，在消费方发起远程调用前，为了更周全地考虑调用过程中可能会发生的一些状况，我们一般都会考虑为远程调用配置一些参数：

![image-20250320225703560](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503202257835.png)

这些配置，站在代码层面来说，就是平常接触的标签、注解、API，更实际点说，落地到类层面就是代码中各种 XxxConfig 类，比如 ServiceConfig、ReferenceConfig，都是我们比较熟悉的配置类， **Dubbo 把这样专门存储与读取配置打交道的层次称为配置层，即 Config。**

**3\. Proxy**

现在 Config 配置好了，接下来是时候准备调用远程了。

接口在消费方又没有实现类，然后有一位中间商悄悄干完了所有的事情，这个所谓的“中间商”不就是像代理商一样么，消费方有什么诉求，代理商就实现这个诉求，至于这个诉求如何实现，是坐船还是坐飞机，那都是代理商的事情，和消费方无关。

![image-20250320225922938](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503202259195.png)

它们背地里都利用了动态代理，为实现远程调用穿了一层马甲，这也势必迫使提供方按照统一的代理逻辑接收处理，然后想办法分发调用不同的实现类。 **因此 Dubbo 把这种代理接口发起远程调用，或代理接收请求进行实例分发处理的层次，称为服务代理层，即 Proxy。**

**4\. Registry**

代理逻辑都要发起远程调用了，但发起远程调用是需要知道目标 IP 地址的，可是，提供方的 IP 地址在哪里呢？

![image-20250320230122417](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503202301688.png)

这就衍生出了一个专门和注册中心打交道的模块，来帮我们注册服务、发现服务， **因此 Dubbo 把这种专门与注册中心打交道的层次，称为注册中心层，即 Registry。**

**5\. Cluster**

现在，消费方的 Registry 拿到一堆提供方的 IP 地址列表，每个 IP 地址就相当于一个提供方。

那么想调用一个接口，还得想办法从众多提供方列表中按照一定的算法选择一个，选择的时候又得考虑是否需要过滤一些不想要的，最终筛选出一个符合逻辑的提供方。

![image-20250320230214369](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503202302636.png)

Dubbo 将这种封装多个提供者并承担路由过滤和负载均衡的层次，称为路由层，即 Cluster。

**6\. Monitor**

然而一次远程调用，总归是要有结果的，正常也好，异常也好，都是一种结果。比如某个方法调用成功了多少次，失败了多少次，调用前后所花费的时间是多少。这些看似和业务逻辑无关紧要，实际，对我们开发人员在分析问题或者预估未来趋势时有着无与伦比的价值。

但是，谁来做这个上报调用结果的事情呢？

![image-20250320230345121](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503202303382.png)

于是诞生了一个监控模块来专门处理这种事情， **Dubbo 将这种同步调用结果的层次称为监控层，即 Monitor。**

**7\. Protocol**

如果把远程调用看作一个“实体对象”，拿着这个“实体对象”就能调出去拿到结果，就好像“实体对象”封装了 RPC 调用的细节，我们只需要感知“实体对象”的存在就好了。

![image-20250320230454395](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503202304699.png)

那么封装调用细节，取回调用结果， **Dubbo 将这种封装调用过程的层次称为远程调用层，即 Protocol。**

**8\. Exchange**

对于我们平常接触的HTTP请求来说，开发人员感知的是调用五花八门的URL地址，但发送 HTTP 报文的逻辑最终归到一个抽象的发送数据的口子，统一处理。

![image-20250320230607622](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503202306893.png)

对 Dubbo 框架来说也是一样，消费方的五花八门的业务请求数据最终会封装为 Request、Response 对象，至于拿着 Request 对象是进行同步调用，还是直接转异步调用通过 Future.get 拿结果，那是底层要做的事情， **因此 Dubbo 将这种封装请求并根据同步异步模式获取响应结果的层次，称为信息交换层，即 Exchange。**

**9\. Transport**

当 Request 请求对象准备好了，不管是同步发送，还是异步发送，最终都是需要发送出去的，但是对象通过谁来发到网络中的呢？

![image-20250320230636839](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503202306124.png)

这就需要网络通信框架出场了。网络通信框架，封装了网络层面的各种细节，只暴露一些发送对象的简单接口，上层只需要放心把 Request 对象交给网络通信框架就可以了， **因此 Dubbo 把这种能将数据通过网络发送至对端服务的层次称为网络传输层，即 Transport。**

**10\. Serialize**

了解过七层网络模型的你也知道，网络通信框架最终要把对象转成二进制才能往网卡中发送，那么谁来将这些实打实的 Request、Response 对象翻译成网络中能识别的二进制数据呢？

![image-20250320230733756](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503202307022.png)

这就衍生出了一个将对象转成二进制或将二进制转成对象的模块， **Dubbo 将这种能把对象与二进制进行相互转换的正反序列化的层次称为数据序列化层，即 Serialize。**

**代码分包架构**

![image-20250320230822728](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503202308010.png)

图中10个模块都对号入座了，结合每一层的作用。还有些未圈出来的模块，这里我们也举 3 个平常比较关注的 Module：

1. **dubbo-common** 是 Dubbo 的公共逻辑模块，包含了许多工具类和一些通用模型对象。
2. **dubbo-configcenter** 是专门来与外部各种配置中心进行交互的，我们配置过 `<dubbo:config-center/>` 标签，标签内容填写的 address 是 nacos 配置中心的地址， 其实就是该模块屏蔽了与外部配置中心的各种交互的细节逻辑。
3. **dubbo-filter** 是一些与过滤器有着紧密关联的功能，目前有缓存过滤器、校验过滤器两个功能。

# 13｜集成框架：框架如何与Spring有机结合？

今天我们来学习框架的集成。

**现状 integration 层代码编写形式**

假设我们正在开发一个已经集成了 Dubbo 框架的消费方系统，你需要编写代码远程调用下游提供方系统，获取业务数据。这是很常见的需求了。

当系统设计的层次比较鲜明，我们一般会把调用下游提供方系统的功能都放在 integration 层，也就意味着当前系统调用下游提供方系统的引用关系都封装在 integration 层。那你的代码可能会这么写：

```java
// 下游系统定义的一个接口
public interface SamplesFacade {
    QueryOrderRes queryOrder(QueryOrderReq req);
}
```

```java
// 当前服务 integration 层定义的一个接口
public interface SamplesFacadeClient {
    QueryOrderResponse queryRemoteOrder(QueryOrderRequest req);
}

// 当前服务 integration 层中调用下游系统实现
public class SamplesFacadeClientImpl implements SamplesFacadeClient {
    @DubboReference
    private SamplesFacade samplesFacade;
    @Override
    public QueryOrderResponse queryRemoteOrder(QueryOrderRequest req){
        // 构建下游系统需要的请求入参对象
        QueryOrderReq integrationReq = buildIntegrationReq(req);

        // 调用 Dubbo 接口访问下游提供方系统
        QueryOrderRes resp = samplesFacade.queryOrder(integrationReq);

        // 判断返回的错误码是否成功
        if(!"000000".equals(resp.getRespCode())){
            throw new RuntimeException("下游系统 XXX 错误信息");
        }

        // 将下游的对象转换为当前系统的对象
        return convert2Response(resp);
    }
}
```

抽象，是把相似流程的骨架抽象出来，可是到底该怎么抽象呢？

我们针对 SamplesFacadeClient 定义了两个注解，@DubboFeignClient 是类注解，@DubboMethod 是方法注解。

```java
@DubboFeignClient(
        remoteClass = SamplesFacade.class,
        needResultJudge = true,
        resultJudge = (remoteCodeNode = "respCode", remoteCodeSuccValueList = "000000", remoteMsgNode = "respMsg")
)
// 当前服务定义的接口
public interface SamplesFacadeClient {
    @DubboMethod(
            timeout = "5000",
            retries = "3",
            loadbalance = "random",
            remoteMethodName = "queryRemoteOrder",
            remoteMethodParamsTypeName = {"com.hmily.QueryOrderReq"}
     )
    QueryOrderResponse queryRemoteOrderInfo(QueryOrderRequest req);
}
```

把 SamplesFacadeClient 设计好后，开发者用起来也特别舒服，之前调用下游提供方接口时要写的一堆代码，现在只需要自己定义一个接口并添加两种注解就完事了。

可是要想在代码中使用这个接口，该怎么实现呢？我们还得继续想办法。

**仿照 Spring 类扫描**

在使用接口时可能会这么写：

```java
@Autowired
private SamplesFacadeClient samplesClient;
```

那么第一个问题来了，samplesClient 要想在运行时调用方法，首先 samplesClient 必须得是一个实例化的对象。 

还有一个问题值得思考：Spring 框架是怎么知道 @Component、@Configuration 等注解的存在呢，关键是这些注解遍布在工程代码的各个角落，Spring 又是怎么找到的呢？

这就需要你了解 Spring 源码里的一个类 org.springframework.context.annotation.ClassPathBeanDefinitionScanner，它是 Spring 为了扫描一堆的 BeanDefinition 而设计，目的就是要 **从 @SpringBootApplication 注解中设置过的包路径及其子包路径中的所有类文件中，扫描出含有 @Component、@Configuration 等注解的类，并构建 BeanDefinition 对象**。

借鉴了源码思想，我们写下了这样的代码：

```java
public class DubboFeignScanner extends ClassPathBeanDefinitionScanner {
    // 定义一个 FactoryBean 类型的对象，方便将来实例化接口使用
    private DubboClientFactoryBean<?> factoryBean = new DubboClientFactoryBean<>();
    // 重写父类 ClassPathBeanDefinitionScanner 的构造方法
    public DubboFeignScanner(BeanDefinitionRegistry registry) {
        super(registry);
    }
    // 扫描各个接口时可以做一些拦截处理
    // 但是这里不需要做任何扫描拦截，因此内置消化掉返回true不需要拦截
    public void registerFilters() {
        addIncludeFilter((metadataReader, metadataReaderFactory) -> true);
    }
    // 重写父类的 doScan 方法，并将 protected 修饰范围放大为 public 属性修饰
    @Override
    public Set<BeanDefinitionHolder> doScan(String... basePackages) {
        // 利用父类的doScan方法扫描指定的包路径
        // 在此，DubboFeignScanner自定义扫描器就是利用Spring自身的扫描特性，
        // 来达到扫描指定包下的所有类文件，省去了自己写代码去扫描这个庞大的体力活了
        Set<BeanDefinitionHolder> beanDefinitions = super.doScan(basePackages);
        if(beanDefinitions == null || beanDefinitions.isEmpty()){
            return beanDefinitions;
        }
        processBeanDefinitions(beanDefinitions);
        return beanDefinitions;
    }
    // 自己手动构建 BeanDefinition 对象
    private void processBeanDefinitions(Set<BeanDefinitionHolder> beanDefinitions) {
        GenericBeanDefinition definition = null;
        for (BeanDefinitionHolder holder : beanDefinitions) {
            definition = (GenericBeanDefinition)holder.getBeanDefinition();
            definition.getConstructorArgumentValues().addGenericArgumentValue(definition.getBeanClassName());
            // 特意针对 BeanDefinition 设置 DubboClientFactoryBean.class
            // 目的就是在实例化时能够在 DubboClientFactoryBean 中创建代理对象
            definition.setBeanClass(factoryBean.getClass());
            definition.setAutowireMode(AbstractBeanDefinition.AUTOWIRE_BY_TYPE);
        }
    }
}
```

我们就可以重写 doScan 方法接收一个包路径（SamplesFacadeClient 接口所在的包路径），然后利用 super.doScan 让 Spring 帮我们去扫描指定包路径下的所有类文件。

我们如何保障精准扫描出指定注解的类呢？

你会发现 Spring 源码在添加 BeanDefinition 时，需要借助一个 org.springframework.context.annotation.ClassPathScanningCandidateComponentProvider#isCandidateComponent 方法，来判断是不是候选组件，也就是，是不是需要拾取指定注解。

```java
public class DubboFeignScanner extends ClassPathBeanDefinitionScanner {
    // ...省略部分同上代码
    
    // 重写父类中“是否是候选组件”的方法，即我们认为哪些扫描到的类可以是候选类
    @Override
    protected boolean isCandidateComponent(AnnotatedBeanDefinition beanDefinition) {
        AnnotationMetadata metadata = beanDefinition.getMetadata();
        if (!(metadata.isInterface() && metadata.isIndependent())) {
            return false;
        }
        // 针对扫描到的类，然后看看扫描到的类中是否有 DubboFeignClient 注解信息
        Map<String, Object> attributes = metadata.getAnnotationAttributes(DubboFeignClient.class.getName());
        // 若扫描到的类上没有 DubboFeignClient 注解信息则认为不是认可的类
        if (attributes == null) {
            return false;
        }
        // 若扫描到的类上有 DubboFeignClient 注解信息则起码是认可的类
        AnnotationAttributes annoAttrs = AnnotationAttributes.fromMap(attributes);
        if (annoAttrs == null) {
            return false;
        }
        // 既然是认可的类，那再看看类注解中是否有 remoteClass 字段信息
        // 若 remoteClass 字段信息有值的话，则认为是我们最终认定合法的候选类
        Object remoteClass = annoAttrs.get("remoteClass");
        if (remoteClass == null) {
            return false;
        }
        return true;
    }
}
```

代码中在 isCandidateComponent 方法中进行了识别 DubboFeignClient 类注解的业务逻辑处理，如果有类注解且有 remoteClass 属性的话，就认为是我们寻找的类。

这样，所有含有 @DubboFeignClient 注解的类的 BeanDefinition 对象都被扫描收集起来了，接下来就交给 Spring 本身 refresh 方法中的 org.springframework.beans.factory.support.DefaultListableBeanFactory#preInstantiateSingletons 方法进行实例化了，而实例化的时候，如果发现 BeanDefinition 对象是 org.springframework.beans.factory.FactoryBean 类型，会调用 FactoryBean 的 getObject 方法创建代理对象。

同理我们写出：

```java
public class DubboClientFactoryBean<T> implements FactoryBean<T>, ApplicationContextAware {
    private Class<T> dubboClientInterface;
    private ApplicationContext appCtx;
    public DubboClientFactoryBean() {
    }
    // 该方法是在 DubboFeignScanner 自定义扫描器的 processBeanDefinitions 方法中，
    // 通过 definition.getConstructorArgumentValues().addGenericArgumentValue(definition.getBeanClassName()) 代码设置进来的
    // 这里的 dubboClientInterface 就等价于 SamplesFacadeClient 接口
    public DubboClientFactoryBean(Class<T> dubboClientInterface) {
        this.dubboClientInterface = dubboClientInterface;
    }

    // Spring框架实例化FactoryBean类型的对象时的必经之路
    @Override
    public T getObject() throws Exception {
        // 为 dubboClientInterface 创建一个 JDK 代理对象
        // 同时代理对象中的所有业务逻辑交给了 DubboClientProxy 核心代理类处理
        return (T) Proxy.newProxyInstance(dubboClientInterface.getClassLoader(),
                new Class[]{dubboClientInterface}, new DubboClientProxy<>(appCtx));
    }
    // 标识该实例化对象的接口类型
    @Override
    public Class<?> getObjectType() {
        return dubboClientInterface;
    }
    // 标识 SamplesFacadeClient 最后创建出来的代理对象是单例对象
    @Override
    public boolean isSingleton() {
        return true;
    }
    @Override
    public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
        this.appCtx = applicationContext;
    }
}
```

代码中 getObject 是我们创建代理对象的核心过程，细心的你可能会发现我们还创建了一个 DubboClientProxy 对象，这个对象放在 `java.lang.reflect.Proxy#newProxyInstance(java.lang.ClassLoader, java.lang.Class<?>[], java.lang.reflect.InvocationHandler)` 方法中的第三个参数。

这意味着，将来含有 @DubboFeignClient 注解的类的方法被调用时，一定会触发调用 DubboClientProxy 类，也就说我们可以在 DubboClientProxy 类拦截方法，这正是我们梦寐以求的核心拦截方法的地方。

来看DubboClientProxy 的实现：

```java
public class DubboClientProxy<T> implements InvocationHandler, Serializable {
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        // 省略前面的一些代码

        // 读取接口（例：SamplesFacadeClient）上对应的注解信息
        DubboFeignClient dubboClientAnno = declaringClass.getAnnotation(DubboFeignClient.class);
        // 读取方法（例：queryRemoteOrderInfo）上对应的注解信息
        DubboMethod methodAnno = method.getDeclaredAnnotation(DubboMethod.class);
        // 获取需要调用下游系统的类、方法、方法参数类型
        Class<?> remoteClass = dubboClientAnno.remoteClass();
        String mtdName = getMethodName(method.getName(), methodAnno);
        Method remoteMethod = MethodCache.cachedMethod(remoteClass, mtdName, methodAnno);
        Class<?> returnType = method.getReturnType();

        // 发起真正远程调用
        Object resultObject = doInvoke(remoteClass, remoteMethod, args, methodAnno);

        // 判断返回码，并解析返回结果
        return doParse(dubboClientAnno, returnType, resultObject);
    }
}
```

这下是真正做到了用一套代码解决了所有 integration 层接口的远程调用，简化了重复代码开发的劳动力成本，而且也使代码的编写更加简洁美观。

> 这样一看，多写一些下游转发代码其实也没什么。

# 14｜SPI机制：Dubbo的SPI比JDK的SPI好在哪里？

今天我们来深入研究Dubbo源码的第三篇，SPI 机制。

SPI，英文全称是Service Provider Interface，按每个单词翻译就是：服务提供接口。

**SPI是怎么来的？**

我们结合具体的应用场景来思考：

![image-20250322223808782](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503222238882.png)

app-web 后台应用引用了一款开源的 web-fw.jar 插件，这个插件的作用就是辅助后台应用的启动，并且控制 Web 应用的核心启动流程，也就是说这个插件控制着 Web 应用启动的整个生命周期。

现在，有这样一个需求， **在 Web 应用成功启动的时刻，我们需要预加载 Dubbo 框架的一些资源，你会怎么做呢？**

**JDK SPI**

JDK SPI 底层实现源码流程主要有三块。

- 第一块，将接口传入到 ServiceLoader.load 方法后，得到了一个内部类的迭代器。
- 第二块，通过调用迭代器的 hasNext 方法，去读取“/META-INF/services/接口类路径”这个资源文件内容，并逐行解析出所有实现类的类路径。
- 第三块，将所有实现类的类路径通过“Class.forName”反射方式进行实例化对象。

在跟踪源码的过程中，我还发现了一个问题， **当我们使用 ServiceLoader 的 load 方法执行多次时，会不断创建新的实例对象**。你可以这样编写代码验证：

```java
public static void main(String[] args) {
    // 模拟进行 3 次调用 load 方法并传入同一个接口
    for (int i = 0; i < 3; i++) {
        // 加载 ApplicationStartedListener 接口的所有实现类
        ServiceLoader<ApplicationStartedListener> loader
               = ServiceLoader.load(ApplicationStartedListener.class);
        // 遍历 ApplicationStartedListener 接口的所有实现类，并调用里面的 onCompleted 方法
        Iterator<ApplicationStartedListener> it = loader.iterator();
        while (it.hasNext()){
            // 获取其中的一个实例，并调用 onCompleted 方法
            ApplicationStartedListener instance = it.next();
            instance.onCompleted();
        }
    }
}
```

代码中，尝试调用 3 次 ServiceLoader 的 load 方法，并且每一次传入的都是同一个接口，运行编写好的代码，打印出如下信息：

```
预加载 Dubbo 框架的一些资源, com.hmilyylimh.cloud.jdk.spi.PreloadDubboResourcesListener@300ffa5d
预加载 Dubbo 框架的一些资源, com.hmilyylimh.cloud.jdk.spi.PreloadDubboResourcesListener@1f17ae12
预加载 Dubbo 框架的一些资源, com.hmilyylimh.cloud.jdk.spi.PreloadDubboResourcesListener@4d405ef7
```

创建出多个实例对象，有什么问题呢？

问题一，使用 load 方法频率高，容易影响 IO 吞吐和内存消耗。如果调用 load 方法的频率比较高，那每调用一次其实就在做读取文件->解析文件->反射实例化这几步，不但会影响磁盘IO读取的效率，还会明显增加内存开销，我们并不想看到。

问题二，使用 load 方法想要获取指定实现类，需要自己进行遍历并编写各种比较代码。每次在调用时想拿到其中一个实现类，使用起来也非常不舒服，因为我们不知道想要的实现类，在迭代器的哪个位置，只有遍历完所有的实现类，才能找到想要的那个。假如项目中，有很多业务逻辑都需要获取指定的实现类，那将会充斥着各色各样针对 load 进行遍历的代码并比较，无形中，我们又悄悄产生了很多雷同代码。

**Dubbo SPI**

为了弥补我们分析的 JDK SPI 的不足，Dubbo 也定义出了自己的一套 SPI 机制逻辑，既要通过 O(1) 的时间复杂度来获取指定的实例对象，还要控制缓存创建出来的对象，做到按需加载获取指定实现类，并不会像JDK SPI那样一次性实例化所有实现类。

在代码层面使用起来也很方便，你看这里的代码：

```java
///////////////////////////////////////////////////
// Dubbo SPI 的测试启动类
///////////////////////////////////////////////////
public class Dubbo14DubboSpiApplication {
    public static void main(String[] args) {
        ApplicationModel applicationModel = ApplicationModel.defaultModel();
        // 通过 Protocol 获取指定像 ServiceLoader 一样的加载器
        ExtensionLoader<IDemoSpi> extensionLoader = applicationModel.getExtensionLoader(IDemoSpi.class);

        // 通过指定的名称从加载器中获取指定的实现类
        IDemoSpi customSpi = extensionLoader.getExtension("customSpi");
        System.out.println(customSpi + ", " + customSpi.getDefaultPort());

        // 再次通过指定的名称从加载器中获取指定的实现类，看看打印的引用是否创建了新对象
        IDemoSpi customSpi2 = extensionLoader.getExtension("customSpi");
        System.out.println(customSpi2 + ", " + customSpi2.getDefaultPort());
    }
}

///////////////////////////////////////////////////
// 定义 IDemoSpi 接口并添加上了 @SPI 注解，
// 其实也是在定义一种 SPI 思想的规范
///////////////////////////////////////////////////
@SPI
public interface IDemoSpi {
    int getDefaultPort();
}

///////////////////////////////////////////////////
// 自定义一个 CustomSpi 类来实现 IDemoSpi 接口
// 该 IDemoSpi 接口被添加上了 @SPI 注解，
// 其实也是在定义一种 SPI 思想的规范
///////////////////////////////////////////////////
public class CustomSpi implements IDemoSpi {
    @Override
    public int getDefaultPort() {
        return 8888;
    }
}

///////////////////////////////////////////////////
// 资源目录文件
// 路径为：/META-INF/dubbo/internal/com.hmilyylimh.cloud.dubbo.spi.IDemoSpi
///////////////////////////////////////////////////
customSpi=com.hmilyylimh.cloud.dubbo.spi.CustomSpi
```

然后运行这段简短的代码，打印出日志。

```
com.hmilyylimh.cloud.dubbo.spi.CustomSpi@143640d5, 8888
com.hmilyylimh.cloud.dubbo.spi.CustomSpi@143640d5, 8888
```

从日志中可以看到，再次通过别名去获取指定的实现类时，打印的实例对象的引用是同一个，说明 Dubbo 框架做了缓存处理。而且整个操作，我们只通过一个简单的别名，就能从 ExtensionLoader 中拿到指定实现类，确实简单方便。

# 15｜Wrapper机制：Wrapper是怎么降低调用开销的？

今天是我们深入研究Dubbo源码的第四篇，Wrapper 机制。

Wrapper，它是Dubbo中的一种动态生成的代理类。你可能已经想到了 JDK 和 Cglib 两个常见的代理，JDK 代理是动态生成了一个继承 Proxy 的代理类，而 Cglib 代理是动态生成了一个继承被代理类的派生代理类，既然都有现成的动态生成代理类的解决方案了，为什么 Dubbo 还需要动态生成自己的代理类呢？

结合具体的应用场景来思考，有三个请求，每个请求中的四个字段值都不一样，现在要发往提供方服务：

![image-20250326230446680](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503262304026.png)

**JDK 代理**

可以通过反射机制获取接口类名对应的类对象，通过类对象的简称获取到对应的接口服务，通过接口方法名和接口方法参数，来精准定位需要提供方接口服务中的哪个方法进行处理。

```java
///////////////////////////////////////////////////
// 提供方服务：统一入口接收请求的控制器，原始的 if...else 方式
///////////////////////////////////////////////////
@RestController
public class CommonController {
    // 定义统一的URL地址
    @PostMapping("gateway/{className}/{mtdName}/{parameterTypeName}/request")
    public String recvCommonRequest(@PathVariable String className,
                                    @PathVariable String mtdName,
                                    @PathVariable String parameterTypeName,
                                    @RequestBody String reqBody) throws Exception {
        // 统一的接收请求的入口
        return commonInvoke(className, parameterTypeName, mtdName, reqBody);
    }

    /**
     * <h2>统一入口的核心逻辑。</h2>
     *
     * @param className：接口归属方法的全类名。
     * @param mtdName：接口的方法名。
     * @param parameterTypeName：接口的方法入参的全类名。
     * @param reqParamsStr：请求数据。
     * @return 接口方法调用的返回信息。
     * @throws Exception
     */
    public static String commonInvoke(String className,
                                      String mtdName,
                                      String parameterTypeName,
                                      String reqParamsStr) throws Exception {
        // 通过反射机制可以获取接口类名对应的类对象
        Class<?> clz = Class.forName(className);

        // 接着通过类对象的简称获取到对应的接口服务
        Object cacheObj = SpringCtxUtils.getBean(clz);

        // 然后通过接口方法名和接口方法参数
        if (cacheObj.getClass().getName().equals(className)) {
            // 来精准定位需要提供方接口服务中的哪个方法进行处理
            if ("sayHello".equals(mtdName) && String.class.getName().equals(parameterTypeName)) {
                // 真正的发起对源对象（被代理对象）的方法调用
                return ((DemoFacade) cacheObj).sayHello(reqParamsStr);
            } else if("say".equals(mtdName) && Void.class.getName().equals(parameterTypeName)){
                // 真正的发起对源对象（被代理对象）的方法调用
                return ((DemoFacade) cacheObj).say();
            }

            // 如果找不到的话，就抛出异常，提示方法不存在
            throw new RuntimeException(String.join(".", className, mtdName) + " 的方法不存在");
        }

        // 如果找不到的话，就抛出异常，提示类不存在
        throw new RuntimeException(className + " 类不存在");
    }
}
```

不停地利用 if…else 逻辑找到不同方法名对应方法逻辑，让提供方服务的统一入口外表看起来光鲜靓丽，内部实现其实丑陋不堪，一旦将来接口新增了方法，这里的 if…else 逻辑又得继续扩充，没完没了，永无止境。

```java
///////////////////////////////////////////////////
// 提供方服务：统一入口接收请求的控制器，反射改善后的方式
///////////////////////////////////////////////////
@RestController
public class CommonController {
    // 定义URL地址
    @PostMapping("gateway/{className}/{mtdName}/{parameterTypeName}/request")
    public String recvCommonRequest(@PathVariable String className,
                                    @PathVariable String mtdName,
                                    @PathVariable String parameterTypeName,
                                    @RequestBody String reqBody) throws Exception {
        // 统一的接收请求的入口
        return commonInvoke(className, parameterTypeName, mtdName, reqBody);
    }

    /**
     * <h2>统一入口的核心逻辑。</h2>
     *
     * @param className：接口归属方法的全类名。
     * @param mtdName：接口的方法名。
     * @param parameterTypeName：接口的方法入参的全类名。
     * @param reqParamsStr：请求数据。
     * @return 接口方法调用的返回信息。
     * @throws Exception
     */
    public static String commonInvoke(String className,
                                      String mtdName,
                                      String parameterTypeName,
                                      String reqParamsStr) throws Exception {
        // 通过反射机制可以获取接口类名对应的类对象
        Class<?> clz = Class.forName(className);

        // 接着通过类对象的简称获取到对应的接口服务的【代理对象】
        // 相当于不同的 clz 就会获取不同的代理对象，各个代理对象代理的源对象都不一样的
        ProxyInvoker proxyInvoker = SpringCtxUtils.getBean(clz);

        // 【代理对象】调用自身的统一方法，然后内部会去识别方法名、方法参数调用不同的方法
        return proxyInvoker.invoke(clz, mtdName, parameterTypeName, reqParamsStr);
    }

    ///////////////////////////////////////////////////
    // 提供方服务：模拟的是其中一个代理类结构样子
    ///////////////////////////////////////////////////
    public class ProxyInvoker$1 extends ProxyInvoker {
        // 暴露的统一被调用的方法
        public Object invoke(Class<?> clz,
                             String mtdName,
                             String parameterTypeName,
                             String reqParamsStr){
            // 通过反射找到方法对应的 Method 对象
            Method method = clz.getDeclaredMethod(mtdName, Class.forName(parameterTypeName));
            method.setAccessible(true);
            // 反射调用
            return method.invoke(getSourceTarget(), reqParamsStr);
        }
    }
}
```

这就是 JDK 的动态代理模式，会动态生成一个继承 Proxy 的代理类。

为什么 Dubbo 不用 JDK 的代理模式呢？我们通过一个示例来对比，代码也非常简单，一段是正常创建对象并调用对象的方法，一段是反射创建对象并反射调用对象的方法，然后各自循环调用一百万次看耗时，看运行结果。

```
正常调用耗时为：5 毫秒
反射调用耗时为：745 毫秒
```

**Cglib 代理**

Cglib 的核心原理，就是通过执行拦截器的回调方法（methodProxy.invokeSuper），从代理类的众多方法引用中匹配正确方法，并执行被代理类的方法。

Cglib的这种方式，就像代理类的内部动态生成了一堆的 if…else 语句来调用被代理类的方法，避免了手工写各种 if…else 的硬编码逻辑，省去了不少硬编码的活。

但是这么一来，如何生成动态代理类的逻辑就至关重要了，而且万一我们以后有自主定制的诉求，想修改这段生成代理类的这段逻辑，反而受 Cglib 库的牵制。

因此为了长远考虑，我们还是自己实现一套有 Cglib 思想的方案更好，并且还可以在此思想上，利用最简单的代码，定制适合自己框架的代理类。这其实也是Dubbo的想法。

> 缺少实际的例子说明。

**自定义代理**

我们总结下使用 JDK 和 Cglib 代理的一些顾虑。

- JDK 代理，核心实现是进行反射调用，性能损耗不小。
- Cglib 代理，核心实现是生成了各种 if…else 代码来调用被代理类的方法，但是这块生成代理的逻辑不够灵活，难以自主修改。

基于这两点，我们考虑综合一下，自己打造一个简化版的迷你型 Cglib 代理工具，这样一来，就可以在自己的代理工具中做各种与框架密切相关的逻辑了。

我们来设计代码模板：

```java
///////////////////////////////////////////////////
// 代码模板
///////////////////////////////////////////////////
public class $DemoFacadeCustomInvoker extends CustomInvoker {
    @Override
    public Object invokeMethod(Object instance, String mtdName, Class<?>[] types, Object[] args) throws NoSuchMethodException {
        // 这里就是进行简单的 if 代码判断
        if ("sayHello".equals(mtdName)) {
            return ((DemoFacade) instance).sayHello(String.valueOf(args[0]));
        }
        if ("say".equals(mtdName)) {
            return ((DemoFacade) instance).say();
        }
        throw new NoSuchMethodException("Method [" + mtdName + "] not found.");
    }
}
```

有了代码模板，我们对照着代码模板用 Java 语言编写生成出来。

```java
///////////////////////////////////////////////////
// 自定义代理生成工具类
///////////////////////////////////////////////////
public class CustomInvokerProxyUtils {
    private static final AtomicInteger INC = new AtomicInteger();

    // 创建源对象（被代理对象）的代理对象
    public static Object newProxyInstance(Object sourceTarget) throws Exception{
        String packageName = "com.hmilyylimh.cloud.wrapper.custom";
        // filePath = /E:/工程所在的磁盘路径/dubbo-15-dubbo-wrapper/target/classes/com/hmilyylimh/cloud/wrapper/custom
        String filePath = CustomInvokerProxyUtils.class.getResource("/").getPath()
                + CustomInvokerProxyUtils.class.getPackage().toString().substring("package ".length()).replaceAll("\\.", "/");
        Class<?> targetClazz = sourceTarget.getClass().getInterfaces()[0];
        // proxyClassName = $DemoFacadeCustomInvoker_1
        String proxyClassName = "$" + targetClazz.getSimpleName() + "CustomInvoker_" + INC.incrementAndGet();
        // 获取代理的字节码内容
        String proxyByteCode = getProxyByteCode(packageName, proxyClassName, targetClazz);
        // 缓存至磁盘中
        file2Disk(filePath, proxyClassName, proxyByteCode);
        // 等刷盘稳定后
        TimeUtils.sleep(2000);
        // 再编译java加载class至内存中
        Object compiledClazz = compileJava2Class(filePath, packageName, proxyClassName, sourceTarget, targetClazz);
        // 返回实例化的对象
        return compiledClazz;
    }
    // 生成代理的字节码内容，其实就是一段类代码的字符串
    private static String getProxyByteCode(String packageName, String proxyClassName, Class<?> targetClazz) {
        StringBuilder sb = new StringBuilder();
        // pkgContent = package com.hmilyylimh.cloud.wrapper.custom;
        String pkgContent = "package " + packageName + ";";
        // importTargetClazz = import com.hmilyylimh.cloud.facade.demo.DemoFacade;
        String importTargetClazz = "import " + targetClazz.getName() + ";";
        // importNoSuchMethodException = import org.apache.dubbo.common.bytecode.NoSuchMethodException;
        String importNoSuchMethodException = "import " + org.apache.dubbo.common.bytecode.NoSuchMethodException.class.getName() + ";";
        // classHeadContent = public class $DemoFacadeCustomInvoker extends CustomInvoker {
        String classHeadContent = "public class " + proxyClassName + " extends " + CustomInvoker.class.getSimpleName() + " {" ;
        // 添加内容
        sb.append(pkgContent).append(importTargetClazz).append(importNoSuchMethodException).append(classHeadContent);
        // invokeMethodHeadContent = public Object invokeMethod(Object instance, String mtdName, Class<?>[] types, Object[] args) throws NoSuchMethodException {
        String invokeMethodHeadContent = "public " + Object.class.getName() + " invokeMethod" +
                "(" + Object.class.getName() + " instance, "
                + String.class.getName() + " mtdName, " + Class.class.getName() + "<?>[] types, "
                + Object.class.getName() + "[] args) throws " + org.apache.dubbo.common.bytecode.NoSuchMethodException.class.getName() + " {\n";
        sb.append(invokeMethodHeadContent);
        for (Method method : targetClazz.getDeclaredMethods()) {
            String methodName = method.getName();
            Class<?>[] parameterTypes = method.getParameterTypes();
            // if ("sayHello".equals(mtdName)) {
            String ifHead = "if (\"" + methodName + "\".equals(mtdName)) {\n";
            // return ((DemoFacade) instance).sayHello(String.valueOf(args[0]));
            String ifContent = null;
            // 这里有 bug ，姑且就入参就传一个入参对象吧
            if(parameterTypes.length != 0){
                ifContent = "return ((" + targetClazz.getName() + ") instance)." + methodName + "(" + String.class.getName() + ".valueOf(args[0]));\n";
            } else {
                ifContent = "return ((" + targetClazz.getName() + ") instance)." + methodName + "();\n";
            }
            // }
            String ifTail = "}\n";
            sb.append(ifHead).append(ifContent).append(ifTail);
        }
        // throw new NoSuchMethodException("Method [" + mtdName + "] not found.");
        String invokeMethodTailContent = "throw new " + org.apache.dubbo.common.bytecode.NoSuchMethodException.class.getName() + "(\"Method [\" + mtdName + \"] not found.\");\n}\n";
        sb.append(invokeMethodTailContent);
        // 类的尾巴大括号
        String classTailContent = " } ";
        sb.append(classTailContent);
        return sb.toString();
    }
    private static void file2Disk(String filePath, String proxyClassName, String proxyByteCode) throws IOException {
        File file = new File(filePath + File.separator + proxyClassName + ".java");
        if (!file.exists()) {
            file.createNewFile();
        }
        FileWriter fileWriter = new FileWriter(file);
        fileWriter.write(proxyByteCode);
        fileWriter.flush();
        fileWriter.close();
    }
    private static Object compileJava2Class(String filePath, String packageName, String proxyClassName, Object argsTarget, Class<?> targetClazz) throws Exception {
        // 编译 Java 文件
        JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
        StandardJavaFileManager fileManager = compiler.getStandardFileManager(null, null, null);
        Iterable<? extends JavaFileObject> compilationUnits =
                fileManager.getJavaFileObjects(new File(filePath + File.separator + proxyClassName + ".java"));
        JavaCompiler.CompilationTask task = compiler.getTask(null, fileManager, null, null, null, compilationUnits);
        task.call();
        fileManager.close();
        // 加载 class 文件
        URL[] urls = new URL[]{new URL("file:" + filePath)};
        URLClassLoader urlClassLoader = new URLClassLoader(urls);
        Class<?> clazz = urlClassLoader.loadClass(packageName + "." + proxyClassName);
        // 反射创建对象，并且实例化对象
        Constructor<?> constructor = clazz.getConstructor();
        Object newInstance = constructor.newInstance();
        return newInstance;
    }
}
```

接下来我们就使用代理工具类，生成代理类并调用方法看看。

```java
public static void main(String[] args) throws Exception {
    // 创建源对象（即被代理对象）
    DemoFacadeImpl demoFacade = new DemoFacadeImpl();
    // 生成自定义的代理类
    CustomInvoker invoker =
         (CustomInvoker)CustomInvokerProxyUtils.newProxyInstance(demoFacade);
    // 调用代理类的方法
    invoker.invokeMethod(demoFacade, "sayHello", new Class[]{String.class}, new Object[]{"Geek"});
}
```

**Wrapper 机制的原理**

通过一番自定义实现后，想必你已经理解了 Dubbo 的用意了，我们来看看源码层面Dubbo是怎么生成代理类的，有哪些值得关注的细节。

```java
// org.apache.dubbo.rpc.proxy.javassist.JavassistProxyFactory#getInvoker
// 创建一个 Invoker 的包装类
@Override
public <T> Invoker<T> getInvoker(T proxy, Class<T> type, URL url) {
    // 这里就是生成 Wrapper 代理对象的核心一行代码
    final Wrapper wrapper = Wrapper.getWrapper(proxy.getClass().getName().indexOf('$') < 0 ? proxy.getClass() : type);
    // 包装一个 Invoker 对象
    return new AbstractProxyInvoker<T>(proxy, type, url) {
        @Override
        protected Object doInvoke(T proxy, String methodName,
                                  Class<?>[] parameterTypes,
                                  Object[] arguments) throws Throwable {
            // 使用 wrapper 代理对象调用自己的 invokeMethod 方法
            // 以此来避免反射调用引起的性能开销
            // 通过强转来实现统一方法调用
            return wrapper.invokeMethod(proxy, methodName, parameterTypes, arguments);
        }
    };
}
```

代码外表看起来很简单，内部的调用情况还是很深的，这里我也总结了代码调用流程图：

![image-20250326233314604](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503262333932.png)

我们来使用一下 Wrapper 机制，方便你更直观地理解，使用方式如下：

```java
public class InvokeDemoFacade {
    public static void main(String[] args) throws Exception {
        // 创建一个源对象（即被代理类）
        DemoFacadeImpl demoFacade = new DemoFacadeImpl();
        // 使用 Wrapper 机制获取一个继承  Wrapper 的代理类
        final Wrapper wrapper = Wrapper.getWrapper(demoFacade.getClass());
        // 使用生成的 wrapper 代理类调用通用的 invokeMethod 方法获取结果
        Object result = wrapper.invokeMethod(
                demoFacade,
                "sayHello",
                new Class[]{String.class},
                new Object[]{"Geek"}
        );
        // 然后打印调用的结果
        System.out.println("wrapper调用结果为：" + result);
    }
}
```

然后把生成是 wrapper 代理类 class 文件反编译为 Java 代码，看看生成的内容到底长什么样的。

```java
///////////////////////////////////////////////////
// Wrapper.getWrapper(demoFacade.getClass())
// 这句代码生成出来的 wrapper 代理对象，对应类的代码结构
///////////////////////////////////////////////////
package com.hmilyylimh.cloud.wrapper.demo;
import java.lang.reflect.InvocationTargetException;
import java.util.Map;
import org.apache.dubbo.common.bytecode.NoSuchMethodException;
import org.apache.dubbo.common.bytecode.NoSuchPropertyException;
import org.apache.dubbo.common.bytecode.Wrapper;
import org.apache.dubbo.common.bytecode.ClassGenerator.DC;
// Dubbo 框架生成代理类的类名为 DemoFacadeImplDubboWrap0，
// 然后也继承了一个 Wrapper 对象，需要一个 invokeMethod 方法来统一调用
public class DemoFacadeImplDubboWrap0 extends Wrapper implements DC {
    public static String[] pns;
    public static Map pts;
    public static String[] mns;
    public static String[] dmns;
    public static Class[] mts0;
    public static Class[] mts1;
    public String[] getPropertyNames() { return pns; }
    public boolean hasProperty(String var1) { return pts.containsKey(var1); }
    public Class getPropertyType(String var1) { return (Class)pts.get(var1); }
    public String[] getMethodNames() { return mns; }
    public String[] getDeclaredMethodNames() { return dmns; }
    public void setPropertyValue(Object var1, String var2, Object var3) {
        try {
            DemoFacadeImpl var4 = (DemoFacadeImpl)var1;
        } catch (Throwable var6) {
            throw new IllegalArgumentException(var6);
        }
        throw new NoSuchPropertyException("Not found property \"" + var2 + "\" field or setter method in class com.hmilyylimh.cloud.wrapper.demo.DemoFacadeImpl.");
    }
    public Object getPropertyValue(Object var1, String var2) {
        try {
            DemoFacadeImpl var3 = (DemoFacadeImpl)var1;
        } catch (Throwable var5) {
            throw new IllegalArgumentException(var5);
        }
        throw new NoSuchPropertyException("Not found property \"" + var2 + "\" field or getter method in class com.hmilyylimh.cloud.wrapper.demo.DemoFacadeImpl.");
    }
    // !!!!!!!!!!!!!!!!!!!!!!!!!!!
    // 重点看这里，这才是调用的关键代码
    // 这里也动态生成了 if...else 代码
    // 然后通过强转调用源对象（被代理对象）的方法
    public Object invokeMethod(Object var1, String var2, Class[] var3, Object[] var4) throws InvocationTargetException {
        DemoFacadeImpl var5;
        try {
            var5 = (DemoFacadeImpl)var1;
        } catch (Throwable var8) {
            throw new IllegalArgumentException(var8);
        }
        try {
            if ("sayHello".equals(var2) && var3.length == 1) {
                return var5.sayHello((String)var4[0]);
            }
            if ("say".equals(var2) && var3.length == 0) {
                return var5.say();
            }
        } catch (Throwable var9) {
            throw new InvocationTargetException(var9);
        }
        throw new NoSuchMethodException("Not found method \"" + var2 + "\" in class com.hmilyylimh.cloud.wrapper.demo.DemoFacadeImpl.");
    }
    public DemoFacadeImplDubboWrap0() {
    }
}
```

我们最后比较一下正常调用、反射调用、Wrapper调用的耗时情况：

```
正常调用耗时为：8 毫秒
反射调用耗时为：2019 毫秒
Wrapper调用耗时为：12 毫秒
```

**Wrapper 机制的利弊**

Wrapper机制既然这么牛，难道我们可以摒弃已有的 JDK 和 Cglib 代理了么？其实不是的，使用时也有利弊之分的。

Wrapper机制，对于搭建高性能的底层调用框架还是非常高效的，而且开辟了一条直接通过Java代码生成代理类的简便途径，为框架的未来各种定制扩展，提供了非常灵活的自主控制权。但不适合大众化，因为Wrapper机制定制化程度高，对维护人员会有较高的开发门槛要求。

# 16｜Compiler编译：神乎其神的编译你是否有过胆怯？

今天是我们深入研究Dubbo源码的第五篇，Compiler 编译。

**Javassist 编译**

参考 Dubbo 的实现 ClassGenerator，代码如下：

```java
// org.apache.dubbo.common.bytecode.ClassGenerator#toClass(java.lang.Class<?>, java.lang.ClassLoader, java.security.ProtectionDomain)
public Class<?> toClass(Class<?> neighborClass, ClassLoader loader, ProtectionDomain pd) {
    if (mCtc != null) {
        mCtc.detach();
    }
    // 自增长类名尾巴序列号，类似 $Proxy_01.class 这种 JDK 代理名称的 01 数字
    long id = CLASS_NAME_COUNTER.getAndIncrement();
    try {
        // 从 ClassPool 中获取 mSuperClass 类的类型
        // 我们一般还可以用 mPool 来看看任意类路径对应的 CtClass 类型对象是什么
        // 比如可以通过 mPool.get("java.lang.String") 看看 String 的 CtClass 类型对象是什么
        // 之所以要这么做，主要是为了迎合这样的API语法而操作的
        CtClass ctcs = mSuperClass == null ? null : mPool.get(mSuperClass);
        if (mClassName == null) {
            mClassName = (mSuperClass == null || javassist.Modifier.isPublic(ctcs.getModifiers())
                    ? ClassGenerator.class.getName() : mSuperClass + "$sc") + id;
        }
        // 通过 ClassPool 来创建一个叫 mClassName 名字的类
        mCtc = mPool.makeClass(mClassName);
        if (mSuperClass != null) {
            // 然后设置一下 mCtc 这个新创建类的父类为 ctcs
            mCtc.setSuperclass(ctcs);
        }
        // 为 mCtc 新建类添加一个实现的接口
        mCtc.addInterface(mPool.get(DC.class.getName())); // add dynamic class tag.
        if (mInterfaces != null) {
            for (String cl : mInterfaces) {
                mCtc.addInterface(mPool.get(cl));
            }
        }
        // 为 mCtc 新建类添加一些字段
        if (mFields != null) {
            for (String code : mFields) {
                mCtc.addField(CtField.make(code, mCtc));
            }
        }
        // 为 mCtc 新建类添加一些方法
        if (mMethods != null) {
            for (String code : mMethods) {
                if (code.charAt(0) == ':') {
                    mCtc.addMethod(CtNewMethod.copy(getCtMethod(mCopyMethods.get(code.substring(1))),
                            code.substring(1, code.indexOf('(')), mCtc, null));
                } else {
                    mCtc.addMethod(CtNewMethod.make(code, mCtc));
                }
            }
        }
        // 为 mCtc 新建类添加一些构造方法
        if (mDefaultConstructor) {
            mCtc.addConstructor(CtNewConstructor.defaultConstructor(mCtc));
        }
        if (mConstructors != null) {
            for (String code : mConstructors) {
                if (code.charAt(0) == ':') {
                    mCtc.addConstructor(CtNewConstructor
                            .copy(getCtConstructor(mCopyConstructors.get(code.substring(1))), mCtc, null));
                } else {
                    String[] sn = mCtc.getSimpleName().split("\\$+"); // inner class name include $.
                    mCtc.addConstructor(
                            CtNewConstructor.make(code.replaceFirst(SIMPLE_NAME_TAG, sn[sn.length - 1]), mCtc));
                }
            }
        }
        // 将 mCtc 新创建的类转成 Class 对象
        try {
            return mPool.toClass(mCtc, neighborClass, loader, pd);
        } catch (Throwable t) {
            if (!(t instanceof CannotCompileException)) {
                return mPool.toClass(mCtc, loader, pd);
            }
            throw t;
        }
    } catch (RuntimeException e) {
        throw e;
    } catch (NotFoundException | CannotCompileException e) {
        throw new RuntimeException(e.getMessage(), e);
    }
}
```

基本了解如何使用之后，上一讲的代码模板，我们可以用 Javassist 实现一遍，代码如下：

```java
///////////////////////////////////////////////////
// 采用 Javassist 的 API 来动态创建代码模板
///////////////////////////////////////////////////
public class JavassistProxyUtils {
    private static final AtomicInteger INC = new AtomicInteger();
    public static Object newProxyInstance(Object sourceTarget) throws Exception{
        // ClassPool：Class对象的容器
        ClassPool pool = ClassPool.getDefault();

        // 通过ClassPool生成一个public类
        Class<?> targetClazz = sourceTarget.getClass().getInterfaces()[0];
        String proxyClassName = "$" + targetClazz.getSimpleName() + "CustomInvoker_" + INC.incrementAndGet();
        CtClass ctClass = pool.makeClass(proxyClassName);
        ctClass.setSuperclass(pool.get("com.hmilyylimh.cloud.compiler.custom.CustomInvoker"));

        // 添加方法  public Object invokeMethod(Object instance, String mtdName, Class<?>[] types, Object[] args) throws NoSuchMethodException { {...}
        CtClass returnType = pool.get("java.lang.Object");
        CtMethod newMethod=new CtMethod(
                returnType,
                "invokeMethod",
                new CtClass[]{ returnType, pool.get("java.lang.String"), pool.get("java.lang.Class[]"), pool.get("java.lang.Object[]") },
                ctClass);
        newMethod.setModifiers(Modifier.PUBLIC);
        newMethod.setBody(buildBody(targetClazz).toString());
        ctClass.addMethod(newMethod);

        // 生成 class 类
        Class<?> clazz = ctClass.toClass();

        // 将 class 文件写到 target 目录下，方便调试查看
        String filePath = JavassistProxyUtils.class.getResource("/").getPath()
                + JavassistProxyUtils.class.getPackage().toString().substring("package ".length()).replaceAll("\\.", "/");
        ctClass.writeFile(filePath);

        // 反射实例化创建对象
        return clazz.newInstance();
    }
    // 构建方法的内容字符串
    private static StringBuilder buildBody(Class<?> targetClazz) {
        StringBuilder sb = new StringBuilder("{\n");
        for (Method method : targetClazz.getDeclaredMethods()) {
            String methodName = method.getName();
            Class<?>[] parameterTypes = method.getParameterTypes();
            // if ("sayHello".equals(mtdName)) {
            String ifHead = "if (\"" + methodName + "\".equals($2)) {\n";
            // return ((DemoFacade) instance).sayHello(String.valueOf(args[0]));
            String ifContent = null;
            // 这里有 bug ，姑且就入参就传一个入参对象吧
            if(parameterTypes.length != 0){
                ifContent = "return ((" + targetClazz.getName() + ") $1)." + methodName + "(" + String.class.getName() + ".valueOf($4[0]));\n";
            } else {
                ifContent = "return ((" + targetClazz.getName() + ") $1)." + methodName + "();\n";
            }
            // }
            String ifTail = "}\n";
            sb.append(ifHead).append(ifContent).append(ifTail);
        }
        // throw new NoSuchMethodException("Method [" + mtdName + "] not found.");
        String invokeMethodTailContent = "throw new " + org.apache.dubbo.common.bytecode.NoSuchMethodException.class.getName() + "(\"Method [\" + $2 + \"] not found.\");\n}\n";
        sb.append(invokeMethodTailContent);
        return sb;
    }
}

```

可以发现确实比拼接字符串简单多了，而且 API 使用起来也比较清晰明了，完全按照平常的专业术语命名规范，马上就能找到对应的 API，根本不需要花很多准备工作。

用新方案编译源代码后，我们验证一下结果，编写测试验证代码。

```java
public static void main(String[] args) throws Exception {
    // 创建源对象（即被代理对象）
    DemoFacadeImpl demoFacade = new DemoFacadeImpl();
    // 生成自定义的代理类
    CustomInvoker invoker = (CustomInvoker) JavassistProxyUtils.newProxyInstance(demoFacade);
    // 调用代理类的方法
    invoker.invokeMethod(demoFacade, "sayHello", new Class[]{String.class}, new Object[]{"Geek"});
}
```

**ASM 编译**

既然 Javassist 这么好用，为什么公司的大佬还在用 ASM 进行操作呢？其实，ASM 是一款侧重于性能的字节码插件，属于一种轻量级的高性能字节码插件，但同时实现的难度系数也会变大。这么讲你也许会好奇了，能有多难？

我们还是举例来看，例子是把敏感字段加密存储到数据库。

![image-20250327231739352](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503272317784.png)

```java
public class UserBean {
    private String name;
    public UserBean(String name) { this.name = name; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    @Override
    public String toString() { return "UserBean{name='" + name + '\'' + '}'; }
}
```

上层业务有一个对象，创建对象后，需要给对象的 setName 方法进行赋值。

如果想要给传入的 name 字段进行加密，一般我们会这么做。

```java
// 先创建一个对象
UserBean userBean = new UserBean();
// 将即将赋值的 Geek 先加密，然后设置到 userBean 对象中
userBean.setName(AESUtils.encrypt("Geek"));
// 最后将 userBean 插入到数据库中
userDao.insertData(userBean);
```

把传入 setName 的值先进行加密处理，然后把加密后的值放到 userBean 对象中，在入库时，就能把密文写到数据库了。

但是这样就显得很累赘，今天这个字段需要加密，明天那个字段需要加密，那就没完没了，于是有人就想到了，可以将加密的这段操作内嵌到代理对象中，比如这样：

![图片](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503272318799.jpg)

在上层业务中，该怎么赋值还是继续怎么赋值，不用感知加密的操作，所有加密的逻辑全部内嵌到代理对象中。当然，如果这么做，就得设计一个代码模板，借助自定义代理的经验，想必你也有了设计思路：

```java
///////////////////////////////////////////////////
// 代码模板，将 UserBean 变成了 UserBeanHandler 代理对象，并且实现一个自己定义的 Handler 接口
///////////////////////////////////////////////////
public class UserBeanHandler implements Handler<UserBean> {
    @Override
    public void addBefore(UserBean u) {
        if (u.getName() != null && u.getName().length() > 0) {
            // 我这里仅仅只是告诉大家我针对了 name 的这个字段做了处理，
            // 以后大家应用到实际项目中的话，可以在这里将我们的 name 字段进行加密处理
            u.setName("#BEFORE#" + u.getName());
        }
    }
}

///////////////////////////////////////////////////
// 配合代码模板设计出来的一个接口
///////////////////////////////////////////////////
public interface Handler<T> {
    public void addBefore(T t);
}

```

代码模板的思路也很简单，主要注意 2 点。

- 设计一个对象的代理类，暴露一个 addBefore 方法来将字段进行加密操作。
- 代理类为了迎合具备一个 addBefore 方法，就得设计出一个接口，避免 Java 类单继承无法扩展的瓶颈。

代码模板是定义好了，可是操作字节码的时候，去哪里弄到该 UserBeanHandler 的字节码呢？

其实 IDEA 工具已经为你预留了一个查看字节码的入口。

![图片](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503272328371.png)

选中代码模板后，展开顶部的 View 菜单，选中 Show Bytecode 看到该类对应的字节码。

```java
// class version 50.0 (50)
// access flags 0x21
// signature Ljava/lang/Object;Lcom/hmilyylimh/cloud/compiler/asm/Handler<Lcom/hmilyylimh/cloud/compiler/asm/UserBean;>;
// declaration: com/hmilyylimh/cloud/compiler/asm/UserBeanHandler implements com.hmilyylimh.cloud.compiler.asm.Handler<com.hmilyylimh.cloud.compiler.asm.UserBean>
public class com/hmilyylimh/cloud/compiler/asm/UserBeanHandler extends Ljava/lang/Object; implements com/hmilyylimh/cloud/compiler/asm/Handler {

  // compiled from: UserBeanHandler.java

  // access flags 0x1
  public <init>()V
    ALOAD 0
    INVOKESPECIAL java/lang/Object.<init> ()V
    RETURN
    MAXSTACK = 1
    MAXLOCALS = 1

  // access flags 0x1
  public addBefore(Lcom/hmilyylimh/cloud/compiler/asm/UserBean;)V
    ALOAD 1
    INVOKEVIRTUAL com/hmilyylimh/cloud/compiler/asm/UserBean.getName ()Ljava/lang/String;
    IFNULL L0
    ALOAD 1
    INVOKEVIRTUAL com/hmilyylimh/cloud/compiler/asm/UserBean.getName ()Ljava/lang/String;
    INVOKEVIRTUAL java/lang/String.length ()I
    IFLE L0
    ALOAD 1
    NEW java/lang/StringBuilder
    DUP
    INVOKESPECIAL java/lang/StringBuilder.<init> ()V
    LDC "#BEFORE#"
    INVOKEVIRTUAL java/lang/StringBuilder.append (Ljava/lang/String;)Ljava/lang/StringBuilder;
    ALOAD 1
    INVOKEVIRTUAL com/hmilyylimh/cloud/compiler/asm/UserBean.getName ()Ljava/lang/String;
    INVOKEVIRTUAL java/lang/StringBuilder.append (Ljava/lang/String;)Ljava/lang/StringBuilder;
    INVOKEVIRTUAL java/lang/StringBuilder.toString ()Ljava/lang/String;
    INVOKEVIRTUAL com/hmilyylimh/cloud/compiler/asm/UserBean.setName (Ljava/lang/String;)V
   L0
   FRAME SAME
    RETURN
    MAXSTACK = 3
    MAXLOCALS = 2

  // access flags 0x1041
  public synthetic bridge addBefore(Ljava/lang/Object;)V
    ALOAD 0
    ALOAD 1
    CHECKCAST com/hmilyylimh/cloud/compiler/asm/UserBean
    INVOKEVIRTUAL com/hmilyylimh/cloud/compiler/asm/UserBeanHandler.addBefore (Lcom/hmilyylimh/cloud/compiler/asm/UserBean;)V
    RETURN
    MAXSTACK = 2
    MAXLOCALS = 2
}
```

看到一大片密密麻麻的字节码指令，想必你已经头都大了，不过别慌，这个问题在 [ASM 的官网指引](https://asm.ow2.io/developer-guide.html) 中也解答了，我们只需要按部就班把字节码指令翻译成为 Java 代码就可以了。

好吧，既然官网都这么贴心了，那就勉强当一回工具人，我们按照官网的指示，依葫芦画瓢把代码模板翻译出来。

经过一番漫长的翻译之后，我们终于写出了自己看看都觉得头皮发麻的长篇大论的代码，关键位置我都加注释了。

```java
///////////////////////////////////////////////////
// ASM 字节码操作的代理工具类
///////////////////////////////////////////////////
public class AsmProxyUtils implements Opcodes {
    /**
     * <h2>创建代理对象。</h2>
     *
     * @param originClass：样例：UserBean.class
     * @return
     */
    public static Object newProxyInstance(Class originClass) throws Exception{
        String newClzNameSuffix = "Handler";
        byte[] classBytes = generateByteCode(originClass, newClzNameSuffix);

        // 可以想办法将 classBytes 存储为一个文件
        String filePath = AsmProxyUtils.class.getResource("/").getPath()
                + AsmProxyUtils.class.getPackage().toString().substring("package ".length()).replaceAll("\\.", "/");
        FileOutputStream fileOutputStream = new FileOutputStream(new File(filePath,
                originClass.getSimpleName() + newClzNameSuffix + ".class"));
        fileOutputStream.write(classBytes);
        fileOutputStream.close();

        // 还得把 classBytes 加载到 JVM 内存中去
        ClassLoader loader = Thread.currentThread().getContextClassLoader();
        Class<?> loaderClass = Class.forName("java.lang.ClassLoader");
        Method defineClassMethod = loaderClass.getDeclaredMethod("defineClass",
                String.class,
                byte[].class,
                int.class,
                int.class);
        defineClassMethod.setAccessible(true);
        Object respObject = defineClassMethod.invoke(loader, new Object[]{
                originClass.getName() + newClzNameSuffix,
                classBytes,
                0,
                classBytes.length
        });

        // 实例化对象
        return ((Class)respObject).newInstance();
    }
    /**
     * <h2>生成字节码的核心。</h2><br/>
     *
     * <li><h2>注意：接下来的重点就是如何用asm来动态产生一个 UserBeanHandler 类。</h2></li>
     *
     * @param originClass：样例：UserBean.class
     * @param newClzNameSuffix： 样例：Handler
     * @return
     */
    private static byte[] generateByteCode(Class originClass, String newClzNameSuffix) {
        String newClassSimpleNameAndSuffix = originClass.getSimpleName() + newClzNameSuffix + ".java";
        /**********************************************************************/
        // 利用 ASM 编写创建类文件头的相关信息
        /**********************************************************************/
        ClassWriter classWriter = new ClassWriter(0);
        /////////////////////////////////////////////////////////
        // class version 50.0 (50)
        // access flags 0x21
        // signature Ljava/lang/Object;Lcom/hmilyylimh/cloud/compiler/asm/Handler<Lcom/hmilyylimh/cloud/compiler/asm/UserBean;>;
        // declaration: com/hmilyylimh/cloud/compiler/asm/UserBeanHandler implements com.hmilyylimh.cloud.compiler.asm.UserBean<com.hmilyylimh.cloud.compiler.asm.UserBean>
        // public class com/hmilyylimh/cloud/compiler/asm/UserBeanHandler extends Ljava/lang/Object; implements com/hmilyylimh/cloud/compiler/asm/Handler {
        /////////////////////////////////////////////////////////
        classWriter.visit(
                V1_6,
                ACC_PUBLIC + ACC_SUPER,
                Type.getInternalName(originClass) + newClzNameSuffix,
                Type.getDescriptor(Object.class)+Type.getDescriptor(Handler.class).replace(";","")+"<"+Type.getDescriptor(originClass)+">;",
                Type.getDescriptor(Object.class),
                new String[]{ Type.getInternalName(Handler.class) }
        );
        /////////////////////////////////////////////////////////
        // UserBeanHandler.java
        /////////////////////////////////////////////////////////
        classWriter.visitSource(newClassSimpleNameAndSuffix, null);
        /**********************************************************************/
        // 创建构造方法
        /**********************************************************************/
        /////////////////////////////////////////////////////////
        // compiled from: UserBeanHandler.java
        // access flags 0x1
        // public <init>()V
        /////////////////////////////////////////////////////////
        MethodVisitor initMethodVisitor = classWriter.visitMethod(
                ACC_PUBLIC,
                "<init>",
                "()V",
                null,
                null
        );
        initMethodVisitor.visitCode();
        /////////////////////////////////////////////////////////
        // ALOAD 0
        // INVOKESPECIAL java/lang/Object.<init> ()V
        // RETURN
        /////////////////////////////////////////////////////////
        initMethodVisitor.visitVarInsn(ALOAD, 0);
        initMethodVisitor.visitMethodInsn(INVOKESPECIAL,
                Type.getInternalName(Object.class),
                "<init>",
                "()V"
                );
        initMethodVisitor.visitInsn(RETURN);
        /////////////////////////////////////////////////////////
        // MAXSTACK = 1
        // MAXLOCALS = 1
        /////////////////////////////////////////////////////////
        initMethodVisitor.visitMaxs(1, 1);
        initMethodVisitor.visitEnd();

        /**********************************************************************/
        // 创建 addBefore 方法
        /**********************************************************************/
        /////////////////////////////////////////////////////////
        // access flags 0x1
        // public addBefore(Lcom/hmilyylimh/cloud/compiler/asm/UserBean;)V
        /////////////////////////////////////////////////////////
        MethodVisitor addBeforeMethodVisitor = classWriter.visitMethod(
                ACC_PUBLIC,
                "addBefore",
                "(" + Type.getDescriptor(originClass) + ")V",
                null,
                null
        );
        addBeforeMethodVisitor.visitCode();
        /////////////////////////////////////////////////////////
        // ALOAD 1
        // INVOKEVIRTUAL com/hmilyylimh/cloud/compiler/asm/UserBean.getName ()Ljava/lang/String;
        /////////////////////////////////////////////////////////
        addBeforeMethodVisitor.visitVarInsn(ALOAD, 1);
        addBeforeMethodVisitor.visitMethodInsn(INVOKEVIRTUAL,
                Type.getInternalName(originClass),
                "getName",
                "()" + Type.getDescriptor(String.class));
        /////////////////////////////////////////////////////////
        // IFNULL L0
        // ALOAD 1
        // INVOKEVIRTUAL com/hmilyylimh/cloud/compiler/asm/UserBean.getName ()Ljava/lang/String;
        // INVOKEVIRTUAL java/lang/String.length ()I
        // IFLE L0
        /////////////////////////////////////////////////////////
        Label L0 = new Label();
        addBeforeMethodVisitor.visitJumpInsn(IFNULL, L0);
        addBeforeMethodVisitor.visitVarInsn(ALOAD, 1);
        addBeforeMethodVisitor.visitMethodInsn(INVOKEVIRTUAL,
                Type.getInternalName(originClass),
                "getName",
                "()" + Type.getDescriptor(String.class));
        addBeforeMethodVisitor.visitMethodInsn(INVOKEVIRTUAL,
                Type.getInternalName(String.class),
                "length",
                "()I");
        addBeforeMethodVisitor.visitJumpInsn(IFLE, L0);
        /**********************************************************************/
        // 接下来要干的事情就是：u.setName("#BEFORE#" + u.getName());
        /**********************************************************************/
        /////////////////////////////////////////////////////////
        // ALOAD 1
        // NEW java/lang/StringBuilder
        // DUP
        /////////////////////////////////////////////////////////
        addBeforeMethodVisitor.visitVarInsn(ALOAD, 1);
        addBeforeMethodVisitor.visitTypeInsn(NEW, Type.getInternalName(StringBuilder.class));
        addBeforeMethodVisitor.visitInsn(DUP);
        /////////////////////////////////////////////////////////
        // INVOKESPECIAL java/lang/StringBuilder.<init> ()V
        // LDC "#BEFORE#"
        // INVOKEVIRTUAL java/lang/StringBuilder.append (Ljava/lang/String;)Ljava/lang/StringBuilder;
        /////////////////////////////////////////////////////////
        addBeforeMethodVisitor.visitMethodInsn(INVOKESPECIAL,
                Type.getInternalName(StringBuilder.class),
                "<init>",
                "()V");
        addBeforeMethodVisitor.visitLdcInsn("#BEFORE#");
        addBeforeMethodVisitor.visitMethodInsn(INVOKEVIRTUAL,
                Type.getInternalName(StringBuilder.class),
                "append",
                "("+ Type.getDescriptor(String.class) + ")" + Type.getDescriptor(StringBuilder.class));
        /////////////////////////////////////////////////////////
        // ALOAD 1
        // INVOKEVIRTUAL com/hmilyylimh/cloud/compiler/asm/UserBean.getName ()Ljava/lang/String;
        // INVOKEVIRTUAL java/lang/StringBuilder.append (Ljava/lang/String;)Ljava/lang/StringBuilder;
        // NVOKEVIRTUAL java/lang/StringBuilder.toString ()Ljava/lang/String;
        // INVOKEVIRTUAL com/hmilyylimh/cloud/compiler/asm/UserBean.setName (Ljava/lang/String;)V
        /////////////////////////////////////////////////////////
        addBeforeMethodVisitor.visitVarInsn(ALOAD, 1);
        addBeforeMethodVisitor.visitMethodInsn(INVOKEVIRTUAL,
                Type.getInternalName(originClass),
                "getName",
                "()" + Type.getDescriptor(String.class));
        addBeforeMethodVisitor.visitMethodInsn(INVOKEVIRTUAL,
                Type.getInternalName(StringBuilder.class),
                "append",
                "("+ Type.getDescriptor(String.class) + ")" + Type.getDescriptor(StringBuilder.class));
        addBeforeMethodVisitor.visitMethodInsn(INVOKEVIRTUAL,
                Type.getInternalName(StringBuilder.class),
                "toString",
                "()" + Type.getDescriptor(String.class));
        addBeforeMethodVisitor.visitMethodInsn(INVOKEVIRTUAL,
                Type.getInternalName(originClass),
                "setName",
                "(" + Type.getDescriptor(String.class)+")V");
        /////////////////////////////////////////////////////////
        // L0
        // FRAME SAME
        // RETURN
        /////////////////////////////////////////////////////////
        addBeforeMethodVisitor.visitLabel(L0);
        addBeforeMethodVisitor.visitFrame(F_SAME, 0, null, 0, null);
        addBeforeMethodVisitor.visitInsn(RETURN);
        /////////////////////////////////////////////////////////
        // LMAXSTACK = 3
        // MAXLOCALS = 2
        /////////////////////////////////////////////////////////
        addBeforeMethodVisitor.visitMaxs(3, 2);
        addBeforeMethodVisitor.visitEnd();
        /**********************************************************************/
        // 创建桥接 addBefore 方法
        /**********************************************************************/
        /////////////////////////////////////////////////////////
        // access flags 0x1041
        // public synthetic bridge addBefore(Ljava/lang/Object;)V
        /////////////////////////////////////////////////////////
        MethodVisitor bridgeAddBeforeMethodVisitor = classWriter.visitMethod(ACC_PUBLIC + ACC_SYNTHETIC + ACC_BRIDGE,
                "addBefore",
                "(" + Type.getDescriptor(Object.class) + ")V",
                null,
                null
        );
        bridgeAddBeforeMethodVisitor.visitCode();
        /////////////////////////////////////////////////////////
        // ALOAD 0
        // ALOAD 1
        /////////////////////////////////////////////////////////
        bridgeAddBeforeMethodVisitor.visitVarInsn(ALOAD, 0);
        bridgeAddBeforeMethodVisitor.visitVarInsn(ALOAD, 1);
        /////////////////////////////////////////////////////////
        // CHECKCAST com/hmilyylimh/cloud/compiler/asm/UserBean
        // INVOKEVIRTUAL com/hmilyylimh/cloud/compiler/asm/UserBeanHandler.addBefore (Lcom/hmilyylimh/cloud/compiler/asm/UserBean;)V
        // RETURN
        /////////////////////////////////////////////////////////
        bridgeAddBeforeMethodVisitor.visitTypeInsn(CHECKCAST, Type.getInternalName(originClass));
        bridgeAddBeforeMethodVisitor.visitMethodInsn(INVOKEVIRTUAL,
                Type.getInternalName(originClass) + newClzNameSuffix,
                "addBefore",
                "(" + Type.getDescriptor(originClass) + ")V");
        bridgeAddBeforeMethodVisitor.visitInsn(RETURN);
        /////////////////////////////////////////////////////////
        // MAXSTACK = 2
        // MAXLOCALS = 2
        /////////////////////////////////////////////////////////
        bridgeAddBeforeMethodVisitor.visitMaxs(2, 2);
        bridgeAddBeforeMethodVisitor.visitEnd();
        /**********************************************************************/
        // 创建结束
        /**********************************************************************/
        classWriter.visitEnd();
        return classWriter.toByteArray();
    }
}
```

写的过程有些卡壳，难度系数也不低，我们有 3 个小点要注意。

- 有些字节码指令不知道如何使用 ASM API，比如 INVOKESPECIAL 不知道怎么调用 API，你可以网络检索一下“ **MethodVisitor INVOKESPECIAL**”关键字，就能轻松找到与之对应的 API 了。
- 重点关注调用 API 各参数的位置，千万别放错了，否则问题排查起来比较费时间。
- 生成的字节码文件直接保存到文件中，然后利用 ClassLoader.defineClass 方法，把字节码交给 JVM 虚拟机直接变成一个 Class 类型实例。

在写的时候，你一定要沉下心慢慢转换，一步都不能错，否则时间浪费了还得不到有效的成果。

写好之后，你一定非常兴奋，我们还是先写个测试代码验证一下：

```java
public static void main(String[] args) throws Exception {
    UserBean userBean = new UserBean("Geek");
    // 从 mybatis 的拦截器里面拿到了准备更新 db 的数据对象，然后创建代理对象
    Handler handler = (Handler) AsmProxyUtils.newProxyInstance(userBean.getClass());
    // 关键的一步，在 mybatis 中模拟将入参对象进行加密操作
    handler.addBefore(userBean);
    // 这里为了观察效果，先打印一下 userBean 的内容看看
    System.out.println(userBean);

    // 接下来，假设有执行 db 的操作，那就直接将密文入库了

    // db 操作完成之后，还得将 userBean 的密文变成明文，这里应该还有 addAfter 解密操作
}
```

打印输出的内容为：

```java
打印一下加密内容: UserBean{name='#BEFORE#Geek'}
```

结果如预期所料，把入参的数据成功加密了，我们终于可以喘口气了，不过辛苦是值得的，学到了大量的底层 ASM 操控字节码的知识，也见识到了底层功能的强大威力。

**Compiler 编译方式的适用场景**

今天我们见识到 Javassist 和 ASM 的强大威力，之前也用过JavaCompiler和Groovy 插件，这么多款工具可以编译生成类信息，有哪些适用场景呢？

- JavaCompiler：是 JDK 提供的一个工具包，我们熟知的 Javac 编译器其实就是 JavaCompiler 的实现，不过JDK 的版本迭代速度快，变化大，我们升级 JDK 的时候，本来在低版本 JDK 能正常编译的功能，跑到高版本就失效了。
- Groovy：属于第三方插件，功能很多很强大，几乎是开发小白的首选框架，不需要考虑过多 API 和字节码指令，会构建源代码字符串，交给 Groovy 插件后就能拿到类信息，拿起来就可以直接使用，但同时也是比较重量级的插件。
- Javassist：封装了各种API来创建类，相对于稍微偏底层的风格，可以动态针对已有类的字节码，调用相关的 API 直接增删改查，非常灵活，只要熟练使用 API 就可以达到很高的境界。
- ASM：是一个通用的字节码操作的框架，属于非常底层的插件了，操作该插件的技术难度相当高，需要对字节码指令有一定的了解，但它体现出来的性能却是最高的，并且插件本身就是定位为一款轻量级的高性能字节码插件。

有了众多动态编译方式的法宝，从简单到复杂，从重量级到轻量级，你都学会了，相信再遇到一堆神乎其神的Compiler 编译方式，内心也不会胆怯了。

不过工具多了，有同学可能就有选择困难症，这里我也讲下个人的选择标准。

如果需要开发一些底层插件，我倾向使用 Javassist 或者 ASM。使用 Javassist 是因为用API 简单而且方便后人维护，使用 ASM 是在一些高度频繁调用的场景出于对性能的极致追求。如果开发应用系统的业务功能，对性能没有太强的追求，而且便于加载和卸载，我倾向使用 Groovy 这款插件。

# 17｜Adaptive适配：Dubbo的Adaptive特殊在哪里？

深入 Dubbo SPI 机制的底层原理时，在加载并解析 SPI 文件的逻辑中，你会看到有一段专门针对 Adaptive 注解进行处理的代码；在 Dubbo 内置的被 @SPI 注解标识的接口中，你同样会看到好多方法上都有一个 @Adaptive 注解。

这么多代码和功能都与 Adaptive 有关，难道有什么特殊含义么？Adaptive究竟是用来干什么的呢？我们开始今天的学习。

**自适应扩展点**

我们还是设计一下验证的大体代码结构：

![图片](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503282329646.jpg)

图中，定义了一个 Geek 接口，然后有 3 个实现类，分别是 Dubbo、SpringCloud 和 AdaptiveGeek，但是 AdaptiveGeek 实现类上有 @Adaptive 注解。

有了这种结构图，鉴于刚分析的结论，@Adaptive 在实现类上还是在方法上，会有很大的区别，所以我们做两套验证方案。

- 验证方案一：只有两个实现类 Dubbo 和 SpringCloud，然后 @Adaptive 添加在 Geek 接口的方法上。
- 验证方法二：在验证方案一的基础之上，再添加一个实现类 AdaptiveGeek 并添加 @Adaptive 注解。

设计完成，我们编写代码。

```java
///////////////////////////////////////////////////
// SPI 接口：Geek，默认的扩展点实现类是 Dubbo 实现类
// 并且该接口的 getCourse 方法上有一个 @Adaptive 注解
///////////////////////////////////////////////////
@SPI("dubbo")
public interface Geek {
    @Adaptive
    String getCourse(URL url);
}
///////////////////////////////////////////////////
// Dubbo 实现类
///////////////////////////////////////////////////
public class Dubbo implements Geek {
    @Override
    public String getCourse(URL url) {
        return "Dubbo实战进阶课程";
    }
}
///////////////////////////////////////////////////
// SpringCloud 实现类
///////////////////////////////////////////////////
public class SpringCloud implements Geek {
    @Override
    public String getCourse(URL url) {
        return "SpringCloud入门课程100集";
    }
}
///////////////////////////////////////////////////
// 资源目录文件
// 路径为：/META-INF/dubbo/com.hmilyylimh.cloud.adaptive.spi.Geek
///////////////////////////////////////////////////
dubbo=com.hmilyylimh.cloud.adaptive.spi.Dubbo
springcloud=com.hmilyylimh.cloud.adaptive.spi.SpringCloud

///////////////////////////////////////////////////
// 启动类，验证代码用的
///////////////////////////////////////////////////
public static void main(String[] args) {
    ApplicationModel applicationModel = ApplicationModel.defaultModel();
    // 通过 Geek 接口获取指定像 扩展点加载器
    ExtensionLoader<Geek> extensionLoader = applicationModel.getExtensionLoader(Geek.class);

    Geek geek = extensionLoader.getAdaptiveExtension();
    System.out.println("【指定的 geek=springcloud 的情况】动态获取结果为: "
            + geek.getCourse(URL.valueOf("xyz://127.0.0.1/?geek=springcloud")));
    System.out.println("【指定的 geek=dubbo 的情况】动态获取结果为: "
            + geek.getCourse(URL.valueOf("xyz://127.0.0.1/?geek=dubbo")));
    System.out.println("【不指定的 geek 走默认情况】动态获取结果为: "
            + geek.getCourse(URL.valueOf("xyz://127.0.0.1/")));
    System.out.println("【随便指定 geek=xyz 走报错情况】动态获取结果为: "
            + geek.getCourse(URL.valueOf("xyz://127.0.0.1/?geek=xyz")));
}
```

运行结果如下：

```
【指定的 geek=springcloud 的情况】动态获取结果为: SpringCloud入门课程100集
【指定的 geek=dubbo 的情况】动态获取结果为: Dubbo实战进阶课程
【不指定的 geek 走默认情况】动态获取结果为: Dubbo实战进阶课程
Exception in thread "main" java.lang.IllegalStateException: No such extension com.hmilyylimh.cloud.adaptive.spi.Geek by name xyz, no related exception was found, please check whether related SPI module is missing.
	at org.apache.dubbo.common.extension.ExtensionLoader.findException(ExtensionLoader.java:747)
	at org.apache.dubbo.common.extension.ExtensionLoader.createExtension(ExtensionLoader.java:754)
	at org.apache.dubbo.common.extension.ExtensionLoader.getExtension(ExtensionLoader.java:548)
	at org.apache.dubbo.common.extension.ExtensionLoader.getExtension(ExtensionLoader.java:523)
	at com.hmilyylimh.cloud.adaptive.spi.Geek$Adaptive.getCourse(Geek$Adaptive.java)
	at com.hmilyylimh.cloud.adaptive.Dubbo17DubboAdaptiveApplication.main(Dubbo17DubboAdaptiveApplication.java:24)
```

从验证方案一的实施结果来看，在 URL 中指定 geek 参数的值为 springcloud 或 dubbo，都能走到正确的实现类逻辑中，不指定 geek 参数就走默认的实现类，随便指定 geek 参数的值就会抛出异常。

接着实施验证方案二：

```java
///////////////////////////////////////////////////
// SPI 接口：Geek，默认的扩展点实现类是 Dubbo 实现类
// 并且该接口的 getCourse 方法上有一个 @Adaptive 注解
///////////////////////////////////////////////////
@SPI("dubbo")
public interface Geek {
    @Adaptive
    String getCourse(URL url);
}
///////////////////////////////////////////////////
// Dubbo 实现类
///////////////////////////////////////////////////
public class Dubbo implements Geek {
    @Override
    public String getCourse(URL url) {
        return "Dubbo实战进阶课程";
    }
}
///////////////////////////////////////////////////
// SpringCloud 实现类
///////////////////////////////////////////////////
public class SpringCloud implements Geek {
    @Override
    public String getCourse(URL url) {
        return "SpringCloud入门课程100集";
    }
}
///////////////////////////////////////////////////
// AdaptiveGeek 实现类，并且该实现类上有一个 @Adaptive 注解
///////////////////////////////////////////////////
@Adaptive
public class AdaptiveGeek implements Geek {
    @Override
    public String getCourse(URL url) {
        return "17｜Adaptive 适配：Dubbo的Adaptive特殊在哪里？";
    }
}
///////////////////////////////////////////////////
// 资源目录文件
// 路径为：/META-INF/dubbo/com.hmilyylimh.cloud.adaptive.spi.Geek
///////////////////////////////////////////////////
dubbo=com.hmilyylimh.cloud.adaptive.spi.Dubbo
springcloud=com.hmilyylimh.cloud.adaptive.spi.SpringCloud
adaptivegeek=com.hmilyylimh.cloud.adaptive.spi.AdaptiveGeek

///////////////////////////////////////////////////
// 启动类，验证代码用的
///////////////////////////////////////////////////
public static void main(String[] args) {
    ApplicationModel applicationModel = ApplicationModel.defaultModel();
    // 通过 Geek 接口获取指定像 扩展点加载器
    ExtensionLoader<Geek> extensionLoader = applicationModel.getExtensionLoader(Geek.class);

    Geek geek = extensionLoader.getAdaptiveExtension();
    System.out.println("【指定的 geek=springcloud 的情况】动态获取结果为: "
            + geek.getCourse(URL.valueOf("xyz://127.0.0.1/?geek=springcloud")));
    System.out.println("【指定的 geek=dubbo 的情况】动态获取结果为: "
            + geek.getCourse(URL.valueOf("xyz://127.0.0.1/?geek=dubbo")));
    System.out.println("【不指定的 geek 走默认情况】动态获取结果为: "
            + geek.getCourse(URL.valueOf("xyz://127.0.0.1/")));
    System.out.println("【随便指定 geek=xyz 走报错情况】动态获取结果为: "
            + geek.getCourse(URL.valueOf("xyz://127.0.0.1/?geek=xyz")));
}
```

运行结果如下：

```
【指定的 geek=springcloud 的情况】动态获取结果为: 17｜Adaptive 适配：Dubbo的Adaptive特殊在哪里？
【指定的 geek=dubbo 的情况】动态获取结果为: 17｜Adaptive 适配：Dubbo的Adaptive特殊在哪里？
【不指定的 geek 走默认情况】动态获取结果为: 17｜Adaptive 适配：Dubbo的Adaptive特殊在哪里？
【随便指定 geek=xyz 走报错情况】动态获取结果为: 17｜Adaptive 适配：Dubbo的Adaptive特殊在哪里？
```

从方案二的验证结果来看，一旦走进了带有 @Adaptive 注解的实现类后，所有的逻辑就完全按照该实现类去执行了，也就不存在动态代理逻辑一说了。

**源码跟踪**

我们就先从 ExtensionLoader 的 getAdaptiveExtension 方法开始吧。getAdaptiveExtension 方法是如何被使用的呢？

```java
Cluster cluster = ExtensionLoader
    // 获取 Cluster 接口对应扩展点加载器
    .getExtensionLoader(Cluster.class)
    // 从 Cluster 扩展点加载器中获取自适应的扩展点
    .getAdaptiveExtension();
```

getAdaptiveExtension 方法：

![image-20250328234027767](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503282340034.png)

从 getAdaptiveExtension 方法中，我们可以知道，最核心的方法是 createAdaptiveExtension 方法。

```java
// org.apache.dubbo.common.extension.ExtensionLoader#getAdaptiveExtensionClass
// 创建自适应扩展点方法
private T createAdaptiveExtension() {
    try {
        // 这一行从 newInstance 这个关键字便知道这行代码就是创建扩展点的核心代码
        T instance = (T) getAdaptiveExtensionClass().newInstance();

        // 这里针对创建出来的实例对象做的一些类似 Spring 的前置后置的方式处理
        instance = postProcessBeforeInitialization(instance, null);
        instance = injectExtension(instance);
        instance = postProcessAfterInitialization(instance, null);
        initExtension(instance);
        return instance;
    } catch (Exception e) {
        throw new IllegalStateException("Can't create adaptive extension " + type + ", cause: " + e.getMessage(), e);
    }
}
                  ↓
// 获取自适应扩展点的类对象
private Class<?> getAdaptiveExtensionClass() {
    // 获取当前扩展点（Cluster）的加载器（ExtensionLoader）中的所有扩展点
    getExtensionClasses();
    // 如果缓存的自适应扩展点不为空的话，就提前返回
    // 这里也间接的说明了一点，每个扩展点（Cluster）只有一个自适应扩展点对象
    if (cachedAdaptiveClass != null) {
        return cachedAdaptiveClass;
    }
    // 这里便是创建自适应扩展点类对象的逻辑，我们需要直接进入没有缓存时的创建逻辑
    return cachedAdaptiveClass = createAdaptiveExtensionClass();
}
                  ↓
// 创建自适应扩展点类对象
private Class<?> createAdaptiveExtensionClass() {
    // Adaptive Classes' ClassLoader should be the same with Real SPI interface classes' ClassLoader
    ClassLoader classLoader = type.getClassLoader();
    try {
        if (NativeUtils.isNative()) {
            return classLoader.loadClass(type.getName() + "$Adaptive");
        }
    } catch (Throwable ignore) {
    }
    // 看见这行关键代码，发现使用了一个叫做扩展点源码生成器的类
    // 看意思，就是调用 generate 方法生成一段 Java 编写的源代码
    String code = new AdaptiveClassCodeGenerator(type, cachedDefaultName).generate();
    // 紧接着把源代码传入了 Compiler 接口的扩展点
    // 这个 Compiler 接口不就是我们上一讲思考题刚学过的知识点么
    org.apache.dubbo.common.compiler.Compiler compiler = extensionDirector.getExtensionLoader(
        org.apache.dubbo.common.compiler.Compiler.class).getAdaptiveExtension();
    // 通过调用 compile 方法，也就大致明白了，就是通过源代码生成一个类对象而已
    return compiler.compile(type, code, classLoader);
}
```

进入 createAdaptiveExtension 源码，通读一遍大致的逻辑，我们总结出了 3 点。

1. 在 Dubbo 框架里，自适应扩展点是通过双检索（DCL）以线程安全的形式创建出来的。
2. 创建自适应扩展点时，每个接口有且仅有一个自适应扩展点。
3. 自适应扩展点的创建，是通过生成了一段 Java 的源代码，然后使用 Compiler 接口编译生成了一个类对象，这说明自适应扩展点是动态生成的。

我们通过断点的方式，把 code 源代码拷贝出来。

```java
package org.apache.dubbo.rpc.cluster;
import org.apache.dubbo.rpc.model.ScopeModel;
import org.apache.dubbo.rpc.model.ScopeModelUtil;
// 类名比较特别，是【接口的简单名称】+【$Adaptive】构成的
// 这就是自适应动态扩展点对象的类名
public class Cluster$Adaptive implements org.apache.dubbo.rpc.cluster.Cluster {
    public org.apache.dubbo.rpc.Invoker join(org.apache.dubbo.rpc.cluster.Directory arg0, boolean arg1) throws org.apache.dubbo.rpc.RpcException {
        // 如果 Directory 对象为空的话，则抛出异常
        // 一般正常的逻辑是不会走到为空的逻辑里面的，这是一种健壮性代码考虑
        if (arg0 == null) throw new IllegalArgumentException("org.apache.dubbo.rpc.cluster.Directory argument == null");
        // 若 Directory  对象中的 URL 对象为空抛异常，同样是健壮性代码考虑
        if (arg0.getUrl() == null)
            throw new IllegalArgumentException("org.apache.dubbo.rpc.cluster.Directory argument getUrl() == null");
        org.apache.dubbo.common.URL url = arg0.getUrl();
        // 这里关键点来了，如果从 url 中取出 cluster 为空的话
        // 则使用默认的 failover 属性，这不恰好就证实了若不配置的走默认逻辑，就在这里体现了
        String extName = url.getParameter("cluster", "failover");
        if (extName == null)
            throw new IllegalStateException("Failed to get extension (org.apache.dubbo.rpc.cluster.Cluster) name from" +
                    " url (" + url.toString() + ") use keys([cluster])");
        ScopeModel scopeModel = ScopeModelUtil.getOrDefault(url.getScopeModel(),
                org.apache.dubbo.rpc.cluster.Cluster.class);
        // 反正得到了一个 extName 扩展点名称，则继续获取指定的扩展点
        org.apache.dubbo.rpc.cluster.Cluster extension =
                (org.apache.dubbo.rpc.cluster.Cluster) scopeModel.getExtensionLoader(org.apache.dubbo.rpc.cluster.Cluster.class)
                .getExtension(extName);
        // 拿着指定的扩展点继续调用其对应的方法
        return extension.join(arg0, arg1);
    }
    // 这里默认抛异常，说明不是自适应扩展点需要处理的业务逻辑
    public org.apache.dubbo.rpc.cluster.Cluster getCluster(org.apache.dubbo.rpc.model.ScopeModel arg0,
                                                           java.lang.String arg1) {
        throw new UnsupportedOperationException("The method public static org.apache.dubbo.rpc.cluster.Cluster org" +
                ".apache.dubbo.rpc.cluster.Cluster.getCluster(org.apache.dubbo.rpc.model.ScopeModel,java.lang.String)" +
                " of interface org.apache.dubbo.rpc.cluster.Cluster is not adaptive method!");
    }
    // 这里默认也抛异常，说明也不是自适应扩展点需要处理的业务逻辑
    public org.apache.dubbo.rpc.cluster.Cluster getCluster(org.apache.dubbo.rpc.model.ScopeModel arg0,
                                                           java.lang.String arg1, boolean arg2) {
        throw new UnsupportedOperationException("The method public static org.apache.dubbo.rpc.cluster.Cluster org" +
                ".apache.dubbo.rpc.cluster.Cluster.getCluster(org.apache.dubbo.rpc.model.ScopeModel,java.lang.String," +
                "boolean) of interface org.apache.dubbo.rpc.cluster.Cluster is not adaptive method!");
    }
    // !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    // 重点推导
    // !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    // 然后继续看看 Cluster，得搞清楚为什么两个 getCluster 方法会抛异常，而 join 方法不抛异常
    // 结果发现接口中的 join 方法被 @Adaptive 注解标识了，但是另外 2 个 getCluster 方法没有被 @Adaptive 标识
    // 由此可以说明一点，含有被 @Adaptive 注解标识的 SPI 接口，是会生成自适应代理对象的
}
```

仔细看完自适应扩展点对应的源代码，你会发现一个很奇怪的现象，为什么 join 方法不抛异常，而另外两个 getCluster 方法会抛异常呢？

我们进入 Cluster 接口看看，发现： **CLuster 接口中的 join 方法被 @Adaptive 注解标识了，但是另外 2 个 getCluster 方法没有被 @Adaptive 标识。**所以，我们可以大胆推测，在生成自适应扩展点源代码的时候，应该是识别了具有 @Adaptive 注解的方法，方法有注解的话，就为这个方法生成对应的代理逻辑。

# 18｜实例注入：实例注入机制居然可以如此简单？

Dubbo 的实例注入机制是怎样的？与Spring有哪些异同？我们开始今天的学习。

**Dubbo 实例注入验证**

先设计一下验证的大体代码结构：

![image-20250407231314165](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504072313414.png)

先定义一个 Geek 接口，有 4 个实现类，分别是 Dubbo、SpringCloud 、AppleWrapper 和 GeekWrapper，但是 AppleWrapper、GeekWrapper 包装类上有 @Wrapper 注解。然后定义了一个 Animal 接口，只有 1 个实现类 Monkey。

我们需要验证3个功能点：

- 功能点一：通过 setter 可以实现指定实现类的注入。
- 功能点二：通过设计一个构造方法只有一个入参，且入参对应的 SPI 接口，可以把实现类变成包装类。比如这样：

```java
public class GeekWrapper implements Geek {
    private Geek geek;
    // GeekWrapper 的带参构造方法，只不过参数是当前实现类对应的 SPI 接口（Geek）
    public GeekWrapper(Geek geek) {
        this.geek = geek;
    }
    // 省略其他部分代码...
}
```

- 功能点三：@Wrapper 注解中的 mismatches 是可以剔除一些扩展点名称的，比如这样：

```java
@Wrapper(order = 10, mismatches = {"springcloud"})
```

设计完成，我们编写代码。

```java
///////////////////////////////////////////////////
// SPI 接口：Geek，默认的扩展点实现类是 Dubbo 实现类
// 并且该接口的 getCourse 方法上有一个 @Adaptive 注解
///////////////////////////////////////////////////
@SPI("dubbo")
public interface Geek {
    @Adaptive
    String getCourse(URL url);
}
///////////////////////////////////////////////////
// Dubbo 实现类
///////////////////////////////////////////////////
public class Dubbo implements Geek {
    @Override
    public String getCourse(URL url) {
        return "Dubbo实战进阶课程";
    }
}
///////////////////////////////////////////////////
// SpringCloud 实现类
///////////////////////////////////////////////////
public class SpringCloud implements Geek {
    @Override
    public String getCourse(URL url) {
        return "SpringCloud入门课程100集";
    }
}
///////////////////////////////////////////////////
// AppleWrapper 实现类，并且该实现类上有一个 @Wrapper 注解, order 越小越先执行
///////////////////////////////////////////////////
@Wrapper(order = 1)
public class AppleWrapper implements Geek {
    private Geek geek;
    public AppleWrapper(Geek geek) {
        this.geek = geek;
    }
    @Override
    public String getCourse(URL url) {
        return "【课程AppleWrapper前...】" + geek.getCourse(url) + "【课程AppleWrapper后...】";
    }
}
///////////////////////////////////////////////////
// GeekWrapper 实现类，并且该实现类上有一个 @Wrapper 注解,
// order 越小越先执行，所以 GeekWrapper 会比 AppleWrapper 后执行
// 然后还有一个 mismatches 属性为 springcloud
///////////////////////////////////////////////////
@Wrapper(order = 10, mismatches = {"springcloud"})
public class GeekWrapper implements Geek {
    private Geek geek;
    private Animal monkey;
    public void setMonkey(Animal monkey){
        this.monkey = monkey;
    }
    public GeekWrapper(Geek geek) {
        this.geek = geek;
    }
    @Override
    public String getCourse(URL url) {
        return "【课程GeekWrapper前...】" + geek.getCourse(url) + "【课程GeekWrapper后...】||【"+monkey.eat(url)+"】";
    }
}

///////////////////////////////////////////////////
// SPI 接口：Animal ，默认的扩展点实现类是 Monkey 实现类
// 并且该接口的 eat 方法上有一个 @Adaptive 注解
///////////////////////////////////////////////////
@SPI("monkey")
public interface Animal {
    @Adaptive
    String eat(URL url);
}
///////////////////////////////////////////////////
// Dubbo 实现类
///////////////////////////////////////////////////
public class Monkey implements Animal {
    @Override
    public String eat(URL url) {
        return "猴子吃香蕉";
    }
}
///////////////////////////////////////////////////
// 资源目录文件
// 路径为：/META-INF/dubbo/com.hmilyylimh.cloud.inject.spi.Geek
// 注意：GeekWrapper、AppleWrapper 两个包装类是可以不用写别名的
///////////////////////////////////////////////////
dubbo=com.hmilyylimh.cloud.inject.spi.Dubbo
springcloud=com.hmilyylimh.cloud.inject.spi.SpringCloud
com.hmilyylimh.cloud.inject.spi.GeekWrapper
com.hmilyylimh.cloud.inject.spi.AppleWrapper

///////////////////////////////////////////////////
// 资源目录文件
// 路径为：/META-INF/dubbo/com.hmilyylimh.cloud.inject.spi.Animal
///////////////////////////////////////////////////
monkey=com.hmilyylimh.cloud.inject.spi.Monkey

///////////////////////////////////////////////////
// 启动类，验证代码用的
///////////////////////////////////////////////////
public static void main(String[] args) {
    ApplicationModel applicationModel = ApplicationModel.defaultModel();
    // 通过 Geek 接口获取指定像 扩展点加载器
    ExtensionLoader<Geek> extensionLoader = applicationModel.getExtensionLoader(Geek.class);
    Geek geek = extensionLoader.getAdaptiveExtension();
    System.out.println("日志1：【指定的 geek=springcloud 的情况】动态获取结果为: "
            + geek.getCourse(URL.valueOf("xyz://127.0.0.1/?geek=springcloud")));
    System.out.println("日志2：【指定的 geek=dubbo 的情况】动态获取结果为: "
            + geek.getCourse(URL.valueOf("xyz://127.0.0.1/?geek=dubbo")));
    System.out.println("日志3：【不指定的 geek 走默认情况】动态获取结果为: "
            + geek.getCourse(URL.valueOf("xyz://127.0.0.1/")));
}
```

运行一下，看打印结果。

```
日志1：【指定的 geek=springcloud 的情况】动态获取结果为: 【课程AppleWrapper前...】SpringCloud入门课程100集【课程AppleWrapper后...】
日志2：【指定的 geek=dubbo 的情况】动态获取结果为: 【课程AppleWrapper前...】【课程GeekWrapper前...】Dubbo实战进阶课程【课程GeekWrapper后...】||【猴子吃香蕉】【课程AppleWrapper后...】
日志3：【不指定的 geek 走默认情况】动态获取结果为: 【课程AppleWrapper前...】【课程GeekWrapper前...】Dubbo实战进阶课程【课程GeekWrapper后...】||【猴子吃香蕉】【课程AppleWrapper后...】
```

日志1，指定 geek=springcloud 的时候，我们发现 GeekWrapper 并没有执行，说明当@Wrapper 中的 mismatches 属性值，包含入参给定的扩展名称，那么这个 GeekWrapper 就不会触发执行。

日志2，指定 geek=dubbo 的时候，两个包装器都执行了，说明构造方法确实注入成功了，构造方法的注入让实现类变成了一个包装类。

日志2和3，发现了“猴子吃香蕉”的文案，说明在 GeekWrapper 中 setter 注入也成功了。另外，还可以看到 AppleWrapper 总是在 GeekWrapper 之前打印执行，说明 @Wrapper 注解中的 order 属性值越小就越先执行，并且包装类还有一种类似切面思想的功能，在方法调用之前、之后进行额外的业务逻辑处理。

最后，从资源目录 SPI 文件内容中可以发现，包装类不需要设置别名，也可以被正确无误地识别出来。

**Spring 和 Dubbo 在实例注入层面的区别**

Spring 支持三种方式注入，字段属性注入、setter 方法注入、构造方法注入。Dubbo 的注入方式只有 setter 方法注入和构造方法注入这2种，并且 Dubbo 的构造方法注入还有局限性，构造方法的入参个数只能是一个，且入参类型必须为当前实现类对应的 SPI 接口类型。

# 19｜发布流程：带你一窥服务发布的三个重要环节

发布的大致流程就 3 个环节“ **配置 -> 导出 -\> 注册**”。

![image-20250409231717397](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504092317591.png)

第 ① 步编写提供方的 XML 配置文件，服务的发布首先需要进行一系列的配置，配置好后，可以通过 dubbo:service 标签进行服务的导出与注册，然后，在第 ③ 步中，提供方可以通过设置 dubbo.application.register-mode 属性来自由控制服务的注册方式。

**配置**

我们开始吧，先来简单看看提供方的一段代码。

```java
///////////////////////////////////////////////////
// 提供方应用工程的启动类
///////////////////////////////////////////////////
// 启动Dubbo框架的注解
@EnableDubbo
// SpringBoot应用的一键式启动注解
@SpringBootApplication
public class Dubbo19DubboDeployProviderApplication {
    public static void main(String[] args) {
        // 调用最为普通常见的应用启动API
        SpringApplication.run(Dubbo19DubboDeployProviderApplication.class, args);
        // 启动成功后打印一条日志
        System.out.println("【【【【【【 Dubbo19DubboDeployProviderApplication 】】】】】】已启动.");
    }
}
///////////////////////////////////////////////////
// 提供方应用工程的启动配置
///////////////////////////////////////////////////
@Configuration
public class DeployProviderConfig {
    // 提供者的应用服务名称
    @Bean
    public ApplicationConfig applicationConfig() {
        return new ApplicationConfig("dubbo-19-dubbo-deploy-provider");
    }
    // 注册中心的地址，通过 address 填写的地址提供方就可以联系上 zk 服务
    @Bean
    public RegistryConfig registryConfig() {
        return new RegistryConfig("zookeeper://127.0.0.1:2181");
    }
    // 提供者需要暴露服务的协议，提供者需要暴露服务的端口
    @Bean
    public ProtocolConfig protocolConfig(){
        return new ProtocolConfig("dubbo", 28190);
    }
}
///////////////////////////////////////////////////
// 提供方应用工程的一个DemoFacade服务
///////////////////////////////////////////////////
@Component
@DubboService(timeout = 8888)
public class DemoFacadeImpl implements DemoFacade {
    @Override
    public String sayHello(String name) {
        String result = String.format("Hello %s, I'm in 'dubbo-19-dubbo-deploy-provider.", name);
        System.out.println(result);
        return result;
    }
}
///////////////////////////////////////////////////
// 资源目录文件
// 路径为：/dubbo.properties
// 只进行接口级别注册
///////////////////////////////////////////////////
dubbo.application.register-mode=interface
```

我总结了一下逆向排查的查找流程。

![image-20250409230601332](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504092306570.png)

**导出**

通过 dubbo:service 标签进行服务的导出。

现在，你应该知道 @DubboService 注解中的配置怎么嫁接到了 ServiceBean 上了吧，第一步“配置”环节的源码我们就学好了，接下来看第二步“导出”，走进 doExport 核心导出逻辑的大门。

**注册**

第二步导出的源码我们探索完成，最后我们看看第三步注册，服务接口信息又是如何写到注册中心的？

![image-20250409231133576](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504092311741.png)

从 RegistryProtocol 的注册入口，经过几步深入，最终可以发现，向 Zookeeper 服务写数据其实也非常简单，我们调用了 CuratorFramework 框架的类来向 Zookeeper 写数据。

**总结**

今天，我们和Dubbo 总体架构示意图中的 ①②③ 步再续前缘，通过熟知的流程，引出了陌生的发布流程，从配置、导出、注册三方面深入研究了源码。

- 配置流程，通过扫描指定包路径下含有 @DubboService 注解的 Bean 定义，把扫描出来的 Bean 定义属性，全部转移至新创建的 ServiceBean 类型的 Bean 定义中，为后续导出做准备。
- 导出流程，主要有两块，一块是 injvm 协议的本地导出，一块是暴露协议的远程导出，远程导出与本地导出有着实质性的区别，远程导出会使用协议端口通过 Netty 绑定来提供端口服务。
- 注册流程，其实是远程导出的一个分支流程，会将提供方的服务接口信息，通过 Curator 客户端，写到 Zookeeper 注册中心服务端去。

![image-20250409231302323](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504092313471.png)

# 20｜订阅流程：消费方是怎么知道提供方地址信息的？

今天我们深入研究Dubbo源码的第九篇，订阅流程。

![image-20250410231154047](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504102311286.png)

```java
///////////////////////////////////////////////////
// org.apache.dubbo.registry.zookeeper.ZookeeperRegistry#doSubscribe
// 订阅的核心逻辑，读取 zk 目录下的数据，然后通知刷新内存中的数据
///////////////////////////////////////////////////
@Override
public void doSubscribe(final URL url, final NotifyListener listener) {
    try {
        checkDestroyed();
        // 因为这里用 * 号匹配，我们在真实的线上环境也不可能将服务接口配置为 * 号
        // 因此这里的 * 号逻辑暂且跳过，直接看后面的具体接口的逻辑
        if ("*".equals(url.getServiceInterface())) {
            // 省略其他部分代码...
        }
        // 能来到这里，说明 ServiceInterface 不是 * 号
        // url.getServiceInterface() = com.hmilyylimh.cloud.facade.demo.DemoFacade
        else {
            CountDownLatch latch = new CountDownLatch(1);
            try {
                List<URL> urls = new ArrayList<>();
                // toCategoriesPath(url) 得出来的集合有以下几种：
                // 1、/dubbo/com.hmilyylimh.cloud.facade.demo.DemoFacade/providers
                // 2、/dubbo/com.hmilyylimh.cloud.facade.demo.DemoFacade/configurators
                // 3、/dubbo/com.hmilyylimh.cloud.facade.demo.DemoFacade/routers
                for (String path : toCategoriesPath(url)) {
                    ConcurrentMap<NotifyListener, ChildListener> listeners = zkListeners.computeIfAbsent(url, k -> new ConcurrentHashMap<>());
                    ChildListener zkListener = listeners.computeIfAbsent(listener, k -> new RegistryChildListenerImpl(url, path, k, latch));
                    if (zkListener instanceof RegistryChildListenerImpl) {
                        ((RegistryChildListenerImpl) zkListener).setLatch(latch);
                    }
                    // 向 zk 创建持久化目录，一种容错方式，担心目录被谁意外的干掉了
                    zkClient.create(path, false);

                    // !!!!!!!!!!!!!!!!
                    // 这段逻辑很重要了，添加对 path 目录的监听，
                    // 添加监听完成后，还能拿到 path 路径下所有的信息
                    // 那就意味着监听一旦添加完成，那么就能立马获取到该 DemoFacade 接口到底有多少个提供方节点
                    List<String> children = zkClient.addChildListener(path, zkListener);
                    // 将返回的信息全部添加到 urls 集合中
                    if (children != null) {
                        urls.addAll(toUrlsWithEmpty(url, path, children));
                    }
                }

                // 从 zk 拿到了所有的信息后，然后调用 notify 方法
                // url.get(0) = dubbo://192.168.100.183:28200/com.hmilyylimh.cloud.facade.demo.DemoFacade?anyhost=true&application=dubbo-20-subscribe-consumer&background=false&check=false&deprecated=false&dubbo=2.0.2&dynamic=true&generic=false&interface=com.hmilyylimh.cloud.facade.demo.DemoFacade&methods=sayHello,say&register-mode=interface&release=3.0.7&side=provider
                // url.get(1) = empty://192.168.100.183/com.hmilyylimh.cloud.facade.demo.DemoFacade?application=dubbo-20-subscribe-consumer&background=false&category=configurators&dubbo=2.0.2&interface=com.hmilyylimh.cloud.facade.demo.DemoFacade&methods=sayHello,say&pid=11560&qos.enable=false&release=3.0.7&side=consumer&sticky=false&timestamp=1670846788876
                // url.get(2) = empty://192.168.100.183/com.hmilyylimh.cloud.facade.demo.DemoFacade?application=dubbo-20-subscribe-consumer&background=false&category=routers&dubbo=2.0.2&interface=com.hmilyylimh.cloud.facade.demo.DemoFacade&methods=sayHello,say&pid=11560&qos.enable=false&release=3.0.7&side=consumer&sticky=false&timestamp=1670846788876
                notify(url, listener, urls);
            } finally {
                // tells the listener to run only after the sync notification of main thread finishes.
                latch.countDown();
            }
        }
    } catch (Throwable e) {
        throw new RpcException("Failed to subscribe " + url + " to zookeeper " + getUrl() + ", cause: " + e.getMessage(), e);
    }
}
```

# 21｜调用流程：消费方的调用流程体系，你知道多少？

今天我们深入研究Dubbo源码的第十篇，调用流程。

在消费方你一定见过这样一段代码：

```java
@DubboReference
private DemoFacade demoFacade;
```

我们现在看到的这个 demoFacade 变量，在内存运行时，值类型还属于 DemoFacade 这个类型么？如果不是，那拿着 demoFacade 变量去调用里面的方法时，在消费方到底会经历怎样的调用流程呢？

**sayHello 调试**

先来看下我们的消费方调用代码。

```java
///////////////////////////////////////////////////
// 消费方的一个 Spring Bean 类
// 1、里面定义了下游 Dubbo 接口的成员变量，并且还用 @DubboReference 修饰了一下。
// 2、还定义了一个 invokeDemo 方法被外部调用，但其重点是该方法可以调用下游的 Dubbo 接口
///////////////////////////////////////////////////
@Component
public class InvokeDemoService {

    // 定义调用下游接口的成员变量，
    // 并且用注解修饰
    @DubboReference
    private DemoFacade demoFacade;

    // 该 invokeDemo 逻辑中调用的是下游 DemoFacade 接口的 sayHello 方法
    public String invokeDemo() {
        return demoFacade.sayHello("Geek");
    }
}
```

**1\. JDK代理**

我们在调用 sayHello 方法的这行打上一个断点，先运行提供方，再 Debug 运行消费方，很快断点就到来了。

![image-20250415230641100](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504152306377.png)

从图中，我们可以清楚地看到，demoFacade 的类型，是一个随机生成的代理类名，不再属于 DemoFacade 这个类型了，而且结合 $Proxy 类名、代理类中的 h 成员变量属于 JdkDynamicAopProxy 类型，综合判断，这是采用 JDK 代理动态，生成了一个继承 Proxy 的代理类。

我们再来看 interfacaces 变量。这里除了有我们调用下游的接口 DemoFacade，还有一个回声测试接口（EchoService）和一个销毁引用的接口（Destroyable）。

好，简单整理一下。demoFacade 在运行时并非我们所见的 DemoFacade 类型，而是由 JDK 动态代理生成的一个代理对象类型。

在生成的代理对象中，targetSource 成员变量创建的底层核心逻辑还是 ReferenceConfig 的 get 方法，不得不说 ReferenceConfig 是消费方引用下游接口逻辑中非常重要的一个类。

同时还认识了 EchoService 和 Destroyable 两个接口，让我们使用 demoFacade 时不仅可以调用 sayHello 方法，还可以强转为这两个接口调用不同的方法，使得一个 demoFacade 变量拥有三种能力，这就是代理增强的魅力所在。

**2\. InvokerInvocationHandler**

接下来，我们继续 Debug 进入 sayHello 方法中，发现了一个名字有点眼熟的 InvokerInvocationHandler 类，它实现了 JDK 代理中的 InvocationHandler 接口，所以，我们可以认为，这个 InvokerInvocationHandler 类是 Dubbo 框架接收 JDK 代理触发调用的入口。

来看看 InvokerInvocationHandler 的 invoke 方法，验证一下。

```java
///////////////////////////////////////////////////
// org.apache.dubbo.rpc.proxy.InvokerInvocationHandler#invoke
// JDK 代理被触发调用后紧接着就开始进入 Dubbo 框架的调用，
// 因此跟踪消费方调用的入口，一般直接搜索这个 InvokerInvocationHandler 即可，
// 再说一点，这个 InvokerInvocationHandler 继承了 InvocationHandler 接口。
///////////////////////////////////////////////////
@Override
public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
    // 省略不重要的代码 ...

    RpcInvocation rpcInvocation = new RpcInvocation(serviceModel, method, invoker.getInterface().getName(), protocolServiceKey, args);
    if (serviceModel instanceof ConsumerModel) {
        rpcInvocation.put(Constants.CONSUMER_MODEL, serviceModel);
        rpcInvocation.put(Constants.METHOD_MODEL, ((ConsumerModel) serviceModel).getMethodModel(method));
    }
    // 然后转手就把逻辑全部收口到一个 InvocationUtil 类中，
    // 从命名也看得出，就是一个调用的工具类
    return InvocationUtil.invoke(invoker, rpcInvocation);
}
```

发现最终并没有使用 proxy 代理对象，而是使用了 invoker + rpcInvocation 传入 InvocationUtil 工具类，完成了逻辑收口。

**3\. MigrationInvoker**

Debug 一直往后走，来到了一个 MigrationInvoker 的调用类，从类的名字上看是“迁移”的意思，有点 Dubbo2 与 Dubbo3 新老兼容迁移的味道。

那来看看 MigrationInvoker 的 invoke 方法代码逻辑。

```java
///////////////////////////////////////////////////
// org.apache.dubbo.registry.client.migration.MigrationInvoker#invoke
// 迁移兼容调用器
///////////////////////////////////////////////////
@Override
public Result invoke(Invocation invocation) throws RpcException {
    if (currentAvailableInvoker != null) {
        if (step == APPLICATION_FIRST) {
            // call ratio calculation based on random value
            if (promotion < 100 && ThreadLocalRandom.current().nextDouble(100) > promotion) {
                return invoker.invoke(invocation);
            }
        }
        return currentAvailableInvoker.invoke(invocation);
    }

    switch (step) {
        case APPLICATION_FIRST:
            if (checkInvokerAvailable(serviceDiscoveryInvoker)) {
                currentAvailableInvoker = serviceDiscoveryInvoker;
            } else if (checkInvokerAvailable(invoker)) {
                currentAvailableInvoker = invoker;
            } else {
                currentAvailableInvoker = serviceDiscoveryInvoker;
            }
            break;
        case FORCE_APPLICATION:
            currentAvailableInvoker = serviceDiscoveryInvoker;
            break;
        case FORCE_INTERFACE:
        default:
            currentAvailableInvoker = invoker;
    }

    return currentAvailableInvoker.invoke(invocation);
}
```

**4\. MockClusterInvoker**

然后走进”step == APPLICATION\_FIRST“的分支逻辑，进入 currentAvailableInvoker 的 invoke 方法，来到了 MockClusterInvoker 这个类，看名字是“模拟集群调用”的意思。

```java
///////////////////////////////////////////////////
// org.apache.dubbo.rpc.cluster.support.wrapper.MockClusterInvoker#invoke
// 调用异常时进行使用mock逻辑来处理数据的返回
///////////////////////////////////////////////////
@Override
public Result invoke(Invocation invocation) throws RpcException {
    Result result;
    // 从远程引用的url中看看有没有 mock 属性
    String value = getUrl().getMethodParameter(invocation.getMethodName(), "mock", Boolean.FALSE.toString()).trim();
    // mock 属性值为空的话，相当于没有 mock 逻辑，则直接继续后续逻辑调用
    if (ConfigUtils.isEmpty(value)) {
        //no mock
        result = this.invoker.invoke(invocation);
    }
    // 如果 mock 属性值是以 force 开头的话
    else if (value.startsWith("force")) {
        // 那么就直接执行 mock 调用逻辑，
        // 用事先准备好的模拟逻辑或者模拟数据返回
        //force:direct mock
        result = doMockInvoke(invocation, null);
    }
    // 还能来到这说明只是想在调用失败的时候尝试一下 mock 逻辑
    else {
        //fail-mock
        try {
            // 先正常执行业务逻辑调用
            result = this.invoker.invoke(invocation);
            //fix:#4585
            // 当业务逻辑执行有异常时，并且这个异常类属于RpcException或RpcException子类时，
            // 还有异常的原因如果是 Dubbo 框架层面的业务异常时，则不做任何处理。
            // 如果不是业务异常的话，则会继续尝试执行 mock 业务逻辑
            if(result.getException() != null && result.getException() instanceof RpcException){
                RpcException rpcException= (RpcException)result.getException();
                // 如果异常是 Dubbo 系统层面所认为的业务异常时，就不错任何处理
                if(rpcException.isBiz()){
                    throw rpcException;
                }else {
                    // 能来到这里说明是不是业务异常的话，那就执行模拟逻辑
                    result = doMockInvoke(invocation, rpcException);
                }
            }
        } catch (RpcException e) {
            // 业务异常直接往上拋
            if (e.isBiz()) {
                throw e;
            }
            // 不是 Dubbo 层面所和认为的异常信息时代，
            // 直接
            result = doMockInvoke(invocation, e);
        }
    }
    return result;
}
```

**5\. 过滤器链**

这里，看到 Cluster 这个关键字，想必你也想到了它是一个 SPI 接口，那在“发布流程”中我们也学过，远程导出和远程引用的时候，会用过滤器链把 invoker 层层包装起来。

那么我们就接着断点下去，发现确实进入 FutureFilter、MonitorFilter 等过滤器，这也证明了过滤器链包裹消费方 invoker 的存在。

**6\. FailoverClusterInvoker**

断点一层层走完了所有的过滤器，接着又来到了 FailoverClusterInvoker 这个类，从名字上一看就是在“ [温故知新](https://time.geekbang.org/column/article/611355)”中接触的故障转移策略，是不是有点好奇故障到底是怎么转移的？

我们不妨继续断点，进入它的 doInvoke 方法看看。

```java
///////////////////////////////////////////////////
// org.apache.dubbo.rpc.cluster.support.FailoverClusterInvoker#doInvoke
// 故障转移策略的核心逻辑实现类
///////////////////////////////////////////////////
@Override
@SuppressWarnings({"unchecked", "rawtypes"})
public Result doInvoke(Invocation invocation, final List<Invoker<T>> invokers, LoadBalance loadbalance) throws RpcException {
    List<Invoker<T>> copyInvokers = invokers;
    checkInvokers(copyInvokers, invocation);
    // 获取此次调用的方法名
    String methodName = RpcUtils.getMethodName(invocation);
    // 通过方法名计算获取重试次数
    int len = calculateInvokeTimes(methodName);
    // retry loop.
    // 循环计算得到的 len 次数
    RpcException le = null; // last exception.
    List<Invoker<T>> invoked = new ArrayList<Invoker<T>>(copyInvokers.size()); // invoked invokers.
    Set<String> providers = new HashSet<String>(len);
    for (int i = 0; i < len; i++) {
        //Reselect before retry to avoid a change of candidate `invokers`.
        //NOTE: if `invokers` changed, then `invoked` also lose accuracy.
        // 从第2次循环开始，会有一段特殊的逻辑处理
        if (i > 0) {
            // 检测 invoker 是否被销毁了
            checkWhetherDestroyed();
            // 重新拿到调用接口的所有提供者列表集合，
            // 粗俗理解，就是提供该接口服务的每个提供方节点就是一个 invoker 对象
            copyInvokers = list(invocation);
            // check again
            // 再次检查所有拿到的 invokes 的一些可用状态
            checkInvokers(copyInvokers, invocation);
        }
        // 选择其中一个，即采用了负载均衡策略从众多 invokers 集合中挑选出一个合适可用的
        Invoker<T> invoker = select(loadbalance, invocation, copyInvokers, invoked);
        invoked.add(invoker);
        // 设置 RpcContext 上下文
        RpcContext.getServiceContext().setInvokers((List) invoked);
        boolean success = false;
        try {
            // 得到最终的 invoker 后也就明确了需要调用哪个提供方节点了
            // 反正继续走后续调用流程就是了
            Result result = invokeWithContext(invoker, invocation);
            // 如果没有抛出异常的话，则认为正常拿到的返回数据
            // 那么设置调用成功标识，然后直接返回 result 结果
            success = true;
            return result;
        } catch (RpcException e) {
            // 如果是 Dubbo 框架层面认为的业务异常，那么就直接抛出异常
            if (e.isBiz()) { // biz exception.
                throw e;
            }
            // 其他异常的话，则不继续抛出异常，那么就意味着还可以有机会再次循环调用
            le = e;
        } catch (Throwable e) {
            le = new RpcException(e.getMessage(), e);
        } finally {
            // 如果没有正常返回拿到结果的话，那么把调用异常的提供方地址信息记录起来
            if (!success) {
                providers.add(invoker.getUrl().getAddress());
            }
        }
    }

    // 如果 len 次循环仍然还没有正常拿到调用结果的话，
    // 那么也不再继续尝试调用了，直接索性把一些需要开发人员关注的一些信息写到异常描述信息中，通过异常方式拋出去
    throw new RpcException(le.getCode(), "Failed to invoke the method "
            + methodName + " in the service " + getInterface().getName()
            + ". Tried " + len + " times of the providers " + providers
            + " (" + providers.size() + "/" + copyInvokers.size()
            + ") from the registry " + directory.getUrl().getAddress()
            + " on the consumer " + NetUtils.getLocalHost() + " using the dubbo version "
            + Version.getVersion() + ". Last error is: "
            + le.getMessage(), le.getCause() != null ? le.getCause() : le);
}
```

代码流程分析也比较简单。

- 从代码流程看，主要就是一个大的 for 循环，循环体中进行了 select 操作，拿到了一个合适的 invoker，发起后续逻辑调用。
- 从方法的入参和返回值看，入参是 invocation、invokers、loadbalance 三个参数，猜测应该就是利用 loadbalance 负载均衡器，从 invokers 集合中，选择一个 invoker 来发送 invocation 数据，发送完成后得到了返参的 Result 结果。
- 再看看方法实现体的一些细节，通过计算 retries 属性值得到重试次数并循环，每次循环都是利用负载均衡器选择一个进行调用，如果出现非业务异常，继续循环调用，直到所有次数循环完，还是没能拿到结果的话就会抛出 RpcException 异常了。

**7\. DubboInvoker**

了解完故障转移策略，我们继续 Debug，结果来到了 DubboInvoker 这个类。

**8\. ReferenceCountExchangeClient**

因为我们没有单独设置调用不需要响应，就继续断点进入 currentClient 的 request 方法，看看到底是怎么发送的，来到了 ReferenceCountExchangeClient 类。

```java
///////////////////////////////////////////////////
// org.apache.dubbo.rpc.protocol.dubbo.ReferenceCountExchangeClient#request(java.lang.Object, int, java.util.concurrent.ExecutorService)
// 这里将构建好的 request 对象发送出去，然后拿到了一个 CompletableFuture 异步化的对象
///////////////////////////////////////////////////
@Override
public CompletableFuture<Object> request(Object request, int timeout, ExecutorService executor) throws RemotingException {
    // client为：HeaderExchangeClient
    return client.request(request, timeout, executor);
}
```

**9\. NettyClient**

仍然没有看到数据是怎么发送的，我们继续深入 HeaderExchangeClient 的 request 方法中，Debug 几步后发现，进入了抽象类 AbstractPeer 的 send 方法。

```java
///////////////////////////////////////////////////
// org.apache.dubbo.remoting.transport.AbstractPeer#send
// this：NettyClient
// NettyClient 负责和提供方服务建立连接、发送数据等操作
///////////////////////////////////////////////////
@Override
public void send(Object message) throws RemotingException {
    send(message, url.getParameter(Constants.SENT_KEY, false));
}
```

那我们从 NettyClient 的 send 方法细看，结果发现了最终调用了 NioSocketChannel 的 writeAndFlush 方法，这个不就是 Netty 网络通信框架的 API 么？

到这里，我们在代码层面解释了数据原来是通过 Netty 框架的 NioSocketChannel 发送出去的。

**10\. NettyCodecAdapter**

一旦进入到 Netty 框架，再通过断点一步步跟踪数据就有点难了，因为 Netty 框架内部处处都是“线程+队列”的异步操作方式，这里我们走个捷径，进入 NettyClient 类，找找初始化 NettyClient 的相关 Netty 层面的配置。

你会找到一个 NettyCodecAdapter 类，对数据进行编解码，直接在类中的 encode 方法打个断点，等断点过来。

```java
///////////////////////////////////////////////////
// org.apache.dubbo.remoting.transport.netty4.NettyCodecAdapter.InternalEncoder#encode
// 将对象按照一定的序列化方式发送出去
///////////////////////////////////////////////////
private class InternalEncoder extends MessageToByteEncoder {

    @Override
    protected void encode(ChannelHandlerContext ctx, Object msg, ByteBuf out) throws Exception {
        ChannelBuffer buffer = new NettyBackedChannelBuffer(out);
        Channel ch = ctx.channel();
        NettyChannel channel = NettyChannel.getOrAddChannel(ch, url, handler);
        codec.encode(channel, buffer, msg);
    }
}
```

可以看到，编码的方法简单干脆。

- 从代码流程看，调用了一个 codec 编码器的变量，对入参编码处理。
- 从方法的入参和返回值看，msg 是请求数据对象，out 变量是 ByteBuf 缓冲区，应该是将 msg 编码之后的数据流。
- 再看看方法实现体的一些细节，没什么特别之处，无非就是走后续编解码器的编码方法，编码完成后，再通过 Netty 框架把数据流发送出去。

![image-20250415234820136](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504152348520.png)

**调用流程的其他案例**

第一，Tomcat 容器接收请求流程，通过在 HttpServlet 的 service 方法打个断点，从调用堆栈的最下面开始，可以分析出 Tomcat 的整体架构。

第二，SpringMvc 处理请求的流程，通过在 Controller 的任意方法打个断点，就可以逐步分析出一个 SpringMvc 处理请求的大致流程框架。

第三，Spring 的 getBean 方法，通过这个方法的层层深入，可以分析出一个庞大的 Spring 对象生成体系，也能挖掘出非常多 Spring 各种操控对象的扩展机制。

**总结**

总结一下跟踪源码的 12 字方针。

- “不钻细节：只看流程。”代码虽然多，但我们不必研究每个细节，要先捡方法中的重要分支流程，一些提前返回的边边角角的流程一概忽略不看。
- “不看过程：只看结论。”每个方法的代码逻辑可长可短，我们可以重点研究这个方法需要什么入参，又能给出什么返参，以此推测方法在干什么，到底要完成一件什么样的事情，搞清楚并得出结论。
- “再看细节：再看过程。”当你按照前两点认真调试后，大概的调用流程体系就清楚了。在此基础之上，再来细看被遗忘的边角料代码，有助于你进一步丰富调用流程图，体会源码细节中那些缜密的思维逻辑。

![image-20250415234942042](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504152349555.png)

# 22｜协议编解码：接口调用的数据是如何发到网络中的？

今天我们深入研究Dubbo源码的最后一篇，协议编解码。

> 用处不大。

