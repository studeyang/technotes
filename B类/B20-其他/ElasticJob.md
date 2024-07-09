> 参考资料：https://shardingsphere.apache.org/elasticjob/current/cn/overview/

# 一、概览

## 1.1 简介

使用 ElasticJob 能够让开发工程师不再担心任务的线性吞吐量提升等非功能需求，使他们能够更加专注于面向业务编码设计； 

同时，它也能够解放运维工程师，使他们不必再担心任务的可用性和相关管理需求，只通过轻松的增加服务节点即可达到自动化运维的目的。

ElasticJob 定位为轻量级无中心化解决方案，使用 jar 的形式提供分布式任务的协调服务。

![image-20240703223744793](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407032237856.png)

## 1.2 功能

- 弹性调度
  - 支持任务在分布式场景下的分片和高可用
  - 能够水平扩展任务的吞吐量和执行效率
  - 任务处理能力随资源配备弹性伸缩
- 资源分配
  - 在适合的时间将适合的资源分配给任务并使其生效
  - 相同任务聚合至相同的执行器统一处理
  - 动态调配追加资源至新分配的任务
- 作业治理
  - 失效转移
  - 错过作业重新执行
  - 自诊断修复
- 作业依赖(TODO)
  - 基于有向无环图（DAG）的作业间依赖
  - 基于有向无环图（DAG）的作业分片间依赖
- 作业开放生态
  - 可扩展的作业类型统一接口
  - 丰富的作业类型库，如数据流、脚本、HTTP、文件、大数据等
  - 易于对接业务作业，能够与 Spring 依赖注入无缝整合
- 可视化管控端
  - 作业管控端
  - 作业执行历史数据追踪
  - 注册中心管理

# 二、快速入门

**1、引入 Maven 依赖**

```xml
<dependency>
    <groupId>org.apache.shardingsphere.elasticjob</groupId>
    <artifactId>elasticjob-bootstrap</artifactId>
    <version>${latest.release.version}</version>
</dependency>
```

**2、作业开发**

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

**3、作业配置**

```java
JobConfiguration jobConfig = JobConfiguration.newBuilder("MyJob", 3)
        .cron("0/5 * * * * ?").build();
```

**4、作业调度**

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

# 三、概念&功能

## 3.1 调度模型

ElasticJob 是面向进程内的线程级调度框架。

## 3.2 弹性调度

弹性调度是 ElasticJob 最重要的功能，也是这款产品名称的由来。 它是一款能够让任务通过分片进行水平扩展的任务处理系统。

### 分片

每台任务服务器只运行分配给该服务器的分片。 随着服务器的增加或宕机，ElasticJob 会近乎实时的感知服务器数量的变更，从而重新为分布式的任务服务器分配更加合理的任务分片项。

任务的分布式执行，需要将一个任务拆分为多个独立的任务项，然后由分布式的服务器分别执行某一个或几个分片项。

举例说明，如果作业分为 4 片，用两台服务器执行，则每个服务器分到 2 片，分别负责作业的 50% 的负载，如下图所示。

![image-20240703225714203](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407032257259.png)

### 分片项

分片项为数字，始于 0 而终于分片总数减 1。

ElasticJob 将分片项分配至各个运行中的作业服务器，开发者需要自行处理分片项与业务的对应关系。

再回到上面的 Job 示例：

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

例如：按照地区水平拆分数据库，数据库 A 是北京的数据；数据库 B 是上海的数据；数据库 C 是广州的数据。 如果仅按照分片项配置，开发者需要了解 0 表示北京；1 表示上海；2 表示广州。 合理使用个性化参数可以让代码更可读，如果配置为 0=北京,1=上海,2=广州，那么代码中直接使用北京，上海，广州的枚举值即可完成分片项和业务逻辑的对应关系。

### 资源最大限度利用

ElasticJob 提供最灵活的方式，最大限度的提高执行作业的吞吐量。 当新增加作业服务器时，ElasticJob 会通过注册中心的临时节点的变化感知到新服务器的存在，并在下次任务调度的时候重新分片，新的服务器会承载一部分作业分片，如下图所示。

![image-20240703230447749](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407032304811.png)

将分片项设置为大于服务器的数量，最好是大于服务器倍数的数量，作业将会合理的利用分布式资源，动态的分配分片项。

例如：3 台服务器，分成 10 片，则分片项分配结果为服务器 A = 0,1,2,9；服务器 B = 3,4,5；服务器 C = 6,7,8。 如果服务器 C 崩溃，则分片项分配结果为服务器 A = 0,1,2,3,4; 服务器 B = 5,6,7,8,9。 在不丢失分片项的情况下，最大限度的利用现有资源提高吞吐量。

### 高可用

当作业服务器在运行中宕机时，注册中心同样会通过临时节点感知，并将在下次运行时将分片转移至仍存活的服务器，以达到作业高可用的效果。 本次由于服务器宕机而未执行完的作业，则可以通过失效转移的方式继续执行。如下图所示。

![image-20240703231303299](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407032313345.png)

将分片总数设置为 1，并使用多于 1 台的服务器执行作业，作业将会以 1 主 n 从的方式执行。 一旦执行作业的服务器宕机，等待执行的服务器将会在下次作业启动时替补执行。开启失效转移功能效果更好，如果本次作业在执行过程中宕机，备机会立即替补执行。

### 实现原理

ElasticJob 并无作业调度中心节点，而是基于部署作业框架的程序在到达相应时间点时各自触发调度。 注册中心仅用于作业注册和监控信息存储。而主作业节点仅用于处理分片和清理等功能。

**1、弹性分布式实现**

- 第一台服务器上线触发主服务器选举。主服务器一旦下线，则重新触发选举，选举过程中阻塞，只有主服务器选举完成，才会执行其他任务。
- 某作业服务器上线时会自动将服务器信息注册到注册中心，下线时会自动更新服务器状态。
- 主节点选举，服务器上下线，分片总数变更均更新重新分片标记。
- 定时任务触发时，如需重新分片，则通过主服务器分片，分片过程中阻塞，分片结束后才可执行任务。如分片过程中主服务器下线，则先选举主服务器，再分片。
- 通过上一项说明可知，为了维持作业运行时的稳定性，运行过程中只会标记分片状态，不会重新分片。分片仅可能发生在下次任务触发前。
- 每次分片都会按服务器IP排序，保证分片结果不会产生较大波动。
- 实现失效转移功能，在某台服务器执行完毕后主动抓取未分配的分片，并且在某台服务器下线后主动寻找可用的服务器执行任务。

**2、注册中心数据结构**

注册中心在定义的命名空间下，创建作业名称节点，用于区分不同作业，所以作业一旦创建则不能修改作业名称，如果修改名称将视为新的作业。 作业名称节点下又包含5个数据子节点，分别是 config, instances, sharding, servers 和 leader。

**3、config 节点**

作业配置信息，以 YAML 格式存储。

**4、instances 节点**

作业运行实例信息，子节点是当前作业运行实例的主键。 作业运行实例主键由作业运行服务器的 IP 地址和 PID 构成。 作业运行实例主键均为临时节点，当作业实例上线时注册，下线时自动清理。注册中心监控这些节点的变化来协调分布式作业的分片以及高可用。 可在作业运行实例节点写入 TRIGGER 表示该实例立即执行一次。

**5、sharding 节点**

作业分片信息，子节点是分片项序号，从零开始，至分片总数减一。 分片项序号的子节点存储详细信息。每个分片项下的子节点用于控制和记录分片运行状态。 节点详细信息说明：

| 子节点名 | 临时节点 | 描述                                                         |
| :------- | :------- | :----------------------------------------------------------- |
| instance | 否       | 执行该分片项的作业运行实例主键                               |
| running  | 是       | 分片项正在运行的状态 仅配置 monitorExecution 时有效          |
| failover | 是       | 如果该分片项被失效转移分配给其他作业服务器，则此节点值记录执行此分片的作业服务器 IP |
| misfire  | 否       | 是否开启错过任务重新执行                                     |
| disabled | 否       | 是否禁用此分片项                                             |

**6、servers 节点**

作业服务器信息，子节点是作业服务器的 IP 地址。 可在 IP 地址节点写入 DISABLED 表示该服务器禁用。 在新的云原生架构下，servers 节点大幅弱化，仅包含控制服务器是否可以禁用这一功能。 为了更加纯粹的实现作业核心，servers 功能未来可能删除，控制服务器是否禁用的能力应该下放至自动化部署系统。

**7、leader 节点**

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

**8、流程图**

作业启动：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407032323436.jpg)

作业执行：

![作业执行](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407032324815.jpg)

## 3.3 失效转移

ElasticJob 不会在本次执行过程中进行重新分片，而是等待下次调度之前才开启重新分片流程。 当作业执行过程中服务器宕机，失效转移允许将该次未完成的任务在另一作业节点上补偿执行。

举例说明，若作业以每小时为间隔执行，每次执行耗时 30 分钟。如下如图所示。

![定时作业](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407092346004.png)

图中表示作业分别于 12:00，13:00 和 14:00 执行。图中显示的当前时间点为 13:00 的作业执行中。

如果作业的其中一个分片服务器在 13:10 的时候宕机，那么剩余的 20 分钟应该处理的业务未得到执行，并且需要在 14:00 时才能再次开始执行下一次作业。 也就是说，在不开启失效转移的情况下，位于该分片的作业有 50 分钟空档期。如下如图所示。

![作业宕机](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407092346631.png)

在开启失效转移功能之后，ElasticJob 的其他服务器能够在感知到宕机的作业服务器之后，补偿执行该分片作业。如下图所示。

![补偿执行](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407092346006.png)

在资源充足的情况下，作业仍然能够在 13:30 完成执行。

### 执行机制

作业服务在本次任务执行结束后，会向注册中心问询待执行的失效转移分片项，如果有，则开始补偿执行。 也称为异步执行。

当其他服务器感知到有失效转移的作业需要处理时，且该作业服务器已经完成了本次任务，则会实时的拉取待失效转移的分片项，并开始补偿执行。 也称为实时执行。

### 适用场景

在一次运行耗时较长且间隔较长的作业场景，失效转移是提升作业运行实时性的有效手段；

 对于间隔较短的作业，会产生大量与注册中心的网络通信，对集群的性能产生影响。 而且间隔较短的作业并未见得关注单次作业的实时性，可以通过下次作业执行的重分片使所有的分片正确执行，因此不建议短间隔作业开启失效转移。



## 3.4 错过任务重执行

ElasticJob 不允许作业在同一时间内叠加执行。 当作业的执行时长超过其运行间隔，错过任务重执行能够保证作业在完成上次的任务后继续执行逾期的作业。

举例说明，若作业以每小时为间隔执行，每次执行耗时 30 分钟。如下如图所示。

![定时作业](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407092340427.png)

图中表示作业分别于 12:00，13:00 和 14:00 执行。图中显示的当前时间点为 13:00 的作业执行中。

如果 12：00 开始执行的作业在 13:10 才执行完毕，那么本该由 13:00 触发的作业则错过了触发时间，需要等待至 14:00 的下次作业触发。 如下如图所示。

![错过作业](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407092341999.png)

在开启错过任务重执行功能之后，ElasticJob 将会在上次作业执行完毕后，立刻触发执行错过的作业。如下图所示。

![错过作业重执行](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202407092341057.png)

在 13：00 和 14:00 之间错过的作业将会重新执行。

## 3.5 作业开放生态

ElasticJob 的作业可划分为基于 class 类型和基于 type 类型两种。

Class 类型的作业由开发者直接使用，需要由开发者实现该作业接口实现业务逻辑。典型代表：Simple 类型、Dataflow 类型。 Type 类型的作业只需提供类型名称即可，开发者无需实现该作业接口，而是通过外置配置的方式使用。典型代表：Script 类型、HTTP 类型。

# 四、用户手册

## 4.1 使用手册

### 作业 API

1、简单作业

```java
public class MyElasticJob implements SimpleJob {
    
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

2、数据流作业

```java
public class MyElasticJob implements DataflowJob<Foo> {
    
    @Override
    public List<Foo> fetchData(ShardingContext context) {
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

3、脚本作业

支持 shell，python，perl 等所有类型脚本。

```shell
#!/bin/bash
echo sharding execution context is $*
```

作业运行时将输出：

```
sharding execution context is {"jobName":"scriptElasticDemoJob","shardingTotalCount":10,"jobParameter":"","shardingItem":0,"shardingParameter":"A"}
```

4、HTTP作业

（3.0.0-beta 提供）

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

execute接口将输出：

```
execute from source : ejob, shardingContext : {"jobName":"scriptElasticDemoJob","shardingTotalCount":3,"jobParameter":"","shardingItem":0,"shardingParameter":"Beijing"}
```





