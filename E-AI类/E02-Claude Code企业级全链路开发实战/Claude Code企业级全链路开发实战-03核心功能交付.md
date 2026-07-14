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

![img](https://static001.geekbang.org/resource/image/07/cb/077c8ba2b07501f978ee9ddb080921cb.png?wh=1850x418)

按认证方式分：Bearer Token（OpenAI、DeepSeek）、自定义 Header（Anthropic 用 x-api-key）、URL 参数（Gemini）、无认证（Ollama）、JWT 自签名（智谱 GLM）。由于这个差异，auth_config 我们决定使用 JSON 存储。

按消息格式分：OpenAI 格式（大多数）、Anthropic 独立 system 字段、Gemini 完全不同格式（contents + parts）。这个差异决定了后面适配层要怎么设计。

基于这个分析，我的判断，一期支持三种类型加一个通用兼容：

![img](https://static001.geekbang.org/resource/image/7a/88/7ab378297b885b468045578bafb7cd88.png?wh=1746x512)

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

![img](https://static001.geekbang.org/resource/image/b0/21/b02005b99681947c2cf04df462464421.png?wh=1440x1102)

## 后端拆解执行

8 个任务，两三个小时全部交付。

![img](https://static001.geekbang.org/resource/image/08/ab/08217b68e115ba3756ec3d2e9f383eab.png?wh=2016x896)

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

![img](https://static001.geekbang.org/resource/image/ff/c3/ff86ac79907704b0cbdc7a6c12d9fcc3.png?wh=1440x866)

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

![img](https://static001.geekbang.org/resource/image/c3/d9/c3aa65419200d64db34398c793b1b9d9.png?wh=1440x804)

**第二步：让 Claude Code 告诉你别人怎么用 Skill**

```
业界用 Claude Code Skill 的最佳实践有哪些？大家一般用 Skill 解决什么问题？给我列举一些常见的 Skill 类型和使用场景。
```

![img](https://static001.geekbang.org/resource/image/86/3d/8636f8c3009d3973fc4e7cfcd83eb43d.png?wh=1440x862)

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

![img](https://static001.geekbang.org/resource/image/e3/78/e379b0733f9c65b431f575yyfb7a4478.png?wh=1974x652)

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

![img](https://static001.geekbang.org/resource/image/c2/b0/c201732bb05f9e431c5fa7d277bbe1b0.png?wh=1440x848)

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

![img](https://static001.geekbang.org/resource/image/c0/36/c0135b123afe8e39661b86d32b85b836.png?wh=1440x1016)





**从 Agent 到 LLM 应用：智能客服**



**拆解 Agent 的 CRUD**



# 16｜对话引擎（上）：理解对话链路与流式技术选型



# ==核心功能交付：高级篇==

