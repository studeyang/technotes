## 一、使用 Stream 实现 List 转 Map

### Value 对象类型不变

```java
/*
[
  {"id": "100", "type": "created"}，
  {"id": "101", "type": "update"}，
]
*/
List<Message> messages = new ArrayList<>();
/*
  id -> {"id": "100", "type": "created"}
*/
Map<String, Message> map = messages.stream()
    .collect(Collectors.toMap(Message::getId, Function.identity()));
```

### Value 对象类型转化

```java
/*
[
  {"id": "100", "type": "created"}，
  {"id": "101", "type": "update"}，
]
*/
List<Message> messages = new ArrayList<>();
/*
  id -> type
*/
Map<String, String> map = messages.stream()
    .collect(Collectors.toMap(Message::getId, Message::getType));
```

### 对象分组

```java
/*
[
  {"id": "100", "type": "created"},
  {"id": "100", "type": "update"}
]
*/
List<Message> messages = new ArrayList<>();
/*
  id -> [
          {"id": "100", "type": "created"},
          {"id": "100", "type": "created"}
        ]
*/
Map<String, List<Message>> map = messages.stream()
    .collect(Collectors.groupingBy(Message::getId));
```

## 二、使用 CompletableFuture 分批并发执行

### Usage

```java
public static void main(String[] args) {

    Function<String, Runnable> function = billGroupId -> () -> {
        // long time to execute
    };
    new HandleAfterRepayProcessor(getMetadata(), function, 50).process();
}
```

### processor

```java
package com.casstime.ec.cloud.service.biz;

import com.google.common.collect.Lists;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.concurrent.CustomizableThreadFactory;

import java.util.List;
import java.util.concurrent.*;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * @since 1.0 2023/6/6
 */
@Slf4j
public class HandleAfterRepayProcessor {

    private final List<List<String>> partitions;
    private final Function<String, Runnable> taskFunction;
    private final ExecutorService executorService;

    public HandleAfterRepayProcessor(List<String> metadata,
                                     Function<String, Runnable> taskFunction,
                                     int partition) {
        this.partitions = Lists.partition(metadata, partition);
        this.taskFunction = taskFunction;
        this.executorService = new ThreadPoolExecutor(
                partition,
                partition,
                0L,
                TimeUnit.MILLISECONDS,
                new LinkedBlockingQueue<>(1000),
                new CustomizableThreadFactory("handle-after-repay-"),
                new ThreadPoolExecutor.CallerRunsPolicy()
        );
    }

    public void process() {
        for (int i = 0; i < partitions.size(); i++) {
            List<String> partition = partitions.get(i);
            CompletableFuture<Void> future = processPartition(partition);
            future.join();
            int batch = i + 1;
            future.thenRun(() -> log.debug("第 {} 批, 处理完成 {} 条数据", batch, partition.size()));
        }
        executorService.shutdown();
    }

    /**
     * 异步转同步
     */
    private CompletableFuture<Void> processPartition(List<String> metadata) {
        List<CompletableFuture<Void>> futures = metadata
                .stream()
                .map(taskFunction)
                .map(task -> CompletableFuture.runAsync(task, executorService))
                .collect(Collectors.toList());
        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]));
    }

}
```

## 三、Java 8 Map 的优雅写法

### 添加元素

```java
public class MapListExample {
    public static void main(String[] args) {
        // 创建一个Map<String, List<String>>
        Map<String, List<String>> map = new HashMap<>();

        // 添加元素的示例
        map.computeIfAbsent("fruits", k -> new ArrayList<>()).add("Apple");
        map.computeIfAbsent("fruits", k -> new ArrayList<>()).add("Banana");
        map.computeIfAbsent("vegetables", k -> new ArrayList<>()).add("Carrot");

        // 打印Map内容
        System.out.println("Map内容: " + map);
    }
}

// Map内容: {fruits=[Apple, Banana], vegetables=[Carrot]}
```

### 收集

```java
// List<List<String>> 怎么收集到一个 List<String> 中？用 Java8 实现

List<List<String>> listOfLists = Arrays.asList(
    Arrays.asList("a", "b"),
    Arrays.asList("c", "d", "e"),
    Collections.singletonList("f")
);

List<String> flattenedList = listOfLists.stream()
    .flatMap(List::stream)  // 将每个内部List转换为流，然后合并
    .collect(Collectors.toList());

System.out.println(flattenedList); // 输出: [a, b, c, d, e, f]
```

