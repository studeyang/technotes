> Java 业务开发常见错误 100 例--朱晔
>
> 相关源码：https://github.com/JosephZhu1983/java-common-mistakes

# 21 | 代码重复：搞定代码重复的三个绝招

今天，我从业务代码中最常见的三个需求展开，和你聊聊如何使用 Java 中的一些高级特性、设计模式，以及一些工具消除重复代码。

**一、利用工厂模式 + 模板方法模式**

假设要开发一个购物车下单的功能，针对不同用户进行不同处理：

- 普通用户需要收取运费，运费是商品价格的 10%，无商品折扣；
- VIP 用户同样需要收取商品价格 10% 的快递费，但购买两件以上相同商品时，第三件开始享受一定折扣；
- 内部用户可以免运费，无商品折扣。

我们的目标是实现三种类型的购物车业务逻辑，把入参 Map 对象（Key 是商品 ID，Value 是商品数量），转换为出参购物车类型 Cart。

先实现针对普通用户的购物车处理逻辑：

```java
//购物车
@Data
public class Cart {
    //商品清单
    private List < Item > items = new ArrayList < > ();
    //总优惠
    private BigDecimal totalDiscount;
    //商品总价
    private BigDecimal totalItemPrice;
    //总运费
    private BigDecimal totalDeliveryPrice;
    //应付总价
    private BigDecimal payPrice;
}

//购物车中的商品
@Data
public class Item {
    //商品ID
    private long id;
    //商品数量
    private int quantity;
    //商品单价
    private BigDecimal price;
    //商品优惠
    private BigDecimal couponPrice;
    //商品运费
    private BigDecimal deliveryPrice;
}

//普通用户购物车处理
public class NormalUserCart {

    // items: Key 是商品 ID，Value 是商品数量
    public Cart process(long userId, Map < Long, Integer > items) {
        Cart cart = new Cart();
        //把Map的购物车转换为Item列表
        List < Item > itemList = new ArrayList < > ();
        items.entrySet().stream().forEach(entry - > {
            Item item = new Item();
            item.setId(entry.getKey());
            item.setPrice(Db.getItemPrice(entry.getKey()));
            item.setQuantity(entry.getValue());
            itemList.add(item);
        });
        cart.setItems(itemList);
        //处理运费和商品优惠
        itemList.stream().forEach(item - > {
            //运费为商品总价的10%
            item.setDeliveryPrice(item.getPrice()
            	.multiply(BigDecimal.valueOf(item.getQuantity()))
            	.multiply(new BigDecimal("0.1")));
            //无优惠
            item.setCouponPrice(BigDecimal.ZERO);
        });

        //计算商品总价
        cart.setTotalItemPrice(cart.getItems().stream()
        	.map(item - > item.getPrice().multiply(BigDecimal.valueOf(item.getQuantity())))
        	.reduce(BigDecimal.ZERO, BigDecimal::add));
        //计算运费总价
        cart.setTotalDeliveryPrice(cart.getItems().stream()
        	.map(Item::getDeliveryPrice)
        	.reduce(BigDecimal.ZERO, BigDecimal::add));
        //计算总优惠
        cart.setTotalDiscount(cart.getItems().stream()
        	.map(Item::getCouponPrice)
        	.reduce(BigDecimal.ZERO, BigDecimal::add));
        //应付总价=商品总价+运费总价-总优惠
        cart.setPayPrice(cart.getTotalItemPrice()
        	.add(cart.getTotalDeliveryPrice())
        	.subtract(cart.getTotalDiscount()));
        return cart;
    }
}
```

然后实现针对 VIP 用户的购物车逻辑。与普通用户购物车逻辑的不同在于，VIP 用户能享受同类商品多买的折扣。所以，这部分代码只需要额外处理多买折扣部分：

```java
public class VipUserCart {
    public Cart process(long userId, Map < Long, Integer > items) {
        ...
        itemList.stream().forEach(item - > {
            //运费为商品总价的10%
            item.setDeliveryPrice(item.getPrice()
            	.multiply(BigDecimal.valueOf(item.getQuantity()))
            	.multiply(new BigDecimal("0.1")));
            //购买两件以上相同商品，第三件开始享受一定折扣
            if (item.getQuantity() > 2) {
                item.setCouponPrice(item.getPrice()
                    .multiply(BigDecimal.valueOf(100 - Db.getUserCouponPercent(userId)).divide(new BigDecimal("100")))
                    .multiply(BigDecimal.valueOf(item.getQuantity() - 2)));
            } else {
                item.setCouponPrice(BigDecimal.ZERO);
            }
        });
        ...
        return cart;
    }
}
```

最后是免运费、无折扣的内部用户，同样只是处理商品折扣和运费时的逻辑差异：

```java
public class InternalUserCart {
    public Cart process(long userId, Map < Long, Integer > items) {
        ...
        itemList.stream().forEach(item - > {
            //免运费
            item.setDeliveryPrice(BigDecimal.ZERO);
            //无优惠
            item.setCouponPrice(BigDecimal.ZERO);
        });
        ...
        return cart;
    }
}
```

有了三个购物车后，我们就需要根据不同的用户类型使用不同的购物车了。如下代码所示，使用三个 if 实现不同类型用户调用不同购物车的 process 方法：

```java
@GetMapping("wrong")
public Cart wrong(@RequestParam("userId") int userId) {
    //根据用户ID获得用户类型
    String userCategory = Db.getUserCategory(userId);
    //普通用户处理逻辑
    if (userCategory.equals("Normal")) {
        NormalUserCart normalUserCart = new NormalUserCart();
        return normalUserCart.process(userId, items);
    }
    //VIP用户处理逻辑
    if (userCategory.equals("Vip")) {
        VipUserCart vipUserCart = new VipUserCart();
        return vipUserCart.process(userId, items);
    }
    //内部用户处理逻辑
    if (userCategory.equals("Internal")) {
        InternalUserCart internalUserCart = new InternalUserCart();
        return internalUserCart.process(userId, items);
    }
    return null;
}
```

电商的营销玩法是多样的，以后势必还会有更多用户类型，需要更多的购物车。我们就只能不断增加更多的购物车类，一遍一遍地写重复的购物车逻辑、写更多的 if 逻辑吗？

我们用模板方法模式来重构上面代码。

```java
public abstract class AbstractCart {
    //处理购物车的大量重复逻辑在父类实现
    public Cart process(long userId, Map < Long, Integer > items) {
        Cart cart = new Cart();
        List < Item > itemList = new ArrayList < > ();
        items.entrySet().stream().forEach(entry - > {
            Item item = new Item();
            item.setId(entry.getKey());
            item.setPrice(Db.getItemPrice(entry.getKey()));
            item.setQuantity(entry.getValue());
            itemList.add(item);
        });
        cart.setItems(itemList);
        //让子类处理每一个商品的优惠
        itemList.stream().forEach(item - > {
            processCouponPrice(userId, item);
            processDeliveryPrice(userId, item);
        });
        //计算商品总价
        cart.setTotalItemPrice(cart.getItems().stream()
            .map(item - > item.getPrice().multiply(BigDecimal.valueOf(item.getQuantity())))
            .reduce(BigDecimal.ZERO, BigDecimal::add));
        //计算总运费
        cart.setTotalDeliveryPrice(cart.getItems().stream()
            .map(Item::getDeliveryPrice)
            .reduce(BigDecimal.ZERO, BigDecimal::add));
        //计算总折扣
        cart.setTotalDiscount(cart.getItems().stream()
            .map(Item::getCouponPrice)
            .reduce(BigDecimal.ZERO, BigDecimal::add));
        //计算应付价格
        cart.setPayPrice(cart.getTotalItemPrice()
            .add(cart.getTotalDeliveryPrice())
            .subtract(cart.getTotalDiscount()));
        return cart;
    }
    //处理商品优惠的逻辑留给子类实现
    protected abstract void processCouponPrice(long userId, Item item);
    //处理配送费的逻辑留给子类实现
    protected abstract void processDeliveryPrice(long userId, Item item);
}
```

抽象类和三个子类的实现关系图，如下所示：

![image-20240115230125792](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202401152301902.png)

接下来，我们再看看如何能避免三个 if 逻辑。

定义三个购物车子类时，我们在 @Service 注解中对 Bean 进行了命名。既然三个购物车都叫 XXXUserCart，那我们就可以把用户类型字符串拼接 UserCart 构成购物车 Bean 的名称，然后利用 Spring 的 IoC 容器，通过 Bean 的名称直接获取到 AbstractCart，调用其 process 方法即可实现通用。

其实，这就是工厂模式，只不过是借助 Spring 容器实现罢了：

```java
@GetMapping("right")
public Cart right(@RequestParam("userId") int userId) {
    String userCategory = Db.getUserCategory(userId);
    AbstractCart cart = (AbstractCart) applicationContext.getBean(userCategory);
    return cart.process(userId, items);
}
```

这样一来，我们就利用工厂模式 + 模板方法模式，不仅消除了重复代码，还避免了修改既有代码的风险。这就是设计模式中的开闭原则：对修改关闭，对扩展开放。

**二、利用注解 + 反射消除重复代码**

```java
@BankAPI(url = "/bank/pay", desc = "支付接口")
@Data
public class PayAPI extends AbstractAPI {
    @BankAPIField(order = 1, type = "N", length = 20)
    private long userId;
    @BankAPIField(order = 2, type = "M", length = 10)
    private BigDecimal amount;
}
```

**三、利用属性拷贝工具消除重复代码**

```java
ComplicatedOrderDTO orderDTO = new ComplicatedOrderDTO();
ComplicatedOrderDO orderDO = new ComplicatedOrderDO();
orderDO.setAcceptDate(orderDTO.getAcceptDate());
orderDO.setAddress(orderDTO.getAddress());
orderDO.setAddressId(orderDTO.getAddressId());
orderDO.setCancelable(orderDTO.isCancelable());
orderDO.setCommentable(orderDTO.isComplainable()); //属性错误
orderDO.setComplainable(orderDTO.isCommentable()); //属性错误
orderDO.setCancelable(orderDTO.isCancelable());
orderDO.setCouponAmount(orderDTO.getCouponAmount());
orderDO.setCouponId(orderDTO.getCouponId());
orderDO.setCreateDate(orderDTO.getCreateDate());
orderDO.setDirectCancelable(orderDTO.isDirectCancelable());
orderDO.setDeliverDate(orderDTO.getDeliverDate());
orderDO.setDeliverGroup(orderDTO.getDeliverGroup());
orderDO.setDeliverGroupOrderStatus(orderDTO.getDeliverGroupOrderStatus());
orderDO.setDeliverMethod(orderDTO.getDeliverMethod());
orderDO.setDeliverPrice(orderDTO.getDeliverPrice());
orderDO.setDeliveryManId(orderDTO.getDeliveryManId());
orderDO.setDeliveryManMobile(orderDO.getDeliveryManMobile()); //对象错误
orderDO.setDeliveryManName(orderDTO.getDeliveryManName());
orderDO.setDistance(orderDTO.getDistance());
orderDO.setExpectDate(orderDTO.getExpectDate());
orderDO.setFirstDeal(orderDTO.isFirstDeal());
orderDO.setHasPaid(orderDTO.isHasPaid());
orderDO.setHeadPic(orderDTO.getHeadPic());
orderDO.setLongitude(orderDTO.getLongitude());
orderDO.setLatitude(orderDTO.getLongitude()); //属性赋值错误
```

```java
ComplicatedOrderDTO orderDTO = new ComplicatedOrderDTO();
ComplicatedOrderDO orderDO = new ComplicatedOrderDO();
BeanUtils.copyProperties(orderDTO, orderDO, "id");
return orderDO;
```

# 22 | 接口设计：系统间对话的语言，一定要统一

今天，我通过我遇到的实际案例，和你一起看看因为接口设计思路和调用方理解不一致所导致的问题，以及相关的实践经验。

**接口的响应要明确表示接口的处理结果**

我曾遇到过一个处理收单的收单中心项目，下单接口返回的响应体中，包含了 success、code、info、message 等属性，以及二级嵌套对象 data 结构体。在对项目进行重构的时候，我们发现真的是无从入手，接口缺少文档，代码一有改动就出错。

```json
{
    "success": true,
    "code": 5001,
    "info": "Risk order detected",
    "message": "OK",
    "data":
    {
        "orderStatus": "Cancelled",
        "orderId": -1
    }
}
```

这样的结果，让我们非常疑惑：

- 结构体的 code 和 HTTP 响应状态码，是什么关系？
- success 到底代表下单成功还是失败？
- info 和 message 的区别是什么？
- data 中永远都有数据吗？什么时候应该去查询 data？

为了将接口设计得更合理，我们需要考虑如下两个原则：

- 对外隐藏内部实现。虽然说收单服务调用订单服务进行真正的下单操作，但是直接接口其实是收单服务提供的，收单服务不应该“直接”暴露其背后订单服务的状态码、错误描述。
- 设计接口结构时，明确每个字段的含义，以及客户端的处理方式。

基于这两个原则，我们调整一下返回结构体：

```java
@Data
public class APIResponse < T > {
    private boolean success;
    private T data;
    private int code;
    private String message;
}
```

**要考虑接口变迁的版本控制策略**

接口不可能一成不变，需要根据业务需求不断增加内部逻辑。如果做大的功能调整或重构，涉及参数定义的变化或是参数废弃，导致接口无法向前兼容，这时接口就需要有版本的概念。在考虑接口版本策略设计时，我们需要注意的是，最好一开始就明确版本策略，并考虑在整个服务端统一版本策略。

- 第一，版本策略最好一开始就考虑。

比如，确定是通过 URL Path 实现，是通过 QueryString 实现，还是通过 HTTP 头实现。

```java
//通过URL Path实现版本控制
@GetMapping("/v1/api/user")
    public int right1(){
    return 1;
}
//通过QueryString中的version参数实现版本控制
@GetMapping(value = "/api/user", params = "version=2")
public int right2(@RequestParam("version") int version) {
    return 2;
}
//通过请求头中的X - API - VERSION参数实现版本控制
@GetMapping(value = "/api/user", headers = "X-API-VERSION=3")
public int right3(@RequestHeader("X-API-VERSION") int version) {
    return 3;
}
```

这三种方式中，URL Path 的方式最直观也最不容易出错；

- 第二，版本实现方式要统一。

之前，我就遇到过一个 O2O 项目，需要针对商品、商店和用户实现 REST 接口。虽然大家约定通过 URL Path 方式实现 API 版本控制，但实现方式不统一，有的是 /api/item/v1，有的是 /api/v1/shop，还有的是 /v1/api/merchant。

显然，商品、商店和商户的接口开发同学，没有按照一致的 URL 格式来实现接口的版本控制。

相比于在每一个接口的 URL Path 中设置版本号，更理想的方式是在框架层面实现统一。如果你使用 Spring 框架的话，可以按照下面的方式自定义 RequestMappingHandlerMapping 来实现。

首先，创建一个注解来定义接口的版本。@APIVersion 自定义注解可以应用于方法或 Controller 上：

```java
@Target({ ElementType.METHOD, ElementType.TYPE })
@Retention(RetentionPolicy.RUNTIME)
public @interface APIVersion {
    String[] value();
}
```

然后，定义一个 APIVersionHandlerMapping 类继承 RequestMappingHandlerMapping。

RequestMappingHandlerMapping 的作用，是根据类或方法上的 @RequestMapping 来生成 RequestMappingInfo 的实例。我们覆盖 registerHandlerMethod 方法的实现，从 @APIVersion 自定义注解中读取版本信息，拼接上原有的、不带版本号的 URL Pattern，构成新的 RequestMappingInfo，来通过注解的方式为接口增加基于 URL 的版本号：

```java
public class APIVersionHandlerMapping extends RequestMappingHandlerMapping {
    @Override
    protected boolean isHandler(Class<?> beanType) {
        return AnnotatedElementUtils.hasAnnotation(beanType, Controller.class);
    }

    @Override
    protected void registerHandlerMethod(Object handler, Method method, RequestMappingInfo mapping) {
        Class<?> controllerClass = method.getDeclaringClass();
        APIVersion apiVersion = AnnotationUtils.findAnnotation(controllerClass, APIVersion.class);
        APIVersion methodAnnotation = AnnotationUtils.findAnnotation(method, APIVersion.class);
        //以方法上的注解优先
        if (methodAnnotation != null) {
            apiVersion = methodAnnotation;
        }

        String[] urlPatterns = apiVersion == null ? new String[0] : apiVersion.value();

        PatternsRequestCondition apiPattern = new PatternsRequestCondition(urlPatterns);
        PatternsRequestCondition oldPattern = mapping.getPatternsCondition();
        PatternsRequestCondition updatedFinalPattern = apiPattern.combine(oldPattern);
        mapping = new RequestMappingInfo(mapping.getName(), updatedFinalPattern, mapping.getMethodsCondition(),
                mapping.getParamsCondition(), mapping.getHeadersCondition(), mapping.getConsumesCondition(),
                mapping.getProducesCondition(), mapping.getCustomCondition());
        super.registerHandlerMethod(handler, method, mapping);
    }
}
```

最后，也是特别容易忽略的一点，要通过实现 WebMvcRegistrations 接口，来生效自定义的 APIVersionHandlerMapping：

```java
@SpringBootApplication
public class CommonMistakesApplication implements WebMvcRegistrations {
    @Override
    public RequestMappingHandlerMapping getRequestMappingHandlerMapping() {
        return new APIVersionHandlerMapping();
    }
}
```

这样，就实现了在 Controller 上或接口方法上通过注解，来实现以统一的 Pattern 进行版本号控制：

```java
@Slf4j
@RequestMapping("apiversion")
@RestController
@APIVersion("v1")
public class APIVersoinController {
    @GetMapping(value = "/api/user")
    @APIVersion("v4")
    public int right4() {
        return 4;
    }
}
```

加上注解后，访问浏览器查看效果：

![image-20240118231820325](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202401182318530.png)

使用框架来明确 API 版本的指定策略，不仅实现了标准化，更实现了强制的 API 版本控制。对上面代码略做修改，我们就可以实现不设置 @APIVersion 接口就给予报错提示。

**接口处理方式要明确同步还是异步**

有一个文件上传服务 FileService，其中一个 upload 文件上传接口特别慢，原因是这个上传接口在内部需要进行两步操作，首先上传原图，然后压缩后上传缩略图。如果每一步都耗时 5 秒的话，那么这个接口返回至少需要 10 秒的时间。

于是，开发同学把接口改为了异步处理，每一步操作都限定了超时时间，也就是分别把上传原文件和上传缩略图的操作提交到线程池，然后等待一定的时间：

```java
private ExecutorService threadPool = Executors.newFixedThreadPool(2);

public UploadResponse upload(UploadRequest request) {
    UploadResponse response = new UploadResponse();
    Future<String> uploadFile = threadPool.submit(() -> uploadFile(request.getFile()));
    Future<String> uploadThumbnailFile = threadPool.submit(() -> uploadThumbnailFile(request.getFile()));
    try {
        response.setDownloadUrl(uploadFile.get(1, TimeUnit.SECONDS));
    } catch (Exception e) {
        e.printStackTrace();
    }
    try {
        response.setThumbnailDownloadUrl(uploadThumbnailFile.get(1, TimeUnit.SECONDS));
    } catch (Exception e) {
        e.printStackTrace();
    }
    return response;
}
```

上传接口的请求和响应比较简单，传入二进制文件，传出原文件和缩略图下载地址：

```java
@Data
public class UploadRequest {
    private byte[] file;
}
@Data
public class UploadResponse {
    private String downloadUrl;
    private String thumbnailDownloadUrl;
}
```

到这里，你能看出这种实现方式的问题是什么吗？

从接口命名上看虽然是同步上传操作，但其内部通过线程池进行异步上传，并因为设置了较短超时所以接口整体响应挺快。但是，一旦遇到超时，接口就不能返回完整的数据，不是无法拿到原文件下载地址，就是无法拿到缩略图下载地址，接口的行为变得不可预测：

![image-20240118232625336](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202401182326480.png)

所以，这种优化接口响应速度的方式并不可取，更合理的方式是，让上传接口要么是彻底的同步处理，要么是彻底的异步处理：

- 所谓同步处理，接口一定是同步上传原文件和缩略图的，调用方可以自己选择调用超时，如果来得及可以一直等到上传完成，如果等不及可以结束等待，下一次再重试；
- 所谓异步处理，接口是两段式的，上传接口本身只是返回一个任务 ID，然后异步做上传操作，上传接口响应很快，客户端需要之后再拿着任务 ID 调用任务查询接口查询上传的文件 URL。

同步上传接口的实现代码如下，把超时的选择留给客户端：

```java
public SyncUploadResponse syncUpload(SyncUploadRequest request) {
    SyncUploadResponse response = new SyncUploadResponse();
    response.setDownloadUrl(uploadFile(request.getFile()));
    response.setThumbnailDownloadUrl(uploadThumbnailFile(request.getFile()));
    return response;
}
```

接下来，我们看看异步的上传文件接口如何实现。

```java
//计数器，作为上传任务的ID
private AtomicInteger atomicInteger = new AtomicInteger(0);
//暂存上传操作的结果，生产代码需要考虑数据持久化
private ConcurrentHashMap<String, SyncQueryUploadTaskResponse> downloadUrl = new ConcurrentHashMap<>();
//异步上传操作
public AsyncUploadResponse asyncUpload(AsyncUploadRequest request) {
    AsyncUploadResponse response = new AsyncUploadResponse();
    //生成唯一的上传任务ID
    String taskId = "upload" + atomicInteger.incrementAndGet();
    //异步上传操作只返回任务ID
    response.setTaskId(taskId);
    //提交上传原始文件操作到线程池异步处理
    threadPool.execute(() -> {
        String url = uploadFile(request.getFile());
        downloadUrl.computeIfAbsent(taskId, id -> new SyncQueryUploadTaskResponse(id)).setDownloadUrl(url);
    });
    threadPool.execute(() -> {
        String url = uploadThumbnailFile(request.getFile());
        downloadUrl.computeIfAbsent(taskId, id -> new SyncQueryUploadTaskResponse(id)).setThumbnailDownloadUrl(url)
    });
    return response;
}
```

经过改造的 FileService 不再提供一个看起来是同步上传，内部却是异步上传的 upload 方法，改为提供很明确的：

- 同步上传接口 syncUpload；
- 异步上传接口 asyncUpload，搭配 syncQueryUploadTask 查询上传结果。

使用方可以根据业务性质选择合适的方法：如果是后端批处理使用，那么可以使用同步上传，多等待一些时间问题不大；如果是面向用户的接口，那么接口响应时间不宜过长，可以调用异步上传接口，然后定时轮询上传结果，拿到结果再显示。

# 23 | 缓存设计：缓存可以锦上添花也可以落井下石

> [全栈工程师修炼指南](../D14-行业视角/全栈工程师修炼指南.md)--21 | 赫赫有名的双刃剑：缓存（上）

使用 Redis 做缓存虽然简单好用，但使用和设计缓存并不是 set 一下这么简单，需要注意缓存的同步、雪崩、并发、穿透等问题。今天，我们就来详细聊聊。

**不要把 Redis 当作数据库**

通常，我们会使用 Redis 等分布式缓存数据库来缓存数据，但是千万别把 Redis 当做数据库来使用。我就见过许多案例，因为 Redis 中数据消失导致业务逻辑错误，并且因为没有保留原始数据，业务都无法恢复。

**注意缓存雪崩问题**

由于缓存系统的 IOPS 比数据库高很多，因此要特别小心短时间内大量缓存失效的情况。这种情况一旦发生，可能就会在瞬间有大量的数据需要回源到数据库查询，对数据库造成极大的压力，极限情况下甚至导致后端数据库直接崩溃。这就是我们常说的缓存失效，也叫作缓存雪崩。

从广义上说，产生缓存雪崩的原因有两种：

- 第一种是，缓存系统本身不可用，导致大量请求直接回源到数据库；
- 第二种是，应用设计层面大量的 Key 在同一时间过期，导致大量的数据回源。

第一种原因，主要涉及缓存系统本身高可用的配置，不属于缓存设计层面的问题，所以今天我主要和你说说如何确保大量 Key 不在同一时间被动过期。

解决缓存 Key 同时大规模失效需要回源，导致数据库压力激增问题的方式有两种。

方案一，差异化缓存过期时间，不要让大量的 Key 在同一时间过期。比如，在初始化缓存的时候，设置缓存的过期时间是 30 秒 +10 秒以内的随机延迟（扰动值）。这样，这些Key 不会集中在 30 秒这个时刻过期，而是会分散在 30~40 秒之间过期。

```java
public void rightInit1() {
    IntStream.rangeClosed(1, 1000).forEach(i -> stringRedisTemplate.opsForValue().set("city" + i, getCityFromDb(i), 30 + ThreadLocalRandom.current().nextInt(10), TimeUnit.SECONDS));
    log.info("Cache init finished");
    Executors.newSingleThreadScheduledExecutor().scheduleAtFixedRate(() -> {
        log.info("DB QPS : {}", atomicInteger.getAndSet(0));
    }, 0, 1, TimeUnit.SECONDS);
}
```

方案二，让缓存不主动过期。初始化缓存数据的时候设置缓存永不过期，然后启动一个后台线程 30 秒一次定时把所有数据更新到缓存，而且通过适当的休眠，控制从数据库更新数据的频率，降低数据库压力。

```java
@PostConstruct
public void rightInit2() throws InterruptedException {
    CountDownLatch countDownLatch = new CountDownLatch(1);
    Executors.newSingleThreadScheduledExecutor().scheduleAtFixedRate(() -> {
        IntStream.rangeClosed(1, 1000).forEach(i -> {
            String data = getCityFromDb(i);
            //模拟更新缓存需要一定的时间
            try {
                TimeUnit.MILLISECONDS.sleep(20);
            } catch (InterruptedException e) {
            }
            if (!StringUtils.isEmpty(data)) {
                //缓存永不过期，被动更新
                stringRedisTemplate.opsForValue().set("city" + i, data);
            }
        });
        log.info("Cache update finished");
        countDownLatch.countDown();
    }, 0, 30, TimeUnit.SECONDS);
    Executors.newSingleThreadScheduledExecutor().scheduleAtFixedRate(() -> {
        log.info("DB QPS : {}", atomicInteger.getAndSet(0));
    }, 0, 1, TimeUnit.SECONDS);
    countDownLatch.await();
}
```

关于这两种解决方案，我们需要特别注意以下三点：

- 方案一和方案二是截然不同的两种缓存方式，如果无法全量缓存所有数据，那么只能使用方案一；
- 即使使用了方案二，缓存永不过期，同样需要在查询的时候，确保有回源的逻辑。正如之前所说，我们无法确保缓存系统中的数据永不丢失。
- 不管是方案一还是方案二，在把数据从数据库加入缓存的时候，都需要判断来自数据库的数据是否合法，比如进行最基本的判空检查。

之前我就遇到过这样一个重大事故，某系统会在缓存中对基础数据进行长达半年的缓存，在某个时间点 DBA 把数据库中的原始数据进行了归档（可以认为是删除）操作。因为缓存中的数据一直在所以一开始没什么问题，但半年后的一天缓存中数据过期了，就从数据库中查询到了空数据加入缓存，爆发了大面积的事故。

这个案例说明，缓存会让我们更不容易发现原始数据的问题，所以在把数据加入缓存之前一定要校验数据，如果发现有明显异常要及时报警。

**注意缓存击穿问题**

在某些 Key 属于极端热点数据，且并发量很大的情况下，如果这个 Key 过期，可能会在某个瞬间出现大量的并发请求同时回源，相当于大量的并发请求直接打到了数据库。这种情况，就是我们常说的缓存击穿或缓存并发问题。

我们来重现下这个问题。在程序启动的时候，初始化一个热点数据到 Redis 中，过期时间设置为 5 秒，每隔 1 秒输出一下回源的 QPS：

```java
@PostConstruct
public void init() {
    //初始化一个热点数据到Redis中，过期时间设置为5秒
    stringRedisTemplate.opsForValue().set("hotsopt", getExpensiveData(), 5, TimeUnit.SECONDS);
    //每隔1秒输出一下回源的QPS
    Executors.newSingleThreadScheduledExecutor().scheduleAtFixedRate(() -> {
        log.info("DB QPS : {}", atomicInteger.getAndSet(0));
    }, 0, 1, TimeUnit.SECONDS);
}
@GetMapping("wrong")
public String wrong() {
    String data = stringRedisTemplate.opsForValue().get("hotsopt");
    if (StringUtils.isEmpty(data)) {
        data = getExpensiveData();
        //重新加入缓存，过期时间还是5秒
        stringRedisTemplate.opsForValue().set("hotsopt", data, 5, TimeUnit.SECONDS);
    }
    return data;
}
```

可以看到，每隔 5 秒数据库都有 20 左右的 QPS：

![image-20240119224819146](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202401192250306.png)

如果回源操作特别昂贵，那么这种并发就不能忽略不计。这时，我们可以考虑使用锁机制来限制回源的并发。比如如下代码示例，使用 Redisson 来获取一个基于 Redis 的分布式锁，在查询数据库之前先尝试获取锁：

```java
@GetMapping("right")
public String right() {
    String data = stringRedisTemplate.opsForValue().get("hotsopt");
    if (StringUtils.isEmpty(data)) {
        RLock locker = redissonClient.getLock("locker");
        //获取分布式锁
        if (locker.tryLock()) {
            try {
                data = stringRedisTemplate.opsForValue().get("hotsopt");
                //双重检查，因为可能已经有一个B线程过了第一次判断
                if (StringUtils.isEmpty(data)) {
                    //回源到数据库查询
                    data = getExpensiveData();
                    stringRedisTemplate.opsForValue().set("hotsopt", data, 5, TimeUnit.SECONDS);
                }
            } finally {
                locker.unlock();
            }
        }
    }
    return data;
}
```

这样，可以把回源到数据库的并发限制在 1：

![image-20240119225204193](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202401192252344.png)

在真实的业务场景下，不一定要这么严格地使用双重检查分布式锁进行全局的并发限制，因为这样虽然可以把数据库回源并发降到最低，但也限制了缓存失效时的并发。可以考虑的方式是：

- 方案一，使用进程内的锁进行限制，这样每一个节点都可以以一个并发回源数据库；
- 方案二，不使用锁进行限制，而是使用类似 Semaphore 的工具限制并发数，比如限制为 10，这样既限制了回源并发数不至于太大，又能使得一定量的线程可以同时回源。

**注意缓存穿透问题**

在之前的例子中，缓存回源的逻辑都是当缓存中查不到需要的数据时，回源到数据库查询。这里容易出现的一个漏洞是，缓存中没有数据不一定代表数据没有缓存，还有一种可能是原始数据压根就不存在。

比如下面的例子。数据库中只保存有 ID 介于 0（不含）和 10000（包含）之间的用户，如果从数据库查询 ID 不在这个区间的用户，会得到空字符串，所以缓存中缓存的也是空字符串。如果使用 ID=0 去压接口的话，从缓存中查出了空字符串，认为是缓存中没有数据回源查询，其实相当于每次都回源：

如果这种漏洞被恶意利用的话，就会对数据库造成很大的性能压力。这就是缓存穿透。

解决缓存穿透有以下两种方案。

方案一，对于不存在的数据，同样设置一个特殊的 Value 到缓存中，比如当数据库中查出的用户信息为空的时候，设置 NODATA 这样具有特殊含义的字符串到缓存中。这样下次请求缓存的时候还是可以命中缓存，即直接从缓存返回结果，不查询数据库。

但，这种方式可能会把大量无效的数据加入缓存中，如果担心大量无效数据占满缓存的话还可以考虑方案二，即使用布隆过滤器做前置过滤。

布隆过滤器不保存原始值，空间效率很高，平均每一个元素占用 2.4 字节就可以达到万分之一的误判率。这里的误判率是指，过滤器判断值存在而实际并不存在的概率。我们可以设置布隆过滤器使用更大的存储空间，来得到更小的误判率。

你可以把所有可能的值保存在布隆过滤器中，从缓存读取数据前先过滤一次：

- 如果布隆过滤器认为值不存在，那么值一定是不存在的，无需查询缓存也无需查询数据库；
- 对于极小概率的误判请求，才会最终让非法 Key 的请求走到缓存或数据库。

要用上布隆过滤器，我们可以使用 Google 的 Guava 工具包提供的 BloomFilter 类改造一下程序：启动时，初始化一个具有所有有效用户 ID 的、10000 个元素的 BloomFilter，在从缓存查询数据之前调用其 mightContain 方法，来检测用户 ID 是否可能存在；如果布隆过滤器说值不存在，那么一定是不存在的，直接返回：

```java
private BloomFilter<Integer> bloomFilter;

@PostConstruct
public void init() {
    Executors.newSingleThreadScheduledExecutor().scheduleAtFixedRate(() -> {
        log.info("DB QPS : {}", atomicInteger.getAndSet(0));
    }, 0, 1, TimeUnit.SECONDS);
    //创建布隆过滤器，元素数量10000，期望误判率1%
    bloomFilter = BloomFilter.create(Funnels.integerFunnel(), 10000, 0.01);
    IntStream.rangeClosed(1, 10000).forEach(bloomFilter::put);
}

@GetMapping("right2")
public String right2(@RequestParam("id") int id) {
    String data = "";
    //通过布隆过滤器先判断
    if (bloomFilter.mightContain(id)) {
        String key = "user" + id;
        //走缓存查询
        data = stringRedisTemplate.opsForValue().get(key);
        if (StringUtils.isEmpty(data)) {
            //走数据库查询
            data = getCityFromDb(id);
            stringRedisTemplate.opsForValue().set(key, data, 30, TimeUnit.SECONDS);
        }
    }
    return data;
}
```

对于方案二，我们需要同步所有可能存在的值并加入布隆过滤器，这是比较麻烦的地方。如果业务规则明确的话，你也可以考虑直接根据业务规则判断值是否存在。

其实，方案二可以和方案一同时使用，即将布隆过滤器前置，对于误判的情况再保存特殊值到缓存，双重保险避免无效数据查询请求打到数据库。

**注意缓存数据同步策略**

前面提到的 3 个案例，其实都属于缓存数据过期后的被动删除。在实际情况下，修改了原始数据后，考虑到缓存数据更新的及时性，我们可能会采用主动更新缓存的策略。这些策略可能是：

- 先更新缓存，再更新数据库；
- 先更新数据库，再更新缓存；
- 先删除缓存，再更新数据库，访问的时候按需加载数据到缓存；
- 先更新数据库，再删除缓存，访问的时候按需加载数据到缓存。

“先更新数据库再删除缓存，访问的时候按需加载数据到缓存”策略是最好的。虽然在极端情况下，这种策略也可能出现数据不一致的问题，但概率非常低，基本可以忽略。举一个“极端情况”的例子，比如更新数据的时间节点恰好是缓存失效的瞬间，这时 A 先从数据库读取到了旧值，随后在 B 操作数据库完成更新并且删除了缓存之后，A 再把旧值加入缓存。

# 24 | 业务代码写完，就意味着生产就绪了？



**准备工作：配置 Spring Boot Actuator**



**指标 Metrics 是快速定位问题的“金钥匙”**



# 25 | 异步处理好用，但非常容易用错



![image-20240120223000967](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202401202230243.png)



**注意消息模式是广播还是工作队列**



**别让死信堵塞了消息队列**





























