> 来自拉勾教育《深入剖析 MyBatis 核心原理》--杨四正
>
> https://github.com/xxxlxy2008/mybatis

# 开篇词

我是从以下四个层面来设计这门课程的。

- 从基础知识开始，通过一个订票系统持久层的 Demo 演示，手把手带你快速上手 MyBatis 的基础使用。之后在此基础上，再带你了解 MyBatis 框架的整体三层架构，并介绍 MyBatis 中各个模块的核心功能，为后面的分析打好基础。
- 带你自底向上剖析 MyBatis 的核心源码实现，深入理解 MyBatis 基础模块的工作原理及核心实现，让你不再停留在简单使用 MyBatis 的阶段，做到知其然，也知其所以然。
- 在介绍源码实现的过程中，还会穿插设计模式的相关知识点，带领你了解设计模式的优秀实践方式，让你深刻体会优秀架构设计的美感。这样在你进行架构设计以及代码编写的时候，就可以真正使用这些设计模式，进而让你的代码扩展性更强、可维护性更好。
- 还会带领你了解 MyBatis 周边的扩展，帮助你打开视野，让你不仅能够学到 MyBatis 本身的原理和设计，还会了解到 MyBatis 与 Spring 集成的底层原理、MyBatis 插件扩展的精髓，以及 MyBatis 衍生生态的魅力。

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

Executor 会调用事务管理模块实现事务的相关控制，同时会通过缓存模块管理一级缓存和二级缓存。

SQL 语句的真正执行将会由 StatementHandler 实现。StatementHandler 会先依赖 ParameterHandler 进行 SQL 模板的实参绑定，然后由 java.sql.Statement 对象将 SQL 语句以及绑定好的实参传到数据库执行，从数据库中拿到 ResultSet，最后，由 ResultSetHandler 将 ResultSet 映射成 Java 对象返回给调用方，这就是 SQL 执行模块的核心。

- 插件

很多成熟的开源框架，都会以各种方式提供扩展能力。当框架原生能力不能满足某些场景的时候，就可以针对这些场景实现一些插件来满足需求，这样的框架才能有足够的生命力。这也是 MyBatis 插件接口存在的意义。

**接口层**

接口层是 MyBatis 暴露给调用的接口集合，这些接口都是使用 MyBatis 时最常用的一些接口，例如，SqlSession 接口、SqlSessionFactory 接口等。

其中，最核心的是 SqlSession 接口，你可以通过它实现很多功能，例如，获取 Mapper 代理、执行 SQL 语句、控制事务开关等。

# 模块二：基础支撑层

## 04 | MyBatis 反射工具箱：带你领略不一样的反射设计思路

反射工具箱的具体代码实现位于 org.apache.ibatis.reflection 包中。下面我们就一起深入分析该模块的核心实现。

**Reflector**

[Reflector](https://github.com/studeyang/mybatis-notes/blob/master/src/main/java/org/apache/ibatis/reflection/Reflector.java) 是 MyBatis 反射模块的基础。要使用反射模块操作一个 Class，都会先将该 Class 封装成一个 Reflector 对象。

- 核心方法

在第 3 行出现了 `currentMethod.isBridge()`：

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

- [ReflectorFactory](https://github.com/studeyang/mybatis-notes/blob/master/src/main/java/org/apache/ibatis/reflection/ReflectorFactory.java)

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

<div align="center"> <img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206162158152.png" width="600px"/> </div>

## 05 | 类型转换：数据库类型体系与 Java 类型体系之间的“爱恨情仇”

JDBC 的数据类型与 Java 语言中的数据类型虽然有点对应关系，但还是无法做到一一对应，也自然无法做到自动映射。

| 数据库类型         | Java类型             |
| ------------------ | -------------------- |
| VARCHAR            | Java.lang.String     |
| CHAR               | Java.lang.String     |
| BLOB               | Java.lang.byte[]     |
| INTEGER UNSIGNED   | Java.lang.Long       |
| TINYINT UNSIGNED   | Java.lang.Integer    |
| SMALLINT UNSIGNED  | Java.lang.Integer    |
| MEDIUMINT UNSIGNED | Java.lang.Integer    |
| BIT                | Java.lang.Boolean    |
| BIGINT UNSIGNED    | Java.math.BigInteger |
| FLOAT              | Java.lang.Float      |
| DOUBLE             | Java.lang.Double     |
| DECIMAL            | Java.math.BigDecimal |

在 MyBatis 中，可以使用类型转换器类型转换，如下图所示：

<div align="center"> <img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202206172141413.png" width="400px"/> </div>

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

# 模块三：核心处理层

## 10 | 鸟瞰 MyBatis 初始化，把握 MyBatis 启动流程脉络（上）

在初始化的过程中，MyBatis 会读取 mybatis-config.xml 这个全局配置文件以及所有的 Mapper 映射配置文件，同时还会加载这两个配置文件中指定的类，解析类中的相关注解，最终将解析得到的信息转换成配置对象。完成配置加载之后，MyBatis 就会根据得到的配置对象初始化各个模块。

MyBatis 在加载配置文件、创建配置对象的时候，会使用到经典设计模式中的构造者模式。

**构造者模式**

构造者模式是将复杂对象的创建过程分解成了多个简单步骤，在创建复杂对象的时候，只需要了解复杂对象的基本属性即可，而不需要关心复杂对象的内部构造过程。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207021601510.png" alt="image-20220702160153109" style="zoom: 67%;" />

从图中，我们可以看到构造者模式的四个核心组件。

- Product 接口：复杂对象的接口，定义了要创建的目标对象的行为。
- ProductImpl 类：Product 接口的实现，它真正要创建的复杂对象，其中实现了我们需要的复杂业务逻辑。
- Builder 接口：定义了构造 Product 对象的每一步行为。
- BuilderImpl 类：Builder 接口的具体实现，其中具体实现了构造一个 Product 的每一个步骤，例如上图中的 setPart1()、setPart2() 等方法，都是用来构造 ProductImpl 对象的各个部分。在完成整个 Product 对象的构造之后，我们会通过 build() 方法返回这个构造好的 Product 对象。

**mybatis-config.xml 解析全流程**

MyBatis 初始化的第一个步骤就是加载和解析 mybatis-config.xml 这个全局配置文件，得到对应的 Configuration 全局配置对象。入口是 XMLConfigBuilder 这个 Builder 对象。

首先我们来了解一下 XMLConfigBuilder 的核心字段。

- parsed（boolean 类型）：状态标识字段，记录当前 XMLConfigBuilder 对象是否已经成功解析完 mybatis-config.xml 配置文件。
- parser（XPathParser 类型）：XPathParser 对象是一个 XML 解析器，这里的 parser 对象就是用来解析 mybatis-config.xml 配置文件的。
- environment（String 类型）： 标签定义的环境名称。
- localReflectorFactory（ReflectorFactory 类型）：ReflectorFactory 接口的核心功能是实现对 Reflector 对象的创建和缓存。

XMLConfigBuilder.parse() 方法触发了 mybatis-config.xml 配置文件的解析，其中的 parseConfiguration() 方法定义了解析 mybatis-config.xml 配置文件的完整流程，核心步骤如下：

- 解析 \<properties> 标签；
- 解析 \<settings> 标签；
- 处理日志相关组件；
- 解析 \<typeAliases> 标签；
- 解析 \<plugins> 标签；
- 解析 \<objectFactory> 标签；
- 解析 \<objectWrapperFactory\> 标签；
- 解析 \<reflectorFactory\> 标签；
- 解析 \<environments> 标签；
- 解析 \<databaseIdProvider> 标签；
- 解析 \<typeHandlers> 标签；
- 解析 \<mappers> 标签。

下面我们就逐一介绍这些方法的核心实现。

**1. 处理\<properties>标签**

我们可以通过 <properties> 标签定义 KV 信息供 MyBatis 使用，propertiesElement() 方法的核心逻辑就是解析 mybatis-config.xml 配置文件中的 <properties> 标签。

从 <properties> 标签中解析出来的 KV 信息会被记录到一个 Properties 对象中，在后续解析其他标签的时候，MyBatis 会使用这个 Properties 对象中记录的 KV 信息替换匹配的占位符。

**2. 处理\<settings>标签**

MyBatis 中有很多全局性的配置，例如，是否使用二级缓存、是否开启懒加载功能等，这些都是通过 mybatis-config.xml 配置文件中的 <settings> 标签进行配置的。

XMLConfigBuilder.settingsAsProperties() 方法的核心逻辑就是解析 <settings> 标签，并将解析得到的配置信息记录到 Configuration 这个全局配置对象的同名属性中。

**3. 处理\<typeAliases>和\<typeHandlers>标签**

XMLConfigBuilder 中提供了 typeAliasesElement() 方法和 typeHandlerElement() 方法，分别用来负责处理 <typeAliases> 标签和 <typeHandlers> 标签，解析得到的别名信息和 TypeHandler 信息就会分别记录到 TypeAliasRegistry 和 TypeHandlerRegistry。

**4. 处理\<plugins>标签**

MyBatis 是一个非常易于扩展的持久层框架，而插件就是 MyBatis 提供的一种重要扩展机制。

XMLConfigBuilder 中的 pluginElement()方法的核心就是解析 <plugins> 标签中配置的自定义插件。

**5. 处理\<objectFactory>标签**

MyBatis 支持自定义 ObjectFactory 实现类和 ObjectWrapperFactory。XMLConfigBuilder 中的 objectFactoryElement() 方法就实现了加载自定义 ObjectFactory 实现类的功能，其核心逻辑就是解析 <objectFactory> 标签中配置的自定义 ObjectFactory 实现类，并完成相关的实例化操作。

除了 <objectFactory> 标签之外，我们还可以通过 <objectWrapperFactory> 标签和 <reflectorFactory> 标签配置自定义的 ObjectWrapperFactory 实现类和 ReflectorFactory 实现类，这两个标签的解析分别对应 objectWrapperFactoryElement() 方法和 reflectorFactoryElement() 方法。

**6. 处理\<environments>标签**

在 MyBatis 中，我们可以通过 <environment> 标签为不同的环境添加不同的配置，例如，线上环境、预上线环境、测试环境等，每个 <environment> 标签只会对应一种特定的环境配置。

environmentsElement() 方法中实现了 XMLConfigBuilder 处理 <environments> 标签的核心逻辑，它会根据 XMLConfigBuilder.environment 字段值，拿到正确的 <environment> 标签，然后解析这个环境中使用的 TransactionFactory、DataSource 等核心对象，也就知道了 MyBatis 要请求哪个数据库、如何管理事务等信息。

**7. 处理\<databaseIdProvider>标签**

在 MyBatis 中编写的都是原生的 SQL 语句，而很多数据库产品都会有一些 SQL 方言，这些方言与标准 SQL 不兼容。

在 mybatis-config.xml 配置文件中，我们可以通过 <databaseIdProvider> 标签定义需要支持的全部数据库的 DatabaseId，在后续编写 Mapper 映射配置文件的时候，就可以为同一个业务场景定义不同的 SQL 语句，来支持不同的数据库，这里就是靠 DatabaseId 来确定哪个 SQL 语句支持哪个数据库的。

databaseIdProviderElement() 方法是 XMLConfigBuilder 处理 <databaseIdProvider> 标签的地方，其中的核心就是获取 DatabaseId 值。

**8. 处理\<mappers>标签**

除了 mybatis-config.xml 这个全局配置文件之外，MyBatis 初始化的时候还会加载 <mappers> 标签下定义的 Mapper 映射文件。<mappers> 标签中会指定 Mapper.xml 映射文件的位置，通过解析 <mappers> 标签，MyBatis 就能够知道去哪里加载这些 Mapper.xml 文件了。

mapperElement() 方法就是 XMLConfigBuilder 处理 <mappers> 标签的具体实现，其中会初始化 XMLMapperBuilder 对象来加载各个 Mapper.xml 映射文件。同时，还会扫描 Mapper 映射文件相应的 Mapper 接口，处理其中的注解并将 Mapper 接口注册到 MapperRegistry 中。

## 11 | 鸟瞰 MyBatis 初始化，把握 MyBatis 启动流程脉络（下）

这一讲我们就紧接着上一讲的内容，继续介绍 MyBatis 初始化流程，重点介绍Mapper.xml 配置文件的解析以及 SQL 语句的处理逻辑。

**Mapper.xml 映射文件解析全流程**

MyBatis 会为每个 Mapper.xml 映射文件创建一个 XMLMapperBuilder 实例完成解析。XMLMapperBuilder 中 configurationElement() 方法是真正解析 Mapper.xml 映射文件的地方，其中定义了处理 Mapper.xml 映射文件的核心流程：

- 获取 \<mapper\> 标签中的 namespace 属性，同时会进行多种边界检查；
- 解析 \<cache\> 标签；
- 解析 \<cache-ref\> 标签；
- 解析 \<resultMap\> 标签；
- 解析 \<sql\> 标签；
- 解析 \<select\>、\<insert\>、\<update\>、\<delete\> 等 SQL 标签。

下面我们就按照顺序逐一介绍这些方法的核心实现。

**1. 处理 <cache> 标签**

Cache 接口及其实现是MyBatis 一级缓存和二级缓存的基础，其中，一级缓存是默认开启的，而二级缓存默认情况下并没有开启，如有需要，可以通过<cache>标签为指定的namespace 开启二级缓存。

XMLMapperBuilder 中解析 <cache> 标签的核心逻辑位于 cacheElement() 方法之中，其具体步骤如下：

- 获取 <cache> 标签中的各项属性（type、flushInterval、size 等属性）；
- 读取 <cache> 标签下的子标签信息，这些信息将用于初始化二级缓存；
- MapperBuilderAssistant 会根据上述配置信息，创建一个全新的Cache 对象并添加到 Configuration.caches 集合中保存。

**2. 处理<cache-ref>标签**

MyBatis 可以通过 <cache> 标签为每个 namespace 开启二级缓存，二级缓存是 namespace 级别的。但是，在有的场景中，我们会需要在多个 namespace 共享同一个二级缓存，也就是共享同一个 Cache 对象。

为了解决这个需求，MyBatis提供了 <cache-ref> 标签来引用另一个 namespace 的二级缓存。cacheRefElement() 方法是处理 <cache-ref> 标签的核心逻辑所在，在 Configuration 中维护了一个 cacheRefMap 字段（HashMap<String,String> 类型），其中的 Key 是 <cache-ref> 标签所属的namespace 标识，Value 值是 <cache-ref> 标签引用的 namespace 值，这样的话，就可以将两个namespace 关联起来了，即这两个 namespace 共用一个 Cache对象。

**3. 处理<resultMap>标签**

在使用 JDBC 的时候，我们需要手动写代码将select 语句的结果集转换成 Java 对象，这是一项重复性很大的操作。

为了将 Java 开发者从这种重复性的工作中解脱出来，MyBatis 提供了 <resultMap> 标签来定义结果集与 Java 对象之间的映射规则。

整个 <resultMap> 标签最终会被解析成 ResultMap 对象，它与 ResultMapping 之间的映射关系如下图所示：

![image-20220702220214547](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207022202838.png)

**SQL 语句解析全流程**

在 Mapper.xml 映射文件中，除了上面介绍的标签之外，还有一类比较重要的标签，那就是 <select>、<insert>、<delete>、<update> 等 SQL 语句标签。

虽然定义在 Mapper.xml 映射文件中，但是这些标签是由 XMLStatementBuilder 进行解析的，而不再由 XMLMapperBuilder 来完成解析。

**1. 处理 <include> 标签**

在实际应用中，我们会在<sql> 标签中定义一些能够被重用的SQL 片段，在 XMLMapperBuilder.sqlElement() 方法中会根据当前使用的 DatabaseId 匹配 <sql> 标签，只有匹配的 SQL 片段才会被加载到内存。

针对 <include> 标签的处理如下：

- 查找 refid 属性指向的 <sql> 标签，得到其对应的 Node 对象；
- 解析 <include> 标签下的 <property> 标签，将得到的键值对添加到 variablesContext 集合（Properties 类型）中，并形成新的 Properties 对象返回，用于替换占位符；
- 递归执行 applyIncludes()方法，因为在 <sql> 标签的定义中可能会使用 <include> 引用其他 SQL 片段，在 applyIncludes()方法递归的过程中，如果遇到“${}”占位符，则使用 variablesContext 集合中的键值对进行替换；
- 最后，将 <include> 标签替换成 <sql> 标签的内容。

<include> 标签和 <sql> 标签是可以嵌套多层的，此时就会涉及 applyIncludes()方法的递归，同时可以配合“${}”占位符，实现 SQL 片段模板化，更大程度地提高 SQL 片段的重用率。

**2. 处理 <selectKey> 标签**

在有的数据库表设计场景中，我们会添加一个自增 ID 字段作为主键，例如，用户 ID、订单 ID 或者这个自增 ID 本身并没有什么业务含义，只是一个唯一标识而已。在某些业务逻辑里面，我们希望在执行 insert 语句的时候返回这个自增 ID 值，<selectKey> 标签就可以实现自增 ID 的获取。

<selectKey> 标签不仅可以获取自增 ID，还可以指定其他 SQL 语句，从其他表或执行数据库的函数获取字段值。

**3. 处理 SQL 语句**

经过 <include> 标签和 <selectKey> 标签的处理流程之后，XMLStatementBuilder 中的 parseStatementNode()方法接下来就要开始处理 SQL 语句了。

## 12 | 深入分析动态 SQL 语句解析全流程（上）

MyBatis 会将 Mapper 映射文件中定义的 SQL 语句解析成 SqlSource 对象，其中的动态标签、SQL 语句文本等，会解析成对应类型的 SqlNode 对象。

在开始介绍 SqlSource 接口、SqlNode 接口等核心接口的相关内容之前，我们需要先来了解一下动态 SQL 中使用到的基础知识和基础组件。

**OGNL 表达式语言**

OGNL 表达式语言是一款成熟的、面向对象的表达式语言。在动态 SQL 语句中使用到了 OGNL 表达式读写 JavaBean 属性值、执行 JavaBean 方法这两个基础功能。

OGNL 表达式是相对完备的一门表达式语言，我们可以通过“对象变量名称.方法名称/属性名称”调用一个 JavaBean 对象的方法/属性，还可以通过“@[类的完全限定名]@[静态方法/静态字段]”调用一个 Java 类的静态方法/静态字段。

下面我就通过一个示例来帮助你快速了解 OGNL 表达式的基础使用：

```java
public class OGNLDemo {
    private static Customer customer;
    private static OgnlContext context;
    private static Customer createCustomer() {
        customer = new Customer();
        customer.setId(1);
        customer.setName("Test Customer");
        customer.setPhone("1234567");
        Address address = new Address();
        address.setCity("city-001");
        address.setId(1);
        address.setCountry("country-001");
        address.setStreet("street-001");
        ArrayList<Address> addresses = new ArrayList<>();
        addresses.add(address);
        customer.setAddresses(addresses);
        return customer;
    }
    public static void main(String[] args) throws Exception {
        customer = createCustomer(); // 创建Customer对象以及Address对象
        // 创建OgnlContext上下文对象
        context = new OgnlContext(new DefaultClassResolver(),
                new DefaultTypeConverter(),
                new OgnlMemberAccess());
        // 设置root以及address这个key，默认从root开始查找属性或方法
        context.setRoot(customer);
        context.put("address", customer.getAddresses().get(0));
        // Ognl.paraseExpression()方法负责解析OGNL表达式，获取Customer的addresses属性
        Object obj = Ognl.getValue(Ognl.parseExpression("addresses"),
                context, context.getRoot());
        System.out.println(obj);
        // 输出是[Address{id=1, street='street-001', city='city-001', country='country-001'}]
        // 获取city属性
        obj = Ognl.getValue(Ognl.parseExpression("addresses[0].city"),
                context, context.getRoot());
        System.out.println(obj); // 输出是city-001
        // #address表示访问的不是root对象，而是OgnlContext中key为addresses的对象
        obj = Ognl.getValue(Ognl.parseExpression("#address.city"), context,
                context.getRoot());
        System.out.println(obj); // 输出是city-001
        // 执行Customer的getName()方法
        obj = Ognl.getValue(Ognl.parseExpression("getName()"), context,
                context.getRoot());
        System.out.println(obj);
        // 输出是Test Customer
    }
}
```

MyBatis 为了提高 OGNL 表达式的工作效率，添加了一层 OgnlCache 来缓存表达式编译之后的结果（不是表达式的执行结果）。

**DynamicContext 上下文**

在 MyBatis 解析一条动态 SQL 语句的时候，可能整个流程非常长，其中涉及多层方法的调用、方法的递归、复杂的循环等，其中产生的中间结果需要有一个地方进行存储，那就是 DynamicContext 上下文对象。

**组合模式**

组合模式（有时候也被称为“部分-整体”模式）是将同一类型的多个对象组合成一个树形结构。在使用这个树形结构的时候，我们可以像处理一个对象那样进行处理，而不用关心其复杂的树形结构。

组合模式的核心结构如下图所示：

![image-20220706224428437](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207062244773.png)

从上图中，我们可以看出组合模式的核心组件有下面三个。

- Component 接口：定义了整个树形结构中每个节点的基础行为。一般情况下会定义两类方法，一类是真正的业务行为，另一类是管理子节点的行为，例如 addChild()、removeChild()、getChildren() 等方法。
- Leaf 类：抽象的是树形结构中的叶子节点。Leaf 类只实现了 Component 接口中的业务方法，而管理子节点的方法是空实现或直接抛出异常。
- Composite 类：抽象了树形结构中的树枝节点（非叶子节点）。Composite 类不仅要实现 Component 接口的业务方法，而且还需要实现子节点管理的相关方法，并在内部维护一个集合类来管理这些子节点。Composite 实现的业务方法一般逻辑比较简单，大都是直接循环调用所有子节点的业务方法。

可以看出组合模式有以下两个优势：

- 由于使用方并不关心自己使用的是树形 Component 结构还是单个 Component 对象，所以可以帮助上层使用方屏蔽复杂的树形结构，将使用方的逻辑与树形结构解耦；
- 如果要在树形结构中添加新的功能，只需要增加树形结构中的节点即可，也就是提供新的 Component 接口实现并添加到树中，这符合“开放-封闭”原则。

**SqlNode**

在 MyBatis 处理动态 SQL 语句的时候，会将动态 SQL 标签解析为 SqlNode 对象，多个 SqlNode 对象就是通过组合模式组成树形结构供上层使用的。

首先，介绍一下 SqlNode 接口的定义，如下所示：

```java
public interface SqlNode {
    // apply()方法会根据用户传入的实参，解析该SqlNode所表示的动态SQL内容并
    // 将解析之后的SQL片段追加到DynamicContext.sqlBuilder字段中暂存。
    // 当SQL语句中全部的动态SQL片段都解析完成之后，就可以从DynamicContext.sqlBuilder字段中
    // 得到一条完整的、可用的SQL语句了
    boolean apply(DynamicContext context);
}
```

MyBatis 为 SqlNode 接口提供了非常多的实现类（如下图），其中很多实现类都对应一个动态 SQL 标签，但是也有 SqlNode 实现扮演了组合模式中 Composite 的角色，例如，MixedSqlNode 实现类。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207062250235.png)

## 13 | 深入分析动态 SQL 语句解析全流程（下）

我们紧接着上一讲，继续介绍剩余 SqlNode 实现以及 SqlSource 的相关内容。

**SqlNode 剩余实现类**

在上一讲我们已经介绍了 StaticTextSqlNode、MixedSqlNode、TextSqlNode、IfSqlNode、TrimSqlNode 这几个 SqlNode 的实现，下面我们再把剩下的三个 SqlNode 实现类也说明下。

**1. ForeachSqlNode**

ForeachSqlNode 就是 <foreach> 标签的抽象。

**2. ChooseSqlNode**

在 Java 中，我们可以通过 switch...case...default 的方式来编写这段代码；在 MyBatis 的动态 SQL 语句中，我们可以使用 <choose>、<when> 和 <otherwise> 三个标签来实现类似的效果。

<choose> 标签会被 MyBatis 解析成 ChooseSqlNode 对象，<when> 标签会被解析成 IfSqlNode 对象，<otherwise> 标签会被解析成 MixedSqlNode 对象。

**3. VarDeclSqlNode**

VarDeclSqlNode 抽象了 <bind> 标签，其核心功能是将一个 OGNL 表达式的值绑定到一个指定的变量名上，并记录到 DynamicContext 上下文中。

**SqlSourceBuilder**

动态 SQL 语句经过上述 SqlNode 的解析之后，接着会由 SqlSourceBuilder 进行下一步处理。

SqlSourceBuilder 的核心操作主要有两个：

- 解析“#{}”占位符中携带的各种属性，例如，“#{id, javaType=int, jdbcType=NUMERIC, typeHandler=MyTypeHandler}”这个占位符，指定了 javaType、jdbcType、typeHandler 等配置；
- 将 SQL 语句中的“#{}”占位符替换成“?”占位符，替换之后的 SQL 语句就可以提交给数据库进行编译了。

**SqlSource**

经过上述一系列处理之后，SQL 语句最终会由 SqlSource 进行最后的处理。

在 SqlSource 接口中只定义了一个 getBoundSql() 方法，它控制着动态 SQL 语句解析的整个流程，它会根据从 Mapper.xml 映射文件（或注解）解析到的 SQL 语句以及执行 SQL 时传入的实参，返回一条可执行的 SQL。

下图展示了 SqlSource 接口的核心实现：

![image-20220707221317202](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207072213709.png)

下面我们简单介绍一下这三个核心实现类的具体含义。

- DynamicSqlSource：当 SQL 语句中包含动态 SQL 的时候，会使用 DynamicSqlSource 对象。
- RawSqlSource：当 SQL 语句中只包含静态 SQL 的时候，会使用 RawSqlSource 对象。
- StaticSqlSource：DynamicSqlSource 和 RawSqlSource 经过一系列解析之后，会得到最终可提交到数据库的 SQL 语句，这个时候就可以通过 StaticSqlSource 进行封装了。

## 14 | 探究 MyBatis 结果集映射机制背后的秘密（上）

ResultMap 只是定义了一个静态的映射规则，那在运行时，MyBatis 是如何根据映射规则将 ResultSet 映射成 Java 对象的呢？

当 MyBatis 执行完一条 select 语句，拿到 ResultSet 结果集之后，会将其交给关联的 ResultSetHandler 进行后续的映射处理。ResultSetHandler 是一个接口，其中定义了三个方法，分别用来处理不同的查询返回值：

```java
public interface ResultSetHandler {
    // 将ResultSet映射成Java对象
    <E> List<E> handleResultSets(Statement stmt) throws SQLException;
    // 将ResultSet映射成游标对象
    <E> Cursor<E> handleCursorResultSets(Statement stmt) throws SQLException;
    // 处理存储过程的输出参数
    void handleOutputParameters(CallableStatement cs) throws SQLException;
}
```

在 MyBatis 中只提供了一个 ResultSetHandler 接口实现，即 DefaultResultSetHandler。下面我们就以 DefaultResultSetHandler 为中心，介绍 MyBatis 中 ResultSet 映射的核心流程。

**结果集处理入口**

DefaultResultSetHandler 实现的 handleResultSets() 方法支持多个 ResultSet 的处理（单 ResultSet 的处理只是其中的特例）。

**简单映射**

了解了处理 ResultSet 的入口逻辑之后，下面我们继续来深入了解一下 DefaultResultSetHandler 是如何处理单个结果集的，这部分逻辑的入口是 handleResultSet() 方法。

# 模块四：扩展延伸

## 19 | 深入 MyBatis 内核与业务逻辑的桥梁——接口层

这一讲我们就来重点看一下 MyBatis 接口层的实现以及其中涉及的设计模式。

**策略模式**

在策略模式中，我们会将每个算法单独封装成不同的算法实现类（这些算法实现类都实现了相同的接口），每个算法实现类就可以被认为是一种策略实现，我们只需选择不同的策略实现来解决业务问题即可，这样每种算法相对独立，算法内的变化边界也就明确了，新增或减少算法实现也不会影响其他算法。

如下是策略模式的核心类图，其中 StrategyUser 是算法的调用方，维护了一个 Strategy 对象的引用，用来选择具体的算法实现。

![image-20220712224710785](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207122247123.png)

**SqlSession**

SqlSession是MyBatis对外提供的一个 API 接口，整个MyBatis 接口层也是围绕 SqlSession接口展开的，SqlSession 接口中定义了下面几类方法。

- select*() 方法：用来执行查询操作的方法，SqlSession 会将结果集映射成不同类型的结果对象，例如，selectOne() 方法返回单个 Java 对象，selectList()、selectMap() 方法返回集合对象。
- insert()、update()、delete() 方法：用来执行 DML 语句。
- commit()、rollback() 方法：用来控制事务。
- getMapper()、getConnection()、getConfiguration() 方法：分别用来获取接口对应的 Mapper 对象、底层的数据库连接和全局的 Configuration 配置对象。

如下图所示，MyBatis 提供了两个 SqlSession接口的实现类，同时提供了SqlSessionFactory 工厂类来创建 SqlSession 对象。

![image-20220712225527626](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207122255894.png)

默认情况下，我们在使用 MyBatis 的时候用的都是 DefaultSqlSession 这个默认的 SqlSession 实现。DefaultSqlSession 中维护了一个 Executor 对象，通过它来完成数据库操作以及事务管理。DefaultSqlSession 在选择使用哪种 Executor 实现的时候，使用到了策略模式：DefaultSqlSession 扮演了策略模式中的 StrategyUser 角色，Executor 接口扮演的是 Strategy 角色，Executor 接口的不同实现则对应 StrategyImpl 的角色。

**DefaultSqlSessionFactory**

DefaultSqlSessionFactory 是MyBatis中用来创建DefaultSqlSession 的具体工厂实现。通过 DefaultSqlSessionFactory 工厂类，我们可以有两种方式拿到 DefaultSqlSession对象。

第一种方式是通过数据源获取数据库连接，然后在其基础上创建 DefaultSqlSession 对象，其核心实现位于 openSessionFromDataSource() 方法。

第二种方式是上层调用方直接提供数据库连接，并在该数据库连接之上创建 DefaultSqlSession 对象，这种创建方式的核心逻辑位于 openSessionFromConnection() 方法中。

**SqlSessionManager**

通过前面的 SqlSession 继承关系图我们可以看到，SqlSessionManager 同时实现了 SqlSession 和 SqlSessionFactory 两个接口，也就是说，它同时具备操作数据库的能力和创建SqlSession的能力。

## 20 | 插件体系让 MyBatis 世界更加精彩

插件是应用程序中最常见的一种扩展方式。例如，Dubbo 通过 SPI 方式实现了插件化的效果，SkyWalking 依赖“微内核+插件”的架构轻松加载插件，实现扩展效果。

MyBatis 也提供了类似的插件扩展机制。该模块位于 org.apache.ibatis.plugin 包中，主要使用了两种设计模式：代理模式和责任链模式。

**责任链模式**

在责任链模式中，Handler 处理器会持有对下一个 Handler 处理器的引用。也就是说当一个 Handler 处理器完成对关注部分的处理之后，会将请求通过这个引用传递给下一个 Handler 处理器，如此往复，直到整个责任链中全部的 Handler 处理器完成处理。责任链模式的核心类图如下所示：

![image-20220711224442895](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202207112244232.png)

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

> 本段：Interceptor 的加载。

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

> 本段：我们再来看 Interceptor 是如何拦截目标类中的目标方法的。

MyBatis 中 Executor、ParameterHandler、ResultSetHandler、StatementHandler 等与 SQL 执行相关的核心组件都是通过 Configuration.new() 方法生成的。以 newExecutor() 方法为例，我们会看到下面这行代码，InterceptorChain.pluginAll() 方法会为目标对象创建代理对象并返回。

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

我们可以通过 MapperFactoryBean 直接将 Mapper 接口注入 Service 层的 Bean 中，由 Mapper 接口完成 DAO 层的功能。

```xml
<!-- 配置id为customerMapper的Bean -->
<bean id="customerMapper" class="org.mybatis.spring.mapper.MapperFactoryBean">
   <!-- 配置Mapper接口 -->
   <property name="mapperInterface" value="com.example.mapper.CustomerMapper" />
   <!-- 配置SqlSessionFactory，用于创建底层的SqlSessionTemplate -->
   <property name="sqlSessionFactory" ref="sqlSessionFactory" />
</bean>
```

在 MapperFactoryBean 这个 Bean 初始化的时候，会加载 mapperInterface 配置项指定的 Mapper 接口，并调用 Configuration.addMapper() 方法将 Mapper 接口注册到 MapperRegistry，在注册过程中同时会解析对应的 Mapper.xml 配置文件。

虽然通过 MapperFactoryBean 可以不写一行 Java 代码就能实现 DAO 层逻辑，但还是需要在 Spring 的配置文件中为每个 Mapper 接口配置相应的 MapperFactoryBean，这依然是有一定工作量的。如果连配置信息都不想写，那我们就可以使用 MapperScannerConfigurer 扫描指定包下的全部 Mapper 接口。

## 22 | 基于 MyBatis 的衍生框架一览

**MyBatis-Generator**

可以选择 MyBatis-Generator 工具自动生成 Mapper 接口和 Mapper.xml 配置文件。

**MyBatis 分页插件**

MyBatis 本身提供了 RowBounds 参数，可以实现分页的效果。但通过 RowBounds 方式实现分页的时候，本质是将整个结果集数据加载到内存中，然后在内存中过滤出需要的数据，这其实也是我们常说的“内存分页”。

如果我们想屏蔽底层数据库的分页 SQL 语句的差异，同时使用 MyBatis 的 RowBounds 参数实现“物理分页”，可以考虑使用 MyBatis 的分页插件PageHelper。PageHelper 的使用比较简单，只需要在 pom.xml 中引入 PageHelper 依赖包，并在 mybatis-config.xml 配置文件中配置 PageInterceptor 插件即可，核心配置如下：

```xml
<plugins>
    <plugin interceptor="com.github.pagehelper.PageInterceptor">
        <property name="helperDialect" value="mysql"/>
	</plugin>
</plugins>
```

**MyBatis-Plus**

MyBatis-Plus 是国人开发的一款 MyBatis 增强工具，它并没有改变 MyBatis 本身的功能，而是在 MyBatis 的基础上提供了很多增强功能，使我们的开发更加简洁高效。

MyBatis-Plus 对 MyBatis 的很多方面进行了增强，例如：

- 内置了通用的 Mapper 和通用的 Service，只需要添加少量配置即可实现 DAO 层和 Service 层；
- 内置了一个分布式唯一 ID 生成器，可以提供分布式环境下的 ID 生成策略；
- 通过 Maven 插件可以集成生成代码能力，可以快速生成 Mapper、Service 以及 Controller 层的代码，同时支持模块引擎的生成；
- 内置了分页插件，可以实现和 PageHelper 类似的“物理分页”，而且分页插件支持多种数据库；
- 内置了一款性能分析插件，通过该插件我们可以获取一条 SQL 语句的执行时间，可以更快地帮助我们发现慢查询。

