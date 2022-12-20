# 01 | 快速使用

> 参考：https://github.com/camunda-community-hub/spring-zeebe/tree/8.1.12/example

## 1.1 添加依赖

```xml
<dependency>
    <groupId>io.camunda</groupId>
    <artifactId>spring-zeebe-starter</artifactId>
    <version>1.2.6</version>
</dependency>
<dependency>
    <groupId>io.grpc</groupId>
    <artifactId>grpc-netty</artifactId>
    <version>1.40.1</version>
</dependency>
```

## 1.2 配置连接

```properties
zeebe.client.cloud.cluster-id=xxx
zeebe.client.cloud.client-id=xxx
zeebe.client.cloud.client-secret=xxx
zeebe.client.cloud.region=bru-2
```

## 1.3 启动工作流

```java
@SpringBootApplication
@EnableZeebeClient
@EnableScheduling
@ZeebeDeployment(resources = "classpath:demoProcess.bpmn")
@Slf4j
public class StarterApplication {

  public static void main(final String... args) {
    SpringApplication.run(StarterApplication.class, args);
  }

  @Autowired
  private ZeebeClientLifecycle client;

  @Scheduled(fixedRate = 5000L)
  public void startProcesses() {
    if (!client.isRunning()) {
      return;
    }

    final ProcessInstanceEvent event =
      client
        .newCreateInstanceCommand()
        .bpmnProcessId("demoProcess")
        .latestVersion()
        .variables("{\"a\": \"" + UUID.randomUUID().toString() + "\",\"b\": \"" + new Date().toString() + "\"}")
        .send()
        .join();

    log.info("started instance for workflowKey='{}', bpmnProcessId='{}', version='{}' with workflowInstanceKey='{}'",
      event.getProcessDefinitionKey(), event.getBpmnProcessId(), event.getVersion(), event.getProcessInstanceKey());
  }
}
```

工作流定义如下：

![image-20220420105244258](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220420105244258.png)

## 1.4 实现 Worker

```java
@SpringBootApplication
@EnableZeebeClient
@Slf4j
public class WorkerApplication {

  public static void main(final String... args) {
    SpringApplication.run(WorkerApplication.class, args);
  }

  private static void logJob(final ActivatedJob job, Object parameterValue) {
    log.info(
      "complete job\n>>> [type: {}, key: {}, element: {}, workflow instance: {}]\n{deadline; {}]\n[headers: {}]\n[variable parameter: {}\n[variables: {}]",
      job.getType(),
      job.getKey(),
      job.getElementId(),
      job.getProcessInstanceKey(),
      Instant.ofEpochMilli(job.getDeadline()),
      job.getCustomHeaders(),
      parameterValue,
      job.getVariables());
  }

  @ZeebeWorker(type = "foo")
  public void handleFooJob(final JobClient client, final ActivatedJob job) {
    logJob(job, null);
    client.newCompleteCommand(job.getKey()).variables("{\"foo\": 1}").send().whenComplete((result, exception) -> {
      if (exception == null) {
        log.info("Completed job successful");
      } else {
        log.error("Failed to complete job", exception);
      }
    });
  }

  // Variable "foo" gets renamed to "bar" by IO mapping in the process
  @ZeebeWorker(type = "bar", fetchVariables = "bar", autoComplete = true)
  public Map<String, Object> handleBarJob(final JobClient client, final ActivatedJob job, @ZeebeVariable String a) {
    logJob(job, a);
    // Done by auto complete: client.newCompleteCommand(job.getKey()).send()
    return Collections.singletonMap("someResult", "42");
  }

  @ZeebeWorker(type = "fail", autoComplete = true, forceFetchAllVariables = true)
  public void handleFailingJob(final JobClient client, final ActivatedJob job, @ZeebeVariable Integer bar) {
    logJob(job, bar);
    throw new ZeebeBpmnError("DOESNT_WORK", "This will actually never work :-)");
  }
}
```

# 02 | 场景应用

## 2.1 隐私通话

```java
@RestController
@RequestMapping("/axb")
@Slf4j
public class AXBZeebeAutoController {
    @Autowired
    private ZeebeClientLifecycle zeebeClient;
    
    @PostMapping(value = "/bind")
    public String axbBindNumber(@RequestBody AXBBindRequest request) {
        HashMap<String, Object> params = Maps.newHashMap();
        params.put("axbBindRequest", JsonUtil.serializer(request));

        log.info("> 开始激活虚拟号码绑定流程");
        // 启动一个流程, 等待结果返回
        ProcessInstanceResult processInstanceResult = zeebeClient
                .newCreateInstanceCommand()
                .bpmnProcessId("private-number-service-axb-bind")
                .latestVersion()
                .variables(params)
                .withResult()
                .send().join();

        log.info("> 虚拟号码绑定流程结束: {}", processInstanceResult.getVariablesAsMap());
        return (String) processInstanceResult.getVariablesAsMap().get("axb_bind_response");
    }
    
}
```

# 03 | zeebe-http-worker

> https://github.com/camunda-community-hub/zeebe-http-worker



# 04 | 了解 zeebe

> - 项目地址：https://github.com/camunda/zeebe
> - 官网：https://camunda.com/platform/zeebe/
> - InfoQ文章：https://xie.infoq.cn/article/4e361655b83634d2a3a0c9a61

## 4.1 Zeebe 介绍

Zeebe 是开源的用于微服务编排的分布式工作流引擎。

### Zeebe 架构

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/c337f96566db5c56aa42adcd6acfc725.png)

### Zeebe Cluster

![image-20221220144645588](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221220144645588.png)

### Partitions

多个 brokers 组成 partition，通过 Raft protocol 选举 partition 中的 leader。

![image-20221220144909821](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221220144909821.png)

类似 Kafka 中的 partition，Zeebe 中将 Process 分发到所有的 partition。

### Zeebe Example

![image-20221220150409974](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221220150409974.png)

### 支持 Spring Boot Worker

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/1d08e786f4b9f37b8905e901857a8b04.png)

### Operate 可视化


![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/1847c45cfcefb264646f072d570d7c47.png)

## 4.2 官方资料

### Overview Components

![ComponentsAndArchitecture_SaaS-edd9396b71911e6e4df0e16fa905e869](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/ComponentsAndArchitecture_SaaS-edd9396b71911e6e4df0e16fa905e869.png)

