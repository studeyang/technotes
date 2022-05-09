# 01 | 快速使用

> 参考：https://github.com/camunda-community-hub/spring-zeebe/tree/master/examples

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



## 

