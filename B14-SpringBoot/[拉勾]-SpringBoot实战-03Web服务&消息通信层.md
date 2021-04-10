# Web服务层

# 11 | 构建一个 RESTful 风格的 Web 服务

**理解 RESTful 架构风格**

REST（Representational State Transfer，表述性状态转移）这种架构风格把位于服务器端的访问入口看作一个资源，在传输协议上使用标准的 HTTP 方法，比如最常见的 GET、PUT、POST 和 DELETE。

下表展示了 RESTful 风格的一些具体示例：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210410220238.png" alt="image-20210410220238139"  />

对于 RESTful 风格设计 HTTP 端点，业界也存在一些约定。以 Account 这个领域实体为例，如果我们把它视为一种资源，那么 HTTP 端点的根节点命名上通常采用复数形式，即“/accounts”。

在设计 RESTful API 时，针对常见的 CRUD 操作，下图展示了 RESTful API 与非 RESTful API 的一些区别。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210410221357.png" alt="image-20210410221357316" style="zoom:50%;" />

**使用基础注解**

- @RestController

@RestController 注解继承自 Spring MVC 中的 @Controller 注解，是一个基于 RESTful 风格的 HTTP 端点，并且会自动使用 JSON 实现 HTTP 请求和响应的序列化/反序列化方式。

- @GetMapping

@GetMapping 的注解的定义与 @RequestMapping 非常类似，只是默认使用了 RequestMethod.GET 指定 HTTP 方法。

**控制请求的输入**

- @PathVariable

@PathVariable 注解用于获取路径参数。即从类似 url/{id} 这种形式的路径中获取 {id} 参数的值。

- @RequestParam

@RequestParam 注解也是用于获取请求中的参数，但是它面向类似 url?id=XXX 这种路径形式。

- @RequestMapping

在 HTTP 协议中，content-type 属性用来指定所传输的内容类型，我们可以通过 @RequestMapping 注解中的 produces 属性来设置这个属性。

- @RequestBody

@RequestBody 注解用来处理 content-type 为 application/json 类型的编码内容，通过 @RequestBody 注解可以将请求体中的 JSON 字符串绑定到相应的 JavaBean 上。

# 12 | 如何使用 RestTemplate 消费 RESTful 服务？

**创建 RestTemplate**

如果我们想创建一个 RestTemplate 对象，最简单且最常见的方法是直接 new 一个该类的实例，如下代码所示：





**使用 RestTemplate 访问 Web 服务**



**RestTemplate 其他使用技巧**







