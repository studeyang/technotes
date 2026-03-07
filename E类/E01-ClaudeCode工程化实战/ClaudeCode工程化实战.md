> 来自极客时间《Claude Code工程化实战》--黄佳

# 开篇词｜共生而非替代：极客和 AI 的共舞

以前写代码是这样的：打开 IDE，敲键盘，查文档，调试，再敲键盘。大脑是主机，手指是输出设备。

现在写代码是这样的：我描述意图，AI 生成代码，我审阅确认，AI 继续迭代。大脑变成了导演，AI 变成了演员。

这不是效率提升 10% 或 20% 的量变。这是角色本身的转换——从“执行者”到“指挥者”。

**Another AI Coder？—— Claude Code 远不止如此**

Claude Code 出现时，包括我在内的很多人都明确意识到：真正被重塑的，已经不是“写代码”，而是 Vibe Coding 这件事本身。

在 Claude Code 中，你更容易这样描述任务：

> “这个模块现在可读性差、测试覆盖不足，还可能有安全隐患。我希望你帮我系统性地重构它，但不要影响对外接口。”

你会发现，Claude Code 非常懂工程。它直接把 Agent 和工程治理写进了产品架构里——Sub-Agents、Skills、Hooks，这些从 Claude Code 的设计过程中创建出来的概念，已经超越了“编程工具”本身，形成了通用智能体设计模式的一部分。

现在我们使用 Claude Code 等 AI Coding 工具编码，其实你不再只是把自然语言翻译成代码， 而是在做设计，具体来说是做三件更高级的事情：

- 拆解问题
- 分配任务
- 组织多个智能体协作完成目标

这已经不是“编程工具”的范畴了，而是一种新的工作范式。Claude Code 代表的不只是一个产品，而是一种范式：人机协作的新范式。

**当 Sub-Agents 和 Skills 成为通用语言**

- Sub-Agents（子代理） 的核心思想是：一个复杂任务可以拆解给多个专职角色。

就像一家公司不会让 CEO 亲自写代码、做测试、查日志，AI Agent 也需要“组织架构”。我们可以这样理解，主代理是指挥官，子代理是专业兵种。有人负责代码审查（只读，不能改），有人负责跑测试（执行，汇报结果），有人负责分析日志（消化噪声，提炼结论）。

![img](https://static001.geekbang.org/resource/image/f4/b6/f48afa2fbc5370dce19d59786d2b78b6.png?wh=1408x768)

- Skills（技能） 的核心思想是：AI 应该知道什么时候用什么能力。

传统工具需要用户手动触发——你输入  /review，它就审查代码。但 Skills 不同，你只需要说“帮我看看这段代码有没有安全问题”，AI 就能自动判断这是代码安全审查任务，并自动激活对应的 Skill，自动应用领域知识和检查清单。

这种“语义触发”的设计，让 AI 从执行命令的工具，升级为理解意图的工作伙伴。

Skills 的渐进式披露架构——不是把所有知识一股脑灌给 AI，而是按需加载，用到什么加载什么。这解决了 LLM 上下文窗口的根本限制。

![img](https://static001.geekbang.org/resource/image/e7/46/e74e0bfded85a6c26c7cfa73228f8e46.png?wh=1408x768)

**这门课会带给你什么**

这是一门工程化实战课，目标是让你从 Claude Code 的使用者，成长为能够驾驭 AI 的工程指挥者。

我们不是从功能出发，而是从工程协作中的真实卡点出发，反推需要哪些机制。围绕真实工程中 Agent 协作常见的痛点，后续课程将带你逐一拆解并解决以下问题。

- Memory： 解决 Agent 每次对话都“从零开始”、不理解项目背景的问题，让 AI 真正记住你的代码结构、约束和上下文。
- Sub-Agents： 解决单一 Agent 角色混乱、上下文污染、又写代码又做审查的问题，通过职责拆分实现关注点分离。
- Skills： 解决 Prompt 不可复用、经验无法沉淀、团队能力难以传承的问题，把个人技巧变成可组合的工程资产。
- Hooks： 解决 Agent 执行过程不可控、缺乏检查点、容易“越权操作”的问题，在关键节点引入自动校验和人工兜底。
- Headless： 解决 Agent 只能在 IDE 里交互、无法进入自动化流程的问题，让 AI 能在 CI/CD 中无人值守地运行。
- Agent SDK：解决只会用对话的方式使用 Agent，难以嵌入现有系统和工作流的问题，用代码驱动 Agent，构建可编排的工程流程。

Github: https://github.com/huangjia2019/claude-code-engineering

我们的具体学习目标是：

- 把 Claude Code 从“聊天式工具”，升级为可持续运转的 AI 工程团队。
- 让 AI 能“接手真实项目”，而不仅是写示例代码。
- 构建可复用的 Sub-Agents 和 Skills，把个人经验变成团队资产。
- 让 AI Agent 真正进入 CI/CD，而不是停留在 IDE 里。
- 从“写代码的人”，转变为组织管理智能体的人，从执行者蜕变为技术指挥者。

# 01｜登台远望：Claude Code 底层技术全景导览

Claude Code 不只是一个“工具“，而是一个“平台”——你可以在上面构建自己的 AI 工作流。它的真正身份是：一个可编程、可扩展、可组合的 AI Agent 框架。

### 5 分钟快速上手

下面常用命令的速查表。

![img](https://static001.geekbang.org/resource/image/23/fa/236e47af6e9df067a36b65ff7d5b9ffa.jpg?wh=2898x1907)

### 从使用者到驾驭者

- 使用者（你问，它答）：用户 → 输入问题 → Claude 回答 → 完成
- 驾驭者（你设计，它执行）：用户 → 配置 Agent → Agent 自主工作 → 自动完成任务

举个例子：

![img](https://static001.geekbang.org/resource/image/4b/9c/4b2f74d224498bfc75faea1c22c32b9c.jpg?wh=3926x1802)

用学开车打个比方：

- 使用者：知道方向盘转哪边车往哪走，油门让车动，刹车让车停。
- 驾驭者：理解发动机、变速箱、刹车系统的工作原理，能改装车辆。

对于 Claude Code：

- 使用者：知道怎么提问，怎么让 Claude 帮你写代码。
- 驾驭者：理解记忆系统、子代理、技能包、钩子的工作原理，能构建自定义工作流。

这门课的目标，把你从被动使用者变成主动驾驭者。

### Claude Code 底层技术全景图

Claude Code 的底层能力从技术上拆解可以分为四个层次：基础层、扩展层、集成层和编程接口层。

![img](https://static001.geekbang.org/resource/image/97/91/97f666c51958b16be8910a4139ff0891.jpg?wh=4280x2214)

#### 1、基础层：Memory（记忆系统）

基础层也可以称为是 Claude Code 的长期记忆系统，它的核心文件是 CLAUDE.md。

CLAUDE.md 就是 Claude 的“新员工手册”，它会告诉你：

- 公司的代码风格是什么。
- Git 提交信息怎么写。
- 项目的架构是怎样的。
- 有哪些不能碰的“禁区”。

例如，当我们要开始一个新的电商项目，我创建了下面的 CLAUDE.md 文件。

```markdown
# Project: E-commerce Platform

## Tech Stack
- Frontend: React + TypeScript
- Backend: Node.js + Express
- Database: PostgreSQL

## Code Style
- Use functional components
- Prefer async/await over .then()
- Maximum line length: 100 characters

## Important Rules
- NEVER commit to main directly
- Always run tests before pushing
```

#### 2、扩展层：四大核心组件

**Commands（斜杠命令）**

Commands 适合标准化操作——团队统一的 commit 格式、固定的部署流程等。例如：

```
用户输入: /review

Claude 执行: 根据 .claude/commands/review.md 的指令审查代码
```

**Skills（技能）**

技能代表着 AI 的一系列专属能力组合，例如：

```
用户说: "帮我看看这段代码有没有安全问题"

Claude 思考: 这是代码安全审查任务 → 激活 security-review Skill

Claude 执行: 按照 Skill 中定义的流程审查代码
```

> 与 Tool 的区别：
>
> - Tool 解决的是我能不能做；
> - Skill 解决的是我能不能做、怎么做、做到什么程度。
>
> 与 Commands 的区别：
>
> - Commands 是显式、可复用、可审计、通过斜杠命令固定触发的操作指令集，是相对固化的标准流程；
> - Skill 内部，是“像专家一样”的行为说明，它不是流程执行，而是专家判断。

**SubAgents（子代理）**

子代理适合隔离执行——高噪声任务（比如在大量日志中寻找出错信息，在大量文档中检索相关资源）、需要特定权限的任务。

```
主 Claude: 这个任务需要跑大量测试，让我创建一个子代理来处理。

子代理（test-runner）: 执行测试，只把结果汇报给主 Claude
```

**Hooks（钩子）**

钩子是在特定事件触发时自动执行的脚本，其触发方式是事件自动触发。

```
事件: Claude 即将执行 Edit 工具

Hook: 自动检查是否有安全敏感内容

结果: 如果发现问题，阻止执行并警告
```

Hooks 适合自动化检查——格式化、安全检查、日志记录等。

#### 3、集成层：连接外部世界

集成层负责链接外部世界。包含 Headless（无头模式）和 MCP（Model Context Protocol）两大技术。

**Headless（无头模式）**

无头模式让 Claude Code 在没有人工交互的情况下运行，适合  CI/CD 集成——自动代码审查、自动修复、自动生成变更日志等。

```markdown
# GitHub Actions 中
- name: Auto-fix code issues
  run: claude --headless "Fix all linting errors in src/"
```

**MCP（Model Context Protocol）**

MCP 让 Claude 连接外部工具和服务，适合工具连接——可以把任何外部系统变成 Claude 可调用的工具。

```
Claude → MCP → 数据库
Claude → MCP → Jira
Claude → MCP → 自定义 API
```

#### 4、编程接口层：Agent SDK

当配置式的扩展不够用时，你可以用代码来驱动 Claude。这种方式适合构建自定义 Agent——完全控制执行流程、自定义工具、复杂工作流。

```python
from claude_sdk import ClaudeSDKClient

client = ClaudeSDKClient()

# 执行任务
result = client.query(
    prompt="Review this code for security issues",
    tools=["Read", "Grep"],
    max_turns=10
)
```

### 组件关系和技术选型指南

在真实的系统中，这些组件不是孤立存在的——它们相互协作，共同完成复杂任务。

**触发方式**

![img](https://static001.geekbang.org/resource/image/5e/1b/5e4c6e3408de80c964d3ba910366db1b.jpg?wh=3423x1677)

**数据流向**

我们来看数据是怎么在系统中流动的。这张图展示了一个典型请求的生命周期：

![img](https://static001.geekbang.org/resource/image/f2/04/f2bf832eb5444774d2f7e3ee29c22a04.jpg?wh=3348x2232)

当用户输入“帮我修复 src/api.js 中的安全漏洞”之后，Claude 可能的处理流程如下。

1. Memory 层：Claude 首先加载  CLAUDE.md，了解到这是一个 Node.js 项目，团队要求所有安全修复必须附带测试。

2. 扩展层分发：

   a. 用户没有输入斜杠命令，所以 Commands 不参与。

   b. Claude 识别出“安全漏洞”关键词，激活  security-review Skill。

   c. Skill 指示 Claude 创建一个子代理来执行测试。

3. Hooks 监控：Claude 准备执行  Edit 工具修改代码时，Hooks 自动运行预检查脚本，确保没有引入新的安全问题。
4. 工具执行：通过 Read、Edit 等工具完成代码修改。
5. MCP 连接：如果配置了 Jira MCP，还可以自动更新相关的 ticket 状态。

**Plugins：打包容器**

当你开发了一套好用的 Commands、Skills、Hooks 组合，想要分享给团队或社区时，就需要 Plugins。

```
my-team-plugin/
├── commands/           # 斜杠命令
│   └── review.md
├── skills/             # 技能
│   └── security-check/
│       └── SKILL.md
├── agents/             # 子代理
│   └── test-runner.md
├── hooks/              # 钩子
│   └── pre-edit.sh
└── plugin.json         # 插件配置
```

Plugin 的价值在于可复用、可版本化、可分发。在第 16 讲我们还会详细讲解如何创建和发布 Plugins。

**技术选型指南**

当你面对一个真实需求时，如何选择正确的技术？下面这是我总结的决策流程：

![img](https://static001.geekbang.org/resource/image/a9/a0/a9d52fb4b7947b3ebff1844b62148ba0.jpg?wh=2916x1596)

为了帮助你快速匹配，我也准备了一份场景 VS 方案的速查表。

![img](https://static001.geekbang.org/resource/image/d7/f7/d704a4daffc7192a173d54ac579c83f7.jpg?wh=3638x1899)

**组合使用**

假设你想实现这样一个流程：每当有人提交 PR，自动进行代码审查，发现问题就评论，没问题就通过。这需要组合多种技术：

```
1. Headless 模式在 CI 中触发
   └── GitHub Actions 监听 PR 事件，调用 claude --headless

2. 调用 code-review SubAgent
   └── 隔离审查任务，避免污染主流程上下文

3. SubAgent 使用 security-check Skill
   └── 自动识别安全相关代码，应用专业审查规则

4. Hooks 记录审查日志
   └── 每次工具调用都记录，便于审计和调试

5. 结果通过 MCP 发送到 Slack
   └── 审查完成后通知相关人员
```

# 02｜过目不忘：Claude Code记忆系统与CLAUDE.md







