> 参考资料：https://code.claude.com/docs/zh-CN/overview

# 01 | 工具和插件

## 1.1 Model Context Protocol(MCP)

### 使用 MCP 可以做什么

连接 MCP 服务器后，您可以要求 Claude Code：

- 从问题跟踪器实现功能：“添加 JIRA 问题 ENG-4521 中描述的功能，并在 GitHub 上创建 PR。”
- 分析监控数据：“检查 Sentry 和 Statsig 以检查 ENG-4521 中描述的功能的使用情况。”
- 查询数据库：“根据我们的 PostgreSQL 数据库，查找使用功能 ENG-4521 的 10 个随机用户的电子邮件。”
- 集成设计：“根据在 Slack 中发布的新 Figma 设计更新我们的标准电子邮件模板”
- 自动化工作流：“创建 Gmail 草稿，邀请这 10 个用户参加关于新功能的反馈会议。”
- 对外部事件做出反应：MCP 服务器也可以充当[频道](https://code.claude.com/docs/zh-CN/channels)，将消息推送到您的会话中，因此当您不在时，Claude 可以对 Telegram 消息、Discord 聊天或 webhook 事件做出反应。

### 安装 MCP 服务器

- 选项 1：添加远程 HTTP 服务器

```shell
# 基本语法
claude mcp add --transport http <name> <url>

# 真实示例：连接到 Notion
claude mcp add --transport http notion https://mcp.notion.com/mcp

# 带有 Bearer 令牌的示例
claude mcp add --transport http secure-api https://api.example.com/mcp \
  --header "Authorization: Bearer your-token"
```

- 选项 2：添加远程 SSE 服务器

> SSE (Server-Sent Events) 传输已弃用。请在可用的地方使用 HTTP 服务器。

- 选项 3：添加本地 stdio 服务器

```shell
#Stdio 服务器作为您机器上的本地进程运行。它们非常适合需要直接系统访问或自定义脚本的工具。

# 基本语法
claude mcp add [options] <name> -- <command> [args...]
```

所有选项（`--transport`、`--env`、`--scope`、`--header`）必须在服务器名称之前。然后 `--`（双破折号）将服务器名称与传递给 MCP 服务器的命令和参数分开。例如：

```shell
# 运行 `npx server`
claude mcp add --transport stdio myserver -- npx server

# 运行 `python server.py --port 8080`，环境中有 `KEY=value`
claude mcp add --transport stdio --env KEY=value myserver -- python server.py --port 8080
```

这可以防止 Claude 的标志与服务器标志之间的冲突。


- 选项 4：从 JSON 添加 MCP 服务器

```shell
# 基本语法
claude mcp add-json <name> '<json>'

# 示例：添加带有 JSON 配置的 HTTP 服务器
claude mcp add-json weather-api '{"type":"http","url":"https://api.weather.com/mcp","headers":{"Authorization":"Bearer token"}}'

# 示例：添加带有 JSON 配置的 stdio 服务器
claude mcp add-json local-weather '{"type":"stdio","command":"/path/to/weather-cli","args":["--api-key","abc123"],"env":{"CACHE_DIR":"/tmp"}}'

# 示例：添加带有预配置 OAuth 凭据的 HTTP 服务器
claude mcp add-json my-server '{"type":"http","url":"https://mcp.example.com/mcp","oauth":{"clientId":"your-client-id","callbackPort":8080}}' --client-secret
```

### MCP 安装范围

- 本地范围：默认配置级别，存储在您项目路径下的 `~/.claude.json` 中

```shell
# 添加本地范围的服务器（默认）
claude mcp add --transport http stripe https://mcp.stripe.com

# 显式指定本地范围
claude mcp add --transport http stripe --scope local https://mcp.stripe.com
```

- 项目范围：存储配置在项目根目录 `.mcp.json` 文件中

```shell
# 添加项目范围的服务器
claude mcp add --transport http paypal --scope project https://mcp.paypal.com/mcp
```

- 用户范围：存储在 `~/.claude.json` 中

```shell
# 添加用户服务器
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic
```

> `.mcp.json` 中的环境变量支持的语法：
>
> - `${VAR}` - 扩展为环境变量 `VAR` 的值
> - `${VAR:-default}` - 如果设置了 `VAR`，则扩展为 `VAR`，否则使用 `default`
>
> 示例：
>
> ```json
> {
>   "mcpServers": {
>     "api-server": {
>       "type": "http",
>       "url": "${API_BASE_URL:-https://api.example.com}/mcp",
>       "headers": {
>         "Authorization": "Bearer ${API_KEY}"
>       }
>     }
>   }
> }
> ```

### 实际示例

- 示例1：连接到 GitHub 进行代码审查

```shell
#1、添加mcp服务
claude mcp add --transport http github https://api.githubcopilot.com/mcp/
#2、进行身份验证（按照浏览器中的步骤登录）
/mcp
#3、然后使用 GitHub
- `审查 PR #456 并建议改进`
- `为我们刚发现的错误创建新问题`
- `显示分配给我的所有开放 PR`
```

- 示例2：查询您的 PostgreSQL 数据库

```shell
#1、添加mcp服务
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub \
  --dsn "postgresql://readonly:pass@prod.db.com:5432/analytics"
#2、然后自然地查询您的数据库
- `本月我们的总收入是多少？`
- `显示订单表的架构`
- `查找 90 天内未进行购买的客户`
```

## 1.2 通过市场发现和安装预构建插件

插件通过 skills、agents、hooks 和 MCP servers 扩展 Claude Code。

### 添加插件

1、添加市场

```shell
#从 GitHub 添加, 使用 owner/repo 格式
`/plugin marketplace add anthropics/claude-code`
#从其他 Git 主机添加(使用 HTTPS)
`/plugin marketplace add https://gitlab.com/company/plugins.git`
#从其他 Git 主机添加(使用 SSH)
`/plugin marketplace add git@gitlab.com:company/plugins.git`
#从其他 Git 主机添加(特定分支或标签)
`/plugin marketplace add https://gitlab.com/company/plugins.git#v1.0.0`
#从本地路径添加
`/plugin marketplace add ./my-marketplace`
#从远程 URL 添加
`/plugin marketplace add https://example.com/marketplace.json`
```

2、浏览可用插件：运行 `/plugin` 打开插件管理器

3、安装插件：选择一个插件以查看其详细信息，然后选择安装范围；也可以从命令行直接安装。

```shell
#默认安装到用户范围
`/plugin install plugin-name@marketplace-name`
```

4、使用您的新插件：运行 `/reload-plugins` 以激活插件

插件命令由插件名称命名：

```claude
/commit-commands:commit
```

### 创建插件

1、创建插件目录

```shell
mkdir my-first-plugin
```

2、创建插件清单

```shell
mkdir my-first-plugin/.claude-plugin
```

然后使用以下内容创建 `my-first-plugin/.claude-plugin/plugin.json`：

```json
{
  "name": "my-first-plugin",
  "description": "A greeting plugin to learn the basics",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  }
}
```

3、添加 skill

```shell
mkdir -p my-first-plugin/skills/hello
```

然后使用以下内容创建 `my-first-plugin/skills/hello/SKILL.md`：

```markdown
---
description: Greet the user with a friendly message
disable-model-invocation: true
---

Greet the user warmly and ask how you can help them today.
```

4、测试你的插件

```shell
#加载你的插件
claude --plugin-dir ./my-first-plugin
#尝试你的新 skill
/my-first-plugin:hello
```

5、添加 skill 参数

通过接受用户输入使你的 skill 动态化。`$ARGUMENTS` 占位符捕获用户在 skill 名称后提供的任何文本。更新你的 `SKILL.md` 文件：

```markdown
---
description: Greet the user with a personalized message
---

# Hello Skill

Greet the user named "$ARGUMENTS" warmly and ask how you can help them today. Make the greeting personal and encouraging.
```

# 02 | 相关命令

## 2.1 CLI参考

### CLI命令

| 命令            | 描述           | 示例            |
| :-------------- | :------------- | :-------------- |
| `claude update` | 更新到最新版本 | `claude update` |

### CLI标志

| 标志                                   | 描述                                                         | 示例                                                         |
| :------------------------------------- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| `--allow-dangerously-skip-permissions` | 将 `bypassPermissions` 添加到 `Shift+Tab` 模式循环中而不启动它。允许您以不同的模式（如 `plan`）开始，稍后切换到 `bypassPermissions`。请参阅 [权限模式](https://code.claude.com/docs/zh-CN/permission-modes#skip-all-checks-with-bypasspermissions-mode) | `claude --permission-mode plan --allow-dangerously-skip-permissions` |
| `--effort`                             | 为当前会话设置 [工作量级别](https://code.claude.com/docs/zh-CN/model-config#adjust-effort-level)。选项：`low`、`medium`、`high`、`max`（仅限 Opus 4.6）。会话范围内，不会持久化到设置 | `claude --effort high`                                       |
| `--fork-session`                       | 恢复时，创建新的会话 ID 而不是重用原始 ID（与 `--resume` 或 `--continue` 一起使用） | `claude --resume abc123 --fork-session`                      |
| `--ide`                                | 如果恰好有一个有效的 IDE 可用，则在启动时自动连接到 IDE      | `claude --ide`                                               |
| `--name`, `-n`                         | 为会话设置显示名称，显示在 `/resume` 和终端标题中。您可以使用 `claude --resume <name>` 恢复命名会话。 | `claude -n "my-feature-work"`                                |
| `--settings`                           | 设置 JSON 文件的路径或 JSON 字符串以加载其他设置             | `claude --settings ./settings.json`                          |
| `--worktree`, `-w`                     | 在隔离的 [git worktree](https://code.claude.com/docs/zh-CN/common-workflows#run-parallel-claude-code-sessions-with-git-worktrees) 中启动 Claude，位于 `<repo>/.claude/worktrees/<name>`。如果未给出名称，则自动生成一个 | `claude -w feature-auth`                                     |

## 2.2 内置命令

| 命令                      | 用途                                                         |
| :------------------------ | :----------------------------------------------------------- |
| `/btw <question>`         | 提出快速[附加问题](https://code.claude.com/docs/zh-CN/interactive-mode#side-questions-with-btw)，无需添加到对话中 |
| `/clear`                  | 清除对话历史记录并释放上下文。别名：`/reset`、`/new`         |
| `/color [color|default]`  | 为当前会话设置提示栏颜色。可用颜色：`red`、`blue`、`green`、`yellow`、`purple`、`orange`、`pink`、`cyan`。使用 `default` 重置 |
| `/compact [instructions]` | 压缩对话，可选择性地提供焦点说明                             |
| `/config`                 | 打开[设置](https://code.claude.com/docs/zh-CN/settings)界面以调整主题、模型、[输出样式](https://code.claude.com/docs/zh-CN/output-styles)和其他偏好设置。别名：`/settings` |
| `/copy [N]`               | 将最后一个助手响应复制到剪贴板。传递数字 `N` 以复制第 N 个最新响应：`/copy 2` 复制倒数第二个。当存在代码块时，显示交互式选择器以选择单个块或完整响应。在选择器中按 `w` 将选择内容写入文件而不是剪贴板，这在 SSH 上很有用 |
| `/desktop`                | 在 Claude Code Desktop 应用中继续当前会话。仅限 macOS 和 Windows。别名：`/app` |
| `/doctor`                 | 诊断并验证您的 Claude Code 安装和设置                        |
| `/export [filename]`      | 将当前对话导出为纯文本。使用文件名时，直接写入该文件。不使用文件名时，打开对话框以复制到剪贴板或保存到文件 |
| `/fast [on|off]`          | 切换[快速模式](https://code.claude.com/docs/zh-CN/fast-mode)开启或关闭 |
| `/ide`                    | 管理 IDE 集成并显示状态                                      |
| `/init`                   | 使用 `CLAUDE.md` 指南初始化项目。设置 `CLAUDE_CODE_NEW_INIT=1` 以获得交互式流程，该流程还会引导您完成 skills、hooks 和个人内存文件 |
| `/memory`                 | 编辑 `CLAUDE.md` 内存文件，启用或禁用 [auto-memory](https://code.claude.com/docs/zh-CN/memory#auto-memory)，并查看自动内存条目 |
| `/rename [name]`          | 重命名当前会话并在提示栏上显示名称。不使用名称时，从对话历史记录自动生成一个 |
| `/resume [session]`       | 按 ID 或名称恢复对话，或打开会话选择器。别名：`/continue`    |
| `/rewind`                 | 将对话和/或代码倒回到上一个点，或从选定的消息进行总结。请参阅 [checkpointing](https://code.claude.com/docs/zh-CN/checkpointing)。别名：`/checkpoint` |
| `/tasks`                  | 列出并管理后台任务。也可用作 `/bashes`                       |
| ~~`/vim`~~                | ~~在 Vim 和普通编辑模式之间切换~~                            |
| ~~`/voice`~~              | ~~切换推送通话[语音听写](https://code.claude.com/docs/zh-CN/voice-dictation)。需要 Claude.ai 账户~~ |



