# 用法一：List转Map

**Value 对象类型不变**

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

**Value 对象类型转化**

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

**对象分组**

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

