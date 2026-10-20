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

# 协议综述篇 (2讲)

# 01｜开箱即用：MCP是LLM开发范式的增强

这节课，我们将用一个通过 MCP 协议调用外部工具的实战，来理解 MCP 协议的强大之处。

我们不妨先来回顾一下这两三年来，也就是 MCP 出现之前，我们是如何使用大模型的。

**从提示工程到 RAG**

RAG 这种 LLM 应用开发范式背后的基本思想，就是通过将 LLM 与外部数据源相结合来提高其准确性和相关性。

1. 检索：首先通过向量数据库或其他检索系统，找出与用户查询相关的信息；
2. 增强：将检索到的信息作为上下文提供给大模型；
3. 生成：大模型基于这些额外信息生成回答。

![img](https://static001.geekbang.org/resource/image/f4/53/f4347e68188a8834965932fd2f602a53.jpg)

举例来说，我们需要编写 SQL 查询来检索过去 10 天内最畅销的产品。由于 LLM 不知道表模式或列名，因此直接询问 LLM 可能会导致无法使用的 SQL 查询。为了改进这一点，可以通过 RAG 来获取模式和列，以便 LLM 可以更准确地生成查询。

**从 RAG 到 Agent 和工具调用**

RAG 解决的是让 LLM 使用内部知识，同时减少幻觉的问题，但是它并没有增强大模型的行动能力。

于是 Agent 模式应运而生。Agent 本质上是赋予了大模型使用工具并采取行动的开发范式。它的工作流程包括：

1. 规划：大模型理解用户需求，规划解决方案。
2. 工具选择：决定使用哪些工具来完成任务。
3. 工具调用：调用选定的工具并处理返回结果。
4. 反思与调整：评估进展，必要时调整计划。
5. 输出结果：向用户呈现最终结果。

![img](https://static001.geekbang.org/resource/image/74/75/74795f1839ca9df24bd35a596007ef75.jpg?wh=3536x2172)

**大模型应用开发的两个范式**

以上所说的 RAG 和 Agent，就是大模型应用开发的目前最常用，也最通用的两个范式。

![img](https://static001.geekbang.org/resource/image/a3/85/a3dyyc6b092bcef2yy139623c5382a85.png?wh=1084x496)

**MCP 增强了 RAG 和 Agent**

对于 RAG 来说，MCP 通过定义统一的 SessionMessage 协议和工具发现机制，使 RAG 能够无缝接入多源数据检索，只需一次集成即可动态检索并注入上下文，大幅提高了检索增强生成的准确性和可维护性。

同时，MCP 为 Agent 提供了标准化的工具调用接口和结果回传格式，让大模型可以自主选择、分步调度各类工具执行复杂任务，无需手动注册或编码集成。这将显著提升 Agent 应用的开发效率和扩展能力。

**MCP 实战：Cursor（或 Copilot）+ DuckDB**

下面，我们正式开始一次通过 MCP 进行工具调用的实战。这个实战案例中，我要在我的代码编辑器中用一个叫做 DuckDB 的数据分析工具来帮我自动分析我的图书销售情况。

> 如果你也像我一样，对 [MotherDuck](https://motherduck.com/docs/getting-started/) 完全不了解。那么正合适，MCP 简单到什么程度呢？你在完全不懂的情况下，也可以快速展开对该服务的使用。 所有细节都封装在 MCP 协议内部，我们只要知道它大概可以做数据分析就可以开始用了。

把下面这段配置给复制并粘贴到你的 mcp.json 文件中。

```json
{
  "mcpServers": {
    "mcp-server-motherduck": {
      "command": "uvx",
      "args": [
        "mcp-server-motherduck",
        "--db-path",
        "md:",
        "--motherduck-token",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRvaHVhbmdqaWFAZ21haWwuY29tIiwic2Vzc2lvbiI6InRvaHVhbmdqaWEuZ21haWwuY29tIiwicGF0IjoiLUFvRmlRcE9xREZNb05sVFdwZzJha28yMDNnc0tkM3VyMXhBeHRKS3phZyIsInVzZXJJZCI6ImU0ZmUwZTYxLTgxMDEtNDdlZC05OGNhLTJmNGQ2MjZkYTUxYyIsImlzcyI6Im1kX3BhdCIsInJlYWRPbmx5IjpmYWxzZSwidG9rZW5UeXBlIjoicmVhZF93cml0ZSIsImlhdCI6MTc0Nzc0MTUxOX0.kmAvQ2AllpYo9UdotsqaysLHfe_yU51EeOpXYd85bkc"
      ]
    }
  }
}

```

接下来，我们利用 Cursor 这个 MCP Client 来调用 Mother Duck 的工具服务了！我在 Cursor 的对话界面中输入下面的话：

```
请调用mother duck工具帮我做数据分析
```

![img](https://static001.geekbang.org/resource/image/8f/2d/8f0ec49f4f1fcccf7a455fac9d89162d.png?wh=1237x302)

Cursor 回答我说当然可以，但是你需要提交一个数据表。在 MotherDuck 网页版进行了几个简单操作，就把我的数据文件上载到了云端数据库。

![img](https://static001.geekbang.org/resource/image/56/94/5602b35ac30f717a2cf9c9e3d58d6c94.png?wh=600x1069)

# 02｜来而有往：A2A 协议是 Agent 之间的桥梁

在大规模部署自主 AI Agent 的时代，不同供应商和框架下的 Agent 往往各自为政，难以互通协作。在多 Agent 协作的场景下，我们需要一种全新的协议来实现 Agent 之间的无缝对话。这就是 Google 在 2025年4月 发布的 Agent-to-Agent 协议（简称 A2A）。

**A2A和MCP是互补而非互斥关系**

A2A 与 MCP 各有专长，再加上 LLM，它们共同构成了一个完整的智能代理生态系统。正如下图所示，两者的关系可以这样理解：

- LLM：是 Agent 毫无疑问的“大脑”，负责处理信息，推理，做决策。
- MCP：负责模型与工具/资源的连接，是 Agent 的“手”，让 Agent 能够获取信息和执行操作。
- A2A：负责 Agent 之间的通信，是 Agent 的“嘴”，让 Agent 能够相互交流、协作完成任务。

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/73d76434f9f324846aed5c35449f746c.png)

“Local Agents”（本地智能体）是在主智能体生态系统内工作的较小的子智能体。

**A2A的5大核心设计原则**

A2A 协议设计有5个核心设计原则。

![图片](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/192367eb31ce092fc53e8d1552476d1e.jpg)

第一是拥抱 Agent 能力：Agent 无需共享内部思考、计划或工具，因此 Agent 相互之间成为黑盒，无需向对方暴露任何不想暴露的隐私。

第二是基于现有标准：在 HTTP、Server-Sent Events、JSON-RPC 等成熟技术之上构建，确保与现有 IT 架构无缝集成。

第三是企业级安全：A2A 内置与 OpenAPI 同级别的认证与授权机制，满足企业级安全与合规需求。

第四是长任务支持：除了即时调用，还可管理需人机环节介入、耗时数小时甚至数天的深度研究任务，并实时反馈状态与结果。

第五是多模态无差别：不仅限于文本，还原生支持音频、视频、富表单、嵌入式 iframe 等多种交互形式。

**A2A协议的角色**

我们接下来来看一下协议中定义的三个关键角色，看看它们如何各司其职、协同配合，共同支撑多 Agent 生态的运行。

如下图所示，A2A协议定义了三个角色。

1. 用户（User）：最终用户（人类或服务），使用Agent系统完成任务。

2. 客户端（Client）：代表用户向远程Agent请求行动的实体。

3. 远程Agent（Remote Agent）：作为A2A服务器的“黑盒”Agent。

![图片](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/79a01b084bfda6bdab450f87bd922ac0.png)

**A2A协议的核心对象**

A2A 协议设计了一套完整的对象体系，包括 Agent Card、Task、Artifact 和Message。它们用于实现不同 Agent 之间的高效协作，这些核心对象相互配合，共同构成了 A2A 的通信框架。

1、Agent Card（Agent名片）

每个支持 A2A 的远程 Agent 需要发布一个 JSON 格式的 “Agent Card”，描述该 Agent 的能力和认证机制。Client 可以通过这些信息选择最适合的 Agent 来完成任务。

我们来看看一个典型的 Agent Card 长什么样：

```json
{
  "name": "Google Maps Agent",
  "description": "Plan routes, remember places, and generate directions",
  "url": "https://maps-agent.google.com",
  "provider": {
    "organization": "Google",
    "url": "https://google.com"
  },
  "version": "1.0.0",
  "authentication": {
    "schemes": "OAuth2"
  },
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain", "application/html"],
  "capabilities": {
    "streaming": true,
    "pushNotifications": false
  },
  "skills": [
    {
      "id": "route-planner",
      "name": "Route planning",
      "description": "Helps plan routing between two locations",
      "tags": ["maps", "routing", "navigation"],
      "examples": [
        "plan my route from Sunnyvale to Mountain View",
        "what's the commute time from Sunnyvale to San Francisco at 9AM"
      ],
      "outputModes": ["application/html", "video/mp4"]
    }
  ]
}

```

2、Task（任务）

Task 是 Client 和 Remote Agent 之间协作的核心概念。一个 Task 代表一个需要完成的任务，包含状态、历史记录和结果。

Task 的具体状态列表如下：

- submitted（已提交）

- working（处理中）

- input-required（需要额外输入）

- completed（已完成）

- canceled（已取消）

- failed（失败）

- unknown（未知）

3、Artifact（成果）

Artifact 是 Remote Agent 生成的任务结果。Artifact 可以有多个部分（parts），可以是文本、图像等。

4、Message（消息）

Message 用于 Client 和 Remote Agent 之间的通信，可以包含指令、状态更新等内容。一个 Message 可以包含多个 parts，用于传递不同类型的内容。

**A2A协议工作流程**

A2A协议的典型工作流程如下：

1. 能力发现：每个 Agent 通过一个 JSON 格式的 “Agent Card” 公布自己能执行的能力（如检索文档、调度会议等）。
2. 任务管理：Agent 间围绕一个 “task” 对象展开协作。该对象有生命周期、状态更新和最终产物（artifact），支持即时完成与长跑任务两种模式。
3. 消息协作：双方可互发消息，携带上下文、用户指令或中间产物；消息中包含若干 “parts”，每个 part 都指明内容类型，便于双方就 UI 呈现形式（如图片、表单、视频）进行协商。
4. 状态同步：通过 SSE 等机制，Client Agent 与 Remote Agent 保持实时状态同步，确保用户看到最新的进度和结果。

以“招聘候选人搜寻”这个应用场景为例：

- 用户在统一界面下向自己的 Agent 发起“寻找 XX 岗位候选人”请求。

- Client Agent 根据岗位需求调用简历检索 Agent、技能筛选 Agent 等多个 Remote Agent。

- 各 Agent 协同返回候选人名单（artifact），并由 Client Agent 汇总、展示。

- 后续可继续调用“面试安排 Agent”“背景调查 Agent”，形成端到端招聘流程自动化。


![图片](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/aaecc9ee987f8b1840d5948d733f6434.jpg)

**A2A的生态与未来**

目前，Google Cloud 已联手 50 多家技术与服务伙伴（包括 Atlassian、Salesforce、MongoDB、Accenture、Deloitte 等），共建 A2A 生态。未来预计将在开源社区中逐步完善规范，并推出生产级实现，推动异构 Agent 在企业级场景中的深度互操作，助力跨系统、跨组织的智能协作大规模落地。

![图片](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/ecbcca6a677d0c99c07d8098a2352f50.png)

# 快速实战篇 (3讲)

# 03｜协议实战（上）：高德地图 + MiniMax语音开发私域旅游小助手

**私域旅游小助手开发流程**

1. 注册并配置高德地图 MCP 服务：获取城市与景点的推荐接口，实现地点信息检索。

2. 注册并配置 Minimax 语音生成 MCP 服务：将文字转为语音，生成导览音频。

3. 在 Cursor 中完成 MCP 服务的接入与调用配置：包括填写密钥、Model 兼容性设置、Agent 自动运行配置等。

4. 编写 Prompt 驱动 Agent：自动获取西安各类景点介绍，并按类别分条整理。

5. 调用 Minimax 生成语音导览：将生成的景点介绍文本自动转为语音文件。

6. 生成并部署 HTML 页面：利用 Agent 将整理好的文本输出为一个静态网页，并部署到线上。

**使用高德开放平台的地图MCP服务**

1. 我们需要在 [这里](https://lbs.amap.com/) 登录高德开放平台，创建一个应用，并获取相应的key。
2. 我们需要在 [这里](https://console.amap.com/dev/id/select) 注册自己为高德开放平台开发者。
3. 获取高德服务密钥。
4. 在Cursor中配置高德MCP。

**使用MiniMax大模型的语音服务**

1. 注册Minimax开放平台。[https://minimaxi.com](https://minimaxi.com) 是MiniMax境内的官网
2. 登录MiniMax平台后进入 [账户管理](https://platform.minimaxi.com/user-center/basic-information/interface-key)，创建接口密钥。
3. 在 [ModelScope](https://modelscope.cn/mcp/servers/@MiniMax-AI/MiniMax-MCP) 平台部署 Minimax sse。Minimax官方在 [ModelScope 平台](https://modelscope.cn/mcp/servers/@MiniMax-AI/MiniMax-MCP) 提供了在线部署服务。
4. 在Cursor中配置Minimax MCP

**在Cursor中使用MCP服务开发自己的应用**

1. 选择对MCP兼容性好的模型。这里推荐Agent执行能力、对MCP反馈的整合能力都很强的模型：gemini-2.5-pro-exp-03-25。
2. 允许自动流畅执行MCP工具调用

3、获取城市景点的介绍

![图片](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202610122000916.png)

4、按照类别整理景点介绍

![图片](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202610122001509.png)

5、调用Minimax生成语音导览

![图片](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202610122002877.png)

Agent会识别、嵌入成功调用MCP并正确返回的url，自动修改markdown文件。

![图片](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202610122002177.png)

6、网页制作和部署

新建一个文件，叫 “prompt.md”，然后保存下面的内容。

```markdown
Markdown
   #   页面提示词
   ## 网页风格指南
   你是一位国际顶尖的数字景区导览设计师和前端开发专家，擅长将传统景区介绍与现代网页设计完美融合，创造出令人身临其境的视觉体验。请设计高品质景区介绍手机h5网页，将景区信息以生动优雅的方式呈现，让用户在浏览前就能感受到景区魅力。
   **可选设计风格：
   **1. **文化复古风格**
       适合历史文化类景区，使用仿古纸张纹理背景，搭配书法或篆刻风格的标题。色调以米黄、棕色等复古色系为主，点缀传统中国色。排版可参考古籍设计，正文使用简体宋体增强文化氛围。可加入水墨画元素作为分隔符或装饰。文案语调应庄重有文化底蕴，介绍中可穿插诗词或历史典故。
   2. **现代简约风格**
       采用极简设计理念，主色调限制在2-3种，确保视觉统一性。排版注重网格系统，所有元素严格对齐。字体选用无衬线体，增强现代感。景点信息使用卡片式设计，便于用户快速浏览。图标采用线性设计，保持风格一致性。动效应简洁克制，仅用于增强用户体验的关键环节。整体设计追求"少即是多"的理念，让内容成为主角。
   **必要页面组件：**
   1. **景区名称列表**：
     1. 景区名称
     2. 音频开始按钮：点击音频可以直接播放，播放时可以暂停，暂停的音频还可以继续播放
   2. **景区介绍**：
     1. 默认收缩，点击景区名称可弹出详细介绍
   ## 技术规范
   * 资源引用：
     * Tailwind CSS:   `https://lf3-cdn-tos.bytecdntp.com/cdn/expire-1-M/tailwindcss/2.2.19/tailwind.min.css`
     * Font Awesome:   `https://lf6-cdn-tos.bytecdntp.com/cdn/expire-100-M/font-awesome/6.0.0/css/all.min.css`
     * 中文字体:   `https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700&display=swap`
     * Alpine.js:   `https://unpkg.com/alpinejs@3.10.5/dist/cdn.min.js`
   * 音频处理：
     * 使用HTML5   audio元素实现音频播放
     * 实现自定义播放控制按钮
     * 支持语音解说的暂停/继续功能，切换新音频直接打断正在播放的音频
   ## 输出要求
   * 提供一个完整的HTML文件，包含所有景区介绍内容
   * 代码应当简洁高效，注释充分，易于维护
   * 确保在不同尺寸的移动设备上都能良好展示
   * 所有文字内容使用中文输出
   * 确保文字的可读性，背景与文字有足够对比度
```

最后一步，准备好提示词和刚刚的景点介绍内容文件，交给Agent生成HTML页面。

![图片](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202610122004917.png)

**网页效果的呈现**

下面，我们把这个页面上传到youware.com，进行部署和展示。

你可以通过 [这个链接](https://www.youware.com/project/a87n5fcmtr) 来感受一下这个花费2个小时私人定制的旅游助理的效果。

# 04｜协议实战（中）：从0到1，基于MCP快速搭建RAG“医疗健康“指北”

> Demo 代码：https://github.com/huangjia2019/mcp-in-action

我将带你开发一套基于 MCP + FAISS 的 RAG 框架，这个MCP服务将具备端到端的索引、检索和工具提供能力，是一个非常清晰的原型RAG系统。

![图片](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202610131556287.png)

**整体思路**

在我们这个 MCP 服务提供的 RAG 示例中，嵌入（Embedding）服务和检索（Retrieval）都以工具的形式通过 MCP 协议提供给 Client。

整体设计思路如下图所示。

![图片](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202610131600089.png)

其中，服务端（rag-server），将用 MCP 定义两个工具——index\_docs 和 retrieve\_docs，用于实现向量检索。

- index\_docs 把新文档的向量添加到索引，并把文本保存在 \_docs 列表里；
- retrieve\_docs 用查询向量在索引里做最近邻搜索，返回对应的文本片段。

内存中用 FAISS 的 IndexFlatL2(1536) 存储向量索引，维度 1536 与 OpenAI 的嵌入模型 text-embedding-3-small 输出一致。通过 embed\_text 函数异步调用 OpenAI Embeddings API，批量生成文本向量并返回 float32 numpy 数组。

客户端（rag-client） 将通过 StdioServerParameters 启动服务器进程（.venv/bin/python server.py），并用 MCP 的 stdio 通道建立双向通信。 

# 05｜协议实战（下）：通过 A2A，你的智能体不仅能对话还可以协作！

> A2A Demo代码：https://github.com/huangjia2019/a2a-in-action

上节课我们完成了快速搭建MCP RAG服务，这节课我们继续进行协议实战，感受一下A2A的协议用法。

**A2A Demo的设计实现**

从整体架构上看，一个A2A 系统由以下主要组件构成：

- Agent Card: 代理的身份标识和能力声明。

- Skill: 代理可执行的具体能力。

- Task Manager: 处理任务流和状态管理。

- Server: 提供HTTP接口让其他代理/客户端访问。

在具体实现上：

- 每个 Agent 启动时会生成自己的 AgentCard，内含名称、描述、服务 URL 以及所支持的能力和技能等关键信息；
- 启动后，Agent 通过 A2A Server 将自己的 AgentCard 向注册中心登记；
- Host 端则通过注册/发现机制（如调用 demo/ui/utils/agent\_card.py 中的 get\_agent\_card 接口）远程拉取所有 AgentCard，实现能力路由与展示，从而完成代理之间的能力发现与互操作。

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202610141505259.jpg)

# MCP详解篇 (6讲)

# 06

# 07

# 08

# 09

# 10

# 11