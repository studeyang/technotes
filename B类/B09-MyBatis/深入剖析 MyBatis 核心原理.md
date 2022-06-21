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

## 04 | MyBatis 反射工具箱：带你领略不一样的反射设计思路

反射工具箱的具体代码实现位于 org.apache.ibatis.reflection 包中。下面我们就一起深入分析该模块的核心实现。

**Reflector**

Reflector 是 MyBatis 反射模块的基础。要使用反射模块操作一个 Class，都会先将该 Class 封装成一个 Reflector 对象。

> [Reflector.java](https://github.com/dbses/mybatis-3.5.6/blob/master/src/main/java/org/apache/ibatis/reflection/Reflector.java)

- 核心方法

在 331 行出现了 `currentMethod.isBridge()`：

```java
private void addUniqueMethods(Map<String, Method> uniqueMethods, Method[] methods)
    for (Method currentMethod : methods) {
        if (!currentMethod.isBridge()) {
            // 值样例：java.lang.String#addGetMethods:java.lang.Class
            String signature = getSignature(currentMethod);
            // check to see if the method is already known
            // if it is known, then an extended class must have
            // overridden a method
            if (!uniqueMethods.containsKey(signature)) {
                uniqueMethods.put(signature, currentMethod);
            }
        }
    }
}
```

> 这篇文章解释了桥接方法：https://blog.csdn.net/liu20111590/article/details/81294362

- Invoker

在 Reflector 对象的初始化过程中，所有属性的 getter/setter 方法都会被封装成 MethodInvoker 对象，没有 getter/setter 的字段也会生成对应的 Get/SetFieldInvoker 对象。下面我们就来看看这个 Invoker 接口的定义：

```java
public interface Invoker {
   // 调用底层封装的Method方法或是读写指定的字段
   Object invoke(Object target, Object[] args);
   Class<?> getType(); // 返回属性的类型
}
```

Invoker 接口的继承关系如下图所示：

![image-20220616213607612](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206162136798.png)

- ReflectorFactory

通过上面的分析我们知道，Reflector 初始化过程会有一系列的反射操作，为了提升 Reflector 的初始化速度，MyBatis 提供了 ReflectorFactory 这个工厂接口对 Reflector 对象进行缓存，其中最核心的方法是用来获取 Reflector 对象的 findForClass() 方法。

**DefaultObjectFactory 默认对象工厂**

ObjectFactory 是 MyBatis 中的反射工厂，DefaultObjectFactory 是 ObjectFactory 接口的默认实现，其 create() 方法会选择合适的构造函数实例化对象。

除了使用 DefaultObjectFactory 这个默认实现之外，我们还可以在 mybatis-config.xml 配置文件中配置自定义 ObjectFactory 接口扩展实现类，完成自定义的功能扩展。

**reflection.property 包下的属性解析工具**

PropertyTokenizer 工具类负责解析由“.”和“[]”构成的表达式。PropertyTokenizer 继承了 Iterator 接口，可以迭代处理嵌套多层表达式。

PropertyCopier 是一个属性拷贝的工具类，提供了与 Spring 中 BeanUtils.copyProperties() 类似的功能，实现相同类型的两个对象之间的属性值拷贝，其核心方法是 copyBeanProperties() 方法。

PropertyNamer 工具类提供的功能是转换方法名到属性名，以及检测一个方法名是否为 getter 或 setter 方法。

**MetaClass**

MetaClass 中封装的是 Class 元信息。提供了获取类中属性描述信息的功能，底层依赖前面介绍的 Reflector。

**ObjectWrapper**

ObjectWrapper 封装的是对象元信息。实现了读写对象属性值、检测 getter/setter 等基础功能。实现类如下图所示：

![image-20220616215821025](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206162158152.png)

## 05 | 类型转换：数据库类型体系与 Java 类型体系之间的“爱恨情仇”

JDBC 的数据类型与 Java 语言中的数据类型虽然有点对应关系，但还是无法做到一一对应，也自然无法做到自动映射。

| 数据库类型         | Java类型             |
| ------------------ | -------------------- |
| VARCHAR            | Java.lang.String     |
| CHAR               | Java.lang.String     |
| BLOB               | Java.lang.byte[]     |
| INTEGER UNSIGNED   | Java.lang..Long      |
| TINYINT UNSIGNED   | Java.lang.Integer    |
| SMALLINT UNSIGNED  | Java.lang.Integer    |
| MEDIUMINT UNSIGNED | Java.lang.Integer    |
| BIT                | Java.lang.Boolean    |
| BIGINT UNSIGNED    | Java.math.BigInteger |
| FLOAT              | Java.lang.Float      |
| DOUBLE             | Java.lang.Double     |
| DECIMAL            | Java.math.BigDecimal |

在 MyBatis 中，可以使用类型转换器类型转换，如下图所示：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206172141413.png" alt="img" style="zoom: 33%;" />

**深入 TypeHandler**

类型转换器到底是怎么定义的呢？其实，MyBatis 中的类型转换器就是 TypeHandler 这个接口，其定义如下：

```java
public interface TypeHandler<T> {
  void setParameter(PreparedStatement ps, int i, T parameter, JdbcType jdbcType) throws SQLException;
  T getResult(ResultSet rs, String columnName) throws SQLException;
  T getResult(ResultSet rs, int columnIndex) throws SQLException;
  T getResult(CallableStatement cs, int columnIndex) throws SQLException;
}
```

MyBatis 中定义了 BaseTypeHandler 抽象类来实现一些 TypeHandler 的公共逻辑，BaseTypeHandler 在实现 TypeHandler 的同时，还实现了 TypeReference 抽象类。其继承关系如下图所示：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206172146283.png" alt="image-20220617214600114" style="zoom:50%;" />

在 BaseTypeHandler 中，简单实现了 TypeHandler 接口的 setParameter() 方法和 getResult() 方法。下图展示了 BaseTypeHandler 的全部实现类：

![image-20220617214838819](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206172148975.png)

**TypeHandler 注册与查询**

了解了 TypeHandler 接口实现类的核心原理之后，我们就来思考下面两个问题：

- MyBatis 如何管理这么多的 TypeHandler 接口实现呢？

MyBatis 会在初始化过程中，获取所有已知的 TypeHandler（包括内置实现和自定义实现），然后创建所有 TypeHandler 实例并注册到 TypeHandlerRegistry 中，由 TypeHandlerRegistry 统一管理所有 TypeHandler 实例。

- 如何在合适的场景中使用合适的 TypeHandler 实现进行类型转换呢？

该功能的具体实现是在 TypeHandlerRegistry 的 getTypeHandler() 方法中，会根据传入的 Java 类型和 JDBC 类型，从底层的几个集合中查询相应的 TypeHandler 实例。

**别名管理**

在 mybatis-config.xml 配置文件中可以使用 \<typeAlias\> 标签为 Customer 等 Java 类的完整名称定义了相应的别名，后续编写 SQL 语句、定义 \<resultMap\> 的时候，直接使用这些别名即可完全替代相应的完整 Java 类名，这样就非常易于代码的编写和维护。

TypeAliasRegistry 是维护别名配置的核心实现所在，其中提供了别名注册、别名查询的基本功能。

## 06 | 日志框架千千万，MyBatis 都能兼容的秘密是什么？

MyBatis 使用的日志接口是自己定义的 Log 接口，但是 Apache Commons Logging、Log4j、Log4j2 等日志框架提供给用户的都是自己的 Logger 接口。

为了统一这些第三方日志框架，MyBatis 使用适配器模式添加了针对不同日志框架的 Adapter 实现，使得第三方日志框架的 Logger 接口转换成 MyBatis 中的 Log 接口，从而实现集成第三方日志框架打印日志的功能。

适配器模式如下图所示：

![image-20220620223954393](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206202239662.png)

下面我们就来看看该模块的具体实现。

**日志模块**

首先是 LogFactory 工厂类，它负责创建 Log 对象。这些 Log 接口的实现类中，就包含了多种第三方日志框架的适配器，如下图所示：

![image-20220620225926870](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206202259063.png)

在 LogFactory 类中有如下一段静态代码块，会依次加载各个第三方日志框架的适配器。

```java
static {
    // 尝试按照Slf4j、Common Loggin、Log4j2、Log4j、Jdk Logging、No Logging的顺序，
    // 依次加载对应的适配器，一旦加载成功，就会记录到logConstructor字段中，并会停止后续适配器
    tryImplementation(LogFactory::useSlf4jLogging);
    tryImplementation(LogFactory::useCommonsLogging);
    tryImplementation(LogFactory::useLog4J2Logging);
    tryImplementation(LogFactory::useLog4JLogging);
    tryImplementation(LogFactory::useJdkLogging);
    tryImplementation(LogFactory::useNoLogging);
}
```

**JDBC Logger**

下面我们开始分析 org.apache.ibatis.logging.jdbc 包中的内容。

首先来看其中最基础的抽象类—— BaseJdbcLogger，它是 jdbc 包下其他 Logger 类的父类，继承关系如下图所示：

![image-20220620225404120](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206202254305.png)

从上面的 BaseJdbcLogger 继承关系图中可以看到，BaseJdbcLogger 的子类同时会实现 InvocationHandler 接口。这是 jdk 动态代理。

代理模式如下所示：

![image-20220620231729319](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206202317471.png)

ConnectionLogger 代理了 Connection 的方法执行，打印了一些执行 sql 日志；

ResultSetLogger 代理了 ResultSet 的方法执行，记录了 ResultSet 中的行数。

## 07 | 深入数据源和事务，把握持久化框架的两个关键命脉

作为一款成熟的持久化框架，MyBatis 不仅自己提供了一套数据源实现，而且还能够方便地集成第三方数据源。

MyBatis 提供了两种类型的数据源实现，分别是 PooledDataSource 和 UnpooledDataSource，继承关系如下图所示：

![image-20220621224022707](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206212240915.png)

针对不同的 DataSource 实现，MyBatis 提供了不同的工厂实现来进行创建，如下图所示，这是工厂方法模式的一个典型应用场景。

![image-20220621224158026](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206212241156.png)

MyBatis 对数据库事务抽象了一层 Transaction 接口，它可以管理事务的开启、提交和回滚。

**数据源工厂**

DataSourceFactory 接口中最核心的方法是 getDataSource() 方法，该方法用来生成一个 DataSource 对象。

![image-20220621224402718](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206212244883.png)

在 UnpooledDataSourceFactory 这个实现类的初始化过程中，会直接创建 UnpooledDataSource 对象，其中的 dataSource 字段会指向该 UnpooledDataSource 对象。接下来调用的 setProperties() 方法会根据传入的配置信息，完成对该 UnpooledDataSource 对象相关属性的设置。

PooledDataSourceFactory 是通过继承 UnpooledDataSourceFactory 间接实现了 DataSourceFactory 接口。在 PooledDataSourceFactory 中并没有覆盖 UnpooledDataSourceFactory 中的任何方法，唯一的变化就是将 dataSource 字段指向的 DataSource 对象类型改为 PooledDataSource 类型。

**DataSource**

MyBatis 提供的数据源实现有两个，一个 UnpooledDataSource 实现，另一个 PooledDataSource 实现。

- UnpooledDataSource

MyBatis 的 UnpooledDataSource 实现中定义了如下静态代码块，从而在 UnpooledDataSource 加载时，将已在 DriverManager 中注册的 JDBC 驱动器实例复制一份到 UnpooledDataSource.registeredDrivers 集合中。

```java
static {
    // 从DriverManager中读取JDBC驱动
    Enumeration<Driver> drivers = DriverManager.getDrivers();
    while (drivers.hasMoreElements()) {
        Driver driver = drivers.nextElement();
        // 将DriverManager中的全部JDBC驱动记录到registeredDrivers集合
        registeredDrivers.put(driver.getClass().getName(), driver);
    }
}
```

在 getConnection() 方法中，UnpooledDataSource 会调用 doGetConnection() 方法获取数据库连接，具体实现如下：

```java
private Connection doGetConnection(Properties properties) throws SQLException {
    // 初始化数据库驱动
    initializeDriver();
    // 创建数据库连接
    Connection connection = DriverManager.getConnection(url, properties);
    // 配置数据库连接
    configureConnection(connection);
    return connection;
}
```

这里需要注意两个方法：

在调用的 initializeDriver() 方法中，完成了 JDBC 驱动的初始化，其中会创建配置中指定的 Driver 对象，并将其注册到 DriverManager 以及上面介绍的 UnpooledDataSource.registeredDrivers 集合中保存；

configureConnection() 方法会对数据库连接进行一系列配置，例如，数据库连接超时时长、事务是否自动提交以及使用的事务隔离级别。

- PooledDataSource

JDBC 连接的创建是非常耗时的，从数据库这一侧看，能够建立的连接数也是有限的，所以在绝大多数场景中，我们都需要使用数据库连接池来缓存、复用数据库连接。

> 因此，在设置数据库连接池的最大连接数以及最大空闲连接数时，需要进行折中和权衡，当然也要执行一些性能测试来辅助我们判断。

在 PooledDataSource 中并没有直接维护数据库连接的集合，而是维护了一个 PooledState 类型的字段（state 字段），而这个 PooledState 才是管理连接的地方。在 PooledState 中维护的数据库连接并不是真正的数据库连接（不是 java.sql.Connection 对象），而是 PooledConnection 对象。

**事务接口**

MyBatis 专门抽象出来一个 Transaction 接口，Transaction 接口是 MyBatis 中对数据库事务的抽象，其中定义了提交事务、回滚事务，以及获取事务底层数据库连接的方法。

![image-20220621233947614](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206212339797.png)

TransactionFactory 是用于创建 Transaction 的工厂接口，其中最核心的方法是 newTransaction() 方法，它会根据数据库连接或数据源创建 Transaction 对象。

JdbcTransactionFactory 和 ManagedTransactionFactory 是 TransactionFactory 的两个实现类，分别用来创建 JdbcTransaction 对象和 ManagedTransaction 对象。

JdbcTransaction 都是通过 java.sql.Connection 的同名方法实现事务的提交和回滚的。

ManagedTransaction 的实现相较于 JdbcTransaction 来说，有些许类似，也是依赖关联的 DataSource 获取数据库连接，但其 commit()、rollback() 方法都是空实现，事务的提交和回滚都是依靠容器管理的，这也是它被称为 ManagedTransaction 的原因。 







# 模块三：核心处理层





# 模块四：扩展延伸















