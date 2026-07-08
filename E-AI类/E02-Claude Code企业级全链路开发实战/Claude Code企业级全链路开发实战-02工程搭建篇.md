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

# 09｜工程初始化（下）：前端工程与一键启动

上一讲我们搭好了后端骨架——Maven 多模块结构、公共基础设施、健康检查接口，java -jar 能跑，访问 /api/v1/health 返回 200。

这一讲我们把前端 Vue 工程、前后端联通、启动脚本补齐。

## 前端 Vue 工程搭建

我分成三步：项目骨架、axios 统一请求层、路由和页面空壳。

### 第一步：项目骨架

给 Claude Code 的指令思路：

```
初始化 Hify 前端项目 hify-web。Vue 3 + TypeScript + Vite + Element Plus。目录结构按 CLAUDE.md 中定义的前端结构来。Vite 开发服务器配置代理：/api 请求转发到 localhost:8080。
```

输出是：

![img](https://static001.geekbang.org/resource/image/42/88/42df25ffef87fa9e041f811c7ef50388.png?wh=1068x952)

开发阶段前端跑在 5173 端口，通过 Vite 代理转发 /api 请求到后端 8080 端口，解决跨域问题。

![img](https://static001.geekbang.org/resource/image/e0/3f/e0f80023f9927337bfc524542820cb3f.png?wh=1014x184)

### 第二步：axios 统一请求层

后端定了统一响应格式 `Result<T>`，每个接口都返回 `{ code: 200, message: "success", data: {...} }`。前端的 axios 封装要和这套格式对接，让业务代码不需要每次都手动处理 code 判断和 data 解包。

给 Claude Code 的指令思路：

```
在 hify-web/src/utils/ 下创建 request.ts，封装 axios 实例。baseURL 设为 /api。响应拦截器里判断 code：200 直接返回 data  字段（自动解包），非 200 用 Element Plus 的 ElMessage.error 提示 message，然后 reject。导出 get、post、put、del 四个方法。
```

为什么要在拦截器里自动解包 data？

```typescript
// 封装之前
const result = await providerApi.getList()
const list = result.data  // 每次都要 .data

// 封装之后
const list = await providerApi.getList() // 直接拿到 data
```

来看生成的 request.ts 的代码：

```typescript
import axios from 'axios'
import { ElMessage } from 'element-plus'

const instance = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

instance.interceptors.response.use(
  (response) => {
    const { code, message, data } = response.data
    if (code !== 200) {
      ElMessage.error(message || '请求失败')
      return Promise.reject(new Error(message))
    }
    return data
  },
  (error) => {
    ElMessage.error(error.message || '网络异常')
    return Promise.reject(error)
  }
)

export const get = <T>(url: string, params?: object): Promise<T> =>
  instance.get(url, { params })

export const post = <T>(url: string, data?: object): Promise<T> =>
  instance.post(url, data)

export const put = <T>(url: string, data?: object): Promise<T> =>
  instance.put(url, data)

export const del = <T>(url: string): Promise<T> =>
  instance.delete(url)
```

然后让 Claude Code 基于这个封装写一个示例 API 文件：

```
在 hify-web/src/api/ 下创建 health.ts，用封装好的 request 调用 GET /api/v1/health。导出 getHealth 方法。
```

文件代码是：

```typescript
import { get } from '@/utils/request'

export const getHealth = () => get<string>('/v1/health')
```

### 第三步：路由和页面空壳

给 Claude Code 的指令是：

```
在 hify-web 中配置 Vue Router，创建以下路由和对应的空壳页面组件：模型管理、Agent 管理、对话。每个空壳页面只显示页面名称，比如 ProviderList.vue 里就一行"模型提供商管理"。再创建一个 App.vue 布局：左侧 Element Plus 菜单栏（三个菜单项对应三个路由），右侧内容区用 router-view。
```

这一步生成的是一个有完整导航结构的空壳应用——左边菜单、右边内容，点菜单能切换页面，每个页面都是占位文字。后面往里填内容就行。

![img](https://static001.geekbang.org/resource/image/60/89/608730ab62b366b6fed1ca2574769f89.png?wh=2704x1008)

整个调用链路如下：

![img](https://static001.geekbang.org/resource/image/c4/7a/c4cebd3e995b5936137641c30574da7a.jpg?wh=1440x592)

# 10｜基础组件（上）：后端业务基础设施

这些是所有业务模块都会用到的底层能力，不先搭好，后面每个模块都要重复处理一遍。但问题来了：具体需要准备哪些基础组件？你可能有经验能列出一部分，但难免有遗漏。这一讲引入一个新的协作模式来解决这个问题。

**新的协作模式：先问再做**

“业务开发前需要准备哪些基础组件”这个问题，你有大致想法，但不确定有没有遗漏、先后顺序对不对。

先让 Claude Code 帮你想，再让它做，把它当成一个资深架构师来咨询。

咨询模式：你知道大方向但不确定细节  → 先问 Claude Code → 它帮你梳理  → 你判断取舍  → 再给指令执行。适合不确定性高的时候。

**让 Claude Code 梳理基础组件清单**

我问 Claude Code：

```
Hify 项目工程骨架已经搭好（Maven 多模块、hify-common 的 Result / 异常处理 / MyBatis-Plus 配置 / Redis 配置、前端 Vue 工程）。现在要开始做业务功能了。在写业务代码之前，还需要准备哪些基础组件？从数据库层、接口层、外部调用、缓存、可观测性几个角度帮我梳理，每个组件说明它解决什么问题。
```

它给了一份很详细的清单：

![img](https://static001.geekbang.org/resource/image/21/yy/2144ab642ebd1e1df536f2b146499eyy.png?wh=716x600)

Claude Code 见过的项目比你多，它的建议不能直接照搬，但用来查漏补缺非常好。



