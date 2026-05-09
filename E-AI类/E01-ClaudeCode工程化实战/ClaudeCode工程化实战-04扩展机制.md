> 来自极客时间《Claude Code工程化实战》--黄佳

# <mark>扩展机制（15~18）</mark>

# 15｜防微杜渐：Hooks 事件驱动自动化

今天我们进入一个全新的领域——Hooks，事件驱动自动化。它是 Claude Code 三大扩展机制中唯一能拦截和修改 Claude 行为的机制，也是工程化实践中安全防线的最后一道闸门。

## Hooks 的本质——AI 时代的中间件

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

截至 2026 年 3 月，根据  [Anthropic 官方文档](https://code.claude.com/docs/en/hooks-guide)，Claude Code 支持  17 种 Hook 事件，覆盖了从会话启动到结束的完整生命周期：

| 事件               | 触发时机                      | 能否阻止？ | 典型用途                             |
| ------------------ | ----------------------------- | ---------- | ------------------------------------ |
| SessionStart       | 会话开始或恢复时              | (默认否)   | 环境初始化、注入上下文、设置环境变量 |
| UserPromptSubmit   | 用户提交输入后、Claude 处理前 | 能         | 输入预处理、输入校验、注入上下文     |
| **PreToolUse**     | 工具执行前                    | 能         | 权限检查、参数修改、危险操作拦截     |
| PermissionRequest  | 权限对话框弹出时              | 能         | 自动批准或拒绝权限请求               |
| **PostToolUse**    | 工具执行成功后                |            | 格式化、验证、日志记录               |
| PostToolUseFailure | 工具执行失败后                |            | 错误日志、告警、纠正性反馈           |
| Notification       | Claude 发送通知时             |            | 自定义通知方式（桌面提醒等）         |
| **SubagentStart**  | 子代理启动时                  |            | 为子代理注入上下文                   |
| **SubagentStop**   | 子代理完成时                  | 能         | 验证子任务结果、强制子代理继续       |
| **Stop**           | Claude 完成响应时             | 能         | 质量检查、自动测试                   |
| PreCompact         | 上下文压缩前                  |            | 手动/自动压缩时的预处理              |
| SessionEnd         | 会话结束时                    |            | 清理资源、记录统计                   |

**Hook 配置详解**

怎么选择配置位置？一个简单的判断流程：

- 用户级（~/.claude/settings.json）：个人习惯。比如你喜欢的日志格式、桌面通知方式。这些配置只影响你自己，不需要和团队同步。
- 项目级（.claude/settings.json）：团队约定。比如代码格式化规则、敏感文件保护列表。这些配置应该提交到 git，让团队所有成员共享。
- 本地覆盖（.claude/settings.local.json）：当你需要在本地临时覆盖团队配置时使用，比如调试时关闭某个 Hook。
- 子代理 frontmatter：子代理专属的 Hook。比如  db-reader 的 SQL 注入检查——这个检查只和数据库操作相关，不应该影响其他场景。

一个典型的 Hook 配置长这样：

```json
{
  "hooks": {                       //← 第一层：顶层容器
    "PreToolUse": [                //← 第二层：事件类型（什么时候触发）
      {                   // 第一组规则
        "matcher": "Bash",         //← 第三层：匹配器（针对哪个工具）
        "hooks": [                 //← 第四层：Hook 列表（执行什么）
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

第一种：Command 类型——执行 Shell 脚本

```json
{
  "type": "command",
  "command": "./hooks/check-security.sh",
  "timeout": 30000  //指定超时时间（毫秒），默认 60 秒
}
```

第二种：Prompt 类型——LLM 评估

Prompt 类型会用一个小型 LLM（通常是 Haiku）来评估当前情况。比如“这段代码是否有安全隐患”。

```json
{
  "type": "prompt",
  "prompt": "Evaluate if this task was completed correctly. Check for any errors or incomplete work."
}
```

第三种：Agent 类型——子代理评估

Agent Hook 会启动一个子代理，这个子代理可以使用 Read、Grep、Glob 等工具来验证条件。比如验证“所有公共 API 都有文档注释”。

```json
{
  "type": "agent",
  "prompt": "Verify that all unit tests pass. Run the test suite and check the results. $ARGUMENTS",
  "timeout": 120
}
```

第四种：HTTP 类型

它不在本地执行逻辑，而是把事件数据以 POST 请求发送到远程 HTTP 端点，由远程服务返回决策结果。适合团队共享审计服务、集中式安全扫描等场景。我们会在下一讲详细展开。

## PreToolUse：工具执行前的守门员

要写出有效的 PreToolUse Hook，你需要理解它的通信协议——脚本从 stdin 读入什么数据、向 Claude 返回什么决策。我们快速过一遍，然后直接进入实战。

每个 Hook 脚本通过 stdin 接收一个 JSON 对象，包含做出判断所需的全部上下文。

```json
{
  "session_id": "abc123",          //谁在执行
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/project/root",          //在哪里执行
  "permission_mode": "default",    //什么权限模式
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",             //要执行什么工具
  "tool_input": {                  //什么参数
    // Bash 工具传 command
    "command": "rm -rf /tmp/test", //什么参数
    // Write 和 Edit 工具传 file_path
    "file_path": ""
  }
}
```

有了这些信息，你的脚本就能精准判断这个操作是否安全。

Hook 脚本通过退出码和 stdout JSON 告诉 Claude 下一步做什么。最简单的方式是用退出码——exit 0 表示放行，exit 2 表示阻止，其他非零退出码表示脚本出错但不阻止。

需要更精细的控制时，通过 stdout 输出 JSON 决策。官方推荐的  hookSpecificOutput 格式支持四种响应方式。

> 以下描述了4种控制方式

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

**PreToolUse 实战案例 1：阻止危险命令**

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
    "curl.*| sh"    # 危险的管道执行
    "curl.*| bash"  # 危险的管道执行
    "wget.*| sh"    # 危险的管道执行
    "wget.*| bash"  # 危险的管道执行
)

# 检查每个危险模式
for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if [[ "$COMMAND" == *"$pattern"* ]]; then
        echo "BLOCKED: Command matches dangerous pattern: $pattern" >&2
        #stdout JSON 告诉 Claude 下一步做什么
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

**PreToolUse 实战案例 2：保护敏感文件**

另一个常见需求是保护敏感文件（如.env 文件）不被 Claude 修改或读取——即使 Claude 出于好意想“帮你整理一下配置文件”，敏感文件也绝对不能被触碰。

这种保护需要覆盖两个维度，文件本身（.env、credentials.json 等配置文件）和密钥文件（.pem、.key、id_rsa 等加密文件）。前者包含运行时密钥，后者包含身份认证凭据。两者泄露的后果都是灾难性的。脚本位于hooks/protect-files.sh。

```bash
#!/bin/bash
# protect-files.sh
# 保护敏感文件不被修改

set -e

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""')

# 如果没有文件路径，跳过检查
if [ -z "$FILE_PATH" ]; then
    echo '{}'
    exit 0
fi

# 敏感文件模式
PROTECTED_PATTERNS=(
    ".env"
    ".env.*"
    "credentials.json"
    "secrets.yaml"
    "secrets.yml"
    "*.pem"
    "*.key"
    "id_rsa"
    "id_ed25519"
    ".ssh/config"
    "kubeconfig"
)

for pattern in "${PROTECTED_PATTERNS[@]}"; do
    if [[ "$FILE_PATH" == *$pattern* ]]; then
        cat <<EOF
{
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "Cannot modify sensitive file: $FILE_PATH. This file may contain secrets or credentials."
    }
}
EOF
        exit 2
    fi
done

echo '{}'
exit 0
```

这个脚本的结构和  block-dangerous.sh 很像，都是黑名单匹配。但注意一个细节：它检查的是  tool_input.file_path 而不是  tool_input.command。不同的工具传入不同的参数字段——Bash 工具传  command，Write 和 Edit 工具传  file_path。

你的 Hook 脚本需要知道自己在拦截哪个工具，才能提取正确的字段。配置时，这个 Hook 要同时匹配 Write 和 Edit 两个工具。

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "./hooks/protect-files.sh"
          }
        ]
      }
    ]
  }
}
```

这个 Hook 会阻止 Claude 修改任何看起来像是敏感文件的东西。即使 Claude 误判了用户的意图，敏感文件也不会被触碰。安全防线的价值不在于它每天拦截多少次，而在于它在那个唯一需要的瞬间不会缺席。

## PostToolUse：工具执行后的质量守卫

PostToolUse 在工具成功执行后运行。它不能阻止已经发生的操作（文件已经写入了，命令已经执行了），但它可以做三件同样重要的事情：

- 后处理（格式化、清理）
- 反馈（向 Claude 提供 lint 结果、警告）
- 记录（写入审计日志）。

PostToolUse 接收的 JSON 比 PreToolUse 多一个关键字段——tool_response，即工具执行的结果：

```json
{
  "session_id": "abc123",
  "hook_event_name": "PostToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/project/src/app.js",
    "content": "..."
  },
  "tool_response": {
    "success": true,
    "result": "File written successfully"
  }
}
```

有了  tool_response，你的 Hook 脚本不仅知道“Claude 想做什么”，还将知道“做的结果怎样”。PostToolUse 最强大的能力在于通过  additionalContext 向 Claude 反馈信息：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "ESLint found 3 errors in the file you just wrote."
  }
}
```

additionalContext 的内容会被注入到 Claude 的上下文中，Claude 会看到这条反馈并据此调整行为。

比如你告诉它“ESLint 发现了 3 个错误”，它就会主动去修复这些错误。这不是简单的日志记录，而是一个闭环反馈机制——Hook 观察到问题，反馈给 Claude，Claude 自动修复。下面我们通过三个经典实战案例来体会这些能力。

**PostToolUse 实战案例 1：自动格式化**

这是最受欢迎的 PostToolUse 应用——每次 Claude 写入或修改文件后，自动运行格式化工具。

为什么自动格式化如此重要？因为 Claude 的代码风格和你团队的风格规范不一定一致。Claude 可能用 2 空格缩进，你团队用 4 空格；Claude 可能不加尾逗号，你团队的 Prettier 配置要求加。每次手动跑  prettier --write 太麻烦，也容易忘记。PostToolUse Hook 把这件事彻底自动化了——Claude 只管写代码，格式化自动发生。脚本位于hooks/auto-format.sh：

```bash
#!/bin/bash
# auto-format.sh
# 自动格式化代码文件

set -e

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""')

# 如果没有文件路径或文件不存在，跳过
if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
    echo '{}'
    exit 0
fi

echo "DEBUG: Formatting file: $FILE_PATH" >&2

# 获取文件扩展名
EXTENSION="${FILE_PATH##*.}"

# 通过文件扩展名自动选择格式化工具
case "$EXTENSION" in
    js|jsx|ts|tsx|json|md|css|scss|html)  # JavaScript/TypeScript 用 Prettier
        if command -v npx &> /dev/null; then  # 检查是否安装
            if npx prettier --write "$FILE_PATH" 2>&1; then
                echo '{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "Formatted with Prettier"}}'
            else
                echo '{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "Prettier formatting failed"}}'
            fi
        else  # Hook 的失败不应该阻碍正常工作流
            echo '{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "Prettier not available"}}'
        fi
        ;;
    py)  # Python 用 Black
        if command -v black &> /dev/null; then
            if black "$FILE_PATH" 2>&1; then
                echo '{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "Formatted with Black"}}'
            else
                echo '{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "Black formatting failed"}}'
            fi
        fi
        ;;
    go)  # Go 用 gofmt
        if command -v gofmt &> /dev/null; then
            gofmt -w "$FILE_PATH" 2>&1
            echo '{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "Formatted with gofmt"}}'
        fi
        ;;
    rs)  # Rust 用 rustfmt
        if command -v rustfmt &> /dev/null; then
            rustfmt "$FILE_PATH" 2>&1
            echo '{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "Formatted with rustfmt"}}'
        fi
        ;;
    *)
        echo '{}'
        ;;
esac

exit 0
```

这个脚本有几个值得注意的设计决策。

- 多语言策略：通过文件扩展名自动选择格式化工具。这意味着在一个多语言项目中，你只需要一个 Hook 脚本就能覆盖所有文件类型。
- 优雅降级：每种工具的调用都先用  command -v 检查是否安装。如果 Prettier 没装，脚本不会报错崩溃，而是优雅地跳过并通过  additionalContext 告诉 Claude “Prettier not available”。这很重要——Hook 的失败不应该阻碍正常工作流。
- 反馈闭环：格式化完成后，通过  additionalContext 告诉 Claude 用了什么工具格式化的。这不仅是日志记录，还让 Claude 知道格式化已经发生——它不需要自己再做一次。

这个 Hook 的美妙之处在于，Claude 不需要知道项目用什么格式化工具。无论是 Prettier、Black、gofmt 还是 rustfmt，只要本地安装了，就会自动应用。这就是中间件的力量——业务逻辑（Claude 写代码）和横切关注点（格式化）完全解耦。

**PostToolUse 实战案例 2：自动 Lint 检查**

格式化解决了“代码长什么样”的问题，Lint 检查解决的是“代码有没有问题”。两者结合，构成了一个完整的代码质量反馈循环：Claude 写代码 → 自动格式化 → 自动 Lint → 发现问题 → Claude 收到反馈 → Claude 修复。

这个循环全部自动发生，无需人工介入。脚本位于hooks/lint-check.sh：

```bash
#!/bin/bash
# lint-check.sh
# 自动运行 lint 检查并反馈结果

set -e

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""')

# 只检查 JS/TS 文件
if [[ "$FILE_PATH" == *.js || "$FILE_PATH" == *.ts || "$FILE_PATH" == *.jsx || "$FILE_PATH" == *.tsx ]]; then
    echo "DEBUG: Linting $FILE_PATH" >&2

    # || true 确保 ESLint 的退出码被捕获但不会触发脚本退出
    LINT_RESULT=$(npx eslint "$FILE_PATH" 2>&1) || true
    LINT_EXIT_CODE=$?

    if [ $LINT_EXIT_CODE -ne 0 ]; then
        # 有 lint 错误，反馈给 Claude
        ESCAPED_RESULT=$(echo "$LINT_RESULT" | head -30 | jq -Rs '.')
        cat <<EOF
{
    "hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": "ESLint found issues:\n$ESCAPED_RESULT"
    }
}
EOF
    else
        echo '{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "ESLint: No issues found"}}'
    fi
else
    echo '{}'
fi

exit 0
```

注意  || true 这个细节：ESLint 发现错误时会返回非零退出码，但我们不希望脚本因此中断（set -e 会让脚本在任何非零退出码时终止）。|| true 确保 ESLint 的退出码被捕获但不会触发脚本退出。

head -30 限制了反馈的长度。ESLint 的输出可能非常长，但我们只需要把前 30 行（通常包含了最关键的错误信息）反馈给 Claude 就够了。这又是一个“高噪声处理”的应用——和我们在第 6 讲学到的子代理噪声过滤是同一个思路。

这创造了一个自动化的质量循环：Claude 修改文件 → PostToolUse 触发 → Lint 检查 → 发现问题 → 反馈给 Claude → Claude 自动修复 → 再次触发 PostToolUse → 再次检查.……直到所有 Lint 错误消除。整个过程无需人工介入。

**PostToolUse 实战案例 3：审计日志**

对于金融、医疗、政府等合规性要求高的场景，你可能需要记录 Claude 的所有操作——不是为了阻止什么，而是为了事后追溯。谁在什么时间修改了什么文件？执行了什么命令？

这些信息在安全事件调查和合规审计中至关重要。脚本位于hooks/audit-log.sh：

```bash
#!/bin/bash
# audit-log.sh
# 记录所有工具调用

INPUT=$(cat)
# 如果 CLAUDE_PROJECT_DIR 环境变量存在就用它，否则用当前目录 .
LOG_FILE="${CLAUDE_PROJECT_DIR:-.}/.claude/audit.log"

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"

# 记录时间戳（如 2025-03-01T14:30:00+08:00）
TIMESTAMP=$(date -Iseconds)
# 工具名
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "unknown"')
# 输入摘要。jq -c 的 -c 参数表示“紧凑输出”，把 JSON 压缩成一行
TOOL_INPUT=$(echo "$INPUT" | jq -c '.tool_input // {}')

echo "[$TIMESTAMP] $TOOL_NAME: $TOOL_INPUT" >> "$LOG_FILE"

# 不阻止执行
echo '{}'
exit 0
```

这个脚本很短，但有几个细节值得注意。

- ${CLAUDE_PROJECT_DIR:-.} 使用了 Bash 的默认值语法——如果  CLAUDE_PROJECT_DIR 环境变量存在就用它，否则用当前目录 .。
- jq -c 的  -c 参数表示“紧凑输出”，把 JSON 压缩成一行，便于日志文件的每一行对应一次操作。
- date -Iseconds 生成 ISO 8601 格式的时间戳（如  2025-03-01T14:30:00+08:00），这是最标准的时间格式，方便后续用脚本解析。

配置时用  matcher: "*" 匹配所有工具，这样每次工具调用都会被记录：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "./hooks/audit-log.sh"
          }
        ]
      }
    ]
  }
}
```

审计日志的价值不在当下，而在未来。当你某天需要回答“上周三 Claude 到底改了什么导致了这个 bug”时，审计日志就是你的时光机。

# 16｜未雨绸缪：Hooks 高级模式与工程实践

PreToolUse 在工具执行前做“入口安检”，PostToolUse 在工具执行后做“过程质检”。但还有一个关键环节我们没有覆盖：Claude 做完整个任务后，谁来验收？

这道终检，就是 Stop Hook。除了 Stop Hook，这一讲中我们还会介绍子代理场景下的 SubagentStart 和 SubagentStop 事件、frontmatter 内置 Hooks 的精准控制、多 Hook 链的组合模式，以及 Hook 工程设计的系统方法论。

内容不少，我们将步步为营，把整个 Hook 体系的高级武器库全部打通。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202605091526812.jpeg)

## Stop Hook——任务完成时的质量门控

Stop Hook 在 Claude 完成响应后运行，它的核心能力是让 Claude 继续工作，这个能力来源于它的  continue 字段：

> 这也是 Stop Hook 和其他 Hook 的最大区别。

```json
{
  "decision": "block",
  "reason": "Tests are failing, please fix them",
  "continue": true
}
```

这创造了一个自动循环：Claude 认为完成了 → Stop Hook 检查 → 发现测试失败 → 把失败信息反馈给 Claude → Claude 继续修复 → 再次完成 → 再次检查……直到所有检查通过，Claude 才被允许真正停下来。

**实战：自动测试门控**

这是 Stop Hook 最经典的应用——Claude 完成任务后自动运行测试，测试不通过就不让停。

实战项目位于  hooks/run-tests.sh：

```bash
#!/bin/bash
# run-tests.sh
# 在 Claude 完成时自动运行测试

set -e

echo "DEBUG: Running tests before stopping..." >&2

# 确定项目目录
if [ -n "$CLAUDE_PROJECT_DIR" ]; then
    cd "$CLAUDE_PROJECT_DIR"
fi

# 检测项目类型并运行相应的测试
RUN_TESTS=false
TEST_RESULT=""
TEST_PASSED=true

# 通过检查特征文件来判断项目类型

# Node.js 项目
if [ -f "package.json" ]; then
    RUN_TESTS=true
    echo "DEBUG: Detected Node.js project" >&2
    # 先检查 package.json 中是否有 test 脚本
    if grep -q '"test"' package.json; then
        TEST_RESULT=$(npm test 2>&1) || TEST_PASSED=false
    else
        TEST_RESULT="No test script found in package.json"
        TEST_PASSED=true  # 没有测试不算失败
    fi

# Python 项目
elif [ -f "pytest.ini" ] || [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
    RUN_TESTS=true
    echo "DEBUG: Detected Python project" >&2

    if command -v pytest &> /dev/null; then
        TEST_RESULT=$(pytest 2>&1) || TEST_PASSED=false
    fi

# Go 项目
elif [ -f "go.mod" ]; then
    RUN_TESTS=true
    TEST_RESULT=$(go test ./... 2>&1) || TEST_PASSED=false

# Rust 项目
elif [ -f "Cargo.toml" ]; then
    RUN_TESTS=true
    TEST_RESULT=$(cargo test 2>&1) || TEST_PASSED=false
fi

# 如果没有检测到测试框架
if [ "$RUN_TESTS" = false ]; then
    echo '{}'
    exit 0
fi

# 转义 JSON 特殊字符
# 只取测试输出的前 50 行（Claude 只需要看到关键的错误信息就能定位问题，传入太多信息反而会稀释重点）
TEST_RESULT_ESCAPED=$(echo "$TEST_RESULT" | head -50 | jq -Rs '.')

if [ "$TEST_PASSED" = true ]; then
    # 测试通过，允许停止
    echo '{"decision": "approve", "reason": "All tests passed."}'
else
    # 测试失败，让 Claude 继续修复
    cat <<EOF
{
    "decision": "block",
    "reason": "Tests are failing. Please fix the issues before stopping.",
    "continue": true,  # 强制 Claude 继续工作
    "systemMessage": $TEST_RESULT_ESCAPED
}
EOF
fi

exit 0
```

配置方式：

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "./hooks/run-tests.sh"
          }
        ]
      }
    ]
  }
}
```

> 注意 Stop 事件没有  matcher 字段——因为 Stop 是生命周期事件，不针对特定工具。
>

动手试一下——进入质量钩子项目，让 Claude 写一段会导致测试失败的代码，观察 Stop Hook 的自动门控行为：

```bash
# 进入质量钩子项目（已配好 .claude/settings.json）
cd 06-Hooks/projects/02-quality-hooks

# 启动 Claude Code
claude
```

进入会话后，给 Claude 一个会产生测试失败的任务：

```
帮我创建一个 Node.js 项目，写一个 add 函数和对应的测试，但故意让测试失败
```

当 Claude 写完代码准备停下来时，Stop Hook 自动触发  run-tests.sh。如果测试失败，你会看到：

```
● Stop hook returned blocking error
  Tests are failing. Please fix the issues before stopping.
  ⎿  [测试失败的详细输出...]

● Claude 继续修复代码...
```

Claude 收到失败信息后会自动修复，直到测试通过才真正停下来。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202605091528857.jpeg)

**用 Prompt 类型实现更灵活的 Stop Hook**

Shell 脚本适合检查客观事实——测试通不通过、文件存不存在。但有时候你需要检查更“主观”的东西，包括代码风格是否合理？功能实现是否完整？有没有遗漏边界情况？这些判断需要“理解力”，不是模式匹配能解决的。

这时可以用 Prompt 类型的 Stop Hook，让一个小型 LLM（通常是 Haiku）担任代码审查员：

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Review the changes made in this session. Check that: 1) All requested features are implemented 2) No obvious bugs or security issues 3) Code follows project conventions. If any issues found, respond with continue: true and explain what needs to be fixed."
          }
        ]
      }
    ]
  }
}
```

这相当于在 Claude 完成工作后，让另一个 AI 做 code review。

**防止 Stop Hook 死循环：stop_hook_active**

Stop Hook 的  continue: true 很强大，但也有风险——如果 Claude 一直修不好，就会进入死循环：测试失败 → Claude 修复 → 测试还是失败 → Claude 再修 → 还是失败……如此无限循环。

所幸官方提供了一个安全字段  stop_hook_active：当 Claude 因为 Stop Hook 而继续工作时，下一次 Stop 事件的输入中  stop_hook_active 会被设为  true。你的脚本应该检查这个字段来避免死循环：

```bash
#!/bin/bash
INPUT=$(cat)

# 检查是否已经因为 Stop Hook 继续过了
if [ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ]; then
    # 已经重试过一次了，这次让 Claude 停下来
    exit 0
fi

# 正常的测试逻辑
npm test 2>&1
if [ $? -ne 0 ]; then
    # 疑问：为什么没有 "continue": true ?
    echo '{"decision": "block", "reason": "Tests still failing, please fix."}'
else
    exit 0
fi
```

## 子代理事件——SubagentStart 与 SubagentStop

**SubagentStart：为子代理注入上下文**

SubagentStart 在子代理被启动时触发。它的 matcher 匹配的是子代理类型名，而不是工具名。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202605091530117.jpeg)

SubagentStart 接收的输入数据包含子代理的标识信息。

```json
{
  "session_id": "abc123",
  "cwd": "/project/root",
  "hook_event_name": "SubagentStart",
  "agent_id": "agent-def456",
  "agent_type": "code-reviewer"
}
```

SubagentStart 可以通过  additionalContext 向子代理注入上下文信息。

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SubagentStart",
    "additionalContext": "当前分支是 feature/payment-refactor，请特别关注支付相关的代码变更"
  }
}
```

这个能力的价值在于自动化上下文注入。比如你有一个  code-reviewer 子代理，每次启动时都需要知道团队的编码规范。如果没有 SubagentStart Hook，你得在每次调用子代理时手动提醒它“请遵循 camelCase 命名规范“。有了 Hook，这个提醒将自动发生。

```json
{
  "hooks": {
    "SubagentStart": [
      {
        "matcher": "code-reviewer",
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"hookSpecificOutput\":{\"hookEventName\":\"SubagentStart\",\"additionalContext\":\"Team coding standards: use camelCase, max line length 100, always add JSDoc for public APIs\"}}'"
          }
        ]
      }
    ]
  }
}
```

这样，每次  code-reviewer 子代理启动时，都会自动收到团队编码规范——不需要在每次调用时手动提醒，不需要把规范写到子代理的 prompt 里（那样会占用子代理的上下文空间）。

**SubagentStop：验证子代理的工作成果**

SubagentStop 在子代理完成工作后触发。SubagentStop 的输入数据有一个独特的字段，agent_transcript_path。

```json
{
  "session_id": "abc123",
  "cwd": "/project/root",
  "hook_event_name": "SubagentStop",
  "stop_hook_active": false,
  "agent_id": "agent-def456",
  "agent_type": "code-reviewer",
  // 主会话的对话记录
  "transcript_path": "~/.claude/projects/.../main-session.jsonl",
  // 子代理自己的对话记录
  "agent_transcript_path": "~/.claude/projects/.../subagents/agent-def456.jsonl"
}
```

SubagentStop 的决策控制和 Stop 事件一样，可以用  decision: "block" 阻止子代理完成，强制它继续工作。

```json
{
  "decision": "block",
  "reason": "Code review is incomplete: you found 3 issues but only provided fixes for 2. Please complete the review."
}
```

**实战：用 SubagentStop 验证代码审查质量**

下面这个脚本验证 code-reviewer 子代理的审查是否完整——如果它发现了问题但没有给出修复建议，就强制它继续工作。

这个需求背后的逻辑是：一个好的代码审查不仅要发现问题，还要提供解决方案。只说“这里有 bug，而不说建议如何修复的审查是不完整的。Hook 可以把这个“完整性要求”固化为自动检查：

```bash
#!/bin/bash
# verify-review-quality.sh
# 验证 code-reviewer 子代理的审查是否完整

INPUT=$(cat)
AGENT_TYPE=$(echo "$INPUT" | jq -r '.agent_type')
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active')
TRANSCRIPT=$(echo "$INPUT" | jq -r '.agent_transcript_path')

# 只检查 code-reviewer, 其他子代理直接放行
if [ "$AGENT_TYPE" != "code-reviewer" ]; then
    exit 0
fi

# 防止死循环
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
    exit 0
fi

# 读取子代理的输出，检查是否包含必要的审查要素
if [ -f "$TRANSCRIPT" ]; then
    HAS_ISSUES=$(grep -c "issue\|问题\|bug\|warning" "$TRANSCRIPT" || true)
    HAS_SUGGESTIONS=$(grep -c "suggest\|建议\|recommend" "$TRANSCRIPT" || true)

    if [ "$HAS_ISSUES" -gt 0 ] && [ "$HAS_SUGGESTIONS" -eq 0 ]; then
        cat <<EOF
{
    "decision": "block",
    "reason": "You found issues but didn't provide suggestions. Please add actionable suggestions for each issue."
}
EOF
        exit 0
    fi
fi

exit 0
```

配置方式如下：

```json
{
  "hooks": {
    "SubagentStop": [
      {
        "matcher": "code-reviewer",
        "hooks": [
          {
            "type": "command",
            "command": "./hooks/verify-review-quality.sh"
          }
        ]
      }
    ]
  }
}
```

当然，用关键词匹配来判断审查质量是比较粗糙的。对于更精细的质量验证，可以用 Prompt 或 Agent 类型的 Hook，让 LLM 来评估子代理的输出：

```json
{
  "hooks": {
    "SubagentStop": [
      {
        "matcher": "code-reviewer",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Evaluate this code review result: $ARGUMENTS. Check that: 1) All issues have severity levels 2) Each issue has a concrete suggestion 3) No false positives. Respond with {\"ok\": true} or {\"ok\": false, \"reason\": \"what's missing\"}."
          }
        ]
      }
    ]
  }
}
```

这让 LLM 来理解审查报告的语义，而不仅仅是匹配关键词。它能判断这个建议是否具体可操作，这是脚本无法做到的。

## 实战项目——完整的 Hook 系统

现在让我们把前面学到的知识组合起来，构建两个完整的 Hook 项目。

**项目一：安全钩子系统**

目标：保护敏感资源，防止危险操作，记录审计日志。

项目结构：

```
.claude/
├── settings.json
└── hooks/
    ├── block-dangerous.sh    # 阻止危险命令
    ├── protect-files.sh      # 保护敏感文件
    └── audit-log.sh          # 记录操作日志
```

.claude/settings.json：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {"type": "command", "command": "./hooks/block-dangerous.sh"}
        ]
      },
      {
        "matcher": "Write",
        "hooks": [
          {"type": "command", "command": "./hooks/protect-files.sh"}
        ]
      },
      {
        "matcher": "Edit",
        "hooks": [
          {"type": "command", "command": "./hooks/protect-files.sh"}
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {"type": "command", "command": "./hooks/audit-log.sh"}
        ]
      }
    ]
  }
}
```

这个配置创建了一个纵深防御体系——三道防线各司其职，形成层层递进的安全屏障。

- 第一道防线：命令拦截（PreToolUse → Bash）
- 第二道防线：文件保护（PreToolUse → Write|Edit）
- 第三道防线：审计日志（PostToolUse → *）

三道防线的强度递减（拦截 → 拦截 → 记录），但覆盖面递增（Bash → Write|Edit → 所有工具）。这就是经典的纵深防御策略——不把安全寄托在任何单一防线上。

**项目二：质量钩子系统**

目标：自动格式化代码，检查 lint 错误，确保测试通过。

项目结构：

```
.claude/
├── settings.json
└── hooks/
    ├── auto-format.sh        # 自动格式化
    ├── lint-check.sh         # Lint 检查
    └── run-tests.sh          # 运行测试
```

.claude/settings.json：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          // 两个 Hook 在同一个  hooks 数组中，它们会按顺序执行
          {"type": "command", "command": "./hooks/auto-format.sh"},
          {"type": "command", "command": "./hooks/lint-check.sh"}
        ]
      },
      {
        "matcher": "Edit",
        "hooks": [
          {"type": "command", "command": "./hooks/auto-format.sh"},
          {"type": "command", "command": "./hooks/lint-check.sh"}
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {"type": "command", "command": "./hooks/run-tests.sh"}
        ]
      }
    ]
  }
}
```

这个配置创建了一个两阶段质量保证流水线。

- 第一阶段：逐文件质量保证（PostToolUse → Write|Edit）
- 第二阶段：全局质量门控（Stop）

两个阶段的分工很明确——第一阶段是"边做边查"，保证每个文件的局部质量；第二阶段是做完再验，保证整体功能的正确性。

## 高级模式与最佳实践

<!-- 从这里开始整理 -->

前面的实战项目覆盖了最常见的使用场景。下面来看一些进阶技巧和最佳实践。

**进阶技巧一：多 Hook 链**

可以为同一事件配置多个 Hook，它们按顺序执行：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          { "type": "command", "command": "./hooks/format.sh" },
          { "type": "command", "command": "./hooks/lint.sh" },
          { "type": "command", "command": "./hooks/log.sh" }
        ]
      }
    ]
  }
}
```

如果任何一个 Hook 返回阻止决策（比如 lint.sh 返回  exit 2），后续的 Hook（log.sh）不会执行。所以你应该把“不能失败”的 Hook（如日志记录）放在最前面，或者确保它们不会互相干扰。

**进阶技巧二：环境变量**

Hooks 可以访问多个环境变量，让你的脚本更灵活。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202605091534616.jpeg)

其中 CLAUDE_ENV_FILE 是一个特别有用的变量。SessionStart Hook 可以向这个文件写入 export 语句，这些环境变量会在后续所有 Bash 命令中生效，相当于在会话开始时，就设置了全局环境。

```bash
#!/bin/bash
# session-setup.sh - SessionStart hook
if [ -n "$CLAUDE_ENV_FILE" ]; then
    echo 'export NODE_ENV=development' >> "$CLAUDE_ENV_FILE"
    echo 'export DEBUG_LOG=true' >> "$CLAUDE_ENV_FILE"
fi
exit 0
```

利用  CLAUDE_FILE_PATH 可以让 Hook 只在特定目录下生效——比如只对  src/ 目录下的文件运行 Lint。

```bash
#!/bin/bash
# 只在 src/ 目录执行 lint
if [[ "$CLAUDE_FILE_PATH" == */src/* ]]; then
    npm run lint "$CLAUDE_FILE_PATH"
fi
```

这种条件过滤让 Hook 更精准，你不需要对配置文件、文档、测试文件都跑同样的检查。

**进阶技巧三：在 Commands 和 Skills 中定义临时 Hooks**

前一讲我们学过，Commands 和 Skills 可以在 frontmatter 中包含临时 Hooks（仅在该命令 / 技能执行期间有效）。

```markdown
---
description: Deploy with safety checks
hooks:
  - event: PreToolUse
    matcher: Bash
    command: |
      if [[ "$TOOL_INPUT" == *"production"* ]]; then
        echo "Production deployment detected" >&2
      fi
  - event: PostToolUse
    matcher: Edit
    command: npx prettier --write "$FILE_PATH"

    once: true  # 表示 Hook 只触发一次
---

Deploy the application to staging environment.
```

这适合“完成后运行一次测试”这类不需要重复执行的场景。注意  once 仅在 Skill 中可用，子代理中不支持。

**进阶技巧四：子代理 frontmatter 内置 Hooks——比全局配置更精准的方案**

在第 3 讲中，我们学习了子代理的 frontmatter 可以定义各种配置字段。现在来看其中最强大的一个——hooks 字段。

考虑这个场景：你有一个  db-reader 子代理，它可以执行 SQL 查询。你想在它每次执行 Bash 命令前检查 SQL 注入风险。

- 方案一：全局 settings.json

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {"type": "command", "command": "./hooks/check-sql-injection.sh"}
        ]
      }
    ]
  }
}
```

问题来了：所有 Bash 命令都会被 SQL 注入检查——包括  npm install、git status、ls -la 这些和 SQL 毫无关系的命令。这既浪费性能（每次 Bash 命令多执行一个脚本），又可能误拦截（脚本中某个字符串碰巧匹配了 SQL 注入模式）。

- 方案二：子代理 frontmatter Hooks

```markdown
---
name: db-reader
description: Read-only database explorer for analyzing data patterns
tools: Read, Grep, Glob, Bash
permissionMode: plan
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./hooks/check-sql-injection.sh"
  Stop:
    - hooks:
        - type: prompt
          prompt: "Check if any query results contain PII (names, emails, phone numbers). If so, respond with {\"ok\": false, \"reason\": \"Results may contain PII, please redact before returning\"}."
---

You are a database analysis specialist. Execute read-only SQL queries to help understand data patterns.

## Rules
- ONLY execute SELECT queries
- NEVER use INSERT, UPDATE, DELETE, DROP, or any data-modifying SQL
- Limit results to 100 rows unless explicitly requested
```

这样做，SQL 注入检查只在  db-reader 子代理的 Bash 命令上触发。主会话和其他子代理的 Bash 命令完全不受影响。

结合下表，两种方案的差异一目了然。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202605091535402.jpeg)

frontmatter Hooks 的关键规则：

1. 支持所有事件类型：PreToolUse、PostToolUse、Stop 等都可以用。
2. Stop 会自动转换为 SubagentStop：在子代理 frontmatter 中定义的  Stop Hook，实际触发的是  SubagentStop 事件——因为子代理完成时触发的是 SubagentStop 而非 Stop。
3. 生命周期绑定：Hook 在子代理启动时激活，子代理完成时自动清理。
4. 格式与 settings.json 一致：YAML 格式，但字段名和结构完全相同。

为了让你加深理解，我们来看一个更复杂的例子，这是一个带安全检查的部署子代理。

```bash
---
name: deploy-checker
description: Verify deployment readiness with safety checks
tools: Read, Grep, Glob, Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: |
            INPUT=$(cat)
            CMD=$(echo "$INPUT" | jq -r '.tool_input.command // ""')
            # 阻止任何直接操作生产环境的命令
            if echo "$CMD" | grep -qi "production\|prod-db\|deploy.*--force"; then
              echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Direct production operations are not allowed in this agent. Use the deployment pipeline instead."}}'
            fi
  Stop:
    - hooks:
        - type: agent
          prompt: "Review the deployment check results. Verify that: 1) All health checks pass 2) No breaking API changes detected 3) Database migrations are backward-compatible. $ARGUMENTS"
          timeout: 60
---

You are a deployment readiness checker...
```

这个子代理有两层保护。PreToolUse Hook 用确定性规则阻止直接操作生产环境的命令，这是“硬规则”，不需要判断力，只需要模式匹配。Stop Hook（实际触发为 SubagentStop）用 Agent 类型验证部署检查结果——这需要判断力和代码检查能力，所以用了最强的 Agent 类型。

**什么时候用 frontmatter Hooks vs 全局 Hooks？**

判断流程很简单：

```
判断流程：
├── 这个 Hook 是否只与特定子代理相关？
│   ├── 是 → frontmatter Hooks
│   │   例：db-reader 的 SQL 注入检查、deploy-checker 的生产环境保护
│   └── 否 → 全局 settings.json
│       例：所有 Write 操作后的格式化、所有 Bash 命令的危险命令拦截
│
├── 这个 Hook 是否需要随子代理定义一起分发？
│   ├── 是 → frontmatter Hooks
│   │   例：开源项目中的子代理，使用者不需要额外配置 settings.json
│   └── 否 → 全局 settings.json
│
└── 这个 Hook 是否需要在子代理外也生效？
    ├── 是 → 全局 settings.json
    └── 否 → frontmatter Hooks
```

**调试技巧**

Hook 脚本出问题时，调试手段和普通 Shell 脚本有所不同，因为 Hook 的 stdin/stdout 都有特殊用途。我来为你分享四个最实用的调试技巧。

1. 使用 stderr 输出调试信息

```bash
# 调试信息输出到 stderr（不影响 JSON 响应）
echo "DEBUG: Processing file $FILE_PATH" >&2

# 正常输出到 stdout
echo '{"decision": "allow"}'
```

记住，stdout 是给 Claude 读的 JSON，stderr 是给你看的调试信息。混淆两者是 Hook 开发中最常见的错误。

2. 手动测试 Hook 脚本

不需要启动 Claude 就能测试你的 Hook——手动构造 JSON 输入，通过管道传给脚本：

```bash
# 创建测试输入
echo '{
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf /tmp/test"
  }
}' | ./hooks/block-dangerous.sh

# 检查退出码
echo "Exit code: $?"
```

这让你能在开发过程中快速迭代——修改脚本、手动测试、检查输出，不需要每次都等 Claude 触发。 

3. 使用claude --debug查看完整执行细节

```
[DEBUG] Executing hooks for PostToolUse:Write
[DEBUG] Found 1 hook matchers in settings
[DEBUG] Matched 1 hooks for query "Write"
[DEBUG] Hook command completed with status 0: <stdout output>
```

也可以在会话中用  Ctrl+O 切换详细模式（verbose mode），在对话记录中查看 Hook 的输出。

4. 常见问题排查清单

- Hook 不触发：检查 matcher 是否正确（区分大小写）；如果直接编辑了 settings 文件，需要在  /hooks 菜单中确认或重启会话才能生效。
- 权限问题：确保脚本有执行权限——chmod +x hooks/*.sh
- JSON 解析错误：确保输出是有效 JSON。注意：如果你的 shell profile。（~/.zshrc 或  ~/.bashrc）中有无条件的  echo 语句，它会污染 stdout 导致 。JSON 解析失败。解决方法是用  [[ $- == *i* ]] 包裹 echo，只在交互式 shell 中输出。
- Stop Hook 死循环：检查是否遗漏了  stop_hook_active 判断（参见前面的"防止死循环"一节）。

**异步 Hook：后台执行不阻塞**

默认情况下，Hook 会阻塞 Claude 的执行直到完成。这在大多数场景下是合理的——安全检查必须在操作前完成，格式化必须在下一步操作前完成。但对于耗时操作（运行完整测试套件、发送通知、调用外部 API），阻塞会显著拖慢 Claude 的响应速度。

async: true 让 Hook 在后台运行，不阻塞主流程：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "./hooks/run-tests-async.sh",
            "async": true,
            "timeout": 300
          }
        ]
      }
    ]
  }
}
```

你需要知道异步 Hook 的三个限制。

1. 只有  type: "command" 支持异步，prompt 和 agent 类型不支持——因为它们需要实时影响 Claude 的决策。
2. 异步 Hook 不能阻止操作，因为操作在 Hook 完成前就已经继续了
3. Hook 完成后的输出会在下一个对话轮次传递给 Claude，这是有延迟的。

所以异步 Hook 适合“我不需要立即知道结果”的场景，在后台跑测试、发送 Slack 通知、写日志到远程服务。

**HTTP Hook：对接外部服务**

前面讲的 command、prompt、agent 三种 Hook 类型，执行逻辑都在本地——要么跑脚本，要么调 LLM。但有些场景下，Hook 的处理逻辑不在本地，而是在一个远程服务上：团队共享的审计服务、集中式的安全扫描平台、公司内部的合规检查 API。

这时候就该用  type: "http"。HTTP Hook 把事件数据以 POST 请求发送到指定 URL，由远程服务处理后返回决策结果。

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "http",
            "url": "http://localhost:8080/hooks/tool-use",
            "headers": {
              "Authorization": "Bearer $MY_TOKEN"
            },
            "allowedEnvVars": ["MY_TOKEN"]
          }
        ]
      }
    ]
  }
}
```

远程服务收到的 JSON 和 command Hook 从 stdin 读到的完全一样。返回的响应体也遵循相同的 JSON 格式——要阻止工具调用，在响应体里返回对应的  hookSpecificOutput 字段即可。注意：HTTP 状态码（如 403）不能阻止操作，必须在 2xx 响应体里用 JSON 表达决策。 headers 中的值支持  $VAR_NAME 语法做环境变量插值，但只有  allowedEnvVars 列表中的变量才会被解析，其他  $VAR 引用会保持为空。这是一个安全设计——防止意外泄露环境变量。

HTTP Hook 有一个限制，目前只能通过手动编辑 settings JSON 来配置，/hooks 交互菜单暂不支持添加 HTTP 类型。

四种 Hook 类型各有所长，我为你梳理了表格。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202605091539452.jpeg)

选择原则不变：能用 command 解决的不要用 prompt，能用 prompt 解决的不要用 agent，需要对接远程服务时用 http。

**安全最佳实践**

最后，我们来梳理几条在生产环境中久经验证的安全建议。

1. 使用绝对路径引用脚本：用  "$CLAUDE_PROJECT_DIR"/.claude/hooks/xxx.sh，比相对路径更可靠。相对路径在子代理中可能解析到错误的目录。
2. 最小权限原则：PreToolUse 只检查必要的条件。检查越多，误拦截的概率越高，用户绕过 Hook 的冲动也越强。
3. 快速失败：Hook 应该快速返回，避免长时间阻塞。如果确实需要耗时操作，用  async: true。
4. 优雅降级：格式化工具不存在时应跳过而不是报错。Hook 的失败不应该阻碍正常工作流。
5. 输入校验：永远不要盲目信任 stdin 输入，用  jq 解析并验证。
6. 引号包裹变量：使用  "$VAR" 而非  $VAR，防止路径中的空格导致问题。
7. 路径遍历防护：检查文件路径中是否有  ..，防止恶意路径逃逸。

**Hook 工程设计方法论**

前面教的是“Hooks 能做什么、怎么配置”。

下面来回答一个更重要的工程问题：面对一个具体需求，如何系统地设计 Hook 方案？

**三维决策框架**

设计一个 Hook 方案，我们需要想清楚三个问题。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202605091540139.jpeg)

三个维度两两正交——你可以在任何事件上使用任何类型的 Hook，配置在任何位置。但能做不等于应该做。好的工程设计是在这三个维度上找到最恰当的交叉点——用最轻量的类型解决问题，在最小的作用域内生效。

**Hook + SubAgent 组合模式**

Hooks 和 SubAgent 是两个独立的机制，但组合使用时能产生强大的协同效果。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202605091540352.jpeg)

来看一个完整的组合案例，这是一个带质量门控的代码审查子代理。

```
子代理定义（.claude/agents/code-reviewer.md）
├── frontmatter
│   ├── tools: Read, Grep, Glob
│   ├── permissionMode: plan
│   └── hooks:
│       └── Stop: prompt hook 检查审查是否完整
│
全局 settings.json
├── SubagentStart hook（matcher: code-reviewer）
│   └── 注入当前分支的变更列表
└── SubagentStop hook（matcher: code-reviewer）
    └── 验证审查报告格式和质量
```

这三层保护各司其职：

1. frontmatter Hook：子代理内部的自检，检测我的输出完整是否完整。
2. SubagentStart Hook：外部注入，给它必要的上下文。
3. SubagentStop Hook：外部验收，判断它的工作是否达标。

内部自检发现的是“自己知道自己漏了什么”的问题，外部验收发现的是“它觉得完成了，但其实不够好”的问题。两者视角不同，互为补充。

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202605091541811.jpeg)



# ==18｜庖丁解牛：Tools 工具系统内核剖析==









