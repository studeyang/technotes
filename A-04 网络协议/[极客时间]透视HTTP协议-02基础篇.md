# 08 | 键入网址再按下回车，后面究竟发生了什么？

**使用 IP 地址访问 Web 服务器**

下图是一次在 Chrome 浏览器的地址栏里输入“http://127.0.0.1/”，再按下回车键，等欢迎页面显示出来后 Wireshark 里捕获的数据包。

![image-20201101223615503](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201101223615.png)

**抓包分析**

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201101224832.png" alt="image-20201101224832375" style="zoom:50%;" />

1. 浏览器要用 HTTP 协议收发数据，首先要做的就是建立 TCP 连接。使用“三次握手”建立与 Web 服务器的连接。（No 1-3）

   <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201101224900.png" alt="image-20201101224900308" style="zoom:50%;" />

2. 浏览器按照 HTTP 协议规定的格式，通过 TCP 发送了一个“GET / HTTP/1.1”请求报文（No 7）

3. 随后，Web 服务器回复了第五个包，在 TCP 协议层面确认：“刚才的报文我已经收到了”，不过这个 TCP 包 HTTP 协议是看不见的。（No 8）

4. Web 服务器收到报文后在内部就要处理这个请求。同样也是依据 HTTP 协议的规定，解析报文，看看浏览器发送这个请求想要干什么。再拼成符合 HTTP 格式的报文，发回去。（No 9）

5. 浏览器也要给服务器回复一个 TCP 的 ACK 确认，“你的响应报文收到了，多谢。”（No 10）

   <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201101225051.png" style="zoom:50%;" />

6. 这时浏览器就收到了响应数据，但里面是什么呢？所以也要解析报文。一看，服务器给我的是个 HTML 文件，好，那我就调用排版引擎、JavaScript 引擎等等处理一下，然后在浏览器窗口里展现出了欢迎页面。

   > 这之后还有两个来回，共四个包，重复了相同的步骤。这是浏览器自动请求了作为网站图标的“favicon.ico”文件，与我们输入的网址无关。但因为我们的实验环境没有这个文件，所以服务器在硬盘上找不到，返回了一个“404 Not Found”。
   >
   > <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201101225125.png" alt="image-20201101225125358" style="zoom:50%;" />

至此，“键入网址再按下回车”的全过程就结束了。TCP 执行四次挥手。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201101225158.png" alt="image-20201101225157975" style="zoom:50%;" />

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
> <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201102222121.png" alt="image-20201102222121278" style="zoom:50%;" />

HTTP 协议的请求报文和响应报文的结构基本相同，由三大部分组成：

1. 起始行（start line）：描述请求或响应的基本信息；
2. 头部字段集合（header）：使用 key-value 形式更详细地说明报文；
3. 消息正文（entity）：实际传输的数据，它不一定是纯文本，可以是图片、视频等二进制数据。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201102222451.png" alt="image-20201102222451597" style="zoom:50%;" />

报文的最后是一个空白行结束，没有 body。

**请求行**

请求行（request line）是 HTTP 的起始行，它简要地描述了客户端想要如何操作服务器端的资源。

请求行由三部分构成：

1. 请求方法：是一个动词，如 GET/POST，表示对资源的操作；
2. 请求目标：通常是一个 URI，标记了请求方法要操作的资源；
3. 版本号：表示报文使用的 HTTP 协议版本。

这三个部分通常使用空格（space）来分隔，最后要用 CRLF 换行表示结束。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201102222849.png" alt="image-20201102222849101" style="zoom:50%;" />

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

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201102223141.png" alt="image-20201102223141078" style="zoom:50%;" />

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

  <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201102224351.png" alt="image-20201102224351640" style="zoom:50%;" />

  它的 Server 字段里就看不出是使用了 Apache 还是 Nginx，只是显示为“GitHub.com”。

- Content-Length

  它表示报文里 body 的长度，也就是请求头或响应头空行后面数据的长度。

**课下作业**

1. 如果拼 HTTP 报文的时候，在头字段后多加了一个 CRLF，导致出现了一个空行，会发生什么？
2. 讲头字段时说“:”后的空格可以有多个，那为什么绝大多数情况下都只使用一个空格呢？





















