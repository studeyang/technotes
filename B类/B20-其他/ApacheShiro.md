> 介绍：
>
> - [Application Security With Apache Shiro](https://www.infoq.com/articles/apache-shiro/)
> - [10 Minute Tutorial on Apache Shiro](https://shiro.apache.org/10-minute-tutorial.html)

# 一、介绍

## 1.1 什么是 Apache Shiro？

Apache Shiro 是一个功能强大且易于使用的 Java 安全框架，表现在身份验证、授权、加密和会话管理，可用于保护任何应用程序，小到命令行应用程序、移动应用程序，大到 Web 和企业应用程序。

应用程序安全性的 4 个基石：

- 身份验证 - 证明用户身份，通常称为用户“登录”
- 授权 - 访问控制
- 密码学 - 保护或隐藏数据免遭窥探
- 会话管理 - 每个用户的时间敏感状态

## 1.2 核心概念

### Subject

“主题”一词是一个安全术语，基本上意味着“当前正在执行的用户”。它只是不被称为“用户”，因为“用户”一词通常与人类相关联。在安全领域，术语“主题”可以指人类，也可以指第三方进程、守护程序帐户或任何类似的东西。它只是意味着“当前正在与软件交互的事物”。不过，大多数情况下，您可以将其视为 Shiro 的“用户”概念。

Acquiring the Subject：

```java
Subject currentUser = SecurityUtils.getSubject();
```

### SecurityManager

Subject 代表当前用户的安全操作，SecurityManager 管理所有用户的安全操作。它是 Shiro 架构的核心，充当一种“伞”对象，引用许多形成对象图的内部嵌套安全组件。然而，一旦配置了 SecurityManager 及其内部对象图，通常就不再管它了，应用程序开发人员几乎将所有时间都花在了 Subject API 上。

使用 INI 配置 Shiro：

```ini
[main]
cm = org.apache.shiro.authc.credential.HashedCredentialsMatcher
cm.hashAlgorithm = SHA-512
cm.hashIterations = 1024
# Base64 encoding (less text):
cm.storedCredentialsHexEncoded = false

[users]
jdoe = TWFuIGlzIGRpc3Rpbmd1aXNoZWQsIG5vdCBvbmx5IGJpcyByZWFzb2
asmith = IHNpbmd1bGFyIHBhc3Npb24gZnJvbSBvdGhlciBhbXNoZWQsIG5vdCB
```

加载 shiro.ini 配置文件：

```java
//1. 加载INI配置
Factory<SecurityManager> factory =
new IniSecurityManagerFactory("classpath:shiro.ini");

//2. 创建 SecurityManager
SecurityManager securityManager = factory.getInstance();

//3. Make it accessible
SecurityUtils.setSecurityManager(securityManager);
```

### Realms

Shiro 中的第三个也是最后一个核心概念是领域。 Realm 充当 Shiro 和应用程序安全数据之间的“桥梁”或“连接器”。也就是说，当实际与安全相关数据（例如用户帐户）进行交互以执行身份验证（登录）和授权（访问控制）时，Shiro 从应用程序配置的一个或多个领域中查找其中的内容。

从这个意义上说，Realm 本质上是一个特定于安全方面的 DAO：它封装了数据源的连接详细信息，使得 Shiro 可以使用相关数据。配置 Shiro 时，您必须至少指定一个用于身份验证和/或授权的 Realm。

Shiro 提供开箱即用的 Realms 来连接到许多安全数据源，例如 LDAP、关系数据库 (JDBC)、文本配置源（例如 INI 和属性文件）等等。如果默认 Realm 不能满足您的需求，您可以插入自己的 Realm 实现来表示自定义数据源。下面是使用 LDAP 目录作为应用程序的 Realms 的配置示例。

```ini
[main]
ldapRealm = org.apache.shiro.realm.ldap.JndiLdapRealm
ldapRealm.userDnTemplate = uid={0},ou=users,dc=mycompany,dc=com
ldapRealm.contextFactory.url = ldap://ldapHost:389
ldapRealm.contextFactory.authenticationMechanism = DIGEST-MD5 
```

## 1.3 Authentication

身份验证是验证用户身份的过程，通常有三步。

- 收集用户的身份信息（称为主体 principals）和身份证明（称为凭证 credentials）
- 将主体和凭证提交到系统
- 如果提交的凭证与系统中该用户身份相匹配，则该用户被视为已通过身份验证

此过程的一个常见示例是用户名/密码组合。当大多数用户登录软件应用程序时，他们通常会提供用户名（主体）和密码（凭证 ）。如果系统中存储的密码与用户指定的密码相匹配，则认为他们已通过身份验证。

用户登录：

```java
//1. Acquire submitted principals and credentials:
AuthenticationToken token =
new UsernamePasswordToken(username, password);
//2. Get the current Subject:
Subject currentUser = SecurityUtils.getSubject();
//3. Login
currentUser.login(token);
```

当调用登录方法时，SecurityManager 将接收 AuthenticationToken 并将其分派到一个或多个已配置的 Realms，以允许每个 Realms 根据需要执行身份验证检查。每个 Realms 都能够根据需要对提交的 AuthenticationToken 做出响应。但是如果登录失败会发生什么？如果用户指定了错误的密码怎么办？您可以使用 Shiro 的运行时 AuthenticationException 来处理故障。

```java
//3. Login:
try {
    currentUser.login(token);
} catch (IncorrectCredentialsException ice) {
    ...
} catch (LockedAccountException lae) {
    ...
}
catch (AuthenticationException ae) {
    ...
} 
```

您可以选择捕获 AuthenticationException 异常，例如，向用户显示通用的“用户名或密码不正确”消息。

主题成功登录后，他们被视为已通过身份验证，通常您允许他们使用您的应用程序。但用户证明了他们的身份并不意味着他们可以在您的应用程序中做任何他们想做的事情。这就引出了下一个问题：“我如何控制用户可以做什么？不可以做什么？”

决定允许用户做什么称为授权。接下来我们将介绍 Shiro 如何启用授权。

## 1.4 Authorization



















