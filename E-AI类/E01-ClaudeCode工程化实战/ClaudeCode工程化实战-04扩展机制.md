> 来自极客时间《Claude Code工程化实战》--黄佳

# <mark>扩展机制（15~16）</mark>

# 15｜防微杜渐：Hooks 事件驱动自动化

今天我们进入一个全新的领域——Hooks，事件驱动自动化。它是 Claude Code 三大扩展机制中唯一能拦截和修改 Claude 行为的机制，也是工程化实践中安全防线的最后一道闸门。

**Hooks 的本质——AI 时代的中间件**

如果你有 Web 开发经验，你一定熟悉中间件（Middleware）的概念。

```
请求 → 中间件1 → 中间件2 → 中间件3 → 处理函数
                    ↓
              认证、日志、限流
```

Claude Code 的 Hooks 机制与此异曲同工，但它针对的不是 HTTP 请求，而是  AI Agent 的工具调用。

```
用户请求 → Claude 决策 → [PreToolUse Hook] → 工具执行 → [PostToolUse Hook] → 响应
                              ↓                            ↓
                         权限检查、拦截             格式化、验证、日志
```

**17 种 Hook 事件——完整生命周期覆盖**

截至 2026 年 3 月，根据  Anthropic 官方文档，Claude Code 支持  17 种 Hook 事件，覆盖了从会话启动到结束的完整生命周期：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202604202142359.jpeg)

**Hook 配置详解**

怎么选择配置位置？一个简单的判断流程：

- 用户级（~/.claude/settings.json）：个人习惯。比如你喜欢的日志格式、桌面通知方式。这些配置只影响你自己，不需要和团队同步。
- 项目级（.claude/settings.json）：团队约定。比如代码格式化规则、敏感文件保护列表。这些配置应该提交到 git，让团队所有成员共享。
- 本地覆盖（.claude/settings.local.json）：当你需要在本地临时覆盖团队配置时使用，比如调试时关闭某个 Hook。
- 子代理 frontmatter：子代理专属的 Hook。比如  db-reader 的 SQL 注入检查——这个检查只和数据库操作相关，不应该影响其他场景。

一个典型的 Hook 配置长这样：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "./hooks/block-dangerous.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "prettier --write $CLAUDE_FILE_PATH"
          }
        ]
      }
    ]
  }
}
```

这个 JSON 结构有三层嵌套，初看可能有点绕。让我用树形图来拆解它的逻辑层次。

```
hooks                            ← 第一层：顶层容器
├── PreToolUse                   ← 第二层：事件类型（什么时候触发）
│   └── [第一组规则]
│       ├── matcher: "Bash"      ← 第三层：匹配器（针对哪个工具）
│       └── hooks: [...]         ← 第三层：Hook 列表（执行什么）
│           └── type: "command"
│           └── command: "..."
└── PostToolUse
    └── [第二组规则]
        ├── matcher: "Write"
        └── hooks: [...]
```

Matcher 匹配用于指定 Hook 应用于哪些工具。它支持四种匹配模式：

```
// 精确匹配单个工具
"matcher": "Write"

// 匹配多个工具（用竖线分隔）
"matcher": "Edit|Write|MultiEdit"

// 匹配所有工具
"matcher": "*"

// 空匹配（用于生命周期事件）
"matcher": ""
```

**四种 Hook 执行类型**

当一个 Hook 被触发后，其具体执行方式有四种。

- Command 类型——执行 Shell 脚本

```json
{
  "type": "command",
  "command": "./hooks/check-security.sh",
  "timeout": 30000  //指定超时时间（毫秒），默认 60 秒
}
```

- Prompt 类型——LLM 评估

Prompt 类型会用一个小型 LLM（通常是 Haiku）来评估当前情况。比如“这段代码是否有安全隐患”。

```json
{
  "type": "prompt",
  "prompt": "Evaluate if this task was completed correctly. Check for any errors or incomplete work."
}
```

- Agent 类型——子代理评估

Agent Hook 会启动一个子代理，这个子代理可以使用 Read、Grep、Glob 等工具来验证条件。比如验证“所有公共 API 都有文档注释”。

```json
{
  "type": "agent",
  "prompt": "Verify that all unit tests pass. Run the test suite and check the results. $ARGUMENTS",
  "timeout": 120
}
```

- HTTP 类型

它不在本地执行逻辑，而是把事件数据以 POST 请求发送到远程 HTTP 端点，由远程服务返回决策结果。适合团队共享审计服务、集中式安全扫描等场景。我们会在下一讲详细展开。

**PreToolUse：工具执行前的守门员**

要写出有效的 PreToolUse Hook，你需要理解它的通信协议——脚本从 stdin 读入什么数据、向 Claude 返回什么决策。我们快速过一遍，然后直接进入实战。

每个 Hook 脚本通过 stdin 接收一个 JSON 对象，包含做出判断所需的全部上下文。

```json
{
  "session_id": "abc123",  //谁在执行
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/project/root",  //在哪里执行
  "permission_mode": "default",  //什么权限模式
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",  //要执行什么工具
  "tool_input": {  //什么参数
    "command": "rm -rf /tmp/test"
  }
}
```

有了这些信息，你的脚本就能精准判断这个操作是否安全。

Hook 脚本通过退出码和 stdout JSON 告诉 Claude 下一步做什么。最简单的方式是用退出码——exit 0 表示放行，exit 2 表示阻止，其他非零退出码表示脚本出错但不阻止。

需要更精细的控制时，通过 stdout 输出 JSON 决策。官方推荐的  hookSpecificOutput 格式支持四种响应方式。

- 允许执行——检查通过，放行

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow"
  }
}
```

- 拒绝执行——发现危险操作，直接拦截。permissionDecisionReason 会反馈给 Claude。

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "This command is not allowed"
  }
}
```

- 交给用户确认——操作不是明确的“安全”或“危险”，而是“需要人类判断”。

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "This command modifies production data"
  }
}
```

- 修改输入后执行——不拦截操作，而是改写参数后放行

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "updatedInput": {
      "command": "rm -rf /tmp/test --dry-run"
    }
  }
}
```

比如用户要执行  rm -rf /tmp/test，你可以把它改成  rm -rf /tmp/test --dry-run，先看看会删什么再说。

### PreToolUse 实战案例 1：阻止危险命令

每个工程团队都有一些“绝对不能执行”的命令。rm -rf / 会删除整个文件系统，git push --force origin main 会覆盖远程主分支的历史，DROP DATABASE 会销毁整个数据库。这些命令的共同特点是：一旦执行就无法挽回。

> 人在清醒状态下当然不会执行它们，但 Claude 作为 AI 有时会过于“积极”——如果用户说”清理一下项目”，Claude 可能会把  rm -rf 理解得过于字面。

下面这个脚本用模式匹配来拦截这些灾难性命令：（脚本位于hooks/block-dangerous.sh）

```bash
#!/bin/bash
# block-dangerous.sh

set -e

# 从 stdin 读取 Claude 传入的 JSON 数据
INPUT=$(cat)

# 提取要执行的命令字符串
# // ""  是 jq 的空值保护——如果字段不存在，返回空字符串而不是报错
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

# 调试信息必须输出到 stderr（文件描述符 2），而不是 stdout
# 因为 stdout 被 Claude 用来读取 JSON 决策——如果你往 stdout 打了一行调试文本，Claude 会因为 JSON 解析失败而报错
echo "DEBUG: Checking command: $COMMAND" >&2

# 定义了所有需要拦截的命令模式
DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf ~"
    "rm -rf \$HOME"
    "rm -rf /*"
    "> /dev/sd"
    "mkfs."
    "dd if="
    ":(){:|:&};:"               # Fork bomb
    "chmod -R 777 /"
    "git push --force origin main"
    "git push --force origin master"
    "git reset --hard origin"
    "DROP DATABASE"
    "DROP TABLE"
    "TRUNCATE"
    #这是一种常见的攻击手法：从网络下载脚本并直接执行，绕过任何安全审查
    "curl.*| sh"  # 危险的管道执行
    "curl.*| bash"  # 危险的管道执行
    "wget.*| sh"  # 危险的管道执行
    "wget.*| bash"  # 危险的管道执行
)

# 检查每个危险模式
for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if [[ "$COMMAND" == *"$pattern"* ]]; then
        echo "BLOCKED: Command matches dangerous pattern: $pattern" >&2
        cat <<EOF
{
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "Blocked dangerous command pattern: $pattern. This command could cause irreversible damage."
    }
}
EOF
        #exit 2 是“有意阻止”
        exit 2
    fi
done

# 命令安全，允许执行
echo '{}'
#exit 0 是“检查通过、放行”
exit 0
```

配置方式如下。

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "./hooks/block-dangerous.sh"
          }
        ]
      }
    ]
  }
}
```

接下来我们动手试一下。我们在 Claude Code 里实际触发一次拦截：

```bash
# 1. 确认 jq 可用
which jq

# 2. 进入项目目录（已配好 .claude/settings.json 和 hooks 脚本）
cd 06-Hooks/projects/01-safety-hooks

# 3. 启动 Claude Code
claude
```

进入会话后，故意让 Claude 执行一个危险命令：

```
请帮我执行 rm -rf /tmp/test，清理一下临时文件
```

Claude 收到拦截信息后，会自动调整策略——它不会傻傻地重试被拦截的命令，而是换一种更安全的方式来完成你的请求。整个过程你什么都不用做，防线自动运行。 

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202604202236027.png)

你也可以用管道手动验证脚本逻辑，不需要启动 Claude：

```bash
# 危险命令 → 预期 deny（exit 2）
echo '{"tool_input":{"command":"rm -rf /"}}' | ./hooks/block-dangerous.sh

# 安全命令 → 预期 allow（exit 0）
echo '{"tool_input":{"command":"git status"}}' | ./hooks/block-dangerous.sh
```

### PreToolUse 实战案例 2：保护敏感文件

### PostToolUse：工具执行后的质量守卫

### PostToolUse 实战案例 1：自动格式化

### PostToolUse 实战案例 2：自动 Lint 检查

### PostToolUse 实战案例 3：审计日志

# ==18｜庖丁解牛：Tools 工具系统内核剖析==