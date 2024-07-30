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
- 密码 - 保护或隐藏数据免遭窥探
- 会话管理 - 每个用户的时间敏感状态

## 1.2 核心概念

### 主题（Subject）

“主题”一词是一个安全术语，基本上意味着“当前正在执行的用户”。它只是不被称为“用户”，因为“用户”一词通常与人类相关联。在安全领域，术语“主题”可以指人类，也可以指第三方进程、守护程序帐户或任何类似的东西。它只是意味着“当前正在与软件交互的事物”。不过，大多数情况下，您可以将其视为 Shiro 的“用户”概念。

*获取主题：*

```java
Subject currentUser = SecurityUtils.getSubject();
```

### 安全管理器（SecurityManager）

Subject 代表当前用户的安全操作，SecurityManager 管理所有用户的安全操作。它是 Shiro 架构的核心，充当一种“伞”对象，引用许多形成对象图的内部嵌套安全组件。然而，一旦配置了 SecurityManager 及其内部对象图，通常就不再管它了，应用程序开发人员几乎将所有时间都花在了 Subject API 上。

*使用 INI 配置 Shiro：*

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

*加载 shiro.ini 配置文件：*

```java
//1. 加载INI配置
Factory<SecurityManager> factory =
new IniSecurityManagerFactory("classpath:shiro.ini");

//2. 创建 SecurityManager
SecurityManager securityManager = factory.getInstance();

//3. Make it accessible
SecurityUtils.setSecurityManager(securityManager);
```

### 领域（Realms）

Shiro 中的第三个也是最后一个核心概念是领域。 Realm 充当 Shiro 和应用程序安全数据之间的“桥梁”或“连接器”。也就是说，当实际与安全相关数据（例如用户帐户）进行交互以执行身份验证（登录）和授权（访问控制）时，Shiro 从应用程序配置的一个或多个领域中查找其中的内容。

从这个意义上说，Realm 本质上是一个特定于安全方面的 DAO：它封装了数据源的连接详细信息，使得 Shiro 可以使用相关数据。配置 Shiro 时，您必须至少指定一个用于身份验证和/或授权的 Realm。

Shiro 提供开箱即用的 Realms 来连接到许多安全数据源，例如 LDAP、关系数据库 (JDBC)、文本配置源（例如 INI 和属性文件）等等。如果默认 Realm 不能满足您的需求，您可以插入自己的 Realm 实现来表示自定义数据源。下面是使用 LDAP 目录作为应用程序的 Realms 的配置示例。

*连接到 LDAP 用户数据存储的领域配置片段示例：*

```ini
[main]
ldapRealm = org.apache.shiro.realm.ldap.JndiLdapRealm
ldapRealm.userDnTemplate = uid={0},ou=users,dc=mycompany,dc=com
ldapRealm.contextFactory.url = ldap://ldapHost:389
ldapRealm.contextFactory.authenticationMechanism = DIGEST-MD5 
```

## 1.3 认证（Authentication）

身份认证是验证用户身份的过程，通常有三步。

- 收集用户的身份信息（称为主体 principals）和身份证明（称为凭证 credentials）
- 将主体和凭证提交到系统
- 如果提交的凭证与系统中该用户身份相匹配，则该用户被视为已通过身份验证

此过程的一个常见示例是用户名/密码组合。当大多数用户登录软件应用程序时，他们通常会提供用户名（主体）和密码（凭证 ）。如果系统中存储的密码与用户指定的密码相匹配，则认为他们已通过身份验证。

*主题登录：*

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

*处理失登录败：*

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

## 1.4 授权（Authorization）

授权本质上是控制用户可以在应用程序中访问哪些内容，例如资源、网页等。

大多数用户通过使用角色和权限等概念来执行访问控制，允许用户执行或不执行某些操作，通常取决于分配给他们的角色和/或权限。然后，您的应用程序可以根据对这些角色和权限的检查来控制公开哪些功能。正如您所期望的，Subject API 允许您非常轻松地执行角色和权限检查。

*角色检查：*

```java
if ( subject.hasRole(“administrator”) ) {
    //show the ‘Create User’ button
} else {
    //grey-out the button?
} 
```

权限检查是执行授权的另一种方式。如上例所示检查角色存在一个重大缺陷：您无法在运行时添加或删除角色。您的代码是使用角色名称进行硬编码的，因此如果您更改了角色名称和/或配置，您的代码将会被破坏！如果您需要能够在运行时更改角色的含义，或者根据需要添加或删除角色，则必须依赖其他东西。

为此，Shiro 支持其权限概念。权限是功能的原始声明，例如“打开一扇门”、“创建博客条目”、“删除'jsmith'用户”等。通过让权限反映应用程序的原始功能，当您想更改应用程序的功能时，只需更改权限检查。反过来，您可以在运行时根据需要向角色或用户分配权限。

*权限检查：*

```java
if ( subject.isPermitted(“user:create”) ) {
    //show the ‘Create User’ button
} else {
    //grey-out the button?
} 
```

这样，任何分配了“user:create”权限的角色或用户都可以单击“创建用户”按钮，并且这些角色和分配甚至可以在运行时更改，从而为您提供非常灵活的安全模型。

“user:create”字符串遵守了某些解析的约定。 Shiro 通过其 WildcardPermission 开箱即用地支持此约定。尽管超出了本文的介绍范围，但您将看到 WildcardPermission 在创建安全策略时非常灵活，甚至支持实例级访问控制等功能。

*实例级权限检查：*

```java
if ( subject.isPermitted(“user:delete:jsmith”) ) {
    //delete the ‘jsmith’ user
} else {
    //don’t delete ‘jsmith’
}
```

此示例表明，如果需要，您可以控制对各个资源的访问，甚至可以控制到非常细粒度的实例级别。

这就是 Shiro 授权功能的简要概述。虽然大多数安全框架仅限于身份验证和授权，但 Shiro 提供了更多功能。接下来我们将讨论 Shiro 的高级会话管理功能。

## 1.5 会话管理（Session Management）

Apache Shiro 提供了安全框架领域中独特的东西：可以在任何应用层和架构层中使用的一致性会话 API。

也就是说，您可以在任何应用程序中使用 Shiro Sessions API，从小型守护程序、独立应用程序，到最大的集群 Web 应用程序。开发人员现在可以选择在任何层中使用会话 API，而不是 Servlet 或 EJB 容器内。

Shiro 的架构允许您存储一条插入的会话数据，例如企业缓存、关系数据库、NoSQL 等。这意味着您只需配置一次会话集群，无论您的部署环境如何（Tomcat、Jetty、JEE Server 或独立应用程序），它都会以相同的方式工作，无需根据您部署应用程序的方式重新配置您的应用程序。

Shiro 会话的另一个好处是可以跨客户端共享会话数据。例如，Swing 桌面客户端可以加入同一个 Web 应用程序会话。那么如何访问主题的会话呢？

*获取主题的会话：*

```java
Session session = subject.getSession();
Session session = subject.getSession(boolean create);
```

这些方法在概念上与 HttpServletRequest API 相同。第一个方法将返回主题的现有会话，或者如果还没有会话，它将创建一个新会话并返回它。第二种方法接受一个布尔参数，用于确定是否创建新会话（如果尚不存在）。

一旦获得了主题的会话，就可以像使用 HttpSession 一样使用它。 Shiro 团队认为 HttpSession API 对于 Java 开发人员来说是最舒服的，因此我们保留了它的大部分感觉。当然，最大的区别是您可以在任何应用程序中使用 Shiro Sessions，而不仅仅是 Web 应用程序。

*会话 API：*

```java
Session session = subject.getSession();
session.getAttribute("key", someValue);
Date start = session.getStartTimestamp();
Date timestamp = session.getLastAccessTime();
session.setTimeout(millis);
...
```

## 1.6 密码（Cryptography）

密码是隐藏或混淆数据的过程，使窥探者无法理解它。Shiro 在密码方面的目标是简化并提供 JDK 的密码学支持。

密码通常并不特定于主题，您可以在任何地方使用 Shiro 的加密支持。Shiro 密码专注于两个领域：哈希加密（也称为消息摘要）和密码加密。让我们更详细地看看这两个。

### 哈希（Hashing）

如果您使用过 JDK 的 MessageDigest 类，您很快就会意识到它使用起来有点麻烦。它有一个笨拙的基于静态方法工厂的 API，而不是面向对象的 API，并且您被迫捕获可能永远不需要捕获的已检查异常。如果您需要对消息摘要输出进行十六进制编码或 Base64 编码，则只能靠您自己了——两者都没有标准的 JDK 支持。 Shiro 通过干净直观的哈希 API 解决了这些问题。

例如，让我们考虑一下相对常见的情况：对文件进行 MD5 哈希处理并确定该哈希值的十六进制值。（这称为“校验和”）

这在文件下载时经常使用，用户可以对下载的文件执行自己的 MD5 哈希，并断言其“校验和”与下载网站上的“校验和”匹配。如果它们匹配，用户就可以认为文件在传输过程中没有被篡改。

以下是您在没有 Shiro 的情况下尝试执行此操作的方法：

1. 将文件转换为字节数组。在 JDK 中您需要创建一个 FileInputStream，然后使用字节缓冲区并抛出适当的 IOException 等。
2. 使用 MessageDigest 类对字节数组进行哈希处理，处理适当的异常。
3. 将哈希字节数组编码为十六进制字符。

*JDK 的 MessageDigest：*

```java
try {
    MessageDigest md = MessageDigest.getInstance("MD5");
    md.digest(bytes);
    byte[] hashed = md.digest();
} catch (NoSuchAlgorithmException e) {
    e.printStackTrace();
}
```

现在介绍如何使用 Shiro 做同样的事情。

```java
String hex = new Md5Hash(myFile).toHex(); 
```

SHA-512 哈希和 Base64 编码也同样简单。

```java
String encodedPassword =
    new Sha512Hash(password, salt, count).toBase64();
```

### 密码（Ciphers）













