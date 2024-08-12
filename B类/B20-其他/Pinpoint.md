> 参考资料：
>
> - https://pinpoint-apm.gitbook.io/pinpoint

# 一、插件开发指南

## 1.1 追踪数据

在 Pinpoint 中，一个事务由一组`Spans`组成。每个`Span`代表事务已经历的单个逻辑节点的踪迹。

为了帮助理解，我们假设有一个如下所示的系统。前端服务接收用户的请求，然后将请求发送到后端服务，后端服务查询数据库。

![image-20240812224605691](../../../../Library/Application Support/typora-user-images/image-20240812224605691.png)

当请求到达前端服务时，Pinpoint Agent 会生成一个新的事务 ID 并用它创建一个`Span` 。为了处理该请求，前端服务调用后端服务。此时，Pinpoint Agent 将事务 ID（加上一些用于传播的其他值）注入到调用消息中。当后端服务收到此消息时，它会从消息中提取事务 ID（以及其他值）并使用它们创建一个新的`Span` 。结果，单个事务中的所有`Spans`共享相同的事务 id。

`Span`记录重要的方法调用及其相关数据（参数、返回值等），然后将它们封装为`SpanEvents`。 `Span`及其每个`SpanEvents`代表一个方法调用。

`Span`和`SpanEvent`有很多字段，但其中大部分由 Pinpoint Agent 在内部处理，大多数插件开发人员不需要担心它们。插件开发人员必须处理的字段和数据将在本指南中列出。

## 1.2 Pinpoint 插件结构

Pinpoint 插件由 type-provider.yml 和`ProfilerPlugin`组成。 type-provider.yml 定义了`ServiceTypes`和`AnnotationKeys` ，并将它们提供给 Pinpoint Agent、Web 和 Collector。 Pinpoint Agent 使用`ProfilerPlugin`来转换目标类以记录跟踪数据。

插件以 jar 文件的形式部署。这些 jar 文件打包在 Agent 的插件目录下，而 Collector 和 Web 将它们部署在 WEB-INF/lib 下。启动时，Pinpoint Agent、Collector 和 Web 会循环访问每个插件，解析 type-provider.yml，并使用`ServiceLoader`从以下位置加载`ProfilerPlugin`实现：

- META-INF/pinpoint/type-provider.yml
- META-INF/services/com.navercorp.pinpoint.bootstrap.plugin.ProfilerPlugin

这是一个[模板插件项目，](https://github.com/pinpoint-apm/pinpoint-plugin-template)您可以使用它来开始创建自己的插件。

### 1、type-provider.yml

 type-provider.yml 定义了`ServiceTypes`和`AnnotationKeys`，其格式如下。

```yaml
serviceTypes:
    - code: <short>
      name: <String>
      # May be omitted, defaulting to the same value as name.
      desc: <String>
      # 属性里的所有值都默认是false
      property:
          # 此Span或SpanEvent调用远程节点，但无法使用Pinpoint跟踪目标节点
          terminal: <boolean>
          # 此Span或SpanEvent从消息队列消费消息或向消息队列生产消息
          queue: <boolean>
          # Pinpoint Collector应该收集此Span或SpanEvent的执行时间统计信息
          recordStatistics: <boolean>
          # 此Span或SpanEvent记录destination id，且远程服务器不可追踪。
          includeDestinationId: <boolean>
          # 该服务可能会也可能不会在接入 Pinpoint-Agent（例如 Elasticsearch 客户端）
          alias: <boolean>
      # May be omitted
      matcher: 
          # Any one of 'args', 'exact', 'none'
          type: <String>
          # Annotation key code - required only if type is 'exact'
          code: <int>

annotationKeys:
    - code: <int>  # 必须是唯一的
      name: <String>
      # 属性里的所有值都默认是false
      property:
          # 在事务调用树中显示此注解
          viewInRecordSet: <boolean>
```

此处定义的`ServiceType`和`AnnotationKey`在 Agent 加载时实例化，并且可以使用`ServiceTypeProvider`和`AnnotationKeyProvider`获取，如下所示。

```java
// get by ServiceType code
ServiceType serviceType = ServiceTypeProvider.getByCode(1000);
// get by ServiceType name
ServiceType serviceType = ServiceTypeProvider.getByName("NAME");
// AnnotationKey
AnnotationKey annotationKey = AnnotationKeyProvider.getByCode("100");
```

- ServiceType

每个`Span`和`SpanEvent`都包含一个`ServiceType` 。 `ServiceType`表示跟踪的方法属于哪个库，以及应如何处理`Span`和`SpanEvent` 。

下表显示了`ServiceType`的属性。

| 属性       | 描述                               |
| :--------- | :--------------------------------- |
| name       | `ServiceType`的名称。必须是唯一的  |
| code       | `ServiceType`的 code。必须是唯一的 |
| desc       | 描述                               |
| properties | 特性                               |

`ServiceType`的 code 不同类别有不同的取值范围。

| 类别         | range 范围  |
| :----------- | :---------- |
| 内部使用     | 0 ~ 999     |
| 服务器       | 1000 ~ 1999 |
| 数据库客户端 | 2000 ~ 2999 |
| 缓存客户端   | 8000 ~ 8999 |
| RPC客户端    | 9000 ~ 9999 |
| 其他         | 5000 ~ 7999 |

`ServiceType`的 code 必须是唯一的。因此，如果您正在编写一个公开的插件，则必须联系 Pinpoint 开发团队来获取分配的`ServiceType`的 code。如果您的插件供私人使用，您可以从下表中自由选择`ServiceType`代码的值。

您可以[在此处](https://github.com/pinpoint-apm/pinpoint-plugin-sample/blob/master/plugins/sample/src/main/resources/META-INF/pinpoint/type-provider.yml)找到`type-provider.yml`的示例。

### 2、ProfilerPlugin

`ProfilerPlugin`是用来收集跟踪数据的。按以下步骤启动：

1. Pinpoint Agent 在 JVM 启动时启动。
2. Pinpoint Agent 加载`plugin`目录下的所有插件。
3. Pinpoint Agent 为每个加载的插件调用`ProfilerPlugin.setup(ProfilerPluginSetupContext)` 。
4. 在`setup`方法中，插件向所有要转换的类注册一个`TransformerCallback` 。
5. 目标应用程序启动。
6. 每次加载类时，Pinpoint Agent 都会查找注册到该类的`TransformerCallback` 。
7. 如果注册了`TransformerCallback` ，代理将调用它的`doInTransform`方法。
8. `TransformerCallback`修改目标类的字节代码。（例如添加拦截器、添加字段等）
9. 修改后的字节码返回到 JVM，并用返回的字节码加载该类。
10. 应用程序继续运行。
11. 当调用修改的方法时，将调用注入的拦截器的`before`和`after`方法。
12. 拦截器记录跟踪数据。

编写插件时要考虑的最重要的一点是：

1) 弄清楚有哪些感兴趣的方法以保证跟踪；
2) 注入拦截器来实际跟踪这些方法。

这些拦截器用于在将跟踪数据发送到 Collector 之前提取、存储和传递跟踪数据。拦截器甚至可以相互合作，共享上下文。插件还可以通过向目标类添加 getter 甚至自定义字段来帮助跟踪，以便拦截器可以在执行期间访问它们。

[Pinpoint 插件示例向](https://github.com/pinpoint-apm/pinpoint-plugin-sample)您展示了`TransformerCallback`如何修改类以及注入的拦截器如何跟踪方法。

## 1.3 插件集成测试

## 1.4 添加图片

如果您正在为应用程序开发插件，则需要添加图像，以便服务地图可以渲染相应的节点。插件 jar 本身无法提供这些图像文件，目前，您必须手动将图像文件添加到 Web 模块。

