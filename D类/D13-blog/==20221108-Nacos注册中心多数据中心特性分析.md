# 多数据中心特性分析

多个网络互通的`Region`之间服务共享,打破`Region`之间的服务调用限制。

![image.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/TB1Mo6yJ4jaK1RjSZKzXXXVwXXa-1136-798.png)

官方没有对多数据中心进行灰度支持。自己实现增加调用复杂度，因此使用网关调用较为合适。

![image-20221108151942825](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221108151942825.png)

## 为什么跨注册中心调用复杂？

### 复杂度来源：调用方如何选择环境？

![image-20221108152007147](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221108152007147.png)

这种架构将复杂度抛给了调用方，当 Region 2 灰度切换时，及时通知调用方会存在问题。

### 结合网关的调用方式

![image-20221108152030387](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221108152030387.png)

相较而言，通过网关的反向代理会简单很多。不同 Region 通常是由不同的团队维护，Region2 团队只需在网关层作流量切换，Region 1无感知。

# 注册中心技术选型

一、现状

- 开思电商：Eureka、K8S
- 一号车间：Zookeeper
- 小狮：K8S

二、技术痛点

- 跨团队服务调用困难
- 新服务发布网关需重启
- Eureka 线上问题

各注册中心对比

|        | 对比项             | Nacos                                                        | Eureka      | Zookeeper  | K8S                    |
| ------ | ------------------ | ------------------------------------------------------------ | ----------- | ---------- | ---------------------- |
| 可用性 | **一致性协议**     | CP+AP                                                        | AP          | CP         | CP                     |
| 可用性 | 高可用部署         | 支持                                                         | 支持        | 支持       | 支持                   |
|        | **健康检查**       | TCP/HTTP/MYSQL/Client                                        | Beat Client | Keep Alive | 活性性探针、就绪性探针 |
|        | **手动注册**       | 支持                                                         | 不支持      | 不支持     | 不支持                 |
|        | 负载均衡策略       | 权重/metadata/Selector                                       | Ribbon      | —          | 轮询/SessionAffinity   |
|        | 自动注销实例       | 支持                                                         | 支持        | 支持       | 支持                   |
|        | 访问协议           | HTTP                                                         | HTTP        | TCP        | HTTP                   |
|        | SpringCloud集成    | 支持                                                         | 支持        | 不支持     | 支持                   |
|        | Dubbo集成          | 支持                                                         | 不支持      | 支持       | 支持                   |
| 运维   | **多数据中心**     | 支持（[官网资料](https://nacos.io/zh-cn/docs/nacos-sync.html)） | 支持        | 不支持     | 不支持                 |
| 运维   | **跨注册中心同步** | 支持                                                         | 不支持      | 不支持     | 不支持                 |
| 运维   | 监控支持           | 支持                                                         | 支持        | 支持       | 支持                   |
| 运维   | K8S集成            | 支持（[官网资料](https://nacos.io/zh-cn/docs/use-nacos-with-kubernetes.html)） | 不支持      | 不支持     | 支持                   |

三、分析

1、Nacos 支持 CP 和 AP 模式切换，比 Eureka 和 Zookeeper 更加灵活。

2、Eureka 支持 AP，虽然有数据一致性的牺牲，但是相比 Zookeeper，保障了服务高可用，不会出现长时间服务瘫痪。

3、Eureka 在 2.0 以后宣布闭源，后续使用出现问题要自己承担，而 Nacos 属于 Alibaba 无服务生态，发展良好。

四、结论

推荐使用Nacos

|           | 选择的原因                           | 不选择的原因             |
| --------- | ------------------------------------ | ------------------------ |
| Zookeeper |                                      | 不支持高可用、业务入侵大 |
| Nacos     | 统一技术栈、支持配置中心、运维成本低 |                          |
| K8S       |                                      | 资料少                   |
| Eureka    |                                      | Eureka2.x闭源            |

> [主流微服务注册中心浅析和对比](https://developer.aliyun.com/article/698930)
>
> [微服务下的注册中心如何选择](https://www.cnblogs.com/wtzbk/p/14071040.html)
>
> [Nacos2.0.0-ALPHA2 服务发现性能测试报告](https://nacos.io/zh-cn/docs/nacos2-naming-benchmark.html)
>
> metadata：https://nacos.io/zh-cn/docs/concepts.html
>
> Selector：https://www.jianshu.com/p/ae5dd5c63ad0

# Eureka 的一次线上问题

eureka java.net.SocketTimeoutException: Read timed out：147次

![image-20221108152713648](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221108152713648.png)

完整报错如下：

```
2021-12-04 14:22:10,101:ERROR [,] TaskBatchingWorker-target_deploy-eureka-server-0.service-eureka-server.infra.svc.cluster.local-5 (ReplicationTaskProcessor.java:96) - It seems to be a socket read timeout exception, it will retry later. if it continues to happen and some eureka node occupied all the cpu time, you should set property 'eureka.server.peer-node-read-timeout-ms' to a bigger value
com.sun.jersey.api.client.ClientHandlerException: java.net.SocketTimeoutException: Read timed out
	at com.sun.jersey.client.apache4.ApacheHttpClient4Handler.handle(ApacheHttpClient4Handler.java:187) ~[jersey-apache-client4-1.19.1.jar!/:1.19.1]
	at com.netflix.eureka.cluster.DynamicGZIPContentEncodingFilter.handle(DynamicGZIPContentEncodingFilter.java:48) ~[eureka-core-1.9.8.jar!/:1.9.8]
	at com.netflix.discovery.EurekaIdentityHeaderFilter.handle(EurekaIdentityHeaderFilter.java:27) ~[eureka-client-1.9.8.jar!/:1.9.8]
	at com.sun.jersey.api.client.Client.handle(Client.java:652) ~[jersey-client-1.19.1.jar!/:1.19.1]
	at com.sun.jersey.api.client.WebResource.handle(WebResource.java:682) ~[jersey-client-1.19.1.jar!/:1.19.1]
	at com.sun.jersey.api.client.WebResource.access$200(WebResource.java:74) ~[jersey-client-1.19.1.jar!/:1.19.1]
	at com.sun.jersey.api.client.WebResource$Builder.post(WebResource.java:570) ~[jersey-client-1.19.1.jar!/:1.19.1]
	at com.netflix.eureka.transport.JerseyReplicationClient.submitBatchUpdates(JerseyReplicationClient.java:116) ~[eureka-core-1.9.8.jar!/:1.9.8]
	at com.netflix.eureka.cluster.ReplicationTaskProcessor.process(ReplicationTaskProcessor.java:80) [eureka-core-1.9.8.jar!/:1.9.8]
	at com.netflix.eureka.util.batcher.TaskExecutors$BatchWorkerRunnable.run(TaskExecutors.java:193) [eureka-core-1.9.8.jar!/:1.9.8]
	at java.lang.Thread.run(Thread.java:748) [?:1.8.0_202]
Caused by: java.net.SocketTimeoutException: Read timed out
	at java.net.SocketInputStream.socketRead0(Native Method) ~[?:1.8.0_202]
	at java.net.SocketInputStream.socketRead(SocketInputStream.java:116) ~[?:1.8.0_202]
	at java.net.SocketInputStream.read(SocketInputStream.java:171) ~[?:1.8.0_202]
	at java.net.SocketInputStream.read(SocketInputStream.java:141) ~[?:1.8.0_202]
	at org.apache.http.impl.io.AbstractSessionInputBuffer.fillBuffer(AbstractSessionInputBuffer.java:161) ~[httpcore-4.4.11.jar!/:4.4.11]
	at org.apache.http.impl.io.SocketInputBuffer.fillBuffer(SocketInputBuffer.java:82) ~[httpcore-4.4.11.jar!/:4.4.11]
	at org.apache.http.impl.io.AbstractSessionInputBuffer.readLine(AbstractSessionInputBuffer.java:276) ~[httpcore-4.4.11.jar!/:4.4.11]
	at org.apache.http.impl.conn.DefaultHttpResponseParser.parseHead(DefaultHttpResponseParser.java:138) ~[httpclient-4.5.7.jar!/:4.5.7]
	at org.apache.http.impl.conn.DefaultHttpResponseParser.parseHead(DefaultHttpResponseParser.java:56) ~[httpclient-4.5.7.jar!/:4.5.7]
	at org.apache.http.impl.io.AbstractMessageParser.parse(AbstractMessageParser.java:259) ~[httpcore-4.4.11.jar!/:4.4.11]
	at org.apache.http.impl.AbstractHttpClientConnection.receiveResponseHeader(AbstractHttpClientConnection.java:294) ~[httpcore-4.4.11.jar!/:4.4.11]
	at org.apache.http.impl.conn.DefaultClientConnection.receiveResponseHeader(DefaultClientConnection.java:257) ~[httpclient-4.5.7.jar!/:4.5.7]
	at org.apache.http.impl.conn.AbstractClientConnAdapter.receiveResponseHeader(AbstractClientConnAdapter.java:230) ~[httpclient-4.5.7.jar!/:4.5.7]
	at org.apache.http.protocol.HttpRequestExecutor.doReceiveResponse(HttpRequestExecutor.java:273) ~[httpcore-4.4.11.jar!/:4.4.11]
	at org.apache.http.protocol.HttpRequestExecutor.execute(HttpRequestExecutor.java:125) ~[httpcore-4.4.11.jar!/:4.4.11]
	at org.apache.http.impl.client.DefaultRequestDirector.tryExecute(DefaultRequestDirector.java:679) ~[httpclient-4.5.7.jar!/:4.5.7]
	at org.apache.http.impl.client.DefaultRequestDirector.execute(DefaultRequestDirector.java:481) ~[httpclient-4.5.7.jar!/:4.5.7]
	at org.apache.http.impl.client.AbstractHttpClient.doExecute(AbstractHttpClient.java:835) ~[httpclient-4.5.7.jar!/:4.5.7]
	at org.apache.http.impl.client.CloseableHttpClient.execute(CloseableHttpClient.java:118) ~[httpclient-4.5.7.jar!/:4.5.7]
	at org.apache.http.impl.client.CloseableHttpClient.execute(CloseableHttpClient.java:56) ~[httpclient-4.5.7.jar!/:4.5.7]
	at com.sun.jersey.client.apache4.ApacheHttpClient4Handler.handle(ApacheHttpClient4Handler.java:173) ~[jersey-apache-client4-1.19.1.jar!/:1.19.1]
	... 10 more

```

参考资料：https://github.com/zowe/api-layer/issues/282

解决方案：调整`eureka.server.peer-node-read-timeout-ms`配置。

```
env:
  - name: eureka.client.serviceUrl.defaultZone
    value: >-	http://deploy-eureka-server-0.service-eureka-server.infra.svc.cluster.local:8761/eureka,http://deploy-eureka-server-1.service-eureka-server.infra.svc.cluster.local:8761/eureka,http://deploy-eureka-server-2.service-eureka-server.infra.svc.cluster.local:8761/eureka
  - name: aliyun_logs_infra-logs
    value: /opt/logs/stdout.log
  - name: MALLOC_ARENA_MAX
    value: '1'
  - name: eureka.server.peer-node-read-timeout-ms
    value: '1500'
```

