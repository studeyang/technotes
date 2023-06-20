# Web服务层

# 11 | 构建一个 RESTful 风格的 Web 服务

**理解 RESTful 架构风格**

REST（Representational State Transfer，表述性状态转移）这种架构风格把位于服务器端的访问入口看作一个资源，在传输协议上使用标准的 HTTP 方法，比如最常见的 GET、PUT、POST 和 DELETE。

下表展示了 RESTful 风格的一些具体示例：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210410220238.png" alt="image-20210410220238139"  />

对于 RESTful 风格设计 HTTP 端点，业界也存在一些约定。以 Account 这个领域实体为例，如果我们把它视为一种资源，那么 HTTP 端点的根节点命名上通常采用复数形式，即“/accounts”。

在设计 RESTful API 时，针对常见的 CRUD 操作，下图展示了 RESTful API 与非 RESTful API 的一些区别。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210410221357.png" alt="image-20210410221357316" style="zoom:50%;" />

**使用基础注解**

- @RestController

@RestController 注解继承自 Spring MVC 中的 @Controller 注解，是一个基于 RESTful 风格的 HTTP 端点，并且会自动使用 JSON 实现 HTTP 请求和响应的序列化/反序列化方式。

- @GetMapping

@GetMapping 的注解的定义与 @RequestMapping 非常类似，只是默认使用了 RequestMethod.GET 指定 HTTP 方法。

**控制请求的输入**

- @PathVariable

@PathVariable 注解用于获取路径参数。即从类似 url/{id} 这种形式的路径中获取 {id} 参数的值。

- @RequestParam

@RequestParam 注解也是用于获取请求中的参数，但是它面向类似 url?id=XXX 这种路径形式。

- @RequestMapping

在 HTTP 协议中，content-type 属性用来指定所传输的内容类型，我们可以通过 @RequestMapping 注解中的 produces 属性来设置这个属性。

- @RequestBody

@RequestBody 注解用来处理 content-type 为 application/json 类型的编码内容，通过 @RequestBody 注解可以将请求体中的 JSON 字符串绑定到相应的 JavaBean 上。

# 12 | 如何使用 RestTemplate 消费 RESTful 服务？

**创建 RestTemplate**

如果我们想创建一个 RestTemplate 对象，最简单且最常见的方法是直接 new 一个该类的实例，如下代码所示：

```java
@Bean
public RestTemplate restTemplate(){
    return new RestTemplate();
}
```

我们查看下 RestTemplate 的无参构造函数，如下代码所示：

```java
public RestTemplate() {
    this.messageConverters.add(new ByteArrayHttpMessageConverter());
    this.messageConverters.add(new StringHttpMessageConverter());
    this.messageConverters.add(new ResourceHttpMessageConverter(false));
    this.messageConverters.add(new SourceHttpMessageConverter<>());
    this.messageConverters.add(new AllEncompassingFormHttpMessageConverter());
 
    //省略其他添加 HttpMessageConverter 的代码
}
```

RestTemplate 的无参构造函数添加了一批用于实现消息转换的 HttpMessageConverter 对象。

RestTemplate 还有另外一个更强大的有参构造函数，如下代码所示：

```java
public RestTemplate(ClientHttpRequestFactory requestFactory) {
    this();
    setRequestFactory(requestFactory);
}
```

可以用来设置 HTTP 请求的超时时间等属性，如下代码所示：

```java
@Bean
public RestTemplate customRestTemplate(){
    HttpComponentsClientHttpRequestFactory httpRequestFactory = new HttpComponentsClientHttpRequestFactory();
    // 连接请求超时时间
    httpRequestFactory.setConnectionRequestTimeout(3000);
    // 连接超时时间
    httpRequestFactory.setConnectTimeout(3000);
    httpRequestFactory.setReadTimeout(3000);

    return new RestTemplate(httpRequestFactory);
}
```

**使用 RestTemplate 访问 Web 服务**

- GET

```java
public <T> T getForObject(URI url, Class<T> responseType)
public <T> T getForObject(String url, Class<T> responseType, Object... uriVariables)
public <T> T getForObject(String url, Class<T> responseType, Map<String, ?> uriVariables)
```

也可以使用 getForEntity 方法返回一个 ResponseEntity 对象。

- POST

```java
Order order = new Order();
order.setOrderNumber("Order0001");
order.setDeliveryAddress("DemoAddress");
ResponseEntity<Order> responseEntity = restTemplate.postForEntity("http://localhost:8082/orders", order, Order.class);
return responseEntity.getBody();
```

postForObject 的操作方式也与此类似。

- exchange

```java
ResponseEntity<Order> result = restTemplate.exchange("http://localhost:8082/orders/{orderNumber}", HttpMethod.GET, null, Order.class, orderNumber);
```

```java
//设置 HTTP Header
HttpHeaders headers = new HttpHeaders();
headers.setContentType(MediaType.APPLICATION_JSON_UTF8);
 
//设置访问参数
HashMap<String, Object> params = new HashMap<>();
params.put("orderNumber", orderNumber);
 
//设置请求 Entity
HttpEntity entity = new HttpEntity<>(params, headers);
ResponseEntity<Order> result = restTemplate.exchange(url, HttpMethod.GET, entity, Order.class);
```

**RestTemplate 其他使用技巧**

- 指定消息转换器

假如，我们希望把支持 Gson 的 GsonHttpMessageConverter 加载到 RestTemplate 中，就可以使用如下所示的代码。

```java
@Bean
public RestTemplate restTemplate() {
    List<HttpMessageConverter<?>> messageConverters = new ArrayList<HttpMessageConverter<?>>();
    messageConverters.add(new GsonHttpMessageConverter());
    RestTemplate restTemplate = new RestTemplate(messageConverters);
    return restTemplate;
}
```

- 设置拦截器

这方面最典型的应用场景是在 Spring Cloud 中通过 @LoadBalanced 注解为 RestTemplate 添加负载均衡机制。我们可以在 LoadBalanceAutoConfiguration 自动配置类中找到如下代码。

```java
@Bean
@ConditionalOnMissingBean
public RestTemplateCustomizer restTemplateCustomizer(
    final LoadBalancerInterceptor loadBalancerInterceptor) {
    return new RestTemplateCustomizer() {
        @Override
        public void customize(RestTemplate restTemplate) {
            List<ClientHttpRequestInterceptor> list = new ArrayList<>(
                    restTemplate.getInterceptors());
            list.add(loadBalancerInterceptor);
            restTemplate.setInterceptors(list);
        }
    };
}
```

- 处理异常

请求状态码不是返回 200 时，RestTemplate 在默认情况下会抛出异常，并中断接下来的操作，如果我们不想采用这个处理过程，那么就需要覆盖默认的 ResponseErrorHandler。示例代码结构如下所示：

```java
RestTemplate restTemplate = new RestTemplate();
 
ResponseErrorHandler responseErrorHandler = new ResponseErrorHandler() {
    @Override
    public boolean hasError(ClientHttpResponse clientHttpResponse) throws IOException {
        return true;
    }

    @Override
    public void handleError(ClientHttpResponse clientHttpResponse) throws IOException {
        //添加定制化的异常处理代码
    }
};
 
restTemplate.setErrorHandler(responseErrorHandler);
```

# 13 | RestTemplate 远程调用的实现原理

RestTemplate 的类层结构，如下图所示：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210412233815.png" alt="image-20210412233815363" style="zoom:50%;" />

整个类层结构清晰地分成两条支线，左边支线用于完成与 HTTP 请求相关的实现机制，而右边支线提供了基于 RESTful 风格的操作入口，并使用了面向对象中的接口和抽象类完成这两部分功能的聚合。

**InterceptingHttpAccessor**

它是一个抽象类，包含的核心变量如下代码所示：

```java
public abstract class InterceptingHttpAccessor extends HttpAccessor {
 
    private final List<ClientHttpRequestInterceptor> interceptors = new ArrayList<>();
 
    private volatile ClientHttpRequestFactory interceptingRequestFactory;
    …
}
```

interceptors 负责设置和管理请求拦截器；interceptingRequestFactory 负责创建客户端 HTTP 请求。

InterceptingHttpAccessor 同样存在一个父类 HttpAccessor：

```java
public abstract class HttpAccessor {
 
    private ClientHttpRequestFactory requestFactory = new SimpleClientHttpRequestFactory();
    …
}
```

HttpAccessor 中创建了 SimpleClientHttpRequestFactory 作为系统默认的 ClientHttpRequestFactory。

**RestOperations**

RestOperations 接口的定义，如下代码所示：

```java
public interface RestOperations {
 
    <T> T getForObject(String url, Class<T> responseType, Object... uriVariables) throws RestClientException;
    <T> ResponseEntity<T> getForEntity(String url, Class<T> responseType, Object... uriVariables) throws RestClientException;

    <T> T postForObject(String url, @Nullable Object request, Class<T> responseType,Object... uriVariables) throws RestClientException;
 
    void put(String url, @Nullable Object request, Object... uriVariables) throws RestClientException;
	 
    void delete(String url, Object... uriVariables) throws RestClientException;
    <T> ResponseEntity<T> exchange(String url, HttpMethod method, @Nullable HttpEntity<?> requestEntity,
	 
    Class<T> responseType, Object... uriVariables) throws RestClientException;
    …
}
```

**RestTemplate 核心执行流程**

我们可以从具备多种请求方式的 exchange 方法入手，该方法的定义如下代码所示：

```java
@Override
public <T> ResponseEntity<T> exchange(String url, 
                                      HttpMethod method,
                                      @Nullable HttpEntity<?> requestEntity, Class<T> responseType, 
                                      Object... uriVariables)
    throws RestClientException {

    //构建请求回调
    RequestCallback requestCallback = httpEntityCallback(requestEntity, responseType);
    //构建响应体抽取器
    ResponseExtractor<ResponseEntity<T>> responseExtractor = responseEntityExtractor(responseType);
    //执行远程调用
    return nonNull(execute(url, method, requestCallback, responseExtractor, uriVariables));
}
```

execute 方法定义如下代码所示：

```java
@Override
@Nullable
public <T> T execute(String url, 
                     HttpMethod method, 
                     @Nullable RequestCallback requestCallback, 
                     @Nullable ResponseExtractor<T> responseExtractor, 
                     Object... uriVariables) throws RestClientException {
    URI expanded = getUriTemplateHandler().expand(url, uriVariables);
    return doExecute(expanded, method, requestCallback, responseExtractor);
}
```

doExecute 方法定义如下代码所示：

```java
protected <T> T doExecute(URI url, 
                          @Nullable HttpMethod method, 
                          @Nullable RequestCallback requestCallback,
                          @Nullable ResponseExtractor<T> responseExtractor) 
    throws RestClientException {
    Assert.notNull(url, "URI is required");
    Assert.notNull(method, "HttpMethod is required");
    ClientHttpResponse response = null;
    try {
        // 1. 创建请求对象
        ClientHttpRequest request = createRequest(url, method);
        if (requestCallback != null) {
            //执行对请求的回调
            requestCallback.doWithRequest(request);
        }
      
        // 2. 获取调用结果
        response = request.execute();
        
        // 3. 处理调用结果
        handleResponse(url, method, response);
        //使用结果提取从结果中提取数据
        return (responseExtractor != null ? responseExtractor.extractData(response) : null);
    } catch (IOException ex) {
        String resource = url.toString();
        String query = url.getRawQuery();
        resource = (query != null ? resource.substring(0, resource.indexOf('?')) : resource);
        throw new ResourceAccessException("I/O error on " 
                                          + method.name() +
                                          " request for \"" + resource + "\": " 
                                          + ex.getMessage(), ex);
    } finally {
        if (response != null) {
            response.close();
        }
    }
}
```

# 消息通信层

# 14 | 使用 KafkaTemplate 集成 Kafka

与 JdbcTemplate 和 RestTemplate 类似，Spring Boot 作为一款支持快速开发的集成性框架，同样提供了一批以 -Template 命名的模板工具类用于实现消息通信。

对于 Kafka 而言，这个工具类就是 KafkaTemplate。

**使用 KafkaTemplate 发送消息**

引入依赖：

```xml
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
</dependency>
```

KafkaTemplate 提供了一系列 send 方法用来发送消息，典型的 send 方法定义如下代码所示：

```java
@Override
public ListenableFuture<SendResult<K, V>> send(String topic, @Nullable V data) {
}
```

**使用 @KafkaListener 注解消费消息**

Kafka 的消费者在消费消息时，需要提供一个监听器（Listener）对某个 Topic 实现监听，从而获取消息。

在 Spring 中提供了一个 @KafkaListener 注解实现监听器，该注解定义如下代码所示：

```java
@Target({ ElementType.TYPE, ElementType.METHOD, ElementType.ANNOTATION_TYPE })
@Retention(RetentionPolicy.RUNTIME)
@MessageMapping
@Documented
@Repeatable(KafkaListeners.class)
public @interface KafkaListener {
    String id() default "";
    String containerFactory() default "";
    //消息 Topic
    String[] topics() default {};
    //Topic 的模式匹配表达式
    String topicPattern() default "";
	  //Topic 分区
    TopicPartition[] topicPartitions() default {};
    String containerGroup() default "";
    String errorHandler() default "";
	  //消息分组 Id
    String groupId() default "";
    boolean idIsGroup() default true;
    String clientIdPrefix() default "";
    String beanRef() default "__listener";
}
```

使用 @KafkaListener 注解时，我们把它直接添加在处理消息的方法上即可，如下代码所示：

```java
@KafkaListener(topics = “demo.topic”)
public void handlerEvent(DemoEvent event) {
    //TODO：添加消息处理逻辑
}
```

此外，还需要在消费者的配置文件中指定用于消息消费的配置项：

```yaml
spring:      
  kafka:
    bootstrap-servers:
    - localhost:9092
    template:
      default-topic: demo.topic
    consumer:
      group-id: demo.group
```

# 15 | 使用 JmsTemplate 集成 ActiveMQ

**JMS 规范**

JMS 规范提供了一批核心接口供开发人员使用，而这些接口构成了客户端的 API 体系，如下图所示：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210413232148.png" alt="image-20210413232148719" style="zoom:50%;" />

JMS 规范存在 ActiveMQ、WMQ、TIBCO 等多种第三方实现方式，其中较主流的是 ActiveMQ。

针对 ActiveMQ，目前有两个实现项目可供选择，一个是经典的 5.x 版本，另一个是下一代的 Artemis。

**使用 JmsTemplate 集成 ActiveMQ**

引入依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-artemis</artifactId>
</dependency>
```

ActiveMQ 消费方式有推送型消费者（Push Consumer）和拉取型消费者（Pull Consumer）。

**使用 JmsTemplate 发送消息**

JmsTemplate 中存在一批 send 方法用来实现消息发送，如下代码所示：

```java
@Override
public void send(MessageCreator messageCreator) throws JmsException {
}
 
@Override
public void send(final Destination destination, final MessageCreator messageCreator) throws JmsException {
}
 
@Override
public void send(final String destinationName, final MessageCreator messageCreator) throws JmsException {
}
```

这些方法提供了一个用于创建消息对象的 MessageCreator 接口。通过 send 方法发送消息的典型实现方式如下代码所示：

```java
public void sendDemoObject(DemoObject demoObject) { 
    jmsTemplate.send("demo.queue", new MessageCreator() { 
        @Override 
        public Message createMessage(Session session) throws JMSException { 
	          return session.createObjectMessage(demoObject); 
 	      } 
}
```

JmsTemplate 还提供了一组更为简便的方法实现消息发送，即 convertAndSend 方法，如下代码所示：

```java
public void sendDemoObject(DemoObject demoObject) {
    jmsTemplate.convertAndSend("demo.queue", demoObject, new MessagePostProcessor() {
        @Override
        public Message postProcessMessage(Message message) throws JMSException {
	          //针对 Message 的处理
            return message;
        } 
});
```

**使用 JmsTemplate 消费消息**

我们先来看一下如何实现拉取型消费模式。

在 JmsTemplate 中提供了一批 receive 方法供我们从 artemis 中拉取消息，如下代码所示：

```java
public Message receive() throws JmsException {
}
 
public Message receive(Destination destination) throws JmsException {
}
 
public Message receive(String destinationName) throws JmsException {
}
```

推模式下的消息消费方法，如下代码所示：

```java
@JmsListener(queues = “demo.queue”)
public void handlerEvent(DemoEvent event) {
    //TODO：添加消息处理逻辑
}
```

# 16 | 使用 RabbitTemplate 集成 RabbitMQ

AMQP（Advanced Message Queuing Protocol）是一个提供统一消息服务的应用层标准高级消息队列规范。

**AMQP 规范**

在 AMQP 规范中存在三个核心组件，分别是交换器（Exchange）、消息队列（Queue）和绑定（Binding）。

如果存在多个 Queue，Exchange 如何知道把消息发送到哪个 Queue 中呢？

消息中包含一个路由键（Routing Key），它由消息发送者产生，并提供给 Exchange 路由这条消息的标准。而 Exchange 会检查 Routing Key，并结合路由算法决定将消息路由发送到哪个 Queue 中。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210415225317.png" alt="image-20210415225316968" style="zoom:50%;" />

上图中，不同的路由算法存在不同的 Exchange 类型，AMQP 规范中指定了直接式交换器（Direct Exchange）、广播式交换器（Fanout Exchange）、主题式交换器（Topic Exchange）和消息头式交换器（Header Exchange）。

**使用 RabbitTemplate 发送消息**

引领依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-amqp</artifactId>
</dependency>
```

配置 RabbitMQ 服务器的地址、端口、用户名和密码等信息，如下代码所示：

```yaml
spring:
  rabbitmq:
    host: 127.0.0.1
    port: 5672
    username: guest
    password: guest
    virtual-host: DemoHost
```

在与业务代码进行集成时，我们需要将业务对象转换为 Message 对象，示例代码如下所示：

```java
public void sendDemoObject(DemoObject demoObject) {
    MessageConverter converter = rabbitTemplate.getMessageConverter();
    MessageProperties props = new MessageProperties();
    Message message = converter.toMessage(demoObject, props);
    rabbitTemplate.send("demo.queue", message);
}
```

也可以使用 RabbitTemplate 的 convertAndSend 方法组进行实现，如下代码所示：

```java
public void sendDemoObject(DemoObject demoObject) { 
    rabbitTemplate.convertAndSend("demo.queue", demoObject); 
}
```

有时候我们需要在消息发送的过程中为消息添加一些属性，如下代码所示：

```java
rabbitTemplate.convertAndSend(“demo.queue”, event, new MessagePostProcessor() {
    @Override
    public Message postProcessMessage(Message message) throws AmqpException {
        //针对 Message 的处理
        return message;
    }
});
```

**使用 RabbitTemplate 消费消息**

在拉模式下，使用 RabbitTemplate 的典型示例如下代码所示：

```java
public DemoEvent receiveEvent() {
    return (DemoEvent) rabbitTemplate.receiveAndConvert(“demo.queue”);
}
```

推模式的实现方法也很简单，如下代码所示：

```java
@RabbitListener(queues = "demo.queue")
public void handlerEvent(DemoEvent event) {
    //TODO：添加消息处理逻辑
}
```

