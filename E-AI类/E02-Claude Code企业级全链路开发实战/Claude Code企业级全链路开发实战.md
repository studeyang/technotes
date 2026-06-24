# 开篇词｜一个人用 Claude Code 造一个简版 Dify，需要多久？

先回答标题的问题：大概一周左右。

一个人，用 Claude Code，从零开始，搭建一个支持多模型管理、Agent 配置、对话交互、MCP 工具接入的 AI Agent 开发平台，我们叫它 Hify。基于 Spring Boot + Vue 技术栈，采用模块化单体架构，前后端完整，本地可运行。

**角色转变：从“写代码”到“做决策”**

我给 Claude Code 下达的是清晰的小任务：“按照 CLAUDE.md 中的接口规范，实现模型提供商的 CRUD 接口，包含连通性测试功能，异常按错误码区分三种情况。” 它的输出质量发生了质的飞跃，不是因为它变聪明了，而是因为我给它的输入变清晰了。

到这里我才真正体会到：用 Claude Code 做项目，瓶颈从来不在 AI 的能力上，而在你的思考质量上。你想得越清楚，它做得越准确；你越模糊，它越跑偏。

**方法论：不只是写代码，而是拆解问题**

成为架构师之后，你每天做的最多的事不是写代码，而是拆解问题：这个系统的边界在哪、这个需求分几步、每步交给 Claude Code 的输入是什么。拆得好，它一次做对；拆得差，你反复返工。

这门课教的是一套方法论——当你拿到一个复杂系统的需求，如何把它拆解成 Claude Code 能准确执行的任务链，一个人从零交付出来。我管它叫“Claude Code 全链路开发框架”。

这套框架包含两种协作模式：

- 执行模式是你拆清楚了让它做，你验收；
- 咨询模式是你还没拆清楚，先让它帮你梳理“这一步应该考虑什么”，你判断取舍后再让它执行。

框架还包含一系列支撑拆解过程的具体方法论：

- 规范驱动开发（SDD）让 AI 永远在你定义的轨道上，不自由发挥；
- 三问裁剪法帮你拆解产品边界——做什么、不做什么、做到什么程度；
- 三步检查法帮你高效审查 AI 输出——先查意图、再查质量、最后查边界。

这门课我会带你经历 Hify 从无到有的全过程。但在每个环节，我关注的不是“这个功能怎么实现”，而是问题是怎么被拆解的：

- 在动手之前，我是怎么让 Claude Code 帮我梳理 Dify 的功能全景、怎么用三问裁剪法确定 Hify 的边界、怎么让它给架构方案然后我来拍板的？
- 在核心开发阶段，我是怎么把一个大需求拆成 Claude Code 能准确执行的小任务的？拆的粒度怎么定？它跑偏了我怎么拉回来？
- 在基础设施阶段，我怎么用咨询模式让 Claude Code 帮我发现遗漏的组件？
- 在联调和测试阶段，当问题出在模块之间的交互而不是单个模块内部时，我怎么给它足够的上下文让它定位问题？

![img](https://static001.geekbang.org/resource/image/ed/ea/edaae35df1780ca562b474185d5058ea.jpg?wh=1440x2791)

**AI 是放大器，不是发动机**

我自己的实践经历让我确认了一件事：AI 是放大器，不是发动机。你有方向它放大十倍，你没方向它放大的是零。

能一周交付 Hify，不是因为 Claude Code 厉害，是因为动手之前就知道这个系统应该长什么样。哪些模块必须有，哪些功能可以砍，数据模型怎么设计——这些判断来自自身的经验积累，Claude Code 可以帮我们把判断高效地变成代码，但判断本身是我们自己的。

# ==认知篇==

# 01｜你是架构师，Claude Code 是你的工程团队

这门课我们会围绕用 Claude Code 从零构建一个叫 Hify 的 AI Agent 开发平台来展开。但在动手之前，有一个比“怎么做”更重要的问题要先想清楚——产品需求、架构设计、测试回归、部署运维，这些事情谁来做？

你需要想清楚这些事情，然后让 Claude Code 协助你完成。具体执行可能是 Claude Code 完成 90%，你完成 10%。

**为什么同样的工具，你用和别人用差这么多**

第一个要建立的认知是：你想得越清楚，它做得越准确；你越模糊，它越跑偏。瓶颈不在 AI 的能力上，在你的思考质量上。

**你做决策，它做执行**

我现在和 Claude Code 的协作方式，总结下来就一句话：我是架构师，它是我的工程团队。

想想一个架构师每天干什么：

1. 他不写具体的业务代码，但他决定了系统长什么样。
2. 他定方向：做什么、不做什么。
3. 他做取舍：遇到矛盾选 A 还是选 B。
4. 他立标准：代码怎么写、接口怎么定、出了错怎么处理。
5. 他验收成果：团队交付的东西是不是他要的。

工程团队在干什么？在按标准高效执行。

做一个系统，大部分精力花在了：修低级 bug、反复 review、写测试、写文档。AI 把这些接过去之后，我可以把大部分精力集中在架构设计和核心决策上。

那具体怎么分工？我把它分成三层，你可以直接拿来用。

- 第一层，必须你做的。产品边界、架构决策、技术取舍、跨模块一致性。
- 第二层，AI 做你验收的。业务代码、接口开发、前端页面、测试用例、文档。
- 第三层，AI 全权处理的。格式化、样板代码、简单重构、启动脚本、Makefile。

# 02｜规范驱动开发（SDD）：让 AI 永远在轨道上

上一讲我们明确了一个核心认知：你是架构师，Claude Code 是你的工程团队。你负责做决策，它负责执行。

但这里有一个问题：你怎么把你的决策传达给它？

**规范体系的价值**

给 Claude Code 的指令越清晰，输出质量越高。但这里有一个容易被忽略的问题：你给的清晰指令，只在那一次对话里有效。

要保证整个项目几十次、几百次 AI 输出的一致性，你需要的不是一条好指令，是一套规范体系。

这就是 SDD 和“写好 Prompt”的本质区别。写好 Prompt 是一次性的技巧，SDD 是贯穿整个项目生命周期的方法论。

**SDD 的完整工作流**

第一步：定规范（放在项目 CLAUDE.md 里）

第一版粗一点没关系，但一定要有。关键是覆盖 Claude Code 最容易跑偏的地方。根据我做 Hify 的经验，它最容易跑偏的地方有四个：

- 命名风格

```markdown
# 命名规范
实体类大驼峰，不加前缀后缀。例如 Provider、Agent、ChatMessage。
字段小驼峰。例如 apiKey、baseUrl、modelName。
接口路径：/api/v1/{资源复数名}。
```

- 返回格式

```markdown
# 接口规范
所有接口统一返回 Result<T>：{ code, message, data }
列表字段空时返回空数组 []，不返回 null。
分页参数：page（从 1 开始）、pageSize（默认 20）。
```

- 错误码体系

```markdown
# 错误码
四位数字，按模块分段：
1000-1999 通用 | 2000-2999 Provider | 3000-3999 Agent
4000-4999 Chat | 5000-5999 MCP
```

- 设计原则

```markdown
# 设计原则
不引入不必要的设计模式，除非明确要求。
不做过度抽象，一层能解决的不要拆成两层。
不引入技术栈以外的依赖，需要时先确认。
```

那这个规范从哪来？你也可以先让 Claude Code 帮你梳理“这个项目需要定哪些规范”，它帮你想，你来判断取舍。

第二步：AI 按规范执行

第三步：人验证输出

第四步：迭代规范

- 第一周发现的缺口。Claude Code 在处理空列表时返回了 null。前端拿到 null，页面直接白屏

```
列表字段空时返回空数组 []，不返回 null。
字符串字段空时返回空字符串 ""，不返回 null。
```

- 第二周发现的缺口。做 Agent 模块时，Claude Code 改了一个 Provider 的接口签名。

```
修改已有代码前，先理解相关模块的设计意图。
不要为了实现新功能破坏已有模块的接口契约。
```

每次 AI 跑偏，不要只改代码，也要考虑是不是规范没覆盖到？然后补上那条规范。

![img](https://static001.geekbang.org/resource/image/63/e0/639275cbefa67b9360fe12075d4745e0.jpg?wh=1440x720)

**规范的质量标准**

不是所有规范都能约束住 AI。我在 Hify 的开发中踩过一些弯路，总结出三条判断标准。

- 具体，不模糊

```
没用的规范：“代码要简洁。”
有用的规范：“不引入不必要的设计模式（工厂、策略、观察者等），除非明确要求。每个功能用最简单直接的方式实现。”
```

- 有优先级，不贪多

规范不是越多越好。太多了 Claude Code 也处理不过来，因为上下文窗口是有限的，塞了太多规范反而会稀释重要的那几条。

我的原则是：AI 反复跑偏的地方写细，不跑偏的地方不写。

- 带原因，不只是规则

做 Agent 工具列表更新时，我在指令里写了“不要全量删除再全量插入”。Claude Code 第一版还是用了全量删除再插入——它不理解为什么不能这样做。

我补了一句解释：“全量删除再插入会导致并发场景下 Agent 瞬间失去所有工具关联，如果此时有对话正在读取工具列表，会拿到空列表。”

不过，也不是每条规范都需要解释——“实体类不加前缀”不需要解释原因，照做就行。

# ==顶层设计篇==

# 03｜产品定义：动第一行代码之前你该想清楚什么

我们这节课要做的事情就是：在动第一行代码之前，把产品边界、技术选型、运维预期全部想清楚，写进 CLAUDE.md。

**先搞清楚业界标杆在做什么**

做任何项目之前，第一步不是想“我要做什么”，而是看“业界最好的在做什么”，理解这个领域的全貌。

我们的标杆是 Dify，这一步我直接让 Claude Code 帮忙：

```
帮我梳理  Dify（https://dify.ai）这个产品的核心功能模块，按类别分组，每个模块用一两句话说明它做什么。
```

我拿着 AI 给的这个清单和 Dify 的官方文档、GitHub README 对了一遍，修正了几个过时的描述，补上了它遗漏的 MCP 协议支持。

最终梳理出的 Dify 功能全景：

- 模型管理：接入多个 LLM 提供商（OpenAI、Claude、Gemini、本地模型等），统一管理 API Key、模型参数、调用配额。
- 应用创建：用户可以创建不同类型的 AI 应用——聊天助手、Agent、文本生成、工作流。每个应用可以配置模型、提示词、工具。
- 工作流编排：可视化拖拽界面，把多个节点（LLM 调用、条件判断、代码执行、HTTP 请求）串成一个工作流。这是 Dify 的招牌功能。
- RAG / 知识库：上传文档，自动切片、向量化、存储。对话时自动检索相关内容作为上下文。
- 工具集成：内置和自定义工具，Agent 可以在对话中调用。支持 API 工具和 MCP 协议。
- 对话与调试：完整的对话界面，支持流式响应、多轮对话。有调试模式可以看到推理过程。发布与 API：每个应用可以发布为独立页面或 API，供外部系统调用。
- 运营功能：用量统计、日志追踪、成员管理、API Key 管理、多租户隔离。

![img](https://static001.geekbang.org/resource/image/b7/65/b76d2325df3c3b1389c71770a743f965.jpg?wh=1382x376)

看完这个清单，你就理解为什么“做一个简版 Dify”这句话很模糊了。

**从 Dify 到 Hify：功能取舍**

我先让 Claude Code 做一轮初步分析：

```
我要基于 Dify 做一个简化版的 AI Agent 平台，叫 Hify。约束条件：一个人开发，面向团队内部 20-50 人使用，本地部署。请从刚才梳理的功能列表中，帮我判断哪些是必须做的核心功能，哪些可以砍掉，给出每个的理由。
```

然后我就整理出了最终功能清单：

![img](https://static001.geekbang.org/resource/image/36/37/3614e932e56d3ce97675f06447b1b737.jpg?wh=1508x1288)

**技术选型：匹配定位，不追新**

功能范围定了，接下来选技术栈。我同样让 Claude Code 参与：

```
Hify 是一个 AI Agent 开发平台，一个人开发，本地部署，目标 20-50 人使用。帮我对比以下技术方案的优劣：1) Spring Boot + Vue 2) Go + React 3) Python FastAPI + React。重点考虑开发效率、生态成熟度、AI 领域 SDK 支持、运维复杂度。
```

最终技术栈：

- 后端：Spring Boot 3.x + MyBatis-Plus + MySQL 8.x + Redis 7.x。工程化成熟，一个人能快速交付完整系统。
- 前端：Vue 3 + TypeScript + Element Plus。管理后台场景成熟度最高。
- 容器化：Docker + Docker Compose。最稳、最简。

**提前想清楚怎么跑**

这一步我先自己想一遍，然后让 Claude Code 帮我查漏补缺：

```
Hify 是一个 AI Agent 平台，Docker Compose 本地部署，目标 20-50 人同时在线，主要压力在对话接口（流式 SSE）。帮我估算 QPS、建议缓存策略、列出需要提前考虑的运维事项。
```

Claude Code 给的分析很实在。几个关键结论：

1. QPS 极低，瓶颈不是并发。50 人在线，活跃率 60%，每人每分钟 2 条消息，峰值也就 1 QPS，加上 RAG 检索等内部调用放大 3 倍，也就 3-5QPS。Spring Boot 单实例轻松应对。真正的瓶颈是 LLM 响应延迟（3-30 秒 / 次）占用连接——这不是 QPS 问题，是长连接管理问题。
2. SSE 长连接是唯一需要认真对待的压力点。50 个并发 SSE 连接，每个持续 10-30 秒，意味着 50 个线程被长期占用。Spring Boot 默认 200 线程够用，但要注意：用 SseEmitter 不要用普通 ResponseBody 阻塞线程，设 60 秒超时防止僵尸连接，Nginx 反向代理缓冲（proxy_buffering off）否则流式数据会被攒批再发。这几个坑我自己没全想到，尤其是 Nginx 缓冲那个——不关的话用户看不到打字机效果，要等 LLM 全部输出完才一次性吐出来。
3. 缓存策略简单直接。模型提供商配置和 Agent 配置变更频率极低，用 Redis 缓存。LLM 响应不要缓存——同一问题不同时间答案可能不同。对话历史直接读数据库，50 人规模数据量小，缓存收益不大。
4. 数据持久化是硬性要求。MySQL 数据目录、向量数据库数据目录、上传的文档文件——必须挂载 volume，容器内不存储任何数据。这条看起来是常识，但真有人忘了挂载，容器一重启数据全没了。

最终的运维预期：

- 部署方式：Docker Compose 一键启动。JVM 内存设上限（-Xmx512m），防止容器被 OOM Kill。
- 用户量：20-50 人同时在线，单机部署够用。
- QPS：峰值 3-5QPS，瓶颈在 LLM 长连接不在并发。
- 监控：起步用 Spring Boot Actuator + 日志，后期接 Prometheus + Grafana。
- 扩容：一期单机。架构上不堵死扩容的路——第  04 讲会做模块化设计，为后续拆分留口子。

**写进  CLAUDE.md**

这一步也让 Claude Code 帮忙：

```
根据我们的讨论，帮我把 Hify 的项目概述写进 CLAUDE.md 的“项目概述”部分。包括产品定位、做什么、不做什么、技术栈、部署与运维预期。格式简洁明了。
```

它生成了一版初稿，我检查修改后定稿：

```markdown
## 项目概述

Hify 是一个简版的 AI Agent 开发平台（参考 Dify），可本地部署，
面向团队内部小规模使用（20-50 人同时在线）。

### 做什么
- 多模型提供商管理（OpenAI、Claude、Gemini、Ollama）
- Agent 创建与配置（选模型、绑工具、设系统提示词）
- 对话引擎（流式响应、多轮对话、上下文管理）
- 知识库 + RAG（一期只支持 TXT 文档，固定长度分块）
- 简版工作流（JSON 配置，线性 + 条件分支，不做可视化拖拽）
- MCP 工具接入（Agent 可通过 MCP 协议调用外部工具）
- 管理控制台（模型管理、Agent 配置、对话界面）

### 不做什么
- 不做可视化工作流拖拽编排
- 不做多租户 / 权限体系
- 不做插件市场、计费系统
- 不做文本生成应用、WebApp 发布、嵌入组件
- 不做标注与微调

### 技术栈
后端：Spring Boot 3.x + MyBatis-Plus + MySQL 8.x + Redis 7.x
前端：Vue 3 + TypeScript + Vite + Element Plus
容器化：Docker + Docker Compose

### 部署与运维预期
- Docker Compose 本地一键部署，JVM 内存设上限（-Xmx512m）
- 目标：20-50 人同时在线，峰值 3-5 QPS，瓶颈在 LLM 长连接
- 缓存：Redis Cache-Aside（配置信息 + 会话上下文）
- 监控：起步 Actuator + 日志，后期 Prometheus + Grafana
```

# 04｜架构设计（上）：应用架构与代码组织

这一讲和下一讲合起来是 Hify 的完整架构设计。这一讲（上篇）聚焦代码层面——模块怎么分、Spring 代码怎么组织、外部调用怎么处理。下一讲（下篇）聚焦系统层面——怎么部署、瓶颈在哪、未来怎么扩展、数据怎么存。

**应用架构：模块化单体**

第一个问题：一个 Spring Boot 应用，内部怎么组织？

```
hify/
├── hify-app/               # 启动模块，Spring Boot Application
├── hify-provider/           # 模型提供商管理
├── hify-agent/              # Agent 管理与配置
├── hify-chat/               # 对话引擎
├── hify-mcp/                # MCP 工具管理与调用
├── hify-workflow/           # 工作流编排与执行
├── hify-knowledge/          # 知识库与 RAG
├── hify-common/             # 公共模块（工具类、常量、异常、DTO）
├── hify-web/                # Vue 前端
└── deploy/                  # Docker Compose 配置
```

模块之间的依赖关系需要想清楚。Claude Code 给出分析：

- hify-chat 是依赖最多的模块——对话时要读 Agent 配置（依赖 hify-agent）、调模型（依赖 hify-provider）、可能走工作流（依赖 hify-workflow）、可能做 RAG 检索（依赖 hify-knowledge）、可能调工具（依赖 hify-mcp）
- hify-agent 依赖 hify-mcp（Agent 要绑工具）和 hify-knowledge（Agent 要绑知识库）
- 所有模块依赖 hify-common

关键原则：依赖是单向的，不能循环。 hify-chat 可以依赖 hify-agent，但 hify-agent 不能反过来依赖 hify-chat。如果出现循环依赖，说明模块边界划错了，需要把共用的部分下沉到 hify-common。

![img](https://static001.geekbang.org/resource/image/b9/yy/b9a900cc1131d947324f3f0a2bc4e7yy.jpg?wh=1432x1082)

**Spring 代码组织规范**

我让 Claude Code 帮我梳理：

```
Hify 是模块化单体，用 Spring Boot + MyBatis-Plus。帮我定义代码组织规范，覆盖：每个模块内部的分层结构、每一层的职责边界、跨模块调用的规则。要求具体到 AI 能直接执行，不要模糊的描述。
```

它给了一版，我调整后定稿，每个业务模块内部统一结构：

```
src/main/java/com/hify/{module}/
├── controller/        # REST 接口
├── service/           # 业务逻辑接口
├── service/impl/      # 业务逻辑实现
├── mapper/            # MyBatis-Plus Mapper
├── entity/            # 数据库实体
├── dto/               # 请求/响应对象
├── config/            # 配置类
├── exception/         # 模块级自定义异常
└── constant/          # 模块级常量
```

每一层的职责边界：

- Controller 只做两件事：参数校验和调用 Service。为什么要这么严格？因为 Claude Code 特别喜欢在 Controller 里“顺手”加逻辑，它觉得方便，但你后面测试、重构、拆分全部受影响。
- Service 处理所有业务逻辑，包括事务管理、数据校验、业务规则。Service 之间可以互相调用，但只能调接口（interface），不能直接 new 实现类。
- Mapper 只做数据库操作。不要在 Mapper 的 XML 里写业务逻辑（比如复杂的条件判断），那是 Service 的事。
- Entity 和数据库表一一对应。DTO 是给接口用的请求 / 响应对象。Entity 和 DTO 之间要做转换，不要把 Entity 直接返回给前端（Entity 里可能有敏感字段），DTO 可以控制暴露哪些字段。

跨模块调用规则：这条是模块化单体最关键的规范。模块之间只能通过 Service 接口调用，不能直接引用另一个模块的 Mapper、Entity 或内部类。

为什么？因为我们选模块化单体的一个重要理由是“后续能拆分”。如果有一天要把 hify-chat 拆成独立服务，Service 接口不变，实现类里的本地调用改成 Feign 调用，加上网络异常处理。每个跨模块调用点改两三行代码，改动量可控。

**外部调用设计**

Hify 最大的技术挑战不在 CRUD，在外部 LLM 调用。LLM API 调用有三个特点：慢（一次对话 3-30 秒）、不稳定（随时可能超时、限流、报错）、多供应商（每家行为不一样）。

我让 Claude Code 系统性地分析：

```
Hify 要调用多个外部 LLM API（OpenAI、Claude、Gemini、Ollama），这些调用慢且不稳定。从线程管理、容错、超时、重试四个维度，给出完整的技术方案。
```

它给的方案很全面，我逐个判断：

1、线程池隔离——同意。LLM 调用必须用独立线程池，不能和 Tomcat 的业务线程池共用。

> 第 03 讲分析过：50 个并发 SSE 连接，每个持续 10-30 秒，如果共用线程池，管理页面的请求排在队列里等，用户看到的就是页面一直转圈。独立线程池解决这个问题——对话请求用自己的池子，管理请求用 Tomcat 默认的池子，互不影响。

2、熔断机制——同意。某个 LLM 提供商连续失败时，快速熔断，后续请求直接返回错误，不浪费时间等超时。Claude Code 建议 Resilience4j，每个提供商独立熔断器——OpenAI 挂了不影响 Claude。

3、超时控制——同意，但我追问了细节。它建议对话接口 60 秒超时，连通性测试 10 秒。我追问：流式响应场景下，一个 SSE 连接可能持续一两分钟，60 秒会不会把正常对话切断？它调整了：SSE 连接超时设 120 秒，普通同步调用 60 秒。

4、重试策略——同意，细节有价值。不是所有失败都值得重试。网络抖动重试有意义，认证失败重试没用（重试一百次还是认证失败），限流需要退避重试（等一等再试）。按异常类型区分重试策略，这个细节 Claude Code 给得很好。

![img](https://static001.geekbang.org/resource/image/2f/fa/2fe40123318d21b0ffecf53d8eda11fa.jpg?wh=1440x790)

**写进 CLAUDE.md**

这一讲的所有决策写进 CLAUDE.md：

```markdown
## 架构设计

### 应用架构
模块化单体。一个 Spring Boot 应用，Maven 多模块组织。

模块划分：
- hify-provider：模型提供商管理
- hify-agent：Agent 管理与配置
- hify-chat：对话引擎
- hify-mcp：MCP 工具管理与调用
- hify-workflow：工作流编排与执行
- hify-knowledge：知识库与 RAG
- hify-common：公共模块

依赖原则：单向依赖，不循环。共用逻辑下沉 hify-common。

### 代码组织
每个业务模块统一结构：controller / service / mapper / entity / dto / config

分层规则：
- Controller 只做参数校验和调用 Service，不写业务逻辑
- Service 处理所有业务逻辑，包括事务管理
- 跨模块调用走 Service 接口，不直接引用其他模块的 Mapper 或 Entity
- Entity 不直接返回给前端，用 DTO 做转换

### 外部调用处理
- LLM 调用使用独立线程池，和业务请求隔离
- Resilience4j 熔断，每个提供商独立熔断器
- 同步调用 60s 超时，SSE 流式 120s 超时，连通性测试 10s
- 按异常类型区分重试：网络抖动重试、认证失败不重试、限流退避重试
- 流式响应使用 SseEmitter + 独立线程池，不引入 WebFlux
```

# 05｜架构设计（下）：部署架构、性能预判与数据设计

部署架构从第一天就在影响你的设计决策——缓存放哪、数据库怎么连、服务之间怎么通信，全都取决于你的部署形态。提前想清楚，后面不返工。

## 部署架构

**当前部署架构：50 人规模**

先把当前的部署全貌画出来。我让 Claude Code 帮我梳理：

```
Hify 是模块化单体，技术栈 Spring Boot + Vue + MySQL + Redis + pgvector。目标 50 人内部使用，生产环境用 Docker + K8s 部署。帮我设计当前阶段的部署架构：有哪些组件、请求怎么流转、每个组件的职责是什么。
```

Claude Code 回答是标准的单体  + 三个有状态服务的组合。用户请求经 Nginx 分流，静态资源直接返回，API 请求转发给 Spring Boot，Spring Boot 按需读写 MySQL（业务数据）、Redis（缓存会话）、pgvector（向量检索）。

![img](https://static001.geekbang.org/resource/image/4d/eb/4d317a56e50a08ce0c361a5ffa4350eb.jpg?wh=1440x890)

各组件职责：

![img](https://static001.geekbang.org/resource/image/91/05/9129efa8a7dd1c39086a8eeccb01ab05.png?wh=1412x538)

Claude Code 还给了一个很有价值的对比——当前阶段该做什么、暂时跳过什么：

![img](https://static001.geekbang.org/resource/image/a3/62/a303ac352071cb2481cf25958df8d762.png?wh=1580x454)

**性能瓶颈预判**

你作为架构师，应该在设计阶段就知道瓶颈可能在哪。即使一期不处理，也要做到心里有数。

这一步特别适合让 Claude Code 帮你分析：

```
基于 Hify 当前的部署架构（Nginx + Spring Boot + MySQL + Redis + pgvector +  外部 LLM API），帮我分析：这个系统的性能瓶颈可能在哪？按严重程度排序，每个瓶颈给出触发条件和一期是否需要处理。
```

它按严重程度排了序：

![img](https://static001.geekbang.org/resource/image/d9/yy/d9d81c19b9dbd1fbd20c0713e3a700yy.png?wh=1922x618)

**扩展架构：几千人规模**

一期 50 人，但如果 Hify 做得好，可能要推广到更大范围。我让 Claude Code 设计演进路径：

```
如果 Hify 要从 50 人扩展到几千人，当前架构需要怎么演进？帮我设计一个分阶段的扩展路径，每一步的触发条件是什么、改什么、不改什么。
```

Claude Code 给了三个阶段：

- 第一阶段：50 → 500 人

触发条件：响应变慢，docker stats 显示 CPU / 内存持续告警。

改什么：Spring Boot 从 1 副本扩到 2-3 副本；MySQL 加读写分离（一主一从）；静态资源上 CDN。

不改什么：整体单体架构不动，pgvector 不换，Redis 单节点不动。

难点：Spring Boot 多副本要处理 SSE 的连接粘连——用户的流式对话不能被负载均衡随机分发到不同实例。解决方案是用 Redis 做会话共享。

- 第二阶段：500 → 2000 人

触发条件：LLM 调用队列堆积，对话成功率下降；知识库检索 P99 > 2s。

改什么：引入消息队列（RocketMQ/Kafka）做 LLM 异步调用削峰；pgvector 迁移到独立 Qdrant；MySQL 按业务模块分库。

不改什么：Spring Boot 仍是单体不做微服务拆分，Redis 架构不动。

难点：LLM 异步化后，前端要从 SSE 改成轮询或 WebSocket，是 breaking change。这个改动成本不低，所以不到触发条件不做。

- 第三阶段：2000 → 几千人

触发条件：单个模块的发布频率互相干扰；某一模块（如 Agent 执行）资源消耗远超其他模块。

改什么：按模块拆微服务（Agent 执行、知识库、对话历史各自独立）；引入 API Gateway 替代 Nginx 路由；Redis 换集群模式。

不改什么：MySQL 主从架构不动，Qdrant 不动，K8s 编排层不动。

难点：微服务拆分带来分布式事务问题，需要引入 Saga 或 TCC 模式。第 04 讲定的“跨模块走 Service 接口”在这里发挥作用——拆分时只改调用方式，接口签名不变。

三个阶段的对比总览：

![img](https://static001.geekbang.org/resource/image/3d/6e/3dfd0fe6f11242e837ab3464b2788c6e.png?wh=1442x704)

## 数据模型概览

核心表有哪些、关系怎么样，先列出来。具体字段设计等后面每个模块开发时再定，现在定太细了后面一定会改。

```
基于 Hify 的功能范围（模型管理、Agent、对话、工作流、知识库、MCP 工具），帮我梳理核心数据表和它们之间的关系。只要表名和关系，不展开字段。
```

Claude Code 给了一份完整的梳理：

- 模型管理：model_provider（提供商）→ model（具体模型），一对多。一个 OpenAI 下有 GPT-4o、GPT-3.5 多个模型。
- 知识库：knowledge_base → document → document_chunk，一对多链。document_chunk 是向量化的最小单位，存在 pgvector 里。
- 工具：tool，独立表，存 MCP 工具定义。
- Agent：agent 是关联最多的表，agent → model（多对一，选一个模型），agent ↔ knowledge_base（多对多，通过 agent_knowledge_base），agent ↔ tool（多对多，通过 agent_tool）。
- 工作流：workflow → workflow_node，一对多。workflow_node 里的 LLM 节点也关联  model。
- 对话：conversation → message，一对多。conversation 关联 agent 或 workflow（对话绑定的执行对象）。message → document_chunk 多对多（通过 message_reference，做 RAG 溯源——回答引用了哪些知识库片段）。
- 用户：user 和 api_key。user 发起 conversation，api_key 用于 API 发布调用。

总共约 16 张表。看着多，但按功能域分组后每组就两三张，结构清晰。

![img](https://static001.geekbang.org/resource/image/2d/1d/2d69d6919860b321a022ba0a84cb371d.jpg?wh=1440x1105)

有一个设计决策值得说明：message_reference 这张表，它记录的是“这条 AI 回复引用了知识库的哪些片段”。很多人做 RAG 不存这个关系，回复完就丢掉了检索结果。但存下来有两个好处：

一是用户可以看到“AI 的回答依据是什么”，增加可信度；二是后续优化 RAG 效果时，可以回溯分析检索质量。

一张中间表，成本很低，价值不小。

## 数据库规范

```
Hify 用 MySQL 8.x + pgvector。帮我定义数据库层面的性能规范，覆盖：索引设计原则、大表预判和应对策略、分页查询注意事项、通用字段约定。要求具体到 AI 建表时能直接执行。
```

Claude Code 给了一份非常详细的规范，包含了具体的建表示例。

**通用字段约定**

所有表必须包含四个公共字段：

```sql
id          BIGINT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
created_at  DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
updated_at  DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
deleted     TINYINT(1)      NOT NULL DEFAULT 0
```

几条硬规矩：

1. 主键用自增 BIGINT，禁止 UUID（索引性能差）
2. 禁止用 NULL，业务空值用空字符串或 0 代替
3. 金额和 Token 用量用 BIGINT 存最小精度，不用 DECIMAL
4. 枚举字段用 VARCHAR(32)，不用 MySQL ENUM 类型（ENUM 加值要改表结构）

你看，这是不是就是我们进入团队要学习的团队规范。

**索引设计原则**

Claude Code 给了五条具体规则，每条带示例。

第一，逻辑删除字段必须加进索引。几乎所有查询都带 deleted = 0，不加进索引等于索引白建。

```
-- ✅ 正确
INDEX idx_agent_user (user_id, deleted)
-- ❌ 不够
INDEX idx_agent_user (user_id)
```

第二，组合索引等值列在前，范围列在后。这是 MySQL 索引的基本原则，但不提醒 Claude Code，它自己写查询时经常不遵守。

```
INDEX idx_message_conv_time (conversation_id, created_at)
```

第三，多对多关联表两个方向都要索引。agent_tool 表按 agent_id 查和按 tool_id 查都是高频操作，只建一个方向的索引，另一个方向就全表扫描。

```
PRIMARY KEY (agent_id, knowledge_base_id),
INDEX idx_kb_agent (knowledge_base_id)    -- 反向查询索引
```

第四，唯一约束用 UNIQUE INDEX，不要只在代码层校验。并发场景下代码校验有竞态问题，数据库约束才是最后防线。

第五，禁止在大文本字段建索引。content、prompt 这类 TEXT 字段不能建索引，需要全文搜索的场景后续引入 ES。

**大表预判**

Hify 中增长最快的两张表：

message 表：每次对话产生 2-N 条记录，50 人每天几百到上千条。

应对：建好时间范围索引（conversation_id + created_at），预留按时间归档的能力。一期建好索引够用半年。

document_chunk 表：知识库分块数据，100 篇文档可能产生 5000+ 行。

应对：向量数据存 pgvector，MySQL 只存元数据和 vector_id（指向 pgvector 的记录），不在 MySQL 里存向量本身。

其他表（provider、agent、workflow）都是配置数据，增长慢，不需要特别关注。

**分页查询规范**

```
-- ❌ 禁止 OFFSET 深分页，百万行时极慢
SELECT * FROM message ORDER BY id DESC LIMIT 20 OFFSET 100000;

-- ✅ 用游标分页
SELECT * FROM message
WHERE conversation_id = ?
  AND id < #{lastId}
  AND deleted = 0
ORDER BY id DESC
LIMIT 20;
```

规范先定好，Claude Code 知道用游标分页，后面数据量上来了不用改代码。

还有一条：COUNT 查询单独处理，列表页只在第一页返回 total，翻页不重复查。这个细节对大表的查询性能影响很大。

**pgvector 规范**

向量数据单独存 PostgreSQL，和 MySQL 业务数据分离：

```sql
CREATE TABLE vector_chunk (
    id          BIGSERIAL PRIMARY KEY,
    chunk_id    BIGINT       NOT NULL,    -- 对应 MySQL document_chunk.id
    embedding   vector(1536) NOT NULL,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- 必须建 HNSW 索引，否则全表扫描
CREATE INDEX idx_embedding_hnsw
ON vector_chunk
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

两条硬规矩：

- 必须建 HNSW 索引（一期数据量小感知不到差异，但数据量上来后，没索引检索会从毫秒级变成秒级）。
- 检索时必须加 LIMIT，禁止不加 LIMIT 的向量查询（全量排序会拖垮数据库）。

问了问题，辨别答案，学习答案——这才是把 AI 融入工作的核心思路。

## 写进 CLAUDE.md

这一讲的所有决策写进 CLAUDE.md：

```markdown
### 部署架构
生产环境：Docker + K8s
- 前端：Nginx 托管静态文件 + API 反向代理（proxy_buffering off）
- 后端：Spring Boot，K8s Deployment（一期单副本）
- 数据库：MySQL 8.x（外部服务）
- 缓存：Redis 7.x（外部服务）
- 向量库：PostgreSQL + pgvector（外部服务）
- 本地开发：java -jar + npm run dev，start.sh 一键启动

### 缓存策略
- Provider/Agent 配置：Redis Cache-Aside，TTL 30min
- 对话上下文：Redis，TTL 2h
- 对话消息、知识库文档：不缓存，走数据库
- LLM 响应：不缓存

### 数据库规范
通用字段：
- 主键 id BIGINT 自增，禁止 UUID
- 时间字段 created_at / updated_at，DATETIME(3)
- 逻辑删除 deleted TINYINT(1)
- 禁止 NULL，空值用空字符串或 0
- 枚举用 VARCHAR(32)，不用 MySQL ENUM

索引规则：
- 命名 idx_{表名}_{字段名}
- 逻辑删除字段必须加进组合索引
- 组合索引等值列在前，范围列在后
- 多对多关联表两个方向都要索引
- 唯一约束用 UNIQUE INDEX，不只在代码层校验
- 禁止在 TEXT/BLOB 字段建索引
- 不建数据库级外键约束，应用层维护

分页规则：
- 默认用游标分页（WHERE id < lastId ORDER BY id DESC LIMIT N）
- OFFSET 分页限制最大 10000 条
- COUNT 只在第一页查，翻页不重复查

大表预判：
- message：增长最快，必须建 (conversation_id, created_at) 索引
- document_chunk：MySQL 只存元数据，向量存 pgvector

pgvector 规范：
- 向量表建在 PostgreSQL，维度固定 1536
- 必须建 HNSW 索引
- 检索必须加 LIMIT，禁止全量排序

### 扩展路径
一期单副本 → 多副本 + 主从分离（500人）
→ MQ 异步 + Qdrant（2000人）→ 微服务拆分 + Redis 集群（几千人）
触发条件驱动，条件不到不动。
```

# 06｜Claude Code 实战必备：CLAUDE.md、Skills 与工程规范

这节课我们会从最基础的 CLAUDE.md 开始讲起，里面放一些基础的规范。然后在后续的课程中融入 Skill，让你体验到各个维度工具的优势。

**CLAUDE.md：你和 AI 的合作协议**

它的结构怎么组织？ 前三讲我们已经实践了从宏观到微观的五层：

1. 项目上下文：这是什么项目，做什么不做什么（第 03 讲）
2. 架构规范：模块划分、依赖关系、外部调用处理（第 04 讲）
3. 代码组织规范：分层结构、Controller/Service/Mapper 职责（第 04 讲）
4. 部署与数据库规范：部署架构、索引规则、分页规范、pgvector（第 05 讲）
5. 接口规范与行为指令：这一讲补完

接口规范

```markdown
## 接口规范

### 路径
RESTful 风格：/api/v1/{资源复数名}
GET    /api/v1/providers          # 列表（分页）
POST   /api/v1/providers          # 创建
GET    /api/v1/providers/{id}     # 详情
PUT    /api/v1/providers/{id}     # 更新
DELETE /api/v1/providers/{id}     # 删除
POST   /api/v1/providers/{id}/test-connection  # 非 CRUD 操作用动词

### 统一响应
所有接口返回 Result<T>：
{ "code": 200, "message": "success", "data": {...} }

### 分页
请求：page（从 1 开始）、pageSize（默认 20，最大 100）
响应：Result<PageResult<T>>，PageResult 包含 list、total、page、pageSize

### 空值
- 列表字段空时返回 []，不返回 null
- 字符串字段空时返回 ""，不返回 null
- 对象不存在时返回 null

### 错误码
四位数字，按模块分段：
1000-1999 通用 | 2000-2999 Provider | 3000-3999 Agent
4000-4999 Chat | 5000-5999 MCP | 6000-6999 Workflow | 7000-7999 Knowledge
```

行为指令

```markdown
## 行为指令

### 写代码时
- 每个功能用最简单直接的方式实现
- 不引入不必要的设计模式，除非我明确要求
- 不做过度抽象
- 不引入技术栈以外的依赖，需要时先问我
- 所有外部调用必须有超时设置
- 配置项外化到 application.yml，不硬编码

### 改代码时
- 先理解相关模块的设计意图
- 不要为了新功能破坏已有接口契约
- 改完确保已有测试通过

### 不确定时
- 架构选择给我 2-3 个方案对比，我来拍板
- 规范没覆盖的情况，先问我，不要自己编规矩
```

接口契约：模块级的蓝图

```markdown
# Provider 模块接口契约

GET /api/v1/providers
  描述：分页查询提供商列表
  参数：page, pageSize, name(可选，模糊搜索)
  响应：Result<PageResult<ProviderListResp>>

POST /api/v1/providers
  描述：创建提供商
  请求体：ProviderCreateReq { name, type, apiKey, baseUrl }
  响应：Result<Long>

DELETE /api/v1/providers/{id}
  描述：删除提供商（需检查是否有 Agent 在使用）
  响应：Result<Void>

POST /api/v1/providers/{id}/test-connection
  描述：测试连通性
  响应：Result<ConnectionTestResp> { success, latencyMs, errorCode, errorMessage }
```

**Skills：可复用的规范片段**

后面每个模块开发前都要写接口契约，我把这个过程标准化成一个 Skill：

```markdown
# 接口契约设计 Skill

## 触发条件
当需要为一个新模块设计接口契约时使用。

## 步骤
1. 列出这个模块的核心业务操作（创建、查询、更新、删除、特殊操作）
2. 每个操作定义：HTTP 方法 + 路径 + 入参 + 出参
3. 路径遵循 /api/v1/{资源复数名} 格式
4. 所有接口返回 Result<T>
5. 列表接口支持分页（page, pageSize）
6. 删除接口标注是否需要关联检查
7. 非 CRUD 操作用动词路径（如 /test-connection）
```

创建了这个 Skill 之后，下次你说“帮我设计 Agent 模块的接口契约”，Claude Code 会自动按这个标准流程走，不需要你每次重复描述格式要求。

**用业界规范喂 Claude Code**

比如 Java 编码规范。阿里巴巴 Java 开发手册、Google Java Style Guide 都是业界公认的标准。你不需要自己读完几十页再手写，让 Claude Code 消化后帮你提炼：

```
我在做一个 Spring Boot 项目，请基于阿里巴巴 Java 开发手册，帮我提炼出最关键的 20 条编码规范，写成 CLAUDE.md 可以直接用的格式。重点覆盖命名、异常处理、日志、并发这几个方面。不要照搬原文，要精简到  AI  能直接执行。
```

同样的思路适用于数据库规范：

```
基于业界 MySQL 设计规范（阿里巴巴 MySQL 规范、互联网公司常见的 MySQL 最佳实践），帮我补充 Hify 项目的数据库规范。当前已有的规范是：[贴上 05 讲写的数据库规范]。帮我看看还有哪些重要的规范遗漏了。
```

这个技巧的本质是：你不需要是每个领域的专家，但你可以让 Claude Code 帮你把专家的经验转化成你项目的规范。

**让 Claude Code 帮你生成完整 CLAUDE.md**

```
我在做一个叫 Hify 的项目，以下是前期做的所有决策：[贴上 03-05 讲写进 CLAUDE.md 的所有片段]。另外请基于阿里巴巴 Java 开发手册，补充编码规范部分。请帮我合并生成一份完整的 CLAUDE.md。要求：结构清晰，从项目概述到行为指令，规范要具体到 AI 能直接执行。
```

