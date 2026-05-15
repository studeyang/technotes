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

> - 操作前拦截   → UserPromptSubmit / PreToolUse
> - 操作后反馈   → PostToolUse / PostToolUseFailure
> - 完成时检查   → SubagentStop / Stop
> - 生命周期管理 → SessionStart / PreCompact / SessionEnd

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
      {  // 第一组规则
        "matcher": "Bash",         //← 第三层：匹配器（针对哪个工具）
        "hooks": [                 //← 第四层：Hook 列表（执行什么）
          {
            "type": "command",  // 执行类型(有4种)
            "command": "./hooks/block-dangerous.sh"
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

它不在本地执行逻辑，而是把事件数据以 POST 请求发送到远程 HTTP 端点，由远程服务返回决策结果。适合团队共享审计服务、集中式安全扫描等场景。

```json
{
    "type": "http",
    "url": "http://localhost:8080/hooks/tool-use",
    "headers": {
        "Authorization": "Bearer $MY_TOKEN"
    },
    "allowedEnvVars": ["MY_TOKEN"]
}
```

> 注意：
>
> - 远程服务收到的 JSON 和 command Hook 从 stdin 读到的完全一样。返回的响应体也遵循相同的 JSON 格式——要阻止工具调用，在响应体里返回对应的 hookSpecificOutput 字段即可。
> - HTTP 状态码（如 403）不能阻止操作，必须在 2xx 响应体里用 JSON 表达决策。
> - headers 中的值支持 $VAR_NAME 语法做环境变量插值，但只有 allowedEnvVars 列表中的变量才会被解析，其他  $VAR 引用会保持为空。这是一个安全设计——防止意外泄露环境变量。
> - HTTP Hook 有一个限制，目前只能通过手动编辑 settings JSON 来配置。

四种 Hook 类型各有所长（如下表所示）。选择原则：能用 command 解决的不要用 prompt，能用 prompt 解决的不要用 agent，需要对接远程服务时用 http。

| 类型      | 执行方式        | 最佳场景        | 延迟    |
| ------- | ----------- | ----------- | ----- |
| command | 本地 Shell 脚本 | 确定性规则检查     | 最低    |
| prompt  | 单次 LLM 调用   | 需要判断力的决策    | 低     |
| agent   | 多轮子代理验证     | 需要查代码才能决策   | 较高    |
| http    | POST 到远程服务  | 团队共享服务、集中审计 | 取决于网络 |
## PreToolUse：工具执行前的守门员

Hook 脚本通过 stdin 接收一个 JSON 对象：

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

Hook 脚本通过退出码和 stdout JSON 告诉 Claude 下一步做什么。

退出码 exit 0 表示放行，exit 2 表示阻止，其他非零退出码表示脚本出错但不阻止。需要更精细的控制时，通过 stdout 输出 JSON 决策。官方推荐的  hookSpecificOutput 格式支持四种响应方式。

第一种：允许执行（检查通过，放行）

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow"
  }
}
```

第二种：拒绝执行（发现危险操作，直接拦截。permissionDecisionReason 会反馈给 Claude）

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "This command is not allowed"
  }
}
```

第三种：交给用户确认（操作不是明确的“安全”或“危险”，而是“需要人类判断”）

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "This command modifies production data"
  }
}
```

第四种：修改输入后执行（不拦截操作，而是改写参数后放行）

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

比如用户要执行 `rm -rf /tmp/test`，你可以把它改成 `rm -rf /tmp/test --dry-run`，先看看会删什么再说。

**PreToolUse 实战案例 1：阻止危险命令**

每个工程团队都有一些“绝对不能执行”的命令，一旦执行就无法挽回。`rm -rf /` 会删除整个文件系统，`git push --force origin main` 会覆盖远程主分支的历史，`DROP DATABASE` 会销毁整个数据库。

> 人在清醒状态下当然不会执行它们，但 Claude 作为 AI 有时会过于“积极”——如果用户说”清理一下项目”，Claude 可能会把 `rm -rf` 理解得过于字面。

下面这个脚本用模式匹配来拦截这些灾难性命令：（脚本位于 hooks/block-dangerous.sh）

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
          { "type": "command", "command": "./hooks/block-dangerous.sh" }
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
          { "type": "command", "command": "./hooks/protect-files.sh" }
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
          { "type": "command", "command": "./hooks/audit-log.sh" }
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
          { "type": "command", "command": "./hooks/run-tests.sh" }
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

| Matcher 值 | 匹配的子代理                                                 |
| ---------- | ------------------------------------------------------------ |
| Bash       | 内置 Bash 子代理                                             |
| Explore    | 内置 Explore 子代理                                          |
| Plan       | 内置 Plan 子代理                                             |
| 自定义名称 | 你在 `.claude/agents/` 中定义的子代理，如 code-reviewer、bug-locator |

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
          { "type": "command", "command": "./hooks/verify-review-quality.sh" }
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

| 变量                 | 描述                          | 所有 Hook 可用？    |
| -------------------- | ----------------------------- | ------------------- |
| CLAUDE_PROJECT_DIR   | 项目根目录                    | 是                  |
| CLAUDE_SESSION_ID    | 当前会话 ID                   | 是                  |
| CLAUDE_TOOL_NAME     | 当前工具名称                  | 是                  |
| **CLAUDE_FILE_PATH** | 操作的文件路径（如适用）      | 是                  |
| CLAUDE_NOTIFICATION  | 通知内容（Notification 事件） | 仅 Notification     |
| **CLAUDE_ENV_FILE**  | 环境变量持久化文件路径        | **仅 SessionStart** |
| CLAUDE_CODE_REMOTE   | 是否在远程 Web 环境中运行     | 是                  |
| CLAUDE_PLUGIN_ROOT   | 插件根目录                    | 仅 Plugin hooks     |

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

考虑这个场景：你有一个 db-reader 子代理，它可以执行 SQL 查询。你想在它每次执行 Bash 命令前检查 SQL 注入风险。

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

| 对比维度 | 全局 settings.json       | 子代理 frontmatter            |
| -------- | ------------------------ | ----------------------------- |
| 作用域   | 所有 Bash 命令都检查     | 仅 db-reader 的 Bash 命令检查 |
| 生命周期 | 永远生效                 | 仅子代理活跃期间              |
| 精准度   | 可能误拦截其他 Bash 命令 | 只在特定子代理的上下文中执行  |

frontmatter Hooks 的关键规则：

1. 支持所有事件类型：PreToolUse、PostToolUse、Stop 等都可以用。
2. Stop 会自动转换为 SubagentStop：在子代理 frontmatter 中定义的 Stop Hook，实际触发的是 SubagentStop 事件——因为子代理完成时触发的是 SubagentStop 而非 Stop。
3. 生命周期绑定：Hook 在子代理启动时激活，子代理完成时自动清理。
4. 格式与 settings.json 一致：YAML 格式，字段名和结构完全相同。

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

**调试技巧**

Hook 脚本出问题时，调试手段和普通 Shell 脚本有所不同，因为 Hook 的 stdin/stdout 都有特殊用途。我来为你分享四个最实用的调试技巧。

1. 使用 stderr 输出调试信息

```bash
# 调试信息输出到 stderr（不影响 JSON 响应）
echo "DEBUG: Processing file $FILE_PATH" > &2

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
- JSON 解析错误：确保输出是有效 JSON。注意：如果你的 shell profile（~/.zshrc 或  ~/.bashrc）中有无条件的  echo 语句，它会污染 stdout 导致 JSON 解析失败。
- Stop Hook 死循环：检查是否遗漏了 stop_hook_active 判断（参见前面的"防止死循环"一节）。

**异步 Hook：后台执行不阻塞**

默认情况下，Hook 会阻塞 Claude 的执行直到完成。对于耗时操作（运行完整测试套件、发送通知、调用外部 API），阻塞会显著拖慢 Claude 的响应速度。

async: true 让 Hook 在后台运行，不阻塞主流程：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {"type": "command", "command": "./hooks/run-tests-async.sh", "async": true, "timeout": 300}
        ]
      }
    ]
  }
}
```

你需要知道异步 Hook 的三个限制。

1. 只有  type: "command" 支持异步，prompt 和 agent 类型不支持——因为它们需要实时影响 Claude 的决策。
2. 异步 Hook 不能被阻止。
3. Hook 完成后的输出会在下一个对话轮次传递给 Claude，这是有延迟的。

所以异步 Hook 适合“我不需要立即知道结果”的场景，在后台跑测试、发送 Slack 通知、写日志到远程服务。

**安全最佳实践**

最后，我们来梳理几条在生产环境中久经验证的安全建议。

1. 使用绝对路径引用脚本：用  "$CLAUDE_PROJECT_DIR"/.claude/hooks/xxx.sh 比相对路径更可靠（相对路径在子代理中可能解析到错误的目录）
2. 最小权限原则：PreToolUse 只检查必要的条件（检查越多，误拦截的概率越高，用户绕过 Hook 的冲动也越强）
3. 快速失败：Hook 应该快速返回，避免长时间阻塞（如果确实需要耗时操作，用  async: true）
5. 输入校验：永远不要盲目信任 stdin 输入，用  jq 解析并验证。
6. 引号包裹变量：使用 "$VAR" 而非 $VAR（防止路径中的空格导致问题）
7. 路径遍历防护：检查文件路径中是否有 ..（防止恶意路径逃逸）

## Hook 工程设计方法论

前面教的是“Hooks 能做什么、怎么配置”。下面来回答一个更重要的工程问题：面对一个具体需求，如何系统地设计 Hook 方案？

**三维决策框架**

设计一个 Hook 方案，我们需要想清楚三个问题。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202605091540139.jpeg)

好的工程设计是在这三个维度上找到最恰当的交叉点——用最轻量的类型解决问题，在最小的作用域内生效。

**Hook + SubAgent 组合模式**

Hooks 和 SubAgent 是两个独立的机制，但组合使用时能产生强大的协同效果。

| 组合模式                 | 说明                                         | 示例                                             |
| ------------------------ | -------------------------------------------- | ------------------------------------------------ |
| SubagentStart 注入上下文 | 子代理启动时自动注入领域知识                 | code-reviewer 启动时注入团队编码规范             |
| SubagentStop 质量门控    | 子代理完成时自动验证输出质量                 | 检查代码审查报告是否包含所有必要字段             |
| frontmatter 内置 Hook    | 子代理自带安全检查                           | db-reader 自带 SQL 注入检测                      |
| Stop + 子代理结果验证    | 主对话 Stop Hook 用 agent 类型验证子代理输出 | 用一个 agent Hook 检查所有子代理修改是否通过测试 |

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

1. frontmatter Hook：子代理内部的自检，检测我的输出是否完整。
2. SubagentStart Hook：外部注入，给它必要的上下文。
3. SubagentStop Hook：外部验收，判断它的工作是否达标。

内部自检发现的是“自己知道自己漏了什么”的问题，外部验收发现的是“它觉得完成了，但其实不够好”的问题。两者视角不同，互为补充。

# 17｜海纳百川：MCP 协议与外部工具连接

2024 年 11 月，Anthropic 推出了一项开源协议——Model Context Protocol (MCP)，AI 时代的 USB-C 接口。

## MCP——AI 的 USB-C 接口

在 MCP 出现之前，如果你想让 AI 助手连接外部服务，通常有两种选择：

1. 自定义开发：为每个服务写专门的集成代码
2. 平台绑定：依赖特定平台提供的插件（如 ChatGPT Plugins）

这带来了严重的碎片化问题。假设市场上有 M 个 AI 助手和 N 个外部服务，那么理论上需要 M × N 个专用适配器。每一对组合都需要单独开发、单独维护、单独调试：

![img](https://static001.geekbang.org/resource/image/1a/b2/1a71310130f2fa3359ef325cfaed2cb2.jpg?wh=3000x1443)

MCP （ [Anthropic 官方博客](https://www.anthropic.com/news/model-context-protocol)）的出现改变了这一切。一个协议，通用连接。每个 AI 助手只需要实现一次 MCP Client，每个服务只需要实现一次 MCP Server，然后任意组合即可工作。

> 有了 MCP，M × N 的问题变成了 M + N。

![img](https://static001.geekbang.org/resource/image/66/67/66e77ba71666a2cf1d5021e3b9a85167.jpg?wh=10473x5963)

**MCP 架构与核心概念**

MCP 采用经典的客户端 - 服务器架构。Claude Code 充当 MCP Client，负责发现和调用工具；MCP Server 则暴露工具和资源，作为外部服务的代理。两者之间通过 JSON-RPC 2.0 协议通信。

![img](https://static001.geekbang.org/resource/image/0b/88/0bd8713656afef7c538ebf568ff03b88.jpg?wh=3094x1414)

这个架构的关键组件如下表所示。

| 组件       | 角色     | 说明                                   |
| ---------- | -------- | -------------------------------------- |
| MCP Client | 请求方   | 内置于 Claude Code，负责发现和调用工具 |
| MCP Server | 提供方   | 暴露工具和资源的服务程序               |
| 传输层     | 通信管道 | stdio、SSE、HTTP 三种方式              |

> MCP 复用了  [Language Server Protocol (LSP)](https://en.wikipedia.org/wiki/Language_Server_Protocol) 的消息流思想。VS Code 编辑器的智能提示、跳转定义等功能，都是通过 LSP 与语言服务器通信实现的。MCP 做了同样的事情，只不过它服务的不是代码编辑器，而是 AI Agent。

MCP Server 并不只是简单地“暴露一个函数”。它可以向 Client 提供三种不同类型的能力。

| 能力      | 描述             | 示例                             |
| --------- | ---------------- | -------------------------------- |
| Tools     | 可调用的函数     | 查询数据库、创建 Issue、发送消息 |
| Resources | 可读取的数据     | 文件内容、API 响应、配置信息     |
| Prompts   | 预定义的提示模板 | 代码审查模板、文档生成模板       |

- Tools 是最常用的能力类型——它让 Claude 能够“做事情“。
- Resources 提供只读数据，让 Claude 能够“看到东西”而不仅仅依赖你粘贴的文本。
- Prompts 则是一种便捷机制，让服务器预定义好特定场景的交互模板。

> Claude Code 会在启动时自动发现所有配置的 MCP Server 及其提供的能力。当你说“帮我查一下数据库里的用户数量”时，Claude 会自动找到数据库 MCP Server，调用对应的查询工具，解析结果并返回给你。整个过程对用户完全透明。

**MCP 的三种传输方式**

MCP 支持三种传输方式，适用于不同场景。

Stdio 传输（本地进程）是最简单的方式。MCP Server 作为本地子进程启动，通过标准输入（stdin）接收请求，通过标准输出（stdout）返回响应。适合本地工具和开发测试：

```json
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/home/user/projects"]
    }
  }
}
```

第二种方式是 HTTP 传输。当 MCP Server 运行在远程服务器上时推荐使用。通过标准 HTTP 请求 / 响应通信，支持 TLS 加密和 Bearer Token 认证。GitHub、Notion、Sentry 等云服务通常直接提供 HTTP 类型的 MCP 端点：

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_TOKEN}"
      }
    }
  }
}
```

第三种是 SSE 传输（Server-Sent Events）——基于 HTTP 的单向推送技术，建立持久连接，服务器可以主动向客户端推送数据。适合实时监控和流式数据场景。在实践中使用较少，大多数场景用 stdio 或 HTTP 就够了。

这几种方式怎么选呢？原则是，本地用 stdio，远程用 HTTP，实时用 SSE。如果你拿不定主意，先试 stdio（本地服务器）或 HTTP（远程服务），这两个覆盖了 95% 的场景。

| 传输类型 | 延迟     | 适用场景           | 安全性     |
| -------- | -------- | ------------------ | ---------- |
| stdio    | 最低     | 本地工具、开发测试 | 本地隔离   |
| http     | 中等     | 云服务、远程 API   | TLS 加密   |
| sse      | 持久连接 | 实时数据、监控     | TLS + 认证 |

**MCP 的配置与管理**

MCP 配置有三个 scope，对应三个不同的物理落点。

| 位置             | 实际落点                                             | 入 git? | 用途                               |
| ---------------- | ---------------------------------------------------- | ------- | ---------------------------------- |
| 用户级 (user)    | `~/.claude.json` 顶级 `mcpServers`                   | ❌个人   | 所有项目共享的常用 MCP             |
| 项目级 (project) | `<项目根>/.mcp.json`                                 | ✅ 团队  | 项目共享、团队入 git 的 MCP        |
| 项目本地 (local) | `~/.claude.json` 中 `projects.<项目路径>.mcpServers` | ❌ 个人  | 当前项目私有的 MCP（含个人 token） |

- 个人常用服务，如果是跨项目的，放到 ~/.claude.json 顶级的 mcpServers（user scope）。
- 团队共享的服务配置放到 <项目根>/.mcp.json——提交到 git，团队成员共享。
- 敏感凭证 / 项目私有 MCP 落在 ~/.claude.json 的 projects.<项目路径>.mcpServers（local scope），不入 git。（但不要手写这一段，使用 claude mcp add 命令默认写到这里）

不论使用哪种传输方式，MCP 配置都遵循同一个 JSON 结构。mcpServers 是顶层键，每个子键是服务器名称（可自由命名）。type 指定传输方式，剩余字段根据传输类型而定。

```json
{
  "mcpServers": {
    "server-name": {
      "type": "stdio | sse | http",
      "command": "...",        // stdio 专用
      "args": ["..."],         // stdio 专用
      "url": "...",            // sse/http 专用
      "headers": {},           // sse/http 专用
      "env": {}                // 环境变量
    }
  }
}
```

> 07-MCP/projects/01-basic-config/.mcp.json.example 示例
>
> ```json
> {
>   "$schema": "https://json-schema.org/draft/2020-12/schema",
>   "$comment": "MCP 配置示例 - 与第17讲文章对应的完整开发者工具箱",
> 
>   "mcpServers": {
> 
>     "context7": {
>       "$comment": "实时技术文档 - 写代码时拉取最新官方文档，无需 API Key",
>       "type": "stdio",
>       "command": "npx",
>       "args": ["-y", "@upstash/context7-mcp@latest"]
>     },
> 
>     "github": {
>       "$comment": "GitHub 集成 - HTTP 传输，需要 GITHUB_TOKEN",
>       "type": "http",
>       "url": "https://api.githubcopilot.com/mcp/",
>       "headers": {
>         "Authorization": "Bearer ${GITHUB_TOKEN}"
>       }
>     },
> 
>     "notion": {
>       "$comment": "Notion 集成 - 需要 NOTION_API_KEY",
>       "type": "http",
>       "url": "https://mcp.notion.com/mcp",
>       "headers": {
>         "Authorization": "Bearer ${NOTION_API_KEY}"
>       }
>     },
> 
>     "database": {
>       "$comment": "数据库查询 - 支持 PostgreSQL/MySQL/SQLite，需要 DATABASE_URL",
>       "type": "stdio",
>       "command": "npx",
>       "args": ["-y", "@bytebase/dbhub", "--dsn", "${DATABASE_URL}"]
>     },
> 
>     "fetch": {
>       "$comment": "HTTP 请求能力 - 无需 API Key",
>       "type": "stdio",
>       "command": "uvx",
>       "args": ["mcp-server-fetch"]
>     },
> 
>     "filesystem": {
>       "$comment": "文件系统访问 - 限制在指定目录内",
>       "type": "stdio",
>       "command": "npx",
>       "args": [
>         "@modelcontextprotocol/server-filesystem",
>         "/path/to/allowed/directory"
>       ]
>     },
> 
>     "memory": {
>       "$comment": "持久化记忆存储 - 无需 API Key",
>       "type": "stdio",
>       "command": "npx",
>       "args": ["@modelcontextprotocol/server-memory"]
>     }
>   }
> }
> ```

在配置文件中硬编码敏感信息是危险的。MCP 配置支持通过 ${} 语法引用环境变量：${VAR_NAME} 直接引用，变量不存在会报错；${VAR_NAME:-default} 在变量不存在时使用默认值：

```json
{
  "mcpServers": {
    "secure-api": {
      "type": "http",
      "url": "https://api.example.com/mcp",
      "headers": {
        "Authorization": "Bearer ${API_TOKEN}",
        "X-API-Key": "${API_KEY:-default-key}"
      }
    }
  }
}
```

Claude Code 提供了命令行工具来管理 MCP 服务器，这比手动编辑 JSON 更方便。

```bash
# 添加 HTTP 服务器
claude mcp add --transport http github https://api.githubcopilot.com/mcp/

# 添加 stdio 服务器
claude mcp add filesystem -- npx @modelcontextprotocol/server-filesystem /path

# 添加到用户级别（所有项目可用）
claude mcp add --transport http --scope user github https://api.githubcopilot.com/mcp/

# 带认证头添加
claude mcp add --transport http --header "Authorization: Bearer ${TOKEN}" api https://api.example.com/mcp

# 列出所有服务器
claude mcp list

# 查看服务器详情
claude mcp get github

# 移除服务器
claude mcp remove github
```

## 实战：连接主流 MCP 服务

Anthropic 维护了一套[官方 MCP 服务器集合](https://github.com/modelcontextprotocol/servers)，覆盖最常见的开发需求。这些服务器经过官方测试和维护，是入门 MCP 的最佳起点。

| 服务器            | 用途            | 安装命令                                      |
| ----------------- | --------------- | --------------------------------------------- |
| server-filesystem | 文件系统访问    | `npx @modelcontextprotocol/server-filesystem` |
| server-fetch      | HTTP 请求       | `npx @modelcontextprotocol/server-fetch`      |
| server-memory     | 持久化记忆      | `npx @modelcontextprotocol/server-memory`     |
| server-postgres   | PostgreSQL 查询 | `npx @modelcontextprotocol/server-postgres`   |
| server-git        | Git 操作        | `npx @modelcontextprotocol/server-git`        |

社区也贡献了大量高质量的第三方 MCP 服务器。以下是开发者最常用、真正能跑的几个。

| 服务器                                                       | 用途                 | 连接方式 | 说明                                   |
| ------------------------------------------------------------ | -------------------- | -------- | -------------------------------------- |
| [GitHub MCP](https://github.com/github/github-mcp-server)    | 仓库/Issue/PR 管理   | HTTP     | GitHub 官方维护，功能最全              |
| [Context7](https://github.com/upstash/context7)              | 实时获取最新技术文档 | stdio    | 写代码时自动拉取库的最新文档，极受欢迎 |
| [Notion MCP](https://developers.notion.com/guides/mcp/overview) | Notion 页面读写      | HTTP     | Notion 官方开源维护                    |
| Brave Search                                                 | AI 搜索              | stdio    | 免费搜索 API，适合信息检索             |
| [Sentry MCP](https://docs.sentry.io/ai/mcp/)                 | 错误追踪与诊断       | HTTP     | 直接从终端查看和分析报错               |

我们来介绍几个最典型的配置。

**实战 1：Context7——实时技术文档**

Context7 是开发者社区最火的 MCP 服务器之一。它的价值在于，当你让 Claude 帮你写代码时，Claude 可以实时拉取你用的库的最新文档，而不是依赖训练数据中可能过时的知识。

配置极其简单，一行命令搞定。

```
claude mcp add context7 -- npx -y @upstash/context7-mcp@latest
```

或者在  .mcp.json 中手动配置：

```json
{
  "mcpServers": {
    "context7": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  }
}
```

配置完成后，你可以在提示中加上  use context7 关键词，Claude 就会自动去拉取最新的官方文档：

```
帮我用 Next.js 15 的 App Router 写一个带认证的 API 路由 use context7
```

Claude 会输出：

```
先查一下 Next.js 15 的最新文档...
[调用 context7 MCP server → resolve_library_id → get_library_docs]
根据最新文档，Next.js 15 的 App Router API 路由写法如下...
```

不需要 API Key，不需要付费，开箱即用。这就是为什么它成了开发者的“标配”MCP。

**实战 2：GitHub MCP——仓库操作**

GitHub 官方推出的 MCP 服务器，支持完整的仓库管理操作：创建 Issue、管理 PR、搜索代码、查看 CI/CD 状态。

方式一：HTTP 远程连接（推荐，GitHub 官方托管）

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_TOKEN}"
      }
    }
  }
}
```

方式二：stdio 本地运行（更灵活，可定制参数）

```
claude mcp add github -- docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=${GITHUB_TOKEN} \
  ghcr.io/github/github-mcp-server
```

配置好之后，你可以直接在终端里操作 GitHub：

```
发现一个登录页面的 Bug，当用户输入超长密码时会崩溃，帮我创建一个 Issue
```

Claude 输出如下。

```
让我在 GitHub 上创建这个 Issue...
[调用 GitHub MCP server → create_issue]

已创建 Issue #142: "Login page crashes with extremely long password"
- Labels: bug, high-priority
- URL: https://github.com/your-org/your-repo/issues/142
```

GITHUB_TOKEN 需要事先创建。到 GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens，勾选你需要的仓库权限即可。

**实战 3：Notion MCP——文档集成**

Notion 官方开源了 MCP 服务器，让 Claude 可以直接读写你的 Notion 工作区。

```json
{
  "mcpServers": {
    "notion": {
      "type": "http",
      "url": "https://mcp.notion.com/mcp",
      "headers": {
        "Authorization": "Bearer ${NOTION_API_KEY}"
      }
    }
  }
}
```

NOTION_API_KEY 在  [Notion Developers](https://www.notion.so/profile/integrations) 创建 Internal Integration 后获取。记得在 Notion 页面的 Connections 里添加你创建的 Integration，否则 Claude 看不到页面内容。

```
从 Notion 里读取"Q1 产品路线图"，帮我提取其中的技术任务
```

Claude 输出如下。

```
读取 Notion 文档...
[调用 Notion MCP server → search → get_page]

从 "Q1 产品路线图" 提取的技术任务：
1. 用户认证系统升级（2月前）
   - 支持 OAuth 2.0
   - 添加双因素认证
2. 搜索功能优化（3月前）
   - 实现全文搜索
   - 添加搜索建议
```

**实战 4：数据库——查询与分析**

连接数据库是 MCP 最实用的场景之一。@bytebase/dbhub 支持 PostgreSQL、MySQL、SQLite 等多种数据库：

```json
{
  "mcpServers": {
    "database": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@bytebase/dbhub", "--dsn", "${DATABASE_URL}"]
    }
  }
}
```

DATABASE_URL 格式为  postgresql://user:password@localhost:5432/mydb。建议使用只读账户，防止 Claude 误操作修改数据。

```
帮我查一下数据库里上个月的订单数量和总金额
```

Claude 输出如下。

```
查询数据库...
[调用 database MCP server → run_query]

上个月（2025年12月）的订单统计：
- 订单数量：1,234 笔
- 总金额：¥456,789.00
- 平均客单价：¥370.21
```

把上面几个服务组合到一起，你就拥有了一个连接多个系统的完整工具箱。

以下是一个面向全栈开发者的  .mcp.json 配置：

```json
{
  "mcpServers": {
    "context7": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    },
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_TOKEN}"
      }
    },
    "notion": {
      "type": "http",
      "url": "https://mcp.notion.com/mcp",
      "headers": {
        "Authorization": "Bearer ${NOTION_API_KEY}"
      }
    },
    "database": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@bytebase/dbhub", "--dsn", "${DATABASE_URL}"]
    },
    "fetch": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  }
}
```

对应的  .env 文件（绝对不要提交到版本控制）：

```
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
DATABASE_URL=postgresql://readonly:password@localhost:5432/mydb
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxx
```

有了这个配置，你在终端里的对话可以跨越多个系统而不中断上下文。你可以一边讨论代码中的 Bug，一边查数据库确认问题，一边创建 GitHub Issue，一边翻 Notion 需求文档——Claude 全程保持上下文，不需要你在五个工具间来回切换。

![img](https://static001.geekbang.org/resource/image/03/0c/037bbb7069f48c373aef35cb976c680c.jpg?wh=1536x1024)

## 创建自定义 MCP 服务器

当现有的 MCP 服务器无法满足需求时，你可以创建自己的。MCP 官方提供了 TypeScript 和 Python 两套 SDK，开发一个基本的 MCP Server 只需要几十行代码。

**TypeScript SDK**

TypeScript SDK 是使用最广泛的 MCP 开发工具。安装依赖：

```
npm install @modelcontextprotocol/sdk zod
```

下面是一个完整的 Todo 管理 MCP Server（src/index.ts）。它定义了三个工具（添加、列出、完成待办）和一个资源（统计信息）。注意每个工具都有名称、描述、参数 schema 和处理函数——Claude 通过描述来决定何时调用这个工具：

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// 内存存储
const todos: { id: string; text: string; done: boolean }[] = [];

// 创建 MCP 服务器
const server = new McpServer({
  name: "my-todo-server",
  version: "1.0.0",
});

// 定义工具：添加待办
server.tool(
  "todo_add",
  "Add a new todo item",
  {
    text: z.string().describe("The todo text"),
  },
  async ({ text }) => {
    const todo = {
      id: Math.random().toString(36).substring(2, 9),
      text,
      done: false,
    };
    todos.push(todo);

    return {
      content: [
        {
          type: "text",
          text: `Added todo: ${todo.id} - ${todo.text}`,
        },
      ],
    };
  }
);

// 定义工具：列出待办
server.tool(
  "todo_list",
  "List all todo items",
  {},
  async () => {
    const text = todos.length === 0
      ? "No todos found."
      : todos
          .map((t) => `[${t.done ? "x" : " "}] ${t.id}: ${t.text}`)
          .join("\n");

    return {
      content: [{ type: "text", text: `Todos:\n${text}` }],
    };
  }
);

// 定义工具：完成待办
server.tool(
  "todo_complete",
  "Mark a todo as completed",
  {
    id: z.string().describe("The todo ID"),
  },
  async ({ id }) => {
    const todo = todos.find((t) => t.id === id);
    if (!todo) {
      return {
        content: [{ type: "text", text: `Todo not found: ${id}` }],
        isError: true,
      };
    }

    todo.done = true;
    return {
      content: [{ type: "text", text: `Completed: ${todo.text}` }],
    };
  }
);

// 定义资源：统计信息
server.resource(
  "stats",
  "stats://current",
  async (uri) => {
    return {
      contents: [
        {
          uri: uri.href,
          mimeType: "application/json",
          text: JSON.stringify({
            total: todos.length,
            completed: todos.filter((t) => t.done).length,
            pending: todos.filter((t) => !t.done).length,
          }, null, 2),
        },
      ],
    };
  }
);

// 启动服务器
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP Server started");
}

main().catch(console.error);
```

**Python SDK**

Python 版本使用装饰器风格，对 Python 开发者来说更加自然。

```python
pip install mcp
from mcp.server.fastmcp import FastMCP

server = FastMCP("my-todo-server")

todos = []

@server.tool("todo_add")
async def add_todo(text: str) -> str:
    """Add a new todo item"""
    import random
    import string
    todo_id = ''.join(random.choices(string.ascii_lowercase, k=7))
    todos.append({"id": todo_id, "text": text, "done": False})
    return f"Added todo: {todo_id} - {text}"

@server.tool("todo_list")
async def list_todos() -> str:
    """List all todo items"""
    if not todos:
        return "No todos found."
    return "\n".join(
        f"[{'x' if t['done'] else ' '}] {t['id']}: {t['text']}"
        for t in todos
    )

@server.tool("todo_complete")
async def complete_todo(id: str) -> str:
    """Mark a todo as completed"""
    for todo in todos:
        if todo["id"] == id:
            todo["done"] = True
            return f"Completed: {todo['text']}"
    return f"Todo not found: {id}"

if __name__ == "__main__":
    server.run()
```

**配置自定义服务器**

写完代码后在  .mcp.json 中注册。TypeScript 版本先编译再运行，Python 版本直接运行：

TypeScript 版本：

```json
{
  "mcpServers": {
    "my-todo": {
      "type": "stdio",
      "command": "node",
      "args": ["./mcp-server/build/index.js"]
    }
  }
}
```

Python 版本：

```json
{
  "mcpServers": {
    "my-todo": {
      "type": "stdio",
      "command": "python",
      "args": ["./mcp-server/server.py"]
    }
  }
}
```

**5 条 MCP 安全原则**

MCP 的强大能力也带来了安全风险，它本质上是在给 AI Agent 开放访问外部系统的权限。这里给出五条 MCP 使用的安全原则。

1. 验证服务器来源——只使用官方或知名来源的 MCP 服务器。一个恶意的 MCP Server 可以在你不知情的情况下读取敏感文件、窃取环境变量中的密钥。
2. 限制权限范围——遵循最小权限原则，只给必要的目录和资源访问：

```json
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-filesystem",
        "/safe/directory/only"
      ]
    }
  }
}
```

3. 使用只读凭证——对于数据库等关键系统，永远不要给 MCP Server 写权限——除非你明确需要 Claude 修改数据。
4. 保护敏感凭证——绝对不要在配置文件中硬编码 Token。使用环境变量引用，将敏感值存在不提交到 git 的文件中。
5. 审计 MCP 服务器代码——对于开源服务器，在使用前检查其代码：它请求哪些权限？它如何处理用户数据？花十分钟审计代码，可能帮你避免一次严重的安全事故。

![img](https://static001.geekbang.org/resource/image/b1/7e/b19c952d151228c2ff36e40dc548c37e.png?wh=1536x1024)

**调试与故障排除**

MCP 配置好之后，可能不会一次就跑通。Claude Code 内置了调试工具：

```bash
# 列出所有配置的服务器
claude mcp list

# 查看服务器详细信息
claude mcp get my-server

# 启用调试模式查看 MCP 连接详情
claude --debug
```

常见问题速查表如下。

| 问题           | 可能原因           | 解决方案                                           |
| -------------- | ------------------ | -------------------------------------------------- |
| 服务器无法启动 | 命令或路径错误     | 检查 command 和 args，确保依赖已安装               |
| 连接超时       | 网络问题或服务器慢 | 增加 MCP_TIMEOUT，检查网络                         |
| 认证失败       | Token 错误或过期   | 确认环境变量已设置，检查 token 有效性              |
| 输出被截断     | 超过 token 限制    | 增加 MAX_MCP_OUTPUT_TOKENS，或让服务器返回更少数据 |

MCP 工具可能产生大量输出。因此在 Token 的控制方面，Claude Code 对 MCP 输出提供了两级保护。

| 设置     | 默认值        | 说明           |
| -------- | ------------- | -------------- |
| 警告阈值 | 10,000 tokens | 超过时显示警告 |
| 最大输出 | 25,000 tokens | 超过时截断     |

如果需要处理大量数据，可以通过环境变量调整上限。但更好的做法是在 MCP Server 端做分页或摘要：

```
export MAX_MCP_OUTPUT_TOKENS=50000
```

# ==18｜庖丁解牛：Tools 工具系统内核剖析==

今天我们深入讨论一个更根本的问题：Claude Code 内置的那些工具本身是怎么回事？ 它们和 MCP 扩展的外部工具又是什么关系？

## Agentic Loop——工具驱动的智能循环

如果 Claude 没有工具，它只能做一件事：输出文本。

```
用户: 帮我修复 src/api.js 中的 bug
Claude:（思考）这应该是一个 JavaScript 文件...
       （继续思考）用户想让我修复 bug...
       （输出文本）"您好，请提供 src/api.js 的内容，我来帮您分析问题。"
```

它能思考、能分析、能给建议，但不能行动。

有了工具，情况完全不同，我们和 Claude 的交流可能是这样的。

```
用户: 帮我修复 src/api.js 中的 bug
Claude:（思考）让我先读取这个文件
       （调用 Read 工具）→ 获取文件内容
       （思考）我发现了问题，第 42 行的 null 检查缺失
       （调用 Edit 工具）→ 修改文件
       （思考）让我运行测试确认修复成功
       （调用 Bash 工具）→ 执行 npm test
       （输出）"我已经修复了问题，测试全部通过。"
```

**工具让 Claude 从顾问变成了执行者。**

Claude Code 的工作循环——Agentic Loop 可以分为三个阶段，根据任务需要灵活切换。

![img](https://static001.geekbang.org/resource/image/e8/1d/e89407a8ddef056f5bc509b6503cd81d.jpg?wh=2213x1041)

![img](https://static001.geekbang.org/resource/image/e6/a4/e63bf24c69fd64ea55507e3d8f6773a4.jpg?wh=2735x883)

简单任务可能只需要一轮，复杂任务可能循环几十次。每一次工具调用的返回结果，都会反馈给 Claude，影响下一步的决策。

Claude（模型）负责推理，Tools 负责行动。而 Claude Code 扮演的角色是  Agentic Harness，它把模型和工具连接起来，提供执行环境、上下文管理、权限控制等基础设施。

![img](https://static001.geekbang.org/resource/image/c5/cb/c56f8c4dc4ea0c47e6b9d9b6460fc8cb.jpg?wh=2357x1655)

理解这个架构很重要，因为你配置的所有扩展（Skills、Hooks、MCP）都是在这个 Harness 上工作的，而不是直接修改 Claude 模型本身。



**Claude Code 内置工具完整清单**

早期，Claude Code 只是内置了十几个工具（目前逐渐增多，可能已经有 20 多个了，最新列表在[这里](https://code.claude.com/docs/en/tools-reference)），按功能分为六个类别。

文件操作类，Claude 与代码交互的最基本方式。Read 是只读的，不需要额外授权；Edit、Write、MultiEdit 会修改文件系统，因此需要用户确认。

搜索类，Claude 的“眼睛”——在动手之前先看清楚代码库的全貌。Glob 按文件名模式定位文件，Grep 按内容搜索定位代码行，两者都是只读操作，无需授权。

![img](https://static001.geekbang.org/resource/image/b6/8d/b67dfd847337200f70018e392c8a738d.jpg?wh=2895x614)

执行类，整个工具集里能力最强也最危险的一个。Bash 可以执行操作系统能做的一切。正因如此，它始终需要用户授权。

![img](https://static001.geekbang.org/resource/image/ca/ff/ca5e8cb9f2b72e382b266947590166ff.jpg?wh=2930x463)

网络类，让 Claude 突破本地文件系统的边界，访问互联网上的信息。查文档、搜报错、获取 API 响应都靠这两个工具。

![img](https://static001.geekbang.org/resource/image/f0/16/f0b8fa3a9b6f4a08d62756bb98634f16.jpg?wh=3015x535)

编排类，这组工具不直接操作代码，而是管理 Agent 的工作流程：把复杂任务委派给子代理、在需要时向用户提问、用任务清单跟踪多步骤进度。

![img](https://static001.geekbang.org/resource/image/1b/01/1b6d1f55a11b591783638c57d992f701.jpg?wh=2374x569)

辅助类，支撑性工具，用于管理后台任务和系统状态切换。日常使用中不常直接接触，但在自动化场景下不可或缺。

![img](https://static001.geekbang.org/resource/image/43/d3/43214f8f1cf7ceac3bf63ee185a6ebd3.jpg?wh=2257x730)



**工具的风险等级**

为什么要这样分类？因为不同类别的工具有不同的风险等级：

![img](https://static001.geekbang.org/resource/image/5a/4c/5a78db0bb5b8e1f80cbc1a481896554c.jpg?wh=2489x1228)

理解这个分类，你就能：

- 为子代理配置最小权限（只读任务只给 Read/Grep/Glob）
- 设计防护机制（高风险工具加 Hook 检查）
- 理解权限提示的逻辑（低风险工具不弹窗，高风险工具要确认）



## 从原语到涌现——工具设计哲学

看完工具清单，你可能会问：只有十几个内置工具，凭什么覆盖几乎所有软件工程任务？为什么没有看到重构工具、调试工具、部署工具这些高级工具？

答案指向同一个工程哲学：Claude Code 的工具集是一组精心选择的原语（primitives），而不是一组特化的高级能力。

**软件工程的五个原子操作**

一个开发者每天做的所有事情，无论多么复杂，都可以分解为五种原子操作。

![img](https://static001.geekbang.org/resource/image/94/8e/9439dd702e8e3c2015d6c1827801968e.jpg?wh=2367x1459)

想想你的一天都会哪些动作？

- 你打开文件看代码 → 感知
- 搜索某个函数在哪里被调用 → 搜索
- 你修改代码修复一个 bug → 修改
- 你运行  npm test 验证修复 → 执行
- 你上 Stack Overflow 查错误信息 → 获取

任何复杂任务，无论是“重构整个模块”还是“搭建 CI/CD 流水线”，都是这五种操作的不同排列组合。

![img](https://static001.geekbang.org/resource/image/61/f8/615760bd0bc450196db30116ed8ce3f8.jpg?wh=3055x2177)

这就是 Claude Code 工具设计的核心洞察：不需要为每种任务造一个专用工具，只需要把原子操作做好。



**类比：为什么编程语言只需要几条指令**

这个设计哲学并不新鲜，我们回顾一些优秀的产品，就能发现它们的思路都是这样。

![img](https://static001.geekbang.org/resource/image/a2/56/a257e66024b21752a3bd65af74248756.jpg?wh=2282x724)

Unix 的设计哲学是“做好一件事”（Do One Thing Well），然后通过管道组合。Claude Code 的工具设计完全继承了这个思想，但比 Unix 管道强大得多。Unix 管道是预定义的、线性的。而 Claude Code 的组合是动态的、分支的、自适应的，Claude 在每次工具调用后，根据返回的结果重新推理下一步该做什么。



**涌现：为什么 1+1 远大于 2**

为什么这些简单工具组合在一起，能产生远超其各自能力之和的效果？

答案是涌现（Emergence）：

```
涌现能力 = 原语工具 × LLM 推理 × 反馈循环
```

- 原语工具提供行动能力（感知、搜索、修改、执行、获取）
- LLM 推理提供决策能力（理解任务 → 分解步骤 → 选择工具 → 解读结果）
- 反馈循环让二者持续交互（工具输出 → 新的理解 → 新的行动）

![img](https://static001.geekbang.org/resource/image/99/73/9969f8f6e67a56b929b144acaa855073.jpg?wh=2508x1464)

我们用一个具体例子说明。比方说，我们要完成“修复用户登录时偶尔出现的 500 错误”这任务，虽然没有任何一个工具能“修复 bug”，但看看它们是怎么组合的。

```
第 1 步：Grep("500", "error", "login")
         → 找到 3 个文件中有相关错误日志
         → Claude 推理："日志显示错误出现在 auth-service.js"

第 2 步：Read("src/auth-service.js")
         → 读取 200 行代码
         → Claude 推理："第 87 行的 token 验证没有 null 检查"

第 3 步：Grep("validateToken", type: "files_with_matches")
         → 找到 5 个文件引用了这个函数
         → Claude 推理："需要同时检查调用方是否有防御性处理"

第 4 步：Read("src/middleware/auth.js")
         → 读取调用方代码
         → Claude 推理："调用方也没有 null 检查，需要在源头修复"

第 5 步：Edit("src/auth-service.js", line 87)
         → 添加 null 检查

第 6 步：Bash("npm test -- --grep 'auth'")
         → 运行测试，2 个失败
         → Claude 推理："测试用例需要更新"

第 7 步：Edit("tests/auth.test.js")
         → 更新测试用例

第 8 步：Bash("npm test")
         → 全部通过
```

单独看每一步，只是读文件、搜索文本、编辑文件、执行命令——极其简单。但组合起来看，Claude 完成了一次完整的 bug 调查、定位、修复、验证，还处理了跨文件依赖和测试更新。

这就是涌现——复杂的智能行为从简单工具的交互中自然产生。



**“高级工具”是涌现出来的，不是内置的**

这是一个非常重要的观点，首先我们拆解一下所谓的“高级能力”，实际是哪些工具的组合。

![img](https://static001.geekbang.org/resource/image/ef/4c/ef765be28efc707effb559403e51a44c.jpg?wh=2124x1025)

给 Claude 一个“重构工具”反而是有害的。 因为“重构”不是原子操作，它是一系列决策的集合。把决策权交给 Claude 的推理能力，比交给一个固定逻辑的工具更灵活。



**Bash：图灵完备的万能逃逸舱**

在所有工具中，Bash 最特殊。它是唯一一个“不确定做什么”的工具——其他工具都有明确职责，但 Bash 能做操作系统能做的一切。

从理论上说，仅凭 Bash 一个工具，Claude 就能完成所有任务：用  cat 读文件、sed 改文件、find 搜索。那为什么还需要 Read、Edit、Glob、Grep？

我认为有三个原因。

1. 结构化交互：Read 返回的文件内容带行号、受长度控制；Bash cat 返回原始文本。结构化返回值让 Claude 更准确地理解和定位代码。
2. 权限精细控制：你可以允许 Read 但禁止 Bash，这样 Claude 能看代码但不能执行任意命令。如果只有 Bash，权限就是全有或全无。
3. Token 效率：Bash 输出通常包含大量冗余信息。专用工具返回精简的、Claude 直接需要的信息。

背后的设计原则是，Bash 提供能力的完备性，专用工具提供交互的效率和安全的可控性。二者缺一不可。





## 权限控制体系

如果说工具定义了“Claude 能做什么”，那么权限系统决定了“Claude 可以做到什么程度”。 同一组原语工具，在不同权限边界下，其行为能力和风险等级会呈现出完全不同的形态，这也是 Agent 系统从“可用”走向“可控”的关键一环。

从工程角度看，Claude Code 并不是简单地“给或不给权限”，而是构建了一套分层的权限控制体系：既保证低风险操作的流畅执行，又对高风险行为进行精细约束，从而在效率与安全之间取得平衡。

**权限分层**

Claude Code 使用分层权限系统来平衡能力和安全。

![img](https://static001.geekbang.org/resource/image/56/b5/56b1c786ab56669896ba951ebc9110b5.jpg?wh=2967x1003)

关键区别是，Bash 命令点“Yes, don’t ask again”后永久生效（该项目目录下），文件编辑的授权只在当前会话有效。



**权限模式**

Claude Code 支持多种权限模式，通过  Shift+Tab 循环切换。

![img](https://static001.geekbang.org/resource/image/4e/83/4e155770b822538439a210ca16352983.jpg?wh=2983x1479)



**权限规则语法**

在  settings.json 中可以精细配置工具权限：

```
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Read"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(curl *)",
      "Edit(.env)"
    ]
  }
}
```

规则评估顺序：deny → ask → allow。deny 规则总是优先。

Bash 规则通配符：

```
Bash(npm run build)     # 精确匹配 "npm run build"
Bash(npm run *)         # 匹配 "npm run" 后跟任意内容
Bash(git * main)        # 匹配 "git checkout main", "git merge main" 等
```

注意空格边界：Bash(ls *) 匹配  ls -la 但不匹配  lsof；Bash(ls*) 两者都匹配。

Read/Edit 规则路径语法：

```
{
  "permissions": {
    "allow": [
      "Read",
      "Edit(/src/**/*.ts)"
    ],
    "deny": [
      "Read(./.env)",
      "Edit(//etc/passwd)",
      "Read(~/.ssh/*)"
    ]
  }
}
```

![img](https://static001.geekbang.org/resource/image/92/9f/92365f94203bd4e8197be5dfb7259a9f.jpg?wh=2901x1423)

WebFetch 和 MCP 工具规则：

```
{
  "permissions": {
    "allow": [
      "WebFetch(domain:github.com)",
      "mcp__puppeteer",
      "mcp__database__query"
    ],
    "deny": [
      "WebFetch(domain:internal.company.com)",
      "mcp__database__drop_table"
    ]
  }
}
```



**配置文件层级**

权限配置可以在多个层级设置，按从高到低的优先级排序，如下表所示。

![img](https://static001.geekbang.org/resource/image/de/e7/de20da1a7e03238844bcf14fcda058e7.jpg?wh=2967x1208)

高优先级的配置覆盖低优先级。如果项目配置禁止了某个操作，用户配置无法覆盖。



**CLI 工具控制**

除了配置文件，还可以通过 CLI 参数临时控制工具：

```bash
# 限制可用工具集
claude --tools "Read,Grep,Glob"

# 预授权特定命令（执行时不弹窗）
claude --allowedTools "Bash(npm run *)" "Bash(git diff *)" "Read"

# 禁用特定工具（从上下文中完全移除）
claude --disallowedTools "Bash(curl *)" "Edit"
```

![img](https://static001.geekbang.org/resource/image/44/52/44bc61c913e8c3c99d6a48a9ac0f3c52.jpg?wh=2831x1007)

这些控制机制同样适用于子代理配置：

```
---
name: code-reviewer
description: Review code for security and quality issues
tools: Read, Grep, Glob          # 只给只读工具
model: sonnet
---
```



## 工具扩展与架构定位

下面来看工具扩展的部分。

**工具能力的三个层次**

内置工具覆盖了大部分编码任务，但连接外部系统时需要扩展。工具能力可以分为三个层次——从内置原语到 Bash 可达到 MCP 扩展，每一层都在前一层的基础上拓展能力边界。

![img](https://static001.geekbang.org/resource/image/82/fa/82ce8b4e294c30e1d8d87c8ca17f0efa.jpg?wh=3009x2165)

通过 Bash，Claude 已经可以运行任何命令行工具。那为什么还需要 MCP？三个理由：结构化输入输出（MCP 返回结构化数据，不需要解析文本）、工具发现（连接一个 MCP Server，所有工具自动可用）、安全隔离（MCP 在 Server 端做访问控制，比  Bash(curl *) 精细得多）。这些正是上一讲（第 17 讲）详细讲解的内容。

**工具是基础，其他机制是上层建筑**

回顾一下 Tools 与其他扩展机制的关系。

![img](https://static001.geekbang.org/resource/image/a9/ed/a951a6a7e21da2ede02d3cbfa91977ed.jpg?wh=2848x1955)

![img](https://static001.geekbang.org/resource/image/b9/a9/b96f4124fa221d40aa518a0e4fe770a9.jpg?wh=2894x1130)

这种分层设计让你可以在不同粒度上精确控制 Claude 的能力边界。所有你在前面学过的扩展机制 SubAgents、Skills、Commands、Hooks、MCP，都建立在 Tools 基础上。理解了工具系统，就理解了整座大厦的地基。



## 总结一下

这一讲我们像庖丁解牛般，把 Claude Code 的工具系统彻底拆开来看了看。

**Agentic Loop** 是 Claude Code 的工作核心：收集上下文 → 采取行动 → 验证结果，循环往复。工具是行动的载体，没有工具的 Claude 只能输出文本。Claude Code 作为 Agentic Harness，把模型和工具连接起来。

**工具设计哲学**遵循 Unix 原则——十几个精选的原语工具覆盖了五个原子操作：感知（Read）、搜索（Glob/Grep）、修改（Edit/Write）、执行（Bash）、获取（Web）。涌现公式：原语工具 × LLM 推理 × 反馈循环 = 无限复杂能力。重构、调试、部署这些高级能力不需要专门的工具，它们是原语工具在 LLM 推理驱动下的涌现行为。

**权限控制**分层相当精细。权限模式从 default 到 bypassPermissions 六档可调；规则语法支持通配符、路径模式、域名限制；配置层级从 Managed（组织级）到 User（个人级）四层叠加。

**工具扩展**分三个层次：内置原语 → Bash 可达 → MCP 扩展。Tools 是基础层，Sub-Agents、Skills、Hooks、MCP 这些上层建筑， 都建立在 Tools 层之上。