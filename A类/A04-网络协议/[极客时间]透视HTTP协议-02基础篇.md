# 08 | 键入网址再按下回车，后面究竟发生了什么？

**使用 IP 地址访问 Web 服务器**

下图是一次在 Chrome 浏览器的地址栏里输入“http://127.0.0.1/”，再按下回车键，等欢迎页面显示出来后 Wireshark 里捕获的数据包。

![image-20201101223615503](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201101223615.png)

**抓包分析**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201101224832.png" alt="image-20201101224832375" style="zoom:50%;" />

1. 浏览器要用 HTTP 协议收发数据，首先要做的就是建立 TCP 连接。使用“三次握手”建立与 Web 服务器的连接。（No 1-3）

   <img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201101224900.png" alt="image-20201101224900308" style="zoom:50%;" />

2. 浏览器按照 HTTP 协议规定的格式，通过 TCP 发送了一个“GET / HTTP/1.1”请求报文（No 7）

3. 随后，Web 服务器回复了第五个包，在 TCP 协议层面确认：“刚才的报文我已经收到了”，不过这个 TCP 包 HTTP 协议是看不见的。（No 8）

4. Web 服务器收到报文后在内部就要处理这个请求。同样也是依据 HTTP 协议的规定，解析报文，看看浏览器发送这个请求想要干什么。再拼成符合 HTTP 格式的报文，发回去。（No 9）

5. 浏览器也要给服务器回复一个 TCP 的 ACK 确认，“你的响应报文收到了，多谢。”（No 10）

   <img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201101225051.png" style="zoom:50%;" />

6. 这时浏览器就收到了响应数据，但里面是什么呢？所以也要解析报文。一看，服务器给我的是个 HTML 文件，好，那我就调用排版引擎、JavaScript 引擎等等处理一下，然后在浏览器窗口里展现出了欢迎页面。

   > 这之后还有两个来回，共四个包，重复了相同的步骤。这是浏览器自动请求了作为网站图标的“favicon.ico”文件，与我们输入的网址无关。但因为我们的实验环境没有这个文件，所以服务器在硬盘上找不到，返回了一个“404 Not Found”。
   >
   > <img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201101225125.png" alt="image-20201101225125358" style="zoom:50%;" />

至此，“键入网址再按下回车”的全过程就结束了。TCP 执行四次挥手。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201101225158.png" alt="image-20201101225157975" style="zoom:50%;" />

**使用域名访问 Web 服务器**

现在我们把地址栏的输入改成：http://www.chrono.com，重复 Wireshark 抓包过程。

浏览器首先看一下自己的缓存里有没有，如果没有就向操作系统的缓存要，还没有就检查本机域名解析文件 hosts。

**真实的网络世界**

假设你要访问的是 Apple 网站，在浏览器里只能使用域名“www.apple.com”访问，那么接下来要做的必然是域名解析。这就要用 DNS 协议开始从操作系统、本地 DNS、根 DNS、顶级 DNS、权威 DNS 的层层解析，当然这中间有缓存。

> 别忘了互联网上还有另外一个重要的角色 CDN，它也会在 DNS 的解析过程中“插上一脚”。DNS 解析可能会给出 CDN 服务器的 IP 地址，这样你拿到的就会是 CDN 服务器而不是目标网站的实际地址。
>
> 因为 CDN 会缓存网站的大部分资源，比如图片、CSS 样式表，所以有的 HTTP 请求就不需要再发到 Apple，CDN 就可以直接响应你的请求，把数据发给你。

经过无数的路由器、网关、代理，最后到达目的地。

目标网站的服务器对外表现的是一个 IP 地址，通常在入口是负载均衡设备，如果缓存服务器里没有数据，那么负载均衡设备就要把请求转发给应用服务器了。

应用服务器的输出到了负载均衡设备这里，请求的处理就算是完成了，就要按照原路再走回去，还是要经过许多的路由器、网关、代理。如果这个资源允许缓存，那么经过 CDN 的时候它也会做缓存，这样下次同样的请求就不会到达源站了。

# 09 | HTTP报文是什么样子的？

HTTP 协议的核心部分就是它传输的报文内容。

**报文结构**

> TCP 报文在实际要传输的数据之前附加了一个 20 字节的头部数据，存储 TCP 协议必须的额外信息，例如发送方的端口号、接收方的端口号、包序号、标志位等。
>
> <img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201102222121.png" alt="image-20201102222121278" style="zoom:50%;" />

HTTP 协议的请求报文和响应报文的结构基本相同，由三大部分组成：

1. 起始行（start line）：描述请求或响应的基本信息；
2. 头部字段集合（header）：使用 key-value 形式更详细地说明报文；
3. 消息正文（entity）：实际传输的数据，它不一定是纯文本，可以是图片、视频等二进制数据。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201102222451.png" alt="image-20201102222451597" style="zoom:50%;" />

报文的最后是一个空白行结束，没有 body。

**请求行**

请求行（request line）是 HTTP 的起始行，它简要地描述了客户端想要如何操作服务器端的资源。

请求行由三部分构成：

1. 请求方法：是一个动词，如 GET/POST，表示对资源的操作；
2. 请求目标：通常是一个 URI，标记了请求方法要操作的资源；
3. 版本号：表示报文使用的 HTTP 协议版本。

这三个部分通常使用空格（space）来分隔，最后要用 CRLF 换行表示结束。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201102222849.png" alt="image-20201102222849101" style="zoom:50%;" />

例如：

```http
GET / HTTP/1.1
```

**状态行**

状态行（status line）是响应报文里的起始行，意思是服务器响应的状态。

状态行同样也是由三部分构成：

1. 版本号：表示报文使用的 HTTP 协议版本；
2. 状态码：一个三位数，用代码的形式表示处理的结果，比如 200 是成功，500 是服务器错误；
3. 原因：作为数字状态码补充，是更详细的解释文字，帮助人理解原因。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201102223141.png" alt="image-20201102223141078" style="zoom:50%;" />

例如：

```http
HTTP/1.1 200 OK
```

```http
HTTP/1.1 404 Not Found
```

**头部字段**

头部字段是 key-value 的形式，key 和 value 之间用“:”分隔，最后用 CRLF 换行表示字段结束。

使用头字段需要注意下面几点：

1. 字段名不区分大小写，例如“Host”也可以写成“host”，但首字母大写的可读性更好；
2. 字段名里不允许出现空格，可以使用连字符“-”，但不能使用下划线“_”。例如，“test-name”是合法的字段名，而“test name”“test_name”是不正确的字段名；
3. 字段名后面必须紧接着“:”，不能有空格，而“:”后的字段值前可以有多个空格；
4. 字段的顺序是没有意义的，可以任意排列不影响语义；
5. 字段原则上不能重复，除非这个字段本身的语义允许，例如 Set-Cookie。

**常用头字段**

HTTP 协议的头部字段，基本上可以分为四大类：

1. 通用字段：在请求头和响应头里都可以出现；
2. 请求字段：仅能出现在请求头里，进一步说明请求信息或者额外的附加条件；
3. 响应字段：仅能出现在响应头里，补充说明响应报文的信息；
4. 实体字段：它实际上属于通用字段，但专门描述 body 的额外信息。

- Host

  HTTP/1.1 规范里要求必须出现的字段，并且只能出现在请求头里。Host 字段告诉服务器这个请求应该由哪个主机来处理。

  例如：

  ```http
  GET / HTTP/1.1
  HOST: 127.0.0.1
  ...
  ```

- User-Agent

  User-Agent 是请求字段，只出现在请求头里。它使用一个字符串来描述发起 HTTP 请求的客户端，服务器可以依据它来返回最合适此浏览器显示的页面。

- Date

  Date字段是一个通用字段，但通常出现在响应头里，表示 HTTP 报文创建的时间，客户端可以使用这个时间再搭配其他字段决定缓存策略。

- Server

  Server 字段也不是必须要出现的。有的网站响应头里要么没有这个字段，要么就给出一个完全无关的描述信息。

  例如：

  <img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201102224351.png" alt="image-20201102224351640" style="zoom:50%;" />

  它的 Server 字段里就看不出是使用了 Apache 还是 Nginx，只是显示为“GitHub.com”。

- Content-Length

  它表示报文里 body 的长度，也就是请求头或响应头空行后面数据的长度。

**课下作业**

1. 如果拼 HTTP 报文的时候，在头字段后多加了一个 CRLF，导致出现了一个空行，会发生什么？
2. 讲头字段时说“:”后的空格可以有多个，那为什么绝大多数情况下都只使用一个空格呢？

# 10 | HTTP请求方法

**标准请求方法**

HTTP 协议里为什么要有“请求方法”这个东西呢？

蒂姆·伯纳斯 - 李最初设想的是要用 HTTP 协议构建一个超链接文档系统，这就需要有某种“动作的指示”，告诉操作这些资源的方式。所以，就这么出现了“请求方法”。

目前 HTTP/1.1 规定了八种方法：

1. GET：获取资源，可以理解为读取或者下载数据；
2. HEAD：获取资源的元信息；
3. POST：向资源提交数据，相当于写入或上传数据；
4. PUT：类似 POST；
5. DELETE：删除资源；
6. CONNECT：建立特殊的连接隧道；
7. OPTIONS：列出可对资源实行的方法；
8. TRACE：追踪请求 - 响应的传输路径。

> 前 4 种是常用方法，后 4 种不常用。另外还有一些扩展方法：MKCOL、COPY、MOVE、LOCK、UNLOCK、PATCH。

**GET/HEAD/POST/PUT**

GET 方法是用的最多的，自 0.9 版出现并一直被保留至今，是名副其实的“元老”。它的含义是请求从服务器获取资源。

> GET 方法搭配 URI 和其他头字段就能实现对资源更精细的操作。
>
> 例如，在 URI 后使用“#”，就可以在获取页面后直接定位到某个标签所在的位置；使用 If-Modified-Since 字段就变成了“有条件的请求”，仅当资源被修改时才会执行获取动作；使用 Range 字段就是“范围请求”，只获取资源的一部分数据。

HEAD 方法与 GET 方法类似，可以看做是 GET 方法的一个“简化版”或者“轻量版”。可以用在很多并不真正需要资源的场合，避免传输 body 数据的浪费。

> 比如，想要检查一个文件是否存在，只要发个 HEAD 请求就可以了，没有必要用 GET 把整个文件都取下来。再比如，要检查文件是否有最新版本，同样也应该用 HEAD，服务器会在响应头里把文件的修改时间传回来。

POST 向 URI 指定的资源提交数据，数据就放在报文的 body 里。

> 比如，你上论坛灌水，敲了一堆字后点击“发帖”按钮，浏览器就执行了一次 POST 请求，把你的文字放进报文的 body 里，然后拼好 POST 请求头，通过 TCP 协议发给服务器。

PUT 的作用与 POST 类似，也可以向服务器提交数据，但与 POST 存在微妙的不同，通常 POST 表示的是“新建”“create”的含义，而 PUT 则是“修改”“update”的含义。

> 在实际应用中，PUT 用到的比较少。而且，因为它与 POST 的语义、功能太过近似，有的服务器甚至就直接禁止使用 PUT 方法，只用 POST 方法上传数据。

> 安全性：GET 和 HEAD 方法是“安全”的。POST/PUT/DELETE 是“不安全”的。
>
> 幂等：GET 和 HEAD 是幂等的，DELETE 和 PUT 也是幂等的。POST 不是幂等的。

**非常用方法**

DELETE 方法指示服务器删除资源，因为这个动作危险性太大，所以通常服务器不会执行真正的删除操作，而是对资源做一个删除标记。当然，更多的时候服务器就直接不处理 DELETE 请求。

CONNECT 是一个比较特殊的方法，要求服务器为客户端和另一台远程服务器建立一条特殊的连接隧道，这时 Web 服务器在中间充当了代理的角色。

OPTIONS 方法要求服务器列出可对资源实行的操作方法，在响应头的 Allow 字段里返回。它的功能很有限，用处也不大，有的服务器（例如 Nginx）干脆就没有实现对它的支持。

TRACE 方法多用于对 HTTP 链路的测试或诊断，可以显示出请求 - 响应的传输路径。它的本意是好的，但存在漏洞，会泄漏网站的信息，所以 Web 服务器通常也是禁止使用。

**扩展方法**

虽然 HTTP/1.1 里规定了八种请求方法，但它并没有限制我们只能用这八种方法，这也体现了 HTTP 协议良好的扩展性，我们可以任意添加请求动作，只要请求方和响应方都能理解就行。

例如著名的愚人节玩笑 RFC2324，它定义了协议 HTCPCP，即“超文本咖啡壶控制协议”，为 HTTP 协议增加了用来煮咖啡的 BREW 方法，要求添牛奶的 WHEN 方法。

此外，还有一些得到了实际应用的请求方法（WebDAV），例如 MKCOL、COPY、MOVE、LOCK、UNLOCK、PATCH 等。如果有合适的场景，你也可以把它们应用到自己的系统里，比如用 LOCK 方法锁定资源暂时不允许修改，或者使用 PATCH 方法给资源打个小补丁，部分更新数据。但因为这些方法是非标准的，所以需要为客户端和服务器编写额外的代码才能添加支持。

当然了，你也完全可以根据实际需求，自己发明新的方法，比如“PULL”拉取某些资源到本地，“PURGE”清理某个目录下的所有缓存数据。

# 11 | HTTP网址的组成

**URI 的基本组成**

URI，也就是统一资源标识符（Uniform Resource Identifier），用来标记服务器上的资源。

URI 最常用的形式，由 scheme、host:port、path 和 query 四个部分组成。

![image-20210801214959073](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210801214959.png)

- scheme

中文叫“方案名”或者“协议名”。常见的例如http、https。不常见的例如 ftp、ldap、file、news 等。

在 scheme 之后，必须是三个特定的字符“://”，它把 scheme 和后面的部分分离开。

- authority

表示资源所在的主机名，通常的形式是“host:port”，即主机名加端口号。

- path

有了协议名和主机地址、端口号，再加上后面标记资源所在位置的 path，浏览器就可以连接服务器访问资源了。

> 注意：URI 的 path 部分必须以“/”开始，也就是必须包含“/”，不要把“/”误认为属于前面 authority。

> 你可能见过`file:///D:/http_study/www/`这样的 uri，后面居然有三个斜杠，这是怎么回事？
>
> 这三个斜杠里的前两个属于 URI 特殊分隔符“://”；后面的“/D:/http_study/www/”是路径，而中间的主机名被“省略”了。这实际上是 file 类型 URI 的“特例”，它允许省略主机名，默认是本机 localhost。

- Query

很多时候我们还想在操作资源的时候附加一些额外的修饰参数。

它在 path 之后，用一个“?”开始，但不包含“?”，表示对资源附加的额外要求。查询参数 query 是多个“key=value”的字符串，这些 KV 值用字符“&”连接。

**URI 的完整格式**

URI 还有一个“真正”的完整形态，如下图所示。

![image-20210801215935846](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20210801215935.png)

- 身份信息

“user:passwd@”，表示登录主机时的用户名和密码。

> 现在已经不推荐使用这种形式了（RFC7230），因为它把敏感信息以明文形式暴露出来，存在严重的安全隐患。

- 片段标识符

“#fragment”，它是 URI 所定位的资源内部的一个“锚点”或者说是“标签”，浏览器可以在获取资源后直接跳转到它指示的位置。

> 片段标识符仅能由浏览器这样的客户端使用，服务器是看不到的。也就是说，浏览器永远不会把带“#fragment”的 URI 发送给服务器，服务器也永远不会用这种方式去处理资源的片段。

**URI 的编码**

URI 里只能使用 ASCII 码，如果要在 URI 里使用英语以外的汉字该怎么办呢？

某些特殊的 URI，会在 path、query 里出现“@&?"等起界定符作用的字符，会导致 URI 解析错误，这时又该怎么办呢？

URI 引入了编码机制，对于 ASCII 码以外的字符集和特殊字符做一个特殊的操作，把它们转换成与 URI 语义不冲突的形式。这在 RFC 规范里称为“escape”和“unescape”，俗称“转义”。

例如，空格被转义成“%20”，“?”被转义成“%3F”。而中文通常使用 UTF-8 编码后再转义，例如“银河”会被转义成“%E9%93%B6%E6%B2%B3”。

# 12 | HTTP响应状态码

RFC 标准里规定的状态码是三位数，并把状态码分成了五类。

这五类的具体含义是：

- 1××：提示信息，表示目前是协议处理的中间状态，还需要后续的操作；
- 2××：成功，报文已经收到并被正确处理；
- 3××：重定向，资源位置发生变动，需要客户端重新发送请求；
- 4××：客户端错误，请求报文有误，服务器无法处理；
- 5××：服务器错误，服务器在处理请求时内部发生了错误。

目前 RFC 标准里总共有 41 个状态码，状态码是允许自行扩展的。Apache、Nginx 等 Web 服务器都定义了一些专有的状态码。如果你自己开发 Web 应用，也完全可以在不冲突的前提下定义新的代码。

接下来就实际开发中比较有价值的状态码逐个详细介绍。

**1xx**

1××类状态码属于提示信息，是协议处理的中间状态，实际能够用到的时候很少。

- 101 Switching Protocols

  我们偶尔能够见到的是“101 Switching Protocols”。它的意思是客户端使用 Upgrade 头字段，要求在 HTTP 协议的基础上改成其他的协议继续通信，比如 WebSocket。而如果服务器也同意变更协议，就会发送状态码 101，在这之后的数据传输就不会再使用 HTTP 了。

**2××**

2××类状态码表示服务器收到并成功处理了客户端的请求。

- “200 OK”

  这是最常见的成功状态码，表示一切正常，服务器如客户端所期望的那样返回了处理结果，如果是非 HEAD 请求，通常在响应头后都会有 body 数据。

- “204 No Content”

  这是另一个很常见的成功状态码，它的含义与“200 OK”基本相同，但响应头后没有 body 数据。所以对于 Web 服务器来说，正确地区分 200 和 204 是很必要的。

- “206 Partial Content”

  是 HTTP 分块下载或断点续传的基础，在客户端发送“范围请求”、要求获取资源的部分数据时出现，它与 200 一样，也是服务器成功处理了请求，但 body 里的数据不是资源的全部，而是其中的一部分。

> 状态码 206 通常还会伴随着头字段“Content-Range”，表示响应报文里 body 数据的具体范围，供客户端确认，例如“Content-Range: bytes 0-99/2000”，意思是此次获取的是总计 2000 个字节的前 100 个字节。

**3××**

3××类状态码表示客户端请求的资源发生了变动，客户端必须用新的 URI 重新发送请求获取资源，也就是通常所说的“重定向”。

- “301 Moved Permanently”

  俗称“永久重定向”，含义是此次请求的资源已经不存在了，需要改用改用新的 URI 再次访问。

> 比如，你的网站升级到了 HTTPS，原来的 HTTP 不打算用了，这就是“永久”的，所以要配置 301 跳转，把所有的 HTTP 流量都切换到 HTTPS。

- “302 Found”

  曾经的描述短语是“Moved Temporarily”，俗称“临时重定向”，意思是请求的资源还在，但需要暂时用另一个 URI 来访问。

> 比如，今天夜里网站后台要系统维护，服务暂时不可用，这就属于“临时”的，可以配置成 302 跳转，把流量临时切换到一个静态通知页面，浏览器看到这个 302 就知道这只是暂时的情况，不会做缓存优化，第二天还会访问原来的地址。

> 301 和 302 都会在响应头里使用字段 Location 指明后续要跳转的 URI。

- “304 Not Modified”

  是一个比较有意思的状态码，它用于 If-Modified-Since 等条件请求，表示资源未修改，用于缓存控制。它不具有通常的跳转含义，但可以理解成“重定向已到缓存的文件”（即“缓存重定向”）。

**4××**

4××类状态码表示客户端发送的请求报文有误，服务器无法处理，它就是真正的“错误码”含义了。

- “400 Bad Request”

  表示请求报文有错误，但具体是数据格式错误、缺少请求头还是 URI 超长它没有明确说，只是一个笼统的错误，客户端看到 400 只会是“一头雾水”“不知所措”。所以，在开发 Web 应用时应当尽量避免给客户端返回 400，而是要用其他更有明确含义的状态码。

- “403 Forbidden”

  实际上不是客户端的请求出错，而是表示服务器禁止访问资源。原因可能多种多样，例如信息敏感、法律禁止等，如果服务器友好一点，可以在 body 里详细说明拒绝请求的原因，不过现实中通常都是直接给一个“闭门羹”。

- “404 Not Found”

  表示资源在本服务器上未找到，所以无法提供给客户端。但现在已经被“用滥了”，只要服务器“不高兴”就可以给出个 404，而我们也无从得知后面到底是真的未找到，还是有什么别的原因，某种程度上它比 403 还要令人讨厌。

4××里剩下的一些代码较明确地说明了错误的原因，都很好理解，开发中常用的有：

- 405 Method Not Allowed：不允许使用某些方法操作资源，例如不允许 POST 只能 GET；
- 406 Not Acceptable：资源无法满足客户端请求的条件，例如请求中文但只有英文；
- 408 Request Timeout：请求超时，服务器等待了过长的时间；
- 409 Conflict：多个请求发生了冲突，可以理解为多线程并发时的竞态；
- 413 Request Entity Too Large：请求报文里的 body 太大；
- 414 Request-URI Too Long：请求行里的 URI 太大；
- 429 Too Many Requests：客户端发送了太多的请求，通常是由于服务器的限连策略；
- 431 Request Header Fields Too Large：请求头某个字段或总体太大；

**5××**

5××类状态码表示客户端请求报文正确，但服务器在处理时内部发生了错误，无法返回应有的响应数据，是服务器端的“错误码”。

- “500 Internal Server Error”

  与 400 类似，也是一个通用的错误码，服务器究竟发生了什么错误我们是不知道的。不过对于服务器来说这应该算是好事，通常不应该把服务器内部的详细信息，例如出错的函数调用栈告诉外界。虽然不利于调试，但能够防止黑客的窥探或者分析。

- “501 Not Implemented”

  表示客户端请求的功能还不支持，这个错误码比 500 要“温和”一些，和“即将开业，敬请期待”的意思差不多，不过具体什么时候“开业”就不好说了。

- “502 Bad Gateway”

  通常是服务器作为网关或者代理时返回的错误码，表示服务器自身工作正常，访问后端服务器时发生了错误，但具体的错误原因也是不知道的。

- “503 Service Unavailable

  ”表示服务器当前很忙，暂时无法响应服务，我们上网时有时候遇到的“网络服务正忙，请稍后重试”的提示信息就是状态码 503。

> 503 是一个“临时”的状态，很可能过几秒钟后服务器就不那么忙了，可以继续提供服务，所以 503 响应报文里通常还会有一个“Retry-After”字段，指示客户端可以在多久以后再次尝试发送请求。

# 13 | HTTP有哪些特点？

**1. 灵活可扩展**

HTTP 协议诞生之初只规定了报文的基本格式，比如用空格分隔单词，用换行分隔字段、“header+body”等，报文里的各个组成部分都没有做严格的语法语义限制，可以由开发者任意定制。

**2. 可靠传输**

因为 HTTP 协议是基于 TCP/IP 的，而 TCP 本身是一个“可靠”的传输协议，所以 HTTP 自然也就继承了这个特性，能够在请求方和应答方之间“可靠”地传输数据。

**3. 应用层协议**

HTTP 凭借着可携带任意头字段和实体数据的报文结构，以及连接控制、缓存代理等特性，只要不太苛求性能，HTTP 几乎可以传递一切东西，满足各种需求，称得上是一个“万能”的协议。

**5. 请求 - 应答**

请求 - 应答模式是 HTTP 协议最根本的通信模型，通俗来讲就是“一发一收”、“有来有去”。

请求 - 应答模式也明确了 HTTP 协议里通信双方的定位，永远是请求方先发起连接和请求，是主动的，而应答方只有在收到请求后才能答复，是被动的，如果没有请求时不会有任何动作。

**6. 无状态**

什么是状态？

“状态”其实就是客户端或者服务器里保存的一些数据或者标志，记录了通信过程中的一些变化信息。

TCP 协议是有状态的，一开始处于 CLOSED 状态，连接成功后是 ESTABLISHED 状态，断开连接后是 FIN-WAIT 状态，最后又是 CLOSED 状态。

这些“状态”就需要 TCP 在内部用一些数据结构去维护，可以简单地想象成是个标志量，标记当前所处的状态，例如 0 是 CLOSED，2 是 ESTABLISHED 等等。

什么是无状态？

在 HTTP 整个协议里没有规定任何的“状态”，客户端和服务器建立连接前两者互不知情，每次收发的报文也都是互相独立的，没有任何的联系。收发报文也不会对客户端或服务器产生任何影响，连接后也不会保存任何信息。

> “无状态”形象地来说就是“没有记忆能力”。比如，浏览器发了一个请求，说“我是小明，请给我 A 文件。”，服务器收到报文后就会检查一下权限，看小明确实可以访问 A 文件，于是把文件发回给浏览器。
>
> 接着浏览器还想要 B 文件，但服务器不会记录刚才的请求状态，不知道第二个请求和第一个请求是同一个浏览器发来的，所以浏览器必须还得重复一次自己的身份才行：“我是刚才的小明，请再给我 B 文件。”

**7. 其他特点**

例如传输的实体数据可缓存可压缩、可分段获取数据、支持身份认证、支持国际化语言等。

但这些并不能算是 HTTP 的基本特点，因为这都是由第一个“灵活可扩展”的特点所衍生出来的。

# 14 | HTTP有哪些优点？又有哪些缺点？

今天的讨论范围仅限于 HTTP/1.1，所说的优点和缺点也仅针对 HTTP/1.1。

**简单、灵活、易扩展**

HTTP 协议是很“简单”的，基本的报文格式就是“header+body”，头部信息也是简单的文本格式，用的也都是常见的英文单词。

HTTP 协议里的请求方法、URI、状态码、原因短语、头字段等每一个核心组成要素都没有被“写死”，允许开发者任意定制、扩充或解释，给予了浏览器和服务器最大程度的信任和自由。

**应用广泛、环境成熟**

随着互联网特别是移动互联网的普及，HTTP 已经延伸到了世界的每一个角落：从简单的 Web 页面到复杂的 JSON、XML 数据，从台式机上的浏览器到手机上的各种 APP，你很难找到一个没有使用 HTTP 的地方。

不仅在应用领域，在开发领域 HTTP 协议也得到了广泛的支持。几乎所有的编程语言都有 HTTP 调用库和外围的开发测试工具。

**无状态**

“无状态”，它对于 HTTP 来说既是优点也是缺点。

服务器没有“记忆能力”，所以就不需要额外的资源来记录状态信息，能减轻服务器的负担，把更多的 CPU 和内存用来对外提供服务。

而且，“无状态”也表示服务器没有“状态”的差异，所以可以很容易组成集群，让负载均衡把请求转发到任意一台服务器。使用“堆机器”的“笨办法”轻松实现高并发高可用。

“无状态”又有什么缺点呢？

既然服务器没有“记忆能力”，它就无法支持需要连续多个步骤的“事务”操作。

例如电商购物，首先要登录，然后添加购物车，再下单、结算、支付，这一系列操作都需要知道用户的身份才行，但“无状态”服务器是不知道这些请求是相互关联的，每次都得问一遍身份信息，不仅麻烦，而且还增加了不必要的数据传输量。

> Cookie 技术就使 HTTP 既保留了“无状态”的优点，也发挥了“有状态”的优点。

**明文**

“明文”意思就是 header 里的报文不使用二进制数据，而是用简单可阅读的文本形式。

它的优点是不需要借助任何外部工具，用浏览器、Wireshark 或者 tcpdump 抓包后，就可以很容易地查看或者修改，为我们的开发调试工作带来极大的便利。

它的缺点也是一样显而易见，HTTP 报文的所有信息都会暴露在传输链路上，黑客只要侵入了这个链路里的某个设备，简单地“旁路”一下流量，就可以实现对通信的窥视。

**不安全**

HTTP 协议不支持“完整性校验”，数据在传输过程中容易被窜改而无法验证真伪。

例如，你收到了一条银行用 HTTP 发来的消息：“小明向你转账一百元”，你无法知道小明是否真的就只转了一百元，也许他转了一千元或者五十元，但被黑客窜改成了一百元，真实情况到底是什么样子 HTTP 协议没有办法给你答案。

> 为了解决 HTTP 不安全的缺点，所以就出现了 HTTPS。

**性能**

HTTP 协议基于 TCP/IP，并且使用了“请求 - 应答”的通信模式，所以性能的关键就在这两点上。

现在互联网的特点是移动和高并发，不能保证稳定的连接质量，所以在 TCP 层面上 HTTP 协议有时候就会表现的不够好。

而“请求 - 应答”模式则加剧了 HTTP 的性能问题，这就是著名的“队头阻塞”（Head-of-line blocking），当顺序发送的请求序列中的一个请求因为某种原因被阻塞时，在后面排队的所有请求也一并被阻塞，会导致客户端迟迟收不到数据。

> 现在已经有了终极解决方案：HTTP/2 和 HTTP/3。

