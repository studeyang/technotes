> 来自拉勾教育《深入剖析 MyBatis 核心原理》--杨四正
>
> https://github.com/xxxlxy2008/mybatis

# 模块一：快速入门

## 01 | 常见持久层框架赏析，为什么选择 MyBatis？

从性能角度来看，Hibernate、Spring Data JPA 在对 SQL 语句的掌控、SQL 手工调优、多表连接查询等方面，不及 MyBatis 直接使用原生 SQL 语句方便、高效；

从可移植性角度来看，Hibernate 帮助我们屏蔽了底层数据库方言，Spring Data JPA 帮我们屏蔽了 ORM 的差异，而 MyBatis 因为直接编写原生 SQL，会与具体的数据库完全绑定（但实践中很少有项目会来回切换底层使用的数据库产品或 ORM 框架，所以这点并不是特别重要）；

从开发效率角度来看，Hibernate、Spring Data JPA 处理中小型项目的效率会略高于 MyBatis（这主要还是看需求和开发者技术栈）。

## 02 | 订单系统持久层示例分析，快速上手 MyBatis

**使用场景**

以一个简易订单系统的持久化层为例。domain 设计如下：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206142146511.png)

数据库表设计如下：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206142147613.png)

**使用场景一：一对多查询**

```java
public interface CustomerMapper {
    // 根据用户Id查询Customer(不查询Address)
    Customer find(long id);
    // 根据用户Id查询Customer(同时查询Address)
    Customer findWithAddress(long id);
    // 根据orderId查询Customer
    Customer findByOrderId(long orderId);
    // 持久化Customer对象
    int save(Customer customer);
}
```

```xml
<mapper namespace="org.example.dao.CustomerMapper">
    <!-- 定义映射规则 -->
    <resultMap id="customerSimpleMap" type="Customer">
        <!--  主键映射 -->
        <id property="id" column="id"/>
        <!--  属性映射 -->
        <result property="name" column="name"/>
        <result property="phone" column="phone"/>
    </resultMap>
    <!-- 定义映射规则 -->
    <resultMap id="customerMap" type="Customer">
        <!--  主键映射 -->
        <id property="id" column="id"/>
        <!--  属性映射 -->
        <result property="name" column="name"/>
        <result property="phone" column="phone"/>
        <!-- 映射addresses集合，<collection>标签用于映射集合类的属性，实现一对多的关联关系 -->
        <collection property="addresses" javaType="list" ofType="Address">
            <id property="id" column="address_id"/>
            <result property="street" column="street"/>
            <result property="city" column="city"/>
            <result property="country" column="country"/>
        </collection>
    </resultMap>
    <!-- 定义select语句，CustomerMapper接口中的find()方法会执行该SQL，
        查询结果通过customerSimpleMap这个映射生成Customer对象-->
    <select id="find" resultMap="customerSimpleMap">
        SELECT * FROM t_customer WHERE id = #{id:INTEGER}
    </select>
    <!-- 定义select语句，CustomerMapper接口中的findWithAddress()方法会执行该SQL，
        查询结果通过customerMap这个映射生成Customer对象-->
    <select id="findWithAddress" resultMap="customerMap">
        SELECT c.*,a.id as address_id, a.* FROM t_customer as c join t_address as a
        on c.id = a.customer_id
        WHERE c.id = #{id:INTEGER}
    </select>
    <!-- CustomerMapper接口中的findByOrderId()方法会执行该SQL，
        查询结果通过customerSimpleMap这个映射生成Customer对象-->
    <select id="findByOrderId" resultMap="customerSimpleMap">
        SELECT * FROM t_customer as c join t_order as t
        on c.id = t.customer_id
        WHERE t.customer_id = #{id:INTEGER}
    </select>
    <!-- 定义insert语句，CustomerMapper接口中的save()方法会执行该SQL，
        数据库生成的自增id会自动填充到传入的Customer对象的id字段中-->
    <insert id="save" keyProperty="id" useGeneratedKeys="true">
      insert into t_customer (id, name, phone)
      values (#{id},#{name},#{phone})
    </insert>
</mapper>
```

**使用场景二：一对一查询**

```java
public interface OrderItemMapper {
    // 根据id查询OrderItem对象
    OrderItem find(long id);
    // 查询指定的订单中的全部OrderItem
    List<OrderItem> findByOrderId(long orderId);
    // 保存一个OrderItem信息
    long save(@Param("orderItem")OrderItem orderItem, 
              @Param("orderId") long orderId);
}
```

```xml
<mapper namespace="org.example.dao.OrderItemMapper">
    <!-- 定义t_order_item与OrderItem对象之间的映射关系-->
    <resultMap id="orderItemtMap" type="OrderItem">
        <id property="id" column="id"/>
        <result property="amount" column="amount"/>
        <result property="orderId" column="order_id"/>
        <!--映射OrderItem关联的Product对象，<association>标签用于实现一对一的关联关系-->
        <association property="product" javaType="Product">
            <id property="id" column="product_id"/>
            <result property="name" column="name"/>
            <result property="description" column="description"/>
            <result property="price" column="price"/>
        </association>
    </resultMap>
    <!-- 定义select语句，OrderItemMapper接口中的find()方法会执行该SQL，
        查询结果通过orderItemtMap这个映射生成OrderItem对象-->
    <select id="find" resultMap="orderItemtMap">
        SELECT i.*,p.*,p.id as product_id FROM t_order_item as i join t_product as p
        on i.product_id = p.id WHERE id = #{id:INTEGER}
    </select>
    <!-- 定义select语句，OrderItemMapper接口中的findAll()方法会执行该SQL，
        查询结果通过orderItemtMap这个映射生成OrderItem对象-->
    <select id="findByOrderId" resultMap="orderItemtMap">
        SELECT i.*,p.* FROM t_order_item as i join t_product as p
        on i.product_id = p.id WHERE i.order_id = #{order_id:INTEGER}
    </select>
    <!-- 定义insert语句，OrderItemMapper接口中的save()方法会执行该SQL，
        数据库生成的自增id会自动填充到传入的OrderItem对象的id字段中-->
    <insert id="save" keyProperty="orderItem.id" useGeneratedKeys="true">
      insert into t_order_item (amount, product_id, order_id)
      values (#{orderItem.amount}, #{orderItem.product.id}, #{orderId})
    </insert>
</mapper>
```

**封装DaoUtils工具类**

```java
public class DaoUtils {
    private static SqlSessionFactory factory;
    static { // 在静态代码块中直接读取MyBatis的mybatis-config.xml配置文件
        String resource = "mybatis-config.xml";
        InputStream inputStream = null;
        try {
            inputStream = Resources.getResourceAsStream(resource);
        } catch (IOException e) {
            System.err.println("read mybatis-config.xml fail");
            e.printStackTrace();
            System.exit(1);
        }
        // 加载完mybatis-config.xml配置文件之后，会根据其中的配置信息创建SqlSessionFactory对象
        factory = new SqlSessionFactoryBuilder()
                .build(inputStream);
    }
    public static <R> R execute(Function<SqlSession, R> function) {
        // 创建SqlSession
        SqlSession session = factory.openSession();
        try {
            R apply = function.apply(session);
            // 提交事务
            session.commit();
            return apply;
        } catch (Throwable t) {
            // 出现异常的时候，回滚事务
            session.rollback(); 
            System.out.println("execute error");
            throw t;
        } finally {
            // 关闭SqlSession
            session.close();
        }
    }
}
```

在 DaoUtils 中加载的 mybatis-config.xml 配置文件位于 /resource 目录下，是 MyBatis 框架配置的入口，具体定义如下所示：

```xml
<configuration>
    <properties> <!-- 定义属性值 -->
        <property name="username" value="root"/>
        <property name="id" value="xxx"/>
    </properties>
    <settings><!-- 全局配置信息 -->
        <setting name="cacheEnabled" value="true"/>
    </settings>
    <typeAliases>
        <!-- 配置别名信息，在映射配置文件中可以直接使用Customer这个别名
            代替org.example.domain.Customer这个类 -->
        <typeAlias type="org.example.domain.Customer" alias="Customer"/>
        <typeAlias type="org.example.domain.Address" alias="Address"/>
        <typeAlias type="org.example.domain.Order" alias="Order"/>
        <typeAlias type="org.example.domain.OrderItem" alias="OrderItem"/>
        <typeAlias type="org.example.domain.Product" alias="Product"/>
    </typeAliases>
    <environments default="development">
        <environment id="development">
            <!-- 配置事务管理器的类型 -->
            <transactionManager type="JDBC"/>
            <!-- 配置数据源的类型，以及数据库连接的相关信息 -->
            <dataSource type="POOLED">
                <property name="driver" value="com.mysql.jdbc.Driver"/>
                <property name="url" value="jdbc:mysql://localhost:3306/test"/>
                <property name="username" value="root"/>
                <property name="password" value="xxx"/>
            </dataSource>
        </environment>
    </environments>
    <!-- 配置映射配置文件的位置 -->
    <mappers>
        <mapper resource="mapper/CustomerMapper.xml"/>
        <mapper resource="mapper/AddressMapper.xml"/>
        <mapper resource="mapper/OrderItemMapper.xml"/>
        <mapper resource="mapper/OrderMapper.xml"/>
        <mapper resource="mapper/ProductMapper.xml"/>
    </mappers>
</configuration>
```

使用示例：

```java
public class CustomerService {
    // 创建一个新用户
    public long register(String name, String phone) {
        // 检查传入的name参数以及phone参数是否合法
        Preconditions.checkArgument(!Strings.isNullOrEmpty(name), "name is empty");
        Preconditions.checkArgument(!Strings.isNullOrEmpty(phone), "phone is empty");
        // 我们还可以完成其他业务逻辑，例如检查用户名是否重复、手机号是否重复等，这里不再展示
        return DaoUtils.execute(sqlSession -> {
            // 创建Customer对象，并通过CustomerMapper.save()方法完成持久化
            CustomerMapper mapper = sqlSession.getMapper(CustomerMapper.class);
            Customer customer = new Customer();
            customer.setName(name);
            customer.setPhone(phone);
            int affected = mapper.save(customer);
            if (affected <= 0) {
                throw new RuntimeException("Save Customer fail...");
            }
            return customer.getId();
        });
    }
}
```

## 03 | MyBatis 整体架构解析

**MyBatis 架构简介**

MyBatis 分为三层架构，分别是基础支撑层、核心处理层和接口层，如下图所示：

![image-20220615212517663](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206152125788.png)

**基础支撑层**

MyBatis 基础支撑层可以划分为上图所示的九个基础模块。

- 资源加载模块

- 类型转换模块：实现了 MyBatis 中 JDBC 类型与 Java 类型之间的相互转换。

- 日志模块：集成 Java 生态中的第三方日志框架。

- 反射工具模块：在 Java 反射的基础之上进行的一层封装。

- Binding 模块：我们无须编写 Mapper 接口的具体实现，而是利用 Binding 模块自动生成 Mapper 接口的动态代理对象。

- 数据源模块：MyBatis 的数据源模块提供了一套数据源实现，也提供了与第三方数据源集成的相关接口。

- 缓存模块：MyBatis 提供了一级缓存和二级缓存。

  ![image-20220615213830981](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206152138111.png)

- 解析器模块：MyBatis 中有 mybatis-config.xml，Mapper.xml 两部分配置文件需要进行解析。

- 事务管理模块：MyBatis 对数据库中的事务进行了一层简单的抽象，提供了简单易用的事务接口和实现。

**核心处理层**

核心处理层是 MyBatis 核心实现所在，其中涉及 MyBatis 的初始化以及执行一条 SQL 语句的全流程。

![image-20220615212517663](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206152125788.png)

- 配置解析

MyBatis 有三处可以添加配置信息的地方，分别是：mybatis-config.xml 配置文件、Mapper.xml 配置文件以及 Mapper 接口中的注解信息。在 MyBatis 初始化过程中，会加载这些配置信息，并将解析之后得到的配置对象保存到 Configuration 对象中。

- SQL 解析与 scripting 模块

MyBatis 中的 scripting 模块就是负责动态生成 SQL 的核心模块。它会根据运行时用户传入的实参，解析动态 SQL 中的标签，并形成 SQL 模板，然后处理 SQL 模板中的占位符，用运行时的实参填充占位符，得到数据库真正可执行的 SQL 语句。

- SQL 执行

在 MyBatis 中，要执行一条 SQL 语句，会涉及非常多的组件，比较核心的有：Executor、StatementHandler、ParameterHandler 和 ResultSetHandler。下图展示了 MyBatis 执行一条 SQL 语句的核心过程：

![image-20220615212854829](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206152128946.png)

- 插件

很多成熟的开源框架，都会以各种方式提供扩展能力。当框架原生能力不能满足某些场景的时候，就可以针对这些场景实现一些插件来满足需求，这样的框架才能有足够的生命力。这也是 MyBatis 插件接口存在的意义。

**接口层**

接口层是 MyBatis 暴露给调用的接口集合，这些接口都是使用 MyBatis 时最常用的一些接口，例如，SqlSession 接口、SqlSessionFactory 接口等。

其中，最核心的是 SqlSession 接口，你可以通过它实现很多功能，例如，获取 Mapper 代理、执行 SQL 语句、控制事务开关等。

# 模块二：基础支撑层





# 模块三：核心处理层





# 模块四：扩展延伸















