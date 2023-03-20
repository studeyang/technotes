# 用法一：List转Map

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
  {"id": "100", "type": "created"}，
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

### computeIfAbsent

当 key 不存在时，执行 value 计算方法，计算 value。并插入 key 和 value。

```java
@Test
public void testMap() {
    Map<String, String> map = new HashMap<>();
    map.put("a","A");
    map.put("b","B");
    String v = map.computeIfAbsent("b", k->"v");  // 输出 B
    System.out.println(v);
    String v1 = map.computeIfAbsent("c", k->"v"); // 输出 v
    System.out.println(v1);
}
```





