# ==拓展篇==

# 23｜集群扩展：发送请求遇到服务不可用，怎么办？

今天我们来实操第一个扩展，集群扩展。

你有没有遇到过这样的情况，对于多机房部署的系统应用，线上运行一直比较稳定，可是突然在某一段时间内，部分流量请求先出现一些超时异常，紧接着又出现一些无提供者的异常，最后部分功能就不可用了。

![image-20250416233302549](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504162333790.png)

对于这样一个看似非常简单的异常现象，我们该怎么解决呢？

**异常如何解决？**

要想知道怎么解决，首先就得弄清楚异常发生的原因。调用链路图中可以看到有两个异常，一个是超时异常，一个是无提供者异常。我们先从超时异常开始分析。

**1、超时异常和原因**

遇到异常，我们的第一反应就是去认真阅读异常堆栈的详细信息。

```
Caused by: org.apache.dubbo.remoting.TimeoutException: Waiting server-side response timeout by scan timer. start time: 2022-10-25 20:14:16.718, end time: 2022-10-25 20:14:16.747, client elapsed: 1 ms, server elapsed: 28 ms, timeout: 5 ms, request: Request [id=2, version=2.0.2, twoway=true, event=false, broken=false, data=RpcInvocation [methodName=sayHello, parameterTypes=[class java.lang.String], arguments=[Geek], attachments={path=com.hmilyylimh.cloud.facade.demo.DemoFacade, remote.application=dubbo-04-api-boot-consumer, interface=com.hmilyylimh.cloud.facade.demo.DemoFacade, version=0.0.0, timeout=5}]], channel: /192.168.100.183:62231 -> /192.168.100.183:28043
	at org.apache.dubbo.remoting.exchange.support.DefaultFuture.doReceived(DefaultFuture.java:212)
	at org.apache.dubbo.remoting.exchange.support.DefaultFuture.received(DefaultFuture.java:176)
	at org.apache.dubbo.remoting.exchange.support.DefaultFuture$TimeoutCheckTask.notifyTimeout(DefaultFuture.java:295)
	at org.apache.dubbo.remoting.exchange.support.DefaultFuture$TimeoutCheckTask.lambda$run$0(DefaultFuture.java:282)
	at org.apache.dubbo.common.threadpool.ThreadlessExecutor$RunnableWrapper.run(ThreadlessExecutor.java:184)
	at org.apache.dubbo.common.threadpool.ThreadlessExecutor.waitAndDrain(ThreadlessExecutor.java:103)
	at org.apache.dubbo.rpc.AsyncRpcResult.get(AsyncRpcResult.java:193)
	... 29 more
```

对于这个异常，可以从 3 个线索来进一步排查：

1. 可以从CAT监控平台上观察一下目标IP是否可以继续接收流量；
2. 也可以从Prometheus上观察消费方到目标IP的TCP连接状况
3. 还可以从网络层面通过tcpdump抓包检测消费方到目标IP的连通性等等。

好，为求证目标IP的健康状况，我们把刚刚提到的检监测工具挨个试一下：

- 在CAT上发现了目标IP在出问题期间几乎没有任何流量进来。
- 在Prometheus上发现在最近一段时间内TCP的连接耗时特别大，基本上都是有SYN请求握手包，但是没有SYN ACK响应包。
- 找网络人员帮忙实时tcpdump抓包测试，结果仍然发现没有SYN ACK响应包。

于是通过监测结论，我们基本确认了目标IP处于不可连通的状态，接着只需要去确认目标IP服务是宕机了还是流量被拦截了，就大概知道真相了。

**2、无提供者异常和原因**

无提供者异常，相信你看到这样的异常应该也不陌生，异常堆栈信息长这样。

```
org.apache.dubbo.rpc.RpcException: Failed to invoke the method sayHello in the service com.hmilyylimh.cloud.facade.demo.DemoFacade. No provider available for the service com.hmilyylimh.cloud.facade.demo.DemoFacade from registry 127.0.0.1:2181 on the consumer 192.168.100.183 using the dubbo version 3.0.7. Please check if the providers have been started and registered.
	at org.apache.dubbo.rpc.cluster.support.AbstractClusterInvoker.checkInvokers(AbstractClusterInvoker.java:366)
	at org.apache.dubbo.rpc.cluster.support.FailoverClusterInvoker.doInvoke(FailoverClusterInvoker.java:73)
	at org.apache.dubbo.rpc.cluster.support.AbstractClusterInvoker.invoke(AbstractClusterInvoker.java:340)
	at org.apache.dubbo.rpc.cluster.router.RouterSnapshotFilter.invoke(RouterSnapshotFilter.java:46)
	at org.apache.dubbo.rpc.cluster.filter.FilterChainBuilder$CopyOfFilterChainNode.invoke(FilterChainBuilder.java:321)
	at org.apache.dubbo.monitor.support.MonitorFilter.invoke(MonitorFilter.java:99)
	... 48 more
```

发现报错的关键点日志，是在 AbstractClusterInvoker 类中的第 366 行报错。可以得知， **消费方在内存中找不到对应的提供者，才会提示无提供者异常**。

**3、问题总结**

分析了超时异常、无提供者异常，我们最终发现是因为某些提供方的 IP 节点宕机，但是还有些提供方的节点 IP 是正常提供服务的，这又是为什么呢？

通过对 IP 的分析，梳理出了一张不同机房之间消费者调用提供者的链路图。

![image-20250416233945028](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504162339269.png)

我们可以看到机房A与机房B是不能相互访问的，这也正符合机房的隔离性。

那么假设机房A的某些提供者宕机了，且机房A的消费者状态正常，难道就预示着机房A的消费方发起的请求就无法正常调用了么？这样明显不合理，为什么机房A的提供者有问题，非得把机房A的消费者拉下水导致各种功能无法正常运转。

遇到这种状况，我们该如何改善呢？

**定制Cluster扩展**

消费者可以将请求发给 **中间商** 啊，然后中间商想办法找可用提供者，貌似这条路可行。

![image-20250416234230460](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504162342692.png)

我们来编写代码。

```java
public class TransferClusterInvoker<T> extends FailoverClusterInvoker<T> {
    // 按照父类 FailoverClusterInvoker 要求创建的构造方法
    public TransferClusterInvoker(Directory<T> directory) {
        super(directory);
    }
    // 重写父类 doInvoke 发起远程调用的接口
    @Override
    public Result doInvoke(Invocation invocation, List<Invoker<T>> invokers, LoadBalance loadbalance) throws RpcException {
        try {
            // 先完全按照父类的业务逻辑调用处理，无异常则直接将结果返回
            return super.doInvoke(invocation, invokers, loadbalance);
        } catch (RpcException e) {
            // 这里就进入了 RpcException 处理逻辑

            // 当调用发现无提供者异常描述信息时则向转发服务发起调用
            if (e.getMessage().toLowerCase().contains("no provider available")){
                // TODO 从 invocation 中拿到所有的参数，然后再处理调用转发服务的逻辑
                return doTransferInvoke(invocation);
            }
            // 如果不是无提供者异常，则不做任何处理，异常该怎么抛就怎么抛
            throw e;
        }
    }
}
```

最核心的逻辑我们已经实现了，那在代码中该怎么触发这个 TransferClusterInvoker 运作呢？

我们还是可以借鉴已有源码编写调用的思路，经过一番查找 FailoverClusterInvoker 代码编写调用关系后，我们可以定义一个 TransferCluster 类。

```java
public class TransferCluster implements Cluster {
    // 返回自定义的 Invoker 调用器
    @Override
    public <T> Invoker<T> join(Directory<T> directory, boolean buildFilterChain) throws RpcException {
        return new TransferClusterInvoker<T>(directory);
    }
}
```

当 TransferClusterInvoker、TransferCluster 都实现好后，按照 Dubbo SPI 的规范将 TransferCluster 类路径配置到 META-INF/dubbo/org.apache.dubbo.rpc.cluster.Cluster 文件中，看配置。

```plain
transfer＝com.hmilyylimh.cloud.TransferCluster
```

这段配置为 TransferCluster 取了个 transfer 名字，将来程序调用的时候能够被用上。

最后我们只需要在 dubbo.properties 指定全局使用，看配置。

```java
dubbo.consumer.cluster=transfer
```

全局指定名字叫 transfer 的集群扩展器，然后在调用时会触发 TransferCluster 来执行遇到无提供者异常时，掉头转向调用转发服务器。

# 24｜拦截扩展：如何利用Filter进行扩展？

今天我们继续学习Dubbo拓展的第二篇，拦截扩展。

**四个案例**

我们先看四个可以使用拦截的实际场景，分析一下“拦截”在其中的作用。

![image-20250421230656305](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504212306530.png)

- 案例一，已有的功能在之前和完成时，都记录一下日志的打印。
- 案例二，查询发票详情功能，需要在查询之前先看看有没有缓存数据。
- 案例三，用户在进行支付功能操作时，需要增加一些对入参字段的合法性校验操作。
- 案例四，获取分布式ID时，需要增加重试次数，如果重试次数达到上限后，仍无法获取结果，会在后置环节进行失败兜底逻辑处理，防止意外网络抖动影响正常的业务功能运转。

**解密需求**

需求案例是这样的，原先系统 A 调用了系统 B 的一个方法，方法的入参主要是接收一些用户信息，做一些业务逻辑处理，而且入参值都是明文的。

![image-20250421231940402](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504212319584.png)

后来，出现了安全层面出现了一些整改需求，需要你把用户信息中的一些敏感字段，比如名称 name、身份证号 idNo 用密文传输。到时候系统 B 在接收用户信息name 和 idNo 的值时，就是密文了，对于这样一个简单的需求优化，你该怎么解决呢？

首先要在过滤器中，通过方法级别来进行细粒度控制，我们可以参考“ [流量控制](https://time.geekbang.org/column/article/614130)”中关于计数逻辑的设计，通过服务名+方法名构成唯一，形成一种“约定大于配置”的理念。就像这样。

![image-20250421232111100](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504212321287.png)

有了配置中心的介入，我们可以动态针对某个方法的部分字段进行解密处理了，看代码。

```java
///////////////////////////////////////////////////
// 提供方：解密过滤器，仅在提供方有效，因为 @Activate 注解中设置的是 PROVIDER 侧
// 功能：通过 “类名 + 方法名” 从配置中心获取解密配置，有值就执行解密操作，没值就跳过
///////////////////////////////////////////////////
@Activate(group = PROVIDER)
public class DecryptProviderFilter implements Filter {

    /** <h2>配置中心 AES 密钥的配置名称，通过该名称就能从配置中心拿到对应的密钥值</h2> **/
    public static final String CONFIG_CENTER_KEY_AES_SECRET = "CONFIG_CENTER_KEY_AES_SECRET";

    @Override
    public Result invoke(Invoker<?> invoker, Invocation invocation) throws RpcException {
        // 从 OPS 配置中心里面获取到 aesSecretOpsKey 对应的密钥值
        String privateKey = OpsUtils.getAesSecret(CONFIG_CENTER_KEY_AES_SECRET);

        // 获取此次请求的类名、方法名，并且构建出一个唯一的 KEY
        String serviceName = invocation.getServiceModel().getServiceKey();
        String methodName = RpcUtils.getMethodName(invocation);
        String uniqueKey = String.join("_", serviceName, methodName);

        // 通过唯一 KEY 从配置中心查询出来的值为空，则说明该方法不需要解密
        // 那么就当作什么事也没发生，继续走后续调用逻辑
        String configVal = OpsUtils.get(uniqueKey);
        if (StringUtils.isBlank(configVal)) {
            return invoker.invoke(invocation);
        }

        // 能来到这里说明通过唯一 KEY 从配置中心找到了配置，那么就直接将找到的配置值反序列化为对象
        DecryptConfig decryptConfig = JSON.parseObject(configVal, DecryptConfig.class);
        // 循环解析配置中的所有字段列表，然后挨个解密并回填明文值
        for (String fieldPath : decryptConfig.getFieldPath()) {
            // 通过查找节点工具类，通过 fieldPath 字段路径从 invocation 中找出对应的字段值
            String encryptContent = PathNodeUtils.failSafeGetValue(invocation, fieldPath);
            // 找出来的字段值为空的话，则不做任何处理，继续处理下一个字段
            if (StringUtils.isBlank(encryptContent)) {
                continue;
            }

            // 解密成为明文后，则继续将明文替换掉之前的密文
            String plainContent = AesUtils.decrypt(encryptContent, privateKey);
            PathNodeUtils.failSafeSetValue(invocation, fieldPath, plainContent);
        }

        // 能来到这里，说明解密完成，invocation 中已经是明文数据了，然后继续走后续调用逻辑
        return invoker.invoke(invocation);
    }

    /**
     * <h1>解密配置。</h1>
     */
    @Setter
    @Getter
    public static class DecryptConfig {
        List<String> fieldPath;
    }
}

///////////////////////////////////////////////////
// 提供方资源目录文件
// 路径为：/META-INF/dubbo/org.apache.dubbo.rpc.Filter
///////////////////////////////////////////////////
decryptProviderFilter=com.hmilyylimh.cloud.filter.config.DecryptProviderFilter
```

这段代码也非常简单。

- 首先，从 invocation 中找出类名和方法名，构建出一个唯一 KEY 值。
- 然后，通过唯一 KEY 值去从配置中心查找，如果没找到，就继续走后续调用逻辑。
- 最后，如果找到了对应配置内容，反序列化后，挨个循环配置好的字段路径，依次解密后将明文再次放回到 invocation 对应位置中，继续走后续调用逻辑。

**拦截扩展的源码案例**

通过这个简单的案例，相信你已经掌握如何针对解密过滤器扩展了，在我们日常开发的过程中，有一些框架的源码，其实也有着类似的拦截扩展的机制，这里我也举 4 个常见的拦截机制的源码关键类。

第一，SpringMvc 的拦截过滤器，通过扩展 org.springframework.web.servlet.HandlerInterceptor 接口，就可以在控制器的方法执行之前、成功之后、异常时，进行扩展处理。

第二，Mybatis 的拦截器，通过扩展 org.apache.ibatis.plugin.Interceptor 接口，可以拦截执行的 SQL 方法，在方法之前、之后进行扩展处理。

第三，Spring 的 BeanDefinition 后置处理器，通过扩展 org.springframework.beans.factory.config.BeanFactoryPostProcessor 接口，可以针对扫描出来的 BeanDefinition 对象进行修改操作，改变对象的行为因素。

第四，Spring 的 Bean 后置处理器，还可以通过扩展 org.springframework.beans.factory.config.BeanPostProcessor 接口，在对象初始化前、初始化后做一些额外的处理，比如为 bean 对象创建代理对象的经典操作，就是在 org.springframework.aop.framework.autoproxy.AbstractAutoProxyCreator#postProcessAfterInitialization 方法完成的。

# 25｜注册扩展：如何统一添加注册信息？

今天我们继续学习Dubbo拓展的第三篇，注册扩展。

在需求并行迭代开发的节奏下，不同的 IP 节点，可能部署的是你这个后端应用的不同版本，我们怎么能保证每次前端发起的请求，都会命中需要测试的那个后端应用 IP 节点呢？

![image-20250424232050759](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504242321559.png)

**手动配置 IP**

回忆之前在“ [配置加载顺序](https://time.geekbang.org/column/article/615345)”中学过的四层配置覆盖关系，System Properties 优先级最高，Externalized Configuration 次之，API / XML / 注解的优先级再低一点，Local File 优先级最低。

![image-20250424232209756](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504242322978.png)

我们可以在 System Properties、Externalized Configuration 两个层级进行动态化的配置。

```
///////////////////////////////////////////////////
// System Properties 层级配置
// JVM 启动命令中添加如下 -D 的这一串属性
///////////////////////////////////////////////////
-Ddubbo.reference.com.hmily.dubbo.api.UserQueryFacade.url=dubbo://192.168.0.6:20884

///////////////////////////////////////////////////
// Externalized Configuration 层级配置
// 比如外部配置文件为：dubbo.properties
///////////////////////////////////////////////////
dubbo.reference.com.hmily.dubbo.api.UserQueryFacade.url=dubbo://192.168.0.6:20884
```

**自动识别 IP**

我们想在消费方调用提供方时，通过一些标识，来精准找到指定的 IP 进行远程调用，那回忆一下“ [调用流程](https://time.geekbang.org/column/article/621733)”中的各个步骤，看看能否找到惊喜。看我们当时画的调用流程的总结图。

![image-20250424232643380](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504242326727.png)

在 Cluster 层次模块中，有个故障转移策略的调用步骤，通过重试多次来达到容错目的，恰好这里能拿到多个提供者的 invoker 对象，每个 invoker 对象中就有提供方的 IP 地址。

所有，现在问题变成了， **怎么给 invoker 对象增加一个新字段？**

invoker 是框架层面实打实的硬编码类，想要修改可能有点难，我们得采取一种巧妙的方式，看看这个 invoker 有没有一些扩展属性的字段能用的。我们之前在“ [配置加载顺序](https://time.geekbang.org/column/article/615345)”中见过 invoker 内部的一些属性，看当时的截图。

![image-20250424232852986](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504242328305.png)

果然，我们找到了一个 urlParam 参数，可以在 urlParam 中添加一个新字段，这样一来，我们只需要循环 invoker 列表中的 urlParam 属性，寻找含有新字段的 invoker 对象就可以了。

怎么往 ZooKeeper 写数据，我们之前也学过，在“ [发布流程](https://time.geekbang.org/column/article/620988)”中讲 RegistryProtocol 的 export 方法中，有一段向 ZooKeeper 写数据的代码，这里我也复制过来了。

```java
///////////////////////////////////////////////////
// org.apache.dubbo.registry.integration.RegistryProtocol#export
// 远程导出核心逻辑，开启Netty端口服务 + 向注册中心写数据
///////////////////////////////////////////////////
@Override
public <T> Exporter<T> export(final Invoker<T> originInvoker) throws RpcException {
    // originInvoker.getUrl()：其实是注册中心地址
    // originInvoker.getUrl().toFullString()：registry://127.0.0.1:2181/org.apache.dubbo.registry.RegistryService?REGISTRY_CLUSTER=registryConfig&application=dubbo-19-dubbo-deploy-provider&dubbo=2.0.2&pid=13556&qos.enable=false&register-mode=interface&registry=zookeeper&release=3.0.7&timestamp=1670717595475
    // registryUrl：zookeeper://127.0.0.1:2181/org.apache.dubbo.registry.RegistryService?REGISTRY_CLUSTER=registryConfig&application=dubbo-19-dubbo-deploy-provider&dubbo=2.0.2&pid=13556&qos.enable=false&register-mode=interface&release=3.0.7&timestamp=1670717595475

    // 从 originInvoker 取出 "registry" 的属性值，结果取出了 zookeeper 值
    // 然后将 zookeeper 替换协议 "protocol" 属性的值就变成了 registryUrl
    URL registryUrl = getRegistryUrl(originInvoker);

    // providerUrl：dubbo://192.168.100.183:28190/com.hmilyylimh.cloud.facade.demo.DemoFacade?anyhost=true&application=dubbo-19-dubbo-deploy-provider&background=false&bind.ip=192.168.100.183&bind.port=28190&deprecated=false&dubbo=2.0.2&dynamic=true&generic=false&interface=com.hmilyylimh.cloud.facade.demo.DemoFacade&methods=sayHello,say&pid=13556&qos.enable=false&register-mode=interface&release=3.0.7&side=provider&timeout=8888&timestamp=1670717595488
    // 从 originInvoker.getUrl() 注册中心地址中取出 "export" 属性值
    URL providerUrl = getProviderUrl(originInvoker);
    // 省略部分其他代码...

    // 又看到了一个“本地导出”，此本地导出并不是之前看到的“本地导出”
    // 这里是注册中心协议实现类的本地导出，是需要本地开启20880端口的netty服务
    final ExporterChangeableWrapper<T> exporter = doLocalExport(originInvoker, providerUrl);

    // 根据 registryUrl 获取对应的注册器，这里获取的是对象从外层到内层依次是：
    // ListenerRegistryWrapper -> ZookeeperRegistry，最终拿到了 zookeeper 注册器
    final Registry registry = getRegistry(registryUrl);
    final URL registeredProviderUrl = getUrlToRegistry(providerUrl, registryUrl);
    boolean register = providerUrl.getParameter(REGISTER_KEY, true) && registryUrl.getParameter(REGISTER_KEY, true);
    if (register) {
        // 向 zookeeper 进行写数据，将 registeredProviderUrl 写到注册中心服务中去
        register(registry, registeredProviderUrl);
    }
    // 省略部分其他代码...
.
}
```

再细看这段代码，我们只需要认真研究 getRegistry 方法，拿到一个新的实现类就好了，利用这个新的实现类，把新字段写到 ZooKeeper 中。

**注册扩展**

接下来就来研究怎么扩展 Registry 接口，看看怎么从 getRegistry 方法中拿到另外一个新实现类。

话不多说，我们直接进入 getRegistry。

```java
///////////////////////////////////////////////////
// org.apache.dubbo.registry.integration.RegistryProtocol#getRegistry
// 通过注册中心地址来获取 Registry 实现类
///////////////////////////////////////////////////
/**
 * Get an instance of registry based on the address of invoker
 *
 * @param registryUrl
 * @return
 */
protected Registry getRegistry(final URL registryUrl) {
    // 获取 RegistryFactory 接口的自适应扩展点代理对象
    // 主要是调用了 getAdaptiveExtension 方法即可知道拿到了一个代理对象
    RegistryFactory registryFactory = ScopeModelUtil.getExtensionLoader(RegistryFactory.class, registryUrl.getScopeModel()).getAdaptiveExtension();

    // 通过代理对象获取入参指定扩展点的实现类
    // 默认逻辑是从 address 注册中心地址（zookeeper://127.0.0.1:2181）中根据 zookeeper 来找到对应的实现类
    // 到时候就只需要模仿 ZookeeperRegistry 就行
    return registryFactory.getRegistry(registryUrl);
}
```

方法非常简短，可以得到 2 个重要结论。

1. 拿到了 RegistryFactory 接口的自适应扩展点代理对象。
2. 把注册的地址 registryUrl 对象传入代理对象中，然后返回一个可以向注册中心进行写操作的实现类。提供方，如果是接口级注册模式，拿到的是 ZookeeperRegistry 核心实现类，如果是应用级注册模式，拿到的是 ServiceDiscoveryRegistry 核心实现类。

我们的需求是扩展 Registry 接口， **看看怎么从 getRegistry 方法中拿到另外一个新实现类**。

现在可以锁定一个重要的 RegistryFactory 接口，它的实现类也有两个 ServiceDiscoveryRegistryFactory、ZookeeperRegistryFactory，而且两个都重写了 createRegistry 方法。虽然，功能侧重点不同，但这两个类实现思路是一样的，任意模仿一个就行， 这里我就挑 ZookeeperRegistryFactory 来模仿。

仿照 ZookeeperRegistryFactory 和 ZookeeperRegistry 两个类来写，能继承使用的话就继承使用，不能继承的话可以考虑简单粗暴的 copy 一份。

```java
///////////////////////////////////////////////////
// 功能：RegistryFactory 在实现类：路由编码注册工厂，
// 主要得到一个 RouteNoZkRegistryFactory  对象可以向 zk 进行写操作
// 摘抄源码 ZookeeperRegistryFactory，然后稍加改造了一番，重写了 createRegistry 方法
///////////////////////////////////////////////////
public class RouteNoZkRegistryFactory extends AbstractRegistryFactory {
    private ZookeeperTransporter zookeeperTransporter;
    // 这个方法什么也没改
    public RouteNoZkRegistryFactory() {
        this(ApplicationModel.defaultModel());
    }
    // 这个方法什么也没改
    public RouteNoZkRegistryFactory(ApplicationModel applicationModel) {
        this.applicationModel = applicationModel;
        this.zookeeperTransporter = ZookeeperTransporter.getExtension(applicationModel);
    }
    // 该方法返回了自己创建的实现类
    @Override
    public Registry createRegistry(URL url) {
        return new RouteNoZkRegistry(url, zookeeperTransporter);
    }
}

///////////////////////////////////////////////////
// 功能：分发路由属性注册器，
// 尽量不做大的改动，继承了 ZookeeperRegistry，然后重写了注册与注销的方法
// 在重写的 doRegister、doUnregister 方法中添加了一个新字段，用于标识当前机器的一个身份标识
///////////////////////////////////////////////////
public class RouteNoZkRegistry extends ZookeeperRegistry {
    // 这个方法什么也没改
    public RouteNoZkRegistry(URL url, ZookeeperTransporter zookeeperTransporter) {
        super(url, zookeeperTransporter);
    }
    // 这个方法将 url 对象再次叠加一个 routeNo 新字段
    @Override
    public void doRegister(URL url) {
        super.doRegister(appendRouteNo(url));
    }
    // 这个方法将 url 对象再次叠加一个 routeNo 新字段
    @Override
    public void doUnregister(URL url) {
        super.doUnregister(appendRouteNo(url));
    }
    // 针对入参的 url 对象叠加一个 routeNo 新字段
    private URL appendRouteNo(URL url) {
        // routeNo 属性值，比如填上机器别名，最好具备唯一性
        url = url.addParameter("routeNo", "M20221219");
        return url;
    }
}

///////////////////////////////////////////////////
// 提供方资源目录文件
// 路径为：/META-INF/dubbo/org.apache.dubbo.registry.RegistryFactory
///////////////////////////////////////////////////
routenoregistry=com.hmilyylimh.cloud.registry.config.RouteNoZkRegistryFactory
```

改造后的代码关注 4 点。

- 复制了 ZookeeperRegistryFactory 的源码，并改了个名字为路由编码注册工厂（RouteNoZkRegistryFactory），其中，重写了 createRegistry 方法，返回了自己创建的路由编码注册器（RouteNoZkRegistry）。
- 在路由编码注册器（RouteNoZkRegistry）中，主要继承了已有的 ZookeeperRegistry 类，并重写了注册与注销的方法，在两个方法中都额外添加了一个新字段 routeNo 属性，属性值为当前 IP 机器易于识别的简单别名。
- 把路由编码注册工厂（RouteNoZkRegistryFactory）添加到资源目录对应的 SPI 接口文件中（/META-INF/dubbo/org.apache.dubbo.registry.RegistryFactory）。
- 在设置注册中心地址时，把已有的 zookeeper 替换为 routenoregistry。

```java
///////////////////////////////////////////////////
// Java 代码的配置类，替换 zookeeper 为 routenoregistry
///////////////////////////////////////////////////
@Bean
public RegistryConfig registryConfig() {
    // return new RegistryConfig("zookeeper://127.0.0.1:2181");
    return new RegistryConfig("routenoregistry://127.0.0.1:2181");
}

或者：

///////////////////////////////////////////////////
// dubbo.properties，直接指定 dubbo.registry.address 的值
///////////////////////////////////////////////////
dubbo.registry.address=routenoregistry://127.0.0.1:2181
```

写好之后，相信你迫不及待想验证一下了，我们写测试代码。

```java
///////////////////////////////////////////////////
// 自定义集群包装类，完全模拟 MockClusterWrapper 的源码抄袭改写了一下
///////////////////////////////////////////////////
public class CustomClusterWrapper implements Cluster {

    private final Cluster cluster;

    public CustomClusterWrapper(Cluster cluster) {
        this.cluster = cluster;
    }

    @Override
    public <T> Invoker<T> join(Directory<T> directory, boolean buildFilterChain) throws RpcException {
        return new CustomClusterInvoker<T>(directory,
                this.cluster.join(directory, buildFilterChain));
    }
}

///////////////////////////////////////////////////
// 自定义集群包类对应的 invoker 处理类
// 完全继承了 MockClusterInvoker 类，就是想打印点日志，
// 看看集群扩展器中的所有 invoker 对象，到底有没有拉取到提供方那边新增的 routeNo 标识
///////////////////////////////////////////////////
public class CustomClusterInvoker<T> extends MockClusterInvoker<T> {
    public CustomClusterInvoker(Directory<T> directory, Invoker<T> invoker) {
        super(directory, invoker);
    }
    @Override
    public Result invoke(Invocation invocation) throws RpcException {
        // 重点就看这里的日志打印就好了，也没什么特殊的操作
        List<Invoker<T>> invokers = getDirectory().list(invocation);
        for (Invoker<T> invoker : invokers) {
            System.out.print("invoker信息：");
            System.out.println(invoker.toString());
            System.out.println();
        }
        return super.invoke(invocation);
    }
}

///////////////////////////////////////////////////
// 消费方资源目录文件
// 路径为：/META-INF/dubbo/org.apache.dubbo.rpc.cluster.Cluster
///////////////////////////////////////////////////
com.hmilyylimh.cloud.registry.cluster.CustomClusterWrapper
```

测试代码也比较简单，就是想在消费方调用时，借用自定义的集群包装类，打印一下内存中的 invoker 信息，看看到底有没有拉取到提供方设置的 routeNo 标识。

接下来就是见证奇迹的时刻了，运行一下看打印结果。

> invoker信息：interface com.hmilyylimh.cloud.facade.demo.DemoFacade -> dubbo://192.168.100.183:28250/com.hmilyylimh.cloud.facade.demo.DemoFacade?anyhost=true&application=dubbo-25-registry-ext-provider&background=false&category=providers,configurators,routers&check=false&deprecated=false& **routeNo=M20221219**&dubbo=2.0.2&dynamic=true&generic=false&interface=com.hmilyylimh.cloud.facade.demo.DemoFacade&methods=sayHello,say&pid=8512&qos.enable=false&release=3.0.7&service-name-mapping=true&side=provider&sticky=false

从打印的日志中，看到了 routeNo 字段（加粗显示的部分），说明我们使用注册扩展的方式，通过新增一个 routeNo 字段，消费方可以根据这个标识来自动筛选具体 IP ，省去了手工动态配置 IP 的环节了，彻底解放了我们开发人员的双手。

写好注册扩展机制，已经完成了动态路由最重要的一环，不过，其他辅助的操作也不能落下，主要有 3 个关键点。

- 在申请多台机器的时候，可以自己手动为这一批机器设置一个别名，保证分发路由注册器中 appendrouteNo 能读取到整个别名就行。
- 在消费方自定义一个集群扩展器，把集群扩展器中的 invoker 列表按照 routeNo 进行分组后，再从接收请求的上下文对象中拿到 routeNo 属性值，从分组集合中选出过滤后的 invoker 列表，最后使用过滤后的 invoker 进行负载均衡调用。
- 前端若需要在哪个环境下测试，就在请求头中设置对应的 routeNo 属性以及属性值，这样就充分通过 routeNo 标识，体现了不同环境的隔离。

![图片](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504242332331.jpg)

**注册扩展的应用**

注册扩展如何使用，想必你已经非常清楚了，在我们日常开发的过程中，哪些场景会使用到注册扩展呢？我举 3 个常见的应用场景。

第一，添加路由标识，统一在消费方进行动态路由，以选择正确标识对应的 IP 地址进行远程调用。

第二，添加系统英文名，统一向注册信息中补齐接口归属的系统英文名，当排查一些某些接口的问题时，可以迅速从注册中心查看接口归属的系统英文名。

第三，添加环境信息，统一从请求的入口处，控制产线不同环境的流量比例，主要是控制少量流量对一些新功能进行内测验证。

# 26｜线程池扩展：如何选择Dubbo线程池？

今天我们继续学习Dubbo拓展的第四篇，线程池扩展。

Dubbo 框架里面其实有 4 种线程池，那其他的线程池存在的意义是什么，我们在使用时该怎么选择呢？

**线程池原理**

![image-20250427223300958](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504272233417.png)

假设主线程一直在不停地调用线程池的 execute 方法添加任务。

① 当处理任务的核心线程数量小于 corePoolSize，那就优先把任务分派给核心线程干活。

② 当处理任务的核心线程数量恰好等于 corePoolSize，继续添加任务则会进入 BlockingQueue 阻塞队列中等待。

③ 若任务也把阻塞队列堆满了，就继续尝试把任务分配给非核心线程去处理。

④ 若核心线程数量 \+ 非核心线程数量恰好为最大线程数量（maximumPoolSize），这个时候，如果再添加任务，线程池就吃不消了，所以会采取一定的拒绝策略来应对。

拒绝策略主要有 4 种。

- 策略一：拒绝添加新任务并抛出异常（AbortPolicy）， **同时也是默认的拒绝策略**。
- 策略二：让调用方线程执行新任务（CallerRunsPolicy）。
- 策略三：抛弃新任务（DiscardPolicy）。
- 策略四：丢弃最早入队的任务然后添加新任务（DiscardOldestPolicy）。

**Dubbo 线程池**

 Dubbo 线程池的创建方式，就是基于我们刚刚梳理的拥有 7 个参数的线程池构造方法，我们一个一个看，分别是：FixedThreadPool、LimitedThreadPool、CachedThreadPool、EagerThreadPool。

1. FixedThreadPool

第一个，固定线程数量的线程池，我们直接看这个线程池在源码层面是怎么体现的。

```java
///////////////////////////////////////////////////
// org.apache.dubbo.common.threadpool.support.fixed.FixedThreadPool
// 固定线程数量的线程池
///////////////////////////////////////////////////
public class FixedThreadPool implements ThreadPool {

    @Override
    public Executor getExecutor(URL url) {
        // 获取一些参数变量
        String name = url.getParameter("threadname", (String) url.getAttribute("threadname", "Dubbo"));
        int threads = url.getParameter("threads", 200);
        int queues = url.getParameter("queues", 0);

        // 调用创建线程池的构造方法
        return new ThreadPoolExecutor(
              // 核心线程数量：threads
              threads,
              // 最大线程数量：threads
              threads,
              // 非核心线程空闲时的存活时间等于0
              0,
              // 非核心线程空闲时的存活时间等于0，单位：毫秒
              TimeUnit.MILLISECONDS,
              // 存放任务的阻塞队列
              queues == 0 ? new SynchronousQueue<Runnable>() :
                  (queues < 0 ? new LinkedBlockingQueue<Runnable>()
                      : new LinkedBlockingQueue<Runnable>(queues)),
              // 创建线程的工厂
              new NamedInternalThreadFactory(name, true),
              // 带有导出线程堆栈的拒绝策略，内部继承了 AbortPolicy 抛异常策略
              new AbortPolicyWithReport(name, url)
        );
    }
}
```

从这段简短的创建线程池的代码中，我们能得出 3 点结论。

- 第一， **核心线程数量与最大线程数量是一致的**。这说明只有核心线程的存在，没有非核心线程的存在，而且在没有人为干预设置 threads 属性的情况下，默认核心线程数是 200，这也是 Dubbo 默认线程池数量是 200 个的由来。
- 第二，采用的阻塞队列，是根据队列长度 queues 属性值来确定。长度等于 0 使用同步队列（SynchronousQueue），长度小于 0 使用无界阻塞队列，长度大于 0 使用有界队列。
- 第三，拒绝策略使用的是默认的抛异常策略。不过，这个拒绝策略是经过框架特殊包装处理的，发现拒绝添加任务时，这个策略有导出线程堆栈的能力，特别适合开发人员分析线程池满时的一些实时状况。

从第一点结论我们不难发现，核心线程与最大线程数量等价，也说明了线程数量是固定不变的，所以这个线程池，我们就叫做 **固定线程数量的线程池（FixedThreadPool）**。

固定数量的默认值是 200，也就是说在某时刻最大能并行处理 200 个任务，假设每个任务耗时 1 秒，相当于这台机器的单机 QPS = 200，假设每个任务耗时 5 秒，那这台机器的单机 QPS = 40。

2. LimitedThreadPool

有的同学说：“我这系统又没多大的量，200 个线程有点浪费，量大的时候 QPS 也不过十几，量低的时候 QPS 几乎为零，而且也不好预估量低的时候设置多少合适。”

对于这样的疑惑，需要 Dubbo 的第二个线程池出马。

```java
///////////////////////////////////////////////////
// org.apache.dubbo.common.threadpool.support.limited.LimitedThreadPool
// 有限制数量的线程池
///////////////////////////////////////////////////
public class LimitedThreadPool implements ThreadPool {

    @Override
    public Executor getExecutor(URL url) {
        // 获取一些参数变量
        String name = url.getParameter("threadname", (String) url.getAttribute("threadname", "Dubbo"));
        int cores = url.getParameter("corethreads", 0);
        int threads = url.getParameter("threads", 200);
        int queues = url.getParameter("queues", 0);

        // 调用创建线程池的构造方法
        return new ThreadPoolExecutor(
              // 核心线程数量：cores
              cores,
              // 最大线程数量：threads
              threads,
              // 非核心线程空闲时的永久存活
              Long.MAX_VALUE,
              // 非核心线程空闲时的存活时间，单位：毫秒
              TimeUnit.MILLISECONDS,
              // 存放任务的阻塞队列
              queues == 0 ? new SynchronousQueue<Runnable>() :
                  (queues < 0 ? new LinkedBlockingQueue<Runnable>()
                      : new LinkedBlockingQueue<Runnable>(queues)),
              // 创建线程的工厂
              new NamedInternalThreadFactory(name, true),
              // 带有导出线程堆栈的拒绝策略，内部继承了 AbortPolicy 抛异常策略
              new AbortPolicyWithReport(name, url)
        );
    }
}

```

看过固定数量的线程池后，我们再看这个有限制数量的线程池源码，就非常得心应手，可以得出 2 点结论。

- 第一，核心线程数是由一个单独的 corethreads 属性来赋值的，默认值为 0。最大线程数是由 threads 属性来赋值的，默认值为 200。 **这说明默认情况下没有核心线程，非核心线程数量最大也不能超过 200。**
- 第二，非核心线程的 keepAliveTime 存活时间为 Long 类型的最大值，也就是说永不过期，一旦非核心线程创建出来了，只要不出现什么意外，就会一直存活，有任务就处理任务，没任务就躺在那里休息。

对于那些量小，不知道最初设置多少核心线程合适的，又不想浪费创建过多的线程的时候，我们可以考虑使用这款有限制数量的线程池（LimitedThreadPool）。

3. CachedThreadPool

不过LimitedThreadPool用着用着，你可能会觉得非核心线程一直闲着不回收，会占用内存，又琢磨着怎么让线程在有大量任务来时大量创建线程应对，当任务处理完后，非核心线程都闲置时默默地销毁掉。

这里 Dubbo 也有一款缓存线程池，我们来看它的源码实现。

```java
///////////////////////////////////////////////////
// org.apache.dubbo.common.threadpool.support.cached.CachedThreadPool
// 缓存一定数量的线程池
///////////////////////////////////////////////////
public class CachedThreadPool implements ThreadPool {

    @Override
    public Executor getExecutor(URL url) {
        // 获取一些参数变量
        String name = url.getParameter("threadname", (String) url.getAttribute("threadname", "Dubbo"));
        int cores = url.getParameter("corethreads", 0);
        int threads = url.getParameter("threads", Integer.MAX_VALUE);
        int queues = url.getParameter("queues", 0);
        int alive = url.getParameter("alive", 60 * 1000);

        // 调用创建线程池的构造方法
        return new ThreadPoolExecutor(
              // 核心线程数量：cores
              cores,
              // 最大线程数量：threads
              threads,
              // 非核心线程空闲时的存活时间
              alive,
              // 非核心线程空闲时的存活时间，单位：毫秒
              TimeUnit.MILLISECONDS,
              // 存放任务的阻塞队列
              queues == 0 ? new SynchronousQueue<Runnable>() :
                  (queues < 0 ? new LinkedBlockingQueue<Runnable>()
                      : new LinkedBlockingQueue<Runnable>(queues)),
              // 创建线程的工厂
              new NamedInternalThreadFactory(name, true),
              // 带有导出线程堆栈的拒绝策略，内部继承了 AbortPolicy 抛异常策略
              new AbortPolicyWithReport(name, url)
        );
    }
}

```

对比有数量限制的线程池（LimitedThreadPool），CachedThreadPool 最大的变化就在于创建线程池对象的时候，支持 alive 属性来赋值非核心线程的空闲时的存活时间，默认存活时间是 1 分钟，也就是说， **一旦非核心线程自带了销毁功能，也就变成了缓存线程池了**。

所以，当任务突增，你期望可以开辟非核心线程来执行，等到任务量降下去，你又不希望非核心线程占用空间，期望非核心线程自动销毁的话，可以考虑这个缓存线程池。

4. EagerThreadPool

不过系统总是千奇百怪，每个系统遇到的情况都不一样，你可能会对目前的线程池挑出一些毛病，比如在线程池工作原理图中，分支①发现核心线程都在处理任务的时候，对于新添加的任务你不希望进行等待队列，而是使用最大线程池里的线程。这该怎么办呢？

![image-20250427223954252](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504272240308.png)

我们看 Dubbo 的第四个线程池。

```java
///////////////////////////////////////////////////
// org.apache.dubbo.common.threadpool.support.eager.EagerThreadPool
// 渴望数量的线程池
///////////////////////////////////////////////////
public class EagerThreadPool implements ThreadPool {

    @Override
    public Executor getExecutor(URL url) {
        // 获取一些参数变量
        String name = url.getParameter("threadname", (String) url.getAttribute("threadname", "Dubbo"));
        int cores = url.getParameter("corethreads", 0);
        int threads = url.getParameter("threads", Integer.MAX_VALUE);
        int queues = url.getParameter("queues", 0);
        int alive = url.getParameter("alive", 60 * 1000);

        // 初始化队列和线程池
        TaskQueue<Runnable> taskQueue = new TaskQueue<Runnable>(queues <= 0 ? 1 : queues);
        EagerThreadPoolExecutor executor = new EagerThreadPoolExecutor(
                // 核心线程数量：cores
                cores,
                // 最大线程数量：threads
                threads,
                // 非核心线程空闲时的存活时间
                alive,
                // 非核心线程空闲时的存活时间，单位：毫秒
                TimeUnit.MILLISECONDS,
                // 存放任务的阻塞队列
                taskQueue,
                // 创建线程的工厂
                new NamedInternalThreadFactory(name, true),
                // 带有导出线程堆栈的拒绝策略，内部继承了 AbortPolicy 抛异常策略
                new AbortPolicyWithReport(name, url));
        // 将队列和线程池建立联系
        taskQueue.setExecutor(executor);
        return executor;
    }
}
                  ↓
///////////////////////////////////////////////////
// org.apache.dubbo.common.threadpool.support.eager.TaskQueue#offer
// 尝试添加任务至队列
///////////////////////////////////////////////////
@Override
public boolean offer(Runnable runnable) {
    // 参数必要性检查，若线程池对象为 null 则抛出异常
    if (executor == null) {
        throw new RejectedExecutionException("The task queue does not have executor!");
    }

    // 获取线程池中工作线程 worker 的数量
    int currentPoolThreadSize = executor.getPoolSize();
    // have free worker. put task into queue to let the worker deal with task.
    // 若线程池中活跃的数量小于 worker 的数量，
    // 说明有些 worker 是闲置状态，没有活干
    // 因此把任务添加到队列后，线程就有机会被分派到任务继续干活了
    if (executor.getActiveCount() < currentPoolThreadSize) {
        return super.offer(runnable);
    }

    // return false to let executor create new worker.
    // 还能来到这里，说明目前所有的 worker 都在处于工作状态
    // 那么继续看 worker 的数量和最大线程数量想比，若偏小的话
    // 那么就返回 false 表示需要继续创建 worker 来干活
    // 至于为什么返回 false 就能创建 worker 来继续干活，请看下面的 execute 方法
    if (currentPoolThreadSize < executor.getMaximumPoolSize()) {
        return false;
    }

    // currentPoolThreadSize >= max
    // 还能来到这里，说明已经达到了最大线程数量了，
    // 那该放队列就放队列，队列放不下的的话，又没有非核心线程了，那就走拒绝策略了
    return super.offer(runnable);
}
                  ↓
///////////////////////////////////////////////////
// java.util.concurrent.ThreadPoolExecutor#execute
// 线程池添加任务的方法
// 解释：currentPoolThreadSize < executor.getMaximumPoolSize() 这行代码
//      为什么返回 false 就能创建 worker 来继续干活
// 原理：在 workQueue.offer(command) 返回 false 后继续走下面的
//      else if (!addWorker(command, false)) 尝试添加 worker 工作线程，
//      添加成功了，那就执行任务，添加不成功了，说明已达到了最大线程数量，走拒绝策略
///////////////////////////////////////////////////
public void execute(Runnable command) {
    // 若任务 command 对象为 null 的话，是不合法的，直接抛出 NPE 异常
    if (command == null)
        throw new NullPointerException();
    int c = ctl.get();

    // 若工作线程的数量小于核心线程的数量的话
    if (workerCountOf(c) < corePoolSize) {
        // 则添加核心线程，addWorker(command, true) 中的 true 表示创建核心线程
        // 添加成功就结束该 execute 方法流程了
        if (addWorker(command, true))
            return;
        c = ctl.get();
    }

    // 若还能来到这里，说明工作线程数量已经达到了核心线程的数量了
    // 再来的任务就只能尝试添加至任务阻塞队列了
    // 调用队列的 offer 方法尝试看看能否添加至任务队列
    if (isRunning(c) && workQueue.offer(command)) {
        int recheck = ctl.get();
        // 若添加成功了，但是呢，线程池不处于运行状态，还得将任务移除，
        // 然后执行拒绝策略
        if (! isRunning(recheck) && remove(command))
            reject(command);
        else if (workerCountOf(recheck) == 0)
            addWorker(null, false);
    }

    // 还能来到这里，说明线程池处于运行状态，但是尝试添加至队列 offer 失败了
    // 那么就再次尝试调用 addWorker(command, false) 来创建非核心线程来执行任务
    // 尝试添加失败的话，再走拒绝策略
    else if (!addWorker(command, false))
        reject(command);
}
```

渴望数量的线程池（EagerThreadPool）源码，非常有亮点，可以说一定程度上打破了线程池固有的流程机制。

第一，核心线程数是由一个单独的 corethreads 属性来赋值的，默认值为 0。最大线程数是由 threads 属性来赋值的，默认值为 200，非核心线程的存活时间是由 alive 属性来赋值的，基本上都交给了用户自由设置指定。

第二，任务阻塞队列，既不是 SynchronousQueue，也不是 LinkedBlockingQueue，而是重新设计了一款新的阻塞队列 TaskQueue 放到了线程池中。

新的阻塞队列 TaskQueue，亮点在于 **重写了 LinkedBlockingQueue 的 offer 方法，只要活跃的工作线程数量小于最大线程数量，就优先创建工作线程来处理任务**。这个 offer 方法的优秀设计，主要源于对线程池 execute 方法的深度研究，利用任务入队失败的方式，来促使线程池尝试创建新的工作线程，来快速处理新增的任务。

当你原本设定了一些核心线程提供服务，但是突如其来的任务，需要优先紧急处理，而不想放到队列里面等待，就可以考虑用这款渴望线程数量的线程池（EagerThreadPool）。

**线程池监控**

Dubbo 线程池什么时候耗尽，可能是无法预测的，但是我们可以监控，提前预防，比如当活跃线程数量与最大线程满足多少百分比时，记录一个打点（至于在打点平台如何设置告警策略，或者如何做后续应对，就是后话了）。

```java
///////////////////////////////////////////////////
// 自定义监控固定数量的线程池
///////////////////////////////////////////////////
@Slf4j
public class MonitorFixedThreadPool extends FixedThreadPool implements Runnable {

    private static final Set<ThreadPoolExecutor> EXECUTOR_SET = new HashSet<>();

    /** <h2>高水位线阈值</h2> **/
    private static final double HIGH_WATER_MARK = 0.85;

    // 默认的构造方法，借用该构造方法创建一个带有轮询机制的单线程池
    public MonitorFixedThreadPool() {
        Executors.newSingleThreadScheduledExecutor()
                .scheduleWithFixedDelay(
                        // 当前的 MonitorFixedThreadPool 对象自己
                        this,
                        // 启动后 0 秒执行一次
                        0,
                        // 每间隔 30 秒轮询检测一次
                        30,
                        // 单位：秒
                        TimeUnit.SECONDS
                );
    }

    // 重写了父类的 FixedThreadPool 的 getExecutor 方法
    // 然后择机将返回值 executor 存储起来了
    @Override
    public Executor getExecutor(URL url) {
        // 通过 super 直接调用父类的方法，拿到结果
        Executor executor = super.getExecutor(url);

        // 针对结果进行缓存处理
        if (executor instanceof ThreadPoolExecutor) {
            EXECUTOR_SET.add((ThreadPoolExecutor) executor);
        }
        return executor;
    }

    @Override
    public void run() {
        // 每隔 30 秒，这个 run 方法被触发执行一次
        for (ThreadPoolExecutor executor : EXECUTOR_SET) {
            // 循环检测每隔线程池是否超越高水位线
            doCheck(executor);
        }
    }

    // 检测方法
    private void doCheck(ThreadPoolExecutor executor) {
        final int activeCount = executor.getActiveCount();
        int maximumPoolSize = executor.getMaximumPoolSize();
        double percent = activeCount / (maximumPoolSize * 1.0);

        // 判断计算出来的值，是否大于高水位线
        if (percent > HIGH_WATER_MARK) {
            log.info("溢出高水位线：activeCount={}, maximumPoolSize={}, percent={}",
                    activeCount, maximumPoolSize, percent);

            // 记录打点，将该信息同步值 Cat 监控平台
            CatUtils.logEvent("线程池溢出高水位线",
                    executor.getClass().getName(),
                    "1", buildCatLogDetails(executor));
        }
    }
}

///////////////////////////////////////////////////
// 资源目录文件
// 路径为：/META-INF/dubbo/org.apache.dubbo.common.threadpool.ThreadPool
///////////////////////////////////////////////////
monitorfixed=com.hmilyylimh.cloud.threadpool.config.MonitorFixedThreadPool

///////////////////////////////////////////////////
// 修改 Java 代码配置类指定使用该监控线程池
// 或
// dubbo.provider.threadpool=monitorfixed
///////////////////////////////////////////////////
@Bean
public ProtocolConfig protocolConfig(){
    ProtocolConfig protocolConfig = new ProtocolConfig("dubbo", 28260);
    protocolConfig.setThreadpool("monitorfixed");
    return protocolConfig;
}
```

思路清晰后，写代码并不是很难，关注 4 个重要的点。

- 在重写 getExecutor 的方法逻辑中，通过调用父类的 getExecutor 方法拿到线程池对象，并把线程池对象缓存起来。
- 巧妙利用构造方法，一次性生成带有轮询机制的单线程池对象。
- 在轮询检测中，计算出来的百分比，如果大于预设的高水位线，就记录打点通知 Cat 监控平台。
- 代码编写完后，记得 SPI 文件的配置，以及指定使用新的监控线程池。

# 27｜协议扩展：如何快速控制应用的上下线？

今天我们学习Dubbo拓展的最后一篇，协议扩展。

很多公司使用 Dubbo 的项目，可能都在使用 dubbo-admin 控制台进行应用的上下线发布。当面临要处理四五百个系统甚至上千个系统的上下线发布，你很可能会遇到控制台页面数据更新混乱的情况，极端情况下，还会导致应该上线的没有上线，就像莫名其妙少了几台机器提供服务一样。

这个问题关键在于发布期间大批系统集中进行上下线发布，这意味着 ZooKeeper 注册中心的目录节点，时刻在发生变化。而 dubbo-admin 是个管理功能的控制台系统，自然就会监听 ZooKeeper 上所有系统目录节点。

所以， **短时间内 dubbo-admin 的内存数据急剧变化**，就极可能造成页面刷新不及时。无法快速确保系统的哪些节点发布上线了，哪些节点没有发布上线。

面对这个情况，你的小组经过商讨后，最终决定要把应用的上下线稍微改造一下。

**去掉控制台**

我们从 dubbo-admin 控制台上的“下线”按钮一路跟踪到源码，结果发现最终调用了这样一段代码。

```java
public void disableProvider(Long id) {
	// 省略了其他代码
	Provider oldProvider = findProvider(id);
	if (oldProvider == null) {
		throw new IllegalStateException("Provider was changed!");
	}

	if (oldProvider.isDynamic()) {
		// 保证disable的override唯一
		if (oldProvider.isEnabled()) {
			Override override = new Override();
			override.setAddress(oldProvider.getAddress());
			override.setService(oldProvider.getService());
			override.setEnabled(true);
			override.setParams("disabled" + "=true");
			overrideService.saveOverride(override);
			return;
		}
		// 省略了其他代码
	} else {
		oldProvider.setEnabled(false);
		updateProvider(oldProvider);
	}
}
```

这段代码表明服务“下线”，就是把指定的服务接口设置了 enable=true、disabled=true 两个变量，同时协议变成 override 协议，然后把这串 URL 信息写到注册中心去，就完成了“下线”操作。

原来控制台的下线操作看起来这么简单，就是向注册中心写一条 URL 信息， **我们好像还真可以干掉控制台，下线的时候直接把这串信息写到注册中心去就行了。**

不过，我们手动操作注册中心下线了，等系统重新启动，同样又会把接口写到注册中心，消费方又可以调用了，那这个重新启动之前的下线操作岂不是没什么作用？

这时，联想之前学过的拦截操作，我们可以在系统重启的时候，直接以下线的命令写到注册中心，这样，消费方会认为没有可用的提供方，等提供方认为时机成熟，自己再想办法重新上线，应该就可以了。

思路感觉可行，我们梳理下，主要分为 3 步。

- 第一步，手动操作应用的下线操作，完全模拟控制台的 override 协议 + enable=true + disabled=true 三个主要因素，向注册中心进行写操作。
- 第二步，重新启动应用，应用的启动过程中会把服务注册到注册中心去，我们需要拦截这个注册环节的操作，用第一步的指令操作取而代之，让提供方以毫无存在感的方式默默启动成功。
- 第三步，找个合适的时机，想办法把应用上线，让消费方感知到提供方的存在，然后消费方就可以向提供方发起调用了。

**协议扩展**

我们总结一下，可以绘出大概流程图。

![image-20250428230622217](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202504282306371.png)

可以把流程归纳出 5 个重要的环节。

- 进行协议拦截，主要以禁用协议的方式进行接口注册。
- 在拦截协议的同时，把原始注册信息 URL 保存到磁盘文件中。
- 待服务重新部署成功后，利用自制的简单页面进行简单操作，发布上线指令操作。
- 发布上线的指令的背后操作，就是把对应应用机器上磁盘文件中的原始注册信息 URL 取出来。
- 最后利用操作注册中心的工具类，把取出来的原始注册信息 URL 全部写到注册中心。

有了这关键的五个环节，针对系统协议拦截环节的代码实现，应该就不是很难了。

```java
///////////////////////////////////////////////////
// 禁用协议包装器
///////////////////////////////////////////////////
public class OverrideProtocolWrapper implements Protocol {
    private final Protocol protocol;
    private Registry registry;
    // 存储原始注册信息的，模拟存储硬盘操作
    private static final List<URL> UN_REGISTRY_URL_LIST = new ArrayList<>();
    // 包装器的构造方法写法
    public OverrideProtocolWrapper(Protocol protocol) {
        this.protocol = protocol;
    }

    @Override
    public <T> Exporter<T> export(Invoker<T> invoker) throws RpcException {
        // 如果是注册协议的话，那么就先注册一个 override 到 zk 上，表示禁用接口被调用
        if (UrlUtils.isRegistry(invoker.getUrl())) {
            if (registry == null) {
                registry = getRegistry(invoker);
            }
            // 注册 override url，主要是在这一步让提供方无法被提供方调用
            doRegistryOverrideUrl(invoker);
        }
        // 接下来原来该怎么调用还是接着怎么进行下一步调用
        return this.protocol.export(invoker);
    }

    private <T> void doRegistryOverrideUrl(Invoker<T> invoker) {
        // 获取原始接口注册信息
        URL originalProviderUrl = getProviderUrl(invoker);
        // 顺便将接口注册的原始信息保存到内存中，模拟存储磁盘的过程
        UN_REGISTRY_URL_LIST.add(originalProviderUrl);

        // 构建禁用协议对象
        OverrideBean override = new OverrideBean();
        override.setAddress(originalProviderUrl.getAddress());
        override.setService(originalProviderUrl.getServiceKey());
        override.setEnabled(true);
        override.setParams("disabled=true");

        // 将禁用协议写到注册中心去
        registry.register(override.toUrl());
    }
    
    // 获取操作 Zookeeper 的注册器
    private Registry getRegistry(Invoker<?> originInvoker) {
        URL registryUrl = originInvoker.getUrl();
        if (REGISTRY_PROTOCOL.equals(registryUrl.getProtocol())) {
            String protocol = registryUrl.getParameter(REGISTRY_KEY, DEFAULT_REGISTRY);
            registryUrl = registryUrl.setProtocol(protocol).removeParameter(REGISTRY_KEY);
        }
        RegistryFactory registryFactory = ScopeModelUtil.getExtensionLoader
                (RegistryFactory.class, registryUrl.getScopeModel()).getAdaptiveExtension();
        return registryFactory.getRegistry(registryUrl);
    }
    
    // 获取原始注册信息URL对象
    private URL getProviderUrl(final Invoker<?> originInvoker) {
        return (URL) originInvoker.getUrl().getAttribute("export");
    }
    @Override
    public <T> Invoker<T> refer(Class<T> type, URL url) throws RpcException {
        return protocol.refer(type, url);
    }
    @Override
    public int getDefaultPort() {
        return protocol.getDefaultPort();
    }
    @Override
    public void destroy() {
        protocol.destroy();
    }
}

///////////////////////////////////////////////////
// 提供方资源目录文件
// 路径为：/META-INF/dubbo/org.apache.dubbo.rpc.Protocol
///////////////////////////////////////////////////
com.hmilyylimh.cloud.protocol.config.ext.OverrideProtocolWrapper

///////////////////////////////////////////////////
// 资源目录文件
// 路径为：/dubbo.properties
// 只进行接口级别注册
///////////////////////////////////////////////////
dubbo.application.register-mode=interface
```

代码实现起来也比较简单，关注 4 个关键点。

- 在包装器的 export 方法中，仅针对注册协议进行禁用协议处理。
- 禁用协议主要关注 override 协议 + enable=true + disabled=true 三个重要参数。
- 尝试把原始注册信息存储起来，这里使用内存来存储，间接模拟存储磁盘的过程。
- 最后通过适当的协议转换操作，拿到具体操作 ZooKeeper 的注册器，然后把禁用协议写到 ZooKeeper 中去。

接下来只需要按照相应的操作，把提供方上线就行，模拟上线的代码我也写在这里了。

```java
public void online() {
    // 模拟取出之前保存的原始注册信息列表
    for (URL url : UN_REGISTRY_URL_LIST) {
        OverrideBean override = new OverrideBean();
        override.setAddress(url.getAddress());
        override.setService(url.getServiceKey());
        override.setEnabled(true);
        override.setParams("disabled=false");
        // 先取消禁用
        registry.register(override.toUrl());

        // 然后将原始的注册信息写到注册中心去即可
        registry.register(url);
    }
}
```

**协议扩展的应用场景**

协议扩展除了可以处理上下线功能，还有哪些应用场景呢？

第一，收集接口发布列表，当我们需要统计系统的接口是否都已经发布时，可以通过协议扩展的方式来统计处理。

第二，禁用接口注册，根据一些黑白名单，在应用层面控制哪些接口需要注册，哪些接口不需要注册。

第三，多协议扩展，比如当市场上冒出一种新的协议，你也想在 Dubbo 框架这边支持，可以考虑像 DubboProtocol、HttpProtocol 这些类一样，扩展新的协议实现类。

