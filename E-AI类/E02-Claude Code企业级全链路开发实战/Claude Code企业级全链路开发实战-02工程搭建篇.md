# ==工程搭建篇==

# 08｜工程初始化（上）：后端骨架与公共基础设施

先来展示下 Hify 的本地工作界面吧。

1、模型管理

![img](https://static001.geekbang.org/resource/image/65/dc/65f07dd405797cb17e305c5a7baf4cdc.png?wh=3800x1312)

2、Agent 管理

![img](https://static001.geekbang.org/resource/image/7f/06/7f8f4f03d6639766e8575002e7047006.png?wh=3828x1852)

3、知识库管理

![img](https://static001.geekbang.org/resource/image/74/a0/7496471b6917d24f75fd5bb2a34e31a0.png?wh=3840x1350)

4、工作流

![img](https://static001.geekbang.org/resource/image/76/53/761c2bb967ac7c33e3513206a60e1b53.png?wh=3826x1846)

5、MCP工具

![img](https://static001.geekbang.org/resource/image/c5/38/c529e54f99a827781ceb099d7cf5c138.png?wh=3822x1620)

6、对话

![img](https://static001.geekbang.org/resource/image/11/f7/11aac74261e6656f2cc8a41fe14602f7.png?wh=3826x1892)

看完了效果，我们开始今天的课程内容。这一讲要做的事：让 Claude Code 搭建 Hify 后端的工程骨架。

## 先想清楚怎么拆

我把它拆成四步：

1. Maven 多模块骨架（父 pom + 子模块 pom + 目录结构）
2. hify-common 公共基础设施（Result、BizException、全局异常处理、配置类）
3. 业务模块空壳（每个模块的 package 结构和启动验证）
4. 验收，启动项目，确认一切正常

![img](https://static001.geekbang.org/resource/image/46/9d/465a508ec31f34c9c6558e0258918e9d.jpg?wh=1440x670)

为什么是这个顺序？依赖关系决定了顺序。Maven 骨架是所有东西的容器，必须先有。hify-common 被所有业务模块依赖，排第二。业务模块依赖 common，排第三。最后验收确认整体能跑。

> 先地基，后框架，最后验收。这个顺序不只适用于工程初始化，后面做任何模块都是这个思路。

## 分步搭建

### 第一步：Maven 多模块骨架

给 Claude Code 的指令思路：

```
按照 CLAUDE.md 中的项目结构和技术栈，创建 Hify 的 Maven 多模块工程骨架。父 pom 声明所有子模块，统一管理 Spring Boot、MyBatis-Plus、Redis 等版本号。子模块之间的依赖关系按 CLAUDE.md 中定义的架构来。只创建 pom 和目录结构，不需要写 Java 代码。
```

输出是：

![img](https://static001.geekbang.org/resource/image/9e/6e/9e37d3d49b58130af046f02b1208fb6e.png?wh=3180x1730)

> 注意：检查版本管理是否统一？
>
> Spring Boot、MyBatis-Plus、Redis 的版本号应该只出现在父 pom 的 里，子模块不重复声明版本。

### 第二步：hify-common 公共基础设施

我把这一步进一步拆成五个小任务。

**任务一：统一响应 Result 和分页 PageResult**

Cluade 的指令是：

```
在 hify-common 中创建统一响应类。按照 CLAUDE.md 接口规范：Result<T> 包含 code、message、data 三个字段，提供 ok() 和 fail() 静态方法。PageResult<T> 继承 Result，额外包含 total、page、size。
```

输出是：

![img](https://static001.geekbang.org/resource/image/9d/aa/9d6dfea3e370e0ee5156441e1b1e37aa.png?wh=1880x398)

**任务二：错误码枚举和业务异常**

Cluade 的指令是：

```
在 hify-common 中创建错误码枚举 ErrorCode 和业务异常类 BizException。ErrorCode 包含 code 和 message，覆盖通用错误（参数错误、未授权、系统内部错误等）。BizException 持有 ErrorCode，支持自定义 message 覆盖。
```

输出是：

![img](https://static001.geekbang.org/resource/image/fd/52/fda0902fa6c21f3bc77ce1ec596cf852.png?wh=1180x602)

**任务三：全局异常处理器**

Cluade 的指令是：

```
在 hify-common 中创建全局异常处理器 GlobalExceptionHandler，使用 @RestControllerAdvice。捕获 BizException 返回对应错误码，捕获 MethodArgumentNotValidException 返回参数校验错误，兜底捕获 Exception 返回系统内部错误。所有异常响应必须使用 Result.fail() 和 ErrorCode 枚举。
```

输出是：

![img](https://static001.geekbang.org/resource/image/81/a9/81617cf086f0eaff3e1efc8530279da9.png?wh=1814x440)

这个任务值得多说一点。Claude Code 第一次生成这个处理器的时候，它在兜底的 Exception 处理里没有用 ErrorCode 枚举。

我让它改成 Result.fail(ErrorCode.INTERNAL_ERROR)，然后在 CLAUDE.md 的行为指令里补了一条：“异常处理必须使用 ErrorCode 枚举，禁止硬编码错误码和错误信息。”

每次 AI 跑偏，不只是改掉当前的错，更要把规范补上，堵住同类问题的口子。这就是 SDD 闭环的日常运转——定规范、AI 执行、发现偏差、迭代规范。

**任务四：MyBatis-Plus 配置**

Cluade 的指令是：

```
在 hify-common 中创建 MyBatis-Plus 配置类。包含：分页插件、自动填充（createTime、updateTime）、逻辑删除配置。
```

输出是：

![img](https://static001.geekbang.org/resource/image/93/81/93dbf3d01fc0d361c1cd632a57029581.png?wh=1298x756)

Claude 生成这种模板代码非常快，基本不会出错，因为这些代码是非常标准的。

**任务五：Redis 配置**

Cluade 的指令是：

```
在 hify-common 中创建 Redis 配置类。包含：RedisTemplate 序列化配置（key 用 String，value 用 JSON）、基础的 RedisUtil 工具类（get/set/delete/expire）。
```

输出是：

![img](https://static001.geekbang.org/resource/image/79/53/796ff53815b61c2ecc2c15fc4bcabd53.png?wh=1416x870)

### 第三步：业务模块空壳

现在给每个业务模块创建基础的 package 结构。

```
为 hify-provider、hify-agent、hify-chat、hify-mcp 等业务模块创建标准的 package 结构。按照 CLAUDE.md 代码组织规范，每个模块包含 controller/service/service-impl/mapper/entity/dto/config 目录。每个模块只创建 package 和一个空的占位类，不需要写业务代码。
```

然后在 hify-app 模块里创建 Spring Boot 启动类和 application.yml：

```
在 hify-app 中创建 Spring Boot 启动类 HifyApplication，以及 application.yml 配置文件。配置项包括：数据库连接、Redis 连接、MyBatis-Plus 配置、服务端口 8080。
```

输出是：

![img](https://static001.geekbang.org/resource/image/ac/4c/acdaa9bbee0993713fc0c30ac44e6f4c.png?wh=1422x662)

### 第四步：验收

为了有一个可验证的端点，让 Claude Code 加一个健康检查接口：

```
在 hify-app 中创建 HealthController，路径 GET /api/v1/health，返回 Result.ok(“Hify is running”)。
```

启动后访问 http://localhost:8080/api/v1/health，应该可以看到：

```json
{
  "code": 200,
  "message": "success",
  "data": "Hify is running"
}
```





