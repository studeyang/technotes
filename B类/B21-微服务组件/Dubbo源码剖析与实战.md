# 开篇词｜带你玩转Dubbo微服务框架

在这个专栏里，我会带着你以“发现问题——分析问题——解决问题”的案例驱动的思路，从一个问题现象出发，分析如何思考问题，一步步推导出需要怎样的技术支撑，再从我们已有的知识储备搜刮出可以有哪些解决方案，最后针对这些解决方案，快速有效地细化出落地方案，逐渐找到透过现象看本质的方法论。

具体会分为 4 个模块：

- 基础篇

用一张 Dubbo 的总体架构图，把日常的开发流程串联起来，勾勒起你对 Dubbo 数十个基础知识点的整体印象；在此基础上，用视频形式带你统一梳理 Dubbo 日常开发必须掌握的基础特性，查漏补缺。

如果你是初学者，掌握好基础篇就能应付日常开发实践了。

- 特色篇

以真实案例为背景，逐步分析并推导出需要的技术手段，带你灵活应用框架中的高级特性来解决实际问题。深入理解高级特性外，也有助于你利用高级特性开发出比较通用的产品功能。

如果你是有 Dubbo 基础的开发者，掌握特色篇基本上可以在实战中横着走了。

- 源码篇

通过源码的学习，达到知其然知其所以然。我们会站在框架设计者的角度，体会 Dubbo 框架每个机制设计的亮点所在，锻炼你对 Dubbo 掌握的纵向深度。如果你对自己有更高要求，掌握了源码篇，你可以称得上 Dubbo 框架高手了。

- 拓展篇

在这里我们将针对一些工作中的实际诉求，分析出需要的功能解决方案，并且从前面已学的知识点中，提取关键要素尝试解决，在应用中进一步提升你对 Dubbo 的理解，晋级宗师。

![image-20250226224621979](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202502262246060.png)

课程的代码仓库链接： https://gitee.com/ylimhhmily/GeekDubbo3Tutorial

# ==基础篇==

# 01｜温故知新：Dubbo基础知识你掌握得如何？

**总体架构**

Dubbo 的主要节点角色有五个：

- Container：服务运行容器，为服务的稳定运行提供运行环境。
- Provider：提供方，暴露接口提供服务。
- Consumer：消费方，调用已暴露的接口。
- Registry：注册中心，管理注册的服务与接口。
- Monitor：监控中心，统计服务调用次数和调用时间。

我们画一张 Dubbo 的总体架构示意图，你可以清楚地看到每个角色大致的交互方式：

![image-20250301220000342](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503012200664.png)

对于一个 Dubbo 项目来说，我们首先会从提供方进行工程创建（第 ① 步），并启动工程（第 ② 步）来进行服务注册（第 ③ 步），接着会进行消费方的工程创建（第 ④ 步）并启动订阅服务（第 ⑤ 步）来发起调用（第 ⑥ 步），到这里，消费方就能顺利调用提供方了。

消费方在运行的过程中，会感知注册中心的服务节点变更（第 ⑦ 步），最后消费方和提供方将调用的结果指标同步至监控中心（第 ⑧⑨ 步）。

在这样的完整流程中，每个角色在 Dubbo 架构体系中具体起到了什么样的作用？每一步我们有哪些操作注意点呢？

**1、Container 服务运行容器**

首先，提供方、消费方的正常运转，离不开一个大前提——运行的环境。首先，提供方、消费方的正常运转，离不开一个大前提——运行的环境。

**2、Provider 提供方**

有了 Container 为服务的稳定运行提供环境后，我们就可以开始新建工程了。

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

**3、Consumer 消费方**

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

这是因为 Dubbo 默认使用的是 loadbalance="random" 随机类型的负载均衡策略，为了尽可能雨露均沾调用到提供方各个节点，你可以继续设置 loadbalance="roundrobin" 来进行轮询调用，比如：

```xml
<!-- 引用远程服务 -->
<dubbo:reference id="demoFacade" loadbalance="roundrobin"
        interface="com.hmilyylimh.cloud.facade.demo.DemoFacade">
</dubbo:reference>
```

**4、Registry 注册中心**

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

首先拦截识别异步，当拦截处发现有异步化模式的变量，从上下文对象中取出异步化结果并返回。

![image-20250303225030458](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503032250568.png)

这里要注意一点，凡是异步问题，都需要考虑当前线程如何获取其他线程内数据，所以这里我们要思考：如果异步化处理有点耗时，拦截处从异步化结果中取不到结果该怎么办呢？不停轮询等待吗？还是要作何处理呢？

相信熟悉 JDK 的你已经想到了，非 java.util.concurrent.Future 莫属，这是 Java 1.5 引入的用于异步结果的获取，当异步执行结束之后，结果将会保存在 Future 当中。接下来就一起来看看该如何改造 queryOrderById 这个方法：

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

们追踪源码的调用流程，可以发现最终是通过 CAS 原子性的方式创建了一个 java.util.concurrent.CompletableFuture 对象，这个对象就存储在当前的上下文 org.apache.dubbo.rpc.RpcContextAttachment 对象中。

然后，需要在异步线程中同步父线程的上下文信息：

![image-20250303223702215](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503032237302.png)

可以看到，Dubbo 框架，也是用的 asyncContext 同步不同线程间的信息，也就是信息的拷贝，只不过这个拷贝需要利用到异步模式开启之后的返回对象 asyncContext。

因为 asyncContext 富含上下文信息，只需要把这个所谓的 asyncContext 对象传入到子线程中，然后将 asyncContext 中的上下文信息充分拷贝到子线程中，这样，子线程处理所需要的任何信息就不会因为开启了异步化处理而缺失。

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

**异步应用场景**

Dubbo 的异步实现原理，相信你已经非常清楚了，那哪些应用场景可以考虑异步呢？

- 第一，我们定义了线程池，你可能会认为定义线程池的目的就是为了异步化操作，其实不是，因为异步化的操作会使 queryOrderById 方法立马返回，也就是说，异步化耗时的操作并没有在 queryOrderById 方法所在线程中继续占用资源，而是在新开辟的线程池中占用资源。

  所以对于一些 IO 耗时的操作，比较影响客户体验和使用性能的一些地方，我们是可以采用异步处理的。

- 其次，因为 queryOrderById 开启异步操作后就立马返回了，queryOrderById 所在的线程和异步线程没有太多瓜葛，异步线程的完成与否，不太影响 queryOrderById 的返回操作。

  所以，若某段业务逻辑开启异步执行后不太影响主线程的原有业务逻辑，也是可以考虑采取异步处理的。

- 最后，在 queryOrderById 这段简单的逻辑中，只开启了一个异步化的操作，站在时序的角度上看，queryOrderById 方法返回了，但是异步化的逻辑还在慢慢执行着，完全对时序的先后顺序没有严格要求。所以，时序上没有严格要求的业务逻辑，也是可以采用异步处理的。

**思考**

问：asyncContext.write(resultInfo); 这里将resultInfo 写入 Future 之后，Dubbo框架什么时候调用Future.get 获取计算结果？

答：asyncContext.write(resultInfo); 执行之后是将结果写入到了 Future 当中，但是还有另外一个底层在调用这个 Future#get 的结果，这个调用的地方就是在【org.apache.dubbo.remoting.exchange.support.header.HeaderExchangeHandler#handleRequest】方法中的【handler.reply(channel, msg);】代码处。

【handler.reply(channel, msg);】返回的对象就是 Future 对象，然后调用 Future 对象的 whenComplete 方法，调用完后若没有结果就会等待，有结果的话就会立马进入 whenComplete 方法的回调逻辑中。

# 03｜隐式传递：如何精准找出一次请求的全部日志？

今天我们继续探索 Dubbo 框架的第二道特色风味，隐式传递。

在我们日常开发工作中，查日志是很常见一环了。实际开发会涉及很多系统，如果出问题的功能调用流程非常复杂，你可能都不确定找到的日志是不是出问题时的日志，也可能只是找到了出问题时日志体系中的小部分，还可能找到一堆与问题毫无关系的日志。比如下面这个复杂调用关系：

![image-20250305220918569](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503052209682.png)

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

**泛化调用**

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

虽然不知道 @DubboReference 注解是怎么做到的，但是我们起码能明白一点，只要通过 @DubboReference 修饰的字段就能拿到实例对象，那接下来就是需要一点耐心的环节了，顺着 @DubboReference 注解的核心实现逻辑探索一下源码：

![image-20250310230950063](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503102309227.png)

最终，我们会发现是通过 ReferenceConfig#get 方法创建了代理对象。

**编码实现**

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
                                @RequestBody String reqBody){
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



# ==源码篇==



# ==拓展篇==

