# 开篇词｜带你玩转Dubbo微服务框架

在这个专栏里，我会带着你以“发现问题——分析问题——解决问题”的案例驱动的思路，从一个问题现象出发，分析问题，一步步推导出需要怎样的技术支撑，再从我们已有的知识储备搜刮出可以有哪些解决方案，最后针对这些解决方案，快速有效地细化出落地方案，逐渐找到透过现象看本质的方法论。

具体会分为 4 个模块：

- 基础篇：用一张 Dubbo 的总体架构图，把日常的开发流程串联起来。如果你是初学者，掌握好基础篇就能应付日常开发实践了。
- 特色篇：以真实案例为背景，逐步分析并推导出需要的技术手段，带你灵活应用框架中的高级特性来解决实际问题。如果你是有 Dubbo 基础的开发者，掌握特色篇基本上可以在实战中横着走了。
- 源码篇：通过源码的学习，达到知其然知其所以然。如果你对自己有更高要求，掌握了源码篇，你可以称得上 Dubbo 框架高手了。
- 拓展篇：在这里我们将针对一些工作中的实际诉求，分析出解决方案，并且从前面已学的知识点中，提取关键要素尝试解决，在应用中进一步提升你对 Dubbo 的理解，晋级宗师。

![image-20250226224621979](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202502262246060.png)

课程的代码仓库链接： https://gitee.com/ylimhhmily/GeekDubbo3Tutorial

# ==基础篇==

# 01｜温故知新：Dubbo基础知识

**总体架构**

Dubbo 的主要节点角色有四个：

- Provider：提供方，暴露接口提供服务。
- Consumer：消费方，调用已暴露的接口。
- Registry：注册中心，管理注册的服务与接口。
- Monitor：监控中心，统计服务调用次数和调用时间。

我们画一张 Dubbo 的总体架构示意图，你可以清楚地看到每个角色大致的交互方式：

![image-20250301220000342](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503012200664.png)

对于一个 Dubbo 项目来说，我们首先会从提供方进行工程创建（第 ① 步），并启动工程（第 ② 步）来进行服务注册（第 ③ 步），接着会进行消费方的工程创建（第 ④ 步）并启动订阅服务（第 ⑤ 步）来发起调用（第 ⑥ 步），到这里，消费方就能顺利调用提供方了。

消费方在运行的过程中，会感知注册中心的服务节点变更（第 ⑦ 步），最后消费方和提供方将调用的结果指标同步至监控中心（第 ⑧⑨ 步）。

在这样的完整流程中，每个角色在 Dubbo 架构体系中具体起到了什么样的作用？每一步我们有哪些操作注意点呢？

**1、Provider 提供方**

第 ① 步，先自己新建一个提供方的工程，引用一个 facade.jar 包来对外暴露服务，编写的关键代码如下：

```java
///////////////////////////////////////////////////
// 提供方应用工程的启动类
///////////////////////////////////////////////////
// 导入启动提供方所需要的Dubbo XML配置文件
@ImportResource("classpath:dubbo-04-xml-boot-provider.xml")
// SpringBoot应用的一键式启动注解
@SpringBootApplication
public class Dubbo04XmlBootProviderApplication {
    public static void main(String[] args) {
        // 调用最为普通常见的应用启动API
        SpringApplication.run(Dubbo04XmlBootProviderApplication.class, args);
        // 启动成功后打印一条日志
        System.out.println("【【【【【【 Dubbo04XmlBootProviderApplication 】】】】】】已启动.");
    }
}
```

```xml
///////////////////////////////////////////////////
// 提供方应用工程的Dubbo XML配置文件内容：dubbo-04-xml-boot-provider.xml
///////////////////////////////////////////////////
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xmlns:dubbo="http://dubbo.apache.org/schema/dubbo"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
       http://www.springframework.org/schema/beans/spring-beans-4.3.xsd
       http://dubbo.apache.org/schema/dubbo
       http://dubbo.apache.org/schema/dubbo/dubbo.xsd">
    <!-- 注册中心的地址，通过 address 填写的地址提供方就可以联系上 zk 服务 -->
    <dubbo:registry address="zookeeper://127.0.0.1:2181"></dubbo:registry>
    <!-- 提供者的应用服务名称 -->
    <dubbo:application name="dubbo-04-xml-boot-provider"></dubbo:application>
    <!-- 提供者需要暴露服务的协议，提供者需要暴露服务的端口 -->
    <dubbo:protocol name="dubbo" port="28040"></dubbo:protocol>
    <!-- 提供者暴露服务的全路径为 interface 里面的内容 -->
    <dubbo:service interface="com.hmilyylimh.cloud.facade.demo.DemoFacade"
                   ref="demoFacade"></dubbo:service>
    <!-- 提供者暴露服务的业务实现逻辑的承载体 -->
    <bean id="demoFacade" class="com.hmilyylimh.cloud.xml.demo.DemoFacadeImpl"></bean>
</beans>
```

将提供方应用启动的代码、Dubbo 配置文件内容编写好后，就准备第 ② 步启动了。

> 注意在此之前要把 zookeeper 启动起来，否则会报错。
>
> 不做任何超时时间设置时，ConfigCenterConfig#checkDefault 方法中会默认超时时间为 30 秒，然后将“30 秒”传给 CuratorFramework 让它在有限的时间内连接上注册中心，若 30 秒还没有连接上的话，就抛出了这里你看到的非法状态异常，提示 zookeeper not connected，表示注册中心没有连接上。

运行启动类，就能看到启动成功的打印信息：

```
2022-11-11 23:57:27.261  INFO 12208 --- [           main] .h.c.x.Dubbo04XmlBootProviderApplication : Started Dubbo04XmlBootProviderApplication in 5.137 seconds (JVM running for 6.358)
2022-11-11 23:57:27.267  INFO 12208 --- [pool-1-thread-1] .b.c.e.AwaitingNonWebApplicationListener :  [Dubbo] Current Spring Boot Application is await...
【【【【【【 Dubbo04XmlBootProviderApplication 】】】】】】已启动.
```

接下来的第 ③ 步是在提供方启动的过程中进行的。启动成功后，你可以通过 ZooKeeper 中自带的 zkCli.cmd 或 zkCli.sh 连上注册中心，查看提供方在注册中心留下了哪些痕迹，如图：

![image-20250301214606654](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503012146695.png)

通过 ls / 查看根目录，我们发现 Dubbo 注册了两个目录，/dubbo 和 /services 目录：

![image-20250301221559337](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503012216560.png)

这是 Dubbo 3.x 推崇的一个应用级注册新特性，在不改变任何 Dubbo 配置的情况下，可以兼容一个应用从 2.x 版本平滑升级到 3.x 版本，这个新特性主要是为了将来能支持十万甚至百万的集群实例地址发现，并且可以与不同的微服务体系实现地址发现互联互通。

但这里有个小问题了，控制提供方应用到底应该接口级注册，还是应用级注册，还是两个都注册呢？

你可以通过在提供方设置 dubbo.application.register-mode 属性来自由控制，设置的值有 3 种：

- interface：只接口级注册。
- instance：只应用级注册。
- all：接口级注册、应用级注册都会存在，同时也是默认值。

**2、Consumer 消费方**

提供方启动完成后，我们就可以接着新建消费方的工程了。第 ④ 步，在新建的消费方工程中，同样需要引用 facade.jar 来进行后续的远程调用，你可以参考要编写的关键代码：

```java
///////////////////////////////////////////////////
// 消费方应用工程的启动类
///////////////////////////////////////////////////
// 导入启动消费方所需要的Dubbo XML配置文件
@ImportResource("classpath:dubbo-04-xml-boot-consumer.xml")
// SpringBoot应用的一键式启动注解
@SpringBootApplication
public class Dubbo04XmlBootConsumerApplication {
    public static void main(String[] args) {
        // 调用最为普通常见的应用启动API
        ConfigurableApplicationContext ctx =
                SpringApplication.run(Dubbo04XmlBootConsumerApplication.class, args);
        // 启动成功后打印一条日志
        System.out.println("【【【【【【 Dubbo04XmlBootConsumerApplication 】】】】】】已启动.");
        // 然后向提供方暴露的 DemoFacade 服务进行远程RPC调用
        DemoFacade demoFacade = ctx.getBean(DemoFacade.class);
        // 将远程调用返回的结果进行打印输出
        System.out.println(demoFacade.sayHello("Geek"));
    }
}
```

```xml
///////////////////////////////////////////////////
// 消费方应用工程的Dubbo XML配置文件内容：dubbo-04-xml-boot-consumer.xml
///////////////////////////////////////////////////
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xmlns:dubbo="http://dubbo.apache.org/schema/dubbo"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
       http://www.springframework.org/schema/beans/spring-beans-4.3.xsd        
       http://dubbo.apache.org/schema/dubbo        
       http://dubbo.apache.org/schema/dubbo/dubbo.xsd">
    <!-- 消费者的应用服务名称，最好是大家当前应用归属的系统名称 -->
    <dubbo:application name="dubbo-04-xml-boot-consumer"></dubbo:application>
    <!-- 注册中心的地址，通过 address 填写的地址提供方就可以联系上 zk 服务 -->
    <dubbo:registry address="zookeeper://127.0.0.1:2181"></dubbo:registry>
    <!-- 引用远程服务 -->
    <dubbo:reference id="demoFacade"
                     interface="com.hmilyylimh.cloud.facade.demo.DemoFacade">
    </dubbo:reference>
</beans>
```

把消费方应用启动的代码、Dubbo 配置文件内容编写好后，我们就准备启动了。

不过在启动之前，如果提供方还没有启动，也就是说提供方还没有发布 DemoFacade 服务，这个时候，我们启动消费方会看到这样的报错信息：

```
java.lang.IllegalStateException: Failed to check the status of the service com.hmilyylimh.cloud.facade.demo.DemoFacade. No provider available for the service com.hmilyylimh.cloud.facade.demo.DemoFacade from the url consumer://192.168.100.183/com.hmilyylimh.cloud.facade.demo.DemoFacade?application=dubbo-04-xml-boot-consumer&background=false&dubbo=2.0.2&interface=com.hmilyylimh.cloud.facade.demo.DemoFacade&methods=sayHello,say&pid=11876&qos.enable=false&register.ip=192.168.100.183&release=3.0.7&side=consumer&sticky=false&timestamp=1668219196431 to the consumer 192.168.100.183 use dubbo version 3.0.7
  at org.apache.dubbo.config.ReferenceConfig.checkInvokerAvailable(ReferenceConfig.java:545) ~[dubbo-3.0.7.jar:3.0.7]
  at org.apache.dubbo.config.ReferenceConfig.init(ReferenceConfig.java:293) ~[dubbo-3.0.7.jar:3.0.7]
  at org.apache.dubbo.config.ReferenceConfig.get(ReferenceConfig.java:219) ~[dubbo-3.0.7.jar:3.0.7]
```

上面报错告诉我们检查 DemoFacade 的状态失败了，并提示 No provider available 说明还暂时没有提供者，导致消费方无法启动成功。

怎么解决这个问题呢？我们可以考虑 3 种方案：

- 方案 1：将提供方应用正常启动起来即可。

- 方案 2：可以考虑在消费方的 Dubbo XML 配置文件中，为 DemoFacade 服务添加 check="false" 的属性，来达到启动不检查服务的目的，即：

  ```xml
  <!-- 引用远程服务 -->
  <dubbo:reference id="demoFacade" check="false"
          interface="com.hmilyylimh.cloud.facade.demo.DemoFacade">
  </dubbo:reference>
  ```

- 方案 3：也可以考虑在消费方的 Dubbo XML 配置文件中，为整个消费方添加 check="false" 的属性，来达到启动不检查服务的目的，即：

  ```xml
  <!-- 为整个消费方添加启动不检查提供方服务是否正常 -->
  <dubbo:consumer check="false"></dubbo:consumer>
  ```

我们把提供方应用启动起来，再启动消费方，接下来你就能看到消费方启动成功的日志打印信息，并且也成功调用了提供方的服务，日志信息就是这样：

```
2022-11-12 10:38:18.758  INFO 11132 --- [pool-1-thread-1] .b.c.e.AwaitingNonWebApplicationListener :  [Dubbo] Current Spring Boot Application is await...
【【【【【【 Dubbo04XmlBootConsumerApplication 】】】】】】已启动.
Hello Geek, I'm in 'dubbo-04-xml-boot-provider' project.
```

现在，消费方能成功启动了，接下来就要去注册中心订阅服务了，也就是第 ⑤ 步，这一步也是在消费方启动的过程中进行的。启动成功后，你可以通过 ZooKeeper 中自带的 zkCli.cmd 或 zkCli.sh 连上注册中心，查看消费方在注册中心留下了哪些痕迹：

![image-20250301215016640](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503012150679.png)

我们发现消费方也会向注册中心写数据，前面提到 Dubbo 3.x 推崇的一个应用级注册新特性，在消费方侧也存在如何抉择的问题，到底是订阅接口级注册信息，还是订阅应用级注册信息呢，还是说有兼容方案？

![image-20250301223432630](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503012234741.png)

其实 Dubbo 也为我们提供了过渡的兼容方案，你可以通过在消费方设置 dubbo.application.service-discovery.migration 属性来兼容新老订阅方案，设置的值同样有 3 种：

- FORCE_INTERFACE：只订阅消费接口级信息。
- APPLICATION_FIRST：注册中心有应用级注册信息则订阅应用级信息，否则订阅接口级信息，起到了智能决策来兼容过渡方案。
- FORCE_APPLICATION：只订阅应用级信息。

到现在提供方完成了启动和注册，消费方完成了启动和订阅，接下来消费方就可以向提供方发起调用了，也就是第 ⑥ 步。消费方向提供方发起远程调用的环节，调用的代码也非常简单：

```java
// 然后向提供方暴露的 DemoFacade 服务进行远程RPC调用
DemoFacade demoFacade = ctx.getBean(DemoFacade.class);
// 将远程调用返回的结果进行打印输出
System.out.println(demoFacade.sayHello("Geek"));
```

> ------------重试------------

区区两行代码，就跨越了网络从提供方那边拿到了结果，非常方便简单。不过总有调用不顺畅的时候，尤其是在提供方服务有点耗时的情况下，你可能会遇到这样的异常信息：

```
Exception in thread "main" org.apache.dubbo.rpc.RpcException: Failed to invoke the method sayHello in the service com.hmilyylimh.cloud.facade.demo.DemoFacade. Tried 3 times of the providers [192.168.100.183:28040] (1/1) from the registry 127.0.0.1:2181 on the consumer 192.168.100.183 using the dubbo version 3.0.7. Last error is: Invoke remote method timeout. method: sayHello, provider: DefaultServiceInstance{serviceName='dubbo-04-xml-boot-provider', host='192.168.100.183', port=28040, enabled=true, healthy=true, metadata={dubbo.endpoints=[{"port":28040,"protocol":"dubbo"}], dubbo.metadata-service.url-params={"connections":"1","version":"1.0.0","dubbo":"2.0.2","release":"3.0.7","side":"provider","port":"28040","protocol":"dubbo"}, dubbo.metadata.revision=7c65b86f6f680876cbb333cb7c92c6f6, dubbo.metadata.storage-type=local}}, service{name='com.hmilyylimh.cloud.facade.demo.DemoFacade',group='null',version='null',protocol='dubbo',params={side=provider, application=dubbo-04-xml-boot-provider, release=3.0.7, methods=sayHello,say, background=false, deprecated=false, dubbo=2.0.2, dynamic=true, interface=com.hmilyylimh.cloud.facade.demo.DemoFacade, service-name-mapping=true, generic=false, anyhost=true},}, cause: org.apache.dubbo.remoting.TimeoutException: Waiting server-side response timeout by scan timer. start time: 2022-11-12 13:50:44.215, end time: 2022-11-12 13:50:45.229, client elapsed: 1 ms, server elapsed: 1013 ms, timeout: 1000 ms, request: Request [id=3, version=2.0.2, twoway=true, event=false, broken=false, data=RpcInvocation [methodName=sayHello, parameterTypes=[class java.lang.String], arguments=[Geek], attachments={path=com.hmilyylimh.cloud.facade.demo.DemoFacade, remote.application=dubbo-04-xml-boot-consumer, interface=com.hmilyylimh.cloud.facade.demo.DemoFacade, version=0.0.0, timeout=1000}]], channel: /192.168.100.183:57977 -> /192.168.100.183:28040
```

首先是 RpcException 远程调用异常，发现 Tried 3 times 尝试了 3 次调用仍然拿不到结果。再看 TimeoutException 异常类，client elapsed: 1 ms, server elapsed: 1013 ms, timeout: 1000 ms，提示消费方在有限的 1000ms 时间内未拿到提供方的响应而超时了。

源码中默认的超时时间，可以从这段代码中查看，是 1000ms：

```java
private DefaultFuture(Channel channel, Request request, int timeout) {
    // 省略了其他逻辑代码
    // 源码中 int DEFAULT_TIMEOUT = 1000 是这样的默认值
    // 重点看这里，这里当任何超时时间未设置时，就采用源码中默认的 1000ms 为超时时效
    this.timeout = timeout > 0 ? timeout : channel.getUrl().getPositiveParameter(TIMEOUT_KEY, DEFAULT_TIMEOUT);
    // 省略了其他逻辑代码
}
```

对于这种情况，如果你预估可以稍微把超时时间设置长一点，可以在消费方的 Dubbo XML 配置文件中，为 DemoFacade 服务添加 timeout="5000" 的属性，来达到设置超时时间为 5000ms 的目的，即：

```xml
<!-- 引用远程服务 -->
<dubbo:reference id="demoFacade" timeout="5000"
                 interface="com.hmilyylimh.cloud.facade.demo.DemoFacade">
</dubbo:reference>
```

正常情况下 5000ms 足够了，但有些时候网络抖动延时增大，需要稍微重试几次，你可以继续设置 retries="3" 来多重试 3 次，即：

```xml
<!-- 引用远程服务 -->
<dubbo:reference id="demoFacade" timeout="5100" retries="3"
                 interface="com.hmilyylimh.cloud.facade.demo.DemoFacade">
</dubbo:reference>
```

> ------------容错------------

除了网络抖动影响调用，更多时候可能因为有些服务器故障了，比如消费方调着调着，提供方突然就挂了，消费方如果换台提供方，继续重试调用一下也许就正常了，所以你可以继续设置 cluster="failover" 来进行故障转移，比如：

```xml
<!-- 引用远程服务 -->
<dubbo:reference id="demoFacade" cluster="failover" timeout="5000" retries="3"
                 interface="com.hmilyylimh.cloud.facade.demo.DemoFacade">
</dubbo:reference>
```

当然故障转移只是一种手段，目的是当调用环节遇到一些不可预估的故障时，尽可能保证服务的正常运行，就好比这样的调用形式：

![image-20250301224234304](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503012242412.png)

Dubbo 框架为了尽可能保障运行，除了有 failover 故障转移策略，还有许多的容错策略，我们常用的比如：

![image-20250301215541250](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503012155294.png)

容错设置帮我们尽可能保障服务稳定调用。但调用也有流量高低之分，一旦流量比较高，你可能会发现提供方总是有那么几台服务器流量特别高，另外几个服务器流量特别低。

> ------------负载均衡------------

这是因为 Dubbo 默认使用的是 loadbalance="random" 随机类型的负载均衡策略，为了尽可能雨露均沾调用到提供方各个节点，你可以继续设置 loadbalance="roundrobin" 来进行轮询调用，比如：

```xml
<!-- 引用远程服务 -->
<dubbo:reference id="demoFacade" loadbalance="roundrobin"
        interface="com.hmilyylimh.cloud.facade.demo.DemoFacade">
</dubbo:reference>
```

**3、Registry 注册中心**

前面我们只是新增并注册了一个提供方，当我们逐渐增加节点的时候：

![image-20250301215657726](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503012156771.png)

提供方节点在增加，/dubbo 和 /services 目录的信息也会随之增多，那消费方怎么知道提供方有新节点增加了呢？

这就需要注册中心出场了。Dubbo 默认的注册中心 ZooKeeper 有另外一层通知机制，也就是第 ⑦ 步。比如 DemoFacade 有新的提供方节点启动了，那么 /dubbo/com.hmilyylimh.cloud.facade.demo.DemoFacade/providers 目录下会留下新节点的 URL 痕迹，也就相当于 /dubbo/com.hmilyylimh.cloud.facade.demo.DemoFacade 目录节点有变更。

ZooKeeper 会将目录节点变更的事件通知给到消费方，然后消费方去 ZooKeeper 中拉取 DemoFacade 最新的所有提供方的节点信息放到消费方的本地，这样消费方就能自动感知新的提供方节点的存在了。

**5、Monitor 监控中心**

当服务调用成功或者失败时，机器本身或者使用功能的用户是能感知到的，那我们怎么在第一时间察觉某些服务是否出了问题了呢？

![image-20250301215800743](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503012158819.png)

消费方服务可以将服务的调用成功数、失败数、服务调用的耗时时间上送给监控中心，也就是第 ⑧⑨ 步。这样一来，我们通过在监控中心设置不同的告警策略，就能在第一时间感知到一些异常问题的存在，争取在用户上报问题之前尽可能最快解决异常现象。

# ==特色篇==

# 02｜异步化实践：莫名其妙出现线程池耗尽怎么办？

相信你肯定写过这样的代码：

```java
@DubboService
@Component
public class AsyncOrderFacadeImpl implements AsyncOrderFacade {
    @Override
    public OrderInfo queryOrderById(String id) {
        // 这里模拟执行一段耗时的业务逻辑
        sleepInner(5000);
        OrderInfo resultInfo = new OrderInfo(
                "GeekDubbo",
                "服务方异步方式之RpcContext.startAsync#" + id,
                new BigDecimal(129));
        return resultInfo;
    }
}
```

这就是 Dubbo 服务提供方的一个普通的耗时功能服务，在 queryOrderById 中执行一段耗时的业务逻辑后，拿到 resultInfo 结果并返回。

但如果 queryOrderById 这个方法的调用量上来了，很容易导致 Dubbo 线程池耗尽。因为 Dubbo 线程池总数默认是固定的，200 个，假设系统在单位时间内可以处理 500 个请求，一旦 queryOrderById 的请求流量上来了，极端情况下，可能会出现 200 个线程都在处理这个耗时的任务，那么剩下的 300 个请求，即使是不耗时的功能，也很难有机会拿到线程资源。所以，紧接着就导致 Dubbo 线程池耗尽了。

为了让这种耗时的请求尽量不占用公共的线程池资源，我们就要开始琢磨异步了。

**如何异步处理服务**

我们再来尝试一下改用线程池的实现逻辑方式：

```java
@DubboService
@Component
public class AsyncOrderFacadeImpl implements AsyncOrderFacade {
    @Override
    public OrderInfo queryOrderById(String id) {
        // 创建线程池对象
        ExecutorService cachedThreadPool = Executors.newCachedThreadPool();
        cachedThreadPool.execute(new Runnable() {
            @Override
            public void run() {
                // 这里模拟执行一段耗时的业务逻辑
                sleepInner(5000);
                OrderInfo resultInfo = new OrderInfo(
                        "GeekDubbo",
                        "服务方异步方式之RpcContext.startAsync#" + id,
                        new BigDecimal(129));
                System.out.println(resultInfo);
            }
        });
        return ???;
    }
}
```

这段代码在 queryOrderById 中创建了一个线程池，然后将 Runnable 内部类放到线程池中去执行。但这么修改后，你发现会有2个问题：

- 问题 1：虽然放到了 cachedThreadPool 线程池中去执行了，但是这个 resultInfo 结果还是没有办法返回。
- 问题 2：cachedThreadPool.execute 方法一旦执行就好比开启了异步分支逻辑，那么最终的 “return ???” 这个地方该返回什么呢？

**如何实现拦截并返回结果**

因为 resultInfo 这个变量和当前处理业务的线程息息相关，我们要么借助本地线程 ThreadLocal 来存储，要么借助处理业务的上下文对象来存储。

如果借助本地线程 ThreadLocal 来存储，又会遇到 queryOrderById 所在的线程与 cachedThreadPool 中的线程相互通信的问题。因为 ThreadLocal 存储的内容位于线程私有区域，不同的线程，私有区域是无法相互访问的。

所以这里 **采用上下文对象来存储，那异步化的结果也就毋庸置疑存储在上下文对象中**。我们再来顺一遍流程，首先拦截识别异步，当拦截处发现有异步化模式的变量，从上下文对象中取出异步化结果并返回。

![image-20250303225030458](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503032250568.png)

> ----------线程间通信问题----------

这里我们要思考：如果异步化处理有点耗时，拦截处从异步化结果中取不到结果该怎么办呢？不停轮询等待吗？还是要作何处理呢？

这个问题抽象一下其实就是：A线程执行到某个环节，需要B线程的执行结果，但是B线程还未执行完，A线程是如何应对的？所以，本质回归到了多线程通信上。

相信熟悉 JDK 的你已经想到了，非 java.util.concurrent.Future 莫属，当异步执行结束之后，结果将会保存在 Future 当中。但 java.util.concurrent.Future 是一个接口，我们得找一个它的实现类来用，也就是 java.util.concurrent.CompletableFuture，而且它的 java.util.concurrent.CompletableFuture#get(long timeout, TimeUnit unit) 方法支持传入超时时间，也正好适合我们的场景。

接下来就一起来看看如何用 Dubbo 改造 queryOrderById 这个方法：

```java
@DubboService
@Component
public class AsyncOrderFacadeImpl implements AsyncOrderFacade {
    @Override
    public OrderInfo queryOrderById(String id) {
        // 创建线程池对象
        ExecutorService cachedThreadPool = Executors.newCachedThreadPool();
        
        // 开启异步化操作模式，标识异步化模式开始
        AsyncContext asyncContext = RpcContext.startAsync();
        
        // 利用线程池来处理 queryOrderById 的核心业务逻辑
        cachedThreadPool.execute(new Runnable() {
            @Override
            public void run() {
                // 将 queryOrderById 所在线程的上下文信息同步到该子线程中
                asyncContext.signalContextSwitch();
                
                // 这里模拟执行一段耗时的业务逻辑
                sleepInner(5000);
                OrderInfo resultInfo = new OrderInfo(
                        "GeekDubbo",
                        "服务方异步方式之RpcContext.startAsync#" + id,
                        new BigDecimal(129));
                System.out.println(resultInfo);
                
                // 利用 asyncContext 将 resultInfo 返回回去
                asyncContext.write(resultInfo);
            }
        });
        return null;
    }
}
```

核心实现就 3 点：

1. 定义线程池对象，通过 RpcContext.startAsync 方法开启异步模式；
2. 在异步线程中通过 asyncContext.signalContextSwitch 同步父线程的上下文信息；
3. 在异步线程中将异步结果通过 asyncContext.write 写入到异步线程的上下文信息中。

接下来就让我们来看看，Dubbo 这个优秀框架，在源码层面是怎么实现异步的，和我们的思路异同点在哪里。

**Dubbo 异步实现原理**

首先，还是定义线程池对象，在 Dubbo 中 RpcContext.startAsync 方法意味着异步模式的开启：

![image-20250303223619489](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503032236640.png)

们追踪源码的调用流程，可以发现最终创建了一个 java.util.concurrent.CompletableFuture 对象，这个对象就存储在当前的上下文 org.apache.dubbo.rpc.RpcContextAttachment 对象中。

然后，需要在异步线程中同步父线程的上下文信息：

![image-20250303223702215](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503032237302.png)

可以看到，Dubbo 框架用的是 AsyncContext 同步不同线程间的信息，也就是信息的拷贝，只不过这个拷贝需要利用到异步模式下的对象 AsyncContext。

> 思考：RpcContext, RpcContextAttachment, AsyncContext, AsyncContextImpl 几者的关系？

因为 AsyncContext 富含上下文信息，只需要把这个所谓的 AsyncContext 对象传入到子线程中，然后将 AsyncContext 中的上下文信息充分拷贝到子线程中，这样，子线程处理所需要的任何信息就不会因为开启了异步化处理而缺失。

最后的第三步就是在异步线程中，将异步结果写入到异步线程的上下文信息中：

```java
// org.apache.dubbo.rpc.AsyncContextImpl#write
public void write(Object value) {
    if (isAsyncStarted() && stop()) {
        if (value instanceof Throwable) {
            Throwable bizExe = (Throwable) value;
            future.completeExceptionally(bizExe);
        } else {
            future.complete(value);
        }
    } else {
        throw new IllegalStateException("The async response has probably been wrote back by another thread, or the asyncContext has been closed.");
    }
}
```

Dubbo 用 asyncContext.write 写入异步结果，这样拦截处只需要调用 java.util.concurrent.CompletableFuture#get(long timeout, TimeUnit unit) 方法就可以很轻松地拿到异步化结果了。

> 异步转同步，提升了 Dubbo 线程的利用率。

**异步应用场景**

Dubbo 的异步实现原理，相信你已经非常清楚了，那哪些应用场景可以考虑异步呢？

- 第一，我们定义了线程池，你可能会认为定义线程池的目的就是为了异步化操作，其实不是，异步化耗时的操作并没有在 queryOrderById 方法所在线程中继续占用资源，而是在新开辟的线程池中占用资源。所以对于一些 IO 耗时的操作，比较影响客户体验和使用性能的一些地方，我们是可以采用异步处理的。

- 其次，因为 queryOrderById 开启异步操作后就立马返回了，queryOrderById 所在的线程和异步线程没有太多瓜葛，异步线程的完成与否，不太影响 queryOrderById 的返回操作。

  所以，若某段业务逻辑开启异步执行后不太影响主线程的原有业务逻辑，也是可以考虑采取异步处理的。

- 最后，在 queryOrderById 这段简单的逻辑中，只开启了一个异步化的操作，站在时序的角度上看，queryOrderById 方法返回了，但是异步化的逻辑还在慢慢执行着，完全对时序的先后顺序没有严格要求。所以，时序上没有严格要求的业务逻辑，也是可以采用异步处理的。

**思考**

问：asyncContext.write(resultInfo); 这里将 resultInfo 写入 Future 之后，Dubbo 框架什么时候调用 Future.get 获取计算结果？

答：asyncContext.write(resultInfo); 执行之后是将结果写入到了 Future 当中，但是还有另外一个底层在调用这个 Future#get 的结果，这个调用的地方就是在【org.apache.dubbo.remoting.exchange.support.header.HeaderExchangeHandler#handleRequest】方法中的【handler.reply(channel, msg);】代码处。

【handler.reply(channel, msg);】返回的对象就是 Future 对象，然后调用 Future 对象的 whenComplete 方法，调用完后若没有结果就会等待，有结果的话就会立马进入 whenComplete 方法的回调逻辑中。

> 思考：既然主线程还是在等待，异步化调用能释放 Dubbo 线程池资源吗？
>
> DeepSeek：主线程不会阻塞。
>
> - 如果 `Future` 已经完成，回调可能在调用 `whenComplete` 的线程（主线程）中立即执行
> - 如果 `Future` 未完成，回调将在完成 `Future` 的线程（子线程）中执行
>
> ```
> future.get(); // 这会阻塞主线程
> future.whenComplete(...); // 这不会阻塞
> ```
>
> 当业务线程完成处理完成后，是由 Netty 的 EventLoop 线程发送响应的。
>
> ```java
> // Dubbo 底层处理逻辑（简化版）
> public void handleRequest(Channel channel, Request request) {
>     // 1. 从线程池获取线程（dubbo-protocol-200-thread-1）
>     ThreadPoolExecutor threadPool = getThreadPool(); 
>     threadPool.execute(() -> {
>         // 2. 调用服务方法
>         Object result = serviceMethod.invoke(params);
>         
>         // 3. 如果返回null且存在AsyncContext，立即归还线程
>         if (result == null && RpcContext.hasAsyncContext()) {
>             return; // 线程被释放回线程池
>         }
>         
>         // 同步模式：正常发送响应
>         channel.write(result);
>     });
> }
> ```
>
> 
>
> ```java
> // 业务代码调用asyncContext.write()时
> public void write(Object value) {
>     // 1. 获取挂起的Netty Channel
>     Channel channel = asyncContext.getChannel();
>     
>     // 2. 通过Netty的EventLoop线程发送响应（非业务线程池！）
>     // 线程名示例：nioEventLoopGroup-3-1
>     channel.eventLoop().execute(() -> {
>         channel.writeAndFlush(value);
>     });
> }
> ```
>
> 

# 03｜隐式传递：如何精准找出一次请求的全部日志？

今天我们继续探索 Dubbo 框架的第二道特色风味，隐式传递。

在我们日常开发工作中，查日志是很常见一环了。实际开发会涉及很多系统，如果出问题的功能调用流程非常复杂，你可能都不确定找到的日志是不是出问题时的日志，也可能只是找到了出问题时日志体系中的小部分，还可能找到一堆与问题毫无关系的日志。比如下面这个复杂调用关系：

![image-20250712231834957](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202507122318165.png)

通过请求中的关键字，我们在 A、B、C、D 系统中找到了相关日志：

```
2022-10-28 23:29:01.302 [系统A,DubboServerHandler-1095] INFO com.XxxJob - [JOB] calling start [emp_airOrderNoticeJob] 
2022-10-28 23:29:02.523 [系统B,DubboServerHandler-1093] INFO WARN XxxImpl - queryUser 入参参数为: xxxx 
2022-10-28 23:30:23.257 [系统C,DubboServerHandler-1096] INFO ABCImpl - recv Request... 
2022-10-28 23:30:25.679 [系统D,DubboServerHandler-1094] INFO XyzImpl - doQuery Start... 
2022-10-28 23:31:18.310 [系统B,DubboServerHandler-1093] INFO WARN XxxImpl - queryUser 入参参数不正确
```

看系统 B 的 DubboServerHandler-1093 线程打印的两行日志，第一眼从打印内容的上下文关系上看，我们会误认为这就是要找的错误信息。

但实际开发中一定要考虑不同请求、不同线程这两个因素，你能确定这两行日志一定是同一次请求、同一个线程打印出来的么？

**隐式传递**

我们回忆平时编写代码进行 Dubbo 远程调用时的流程链路：

![image-20250305220144970](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503052201143.png)

这是一个比较简单的消费者调用提供者的链路图，在消费者调用的过程中，一些附加的信息可以设置到 RpcContext 上下文中去，然后 RpcContext 中的信息就会随着远程调用去往提供者那边。

那如何把参数设置到 RpcContext 中呢？

我们需要有一个集中的环节可以进行操作，那么这个集中环节在哪里呢？再来看调用链路图：

![image-20250305220240439](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503052202574.png)

为了尽可能降低侵入性，我们最好能在系统的入口和出口，把接收数据的操作以及发送数据的操作进行完美衔接。这就意味着需要在接收请求的内部、发送请求的内部做好数据的交换。

来看代码实现：

```java
@Activate(group = PROVIDER, order = -9000)
public class ReqNoProviderFilter implements Filter {
    public static final String TRACE_ID = "TRACE-ID";
    @Override
    public Result invoke(Invoker<?> invoker, Invocation invocation) throws RpcException {
        // 获取入参的跟踪序列号值
        Map<String, Object> attachments = invocation.getObjectAttachments();
        String reqTraceId = attachments != null ? (String) attachments.get(TRACE_ID) : null;
        
        // 若 reqTraceId 为空则重新生成一个序列号值，序列号在一段相对长的时间内唯一足够了
        reqTraceId = reqTraceId == null ? generateTraceId() : reqTraceId;
        
        // 将序列号值设置到上下文对象中
        RpcContext.getServerAttachment().setObjectAttachment(TRACE_ID, reqTraceId);
        
        // 并且将序列号设置到日志打印器中，方便在日志中体现出来
        MDC.put(TRACE_ID, reqTraceId);
        
        // 继续后面过滤器的调用
        return invoker.invoke(invocation);
    }
}
```

```java
@Activate(group = CONSUMER, order = Integer.MIN_VALUE + 1000)
public class ReqNoConsumerFilter implements Filter, Filter.Listener {
    public static final String TRACE_ID = "TRACE-ID";
    @Override
    public Result invoke(Invoker<?> invoker, Invocation invocation) throws RpcException {
        // 从上下文对象中取出跟踪序列号值
        String existsTraceId = RpcContext.getServerAttachment().getAttachment(TRACE_ID);
        
        // 然后将序列号值设置到请求对象中
        invocation.getObjectAttachments().put(TRACE_ID, existsTraceId);
        RpcContext.getClientAttachment().setObjectAttachment(TRACE_ID, existsTraceId);
        
        // 继续后面过滤器的调用
        return invoker.invoke(invocation);
    }
}
```

思路也很清晰，主要新增了两个过滤器：

- ReqNoProviderFilter 为提供者维度的过滤器，主要接收请求参数中的 traceId，并将 traceId 的值放置到 RpcContext 上下文对象中。
- ReqNoConsumerFilter 为消费者维度的过滤器，主要从 RpcContext 上下文对象中取出 traceId 的值，并放置到 invocation 请求对象中。

然后遵循 Dubbo 的 SPI 特性将两个过滤器添加到 META-INF/dubbo/org.apache.dubbo.rpc.Filter 配置文件中：

```properties
reqNoConsumerFilter=com.hmilyylimh.cloud.ReqNoConsumerFilter
reqNoProviderFilter=com.hmilyylimh.cloud.ReqNoProviderFilter
```

最后修改一下日志器的打印日志模式：

```
%d{yyyy-MM-dd HH:mm:ss.SSS} [${APP_NAME}, %thread, %X{X-TraceId}] %-5level %c{1} -%msg%n
```

经过改造后，我们看到的日志就会是这样的：

```
2022-10-29 14:29:01.302 [系统A,DubboServerHandler-1095,5a2e67913efee084] INFO com.XxxJob - [JOB] calling start [emp_airOrderNoticeJob] 
2022-10-29 14:29:02.523 [系统B,DubboServerHandler-1093,9b42e2bf4bc2808e] INFO WARN XxxImpl - queryUser 入参参数为: xxxx 
2022-10-29 14:30:23.257 [系统C,DubboServerHandler-1096,6j40e2mn4bc4508e] INFO ABCImpl - recv Request... 
2022-10-29 14:30:25.679 [系统D,DubboServerHandler-1094,wx92bn9f4bc2m8z4] INFO XyzImpl - doQuery Start... 
2022-10-29 14:31:18.310 [系统B,DubboServerHandler-1093,9b42e2bf4bc2808e] INFO WARN XxxImpl - queryUser 入参参数不正确
```

看系统 B 的 DubboServerHandler-1093 线程打印的两行日志，1093 后面都是 9b42e2bf4bc2808e 这个序列号值，说明这一定是同一次请求、同一个线程打印出来的日志。

**隐式传递的应用**

今天学习的隐式传递，在我们的日常开发中，又有哪些应用场景呢？

第一，传递请求流水号，分布式应用中通过链路追踪号来全局检索日志。

第二，传递用户信息，以便不同系统在处理业务逻辑时可以获取用户层面的一些信息。

第三，传递凭证信息，以便不同系统可以有选择性地取出一些数据做业务逻辑，比如 Cookie、Token 等。

总体来说传递的都是一些技术属性数据，和业务属性没有太大关联，为了方便开发人员更为灵活地扩展系统能力，来更好地支撑业务的发展。

# 04｜泛化调用：三步教你搭建通用的泛化调用框架

我们继续探索 Dubbo 框架的第三道特色风味，泛化调用。

我们都知道，页面与后台的交互调用流程一般是，页面发起 HTTP 请求，首先到达 Web 服务器，然后由 Web 服务器向后端各系统发起调用：

![image-20250310232324578](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503102323759.png)

上述实现代码如下：

```java
@RestController
public class UserController {
    // 响应码为成功时的值
    public static final String SUCC = "000000";
    
    // 定义访问下游查询用户服务的字段
    @DubboReference
    private UserQueryFacade userQueryFacade;
    
    // 定义URL地址
    @PostMapping("/queryUserInfo")
    public String queryUserInfo(@RequestBody QueryUserInfoReq req){
        // 将入参的req转为下游方法的入参对象，并发起远程调用
        QueryUserInfoResp resp = 
                userQueryFacade.queryUserInfo(convertReq(req));
        
        // 判断响应对象的响应码，不是成功的话，则组装失败响应
        if(!SUCC.equals(resp.getRespCode())){
            return RespUtils.fail(resp);
        }
        
        // 如果响应码为成功的话，则组装成功响应
        return RespUtils.ok(resp);
    }
}
```

如果现在有十几个的运营页面，大约五十个请求接口，每个请求的核心逻辑都在后端系统，你预估一下，在 Web 服务器中写 Java 代码大概要写多久？

**反射调用**

我们可以使用类似这种 /projects/{project}/versions 占位符形式的 URL，利用 RequestMappingHandlerMapping 中的 URL 注册器去匹配。如果可以把一些变化的因子放到 URL 占位符中，精简 URL 的概率就非常大了。

我们先尝试修改一下：

```java
@RestController
public class CommonController {
    // 响应码为成功时的值
    public static final String SUCC = "000000";
    
    // 定义URL地址
    @PostMapping("/gateway/{className}/{mtdName}/request")
    public String commonRequest(@PathVariable String className,
                                @PathVariable String mtdName,
                                @RequestBody String reqBody){
        // 将入参的req转为下游方法的入参对象，并发起远程调用
        return commonInvoke(className, mtdName, reqBody);
    }

    /**
     * <h2>模拟公共的远程调用方法.</h2>
     *
     * @param className：下游的接口归属方法的全类名。
     * @param mtdName：下游接口的方法名。
     * @param reqParamsStr：需要请求到下游的数据。
     * @return 直接返回下游的整个对象。
     * @throws InvocationTargetException
     * @throws IllegalAccessException
     */
    public static String commonInvoke(String className, 
                                      String mtdName, 
                                      String reqParamsStr) throws InvocationTargetException, IllegalAccessException, ClassNotFoundException {
        // 试图从类加载器中通过类名获取类信息对象
        Class<?> clz = CommonController.class.getClassLoader().loadClass(className);
        // 然后试图通过类信息对象想办法获取到该类对应的实例对象
        Object reqObj = tryFindBean(clz.getClass());
        
        // 通过反射找到 reqObj(例：userQueryFacade) 中的 mtdName(例：queryUserInfo) 方法
        Method reqMethod = ReflectionUtils.findMethod(clz, mtdName);
        // 并设置查找出来的方法可被访问
        ReflectionUtils.makeAccessible(reqMethod);
        
        // 将 reqParamsStr 反序列化为下游对象格式，并反射调用 invoke 方法
        Object resp =  reqMethod.invoke(reqObj, JSON.parseObject(reqParamsStr, reqMethod.getParameterTypes()[0]));
        
        // 判断响应对象的响应码，不是成功的话，则组装失败响应
        if(!SUCC.equals(OgnlUtils.getValue(resp, "respCode"))){
            return RespUtils.fail(resp);
        }
        // 如果响应码为成功的话，则组装成功响应
        return RespUtils.ok(resp);
    }
}
```

这段代码有一个重要的核心逻辑还没解决，tryFindBean，我们该通过什么样的办法拿到下游接口的实例对象呢？或者说，该怎么仿照 @DubboReference 注解，拿到下游接口的实例对象呢？

> 当前服务集成了 Dubbo 服务，并且也已经定义了接口的 Consumer，可通过上述代码泛化调用。如果有新的接口转发，当前服务会有改动。
>
> 如果实现网关式透传？即新的接口也能直接转发。

虽然不知道 @DubboReference 注解是怎么做到的，但是我们起码能明白一点，只要通过 @DubboReference 修饰的字段就能拿到实例对象，那接下来就是需要一点耐心的环节了，顺着 @DubboReference 注解的核心实现逻辑探索一下源码：

![image-20250310230950063](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503102309227.png)

最终，我们会发现是通过 ReferenceConfig#get 方法创建了代理对象。

**透传式调用**

经过一番源码探索后，最难解决的 tryFindBean 逻辑也有了头绪。我们找到了 ReferenceConfig 这个核心类，接下来要做的就是拿到 referenceConfig#get 返回的泛化对象 GenericService，然后调用 GenericService#$invoke 方法进行远程调用。

按思路来调整代码：

```java
@RestController
public class CommonController {
    // 响应码为成功时的值
    public static final String SUCC = "000000";
    
    // 定义URL地址
    @PostMapping("/gateway/{className}/{mtdName}/{parameterTypeName}/request")
    public String commonRequest(@PathVariable String className,
                                @PathVariable String mtdName,
                                @PathVariable String parameterTypeName,
                                @RequestBody String reqBody) {
        // 将入参的req转为下游方法的入参对象，并发起远程调用
        return commonInvoke(className, parameterTypeName, mtdName, reqBody);
    }
    
    /**
     * <h2>模拟公共的远程调用方法.</h2>
     *
     * @param className：下游的接口归属方法的全类名。
     * @param mtdName：下游接口的方法名。
     * @param parameterTypeName：下游接口的方法入参的全类名。
     * @param reqParamsStr：需要请求到下游的数据。
     * @return 直接返回下游的整个对象。
     * @throws InvocationTargetException
     * @throws IllegalAccessException
     */
    public static String commonInvoke(String className,
                                      String mtdName,
                                      String parameterTypeName,
                                      String reqParamsStr) {
        // 然后试图通过类信息对象想办法获取到该类对应的实例对象
        ReferenceConfig<GenericService> referenceConfig = createReferenceConfig(className);
        
        // 远程调用
        GenericService genericService = referenceConfig.get();
        Object resp = genericService.$invoke(
                mtdName,
                new String[]{parameterTypeName},
                new Object[]{JSON.parseObject(reqParamsStr, Map.class)});
        
        // 判断响应对象的响应码，不是成功的话，则组装失败响应
        if(!SUCC.equals(OgnlUtils.getValue(resp, "respCode"))){
            return RespUtils.fail(resp);
        }
        
        // 如果响应码为成功的话，则组装成功响应
        return RespUtils.ok(resp);
    }
    
    private static ReferenceConfig<GenericService> createReferenceConfig(String className) {
        DubboBootstrap dubboBootstrap = DubboBootstrap.getInstance();
        
        // 设置应用服务名称
        ApplicationConfig applicationConfig = new ApplicationConfig();
        applicationConfig.setName(dubboBootstrap.getApplicationModel().getApplicationName());
        
        // 设置注册中心的地址
        String address = dubboBootstrap.getConfigManager().
            getRegistries().iterator().next().getAddress();
        RegistryConfig registryConfig = new RegistryConfig(address);
        ReferenceConfig<GenericService> referenceConfig = new ReferenceConfig<>();
        referenceConfig.setApplication(applicationConfig);
        referenceConfig.setRegistry(registryConfig);
        referenceConfig.setInterface(className);
        
        // 设置泛化调用形式
        referenceConfig.setGeneric("true");
        // 设置默认超时时间5秒
        referenceConfig.setTimeout(5 * 1000);
        return referenceConfig;
    }
}
```

到这里我们今天的学习任务就大功告成了，把枯燥无味的代码用泛化调用形式改善了一番，发起的请求，先经过“泛化调用”，然后调往各个提供方系统，这样发起的请求根本不需要感知提供方的存在，只需要按照既定的“泛化调用”形式发起调用就可以了。

![image-20250310232216887](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503102322101.png)

**泛化调用的应用**

学习了泛化调用，想必你已经可以很娴熟地封装自己的通用网关了，在我们日常开发中，哪些应用场景可以考虑泛化调用呢？

第一，透传式调用，发起方只是想调用提供者拿到结果，没有过多的业务逻辑诉求，即使有，也是拿到结果后再继续做分发处理。

第二，代理服务，所有的请求都会经过代理服务器，而代理服务器不会感知任何业务逻辑，只是一个通道，接收数据 -> 发起调用 -> 返回结果，调用流程非常简单纯粹。

第三，前端网关，有些内网环境的运营页面，对 URL 的格式没有那么严格的讲究，页面的功能都是和后端服务一对一的操作，非常简单直接。

# 05｜点点直连：点对点搭建产线“后⻔”的万能管控

我们继续探索 Dubbo 框架的第四道特⾊⻛味，点点直连。

今天我们来聊一聊产线问题如何快速修复的话题。情况是这样的，一天，运行良好的订单推送系统突然发生了一点异常情况，经过排查后，你发现有一条记录的状态不对，导致订单迟迟不能推送给外部供应商。

为了争取在最短时间内恢复这笔订单的功能运转，我们需要尽快修改这条推送记录在数据库的状态，修复产线数据。对于这样的紧急情况，你会怎么做？

![image-20250311225044426](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503112250636.png)

**1、正规流程**

参考公司平时遇到需要修复数据的情景，找到那行记录，编写一个 Update 语句，然后提交一个数据订正的流程。

**2、粗暴流程**

我们看流程图，从前端切入，重点标出了Web服务器的TOKEN概念：

![image-20250311225250346](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503112252504.png)

可以从Web服务器的后台日志中，弄出用户的TOKEN，然后找到可以更新这条推送记录的URL地址，最后模拟用户的请求，把这条推送记录更新掉就行了。

但如果后台没有暴露更新记录的URL地址呢？

**3、万能管控**

既然提前写好的代码能被调用，是不是可以考虑动态调用代码呢？那如何动态编译呢？我们回忆Java代码从编译到执行的流程：

![image-20250311231935911](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503112319088.png)

在这样的开发过程中，动态编译一般有两种方式：

- 自主编码实现，比如通过Runtime调用javac，或者通过JavaCompile调用run。
- 调用插件实现，比如使用市面上常用的groovy-all.jar插件。

那接下来该如何发起调用呢？我们整理思绪，设计了一下改造的大致思路：

![image-20250311230153722](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503112301867.png)

首先需要准备一个页面，填入5个字段信息，接口类名、接口方法名、接口方法参数类名、指定的URL节点、修复问题的Java代码，然后将这5个字段通过HTTP请求发往Web服务器，Web服务器接收到请求后组装泛化所需对象，最后通过泛化调用的形式完成功能修复。

最终Web服务器代码如下：

```java
@RestController
public class MonsterController {
    // 响应码为成功时的值
    public static final String SUCC = "000000";

    // 定义URL地址
    @PostMapping("/gateway/repair/request")
    public String repairRequest(@RequestBody RepairRequest repairRequest){
        // 将入参的req转为下游方法的入参对象，并发起远程调用
        return commonInvoke(repairRequest);
    }

    private String commonInvoke(RepairRequest repairRequest) {
        // 然后试图通过类信息对象想办法获取到该类对应的实例对象
        ReferenceConfig<GenericService> referenceConfig =
                createReferenceConfig(repairRequest.getClassName(), repairRequest.getUrl());

        // 远程调用
        GenericService genericService = referenceConfig.get();
        Object resp = genericService.$invoke(
                repairRequest.getMtdName(),
                new String[]{repairRequest.getParameterTypeName()},
                new Object[]{JSON.parseObject(repairRequest.getParamsMap(), Map.class)});

        // 判断响应对象的响应码，不是成功的话，则组装失败响应
        if(!SUCC.equals(OgnlUtils.getValue(resp, "respCode"))){
            return RespUtils.fail(resp);
        }

        // 如果响应码为成功的话，则组装成功响应
        return RespUtils.ok(resp);
    }

    private static ReferenceConfig<GenericService> createReferenceConfig(String className, String url) {
        DubboBootstrap dubboBootstrap = DubboBootstrap.getInstance();
        // 设置应用服务名称
        ApplicationConfig applicationConfig = new ApplicationConfig();
        applicationConfig.setName(dubboBootstrap.getApplicationModel().getApplicationName());
        // 设置注册中心的地址
        String address = dubboBootstrap.getConfigManager().getRegistries().iterator().next().getAddress();
        RegistryConfig registryConfig = new RegistryConfig(address);
        ReferenceConfig<GenericService> referenceConfig = new ReferenceConfig<>();
        referenceConfig.setApplication(applicationConfig);
        referenceConfig.setRegistry(registryConfig);
        referenceConfig.setInterface(className);
        // 设置泛化调用形式
        referenceConfig.setGeneric("true");
        // 设置默认超时时间5秒
        referenceConfig.setTimeout(5 * 1000);
        // 设置点对点连接的地址
        referenceConfig.setUrl(url);
        return referenceConfig;
    }
}

@Setter
@Getter
public class RepairRequest {
    /** <h2>接口类名，例：com.xyz.MonsterFacade</h2> **/
    private String className;
    /** <h2>接口方法名，例：heretical</h2> **/
    private String mtdName;
    /** <h2>接口方法参数类名，例：com.xyz.bean.HereticalReq</h2> **/
    private String parameterTypeName;
    /** <h2>指定的URL节点，例：dubbo://ip:port</h2> **/
    private String url;
    /** <h2>可以是调用具体接口的请求参数，也可以是修复问题的Java代码</h2> **/
    private String paramsMap;
}
```

MonsterFacade代码如下：

```java
public interface MonsterFacade {
    // 定义了一个专门处理万能修复逻辑的Dubbo接口
    AbstractResponse heretical(HereticalReq req);
}

public class MonsterFacadeImpl implements MonsterFacade {
    @Override
    AbstractResponse heretical(HereticalReq req){
        // 编译 Java 代码，然后变成 JVM 可识别的 Class 对象信息
        Class<?> javaClass = compile(req.getJavaCode());

        // 为 Class 对象信息，自定义一个名称，将来创建 Spring 单例对象要用到
        String beanName = "Custom" + javaClass.getSimpleName();

        // 通过 Spring 来创建单例对象
        generateSpringBean(beanName, javaClass);

        // 获取 beanName 对应的单例对象
        MonsterInvokeRunnable runnable = (MonsterAction)SpringContextUtils.getBean(beanName);

        // 执行单例对象的方法即可
        Object resp = runnable.run(req.getReqParamsMap());

        // 返回结果
        return new AbstractResponse(resp);
    }

    // 利用 groovy-all.jar 中的 groovyClassLoader 来编译 Java 代码
    private Class<?> compile(String javaCode){
        return groovyClassLoader.parseClass(javaCode);
    }

    // 生成Spring容器Bean对象
    private void generateSpringBean(String beanName, Class<?> javaClass){
        // 构建 Bean 定义对象
        BeanDefinitionBuilder beanDefinitionBuilder =
                BeanDefinitionBuilder.genericBeanDefinition(javaClass);
        AbstractBeanDefinition rawBeanDefinition = beanDefinitionBuilder.getRawBeanDefinition();

        // 将 bean 移交给 Spring 去管理
        ConfigurableApplicationContext appCtx =
                (ConfigurableApplicationContext)SpringContextUtils.getContext();
        appCtx.getAutowireCapableBeanFactory()
                .applyBeanPostProcessorsAfterInitialization(rawBeanDefinition, beanName);
        ((BeanDefinitionRegistry)appCtx.getBeanFactory()).registerBeanDefinition(beanName, rawBeanDefinition);
    }
}
```

这段代码使用Groovy和Spring，完成了万能管控代码的最核心逻辑：

- 首先，将接收的Java代码利用Groovy插件编译为Class对象。
- 其次，将得到的Class对象移交给Spring容器去创建单例Bean对象。
- 最后，调用单例Bean对象的run方法，完成最终动态Java代码的逻辑执行，并达到修复功能的目的。

**点点直连的应用**

好，点点直连的代码逻辑我们就掌握了，之后如果能应用到自己的项目中，相信你再也不用担心紧急的数据订正事件了。在日常开发中，哪些应用场景可以考虑点点直连呢？

第一，修复产线事件，通过直连+泛化+动态代码编译执行，可以轻松临时解决产线棘手的问题。

第二，绕过注册中心直接联调测试，有些公司由于测试环境的复杂性，有时候不得不采用简单的直连方式，来快速联调测试验证功能。

# 06｜事件通知：⼀招打败各种神乎其神的回调事件

今天我们探索 Dubbo 框架的第五道特⾊⻛味，事件通知。

我们看个项目例子，比如有个支付系统提供了一个商品支付功能：

![image-20250312224547937](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503122245150.png)

图中的支付系统暴露了一个支付请求的Dubbo接口，支付核心业务逻辑是调用核心支付系统完成，当支付状态翻转为支付成功后，还需要额外做些事情，比如埋点商品信息、短信告知用户和通知物流派件。

面对这样一个完成核心功能后还需要额外处理多个事件的需求，你会怎么优雅地快速处理呢？

**面向过程编程**

用面向对象编程的思路，把一些小功能用小方法封装一下，让那一大坨代码整体看起来整洁点。

![image-20250312224901516](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503122249693.png)

```java
@DubboService
@Component
public class PayFacadeImpl implements PayFacade {
    // 商品支付功能：一个大方法
    @Override
    public PayResp recvPay(PayReq req){
        // 支付核心业务逻辑处理
        method1();

        // 埋点已支付的商品信息
        method2();

        // 发送支付成功短信给用户
        method3();

        // 通知物流派件
        method4();

        // 返回支付结果
        return buildSuccResp();
    }
}
```

上述代码实现方式可能会为我们之后的繁重工作量埋下种子，⽐如⼀周后需求⼜来了，要发送邮件、通知结算，怎么办呢？是不是还得继续添加⼩⽅法 5 和⼩⽅法 6？

为了提升代码水平，我们继续思考商品支付的功能设计。

**如何解耦**

“分开”其实就是要做解耦，这里我教你一个解耦小技巧，从3方面分析：

1. **功能相关性**。将一些功能非常相近的汇聚成一块，既是对资源的聚焦整合，也降低了他人的学习成本，尊重了人类物以类聚的认知习惯。
2. **密切相关性**。按照与主流程的密切相关性，将一个个小功能分为密切与非密切。
3. **状态变更性**。按照是否有明显业务状态的先后变更，将一个个小功能再归类。

按照小技巧我们再梳理一下这4个功能：

![image-20250312225103943](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503122251128.png)

先看功能相关性，四个小功能的拆分没问题；再看密切相关性，支付核心业务逻辑是最重要的，其他三个事件的重要程度和迫切性并不高；最后看状态变更性，核心业务逻辑有了明显的状态变更后，在支付成功的关键节点后，驱动着继续做另外三件事。

解耦完成，如何形成主次分明的结构呢？

考虑到商品支付这个功能也只是Dubbo众多接口中的一个，我们不妨升维思考，站在Dubbo接口的框架调用流程中，看看是否可以在商品支付功能method1远程调用的前后做点事情来提供事件通知的入口。回忆Dubbo调用远程的整个流程：

![image-20250312225246277](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503122252449.png)

把AOP的思想充分应用到拦截模块中，在执行下一步调用之前、之后、异常时包裹了一层。

![image-20250312225551353](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503122255541.png)

那过滤器的代码该怎么写呢？其实Dubbo底层的源码已经按照我们的预想实现了一番：

```java
@Activate(group = CommonConstants.CONSUMER)
public class FutureFilter implements ClusterFilter, ClusterFilter.Listener {
    protected static final Logger logger = LoggerFactory.getLogger(FutureFilter.class);
    @Override
    public Result invoke(final Invoker<?> invoker, final Invocation invocation) throws RpcException {
        // 调用服务之前：执行Dubbo接口配置中指定服务中的onInvoke方法
        fireInvokeCallback(invoker, invocation);
        // need to configure if there's return value before the invocation in order to help invoker to judge if it's
        // necessary to return future.
        // 调用服务并返回调用结果
        return invoker.invoke(invocation);
    }

    // 调用服务之后：
    // 正常返回执行Dubbo接口配置中指定服务中的onReturn方法
    // 异常返回执行Dubbo接口配置中指定服务中的onThrow方法
    @Override
    public void onResponse(Result result, Invoker<?> invoker, Invocation invocation) {
        if (result.hasException()) {
            // 调用出现了异常之后的应对处理
            fireThrowCallback(invoker, invocation, result.getException());
        } else {
            // 正常调用返回结果的应对处理
            fireReturnCallback(invoker, invocation, result.getValue());
        }
    }

    // 调用框架异常后：
    // 异常返回执行Dubbo接口配置中指定服务中的onThrow方法
    @Override
    public void onError(Throwable t, Invoker<?> invoker, Invocation invocation) {
        fireThrowCallback(invoker, invocation, t);
    }
}
```

**如何改造**

接下来就是轻松环节了，核心逻辑和三个事件逻辑该怎么写呢？我们可以直接根据源码所提供的支撑能力，重新修改 recvPay 方法：

```java
@DubboService
@Component
public class PayFacadeImpl implements PayFacade {
    @Autowired
    @DubboReference(
            /** 为 DemoRemoteFacade 的 sayHello 方法设置事件通知机制 **/
            methods = {@Method(
                    name = "sayHello",
                    oninvoke = "eventNotifyService.onInvoke",
                    onreturn = "eventNotifyService.onReturn",
                    onthrow = "eventNotifyService.onThrow")}
    )
    private DemoRemoteFacade demoRemoteFacade;

    // 商品支付功能：一个大方法
    @Override
    public PayResp recvPay(PayReq req){
        // 支付核心业务逻辑处理
        method1();
        // 返回支付结果
        return buildSuccResp();
    }
    private void method1() {
        // 省略其他一些支付核心业务逻辑处理代码
        demoRemoteFacade.sayHello(buildSayHelloReq());
    }
}
```

```java
// 专门为 demoRemoteFacade.sayHello 该Dubbo接口准备的事件通知处理类
@Component("eventNotifyService")
public class EventNotifyServiceImpl implements EventNotifyService {
    // 调用之前
    @Override
    public void onInvoke(String name) {
        System.out.println("[事件通知][调用之前] onInvoke 执行.");
    }
    // 调用之后
    @Override
    public void onReturn(String result, String name) {
        System.out.println("[事件通知][调用之后] onReturn 执行.");
        // 埋点已支付的商品信息
        method2();
        // 发送支付成功短信给用户
        method3();
        // 通知物流派件
        method4();
    }
    // 调用异常
    @Override
    public void onThrow(Throwable ex, String name) {
        System.out.println("[事件通知][调用异常] onThrow 执行.");
    }
}
```

通过这样的整理，我们彻底在 recvPay 方法中凸显了支付核心业务逻辑的重要性，剥离解耦了其他三件事与主体核心逻辑的边界。

**事件通知的应用**

事件通知的应用我们已经掌握了，不过，事件通知也只是一种机制流程，那在我们日常开发中，哪些应用场景可以考虑事件通知呢？

第一，职责分离，可以按照功能相关性剥离开，让各自的逻辑是内聚的、职责分明的。

第二，解耦，把复杂的面向过程风格的一坨代码分离，可以按照功能是技术属性还是业务属性剥离。

第三，事件溯源，针对一些事件的实现逻辑，如果遇到未知异常后还想再继续尝试重新执行的话，可以考虑事件持久化并支持在一定时间内重新回放执行。

> 这个技巧有点华而不实的味道，想要解耦的话，可以把后面3个方法放到其他业务 Bean 里处理就行了。

# 07｜参数验证：写个参数校验居然也会被训？

今天我们探索 Dubbo 框架的第六道特⾊⻛味，参数验证。

现在你的同事小马就因为漏写了参数校验被老大训话了，来看他写的一段消费方调用提供方的代码：

```java
///////////////////////////////////////////////////
// 消费方的一段调用下游 validateUser 的代码
///////////////////////////////////////////////////
@Component
public class InvokeDemoFacade {
    @DubboReference
    private ValidationFacade validationFacade;

    // 一个简单的触发调用下游 ValidationFacade.validateUser 的方法
    public String invokeValidate(String id, String name, String
        // 调用下游接口
        return validationFacade.validateUser(new ValidateUserInfo(id, name, sex));
    }
}

///////////////////////////////////////////////////
// 提供方的一段接收 validateUser 请求的代码
///////////////////////////////////////////////////
@DubboService
@Component
public class ValidationFacadeImpl implements ValidationFacade {
    @Override
    public String validateUser(ValidateUserInfo userInfo) {
        // 这里就象征性地模拟一下业务逻辑
        String retMsg = "Ret: "
                + userInfo.getId()
                + "," + userInfo.getName()
                + "," + userInfo.getSex();
        System.out.println(retMsg);
        return retMsg;
    }
}
```

老大指出的几个问题：

- 问题1：消费方代码，在调用下游的 validateUser 方法时，没有预先做一些参数的合法性校验。
- 问题2：提供方代码，服务方代码在接收请求的时候，没有对一些必要的字段进行合法性校验。

**统⼀验证**

像过滤器这种具有拦截所有请求机制功能的类，一定要先看看你所在系统的相关底层能力支撑，说不定类似的功能已经存在，我们就能物尽其用了。具体步骤就是：

- 首先找到具有拦截机制的类，这里就是 org.apache.dubbo.rpc.Filter 过滤器。
- 其次找到该 org.apache.dubbo.rpc.Filter 过滤器的所有实现类。
- 最后认真阅读每个过滤器的类名，翻阅一下每个过滤器的类注释，看看有什么用。

我们按照小技巧操作一下，org.apache.dubbo.rpc.Filter接口下有好多个实现类：

```
Filter (org.apache.dubbo.rpc)
- TokenFilter (org.apache.dubbo.rpc.filter)
- MetricsFilter (org.apache.dubbo.monitor.dubbo)
- DeprecatedFilter (org.apache.dubbo.rpc.filter)
- ClassLoaderCallbackFilter (org.apache.dubbo.rpc.filter)
- CacheFilter (org.apache.dubbo.cache.filter)
- ActiveLimitFilter (org.apache.dubbo.rpc.filter)
- ConsumerContextFilter (org.apache.dubbo.rpc.filter)
- ValidationFilter (org.apache.dubbo.validation.filter)
- GenericImplFilter (org.apache.dubbo.rpc.filter)
- MetricsFilter (org.apache.dubbo.monitor.support)
- CompatibleFilter (org.apache.dubbo.rpc.filter)
- ProfilerServerFilter (org.apache.dubbo.rpc.filter)
- ClassLoaderFilter (org.apache.dubbo.rpc.filter)
- ExceptionFilter (org.apache.dubbo.rpc.filter)
- ProviderAuthFilter (org.apache.dubbo.auth.filter)
- ListenableFilter (org.apache.dubbo.rpc)
- FutureFilter (org.apache.dubbo.rpc.protocol.dubbo.filter)
- AccessLogFilter (org.apache.dubbo.rpc.filter)
- TimeoutFilter (org.apache.dubbo.rpc.filter)
- TraceFilter (org.apache.dubbo.rpc.protocol.dubbo.filter)
- ConsumerSignFilter (org.apache.dubbo.auth.filter)
- TpsLimitFilter (org.apache.dubbo.rpc.filter)
- GenericFilter (org.apache.dubbo.rpc.filter)
- MonitorFilter (org.apache.dubbo.monitor.support)
- ExecuteLimitFilter (org.apache.dubbo.rpc.filter)
- ContextFilter (org.apache.dubbo.rpc.filter)
- Filter (com.alibaba.dubbo.rpc)
- EchoFilter (org.apache.dubbo.rpc.filter)
```

耐心些一路看下去，在第9行，你会发现一个 ValidationFilter 类，通过类名的英文单词能大致看出是一个验证的过滤器。是不是底层框架已经做了我们想做的事情了呢？我们进入源码一探究竟。

ValidationFilter 的类注释信息：简单理解就是，ValidationFilter 会根据 url 配置的 validation 属性值找到正确的校验器，在方法真正执行之前触发调用校验器执行参数验证逻辑。

类注释里还举了个例子：

```
e.g. <dubbo:method name="save" validation="jvalidation" />
```

可以在方法层面添加 validation 属性，并设置属性值为 jvalidation，这样就可以正常使用底层提供的参数校验机制了。

还提到特殊设置方式：

```
e.g. <dubbo:method name="save" validation="special" />
where "special" is representing a validator for special character.
special=xxx.yyy.zzz.SpecialValidation under META-INF folders org.apache.dubbo.validation.Validation file.
```

可以在 validation 属性的值上，填充一个自定义的校验类名，并且嘱咐我们记得将自定义的校验类名添加到 META-INF 文件夹下的 org.apache.dubbo.validation.Validation 文件中。

**代码改造**

我们进入 ValidationFilter 源码类看看，找到 invoke 方法，顺着逻辑逐行点进每个方法：

```java
// org.apache.dubbo.validation.filter.ValidationFilter.invoke
public Result invoke(Invoker<?> invoker, Invocation invocation) throws RpcException {
    // Validation 接口的代理类被注入成功，且该调用的方法有 validation 属性
    if (validation != null && !invocation.getMethodName().startsWith("$")
            && ConfigUtils.isNotEmpty(invoker.getUrl().getMethodParameter(invocation.getMethodName(), "validation"))) {
        try {
            // 接着通过 url 中 validation 属性值，并且为该方法创建对应的校验实现类
            Validator validator = validation.getValidator(invoker.getUrl());
            if (validator != null) {
                // 若找到校验实现类的话，则真正开启对方法的参数进行校验
                validator.validate(invocation.getMethodName(), invocation.getParameterTypes(), invocation.getArguments());
            }
        } catch (RpcException e) {
            // RpcException 异常直接抛出去
            throw e;
        } catch (Throwable t) {
            // 非 RpcException 异常的话，则直接封装结果返回
            return AsyncRpcResult.newDefaultAsyncResult(t, invocation);
        }
    }
    // 能来到这里，说明要么没有配置校验过滤器，要么就是校验了但参数都合法
    // 既然没有抛异常的话，那么就直接调用下一个过滤器的逻辑
    return invoker.invoke(invocation);
}

// org.apache.dubbo.validation.support.AbstractValidation.getValidator
public Validator getValidator(URL url) {
    // 将 url 转成字符串形式
    String key = url.toFullString();
    // validators 是一个 Map 结构，即底层可以说明每个方法都可以有不同的校验器
    Validator validator = validators.get(key);
    if (validator == null) {
        // 若通过 url 从 Map 结构中找不到 value 的话，则直接根据 url 创建一个校验器实现类
        // 而且 createValidator 是一个 protected abstract 修饰的
        // 说明是一种模板方式，创建校验器实现类，是可被重写重新创建自定义的校验器
        validators.put(key, createValidator(url));
        validator = validators.get(key);
    }
    return validator;
}

// org.apache.dubbo.validation.support.jvalidation.JValidation
public class JValidation extends AbstractValidation {
    @Override
    protected Validator createValidator(URL url) {
        // 创建一个 Dubbo 框架默认的校验器
        return new JValidator(url);
    }
}

// org.apache.dubbo.validation.support.jvalidation.JValidator
public class JValidator implements Validator {
    // 省略其他部分代码
    // 进入到 Dubbo 框架默认的校验器中，发现真实采用的是 javax 第三方的 validation 插件
    // 由此，我们应该找到了标准产物的关键突破口了
    private final javax.validation.Validator validator;
}
```

跟踪源码的过程：

- 先找到 ValidationFilter 过滤器的 invoke 入口。
- 紧接着找到根据 validation 属性值创建校验器的 createValidator 方法。
- 然后发现创建了一个 JValidator 对象。
- 在该对象中发现了关于 javax 包名的第三方 validation 插件。

最终我们确实发现了一个第三方 validation 插件，顺藤摸瓜你可以找到对应的 maven 坐标：

```xml
<dependency>
    <groupId>org.hibernate</groupId>
    <artifactId>hibernate-validator</artifactId>
</dependency>
```

我们进入 hibernate-validator 插件的 pom 中，能看到里面引用了一个 validation-api 插件坐标：

```xml
<dependency>
    <groupId>javax.validation</groupId>
    <artifactId>validation-api</artifactId>
</dependency>
```

万事俱备，只欠代码，改造如下：

```java
///////////////////////////////////////////////////
// 统一验证：下游 validateUser 的方法入参对象
///////////////////////////////////////////////////
@Setter
@Getter
public class ValidateUserInfo implements Serializable {
    private static final long serialVersionUID = 1558193327511325424L;
    // 添加了 @NotBlank 注解
    @NotBlank(message = "id 不能为空")
    private String id;
    // 添加了 @Length 注解
    @Length(min = 5, max = 10, message = "name 必须在 5~10 个长度之间")
    private String name;
    // 无注解修饰
    private String sex;
}

///////////////////////////////////////////////////
// 统一验证：消费方的一段调用下游 validateUser 的代码
///////////////////////////////////////////////////
@Component
public class InvokeDemoFacade {

    // 注意，@DubboReference 这里添加了 validation 属性
    @DubboReference(validation ＝ "jvalidation")
    private ValidationFacade validationFacade;

    // 一个简单的触发调用下游 ValidationFacade.validateUser 的方法
    public String invokeValidate(String id, String name, String sex) {
        return validationFacade.validateUser(new ValidateUserInfo(id, name, sex));
    }
}

///////////////////////////////////////////////////
// 统一验证：提供方的一段接收 validateUser 请求的代码
///////////////////////////////////////////////////
// 注意，@DubboService 这里添加了 validation 属性
@DubboService(validation ＝ "jvalidation")
@Component
public class ValidationFacadeImpl implements ValidationFacade {
    @Override
    public String validateUser(ValidateUserInfo userInfo) {
        // 这里就象征性的模拟下业务逻辑
        String retMsg = "Ret: "
                + userInfo.getId()
                + "," + userInfo.getName()
                + "," + userInfo.getSex();
        System.out.println(retMsg);
        return retMsg;
    }
}
```

其他代码没有多大变化，主要改动是3点，也就是我们前面梳理的需要改造的3点：

1. 提供方将方法入参的 id、name 字段添加了注解。
2. 提供方在 ValidationFacadeImpl 类的 @DubboService 注解中添加了 validation 属性，属性对应的值为 jvalidation。
3. 消费方在调用提供方时，在 InvokeDemoFacade 中给 validationFacade 字段的 @DubboReference 注解中也添加了一个 validation 属性，属性对应的值也为 jvalidation。

代码写完，再回过头来看看老大训斥的2个问题有没有解决：

- 问题1：消费方代码，在调用下游的 validateUser 方法时，没有预先做一些参数的合法性校验。
- 问题2：提供方代码，服务方代码在接收请求的时候，没有对一些必要的字段进行合法性校验。

问题1我们可以通过在 @DubboReference 注解中添加 validation 属性解决，问题2我们可以在 @DubboService 注解中添加 validation 属性解决。

这样，我们轻松做到了既能在消费方提前预判参数的合法性，也能在提供方进行参数的兜底校验，还能让代码更加精简提升编码效率，减少大量枯燥无味的雷同代码。

**参数验证的应⽤**

但是这种简单的参数校验也不是万能的，在我们实际应用开发过程中，哪些应用场景可以考虑这种参数校验呢？

- 第一，单值简单规则判断，各个字段的校验逻辑毫无关联、相互独立。
- 第二，提前拦截掉脏请求，尽可能把一些参数值不合法的情况提前过滤掉，对于消费方来说尽量把高质量的请求发往提供方，对于提供方来说，尽量把非法的字段值提前拦截，以此保证核心逻辑不被脏请求污染。
- 第三，通用网关校验领域，在网关领域部分很少有业务逻辑，但又得承接请求，对于不合法的参数请求就需要尽量拦截掉，避免不必要的请求打到下游系统，造成资源浪费。

# 08｜缓存操作：如何为接口优雅地提供缓存功能？

今天我们探索 Dubbo 框架的第七道特⾊⻛味，缓存操作。

移动端App你应该不陌生了，不过最近有个项目引发了用户吐槽：

![image-20250317225403361](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503172254647.png)

图中的App，在首页进行页面渲染加载时会向网关发起请求，网关会从权限系统拿到角色信息列表和菜单信息列表，从用户系统拿到当前登录用户的简单信息，然后把三块信息一并返回给到App。

然而，就是这样一个看似简单的功能，每当上下班的时候因为App被打开的频率非常高，首页加载的请求流量在短时间内居高不下，打开很卡顿，渲染很慢。

经过排查后，发现该App只有数十万用户，但意外的是在访问高峰期，权限系统的响应时间比以往增长了近10倍，权限系统集群中单机查询数据库的QPS高达500多，导致数据库的查询压力特别大，从而导致查询请求响应特别慢。

由于目前用户体量尚且不大，架构团队商讨后，为了稳住用户体验，最快的办法就是在网关增加缓存功能，把首页加载请求的结果缓存起来，以提升首页快速渲染页面的时效。

对于这个加缓存的需求，你会如何优雅地处理呢？

**套用源码**

来看 org.apache.dubbo.rpc.Filter 接口的实现类，寻找有没有缓存英文单词的类名，你会发现还真有一个叫 CacheFilter 名字的类，看起来像是缓存过滤器。

我们看注释，还有一部分注释是教我们如何使用缓存的：

```xml
e.g. 1)<dubbo:service cache="lru" />
     2)<dubbo:service /> <dubbo:method name="method2" cache="threadlocal" /> <dubbo:service/>
     3)<dubbo:provider cache="expiring" />
     4)<dubbo:consumer cache="jcache" />
```

接下来我们可以根据源码提示的解决方案去改造代码了。改造如下：

```java
@Component
public class InvokeCacheFacade {
    // 引用下游查询角色信息列表的接口，添加 cache = lru 属性
    @DubboReference(cache = "lru")
    private RoleQueryFacade roleQueryFacade;
    // 引用下游查询菜单信息列表的接口，添加 cache = lru 属性
    @DubboReference(cache = "lru")
    private MenuQueryFacade menuQueryFacade;
    // 引用下游查询菜单信息列表的接口，没有添加缓存属性
    @DubboReference
    private UserQueryFacade userQueryFacade;

    public void invokeCache(){
        // 循环 3 次，模拟网关被 App 请求调用了 3 次
        for (int i = 1; i <= 3; i++) {
            // 查询角色信息列表
            String roleRespMsg = roleQueryFacade.queryRoleList("Geek");
            // 查询菜单信息列表
            String menuRespMsg = menuQueryFacade.queryAuthorizedMenuList("Geek");
            // 查询登录用户简情
            String userRespMsg = userQueryFacade.queryUser("Geek");

            // 打印远程调用的结果，看看是走缓存还是走远程
            String idx = new DecimalFormat("00").format(i);
            System.out.println("第 "+ idx + " 次调用【角色信息列表】结果为: " + roleRespMsg);
            System.out.println("第 "+ idx + " 次调用【菜单信息列表】结果为: " + menuRespMsg);
            System.out.println("第 "+ idx + " 次调用【登录用户简情】结果为: " + userRespMsg);
            System.out.println();
        }
    }
}
```

运行 invokeCache 方法，打印如下：

```
第 01 次调用【角色信息列表】结果为: 2022-11-18_22:52:00.402: Hello Geek, 已查询该用户【角色列表信息】
第 01 次调用【菜单信息列表】结果为: 2022-11-18_22:52:00.407: Hello Geek, 已查询该用户已授权的【菜单列表信息】
第 01 次调用【登录用户简情】结果为: 2022-11-18_22:52:00.411: Hello Geek, 已查询【用户简单信息】

第 02 次调用【角色信息列表】结果为: 2022-11-18_22:52:00.415: Hello Geek, 已查询该用户【角色列表信息】
第 02 次调用【菜单信息列表】结果为: 2022-11-18_22:52:00.419: Hello Geek, 已查询该用户已授权的【菜单列表信息】
第 02 次调用【登录用户简情】结果为: 2022-11-18_22:52:00.422: Hello Geek, 已查询【用户简单信息】

第 03 次调用【角色信息列表】结果为: 2022-11-18_22:52:00.415: Hello Geek, 已查询该用户【角色列表信息】
第 03 次调用【菜单信息列表】结果为: 2022-11-18_22:52:00.419: Hello Geek, 已查询该用户已授权的【菜单列表信息】
第 03 次调用【登录用户简情】结果为: 2022-11-18_22:52:00.426: Hello Geek, 已查询【用户简单信息】
```

“角色信息列表”在第2次和第3次的时间戳信息是一样的 415 结尾，“菜单信息列表”在第2次和第3次的时间戳信息也是一样的，而“登录用户简情”的时间戳每次都是不一样。

日志信息很有力地说明缓存功能生效了。

**改造思考**

1. 改造方案的数据是存储在 JVM 内存中，那会不会撑爆内存呢？

我们盘算一下，假设角色信息列表和菜单信息列表占用内存总和约为 1024 字节，预估有 50 万用户体量，那么最终总共占用 50W \* 1024字节 ≈ 488.28 兆，目前网关的老年代大小约为 1200 兆，是不会撑爆内存的。这个问题解决。

2. 如果某些用户的权限发生了变更，从变更完成到能使用最新数据的容忍时间间隔是多少，如何完成内存数据的刷新操作呢？

目前改造方案使用的是 `cache = "lru"` 缓存策略，虽然我们对底层的实现细节一概不知，但也没有什么好胆怯的，开启 debug 模式去 CacheFilter 中调试一番：

```java
// 过滤器被触发调用的入口
org.apache.dubbo.cache.filter.CacheFilter#invoke
                  ↓
// 根据 invoker.getUrl() 获取缓存容器
org.apache.dubbo.cache.support.AbstractCacheFactory#getCache
                  ↓
// 若缓存容器没有的话，则会自动创建一个缓存容器
org.apache.dubbo.cache.support.lru.LruCacheFactory#createCache
                  ↓
// 最终创建的是一个 LruCache 对象，该对象的内部使用的 LRU2Cache 存储数据
org.apache.dubbo.cache.support.lru.LruCache#LruCache
// 存储调用结果的对象
private final Map<Object, Object> store;
public LruCache(URL url) {
    final int max = url.getParameter("cache.size", 1000);
    this.store = new LRU2Cache<>(max);
}
                  ↓
// LRU2Cache 的带参构造方法，在 LruCache 构造方法中，默认传入的大小是 1000
org.apache.dubbo.common.utils.LRU2Cache#LRU2Cache(int)
public LRU2Cache(int maxCapacity) {
    super(16, DEFAULT_LOAD_FACTOR, true);
    this.maxCapacity = maxCapacity;
    this.preCache = new PreCache<>(maxCapacity);
}
// 若继续放数据时，若发现现有数据个数大于 maxCapacity 最大容量的话
// 则会考虑抛弃掉最古老的一个，也就是会抛弃最早进入缓存的那个对象
@Override
protected boolean removeEldestEntry(java.util.Map.Entry<K, V> eldest) {
    return size() > maxCapacity;
}
                  ↓
// JDK 中的 LinkedHashMap 源码在发生节点插入后
// 给了子类一个扩展删除最旧数据的机制
java.util.LinkedHashMap#afterNodeInsertion
void afterNodeInsertion(boolean evict) { // possibly remove eldest
    LinkedHashMap.Entry<K,V> first;
    if (evict && (first = head) != null && removeEldestEntry(first)) {
        K key = first.key;
        removeNode(hash(key), key, null, false, true);
    }
}
```

一路跟踪源码，最终发现了底层存储数据的是一个继承了 LinkedHashMap 的类，即 LRU2Cache，它重写了父类 LinkedHashMap 中的 removeEldestEntry 方法，当 LRU2Cache 存储的数据个数大于设置的容量后，会删除最先存储的数据，让最新的数据能够保存进来。

所以容忍的时间间隔其实是不确定的，因为请求流量的不确定性，LRU2Cache 的容量不知道多久才能打满，而刷新操作也是依赖于容量被打满后剔除最旧数据的机制，所以容忍的时间间隔和刷新的时效都存在不确定性。

3. 每秒的请求流量峰值是多少呢，会引发缓存雪崩、穿透、击穿三大效应么？

从权限系统的单机查询数据库高达500多的QPS可以大概得知，目前网关接收首页加载的请求在500多QPS左右。

如果用户都在早上的上班时刻打开App，因为每个用户第一次请求在网关是没有缓存数据的，第二次发起的请求就可以使用上缓存数据了，也就是说，只要撑过第一次请求，后面的第二次乃至第N次请求就会改善很多。可以反推出，LruCache 的构造方法中cache.size 参数设置至关重要。

当然问题还有很多，比如网关系统只有这个首页加载的请求需要缓存么，是否还有其他的功能也用了缓存占用了 JVM 内存？

这么问下去，我们简单地用个 lru 策略已经招架不住了，该继续想其他法子了。

**深挖源码**

刚刚只是用了 lru 策略，我们还有另外 threadlocal、jcache、expiring 三个策略可以替换，先到这三个策略对应的缓存工厂类中去看看类注释信息：

- threadlocal，使用的是 ThreadLocalCacheFactory 工厂类，类名中 ThreadLocal 是本地线程的意思，而 ThreadLocal 最终还是使用的是 JVM 内存。
- jcache，使用的是 JCacheFactory 工厂类，是提供 javax-spi 缓存实例的工厂类，既然是一种 spi 机制，可以接入很多自制的开源框架。
- expiring，使用的是 ExpiringCacheFactory 工厂类，内部的 ExpiringCache 中还是使用的 Map 数据结构来存储数据，仍然使用的是 JVM 内存。

由于 JVM 内存的有限性，无法支撑更多的接口具有缓存特性，如果稍不留神，很可能导致网关内存溢出或权限系统的数据库被打爆。那把 `cache = "lru"` 换成 `cache = "jcache"` 试试。

需要引入依赖：

```xml
<dependency>
  <groupId>javax.cache</groupId>
  <artifactId>cache-api</artifactId>
</dependency>
```

Redisson 框架中实现了 CachingProvider 接口的类， 这就是我们要找的 Redis 缓存框架了，引入依赖：

```xml
<dependency>
    <groupId>org.redisson</groupId>
    <artifactId>redisson</artifactId>
    <version>3.18.0</version>
</dependency>
```

接下来，我们编写配置文件。拿创建 redisson-jcache.json 文件举例，方便演示我们就先配置一个单机 redis 服务节点，如果要上到生产，记得采用 clusterServersConfig 集群服务配置：

```json
{
  "singleServerConfig": {
    "address": "redis://127.0.0.1:6379"
  }
}
```

.json配置文件中，我们只是配置了单机Redis服务的节点。现在启动Redis服务，再去触发调用一下运行 invokeCache 方法看看效果。

终于成功了，打印信息如下：

```
第 01 次调用【角色信息列表】结果为: 2022-11-19_01:44:43.482: Hello Geek, 已查询该用户【角色列表信息】
第 01 次调用【菜单信息列表】结果为: 2022-11-19_01:44:43.504: Hello Geek, 已查询该用户已授权的【菜单列表信息】
第 01 次调用【登录用户简情】结果为: 2022-11-19_01:44:43.512: Hello Geek, 已查询【用户简单信息】

第 02 次调用【角色信息列表】结果为: 2022-11-19_01:44:43.482: Hello Geek, 已查询该用户【角色列表信息】
第 02 次调用【菜单信息列表】结果为: 2022-11-19_01:44:43.504: Hello Geek, 已查询该用户已授权的【菜单列表信息】
第 02 次调用【登录用户简情】结果为: 2022-11-19_01:44:43.959: Hello Geek, 已查询【用户简单信息】

第 03 次调用【角色信息列表】结果为: 2022-11-19_01:44:43.482: Hello Geek, 已查询该用户【角色列表信息】
第 03 次调用【菜单信息列表】结果为: 2022-11-19_01:44:43.504: Hello Geek, 已查询该用户已授权的【菜单列表信息】
第 03 次调用【登录用户简情】结果为: 2022-11-19_01:44:43.975: Hello Geek, 已查询【用户简单信息】
```

“角色信息列表”3次调用的时间戳信息完全是一样的，“菜单信息列表”3次调用的时间戳信息也是一样的，我们接入 Redis 缓存框架生效了！

**缓存操作的应用**

在经过一番改造后，采用Redis分布式缓存的确可以缓解短时间内首页加载的压力。

但是也不是任何情况遇到问题了就用缓存处理，缓存也是有一些缺点的，比如大对象与用户进行笛卡尔积的容量很容易撑爆内存，服务器掉电或宕机容易丢失数据，在分布式环境中缓存的一致性问题不但增加了系统的实现复杂度，而且还容易引发各种数据不一致的业务问题。

那哪些日常开发的应用场景可以考虑呢？

- 第一，数据库缓存，对于从数据库查询出来的数据，如果多次查询变化差异较小的话，可以按照一定的维度缓存起来，减少访问数据库的次数，为数据库减压。
- 第二，业务层缓存，对于一些聚合的业务逻辑，执行时间过长或调用次数太多，而又可以容忍一段时间内数据的差异性，也可以考虑采取一定的维度缓存起来。

# 09｜流量控制：控制接口调用请求流量的三个秘诀

今天我们探索 Dubbo 框架的第⼋道特⾊⻛味，流量控制。

**单机限流**

我们先从最简单的单机开始。把 Dubbo 服务中的方法作为最细粒度，对每个方法设计出一个 **标准容量参数**，然后在方法开始执行业务逻辑时进行计数加1，最后在方法结束执行业务时进行计数减1，而这个计数加1、计数减1就是我们需要的 **实时容量参数**。

于是权限系统的流程图变成这样：

![image-20250318222421968](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503182224354.png)

我们可以考虑采用 ConcurrentMap + AtomicInteger 来进行加减操作，ConcurrentMap 中的 key 存储的是服务名加方法名，value 是目前已使用次数，ConcurrentMap 保证同一个 key 在并发时计数不相互覆盖，AtomicInteger 保证原子性的加减计数。

```java
///////////////////////////////////////////////////
// 提供方：自定义限流过滤器
///////////////////////////////////////////////////
@Activate(group = PROVIDER)
public class CustomLimitFilter implements Filter {
    /** <h2>存储计数资源的Map数据结构，预分配容量64，避免无畏的扩容消耗</h2> **/
    private static final ConcurrentMap<String, AtomicInteger> COUNT_MAP = new ConcurrentHashMap<>(64);
    /** <h2>标识启动QPS限流检测，{@code true}：标识开启限流检测，{@code false 或 null}：标识不开启限流检测</h2> **/
    public static final String KEY_QPS_ENABLE = "qps.enable";
    /** <h2>每个方法开启的限流检测值</h2> **/
    public static final String KEY_QPS_VALUE = "qps.value";
    /** <h2>默认的限流检测值，默认为 30</h2> **/
    public static final long DEFAULT_QPS_VALUE = 30;

    @Override
    public Result invoke(Invoker<?> invoker, Invocation invocation) throws RpcException {
        // 获取限流资源的结果，acquired 有三种值：
        // true：获取到计数资源；false：计数已满，无法再获取计数资源；null：不需要限流
        Boolean acquired = null;
        try {
            // 尝试是否能获取到限流计数资源
            acquired = tryAcquire(invoker.getUrl(), invocation);
            // 若获取不到计数资源的话，则直接抛出异常即可，告知调用方限流了
            if (acquired != null && !acquired) {
                throw new RuntimeException(
                    "Failed to acquire service " +
                     String.join(".", invoker.getInterface().getName(), invocation.getMethodName()) +
                     " because of overload.");
            }

            // 能来到这里，要么是不需要限流，要么就是获取到了计数资源，那就直接继续下一步调用即可
            return invoker.invoke(invocation);
        } finally {
            // 调用不管是成功还是失败，都是需要进行计数资源释放的
            release(acquired, invoker.getUrl(), invocation);
        }
    }

    private Boolean tryAcquire(URL url, Invocation invocation) {
        // 从方法层面获取 qps.enable 参数值，如果为 true 则表示开启限流控制，否则不需要限流
        String qpsEnableFlag = url.getMethodParameter(invocation.getMethodName(), KEY_QPS_ENABLE);
        if (!Boolean.TRUE.toString().equals(qpsEnableFlag)) {
            return null;
        }

        // 从方法层面获取 qps.value 限流的标准容量，如果没配置则默认为 30
        long qpsValue = url.getMethodParameter(invocation.getMethodName(), KEY_QPS_VALUE, DEFAULT_QPS_VALUE);
        // 服务名加方法名构建Map的Key
        String serviceKey = String.join("_", url.getServiceKey(), invocation.getMethodName());
        // 尝试看看该服务是否有对应的计数对象
        AtomicInteger currentCount = COUNT_MAP.get(serviceKey);
        if (currentCount == null) {
            // 若没有对应的计数对象的话，则 putIfAbsent 会进行加锁控制，内部有并发锁控制
            COUNT_MAP.putIfAbsent(serviceKey, new AtomicInteger());
            currentCount = COUNT_MAP.get(serviceKey);
        }

        // 若当前的计数值大于或等于已配置的限流值的话，那么返回 false 表示无法获取计数资源
        if (currentCount.get() >= qpsValue) {
            return false;
        }

        // 能来到这里说明是可以获取锁资源的，那么就正常的加锁即可
        currentCount.incrementAndGet();
        return true;
    }

    private void release(Boolean acquired, URL url, Invocation invocation) {
        // 若不需要限流，或者没有获取到计数资源，都不需要进行计数资源释放
        if(acquired == null || !acquired){
            return;
        }
        // 释放计数资源
        String serviceKey = String.join("_", url.getServiceKey(), invocation.getMethodName());
        AtomicInteger currentCount = COUNT_MAP.get(serviceKey);
        currentCount.decrementAndGet();
    }
}

///////////////////////////////////////////////////
// 提供方：查询角色信息列表方法
// 配合限流过滤器而添加的限流参数 qps.enable、qps.value
///////////////////////////////////////////////////
@DubboService(methods = {@Method(
        name = "queryRoleList",
        parameters = {"qps.enable", "true", "qps.value", "3"})}
)
@Component
public class RoleQueryFacadeImpl implements RoleQueryFacade {
    @Override
    public String queryRoleList(String userId) {
        // 睡眠 1 秒，模拟一下查询数据库需要耗费时间
        TimeUtils.sleep(1000);
        String result = String.format(TimeUtils.now() + ": Hello %s, 已查询该用户【角色列表信息】", userId);
        System.out.println(result);
        return result;
    }
}
```

我们顺着代码依次看下在提供方的改造要点：

1. 定义了一个自定义限流过滤器，并设置为主要在提供方生效。
2. 定义了 qps.enable、qps.value 两个方法级别的参数，qps.enable 参数主要表示是否开启流量控制，qps.value 参数主要表示流量的标准容量上限值，这里设置了标准容量的上限值为 3。
3. 在 invoke 方法中先尝试能否获取计数资源，如果不需要限流或已获取限流计数资源，则拦截放行继续向后调用，否则会抛出无法获取计数资源的运行时异常。
4. 在 invoke 的 finally 代码块中处理释放计数资源的逻辑。
5. 在提供方的 @DubboService 注解中，为方法增加了 qps.enable=true、qps.value=3 两个配置，来应用我们刚刚写的限流过滤器。

提供方的代码写的差不多了，马上编写消费方的代码来启动验证看看情况：

```java
@Component
public class InvokeLimitFacade {
    // 引用下游查询角色信息列表的接口
    @DubboReference(timeout = 10000)
    private RoleQueryFacade roleQueryFacade;
    // 引用下游查询菜单信息列表的接口
    @DubboReference(timeout = 10000)
    private MenuQueryFacade menuQueryFacade;
    // 引用下游查询菜单信息列表的接口
    @DubboReference
    private UserQueryFacade userQueryFacade;
    // 定义的一个线程池，来模拟网关接收了很多请求
    ExecutorService executorService = Executors.newCachedThreadPool();

    public void invokeFilter(){
        // 循环 5 次，模拟网关被 App 请求调用了 5 次
        for (int i = 1; i <= 5; i++) {
            int idx = i;
            executorService.execute(() -> invokeCacheInner(idx));
        }
    }

    private void invokeCacheInner(int i){
        // 查询角色信息列表
        String roleRespMsg = roleQueryFacade.queryRoleList("Geek");
        // 查询菜单信息列表
        String menuRespMsg = menuQueryFacade.queryAuthorizedMenuList("Geek");
        // 查询登录用户简情
        String userRespMsg = userQueryFacade.queryUser("Geek");

        // 打印远程调用的结果，看看是走缓存还是走远程
        String idx = new DecimalFormat("00").format(i);
        System.out.println("第 "+ idx + " 次调用【角色信息列表】结果为: " + roleRespMsg);
        System.out.println("第 "+ idx + " 次调用【菜单信息列表】结果为: " + menuRespMsg);
        System.out.println("第 "+ idx + " 次调用【登录用户简情】结果为: " + userRespMsg);
        System.out.println();
    }
}
```

运行 invokeFilter 方法后，网关发起的 5 次请求，3 次是成功的，另外 2 次被拒绝了并且打印了拒绝异常信息如下：

```
Caused by: org.apache.dubbo.remoting.RemotingException: java.lang.RuntimeException: Failed to acquire service com.hmilyylimh.cloud.facade.role.RoleQueryFacade.queryRoleList because of overload.
java.lang.RuntimeException: Failed to acquire service com.hmilyylimh.cloud.facade.role.RoleQueryFacade.queryRoleList because of overload.
	at com.hmilyylimh.cloud.limit.config.CustomLimitFilter.invoke(CustomLimitFilter.java:38)
	at org.apache.dubbo.rpc.cluster.filter.FilterChainBuilder$CopyOfFilterChainNode.invoke(FilterChainBuilder.java:321)
```

**分布式限流**

如果要控制某个接口在所有集群中的流量次数，单机还能做到么？

很多人直觉这还不简单，如果某个方法需要按照 qps = 100 进行限流，集群中有 4 台机器，那么只要设置 qps.value = 100/4 = 25 不就可以了么，轻松搞定。这，也不是不可以，只是前提得保证所有机器都正常运转。如果现在有 1 台机器宕机了，那一段时间内，我们岂不是只能提供 qps.size = 25\*3 = 75 的能力了，不满足添加或减少机器方法总 QPS 不变的诉求。

那我们将提供方的代码稍微改造为用 Redis 来计数处理，代码如下：

```java
///////////////////////////////////////////////////
// 提供方：自定义限流过滤器， jvm + redis 的支持
///////////////////////////////////////////////////
@Activate(group = PROVIDER)
public class CustomLimitFilter implements Filter {
    /** <h2>存储计数资源的Map数据结构，预分配容量64，避免无畏的扩容消耗</h2> **/
    private static final ConcurrentMap<String, AtomicInteger> COUNT_MAP = new ConcurrentHashMap<>(64);
    /** <h2>标识启动QPS限流检测，{@code true}：标识开启限流检测，{@code false 或 null}：标识不开启限流检测</h2> **/
    public static final String KEY_QPS_ENABLE = "qps.enable";
    /** <h2>处理限流的工具，枚举值有：jlimit-JVM限流；rlimit-Redis限流。</h2> **/
    public static final String KEY_QPS_TYPE = "qps.type";
    /** <h2>处理限流的工具，jlimit-JVM限流</h2> **/
    public static final String VALUE_QPS_TYPE_OF_JLIMIT = "jlimit";
    /** <h2>处理限流的工具，rlimit-Redis限流。</h2> **/
    public static final String VALUE_QPS_TYPE_OF_RLIMIT = "rlimit";
    /** <h2>每个方法开启的限流检测值</h2> **/
    public static final String KEY_QPS_VALUE = "qps.value";
    /** <h2>默认的限流检测值</h2> **/
    public static final long DEFAULT_QPS_VALUE = 30;
    /** <h2>策略分发，通过不同的 qps.type 值来选择不同的限流工具进行获取计数资源处理</h2> **/
    private static final Map<String, BiFunction<URL, Invocation, Boolean>> QPS_TYPE_ACQUIRE_MAP = new HashMap<>(4);
    /** <h2>策略分发，通过不同的 qps.type 值来选择不同的限流工具进行释放计数资源处理</h2> **/
    private static final Map<String, BiConsumer<URL, Invocation>> QPS_TYPE_RELEASE_MAP = new HashMap<>(4);
    /** <h2>这里得想办法采取扫描机制简单支持 @Autowired、@Resource 两个注解即可</h2> **/
    @Autowired
    private RedisTemplate redisTemplate;

    /** <h2>利用默认的构造方法在创建的时候，顺便把两个策略Map初始化一下</h2> **/
    public CustomLimitFilter() {
        init();
    }

    private void init() {
        QPS_TYPE_ACQUIRE_MAP.put(VALUE_QPS_TYPE_OF_JLIMIT, (url, invocation) -> tryAcquireOfJvmLimit(url, invocation));
        QPS_TYPE_ACQUIRE_MAP.put(VALUE_QPS_TYPE_OF_RLIMIT, (url, invocation) -> tryAcquireOfRedisLimit(url, invocation));
        QPS_TYPE_RELEASE_MAP.put(VALUE_QPS_TYPE_OF_JLIMIT, (url, invocation) -> releaseOfJvmLimit(url, invocation));
        QPS_TYPE_RELEASE_MAP.put(VALUE_QPS_TYPE_OF_RLIMIT, (url, invocation) -> releaseOfRedisLimit(url, invocation));
    }

    @Override
    public Result invoke(Invoker<?> invoker, Invocation invocation) throws RpcException {
        // 获取限流资源的结果，acquired 有三种值：
        // true：获取到计数资源；false：计数已满，无法再获取计数资源；null：不需要限流
        Boolean acquired = null;
        try {
            // 尝试是否能获取到限流计数资源
            acquired = tryAcquire(invoker.getUrl(), invocation);
            // 若获取不到计数资源的话，则直接抛出异常即可，告知调用方限流了
            if (acquired != null && !acquired) {
                throw new RuntimeException(
                    "Failed to acquire service " +
                     String.join(".", invoker.getInterface().getName(), invocation.getMethodName()) +
                     " because of overload.");
            }
            // 能来到这里，要么是不需要限流，要么就是获取到了计数资源，那就直接继续下一步调用即可
            return invoker.invoke(invocation);
        } finally {
            // 调用不管是成功还是失败，都是需要进行计数资源释放的
            release(acquired, invoker.getUrl(), invocation);
        }
    }

    // 尝试是否能获取到限流计数资源
    private Boolean tryAcquire(URL url, Invocation invocation) {
        // 从方法层面获取 qps.enable 参数值，如果为 true 则表示开启限流控制，否则不需要限流
        String qpsEnableFlag = url.getMethodParameter(invocation.getMethodName(), KEY_QPS_ENABLE);
        if (!Boolean.TRUE.toString().equals(qpsEnableFlag)) {
            return null;
        }

        // 从方法层面获取 qps.type 参数值，默认采用 JVM 内存来处理限流，若设置的类型从 Map 中找不到则当作不需要限流处理
        String qpsTypeVal = url.getMethodParameter
                (invocation.getMethodName(), KEY_QPS_TYPE, VALUE_QPS_TYPE_OF_JLIMIT);
        BiFunction<URL, Invocation, Boolean> func = QPS_TYPE_ACQUIRE_MAP.get(qpsTypeVal);
        if (func == null) {
            return null;
        }

        // 根据 qps.type 找到对应的工具进行策略分发按照不同的工具进行限流处理
        return func.apply(url, invocation);
    }

    // 进行计数资源释放
    private void release(Boolean acquired, URL url, Invocation invocation) {
        // 若不需要限流，或者没有获取到计数资源，都不需要进行计数资源释放
        if(acquired == null || !acquired){
            return;
        }

        // 从方法层面获取 qps.type 参数值，默认采用 JVM 内存来处理限流，若设置的类型从 Map 中找不到则当作不需要限流处理
        String qpsTypeVal = url.getMethodParameter
                (invocation.getMethodName(), KEY_QPS_TYPE, VALUE_QPS_TYPE_OF_JLIMIT);
        BiConsumer<URL, Invocation> func = QPS_TYPE_RELEASE_MAP.get(qpsTypeVal);
        if (func == null) {
            return;
        }

        // 根据 qps.type 找到对应的工具进行策略分发按照不同的工具进行释放计数资源处理
        func.accept(url, invocation);
    }

    // 通过JVM内存的处理方式，来尝试是否能获取到限流计数资源
    private Boolean tryAcquireOfJvmLimit(URL url, Invocation invocation) {
        // 从方法层面获取 qps.value 限流的标准容量，如果没配置则默认为 30
        long qpsValue = url.getMethodParameter
                (invocation.getMethodName(), KEY_QPS_VALUE, DEFAULT_QPS_VALUE);
        // 服务名加方法名构建Map的Key
        String serviceKey = String.join("_", url.getServiceKey(), invocation.getMethodName());

        // 尝试看看该服务是否有对应的计数对象
        AtomicInteger currentCount = COUNT_MAP.get(serviceKey);
        if (currentCount == null) {
            // 若没有对应的计数对象的话，则 putIfAbsent 会进行加锁控制，内部有并发锁控制
            COUNT_MAP.putIfAbsent(serviceKey, new AtomicInteger());
            currentCount = COUNT_MAP.get(serviceKey);
        }

        // 若当前的计数值大于或等于已配置的限流值的话，那么返回 false 表示无法获取计数资源
        if (currentCount.get() >= qpsValue) {
            return false;
        }
        // 能来到这里说明是可以获取锁资源的，那么就正常的加锁即可
        currentCount.incrementAndGet();
        return true;
    }

    // 通过JVM内存的处理方式，来进行计数资源释放
    private void releaseOfJvmLimit(URL url, Invocation invocation) {
        // 释放计数资源
        String serviceKey = String.join("_", url.getServiceKey(), invocation.getMethodName());
        AtomicInteger currentCount = COUNT_MAP.get(serviceKey);
        currentCount.decrementAndGet();
    }

    // 通过Redis的处理方式，来尝试是否能获取到限流计数资源
    private Boolean tryAcquireOfRedisLimit(URL url, Invocation invocation) {
        // 从方法层面获取 qps.value 限流的标准容量，如果没配置则默认为 30
        long qpsValue = url.getMethodParameter
                (invocation.getMethodName(), KEY_QPS_VALUE, DEFAULT_QPS_VALUE);
        // 服务名加方法名构建Map的Key
        String serviceKey = String.join("_", url.getServiceKey(), invocation.getMethodName());

        // 尝试看看该服务在 redis 中当前计数值是多少
        int currentCount = NumberUtils.toInt(redisTemplate.opsForValue().get(serviceKey));
        // 若当前的计数值大于或等于已配置的限流值的话，那么返回 false 表示无法获取计数资源
        if (currentCount.get() >= qpsValue) {
            return false;
        }

        // 能来到这里说明是可以获取锁资源的，那么就正常的加锁即可
        redisTemplate.opsForValue().increment(serviceKey, 1);
        return true;
    }

    // 通过Redis的处理方式，来进行计数资源释放
    private void releaseOfRedisLimit(URL url, Invocation invocation) {
        // 释放计数资源
        String serviceKey = String.join("_", url.getServiceKey(), invocation.getMethodName());
        redisTemplate.opsForValue().increment(serviceKey, -1);
    }
}

///////////////////////////////////////////////////
// 提供方：查询角色信息列表方法
// 配合限流过滤器而添加的限流参数 qps.enable、qps.value
///////////////////////////////////////////////////
@DubboService(methods = {@Method(
        name = "queryRoleList",
        parameters = {
                "qps.enable", "true",
                "qps.value", "3",
                "qps.type", "redis"
        })}
)
@Component
public class RoleQueryFacadeImpl implements RoleQueryFacade {
    @Override
    public String queryRoleList(String userId) {
        // 睡眠 1 秒，模拟一下查询数据库需要耗费时间
        TimeUtils.sleep(1000);
        String result = String.format(TimeUtils.now() + ": Hello %s, 已查询该用户【角色列表信息】", userId);
        System.out.println(result);
        return result;
    }
}
```

> Redis 的 Key 最好加个过期时间吧。

引入了Redis来处理分布式限流，主要 4 个改造点：

1. 新增了 qps.type 方法级别的参数，主要表示处理限流的工具，有 jlimit、rlimit 两种，jlimit 表示采用JVM限流，rlimit 表示采用Redis限流，qps.type 不配置的情况下默认为JVM限流。
2. 根据 qps.type 不同的值需要用不同的工具进行限流处理，这里采用了 Map 结构引入了策略模式来做分发，并把策略模式应用到 invoke 方法的主体逻辑中。
3. 新增了一套关于 Redis 的计数累加、计数核减的逻辑实现。
4. 在提供方的 @DubboService 注解中，继续为方法增加了 qps.type=redis 的配置，表示需要使用分布式限流。

**流量控制的应用**

通过一番改造后，我们知道了可以采用JVM或Redis来进行限流，防止哪天首页加载流量过高引发雪崩效应。在实际应用开发过程中，还有许多的应用场景也在使用限流。

第一，合法性限流，比如验证码攻击、恶意IP爬虫、恶意请求参数，利用限流可以有效拦截这些恶意请求，保证正常业务的运转。

第二，业务限流，比如App案例中的权限系统，参考接口的业务调用频率，我们要合理地评估功能的并发支撑能力。

第三，网关限流，比如App案例中的网关，当首页加载流量异常爆炸时，也可以进行有效的限流控制。

第四，连接数限流，比如利用线程池的数量来控制流量。

# 10｜服务认证：被异构系统侵入调用了，怎么办？

今天我们探索Dubbo框架的第九道特色风味，服务认证。

公司最近要做一个关于提升效能的一体化网站，我们的后端服务全是 Dubbo 提供者，但是负责效能开发的同事只会使用 Go 或 Python 来编写代码，于是经过再三考虑，效能同事最后使用 dubbo-go 来过渡对接后端的 Dubbo 服务。就像这样：

![image-20250319225735090](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503192257344.png)

然而，dubbo-go 服务上线后不久，某个时刻，支付系统的银行账号查询接口的QPS异常突增，引起了相关领导的关注。

目前暴露了一个比较严重的问题，被异构系统访问的接口缺乏一种认证机制，尤其是安全性比较敏感的业务接口，随随便便就被异构系统通过非正常途径调通了，有不少安全隐患。因此很有必要添加一种服务与服务之间的认证机制。

**鉴定真假**

**在客户端发送数据的时候我们添加一个 TOKEN 字段**，然后，服务端收到数据先验证 TOKEN 字段值是否存在，若存在则认为是合法可信任的请求，否则就可以抛出异常中断请求了。

这个 TOKEN 在服务端怎么验证是否存在呢？一般两种处理方式，要么服务端内部就有这个 TOKEN 直接验证，要么服务端去第三方媒介间接验证，总之处理请求的是服务端，至于服务端是内部验证还是依赖第三方媒介验证，那都是服务端的事情。顺着思路画出了这样的调用链路图：

![image-20250319225930103](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503192259296.png)

不过，我们要面临分支选择了，该使用哪种方式呢？

- 方式一无需调用远程，虽然节省了远程调用的开销，加快了处理验证的时效，但是这个 TOKEN 是位于服务端内部的，那就意味着 TOKEN 和服务端的方法有着一定的强绑定关系，不够灵活。
- 方式二远程调用，第三方认证中心可以根据不同的客户端分配不同的 TOKEN 值，并为 TOKEN 设置过期时间，灵活性和可控性变强了，但同时也牺牲了一定的远程调用时间开销。

这里为了方便演示，我们就把方式一落实到代码。

```java
///////////////////////////////////////////////////
// 提供方：自定义TOKEN校验过滤器，主要对 TOKEN 进行验证比对
///////////////////////////////////////////////////
@Activate(group = PROVIDER)
public class ProviderTokenFilter implements Filter {
    /** <h2>TOKEN 字段名</h2> **/
    public static final String TOKEN = "TOKEN";
    /** <h2>方法级别层面获取配置的 auth.enable 参数名</h2> **/
    public static final String KEY_AUTH_ENABLE = "auth.enable";
    /** <h2>方法级别层面获取配置的 auth.token 参数名</h2> **/
    public static final String KEY_AUTH_TOKEN = "auth.token";
    @Override
    public Result invoke(Invoker<?> invoker, Invocation invocation) throws RpcException {
        // 从方法层面获取 auth.enable 参数值
        String authEnable = invoker.getUrl().getMethodParameter
                (invocation.getMethodName(), KEY_AUTH_ENABLE);
        // 如果不需要开启 TOKEN 认证的话，则继续后面过滤器的调用
        if (!Boolean.TRUE.toString().equals(authEnable)) {
            return invoker.invoke(invocation);
        }
        // 能来到这里，说明需要进行 TOKEN 认证
        Map<String, Object> attachments = invocation.getObjectAttachments();
        String recvToken = attachments != null ? (String) attachments.get(TOKEN) : null;
        // 既然需要认证，如果收到的 TOKEN 为空，则直接抛异常
        if (StringUtils.isBlank(recvToken)) {
            throw new RuntimeException(
                    "Recv token is null or empty, path: " +
                     String.join(".", invoker.getInterface().getName(), invocation.getMethodName()));
        }
        // 从方法层面获取 auth.token 参数值
        String authToken = invoker.getUrl().getMethodParameter
                (invocation.getMethodName(), KEY_AUTH_TOKEN);
        // 既然需要认证，如果收到的 TOKEN 值和提供方配置的 TOKEN 值不一致的话，也直接抛异常
        if(!recvToken.equals(authToken)){
            throw new RuntimeException(
                    "Recv token is invalid, path: " +
                     String.join(".", invoker.getInterface().getName(), invocation.getMethodName()));
        }
        // 还能来到这，说明认证通过，继续后面过滤器的调用
        return invoker.invoke(invocation);
    }
}

///////////////////////////////////////////////////
// 提供方：支付账号查询方法的实现逻辑
// 关注 auth.token、auth.enable 两个新增的参数
///////////////////////////////////////////////////
@DubboService(methods = {@Method(
        name = "queryPayAccount",
        parameters = {
                "auth.token", "123456789",
                "auth.enable", "true"
        })}
)
@Component
public class PayAccountFacadeImpl implements PayAccountFacade {
    @Override
    public String queryPayAccount(String userId) {
        String result = String.format(now() + ": Hello %s, 已查询该用户的【银行账号信息】", userId);
        System.out.println(result);
        return result;
    }
    private static String now() {
        return new SimpleDateFormat("yyyy-MM-dd_HH:mm:ss.SSS").format(new Date());
    }
}

///////////////////////////////////////////////////
// 消费方：自定义TOKEN校验过滤器，主要将 TOKEN 传给提供方
///////////////////////////////////////////////////
@Activate(group = CONSUMER)
public class ConsumerTokenFilter implements Filter {
    /** <h2>方法级别层面获取配置的 auth.token 参数名</h2> **/
    public static final String KEY_AUTH_TOKEN = "auth.token";
    /** <h2>TOKEN 字段名</h2> **/
    public static final String TOKEN = "TOKEN";
    @Override
    public Result invoke(Invoker<?> invoker, Invocation invocation) throws RpcException {
        // 从方法层面获取 auth.token 参数值
        String authToken = invoker.getUrl().getMethodParameter
                    (invocation.getMethodName(), KEY_AUTH_TOKEN);
        // authToken 不为空的话则设置到请求对象中
        if (StringUtils.isNotBlank(authToken)) {
            invocation.getObjectAttachments().put(TOKEN, authToken);
        }
        // 继续后面过滤器的调用
        return invoker.invoke(invocation);
    }
}

///////////////////////////////////////////////////
// 消费方：触发调用支付账号查询接口的类
// 关注 auth.token 这个新增的参数
///////////////////////////////////////////////////
@Component
public class InvokeAuthFacade {
    // 引用下游支付账号查询的接口
    @DubboReference(timeout = 10000, methods = {@Method(
            name = "queryPayAccount",
            parameters = {
                    "auth.token", "123456789"
            })})
    private PayAccountFacade payAccountFacade;

    // 该方法主要用来触发调用下游支付账号查询方法
    public void invokeAuth(){
        String respMsg = payAccountFacade.queryPayAccount("Geek");
        System.out.println(respMsg);
    }
}
```

代码写后，我们验证一下，想办法触发调用消费方的 invokeAuth 方法，打印结果长这样：

```
2022-11-22_23:51:07.899: Hello Geek, 已查询该用户的【银行账号信息】
```

认证不通过日志打印如下：

```
Caused by: org.apache.dubbo.remoting.RemotingException: java.lang.RuntimeException: Recv token is invalid, path: com.hmilyylimh.cloud.facade.pay.PayAccountFacade.queryPayAccount
java.lang.RuntimeException: Recv token is invalid, path: com.hmilyylimh.cloud.facade.pay.PayAccountFacade.queryPayAccount
	at com.hmilyylimh.cloud.auth.config.ProviderTokenFilter.invoke(ProviderTokenFilter.java:60)
	at org.apache.dubbo.rpc.cluster.filter.FilterChainBuilder$CopyOfFilterChainNode.invoke(FilterChainBuilder.java:321)
	at org.apache.dubbo.monitor.support.MonitorFilter.invoke(MonitorFilter.java:99)
```

**鉴定篡改**

我们接着看第二个认证工作，鉴定篡改，这个比较好理解，就是证明别人发送过来的内容没有在传输过程中被偷偷改动。

这里我们就以一套常用的 RSA 加签方式进行演示。第一步当然还是梳理代码修改思路：

1. 客户端新增一个 ConsumerAddSignFilter 加签过滤器，同样服务端也得增加一个 ProviderVerifySignFilter 验签过滤器。
2. 客户端将加签的结果放在 Invocation 的 attachments 里面。
3. 服务端获取加签数据时，进行验签处理，若验签通过则放行，否则直接抛出异常。

```java
///////////////////////////////////////////////////
// 提供方：自定义验签过滤器，主要对 SIGN 进行验签
///////////////////////////////////////////////////
@Activate(group = PROVIDER)
public class ProviderVerifySignFilter implements Filter {
    /** <h2>SING 字段名</h2> **/
    public static final String SING = "SING";
    /** <h2>方法级别层面获取配置的 auth.ras.enable 参数名</h2> **/
    public static final String KEY_AUTH_RSA_ENABLE = "auth.rsa.enable";
    /** <h2>方法级别层面获取配置的 auth.rsa.public.secret 参数名</h2> **/
    public static final String KEY_AUTH_RSA_PUBLIC_SECRET = "auth.rsa.public.secret";
    @Override
    public Result invoke(Invoker<?> invoker, Invocation invocation) throws RpcException {
        // 从方法层面获取 auth.ras.enable 参数值
        String authRsaEnable = invoker.getUrl().getMethodParameter
                (invocation.getMethodName(), KEY_AUTH_RSA_ENABLE);
        // 如果不需要验签的话，则继续后面过滤器的调用
        if (!Boolean.TRUE.toString().equals(authRsaEnable)) {
            return invoker.invoke(invocation);
        }

        // 能来到这里，说明需要进行验签
        Map<String, Object> attachments = invocation.getObjectAttachments();
        String recvSign = attachments != null ? (String) attachments.get(SING) : null;
        // 既然需要认证，如果收到的加签值为空的话，则直接抛异常
        if (StringUtils.isBlank(recvSign)) {
            throw new RuntimeException(
                    "Recv sign is null or empty, path: " +
                     String.join(".", invoker.getInterface().getName(), invocation.getMethodName()));
        }

        // 从方法层面获取 auth.rsa.public.secret 参数值
        String rsaPublicSecretOpsKey = invoker.getUrl().getMethodParameter
                (invocation.getMethodName(), KEY_AUTH_RSA_PUBLIC_SECRET);
        // 从 OPS 配置中心里面获取到 rsaPublicSecretOpsKey 对应的密钥值
        String publicKey = OpsUtils.get(rsaPublicSecretOpsKey);
        // 加签处理
        boolean passed = SignUtils.verifySign(invocation.getArguments(), publicKey, recvSign);
        // sign 不为空的话则设置到请求对象中
        if (!passed) {
            throw new RuntimeException(
                    "Recv sign is invalid, path: " +
                     String.join(".", invoker.getInterface().getName(), invocation.getMethodName()));
        }

        // 继续后面过滤器的调用
        return invoker.invoke(invocation);
    }
}

///////////////////////////////////////////////////
// 提供方：支付账号查询方法的实现逻辑
// 关注 auth.rsa.public.secret、auth.rsa.enable 两个新增的参数
///////////////////////////////////////////////////
@DubboService(methods = {@Method(
        name = "queryPayAccount",
        parameters = {
                "auth.rsa.public.secret", "queryPayAccoun_publicSecret",
                "auth.rsa.enable", "true"
        })}
)
@Component
public class PayAccountFacadeImpl implements PayAccountFacade {
    @Override
    public String queryPayAccount(String userId) {
        String result = String.format(now() + ": Hello %s, 已查询该用户的【银行账号信息】", userId);
        System.out.println(result);
        return result;
    }
    private static String now() {
        return new SimpleDateFormat("yyyy-MM-dd_HH:mm:ss.SSS").format(new Date());
    }
}

///////////////////////////////////////////////////
// 消费方：自定义加签过滤器，主要将 SIGN 传给提供方
///////////////////////////////////////////////////
@Activate(group = CONSUMER)
public class ConsumerAddSignFilter implements Filter {
    /** <h2>SING 字段名</h2> **/
    public static final String SING = "SING";
    /** <h2>方法级别层面获取配置的 auth.rsa.private.secret 参数名</h2> **/
    public static final String KEY_AUTH_RSA_PRIVATE_SECRET = "auth.rsa.private.secret";
    @Override
    public Result invoke(Invoker<?> invoker, Invocation invocation) throws RpcException {
        // 从方法层面获取 auth.token 参数值
        String aesSecretOpsKey = invoker.getUrl().getMethodParameter
                (invocation.getMethodName(), KEY_AUTH_RSA_PRIVATE_SECRET);
        // 从 OPS 配置中心里面获取到 aesSecretOpsKey 对应的密钥值
        String privateKey = OpsUtils.get(aesSecretOpsKey);
        // 加签处理
        String sign = SignUtils.addSign(invocation.getArguments(), privateKey);
        // sign 不为空的话则设置到请求对象中
        if (StringUtils.isNotBlank(sign)) {
            invocation.getObjectAttachments().put(SING, sign);
        }
        // 继续后面过滤器的调用
        return invoker.invoke(invocation);
    }
}

///////////////////////////////////////////////////
// 消费方：触发调用支付账号查询接口的类
// 关注 auth.rsa.private.secret 这个新增的参数
///////////////////////////////////////////////////
@Component
public class InvokeAuthFacade {
    // 引用下游支付账号查询的接口
    @DubboReference(timeout = 10000, methods = {@Method(
            name = "queryPayAccount",
            parameters = {
                    "auth.rsa.private.secret", "queryPayAccoun_privateSecret"
            })})
    private PayAccountFacade payAccountFacade;

    // 该方法主要用来触发调用下游支付账号查询方法
    public void invokeAuth(){
        String respMsg = payAccountFacade.queryPayAccount("Geek");
        System.out.println(respMsg);
    }
}
```

# 11｜配置加载顺序：为什么你设置的超时时间不生效？

今天我们探索Dubbo框架的第十道特色风味，配置加载顺序。

