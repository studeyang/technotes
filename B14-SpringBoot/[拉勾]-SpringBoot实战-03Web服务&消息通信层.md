# Web服务层

# 11 | 构建一个 RESTful 风格的 Web 服务

**理解 RESTful 架构风格**

REST（Representational State Transfer，表述性状态转移）这种架构风格把位于服务器端的访问入口看作一个资源，在传输协议上使用标准的 HTTP 方法，比如最常见的 GET、PUT、POST 和 DELETE。

下表展示了 RESTful 风格的一些具体示例：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210410220238.png" alt="image-20210410220238139"  />

对于 RESTful 风格设计 HTTP 端点，业界也存在一些约定。以 Account 这个领域实体为例，如果我们把它视为一种资源，那么 HTTP 端点的根节点命名上通常采用复数形式，即“/accounts”。

在设计 RESTful API 时，针对常见的 CRUD 操作，下图展示了 RESTful API 与非 RESTful API 的一些区别。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210410221357.png" alt="image-20210410221357316" style="zoom:50%;" />

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









