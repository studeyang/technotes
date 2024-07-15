> 参考资料：https://shardingsphere.apache.org/elasticjob/current/cn/overview/

# 一、概况

## 1.1 简介

ElasticJob 定位为轻量级无中心化解决方案，使用 jar 的形式提供分布式任务协调服务（下文统称为“作业服务器”）。

ElasticJob 没有作业调度中心，各个作业服务器在到达相应时间点时各自触发调度。

![image-20240703223744793](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407032237856.png)

## 1.2 概念

ElasticJob 系统有三个角色：作业服务器，注册中心，主作业服务器。

注册中心仅用于作业注册和监控信息的存储；主作业服务器仅用于处理分片和清理分片等功能。

### 分片

任务执行时，会将一个任务拆分为多个独立的 Task 任务项，然后由分布式的任务服务器分别执行某一个或几个分片项。

举例说明，如果作业分为 4 片，用两台服务器执行，则每个服务器分到 2 片，分别负责作业的 50% 的负载，如下图所示。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407032257259.png" alt="image-20240703225714203" style="zoom:50%;" />

### 分片项

分片项为数字，始于 0 而终于分片总数减 1，上图中 Task 0 ~ Task 3。

ElasticJob 将分片项分配至各个运行中的作业服务器，开发者需要自行处理分片项与业务的对应关系。

回到上面的 Job 示例，展示了 3 个分片项的执行过程：

```java
public class MyJob implements SimpleJob {
    
    @Override
    public void execute(ShardingContext context) {
        switch (context.getShardingItem()) {
            case 0: 
                // do something by sharding item 0
                break;
            case 1: 
                // do something by sharding item 1
                break;
            case 2: 
                // do something by sharding item 2
                break;
            // case n: ...
        }
    }
}
```

### 个性化分片参数

个性化参数可以和分片项匹配对应关系，用于将分片项的数字转换为更加可读的业务代码。

通过如下方式来设定分片参数：

```java
JobConfiguration jobConfig = JobConfiguration.newBuilder("myJob", 3)
    .cron("0/5 * * * * ?")
    .shardingItemParameters("0=Beijing,1=Shanghai,2=Guangzhou")
    .build();
```

# 二、功能

ElasticJob 的作业类型有 class 和 type 两种类型。class 的作业类型有Simple、Dataflow 这两种，type 的作业类型有 Script、HTTP 这两种。用户可通过实现 SPI 接口自行扩展作业类型。

## 2.1 简单作业

简单作业需实现 SimpleJob 接口。与 Quartz 原生接口相似，不同的是 ElasticJob 提供了弹性扩缩容和分片等功能。

```java
public class MyElasticJob implements SimpleJob {
    
    @Override
    public void execute(ShardingContext context) {
        // 获取分片总数
        switch (context.getShardingItem()) {
            case 0: 
                // do something by sharding item 0
                break;
            case 1: 
                // do something by sharding item 1
                break;
            case 2: 
                // do something by sharding item 2
                break;
            // case n: ...
        }
    }
}
```

## 2.2 数据流作业

用于处理数据流，需实现 DataflowJob 接口。 该接口提供了 2 个方法，分别用于抓取 (fetchData) 和处理 (processData) 数据。

```java
public class MyElasticJob implements DataflowJob<Foo> {
    
    @Override
    public List<Foo> fetchData(ShardingContext context) {
        // 获取运行在本作业服务器的分片序列号
        switch (context.getShardingItem()) {
            case 0: 
                List<Foo> data = // get data from database by sharding item 0
                return data;
            case 1: 
                List<Foo> data = // get data from database by sharding item 1
                return data;
            case 2: 
                List<Foo> data = // get data from database by sharding item 2
                return data;
            // case n: ...
        }
    }
    
    @Override
    public void processData(ShardingContext shardingContext, List<Foo> data) {
        // process data
        // ...
    }
}
```

可通过属性配置 `streaming.process` 开启或关闭流式处理。

如果开启流式处理，则作业只有在 fetchData 方法的返回值为 null 或集合容量为空时，才停止抓取，否则作业将一直运行下去； 如果关闭流式处理，则作业只会在每次作业执行过程中执行一次 fetchData 和 processData 方法，随即完成本次作业。

如果采用流式作业处理方式，建议 processData 在处理数据后更新其状态，避免 fetchData 再次抓取到，从而使得作业永不停止。

## 2.3 脚本作业

支持 shell，python，perl 等所有类型脚本。可通过属性配置 `script.command.line` 配置待执行脚本，无需编码。 执行脚本路径可包含参数，参数传递完毕后，作业框架会自动追加最后一个参数为作业运行时信息。

例如如下脚本：

```shell
#!/bin/bash
echo sharding execution context is $*
```

作业运行时将输出：

```
sharding execution context is {"jobName":"scriptElasticDemoJob","shardingTotalCount":10,"jobParameter":"","shardingItem":0,"shardingParameter":"A"}
```

## 2.4 HTTP作业

（3.0.0-beta 提供）

可通过属性配置`http.url`,`http.method`,`http.data`等配置待请求的http信息。 分片信息以 Header 形式传递，key 为`shardingContext`，值为 json 格式。

```java
public class HttpJobMain {
    
    public static void main(String[] args) {
        
        new ScheduleJobBootstrap(regCenter, "HTTP", JobConfiguration.newBuilder("javaHttpJob", 1)
                .setProperty(HttpJobProperties.URI_KEY, "http://xxx.com/execute")
                .setProperty(HttpJobProperties.METHOD_KEY, "POST")
                .setProperty(HttpJobProperties.DATA_KEY, "source=ejob")
                .cron("0/5 * * * * ?").shardingItemParameters("0=Beijing").build()).schedule();
    }
}
```

HTTP 接口定义如下。

```java
@Controller
@Slf4j
public class HttpJobController {
    
    @RequestMapping(path = "/execute", method = RequestMethod.POST)
    public void execute(String source, @RequestHeader String shardingContext) {
        log.info("execute from source : {}, shardingContext : {}", source, shardingContext);
    }
}
```

execute 接口将输出：

```
execute from source : ejob, shardingContext : {"jobName":"scriptElasticDemoJob","shardingTotalCount":3,"jobParameter":"","shardingItem":0,"shardingParameter":"Beijing"}
```

## 2.5 失效转移

ElasticJob 不会在本次执行过程中进行重新分片，而是等待下次调度之前才开启重新分片流程。 当作业执行过程中服务器宕机，失效转移允许将该次未完成的任务在另一作业节点上补偿执行。

举例说明，若作业以每小时为间隔执行，每次执行耗时 30 分钟。如下如图所示。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407092346004.png" alt="定时作业" style="zoom:50%;" />

图中表示作业分别于 12:00，13:00 和 14:00 执行。图中显示的当前时间点为 13:00 的作业执行中。

如果作业的其中一个分片服务器在 13:10 的时候宕机，那么剩余的 20 分钟应该处理的业务未得到执行，并且需要在 14:00 时才能再次开始执行下一次作业。 也就是说，在不开启失效转移的情况下，位于该分片的作业有 50 分钟空档期。如下如图所示。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407092346631.png" alt="作业宕机" style="zoom:50%;" />

在开启失效转移功能之后，ElasticJob 的其他服务器能够在感知到宕机的作业服务器之后，补偿执行该分片作业。如下图所示。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407092346006.png" alt="补偿执行" style="zoom:50%;" />

在资源充足的情况下，作业仍然能够在 13:30 完成执行。

### 执行机制

作业服务在本次任务执行结束后，会向注册中心问询待执行的失效转移分片项，如果有，则开始补偿执行。 也称为异步执行。

当其他服务器感知到有失效转移的作业需要处理时，且该作业服务器已经完成了本次任务，则会实时的拉取待失效转移的分片项，并开始补偿执行。 也称为实时执行。

### 适用场景

在一次运行耗时较长且间隔较长的作业场景，失效转移是提升作业运行实时性的有效手段；

对于间隔较短的作业，会产生大量与注册中心的网络通信，对集群的性能产生影响。 而且间隔较短的作业并未见得关注单次作业的实时性，可以通过下次作业执行的重分片使所有的分片正确执行，因此不建议短间隔作业开启失效转移。

## 2.6 错过任务重执行

ElasticJob 不允许作业在同一时间内叠加执行。 当作业的执行时长超过其运行间隔，错过任务重执行能够保证作业在完成上次的任务后继续执行逾期的作业。

举例说明，若作业以每小时为间隔执行，每次执行耗时 30 分钟。如下如图所示。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407092340427.png" alt="定时作业" style="zoom:50%;" />

图中表示作业分别于 12:00，13:00 和 14:00 执行。图中显示的当前时间点为 13:00 的作业执行中。

如果 12：00 开始执行的作业在 13:10 才执行完毕，那么本该由 13:00 触发的作业则错过了触发时间，需要等待至 14:00 的下次作业触发。 如下如图所示。

![image-20240711232912676](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407112329820.png)

在开启错过任务重执行功能之后，ElasticJob 将会在上次作业执行完毕后，立刻触发执行错过的作业。如下图所示。

![image-20240711232924561](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407112329651.png)

在 13：00 和 14:00 之间错过的作业将会重新执行。

# 三、快速入门

## 3.1 引入 Maven 依赖

```xml
<dependency>
    <groupId>org.apache.shardingsphere.elasticjob</groupId>
    <artifactId>elasticjob-bootstrap</artifactId>
    <version>${latest.release.version}</version>
</dependency>
```

## 3.2 作业开发

```java
public class MyJob implements SimpleJob {
    
    @Override
    public void execute(ShardingContext context) {
        switch (context.getShardingItem()) {
            case 0: 
                // do something by sharding item 0
                break;
            case 1: 
                // do something by sharding item 1
                break;
            case 2: 
                // do something by sharding item 2
                break;
            // case n: ...
        }
    }
}
```

## 3.3 作业配置

```java
JobConfiguration jobConfig = JobConfiguration.newBuilder("MyJob", 3)
        .cron("0/5 * * * * ?").build();
```

## 3.4 作业调度

```java
public class MyJobDemo {
    
    public static void main(String[] args) {
        new ScheduleJobBootstrap(createRegistryCenter(), new MyJob(), createJobConfiguration()).schedule();
    }
    
    private static CoordinatorRegistryCenter createRegistryCenter() {
        CoordinatorRegistryCenter regCenter = new ZookeeperRegistryCenter(new ZookeeperConfiguration("zk_host:2181", "my-job"));
        regCenter.init();
        return regCenter;
    }
    
    private static JobConfiguration createJobConfiguration() {
        // 创建作业配置
    }
}

```

# 四、实现原理

## 4.1 高可用

当作业服务器在运行中宕机时，注册中心会通过临时节点感知，并将在下次运行时将分片转移至仍存活的服务器，以达到作业高可用的效果。 

本次由于服务器宕机而未执行完的作业，则可以通过失效转移的方式继续执行。如下图所示。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407032313345.png" alt="image-20240703231303299" style="zoom:50%;" />

### 主服务器选举

主服务器一旦下线，则重新触发选举，选举过程中会阻塞任务执行，只有主服务器选举完成，才会执行其他任务。

### 重新分片

主节点选举、服务器上下线、分片总数变更均会更新重新分片标记。如分片过程中主服务器下线，则先选举主服务器，再分片。

为了维持作业运行时的稳定性，运行过程中只会标记分片状态，不会重新分片。分片仅可能发生在下次任务触发前。

### 失效转移

在某台服务器执行完毕后主动抓取未分配的分片，并且在某台服务器下线后主动寻找可用的服务器执行任务。

## 4.2 注册中心数据结构

```
命名空间
  |-- 作业名称
    |-- config
    |-- instances
      |-- ip+pid
    |-- sharding
      |-- 0
      |-- 1
      |-- 2
    |-- servers
    |-- leader
```

注册中心在定义的命名空间下，创建作业名称节点，用于区分不同作业，所以作业一旦创建则不能修改作业名称，如果修改名称将视为新的作业。 作业名称节点下又包含5个数据子节点，分别是 config, instances, sharding, servers 和 leader。

### config 节点

作业配置信息，以 YAML 格式存储。

### instances 节点

作业运行实例信息，子节点是作业运行服务器的 IP 地址和 PID。它们均为临时节点，当作业实例上线时注册，下线时自动清理。

### sharding 节点

作业分片信息，子节点是分片项序号，从零开始，至分片总数减一。 每个分片项下的子节点用于控制和记录分片运行状态。 节点详细信息说明：

| 子节点名 | 临时节点 | 描述                                                         |
| :------- | :------- | :----------------------------------------------------------- |
| instance |          | 执行该分片项的作业运行实例主键                               |
| running  | 是       | 分片项正在运行的状态 仅配置 monitorExecution 时有效          |
| failover | 是       | 如果该分片项被失效转移分配给其他作业服务器，则此节点值记录执行此分片的作业服务器 IP |
| misfire  |          | 是否开启错过任务重新执行                                     |
| disabled |          | 是否禁用此分片项                                             |

### servers 节点

作业服务器信息，子节点是作业服务器的 IP 地址。 可在 IP 地址节点写入 DISABLED 表示该服务器禁用。 在新的云原生架构下，servers 节点大幅弱化，仅包含控制服务器是否可以禁用这一功能。 为了更加纯粹的实现作业核心，servers 功能未来可能删除，控制服务器是否禁用的能力应该下放至自动化部署系统。

### leader 节点

作业服务器主节点信息，分为 election，sharding 和 failover 三个子节点。 分别用于主节点选举，分片和失效转移处理。

leader节点是内部使用的节点，如果对作业框架原理不感兴趣，可不关注此节点。

| 子节点名              | 临时节点 | 描述                                                         |
| :-------------------- | :------- | :----------------------------------------------------------- |
| election\instance     | 是       | 主节点服务器IP地址 一旦该节点被删除将会触发重新选举 重新选举的过程中一切主节点相关的操作都将阻塞 |
| election\latch        | 否       | 主节点选举的分布式锁 为 curator 的分布式锁使用               |
| sharding\necessary    | 否       | 是否需要重新分片的标记 如果分片总数变化，或作业服务器节点上下线或启用/禁用，以及主节点选举，会触发设置重分片标记 作业在下次执行时使用主节点重新分片，且中间不会被打断 作业执行时不会触发分片 |
| sharding\processing   | 是       | 主节点在分片时持有的节点 如果有此节点，所有的作业执行都将阻塞，直至分片结束 主节点分片结束或主节点崩溃会删除此临时节点 |
| failover\items\分片项 | 否       | 一旦有作业崩溃，则会向此节点记录 当有空闲作业服务器时，会从此节点抓取需失效转移的作业项 |
| failover\items\latch  | 否       | 分配失效转移分片项时占用的分布式锁 为 curator 的分布式锁使用 |

## 4.4 作业启动

作业服务器启动后，在运行任务前需要做以下准备：发起主节点选举、设置分片标记、注册作业全局信息、注册作业服务器信息。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407032323436.jpg)

## 4.5 作业执行

定时任务触发时，如需重新分片，则通过主服务器分片，分片过程中阻塞，分片结束后才可执行任务。

![作业执行](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407032324815.jpg)

# 五、使用手册（Java API）

## 5.1 作业配置

ElasticJob 采用构建器模式创建作业配置对象。

```java
JobConfiguration jobConfig = JobConfiguration.newBuilder("myJob", 3)
    .cron("0/5 * * * * ?")
    .shardingItemParameters("0=Beijing,1=Shanghai,2=Guangzhou")
    .build();
```

## 5.2 作业启动

ElasticJob 调度器分为定时调度和一次性调度两种类型。 每种调度器启动时均需要注册中心配置、作业对象（或作业类型）以及作业配置这 3 个参数。

```java
// 定时调度
public class JobDemo {
    
    public static void main(String[] args) {
        // 调度基于 class 类型的作业
        new ScheduleJobBootstrap(createRegistryCenter(), new MyJob(), createJobConfiguration()).schedule();
        // 调度基于 type 类型的作业
        new ScheduleJobBootstrap(createRegistryCenter(), "MY_TYPE", createJobConfiguration()).schedule();
    }
    
    private static CoordinatorRegistryCenter createRegistryCenter() {
        CoordinatorRegistryCenter regCenter = new ZookeeperRegistryCenter(new ZookeeperConfiguration("zk_host:2181", "elastic-job-demo"));
        regCenter.init();
        return regCenter;
    }
    
    private static JobConfiguration createJobConfiguration() {
        // 创建作业配置
        ...
    }
}
```

```java
// 一次性调度
public class JobDemo {
    
    public static void main(String[] args) {
        OneOffJobBootstrap jobBootstrap = new OneOffJobBootstrap(createRegistryCenter(), new MyJob(), createJobConfiguration());
        // 可多次调用一次性调度
        jobBootstrap.execute();
        jobBootstrap.execute();
        jobBootstrap.execute();
    }
    
    private static CoordinatorRegistryCenter createRegistryCenter() {
        CoordinatorRegistryCenter regCenter = new ZookeeperRegistryCenter(new ZookeeperConfiguration("zk_host:2181", "elastic-job-demo"));
        regCenter.init();
        return regCenter;
    }
    
    private static JobConfiguration createJobConfiguration() {
        // 创建作业配置
        ...
    }
}
```

## 5.4 配置作业导出端口

使用 ElasticJob 过程中可能会碰到一些分布式问题，导致作业运行不稳定。

由于无法在生产环境调试，通过 dump 命令可以把作业内部相关信息导出，方便开发者调试分析；

```java
public class JobMain {
    
    public static void main(final String[] args) {
        SnapshotService snapshotService = new SnapshotService(regCenter, 9888).listen();
    }
    
    private static CoordinatorRegistryCenter createRegistryCenter() {
        // 创建注册中心
    }
}
```

## 5.5 配置错误处理策略

记录日志策略: 记录作业异常日志，但不中断作业执行

```java
public class JobDemo {
    
    public static void main(String[] args) {
        //  定时调度作业
        new ScheduleJobBootstrap(createRegistryCenter(), new MyJob(), createScheduleJobConfiguration()).schedule();
        // 一次性调度作业
        new OneOffJobBootstrap(createRegistryCenter(), new MyJob(), createOneOffJobConfiguration()).execute();
    }
    
    private static JobConfiguration createScheduleJobConfiguration() {
        // 创建定时作业配置，并且使用记录日志策略
        return JobConfiguration.newBuilder("myScheduleJob", 3).cron("0/5 * * * * ?").jobErrorHandlerType("LOG").build();
    }

    private static JobConfiguration createOneOffJobConfiguration() {
        // 创建一次性作业配置，并且使用记录日志策略
        return JobConfiguration.newBuilder("myOneOffJob", 3).jobErrorHandlerType("LOG").build();
    }

    private static CoordinatorRegistryCenter createRegistryCenter() {
        // 配置注册中心
        ...
    }
}
```

抛出异常策略: 抛出系统异常并中断作业执行

```java
private static JobConfiguration createOneOffJobConfiguration() {
    // 创建一次性作业配置，并且使用抛出异常策略
    return JobConfiguration.newBuilder("myOneOffJob", 3).jobErrorHandlerType("THROW").build();
}
```

忽略异常策略: 忽略系统异常且不中断作业执行

```java
private static JobConfiguration createOneOffJobConfiguration() {
    // 创建一次性作业配置， 并且使用忽略异常策略
    return JobConfiguration.newBuilder("myOneOffJob", 3).jobErrorHandlerType("IGNORE").build();
}
```

邮件通知策略: 发送邮件消息通知，但不中断作业执行

```java
<dependency>
    <groupId>org.apache.shardingsphere.elasticjob</groupId>
    <artifactId>elasticjob-error-handler-email</artifactId>
    <version>${latest.release.version}</version>
</dependency>

private static JobConfiguration createOneOffJobConfiguration() {
    // 创建一次性作业配置， 并且使用邮件通知策略
    JobConfiguration jobConfig = JobConfiguration.newBuilder("myOneOffJob", 3).jobErrorHandlerType("EMAIL").build();
    setEmailProperties(jobConfig);
    return jobConfig;
}

private static void setEmailProperties(final JobConfiguration jobConfig) {
    // 设置邮件的配置
    jobConfig.getProps().setProperty(EmailPropertiesConstants.HOST, "host");
    jobConfig.getProps().setProperty(EmailPropertiesConstants.PORT, "465");
    jobConfig.getProps().setProperty(EmailPropertiesConstants.USERNAME, "username");
    jobConfig.getProps().setProperty(EmailPropertiesConstants.PASSWORD, "password");
    jobConfig.getProps().setProperty(EmailPropertiesConstants.FROM, "from@xxx.xx");
    jobConfig.getProps().setProperty(EmailPropertiesConstants.TO, "to1@xxx.xx,to1@xxx.xx");
}
```

企业微信通知策略: 发送企业微信消息通知，但不中断作业执行

```java
<dependency>
    <groupId>org.apache.shardingsphere.elasticjob</groupId>
    <artifactId>elasticjob-error-handler-wechat</artifactId>
    <version>${latest.release.version}</version>
</dependency>

private static JobConfiguration createOneOffJobConfiguration() {
    // 创建一次性作业配置， 并且使用企业微信通知策略
    JobConfiguration jobConfig = JobConfiguration.newBuilder("myOneOffJob", 3).jobErrorHandlerType("WECHAT").build();
    setWechatProperties(jobConfig);
    return jobConfig;
}

private static void setWechatProperties(final JobConfiguration jobConfig) {
    // 设置企业微信的配置
    jobConfig.getProps().setProperty(WechatPropertiesConstants.WEBHOOK, "you_webhook");
}
```

钉钉通知策略: 发送钉钉消息通知，但不中断作业执行

```java
<dependency>
    <groupId>org.apache.shardingsphere.elasticjob</groupId>
    <artifactId>elasticjob-error-handler-dingtalk</artifactId>
    <version>${latest.release.version}</version>
</dependency>

private static JobConfiguration createOneOffJobConfiguration() {
    // 创建一次性作业配置， 并且使用钉钉通知策略
    JobConfiguration jobConfig = JobConfiguration.newBuilder("myOneOffJob", 3).jobErrorHandlerType("DINGTALK").build();
    setDingtalkProperties(jobConfig);
    return jobConfig;
}

private static void setDingtalkProperties(final JobConfiguration jobConfig) {
    // 设置钉钉的配置
    jobConfig.getProps().setProperty(DingtalkPropertiesConstants.WEBHOOK, "you_webhook");
    jobConfig.getProps().setProperty(DingtalkPropertiesConstants.KEYWORD, "you_keyword");
    jobConfig.getProps().setProperty(DingtalkPropertiesConstants.SECRET, "you_secret");
}
```



## 5.6 作业监听器



## 5.7 事件追踪



## 5.8 操作 API



# 六、使用手册（Spring Boot Starter）

## 7.1 作业开发

## 7.2 作业配置

```java
@Component
public class SpringBootDataflowJob implements DataflowJob<Foo> {
    
    @Override
    public List<Foo> fetchData(final ShardingContext shardingContext) {
        // 获取数据
    }
    
    @Override
    public void processData(final ShardingContext shardingContext, final List<Foo> data) {
        // 处理数据
    }
}
```

```yaml
elasticjob:
  regCenter:
    # Zookeeper
    serverLists: localhost:6181
    namespace: elasticjob-springboot
  jobs:
    dataflowJob:
      elasticJobClass: org.apache.shardingsphere.elasticjob.dataflow.job.DataflowJob
      cron: 0/5 * * * * ?
      shardingTotalCount: 3
      shardingItemParameters: 0=Beijing,1=Shanghai,2=Guangzhou
    scriptJob:
      elasticJobType: SCRIPT
      cron: 0/10 * * * * ?
      shardingTotalCount: 3
      props:
        script.command.line: "echo SCRIPT Job: "
```

## 7.3 作业启动

定时调度作业在 Spring Boot 应用程序启动完成后会自动启动，无需其他额外操作。

一次性调度的作业的执行权在开发者手中，开发者可以在需要调用作业的位置注入 `OneOffJobBootstrap`， 通过 `execute()` 方法执行作业。

```yaml
elasticjob:
  jobs:
    myOneOffJob:
      jobBootstrapBeanName: myOneOffJobBean
      ....
```

```java
@RestController
public class OneOffJobController {

    // 通过 "@Autowired" 注入
    @Autowired
    @Qualifier(name = "myOneOffJobBean")
    private OneOffJobBootstrap myOneOffJob2;

    @GetMapping("/execute2")
    public String executeOneOffJob2() {
        myOneOffJob2.execute();
        return "{\"msg\":\"OK\"}";
    }
}
```

## 7.4 配置错误处理策略

```yaml
elasticjob:
  regCenter:
    ...
  jobs:
    ...
    jobErrorHandlerType: LOG #记录日志策略
    jobErrorHandlerType: THROW #抛出异常策略
    jobErrorHandlerType: IGNORE #忽略异常策略
```

```yaml
#邮件通知策略（pom依赖同上）
elasticjob:
  regCenter:
    ...
  jobs:
    ...
    jobErrorHandlerType: EMAIL 
    props:
      email:
        host: host
        port: 465
        username: username
        password: password
        useSsl: true
        subject: ElasticJob error message
        from: from@xxx.xx
        to: to1@xxx.xx,to2@xxx.xx
        cc: cc@xxx.xx
        bcc: bcc@xxx.xx
        debug: false
```

```yaml
#企业微信通知策略（pom依赖同上）
elasticjob:
  regCenter:
    ...
  jobs:
    ...
    jobErrorHandlerType: WECHAT 
    props:
      wechat:
        webhook: you_webhook
        connectTimeout: 3000
        readTimeout: 5000
```

```yaml
#钉钉通知策略（pom依赖同上）
elasticjob:
  regCenter:
    ...
  jobs:
    ...
    jobErrorHandlerType: DINGTALK 
    props:
      dingtalk:
        webhook: you_webhook
        keyword: you_keyword
        secret: you_secret
        connectTimeout: 3000
        readTimeout: 5000
```


# 七、使用手册（Spring XML）



