> Java 业务开发常见错误 100 例--朱晔

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





