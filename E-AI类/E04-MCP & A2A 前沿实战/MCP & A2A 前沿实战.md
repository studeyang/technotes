> 来自极客时间《MCP&A2A前沿实战》

# 开篇词｜浪潮拐点——为何MCP与A2A诞生在此时此刻？

AI 时代的时间仿佛被按下了加速键。技术更迭令人目不暇接，每一项技术突破都如同汹涌的海浪，不断冲击并拓展着我们对于 AI 的认知边界，重塑 AI 应用开发能力的边界。

**大模型应用工程化过程的三大难题**

大模型尽管可以作为智能系统的“核心引擎”，但大模型应用工程化挑战如影随形。开发者面临三大难题：

1、模型与外部世界的割裂

大模型是基于概率计算的新范式，这种新范式虽强大，但仍需要与传统的结构化计算范式相结合，也就是通过工具调用来完成精确任务。

而目前传统结构化工具和大模型之间是割裂的，大模型难以直接、动态地接入实时数据、数据库或企业工具。

2、Agent 协作的孤岛效应

AI Agent 的兴起让“做事”的智能体成为可能，但不同框架（如 LangGraph、AutoGen、CrewAI）各自为政，缺乏统一的通信标准，跨平台协作如同“鸡同鸭讲”。

3、复杂场景的工程化瓶颈

从搜索助手到企业知识中台，RAG（检索增强生成）与多 Agent 系统需要处理多源数据、多模态交互和长时任务，现有工具链难以提供统一的解决方案。

就在此时，MCP 和 A2A 应运而生，恰如涓涓细流汇聚成江河，为“模型主控、客户端驱动”的范式提供了标准化、可扩展的协议层。

它们解决了上述痛点，为大模型应用的工程化铺平了道路。

![img](https://static001.geekbang.org/resource/image/b3/6e/b3291dc25d2306e891bd9cef6540066e.png?wh=1499x890)

对于这两个新技术，我们可以先看看它们的核心理解，以及解决了什么问题，这样更容易抓住其本质。

**MCP：模型主控，客户端驱动**

Model Context Protocol（MCP） 翻译成中文是模型上下文协议。

传统上，将 AI 系统连接到外部工具需要集成多个 API。每个 API 集成都意味着单独的代码、文档、身份验证方法、错误处理和维护。这些 API 就像一扇扇独立的门，每扇门都有自己的钥匙和规则。

![img](https://static001.geekbang.org/resource/image/2b/50/2b9630abb81cbc2922f4fa419c6e9b50.png?wh=1920x1080)

让我们举例子来说。在引入 MCP 之前，如果我要让一个 Agent 同时具备“网络搜索”“数据库查询”“文本翻译”三种能力，通常要写三套适配器：

- 搜索工具：手动拼 HTTP 请求，处理 OAuth 鉴权，解析 HTML 或 JSON，捕获请求超时。
- 数据库查询：配置 JDBC/ODBC 连接，管理连接池，拼装 SQL，逐行读取 ResultSet。
- 翻译服务：对接 Google Translate 或腾讯翻译 API，关注签名算法、流量限速、错误码处理。

每接入一个新工具，都要重复以上流程，代码冗余且难以维护，扩展成本极高。

MCP 则把这些繁琐细节都“藏”到服务器端：

1、服务端只需注册好 Search、QueryDB、Translate 三个工具能力；

2、然后 Agent 发起同一套 JSON-RPC 调用：

```json
{
  "method": "callTool",
  "params": {
    "tool": "Translate",
    "input": "Hello, world!",
    "target_lang": "zh"
  }
}
```

3、MCP 服务器负责底层的 HTTP 请求、鉴权、连接管理和结果解析，最后把翻译结果一并返回给模型。

它是一个客户端 - 服务器的架构，其核心理念是“模型主控、客户端驱动服务器调用”——模型负责推理和决策，客户端则动态提供上下文、工具和资源，而这些工具和资源调用则由外部服务器来提供。

![img](https://static001.geekbang.org/resource/image/f4/6c/f48d4f8a286d53c10c8d681b35f2496c.png?wh=1920x1080)

你可以将其想象成一个专门为 AI 应用提供的 USB-C 端口，即插即用。所有繁琐的事情，都推给 MCP 服务器根据协议来提供。

MCP 真正把“模型想用什么工具干啥”这件事变得极其简单——大模型专注决策，开发者专注业务逻辑，Agent 开发门槛被一举摁平。

![img](https://static001.geekbang.org/resource/image/cc/ec/cc8429ebd851624b8ee76e28bd8cdcec.png?wh=1573x750)

**A2A：Agent 间的“通用语言”**

Agent-to-Agent，翻译过来就是“智能代理之间的协议”。本质上讲，它其实就是让不同的智能代理（Agent）能够无障碍地沟通和协作的标准语言。可以把它理解成大模型 Agent 们用来“聊天”的“通用语言”。

Agent 与 Agent 之间的交互，和人类之间的沟通有点类似。但问题在于，不同的开发者、公司和团队可能会创造出各种各样的 Agent，如果每个 Agent 都有自己的一套沟通方法，那必然是鸡同鸭讲，造成混乱不堪的局面。

于是，A2A 协议应运而生了：它定义了一套清晰、标准的沟通方式，让所有智能代理可以顺畅地交流彼此的需求、能力、决策和状态。

> Agent 们通过 A2A 沟通，就像大家都学会了同一种语言，不管来自哪个“国家”，都能顺畅无阻地交流、互相配合完成任务。

我们还是用一个简单的生活场景来说明 A2A 的运作机制吧。这里假设我们有三个 Agent，分别是旅行规划 Agent（Travel Planner），天气查询 Agent（Weather Checker），酒店预订 Agent（Hotel Booker）。

![img](https://static001.geekbang.org/resource/image/c0/f1/c0231553bc245d0892f2c561b06e36f1.jpg?wh=6655x3583)

用户向旅行规划 Agent 发送“规划北京到上海 3 天行程”的请求，旅行 Agent 通过 A2A 协议依次发出两次标准化能力调用：

1、向天气查询 Agent 发送“请告诉我 5 月 20–22 日上海的天气预报”

2、向酒店预订 Agent 发送“帮我查 5 月 20–22 日上海南京路附近的四星酒店，预算每晚 800 元内”

各 Agent 按统一消息格式（能力发现→调用→异步返回）快速响应并返回天气和酒店信息，旅行 Agent 将结果整合并生成最终行程。

**MCP 与 A2A：相似点与不同点**

相同点：

![img](https://static001.geekbang.org/resource/image/9d/36/9dyy24532301dfeef5dbd62b5e142836.jpg?wh=2426x1359)

不同点：

![img](https://static001.geekbang.org/resource/image/6c/6e/6c88486a1695ffa5279e7571360bf66e.jpg?wh=1920x869)

简而言之。二者尽管相似，但是彼此并非竞争，而是互补的关系，且刚好形成了一个完整的 AI 时代的通信协议方案。

![img](https://static001.geekbang.org/resource/image/b8/yy/b83d289f3f6297cc765681b5b4efc2yy.jpg?wh=1920x1270)

**课程设计架构**

本课程以 “理论奠基 → 协议拆解 → 实战应用 → 综合实践” 为核心架构，分为四个模块。

课程代码仓库：

- https://github.com/huangjia2019/mcp-in-action
- https://github.com/huangjia2019/a2a-in-action

这门课程涉及到的编程语言和技术栈：

![img](https://static001.geekbang.org/resource/image/76/ec/7605de495fb9b5c87e7a008d510ca6ec.jpg?wh=2749x1657)





