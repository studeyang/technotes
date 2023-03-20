# 记一次 Kafka 不消费的排查过程

一次业务方找到我说：我们的服务没收到消息，重启后能收到，但是运行几分钟后，又收不到消息了。

![image-20230306175032627](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/image-20230306175032627.png)



![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/image-20230306174817457.png)



```java
List<DistributeSupplyRecordRequest> cutRequests =
    Lists.partition(standardItemIds, ONE_TASK_SIZE).stream().map(p -> {
    DistributeSupplyRecordRequest request = new DistributeSupplyRecordRequest();
    request.setDemandId(demandId);
    request.setSource(RequestSourceEnum.REQUEST_SOURCE_IC.getKey());
    request.setStandardItemIds(p);
    return request;
}).collect(Collectors.toList());

Object[] results = Observable
    .zip(cutRequests.stream().map(this::queryDistributeSupplyRecordObservable)
         .collect(Collectors.toList()),
         objects -> objects)
    .toBlocking()
    .first(); // 出问题的代码行
```



## 收发消息架构

