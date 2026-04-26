> 来自极客时间《Claude Code工程化实战》--黄佳

# <mark>子代理（03~08）</mark>

# 03｜分而治之：Sub-Agents的核心概念与应用价值

从这一讲开始，我们将进入本课程的第一个核心内容——子代理（Sub-Agents）。

**什么是子代理？**

子代理相当于一个“专职小助手”，带着自己的规则、工具权限、上下文窗口，去完成某一类任务，然后把“结果摘要”带回来。

子代理的工程价值，本质上就是三件事：隔离、约束、复用。

- 隔离（解决的是上下文污染问题）

应用场景1：高噪声输出的任务。例如跑一次测试会输出几百行日志，但你只想知道通过还是失败；

应用场景2：可以并行展开的研究型任务。当你需要对比几种技术方案、从多个视角分析同一个问题时，这些探索之间往往是相互独立的。与其在主对话里来回切换，不如让多个子代理各自去完成自己的探索，再把结果汇总回来。

应用场景3：可以拆成清晰阶段的流水线式任务。比如先定位代码位置，再做代码审查，然后进行修改，最后跑测试验证。

- 约束（解决的是行为不可控问题）

应用场景：角色边界必须非常明确的任务。例如：让代码审查只能读、修 bug 才能写，角色职责不再依赖提示词自觉。

```markdown
# 只读型子代理（代码审查）
tools: Read, Grep, Glob
# 它只能看，不能改任何东西

# 开发型子代理（bug 修复）
tools: Read, Write, Edit, Bash
# 它可以读写文件和执行命令

# 研究型子代理（技术调研）
tools: Read, WebFetch, WebSearch
# 它可以读本地文件和搜索网络
```

- 复用（解决的是经验无法沉淀的问题）

当子代理被定义成文件、放进版本控制后，好的使用方式就从一次性对话，变成了可共享、可迭代的工程资产。

> 一条关键约束：子代理不能生成子代理。这意味着：
>
> 1. 所有编排必须由主对话完成：如果你需要“先审查再修复”，必须由主对话依次调用两个子代理，而不是让第一个子代理去调用第二个
> 2. 流水线的“调度中心”只有一个：就是主对话本身（后续第 6 讲会深入讨论这一点）
> 3. 如果需要在子代理内复用知识：用  skills 字段预加载（而非再嵌套一个子代理），后面配置详解中我们会讲到。

**内置子代理：开箱即用的“好员工”**

当你问 Claude——“给我解释解释这个 Github 代码库”时，在不知不觉间，Claude Code 就会自动调用内置子代理。

下面简单介绍其中的三个。

- Explore 子代理

Explore 子代理负责“翻项目、找位置”，专注快速只读搜索，把成百上千行 grep 和分析过程吞进去，只告诉你结论在哪里。

当你问 Claude“这个项目的认证逻辑在哪里”时，它会自动派出 Explore 子代理去搜索，而不是在主对话中一行行地执行 grep 命令。

- Plan 子代理

Plan 子代理负责“动手前先想清楚”，在真正修改代码之前，收集上下文、梳理依赖、生成实施路径，避免一上来就盲目修改。

当你让 Claude 进入规划模式时，它会用 Plan 子代理来收集信息，设计实施方案。

- General-purpose 子代理

General-purpose 子代理则是“能探索、能修改、能推进”的全能型员工，适合需要多步骤协作的复杂任务。

当任务比较复杂，需要多种能力配合时，就可以使用这个通用型子代理。这些子代理的共同点只有一个：把高噪声过程留在子代理里，让主对话只保留决策信息。

## 子代理配置文件详解

子代理使用  Markdown + YAML frontmatter 格式：

```markdown
---
name: code-reviewer
description: Review code for security issues and best practices. Use after code changes.
tools: Read, Grep, Glob
model: sonnet
---

你是一个代码审查专家。

当被调用时：

1. 首先理解代码变更的范围
2. 检查安全问题
3. 检查代码规范
4. 提供改进建议

输出格式：
## 审查结果
- 安全问题：[列表]
- 规范问题：[列表]
- 建议：[列表]
```

字段详解如下。

| 字段            | 必填 | 说明                                               | 示例                                                         |
| --------------- | ---- | -------------------------------------------------- | ------------------------------------------------------------ |
| name            | 是   | 唯一标识符，使用小写字母和连字符                   | code-reviewer                                                |
| description     | 是   | **最重要的字段！** Claude 据此决定何时自动委派任务 | Review code for security issues. Use proactively after code changes. |
| tools           | 否   | 工具白名单（逗号分隔）。省略则继承主对话的全部工具 | Read, Grep, Glob                                             |
| disallowedTools | 否   | 工具黑名单，从继承列表中排除指定工具               | Write, Edit                                                  |
| model           | 否   | 模型选择。省略则默认为 inherit                     | haiku / sonnet / opus / inherit                              |
| permissionMode  | 否   | 权限模式，控制子代理如何处理权限弹窗               | default / plan / bypassPermissions 等                        |
| skills          | 否   | 启动时预加载的 Skill 列表，注入为上下文            | [api-conventions, error-handling]                            |
| hooks           | 否   | 子代理专属的生命周期 Hook                          | 见后续 Hook 章节                                             |

**description 的设计艺术**

```
# 好的 description：说明做什么 + 什么时候用
description: Review code changes for quality, security vulnerabilities, and best practices. Use proactively after code is modified or when user asks for code review.
```

**tools vs disallowedTools：白名单与黑名单**

```
# 方式一：白名单 (tools) — "只能用这些"
# 适合：需要严格限制的场景（如只读审查）
tools: Read, Grep, Glob

# 方式二：黑名单 (disallowedTools) — “继承所有，但排除这些”
# 适合：需要大部分工具但排除少数危险工具的场景
disallowedTools: Write, Edit
```

以下是根据用途划分的典型工具组合：

- 只读型（审计/检查）：Read, Grep, Glob
- 研究型（信息收集）：Read, Grep, Glob, WebFetch, WebSearch
- 开发型（读写改）：Read, Write, Edit, Bash, Glob, Grep

**model：模型选择与默认值**

| 场景          | 推荐模型 | 原因           |
| ------------- | -------- | -------------- |
| 简单搜索/grep | haiku    | 快且便宜       |
| 代码审查/分析 | sonnet   | 平衡性能和成本 |
| 复杂推理/架构 | opus     | 最强能力       |
| 与主对话一致  | inherit  | 保持一致性     |

**permissionMode：权限模式**

permissionMode 控制子代理在执行过程中遇到需要权限的操作时如何处理。子代理会继承主对话的权限上下文，但可以通过此字段覆盖行为：

| 模式              | 行为                                       | 适用场景             |
| ----------------- | ------------------------------------------ | -------------------- |
| default           | 标准权限检查，每次弹出确认                 | 大多数场景           |
| acceptEdits       | 自动接受文件编辑操作                       | 受信任的修复类子代理 |
| plan              | 只读探索模式                               | 规划和审查类子代理   |
| dontAsk           | 自动拒绝权限弹窗（已显式允许的工具仍可用） | 严格受限的自动化场景 |
| bypassPermissions | 跳过所有权限检查（谨慎使用！）             | 完全受信任的自动化   |

举个例子，如果你希望子代理能跑  git diff 但绝不能修改文件，可以这样配置：

```
---
name: code-reviewer
tools: Read, Grep, Glob, Bash
permissionMode: plan          # 强制只读模式，即使有 Bash 也无法写入
---
```

**skills：为子代理预加载知识**

skills 字段允许你在子代理启动时，把指定 Skill 的完整内容注入到子代理的上下文中。这意味着子代理不需要在执行过程中发现和加载 Skill——知识已经在它的脑子里了。

```
---
name: impact-analyzer
description: Analyze impact scope of code changes on the full call chain.
tools: Read, Grep, Glob, Bash
skills:
  - chain-knowledge        # 链路拓扑和 SLA 约束
  - recent-incidents       # 近期事故记录
---
```

**hooks：子代理专属的生命周期 Hook**

```
---
name: db-reader
description: Execute read-only database queries.
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---
```

上面的例子中，db-reader 虽然拥有 Bash 工具，但每次执行 Bash 命令前都会被 Hook 拦截验证——只有 SELECT 查询能通过，INSERT/UPDATE/DELETE 等写操作会被阻止。这比不给 Bash 工具更灵活（允许读操作），又比无约束的 Bash 更安全。

## 子代理的存放位置与优先级

| 位置                     | 作用域                 | 优先级    | 适用场景                              |
| ------------------------ | ---------------------- | --------- | ------------------------------------- |
| `--agents` CLI 参数      | 仅当次会话             | 1（最高） | 临时测试、CI/CD 自动化                |
| `.claude/agents/`        | 当前项目               | 2         | 项目特有的子代理，提交到 git 团队共享 |
| `~/.claude/agents/`      | 所有项目               | 3         | 个人通用子代理                        |
| Plugin 的 `agents/` 目录 | 启用了该 Plugin 的项目 | 4（最低） | 通过插件分发的子代理                  |

## 创建子代理的三种方式

**方式一：交互式创建（推荐新手使用）。**在 Claude Code 中输入  /agents，按照向导操作；

```
步骤 1：输入 /agents
步骤 2：选择 "Create new agent"
步骤 3：选择存放位置（User-level 或 Project-level）
步骤 4：选择 "Generate with Claude" 并描述功能
步骤 5：选择需要的工具
步骤 6：选择模型
步骤 7：保存
```

这种方式简单直观，Claude 会帮你生成初始的 prompt。

**方式二：手写配置文件。**直接创建  .claude/agents/your-agent.md 文件。其优势是更精细的控制，方便版本管理，可以从其他项目复制。

**方式三：CLI 参数临时创建。**通过  --agents 参数，可以在启动 Claude Code 时传入 JSON 格式的子代理定义。

这种方式创建的子代理仅在当前会话中存在，不会保存到磁盘。特别适合 CI/CD 自动化时在流水线中临时创建任务专用的子代理。

## 子代理的运行模式

| 模式 | 行为                                     | 适用场景                 |
| ---- | ---------------------------------------- | ------------------------ |
| 前台 | 阻塞主对话，权限弹窗和问题会实时传递给你 | 需要人工审批或交互的任务 |
| 后台 | 并行执行，你可以继续在主对话中工作       | 独立的探索或分析任务     |

Claude 会根据任务自动选择前台或后台。你也可以手动控制。

- 对 Claude 说 “run this in the background”
- 正在运行的前台子代理可以按  Ctrl+B 切换到后台

每个子代理执行完成后，Claude 会自动收到它的  agent ID。如果你需要在之前的子代理基础上继续工作，可以让 Claude 恢复（Resume）它：

```
用 code-reviewer 子代理审查认证模块
[子代理完成]

继续刚才的审查，再看一下授权逻辑
[Claude 恢复之前的子代理，保留完整上下文]
```



# ==04｜量体裁衣：从Sub-Agents到Multi-Agent的工程指南==

这节课的目标是帮你建立一种可以立刻用于拆解当下热门产品，也能长期指导工程设计的通用方法论。学完今天的内容，你不仅能更好地理解 Sub-Agent、Skills 这些概念， 也会更清楚：什么时候该用，什么时候不该用。

## 何时该升级到多 Agent？

LangChain 在其架构选型指南中给出了明确建议：“Start with a single agent. Add tools before adding agents. Graduate to multi-agent patterns only when encountering clear architectural limits.” （先从单 Agent 起步，优先通过引入工具扩展能力； 只有当系统确实触及单 Agent 的架构边界时， 才考虑采用多 Agent 的设计模式。）

架构边界是什么？两个核心触发条件：

- 信号一：上下文管理挑战

  当多个能力领域的专业知识无法舒适地塞进单一 prompt 中时——你需要策略性地分发上下文，而不是把所有东西堆在一起。

- 信号二：分布式开发需求
  
  当多个团队需要独立拥有和维护各自的 Agent 能力时，各团队可以独立迭代而不互相干扰。

下面我们从工程视角出发，系统梳理 Sub-Agent 到 Multi-Agent 的四种核心设计模式，并给出性能、成本、可控性三个维度的决策框架。

## 四种核心设计模式

**模式一：Sub-Agents（子代理委派）**

Sub-Agents 的核心设计思想是一个 Supervisor Agent 充当老板，将任务分解后委派给专门的 Sub-Agent。每个 Sub-Agent 解决一个特定的任务。

```
                  +---------------+
                  |  Supervisor   |
                  |  主 Agent     |
                  +---------------+
                          |
        +-----------------+-----------------+
        ↓                 ↓                 ↓
+---------------+ +---------------+ +---------------+
|  Sub-Agent A  | |  Sub-Agent B  | |  Sub-Agent C  |
| （搜索专家）    | | （分析专家）   | | （写作专家）   |
+---------------+ +---------------+ +---------------+
```

> Anthropic 的 Research 功能采用了经典的 Sub-Agent 模式：
>
> 1. LeadResearcher（Claude Opus 4）分析查询、制定策略
> 2. 并行派出  3-5 个 SubAgent（Claude Sonnet 4），各自独立搜索
> 3. 每个 SubAgent 执行 3+ 个并行工具调用
> 4. CitationAgent 处理引用和来源归属
> 5. 结果汇聚回 LeadResearcher 综合输出
>
> 工程评测显示，并行化的 Sub-Agent 执行方式可将复杂查询的整体研究时间最多缩短约 90%，但其代价是相较普通对话约 15 倍的 token 消耗；

**模式二：Skills（渐进式能力加载）**

通过 SKILL.md 文件（或类似配置）实现能力的渐进式加载。Agent 一开始只知道技能的名称和描述，当判断需要某个技能时，才加载完整的指令。

```
                +-------------------------+
                |       Single Agent      |
                |       知道技能名称       |
                +-------------------------+
                             |按需加载
         +-------------------+-------------------+
         ↓                   ↓                   ↓
+-----------------+ +-----------------+ +-----------------+
|    SKILL.md     | |    SKILL.md     | |    SKILL.md     |
|     deploy      | |     review      | |     testing     |
+-----------------+ +-----------------+ +-----------------+
             技能不是独立 Agent，而是“指令文件”
```

> 在 Skills 模式下，系统仍然由单一 Agent 负责全部推理与执行，所有技能共享同一个上下文窗口。
>
> ```
> .claude/skills/           
> ├── deploy/
> │   └── SKILL.md          # 部署技能的完整指令
> ├── review-pr/
> │   └── SKILL.md          # PR 审查技能的指令
> └── database-migration/
>        └── SKILL.md          # 数据库迁移技能的指令
> ```

**模式三：Handoffs（交接）**

Handoffs 的核心思想是活跃的 Agent 根据对话状态动态切换。Agent A 完成自己的阶段后，通过调用  handoff() 工具将控制权（和上下文）传递给 Agent B。

```
┌──────────┐ handoff()   ┌─────────┐  handoff() ┌─────────┐
│ Agent A  │ ──────────> │ Agent B │ ─────────> │ Agent C │
│ 收集信息  │             │ 方案设计 │            │ 执行修复 │
└──────────┘             └─────────┘            └─────────┘
      │                                             ↑
      └─────────────────────────────────────────────┘
                   对话上下文随 handoff 传递
```

> Handoffs 的典型应用是客服工单流程：
>
> ![img](https://static001.geekbang.org/resource/image/6d/a3/6d7ff1533244f6bb9253b78745d1fca3.jpg?wh=2857x1796)

**模式四：Router（路由器 / 并行分发与合成）**

Router 模式的核心在于对输入进行语义拆分与职责分流。系统首先由 Router 对用户请求进行分类和分解，然后将子查询并行分发给各自负责的专业 Agent，最后再将多个结果统一合成为一个对用户友好的响应。

```
             ┌─────────────────┐
             │Router(分类+分发) │
             └────────┬────────┘
                  并行分发
        ┌─────────────┼──────────────┐
        ↓             ↓              ↓
   ┌───────────┐ ┌───────────┐ ┌───────────┐
   │SpecialistA│ │SpecialistB│ │SpecialistC│
   └────┬──────┘ └────┬──────┘ └─────┬─────┘
        └─────────────┼──────────────┘
                   合成结果
                      ↓
             ┌─────────────────┐
             │   Synthesize    │
             └─────────────────┘
```

> 例如在企业知识库场景中，用户一次提问可能同时涉及政策文档、业务数据和实时指标，Router 可以将“退货政策”交由政策文档 Agent 处理，将“销售数据”交由数据分析 Agent 处理，并在上层完成结果整合后统一返回。
>
> ```
> 用户提问：「我们的退货政策是什么？最近的销售数据如何？」
>
> Router 分解：
> ├── 查询 1：退货政策 → 政策文档 Agent
> ├── 查询 2：销售数据 → 数据分析 Agent
> └── 合成结果 → 统一回答
> ```

## 性能、成本、可控性的量化对比

LangChain 对这四种模式做了实际的性能量化测试，分别从单任务请求的模型调用次数、重复请求的效率，和复杂问题的 Token 消耗三个方面进行了对比，结果非常有参考价值。

| 场景                                                 | 结果                                                         |
| ---------------------------------------------------- | ------------------------------------------------------------ |
| 场景一：单任务请求（如“帮我修改函数支持分页查询”）   | ![img](https://static001.geekbang.org/resource/image/51/60/51732788764ca6cd668b5ee174759260.jpg?wh=2889x1616) |
| 场景二：重复请求效率（第二轮相同类型的请求）         | ![img](https://static001.geekbang.org/resource/image/c9/38/c9980a7bd08987bd0e9d593972fdee38.jpg?wh=3024x1604) |
| 场景三：多领域查询（如“对比 Python/JS/Rust 的性能”） | ![img](https://static001.geekbang.org/resource/image/07/bf/07a47c088e4361f761bbabee7d2330bf.jpg?wh=2933x1609) |

比较上面几个表的结论，可以看出：

- 简单任务中，Sub-Agent 模式有额外开销。
- 多轮对话中，有状态模式效率优势明显。
- 多领域查询中，上下文隔离的模式（Sub-Agent、Router）在 token 效率上优势显著——节省 40% 以上的 token 成本。

## 从 Sub-Agent 到 Multi-Agent 的架构演进路径

首先给出一个升级决策树：

```
你的任务需要多 Agent 吗？
├─ 单一领域、工具 < 5 个、上下文 < 50K tokens
│  └─→ 不需要。用单 Agent + 好的 prompt 即可
│
├─ 单一领域、但工具 > 10 个
│  └─→ 考虑 Skills 模式（渐进式能力加载）
│
├─ 多领域、各领域需要独立上下文
│  └─→ 使用 Sub-Agents 模式
│
├─ 需要多步骤状态流转（如客服工单流程）
│  └─→ 使用 Handoffs 模式
│
└─ 需要跨多个数据源并行查询
   └─→ 使用 Router 模式
```

下面是一个典型的项目架构演进路径。

**第一阶段：单 Agent + Tools**

适合大多数初期场景。不要过早引入多 Agent。

```
   ┌─────────┐
   │         │───────────> Tool A
   │         │
   │  Agent  │───────────> Tool B
   │         │
   │         │───────────> Tool C
   └─────────┘
```

**第二阶段：单 Agent + Skills**

当工具数量增多、prompt 变得臃肿时，用 Skills 实现渐进式加载。

```
   ┌─────────┐
   │         │───────────> Skill A
   │         │
   │  Agent  │───────────> Skill B
   │         │
   │         │───────────> Skill C
   └─────────┘
```

**第三阶段：Supervisor + Sub-Agents**

当不同领域需要独立的上下文空间和专业知识时引入。

```
   ┌──────────────┐
   │              │───────────> Sub-Agent A(领域专家)
   │              │
   │  Supervisor  │───────────> Sub-Agent B(领域专家)
   │              │
   │              │───────────> Sub-Agent C(领域专家)
   └──────────────┘
```

**第四阶段：混合架构**

成熟系统中，不同类型的任务流可能采用不同的模式。Router 处理分类，Sub-Agent 处理并行研究，Handoff 处理顺序流程。

```
                       Orchestrator
     ┌───────────┐     ┌──────────┐     ┌────────────┐
     │  Router   │     │Supervisor│     │Handoff Flow│
     └─────┬─────┘     └────┬─────┘     └──────┬─────┘
           ↓                ↓                  ↓
      ┌──────────┐     ┌──────────┐      ┌────────────┐
      │Agent Pool│     │SubAgents │      │Sequential  │
      │          │     │  (并行)   │     │  Agents     │
      └──────────┘     └──────────┘      └────────────┘
```

# 05｜明察秋毫 ：构建只读型安全审计子代理

> 示例工程：03-SubAgents/projects/01-code-reviewer

今天的目标就下面三个。

- 创建一个只有读取权限的代码审查子代理。
- 用它来发现示例代码中的安全问题。
- 体验“最小权限原则”的工程价值。

同时，我们也将从真实工程痛点出发，理解"为什么需要这个子代理"的设计思维。

## 项目场景：代码审查

一个后端开发项目中，我们刚刚好写完了一段认证逻辑，想让 Claude Code 帮你审查一下有没有安全问题。你在主对话中说：“帮我检查一下 auth.js 的安全性”。

Claude 完成这个任务当然不在话下，它读了你的代码，发现了硬编码的密钥，然后顺手帮你改成了环境变量读取。

这就是为什么我们需要只读型子代理。

下面我们一步一步往前走，从理解这些“问题代码”开始，到创建属于我们自己的“代码审查”Sub-Agent，并运行它们，同时验证权限边界、扩展审查维度，完成代码审查子代理的设计和使用闭环。

**第一步：理解“有问题”的代码**

在创建审查器之前，让我们先看看它要审查的代码有什么问题，以设计更好的审查 prompt。在我的 Repo 中，auth.js 存在大量的安全隐患。

```javascript
// 问题 1: 硬编码的密钥
// <这会导致一旦代码仓库泄露，密钥也随之暴露，且无法进行安全轮换>
const SECRET_KEY = 'super-secret-key-12345';
const API_KEY = 'sk-live-abcdef123456';

// 问题 2: 弱密码验证
function validatePassword(password) {
  // 只检查长度，没有复杂度要求
  // <这会降低攻击成本，使暴力破解、重放攻击和伪造身份成为可能>
  return password.length >= 6;
}

// 问题 3: 不安全的 token 生成
function generateToken(userId) {
  // 使用可预测的方式生成 token
  const timestamp = Date.now();
  return Buffer.from(`${userId}:${timestamp}`).toString('base64');
}

// 问题 4: 明文存储密码比较
function checkPassword(inputPassword, storedPassword) {
  // 应该使用 bcrypt 等哈希比较
  return inputPassword === storedPassword;
}

// 问题 5: 信息泄露的错误消息
function login(username, password) {
  const user = findUserByUsername(username);

  if (!user) {
    // 泄露用户是否存在
    throw new Error(`User '${username}' not found`);
  }

  if (!checkPassword(password, user.password)) {
    throw new Error('Invalid password');
  }

  return {
    token: generateToken(user.id),
    user: {
      // ...
      password: user.password,  // 问题 6: 返回密码！
    }
  };
}

// 问题 7: 无会话过期检查

// 问题 8: eval 使用 - 代码注入风险
function processUserConfig(configString) {
  return eval('(' + configString + ')');
}
```

**第二步：创建代码审查子代理**

创建.claude/agents/ 目录，然后在其中创建代码审查子代理的配置文件code-reviewer.md：

~~~markdown
---
name: code-reviewer
description: 审查代码变更的质量、安全性以及最佳实践。在代码修改后主动使用该子代理。
tools: Read, Grep, Glob, Bash
model: sonnet
---

你是一名资深代码审查员，精通安全审查与软件工程最佳实践。

## 调用时机

1. **识别变更**：运行 `git diff` 或读取指定文件
2. **分析代码**：从多个维度进行检查
3. **输出问题报告**：按严重程度分类

## 审查维度

### 安全性（最高优先级）
- SQL 注入漏洞
- XSS 漏洞
- 硬编码密钥/凭证
- 认证/授权问题
- 输入校验缺失
- 不安全的加密实践

### 性能
- N+1 查询模式
- 内存泄漏
- 异步代码中的阻塞操作
- 缺失缓存机会

### 可维护性
- 代码复杂度过高
- 缺少错误处理
- 命名规范较差
- 复杂逻辑缺少文档说明

### 最佳实践
- 违反 SOLID 原则
- 反模式
- 代码重复
- 类型安全缺失

## 输出格式

​```markdown
## 代码审查报告

### 严重问题
- [FILE:LINE] 问题描述
  - 问题影响
  - 建议修复方案

### 警告
- [FILE:LINE] 问题描述
  - 改进建议

### 建议
- [FILE:LINE] 可改进点

### 总结
- 问题总数：X
- 严重问题：X | 警告：X | 建议：X
- 整体风险评估：高/中/低
​```

### 审查准则
- 优先关注安全问题
- 明确指出具体位置（file:line）
- 提供可执行的修复建议
- 聚焦本次变更，而非既有代码（除非涉及安全关键问题）
- 说明保持简洁
~~~

tools 包括 Read，Grep，Glob，Bash 四种，此处是代码审查子代理最为关键的设计决策部分。

| 工具 | 用途                              | 为什么需要        |
| :--: | --------------------------------- | ----------------- |
| Read | 读取代码文件                      | 核心功能          |
| Grep | 搜索特定模式（如 eval、password） | 快速定位问题      |
| Glob | 匹配文件名模式                    | 找到所有 .js 文件 |
| Bash | 执行 git diff 等命令              | 查看改动          |

**第三步：运行代码审查**

1. 显式调用：

```
对Claude Code说：
“让 code-reviewer 审查 src/ 目录下的所有代码”
或者：
“用 code-reviewer 检查 src/auth.js 的安全问题”
```

2. Claude 自动调用

```
对Claude Code说：
“用子代理帮我看看代码有没有安全问题”

但是下面这样说，有可能无法触发子代理：
审查一下最近的改动 （因为没有明确提子代理）
检查一下代码质量（因为没有明确提子代理）
```

**第四步：验证权限边界**

在 Claude Code 中说：

```
让 code-reviewer 修复 auth.js 中的硬编码密钥问题
```

你会看到类似这样的响应：

```
code-reviewer 只有读取权限，无法修改文件。
如需修复问题，请使用其他方式或直接请求修改。
```

**第五步：扩展审查维度**

如果你的项目使用 React，可以在配置中添加框架特定检查。

```markdown
### React Specific
- 列表中缺少 `key` 属性
- 不必要的重复渲染（re-render）
- 直接修改 state（状态突变）
- 在 `useEffect` 中缺少清理逻辑（cleanup）
- Prop drilling 反模式
```

## 从代码审查到影响面分析——真实工程场景延伸

我分享一个课程留言区同学提到的真实线上事故场景：

> 他让 AI 按照 SDD 写了一个老功能的迭代并上线了。但在线上，用户端 7 秒拿不到操作结果。原因是什么？AI 并不知道这条链路上的改动会影响到哪些下游服务，也不知道端用户的体验 SLA 是多少。代码本身没有 bug，但全链路的影响面被忽略了。

这个案例的本质是什么？不是 AI 写错了代码，而是 AI 没有被告辞“在设计阶段就要审视影响面”的职责。

**把工程经验翻译成子代理设计**

让我们用“痛点驱动设计”思维来分析这个场景。

| 思考步骤        | 分析                                           |
| :-------------- | :--------------------------------------------- |
| 1. 痛点是什么   | 代码改动上线后影响了全链路性能，端用户体验劣化 |
| 2. 缺失了什么？ | AI 缺少"链路全局视图"和"SLA 约束"上下文        |
| 3. 该用什么机制 | SubAgent（影响面分析）+ Skill（链路知识沉淀）  |
| 4. 边界怎么画   | 只读分析，不做修改；在方案设计阶段就介入       |
| 5. 如何验证     | 给出改动涉及的链路节点清单，标注 SLA 风险      |

**设计一个影响面分析子代理**

基于上述分析，我们可以设计这样一个子代理：

~~~markdown
---
name: impact-analyzer
description: 分析代码变更在完整调用链上的影响范围。在对存量系统提交技术设计或 PR 之前使用。
tools: Read, Grep, Glob, Bash
model: sonnet
permissionMode: plan
skills:
  - chain-knowledge          # 链路拓扑和 SLA 约束
  - recent-incidents         # 近期事故记录（如有）
---

你是一名资深系统架构师，专注于对存量/既有系统进行影响面分析。

## 你的任务

当针对存量系统提出代码变更时，需要分析：
1. 此变更会影响哪些调用链（call chain）
2. 可能会影响哪些下游服务
3. 是否可能违反任何 SLA/性能约束
4. 变更作者可能尚未考虑到的边界情况（edge cases）

## 分析流程

1. **阅读变更文件**，理解具体做了哪些修改
2. **追踪调用链**：使用 Grep 查找所有变更函数/接口（function/API）的调用方
3. **检查集成点**：关注 HTTP 调用、消息队列（生产者/消费者）、以及会触及受影响表的数据库查询
4. **结合预加载的链路知识交叉验证**：使用启动时已注入到上下文中的链路拓扑与 SLA 约束
5. **评估 SLA 影响**：标记任何可能由于新增延迟或行为改变而影响面向用户响应时间的路径

## 输出格式

​```markdown
## 影响分析报告

### 变更组件
- [FILE:LINE] 变更描述

### 受影响的调用链
- 链路 1：ServiceA → ServiceB → **ChangedModule** → ServiceC → UserEndpoint
  - SLA 风险：新增的数据库查询可能会使该调用链在 3s 的 SLA 预算内增加约 200ms
  - 当前预算消耗：约 2.5s（估算）
  - 剩余余量：约 500ms → 变更后可能不足

### 下游影响
- [Service/Module] 受影响方式
  - 严重程度：HIGH/MEDIUM/LOW

### 未评审依赖
- 依赖于变更接口但尚未被分析的组件
  - 原因：超出当前仓库范围 / 上下文不足

### 建议
- [ ] 使用压测验证 SLA 余量
- [ ] 通知下游团队 X：该接口发生变更
- [ ] 为新增外部调用增加超时/熔断（timeout/circuit breaker）
​```

## 重要约束
- 你是只读（READ-ONLY）。不要建议去运行任何修改操作。
- 如果你缺少完整调用链的信息，请明确说明。不要猜测。
- 当你的分析因为缺少跨服务上下文而不完整时，务必标记出来。
~~~

**配合 Skill 沉淀链路知识**

对于存量系统，维护一个知识库（你的接口在整个链路是如何串联起来的），这样 AI 去改动现有代码的时候，就知道帮你排查这个改动影响了什么链路。

这就是 Skill 的用武之地，注意看上面 impact-analyzer 配置中的 skills 字段：

```
skills:
  - chain-knowledge          # 链路拓扑和 SLA 约束
  - recent-incidents         # 近期事故记录（如有）
```

子代理不会自动继承主对话中可用的 Skill。你必须在 skills 字段中显式列出需要的 Skill 名称，它才会被注入。

## 工程决策：什么时候该创建子代理？

**该创建子代理的场景**

![image-20260320152608269](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202603201526307.png)

**不该创建子代理的场景**

1. 一次性任务：直接在主对话中完成即可。
2. 简单的 prompt 模板：直接用 Skill 文件，不需要独立上下文和工具隔离。
3. 自动化触发动作：用 Hook，不需要 AI 分析判断。

# 06｜去芜存菁 ：高噪声任务处理——测试运行器与日志分析器

什么是高噪声输出？

测试运行是最典型的高噪声场景：输入npm test，输出几十到几百行日志。我们关心的只是通过 / 失败？失败了哪个？为什么？

子代理的价值就在这里：它去执行这些高噪声任务，然后只把结论带回主对话。但不是所有任务都需要子代理来处理，判断标准是信噪比。

这里有一个经验法则：如果一个命令的输出超过 50 行（行数也还要视具体情况而定），且你只关心其中不到 10 行（也就是不到五分之一）的内容，就应该用子代理。

## 项目一：测试运行器

实战项目位于  03-SubAgents/projects/01-test-runner/。

最关键的步骤是创建测试运行子代理，参考  .claude/agents/test-runner.md中的配置。

```markdown
---
name: test-runner
description: Run tests and report results concisely. Use this after code changes to verify everything works.
tools: Read, Bash, Glob, Grep
model: haiku
---

You are a test execution specialist.

When invoked:

1. First, identify the test command by checking package.json or common patterns:
   - Node.js: `npm test` or `node **/*.test.js`
   - Python: `pytest` or `python -m unittest`
   - Go: `go test ./...`

2. Run the tests and capture the output

3. Analyze the results and provide a **concise summary**:

## Output Format

------------
## Test Results

**Status**: PASS / FAIL
**Total**: X tests
**Passed**: X
**Failed**: X

### Failed Tests (if any)
- test_name: brief reason

### Recommendations (if failures)
- What to check/fix
------------

## Guidelines

- Keep the summary SHORT - the user doesn't want to see raw logs
- Focus on actionable information
- Group similar failures together
- If all tests pass, just say so briefly
```

我们重点看一下最后一行，haiku 是一个关键决策：为什么用 haiku 而不是 sonnet？

因为测试运行器的任务相对简单：执行命令是固定化流程，解析输出是模式匹配任务，生成报告只需按模板填充即可。这些任务  haiku 完全胜任，而且更快、更便宜。

> 各种模型所适合的场景：
>
> ![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202603241645393.jpeg)

使用测试运行器：

```
- 让 test-runner 跑一下测试
- 调用相关的Agent帮我跑一下测试看看有没有问题
- （或者）检查一下测试是否都通过 （注意：此时并不能确定是否会百分之百触发test-runner）
```

## 项目二：日志分析器

实战项目位于  03-SubAgents/projects/03-log-analyzer/。

在  .claude/agents/log-analyzer.md 中，进行如下配置：

~~~markdown
---
name: log-analyzer
description: Analyze log files and extract actionable insights. Use when troubleshooting issues or investigating incidents.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a senior SRE (Site Reliability Engineer) specialized in log analysis and incident investigation.

## When Invoked

1. **Identify Log Files**: Use Glob to find relevant log files
2. **Scan for Issues**: Grep for ERROR, WARN, exceptions
3. **Analyze Patterns**: Identify recurring issues and correlations
4. **Provide Insights**: Actionable summary with root cause analysis

## Analysis Approach

### Step 1: Quick Scan
```bash
# Count errors by type
grep -c "ERROR" *.log
# Find unique error patterns
grep "ERROR" *.log | cut -d']' -f2 | sort | uniq -c | sort -rn

### Step 2: Timeline Analysis
- When did issues start?
- Are there patterns (time-based, load-based)?
- What happened before the first error?

### Step 3: Correlation
- Do errors cluster together?
- Are multiple components affected?
- Is there a common root cause?

## Output Format

## Log Analysis Report

### Executive Summary
[1-2 sentence overview of findings]

### Critical Issues (Immediate Action Required)
1. **[Issue Name]**
   - First occurrence: [timestamp]
   - Frequency: [count]
   - Impact: [description]
   - Recommended action: [action]

### Warnings (Monitor)
- [Warning patterns and frequency]

### Timeline
[Chronological sequence of events]

### Root Cause Analysis
[Most likely root causes based on evidence]

### Recommendations
1. [Prioritized action items]

## Guidelines

- Focus on actionable insights, not raw data
- Identify patterns, not just individual errors
- Consider cascading failures (one error causing others)
- Look for the FIRST error in a sequence
- Note any suspicious patterns (repeated IPs, unusual timing)
- Keep the summary concise - details only when necessary
~~~

因为测试运行器的任务是执行命令 + 解析结构化输出，这个任务的难度级别比较普通。而日志分析则需要完成后面这些需要更强推理能力的任务，所以sonnet 更合适。

使用日志分析器：

```
- 让 log-analyzer 分析 logs/ 目录下的错误，找出主要问题
- 用 log-analyzer 分析 10:00-11:00 之间发生了什么问题
```

# 07｜百舸争流：多任务并行探索与流水线编排

今天我们要探索子代理的另外两个强大工程应用场景——并行探索和流水线编排。

这两个应用分别解决的问题是什么呢？并行探索, 当你需要同时从多个角度理解或处理一件事时启用；流水线编排, 当一个复杂任务可以拆成多个连续阶段时启用。

我们还是老规矩，从两个真实场景来开始。

- 场景一：新接手一个大型项目

你刚加入一个团队，需要快速理解一个包含几十个模块的后端项目。这时可以使用并行探索，三个子代理同时工作，各自探索自己的领域，最后汇总成一份综合报告。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202604141616881.jpeg)

- 场景二：修复一个复杂的 bug

你遇到一个“用户登录后偶尔 token 验证失败”的 bug。如果让主对话直接处理，上下文会很快被塞满：

```
1、搜索相关代码 → 200 行输出  (其实我们只关心原因)
2、分析可能的原因 → 又是 200 行  (其实我们只关心代码位置)
3、修复 → 100 行  (其实我们只关心改了什么)
4、验证 → 又是测试输出  (其实我们只关心成功/失败)
```

而流水线的方式，每个阶段只返回摘要，主对话始终保持清洁，可以随时介入做决策。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202604141619366.jpeg)

## 项目一：并行探索

接下来我们直接进入实战演练。

```
04-parallel-explore/
├── src/
│   ├── auth/           # 认证模块
│   │   ├── index.js
│   │   ├── jwt.js
│   │   └── session.js
│   ├── database/       # 数据库模块
│   │   ├── index.js
│   │   ├── models.js
│   │   └── migrations.js
│   └── api/            # API 模块
│       ├── index.js
│       ├── routes.js
│       └── middleware.js
└── .claude/agents/
    ├── auth-explorer.md
    ├── db-explorer.md
    └── api-explorer.md
```

**第一步：创建并行探索子代理**

~~~markdown
---
name: auth-explorer
description: Explore and analyze authentication-related code. Use when investigating auth flows, session management, or security.

tools: Read, Grep, Glob
<!-- tools: Read, Grep, Glob，全部只读，探索不需要修改任何东西，这三个工具足够完成代码探索任务。 -->

model: haiku
<!-- model: haiku，探索任务相对简单，追求速度，haiku 更快更便宜。 -->
---

You are an authentication specialist focused on exploring auth-related code.

## Your Domain

Focus ONLY on authentication-related concerns:
- Login/logout flows
- Token generation and validation (JWT, sessions)
- Password handling
- Permission and role systems
- Session management
<!-- Stay within auth domain：明确告诉子代理它的职责边界，防止它越界去分析不相关的代码。 -->

## When Invoked

1. **Locate Auth Code**: Use Glob to find auth-related files
   - Patterns: `**/auth/**`, `**/*auth*`, `**/*login*`, `**/*session*`, `**/*jwt*`

2. **Analyze Structure**: Read key files and understand:
   - How users authenticate
   - How tokens are generated/validated
   - How sessions are managed
   - How permissions are checked

3. **Report Findings**

## Output Format

```markdown
## Auth Module Analysis

### Overview
[1-2 sentence summary]

### Authentication Flow
1. [Step 1]
2. [Step 2]
...

### Key Components
| Component | File | Purpose |
|-----------|------|---------|
| ... | ... | ... |

### Token Strategy
- Type: [JWT/Session/etc]
- Expiry: [duration]
- Storage: [where stored]

### Security Notes
- [Observations about security posture]

## Guidelines
- Stay within auth domain - don't analyze unrelated code
- Note any security concerns you observe
- Be concise - main conversation will synthesize
~~~

用同样的模式创建另外两个探索子代理 db-explorer 和 api-explorer，只需要修改：

- name 和 description
- Your Domain 部分的关注点
- Output Format 中的报告结构

**第二步：使用并行探索**

进入项目目录，在 Claude Code 的命令行中输入：

```
同时让 auth-explorer、db-explorer、api-explorer 探索各自模块， 然后汇总给我一个整体架构理解
```

传统情况下，如果不使用子代理并行处理，假设每个模块用时 30 秒，串行总耗时 90 秒，主对话上下文会被三个模块的探索过程塞满；

而并行整体用时 30 秒，并行执行不仅更快，而且主对话的上下文更清洁。

> 注意，并行探索的隐含前提：任务必须真正独立。
>
> 并行看起来很美好，但有一个容易被忽略的前提：各子代理的探索任务之间不能有信息依赖。我们拿一个电商项目举例。
>
> ```
> 1、auth-explorer 发现用户认证使用 JWT，token 中包含 role 。
> 2、db-explorer 发现表中 role 字段有冗余，users 表有 role 字段，orders 表里也有 user_role 字段 。
> 3、api-explorer: 发现 /admin/* 使用了 role 进行路由。
> ```
>
> 这三个发现之间有关联——role 的传递路径横跨三个模块，但因为并行执行，每个子代理都不知道其他两个发现了什么！
>
> 这种情况下就只能使用串行模式了。

## 项目二：流水线编排

了解了并行探索的模式，我们再来看看流水线编排如何实现。

```
05-bugfix-pipeline/ 
├── src/ 
│ 
├── user-service.js # 用户服务（有 bug） 
│ ├── cart-service.js # 购物车服务（有 bug） 
│ ├── order-service.js # 订单服务（有 bug） 
│ └── utils.js # 工具函数 
├── tests/ 
│ └── services.test.js # 测试文件 
└── .claude/agents/ 
├── bug-locator.md # 定位：找到问题在哪 
├── bug-analyzer.md # 分析：理解为什么出问题 
├── bug-fixer.md # 修复：实施修复 
└── bug-verifier.md # 验证：确认修复有效
```

这里有四个子代理，对应 Bug 修复流水线的四个阶段。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202603241656714.jpeg)

- Locator：只回答“在哪”；
- Analyzer：只回答 “为什么”；
- Fixer：只负责 “怎么改”；
- Verifier：只负责 “改对没有”。

下面我们按“定位、分析、修复、验证”的分工顺序挨个拆解。

阶段一：Locator（定位）

~~~markdown
---
name: bug-locator
description: Locate the source of bugs in the codebase. First step in bug investigation.
tools: Read, Grep, Glob

model: sonnet
<!-- model: sonnet ：定位 bug 需要较强的推理能 -->
---

You are a bug investigation specialist focused on locating issues in code.

## Your Role

You are the FIRST step in the bug fix pipeline. Your job is to:
1. Understand the bug symptoms
2. Find where the bug likely originates
3. Identify related code that might be affected

## When Invoked

1. **Parse Bug Description**: Extract key information
   - Error messages
   - Stack traces
   - Symptoms/behavior

2. **Search Codebase**: Use Grep/Glob to find relevant code
   - Search for function names from stack traces
   - Search for error messages
   - Search for related keywords

3. **Narrow Down Location**: Identify the most likely source files

## Output Format

```markdown
## Bug Location Report

### Symptoms
[Summary of reported issue]

### Search Results
- Found [X] potentially related files
- Key matches: [list]

### Most Likely Location
**File**: [path]
**Function**: [name]
**Line**: [approximate]
**Confidence**: High/Medium/Low

### Related Code
- [file]: [why related]
- [file]: [why related]

### Handoff to Analyzer
- **Primary suspect**: [file:function:line_range]
- **Symptoms to reproduce**: [具体步骤]
- **Hypothesis**: [为什么怀疑这里]
- **Already excluded**: [搜索过但排除的位置及原因]
- **Related files to check**: [可能受影响的其他文件]
<!-- Handoff to Analyzer：为下一阶段准备信息 -->

## Guidelines
- Be thorough in searching - check multiple patterns
- Consider indirect causes (the bug might manifest in one place but originate elsewhere)
- Note any related code that might be affected by a fix

- DO NOT suggest fixes - that's for the fixer
<!-- DO NOT suggest fixes：明确告诉它这不是它的职责 -->

- Keep output concise for the analyzer to continue
~~~

阶段二：Analyzer（分析）

~~~markdown
---
name: bug-analyzer
description: Analyze root cause of bugs after location is identified. Second step in bug investigation.
tools: Read, Grep, Glob

model: sonnet
<!-- model: sonnet ：分析 bug 需要较强的推理能 -->
---

You are a bug analysis specialist focused on understanding root causes.

## Your Role

You are the SECOND step in the bug fix pipeline. You receive:
- Bug location from the locator
- Symptoms description

Your job is to:
1. Deeply understand WHY the bug occurs
2. Identify the root cause (not just the symptom)
3. Assess the impact and complexity

## When Invoked

1. **Read Identified Code**: Carefully read the suspected location
2. **Trace Execution**: Understand the code flow
3. **Identify Root Cause**: Find the actual bug, not just symptoms
4. **Assess Impact**: What else might be affected?

## Analysis Checklist

- [ ] Data type issues (string vs number, null checks)
- [ ] Race conditions (concurrent access)
- [ ] Edge cases (empty arrays, zero values)
- [ ] Logic errors (wrong operators, missing conditions)
- [ ] Resource leaks (unclosed connections)
- [ ] Error handling gaps

## Output Format

```markdown
## Bug Analysis Report

### Location Confirmed
**File**: [path]
**Function**: [name]
**Line(s)**: [range]

### Root Cause
[Clear explanation of WHY the bug occurs]

### Code Snippet
```javascript
// The problematic code

### Bug Category
- [ ] Logic Error
- [ ] Type Error
- [ ] Race Condition
- [ ] Edge Case
- [ ] Resource Leak
- [ ] Other: [specify]

### Impact Assessment
- **Severity**: Critical/High/Medium/Low
- **Scope**: [what's affected]
- **Data Impact**: [any data corruption risk?]

### Fix Complexity
- **Estimated Effort**: Simple/Moderate/Complex
- **Risk of Regression**: Low/Medium/High

### Handoff to Fixer
**Recommended Approach**: [brief guidance]
**Watch Out For**: [potential pitfalls]

## Guidelines

- Focus on the ROOT cause, not symptoms
<!-- 关注点是“为什么”而不是“症状” -->

- Consider if this is a pattern that might exist elsewhere
- Assess whether the fix could break other things
- DO NOT implement fixes - just analyze
~~~

阶段三：Fixer（修复）

~~~markdown
---
name: bug-fixer
description: Implement bug fixes after analysis is complete. Third step in bug fix pipeline.

tools: Read, Edit, Write, Grep, Glob
<!-- 这个阶段有写权限 -->

model: sonnet
---

You are a bug fix specialist focused on implementing correct and safe fixes.

## Your Role

You are the THIRD step in the bug fix pipeline. You receive:
- Root cause analysis
- Recommended approach

Your job is to:
1. Implement the fix correctly
2. Ensure the fix doesn't break other things
3. Follow code style conventions

## Fix Principles

### Do
- Make the MINIMAL change needed
<!-- 防止过度修改 -->

- Match existing code style
- Add necessary null/type checks
- Use existing utility functions when available
- Add inline comments for non-obvious fixes

### Don't
- Refactor unrelated code
- Add unnecessary abstractions
- Change function signatures without reason
- Remove existing functionality
- Over-engineer the solution

## Output Format

```markdown
## Bug Fix Report

### Changes Made

**File**: [path]
**Type**: Modified/Added/Removed

```diff
- old code
+ new code

### Fix Explanation
[Why this fix works]
### Potential Side Effects
[Any code that might be affected]
### Testing Notes
[What the verifier should check]
### Rollback Plan
[How to revert if needed]
<!-- 考虑回滚方案 -->

## Guidelines

- Keep fixes focused and minimal
- If uncertain, err on the side of safety
- Don't change more than necessary
- Ensure backward compatibility when possible
- Hand off to verifier with clear testing notes
~~~

阶段四：Verifier（验证）

~~~markdown
---
name: bug-verifier
description: Verify bug fixes by running tests. Final step in bug fix pipeline.

tools: Read, Bash, Grep, Glob
<!-- Bash可以执行测试 -->
model: haiku
---

You are a QA specialist focused on verifying bug fixes.

## Your Role

You are the FINAL step in the bug fix pipeline. You receive:
- The fix that was implemented
- Testing notes from the fixer

Your job is to:
1. Run existing tests
2. Verify the fix works
3. Check for regressions

## When Invoked

1. **Run Tests**: Execute the test suite
2. **Analyze Results**: Check pass/fail status
3. **Verify Fix**: Confirm the original bug is fixed
4. **Check Regressions**: Ensure nothing else broke

## Verification Checklist

- [ ] All existing tests pass
- [ ] The specific bug scenario is fixed
- [ ] No new errors introduced
- [ ] Code changes match what was intended
<!-- 检查是否引入新问题 -->

## Output Format

```markdown
## Verification Report

### Test Results
**Status**: PASS / FAIL
**Total Tests**: X
**Passed**: X
**Failed**: X

### Bug Fix Verification
**Original Bug**: [description]
**Status**: FIXED / NOT FIXED / PARTIALLY FIXED

### Regression Check
**New Issues Found**: Yes / No
- [If yes, list them]

### Final Verdict
- [ ] Safe to merge
- [ ] Needs more work: [reason]
- [ ] Needs manual testing: [what to test]

### Notes for Human Review
[Any observations or concerns]

## Commands to Run

```bash
# Check for syntax errors
node --check [file]

# Run tests
npm test
# or
node tests/[test-file].js
<!-- 运行测试验证修复 -->

## Guidelines

- Run ALL tests, not just related ones
- Report any warnings, not just errors
- Be honest about test coverage gaps
- Suggest manual testing if needed
- Provide clear pass/fail verdict  
~~~

**使用流水线**

进入项目目录，描述 bug：

```
我有一个 bug：用户登录后偶尔会 token 验证失败。
帮我用流水线方式修复：
1. 先让 bug-locator 找到相关代码
2. 让 bug-analyzer 分析原因
3. 让 bug-fixer 修复
4. 让 bug-verifier 跑测试验证
```

你可以在任何阶段介入，修正方向，而不用等整个流程跑完才发现问题。比如：

```
Locator：找到了 3 个可能的位置
你：等等，第二个位置不太可能，那是测试代码
Locator：好的，聚焦到第一和第三个位置...
```

## 交接契约

**什么是“交接契约”？**

流水线中，前一个子代理的输出就是后一个子代理的输入（通过主对话转发）。如果前一个阶段输出的信息不完整或格式不对，后一个阶段就会“瞎干”。

```
如果Locator 输出："bug 可能在 auth 模块里。"
                    ↓
Analyzer 收到这句话后："auth 模块？哪个文件？哪个函数？我该分析什么？"
                    ↓
结果：Analyzer 自己又做了一遍 Locator 的工作，流水线形同虚设。
```

交接契约要遵循的经验法则是——交接时信息量要充足，让下一阶段无需重复上一阶段的工作。如果 Analyzer 收到 Locator 的输出后，还需要自己 Grep 一遍才能开始分析，说明交接契约设计不合格。

因此，在每个阶段的输出格式中，应该有一个明确的  Handoff（交接） 部分，告诉下一阶段“你需要关注什么”。

```markdown
## Locator → Analyzer 的交接契约

### Locator 必须提供：
1. 具体文件路径（不是"大概在某模块"）
2. 具体函数/方法名
3. 嫌疑代码行号范围
4. 为什么怀疑这里（搜索证据）
5. 相关联的其他文件列表

### Analyzer 期望收到：
1. 明确的调查范围（文件+函数）
2. 症状描述（用户看到什么）
3. 已排除的可能性（Locator 搜索过但排除的位置）
## Analyzer → Fixer 的交接契约

### Analyzer 必须提供：
1. 根因定位（一句话）
2. 修复方向建议（不超过 3 个方案）
3. 推荐方案及理由
4. 修改涉及的文件列表
5. 需要注意的边界条件

### Fixer 期望收到：
1. 明确的"改什么"（文件+位置+原因）
2. 明确的"怎么改"（方向，不需要具体代码）
3. 明确的"别碰什么"（不应该修改的部分）
## Fixer → Verifier 的交接契约

### Fixer 必须提供：
1. 改了哪些文件（diff 格式）
2. 为什么这么改
3. 可能的副作用清单
4. 需要运行的测试命令
5. 验证通过的标准是什么

### Verifier 期望收到：
1. 变更清单（知道要验证什么）
2. 测试命令（知道怎么验证）
3. 预期结果（知道什么算通过）
```

## 主对话编排

在 Claude Code 中，主对话就是编排者——它负责触发每个阶段、审查每个阶段的输出，决定是否继续、重试或中止、同时在阶段之间注入人工判断。

> 编排者的四种介入形式

编排者有全自动、关键阶段审批、逐阶段审批和回退重试四种介入形式。

```
形式一：全自动（信任度高）
┌─────────┐  自动 ┌─────────┐  自动  ┌─────────┐ 自动  ┌─────────┐
│ Locator │ ────→ │ Analyzer│ ────→ │  Fixer  │ ────→ │Verifier │
└─────────┘       └─────────┘       └─────────┘       └─────────┘

形式二：关键阶段审批（推荐）
┌─────────┐  自动 ┌─────────┐       ┌─────────┐  自动  ┌─────────┐
│ Locator │ ────→ │ Analyzer│ ─?──→ │  Fixer  │ ────→ │Verifier │
└─────────┘       └─────────┘  ↑    └─────────┘       └─────────┘
                            人工审批
                        "这个根因分析对吗？
                         确认后再让它改代码"

形式三：逐阶段审批（谨慎）
┌─────────┐       ┌─────────┐       ┌─────────┐       ┌─────────┐
│ Locator │ ─?──→ │ Analyzer│ ─?──→ │  Fixer  │ ─?──→ │Verifier │
└─────────┘  ↑    └─────────┘  ↑    └─────────┘  ↑    └─────────┘
          人工审批           人工审批           人工审批

形式四：回退重试（遇到问题时）
┌─────────┐       ┌─────────┐       ┌─────────┐
│ Locator │ ────→ │ Analyzer│ ────→ │  Fixer  │
└─────────┘       └─────────┘       └────┬────┘
                       ↑                  │
                       └──────────────────┘
                      "修复方向不对，
                       回退到分析阶段"
```

就 Bug 修复这个具体问题而言，并不是每个阶段都需要人工审批，但有一个关键决策点必须把关：

```
Analyzer → Fixer
 ↑
这个位置最关键！
```

为什么？因为这是从只读到读写的跨越——一旦 Fixer 开始修改代码，回退成本就高了。在这个位置审查 Analyzer 的根因分析，确认方向正确后再继续，是性价比最高的介入方式。

> 编排者的 prompt 设计

你可以在触发流水线时明确编排方式：

```
帮我修复这个 bug：用户登录后偶尔 token 验证失败。

执行方式：
1. 先让 bug-locator 定位 → 自动传给 bug-analyzer
2. bug-analyzer 分析完后 → 先给我看根因分析，我确认后再继续
3. 我确认后 → 让 bug-fixer 修复 → 自动传给 bug-verifier
4. bug-verifier 验证完给我最终报告
```

这就是形式二：关键阶段审批的实际使用方式。

## 适用场景

![img](https://static001.geekbang.org/resource/image/42/aa/4217eb94383a247c592ca6141d9186aa.jpg?wh=2703x1260)

真实工程任务很少是纯并行或纯流水线。更常见的是混合模式——一部分任务并行，一部分串行。

**模式一：Fan-out → Fan-in（扇出→聚合）**

典型场景：接手新项目时，先并行探索各模块，再综合分析。

```
                    ┌─── Explorer A ───┐
                    │                   │
Input ──→ Split ──→├─── Explorer B ───├──→ Synthesizer ──→ Output
                    │                   │
                    └─── Explorer C ───┘

        串行              并行              串行
```

prompt：

```
帮我理解这个项目的架构：
1. 同时让 auth-explorer、db-explorer、api-explorer 各自探索
2. 收到三份报告后，综合分析模块间的依赖关系和数据流
```

**模式二：Pipeline + Parallel Stage（流水线中嵌套并行）**

典型场景：定位到问题位置后，需要从多个维度分析（安全性、性能、兼容性），再综合决定修复方案。

```
┌──────────┐     ┌───────────────────────┐     ┌──────────┐
│          │     │    ┌─── Check A ───┐  │     │          │
│ Locator  │ ──→ │    ├─── Check B ───├  │ ──→ │  Fixer   │
│          │     │    └─── Check C ───┘  │     │          │
└──────────┘     │     并行检查多维度     │     └──────────┘
                 └───────────────────────┘
    串行                  并行                    串行
```

prompt：

```
bug-locator 已经定位到 user-service.js 的 validateToken 函数。现在：
1. 同时从三个角度分析这个函数：
   - 安全性（有没有漏洞）
   - 性能（有没有阻塞）
   - 兼容性（改了会不会影响调用方）
2. 综合三份分析，决定修复方案
3. 让 bug-fixer 执行修复
```

# 08 | 群策群力：Agent Teams 多会话协作架构

略

