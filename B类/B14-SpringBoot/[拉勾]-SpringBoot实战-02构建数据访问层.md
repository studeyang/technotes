# 数据访问层

# 06 | JDBC 访问关系型数据库规范

作为一套统一标准，JDBC 规范具备完整的架构体系，如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210407225931.png" alt="image-20210407225931153" style="zoom:50%;" />

**JDBC 规范中有哪些核心编程对象？**

对于日常开发而言，JDBC 规范中的核心编程对象包括 DriverManger、DataSource、Connection、Statement，及 ResultSet。

- DriverManager

JDBC 中的 DriverManager 主要负责加载各种不同的驱动程序（Driver）。

```java
public interface Driver {
    //获取数据库连接
    Connection connect(String url, java.util.Properties info) throws SQLException;
}
```

针对 Driver 接口，不同的数据库供应商分别提供了自身的实现方案。例如，MySQL 中的 Driver 实现类如下代码所示：

```java
public class Driver extends NonRegisteringDriver implements java.sql.Driver {
    // 通过 DriverManager 注册 Driver
    static {
        try {
            java.sql.DriverManager.registerDriver(new Driver());
        } catch (SQLException E) {
            throw new RuntimeException("Can't register driver!");
        }
    }
    …
}
```

- DataSource

DataSource 是一个中间层，它作为 DriverManager 的替代品而推出，是获取数据库连接的首选方法。

DataSource 接口的定义如下代码所示：

```java
public interface DataSource  extends CommonDataSource, Wrapper {
 
    Connection getConnection() throws SQLException;
 
    Connection getConnection(String username, String password) throws SQLException;
}
```

CommonDataSource 是 JDBC 中关于数据源定义的根接口，除了 DataSource 接口之外，它还有另外两个子接口，如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210407230746.png" alt="image-20210407230746295" style="zoom:50%;" />

其中，DataSource 是官方定义的获取 Connection 的基础接口，XADataSource 用来在分布式事务环境下实现 Connection 的获取，而 ConnectionPoolDataSource 是从连接池 ConnectionPool 中获取 Connection 的接口。

- Connection

Connection 代表一个数据库连接，负责完成与数据库之间的通信。

所有 SQL 的执行都是在某个特定 Connection 环境中进行的，同时它还提供了一组重载方法分别用于创建 Statement 和 PreparedStatement。另一方面，Connection 也涉及事务相关的操作。

```java
public interface Connection extends Wrapper, AutoCloseable {
    //创建 Statement
 	  Statement createStatement() throws SQLException;
    //创建 PreparedStatement
    PreparedStatement prepareStatement(String sql) throws SQLException;
    //提交
    void commit() throws SQLException;
    //回滚
    void rollback() throws SQLException;
    //关闭连接
    void close() throws SQLException;
}
```

- Statement/PreparedStatement

JDBC 规范中的 Statement 存在两种类型，一种是普通的 Statement，一种是支持预编译的 PreparedStatement。

所谓预编译，是指数据库的编译器会对 SQL 语句提前编译，然后将预编译的结果缓存到数据库中，下次执行时就可以通过替换参数并直接使用编译过的语句，从而大大提高 SQL 的执行效率。

当然，这种预编译也需要一定成本，因此在日常开发中，如果对数据库只执行一次性读写操作时，用 Statement 对象进行处理会比较合适；而涉及 SQL 语句的多次执行时，我们可以使用 PreparedStatement。

- ResultSet

一旦我们通过 Statement 或 PreparedStatement 执行了 SQL 语句并获得了 ResultSet 对象，就可以使用该对象中定义的一大批用于获取 SQL 执行结果值的工具方法，如下代码所示：

```java
public interface ResultSet extends Wrapper, AutoCloseable {
    //获取下一个结果
    boolean next() throws SQLException;
    //获取某一个类型的结果值
    Value getXXX(int columnIndex) throws SQLException;
    …
}
```

**如何使用 JDBC 规范访问数据库？**

```java
// 创建池化的数据源
PooledDataSource dataSource = new PooledDataSource ();
// 设置 MySQL Driver
dataSource.setDriver ("com.mysql.jdbc.Driver");
// 设置数据库 URL、用户名和密码
dataSource.setUrl ("jdbc:mysql://localhost:3306/test");
dataSource.setUsername("root");
dataSource.setPassword("root");
// 获取连接
Connection connection = dataSource.getConnection();
 
// 执行查询
PreparedStatement statement = connection.prepareStatement ("select * from user");
// 获取查询结果进行处理
ResultSet resultSet = statement.executeQuery();
while (resultSet.next()) {
	…
}
 
// 关闭资源
statement.close();
resultSet.close();
connection.close();
```

# 07 | 使用 JdbcTemplate 访问关系型数据库

**订单数据模型**

Order 类的定义如下代码所示：

```java
public class Order{

    private Long id; //订单Id
    private String orderNumber; //订单编号
    private String deliveryAddress; //物流地址
    private List<Goods> goodsList;  //商品列表
    //省略了 getter/setter
}
```

Order 对应的数据库 Schema 定义如下代码所示：

```sql
DROP TABLE IF EXISTS `order`;
 
create table `order` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `order_number` varchar(50) not null,
    `delivery_address` varchar(100) not null,
  `create_time` timestamp not null DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
);
```

**使用 JdbcTemplate 实现查询**

首先我们需要引入对它的依赖：

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-jdbc</artifactId>
</dependency>
```

首先设计一个 OrderRepository 接口，用来抽象数据库访问的入口，如下代码所示：

```java
public interface OrderRepository {
    Order getOrderById(Long orderId);
}
```

构建一个 OrderJdbcRepository 类并实现 OrderRepository 接口，如下代码所示：

```java
@Repository("orderJdbcRepository")
public class OrderJdbcRepository implements OrderRepository {
 
    private JdbcTemplate jdbcTemplate;
 
    @Autowired
    public OrderJdbcRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }
  
    @Override
    public Order getOrderById(Long orderId) {
        Order order = jdbcTemplate.queryForObject(
          "select id, order_number, delivery_address from `order` where id=?", 
          this::mapRowToOrder, 
          orderId
        );
        return order;
    }
  
    private Order mapRowToOrder(ResultSet rs, int rowNum) throws SQLException {
        return new Order(
            rs.getLong("id"),
            rs.getString("order_number"),
            rs.getString("delivery_address")
        );
    }
}
```

**使用 JdbcTemplate 实现插入**

```java
public Long saveOrderWithJdbcTemplate(Order order) {
 
    PreparedStatementCreator psc = new PreparedStatementCreator() {
        @Override
        public PreparedStatement createPreparedStatement(Connection con) throws SQLException {
            PreparedStatement ps = con.prepareStatement(
                "insert into `order` (order_number, delivery_address) values (?, ?)",
                Statement.RETURN_GENERATED_KEYS
            );
            ps.setString(1, order.getOrderNumber());
            ps.setString(2, order.getDeliveryAddress());
            return ps;
        }
    };
 
    KeyHolder keyHolder = new GeneratedKeyHolder();
    jdbcTemplate.update(psc, keyHolder);
  
    return keyHolder.getKey().longValue();
}
```

在 PreparedStatement 的创建过程中设置了 Statement.RETURN_GENERATED_KEYS 用于返回自增主键。然后构建了一个 GeneratedKeyHolder 对象用于保存所返回的自增主键。

**使用 SimpleJdbcInsert 简化数据插入过程**

Spring Boot 针对数据插入场景专门提供了一个 SimpleJdbcInsert 工具类，SimpleJdbcInsert 本质上是在 JdbcTemplate 的基础上添加了一层封装。

对 SimpleJdbcInsert 初始化，代码如下：

```java
private SimpleJdbcInsert orderInserter;
 
public OrderJdbcRepository(JdbcTemplate jdbcTemplate) {
    this.jdbcTemplate = jdbcTemplate;
    this.orderInserter = new SimpleJdbcInsert(jdbcTemplate)
      .withTableName("`order`")
      .usingGeneratedKeyColumns("id");
    this.orderGoodsInserter = new SimpleJdbcInsert(jdbcTemplate).withTableName("order_goods");
}
```

实现 Order 对象的插入，代码如下：

```javaß
private Long saveOrderWithSimpleJdbcInsert(Order order) {
    Map<String, Object> values = new HashMap<String, Object>();
    values.put("order_number", order.getOrderNumber());
    values.put("delivery_address", order.getDeliveryAddress());

    Long orderId = orderInserter.executeAndReturnKey(values).longValue();
    return orderId;
}
```

# 08 | JdbcTemplate 数据访问实现原理

JdbcTemplate 是基于模板方法模式和回调机制，解决了原生 JDBC 中的复杂性问题。

**JdbcTemplate 源码解析**

JdbcTemplate 的 execute(StatementCallback action) 方法，如下所示：

```java
public <T> T execute(StatementCallback<T> action) throws DataAccessException {
    Assert.notNull(action, "Callback object must not be null");

    Connection con = DataSourceUtils.getConnection(obtainDataSource());
    Statement stmt = null;
    try {
        stmt = con.createStatement();
        applyStatementSettings(stmt);
        T result = action.doInStatement(stmt);
        handleWarnings(stmt);
        return result;
    } catch (SQLException ex) {
        String sql = getSql(action);
        JdbcUtils.closeStatement(stmt);
        stmt = null;
        DataSourceUtils.releaseConnection(con, getDataSource());
        con = null;
        throw translateException("StatementCallback", sql, ex);
    } finally {
        JdbcUtils.closeStatement(stmt);
        DataSourceUtils.releaseConnection(con, getDataSource());
    }
}
```

> catch 与 finally 重复代码有必要吗？

StatementCallback 回调接口定义代码如下：

```java
public interface StatementCallback<T> {
 
    T doInStatement(Statement stmt) throws SQLException, DataAccessException;
}
```

在 JdbcTemplate 中，还存在另一个 execute(final String sql) 方法，该方法中恰恰使用了 execute(StatementCallback action) 方法，代码如下：

```java
class ExecuteStatementCallback implements StatementCallback<Object>, SqlProvider {
    @Override
    @Nullable
    public Object doInStatement(Statement stmt) throws SQLException {
        stmt.execute(sql);
        return null;
    }
    @Override
    public String getSql() {
        return sql;
    }
}

public void execute(final String sql) throws DataAccessException {
    if (logger.isDebugEnabled()) {
        logger.debug("Executing SQL statement [" + sql + "]");
    }

    execute(new ExecuteStatementCallback());
}
```

JdbcTemplate 基于 JDBC 的原生 API，把模板方法和回调机制结合在了一起，为我们提供了简洁且高扩展的实现方案，值得我们分析和应用。

# 09 | Spring Data 如何对数据访问过程统一抽象？

Spring Data 是 Spring 家族中专门用于数据访问的开源框架，其对数据访问过程的抽象主要体现在两个方面：① 提供了一套 Repository 接口定义及实现；② 实现了各种多样化的查询支持，接下来我们分别看一下。

**Repository 接口及实现**

Repository 接口是 Spring Data 中对数据访问的最高层抽象，接口定义如下所示：

```java
public interface Repository<T, ID> {
}
```

在 Spring Data 中，存在一大批 Repository 接口的子接口和实现类：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210409215021.png" alt="image-20210409215021417" style="zoom:67%;" />

其中 SimpleJpaRepository 类的 save 方法如下代码所示：

```java
private final JpaEntityInformation<T, ?> entityInformation;
private final EntityManager em;
 
@Transactional
public <S extends T> S save(S entity) {
    if (entityInformation.isNew(entity)) {
        em.persist(entity);
        return entity;
    } else {
        return em.merge(entity);
    }
}
```

上述 save 方法依赖于 JPA 规范中的 EntityManager。

**多样化查询支持**

- @Query 注解

这个注解位于 org.springframework.data.jpa.repository 包中，如下所示：

```java
package org.springframework.data.jpa.repository;
 
public @interface Query {
    String value() default "";
    String countQuery() default "";
    String countProjection() default "";
    boolean nativeQuery() default false;
    String name() default "";
    String countName() default "";
}
```

使用 @Query 注解查询的典型例子如下：

```java
public interface AccountRepository extends JpaRepository<Account, Long> {
    @Query("select a from Account a where a.userName = ?1") 
    Account findByUserName(String userName);
}
```

因我们使用的是 JpaRepository，所以这种类似 SQL 语句的语法实际上是一种 JPA 查询语言，也就是所谓的 JPQL（Java Persistence Query Language）。

JPQL 与原生的 SQL 唯一的区别就是 JPQL FROM 语句后面跟的是对象，而原生 SQL 语句中对应的是数据表。

如果将 @Query 注解的 nativeQuery 设置为 true，那么 value 属性则需要指定具体的原生 SQL 语句。

- 方法名衍生查询

方法名衍生查询通过在方法命名上直接使用查询字段和参数，Spring Data 就能自动识别相应的查询条件并组装对应的查询语句。

想要使用方法名实现衍生查询，我们需要对 Repository 中定义的方法名进行一定约束。首先我们需要指定一些查询关键字，常见的关键字如下表所示：

![Lark20201215-174017.png](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210409221850.png)

其次需要指定查询字段和一些限制性条件，例如“firstname”和“lastname”。

如果我们在一个 Repository 中同时指定了 @Query 注解和方法名衍生查询，那么 Spring Data 会具体执行哪一个呢？

在 Spring Data 中，可以定义查询策略，如下代码所示：

```java
public interface QueryLookupStrategy {
 
    public static enum Key {
        CREATE, USE_DECLARED_QUERY, CREATE_IF_NOT_FOUND;

        public static Key create(String xml) {
            if (!StringUtils.hasText(xml)) {
                return null;
            }
            return valueOf(xml.toUpperCase(Locale.US).replace("-", "_"));
        }
    }
}
```

CREATE 策略指的是根据方法名创建查询，即方法名衍生查询。

USE_DECLARED_QUERY 指的是声明方式，即使用 @Query 注解。

CREATE_IF_NOT_FOUND 会先查找 @Query 注解，如果查到没有，会再去找与方法名相匹配的查询。

- QueryByExample 机制

如果查询条件中使用的字段非常多，怎么办呢？

QueryByExample 可以翻译为按示例查询，是一种用户友好的查询技术。它允许我们动态创建查询，且不需要编写包含字段名称的查询方法。

QueryByExample 包括 Probe、ExampleMatcher 和 Example 这三个基本组件。

首先，我们需要在 OrderJpaRepository 接口的定义中继承 QueryByExampleExecutor 接口，如下代码所示：

```java
@Repository("orderJpaRepository")
public interface OrderJpaRepository extends JpaRepository<JpaOrder, Long>, QueryByExampleExecutor<JpaOrder> {
}
```

然后，我们在 JpaOrderService 中实现如下代码所示的 getOrderByOrderNumberByExample 方法：

```java
public JpaOrder getOrderByOrderNumberByExample(String orderNumber) {
    JpaOrder order = new JpaOrder();
    order.setOrderNumber(orderNumber);
 
    ExampleMatcher matcher = ExampleMatcher
      .matching()
      .withIgnoreCase()
      .withMatcher("orderNumber", GenericPropertyMatchers.exact())
      .withIncludeNullValues();
 
    Example<JpaOrder> example = Example.of(order, matcher);
 
    return orderJpaRepository.findOne(example).orElse(new JpaOrder());
}
```

- Specification 机制

如果我们要查询某个实体，但是给定的查询条件不固定，该怎么办呢？

这时我们通过动态构建相应的查询语句即可，而在 Spring Data JPA 中可以通过 JpaSpecificationExecutor 接口实现这类查询。

继承了 JpaSpecificationExecutor 的 OrderJpaRepository 定义如下代码所示：

```java
@Repository("orderJpaRepository")
public interface OrderJpaRepository 
  extends JpaRepository<JpaOrder, Long>, JpaSpecificationExecutor<JpaOrder> {
}
```

对于 JpaSpecificationExecutor 接口而言，它背后使用的就是 Specification 接口：

```java
public interface Specification {
    Predicate toPredicate(
      Root<T> root, 
      CriteriaQuery<?> query, 
      CriteriaBuilder criteriaBuilder
    );
}
```

Root 对象代表所查询的根对象，我们可以通过 Root 获取实体的属性。
CriteriaQuery 代表一个顶层查询对象，用来实现自定义查询。
CriteriaBuilder 用来构建查询条件。

重构后的 getOrderByOrderNumberBySpecification 方法如下代码所示：

```java
public JpaOrder getOrderByOrderNumberBySpecification(String orderNumber) {
    JpaOrder order = new JpaOrder();
    order.setOrderNumber(orderNumber);

    @SuppressWarnings("serial")
    Specification<JpaOrder> spec = new Specification<JpaOrder>() {
        @Override
        public Predicate toPredicate(Root<JpaOrder> root, CriteriaQuery<?> query, CriteriaBuilder cb) {
            Path<Object> orderNumberPath = root.get("orderNumber");

            Predicate predicate = cb.equal(orderNumberPath, orderNumber);
            return predicate;
        }
    };

    return orderJpaRepository.findOne(spec).orElse(new JpaOrder());     
}
```

首先我们从 root 对象中获取了“orderNumber”属性，然后通过 cb.equal 方法将该属性与传入的 orderNumber 参数进行了比对，从而实现了查询条件的构建过程。

# 10 | 使用 Spring Data JPA 访问关系型数据库

JPA 全称是 JPA Persistence API，即 Java 持久化 API，它是一种 ORM（Object Relational Mapping，对象关系映射）技术。

**引入 Spring Data JPA**

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>
```

**定义实体类**

order-service 中存在两个主要领域对象，即 Order 和 Goods。这两个领域对象分别命名为 JpaOrder 和 JpaGoods。

JpaGoods 定义如下代码所示：

```java
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.Table;
 
@Entity
@Table(name="goods")
public class JpaGoods {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;    
    private String goodsCode;
    private String goodsName;
    private Float price;    
    //省略 getter/setter
}
```

JpaOrder 定义如下代码所示：

```java
@Entity
@Table(name="`order`")
public class JpaOrder implements Serializable {
    private static final long serialVersionUID = 1L;
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String orderNumber;
    private String deliveryAddress;
 
    @ManyToMany(targetEntity=JpaGoods.class)
    @JoinTable(
      name = "order_goods", 
      joinColumns = @JoinColumn(name = "order_id", referencedColumnName = "id"), 
      inverseJoinColumns = @JoinColumn(name = "goods_id", referencedColumnName = "id")
    )
    private List<JpaGoods> goods = new ArrayList<>();
 
    //省略 getter/setter
}
```

这里使用了 @JoinTable 注解指定 order_goods 中间表，并通过 joinColumns 和 inverseJoinColumns 注解分别指定中间表中的字段名称以及引用两张主表中的外键名称。

**定义 Repository**

OrderJpaRepository 的定义如下代码所示：

```java
@Repository("orderJpaRepository")
public interface OrderJpaRepository extends JpaRepository<JpaOrder, Long> {
}
```

OrderJpaRepository 实际上已经具备了访问数据库的基本 CRUD 功能。

