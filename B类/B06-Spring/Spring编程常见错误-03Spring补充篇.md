# 18 | Spring Data 常见错误

众所周知，基本上所有的项目都会用到数据库，所以 Spring 提供了对市场上主流数据库的贴心支持，我们不妨通过下面的列表快速浏览下：

```
Spring Data Commons
Spring Data JPA
Spring Data KeyValue
Spring Data LDAP
Spring Data MongoDB
Spring Data Redis
Spring Data REST
Spring Data for Apache Cassandra
Spring Data for Apache Geode
Spring Data for Apache Solr
Spring Data for Pivotal GemFire
Spring Data Couchbase (community module)
Spring Data Elasticsearch (community module)
Spring Data Neo4j (community module)
```

**案例 1：注意读与取的一致性**

当使用 Spring Data Redis 时，我们有时候会在项目升级的过程中，发现存储后的数据有读取不到的情况。这里我们不妨直接写出一个错误案例来模拟下：

```java
@SpringBootApplication
public class SpringdataApplication {
    SpringdataApplication(RedisTemplate redisTemplate, 
                          StringRedisTemplate stringRedisTemplate) {
        String key = "mykey";
        stringRedisTemplate.opsForValue().set(key, "myvalue");
        Object valueGotFromStringRedisTemplate = stringRedisTemplate.opsForValue().get(key);
        System.out.println(valueGotFromStringRedisTemplate);
        Object valueGotFromRedisTemplate = redisTemplate.opsForValue().get(key);
        System.out.println(valueGotFromRedisTemplate);
    }
    public static void main(String[] args) {
        SpringApplication.run(SpringdataApplication.class, args);
    }
}
```

在上述代码中，我们使用了 Redis 提供的两种 Template，一种 RedisTemplate，一种 StringRedisTemplate。但是当我们使用 StringRedisTemplate 去存一个数据后，你会发现使用 RedisTemplate 是取不到对应的数据的。输出结果如下：

```
myvalue
null
```

如果我们是不同的开发者开发不同的项目呢？一个项目只负责存储，另外一个项目只负责读取，两个项目之间缺乏沟通和协调。这种问题在实际工作中并不稀奇。

- 案例解析

首先，我们需要认清一个现实：我们不可能直接将数据存取到 Redis 中，毕竟一些数据是一个对象型，例如 String，甚至是一些自定义对象。我们需要在存取前对数据进行序列化或者反序列化操作。

当带着 key 去存取数据时，它会执行 AbstractOperations#rawKey。

```java
byte[] rawKey(Object key) {
    Assert.notNull(key, "non null key required");
    if (keySerializer() == null && key instanceof byte[]) {
        return (byte[]) key;
    }
    return keySerializer().serialize(key);
}
```

从上述代码可以看出，假设存在 keySerializer，则利用它将 key 序列化。而对于 StringRedisTemplate 来说，它指定的其实是 StringRedisSerializer。具体实现如下：

```java
public class StringRedisSerializer implements RedisSerializer<String> {
    private final Charset charset;
    @Override
    public byte[] serialize(@Nullable String string) {
        return (string == null ? null : string.getBytes(charset));
    }
}
```

而如果我们使用的是 RedisTemplate，则使用的是 JDK 序列化，具体序列化操作参考下面的实现：

```java
public class JdkSerializationRedisSerializer implements RedisSerializer<Object> {
    @Override
    public byte[] serialize(@Nullable Object object) {
        if (object == null) {
            return SerializationUtils.EMPTY_ARRAY;
        }
        try {
            return serializer.convert(object);
        } catch (Exception ex) {
            throw new SerializationException("Cannot serialize", ex);
        }
    }
}
```

上面对 key 的处理，采用的是 JDK 的序列化，最终它调用的方法如下：

```java
public interface Serializer<T> {
    void serialize(T var1, OutputStream var2) throws IOException;
    default byte[] serializeToByteArray(T object) throws IOException {
        ByteArrayOutputStream out = new ByteArrayOutputStream(1024);
        this.serialize(object, out);
        return out.toByteArray();
    }
}
```

你可以直接将"mykey"这个字符串分别用上面提到的两种序列化器进行序列化，你会发现它们的结果确实不同。

- 案例修正

要解决这个问题，非常简单，就是检查自己所有的数据操作，是否使用了相同的 RedisTemplate，就是相同，也要检查所指定的各种 Serializer 是否完全一致，否则就会出现各式各样的错误。

**案例 2：默认值的错误**

当我们使用 Spring Data 时，就像其他 Spring 模块一样，为了应对大多数场景或者方便用户使用，Spring Data 都有很多默认值，但是不见得所有的默认值都是最合适的。

例如在一个依赖 Cassandra 的项目中，有时候我们在写入数据之后，并不能立马读到写入的数据。这里面可能是什么原因呢？这种错误并没有什么报错，一切都是正常的，只是读取不到数据而已。

- 案例解析

当我们什么都不去配置，而是直接使用 Spring Data Cassandra 来操作时，我们实际依赖了 Cassandra driver 内部的配置文件，具体目录如下：

```
.m2\repository\com\datastax\oss\java-driver-core\4.6.1\java-driver-core-4.6.1.jar!\reference.conf
```

我们可以看下它存在很多默认的配置，其中一项很重要的配置是 Consistency，在 driver 中默认为 LOCAL_ONE，具体如下：

```
basic.request {
  # The consistency level.
  # 
  # Required: yes
  # Modifiable at runtime: yes, the new value will be used for requests issued after the change.
  # Overridable in a profile: yes
  consistency = LOCAL_ONE
  //省略其他非关键配置
}
```

所以当我们去执行读写操作时，我们都会使用 LOCAL_ONE。

如果你稍微了解下 Cassandra 的话，你就知道 Cassandra 使用的一个核心原则，就是要使得 R（读）+W（写）>N，即读和写的节点数之和需要大于备份数。

例如，假设我们的数据备份是 3 份，待写入的数据分别存储在 A、B、C 三个节点上。那么常见的搭配是 R（读）和 W（写）的一致性都是 LOCAL_QURAM，这样可以保证能及时读到写入的数据；而假设在这种情况下，我们读写都是用 LOCAL_ONE，那么则可能发生这样的情况，即用户写入一个节点 A 就返回了，但是用户 B 立马读的节点是 C，且由于是 LOCAL_ONE 一致性，则读完 C 就可以立马返回。此时，就会出现数据读取可能落空的情况。

![image-20220826221957720](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208262219855.png)

那么考虑一个问题，为什么 Cassandra driver 默认是使用 LOCAL_ONE 呢？

实际上，当你第一次学习和应用 Cassandra 时，你一定会先只装一台机器玩玩。此时，设置为 LOCAL_ONE 其实是最合适的，也正因为只有一台机器，你的读写都只能命中一台。这样的话，读写是完全没有问题的。但是产线上的 Cassandra 大多都是多数据中心多节点的，备份数大于 1。所以读写都用 LOCAL_ONE 就会出现问题。

- 案例修正

通过这个案例的分析，我们知道 Spring Data Cassandra 的默认值不见得适应于所有情况，甚至说，不一定适合于产线环境，所以这里我们不妨修改下默认值，还是以 consistency 为例。

我们看下如何修改它：

```java
@Override
protected SessionBuilderConfigurer getSessionBuilderConfigurer() {
    return cqlSessionBuilder -> {
        DefaultProgrammaticDriverConfigLoaderBuilder defaultProgrammaticDriverConfigLoaderBuilder = 
            new DefaultProgrammaticDriverConfigLoaderBuilder();
        driverConfigLoaderBuilderCustomizer().customize(defaultProgrammaticDriverConfigLoaderBuilder);
        cqlSessionBuilder.withConfigLoader(defaultProgrammaticDriverConfigLoaderBuilder.build());
        return cqlSessionBuilder;
    }
}

@Bean
public DriverConfigLoaderBuilderCustomizer driverConfigLoaderBuilderCustomizer() {
    return loaderBuilder -> loaderBuilder
        .withString(REQUEST_CONSISTENCY, ConsistencyLevel.LOCAL_QUORUM.name());
}
```

这里我们将一致性级别从 LOCAL_ONE 改成了 LOCAL_QUARM，更符合我们的实际产品部署和应用情况。







