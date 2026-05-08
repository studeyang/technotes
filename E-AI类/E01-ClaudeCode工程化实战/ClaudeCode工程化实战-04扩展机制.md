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
| PreToolUse         | 工具执行前                    | 能         | 权限检查、参数修改、危险操作拦截     |
| PermissionRequest  | 权限对话框弹出时              | 能         | 自动批准或拒绝权限请求               |
| PostToolUse        | 工具执行成功后                |            | 格式化、验证、日志记录               |
| PostToolUseFailure | 工具执行失败后                |            | 错误日志、告警、纠正性反馈           |
| Notification       | Claude 发送通知时             |            | 自定义通知方式（桌面提醒等）         |
| SubagentStart      | 子代理启动时                  |            | 为子代理注入上下文                   |
| SubagentStop       | 子代理完成时                  | 能         | 验证子任务结果、强制子代理继续       |
| Stop               | Claude 完成响应时             | 能         | 质量检查、自动测试                   |
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

# ==18｜庖丁解牛：Tools 工具系统内核剖析==









