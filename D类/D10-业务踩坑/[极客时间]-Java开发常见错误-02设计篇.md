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

















