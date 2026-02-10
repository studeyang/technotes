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



# 03 | 终端外部

## 3.1 
