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



























