> 介绍：
>
> - [Application Security With Apache Shiro](https://www.infoq.com/articles/apache-shiro/)
> - [10 Minute Tutorial on Apache Shiro](https://shiro.apache.org/10-minute-tutorial.html)

# 一、介绍

## 1.1 什么是 Apache Shiro？

Apache Shiro 是一个功能强大且易于使用的 Java 安全框架，表现在身份认证、授权、加密和会话管理，可用于保护任何应用程序，小到命令行应用程序、移动应用程序，大到 Web 和企业应用程序。

应用程序安全性的 4 个基石：

- 身份验证 - 证明用户身份，通常称为用户“登录”
- 授权 - 访问控制
- 加密 - 保护或隐藏数据免遭窥探
- 会话管理 - 每个用户的时间敏感状态

## 1.2 核心概念

### 主题（Subject）

“主题”一词是一个安全术语，基本上意味着“当前正在执行的用户”。它只是不被称为“用户”，因为“用户”一词通常与人类相关联。在安全领域，术语“主题”可以指人类，也可以指第三方进程、守护帐户或任何类似的东西。它只是意味着“当前正在与软件交互的事物”。不过，大多数情况下，您可以将其视为 Shiro 的“用户”概念。

*清单 1. 获取主题：*

```java
Subject currentUser = SecurityUtils.getSubject();
```

### 安全管理器（SecurityManager）

主题（Subject）的“幕后”对应的是 SecurityManager。Subject 管理的是一个用户的安全操作，SecurityManager 管理所有用户的安全操作。SecurityManager 引用了许多内部嵌套安全组件，然而，一旦配置了 SecurityManager，通常就不用再管它了，只需关注 Subject API 即可。

那么如何配置 SecurityManager 呢？这取决于您的应用程序环境，例如，Web 应用程序通常会在 web.xml 中指定 Shiro Servlet Filter。

> 见：【1.7 Web 支持】*清单 14. web.xml 中的 ShiroFilter*

每个应用程序通常只有一个 SecurityManager 实例，它本质上是一个单例。默认的 SecurityManager 实现是 POJO，可以通过任何与 POJO 兼容的配置机制进行配置，例如，普通 Java 代码、Spring XML、YAML、.properties 和 .ini 文件等。

Shiro 默认基于文本 INI 配置，INI 易于阅读、使用简单，并且需要很少的依赖项。

*清单 2. 使用 INI 配置 Shiro：*

```ini
[main]
cm = org.apache.shiro.authc.credential.HashedCredentialsMatcher
cm.hashAlgorithm = SHA-512
cm.hashIterations = 1024
# Base64 encoding (less text):
cm.storedCredentialsHexEncoded = false
iniRealm.credentialsMatcher = $cm

[users]
jdoe = TWFuIGlzIGRpc3Rpbmd1aXNoZWQsIG5vdCBvbmx5IGJpcyByZWFzb2
asmith = IHNpbmd1bGFyIHBhc3Npb24gZnJvbSBvdGhlciBhbXNoZWQsIG5vdCB
```

我们看到了配置 SecurityManager 实例的 INI 配置，INI 有两个部分：[main] 和 [users]。

[main] 部分是您配置 SecurityManager 对象以及 SecurityManager 使用对象（如领域）的地方。在此示例中，我们正在配置两个对象：

1. cm 对象，它是 Shiro 的 HashedCredentialsMatcher 类的实例。
2. iniRealm 对象，它是 SecurityManager 用来表示用户帐户的组件。

在 [users] 部分，您可以指定用户帐户列表，以便测试使用。在此示例中，我们配置了两个用户：

1. 用户名为`jdoe`，密码为`TWFuIGlzIGRpc3Rpbmd1aXNoZWQsIG5vdCBvbmx5IGJpcyByZWFzb2`的用户。
2. 用户名为`asmith`，密码为`IHNpbmd1bGFyIHBhc3Npb24gZnJvbSBvdGhlciBhbXNoZWQsIG5vdCB`的用户。

INI 是配置 Shiro 的一种简单方法。有关 INI 配置的更多详细信息，请参阅 Shiro 的文档。

*清单 3. 加载 shiro.ini 配置文件：*

```java
//1. 加载INI配置
Factory<SecurityManager> factory =
new IniSecurityManagerFactory("classpath:shiro.ini");

//2. 创建 SecurityManager
SecurityManager securityManager = factory.getInstance();

//3. 使 SecurityManager 单例可供应用程序访问
SecurityUtils.setSecurityManager(securityManager);
```

### 领域（Realms）

Shiro 的最后一个核心概念是领域（Realms）。 Realm 充当 Shiro 和安全数据之间的“桥梁”。也就是说，在与安全数据（例如用户帐户）进行交互时，例如执行身份验证（登录）和授权（访问控制），Shiro 从应用程序配置的一个或多个 Realm 中查找其中的内容。

从这个意义上说，Realm 本质上是一个安全方面的 DAO：它封装了数据源连接的详细信息，使得 Shiro 可以使用相关数据。配置 Shiro 时，您必须至少指定一个用于身份验证和授权的 Realm。

Shiro 提供开箱即用的 Realms 来连接一些安全数据源，例如 LDAP、关系数据库 (JDBC)、文本配置源（例如 INI 和配置文件）等等。如果默认的 Realm 不能满足您的需求，您可以添加自己的 Realm 实现自定义数据源。下面是使用 LDAP 作为应用程序的 Realms 的配置示例。

*清单 4. 连接到 LDAP 用户数据存储的 Realm 配置片段：*

```ini
[main]
ldapRealm = org.apache.shiro.realm.ldap.JndiLdapRealm
ldapRealm.userDnTemplate = uid={0},ou=users,dc=mycompany,dc=com
ldapRealm.contextFactory.url = ldap://ldapHost:389
ldapRealm.contextFactory.authenticationMechanism = DIGEST-MD5 
```

## 1.3 认证（Authentication）

认证是验证用户身份的过程，通常有三步。

- 收集用户的身份信息（称为主体 Principals）和身份证明（称为凭证 Credentials）
- 将主体和凭证提交到系统
- 如果提交的凭证与系统中该用户身份相匹配，则该用户被视为已通过认证

常见的认证方式是用户名/密码组合。当用户登录软件应用程序时，他们通常会提供用户名（主体）和密码（凭证 ），如果系统中存储的密码与用户指定的密码相匹配，则认为该用户已通过身份认证。

*清单 5. Subject 登录：*

```java
//1. Acquire submitted principals and credentials:
AuthenticationToken token = new UsernamePasswordToken(username, password);
//2. Get the current Subject:
Subject currentUser = SecurityUtils.getSubject();
//3. Login
currentUser.login(token);
```

当调用登录方法时，SecurityManager 将接收 AuthenticationToken 并将其分派到一个或多个已配置的 Realms，以允许每个 Realms 根据需要执行身份检查。但是如果登录失败会发生什么？如果用户指定了错误的密码怎么办？您可以使用 Shiro 的运行时 AuthenticationException 来处理异常。

*清单 6. 处理失登录败：*

```java
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

您可以选择捕获 AuthenticationException 异常，向用户提示“用户名或密码不正确”消息。

Subject 登录成功后，他们被视为已通过身份认证，表示您允许他们使用您的应用程序。但用户认证了他们的身份并不意味着他们可以在您的应用程序中做任何事情。这就引出了下一个问题：“我如何控制用户可以做什么？不可以做什么？”

决定允许用户做什么称为授权。接下来我们将介绍 Shiro 如何启用授权。

## 1.4 授权（Authorization）

授权本质上是控制用户可以在应用程序中访问哪些内容，例如资源、网页等。

大多数用户通过使用角色和权限等概念来执行访问控制，允许用户执行某些操作，通常取决于分配给他们的角色或权限。然后，您的应用程序可以根据这些角色和权限，来控制公开哪些资源。

*清单 7. 角色检查：*

```java
if ( subject.hasRole("administrator") ) {
    //show the 'Create User' button
} else {
    //grey-out the button
} 
```

权限检查是执行授权的另一种方式。如上例所示的角色检查存在一个重大缺陷：您无法在运行时添加或删除角色。

您的代码是使用角色名称进行硬编码的，因此如果您更改了角色名称或配置，您的代码将会被破坏！如果您需要能够在运行时更改角色的含义，或者根据需要添加或删除角色，则必须依赖其他东西。

为此，Shiro 支持权限的概念。权限是功能的原始声明，例如“打开一扇门”、“创建博客条目”、“删除'jsmith'用户”等。通过权限来反映应用程序的原始功能，当您想更改应用程序的功能时，只需更改权限检查。反过来，您可以在运行时根据需要向角色或用户分配权限。

*清单 8. 权限检查：*

```java
if ( subject.isPermitted("user:create") ) {
    //show the 'Create User' button
} else {
    //grey-out the button
} 
```

这样，任何分配了`user:create`权限的角色或用户都可以单击“创建用户”按钮，并且这些角色和分配甚至可以在运行时更改，从而为您提供非常灵活的安全模型。

`user:create`字符串遵守了某些解析的约定。 Shiro 通过其 WildcardPermission 开箱即用地支持此约定。尽管超出了本文的介绍范围，但您将看到 WildcardPermission 在创建安全策略时非常灵活，甚至支持实例级访问控制等功能。

*清单 9. 实例级权限检查：*

```java
if ( subject.isPermitted(“user:delete:jsmith”) ) {
    //delete the ‘jsmith’ user
} else {
    //don’t delete ‘jsmith’
}
```

此示例表明，如果需要，您可以控制对各个资源的访问，甚至可以控制到非常细粒度的实例级别。

这就是 Shiro 授权功能的简要概述。接下来我们将讨论 Shiro 的高级会话管理功能。

## 1.5 会话管理（Session Management）

Apache Shiro 提供了安全框架领域中独特的东西：可以在任何应用程序中使用一致性会话 API。

也就是说，您可以在任何应用程序中使用 Shiro Sessions API，从小型守护程序、独立应用程序，到大型集群 Web 应用程序。开发人员现在可以在任何应用程序中使用会话 API，而不是 Servlet 或 EJB 容器内。

【Shiro 允许您存储一条插入的会话数据，例如缓存、关系型数据库、NoSQL 等。这意味着您只需配置一次会话集群，无论您的部署环境如何（Tomcat、Jetty、JEE Server 或独立应用程序），它都会以相同的方式工作，无需根据您部署应用程序的方式重新配置您的应用程序。】

【Shiro 会话的另一个好处是可以跨客户端共享会话数据。例如，Swing 桌面客户端可以加入同一个 Web 应用程序会话。那么如何访问主题的会话呢？】

*清单 10. 获取主题的会话：*

```java
Session session = subject.getSession();
Session session = subject.getSession(boolean create);
```

这些方法在概念上与 HttpServletRequest API 相同。第一个方法将返回主题的现有会话，如果还没有会话，它将创建一个新会话并返回它。第二种方法接受一个布尔参数，用于确定是否创建新会话（如果尚不存在）。

一旦获得了主题的会话，就可以像使用 HttpSession 一样使用它。 Shiro 团队认为 HttpSession API 对于 Java 开发人员来说是最舒服的，因此我们保留了它的大部分东西。当然，最大的区别是您可以在任何应用程序中使用 Shiro Sessions，而不仅仅是 Web 应用程序中。

*清单 11. 会话 API：*

```java
Session session = subject.getSession();
session.getAttribute("key", someValue);
Date start = session.getStartTimestamp();
Date timestamp = session.getLastAccessTime();
session.setTimeout(millis);
...
```

## 1.6 加密（Cryptography）

加密是隐藏数据的过程，使窥探者无法理解它。在加密领域，Shiro 的目标是简化并提供 JDK 的密码支持。

加密通常并不特定于 Subject，您可以在任何地方使用 Shiro 的加密支持。Shiro 加密专注于两个领域：哈希加密（也称为消息摘要）和密文加密。让我们更详细地看看这两个。

### 哈希（Hashing）

如果您使用过 JDK 的 MessageDigest 类，您很快就会意识到它使用起来有点麻烦。

例如，让我们考虑一个相对常见的场景：对文件进行 MD5 哈希加密处理，并进行 Base64 编码。

产生密文数据称为校验和（checksum），这在文件下载时经常使用，用户可以对下载的文件执行自己的 MD5 哈希，并断言其校验和与下载网站上的校验和匹配。如果它们匹配，用户就可以认为文件在传输过程中没有被篡改。

以下是您在没有 Shiro 的情况下尝试执行此操作的方法：

1. 将文件转换为字节数组。在 JDK 中您需要创建一个 FileInputStream，然后使用字节缓冲区并抛出适当的 IOException 等。
2. 使用 MessageDigest 类对字节数组进行哈希处理，处理适当的异常。
3. 将哈希字节数组进行 Base64 编码。

*清单 12. JDK 的 MessageDigest：*

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

### 密文（Ciphers）

我们通常使用密文来保证数据安全，特别是在传输或存储数据时。

如果您使用过 JDK Cryptography API，特别是 javax.crypto.Cipher 类，您就会知道它可能是一头难以驯服的野兽。

Shiro 试图通过引入其 CipherService API 来简化加密的整个过程。CipherService 是大多数开发人员在加密数据时想要使用的，它是一种简单、无状态、线程安全的 API，可以在一个方法调用中完整地加密或解密数据。您所需要做的就是提供您的密钥。

例如，可以使用 256 位 AES 加密，如下面的清单所示。

*清单 13. Apache Shiro 的加密 API：*

```java
AesCipherService cipherService = new AesCipherService();
cipherService.setKeySize(256);

//创建一个测试密钥：
byte[] testKey = cipherService.generateNewKey();

//加密文件的字节：
byte[] encrypted = cipherService.encrypt(fileBytes, testKey);
```

Shiro 的 CipherService API 还有其他好处，例如能够支持基于流的加密/解密（如加密音频或视频）。

## 1.7 Web 支持

最后，我们将简要地介绍 Shiro 的 Web 支持。为 Web 应用程序设置 Shiro 非常简单，唯一需要做的就是在 web.xml 中定义 Shiro Servlet Filter。

*清单 14. web.xml 中的 ShiroFilter：*

```xml
<filter>
    <filter-name>ShiroFilter</filter-name>
    <filter-class>
        org.apache.shiro.web.servlet.IniShiroFilter
    </filter-class>
    <!-- no init-param means load the INI config
        from classpath:shiro.ini --> 
</filter>

<filter-mapping>
    <filter-name>ShiroFilter</filter-name>
     <url-pattern>/*</url-pattern>
</filter-mapping>
```

此过滤器可以读取上述 shiro.ini 配置。配置完成后，Shiro Filter 将过滤每个请求。

### 特定 URL 的过滤器链

Shiro 支持特定的过滤规则。它允许您为任何匹配的 URL 指定临时过滤器链，这比单独在 web.xml 中定义过滤器要灵活得多。清单 15 显示了 Shiro INI 中的配置片段。

*清单 15. 特定路径的过滤器链：*

```ini
[urls]
/assets/** = anon
/user/signup = anon
/user/** = user
/rpc/rest/** = perms[rpc:invoke], authc
/** = authc
```

[urls] 部分可供 Web 应用程序使用。对于每一行，等号左边的值表示 Web 应用程序资源路径，右侧的值定义了一个过滤器链，过滤器链是一个有序的 Servlet 过滤器列表（多个以逗号分隔）。您在上面看到的过滤器名称（anon、user、perms、authc）是 Shiro 提供的开箱即用的过滤器。

您可以在 web.xml 中仅定义 Shiro 过滤器，并在 shiro.ini 中定义所有其他过滤器和过滤器链，这种定义机制更加简洁且易于理解。

### JSP 标签库

Shiro 还提供了一个 JSP 标签库，允许您根据当前主题（Subject）的状态控制 JSP 页面的输出。一个常见的例子是在用户登录后显示 “Hello \<username\>” 文本。但如果他们是匿名的，您可能想显示其他内容，例如 “Hello! Register today!”

清单 16 显示了如何使用 Shiro 的 JSP 标记来支持这一点。

*清单 16. JSP 标记库示例：*

```xml
<%@ taglib prefix="shiro" uri="http://shiro.apache.org/tags" %>
...
<p>Hello
<shiro:user>
    <!-- shiro:principal prints out the Subject’s main
        principal - in this case, a username -->
    <shiro:principal/>!
</shiro:user>
<shiro:guest>
    <!-- not logged in - considered a guest. Show
        the register link -->
    ! <a href=”register.jsp”>Register today!</a>
</shiro:guest>
</p> 
```

还有其他标签，允许您根据他们的角色、分配的权限以及他们是否经过身份验证。

在 Web 应用中，Shiro 还支持许多其他的功能，例如“记住我”服务、REST 和 BASIC 身份验证，当然还有透明的 HttpSession 支持。

### Web 会话管理

对于 Web 应用程序，Shiro 会话默认使用的是我们都习惯的 Servlet 容器会话。也就是说，当您调用方法 subject.getSession() 和 subject.getSession(boolean) 时，Shiro 将返回 Servlet 容器的 HttpSession 实例。

# 二、10 分钟教程

## 2.1 快速入门

> 参考：https://github.com/apache/shiro/blob/main/samples/quickstart/src/main/java/Quickstart.java

```java
public class Quickstart {

    private static final transient Logger log = LoggerFactory.getLogger(Quickstart.class);

    public static void main(String[] args) {

        // 配置 Shiro SecurityManager 最简单的方法
        // 领域、用户、角色和权限使用简单的 INI 配置。
        SecurityManager securityManager = new BasicIniEnvironment("classpath:shiro.ini").getSecurityManager();

        // 创建 SecurityManager
        // 可作为 JVM 单例访问，但大多数应用程序不会这样做
        // 而是依赖其容器配置或 web.xml
        SecurityUtils.setSecurityManager(securityManager);

        // 现在一个简单的 Shiro 环境已经搭建完毕，让我们看看可以做什么

        // 获取当前用户
        Subject currentUser = SecurityUtils.getSubject();

        // 使用 Session 做一些事情（不依赖 Web 或 EJB 容器！！！）
        Session session = currentUser.getSession();
        session.setAttribute("someKey", "aValue");
        String value = (String) session.getAttribute("someKey");
        if (value.equals("aValue")) {
            log.info("Retrieved the correct value! [" + value + "]");
        }

        // 让我们登录当前用户，以便我们可以检查角色和权限
        if (!currentUser.isAuthenticated()) {
            UsernamePasswordToken token = new UsernamePasswordToken("lonestarr", "vespa");
            token.setRememberMe(true);
            try {
                currentUser.login(token);
            } catch (UnknownAccountException uae) {
                log.info("There is no user with username of " + token.getPrincipal());
            } catch (IncorrectCredentialsException ice) {
                log.info("Password for account " + token.getPrincipal() + " was incorrect!");
            } catch (LockedAccountException lae) {
                log.info("The account for username " + token.getPrincipal() + " is locked.  " +
                        "Please contact your administrator to unlock it.");
            }
            // ...在这里捕获更多异常
            catch (AuthenticationException ae) {
                //unexpected condition?  error?
            }
        }

        // 打印他们的身份主体（在本例中为用户名）
        log.info("User [" + currentUser.getPrincipal() + "] logged in successfully.");

        // 测试角色
        if (currentUser.hasRole("schwartz")) {
            log.info("May the Schwartz be with you!");
        } else {
            log.info("Hello, mere mortal.");
        }

        // 测试类型化权限（不是实例级）
        if (currentUser.isPermitted("lightsaber:wield")) {
            log.info("You may use a lightsaber ring.  Use it wisely.");
        } else {
            log.info("Sorry, lightsaber rings are for schwartz masters only.");
        }

        // 一个（非常强大的）实例级别权限
        if (currentUser.isPermitted("winnebago:drive:eagle5")) {
            log.info("You are permitted to 'drive' the winnebago with license plate (id) 'eagle5'.  " +
                    "Here are the keys - have fun!");
        } else {
            log.info("Sorry, you aren't allowed to drive the 'eagle5' winnebago!");
        }

        // 全部完成 - 注销！
        currentUser.logout();

        System.exit(0);
    }
}
```

上面的`Quickstart.java` 包含了可以让您熟悉 API 的所有代码。现在让我们把它分成几个部分，这样你就可以很容易地理解发生了什么。

在几乎所有环境中，您都可以通过以下调用获取当前用户：

```java
Subject currentUser = SecurityUtils.getSubject();
```

现在您有了一个`Subject` ，您可以用它做什么？

如果您想让用户在应用程序的当前会话期间使用某些内容，您可以获取他们的会话：

```java
Session session = currentUser.getSession();
session.setAttribute( "someKey", "aValue" );
```

`Session`是一个特定于 Shiro 的实例，它提供了您所习惯的常规 HttpSession 的大部分功能，但还有一些额外的好处和一个很大的区别：它不需要 HTTP 环境！

如果部署在 Web 应用程序内部，默认情况下`Session`将基于`HttpSession`。但是，在非 Web 环境中，Shiro 默认将自动使用其企业会话管理。

上面的`Subject`实例代表当前用户，但当前用户是谁？好吧，在登录之前他们是匿名的。所以，让我们这样做：

```java
if ( !currentUser.isAuthenticated() ) {
    //collect user principals and credentials in a gui specific manner
    //such as username/password html form, X509 certificate, OpenID, etc.
    //We'll use the username/password example here since it is the most common.
    //(do you know what movie this is from? ;)
    UsernamePasswordToken token = new UsernamePasswordToken("lonestarr", "vespa");
    //this is all you have to do to support 'remember me' (no config - built in!):
    token.setRememberMe(true);
    currentUser.login(token);
}
```

但是，如果登录失败怎么办？您可以捕获各种特定的异常，这些异常会告诉您到底发生了什么，并允许您进行相应的处理：

```java
try {
    currentUser.login( token );
    //if no exception, that's it, we're done!
} catch ( UnknownAccountException uae ) {
    //username wasn't in the system, show them an error message?
} catch ( IncorrectCredentialsException ice ) {
    //password didn't match, try again?
} catch ( LockedAccountException lae ) {
    //account for that username is locked - can't login.  Show them a message?
}
    // ... more types exceptions to check if you want ...
} catch ( AuthenticationException ae ) {
    //unexpected condition - error?
}
```

现在我们已经有一个登录用户了，我们还能做什么？

说说他们是谁：

```java
//print their identifying principal (in this case, a username):
log.info( "User [" + currentUser.getPrincipal() + "] logged in successfully." );
```

我们还可以测试一下它们是否具有特定的角色：

```java
if ( currentUser.hasRole( "schwartz" ) ) {
    log.info("May the Schwartz be with you!" );
} else {
    log.info( "Hello, mere mortal." );
}
```

我们还可以查看他们是否有权对某种类型的实体进行操作：

```java
if ( currentUser.isPermitted( "lightsaber:wield" ) ) {
    log.info("You may use a lightsaber ring.  Use it wisely.");
} else {
    log.info("Sorry, lightsaber rings are for schwartz masters only.");
}
```

此外，我们可以执行强大的实例级权限检查，能够查看用户是否有能力访问特定类型的实例：

```java
if ( currentUser.isPermitted( "winnebago:drive:eagle5" ) ) {
    log.info("You are permitted to 'drive' the 'winnebago' with license plate (id) 'eagle5'.  " +
                "Here are the keys - have fun!");
} else {
    log.info("Sorry, you aren't allowed to drive the 'eagle5' winnebago!");
}
```

最后，当用户使用完应用程序后，可以注销：

```java
currentUser.logout(); //removes all identifying information and invalidates their session too.
```

您可能会问：谁负责在登录期间获取用户数据（用户名和密码、角色和权限等），以及谁在运行时实际执行这些安全检查？好吧，您可以通过实现 Shiro 的 Realm 配置来实现。

## 2.2 认证（Authentication）



## 2.3 授权（Authorization）



















