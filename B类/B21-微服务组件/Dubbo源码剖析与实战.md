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

因为这个变量和当前处理业务的线程息息相关，我们要么借助本地线程 ThreadLocal 来存储，要么借助处理业务的上下文对象来存储。

如果借助本地线程 ThreadLocal 来存储，又会遇到 queryOrderById 所在的线程与 cachedThreadPool 中的线程相互通信的问题。因为 ThreadLocal 存储的内容位于线程私有区域，从代码层面则体现在 java.lang.Thread#threadLocals 这个私有变量上，这也决定了，不同的线程，私有区域是无法相互访问的。

所以这里 **采用上下文对象来存储，那异步化的结果也就毋庸置疑存储在上下文对象中**。

首先拦截识别异步，当拦截处发现有异步化模式的变量，从上下文对象中取出异步化结果并返回。

![image-20250303225030458](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202503032250568.png)

这里要注意一点，凡是异步问题，都需要考虑当前线程如何获取其他线程内数据，所以这里我们要思考：如果异步化处理有点耗时，拦截处从异步化结果中取不到结果该怎么办呢？不停轮询等待吗？还是要作何处理呢？

这个问题抽象一下其实就是：A线程执行到某个环节，需要B线程的执行结果，但是B线程还未执行完，A线程是如何应对的？所以，本质回归到了多线程通信上。

相信熟悉 JDK 的你已经想到了，非 java.util.concurrent.Future 莫属，这是 Java 1.5 引入的用于异步结果的获取，当异步执行结束之后，结果将会保存在 Future 当中。但 java.util.concurrent.Future 是一个接口，我们得找一个它的实现类来用，也就是 java.util.concurrent.CompletableFuture，而且它的 java.util.concurrent.CompletableFuture#get(long timeout, TimeUnit unit) 方法支持传入超时时间，也正好适合我们的场景。

接下来就一起来看看该如何改造 queryOrderById 这个方法：

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

> 异步转同步，提升了 Dubbo 线程的利用率。

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

# ==源码篇==

# 12｜源码框架：框架在源码层面如何体现分层？

从今天起我们进入Dubbo源码的学习。

不过在深入研究底层源码之前，我们得先窥其全貌，站在上帝视角来俯视一番，看看框架在代码层面到底是如何分层搭建的。

**模块流程图**

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
        Map<String, Object> attributes = metadata
        .getAnnotationAttributes(DubboFeignClient.class.getName());
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

代码中 getObject 是我们创建代理对象的核心过程，细心的你可能会发现我们还创建了一个 DubboClientProxy 对象，这个对象放在 `java.lang.reflect.Proxy#newProxyInstance(java.lang.ClassLoader, java.lang.Class<?>[], **java.lang.reflect.InvocationHandler**)` 方法中的第三个参数。

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

> 这样一看，多写一些下游转发代码其实也没什么

# 14｜SPI机制：Dubbo的SPI比JDK的SPI好在哪里？

今天我们来深入研究Dubbo源码的第三篇，SPI 机制。

SPI，英文全称是Service Provider Interface，按每个单词翻译就是：服务提供接口。

**SPI是怎么来的**

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



# 26｜线程池扩展：如何选择Dubbo线程池？



# 27｜协议扩展：如何快速控制应用的上下线？

