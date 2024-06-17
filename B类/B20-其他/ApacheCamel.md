> 参考资料：https://camel.apache.org/manual/index.html

# 一、入门

## 1.1 创建您的第一个项目

### 生成项目

```shell
mvn archetype:generate -B -DarchetypeGroupId=org.apache.camel.archetypes -DarchetypeArtifactId=camel-archetype-java -DarchetypeVersion=3.18.4 -Dpackage=org.apache.camel.learn -DgroupId=org.apache.camel.learn -DartifactId=first-camel-integration -Dversion=1.0.0-SNAPSHOT
```

### 构建和运行项目

您可以运行以下命令来构建项目：

```shell
mvn clean package
```

要运行该项目，您可以运行以下命令：

```shell
mvn camel:run -Dcamel.main.durationMaxMessages=2
```

您刚刚运行的工程使用了两个文件，在项目中的 `target/messages` 目录：

```
target/messages
target/messages/others
target/messages/others/message2.xml
target/messages/uk
target/messages/uk/message1.xml
```

## 1.2 了解项目

您创建的工程实现了一种称为基于内容的路由器的模式。此模式的 Camel 实现允许您实现根据消息内容路由消息的逻辑。

更具体地说，查看工程 `src/data` 目录中 XML 文件的内容。如果元素 `city` 的内容是 London，则它将文件移动到目录 `target/messages/uk` 。否则，它将文件移动到目录 `target/messages/others` 。

为了创建执行此任务的集成，此代码配置一条路由，将地址 `file:src/data?noop=true` 表示的源端点连接到地址 `file:target/messages/uk` 和 `file:target/messages/others`

### ENDPOINT

当我们谈论进程间通信（例如客户端/服务器或微服务）时，我们经常使用术语端点来指代软件实体。端点的一个特征是它可以在某个地址上进行联系。地址本身可以传达端点的附加特征。例如，地址 `host:port` 传达基于 TCP 的通信端点的端口和网络名称。

Camel 为使用多种通信技术实现的端点提供开箱即用的支持。以下是受支持的端点技术的一些示例：

- JMS 队列
- web 服务
- 一份文件（一个应用程序可能会将信息写入文件，然后另一个应用程序可能会读取该文件）
- FTP 服务器
- 一个电子邮件地址（客户端可以向电子邮件地址发送消息，服务器可以读取来自邮件服务器的传入消息）
- POJO

### ROUTES

在基于 Camel 的应用程序中，您可以创建路由。路由用于将源端点连接到目标端点。

“路由”描述了消息从源端点通过某一类型的决策例程（例如过滤器和路由器）到目标端点的逐步移动。

在您创建的项目中，目录 `src/main/java/org/apache/camel/learn` 中应该有 2 个源文件：

- `MainApp.java` ：用于配置和启动应用程序的代码。
- `MyRouteBuilder.java` ：路由的代码。

路由代码：

```java
public class MyRouteBuilder extends RouteBuilder {
    public void configure() {
        from("file:src/data?noop=true")
            .choice()
                .when(xpath("/person/city = 'London'"))
                    .log("UK message")
                    .to("file:target/messages/uk")
                .otherwise()
                    .log("Other message")
                    .to("file:target/messages/others");
    }
}
```

在此路由配置中，我们将地址 `file:src/data?noop=true` 表示的源端点连接到地址 `file:target/messages/uk` 和 `file:target/messages/others` 表示的其他两个端点。在 Camel 中，统一资源标识符 (URI) 表示端点的地址。

**URL、URI 和 URN 的含义**

大多数人都熟悉 URL（统一资源定位符），例如 `http://…` 、 `ftp://…` 、 `\mailto:…:` 。 

URN 是不同“唯一标识符”的包装器，它的语法是 `urn:<scheme-name>:<unique-identifier>` 。 URN 唯一标识资源（即：一本书、人或一件设备）。 URN 本身并不指定资源的位置。

URI（统一资源标识符）是 URL 或 URN。

**端点地址**

在 Camel 中，表示端点地址的 URI 采用以下格式：

```
component:resource[?options]
```

URI 的协议部分表示用于消费或生成数据的组件。 Camel 包含 300 多个组件，允许您的应用程序与许多系统、协议和应用程序进行通信。

以下是 Camel 的有效 URI 的一些示例： `jms:queue:order` 、 `kafka:myTopic?groupId=KafkaConsumerFullIT` 、 `direct:result` 。通过查看这些 URI，我们可以识别它们正在使用 `jms` 、 `kafka` 和 `direct` 组件。

每个组件都有其自己特定的一组功能、约束和要求，我们在使用它们时必须遵守这些功能、约束和要求。 Camel 通过 `resource` 和 `options` 公开它们。资源是什么取决于我们正在使用的组件。例如，在文件组件中，资源是一个目录；在Kafka组件中，资源就是主题； 

### 添加路由并运行应用程序

在执行路由之前，需要对其进行配置并添加到CamelContext中。

```java
public class MainApp {
    public static void main(String... args) throws Exception {
        Main main = new Main();
        main.configure().addRoutesBuilder(new MyRouteBuilder());
        main.run(args);
    }
}
```

## 1.3 基本概念和术语

### CamelContext

CamelContext 是运行时系统，它将我们迄今为止介绍的所有基本概念（路由、端点、组件等）结合在一起。

这个上下文对象代表Camel运行时系统。通常，应用程序中有一个 CamelContext 实例。

您没有在创建的示例应用程序中操作 CamelContext，因为 Main 组件为您管理它。随着您的集成变得越来越复杂，您最终将需要对其进行操作。典型的应用程序执行以下步骤：

- 创建上下文对象
- 添加端点
- 将路由添加到上下文对象以连接端点
- 对上下文对象调用 `start()` 操作
- 最终调用上下文对象上的 `stop()` 操作

### Components

组件用于将路由连接到各种外部系统和服务。 Camel 附带大量内置组件，提供与各种技术和协议的连接，例如 HTTP、JMS、文件等。如果内置组件不能满足您的需求，您还可以创建自定义组件。

### Message与Exchange

`Message` 接口提供单个消息的抽象，例如请求、回复或异常消息。`Message` 接口的公共API提供了getter和setter方法。您可以使用它们来访问消息的消息 ID、正文和各个标头字段。

`Exchange` 接口提供了消息交换的抽象，是请求消息及其相应的回复或异常消息。在 Camel 中，请求、回复和异常消息被称为调入、调出和故障消息。

### Processor

处理器用于实现消息交换的使用者或实现消息转换器以及其他用例。在编写路由时，您可以使用处理器在 Exchange 上执行更复杂的逻辑。例如：

```java
public void process(Exchange exchange) {
    final String body = exchange.getMessage().getBody(String.class);
    System.out.println(“Updated body: “ + body.replace(“city”, “county”));

    // ... more code here
}

public void configure() {
    from(“file:src/data?noop=true”)
        .process(this::process);
}
```

`process()` 方法的参数是 `Exchange` 而不是 `Message` 。这提供了灵活性。例如，要获取输入消息并对其进行处理，此方法的实现最初可能会调用方法 `exchange.getIn()` 。如果处理过程中发生错误，那么它可以调用 `exchange.setException()` 方法。

Camel 库中的许多类以支持 E.I.P. 中的设计模式的方式实现 `Processor` 接口。

- `ChoiceProcessor` 实现消息路由器模式，即它使用级联 if-then-else 语句将消息从输入队列路由到多个输出队列之一。
- `FilterProcessor` 类丢弃不满足指定谓词（即条件）的消息。

### 路由、路由构建器和 JAVA DSL

Camel为应用程序开发人员提供了三种指定路由的方法：

- 使用 XML
- 使用 YAML
- 使用 Java 领域特定语言 (DSL)











