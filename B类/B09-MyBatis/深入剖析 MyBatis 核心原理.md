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

## 08 | Mapper 文件与 Java 接口的优雅映射之道

- 为什么需要 CustomerMapper 接口来执行对应的 SQL 语句呢？
- 为什么无须提供 CustomerMapper 接口的实现类呢？
- 实际使用的 CustomerMapper 对象是什么呢？CustomerMapper 对象是怎么创建的呢？底层原理是什么呢？

学习完这一讲，你就会找到这些问题的答案。

在 MyBatis 中，实现 CustomerMapper 接口与 CustomerMapper.xml 配置文件映射功能的是 binding 模块，其中涉及的核心类如下图所示：

![image-20220622220952236](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206222209513.png)

下面我们就开始详细分析 binding 模块中涉及的这些核心组件。

**MapperRegistry**

MapperRegistry 是 MyBatis 初始化过程中构造的一个对象，主要作用就是统一维护 Mapper 接口以及这些 Mapper 的代理对象工厂。

MapperRegistry 中的核心字段如下。

```text
config（Configuration 类型）：指向 MyBatis 全局唯一的 Configuration 对象，其中维护了解析之后的全部 MyBatis 配置信息。
knownMappers（Map<Class<?>, MapperProxyFactory<?>> 类型）：维护了所有解析到的 Mapper 接口以及 MapperProxyFactory 工厂对象之间的映射关系。
```

在我们使用 CustomerMapper.find() 方法执行数据库查询的时候，MyBatis 会先从MapperRegistry 中获取 CustomerMapper 接口的代理对象，这里就使用到 MapperRegistry.getMapper()方法，它会拿到 MapperProxyFactory 工厂对象，并调用其 newInstance() 方法创建 Mapper 接口的代理对象。

**MapperProxyFactory**

MapperProxyFactory 的核心功能就是创建 Mapper 接口的代理对象，其底层核心原理就是 JDK 动态代理。

MapperProxyFactory 的 newInstance() 方法创建代理对象过程如下。

```java
protected T newInstance(MapperProxy<T> mapperProxy) {
    // 创建实现了mapperInterface接口的动态代理对象，这里使用的InvocationHandler 实现是MapperProxy
    return (T) Proxy.newProxyInstance(mapperInterface.getClassLoader(),
            new Class[]{mapperInterface}, mapperProxy);
}
```

**MapperProxy**

MapperProxy 是生成 Mapper 接口代理对象的关键，它实现了 InvocationHandler 接口。

这里涉及 MethodHandle 的内容，所以下面我们就来简单介绍一下 MethodHandle 的基础知识点。

- MethodHandle 简介

从 Java 7 开始，除了反射之外，在 java.lang.invoke 包中新增了 MethodHandle 这个类，它的基本功能与反射中的 Method 类似，但它比反射更加灵活。

使用 MethodHandle 进行方法调用的时候，往往会涉及下面几个核心步骤：

1. 创建 MethodType 对象，确定方法的签名，这个签名会涉及方法参数及返回值的类型；
2. 在 MethodHandles.Lookup 这个工厂对象中，根据方法名称以及上面创建的 MethodType 查找对应 MethodHandle 对象；
3. 将 MethodHandle 绑定到一个具体的实例对象；
4. 调用 MethodHandle.invoke()/invokeWithArguments()/invokeExact() 方法，完成方法调用。

下面是 MethodHandle 的一个简单示例：

```java
public class MethodHandleDemo {
    // 定义一个sayHello()方法
    public String sayHello(String s) {
        return "Hello, " + s;
    }
    public static void main(String[] args) throws Throwable {
        // 初始化MethodHandleDemo实例
        MethodHandleDemo subMethodHandleDemo = new SubMethodHandleDemo();
        // 定义sayHello()方法的签名，第一个参数是方法的返回值类型，第二个参数是方法的参数列表
        MethodType methodType = MethodType.methodType(String.class, String.class);
        // 根据方法名和MethodType在MethodHandleDemo中查找对应的MethodHandle
        MethodHandle methodHandle = MethodHandles.lookup()
                .findVirtual(MethodHandleDemo.class, "sayHello", methodType);
        // 将MethodHandle绑定到一个对象上，然后通过invokeWithArguments()方法传入实参并执行
        System.out.println(methodHandle.bindTo(subMethodHandleDemo)
                .invokeWithArguments("MethodHandleDemo"));
        // 下面是调用MethodHandleDemo对象(即父类)的方法
        MethodHandleDemo methodHandleDemo = new MethodHandleDemo();
        System.out.println(methodHandle.bindTo(methodHandleDemo)
                .invokeWithArguments("MethodHandleDemo"));
    }
    public static class SubMethodHandleDemo extends MethodHandleDemo{
        // 定义一个sayHello()方法
        public String sayHello(String s) {
            return "Sub Hello, " + s;
        }
    }
}
```

- MethodProxy 中的代理逻辑

介绍完 MethodHandle 的基础之后，我们回到 MethodProxy 继续分析。

MapperProxy.invoke() 方法是代理对象执行的入口，其中会拦截所有非 Object 方法，针对每个被拦截的方法，都会调用 cachedInvoker() 方法获取对应的 MapperMethod 对象，并调用其 invoke() 方法执行代理逻辑以及目标方法。

```java
private MapperMethodInvoker cachedInvoker(Method method) throws Throwable {
    // 尝试从methodCache缓存中查询方法对应的MapperMethodInvoker
    MapperMethodInvoker invoker = methodCache.get(method);
    if (invoker != null) {
        return invoker;
    }
    // 如果方法在缓存中没有对应的MapperMethodInvoker，则进行创建
    return methodCache.computeIfAbsent(method, m -> {
        if (m.isDefault()) { // 针对default方法的处理
            // 这里根据JDK版本的不同，获取方法对应的MethodHandle的方式也有所不同
            // 在JDK 8中使用的是lookupConstructor字段，而在JDK 9中使用的是
            // privateLookupInMethod字段。获取到MethodHandle之后，会使用
            // DefaultMethodInvoker进行封装
            if (privateLookupInMethod == null) {
                return new DefaultMethodInvoker(getMethodHandleJava8(method));
            } else {
                return new DefaultMethodInvoker(getMethodHandleJava9(method));
            }
        } else {
            // 对于其他方法，会创建MapperMethod并使用PlainMethodInvoker封装
            return new PlainMethodInvoker(
                    new MapperMethod(mapperInterface, method, sqlSession.getConfiguration()));
        }
    });
}
```

在 PlainMethodInvoker.invoke() 方法中，会通过底层维护的 MapperMethod 完成方法调用，其核心实现如下：

```java
public Object invoke(Object proxy, Method method, Object[] args, SqlSession sqlSession) throws Throwable {
    // 直接执行MapperMethod.execute()方法完成方法调用
    return mapperMethod.execute(sqlSession, args);
}
```

**MapperMethod**

通过对 MapperProxy 的分析我们知道，MapperMethod 是最终执行 SQL 语句的地方，同时也记录了 Mapper 接口中的对应方法，其核心字段也围绕这两方面的内容展开。

- SqlCommand

MapperMethod 的第一个核心字段是 command（SqlCommand 类型），其中维护了关联 SQL 语句的相关信息。

- MethodSignature

MapperMethod 的第二个核心字段是 method 字段（MethodSignature 类型），其中维护了 Mapper 接口中方法的相关信息。

- 深入 execute() 方法

execute() 方法是 MapperMethod 中最核心的方法之一。execute() 方法会根据要执行的 SQL 语句的具体类型执行 SqlSession 的相应方法完成数据库操作，其核心实现如下：

```java
public Object execute(SqlSession sqlSession, Object[] args) {
    Object result;
    switch (command.getType()) { // 判断SQL语句的类型
        case INSERT: {
            // 通过ParamNameResolver.getNamedParams()方法将方法的实参与
            // 参数的名称关联起来
            Object param = method.convertArgsToSqlCommandParam(args);
            // 通过SqlSession.insert()方法执行INSERT语句，
            // 在rowCountResult()方法中，会根据方法的返回值类型对结果进行转换
            result = rowCountResult(sqlSession.insert(command.getName(), param));
            break;
        }
        case UPDATE: {
            Object param = method.convertArgsToSqlCommandParam(args);
            // 通过SqlSession.update()方法执行UPDATE语句
            result = rowCountResult(sqlSession.update(command.getName(), param));
            break;
        }
        // DELETE分支与UPDATE类似，省略
        case SELECT:
            if (method.returnsVoid() && method.hasResultHandler()) {
                // 如果方法返回值为void，且参数中包含了ResultHandler类型的实参，
                // 则查询的结果集将会由ResultHandler对象进行处理
                executeWithResultHandler(sqlSession, args);
                result = null;
            } else if (method.returnsMany()) {
                // executeForMany()方法处理返回值为集合或数组的场景
                result = executeForMany(sqlSession, args);
            } else ...// 省略针对Map、Cursor以及Optional返回值的处理
            }
            break;
            // 省略FLUSH和default分支
    }
    return result;
}
```

## 09 | 基于 MyBatis 缓存分析装饰器模式的最佳实践

MyBatis 的缓存分为一级缓存、二级缓存两个级别，并且都实现了 Cache 接口，所以这一讲我们就重点来介绍 Cache 接口及其核心实现类。

**装饰器模式**

装饰器模式是一种通过组合方式实现扩展的设计模式。相较于继承这种静态的扩展方式，装饰器模式可以在运行时根据系统状态，动态决定为一个实现类添加哪些扩展功能。

装饰器模式的核心类图，如下所示：

![image-20220630223436152](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206302234508.png)

装饰器模式中的核心类主要有下面四个。

- Component 接口：整个功能的核心抽象，JDK 中的 IO 流体系就使用了装饰器模式，其中的 InputStream 接口就扮演了 Component 接口的角色。
- ComponentImpl 实现类：实现了 Component 接口最基础、最核心的功能，也就是被装饰的、原始的基础类。在 JDK IO 流体系之中的 FileInputStream 就扮演了 ComponentImpl 的角色
- Decorator 抽象类：其核心不是提供新的扩展能力，而是封装一个 Component 类型的字段。
- DecoratorImpl1、DecoratorImpl2：它们的核心就是在被装饰对象的基础之上添加新的扩展功能。

**Cache 接口及核心实现**

Cache 接口中的核心方法主要是 putObject()、getObject() 和 removeObject() 三个方法，分别用来写入、查询和删除缓存数据。

Cache 接口的 PerpetualCache 实现类扮演了装饰器模式中 ComponentImpl 这个角色，实现了 Cache 接口缓存数据的基本能力。

PerpetualCache 中有两个核心字段：一个是 id 字段（String 类型），记录了缓存对象的唯一标识；另一个是 cache 字段（HashMap 类型），真正实现 Cache 存储的数据结构。

**Cache 接口装饰器**

除了 PerpetualCache 之外的其他所有 Cache 接口实现类，都是装饰器实现。

1. BlockingCache

BlockingCache 是在原有 Cache 实现之上添加了阻塞线程的特性。对于一个 Key 来说，同一时刻，BlockingCache 只会让一个业务线程到数据库中去查找，查找到结果之后，会添加到 BlockingCache 中缓存。

BlockingCache 的核心原理如下图所示：

![image-20220630225350095](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206302253339.png)

2. FifoCache

为了控制 Cache 的大小，MyBatis 提供了缓存淘汰规则。FifoCache 是 FIFO（先入先出）策略的装饰器，当 Cache 中的缓存条目达到上限的时候，则会将 Cache 中最早写入的缓存条目清理掉。

FifoCache 作为一个 Cache 装饰器，自然也会包含一个指向 Cache 的 delegate 字段。同时它还维护了两个与 FIFO 相关的字段：一个是 keyList 队列（LinkedList）。

3. LruCache

除了 FIFO 策略之外，MyBatis 还支持 LRU（Least Recently Used，近期最少使用算法）策略来清理缓存。

LruCache 中除了有一个 delegate 字段指向被装饰 Cache 对象之外，还维护了一个 LinkedHashMap 集合（keyMap 字段），用来记录各个缓存条目最近的使用情况，以及一个 eldestKey 字段（Object 类型），用来指向最近最少使用的 Key。

4. SoftCache

我们先来简单回顾一下 Java 中的强引用和软引用，以及这些引用的相关机制。

强引用是 JVM 中最普遍的引用，我们常用的赋值操作就是强引用，例如，Person p = new Person(); 这个 Person 对象被引用的时候，即使是 JVM 内存空间不足触发 GC，甚至是内存溢出（OutOfMemoryError），也不会回收这个 Person 对象。

软引用比强引用稍微弱一些。当 JVM 内存不足时，GC 才会回收那些只被软引用指向的对象，从而避免 OutOfMemoryError。根据软引用的这一特性，我们会发现软引用特别适合做缓存。

SoftCache 中的 value 是 SoftEntry 类型的对象，具体实现如下：

```java
private static class SoftEntry extends SoftReference<Object> {
    private final Object key;
    SoftEntry(Object key, Object value, ReferenceQueue<Object> garbageCollectionQueue) {
        // 指向value的是软引用，并且关联了引用队列
        super(value, garbageCollectionQueue);
        // 指向key的是强引用
        this.key = key;
    }
}
```

5. WeakCache

弱引用比软引用的引用强度还要弱。在 JVM 进行垃圾回收的时候，若发现某个对象只有一个弱引用指向它，那么这个对象会被 GC 立刻回收。

从这个特性我们可以得到一个结论：只被弱引用指向的对象只在两次 GC 之间存活。而只被软引用指向的对象是在 JVM 内存紧张的时候才被回收，它是可以经历多次 GC 的，这就是两者最大的区别。

## 10 | 鸟瞰 MyBatis 初始化，把握 MyBatis 启动流程脉络（上）



























# 模块三：核心处理层





# 模块四：扩展延伸

## 20 | 插件体系让 MyBatis 世界更加精彩

插件是应用程序中最常见的一种扩展方式。例如，Dubbo 通过 SPI 方式实现了插件化的效果，SkyWalking 依赖“微内核+插件”的架构轻松加载插件，实现扩展效果。

MyBatis 也提供了类似的插件扩展机制。该模块位于 org.apache.ibatis.plugin 包中，主要使用了两种设计模式：代理模式和责任链模式。

**Interceptor**

MyBatis 插件模块中最核心的接口就是 Interceptor 接口，它是所有 MyBatis 插件必须要实现的接口，其核心定义如下：

```java
public interface Interceptor {
  // 插件实现类中需要实现的拦截逻辑
  Object intercept(Invocation invocation) throws Throwable;
  // 在该方法中会决定是否触发intercept()方法
  default Object plugin(Object target) {
    return Plugin.wrap(target, this);
  }
  default void setProperties(Properties properties) {
    // 在整个MyBatis初始化过程中用来初始化该插件的方法
  }
}
```

MyBatis允许我们自定义 Interceptor 拦截 SQL 语句执行过程中的某些关键逻辑，允许拦截的方法有：

- Executor 类中的 update()、query()、flushStatements()、commit()、rollback()、getTransaction()、close()、isClosed()方法；
- ParameterHandler 中的 setParameters()、getParameterObject() 方法；
- ResultSetHandler中的 handleOutputParameters()、handleResultSets()方法；
- StatementHandler 中的parameterize()、prepare()、batch()、update()、query()方法。

下面我们就结合一个 MyBatis 插件示例，介绍一下 MyBatis 中 Interceptor 接口的具体使用方式。这里我们首先定义一个DemoPlugin 类，定义如下：

```java
@Intercepts({
        @Signature(type = Executor.class, method = "query", args = {
                MappedStatement.class, Object.class, RowBounds.class,
                ResultHandler.class}),
        @Signature(type = Executor.class, method = "close", args = {boolean.class})
})
public class DemoPlugin implements Interceptor {
    private int logLevel; 
    ... // 省略其他方法的实现
}
```

@Signature 注解用来指定 DemoPlugin 插件实现类要拦截的目标方法信息，其中的 type 属性指定了要拦截的类，method 属性指定了要拦截的目标方法名称，args 属性指定了要拦截的目标方法的参数列表。

> Interceptor 的加载。

为了让 MyBatis 知道这个类的存在，我们要在 mybatis-config.xml 全局配置文件中对 DemoPlugin 进行配置，相关配置片段如下：

```xml
<plugins>
    <plugin interceptor="design.Interceptor.DemoPlugin">
        <!-- 对拦截器中的属性进行初始化 -->
        <property name="logLevel" value="1"/>
    </plugin>
</plugins>
```

MyBatis 会在初始化流程中解析 mybatis-config.xml 全局配置文件，其中的 \<plugin\> 节点就会被处理成相应的 Interceptor 对象，同时调用 setProperties() 方法完成配置的初始化，最后MyBatis 会将 Interceptor 对象添加到Configuration.interceptorChain 这个全局的 Interceptor 列表中保存。

> 我们再来看 Interceptor 是如何拦截目标类中的目标方法的。

MyBatis 中 Executor、ParameterHandler、ResultSetHandler、StatementHandler 等与 SQL 执行相关的核心组件都是通过 Configuration.new*() 方法生成的。以 newExecutor() 方法为例，我们会看到下面这行代码，InterceptorChain.pluginAll() 方法会为目标对象创建代理对象并返回。

```java
executor = (Executor) interceptorChain.pluginAll(executor);
```

InterceptorChain 的 interceptors 字段中维护了 MyBatis 初始化过程中加载到的全部 Interceptor 对象，在其 pluginAll() 方法中，会调用每个 Interceptor 的 plugin() 方法创建目标类的代理对象，核心实现如下：

```java
public Object pluginAll(Object target) {
  for (Interceptor interceptor : interceptors) {
    // 遍历interceptors集合，调用每个Interceptor对象的plugin()方法
    target = interceptor.plugin(target);
  }
  return target;
}
```

**Plugin**

了解了 Interceptor 的加载流程和基本工作原理之后，我们再来介绍一下自定义 Interceptor 的实现。我们首先回到 DemoPlugin 这个示例，关注其中 plugin() 方法的实现：

```java
@Override
public Object plugin(Object target) {
    // 依赖Plugin工具类创建代理对象
    return Plugin.wrap(target, this);
}
```

Plugin 实现了 JDK 动态代理中的 InvocationHandler 接口，我们需要关注其 invoke() 方法实现：

```java
public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
    try {
        // 获取当前待执行方法所属的类
        Set<Method> methods = signatureMap.get(method.getDeclaringClass());
        // 如果当前方法需要被代理，则执行intercept()方法进行拦截处理
        if (methods != null && methods.contains(method)) {
            return interceptor.intercept(new Invocation(target, method, args));
        }
        // 如果当前方法不需要被代理，则调用target对象的相应方法
        return method.invoke(target, args);
    } catch (Exception e) {
        throw ExceptionUtil.unwrapThrowable(e);
    }
}
```

最后，我们来看一下 Plugin 工具类对外提供的 wrap() 方法是如何创建 JDK 动态代理的。

```java
public static Object wrap(Object target, Interceptor interceptor) {
    // 获取自定义Interceptor实现类上的@Signature注解信息，
    // 这里的getSignatureMap()方法会解析@Signature注解，得到要拦截的类以及要拦截的方法集合
    Map<Class<?>, Set<Method>> signatureMap = getSignatureMap(interceptor);
    Class<?> type = target.getClass();
    // 检查当前传入的target对象是否为@Signature注解要拦截的类型，如果是的话，就
    // 使用JDK动态代理的方式创建代理对象
    Class<?>[] interfaces = getAllInterfaces(type, signatureMap);
    if (interfaces.length > 0) {
        // 创建JDK动态代理
        return Proxy.newProxyInstance(
                type.getClassLoader(),
                interfaces,
                // 这里使用的InvocationHandler就是Plugin本身
                new Plugin(target, interceptor, signatureMap));
    }
    return target;
}
```

## 21 | 深挖 MyBatis 与 Spring 集成底层原理

**Spring**

依赖注入（Dependency Injection）是实现 IoC 的常见方式之一。所谓依赖注入，就是我们的系统不再主动维护业务对象之间的依赖关系，而是将依赖关系转移到 IoC 容器中动态维护。

Spring 中另一个比较重要的概念是 AOP（Aspect Oriented Programming）。AOP 中有几个关键概念：

- 横切关注点：
- 切面（@Aspect）：对横切关注点的抽象。
- 连接点（JoinPoint）：业务逻辑中的某个方法，该方法会被 AOP 拦截。
- 切入点（@Pointcut）：对连接点进行拦截的定义。
- 通知：拦截到连接点之后要执行的代码，可以分为5类，分别是前置通知（@Before）、后置通知（@AfterReturning）、异常通知（@AfterThrowing）、最终通知和环绕通知（@Around）。

**Spring MVC**

下图展示了 Spring MVC 处理一次 HTTP 请求的完整流程：

![image-20220628212309690](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206282123031.png)

Spring MVC 框架处理 HTTP 请求的核心步骤如下。

1. 用户的请求到达服务器后，经过HTTP Server 处理得到 HTTP Request 对象，并传到 Spring MVC 框架中的 DispatcherServlet 进行处理。
2. DispatcherServlet 在接收到请求之后，会根据请求查找对应的 HandlerMapping，在 HandlerMapping 中维护了请求路径与 Controller 之间的映射。
3. DispatcherServlet 根据步骤 2 中的 HandlerMapping 拿到请求相应的 Controller ，并将请求提交到该 Controller 进行处理。Controller 会调用业务 Service 完成请求处理，得到处理结果；Controller 会根据 Service 返回的处理结果，生成相应的 ModelAndView 对象并返回给 DispatcherServlet。
4. DispatcherServlet 会从 ModelAndView 中解析出 ViewName，并交给 ViewResolver 解析出对应的 View 视图。
5. DispatcherServlet 会从 ModelAndView 中拿到 Model（在 Model 中封装了我们要展示的数据），与步骤 4 中得到的 View 进行整合，得到最终的 Response 响应。

**SSM 环境搭建**

> https://github.com/xxxlxy2008/SSM

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206282204120.png)

项目中的核心配置文件如下：

- 第一个是 web.xml 配置文件。指定了初始化 Spring 上下文的 ContextLoaderListener 监听器；配置Spring MVC 中的 DispatcherServlet。
- 第二个是 Spring 初始化时读取的 applicationContext.xml 配置文件。

**Spring 集成 MyBatis 原理剖析**

在搭建 SSM 开发环境的时候，我们引入了一个 mybatis-spring-*.jar 的依赖，这个依赖是 Spring 集成 MyBatis 的关键所在。

下面我们就来看一下 Spring 集成 MyBatis 的几个关键实现。

1. SqlSessionFactoryBean

```java
protected SqlSessionFactory buildSqlSessionFactory() throws IOException {
    Configuration configuration;
    XMLConfigBuilder xmlConfigBuilder = null;
    if (this.configLocation != null) {
        // 创建XMLConfigBuilder对象，读取指定的配置文件
        xmlConfigBuilder = new XMLConfigBuilder(this.configLocation.getInputStream(),
            null, this.configurationProperties);
        configuration = xmlConfigBuilder.getConfiguration();
    } else {
        // 其他方式初始化Configuration全局配置对象
    }
    // 下面会根据前面第10、11讲介绍的初始化流程，初始化MyBatis的相关配置和对象，其中包括：
    // 扫描typeAliasesPackage配置指定的包，并为其中的类注册别名
    // 注册plugins集合中指定的插件
    // 扫描typeHandlersPackage指定的包，并注册其中的TypeHandler
    // 配置缓存、配置数据源、设置Environment等一系列操作
    if (this.transactionFactory == null) {
        // 默认使用的事务工厂类
        this.transactionFactory = new SpringManagedTransactionFactory();
    }

    // 根据mapperLocations配置，加载Mapper.xml映射配置文件以及对应的Mapper接口
    for (Resource mapperLocation : this.mapperLocations) {
        XMLMapperBuilder xmlMapperBuilder = new XMLMapperBuilder(...);
        xmlMapperBuilder.parse();
    }
    // 最后根据前面创建的Configuration全局配置对象创建SqlSessionFactory对象
    return this.sqlSessionFactoryBuilder.build(configuration);
}
```

2. SpringManagedTransaction

在 SSM 集成环境中默认使用 SpringManagedTransactionFactory 这个 TransactionFactory 接口实现来创建 Transaction 对象，其中创建的 Transaction 对象是 SpringManagedTransaction。需要说明的是，这里的 Transaction 和 TransactionFactory 接口都是 MyBatis 中的接口。

3. SqlSessionTemplate

当 Spring 集成 MyBatis 使用的时候，SqlSession 接口的实现不再直接使用 MyBatis 提供的 DefaultSqlSession 默认实现，而是使用 SqlSessionTemplate，如果我们没有使用 Mapper 接口的方式编写 DAO 层，而是直接使用 Java 代码手写 DAO 层，那么我们就可以使用 SqlSessionTemplate。

SqlSessionTemplate 是线程安全的，可以在多个线程之间共享使用。

4. MapperFactoryBean 与 MapperScannerConfigurer









