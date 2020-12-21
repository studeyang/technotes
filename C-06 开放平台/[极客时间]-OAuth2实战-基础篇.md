# 开篇词 | 为什么要学OAuth 2.0？

触开放平台相关的技术，主要包括网关、授权两块的内容。

**怎么学习这门课？**

第一部分：必须要掌握的 OAuth2 的基础知识。会细致讲解授权码许可（Authorization Code）类型的流程，包括 OAuth2 内部组件之间的通信方式，以及授权服务、客户端（第三方软件）、受保护资源服务这三个组件的原理。

在此基础上，我还会为你讲解其他三种常见许可类型，分别是资源拥有者凭据许可 （Resource Owner Password Credentials）、隐式许可（Implicit）、客户端凭据许可 （Client Credentials）的原理，以及如何选择适合自己实际场景的授权类型。

学完基础篇的内容，你就可以把 OAuth 2.0 用到实际的工作场景了。

第二部分：侧重讲一些 OAuth2 更高级的用法，更安全、扩展性地使用 OAuth2。

包括如何在移动 App 中使用 OAuth 2.0，因使用不当而导致的 OAuth 2.0 安全漏洞有哪些，以及如何利用 OAuth 2.0 实现一个 OpenID Connect 用户身份认证协议。

[Github](http://github.com/xindongbook/oauth2-code)

OAuth 2.0 知识体系图：

![OAuth2](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201219231943.jpeg)

# 01 | OAuth 2.0是要通过什么方式解决什么问题？

**OAuth 2.0 是什么？**

用一句话总结来说，OAuth 2.0 就是一种授权协议。

假如你是一个卖家，在京东商城开了一个店铺， 日常运营中你要将订单打印出来以便给用户发货。但打印这事儿也挺繁琐的，之前你总是手工操作，后来发现有个叫“小兔”的第三方软件，它可以帮你高效率地处理这事。

小兔是怎么访问到这些订单数据的呢？其实是这样，京东商城提供了开放平台， 小兔通过京东商家开放平台的 API 就能访问到用户的订单数据。只要你在软件里点击同意，小兔就可以拿到一个访问令牌，通过访问令牌来获取到你的订单数据.

**为什么用 OAuth 2.0？**

OAuth 2.0 这种授权协议，就是保证第三方（软件）只有在获得授权之后， 才可以进一步访问授权者的数据。因此，我们常常还会听到一种说法，OAuth 2.0 是一种安全协议。

现在访问授权者的数据主要是通过 Web API，所以凡是要保护这种对外的 API 时，都需要 这样授权的方式。而 OAuth 2.0 的这种颁发访问令牌的机制，是再合适不过的方法了。同 时，这样的 Web API 还在持续增加，所以 OAuth 2.0 是目前 Web 上重要的安全手段之一 了。

**OAuth 2.0 是怎样运转的？**

![image-20201219233700427](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201219233700.png)

OAuth 2.0 授权的核心就是颁发访问令牌、使用访问令牌，而且不管是哪种类型的授权流程都是这样。

在小兔软件这个例子中呢，我们使用的就是授权码许可（Authorization Code）类型。此外，还有 3 种基础的许可类型，分别是隐式许可 （Implicit）、客户端凭据许可（Client Credentials）、资源拥有者凭据许可（Resource Owner Password Credentials）。

# 02 | 授权码许可类型中，为什么一定要有授权码？

上一讲，讲了 OAuth 2.0 的授权码许可类型。小兔打单软件的例子里面，小兔最终是通过访问令牌请求到小明的店铺里的订单数据。这个访问令牌是通过授权码换来的。

**为什么需要授权码？**

> 名词说明：
>
> 资源拥有者 -> 小明
> 第三方软件（客户端） - > 小兔软件
> 授权服务 -> 京东商家开放平台的授权服务
> 受保护资源 -> 小明店铺在京东上面的订单

OAuth 诞生之初就是为了解决 Web 浏览器场景下的授权问题，所以我基于浏览 器的场景，在上一讲的小明使用小兔软件打印订单的整体流程的基础上，画了一个授权码 许可类型的序列图。

![image-20201220121243904](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201220121243.png)

从图中看到，在第 4 步授权服务生成了授权码 code，按照一开始我们提出来的问题，如果不要授权码，这一步实际上就可以直接返回访问令牌 access_token 了。

如果没有授权码的话，我们就只能把访问令牌发送给第三方软件小兔的后端服务。因为使用重定向的方式，会把安全保密性要求极高的访问令牌暴露在浏览器上，从而将会面临访问令牌失窃的安全风险。显然，这是不能被允许的。上面的流程图就会变成下面这样：

![image-20201220123102175](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201220123102.png)

这样，问题就来了。当小明被浏览器重定向到授权服务上之后，小明跟小兔软件之间的 “连接” 就断了，相当于此时此刻小明跟授权服务建立了“连接”后，将一 直“停留在授权服务的页面上”。你会看到图 2 中问号处的时序上，小明再也没有重新“连接”到小兔软件。

为了让小明跟小兔软件重新建立起 “连接”，需要进行第二次重定向，小明授权之后，又重新重定向回到了小兔软件的地址上，这样小明就跟小兔软件有了新的 “连接”。

到这里，就能理解在授权码许可的流程中，为什么需要两次重定向了。

为了重新建立起这样的一次连接，我们又不能让访问令牌暴露出去，就有了这样一个临时的、间接的凭证：授权码。

小兔软件最终要拿到的是安全保密性要求极高的访问令牌，并不是授权码，而授权码是可以暴露在浏览器上面的。这样有了授权码的参与，访问令牌可以在后端服务之间传输，同时还可以重新建立小明与小兔软件之间的“连接”。 这样通过一个授权码，既“照顾”到了小明的体验，又“照顾”了通信的安全。

到这里，就知道了为什么要有授权码了。

那么，在执行授权码流程的时候，授权码和访问令牌在小兔软件和授权服务之间到底是怎么流转的呢？

**授权码许可类型的通信过程**

下面我们从直接通信和间接通信的维度来分析。所谓的间接通信就是指获取授权码的交互，而直接通信就是指通过授权码换取访问令牌的交互。

- 间接通信（通过授权码换取访问令牌的交互）

  ![image-20201220135304992](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201220135349.png)

  第三方软件小兔和授权服务之间，并没有发生直接的通信，而是通过浏览器这个“中间人” 来 “搭线”的。因此，我们说这是一个间接通信的方式。

- 直接通信（获取授权码的交互）

  ![image-20201220135443932](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201220135443.png)

  第三方软件小兔获取到授权码 code 值后，向授权服务发起获取访问令牌 access_token 通信请求。这个请求是第三方软件服务器跟授权服务的服务器之间的通信，都是在后端服务器之间的请求和响应，因此也叫作后端通信。

**两个 “一伙”**

OAuth 2.0 中的 4 个角色是 “两两 站队” 的：资源拥有者和第三方软件“站在一起”，因为第三方软件要代表资源拥有者去访问受保护资源；授权服务和受保护资源“站在一起”，因为授权服务负责颁发访问令牌，受保护资源负责接收并验证访问令牌。

![image-20201220221358951](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201220221358.png)

介绍授权码流程的时候我都是以浏览器参与的场景来讲的，那么浏览器一定要参与到这个流程中吗？

**一定要有浏览器吗？**

OAuth 2.0 发展之初，开放生态环境相对单薄，以浏览器为代理的 Web 应用居多，授权码许可类型 “理所当然” 地被应用到了通过浏览器才能访问的 Web 应用中。 

但实际上，OAuth 2.0 是一个授权理念，或者说是一种授权思维。它的授权码模式的思维 可以移植到很多场景中，比如微信小程序。在开发微信小程序应用时，我们通过授权码模 式获取用户登录信息，[官方文档的地址示例](https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/login/auth.code2Session.html)中给出的 grant_type=authorization_code ，就没有用到浏览器。

根据微信官方文档描述，开发者获取用户登录态信息的过程正是一个授权码的许可流程：

```
首先，开发者通过 wx.login(Object object) 方法获取到登录凭证 code 值，这一步的流程是在小程序内部通过调用微信提供的 SDK 实现；
然后，再通过该 code 值换取用户的 session_key 等信息，也就是官方文档的 auth.code2Session 方法，同时该方法也是被强烈建议通过开发者的后端服务来调用的。
```

你可以看到，这个过程并没有使用到浏览器，但确实按照授权码许可的思想走了一个完整 的授权码许可流程。也就是说，先通过小程序前端获取到 code 值，再通过小程序的后端服务使用 code 值换取 session_key 等信息，只不过是访问令牌 access_token 的值被换成了 session_key。

```

GET https://api.weixin.qq.com/sns/jscode2session?appid=APPID&secret=SECRET&js_code=JSCODE&grant_type=authorization_code
```

这整个过程体现的就是授权码许可流程的思想。

# 03 | 授权服务：授权码和访问令牌的颁发流程是怎样的？

在介绍授权码许可类型时，我提到了很多次 “授权服务”。一句话概括，授权服务就是负责颁发访问令牌的服务。更进一步地讲，OAuth 2.0 的核心是授权服务，而授权服务的核心就是令牌。

那么，授权服务到底是怎么生成访问令牌的，这其中包含了哪些操作呢？访问令牌过期了而用户又不在场的情况下，又如何重新生成访问令牌呢？

**授权服务的工作过程**

开始之前，先回想下小明给小兔软件授权订单数据的整个流程。

授权之前，小兔要去平台那里“备案”，也就是注册。注册完后，京东商家开放平台就会给小兔软件 app_id 和 app_secret 等信息，以方便后面授权时的各种身份校验。

同时，注册的时候，第三方软件也会请求受保护资源的可访问范围。比如，小兔能否获取小明店铺 3 个月以前的订单，能否获取每条订单的所有字段信息等等。这个权限范围就是 scope。相应代码如下：

```java
//模拟第三方软件注册之后的数据库存储
Map<String, String> appMap = new HashMap<>();

appMap.put("app_id","APPID_RABBIT");
appMap.put("app_secret","APPSECRET_RABBIT");
appMap.put("redirect_uri","http://localhost:8080/AppServlet-ch03");
appMap.put("scope", "nickname address pic");
```

备完案之后，小明过来让平台把他的订单数据给小兔，平台对了下暗号，发现小兔是合法的，于是就要推进下一步了。

上节课讲过，在授权码许可类型中，授权服务的工作，可以划分为两大部分，一个是颁发授权码 code，一个是颁发访问令牌 access_token。为了更能表达授权码和访问令牌 的存在，我在图中用深色将其标注了出来：

![image-20201221113635203](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/image-20201221113635203.png)

我们先看看颁发授权码 code 的流程。

**授权服务的工作过程一：颁发授权码 code**

在这个过程中，授权服务需要完成两部分工作，分别是准备工作和生成授权码 code。

小明在给第三方软件小兔打单软件进行授权的时候，会看到授权页面上有一个授权按钮，但是授权服务在小明看到这个授权按钮之前，实际上已经做了一系列动作。这些动作，就是所谓的准备工作，包括验证基本信息、验证权限范围（第一次）和生成授权请求页面这三步。我们具体分析下。

准备工作第一步，验证基本信息

验证基本信息，包括对第三方软件小兔合法性和回调地址合法性的校验。

```java
if(!appMap.get("redirect_uri").equals(redirectUri)) {
    // 回调地址不存在
}
```

请求参数有：

```
response_type：表示授权类型，必选项，此处的值固定为"code"
app_id：表示客户端的ID，必选项
redirect_uri：表示重定向URI，可选项
scope：表示申请的权限范围，可选项
state：表示客户端的当前状态，可以指定任意值，认证服务器会原封不动地返回这个值。
```

准备工作第二步，验证权限范围（第一次）

我们需要对小兔传过来的 scope 参数，与小兔注册时申请的权限范围做比对。如果请求过来的权限范围大于注册时的范围，就需要作出越权提示。此刻是第一次权限校验。

```java
String scope = request.getParameter("scope");
if(!checkScope(scope)) {
    // 超出注册的权限范围
}
```

准备工作第三步，生成授权请求页面

这个授权请求页面就是授权服务上的页面，如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/image-20201221152357738.png" alt="image-20201221152357738" style="zoom: 67%;" />

至此，颁发授权码 code 的准备工作就完成了。这只是准备工 作，因为当用户点击授权按钮“approve”后，才会生成授权码 code 值和访问令牌 acces_token 值，一切才真正开始。

小明点击“approve”按钮之后，生成授权码 code 的流程就正式开始了，主要包括验证权限范围（第二次）、处理授权请求生成授权码 code 和重定向至第三方软件这三大步。 接下来，我们一起分析下这三步。

生成授权码第一步，验证权限范围（第二次）

这里为什么又要校验一次呢？因为凡是输入性数据都会涉及到合法性检查。另外，这也是要求我们养成一种在服务端对输入数据的请求，都尽可能做一次合法性校验的好习惯。

```java
String[] rscope = request.getParameterValues("rscope");
if(!checkScope(rscope)) {
    // 超出注册的权限范围
}
```

生成授权码第二步，处理授权请求生成授权码

当小明同意授权之后，授权服务会校验响应类型 response_type 的值。response_type 有 code 和 token 两种类型的值。

```java
String responseType = request.getParameter("response_type");
if("code".equals(responseType)) {
    // 生成授权码
}
```

在授权服务中，需要将生成的授权码 code 值与 app_id、user 进行关系映射。

```java
// 模拟登录用户为USERTEST
String code = generateCode(appId, "USERTEST");
private String generateCode(String appId, String user) {
    //...
    String code = strb.toString();
    codeMap.put(code, appId + "|" + user + "|" + System.currentTimeMillis());
    return code;
}
```

同时，授权服务还需要将生成的授权码 code 跟已经授权的权限范围 rscope 进行绑定并存储，以便后续们能够通过 code 值取出授权范围并与访问令牌绑定。

```java
Map<String, String[]> codeScopeMap = new HashMap<>();
// 授权范围与授权码做绑定
codeScopeMap.put(code, rscope);
```

生成授权码第三步，重定向至第三方软件

生成授权码 code 值之后，授权服务需要将该 code 值告知第三方软件小兔。开始时我们提到，颁发授权码 code 是通过前端通信完成的，因此这里采用重定向的方式。

```java
Map<String, String> params = new HashMap<String, String>();
params.put("code", code);
//构造第三方软件的回调地址，并重定向到该地址
String toAppUrl = URLParamsUtil.appendParams(redirectUri, params);
//授权码流程的“第二次”重定向
response.sendRedirect(toAppUrl);
```

响应参数有：

```
code：表示授权码，必选项。该码的有效期应该很短，通常设为10分钟，客户端只能使用该码一次，否则会被授权服务器拒绝。该码与客户端ID和重定向URI，是一一对应关系。
state：如果客户端的请求中包含这个参数，认证服务器的回应也必须一模一样包含这个参数。
```

到此，颁发授权码 code 的流程全部完成。当小兔获取到授权码 code 值以后，就可以开始请求访问令牌 access_token 的值了。

**授权服务的工作过程二：颁发访问令牌 access_token**

当小兔拿着授权码 code 来请求的时候，授权服务需要为之生成最终的请求访问令牌。这个过程主要包括验证第三方软件小兔是否存在、验证 code 值是否合法和生成 access_token 值这三大步。接下来，我们一起分析下每一步。

第一步，验证第三方软件是否存在

此时，接收到的 grant_type 的类型为 authorization_code。

```java
String grantType = request.getParameter("grant_type");
if("authorization_code".equals(grantType)) {
    //
}
```

由于颁发访问令牌是通过后端通信完成的，所以这里除了要校验 app_id 外，还要校验 app_secret。

```java
if(!appMap.get("app_id").equals(appId)) {
    // app_id不存在
}
if(!appMap.get("app_secret").equals(appSecret)) {
    // app_secret不合法
}
```

请求参数有：

```
grant_type：表示使用的授权模式，必选项，此处的值固定为"authorization_code"。
code：表示上一步获得的授权码，必选项。
redirect_uri：表示重定向URI，必选项，且必须与A步骤中的该参数值保持一致。
app_id：表示客户端ID，必选项。
app_secret：表示客户端密码，必选项。
```

第二步，验证授权码 code 值是否合法

授权服务在颁发授权码 code 的阶段已经将 code 值存储了起来，此时对比从 request 中接收到的 code 值和从存储中取出来的 code 值。

```java
String code = request.getParameter("code");
// 验证code值
if(!isExistCode(code)) {
    // code不存在
    return;
}
// 授权码一旦被使用，须立即作废
codeMap.remove(code);
```

确认过授权码 code 值有效以后，应该立刻从存储中删除当前的 code 值，以防止第三方软件恶意使用一个失窃的授权码 code 值来请求授权服务。

第三步，生成访问令牌 access_token 值

关于按照什么规则来生成访问令牌 access_token 的值，OAuth 2.0 规范中并没有明确规定，但必须符合三个原则：唯一性、不连续性、不可猜性。

```java
Map<String, String[]> tokenScopeMap = new HashMap<>();
// 生成访问令牌access_token
String accessToken = generateAccessToken(appId, "USERTEST");
// 授权范围与访问令牌绑定
tokenScopeMap.put(accessToken, codeScopeMap.get(code));

/** 生成访问令牌的方法 */
private String generateAccessToken(Stirng appId, String user) {
    String accessToken = UUID.randomUUID().toString();
    // 1天时间过期
    String expires_in = "1";
    tokenMap.put(accessToken, appId + "|" + System.currentTimeMillis() + "|" + expires_in);
    return accessToken;
}
```

正因为 OAuth 2.0 规范没有约束访问令牌内容的生成规则，所以我们有更高的自由度。我们既可以像 Demo 中那样生成一个 UUID 形式的数据存储起来，让授权服务和受保护资源共享该数据；也可以将一些必要的信息通过结构化的处理放入令牌本身。我们将包含了一 些信息的令牌，称为结构化令牌，简称 JWT。

至此，授权码许可类型下授权服务的两大主要过程，也就是颁发授权码和颁发访问令牌的流程，就讲完了。

到这里，你应该还会注意到一个问题，在生成访问令牌的时候，我们还给它附加了一个过期时间 expires_in，这意味着访问令牌会在一定的时间后失效。访问令牌失效，就意味着资源拥有者给第三方软件的授权失效了，第三方软件无法继续访问资源拥有者的受保护资源了。

**刷新令牌**

刷新令牌也是给第三方软件使用的，同样需要遵循先颁发再使用的原则。因此，我们还是 从颁发和使用两个环节来学习刷新令牌。不过，这个颁发和使用流程和访问令牌有些是相 同的，所以我只会和你重点讲述其中的区别。

**颁发刷新令牌**

其实，颁发刷新令牌和颁发访问令牌是一起实现的，都是在过程二的步骤三生成访问令牌 access_token 中生成的。也就是说，第三方软件得到一个访问令牌的同时，也会得到一个刷新令牌：

```java
Map<String, String> refreshTokenMap = new HashMap<>();
// 生成刷新令牌refresh_token
String refreshToken = generateRefreshToken(appId, "USERTEST");

private String generateRefreshToken(String appId, String user) {
    String refreshToken = UUID.randomUUID().toString();
    refreshTokenMap.put(refreshToken, appId + "|" + user + "|" + System.currentTimeMillis());
    return refreshToken;
}
```

看到这里你可能要问了，为什么要一起生成访问令牌和刷新令牌呢？ 

其实，这就回到了刷新令牌的作用上了。刷新令牌存在的初衷是，在访问令牌失效的情况下，为了不让用户频繁手动授权，用来通过系统重新请求生成一个新的访问令牌。那么， 如果访问令牌失效了，而“身边”又没有一个刷新令牌可用，岂不是又要麻烦用户进行手动授权了。所以，它必须得和访问令牌一起生成。 

到这里，我们就解决了刷新令牌的颁发问题。

**使用刷新令牌**

说到刷新令牌的使用，我们需要先明白一点。在 OAuth 2.0 规范中，刷新令牌是一种特殊的授权许可类型，是嵌入在授权码许可类型下的一种特殊许可类型。在授权服务的代码里，当我们接收到这种授权许可请求的时候，会先比较 grant_type 和 refresh_token 的值，然后做下一步处理。

这其中的流程主要包括如下两大步骤。

第一步，接收刷新令牌请求，验证基本信息。

此时请求中的 grant_type 值为 refresh_token。

```java
String grantType = request.getParameter("grant_type");
if("refresh_token".equals(grantType)) {
    //
}
```

和颁发访问令牌前的验证流程一样，这里我们也需要验证第三方软件是否存在。需要注意的是，这里需要同时验证刷新令牌是否存在，目的就是要保证传过来的刷新令牌的合法性。

```java
String refresh_token = request.getParameter("refresh_token");
if(!refreshTokenMap.containsKey(refresh_token)) {
    // 该refresh_token值不存在
}
```

另外，我们还需要验证刷新令牌是否属于该第三方软件。授权服务是将颁发的刷新令牌与第三方软件、当时的授权用户绑定在一起的，因此这里需要判断该刷新令牌的归属合法性。

```java
String appStr = refreshTokenMap.get("refresh_token");
if(!appStr.startsWith(appId + "|" + "USERTEST")) {
    // 该refresh_token值不是颁发给该第三方软件的
}
```

需要注意，一个刷新令牌被使用以后，授权服务需要将其废弃，并重新颁发一个刷新令牌。

第二步，重新生成访问令牌。

生成访问令牌的处理流程，与颁发访问令牌环节的生成流程是一致的。授权服务会将新的访问令牌和新的刷新令牌，一起返回给第三方软件。

# 04 | 在OAuth 2.0中，如何使用JWT结构化令牌？

结构化令牌这方面，目前用得最多的就是 JWT 令牌了。接下来，我就要和你详细讲讲，JWT 是什么、原理是怎样的、优势是什么，以及怎么使用，同时我还会讲到令牌生命周期的问题。

**JWT 结构化令牌**

关于什么是 JWT，官方定义是这样描述的：

```
JSON Web Token（JWT）是一个开放标准（RFC 7519），它定义了一种紧凑的、自包含的方式，用于作为 JSON 对象在各方之间安全地传输信息。
```

JWT 就是用一种结构化封装的方式来生成 token 的技术。结构化后的 token 可以被赋予非常丰富的含义，这也是它与原先毫无意义的、随机的字符串形式 token 的最大区别。

JWT 这种结构化体可以分为 HEADER（头部）、PAYLOAD（数据体）和 SIGNATURE（签名）三部分。经过签名之后的 JWT 的整体结构，是被句点符号分割的三段内容，结构为 header.payload.signature 。比如下面这个示例：

```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJVU0VSVEVTVCIsImV4cCI6MTU4NDEwNTc5MDcwMywiaWF0IjoxNTg0MTA1OTQ4MzcyfQ.1HbleXbvJ_2SW8ry30cXOBGR9FW4oSWBd3PWaWKsEXE
```

把它拷贝到 https://jwt.io/ 网站中，就可以看到解码之后的数据：

![image-20201221230920531](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201221230920.png)

HEADER 表示装载令牌类型和算法等信息，是 JWT 的头部。其中，typ 表示第二部分 PAYLOAD 是 JWT 类型，alg 表示使用 HS256 对称签名的算法。

PAYLOAD 表示是 JWT 的数据体，代表了一组数据。其中，sub（令牌的主体，一般设为资源拥有者的唯一标识）、exp（令牌的过期时间戳）、iat（令牌颁发的时间戳）是 JWT 规范性的声明，代表的是常规性操作。更多的通用声明，你可以参考 RFC 7519 开放标准。不过，在一个 JWT 内可以包含一切合法的 JSON 格式的数据，也就是说，PAYLOAD 表示的一组数据允许我们自定义声明。

SIGNATURE 表示对 JWT 信息的签名。那么，它有什么作用呢？我们可能认为，有了 HEADER 和 PAYLOAD 两部分内容后，就可以让令牌携带信息了，似乎就可以在网络中传输了，但是在网络中传输这样的信息体是不安全的，因为你在“裸奔”啊。所以，我们还需要对其进行加密签名处理，而 SIGNATURE 就是对信息的签名结果，当受保护资源接收到第三方软件的签名后需要验证令牌的签名是否合法。

JWT 令牌是如何被使用的呢？在讲如何使用之前呢，我先和你说说“令牌内检”。

**令牌内检**

什么是令牌内检呢？授权服务颁发令牌，受保护资源服务就要验证令牌。同时呢，授权服务和受保护资源服务，它俩是“一伙的”。受保护资源来调用授权服务提供的检验令牌的服务，我们把这种校验令牌的方式称为令牌内检。

有时候授权服务依赖一个数据库，然后受保护资源服务也依赖这个数据库，也就是我们说的“共享数据库”。不过，在如今已经成熟的分布式以及微服务的环境下，不同的系统之间是依靠服务而不是数据库来通信了，比如授权服务给受保护资源服务提供一个 RPC 服 务。如下图所示。

![image-20201221231740063](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201221231740.png)

那么，在有了 JWT 令牌之后，我们就多了一种选择，因为 JWT 令牌本身就包含了之前所要依赖数据库或者依赖 RPC 服务才能拿到的信息，比如我上面提到的哪个用户为哪个软件进行了授权等信息。

接下来就让我们看看有了 JWT 令牌之后，整体的内检流程会变成什么样子。

**JWT 是如何被使用的？**

有了 JWT 令牌之后的通信方式，就如下面的图 3 所展示的那样了，授权服务“扔出”一个 令牌，受保护资源服务“接住”这个令牌，然后自己开始解析令牌本身所包含的信息就可以了，而不需要再去查询数据库或者请求 RPC 服务。这样也实现了我们上面说的令牌内检。

![image-20201221231951795](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201221231951.png)

在上面这幅图中呢，为了更能突出 JWT 令牌的位置，我简化了逻辑关系。实际上，授权服务颁发了 JWT 令牌后给到了小兔软件，小兔软件拿着 JWT 令牌来请求受保护资源服务， 也就是小明在京东店铺的订单。很显然，JWT 令牌需要在公网上做传输。所以在传输过程中，JWT 令牌需要进行 Base64 编码以防止乱码，同时还需要进行签名及加密处理来防止数据信息泄露。

如果是我们自己处理这些编码、加密等工作的话，就会增加额外的编码负担。好在，我们可以借助一些开源的工具来帮助我们处理这些工作。比如，我在下面的 Demo 中，给出了开源 JJWT（Java JWT）的使用方法。

JJWT 是目前 Java 开源的、比较方便的 JWT 工具，封装了 Base64URL 编码和对称 HMAC、非对称 RSA 的一系列签名算法。使用 JJWT，我们只关注上层的业务逻辑实现， 而无需关注编解码和签名算法的具体实现，这类开源工具可以做到“开箱即用”。

这个 Demo 的代码如下，使用 JJWT 可以很方便地生成一个经过签名的 JWT 令牌，以及 解析一个 JWT 令牌。

```java
// 密钥
String sharedTokenSecret = "hellooauthhellooauthhellooauthhellooauth";
Key key = new SecretKeySpec(sharedTokenSecret.getBytes(),
SignatureAlgorithm.HS256.getJcaName());
//生成JWT令牌
String jwts=
Jwts.builder().setHeaderParams(headerMap).setClaims(payloadMap).signWith(key, SignatureAlgorithm.HS256).compact();
//解析JWT令牌
Jws<Claims> claimsJws = Jwts.parserBuilder().setSigningKey(key).build().parseClaimsJws(jwts);
JwsHeader header = claimsJws.getHeader();
Claims body = claimsJws.getBody();
```

使用 JJWT 解析 JWT 令牌时包含了验证签名的动作，如果签名不正确就会抛出异常信息。 我们可以借助这一点来对签名做校验，从而判断是否是一个没有被伪造过的、合法的 JWT 令牌。

异常信息，一般是如下的样子：

```
JWT signature does not match locally computed signature. JWT validity cannot be asserted 
```

以上就是借助开源工具，将 JWT 令牌应用到授权服务流程中的方法了。到这里，你是不是一直都有一个疑问：为什么要绕这么大一个弯子，使用 JWT，而不是使用没有啥内部结构，也不包含任何信息的随机字符串呢？JWT 到底有什么好处？

**为什么要使用 JWT 令牌？**

使用 JWT 格式令牌的三大好处如下。

第一，JWT 的核心思想，就是用计算代替存储，有些 “时间换空间” 的 “味道”。当然，这种经过计算并结构化封装的方式，也减少了“共享数据库” 因远程调用而带来的网络传输消耗，所以也有可能是节省时间的。

第二，也是一个重要特性，是加密。因为 JWT 令牌内部已经包含了重要的信息，所以在整个传输过程中都必须被要求是密文传输的，这样被强制要求了加密也就保障了传输过程中的安全性。这里的加密算法，既可以是对称加密，也可以是非对称加密。

第三，使用 JWT 格式的令牌，有助于增强系统的可用性和可伸缩性。我们前面讲到了，这种 JWT 格式的令牌，通过“自编码”的方式包含了身份验证需要的信息，不再需要服务端进行额外的存储，所以每次的请求都是无状态会话。这就符合了我们尽可能遵循无状态架构设计的原则，也就是增强了系统的可用性和伸缩性。

JWT 令牌也有缺点。

JWT 格式令牌的最大问题在于 “覆水难收”，也就是说，没办法在使用过程中修改令牌状态。我们还是借助小明使用小兔软件例子，先停下来想一下。

小明在使用小兔软件的时候，是不是有可能因为某种原因修改了在京东的密码，或者是不是有可能突然取消了给小兔的授权？这时候，令牌的状态是不是就要有相应的变更，将原来对应的令牌置为无效。

但，使用 JWT 格式令牌时，每次颁发的令牌都不会在服务端存储，这样我们要改变令牌状态的时候，就无能为力了。因为服务端并没有存储这个 JWT 格式的令牌。这就意味着，JWT 令牌在有效期内，是可以“横行无止”的。

为了解决这个问题，我们可以把 JWT 令牌存储到远程的分布式内存数据库中吗？显然不能，因为这会违背 JWT 的初衷（将信息通过结构化的方式存入令牌本身）。因此，我们通常会有两种做法：

```
一是，将每次生成 JWT 令牌时的秘钥粒度缩小到用户级别，也就是一个用户一个秘钥。 这样，当用户取消授权或者修改密码后，就可以让这个密钥一起修改。一般情况下，这种方案需要配套一个单独的密钥管理服务。
```

```
二是，在不提供用户主动取消授权的环境里面，如果只考虑到修改密码的情况，那么我们就可以把用户密码作为 JWT 的密钥。当然，这也是用户粒度级别的。这样一来，用户修改密码也就相当于修改了密钥。
```

**令牌的生命周期**

我刚才讲了 JWT 令牌有效期的问题，讲到了它的失效处理，另外咱们在第 3 讲中提到， 授权服务颁发访问令牌的时候，都会设置一个过期时间，其实这都属于令牌的生命周期的管理问题。接下来，我便向你讲一讲令牌的生命周期。

JWT 令牌可以把有效期的信息存储在本身的结构体中。具体到 OAuth 2.0 的令牌生命周期，通常会有三种情况。

第一种情况是令牌的自然过期过程，这也是最常见的情况。这个过程是，从授权服务创建一个令牌开始，到第三方软件使用令牌，再到受保护资源服务验证令牌，最后再到令牌失效。同时，这个过程也不排除主动销毁令牌的事情发生，比如令牌被泄露，授权服务可以做主让令牌失效。

生命周期的第二种情况，也就是上一讲提到的，访问令牌失效之后可以使用刷新令牌请求新的访问令牌来代替失效的访问令牌，以提升用户使用第三方软件的体验。

生命周期的第三种情况，就是让第三方软件比如小兔，主动发起令牌失效的请求，然后授权服务收到请求之后让令牌立即失效。我们来想一下，什么情况下会需要这种机制。

比如有些时候，用户和第三方软件之间存在一种订购关系，比如小明购买了小兔软件，那么在订购时长到期或者退订，且小明授权的 token 还没有到期的情况下，就需要有这样的一种令牌撤回协议，来支持小兔软件主动发起令牌失效的请求。作为平台一方比如京东商家开放平台，也建议有责任的第三方软件比如小兔软件，遵守这样的一种令牌撤回协议。

我将以上三种情况整理成了一份序列图，以便帮助你理解。同时，为了突出令牌，我将访问令牌和刷新令牌，特意用深颜色标识出来，并单独作为两个角色放进了整个序列图中。

![image-20201221234105261](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201221234105.png)

