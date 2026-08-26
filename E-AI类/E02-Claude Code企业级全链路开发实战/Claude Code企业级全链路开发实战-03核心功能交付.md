# ==核心功能交付：基础篇==

# 13｜模型提供商管理：第一个完整功能的交付闭环

 第一个模块是模型提供商管理，让用户配置 OpenAI、Claude、Gemini、Ollama 这些 LLM 提供商，管理 API Key，查看支持的模型，监控健康状态。

我会分四个部分展开：先想清楚、后端拆解执行、前端对接、完整验收。

## 先想清楚

### 1、支持哪些供应商？

你可以问 Claude Code：

```
Hify 要支持 LLM 模型提供商管理。帮我分析：主流的 LLM 供应商有哪些？它们的 API 有什么共性和差异？哪些是一期必须支持的？
```

Claude Code 给了一份非常详细的分析。

按接口兼容性分：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061747904.png)

按认证方式分：Bearer Token（OpenAI、DeepSeek）、自定义 Header（Anthropic 用 x-api-key）、URL 参数（Gemini）、无认证（Ollama）、JWT 自签名（智谱 GLM）。由于这个差异，auth_config 我们决定使用 JSON 存储。

按消息格式分：OpenAI 格式（大多数）、Anthropic 独立 system 字段、Gemini 完全不同格式（contents + parts）。这个差异决定了后面适配层要怎么设计。

基于这个分析，我的判断，一期支持三种类型加一个通用兼容：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061747371.png)

Gemini 消息格式差异最大，适配成本高，放二期。

### 2、有没有现成的依赖库？

```
Java 生态里有没有封装了多 LLM 供应商调用的库？Spring AI、LangChain4j 等，分析成熟度和优缺点。
```

Spring AI 和我们技术栈最匹配，但 API 还在快速迭代，LangChain4j 功能全但概念太重。

我的判断：一期不引入这些框架，基于 10 讲封装的 LlmHttpClient 自己做。大部分供应商兼容 OpenAI 格式，自己封装工作量不大。引入大框架只为用模型调用部分，性价比不高。

### 3、数据模型设计

```
基于上面的分析，设计 Provider 模块的数据模型。需要考虑：多种供应商鉴权方式的差异怎么统一存储、一个供应商下有多个模型怎么管理、供应商健康状态怎么表示。
```

Claude Code 给了一版很扎实的设计。

**鉴权信息怎么存？**

不同供应商的鉴权差异很大。OpenAI 用 API Key，Anthropic 额外需要 anthropicVersion Header，Azure 需要 resourceName 和 apiVersion，Ollama 完全不需要认证。给每种方式定固定列行不通。

用 auth_config JSON 字段，按 type 存不同结构：

```json
// OPENAI / OPENAI_COMPATIBLE
{ "apiKey": "sk-xxx" }

// ANTHROPIC
{ "apiKey": "sk-ant-xxx", "anthropicVersion": "2023-06-01" }

// OLLAMA
{}
```

**模型列表怎么管理？**

model_config 表有两个容易混淆的字段：name 是展示名（比如 GPT-4o），model_id 是调用时实际传给 API 的值（比如 gpt-4o）。

另外加了 context_size 字段存上下文窗口大小，后面对话引擎做上下文管理时直接用，不需要再去查。enabled 字段让用户选择启用哪些模型开放给  Agent。

**健康状态为什么独立成表？ **

这是 Claude Code 给的一个我没想到的好设计。

健康状态写频繁——定时探测每分钟更新一次，每次 LLM 调用也可能更新状态。如果放在 provider 表里，高频写操作会和业务读竞争锁。分离之后，provider 表写少读多，可以放心加 @Cacheable 缓存；provider_health 表不缓存，直接读库。

而且 provider_health 表的字段比简单的 status 丰富得多：fail_count（连续失败次数，配合熔断器）、latency_ms（最近延迟）、last_success_at（最后成功时间）、error_message（最近失败原因）。这些信息在管理控制台展示时非常有用。

最终表结构：

```mysql
-- 模型提供商
CREATE TABLE provider (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '供应商名称，唯一',
    type VARCHAR(30) NOT NULL COMMENT 'OPENAI/ANTHROPIC/OLLAMA/OPENAI_COMPATIBLE',
    base_url VARCHAR(500) NOT NULL COMMENT 'API 基础地址',
    auth_config JSON COMMENT '鉴权配置，结构按 type 不同',
    enabled TINYINT DEFAULT 1 COMMENT '0=禁用 1=启用',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    deleted TINYINT DEFAULT 0
) COMMENT '模型提供商';

-- 模型配置
CREATE TABLE model_config (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    provider_id BIGINT NOT NULL COMMENT '所属供应商 ID',
    name VARCHAR(100) NOT NULL COMMENT '展示名，如 GPT-4o',
    model_id VARCHAR(100) NOT NULL COMMENT '调用时传给 API 的值',
    context_size INT COMMENT '上下文窗口大小（token 数）',
    extra_params JSON COMMENT '模型级别扩展参数',
    enabled TINYINT DEFAULT 1 COMMENT '0=禁用 1=启用',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    deleted TINYINT DEFAULT 0
) COMMENT '模型配置';

-- 供应商健康状态（独立表，高频写不影响 provider 缓存）
CREATE TABLE provider_health (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    provider_id BIGINT NOT NULL COMMENT '供应商 ID，唯一索引',
    status VARCHAR(20) DEFAULT 'UNKNOWN' COMMENT 'UP/DOWN/DEGRADED/UNKNOWN',
    last_check_at DATETIME COMMENT '最后探测时间',
    last_success_at DATETIME COMMENT '最后成功时间',
    fail_count INT DEFAULT 0 COMMENT '连续失败次数',
    latency_ms INT COMMENT '最近一次延迟 ms',
    error_message VARCHAR(500) COMMENT '最近失败原因',
    updated_at DATETIME NOT NULL,
    UNIQUE INDEX idx_provider_health_provider_id (provider_id)
) COMMENT '供应商健康状态';
```

实体关系：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061747365.png)

## 后端拆解执行

8 个任务，两三个小时全部交付。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061747600.png)

我挑几个有代表性的任务展示。

任务  1：Entity + Mapper

```
按照 CLAUDE.md 规范和上面的表结构，在  hify-provider 中创建 Provider、ModelConfig、ProviderHealth 的 Entity 和 Mapper。Entity 继承 BaseEntity（ProviderHealth 除外，它有自己的字段结构），Mapper 继承 BaseMapper。auth_config 和 extra_params 字段用 MyBatis-Plus 的 JSON TypeHandler。
```

任务  3：Service — CRUD

```
在 hify-provider 中实现 ProviderService。CRUD 基础逻辑：创建时校验名称不重复，列表支持按 type 和 enabled 筛选，详情接口返回关联的 modelConfig 列表和 providerHealth 信息。缓存：列表和详情加 @Cacheable(cacheNames = “provider-cache”)，更新和删除加 @CacheEvict。
```

任务  4：连通性测试

```
在 hify-provider 中实现连通性测试。根据 provider.type 分发到不同的测试方法：openai 和 openai_compatible 调 GET /v1/models（Bearer Token），anthropic 调 GET /v1/models（Header 带 x-api-key + anthropic-version），ollama 调 GET /api/tags（无认证）。统一返回 ConnectionTestResult（success、latencyMs、modelCount、errorMessage）。使用 10 讲封装的 LlmHttpClient，超时 10 秒。
```

任务  6：健康检查定时任务

```
在 hify-provider 中实现供应商健康检查定时任务。@Scheduled 每分钟执行一次，遍历所有 enabled 的 provider，调连通性测试方法。成功则更新 provider_health：status=UP、latency_ms、last_success_at、fail_count 归零。失败则 fail_count+1，连续失败 3 次标记 DOWN。使用 asyncExecutor 线程池异步执行，不阻塞主线程。
```

任务  7：Controller

```
在 hify-provider 中创建 ProviderController，按照 CLAUDE.md 接口规范实现所有接口：POST 创建、GET 列表（分页）、GET 详情（含 modelConfig 和 health）、PUT 更新、DELETE 删除、POST /{id}/test-connection 连通性测试。所有接口返回 Result，入参加 @Valid 校验。
```

## 前端对接：把 mock 换成真实 API

```
把 ProviderList.vue 的 mock 数据换成真实 API 调用。具体改动：

1. 在 src/api/provider.ts 中创建 API 方法：getProviderList（分页）、createProvider、updateProvider、deleteProvider、testConnection
2. HifyTable 的 api prop 从 mock 函数换成 getProviderList
3. HifyFormDialog 的 submit 事件处理从 console.log 换成 createProvider/updateProvider
4. 删除按钮的 useConfirm 从 mock 换成 deleteProvider
5. 列表加一列“操作”：连通性测试按钮，点击调 testConnection，结果用 ElMessage 提示
6. 加一列“健康状态”：从 provider_health 关联查询，UP 绿色 tag、DOWN 红色 tag、DEGRADED 黄色 tag、UNKNOWN 灰色 tag，显示最近延迟 ms
7. 加一列“模型数”：显示该供应商下已启用的模型数量，点击可展开模型列表
```

## 完整验收

启动后端和前端，打开浏览器 http://localhost:5173

回头看一下速度：想清楚大概一个小时（供应商分析、数据模型设计），后端 8 个任务一个小时，前端对接半小时。

# 14｜把经验变成 Skill：让 Claude Code 自动按流程走

在继续做下一个模块之前，我们先停下来做两件事。

第一件事：回头看看 13 讲里真正决定模块质量的是什么。不是代码，是代码之前的那些判断——支持哪些供应商、鉴权信息怎么存、健康状态要不要独立成表。这些判断靠的是领域知识。

第二件事：13 讲的交付流程是固定的——咨询→设计→拆解→执行→前端对接→验收。后面做 Agent、对话引擎、MCP，每个模块都是这套流程。既然固定，为什么不把它告诉 Claude Code，让它以后自动按流程走？

这一讲我们就解决这两个问题。

## 领域理解：被低估的瓶颈

Claude Code 让执行成本趋近于零之后，领域理解的权重不是降低了，而是大幅提升了。

然而，Claude Code 本身就是一个极好的领域学习工具，关键是你要问对问题。

**领域快速理解四问**

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061747237.png)

第一问：它是什么，解决什么问题？Dify 是 AI 应用开发平台，让不会写代码的人也能搭建 AI 应用。

第二问：用在哪里，什么场景？企业用 Dify 主要做智能客服、内部知识问答、文档处理。这决定了对话能力和工具接入是刚需，工作流编排是进阶需求。

第三问：由什么组成，哪些是必要的？Claude Code 列出模型管理、Agent、工作流、RAG、对话、工具接入等模块。追问“哪些是必须有的”，它帮你区分核心和外围。

第四问：技术架构是怎样的？了解到 Dify 后端是 Python + Flask，用 Celery 做异步任务——不是照抄，而是理解它为什么这么选，然后根据自己的约束做不同选择。

四个问题从外到内，一两个小时建立 70% 的领域认知，剩下 30% 靠亲手用一下产品、翻一下文档来补。

## Skill：让 Claude Code 教你

**第一步：让 Claude Code 教你 Skill 是什么**

提示词是：

```
Claude Code 的 Skill 机制是什么？怎么创建 Skill、怎么使用、Skill 文件放在哪里？和 CLAUDE.md 有什么区别？请详细解释，给我举个例子。
```

Claude Code 会告诉你：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061747975.png)

**第二步：让 Claude Code 告诉你别人怎么用 Skill**

```
业界用 Claude Code Skill 的最佳实践有哪些？大家一般用 Skill 解决什么问题？给我列举一些常见的 Skill 类型和使用场景。
```

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061747177.png)

> 有点局限了，有个开源项目名字取的好：everything claude code

**第三步：让 Claude Code 帮你写 Skill**

知道了 Skill 是什么、别人怎么用，现在让 Claude Code 帮你写。

```
我刚完成了 Hify 项目 Provider 模块的开发，流程是这样的：

1、先用咨询模式梳理了供应商选型、数据模型设计、边界问题
2、数据模型确定后更新 schema.sql
3、后端按 MVC 分层拆解：Entity+Mapper → DTO → Service（CRUD+ 连通性测试 + 模型同步 + 健康检查）→ Controller
4、每步编译或 curl 验证通过再进下一步
5、前端对接：创建 API 文件，把 mock 数据源换成真实 API
6、完整验收：后端 curl + 浏览器全流程

帮我把这个流程沉淀成一个 Skill 文件，放在  .claude/skills/module-delivery.md。要求：每一步有明确的产出物和验证方式，关键决策点标注“等待用户确认”，把我踩过的坑写成注意事项。
```

**实际跑一遍：用 Skill 启动 Agent 模块**

Skill 写好了，当场验证。给 Claude Code：

```
按模块交付 Skill 的流程，帮我做 Agent 管理模块。先从第一步开始，梳理 Agent 模块的需求和数据模型。
```

# 15｜Agent 创建与配置：复杂业务逻辑的拆解策略

## Agent 是什么？

直接向 Cluade Code 提问：

```
在 AI 应用平台（比如 Dify）里，Agent 是什么概念？它和普通的对话有什么区别？用户创建一个 Agent 需要配置哪些东西？从产品层面帮我梳理。
```

Agent 是有目标、能行动的对话主体。它不只是回答问题，而是根据目标调用工具、根据结果决定下一步。核心差异在于有没有 Tool Use + 多轮自主决策。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061747521.png)

**从概念映射到数据结构**

理解了 Agent 是什么，下一步自然是：这些信息怎么存？

这次的提示词是：

```
基于刚才的分析，Agent 在数据库里应该怎么存？需要哪些表？表之间什么关系？特别是：System Prompt 用什么类型、模型参数怎么存、Agent 和工具的多对多关系怎么处理。
```

3 张表就够：agent 主表、agent_tool 关联表。chat_session 已有 agent_id 外键不需要新表。

模型参数怎么存？方案 A（字段打散存）：temperature、max_tokens、max_context_turns 各一列。查询直接、类型约束清晰，加参数要 ALTER TABLE。

agent_tool 绑 Server 还是绑 Tool？绑 Server 意味着 Agent 自动获得该服务的所有工具（新工具自动生效），绑 Tool 是精细管控（更繁琐）。

我的判断：绑 Server。20-50 人内部使用，不需要精细管控到单个工具。简单优先。

最终表结构：

```sql
CREATE TABLE agent (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(500) NOT NULL DEFAULT '',
    system_prompt TEXT COMMENT '角色指令，可以很长',
    model_config_id BIGINT NOT NULL COMMENT '绑定的模型配置',
    temperature DECIMAL(3,2) NOT NULL DEFAULT 0.70 COMMENT '0.00~1.00',
    max_tokens INT NOT NULL DEFAULT 2048,
    max_context_turns INT NOT NULL DEFAULT 10 COMMENT '保留最近几轮上下文',
    enabled TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    deleted TINYINT NOT NULL DEFAULT 0,
    INDEX idx_agent_model_config_id (model_config_id)
) COMMENT 'Agent 配置';

CREATE TABLE agent_tool (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    agent_id BIGINT NOT NULL,
    tool_id BIGINT NOT NULL COMMENT '关联 mcp_server.id',
    created_at DATETIME NOT NULL,
    UNIQUE KEY uk_agent_tool (agent_id, tool_id),
    INDEX idx_agent_tool_agent_id (agent_id)
) COMMENT 'Agent 与工具关联';
```

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061747720.png)

## 从 Agent 到 LLM 应用：智能客服

概念和数据结构都有了，现在来看看它在真实业务中是什么样的。

它怎么对应到上面的数据结构呢？ 我们来一一对比下。

1. 选模型：GPT-4o。客服场景需要准确理解用户的问题，尤其是涉及产品功能的专业描述，4o 更稳。成本上，内部 20-50 人的使用量，4o 的费用完全可控。

2. 写 System Prompt：这是 Agent 的灵魂。不是随便写一句“你是客服”就行了，每一条指令都有用意：

   ```
   你是 Hify 平台的智能客服助手，负责解答用户关于产品功能、使用方法、常见问题的咨询。语气专业友好，回答简洁明了。如果用户的问题超出你的知识范围，诚实告知并引导联系人工客服。不编造不确定的信息。
   
   拆解一下：
   - 语气专业友好：不要太机械也不要太随意。
   - 回答简洁明了：客服场景用户要的是答案不是长篇大论。
   - 超出知识范围诚实告知：这是最关键的一条，防止模型“幻觉”编造不存在的功能。
   - 引导联系人工客服：给用户一个兜底方案。
   ```

3. 调参数：temperature 设 0.3。temperature 越高越有创意，但也越不可控，客服场景要的是可靠不是创意，同一个问题问两次，答案应该基本一致。

4. max_context_turns 设 8。每多保留一轮对话上下文，就多消耗一轮的 token 费用。客服场景大部分问题 3-5 轮就解决了，8 轮留够余量。

## 拆解 Agent 的 CRUD

那么智能客服的配置想清楚了，接下来回到技术实现，Agent 模块的 CRUD 怎么做。

```
帮我拆解 Agent CRUD 的完整逻辑：从前端点保存到数据库落库，中间要经过哪些步骤？把创建、查询、更新、删除四个场景都拆解出来。
```

- 创建：前端发 POST 请求  → Controller 参数校验（name 非空、modelConfigId 非空、temperature 0~1）→ Service 检查 name 唯一性  → 跨模块校验 modelConfigId 存在且 enabled（调 ProviderService 接口，不直接查 mapper）→ INSERT agent 主表  → 如果 toolIds 非空，批量 INSERT agent_tool → 清除缓存  → 返回详情。
- 列表查询：先分页查 agent，再批量查各 agent 的工具数量（SELECT agent_id, COUNT(*) FROM agent_tool WHERE agent_id IN (...) GROUP BY agent_id）。不 JOIN，不 N+1——批量 IN 查询是最优平衡。
- 详情查询：查 agent + 查关联的 mcp_server 列表，组装完整响应。加  @Cacheable。
- 更新工具列表：Claude Code 对比了两种方案。方案 A 全量替换（DELETE 再 INSERT），方案 B 增量 diff。它推荐方案 A，agent_tool 数据量小，全删重插没性能问题，逻辑简单。我同意。不是所有场景都需要最优雅的方案，够用且简单就是最好的。
- 删除：不做对话会话拦截——agent 删了，进行中的对话自然找不到 agent 配置返回错误，接受这个行为。级联删 agent_tool（物理删除，关联表没有逻辑删除的意义），agent 本身逻辑删除（deleted=1）。chat_session 里的 agent_id 不处理，历史会话保留。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061747958.png)

# 16｜对话引擎（上）：理解对话链路与流式技术选型

对话引擎是 Hify 最核心的模块。没有它，前面做的模型管理、适配层、Agent 配置都只是准备工作。这一讲和下一讲会把对话引擎做完。

我们先搞清楚对话引擎到底是什么，再动手。

## 对话引擎

**对话引擎是什么**

```
在 AI 应用平台里，对话引擎是什么？它的职责是什么？和普通的 HTTP 接口调用有什么区别？
```

对话引擎是连接用户和 LLM 的一条处理管道，中间要做很多事。

1. 会话管理。对话引擎要维护“会话”的概念，哪些消息属于同一次对话、会话什么时候创建、什么时候结束。
2. 上下文拼装。对话引擎要把 System Prompt + 历史消息 + 当前消息拼成一个完整的 messages 数组，每次调用都带上上下文，让 LLM “看起来”有记忆。
3. 流式响应。对话引擎要做流式推送，LLM 生成一个字就推一个字给前端，用户看到的是像人打字一样一个字一个字冒出来。
4. 消息存储。对话结束后，用户消息和 AI 回复要持久化到数据库。用户下次打开能看到历史记录，管理员能做数据分析。

普通接口是请求 - 响应模式，一来一回就结束。对话引擎是长连接 + 流式。这带来了完全不同的技术挑战：线程不能一直占着、连接不能提前断、前端要实时渲染。

**对话引擎的完整链路**

概念清楚了，让 Claude Code 帮我画出完整的技术链路：

```
用户和一个 Agent 对话，从前端发消息到收到流式回复，中间每一步技术上发生了什么？从前端到 Controller 到 Service 到 LLM 再回来，逐步梳理。
```

Claude Code 给了一张非常完整的链路图：

```
用户输入 "Hify 怎么创建 Agent？"
    │
    ▼
[前端] POST /api/v1/chat/sessions/{sessionId}/messages
       接收: SSE 流式响应
    │
    ▼
[ChatService] ── 组装上下文 ──
    │  1. 查 session → 拿到 agentId
    │  2. 查 Agent → 拿到 systemPrompt、modelConfigId、参数
    │  3. 查 ModelConfig → 拿到 modelId、providerId
    │  4. 查 Provider → 拿到 baseUrl、authConfig
    │  5. 从 Redis 取最近 N 轮历史消息
    │
    ▼
[ChatService] ── 写入用户消息 ──
    │  INSERT chat_message(role='user', content)
    │
    ▼
[ChatService] ── 构造 LLM 请求 ──
    │  messages = [
    │    { role: "system",    content: agent.systemPrompt },
    │    { role: "user",      content: "上上轮问题" },
    │    { role: "assistant", content: "上上轮回复" },
    │    { role: "user",      content: "Hify 怎么创建 Agent？" }
    │  ]
    │
    ▼
[LlmHttpClient] ── 流式调用 LLM ──
    │  llmExecutor 线程池（和业务线程隔离）
    │  Resilience4j 熔断器包裹
    │
    ▼
[LLM API] 返回 SSE 流 → 边收边推给前端
    │
    ▼
[ChatService] ── 流结束后 ──
    │  INSERT chat_message(role='assistant', content=完整回复)
    │  更新 Redis 历史消息

```

**数据结构设计**

在深入流式技术之前，先把数据模型定下来。

```
对话引擎需要哪些表？会话和消息怎么存？消息表需要哪些字段？
```

SQL Schema 如下：

```
chat_session
  id          bigint PK
  agent_id    bigint          -- 关联 agent
  title       varchar(200)    -- 首条消息前 20 字自动生成
  status      varchar(20)     -- ACTIVE / ARCHIVED
  deleted / created_at / updated_at

chat_message
  id            bigint PK
  session_id    bigint         -- 关联 chat_session
  role          varchar(20)    -- user / assistant / system
  content       longtext
  tokens        int            -- token 数（上下文管理用）
  finish_reason varchar(20)    -- stop / length / error
  latency_ms    int            -- 响应耗时 ms
  deleted / created_at / updated_at
```

## 流式响应：SSE 完整解析

这是对话引擎技术含量最高的部分。

**SSE 是什么？**

```
SSE（Server-Sent Events）的工作原理是什么？和普通 HTTP 请求有什么区别？数据格式是什么样的？
```

Claude Code 的解释：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061747222.png)

客户端发请求，服务端保持连接不关闭，持续往客户端推数据，直到主动关闭。数据格式很简单，每条消息以  data: 开头，用两个换行分隔：

```json
data: {"type":"delta","content":"在"}

data: {"type":"delta","content":"Hify"}

data: {"type":"delta","content":"中"}

data: {"type":"done","finishReason":"stop"}
```

前端用 EventSource API 接收，浏览器原生支持，不需要额外依赖：

```javascript
const es = new EventSource('/api/v1/chat/sessions/1/messages/stream')
es.onmessage = e => appendToken(JSON.parse(e.data).content)
es.onerror = () => es.close()
```

**为什么不用 WebSocket**

```
AI 对话的流式响应，用 SSE 还是 WebSocket？
```

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061747016.png)

业界验证：OpenAI、Anthropic、Dify，所有主流 AI 对话产品都选 SSE。

**SseEmitter 的工作原理**

```
Spring MVC 的 SseEmitter 怎么工作？生命周期是什么样的？
```

SseEmitter 本质是一个长连接容器。Controller 方法返回 SseEmitter 对象后，Spring 不会关闭 HTTP 连接，而是持有它。后续代码通过  emitter.send() 往这个连接里推数据，最后  emitter.complete() 关闭连接。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061747969.png)

关键在于线程切换。Tomcat 的请求线程创建 SseEmitter 后立刻返回，实际的 LLM 调用在 llmExecutor 线程池里异步执行：

```
Tomcat 线程:
  创建 SseEmitter(120s) → 提交任务给 llmExecutor → return emitter
  （线程释放，可以处理其他请求）

llmExecutor 线程:
  调用 LLM stream API → 收到 delta → emitter.send(delta)
                       → 收到 delta → emitter.send(delta)
                       → 收到 [DONE] → 存消息 → emitter.complete()
```

**SseEmitter 的三个坑**

1. LLM 回复容易中断。SseEmitter 默认超时 30 秒，LLM 生成一个长回复可能要一两分钟，30 秒一到连接直接断了用户看到半截回复。必须设长，new SseEmitter(120_000L)，120 秒。

2. HTTP 客户端断开连接，后端要 catch 异常并释放线程。用户对话到一半关了浏览器标签页，但 llmExecutor 线程不知道，它还在调 LLM 并 emitter.send()。如果不 catch IOException 这个异常并停止 LLM 调用，线程会白跑到 LLM 输出完，浪费 llmExecutor 的线程资源。

3. Nginx 缓冲。Nginx 默认会缓冲上游响应，收集一批数据后才一次性发给客户端。结果用户看到的是“等了十几秒突然全部内容一起出现”，流式效果完全失效。必须在 Nginx 配置里关掉缓冲：

   ```nginx
   location /api/ {
       proxy_pass http://backend;
       proxy_buffering off;
       proxy_cache off;
       proxy_read_timeout 120s;
   }
   ```

# 17｜对话引擎（下）：让智能客服真正开口说话

在写 CRUD 之前，有一个核心问题要先解决：上下文。

## 上下文是什么

我问 Claude Code：

```
AI 对话里的“上下文”到底是什么？LLM 本身有记忆吗？多轮对话是怎么实现的？
```

LLM 本身没有记忆。 每次调用都是无状态的，你上一轮告诉它“我的订单号是 12345”，下一轮它完全不知道。它不像数据库会持久化状态，每次调用都是一张白纸。

那 ChatGPT 怎么做到记住你说过什么？答案是每次调用都把历史消息重新塞进请求里，让模型在同一次推理中“看到”历史，造成记得的假象。

上下文就是你传给模型的 messages 数组的全部内容：

```json
{
  "messages": [
    { "role": "system",    "content": "你是专业客服" },
    { "role": "user",      "content": "我的订单在哪里" },
    { "role": "assistant", "content": "请提供订单号" },
    { "role": "user",      "content": "订单号是 12345" },
    { "role": "assistant", "content": "您的订单正在配送中" },
    { "role": "user",      "content": "大概几天到" }
  ]
}
```

模型能处理的 messages 总长度有上限，叫 context window，单位是 token。Claude 3.5 Sonnet 是 200K，本地 Llama 3 可能只有 8K。超出窗口直接报错或截断。而且 token 是要花钱的，历史越长，每次调用越贵。

接下来我问：

```
对话上下文管理有哪几种常见策略？各自的优缺点是什么？
```

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061747869.png)

最终 Hify 选滑动窗口。理由是：20-50 人内部使用，对话不会特别长。Redis List 天然支持 RPUSH 新消息，超出时 LPOP 旧的，实现十行以内。

## 对话存储选型

```
对话历史应该存在哪？Redis、MySQL、向量数据库在对话引擎里分别扮演什么角色？
```

Claude Code 的分析帮我理清了三者的分工：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061747959.png)

MySQL 是真相来源（全量），Redis 是热缓存（最近 N 轮）。写入时两边同时写，消息存 MySQL 的同时 RPUSH 到 Redis，读取上下文只读 Redis，Redis 过期后从 MySQL 重新加载（Cache-Aside）：

```java
List<ChatMessage> history = redis.get(sessionKey);
if (history == null) {
    // 冷启动：从 MySQL 加载最近 N 条，回写 Redis
    history = chatMessageMapper.selectRecent(sessionId, maxContextTurns * 2);
    redis.set(sessionKey, history, Duration.ofHours(2));
}
```

pgvector 在 Hify 里的角色是 RAG 知识库，把产品文档切成小段，每段生成一个向量表示（1536 维 float 数组）存进 pgvector，用户提问时做语义检索找到最相关的文档段落，拼进上下文给 LLM 参考。

三者协作的完整流程：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061747612.png)

## CRUD 实现

上下文和存储方案都定了，开始写代码。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061747364.png)

重点是任务  3——ChatService.sendMessage，它串联了 16 讲的整条六步链路：

```
实现 ChatService.sendMessage 方法。接收 sessionId（可选）和 content。流程：异常处理：LLM 超时走 onTimeout 回调、客户端断开 catch IOException 停止 LLM 调用、send 失败调 completeWithError。事务注意：写消息操作拆成独立方法，不要在返回 SseEmitter 的方法上加 @Transactional。
```

**验收：和智能客服对话**

```bash
# 创建会话，发第一条消息
curl -N -X POST http://localhost:8080/api/v1/chat/sessions \
  -H "Content-Type: application/json" \
  -d '{"agentId": 1}'
# 返回 sessionId

# 和智能客服对话（流式）
curl -N -X POST http://localhost:8080/api/v1/chat/sessions/{sessionId}/messages \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"content": "Hify 怎么创建 Agent？", "stream": true}'

# 应该看到流式输出：
# data: {"type":"delta","content":"在"}
# data: {"type":"delta","content":"Hify"}
# data: {"type":"delta","content":"中，您可以..."}
# data: {"type":"done","finishReason":"stop","latencyMs":3200}
```

第一轮通了。现在测上下文，这是关键验证点：

```bash
# 追问（不重复说明背景）
curl -N -X POST http://localhost:8080/api/v1/chat/sessions/{sessionId}/messages \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"content": "那怎么配置模型？", "stream": true}'
```

检查数据：

```bash
# MySQL：全量历史
SELECT role, LEFT(content, 50), tokens FROM chat_message
WHERE session_id = {sessionId} ORDER BY created_at;

# Redis：最近 N 轮
redis-cli LLEN session:{sessionId}
# 应该等于 maxContextTurns * 2（一问一答算两条）
```

全部通过。智能客服能流式回复，能记住上下文，历史太长会自动裁剪。

# 18｜复杂前端交互：流式聊天界面

## 复杂度分层

复杂页面需要拆解，拆解的顺序有三层，有顺序依赖：

- 结构层：页面长什么样，组件怎么排列
- 行为层：用户做了什么，页面发生什么
- 细节层：动画速度、样式微调、边界处理

乱了顺序就会返工，所以正确的顺序是：先对齐结构，再描述行为，最后打磨细节。

**第一步：草稿图对齐结构**

打开 ChatGPT 或 Claude 的对话页面，截一张图，上传给 Claude Code：

```
参考这张图的整体布局。左侧会话列表，右侧聊天窗口，底部固定输入框。用 Element Plus 实现，配色用 Hify 的浅色主题。
```

**第二步：文字描述填充行为**

静态交互：四维度描述

```
Provider 管理页。
布局：顶部操作栏（标题 + 新增按钮），主体是 Provider 列表表格。
数据：展示 name、type、status，status 用标签区分启用 / 禁用。
交互：点新增弹出表单弹窗，字段包括名称、类型（下拉选 OpenAI/Anthropic/Ollama）、Base URL、API Key；保存后列表刷新；支持编辑和删除，删除需二次确认。
接口：GET /api/v1/providers 查列表，POST 新增，PUT 编辑，DELETE 删除。
```

动态交互：时间线描述

```
发送消息的完整时间线： 
1.用户在输入框输入内容，点发送（或按 Enter）
2.输入框立刻清空，发送按钮变为不可点击
3.消息区域底部出现用户消息气泡（靠右，深色背景）
4.紧接着出现 AI 消息气泡（靠左，浅色背景），内容区域为空，显示加载动画
5.前端用 fetch 手动处理 SSE 流（不要用 EventSource，接口是 POST）
6.每收到一个 delta chunk，把 content 追加到 AI 气泡，同时滚动到底部
7.收到 done 事件，加载动画消失，发送按钮恢复可用
8.如果请求失败或收到 error 事件，AI 气泡显示红色错误提示，发送按钮恢复
```

**第三步：增量调整**

调整时一个原则：每次只改一个维度，描述说清楚 delta。

调整 1

```
当前打字机效果每字符间隔 50ms，感觉太快，改成 30ms，其他不变。
(是太快还是太慢？)
```

调整 2

```
AI 消息气泡没有渲染 Markdown，引入 marked.js 把 content 渲染成 HTML，代码块用等宽字体，其他样式保持。
```

调整 3

```
会话列表的消息摘要显示完整内容，改为最多 30 个字符，超出用省略号截断。
```

## 验收：同一个接口，从 curl 到浏览器

用 curl 直接调后端接口：

```bash
curl -N -X POST http://localhost:8080/api/v1/chat/sessions/{sessionId}/messages \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"content": "我的订单状态怎么查？", "stream": true}'

# data: {"type":"delta","content":"您"}
# data: {"type":"delta","content":"好"}
# data: {"type":"delta","content":"，请问"}
# ...
# data: {"type":"done","finishReason":"stop","latencyMs":2800}
```

后端通了。在浏览器里调用，走完整的用户操作流程：

```
1. 打开 Hify，进入“对话”，新建对话，选“退货客服” Agent
2. 发送“我的订单状态怎么查？”看到用户气泡靠右，AI 气泡靠左，内容逐字追加
3. 追问“那退款流程呢？”智能客服记住上下文，直接回答，不需要重复背景
```

再问几轮，确认多轮对话连贯。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061748950.png)

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061748686.png)

会话管理：

```
1. 左侧列表出现这个对话，显示 Agent 名称和消息摘要
2. 新建第二个对话，列表有两条，点击切换，右侧记录对应切换
3. 刷新页面，两个对话都还在（MySQL 持久化正常）
```

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061748940.png)

# ==核心功能交付：高级篇==

# 20｜RAG 知识库（上）：RAG 和向量数据库

当你要给一个跑通的系统加入一个你完全不了解的技术能力，怎么做？

答案不是去读文档、去找教程，而是用你现在已有的工具Claude Code，一步一步把陌生的东西变熟悉。这个方法论，以后遇到任何陌生技术都能复用。

**先搞清楚要解决什么问题**

碰到陌生技术，很多人的第一反应是去查“XXX是什么”。这个问题太宽泛，答案往往是一大段定义，读完还是不知道和自己的场景有什么关系。

比较好的方式是从业务痛点出发，用自己的场景问：

```
我的智能客服 Agent 现在只能靠模型的通用知识回答问题，无法引用公司的产品手册和政策文档。我听说 RAG 可以解决这个问题。帮我解释：RAG 的核心思路是什么？它是怎么让 LLM 能引用私有文档的？
```

> 为什么要这样问？因为这样的问题有具体场景，你越能描述清楚自己的痛点，它的回答就越有针对性。

LLM 的知识来自训练数据，训练完成后就固化了。你的产品手册、退换货政策、内部 FAQ，这些文档不在训练集里，模型物理上不知道这些内容。

解决这个问题有两条路：

- Fine-tuning（微调）：把文档塞进训练过程，改变模型权重。问题是贵、慢，而且文档一旦更新就得重新训练，完全不实际。
- RAG：不动模型，在每次对话时实时把相关文档片段塞进 Prompt。模型本身没变，变的是它看到的输入。

RAG 选的是第二条路，思路是检索  → 增强  → 生成。用户提问  → 去文档库找最相关的几段内容  → 把这几段原文拼进 Prompt → LLM 基于这些内容回答。

**拆解技术组件，缩小陌生范围**

知道 RAG 是什么、解决什么问题之后，下一步是搞清楚它涉及哪些技术组件。

```
实现一个完整的 RAG 功能，需要哪些技术组件？每个组件的作用是什么？
```

Claude Code 按数据流向拆出了两个阶段、六个组件。

阶段一：文档入库管道

1. 文档解析器，把各种格式的文件转成纯文本。TXT 直接读，PDF 有文字版和扫描版两种，Word 用 Apache POI 解析。

   （Hify 一期只支持 TXT 和 PDF 文字版，够用。）

2. 文本分块器，把长文档切成适合检索的小块。这是 RAG 里最影响效果的环节。块太大，Embedding 语义被稀释，检索不准，塞进 Prompt 还占 token 多；块太小，上下文丢失，答案不完整。常见策略有固定大小切分、按段落切分、递归分割（先按段落，太长再按句子）。

   （Hify 用递归分割，chunk_size 512 token，overlap 64 token。）

3. Embedding 模型，把文本转成向量（一串浮点数）。语义相近的文本向量在空间里也相近。调用方式是 POST 一个接口，拿回向量数组，和 Chat Completion 本质上是同一类 API 调用。

4. 向量数据库，存向量，支持相似度检索。

阶段二：检索对话链路

5. 检索器，用户提问时把问题也转成向量，在向量数据库里找 Top-K 最相关的块。
6. Prompt 组装器，把检索到的原文块拼进上下文，告诉 LLM 基于以下资料回答。

向量搜索的关键是：语义相近的文本，向量距离就近。不管用词怎么不同，只要意思相近就能找到。这就是 RAG 检索质量高于关键词搜索的根本原因。

**向量数据库选型**

给约束让 Claude Code 分析，你来判断。

```
向量数据库有哪些主流选项？我的约束是：Java 技术栈、已有 PostgreSQL、一期数据量不大（几千到几万条分块）、基本的相似度检索够用。帮我对比 pgvector、Milvus、Qdrant、Elasticsearch 的优缺点。
```

> 为什么问题里要列出约束？把你的实际约束给出来，Claude Code才能给出有判断立场的分析，而不是中立的百科全书。

1. pgvector 是 PostgreSQL 的扩展，装一个插件就行，不引入新组件。SQL 操作，Java 生态直接用 JDBC，零学习成本。性能在百万级以下够用。缺点是超大规模数据不如专业向量数据库。
2. Milvus 是专业向量数据库，性能最强，支持十亿级向量。但部署极重，依赖 etcd 和 MinIO，需要单独一套集群，运维成本高，Java SDK 文档也不如 Python 完善。
3. Qdrant 轻量，Rust 写的，单二进制部署，REST API 友好。比 Milvus 轻得多，但仍然是一个额外的服务，需要单独部署、端口要开、故障要排查。
4. Elasticsearch 8.x 开始支持向量检索，全文加向量混合检索很强。但极重，JVM 堆内存至少 4GB 起，运维复杂度高。专门为 RAG 引入一套 ES 集群，性价比极低。

我的判断：选 pgvector。能不加新依赖就不加。Hify 已经在用 PostgreSQL，pgvector 只是一个扩展，不引入新组件，不增加运维负担，SQL 操作和现有的 document 表、knowledge_base 表直接 JOIN，业务逻辑简单。一期数据量小，性能完全够用。

**最小 Demo 跑通：从理论到手感**

在把 pgvector 集成进 Hify 之前，我需要先有手感——能插入向量、能查到相似结果，知道它到底怎么工作。

```
我选了 pgvector。帮我从零上手：怎么安装、怎么建表、怎么插入向量、怎么做相似度查询？给我一个能跑通的最小示例。
```

> 为什么要先跑最小Demo？新技术有很多细节只有亲手跑过才知道，这些问题如果第一次遇到是在Hify的代码里，排查成本会很高。先单独跑通，建立手感，再集成就不会茫然。

Claude Code 给了建表和查询的核心 SQL：

```sql
-- 启用扩展（每个数据库执行一次）
CREATE EXTENSION IF NOT EXISTS vector;

-- 建表，1536 维对应 OpenAI text-embedding-3-small
CREATE TABLE document_chunk (
    id        BIGSERIAL PRIMARY KEY,
    content   TEXT NOT NULL,
    embedding vector(1536)
);

-- 相似度查询：<=> 是余弦距离，越小越相似，取最近 3 条
SELECT content,
       1 - (embedding <=> '[0.011, -0.033, ...]') AS similarity
FROM document_chunk
ORDER BY embedding <=> '[0.011, -0.033, ...]'
LIMIT 3;
```

`<=>` 是 pgvector 的余弦距离运算符。用  `1 - 距离` 转成相似分，越接近 1 越相似。这个运算符是 pgvector 扩展引入的，标准 SQL 里没有。

然后问 Java 集成：

```
pgvector 在 Java 里怎么用？MyBatis-Plus 能直接操作 vector 类型吗？
```

MyBatis-Plus 不原生支持 vector 类型，直接用会报类型转换错误。解法是自定义 TypeHandler，告诉 MyBatis 怎么把 Java 的  float[] 和 pgvector 的  vector 类型互转。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608061748690.png)

**Embedding模型选型与接入**

向量数据库搞定了。接下来是Embedding模型，它是把文本变成向量的工具。

```
我要调用OpenAI的Embedding API。接口怎么调？和Chat Completion有什么区别？有哪些模型可以选？有什么限制？
```

> 问这个问题是因为：Embedding接口虽然也是调OpenAI，但它和Chat Completion是完全不同的接口，返回结构也不一样，Chat Completion返回文本，Embedding返回向量数组。

Chat Completion是“文本→文本”，Embedding是“文本→向量”。

接口是 `POST /v1/embeddings`，入参 `{model, input}`，返回 `data[0].embedding`，一个长度1536的float数组。和Chat Completion最大的区别是没有流式响应，同步返回，等向量算完一次性给你。

模型选哪个？Claude Code给了三个选项的对比：

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/20-RAG知识库（_970416_5a5d6b2e6a.png)

我的判断：选text-embedding-3-small。同样1536维，价格是ada-002的五分之一，效果还更好。

# 21｜RAG 知识库（下）：给客服一本手册，对话功能集成 RAG

上一讲完成了探路，pgvector装好了，Embedding API能调了，两个能力分别验证通过。

我们这节课是要实现RAG的全流程。

**先想清楚要改哪里**

当前链路是：

```
1. 加载 Session → 拿到 agentId
2. 加载 Agent   → 拿到 systemPrompt、modelConfigId、temperature、maxContextTurns
3. 加载 ModelConfig → 拿到 modelId、providerId
4. 加载 Provider → 拿到 baseUrl、authConfig
5. 写入用户消息到 MySQL
6. 从 Redis 加载上下文历史
7. 拼 messages 数组：[system] + 历史 + 当前消息
8. 调 LLM streamChat
9. 写入 assistant 消息，更新 Redis
```

RAG检索插在第6步之后、第7步之前，标记为第6.5步：

```
6.5 ★ RAG 检索：用户问题 → Embedding → pgvector Top-K → 相关 chunk
```

**数据模型**

```
Hify要支持RAG知识库。管理员上传文档，系统自动分块、向量化存入pgvector。对话时检索相关内容注入上下文。帮我设计数据模型。
```

Claude Code给了三张表的设计：

```
MySQL
  knowledge_base   — 知识库容器
  document         — 文档元信息 + 处理状态

PostgreSQL (pgvector)
  document_chunk   — 分块文本 + embedding 向量
```

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/21-RAG知识库（_971417_d3cb8129e5.png)

DDL

```sql
CREATE TABLE knowledge_base (
    id          BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    description VARCHAR(500) DEFAULT '',
    enabled     TINYINT(1)   NOT NULL DEFAULT 1,
    deleted     TINYINT(1)   NOT NULL DEFAULT 0,
    created_at  DATETIME     NOT NULL,
    updated_at  DATETIME     NOT NULL
);

-- 关联 knowledge_base_id，记录文件元信息和处理状态。
CREATE TABLE document (
    id                BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    knowledge_base_id BIGINT       NOT NULL,
    name              VARCHAR(200) NOT NULL,
    file_type         VARCHAR(20)  NOT NULL,   -- txt / pdf / md
    file_size         BIGINT       NOT NULL,
    status            VARCHAR(20)  NOT NULL DEFAULT 'PENDING',
    -- PENDING / PROCESSING / DONE / FAILED
    error_message     VARCHAR(500) DEFAULT '',
    chunk_count       INT          NOT NULL DEFAULT 0,
    deleted           TINYINT(1)   NOT NULL DEFAULT 0,
    created_at        DATETIME     NOT NULL,
    updated_at        DATETIME     NOT NULL,
    KEY idx_document_kb_id (knowledge_base_id)
);

-- PostgreSQL：document_chunk
-- 向量数据，存分块文本和embedding。
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE document_chunk (
    id                BIGSERIAL    PRIMARY KEY,
    knowledge_base_id BIGINT       NOT NULL,   -- 冗余，检索时免 JOIN
    document_id       BIGINT       NOT NULL,
    chunk_index       INT          NOT NULL,
    content           TEXT         NOT NULL,
    embedding         vector(1536) NOT NULL,   -- text-embedding-3-small
    token_count       INT          NOT NULL DEFAULT 0,
    deleted           SMALLINT     NOT NULL DEFAULT 0,
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chunk_kb ON document_chunk (knowledge_base_id) WHERE deleted = 0;
```

agent表加一列：

```sql
ALTER TABLE agent
    ADD COLUMN knowledge_base_id BIGINT DEFAULT NULL;
```

NULL表示不启用RAG，有值表示启用。

**知识库的全流程**

1、知识库CRUD指令：

```
实现以下接口：
POST   /api/v1/knowledge-bases          — 创建知识库，参数：name（必填）、description（可选）
GET    /api/v1/knowledge-bases          — 分页查询知识库列表，参数：page、size、name（模糊搜索）
GET    /api/v1/knowledge-bases/{id}     — 查询单个知识库详情
PUT    /api/v1/knowledge-bases/{id}     — 更新知识库，参数：name、description、enabled
DELETE /api/v1/knowledge-bases/{id}     — 逻辑删除知识库
```

文档管理CRUD指令：

```
实现以下接口：
POST   /api/v1/knowledge-bases/{kbId}/documents    — 上传文档
       接收 multipart/form-data，校验文件类型（只接受 txt/md/pdf）和大小（不超过 10MB）
       文件落盘到 upload 目录，MySQL 写入 document 记录（status=PENDING）
       立即返回 documentId，提交异步任务到线程池
GET    /api/v1/knowledge-bases/{kbId}/documents     — 分页查询知识库下的文档列表
GET    /api/v1/documents/{id}                       — 查询单个文档详情（含 status、chunk_count、error_message）
GET    /api/v1/documents/{id}/chunks                — 查询文档的分块列表（调 pgvector 的 JdbcTemplate）
DELETE /api/v1/documents/{id}                       — 逻辑删除文档，同时删除 pgvector 里的 chunk
```

2、处理逻辑

上传接口提交异步任务后，知识库流程开始工作，分五个环节串联处理。

```
1. 状态更新
   document.status = PROCESSING

2. 解析 — extractText(filePath, fileType) → String
   TXT/MD：直接读文件内容，UTF-8
   PDF：用 Apache PDFBox 提取文字层。扫描版 PDF（提取文字为空）一期不支持，返回错误
   解析失败（加密 PDF、损坏文件）→ status=FAILED，写 error_message，后续环节不执行

3. 分块 — splitChunks(text) → List<ChunkDTO>
   递归分割：chunk_size=512 token，overlap=64 token
   切割优先级：段落边界（\n\n）> 句子边界（句号、问号）> 字符数截断
   每个 ChunkDTO 包含：chunkIndex、content、tokenCount

4. 向量化 — embedChunks(List<ChunkDTO>) → List<ChunkDTO>（补上 embedding 字段）
   调用 Embedding API，input 支持数组，一次请求处理多个块
   分批逻辑：每批最多 100 条，超过就分多批
   注意：API 返回的 data[] 数组按 index 字段排序后再和原始 chunk 列表对应
   不能假设返回顺序和输入顺序一致

5. 存储 — saveChunks(documentId, knowledgeBaseId, List<ChunkDTO>)
   JdbcTemplate.batchUpdate() 批量写入 pgvector 的 document_chunk 表
   写完后更新 document.status=DONE，chunk_count=N
```

3、前端页面

后端接口跑通后，做前端。分两个页面：知识库管理和文档管理。

知识库管理：

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/21-RAG知识库（_971417_883afd13fd.png)

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/21-RAG知识库（_971417_08f7374726.png)

上传文档，拆解为向量存储：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/21-RAG知识库（_971417_156b04a660.png)

# 22｜工作流编排（上）：搞懂工作流，把它存起来

智能客服现在所有问题都走同一个 Prompt，用户问退换货政策和问产品功能，客服用同样的方式回答。

更好的做法是：先判断用户问的是什么类型，然后走不同的处理路径。售前走产品知识Prompt，售后走政策条款 Prompt，技术支持走故障排查 Prompt。每条路径更聚焦，回答更精准。

这就是工作流要解决的问题。工作流由两部分组成：元数据和执行引擎。

1. 元数据是工作流的配置，它有哪些节点、节点之间怎么连接、每个节点做什么。
2. 执行引擎是让这份配置真正跑起来的逻辑，从起始节点开始，一步步往下走，直到结束。

这一讲做元数据：搞懂工作流是什么，设计存储结构，实现CRUD。下一讲做执行引擎。

**工作流是什么**

先让 Claude Code 解释清楚再动手。

```
在 AI 应用平台中，工作流是什么概念？
用智能客服的场景帮我解释，不要讲理论，给我具体的例子。
```

用户发来一条消息：“我昨天下的订单还没到，帮我查一下。”

工作流的处理方式：把这件事拆成有序的步骤，每步做一件具体的事。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/22-工作流编排（上_972496_498a23d892.png)

**工作流在代码里长什么样**

```
工作流在代码层面怎么表示？
帮我用最直白的方式解释——不要说 DAG、不要说图论，
就告诉我它在代码里是什么数据结构。
```

两个概念——节点 + 连线。节点是做什么，每个节点就是一条数据库记录：

```
WorkflowNode {
    workflowId  = 1
    type        = "LLM"       // 这个节点干什么：调LLM / 调API / 做判断
    name        = "意图识别"
    config      = {"prompt": "判断用户意图，返回 ORDER_QUERY 或 POLICY_QUERY"}
}

WorkflowNode {
    workflowId  = 1
    type        = "CONDITION"
    name        = "有没有订单号"
    config      = {"expression": "{{intent}} == 'ORDER_QUERY'"}
}
```

连线是做完去哪，记录节点之间的跳转关系：

```
WorkflowEdge {
    sourceNodeKey = "classify"   // 从"意图识别"
    targetNodeKey = "router"     // 到"条件判断"
    condition     = null         // 无条件，直接走
}

WorkflowEdge {
    sourceNodeKey = "router"     // 从"条件判断"
    targetNodeKey = "order_api"  // 到"查询订单"
    condition     = "true"       // 条件为真时走这条线
}
```

两张表，存库是平铺的两张表，执行时加载进内存变成 Map + while 循环。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/22-工作流编排（上_972496_66c469dd95.png)

理解了这些，工作流就不神秘了。下一步把它映射成完整的存储设计。

**工作流怎么设计，由哪些部分组成**

让Claude Code帮我把代码设计做完整。

```
基于上面的工作流结构，帮我设计数据模型。要考虑：

1.如何存储工作流基本信息
2.如何存储节点，不同类型节点配置格式不同怎么处理
3.如何存储节点之间的连接关系
4.Java 代码里如何做类型安全的解析
```

一份 JSON 拆成三张表，创建时拆分写入，查询时组装还原。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/22-工作流编排（上_972496_8ffe0dfe8b.png)

- `workflow` 存工作流基本信息：名称、描述、状态（DRAFT / PUBLISHED / DISABLED）。
- `workflow_node` 存节点：`node_key` 是节点在工作流内的唯一标识（如 `classify`、`router`），`type` 是节点类型，`config` 是JSON字段存各类型节点的配置。
- `workflow_edge` 存连线：`source_node_key` → `target_node_key`，`condition` 是条件表达式，`NULL` 表示无条件直接走。

Java 代码实现：

```java
public sealed interface NodeConfig
    permits StartNodeConfig, LlmNodeConfig, ConditionNodeConfig,
            ApiCallNodeConfig, KnowledgeNodeConfig, EndNodeConfig {}

// 每种类型一个 record
public record LlmNodeConfig(Long modelConfigId, String prompt, String outputVariable)
    implements NodeConfig {}

// 解析时按 type 分发
NodeConfig config = switch (type) {
    case "LLM"       -> objectMapper.readValue(configJson, LlmNodeConfig.class);
    case "CONDITION" -> objectMapper.readValue(configJson, ConditionNodeConfig.class);
    // ...
};
```

执行引擎里用 `switch` 模式匹配处理不同类型：

```java
switch (config) {
    case LlmNodeConfig llm            -> executeLlm(llm, context);
    case ConditionNodeConfig cond     -> evaluateCondition(cond, context);
    case ApiCallNodeConfig api        -> callApi(api, context);
    case KnowledgeNodeConfig kb       -> retrieveKnowledge(kb, context);
    case StartNodeConfig start        -> initContext(start, context);
    case EndNodeConfig end            -> buildOutput(end, context);
}
// 漏写任何一个 case，编译报错
```

新增节点类型只需要加一个 `record`，在 `NodeConfigParser` 加一行 `case`，不改其他代码。

**实现CRUD**

设计确认了，开始实现，我们的提示词如下：

```markdown
在 hify-workflow 模块中实现工作流的 CRUD。

接口列表：
POST   /api/v1/workflows          — 创建工作流
GET    /api/v1/workflows          — 分页查询工作流列表
GET    /api/v1/workflows/{id}     — 查询工作流详情（含完整节点和边）
PUT    /api/v1/workflows/{id}     — 更新工作流
DELETE /api/v1/workflows/{id}     — 逻辑删除工作流

约束：
- 创建接口接收完整请求体（包含 nodes 和 edges），拆分写入三张表
  workflow 写一条，nodes 批量插入 workflow_node，edges 批量插入 workflow_edge
  三张表在同一个事务里，任何一张写失败全部回滚

- 查询详情接口从三张表组装回完整结构返回
  nodes 数组和 edges 数组都要还原，结构和创建时一致

- 更新工作流时，先逻辑删除原有的 nodes 和 edges，再批量插入新的
  不要做 diff 更新，直接替换

- 删除工作流时，关联的 nodes 和 edges 一起逻辑删除

- 节点配置用 NodeConfigParser 解析，NodeConfig sealed interface + record 体系

- 代码放在 hify-workflow 模块，遵循 CLAUDE.md 的代码组织规范
```

一个关键约束：更新时直接替换，不做 diff。工作流改动往往涉及多个节点和边，diff 逻辑复杂且容易出错。先删再插，三张表始终保持一致，多几条SQL完全值得。

**串起来验证**

CRUD 实现完，用一份真实的工作流配置验证数据模型能正确存储和还原。

```bash
# 创建工作流
curl -X POST http://localhost:8080/api/v1/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "name": "智能客服分类工作流",
    "nodes": [
      {"nodeKey": "classify", "type": "LLM", "name": "问题分类",
       "config": {"prompt": "判断问题类型，返回：售前/售后/技术支持", "outputVariable": "intent"}},
      {"nodeKey": "router", "type": "CONDITION", "name": "路由分发",
       "config": {"expression": "{{intent}}", "outputVariable": "route"}},
      {"nodeKey": "presale", "type": "LLM", "name": "售前咨询",
       "config": {"prompt": "你是产品顾问，介绍产品功能和优势", "outputVariable": "answer"}},
      {"nodeKey": "aftersale", "type": "LLM", "name": "售后服务",
       "config": {"prompt": "你是售后客服，回答退换货和保修问题", "outputVariable": "answer"}},
      {"nodeKey": "techsupport", "type": "LLM", "name": "技术支持",
       "config": {"prompt": "你是技术工程师，帮用户排查使用问题", "outputVariable": "answer"}}
    ],
    "edges": [
      {"sourceNodeKey": "classify",  "targetNodeKey": "router",      "condition": null},
      {"sourceNodeKey": "router",    "targetNodeKey": "presale",     "condition": "售前"},
      {"sourceNodeKey": "router",    "targetNodeKey": "aftersale",   "condition": "售后"},
      {"sourceNodeKey": "router",    "targetNodeKey": "techsupport", "condition": "技术支持"}
    ]
  }'

# 查询详情，验证能完整还原
curl http://localhost:8080/api/v1/workflows/1
# 返回的结构应和创建时一致：五个节点都在，四条边都在，config 没有丢失字段

# 给 Agent 绑定工作流
curl -X PUT http://localhost:8080/api/v1/agents/1 \
  -H "Content-Type: application/json" \
  -d '{"workflowId": 1}'
```

验收标准只有一个：创建进去的配置，查询出来能完整还原。不多不少，节点对齐，边对齐，config JSON字段不丢失。

# 23｜工作流编排（下）：实现执行引擎，让工作流跑起来

22讲我们把工作流的元数据存进去了，但它只是一份静态配置，存进去读出来，就是不会动，这一讲让它动起来。怎么让它动起来呢？就是我们这节课要讲的执行引擎。

**执行引擎是什么**

```
工作流执行引擎是什么概念？
它和 22 讲存的工作流配置是什么关系？
怎么被触发？从用户发消息到工作流执行完毕返回结果，完整链路是什么样的？
不要讲理论，结合 Hify 智能客服的场景解释。
```

WorkflowServiceImpl 是工作流的元数据的存储，它是管配置的。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/23-工作流编排（下_972505_a3fe963edc.png)

执行引擎是从数据库加载配置，构建 `nodeMap + edgeMap`，然后从起始节点开始一个节点一个节点地执行，最终结果通过 SseEmitter 推给用户。

**业界怎么做**

```
工作流执行引擎在业界有哪些主流的实现方案？
重点看 Dify、Coze、n8n 这类 AI 应用平台是怎么设计的。
我想了解：线程模型怎么选、节点执行怎么隔离、上下文数据怎么在节点间传递、错误处理和执行记录怎么做。
最后给我一个建议：Hify 这种体量的项目应该选哪种方案，为什么。
```

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/23-工作流编排（下_972505_5a410e8e4b.png)

**执行引擎在代码里长什么样**

```
基于上面的调研结论，帮我把 Hify 执行引擎的代码结构梳理清楚。
四个部分：线程池、ExecutionContext、NodeExecutor 体系、核心循环。
每个部分是什么，相互之间怎么协作，用代码示例说明。
先把现有的代码都读清楚，不基于假设设计。
```

Claude Code 先把现有代码读完，`ThreadPoolConfig.java`、`NodeConfigDef.java`、`NodeConfigParser.java`、`WorkflowNode.java`、`LlmHttpClient.java` 等，然后基于真实代码给出设计。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/23-工作流编排（下_972505_c0295f5427.png)

ExecutionContext：贯穿整个工作流的变量池。对标 Dify 的 VariablePool。一次执行创建一个，从 START 节点活到 END 节点。

```java
public class ExecutionContext {
    private final Map<String, Object> variables = new LinkedHashMap<>();

    public ExecutionContext(Long workflowRunId, String userMessage) {
        variables.put("start.userMessage", userMessage);  // 预写入，后续节点用 {{start.userMessage}} 引用
    }

    public void set(String nodeKey, String varName, Object value) {
        variables.put(nodeKey + "." + varName, value);
    }

    // 把 "根据以下内容判断意图：{{start.userMessage}}" 替换为实际值
    public String resolve(String template) {
        String result = template;
        for (Map.Entry<String, Object> entry : variables.entrySet()) {
            result = result.replace("{{" + entry.getKey() + "}}",
                entry.getValue() != null ? entry.getValue().toString() : "");
        }
        return result;
    }
}
```

NodeExecutor 体系：四种 Executor，Spring 自动注册到 Registry，按 type 分发。

```java
public interface NodeExecutor {
    void execute(WorkflowNode node, NodeConfigDef config, ExecutionContext ctx);
    String nodeType();
}
```

1. `LlmNodeExecutor`：解析 config 里的 promptTemplate，用 `ctx.resolve()` 替换模板变量，复用已有的 ProviderAdapter 调 LLM，把返回内容写入 ctx。
2. `ConditionNodeExecutor`：解析 expression，`ctx.resolve()` 替换变量后做字符串匹配，把 true / false 写入 ctx。
3. `ApiCallNodeExecutor`：解析 url，替换变量后用 `LlmHttpClient` 调外部接口，把响应写入 ctx。
4. `KnowledgeNodeExecutor`：调 `KnowledgeService.searchChunks()`，把检索结果拼成字符串写入 ctx，后续 LLM 节点用 `{{kb.docs}}` 引用。

核心循环：WorkflowEngine。把前三件事串起来，加上执行记录。骨架就是一个while循环：

```java
public String execute(Long workflowId, String userMessage) {
    // 1. 从 DB 加载配置，构建内存结构
    Map<String, WorkflowNode> nodeMap = loadNodeMap(workflowId);
    Map<String, List<WorkflowEdge>> edgeMap = loadEdgeMap(workflowId);

    // 2. 创建执行记录 + Context
    WorkflowRun run = createRun(workflowId, userMessage);
    ExecutionContext ctx = new ExecutionContext(run.getId(), userMessage);

    // 3. 从 START 节点开始逐节点执行
    String currentKey = findStartKey(nodeMap);
    while (currentKey != null) {
        WorkflowNode node = nodeMap.get(currentKey);
        if ("END".equals(node.getType())) break;

        WorkflowNodeRun nodeRun = createNodeRun(run.getId(), node);
        try {
            NodeConfigDef config = configParser.parse(node.getType(), node.getConfig());
            executorRegistry.get(node.getType()).execute(node, config, ctx);
            finishNodeRun(nodeRun, "SUCCESS", ctx.snapshot(), null, elapsed);
        } catch (Exception e) {
            finishNodeRun(nodeRun, "FAILED", ctx.snapshot(), e.getMessage(), elapsed);
            throw e;  // 向外抛，外层更新 run 状态
        }

        currentKey = pickNext(edgeMap, currentKey, node.getType(), ctx);
    }

    // 4. 取最终输出
    String output = resolveEndOutput(nodeMap, ctx, currentKey);
    finishRun(run, "SUCCESS", output, null);
    return output;
}
```

**前端**

先说说工作流前端真正应该是什么样子。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/23-工作流编排（下_972505_bedf8a3df6.png)

完整的工作流前端是可视化拖拽编排：节点从左侧面板拖进画布，节点之间连线，点击节点在右侧面板配置 Prompt 和参数。Dify、Coze、n8n 都是这个形态。

> 用 React Flow 或 Vue Flow 库就可以实现。

我们本次做最简版：列表页 + 创建页，JSON直接手写提交。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/23-工作流编排（下_972505_1b41e9a3dd.png)

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/23-工作流编排（下_972505_ce8b0d7bc9.png)

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/23-工作流编排（下_972505_fe5237aa12.png)

# 24｜MCP 工具接入（上）：搞懂协议，把 Client 跑通

这一讲搞懂协议，把 Client 跑通。下一讲开发真实的 MCP Server。

**为什么不直接调API**

智能客服要对接的系统不止一个，订单系统、库存系统、工单系统、物流系统，每个系统的API格式都不一样：

```
订单系统：POST /orders/query，JSON，Bearer Token
物流系统：GET  /tracking?waybillNo=SF123，XML，签名验证
工单系统：GraphQL，OAuth2
库存系统：gRPC，proto 文件
```

让 Hify 直接对接每个系统，就要为每个系统写一套适配代码，处理不同的参数格式、认证方式、返回结构。

更麻烦的是，LLM 怎么知道有哪些工具可用？你得手动写进 Prompt，每接一个新系统，就要改 Prompt。

Anthropic 在 2024年 底提出了 MCP 协议来解决这个问题。

**MCP是什么**

```
MCP 协议是什么？它解决什么问题？
和直接调 REST API 有什么区别？
用智能客服的场景帮我解释，重点说清楚为什么需要标准化协议。
```

MCP 是工具的标准化描述和调用协议。工具提供方按 MCP 标准暴露自己的能力，调用方通过统一方式发现和调用这些工具。

Tool Schema：每个工具的标准描述，包括名称、说明、参数类型等。LLM 通过 Schema 知道有哪些工具可用，决定什么时候调哪个。

```json
{
  "name": "query_order",
  "description": "根据用户ID和订单号查询订单状态，当用户询问订单、物流、快递相关问题时使用",
  "inputSchema": {
    "type": "object",
    "properties": {
      "userId":  {"type": "string", "description": "用户ID"},
      "orderId": {"type": "string", "description": "订单号，不知道时传空字符串"}
    },
    "required": ["userId"]
  }
}
```

MCP 之前，M个 AI 平台 × N个工具 = M×N 套适配代码。MCP之后，工具开发者只写一个 Server，任何支持 MCP 的平台都能接 = M+N。这和 USB 解决的问题一样。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/24-MCP工具接入_972992_b60654207d.png)

**Function Calling是什么**

知道了MCP是什么，下一个问题：LLM怎么知道要调哪个工具？

```
Function Calling 是什么？
LLM 怎么知道有哪些工具可用？
怎么决定什么时候调工具、调哪个、传什么参数？
一次用户对话如果需要调工具，完整的交互流程是什么样的？
```

LLM 本质上只能输入文本、输出文本。Function Calling 是一种约定，LLM 的输出文本里，有时候不是给用户看的回答，而是一个结构化的“我要调这个函数、传这些参数”的指令。

LLM 怎么知道有哪些工具？工具定义随每次请求一起发过去。不是持久记忆，是每次都告知。

```json
{
  "messages": [{"role": "user", "content": "我昨天下的订单还没到"}],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "query_order",
        "description": "查询订单状态，当用户询问订单、物流、快递相关问题时使用",
        "parameters": { ... }
      }
    }
  ]
}
```

LLM 怎么决定调哪个工具？靠 `description` 字段。LLM 读到“我昨天下的订单还没到”，判断这是订单问题，`query_order` 的 description 说“用户询问订单相关问题时使用”，场景匹配，调它。

下面是一次用户对话后的过程。

第一次 LLM 调用，LLM 判断需要调工具，返回的是工具调用指令：

```json
{
  "finish_reason": "tool_calls",
  "message": {
    "tool_calls": [{
      "id": "call_abc123",
      "function": {
        "name": "query_order",
        "arguments": "{\"userId\": \"u001\", \"orderId\": \"12345\"}"
      }
    }]
  }
}
```

Hify 拿到指令，通过 MCP Client 调订单服务，拿到真实数据，把结果追加进对话历史：

```json
{"role": "tool", "tool_call_id": "call_abc123",
 "content": "{\"status\":\"运输中\",\"trackingNo\":\"SF1234567\",\"estimatedDate\":\"明天\"}"}
```

第二次 LLM 调用，LLM 基于工具结果生成最终回答，`finish_reason` 变成 `stop`，这次是真正给用户的回答。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/24-MCP工具接入_972992_963fedc7c4.png)

循环次数由 LLM 决定，不是固定的。理论上 LLM 可以连续调多个工具（先查订单再查物流），Agent 框架一般设置最大轮次（比如10次）防止死循环。

**MCP Client选型**

```
Java 生态有哪些 MCP Client 的 SDK？
帮我调研主流选项，从成熟度、文档质量、和 Spring 生态兼容性几个维度对比。
最后给出建议，Hify 应该选哪个。
```

调研结果有三个实质选项：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/24-MCP工具接入_972992_391053b3ac.png)

Claude Code的建议：用官方Java SDK，不用Spring AI MCP。

```xml
<!-- hify-mcp/pom.xml -->
<dependency>
    <groupId>io.modelcontextprotocol.sdk</groupId>
    <artifactId>mcp</artifactId>
    <version>1.1.1</version>
</dependency>

```

> Hify 已经有自己的一套：`ProviderAdapter` 适配各LLM、`LlmHttpClient` 做HTTP 通信、`ChatServiceImpl` 管对话流程。
>
> 引入Spring AI MCP 意味着：引入整个 `spring-ai-bom`，工具调用结果要适配 `ToolCallback` 接口，这和现有 `ProviderAdapter` 冲突。
>
> 官方 Java SDK 只做一件事：实现 MCP 协议的序列化/反序列化和请求响应。不绑定任何 AI 框架，剩下的连接管理、异常处理、工具结果转换全按 Hify 现有风格写。

**动手实现**

MCP Server管理

```
在 hify-mcp 模块中实现 MCP Server 管理。参照 12 讲 Provider 管理的模式。

接口列表：
POST   /api/v1/mcp-servers              创建 MCP Server（name、endpoint、enabled）
GET    /api/v1/mcp-servers              分页查询列表
GET    /api/v1/mcp-servers/{id}         查询详情（含工具列表）
PUT    /api/v1/mcp-servers/{id}         更新
DELETE /api/v1/mcp-servers/{id}         逻辑删除
POST   /api/v1/mcp-servers/{id}/test    测试连通性

连通性测试逻辑：
  用 io.modelcontextprotocol.sdk:mcp:1.1.1 的 McpSyncClient
  调 tools/list 接口，成功则把返回的工具列表存入 mcp_tool 表
  （name、description、inputSchema JSON 字段）
  失败返回错误信息

删除时检查：是否有 Agent 绑定了该 Server 的工具，有则拒绝删除

实现 McpClientService：
  callTool(mcpServerId, toolName, arguments) → String
    按调用创建 McpSyncClient，用完关闭（try-with-resources）
    工具调用失败 catch 住，抛 BizException(MCP_TOOL_CALL_FAILED)
    结果取 TextContent，多条用换行拼接

  listTools(mcpServerId) → List<String>
    同样 try-with-resources，失败抛 BizException(MCP_SERVER_NOT_FOUND)

代码放在 hify-mcp 模块，遵循 CLAUDE.md 规范
```

Agent绑定工具

```
新建 agent_tool 关联表，支持多工具绑定：

CREATE TABLE agent_tool (
    id        BIGINT   AUTO_INCREMENT PRIMARY KEY,
    agent_id  BIGINT   NOT NULL,
    tool_id   BIGINT   NOT NULL,
    created_at DATETIME NOT NULL,
    UNIQUE KEY uk_agent_tool (agent_id, tool_id)
);

实现接口：
PUT /api/v1/agents/{id}/tools    绑定工具列表（传 toolId 数组，全量替换）

约束：
- 绑定时校验 toolId 是否存在且对应 MCP Server 处于启用状态
- 一个 Agent 最多绑定 10 个工具（防止 tools 参数过长影响 LLM 效果）
```

接入对话引擎

```
修改 ChatService 的对话逻辑，加入 MCP 工具调用支持。

改动范围：只改 buildMessages 和 LLM 调用这两处。

具体逻辑：
1. 加载 Agent 绑定的工具列表
   从 agent_tool 关联 mcp_tool 表，拿到所有工具的 name、description、inputSchema
2. 工具列表不为空时，把 tool schema 加入第一次 LLM 调用的 tools 参数
3. 第一次 LLM 调用后判断返回：
   finish_reason = "tool_calls"：解析 tool_calls，执行第 4 步
   finish_reason = "stop"：直接走原有流式推送逻辑
4. 解析 tool_calls，拿工具名和 arguments JSON
   从 mcp_tool 表找到对应的 mcpServerId
   调 McpClientService.callTool(mcpServerId, toolName, arguments)
5. 把工具结果作为 role=tool 的消息追加进对话历史
   对应上 tool_call_id（LLM 第一次返回的那个 id）
6. 发起第二次 LLM 调用（流式），结果推给用户

约束：
- 工具列表为空时，和原有逻辑完全一致，一行不改
- RAG 和工具调用不冲突：system prompt 里既可以有 RAG 检索结果，
  也可以有工具 schema，一个 Agent 可以同时绑知识库和工具
- workflowId 不为空时已经 return，不进入这段逻辑
- 工具调用失败：把错误信息作为 tool 消息返回给 LLM，
  让 LLM 告知用户，不要直接抛异常中断对话
- 不改 Controller 层，不改 SseEmitter 管理逻辑
```

下面是我们实现的在 MCP 工具的管理：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/24-MCP工具接入_972992_3350699525.png)



# 26





































