> 参考资料：https://code.claude.com/docs/zh-CN/overview

# 01 | 快速开始

## 1.1 概览

**Claude Code 为您做什么**

- 制定计划并执行：用纯英文告诉 Claude 您想构建什么。它将制定计划、编写代码并确保其正常工作。
- 调试及修复问题：描述一个错误信息，Claude Code 将分析您的代码库、识别问题并实施修复。
- 导航代码库：Claude Code 维护对整个项目结构的认识，并且通过 [MCP](https://code.claude.com/docs/zh-CN/mcp) 可以从 Google Drive、Figma 和 Slack 等外部数据源提取数据。
- 执行繁琐任务：解决合并冲突。

 **在任何地方使用 Claude Code**

Claude Code 在您的整个开发环境中工作：在您的终端、IDE、云中和 Slack 中。

- **[终端 (CLI)](https://code.claude.com/docs/zh-CN/quickstart)**：核心 Claude Code 体验。在任何终端中运行 `claude` 开始编码。
- **[网络上的 Claude Code](https://code.claude.com/docs/zh-CN/claude-code-on-the-web)**：从您的浏览器在 [claude.ai/code](https://claude.ai/code) 或 Claude iOS 应用中使用 Claude Code，无需本地设置。并行运行任务、处理您本地没有的仓库，并在内置的 diff 视图中查看更改。
- **[桌面应用](https://code.claude.com/docs/zh-CN/desktop)**：一个独立应用程序，具有 diff 审查、通过 git worktrees 的并行会话以及启动云会话的能力。
- **[VS Code](https://code.claude.com/docs/zh-CN/vs-code)**：一个原生扩展，具有内联 diff、@-提及和计划审查。
- **[JetBrains IDE](https://code.claude.com/docs/zh-CN/jetbrains)**：IntelliJ IDEA、PyCharm、WebStorm 和其他 JetBrains IDE 的插件，具有 IDE diff 查看和上下文共享。
- **[GitHub Actions](https://code.claude.com/docs/zh-CN/github-actions)**：使用 `@claude` 提及在 CI/CD 中自动化代码审查、问题分类和其他工作流。
- **[GitLab CI/CD](https://code.claude.com/docs/zh-CN/gitlab-ci-cd)**：GitLab 合并请求和问题的事件驱动自动化。
- **[Slack](https://code.claude.com/docs/zh-CN/slack)**：在 Slack 中提及 Claude 以将编码任务路由到网络上的 Claude Code 并获取 PR。
- **[Chrome](https://code.claude.com/docs/zh-CN/chrome)**：将 Claude Code 连接到您的浏览器以进行实时调试、设计验证和网络应用测试。

## 1.2 快速入门

**步骤 1：安装 Claude Code**

**步骤 2：登录您的账户**

```shell
claude
# 首次使用时系统会提示您登录
/login
# 按照提示使用您的账户登录
```

**步骤 3：启动您的第一个会话**

在任何项目目录中打开您的终端并启动 Claude Code：

```
cd /path/to/your/project
claude
```

 **步骤 4：提出您的第一个问题**

让我们从了解您的代码库开始。尝试以下命令之一：

```
> what does this project do?
```

**步骤 5：进行您的第一次代码更改**

现在让我们让 Claude Code 进行一些实际的编码。尝试一个简单的任务：

```
> add a hello world function to the main file
```

Claude Code 将：

1. 找到合适的文件
2. 向您显示建议的更改
3. 请求您的批准
4. 进行编辑

**步骤 6：在 Claude Code 中使用 Git**

Claude Code 使 Git 操作变得对话式：

```
> what files have I changed?
```

**步骤 7：修复错误或添加功能**

Claude 擅长调试和功能实现。用自然语言描述您想要的内容：

```
> add input validation to the user registration form
```

Claude Code 将：

- 定位相关代码
- 理解上下文
- 实现解决方案
- 如果可用，运行测试

**步骤 8：尝试其他常见工作流**

**重构代码**

```
> refactor the authentication module to use async/await instead of callbacks
```

**编写测试**

```
> write unit tests for the calculator functions
```

**更新文档**

```
> update the README with installation instructions
```

**代码审查**

```
> review my changes and suggest improvements
```

# 02 | 核心概念

## 2.1 Claude Code 如何工作

**代理循环**

当您给 Claude 一个任务时，它会经历三个阶段：收集上下文、采取行动和验证结果。这些阶段相互融合。Claude 始终使用工具，无论是搜索文件以了解您的代码、编辑以进行更改，还是运行测试以检查其工作。

![image-20260402153144449](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202604021531588.png)

- 模型

Claude Code 使用 Claude 模型来理解您的代码并推理任务。

- 工具

工具是使 Claude Code 成为代理的原因。有了工具，Claude 可以采取行动：读取您的代码、编辑文件、运行命令、搜索网络并与外部服务交互。每个工具使用都会返回信息，反馈到循环中，告知 Claude 的下一个决定。

**使用会话**

Claude Code 在您工作时将您的对话保存在本地。每条消息、工具使用和结果都被存储。

- 跨分支工作

每个 Claude Code 对话都是一个与您当前目录相关的会话。当您切换分支时，Claude 看到新分支的文件，但您的对话历史保持不变。Claude 记得您讨论过的内容，即使在切换后也是如此。

- 恢复或分叉会话

当您使用 `claude --continue` 或 `claude --resume` 恢复会话时，您使用相同的会话 ID 从中断处继续。

如果您在多个终端中恢复相同的会话，两个终端都会写入相同的会话文件，来自两者的消息会交错。对于从相同起点的并行工作，使用 `--fork-session` 为每个终端提供自己的干净会话。

```shell
claude --continue --fork-session
```

- 上下文窗口

当上下文填满时，Claude Code 会自动管理上下文。它首先清除较旧的工具输出，然后在需要时总结对话。您的请求和关键代码片段被保留；对话早期的详细说明可能会丢失。

除了压缩，您可以使用 skills 和 subagents 管理上下文。

**使用检查点和权限保持安全**

每个文件编辑都是可逆的。 在 Claude 编辑任何文件之前，它会对当前内容进行快照。如果出现问题，按两次 `Esc` 以回退到之前的状态，或要求 Claude 撤销。

**有效使用 Claude Code**

- 向 Claude Code 寻求帮助

Claude Code 可以教您如何使用它。提出问题，如”我如何设置 hooks？“或”构建我的 CLAUDE.md 的最佳方式是什么？“，Claude 会解释。

- 给 Claude 一些东西来验证

Claude 在能够检查自己的工作时表现更好。包括测试用例、粘贴预期 UI 的屏幕截图或定义您想要的输出。

```
实现 validateEmail。测试用例：'user@example.com' → true，
'invalid' → false，'user@.com' → false。之后运行测试。
```

## 2.2 扩展 Claude Code

- [CLAUDE.md](https://code.claude.com/docs/zh-CN/memory) 添加 Claude 每个会话都能看到的持久上下文
- [Skills](https://code.claude.com/docs/zh-CN/skills) 添加可重用的知识和可调用的工作流
- [MCP](https://code.claude.com/docs/zh-CN/mcp) 将 Claude 连接到外部服务和工具
- [Subagents](https://code.claude.com/docs/zh-CN/sub-agents) 在隔离的上下文中运行自己的循环，返回摘要
- [Agent teams](https://code.claude.com/docs/zh-CN/agent-teams) 协调多个独立会话，具有共享任务和点对点消息传递
- [Hooks](https://code.claude.com/docs/zh-CN/hooks) 完全在循环外作为确定性脚本运行
- [Plugins](https://code.claude.com/docs/zh-CN/plugins) 和 [marketplaces](https://code.claude.com/docs/zh-CN/plugin-marketplaces) 打包和分发这些功能

# 03 | 使用 Claude Code

## 3.1 存储指令和记忆

每个 Claude Code 会话都从一个全新的上下文窗口开始。两种机制可以跨会话传递知识：

- CLAUDE.md 文件：你编写的指令，为 Claude 提供持久上下文
- 自动记忆：Claude 根据你的更正和偏好自己编写的笔记

**CLAUDE.md 文件**

运行 `/init` 自动生成起始 CLAUDE.md。Claude 分析你的代码库并创建一个包含构建命令、测试指令和它发现的项目约定的文件。如果 CLAUDE.md 已存在，`/init` 会建议改进而不是覆盖它。

Claude Code 读取 `CLAUDE.md`，而不是 `AGENTS.md`。如果你的项目已经为其他 Code Agent 使用 `AGENTS.md`，创建一个导入它的 `CLAUDE.md`，这样两个工具都可以读取相同的指令而无需重复。

```markdown
@AGENTS.md

## Claude Code

对 `src/billing/` 下的更改使用 plan mode。
```

- CLAUDE.md 文件如何加载

从上层目录加载：Claude Code 通过从当前工作目录向上遍历目录树来读取 CLAUDE.md 文件，检查沿途的每个目录。这意味着如果你在 `foo/bar/` 中运行 Claude Code，它会从 `foo/bar/CLAUDE.md` 和 `foo/CLAUDE.md` 加载指令。

从其他目录加载：要从其他目录加载 CLAUDE.md 文件，包括 `CLAUDE.md`、`.claude/CLAUDE.md` 和 `.claude/rules/*.md`，设置 `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` 环境变量：

```shell
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 claude --add-dir ../shared-config
```

> 试了不行！

- 排除特定的 CLAUDE.md 文件

在大型项目 monorepos 中，项目根目录下的 CLAUDE.md 文件可能包含与你的工作无关的指令。`claudeMdExcludes` 设置让你按路径或 glob 模式跳过特定文件。

```json
{
  "claudeMdExcludes": [
    "**/monorepo/CLAUDE.md",
    "/home/user/monorepo/other-team/.claude/rules/**"
  ]
}
```

**自动记忆**

自动记忆让 Claude 跨会话积累知识，无需你编写任何内容。Claude 在工作时为自己保存笔记：构建命令、调试见解、架构笔记、代码样式偏好和工作流习惯。

每个项目在 `~/.claude/projects/<project>/memory/` 获得自己的记忆目录。要将自动记忆存储在不同位置，在你的用户或本地设置中设置 `autoMemoryDirectory`：

```json
{
  "autoMemoryDirectory": "~/my-custom-memory-dir"
}
```

`/memory` 命令列出在你当前会话中加载的所有 CLAUDE.md 和规则文件，让你切换自动记忆开或关，并提供打开自动记忆文件夹的链接。

## 3.2 权限模式

| 模式                                                         | Claude 无需询问即可执行的操作 | 最适合                         |
| :----------------------------------------------------------- | :---------------------------- | :----------------------------- |
| `default`                                                    | 读取文件                      | 入门、敏感工作                 |
| `acceptEdits`                                                | 读取和编辑文件                | 迭代您正在审查的代码           |
| [`plan`](https://code.claude.com/docs/zh-CN/permission-modes#analyze-before-you-edit-with-plan-mode) | 读取文件                      | 探索代码库、规划重构           |
| [`auto`](https://code.claude.com/docs/zh-CN/permission-modes#eliminate-prompts-with-auto-mode) | 所有操作，带后台安全检查      | 长时间运行的任务、减少提示疲劳 |
| [`bypassPermissions`](https://code.claude.com/docs/zh-CN/permission-modes#skip-all-checks-with-bypasspermissions-mode) | 所有操作，无检查              | 仅隔离容器和 VM                |
| [`dontAsk`](https://code.claude.com/docs/zh-CN/permission-modes#allow-only-pre-approved-tools-with-dontask-mode) | 仅预先批准的工具              | 锁定环境                       |

## 3.3 常见工作流程

**理解新的代码库**

假设您刚加入一个新项目，需要快速了解其结构。

1、导航到项目根目录

```
cd /path/to/project
```

2、启动 Claude Code

```
claude
```

3、求高级概览

```
give me an overview of this codebase
```

4、深入了解特定组件

```
explain the main architecture patterns used here
what are the key data models?
how is authentication handled?
```

**命名您的会话**

给会话起描述性名称以便稍后找到它们。这是在处理多个任务或功能时的最佳实践。

1、命名会话

在启动时使用 `-n` 命名会话：

```
claude -n auth-refactor
```

或在会话期间使用 `/rename`，这也会在提示栏上显示名称：

```
/rename auth-refactor
```

您也可以从选择器重命名任何会话：运行 `/resume`，导航到会话，然后按 `R`。

2、稍后按名称恢复

从命令行：

```
claude --resume auth-refactor
```

或从活跃会话内：

```
/resume auth-refactor
```

## 3.4 Claude Code 最佳实践



# 04 | 平台和集成



