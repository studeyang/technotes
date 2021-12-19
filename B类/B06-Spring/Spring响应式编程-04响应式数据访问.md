# 17 | R2DBC：关系型数据库能具备响应式数据访问特性吗？

R2DBC 是 Reactive Relational Database Connectivity 的全称，即响应式关系型数据库连接，该规范允许驱动程序提供与关系型数据库之间的响应式和非阻塞集成。

**Spring Data R2DBC**

R2DBC 是由 Spring Data 团队领导的一项探索响应式数据库访问的尝试。R2DBC 的目标是定义具有背压支持的响应式数据库访问 API，该项目包含了三个核心组件。

- R2DBC SPI：定义了实现驱动程序的简约 API。
- R2DBC 客户端：提供了一个人性化的 API 和帮助类。
- R2DBC 驱动：截至目前，为 PostgreSQL、H2、Microsoft SQL Server、MariaDB 以及 MySQL 提供了 R2DBC 驱动程序。

如何使用？首先需引入依赖。

```xml
<!-- spring data r2dbc -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-r2dbc</artifactId>
</dependency>
 
<!-- r2dbc 连接池 -->
<dependency>
    <groupId>io.r2dbc</groupId>
    <artifactId>r2dbc-pool</artifactId>
</dependency>
 
<!--r2dbc mysql 库 -->
<dependency>
    <groupId>dev.miku</groupId>
    <artifactId>r2dbc-mysql</artifactId>
</dependency>
```

在引入 Spring Data R2DBC 之后，我们来使用该组件完成一个示例应用程序的实现。让我们先使用 MySQL 数据库来定义一张 ACCOUNT 表。

```java
USE `r2dbcs_account`;
 
DROP TABLE IF EXISTS `ACCOUNT`;
CREATE TABLE `ACCOUNT`(
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `ACCOUNT_CODE` varchar(100) NOT NULL,
  `ACCOUNT_NAME` varchar(100) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
 
INSERT INTO `account` VALUES ('1', 'account1', 'name1');
INSERT INTO `account` VALUES ('2', 'account2', 'name2');
```

然后，基于该数据库表定义一个实体对象。

```java
import org.springframework.data.annotation.Id;
import org.springframework.data.relational.core.mapping.Table;
 
@Table("account")
public class Account {
    @Id
    private Long id;
    private String accountCode;
    private String accountName;
    //省略 getter/setter
}
```

基于 Account 对象，我们可以设计如下所示的 Repository。

```java
import org.springframework.data.r2dbc.repository.Query;
import org.springframework.data.r2dbc.repository.R2dbcRepository;
 
public interface ReactiveAccountRepository extends R2dbcRepository<Account, Long> {
 
    @Query("insert into ACCOUNT (ACCOUNT_CODE, ACCOUNT_NAME) values (:accountCode,:accountName)")
    Mono<Boolean> addAccount(String accountCode, String accountName);

    @Query("SELECT * FROM account WHERE id =:id")
    Mono<Account> getAccountById(Long id);
}
```

为了访问数据库，最后要做的一件事情就是指定访问数据库的地址，如下所示。

```yaml
spring:
   r2dbc:
     url: r2dbcs:mysql://127.0.0.1:3306/r2dbcs_account
     username: root
     password: root
```

最后，我们构建一个 AccountController 来对 ReactiveAccountRepository 进行验证。

```java
@RestController
@RequestMapping(value = "accounts")
public class AccountController {
 
    @Autowired
    private ReactiveAccountRepository reactiveAccountRepository;
 
    @GetMapping(value = "/{accountId}")
    public Mono<Account> getAccountById(@PathVariable("accountId") Long accountId) {

        Mono<Account> account = reactiveAccountRepository.getAccountById(accountId);
        return account;
    }
 
    @PostMapping(value = "/")
    public Mono<Boolean> addAccount(@RequestBody Account account) {

        return reactiveAccountRepository.addAccount(account.getAccountCode(), account.getAccountName());
    }
}
```









