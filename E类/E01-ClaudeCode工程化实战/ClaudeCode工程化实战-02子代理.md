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

**子代理配置文件详解**

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

**子代理的存放位置与优先级**

![img](https://static001.geekbang.org/resource/image/a7/32/a72ae303f03a261b1c6e8yy4d0ae2132.jpg?wh=2420x1089)

**创建子代理的三种方式**

方式一：交互式创建（推荐新手使用）。在 Claude Code 中输入  /agents，按照向导操作；

方式二：手写配置文件，直接创建  .claude/agents/your-agent.md 文件。其优势是更精细的控制，方便版本管理，可以从其他项目复制。

方式三：CLI 参数临时创建，通过  --agents 参数，可以在启动 Claude Code 时传入 JSON 格式的子代理定义。这种方式创建的子代理仅在当前会话中存在，不会保存到磁盘。这种方式特别适合 CI/CD 自动化时在流水线中临时创建任务专用的子代理。

**子代理的运行模式**

子代理可以在前台或后台运行，Claude 会根据任务自动选择前台或后台。你也可以手动控制，对 Claude 说 “run this in the background”。

每个子代理执行完成后，Claude 会自动收到它的  agent ID。如果你需要在之前的子代理基础上继续工作，可以让 Claude 恢复（Resume）它：

```
用 code-reviewer 子代理审查认证模块
[子代理完成]

继续刚才的审查，再看一下授权逻辑
[Claude 恢复之前的子代理，保留完整上下文]
```

# 04｜量体裁衣：从Sub-Agents到Multi-Agent的工程指南

这节课的目标是帮你建立一种可以立刻用于拆解当下热门产品，也能长期指导工程设计的通用方法论。学完今天的内容，你不仅能更好地理解 Sub-Agent、Skills 这些概念， 也会更清楚：什么时候该用，什么时候不该用。

**何时该升级到多 Agent？**

LangChain 在其架构选型指南中给出了明确建议：“Start with a single agent. Add tools before adding agents. Graduate to multi-agent patterns only when encountering clear architectural limits.” （先从单 Agent 起步，优先通过引入工具扩展能力； 只有当系统确实触及单 Agent 的架构边界时， 才考虑采用多 Agent 的设计模式。）

架构边界是什么？两个核心触发条件：

- 信号一：上下文管理挑战

  当多个能力领域的专业知识无法舒适地塞进单一 prompt 中时——你需要策略性地分发上下文，而不是把所有东西堆在一起。

- 信号二：分布式开发需求
  当多个团队需要独立拥有和维护各自的 Agent 能力时，各团队可以独立迭代而不互相干扰。

下面我们从工程视角出发，系统梳理 Sub-Agent 到 Multi-Agent 的四种核心设计模式，并给出性能、成本、可控性三个维度的决策框架。

**四种核心设计模式**

- 模式一：Sub-Agents（子代理委派）

Sub-Agents 的核心设计思想是一个 Supervisor Agent 充当老板，将任务分解后委派给专门的 Sub-Agent。每个 Sub-Agent 解决一个特定的任务。

![img](https://static001.geekbang.org/resource/image/1b/45/1ba621fb0243476599a3eb0a82d99145.jpg?wh=2079x1032)

> Anthropic 的 Research 功能采用了经典的 Sub-Agent 模式：
>
> 1. LeadResearcher（Claude Opus 4）分析查询、制定策略
> 2. 并行派出  3-5 个 SubAgent（Claude Sonnet 4），各自独立搜索
> 3. 每个 SubAgent 执行 3+ 个并行工具调用
> 4. CitationAgent 处理引用和来源归属
> 5. 结果汇聚回 LeadResearcher 综合输出
>
> 工程评测显示，并行化的 Sub-Agent 执行方式可将复杂查询的整体研究时间最多缩短约 90%，但其代价是相较普通对话约 15 倍的 token 消耗；

- 模式二：Skills（渐进式能力加载）

通过 SKILL.md 文件（或类似配置）实现能力的渐进式加载。Agent 一开始只知道技能的名称和描述，当判断需要某个技能时，才加载完整的指令。

![img](https://static001.geekbang.org/resource/image/c6/4d/c6651d3f9a7d2522005054f5375a2b4d.jpg?wh=2108x1187)

> 在 Skills 模式下，系统仍然由单一 Agent 负责全部推理与执行，所有技能共享同一个上下文窗口。
>
> ```
> .claude/skills/           
> ├── deploy/
> │   └── SKILL.md          # 部署技能的完整指令
> ├── review-pr/
> │   └── SKILL.md          # PR 审查技能的指令
> └── database-migration/
>     └── SKILL.md          # 数据库迁移技能的指令
> ```

- 模式三：Handoffs（交接）

Handoffs 的核心思想是活跃的 Agent 根据对话状态动态切换。Agent A 完成自己的阶段后，通过调用  handoff() 工具将控制权（和上下文）传递给 Agent B。

![img](https://static001.geekbang.org/resource/image/33/13/33ee50500cbf7c36cbb12b85e2371413.jpg?wh=2202x774)

> Handoffs 的典型应用是客服工单流程：
>
> ```
> 前台接待Agent --> 技术支持Agent --> 高级工程师Agent
> - 收集用户信息    - 排查问题         - 尝试诊断
> - 识别问题类型    - 尝试解决         - 解决并生成报告
> - handoff对应    - 解决 ? 结案
>   专家Agent        : handoff高
>                    级工程师Agent
> ```

- 模式四：Router（路由器 / 并行分发与合成）

Router 模式的核心在于对输入进行语义拆分与职责分流。系统首先由 Router 对用户请求进行分类和分解，然后将子查询并行分发给各自负责的专业 Agent，最后再将多个结果统一合成为一个对用户友好的响应。

![img](https://static001.geekbang.org/resource/image/78/26/788f2cefef03a2284db65f3b2eef7626.jpg?wh=2116x1453)

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

- 性能、成本、可控性的量化对比

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

**从 Sub-Agent 到 Multi-Agent 的架构演进路径**

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

- 第一阶段：单 Agent + Tools

适合大多数初期场景。不要过早引入多 Agent。

![img](https://static001.geekbang.org/resource/image/1a/8c/1ab61b8ea67869b927e082c41438268c.jpg?wh=2073x940)

- 第二阶段：单 Agent + Skills

当工具数量增多、prompt 变得臃肿时，用 Skills 实现渐进式加载。

![img](https://static001.geekbang.org/resource/image/ff/4c/ffb46a43a3375c076e3bc350c052554c.jpg?wh=2045x918)

- 第三阶段：Supervisor + Sub-Agents

当不同领域需要独立的上下文空间和专业知识时引入。

![img](https://static001.geekbang.org/resource/image/eb/ae/eb52933d9a0d1a8d8b88ae0f62c8efae.jpg?wh=2703x1031)

- 第四阶段：混合架构

成熟系统中，不同类型的任务流可能采用不同的模式。Router 处理分类，Sub-Agent 处理并行研究，Handoff 处理顺序流程。

![img](https://static001.geekbang.org/resource/image/cf/92/cf24fff82f9eb95a690ab108a121d692.jpg?wh=2756x1721)

# 05｜明察秋毫 ：构建只读型安全审计子代理

今天的目标就下面三个。

- 创建一个只有读取权限的代码审查子代理。
- 用它来发现示例代码中的安全问题。
- 体验“最小权限原则”的工程价值。

同时，我们也将从真实工程痛点出发，理解"为什么需要这个子代理"的设计思维。

**项目场景：代码审查**

一个后端开发项目中，我们刚刚好写完了一段认证逻辑，想让 Claude Code 帮你审查一下有没有安全问题。你在主对话中说：“帮我检查一下 auth.js 的安全性”。

Claude 完成这个任务当然不在话下，它读了你的代码，发现了硬编码的密钥，然后顺手帮你改成了环境变量读取。

这就是为什么我们需要只读型子代理。

**从工程痛点到子代理设计：一种思维方式**

- 第一步：理解“有问题”的代码

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

- 第二步：创建代码审查子代理

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

![img](https://static001.geekbang.org/resource/image/da/50/daeabfa0e1b5bc15ef50ac19e3945e50.jpg?wh=9615x4357)

- 第三步：运行代码审查

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

- 第四步：验证权限边界

在 Claude Code 中说：

```
让 code-reviewer 修复 auth.js 中的硬编码密钥问题
```

你会看到类似这样的响应：

```
code-reviewer 只有读取权限，无法修改文件。
如需修复问题，请使用其他方式或直接请求修改。
```

- 第五步：扩展审查维度

如果你的项目使用 React，可以在配置中添加框架特定检查。

```markdown
### React Specific
- 列表中缺少 `key` 属性
- 不必要的重复渲染（re-render）
- 直接修改 state（状态突变）
- 在 `useEffect` 中缺少清理逻辑（cleanup）
- Prop drilling 反模式
```

**从代码审查到影响面分析——真实工程场景延伸**

我分享一个课程留言区同学提到的真实线上事故场景：

> 他让 AI 按照 SDD 写了一个老功能的迭代并上线了。但在线上，用户端 7 秒拿不到操作结果。原因是什么？AI 并不知道这条链路上的改动会影响到哪些下游服务，也不知道端用户的体验 SLA 是多少。代码本身没有 bug，但全链路的影响面被忽略了。

这个案例的本质是什么？不是 AI 写错了代码，而是 AI 没有被告辞“在设计阶段就要审视影响面”的职责。

- 把工程经验翻译成子代理设计

让我们用“痛点驱动设计”思维来分析这个场景。

![img](https://static001.geekbang.org/resource/image/68/9c/68fd5d69244018593c02df4dee8f2c9c.jpg?wh=3041x1555)

- 设计一个影响面分析子代理

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

- 配合 Skill 沉淀链路知识

对于存量系统，维护一个知识库（你的接口在整个链路是如何串联起来的），这样 AI 去改动现有代码的时候，就知道帮你排查这个改动影响了什么链路。

这就是 Skill 的用武之地，注意看上面 impact-analyzer 配置中的 skills 字段：

```
skills:
  - chain-knowledge          # 链路拓扑和 SLA 约束
  - recent-incidents         # 近期事故记录（如有）
```

子代理不会自动继承主对话中可用的 Skill。你必须在 skills 字段中显式列出需要的 Skill 名称，它才会被注入。

**工程决策：什么时候该创建子代理？**

- 该创建子代理的场景

![image-20260320152608269](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202603201526307.png)

- 不该创建子代理的场景

1. 一次性任务：直接在主对话中完成即可。
2. 简单的 prompt 模板：直接用 Skill 文件，不需要独立上下文和工具隔离。
3. 自动化触发动作：用 Hook，不需要 AI 分析判断。

# 06｜去芜存菁 ：高噪声任务处理——测试运行器与日志分析器

什么是高噪声输出？

测试运行是最典型的高噪声场景：输入npm test，输出几十到几百行日志。我们关心的只是通过 / 失败？失败了哪个？为什么？

子代理的价值就在这里：它去执行这些高噪声任务，然后只把结论带回主对话。但不是所有任务都需要子代理来处理，判断标准是信噪比。

这里有一个经验法则：如果一个命令的输出超过 50 行（行数也还要视具体情况而定），且你只关心其中不到 10 行（也就是不到五分之一）的内容，就应该用子代理。

**项目一：测试运行器**

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

**项目二：日志分析器**

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



![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202603241656714.jpeg)























