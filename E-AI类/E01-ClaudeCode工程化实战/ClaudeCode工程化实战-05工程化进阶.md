> 来自极客时间《Claude Code工程化实战》--黄佳

# <mark>工程化进阶（17~20）</mark>

# 19｜无人值守：Headless 模式与 CI/CD 集成

在前面的章节中，我们一直在终端里与 Claude 对话——你输入一句话，Claude 响应，你再输入，它再响应。这是交互模式。交互模式有一个根本限制：需要一个人类一直坐在屏幕前面。

这一讲，我们要打破这个限制。我们要让 Claude Code 在完全没有人工干预的情况下自动运行——在 CI/CD 流水线中审查代码，在 pre-commit hook 里检查提交，在定时任务中生成报告。这就是 Headless 模式的核心：从“有人值守”到“无人值守”。

**凌晨三点的代码审查**

这是一个分布在三个时区的远程团队：亚洲、美国、欧洲。当亚洲的小王在早上 9 点提交 PR 时，美国的 Tech Lead 还在睡觉。当美国的同事审查完代码时，小王已经下班了。每个 PR 的审查周期动辄 24-48 小时，不是因为审查本身需要那么长时间，而是因为人的作息时间不同步。

有一天，团队配置了一个 GitHub Action：每当 PR 创建或更新时，Claude Code 会自动进行初步审查——检查代码风格、潜在 Bug、安全问题。当人类审查者醒来时，他们看到的不是一片空白的 PR，而是已经有一份详细的 AI 审查报告。

PR 的平均审查周期从 36 小时缩短到了 8 小时。这就是 Headless 模式的价值：让 Claude Code 在没有人工干预的情况下自动工作。

## Headless 模式核心机制

> [Anthropic 官方文档](https://code.claude.com/docs/en/headless)说：Claude Code 包含 Headless 模式，用于 CI、pre-commit hooks、构建脚本和自动化等非交互式场景。

Headless 这个词来自“无头浏览器”（Headless Browser）的概念——没有图形界面，但功能完整。同样，Headless 模式下的 Claude Code 没有交互式终端界面，但拥有和交互模式完全相同的代码分析能力、工具调用能力和推理能力。唯一的区别是：输入变成了一次性的 prompt，输出变成了 stdout 上的文本或 JSON，不再有来回对话。

启用 Headless 模式的关键是  -p（或  --print）标志。这个标志的名字很直观，print，意思是“把结果打印出来就行，不要打开交互界面”。

```bash
# 基本 headless 执行
claude -p "解释这段代码是做什么的"

# 从 stdin 读取输入
cat code.py | claude -p "分析这段代码"

# 结合文件内容
claude -p "找出这个文件中的 Bug" < buggy.js
```

下表清晰地展示了两种模式在各个维度上的差异。

| 特性       | 交互模式   | Headless 模式      |
| :--------- | :--------- | :----------------- |
| 用户界面   | 终端 TUI   | 无                 |
| 输入方式   | 实时对话   | 一次性提示         |
| 输出方式   | 流式显示   | stdout/JSON        |
| 用户确认   | 可交互确认 | 自动处理或跳过     |
| 会话持久化 | 自动保存   | 不保存（除非指定） |
| 典型用途   | 开发调试   | 自动化/CI          |

Headless 模式提供了一组命令行参数来精细控制执行行为。

| 参数                | 说明                            | 示例                       |
| :------------------ | :------------------------------ | :------------------------- |
| `-p, --print`       | 启用 headless 模式              | `claude -p "任务"`         |
| `--output-format`   | 输出格式：text/json/stream-json | `--output-format json`     |
| `--max-turns`       | 限制最大执行轮次                | `--max-turns 5`            |
| `--allowedTools`    | 只允许特定工具                  | `--allowedTools Read,Grep` |
| `--disallowedTools` | 禁用特定工具                    | `--disallowedTools Bash`   |
| `--continue`        | 继续上一个会话                  | `--continue`               |
| `--session-id`      | 指定会话 ID                     | `--session-id abc123`      |

> 特别值得注意的是  --allowedTools 和  --max-turns 这两个参数，它们是安全防护的第一道防线，能有效限制 Claude 在无人监管环境中的行为边界。
>
> 在 CI/CD 环境中，我建议你总是同时设置 --allowedTools 和 --max-turns。这不是因为不信任 Claude，而是因为无人值守环境中的任何意外都会被放大——一个失控的循环可能消耗大量 API tokens，一个意外的文件修改可能破坏构建。
>
> 防御性编程的原则不仅适用于业务代码，也适用于 AI 自动化的配置。

**输出格式**

Headless 模式支持三种输出格式。选择哪种格式，取决于你的下游消费者是谁——是人类读者、是程序解析器、还是实时监控系统。

- Text 格式

Text 是默认格式，它直接输出 Claude 的回复文本，没有任何元数据包装。适用场景为日志记录、简单脚本、人工审查。

```bash
claude -p "生成一个 Python hello world 函数" --output-format text
```

输出：

```
Here's a simple hello world function:

def hello_world():
    print("Hello, World!")
```

- JSON 格式

当你需要在程序中解析 Claude 的输出时，JSON 格式是更好的选择。在生产环境的 CI/CD 流水线中，你几乎总是应该使用 JSON 格式，因为它让你能够用程序化的方式验证执行结果、追踪成本、检测异常。

```bash
claude -p "列出当前目录文件" --output-format json
```

输出：

```json
{
  "type": "result",
  "subtype": "success",
  "session_id": "abc123",
  "is_error": false,
  "duration_ms": 1500,
  "duration_api_ms": 1200,                            // 耗时多久
  "num_turns": 1,
  "total_cost_usd": 0.005,                            // 花了多少钱
  "usage": {                                          // 用了多少 tokens
    "input_tokens": 150,
    "output_tokens": 200
  },
  "result": "文件列表：\n- file1.py\n- file2.js\n..."  // claude 回复文本
}
```

- Stream-JSON 格式

对于长时间运行的任务，你可能不想等到执行完成才看到输出，因此这种格式适用于实时进度显示、长时间任务监控、流式处理。Stream-JSON 格式以 JSONL（每行一个 JSON 对象）的方式实时输出执行过程中的每个事件——Claude 的每段回复、每次工具调用、每个工具返回结果。

这种格式特别适合需要实时进度显示的场景，比如在 CI 日志中实时展示 Claude 正在做什么。

```bash
claude -p "分析代码" --output-format stream-json
```

输出里（每行一个事件）：

```json
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"正在分析..."}]}}
{"type":"tool_use","tool":"Read","input":{"file_path":"/path/to/file"}}
{"type":"tool_result","tool":"Read","result":"file content..."}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"分析完成。"}]}}
{"type":"result","session_id":"abc123","is_error":false,"result":"最终结果"}
```

下面这段 Bash 脚本展示了如何逐行读取 Stream JSON 输出，并根据事件类型做出不同响应。你可以在此基础上扩展，比如在检测到 tool_use 事件时，更新进度条，在检测到 result 事件时触发下游通知。

```bash
claude -p "分析代码" --output-format stream-json | while IFS= read -r line; do
  type=$(echo "$line" | jq -r '.type')
  if [ "$type" = "result" ]; then
    echo "最终结果: $(echo "$line" | jq -r '.result')"
  elif [ "$type" = "tool_use" ]; then
    echo "正在使用工具: $(echo "$line" | jq -r '.tool')"
  fi
done
```

**Unix 管道集成**

Claude Code 的一个独特优势是它可以无缝融入 Unix 管道，成为你工具链中的一环。这不是一个附加功能，而是一种设计哲学——Claude Code 遵循 Unix“小工具、大组合”的传统，通过标准输入输出与其他命令行工具互联互通。

管道的核心思想是：前一个命令的输出，成为后一个命令的输入。

```bash
# 分析日志文件
cat server.log | claude -p "找出所有错误并总结原因"

# 解析 JSON
curl https://api.example.com/data | claude -p "提取所有用户的邮箱地址"

# 代码转换
cat old-code.js | claude -p "将这段 JavaScript 转换为 TypeScript"
```

管道的真正威力在于组合。

```bash
# 结合 find 和 xargs 批量处理
find src -name "*.py" | xargs -I {} claude -p "检查 {} 中的类型提示是否完整"

# 结合 git 工作流
git diff HEAD~1 | claude -p "总结这次提交的变更"

# 结合 grep 预过滤
grep -r "TODO" src/ | claude -p "将这些 TODO 转换为 GitHub Issue 格式"
```

Claude 不仅可以接收管道输入，它的输出同样可以通过管道流向下游。

```bash
# Claude 输出 -> jq 解析 -> 下游处理
claude -p "列出所有函数名" --output-format json | jq -r '.result' | sort | uniq

# Claude 生成代码 -> 直接写入文件
claude -p "生成一个 Express 路由处理函数" --output-format text > routes/user.js

# Claude 分析 -> 发送通知
claude -p "检查是否有安全漏洞" --output-format json | \
  jq -r '.result' | \
  mail -s "安全扫描报告" security@company.com
```

**批量处理模式**

当你需要对大量文件执行相同的 AI 分析任务时，批量处理模式就派上用场了。

下面是一个批量代码审查脚本。它遍历  src 目录下的所有 TypeScript 文件，对每个文件运行 Claude 审查，并将结果保存到独立的报告文件中。注意  --max-turns 3 的设置——对于单文件审查，3 轮通常就足够了，这样既能保证审查质量，又能控制成本和耗时。

```bash
#!/bin/bash
# batch-review.sh - 批量代码审查

RESULTS_DIR="review-results"
mkdir -p "$RESULTS_DIR"

# 遍历所有源文件
find src -name "*.ts" | while IFS= read -r file; do
  echo "Reviewing: $file"

  OUTPUT_FILE="$RESULTS_DIR/$(basename "$file").review.md"

  claude -p "Review $file for bugs and best practices. Be concise." \
    --output-format text \
    --max-turns 3 \
    --allowedTools Read > "$OUTPUT_FILE"

  echo "  -> $OUTPUT_FILE"
done

echo "Reviews complete. Results in $RESULTS_DIR/"
```

## GitHub Actions 集成

几行 YAML 配置就能实现 Claude Code 与 GitHub Actions 集成，让“AI 驱动的代码审查”不再停留于概念。

![img](https://static001.geekbang.org/resource/image/43/9a/433d256b69e3931b4b9f5253f0062c9a.jpg?wh=1663x741)

Anthropic 提供了[官方 GitHub Action](https://github.com/anthropics/claude-code-action)，让集成变得极其简单，官方 Action 支持两种模式，分别对应不同的使用场景。

| 模式                | 触发方式        | 适用场景           |
| :------------------ | :-------------- | :----------------- |
| Tag Mode (交互式)   | @claude 提及    | 开发者主动请求帮助 |
| Agent Mode (自动化) | 直接提供 prompt | CI/CD 自动化任务   |

Tag Mode 示例：在 PR 评论中输入 @claude 帮我审查这段代码，Claude 会自动响应并提供审查意见。

Agent Mode 示例：

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    prompt: "审查这个 PR 的所有变更，检查安全漏洞"
```

最简单的设置方式是在 Claude Code 终端中运行 /install-github-app，它会引导你完成整个配置过程，包括创建 GitHub App、配置 Webhook、设置权限等。

如果你更喜欢手动配置，或者需要定制化的工作流，可以按以下步骤操作。

- 第一步是在 GitHub 仓库的 Settings -> Secrets -> Actions 中添加 `ANTHROPIC_API_KEY`——这是唯一需要的密钥。
- 第二步是创建工作流文件，定义触发条件和执行步骤。创建 `.github/workflows/claude.yml`：

```yaml
name: Claude Code

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

jobs:
  claude:
    runs-on: ubuntu-latest
    # 只在 @claude 提及时触发
    if: contains(github.event.comment.body, '@claude')

    permissions:  # 遵循最小权限原则
      contents: read
      pull-requests: write
      issues: write

    steps:
      - uses: actions/checkout@v4

      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

它实现了一个完整的 AI 审查工作流：监听 PR 和 Issue 中的评论，在检测到 @claude 提及时触发，检出代码，然后让 Claude 分析并回复。

**场景一：自动化 PR 审查**

和上面的 Tag Mode 不同，这里不需要任何人工触发，PR 一创建就会自动开始审查。这个工作流稍微复杂一些，因为它需要获取变更文件列表、构建审查 prompt、然后将结果发布为 PR 评论。

```yaml
name: Claude PR Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

# 取消正在运行的重复工作流
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  review:
    runs-on: ubuntu-latest

    permissions:
      contents: read
      pull-requests: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # 需要完整历史以获取 diff

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install Claude Code
        run: npm install -g @anthropic-ai/claude-code

      # 1、获取变更文件列表
      - name: Get changed files
        id: changed
        run: |
          FILES=$(git diff --name-only origin/${{ github.base_ref }}...HEAD)
          echo "files=$(echo "$FILES" | tr '\n' ' ')" >> $GITHUB_OUTPUT

      # 2、构建审查 prompt
      - name: Run Claude Review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude -p "Review this PR for code quality, bugs, security issues.

          Changed files: ${{ steps.changed.outputs.files }}

          Provide specific, actionable feedback with file:line references." \
            --output-format json \
            --max-turns 10 \
            --allowedTools Read,Grep,Glob > review.json

      # 3、将结果发布为 PR 评论
      - name: Post Review Comment
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const review = JSON.parse(fs.readFileSync('review.json', 'utf8'));

            const comment = `## Claude Code Review\n\n${review.result}\n\n---\n*Automated review by Claude Code*`;

            await github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

这个工作流有几个值得注意的设计决策。

- `concurrency` 配置确保同一个 PR 上不会同时运行多个审查，当开发者快速连续推送多个 commit 时，旧的审查会被取消，只保留最新的。
- `fetch-depth: 0` 确保 checkout 时拉取完整的 git 历史，这样才能正确计算 diff。
- `--allowedTools Read,Grep,Glob` 限制 Claude 只能使用只读工具，确保审查过程不会意外修改任何文件。

除了只读审查，Headless 模式还可以用于自动修复。

**场景二：自动修复 Lint 错误**

下面的工作流展示了一个更激进的用例：当 lint 检查失败时，让 Claude 自动修复错误并提交。

> 这种模式适合风格类的 lint 规则（缩进、分号、import 排序等），可以放心让 Claude 自动修复并推送。
>
> 对于逻辑类的 lint 规则则需要更谨慎，可以让 Claude 修复，但不要自动推送，而是创建一个新的 PR 供人类审查。

```yaml
name: Auto Fix Lint Errors

on:
  push:
    branches: [main, develop]

jobs:
  fix:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - uses: actions/checkout@v4

      - name: Setup
        run: |
          npm ci
          npm install -g @anthropic-ai/claude-code

      - name: Run lint
        id: lint
        continue-on-error: true
        run: npm run lint 2>&1 | tee lint-output.txt

      # 注意这里没有设置 --allowedTools，因为 Claude 需要读写文件来完成修复。
      - name: Fix with Claude
        if: steps.lint.outcome == 'failure'
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude -p "Fix the lint errors in lint-output.txt. Make minimal changes." \
            --max-turns 20

      - name: Commit fixes
        run: |
          git config user.name "Claude Bot"
          git config user.email "claude@bot.local"
          git add -A
          git diff --staged --quiet || git commit -m "fix: auto-fix lint errors"
          git push
```

## Pre-commit Hook 集成

Pre-commit Hook 是另一个常见的 Headless 应用场景。与 CI/CD 流水线不同，Pre-commit Hook 运行在开发者的本地机器上，在代码提交之前进行检查。

它的优势是即时反馈——你不需要等到代码推送到远端才知道有问题，在 git commit 的那一刻就能得到 AI 的审查意见。

**基本 Pre-commit Hook**

下面这个 Hook 脚本在每次 git commit 时自动运行。它获取暂存区的文件列表，让 Claude 快速检查有没有明显问题。如果 Claude 回复“OK”，提交正常进行；如果发现问题，提交会被阻止，并显示问题列表。

我们创建 `.git/hooks/pre-commit`。

```bash
#!/bin/bash
# Pre-commit hook: Claude Code 快速审查

# 获取暂存的文件
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
  exit 0
fi

echo "Running Claude Code review on staged files..."

# 运行审查（只读工具，快速模式）
# 关键：让 Claude 用唯一 sentinel 表达"通过"，不要让它输出 "OK"——
# 因为 "OK" 是常见英语词，会在 "looks ok" / "blocked" / "okay" 等中误命中。
RESULT=$(claude -p "Quick review these staged files for obvious issues:
$STAGED_FILES

# 限制执行轮次 3，因为不能让开发者等太久
# 并且只允许只读操作
Focus on: syntax errors, security issues, obvious bugs.
Reply with 'OK' if no issues, or list the problems." \
  --output-format text \
  --max-turns 3 \
  --allowedTools Read,Grep)

# 检查结果
if echo "$RESULT" | grep -qi "OK"; then
  echo "Claude review passed"
  exit 0
else
  echo "Claude found issues:"
  echo "$RESULT"
  echo ""
  echo "Commit blocked. Fix the issues or use --no-verify to skip."
  exit 1
fi
```

然后设置权限：

```
chmod +x .git/hooks/pre-commit
```

**自动生成 Commit Message**

这个 Hook 可以利用 Claude 分析 diff 内容，帮我们自动生成符合 Conventional Commits 规范的 commit message。

创建 `.git/hooks/prepare-commit-msg`：

```bash
#!/bin/bash
# 自动生成 commit message

# 如果用户通过 -m 提供了 commit message，跳过
# $1 表示 commit message 的来源：message(-m)、template、merge、squash
if [ -n "$1" ]; then
  exit 0
fi

# 如果获取到 diff 为空，则跳过
DIFF=$(git diff --cached)

if [ -z "$DIFF" ]; then
  exit 0
fi

# 生成 commit message
MESSAGE=$(claude -p "Generate a concise commit message for these changes: 

$DIFF

Format: <type>: <description>
Types: feat, fix, docs, style, refactor, test, chore
Reply with ONLY the commit message, nothing else." \
  --output-format text \
  --max-turns 1)

# 将生成的 message 写入文件开头，保留 Git 的注释模板
TEMP_FILE=$(mktemp)
echo "$MESSAGE" > "$TEMP_FILE"
echo "" >> "$TEMP_FILE"
cat "$1" >> "$TEMP_FILE"
mv "$TEMP_FILE" "$1"
```

> 使用方式：`git commit`

**使用 pre-commit 框架**

如果你的团队使用 [pre-commit](https://pre-commit.com/) 框架来管理 Git hooks，可以将 Claude 审查集成为框架中的一个 hook。这样的好处是，hook 的安装和更新由框架统一管理，团队成员不需要手动拷贝 hook 脚本。

配置 `.pre-commit-config.yaml`：

```yaml
repos:
  - repo: local
    hooks:
      - id: claude-review
        name: Claude Code Review
        entry: bash -c 'claude -p "Review staged changes for issues" --max-turns 3 --output-format text'
        language: system
        types: [python, javascript, typescript]
        stages: [pre-commit]
```

## 实战项目：完整的 CI/CD 审查系统

前面我们分别学习了 Headless 模式的各个组件——输出格式、管道集成、GitHub Actions、Pre-commit Hook。现在让我们把它们组装成一个完整的自动化审查系统。这个系统涵盖了从本地开发到远程 CI 的完整链路。

![img](https://static001.geekbang.org/resource/image/dc/49/dc120ec7e1a9e4c3dd49c9a99d013049.jpg?wh=2461x1834)

下面的目录结构展示了一个完整的 CI/CD 审查系统需要哪些文件。

```
my-project/
├── .github/
│   └── workflows/
│       └── claude-review.yml    # GitHub Action 配置
├── scripts/
│   └── review.sh                # 本地审查脚本
├── .git/
│   └── hooks/
│       └── pre-commit           # Pre-commit Hook
└── CLAUDE.md                    # Claude 记忆文件
```

**CLAUDE.md**

`CLAUDE.md` 在 Headless 模式中扮演着关键角色。无论是 pre-commit hook 还是 GitHub Actions 中的 Claude，都会读取项目根目录的 CLAUDE.md 来了解审查规范。这意味着你可以通过一份配置文件，统一所有环节的审查标准。

```markdown
# 代码审查规范

## 审查重点
1. 代码质量：命名规范、DRY 原则、复杂度
2. 安全问题：输入验证、SQL 注入、XSS
3. 性能问题：N+1 查询、内存泄漏
4. 测试覆盖：关键路径必须有测试

## 输出格式
- Critical: 必须修复
- Warning: 应该修复
- Suggestion: 建议改进

## 禁止操作
- 不要修改 .env 文件
- 不要执行 npm publish
- 不要修改数据库迁移文件
```

**scripts/review.sh**

`scripts/review.sh` 是一个独立的本地审查脚本，开发者可以在任何时候手动运行它来审查代码，它与 CI 中的审查使用相同的 Claude 能力。

```bash
#!/bin/bash
# review.sh - 本地代码审查脚本

set -e

TARGET=${1:-.}

# 检查 API Key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY not set"
    exit 1
fi

# 检查 Claude Code 是否安装
if ! command -v claude &> /dev/null; then
    echo "Error: Claude Code not installed"
    echo "Install with: npm install -g @anthropic-ai/claude-code"
    exit 1
fi

echo "Starting code review for: $TARGET"

# 构建文件列表
if [ -d "$TARGET" ]; then
    FILES=$(find "$TARGET" -type f \( -name "*.ts" -o -name "*.js" -o -name "*.py" \) | head -20)
else
    FILES="$TARGET"
fi

echo "Files to review:"
echo "$FILES"
echo ""

# 运行审查
PROMPT="Review the following code files:

$FILES

Analyze for:
1. Code quality and readability
2. Potential bugs and edge cases
3. Security vulnerabilities
4. Performance issues
5. Best practices violations

Provide a detailed report with file:line references."

RESULT=$(claude -p "$PROMPT" \
    --output-format text \
    --max-turns 15 \
    --allowedTools Read,Grep,Glob)

# 输出结果
echo "============================================"
echo "               REVIEW REPORT                "
echo "============================================"
echo "$RESULT"

# 保存到文件
REPORT_FILE="review-report-$(date +%Y%m%d-%H%M%S).md"
cat > "$REPORT_FILE" << EOF
# Code Review Report

**Date**: $(date)
**Target**: $TARGET

$RESULT

*Generated by Claude Code*
EOF

echo ""
echo "Report saved to: $REPORT_FILE"
```

**GitHub Action 配置【新修订内容】**

下面是生产级的 GitHub Action 配置，完整文件参见 `.github/workflows/claude-review.yml`：

> 注意看文件中【要点】部分。

```yaml
name: Claude PR Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install Claude Code
        run: npm install -g @anthropic-ai/claude-code

      # 【变化】1、增加了变更文件计数
      - name: Get changed files
        id: changed
        run: |
          FILES=$(git diff --name-only "origin/${{ github.base_ref }}...HEAD" || true)
          # 【要点】2、grep -c . 在空字符串时返回 0；wc -l 会把空字符串错误地计成 1
          COUNT=$(echo "$FILES" | grep -c . || true)
          {
            echo "files<<CHANGED_FILES_EOF_SENTINEL"
            echo "$FILES"
            echo "CHANGED_FILES_EOF_SENTINEL"
          } >> "$GITHUB_OUTPUT"
          echo "count=$COUNT" >> "$GITHUB_OUTPUT"

      - name: Run Claude Review
        id: review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          # 【要点】3、多行变量通过 env: 传，不通过 ${{ }} 直接拼进 shell，避免命令注入。
          CHANGED_FILES: ${{ steps.changed.outputs.files }}
          CHANGED_COUNT: ${{ steps.changed.outputs.count }}
        run: |
          PROMPT="Review this Pull Request.

          <!-- 【变化】4、增加了结构化的审查 prompt -->
          ## Changed Files (${CHANGED_COUNT} files)
          ${CHANGED_FILES}

          <!-- 【变化】5、增加了关键问题检测逻辑 -->
          ## Review Focus
          1. Code Quality: clean code, naming, DRY
          2. Bugs: edge cases, error handling
          3. Security: input validation, secrets, injection
          4. Performance: inefficient code

          ## Output Format

          ### Summary
          [1-2 sentence overview]

          ### Issues Found
          - 🔴 Critical: <file>:<line> — <description>
          - 🟡 Warning: <file>:<line> — <description>
          - 🔵 Suggestion: <file>:<line> — <description>

          <!-- 【要点】6、Verdict 用唯一 sentinel token（request_changes），
          不能用“Approved / Needs Changes / Request Changes”这种单词列表，
          否则 grep 会把 prompt 模板里列出的选项当成实际结论，几乎每次都误判。
           -->
          ### Verdict
          Output EXACTLY ONE sentinel token on its own line — do not echo
          the option list:
          <VERDICT>approved</VERDICT>
          <VERDICT>needs_changes</VERDICT>
          <VERDICT>request_changes</VERDICT>"

          # 【要点】7、claude 失败时显式报错，不要让 set -eo pipefail 静默挂掉。
          if ! claude -p "$PROMPT" \
            --output-format json \
            --max-turns 10 \
            --allowedTools Read,Grep,Glob > review.json 2> claude.err; then
            echo "::error::Claude command failed"
            cat claude.err
            exit 1
          fi

          if ! jq empty review.json 2>/dev/null; then
            echo \"::error::review.json is not valid JSON\"
            cat review.json
            exit 1
          fi

          jq -r '.result // empty' review.json > review.md
          if [ ! -s review.md ]; then
            echo \"::error::Claude returned empty result\"
            cat review.json
            exit 1
          fi

      # 【要点】8、下游全部从 review.md 文件读，不通过 ${{ steps.review.outputs.result }} 把多行 markdown 拼进 shell / JS。
      - name: Post Review Comment
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const review = fs.readFileSync('review.md', 'utf8');
            // 把 verdict sentinel 从 PR 评论里隐藏，纯展示用
            const visible = review.replace(/<VERDICT>[^<]+<\/VERDICT>/g, '').trim();
            const body = [
              '## 🤖 Claude Code Review',
              '',
              visible,
              '',
              '---',
              '*Automated review by Claude Code*'
            ].join('\n');
            await github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body,
            });

      # 【变化】9、如果 Claude 给出 request_changes 结论，工作流将以失败状态退出，从而阻止 PR 合并。
      - name: Enforce verdict
        run: |
          # 用唯一 sentinel token 判断，不会和 prompt 模板字符串冲突
          if grep -q "<VERDICT>request_changes</VERDICT>" review.md; then
            echo "::error::Code review verdict: request_changes"
            exit 1
          fi
          if grep -q "<VERDICT>needs_changes</VERDICT>" review.md; then
            echo "::warning::Code review verdict: needs_changes (non-blocking)"
          fi
```

**安全与成本控制**

在 CI/CD 中运行 AI 代理，安全是绕不开的话题。根据 [eesel.ai](https://www.eesel.ai/blog/claude-code-automation) 的指南，在 CI/CD 中运行 Claude Code 时应该限制权限。最小权限原则的核心思想是：只给 Claude 完成任务所需的最少权限，不多给一分。

```bash
# 对于只读审查任务，只允许 Read、Grep、Glob 三个工具就够了
claude -p "分析代码" --allowedTools Read,Grep,Glob

# 如果不需要执行任意命令，明确禁用 Bash 工具
claude -p "任务" --disallowedTools Bash

# 对于简单任务，限制执行轮次以防止无限循环
claude -p "快速任务" --max-turns 3
```

API Key 是访问 Claude 服务的凭证，泄露它意味着别人可以用你的账号消耗 API 额度。在 CI/CD 配置中，永远不要硬编码 API Key，而是使用平台提供的 Secrets 管理机制。

```yaml
# 不要这样做
env:
  ANTHROPIC_API_KEY: "sk-ant-xxx"  # 硬编码

# 正确做法
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

每次 CI 运行都会消耗 API tokens，而 tokens 意味着真金白银。在高频迭代的项目中，如果每次推送都触发完整的 AI 审查，成本可能会快速累积。通过合理的触发条件和并发控制，可以在保持审查覆盖率的同时有效控制成本。

```yaml
# 只在特定条件下运行
on:
  pull_request:
    types: [opened]  # 不包括 synchronize，减少运行次数
    paths:
      - 'src/**'     # 只在 src 目录变更时运行

# 限制并发
concurrency:
  group: claude-${{ github.event.pull_request.number }}
  cancel-in-progress: true
```

## 其它 CI 平台集成

虽然 GitHub Actions 有官方支持，但 Headless 模式可以在任何 CI 平台上工作。因为 Headless 模式的本质就是命令行调用——只要平台能运行 npm install 和  claude -p，就能集成。下面是三个主流 CI 平台的配置示例。

GitLab CI：GitLab CI 使用 `.gitlab-ci.yml` 配置文件，语法与 GitHub Actions 的 YAML 不同但概念相似。

```yaml
claude-review:
  image: node:20
  script:
    - npm install -g @anthropic-ai/claude-code
    - claude -p "Review the changes in this MR" --output-format text
  variables:
    # 注意变量引用方式的差异：
    # GitLab 使用 $VARIABLE_NAME，而不是 GitHub 的  ${{ secrets.VARIABLE_NAME }}
    ANTHROPIC_API_KEY: $ANTHROPIC_API_KEY
  only:
    - merge_requests
```

CircleCI：CircleCI 使用 `config.yml`，放在 `.circleci/` 目录下。它的配置结构是 jobs -> steps，与 GitHub Actions 的 jobs -> steps 概念对应。

```yaml
version: 2.1
jobs:
  review:
    docker:
      - image: cimg/node:20.0
    steps:
      - checkout
      - run:
          name: Install Claude Code
          command: npm install -g @anthropic-ai/claude-code
      - run:
          name: Run Review
          command: |
            claude -p "Review this code" --output-format text
          environment:
            ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
```

Jenkins：Jenkins 使用 Groovy DSL 定义 Pipeline，风格与上面两个 YAML 驱动的系统截然不同。但核心逻辑是一样的，安装 Claude Code，设置环境变量，运行 headless 命令。

```Groovy 
pipeline {
    agent any
    environment {
        ANTHROPIC_API_KEY = credentials('anthropic-api-key')
    }
    stages {
        stage('Review') {
            steps {
                sh 'npm install -g @anthropic-ai/claude-code'
                sh 'claude -p "Review this code" --output-format text'
            }
        }
    }
}
```

# 20｜有章可循：Rules 规则系统深度剖析

上一讲我们学习了 Headless 模式，Headless 解决了没有人盯着的问题，但也让一个追问变得更加尖锐，没人盯着的时候，谁来定规矩？

这就引出了今天的主题——规则系统。

**两种规则，两个世界**

很多同学把两种“规则“搞混了。有人问：“rules 目录里能不能禁止 Claude 执行 rm 命令？”答案是不能，那是权限规则的事；也有人问：“settings.json 里能不能告诉 Claude 用 TypeScript 写代码？”答案也是不能，那是指令规则的事。

这两种规则解决的是完全不同的问题。今天我们就来把 Claude Code 中所有规则的全貌讲清楚。

Claude Code 中的“规则”分布在两个完全不同的层面：

![img](https://static001.geekbang.org/resource/image/b5/4e/b5e2690885bdd4edf4172a16d24a494e.jpg?wh=3145x1485)

指令规则是 Claude 的认知约束，权限规则是客户端的行为约束。

## 指令规则：.claude/rules/ 完全指南

`.claude/rules/` 目录下的每个 .md 文件，本质上就是一段会被注入 System Prompt 的文本。它和 CLAUDE.md 没有本质区别，唯一的结构化优势是，它可以按主题拆分成多个文件，还支持条件加载。

```
.claude/
└── rules/
    ├── typescript.md       # TypeScript 编码规范
    ├── testing.md          # 测试规范（有 paths 条件）
    ├── api-design.md       # API 设计规范（有 paths 条件）
    └── security.md         # 安全规范（全局生效）
```

**两种加载模式**

这是 rules 最重要的设计细节，也是最多人搞错的地方。

- 模式一：全局加载（无 paths 字段）

```markdown
# security.md —— 没有 YAML 头部，或有头部但不含 paths

## 安全规范
- 不在代码中硬编码密码或 API Key
- 所有用户输入必须做 sanitize
- SQL 查询使用参数化，不拼接字符串
```

这种 rule 在会话启动时就加载进上下文，行为和写在 CLAUDE.md 里完全一样。拆出来的唯一好处是文件组织更清晰。

- 模式二：条件加载（有 paths 字段）

```markdown
---
paths:
  - "src/**/*.test.ts"
  - "tests/**/*.ts"
---

# 测试规范

## 命名
- 单元测试: `*.test.ts`
- 集成测试: `*.integration.test.ts`

## 结构
使用 Arrange-Act-Assert 模式
```

这种 rule 在会话启动时不加载。只有当 Claude 读取或编辑匹配  paths 模式的文件时，才会被注入上下文。

但是注意，一旦加载，就不会卸载。如果你在会话中先编辑了一个测试文件，testing.md 被加载了，然后你去改 CSS，testing.md 仍然在上下文里。

```
会话开始
  → 加载全局 rules（无 paths 的）
  → testing.md 未加载 ✗

用户：帮我改一下 src/utils/format.ts
  → Claude 读取 format.ts
  → paths 不匹配，testing.md 仍未加载 ✗

用户：帮我给这个函数写个测试
  → Claude 创建 src/utils/format.test.ts
  → paths 匹配！testing.md 加载 ✓

用户：再帮我改一下 CSS
  → Claude 读取 styles.css
  → testing.md 仍在上下文中 ✓（不会卸载）
```

**什么时候该从 CLAUDE.md 拆到 rules？**

判断标准很简单，我们可以根据长度决策。

```
CLAUDE.md 的总长度如何？
│
├── < 200 行 → 不用拆，CLAUDE.md 一把梭
│               简单就是好，不要为了组织而组织
│
├── 200-500 行 → 考虑拆
│   └── 有没有"只和特定文件类型相关"的内容？
│       ├── 有 → 拆出来，加 paths
│       │       （如测试规范、前端规范、API 规范）
│       └── 没有 → 拆出来，不加 paths
│                 （纯粹为了文件组织清晰）
│
└── > 500 行 → 必须拆
                CLAUDE.md 太长会稀释重要信息的权重
                把领域规范拆到 rules，CLAUDE.md 只留核心约定
```

**实战：一个全栈项目的 rules 拆分**

假设你有一个 React + Express + PostgreSQL 的全栈项目，CLAUDE.md 膨胀到了 600 行（示例参考）。我们如何拆分呢？

拆分后的 CLAUDE.md（精简到 80 行以内）

```
# 项目概述
全栈 TypeScript 项目。前端 React 18 + Tailwind，后端 Express + Prisma + PostgreSQL。

# 命令
- `pnpm dev` — 启动前后端开发服务器
- `pnpm test` — 运行全部测试
- `pnpm lint` — ESLint + Prettier 检查
- `pnpm db:migrate` — 执行数据库迁移

# 核心约定
- 包管理器用 pnpm，不用 npm 或 yarn
- commit message 用 conventional commits 格式
- 所有 API 返回 { success: boolean, data?: T, error?: string }
- 环境变量通过 .env 管理，不硬编码

# 详细规范
领域规范见 .claude/rules/ 目录，按文件类型自动加载。
```

拆分出的 rules 文件如下：

`.claude/rules/frontend.md`

```markdown
---
paths:
  - "src/components/**"
  - "src/pages/**"
  - "src/hooks/**"
---

# 前端规范

## 组件
- 函数式组件，不用 class 组件
- Props 用 interface 定义，命名 XxxProps
- 组件文件和样式文件同名同目录

## 状态管理
- 局部状态用 useState
- 跨组件状态用 Zustand
- 服务端状态用 TanStack Query

## 样式
- Tailwind 优先，复杂样式用 CSS Modules
- 响应式断点：sm(640) md(768) lg(1024) xl(1280)
```

`.claude/rules/backend.md`

```markdown
---
paths:
  - "server/**"
  - "src/api/**"
  - "prisma/**"
---

# 后端规范

## 路由
- RESTful 风格，资源名用复数
- 路由文件放 server/routes/，一个资源一个文件

## 数据库
- 所有查询通过 Prisma ORM，不写原生 SQL
- 迁移文件不手动编辑
- 关联查询用 include，不用多次查询

## 错误处理
- 业务错误抛 AppError(code, message)
- 统一在 errorHandler 中间件中捕获
```

`.claude/rules/testing.md`

```markdown
---
paths:
  - "**/*.test.ts"
  - "**/*.test.tsx"
  - "**/*.spec.ts"
---

# 测试规范

## 工具
- 单元测试：Vitest
- 组件测试：Testing Library
- E2E：Playwright

## 结构
- Arrange-Act-Assert 模式
- 每个 describe 对应一个函数或组件
- Mock 外部依赖，不 mock 内部模块

## 覆盖率
- 业务逻辑 > 80%
- 工具函数 > 90%
- UI 组件关注交互，不关注快照
```

`.claude/rules/security.md`（注意，没有 paths，全局生效）

```markdown
# 安全规范

- 用户输入在使用前必须 validate + sanitize
- SQL 参数化（Prisma 默认做到了）
- XSS 防护：不使用 dangerouslySetInnerHTML
- CORS 只允许白名单域名
- 敏感信息（API Key、数据库密码）只放 .env
- 认证 token 用 httpOnly cookie，不存 localStorage
```

拆完之后，CLAUDE.md 从 600 行变成 80 行，但规范一条都没少——只是按需加载了。

> 还有一个容易忽略的问题：rules 文件之间不要互相矛盾。CLAUDE.md 说"用 2 空格缩进"，frontend.md 说"用 4 空格缩进"——Claude 碰到这种矛盾会很困惑，行为不可预测。全局规范放一个地方，领域规范只写领域特有的。
>

## 权限规则：行为管控的硬约束

权限规则写在 `.claude/settings.json` 或 `.claude/settings.local.json` 中，由 Claude Code 客户端在工具调用前硬拦截。Claude 根本看不到这些规则——它只知道某个操作被允许了或被拒绝了。

基本结构如下：

```markdown
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

评估顺序：deny → ask → allow。 第一个匹配的规则胜出，deny 总是优先。就算你在 allow 里写了 `Bash(rm -rf *)`，如果 deny 里也有这条，deny 赢。

权限规则所能控制的范围如下：

```
  Bash(command pattern)      → 控制 Shell 命令的执行
  Read(file pattern)         → 控制文件的读取
  Edit(file pattern)         → 控制文件的编辑
  Write(file pattern)        → 控制文件的创建

  WebFetch(domain:pattern)   → 控制网页抓取的域名范围
  WebSearch                  → 控制是否允许网络搜索

  mcp__server__tool          → 控制 MCP 工具的使用
  Skill(skill-name)          → 控制 Skill 的调用
  Task(agent-name)           → 控制子代理的调用
```

权限配置可以在四个层级设置，高优先级覆盖低优先级。

![img](https://static001.geekbang.org/resource/image/d1/9f/d1264e131a814c20bbbc5e2a87e7809f.jpg?wh=3327x1839)

关键规则：高层级的 deny 不可被低层级覆盖。 如果组织策略禁止了 `Bash(curl *)`，项目配置和个人配置都无法解除这个限制。这是企业级安全管控的基石。

**权限规则在扩展机制中的渗透**

权限规则不仅存在于 settings.json 中，它还渗透到了 Claude Code 的各个扩展机制里。

1、Skills 中的 allowed-tools，Skill 被触发时只能使用白名单中的工具。

```markdown
---
name: code-reviewing
description: Review code for quality and security issues
allowed-tools:
  - Read
  - Grep
  - Glob
---
```

2、Sub-Agents 中的 tools，子代理的工具集更加严格，甚至拿不到主对话的 CLAUDE.md。

```
---
name: code-reviewer
tools: Read, Grep, Glob
model: sonnet
---
```

3、Hooks 中的动态拦截，最灵活的权限控制，可以根据动态条件决定是否放行。

```markdown
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

这三者共同构成了权限纵深防御体系。

```
工具调用请求
  ↓
第一关：settings.json 的 deny 规则
  → 命中？直接拦截，不可绕过
  ↓
第二关：Hooks 的 PreToolUse 拦截
  → 脚本返回非零？拦截，可自定义逻辑
  ↓
第三关：Skill/Agent 的 allowed-tools 限制
  → 不在白名单？拦截
  ↓
第四关：settings.json 的 allow 规则 / 用户交互审批
  → 在白名单？自动放行
  → 不在任何规则中？弹窗询问用户
  ↓
工具执行
```

## **两种规则的协同**

让我们用一个真实场景把两种规则串起来：你的团队有一个支付服务项目，既需要编码规范（指令规则），也需要安全管控（权限规则）。

**指令规则部分**

`CLAUDE.md`（精简版，~60 行）

```markdown
# 支付服务
Node.js + TypeScript + Stripe API，处理用户支付流程。

# 命令
- `pnpm dev` — 启动开发服务器
- `pnpm test` — 运行测试
- `pnpm lint` — 代码检查

# 核心约定
- 所有金额用 cents（整数），不用浮点数
- 日志必须包含 requestId，便于追踪
- 不在日志中打印卡号、CVV 等敏感信息
```

`.claude/rules/stripe.md`

```markdown
---
paths:
  - "src/payments/**"
  - "src/webhooks/**"
---

# Stripe 集成规范

## Webhook 处理
- 始终验证 webhook 签名（stripe.webhooks.constructEvent）
- 幂等处理：用 event.id 去重
- 先返回 200，再异步处理业务逻辑

## 错误处理
- StripeCardError → 返回用户友好消息
- StripeRateLimitError → 指数退避重试
- 其他 Stripe 错误 → 记录日志 + 告警
```

**权限规则部分**

`.claude/settings.json`（团队共享）

```markdown
{
  "permissions": {
    "allow": [
      "Bash(pnpm *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Read",
      "Glob",
      "Grep"
    ],
    "deny": [
      "Bash(curl *)",
      "Bash(wget *)",
      "Read(./.env)",
      "Read(./.env.*)",
      "Edit(./.env)",
      "Edit(./.env.*)",
      "Bash(rm -rf *)",
      "Bash(* --force)",
      "Bash(stripe *)"
    ]
  }
}
```

注意这个 deny 列表的设计意图：

- 禁止 `curl/wget`：防止 Claude 自行调用外部 API（包括 Stripe API）
- 禁止读写 `.env`：保护 Stripe Secret Key 等敏感配置
- 禁止 `stripe *`：防止 Claude 用 Stripe CLI 直接操作生产环境
- 禁止 `rm -rf` 和 `--force`：防止破坏性操作

两种规则各司其职， 指令规则告诉 Claude：“处理 webhook 要验签、金额用 cents”——这是认知层面的约束，让 Claude 写出正确的代码。权限规则告诉客户端：“不许读 .env、不许执行 stripe CLI”——这是行为层面的约束，从系统层面堵住安全漏洞。

即使 Claude “忘记”了指令规则中不在日志中打印卡号的要求，权限规则也能确保它无法读取 .env 中的 Stripe Key。纵深防御，不依赖单一层面。

> 这个支付服务的例子是一个做 FinTech 的学员真实碰到的问题。
>
> 他一开始只在 CLAUDE.md 里写了"不要在日志中打印敏感信息"，结果 Claude 有一次调试时把完整的 Stripe webhook payload 打进了日志，里面有卡号后四位。后来他加了权限规则禁止读 .env，又加了 Hooks 在 Bash 执行前检查输出中是否包含 sk_live_前缀。三层防护叠在一起，再也没出过问题。安全从来不靠一道墙，靠的是纵深。

## 架构定位与最佳实践

**Rules 在架构中的定位**

- 指令层有指令规则（`CLAUDE.md`、`.claude/rules/`）
- 能力层有能力规则（Skills 的 `allowed-tools`、Agent 的 `tools`）
- 管控层有权限规则（`settings.json`、Hooks、CLI 参数）

![image-20260521200043975](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202605212001009.png)

“规则”不是架构中的一个方块，而是渗透在每一层中的横切关注点。

这就像安全不是软件中的一个模块，而是贯穿所有模块的设计原则。这里我也顺便说明一下 Rules 的正确学习路径。

| 讲数              | 说明                                    |
| ----------------- | --------------------------------------- |
| 第 2 讲 Memory    | 学指令规则（CLAUDE.md、.claude/rules/） |
| 第 18 讲 Tools    | 学权限规则（settings.json permissions） |
| 第 9 讲 Skills    | 学能力规则（allowed-tools）             |
| 第 3 讲 SubAgents | 学隔离规则（tools / disallowedTools）   |
| 第 15 讲 Hooks    | 学动态规则（PreToolUse 拦截）           |

每一讲都在从自己的角度讲述 Rules 的一个切面。这一讲的价值，就是帮你把这些碎片拼成全景图。

**最佳实践**

rules 目录的标准结构：

```
.claude/
├── settings.json          ← 权限规则（团队共享）
├── settings.local.json    ← 个人权限覆盖（.gitignore）
└── rules/
    ├── coding.md          ← 全局编码规范（无 paths）
    ├── frontend.md        ← 前端规范（paths: src/components/**)
    ├── backend.md         ← 后端规范（paths: server/**)
    ├── testing.md         ← 测试规范（paths: **/*.test.*)
    └── security.md        ← 安全规范（无 paths，全局生效）
```

权限规则的安全基线（适用于大多数团队）：

```markdown
{
  "permissions": {
    "allow": [
      "Read",
      "Glob",
      "Grep",
      "Bash(npm run *)",
      "Bash(pnpm *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(node *)",
      "Bash(npx *)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(* --force)",
      "Bash(curl *)",
      "Bash(wget *)",
      "Read(./.env)",
      "Read(./.env.*)",
      "Edit(./.env)",
      "Edit(./.env.*)",
      "Read(~/.ssh/*)",
      "Read(~/.aws/*)"
    ]
  }
}
```

这个模版你要根据你的项目调整。如果用 Python 就把 `pnpm` 换成 `pip/uv`；如果需要 Claude 访问特定 API，就在 allow 中加 `WebFetch(domain:your-api.com)`。

**常见错误**

```
错误 1: 在 rules/*.md 中写权限控制
  ❌ .claude/rules/security.md 里写："禁止执行 rm -rf 命令"
  → Claude 可能遵守，也可能忘记。这是软约束。
  ✅ 在 settings.json 的 deny 中写：Bash(rm -rf *)
  → 客户端硬拦截，Claude 连尝试的机会都没有。

错误 2: 在 settings.json 中写编码规范
  ❌ settings.json 无法表达"用 TypeScript 写代码"这样的指令
  → 它只能控制 allow/deny，不能传递知识
  ✅ 在 CLAUDE.md 或 rules/*.md 中写编码规范

错误 3: rules 文件之间互相矛盾
  ❌ coding.md 说"缩进用 2 空格"，frontend.md 说"缩进用 4 空格"
  → Claude 会困惑，行为不可预测
  ✅ 全局规范放 coding.md，领域规范只写领域特有的

错误 4: paths 写得太宽或太窄
  ❌ paths: ["**/*"] → 等于没写 paths，不如去掉
  ❌ paths: ["src/components/UserProfile.tsx"] → 太窄，基本不会触发
  ✅ paths: ["src/components/**"] → 合理粒度

错误 5: 以为子代理能继承 rules
  ❌ 期望子代理自动遵守 .claude/rules/ 中的规范
  → 子代理看不到主对话的任何记忆文件
  ✅ 把关键规范写进子代理的 Markdown body 或通过 Skills 注入
```

# 21｜登堂入室 ：通过Agent SDK 掌控 Claude Code

今天我们要更进一步，学习 Claude Agent SDK。

## 什么是 Agent SDK

Claude Agent SDK 是对 Claude Code 这个 Agent 系统的完整封装。你通过 SDK 调用的不是一个简单的文本生成接口，而是一个完整的 Agent 循环——Claude 会自主决定使用哪些工具、读取哪些文件、执行哪些命令，然后把结果返回给你。

简单来说，这三种方式形成了一个递进关系：CLI 是手动操作，Headless 是自动化脚本，SDK 是可编程集成。每一步都在降低人工干预的程度，提升集成的灵活性。

| 方式            | 适用场景               |
| --------------- | ---------------------- |
| Claude Code CLI | 终端交互、脚本自动化   |
| Headless 模式   | CI/CD、Pre-commit      |
| Agent SDK       | 应用集成、自定义 Agent |

**SDK 能力一览**

下面这张表列出了 Agent SDK 赋予你的全部能力。

| 能力     | 说明                     |
| -------- | ------------------------ |
| 文件操作 | Read、Write、Edit 文件   |
| 代码执行 | 运行 Bash 命令、执行脚本 |
| 内容搜索 | Grep、Glob 搜索          |
| 网络访问 | WebFetch、WebSearch      |
| MCP 扩展 | 连接外部工具和服务       |
| 会话管理 | 保持上下文、恢复会话     |
| 权限控制 | 细粒度的工具权限管理     |
| Hooks    | 工具执行前后的拦截和处理 |

**安装与环境配置**

在开始编写代码之前，你需要安装 SDK 并配置好环境。这个过程很简单，但有几个关键点需要注意。

Python 安装要求 Python 3.10 及以上版本。之所以有这个版本要求，是因为 SDK 大量使用了async/await 语法和  match/case 模式匹配等现代 Python 特性。如果你的系统 Python 版本较低，建议使用  pyenv 或  conda 管理多个 Python 版本。

```bash
# 要求 Python 3.10+
pip install claude-agent-sdk
```

安装完成后，用一段简单的代码验证安装是否成功：

```python
from claude_agent_sdk import query
print("Claude Agent SDK installed successfully!")
```

SDK 需要 Anthropic API Key 才能运行，最常见的配置方式是通过环境变量：

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

**两种使用方式**

Agent SDK 提供了两种使用方式，适用于不同场景。

1、query() 函数：简洁高效

query() 是最简单的方式，适合轻量级用例。它接收一个 Prompt 字符串，返回一个异步迭代器，你可以逐条接收 Agent 产生的消息。整个过程不需要手动管理连接、配置选项或处理会话状态，SDK 帮你搞定一切。

这种设计的好处是显而易见的：当你只想快速验证一个想法、写一个脚本、或者做一次性的分析时，不需要写二十行初始化代码。一个函数调用就够了。

```python
from claude_agent_sdk import query
import asyncio

async def main():
    # 简单查询
    async for message in query("解释什么是递归"):
        if message.type == "text":
            print(message.text)

asyncio.run(main())
```

query() 的特点是：

- 一行代码即可调用
- 自动处理工具调用循环
- 适合单次、简单的任务

2、ClaudeSDKClient 类：完整控制

当你需要更精细的控制时，比如限制 Agent 只能使用特定工具、设置最大执行轮次、管理多轮会话，就需要使用  ClaudeSDKClient。它提供了完整的配置能力，让你可以像搭积木一样组合 Agent 的行为。

与开箱即用的 query() 不同，ClaudeSDKClient 要求你显式地创建客户端、配置选项、管理连接生命周期。这种显式性是刻意为之的，在生产环境中，你需要明确知道 Agent 能做什么、不能做什么、在什么条件下停止。隐式的默认值在生产中往往是 Bug 的温床。

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
import asyncio

async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Grep", "Glob"],
        max_turns=10,
        permission_mode="plan"  # 只读模式
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("分析 src/ 目录的代码结构")

        async for message in client.receive_response():
            if message.type == "text":
                print(message.text)
            elif message.type == "tool_use":
                print(f"Using tool: {message.tool_name}")

asyncio.run(main())
```

ClaudeSDKClient的特点是：

- 完整的配置控制
- 支持自定义工具
- 支持 Hooks
- 支持会话恢复

选择哪种方式取决于你的具体场景。下面这张表可以帮你快速判断。

| 场景               | 推荐方式        |
| ------------------ | --------------- |
| 简单查询、快速原型 | query()         |
| 需要自定义工具     | ClaudeSDKClient |
| 需要 Hooks 拦截    | ClaudeSDKClient |
| 需要会话管理       | ClaudeSDKClient |
| 需要精细的权限控制 | ClaudeSDKClient |
| 生产级应用         | ClaudeSDKClient |

在实际项目中，常见的演进路径是先用 query() 快速验证想法，然后在功能成型后迁移到  ClaudeSDKClient 进行工程化。两种方式的消息格式完全兼容，迁移成本很低。

**ClaudeAgentOptions 配置详解**

ClaudeAgentOptions 是控制 Agent 行为的核心配置类。你可以把它理解为 Agent 的“说明书”，它告诉 Agent 该用什么模型、能用什么工具、最多跑几轮、在什么目录下工作。每一个配置项都会直接影响 Agent 的行为和成本。

下面是完整的配置项。

```python
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    # === 模型选择(常用) ===
    model="sonnet",  # "sonnet" | "opus" | "haiku"

    # === 工具控制(常用) ===
    allowed_tools=["Read", "Write", "Bash", "Grep", "Glob"],
    disallowed_tools=["Task"],

    # === 权限模式(常用) ===
    permission_mode="default",  # "default" | "acceptEdits" | "plan" | "bypass"

    # === 执行控制(常用) ===
    max_turns=20,
    cwd="/path/to/project",

    # === 输出格式 ===
    output_format="stream-json",  # "text" | "json" | "stream-json"

    # === 会话管理 ===
    continue_conversation=True,
    resume="session-id",

    # === 系统提示 ===
    system_prompt="You are a helpful coding assistant.",

    # === MCP 服务器 ===
    mcp_servers={
        "my-server": {...}
    },

    # === Hooks ===
    hooks={
        "PreToolUse": [...],
        "PostToolUse": [...]
    }
)
```

**权限模式详解**

选择权限模式时，问自己一个问题：如果 Agent 做了一件错事，最坏的结果是什么？如果最坏结果“改错了一个文件，我  git checkout 恢复一下”，那可以放宽权限；如果最坏结果是“删除了生产数据库”，那必须严格控制。

| 模式        | 说明                     | 适用场景           |
| ----------- | ------------------------ | ------------------ |
| default     | 默认模式，危险操作需确认 | 交互式开发         |
| acceptEdits | 自动接受文件编辑         | 自动化脚本         |
| plan        | 只读模式，不执行修改     | 代码分析、审查     |
| bypass      | 跳过所有权限检查         | 完全自动化（慎用） |

下面的代码展示了两种典型场景下的权限配置。

```python
# 代码审查只需要读取代码，不需要任何修改能力，所以用 plan 模式加上只读工具
options = ClaudeAgentOptions(
    permission_mode="plan",
    allowed_tools=["Read", "Grep", "Glob"]
)

# 自动修复则需要编辑文件的能力，但不需要执行任意命令，所以用 acceptEdits 模式搭配  Read/Write/Edit 工具
options = ClaudeAgentOptions(
    permission_mode="acceptEdits",
    allowed_tools=["Read", "Write", "Edit"]
)
```

你可以精确控制 Agent 能使用哪些工具。SDK 提供了两种控制方式，白名单（allowed_tools）和黑名单（disallowed_tools）。在安全敏感的场景中，推荐使用白名单，明确列出 Agent 能用的工具，而不是试图列出所有它不能用的工具。

内置工具列表：

| 工具      | 功能       |
| --------- | ---------- |
| Read      | 读取文件   |
| Write     | 写入文件   |
| Edit      | 编辑文件   |
| Bash      | 执行命令   |
| Grep      | 搜索内容   |
| Glob      | 文件匹配   |
| Task      | 创建子代理 |
| WebFetch  | 获取网页   |
| WebSearch | 搜索网络   |

下面展示了三种不同的工具限制策略。

```python
# 只允许读取操作
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep", "Glob"]
)

# 禁用危险工具
options = ClaudeAgentOptions(
    disallowed_tools=["Bash", "Write"]
)

# 限制 Bash 命令（只允许 git 和 npm）
options = ClaudeAgentOptions(
    allowed_tools=["Bash(git:*)", "Bash(npm:*)"]
)
```

**消息类型与响应处理**

Agent 不是一次性返回结果的——它是一个异步流，在执行过程中会源源不断地产生五种类型的消息。

- text 是 Claude 生成的文本内容，比如分析结论、代码解释；
- tool_use 表示 Agent 正在调用某个工具；
- tool_result 是工具执行后返回的结果；
- error 表示执行过程中遇到了错误；
- result 是最终的汇总消息，包含执行时间、成本等元数据。

```python
async for message in client.receive_response():
    match message.type:
        case "text":
            # 文本响应
            print(message.text)

        case "tool_use":
            # 工具调用（Agent 正在使用工具）
            print(f"Tool: {message.tool_name}")
            print(f"Input: {message.tool_input}")

        case "tool_result":
            # 工具执行结果
            print(f"Result: {message.result}")

        case "error":
            # 错误信息
            print(f"Error: {message.error}")

        case "result":
            # 最终结果（任务完成）
            print(f"Final: {message.result}")
            print(f"Cost: ${message.total_cost_usd}")
```

当任务完成时，你会收到一个  result 类型的消息。这是整个 Agent 执行过程的“成绩单”，包含了你在生产环境中最关心的信息：这次调用花了多少钱、用了多少 Token、跑了多少轮、耗时多长。这些数据是你做成本监控和性能优化的基础。

```json
{
    "type": "result",
    "subtype": "success",
    "session_id": "abc123",
    "is_error": False,
    "num_turns": 5,
    "duration_ms": 12000,
    "duration_api_ms": 10000,
    "total_cost_usd": 0.05,
    "usage": {
        "input_tokens": 5000,
        "output_tokens": 2000
    },
    "result": "任务完成..."
}
```

在实际项目中，你通常不会只是把消息打印到终端，你需要把它们收集起来，形成结构化的结果，供后续的业务逻辑使用。

下面这个模式是项目中反复验证过的“最佳实践”：把所有消息分类收集到一个字典中，最后返回完整的结构化结果。

```python
async def run_agent(prompt: str) -> dict:
    """运行 Agent 并返回结构化结果"""

    result = {
        "output": [],
        "tools_used": [],
        "metadata": {}
    }

    async with ClaudeSDKClient(options) as client:
        await client.query(prompt)

        async for msg in client.receive_response():
            if msg.type == "text":
                result["output"].append(msg.text)

            elif msg.type == "tool_use":
                result["tools_used"].append({
                    "tool": msg.tool_name,
                    "input": msg.tool_input
                })

            elif msg.type == "result":
                result["metadata"] = {
                    "session_id": msg.session_id,
                    "duration_ms": msg.duration_ms,
                    "cost_usd": msg.total_cost_usd,
                    "turns": msg.num_turns
                }

            elif msg.type == "error":
                result["error"] = msg.error

    return result
```

这个模式的好处是，调用方可以直接从 result["output"] 获取 Agent 的文本输出，从 result["tools_used"] 获取工具调用记录（用于审计），从 result["metadata"] 获取成本和性能数据（用于监控）。

**会话管理**

你让 Agent 分析一个项目的代码结构，分析完之后想让它基于分析结果生成文档。如果没有会话管理，Agent 在第二次调用时完全不记得它之前分析过什么。因此，通过会话管理保持对话上下文，这对于长时间运行的任务或需要分阶段完成的工作特别有用。

在同一个 ClaudeSDKClient 实例中，你可以进行多轮对话。Agent 会自动记住之前的上下文，每次新的 query() 调用都是在之前的上下文基础上继续，而不是从零开始。

```python
async with ClaudeSDKClient() as client:
    # 第一次查询
    await client.query("创建一个 Python 项目结构")
    async for msg in client.receive_response():
        print(msg)

    # 获取会话 ID
    session_id = client.session_id
    print(f"Session ID: {session_id}")

    # 继续对话（Agent 记得之前的上下文）
    await client.query("在项目中添加一个 requirements.txt 文件")
    async for msg in client.receive_response():
        print(msg)
```

有时候你需要在不同的程序运行之间保持对话连续性。比如，你的 Agent 在一次 CI 运行中分析了代码，你想在下一次 CI 运行中让它继续从上次的结论出发。这时候就需要保存 session_id，然后在下次启动时通过 resume 参数恢复会话。

```python
# 保存会话 ID
saved_session_id = "abc123"

# 稍后恢复
options = ClaudeAgentOptions(
    resume=saved_session_id
)

async with ClaudeSDKClient(options=options) as client:
    # 在之前的上下文中继续
    await client.query("继续刚才的任务")
    async for msg in client.receive_response():
        print(msg)
```

下面是一个完整的会话持久化方案。它把 session_id 保存到本地 JSON 文件中，这个方案适用于开发环境和小型项目。

> 在生产环境中，你可能需要把会话 ID 存到 Redis 或数据库中，并设置过期时间——长时间不活跃的会话应该被清理，否则会累积大量上下文，导致 Token 消耗急剧增加。
>

```python
import json
from pathlib import Path

SESSIONS_FILE = Path("sessions.json")

def save_session(name: str, session_id: str):
    """保存会话"""
    sessions = {}
    if SESSIONS_FILE.exists():
        sessions = json.loads(SESSIONS_FILE.read_text())
    sessions[name] = session_id
    SESSIONS_FILE.write_text(json.dumps(sessions, indent=2))

def load_session(name: str) -> str | None:
    """加载会话"""
    if not SESSIONS_FILE.exists():
        return None
    sessions = json.loads(SESSIONS_FILE.read_text())
    return sessions.get(name)

# 使用
async def main():
    # 尝试恢复会话
    session_id = load_session("project-review")

    options = ClaudeAgentOptions(
        resume=session_id  # None 则开始新会话
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("继续代码审查")

        async for msg in client.receive_response():
            if msg.type == "result":
                # 保存会话以便下次恢复
                save_session("project-review", msg.session_id)
```

<!-- 20260610 -->

## 实战项目——代码分析 Agent

理论讲了不少，需要结合实战消化一下，让我们动手构建一个完整的代码分析 Agent。这个项目综合运用了前面讲过的所有知识点：ClaudeSDKClient 的创建和配置、权限模式的选择、工具白名单的设置、消息类型的处理、元数据的收集。

我们的项目需求是，构建一个 Agent，能够完成以下任务。

1. 扫描指定目录的代码
2. 识别项目结构和技术栈
3. 发现潜在问题
4. 生成分析报告

这是一个典型的“只读分析”场景——Agent 只需要读取代码，不需要修改任何文件。因此我们使用  plan 权限模式，配合  Read/Grep/Glob 三个只读工具。这样即使 Agent 的 Prompt 被注入了恶意指令（比如“删除所有文件”），它也没有能力执行。

下面是完整的代码实现。代码分为三个部分：analyze_codebase() 函数负责调用 Agent 并收集结果，format_report() 函数负责把结果格式化为可读的报告，main() 函数负责处理命令行参数和文件输出。

```
#!/usr/bin/env python3
"""
代码分析 Agent

使用 Claude Agent SDK 构建一个自动代码分析工具。
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions


async def analyze_codebase(directory: str) -> dict:
    """
    使用 Claude Agent SDK 分析代码库

    Args:
        directory: 要分析的目录路径

    Returns:
        包含分析结果的字典
    """
    # 配置 Agent 选项
    options = ClaudeAgentOptions(
        # 只允许读取操作，确保安全
        allowed_tools=["Read", "Grep", "Glob"],

        # 使用只读模式
        permission_mode="plan",

        # 限制执行轮次
        max_turns=25,

        # 设置工作目录
        cwd=directory,

        # 使用 Sonnet 模型（平衡性能和成本）
        model="sonnet"
    )

    # 构建分析提示
    prompt = f"""请分析 {directory} 目录中的代码库。

## 分析任务

1. **项目结构**
   - 识别主要目录和文件
   - 确定项目类型（Web 应用、API、CLI 工具等）
   - 列出使用的技术栈

2. **代码质量**
   - 检查代码组织是否合理
   - 识别重复代码
   - 评估命名规范

3. **潜在问题**
   - 查找可能的 bug
   - 识别安全隐患
   - 发现性能问题

4. **改进建议**
   - 提出具体的改进方案
   - 优先级排序

## 输出格式

请以 Markdown 格式输出报告，包含上述所有部分。
在每个问题后注明文件和行号。
"""

    # 收集结果
    result = {
        "directory": directory,
        "timestamp": datetime.now().isoformat(),
        "report": [],
        "tools_used": [],
        "metadata": {}
    }

    try:
        async with ClaudeSDKClient(options=options) as client:
            await client.query(prompt)

            async for message in client.receive_response():
                match message.type:
                    case "text":
                        result["report"].append(message.text)

                    case "tool_use":
                        tool_info = f"{message.tool_name}: {message.tool_input.get('file_path', message.tool_input.get('pattern', ''))}"
                        result["tools_used"].append(tool_info)
                        print(f"  [scanning] {tool_info}")

                    case "result":
                        result["metadata"] = {
                            "duration_ms": message.duration_ms,
                            "total_cost_usd": message.total_cost_usd,
                            "num_turns": message.num_turns,
                            "input_tokens": message.usage.get("input_tokens", 0),
                            "output_tokens": message.usage.get("output_tokens", 0)
                        }

                    case "error":
                        print(f"  [error] {message.error}")
                        result["error"] = message.error

    except Exception as e:
        result["error"] = str(e)
        print(f"Error during analysis: {e}")

    return result


def format_report(result: dict) -> str:
    """格式化分析报告"""
    lines = [
        "=" * 60,
        "           CODE ANALYSIS REPORT",
        "=" * 60,
        "",
        f"Directory: {result['directory']}",
        f"Timestamp: {result['timestamp']}",
        ""
    ]

    if result.get("error"):
        lines.extend([
            "WARNING: Analysis encountered an error:",
            result["error"],
            ""
        ])

    lines.extend([
        "-" * 60,
        "                   REPORT",
        "-" * 60,
        ""
    ])

    # 添加报告内容
    report_text = "\n".join(result.get("report", []))
    lines.append(report_text)

    # 添加元数据
    if result.get("metadata"):
        meta = result["metadata"]
        lines.extend([
            "",
            "-" * 60,
            "                 STATISTICS",
            "-" * 60,
            f"Duration: {meta.get('duration_ms', 0) / 1000:.2f}s",
            f"Cost: ${meta.get('total_cost_usd', 0):.4f}",
            f"Turns: {meta.get('num_turns', 0)}",
            f"Tokens: {meta.get('input_tokens', 0)} in / {meta.get('output_tokens', 0)} out",
            "=" * 60
        ])

    return "\n".join(lines)


async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python code_analyzer.py <directory>")
        print("Example: python code_analyzer.py ./src")
        sys.exit(1)

    directory = sys.argv[1]

    if not Path(directory).is_dir():
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)

    print(f"Analyzing codebase: {directory}")
    print("   This may take a few minutes...")
    print()

    # 运行分析
    result = await analyze_codebase(directory)

    # 输出报告
    report = format_report(result)
    print(report)

    # 保存报告到文件
    report_file = f"analysis-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    with open(report_file, "w") as f:
        f.write(report)

    print(f"\nReport saved to: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())
```

运行这个代码分析 Agent 时，你会看到它逐步扫描文件、搜索模式、阅读代码，最终生成一份结构化的报告。注意 STATISTICS 部分——它告诉你这次分析花了多少钱、用了多少 Token，这些数据对于生产环境的成本预估至关重要。

```
$ python code_analyzer.py ./src

Analyzing codebase: ./src
   This may take a few minutes...

  [scanning] Glob: **/*
  [scanning] Read: ./src/index.ts
  [scanning] Read: ./src/utils/helpers.ts
  [scanning] Grep: TODO
  [scanning] Read: ./src/config.ts

============================================================
           CODE ANALYSIS REPORT
============================================================

Directory: ./src
Timestamp: 2025-01-18T10:30:45.123456

------------------------------------------------------------
                   REPORT
------------------------------------------------------------

## 项目结构

这是一个 TypeScript Web 应用项目，使用 Express 框架...

## 代码质量

代码组织良好，遵循模块化原则...

## 潜在问题

1. **安全隐患** (src/auth.ts:42)
   - SQL 查询使用字符串拼接，存在注入风险

2. **性能问题** (src/data.ts:78)
   - 循环内多次查询数据库，建议使用批量查询

## 改进建议

1. [高优先级] 使用参数化查询替代字符串拼接
2. [中优先级] 添加请求限流中间件
3. [低优先级] 考虑添加单元测试

------------------------------------------------------------
                 STATISTICS
------------------------------------------------------------
Duration: 15.32s
Cost: $0.0523
Turns: 8
Tokens: 12543 in / 2891 out
============================================================

Report saved to: analysis-report-20250118-103045.md
```

**错误处理与监控**

在开发阶段，代码能跑通就行。但在生产环境中，错误处理和监控是不可或缺的。Agent 调用涉及网络通信、模型推理、工具执行三个层面，每一层都可能出错。一个健壮的 Agent 应用必须能优雅地处理这些错误，而不是在用户面前崩溃。

Agent SDK 中的错误分为两类：一类是 SDK 层面的错误（如 API Key 无效、网络超时），抛出  ClaudeAgentError 异常；另一类是 Agent 执行层面的错误（如工具调用失败、权限被拒绝），通过消息流中的  error 类型消息返回。你需要同时处理这两类错误。

```
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentError

async def safe_query(prompt: str):
    """带错误处理的查询"""
    try:
        async with ClaudeSDKClient() as client:
            await client.query(prompt)

            async for msg in client.receive_response():
                if msg.type == "error":
                    # Agent 内部错误
                    print(f"Agent error: {msg.error}")
                    return None
                elif msg.type == "text":
                    print(msg.text)
                elif msg.type == "result":
                    return msg.result

    except ClaudeAgentError as e:
        # SDK 错误（如 API 连接失败）
        print(f"SDK error: {e}")
        return None

    except Exception as e:
        # 未预期的错误
        print(f"Unexpected error: {e}")
        return None
```

**成本监控与控制**

每一次 Agent 调用都会消耗 Token，产生费用。在生产环境中，如果不对成本进行监控，很容易拿到一份让你惊吓的高额账单，一个失控的 Agent 循环可能在几分钟内消耗数十美元。下面的代码展示了如何在每次调用后检查成本，并在超过预设阈值时发出告警。

```
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def monitored_query(prompt: str, cost_limit: float = 0.10):
    """带成本监控的查询"""
    async with ClaudeSDKClient() as client:
        await client.query(prompt)

        turn_count = 0
        async for msg in client.receive_response():
            if msg.type == "tool_use":
                turn_count += 1
                logger.info(f"Turn {turn_count}: {msg.tool_name}")

            if msg.type == "result":
                cost = msg.total_cost_usd
                logger.info(f"Completed in {msg.duration_ms}ms, cost: ${cost}")

                if cost > cost_limit:
                    logger.warning(f"Cost exceeded limit: ${cost} > ${cost_limit}")

                return msg
```

控制 Agent 成本的核心手段有三个：限制轮次、选择更便宜的模型、限制工具。这三个手段可以组合使用，根据具体场景找到性能和成本的最佳平衡点。

```
# 1. 限制轮次
options = ClaudeAgentOptions(
    max_turns=10  # 最多 10 轮
)

# 2. 使用更便宜的模型
options = ClaudeAgentOptions(
    model="haiku"  # Haiku 比 Sonnet 便宜得多
)

# 3. 限制工具（减少读取的文件数）
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob"],  # 不用 Grep
    max_turns=5
)
```

在生产环境运行 Agent，监控关键指标：

- 成本：每次调用花了多少钱
- 耗时：任务执行了多长时间
- 轮次：Agent 循环了多少次
- 错误率：多少任务失败了

![img](https://static001.geekbang.org/resource/image/a7/d1/a7a818b892ce2a7107812808a5ccb1d1.jpg?wh=2598x1098)

# 22｜得心应手：Agent SDK 高级应用

> 释题：得心应手。当你掌握了自定义工具、Hooks 拦截、权限分层和流式会话这些高级能力之后，构建一个像自动化测试修复 Agent 这样的生产级应用，便如得心应手般自然流畅。

上一讲我们学习了 Agent SDK 的基础用法，包括如何创建 Agent、发送查询、处理响应，以及单次调用模式的核心 API。有了这些基础，你已经可以让 Claude 在程序中跑起来了。但要在真实的工程环境中使用它，仅靠基础 API 还远远不够。你需要扩展 Agent 的能力边界，需要在关键节点插入安全控制，需要管理多轮交互的上下文状态，更需要一套完整的生产级运维策略。

这一讲，我们就来深入 Agent SDK 的高级特性。我会带你从自定义工具开始，逐步走过 Hooks 系统、四层权限管理、流式会话，最终完成一个完整的实战项目——自动化测试修复 Agent。这个 Agent 能自动运行测试、分析失败原因、提出修复方案，甚至在获得确认后自动修复代码。

一个中型电商项目在每次提交代码前，CI 会运行完整的测试套件，大约 200 个测试用例。大部分时候测试都能通过，但偶尔会有几个测试失败。问题是，测试失败的原因千奇百怪。有时是代码逻辑错误，有时是测试本身过时了，有时是环境配置问题，有时是 Mock 数据不对。

每次失败，我们都要重复后面的流程。

1. 阅读测试输出，找到失败的测试
2. 打开对应的测试文件，理解测试逻辑
3. 打开被测试的代码，分析失败原因
4. 决定是修复代码还是修复测试
5. 修改，重新运行，验证

这个过程短则十分钟，长则一小时。

那么能否构建一个测试修复 Agent，它能自动运行测试、分析失败原因、提出修复方案，甚至在获得确认后自动修复代码呢？这样一个曾经需要 30 分钟的修复工作，现在只需要 3 分钟的人工确认。

这一讲，我们就来构建这样一个 Agent。

**在 Agent 中注入和使用自定义工具**

Claude Agent SDK 内置了文件操作、命令执行、网络搜索等工具。但在实际项目中，你往往需要领域特定的能力：

- 查询数据库
- 调用内部 API
- 发送通知
- 执行特定的业务逻辑

这就是自定义工具的价值，让 Agent 能够调用你定义的函数。SDK 的自定义工具本质上是运行在你应用进程内的 MCP 服务器。与需要单独进程的常规 MCP 服务器不同，SDK 工具直接在你的 Python 应用中运行，消除了进程管理和 IPC 开销。这种设计让工具调用的延迟极低，同时还能共享应用的内存空间和数据库连接池等资源。

![img](https://static001.geekbang.org/resource/image/1c/35/1c2c34c1594169400c375165df27bb35.jpg?wh=1536x1024)

上图中的架构就是 Agent → MCP Server → Tools 的三层解耦调用链。

左侧的 Agent（大模型 + 记忆 + 推理）并不直接调用具体工具，而是通过统一的 tool_use 请求，将意图表达为标准化的工具调用（如 mcp__{server}__{tool}）。中间的 MCP Server 相当于一个“工具路由中枢”，负责根据命名规范解析请求、完成权限控制与路由分发，并调用对应的工具函数。

右侧的各类自定义工具只专注于执行具体能力（如查询、搜索、发送等），执行完成后将结果返回给 MCP Server，再统一回传给 Agent。通过标准命名 + 中间层路由，实现 Agent 与工具的解耦、可扩展和可治理，从而让系统可以像“插 USB 设备”一样动态接入新能力。

**使用 @tool 装饰器定义工具**

@tool 装饰器是定义自定义工具的最简单方式。你只需要指定工具名称、描述和参数，然后把业务逻辑写在函数体内。SDK 会自动将这个函数注册为一个可被 Agent 调用的工具，Agent 在推理过程中会根据工具描述决定何时调用它。

下面的例子定义了一个天气查询工具。注意返回值必须是包含  content 列表的字典，这是 MCP 协议要求的标准格式。

```
from claude_agent_sdk import tool

@tool(
    name="get_weather",
    description="Get current weather for a city",
    parameters={"city": str, "units": str}
)
async def get_weather(args):
    city = args["city"]
    units = args.get("units", "celsius")

    # 调用天气 API（示例）
    weather = await fetch_weather_api(city, units)

    return {
        "content": [
            {"type": "text", "text": f"Weather in {city}: {weather}"}
        ]
    }
```

下面是  @tool 装饰器的三个核心参数，每个参数都直接影响 Agent 的调用行为。

![img](https://static001.geekbang.org/resource/image/86/82/86d2594dd9010e5ce9811553fd5dc782.jpg?wh=2401x626)

其中  description 尤为关键，它不是给人看的注释，而是给 AI 看的使用指南。写得清晰准确，Agent 才能在正确的时机调用正确的工具。

**创建 SDK MCP 服务器承载工具**

定义好工具函数之后，下一步是创建一个 MCP 服务器来承载它们。你可以把多个工具注册到同一个服务器中，服务器会统一管理这些工具的生命周期和调用路由。

下面的例子创建了一个包含两个工具的服务器。注意  @tool 装饰器的简写形式，当参数简单时，可以直接用位置参数传入名称、描述和参数字典。

```
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("greet", "Greet a user by name", {"name": str})
async def greet_user(args):
    return {
        "content": [
            {"type": "text", "text": f"Hello, {args['name']}!"}
        ]
    }

@tool("calculate", "Perform a calculation", {"expression": str})
async def calculate(args):
    try:
        result = eval(args["expression"])  # 生产环境请用安全的表达式解析器
        return {
            "content": [
                {"type": "text", "text": f"Result: {result}"}
            ]
        }
    except Exception as e:
        return {
            "content": [
                {"type": "text", "text": f"Error: {e}"}
            ],
            "isError": True
        }

# 创建 MCP 服务器
server = create_sdk_mcp_server(
    name="my-tools",
    version="1.0.0",
    tools=[greet_user, calculate]
)
```

服务器创建后，还不能直接使用。你需要把它注入到 Agent 的配置中，Agent 才能“看到”并调用这些工具。

**注入并使用自定义工具**

将 MCP 服务器注入 Agent 的方式很直观，通过  mcp_servers 选项传入服务器实例，然后在  allowed_tools 中声明允许使用的工具。工具名称遵循  mcp\__{服务器名}__{工具名} 的命名格式，这个双下划线的命名规则确保了不同服务器之间的工具名不会冲突。

```
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

options = ClaudeAgentOptions(
    mcp_servers={"tools": server},
    # 工具名称格式：mcp__{服务器名}__{工具名}
    allowed_tools=[
        "mcp__tools__greet",
        "mcp__tools__calculate"
    ]
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Say hello to Alice and calculate 2 + 3 * 4")
    async for msg in client.receive_response():
        print(msg)
```

当 Agent 收到上面的提示时，它会自动识别出需要调用两个工具：先用  greet 向 Alice 打招呼，再用  calculate 计算表达式。这种自动编排能力正是 Agent SDK 的核心价值。

**使用 Pydantic 进行参数验证**

对于简单工具，字典式参数定义已经够用。但当参数变得复杂——比如有默认值、范围限制、可选字段时，Pydantic 模型是更好的选择。它不仅提供自动验证，还能生成更详细的 JSON Schema 供 Agent 参考，从而提高参数传递的准确性。

下面的例子定义了一个数据库查询工具。Pydantic 模型中的  Field 描述会被自动转换为工具参数说明，ge 和  le 约束则确保 Agent 传入的  limit 值在合理范围内。

```
from pydantic import BaseModel, Field
from claude_agent_sdk import tool

class DatabaseQueryParams(BaseModel):
    """数据库查询参数"""
    table: str = Field(..., description="Table name")
    columns: list[str] = Field(default=["*"], description="Columns to select")
    where: str | None = Field(default=None, description="WHERE clause")
    limit: int = Field(default=100, ge=1, le=1000, description="Max rows")

@tool(
    name="query_database",
    description="Execute a SELECT query on the database",
    parameters=DatabaseQueryParams
)
async def query_database(args: DatabaseQueryParams):
    # args 已经通过 Pydantic 验证
    query = f"SELECT {', '.join(args.columns)} FROM {args.table}"
    if args.where:
        query += f" WHERE {args.where}"
    query += f" LIMIT {args.limit}"

    # 执行查询
    results = await db.execute(query)

    return {
        "content": [
            {"type": "text", "text": f"Query: {query}\nResults: {results}"}
        ]
    }
```

![img](https://static001.geekbang.org/resource/image/32/ae/32f886b2b38431abcfb036baf52b69ae.jpg?wh=2579x1179)

下面是一个存在 SQL 注入风险的工具调用示例以及相应的调整。

```
# 危险：直接执行 SQL
@tool("run_sql", "Run any SQL", {"sql": str})
async def run_sql(args):
    return await db.execute(args["sql"])  # SQL 注入风险！
```

```
# 安全：限制操作类型
@tool("query_users", "Query user table", {"user_id": int})
async def query_users(args):
    return await db.execute(
        "SELECT * FROM users WHERE id = ?",
        [args["user_id"]]
    )
```

这个安全示例的核心在于，不要把工具当“能力接口”，而要当“受控权限边界”来设计。

危险版本把任意 SQL 执行权直接暴露给 Agent，相当于让一个不完全可信的系统拥有数据库 root 权限，一旦被误导或注入就可能造成严重破坏；而安全版本通过限制操作范围（只允许查询特定表）、使用参数化查询、防止注入，并对参数进行类型约束，把“无限能力”收敛为“可控动作”。本质上，这体现的是 Agent 系统的一个关键原则，模型可以自由推理，但工具必须严格受限。

**Agent SDK Hooks 系统概述**

Hooks 让你能够在 Agent 执行的各个阶段插入自定义逻辑。如果说自定义工具是扩展了 Agent 能做什么，那么 Hooks 就是控制 Agent 怎么做。它们提供对 Agent 行为的确定性控制——不是建议 Agent 遵守某个规则，而是在系统层面强制执行。

下表列出了 SDK 支持的所有 Hook 事件。每个事件对应 Agent 执行流程中的一个关键节点，你可以在这些节点插入安全检查、日志记录、数据转换等逻辑。

![img](https://static001.geekbang.org/resource/image/69/a5/693575fbf72a41fa657f82a55f3091a5.jpg?wh=3235x1460)

**PreToolUse Hook：执行前拦截**

PreToolUse 是最常用的 Hook，它在工具执行前触发。你可以在这里做三件事，允许执行、拒绝执行、或修改输入参数。这给了你对 Agent 行为的完全控制权。

下面的例子展示了一个 Bash 命令安全检查器。它会拦截所有 Bash 工具调用，检查命令是否包含危险模式（如  rm -rf、sudo），如果发现危险则拒绝执行。对于不在白名单中的命令，它会要求用户手动确认。

```
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

async def check_bash_command(input_data, tool_use_id, context):
    """检查 Bash 命令是否安全"""
    tool_name = input_data["tool_name"]
    tool_input = input_data["tool_input"]

    if tool_name == "Bash":
        command = tool_input.get("command", "")

        # 阻止危险命令
        dangerous_patterns = ["rm -rf", "sudo", "chmod 777", "> /dev/"]
        for pattern in dangerous_patterns:
            if pattern in command:
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"Blocked dangerous command: {pattern}"
                    }
                }

        # 只允许特定命令
        allowed_prefixes = ["npm", "python", "git", "pytest", "ls", "cat"]
        if not any(command.strip().startswith(p) for p in allowed_prefixes):
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": f"Command requires approval: {command}"
                }
            }

    return {}  # 允许执行

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[check_bash_command])
        ]
    }
)
```

注意  HookMatcher 的  matcher 参数，它指定这个 Hook 只对  Bash 工具生效。你也可以用  "*" 来匹配所有工具。

**PreToolUse Hook：修改输入参数**

从 Claude Code v2.0.10 开始，PreToolUse Hook 获得了一个强大的新能力——修改工具输入。这意味着你可以在工具执行前对参数进行转换、规范化或补充，而 Agent 对此完全无感知。

一个典型的应用场景是路径规范化。Agent 生成的文件路径有时是相对路径，但你的工具可能要求绝对路径。通过 PreToolUse Hook，你可以在调用发生前自动完成转换，避免工具报错。

```
async def normalize_file_paths(input_data, tool_use_id, context):
    """规范化文件路径"""
    tool_name = input_data["tool_name"]
    tool_input = input_data["tool_input"]

    if tool_name in ["Read", "Write", "Edit"]:
        file_path = tool_input.get("file_path", "")

        # 将相对路径转为绝对路径
        if not file_path.startswith("/"):
            import os
            absolute_path = os.path.abspath(file_path)

            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                    "updatedInput": {
                        **tool_input,
                        "file_path": absolute_path
                    }
                }
            }

    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="*", hooks=[normalize_file_paths])
        ]
    }
)
```

返回值中的  updatedInput 字段就是修改后的工具输入。SDK 会用它替换原始输入，然后继续执行工具。

**PostToolUse Hook：执行后处理**

PostToolUse 在工具执行成功后触发，适合做日志记录、结果格式化、自动化后处理等工作。与 PreToolUse 不同，PostToolUse 无法改变已经发生的工具调用，但它可以基于调用结果执行额外操作。

下面展示了两个实用的 PostToolUse Hook。第一个记录所有工具的使用日志，用于审计和调试。第二个在文件写入后自动运行代码格式化工具，确保 Agent 生成的代码符合团队代码风格规范。

```
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def log_tool_usage(input_data, tool_use_id, context):
    """记录工具使用日志"""
    tool_name = input_data["tool_name"]
    tool_input = input_data.get("tool_input", {})
    tool_response = input_data.get("tool_response", {})

    logger.info(f"[{datetime.now().isoformat()}] Tool: {tool_name}")
    logger.info(f"  Input: {tool_input}")
    logger.info(f"  Response: {str(tool_response)[:200]}...")

    return {}

async def auto_format_code(input_data, tool_use_id, context):
    """文件写入后自动格式化"""
    tool_name = input_data["tool_name"]
    tool_input = input_data.get("tool_input", {})

    if tool_name in ["Write", "Edit"]:
        file_path = tool_input.get("file_path", "")

        # 根据文件类型运行格式化
        if file_path.endswith(".py"):
            import subprocess
            subprocess.run(["black", file_path], capture_output=True)
        elif file_path.endswith((".ts", ".js")):
            import subprocess
            subprocess.run(["prettier", "--write", file_path], capture_output=True)

    return {}

options = ClaudeAgentOptions(
    hooks={
        "PostToolUse": [
            HookMatcher(matcher="*", hooks=[log_tool_usage]),
            HookMatcher(matcher="Write", hooks=[auto_format_code]),
            HookMatcher(matcher="Edit", hooks=[auto_format_code])
        ]
    }
)
```

自动格式化这个 Hook 特别实用。Agent 生成的代码虽然逻辑正确，但缩进、换行、引号风格可能不符合项目规范。有了这个 Hook，你再也不需要手动跑格式化了。

**canUseTool 回调：运行时权限控制**

除了 Hooks，SDK 还提供了  canUseTool 回调作为另一种权限控制方式。它比 Hooks 更简单，只负责回答一个问题：“这个工具调用是否被允许？”不涉及输入修改、日志记录等复杂逻辑，适合纯粹的权限判断场景。

下面的例子展示了一个保护敏感文件和限制网络操作的  canUseTool 回调。当 Agent 试图读写受保护的文件或执行网络命令时，回调会返回拒绝并附带原因说明。

```
# 受保护的文件列表
PROTECTED_FILES = [
    ".env",
    "secrets.json",
    "config/production.yaml",
    "database/migrations/"
]

async def can_use_tool(tool_name: str, tool_input: dict) -> dict:
    """运行时权限检查"""

    # 检查文件操作
    if tool_name in ["Write", "Edit", "Read"]:
        file_path = tool_input.get("file_path", "")

        for protected in PROTECTED_FILES:
            if protected in file_path:
                return {
                    "allowed": False,
                    "reason": f"Access to {protected} is not allowed"
                }

    # 检查 Bash 命令
    if tool_name == "Bash":
        command = tool_input.get("command", "")

        # 禁止网络操作
        network_commands = ["curl", "wget", "nc", "ssh"]
        for cmd in network_commands:
            if cmd in command:
                return {
                    "allowed": False,
                    "reason": f"Network command '{cmd}' is not allowed"
                }

    return {"allowed": True}

options = ClaudeAgentOptions(
    can_use_tool=can_use_tool
)
```

**Hooks 与 canUseTool 的选择**

Hooks 和 canUseTool 都能控制工具的使用权限，但它们的能力范围差异很大。理解这个差异对于选择合适的机制至关重要。

![img](https://static001.geekbang.org/resource/image/6c/42/6cf0452a683f7fc998656ab0182be042.jpg?wh=3221x1116)

简单来说，只需要权限检查，用  canUseTool；需要修改输入、记录日志、执行后处理，用 Hooks。在实际项目中，两者经常配合使用，canUseTool 负责快速的权限判断，Hooks 负责更复杂的拦截和处理逻辑。

**Agent SDK 权限管理：四道防线**

安全是构建生产级 Agent 的核心议题。Agent SDK 提供了四种互补的权限控制机制，权限模式、canUseTool 回调、Hooks、settings.json 中的权限规则。它们构成了一个分层防御体系。

让我逐一介绍这四道防线。

**权限模式：全局基调**

权限模式是最粗粒度的控制，它设定了整个会话的安全基调。一共有四种模式可选，从宽松到严格，你需要根据使用场景选择合适的模式。

```
options = ClaudeAgentOptions(
    permission_mode="acceptEdits"  # 自动接受文件编辑
)
```

![img](https://static001.geekbang.org/resource/image/59/be/5953eba4afcb0ab4ce98fdacc54032be.jpg?wh=3008x1235)

**工具白名单与黑名单**

第二道防线是工具级别的准入控制。通过  allowed_tools 和  disallowed_tools，你可以精确控制 Agent 能使用哪些工具。这比权限模式更细粒度，你可以允许文件读取但禁止网络搜索，或者只允许运行特定的 Bash 命令。

```
options = ClaudeAgentOptions(
    # 只允许这些工具
    allowed_tools=["Read", "Grep", "Glob", "Bash(pytest:*)"],

    # 禁用这些工具
    disallowed_tools=["Task", "WebSearch"]
)
```

注意  Bash(pytest:*) 这个语法，它表示只允许以  pytest 开头的 Bash 命令。这种细粒度的 Bash 命令过滤是生产环境中非常实用的安全特性。

第三道防线是运行时动态权限检查（canUseTool），第四道防线是最细粒度的 Hooks 控制。它们的工作原理在前面已经详细讲解过，这里不再赘述。

在实际项目中，这四道防线应该配合使用，形成纵深防御。下面的代码展示了一个完整的四层安全配置。请注意每一层防线各司其职：权限模式设定基调，白名单限制工具集，canUseTool 保护敏感资源，Hooks 提供细粒度控制和审计。

```
options = ClaudeAgentOptions(
    # 第一道：权限模式
    permission_mode="acceptEdits",

    # 第二道：工具白名单
    allowed_tools=["Read", "Write", "Edit", "Bash", "Grep", "Glob"],
    disallowed_tools=["WebSearch"],  # 禁止网络搜索

    # 第三道：运行时检查
    can_use_tool=can_use_tool,

    # 第四道：Hooks
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[check_bash_command]),
            HookMatcher(matcher="*", hooks=[log_all_tools])
        ],
        "PostToolUse": [
            HookMatcher(matcher="Write", hooks=[auto_format])
        ]
    }
)
```

**流式会话：为什么以及怎么用**

到目前为止，我们的示例都使用的是单次查询模式——发送一个请求，接收一个响应。但在生产环境中，你往往需要多轮对话、中途干预、动态调整参数。这就是流式会话（Streaming Session）的价值。流式输入模式是使用 Claude Agent SDK 的首选方式。它允许 Agent 作为长时间运行的进程，接收用户输入、处理中断、显示权限请求、管理会话。

下表清晰展示了两种模式的差异。

![img](https://static001.geekbang.org/resource/image/df/56/df1200f2e19b515bf88b5ded19184456.jpg?wh=2569x1034)

流式会话的核心优势是保持上下文。在同一个  async with 块内，你可以发送多次查询，每次查询都能“看到”之前的对话历史。这让 Agent 能够执行复杂的多步骤任务，而不需要你手动管理上下文。

```
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def streaming_session():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash"],
        permission_mode="default"
    )

    async with ClaudeSDKClient(options=options) as client:
        # 第一轮对话
        await client.query("列出当前目录的 Python 文件")
        async for msg in client.receive_response():
            if msg.type == "text":
                print(msg.text)

        # 继续对话（保持上下文）
        await client.query("分析第一个文件的代码质量")
        async for msg in client.receive_response():
            if msg.type == "text":
                print(msg.text)

        # 再次继续
        await client.query("修复发现的问题")
        async for msg in client.receive_response():
            print(msg)
```

这三轮对话共享同一个会话上下文。Agent 在第二轮能引用第一轮列出的文件，在第三轮能基于第二轮的分析结果执行修复。

**处理权限请求**

在流式模式中，当 Agent 试图执行需要权限的操作时，SDK 不会自动处理，而是将权限请求发送给你的代码。你可以根据工具类型、命令内容等信息做出自动决策，也可以将决策权交给用户。

下面的例子展示了一种混合策略：对于测试命令自动批准，对于其他命令则询问用户。

```
async def handle_permission_request(request):
    """处理权限请求"""
    tool_name = request.get("tool_name")
    tool_input = request.get("tool_input")

    print(f"\nPermission Request:")
    print(f"   Tool: {tool_name}")
    print(f"   Input: {tool_input}")

    # 自动决策或询问用户
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if command.startswith("npm test") or command.startswith("pytest"):
            return {"approved": True}

    # 询问用户
    response = input("   Approve? (y/n): ")
    return {"approved": response.lower() == "y"}

async with ClaudeSDKClient(options=options) as client:
    await client.query("运行测试并修复失败的测试")

    async for msg in client.receive_response():
        if msg.type == "permission_request":
            decision = await handle_permission_request(msg)
            await client.respond_to_permission(msg.id, decision)
        else:
            print(msg)
```

**中断和取消**

流式会话支持在任意时刻中断 Agent 的执行。这在 Agent 陷入无意义循环、执行时间过长、或用户改变主意时非常有用。调用  client.interrupt() 后，Agent 会停止当前操作，但会话上下文仍然保留，你可以继续发送新的查询。

```
import asyncio

async def interruptible_session():
    async with ClaudeSDKClient(options=options) as client:
        await client.query("分析整个代码库")

        try:
            async for msg in client.receive_response():
                print(msg)

                # 检查是否需要中断
                if should_interrupt():
                    await client.interrupt()
                    print("Task interrupted by user")
                    break

        except asyncio.CancelledError:
            print("Session cancelled")
```

**动态切换设置**

流式模式还有一个独特的能力：在会话中途动态切换设置。最典型的场景是“先分析后执行”模式，先用只读模式让 Agent 分析问题并制定计划，用户确认后再切换到可编辑模式执行修改。这种两阶段工作流在生产环境中非常常见，它既保证了安全性，又保持了效率。

```
async with ClaudeSDKClient(options=options) as client:
    # 开始时使用只读模式
    await client.update_options(permission_mode="planMode")
    await client.query("分析代码并制定修复计划")
    async for msg in client.receive_response():
        print(msg)

    # 用户确认后，切换到可编辑模式
    await client.update_options(permission_mode="acceptEdits")
    await client.query("执行刚才的修复计划")
    async for msg in client.receive_response():
        print(msg)
```

![img](https://static001.geekbang.org/resource/image/b0/27/b02f59d405e34c7805dfyy247a70d727.jpg?wh=3449x3645)

**实战项目：自动化测试修复 Agent**

现在，让我们把前面学到的所有高级特性组合起来，构建开篇故事中的测试修复 Agent。这个项目会用到自定义工具（运行测试）、Hooks（安全控制）、流式会话（两阶段工作流）和四层权限管理。

这个项目的项目需求是构建一个 Agent 来完成下面的任务。

1. 运行测试套件，捕获失败信息
2. 分析失败原因
3. 提出修复方案
4. 在确认后执行修复
5. 重新运行测试验证

**自定义工具：测试运行器**

首先，我们需要一个能够运行测试并返回结构化结果的自定义工具。这个工具会调用 pytest，解析 JSON 报告，提取失败测试的详细信息（测试名称、错误信息），然后以标准 MCP 格式返回给 Agent。

Agent 拿到这些结构化数据后，就能精确定位需要分析的文件和代码行。

我们还额外定义了一个  get_test_history 工具，用于查询最近的测试运行历史。这能帮助 Agent 判断测试失败是偶发性的还是持续性的，从而做出更准确的修复决策。

```
from claude_agent_sdk import tool, create_sdk_mcp_server
import subprocess
import json

@tool(
    name="run_tests",
    description="Run the test suite and return results",
    parameters={
        "test_path": str,  # 可选：指定测试路径
        "verbose": bool    # 可选：详细输出
    }
)
async def run_tests(args):
    """运行 pytest 测试"""
    test_path = args.get("test_path", "tests/")
    verbose = args.get("verbose", False)

    cmd = ["pytest", test_path, "--tb=short", "-q"]
    if verbose:
        cmd.append("-v")

    # 添加 JSON 输出
    cmd.extend(["--json-report", "--json-report-file=test-results.json"])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 分钟超时
        )

        # 读取 JSON 报告
        try:
            with open("test-results.json") as f:
                report = json.load(f)
        except:
            report = None

        output = {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
            "success": result.returncode == 0
        }

        if report:
            output["summary"] = {
                "total": report.get("summary", {}).get("total", 0),
                "passed": report.get("summary", {}).get("passed", 0),
                "failed": report.get("summary", {}).get("failed", 0),
                "errors": report.get("summary", {}).get("errors", 0)
            }
            output["failed_tests"] = [
                {
                    "name": t["nodeid"],
                    "message": t.get("call", {}).get("longrepr", "")
                }
                for t in report.get("tests", [])
                if t.get("outcome") == "failed"
            ]

        return {
            "content": [
                {"type": "text", "text": json.dumps(output, indent=2)}
            ]
        }

    except subprocess.TimeoutExpired:
        return {
            "content": [
                {"type": "text", "text": "Error: Test execution timed out after 5 minutes"}
            ],
            "isError": True
        }
    except Exception as e:
        return {
            "content": [
                {"type": "text", "text": f"Error running tests: {e}"}
            ],
            "isError": True
        }


@tool(
    name="get_test_history",
    description="Get recent test run history",
    parameters={"limit": int}
)
async def get_test_history(args):
    """获取测试历史（示例实现）"""
    limit = args.get("limit", 5)

    # 实际实现中，这里会从数据库或日志读取
    history = [
        {"timestamp": "2025-01-18 10:00", "passed": 198, "failed": 2},
        {"timestamp": "2025-01-18 09:30", "passed": 200, "failed": 0},
        {"timestamp": "2025-01-18 09:00", "passed": 195, "failed": 5}
    ][:limit]

    return {
        "content": [
            {"type": "text", "text": json.dumps(history, indent=2)}
        ]
    }


# 创建测试工具服务器
test_tools_server = create_sdk_mcp_server(
    name="test-tools",
    version="1.0.0",
    tools=[run_tests, get_test_history]
)
```

**Hooks 配置：安全控制**

测试修复 Agent 需要修改源代码文件，这是一个高风险操作。我们通过 Hooks 实现两个关键的安全控制：第一，限制 Agent 只能修改  tests/、src/、lib/ 目录下的文件，禁止修改  setup.py、pyproject.toml 等项目配置文件；第二，记录所有文件修改操作到日志文件，便于事后审计和回滚。

```
# 允许修改的文件模式
ALLOWED_EDIT_PATTERNS = [
    "tests/",
    "src/",
    "lib/"
]

# 禁止修改的文件
FORBIDDEN_FILES = [
    "setup.py",
    "pyproject.toml",
    "requirements.txt",
    ".github/",
    "conftest.py"
]

async def check_file_modification(input_data, tool_use_id, context):
    """检查文件修改权限"""
    tool_name = input_data["tool_name"]
    tool_input = input_data["tool_input"]

    if tool_name in ["Write", "Edit"]:
        file_path = tool_input.get("file_path", "")

        # 检查禁止列表
        for forbidden in FORBIDDEN_FILES:
            if forbidden in file_path:
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"Modification of {forbidden} is not allowed"
                    }
                }

        # 检查允许列表
        allowed = any(file_path.startswith(p) for p in ALLOWED_EDIT_PATTERNS)
        if not allowed:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": f"File {file_path} is outside allowed directories"
                }
            }

    return {}


async def log_modifications(input_data, tool_use_id, context):
    """记录所有修改"""
    tool_name = input_data["tool_name"]
    tool_input = input_data["tool_input"]

    if tool_name in ["Write", "Edit"]:
        file_path = tool_input.get("file_path", "")

        # 记录到修改日志
        with open("modification-log.txt", "a") as f:
            from datetime import datetime
            f.write(f"[{datetime.now().isoformat()}] {tool_name}: {file_path}\n")

    return {}
```

这两个 Hook 分别挂载在  PreToolUse 和  PostToolUse 事件上，前者在文件修改前做准入检查，后者在修改成功后记录审计日志。

下面是完整的测试修复 Agent 代码。它综合运用了自定义工具、Hooks、流式会话和动态权限切换，实现了“先分析后修复”的两阶段工作流。第一阶段使用  default 权限模式，Agent 只分析不修改；用户确认修复方案后，切换到  acceptEdits 模式执行修复。

```
#!/usr/bin/env python3
"""
自动化测试修复 Agent

运行测试、分析失败、修复代码、验证修复。
"""

import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, HookMatcher

# 导入自定义工具和 Hooks（见上文定义）
# from tools import test_tools_server
# from hooks import check_file_modification, log_modifications


async def run_test_fixer():
    """运行测试修复 Agent"""

    # 配置选项
    options = ClaudeAgentOptions(
        # 模型选择
        model="sonnet",

        # MCP 服务器
        mcp_servers={"test-tools": test_tools_server},

        # 允许的工具
        allowed_tools=[
            "Read",
            "Write",
            "Edit",
            "Grep",
            "Glob",
            "Bash(pytest:*)",  # 只允许 pytest 命令
            "mcp__test-tools__run_tests",
            "mcp__test-tools__get_test_history"
        ],

        # 权限模式：先分析，确认后再修改
        permission_mode="default",

        # 最大轮次
        max_turns=30,

        # Hooks
        hooks={
            "PreToolUse": [
                HookMatcher(matcher="Write", hooks=[check_file_modification]),
                HookMatcher(matcher="Edit", hooks=[check_file_modification])
            ],
            "PostToolUse": [
                HookMatcher(matcher="Write", hooks=[log_modifications]),
                HookMatcher(matcher="Edit", hooks=[log_modifications])
            ]
        }
    )

    # 系统提示
    system_prompt = """你是一个专业的测试修复助手。你的任务是：

1.运行测试套件，识别失败的测试
2.分析每个失败测试的原因
3.确定是代码 bug 还是测试本身的问题
4.提出具体的修复方案
5.在获得确认后执行修复
6.重新运行测试验证修复

修复原则：
- 最小化修改：只改必要的代码
- 优先修复代码：除非测试本身有问题
- 保持测试覆盖：不要删除测试来"修复"问题
- 记录修改：说明每个修改的原因

输出格式：
- 先运行测试，报告结果
- 对每个失败的测试，分析原因
- 提出修复方案，等待确认
- 执行修复后，重新验证
"""

    async with ClaudeSDKClient(options=options) as client:
        print("Test Fixer Agent Started")
        print("=" * 50)

        # 第一阶段：运行测试并分析
        print("\nPhase 1: Running tests and analyzing failures...")

        await client.query(f"""{system_prompt}

请开始：
1. 首先运行测试套件
2. 分析所有失败的测试
3. 为每个失败提出修复方案

注意：在这个阶段只分析，不要修改任何文件。
""")

        analysis_result = []
        async for msg in client.receive_response():
            if msg.type == "text":
                print(msg.text)
                analysis_result.append(msg.text)
            elif msg.type == "tool_use":
                print(f"  [Tool] {msg.tool_name}...")

        # 等待用户确认
        print("\n" + "=" * 50)
        print("Analysis complete. Review the proposed fixes above.")
        confirm = input("Proceed with fixes? (y/n): ")

        if confirm.lower() != "y":
            print("Aborted by user")
            return

        # 第二阶段：执行修复
        print("\nPhase 2: Applying fixes...")

        # 切换到接受编辑模式
        await client.update_options(permission_mode="acceptEdits")

        await client.query("""
现在请执行你提出的修复方案。
修复完成后，重新运行测试验证。
""")

        async for msg in client.receive_response():
            if msg.type == "text":
                print(msg.text)
            elif msg.type == "tool_use":
                print(f"  [Tool] {msg.tool_name}: {msg.tool_input.get('file_path', msg.tool_input.get('command', ''))}")
            elif msg.type == "result":
                print(f"\nCompleted in {msg.duration_ms/1000:.1f}s")
                print(f"   Cost: ${msg.total_cost_usd:.4f}")
                print(f"   Turns: {msg.num_turns}")


if __name__ == "__main__":
    asyncio.run(run_test_fixer())
```

执行测试修复 Agent ，可以看到它自动完成了从运行测试、分析失败、到修复代码、验证结果的完整流程。整个过程中，Agent 精准识别了两个失败测试的根因，一个是模型默认值变更，一个是 API 路径更新，并提出了合理的修复方案。

```
$ python test_fixer.py

Test Fixer Agent Started
==================================================

Phase 1: Running tests and analyzing failures...
  [Tool] mcp__test-tools__run_tests...

Test Results:
- Total: 200
- Passed: 198
- Failed: 2

Failed Tests Analysis:

1. tests/test_user.py::test_user_creation
   Error: AssertionError: expected 'active' but got 'pending'
   Analysis: The User model's default status was changed from 'active' to 'pending'
             in commit abc123, but the test wasn't updated.
   Proposed Fix: Update the test to expect 'pending' status, OR restore the
                 default to 'active' if that was unintentional.

2. tests/test_api.py::test_get_user_endpoint
   Error: 404 Not Found
   Analysis: The endpoint path was changed from /api/user to /api/users (plural)
             but the test still uses the old path.
   Proposed Fix: Update the test to use /api/users

==================================================
Analysis complete. Review the proposed fixes above.
Proceed with fixes? (y/n): y

Phase 2: Applying fixes...
  [Tool] Edit: tests/test_user.py
  [Tool] Edit: tests/test_api.py
  [Tool] mcp__test-tools__run_tests...

All tests passed! (200/200)

Completed in 45.3s
   Cost: $0.0821
   Turns: 12
```

## 生产环境最佳实践

本课的最后，我们来介绍一系列的生产环境中应用 SDK 的的最佳实践。

**成本控制**

将 Agent 部署到生产环境时，成本控制是第一个需要关注的问题。Agent 的每一轮工具调用都会消耗 token，而不受控的 Agent 可能在一次任务中消耗大量 API 额度。以下策略能帮助你有效控制成本：选择合适的模型（简单任务用 Haiku 而非 Sonnet）、限制最大轮次、限制工具集（减少不必要的操作），以及在运行时监控累计成本。

```
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    # 使用更便宜的模型处理简单任务
    model="haiku",

    # 限制轮次
    max_turns=20,

    # 限制工具（减少不必要的操作）
    allowed_tools=["Read", "Grep", "Glob"],  # 只读
)

# 监控成本
async for msg in client.receive_response():
    if msg.type == "result":
        if msg.total_cost_usd > 0.50:
            logger.warning(f"High cost query: ${msg.total_cost_usd}")
```

**错误重试**

网络波动、API 限流、临时性服务中断——这些问题在生产环境中不可避免。一个健壮的 Agent 应用需要内置重试机制。下面的实现使用指数退避策略：第一次失败后等 1 秒重试，第二次等 2 秒，第三次等 4 秒。这种策略既避免了对 API 的过度请求，又在大多数临时性故障中能自动恢复。

```
import asyncio
from claude_agent_sdk import ClaudeAgentError

async def resilient_query(client, prompt, max_retries=3):
    """带重试的查询"""
    for attempt in range(max_retries):
        try:
            await client.query(prompt)
            results = []
            async for msg in client.receive_response():
                results.append(msg)
                if msg.type == "error":
                    raise ClaudeAgentError(msg.error)
            return results

        except ClaudeAgentError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                raise
```

**超时处理**

Agent 任务可能因为各种原因卡住，等待一个永远不会返回的 API 调用，或者陷入无意义的推理循环。设置合理的超时时间是防止资源浪费的重要手段。Python 3.11 引入的  asyncio.timeout 上下文管理器，让超时处理变得非常优雅。

```
import asyncio

async def query_with_timeout(client, prompt, timeout=300):
    """带超时的查询"""
    try:
        await client.query(prompt)

        async with asyncio.timeout(timeout):
            results = []
            async for msg in client.receive_response():
                results.append(msg)
            return results

    except asyncio.TimeoutError:
        await client.interrupt()
        logger.error(f"Query timed out after {timeout}s")
        raise
```

**审计日志**

在企业环境中，所有 Agent 操作都应该被记录下来。审计日志不仅用于调试，更是合规要求。下面的  AuditLogger 以 JSONL 格式（每行一个 JSON 对象）记录所有工具调用，包括时间戳、工具名称、输入参数和调用 ID。这种格式便于后续用 ELK Stack 或 Splunk 等日志分析工具处理。

```
import json
from datetime import datetime

class AuditLogger:
    def __init__(self, log_file="agent-audit.jsonl"):
        self.log_file = log_file

    def log(self, event_type, data):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "data": data
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

audit = AuditLogger()

async def audited_tool_usage(input_data, tool_use_id, context):
    """审计所有工具使用"""
    audit.log("tool_use", {
        "tool": input_data["tool_name"],
        "input": input_data["tool_input"],
        "tool_use_id": tool_use_id
    })
    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="*", hooks=[audited_tool_usage])
        ]
    }
)
```

**总结一下**

这一讲我们深入学习了 Claude Agent SDK 的高级特性，并构建了一个完整的生产级 Agent。

自定义工具让 Agent 能够调用你定义的函数。使用  @tool 装饰器定义工具，使用  create_sdk_mcp_server 创建承载工具的 MCP 服务器，然后通过  mcp_servers 选项注入到 Agent 中。工具命名遵循  mcp__{服务器名}__{工具名} 格式。设计工具时要遵循单一职责、清晰描述、安全优先的原则。

Hooks 系统让你能够在 Agent 执行的各个阶段插入自定义逻辑。PreToolUse 在工具执行前触发，可以允许、拒绝或修改工具输入；PostToolUse 在工具执行后触发，适合日志记录和后处理。canUseTool 是另一种权限控制方式，更简单但功能有限。

权限管理是构建安全 Agent 的关键。SDK 提供四道防线：权限模式（全局设置）、工具白名单 / 黑名单（工具级别）、canUseTool 回调（运行时检查）、Hooks（最细粒度控制）。这四道防线应该配合使用，形成分层防御。

流式会话是生产级应用的首选模式。它支持多轮对话、中断执行、动态切换权限、自定义权限请求处理。相比单次  query() 调用，流式会话提供了更丰富的交互能力和更精细的控制。

实战项目展示了如何将这些特性组合起来。测试修复 Agent 使用自定义工具运行测试、使用 Hooks 控制文件修改权限、使用流式会话实现两阶段工作流（先分析后修复）。这个模式可以推广到许多类似场景，代码审查、文档生成、数据处理等。

下面，我想送给大家一份生产级 Agent 上线清单，把 Agent 部署到生产环境前，你可以过一遍这个清单。

![img](https://static001.geekbang.org/resource/image/01/89/0112f01b4yy4253b253e22f987cb9289.jpg?wh=3938x1195)

希望大家利用好 Agent SDK，设计出功能强大，可用而又可靠的 Agent 系统！

# 23｜化零为整：Plugins 插件打包与分发

> 释题：化零为整。把散落各处的 Commands、Skills、Agents、Hooks、MCP 配置打包成一个可安装、可升级、可分享的插件——项目“团队能力包”将完整演示这个过程。

至此你基本上已经掌握了 Claude Code 全局的方方面面。而上两讲我们又通过 Agent SDK，先用 Python/TypeScript 代码驱动 Claude 执行任务，再深入探索了多轮对话和流式处理等高级模式。此时此刻，你已经掌握了从交互式使用到代码驱动的全部能力。

最后，还剩下一个问题我们还没有回答，这些能力怎么传递给别人？（课程群用户也提到了工作场景中这类困惑“我项目很多同事在维护， 一人好几个 Skill，工作流除了他们自己知道怎么用，别人都不知道”。）

你写了一个好用的  /review 命令，同事想用，你说“把这个文件复制到  .claude/commands/ 下面”。你配了一个安全扫描代理，新人想用，你说“把  agents/ 目录拷过去，然后再配一下 MCP 服务器”。你设了一套 Hooks 自动格式化，团队想统一，你说“把  settings.json 里的 hooks 配置合并进去”。

一个两个还行，十个八个就乱了。文件散落在各处，版本无法追踪，配置因人而异。你从独行侠变成了布道者，但效率反而更低了。这就是本讲要解决的问题。插件系统让你把所有的工具、命令、配置、规范打包成一个整体。新人入职时，只需要一条命令：

```
/plugin install @our-company/dev-toolkit
```

数据库连接、测试命令、代码审查规范、Git 工作流全部就位。30 分钟的入职培训变成了 30 秒的安装命令。

这就是插件的终极价值，把知识变成资产，把重复变成复用，把个人经验变成团队能力。

**理解插件：Claude Code 的“应用商店“**

如果说 Claude Code 是一把瑞士军刀，那么插件就是可以插拔的工具模块。插件是一种轻量级的打包和分享方式，可以组合斜杠命令、子代理、MCP 服务器和 Hooks。你可以用一条命令安装插件，在终端和 VS Code 中都能使用。

一个插件可以包含以下五类组件，每一类我们在前面的课程中都已经深入学习过。

![img](https://static001.geekbang.org/resource/image/2e/3a/2eee295269ca9f1d76a646d3yy46b23a.jpg?wh=1763x768)

插件的价值不在于它引入了新的机制，而在于它提供了一个标准化的打包和分发方式。你在前 20 讲里学到的所有扩展能力，都可以通过插件系统组合、封装、传递给他人。

在没有插件之前，团队协作依赖的是文档、脚本和口耳相传。让我们对比一下这两种方式的差异。

![img](https://static001.geekbang.org/resource/image/9e/b6/9e37ce8c4284b217a8b6962508ccd6b6.jpg?wh=2006x775)

手动配置的根本问题不是麻烦——麻烦只是表象。根本问题是不一致。当 15 个人各自配置时，你得到的是 15 种微妙不同的开发环境。插件把“约定”变成了“约束”，从“应该这样做“变成“只能这样做”。

根据  [Claude Plugins 社区](https://claude-plugins.dev/)的统计，目前已有超过 10,000 个插件和 50,000 个 Agent Skills 可供使用。插件来源包括三个层级。

1. 官方市场：Anthropic 维护的  [claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
2. 社区市场：开发者贡献的公开插件
3. 企业市场：公司内部的私有插件

![img](https://static001.geekbang.org/resource/image/90/51/907ac6b2a120cfe25d959a3933eaf851.png?wh=1536x1024)

有人说，Claude Code 的插件市场就像是 AI 辅助开发工作流的 npm。去中心化的来源，任何人都可以托管市场，一条命令安装。这个类比非常精准。npm 改变了 JavaScript 生态的协作方式，让开发者不再重复造轮子。Claude Code 的插件系统正在对 AI 辅助开发做同样的事情，把个人的最佳实践变成社区的公共资产。

**插件的目录结构**

根据[官方文档](https://code.claude.com/docs/en/plugins)，插件的标准结构如下。理解这个结构是创建插件的第一步，因为 Claude Code 依赖固定的目录约定来发现和加载各类组件：

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json        # 插件元数据（必需）
├── commands/              # 斜杠命令（可选）
│   ├── review.md
│   └── deploy.md
├── agents/                # 子代理（可选）
│   ├── security-scanner.md
│   └── code-reviewer.md
├── skills/                # Agent Skills（可选）
│   └── react-patterns/
│       └── SKILL.md
├── hooks/                 # Hooks 配置（可选）
│   └── hooks.json
├── .mcp.json              # MCP 服务器配置（可选）
└── README.md              # 插件文档
```

> 咖哥发言：只有  plugin.json 放在  .claude-plugin/ 目录内，其他所有目录（commands、agents、skills、hooks）都在插件根目录下。注意不要把 commands 等目录也放进  .claude-plugin/ 里。

**plugin.json：插件的身份证**

每个插件必须有  .claude-plugin/plugin.json 文件。这个文件的作用类似于 npm 的  package.json——它定义了插件的身份、版本和描述信息，是 Claude Code 识别和管理插件的唯一入口：

```
{
  "name": "team-toolkit",
  "version": "1.0.0",
  "description": "团队标准开发工具包：代码审查、测试、部署一体化",
  "author": "DevOps Team",
  "repository": "https://github.com/our-company/team-toolkit",
  "license": "MIT",
  "keywords": ["team", "devops", "workflow", "code-review"]
}
```

各字段的含义和说明如下表。

![img](https://static001.geekbang.org/resource/image/5f/78/5fdd8f7bb2ed001a0ae21aa68da77078.jpg?wh=2139x1028)

![img](https://static001.geekbang.org/resource/image/68/7f/6885a58422265398d439f7b081505d7f.jpg?wh=1950x1294)

**添加斜杠命令**

命令是插件中用户感知最直接的组件。在  commands/ 目录下创建 Markdown 文件，文件名（不含  .md）即为命令名。命令文件的格式与我们在第 10 讲中学习的 Slash Commands 完全一致，frontmatter 定义元数据，正文定义行为指令。

commands/review.md

```
---
name: review
description: 对当前文件或目录进行代码审查
---

当用户运行 `/review [target]` 时，执行代码审查。

## 审查流程

1. 如果指定了 target，审查该文件或目录
2. 如果没有指定，审查当前打开的文件
3. 如果没有上下文，询问用户

## 审查要点

- 代码质量：命名规范、DRY 原则、复杂度
- 潜在 Bug：边界条件、空值处理、类型错误
- 安全问题：输入验证、敏感数据、注入风险
- 性能问题：不必要的循环、内存泄漏
- 最佳实践：框架惯例、设计模式

## 输出格式

​```markdown
## 代码审查报告

**文件**: {file_path}
**审查时间**: {timestamp}

### 发现的问题

🔴 **严重** (必须修复)
- [问题描述] (行号)

🟡 **警告** (建议修复)
- [问题描述] (行号)

🔵 **建议** (可选改进)
- [问题描述] (行号)

### 总结

[1-2 句总结]
```

安装插件后，命令会带上插件名称作为命名空间，避免不同插件的命令冲突。这个机制与编程语言中的模块命名空间是同一个思路。

- 插件名：team-toolkit
- 命令文件：commands/review.md
- 实际命令：/team-toolkit:review

如果只有一个命令或命令名唯一，也可以直接用  /review。Claude Code 会自动解析，优先匹配唯一命令名。

命令可以接受参数，使用  $ARGUMENTS 占位符接收用户输入。在 Markdown 中说明参数格式，让 Claude 知道如何解析。下面这个 TODO 命令展示了如何设计一个支持优先级和指派人的参数化命令：

commands/todo.md

```
---
name: todo
description: 添加 TODO 注释，支持优先级和指派人
---

用法：`/todo [优先级] [消息] [@指派人]`

## 参数

- `优先级`（可选）：
  - `!` 或 `high` → 高优先级
  - `?` 或 `discuss` → 待讨论
  - 默认 → 普通优先级

- `消息`：TODO 的内容

- `@指派人`（可选）：指定负责人

## 示例
/todo 修复登录验证 → // TODO: 修复登录验证
/todo ! 紧急修复安全漏洞 → // TODO [HIGH]: 紧急修复安全漏洞
/todo ? 是否需要缓存 @john → // TODO [DISCUSS @john]: 是否需要缓存

## 行为

1. 自动检测当前文件的语言，使用正确的注释格式
2. 插入到光标位置或相关代码附近
3. 如果没有文件上下文，询问位置
```

**添加子代理**

子代理是插件中的“专业助手”。在  agents/ 目录下创建 Markdown 文件，每个文件定义一个具有特定职责、工具权限和行为准则的代理。这与我们在第 3-8 讲学习的子代理概念完全一致，区别在于现在它被打包进了插件，可以随插件一起安装和分发。

下面是一个安全扫描代理的完整定义。注意它只使用了 Read、Grep、Glob 三个只读工具——遵循我们在第 4 讲强调的最小权限原则。

agents/security-scanner.md

```
---
name: security-scanner
description: 扫描代码中的安全漏洞
tools: Read, Grep, Glob
model: sonnet
---

你是一个安全专家，专门识别代码中的安全漏洞。

## 扫描范围

重点检查：
1. **注入漏洞**：SQL 注入、命令注入、XSS
2. **认证问题**：弱密码、硬编码凭证、会话管理
3. **数据暴露**：敏感信息日志、不安全传输
4. **访问控制**：权限检查、路径遍历
5. **依赖风险**：已知漏洞的依赖包

## 工作流程

1. 使用 Glob 获取所有源代码文件
2. 使用 Grep 搜索可疑模式
3. 使用 Read 深入分析可疑代码
4. 生成结构化报告

## 输出格式

​```markdown
# 安全扫描报告

**扫描时间**: {timestamp}
**扫描范围**: {directory}

## 发现的漏洞

### 🔴 高危 (立即修复)

#### [漏洞名称]
- **文件**: path/to/file.js:42
- **类型**: SQL Injection
- **描述**: [详细描述]
- **修复建议**: [具体建议]

### 🟡 中危 (尽快修复)
...

### 🔵 低危 (建议修复)
...

## 统计

- 高危: X 个
- 中危: Y 个
- 低危: Z 个

## 注意事项
- 只报告有实际证据的问题，不要臆测
- 提供具体的修复建议，不只是指出问题
- 如果不确定是否是漏洞，标注为"疑似"
```

代理的 frontmatter 支持以下配置字段。其中  model 字段值得特别关注，对于只做扫描和分析的代理，使用 sonnet 模型就够了；对于需要快速修复简单问题的代理，haiku 更合适，速度更快、成本更低。

![img](https://static001.geekbang.org/resource/image/fd/4f/fdbcbf627f457ab68a5776a37c81364f.jpg?wh=1704x616)

与安全扫描代理不同，快速修复代理需要写入权限（Edit 工具），因为它的职责是直接修改代码。但它被严格限定在“小问题”范围内——拼写错误、缺失导入、简单语法错误。任何复杂的架构变更或安全问题都不在它的职责范围内，这是通过 prompt 中的明确边界来约束的。

agents/quick-fix.md

```
---
name: quick-fix
description: 快速修复小问题：拼写错误、缺失导入、简单 bug
tools: Read, Edit, Grep, Glob
model: haiku
---

你是快速修复专家。你的任务是**又快又准**地修复小问题。

## 你处理的问题

- 拼写错误
- 缺失的 import/require
- 简单语法错误
- 明显的空值检查遗漏
- 缺失的 return 语句
- Off-by-one 错误

## 你不处理的问题

- 架构变更
- 复杂重构
- 性能优化
- 安全问题（上报这些！）

## 工作流程

1. **识别问题**：阅读错误信息或用户描述
2. **定位问题**：找到确切的位置
3. **最小修复**：只改必要的代码
4. **验证语法**：确保不引入新错误

## 输出格式

\```markdown
## 已修复

**文件**: path/to/file.js
**行号**: 42
**问题**: 变量名拼写错误

\```diff
- const usrName = user.name;
+ const userName = user.name;
\```

**完成。** 修正了变量名拼写。
\```

## 原则

- **快**：不要过度解释
- **小**：最小化修改
- **诚实**：问题复杂就直说，不要硬修
```

**添加 Skills**

Skills 放在  skills/ 目录下，每个 Skill 是一个子目录。这与我们在第 9-14 讲学习的 Skills 系统完全一致，包含一个  SKILL.md 主文件，以及可选的  chapters/ 子目录用于渐进式披露。当 Skill 的知识量较大时，章节化结构可以避免一次性加载所有内容，节省上下文窗口。

```
skills/
└── react-patterns/
    ├── SKILL.md           # 主文件
    └── chapters/          # 可选：分章节
        ├── hooks.md
        ├── context.md
        └── performance.md
```

下面是一个 React 最佳实践 Skill 的示例。注意  description 字段的写法，它不是给人看的说明文档，而是给 Claude 看的触发器。当用户的请求与 description 中的关键词匹配时，Claude 会自动加载这个 Skill。

skills/react-patterns/SKILL.md

```
---
name: React 最佳实践
description: React 组件设计模式、Hooks 使用指南、性能优化技巧
---

# React 最佳实践

本技能包含 React 开发的最佳实践，帮助你编写高质量的 React 代码。

## 目录

- [Hooks 使用指南](./chapters/hooks.md)
- [Context 最佳实践](./chapters/context.md)
- [性能优化](./chapters/performance.md)

## 核心原则

1. **组件单一职责**：一个组件做一件事
2. **状态提升最小化**：状态放在需要它的最近公共祖先
3. **避免过早优化**：先让它工作，再让它快
4. **优先组合而非继承**：使用 children 和 render props

## 快速参考

### 自定义 Hook 命名

​```javascript
// 好的命名
useUser()
useLocalStorage()
useDebounce()

// 不好的命名
fetchUser()      // 不是 use 开头
useData()        // 太模糊

## 组件文件结构
ComponentName/
├── index.ts           # 导出
├── ComponentName.tsx  # 组件实现
├── ComponentName.test.tsx
├── ComponentName.styles.ts
└── types.ts           # 类型定义

```

**添加 Hooks**

Hooks 是插件中的自动触发器。在  hooks/ 目录下创建  hooks.json 配置文件，定义在 Claude 执行工具前后自动运行的检查脚本。这与 Hooks 事件驱动机制（参考第 15 讲）完全一致，只是现在它被封装在插件中，随插件安装自动生效。

hooks/hooks.json

```
{
  "hooks": [
    {
      "event": "PreToolUse",
      "matcher": "Bash",
      "command": ["bash", "./hooks/check-bash.sh"]
    },
    {
      "event": "PostToolUse",
      "matcher": "Write",
      "command": ["bash", "./hooks/auto-format.sh"]
    },
    {
      "event": "PostToolUse",
      "matcher": "Edit",
      "command": ["bash", "./hooks/auto-format.sh"]
    }
  ]
}
```

这个配置做了两件事，在每次 Bash 命令执行前检查是否包含危险模式（PreToolUse），在每次文件写入或编辑后自动格式化代码（PostToolUse）。

下面是两个 Hook 脚本的完整实现。第一个脚本是安全守门员，它从 stdin 读取 Claude 即将执行的 Bash 命令，与危险模式列表逐一比对，发现匹配就拒绝执行。这是一道看不见的防线，防止 Claude 在深夜加班时不小心执行了  rm -rf /等危险命令。

hooks/check-bash.sh

```
#!/bin/bash
# 检查 Bash 命令是否安全

# 从 stdin 读取输入
INPUT=$(cat)

# 提取命令
COMMAND=<!--§§MATH_0§§-->INPUT" | jq -r '.tool_input.command // empty')

# 危险模式列表
DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf ~"
    "sudo rm"
    "> /dev/"
    "chmod 777"
    "curl.*|.*sh"
    "wget.*|.*sh"
)

# 检查每个危险模式
for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if echo "<!--§§MATH_1§§-->pattern"; then
        # 输出拒绝决定
        cat << EOF
{
  "decision": "deny",
  "reason": "Blocked potentially dangerous command pattern: $pattern"
}
EOF
        exit 0
    fi
done

# 允许执行
echo '{"decision": "allow"}'
```

第二个脚本是自动格式化器，它检测被写入文件的扩展名，自动调用对应的格式化工具。Python 文件用 black，JavaScript/TypeScript 用 prettier，Go 文件用 gofmt。这样团队成员不需要记住各种格式化命令，也不会因为忘记格式化而产生风格不一致的代码。

hooks/auto-format.sh

```
#!/bin/bash
# 文件写入后自动格式化

INPUT=$(cat)
FILE_PATH=<!--§§MATH_2§§-->INPUT" | jq -r '.tool_input.file_path // empty')

if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# 根据文件类型格式化
case "$FILE_PATH" in
    *.py)
        if command -v black &> /dev/null; then
            black "$FILE_PATH" 2>/dev/null
        fi
        ;;
    *.js|*.ts|*.jsx|*.tsx)
        if command -v prettier &> /dev/null; then
            prettier --write "$FILE_PATH" 2>/dev/null
        fi
        ;;
    *.go)
        if command -v gofmt &> /dev/null; then
            gofmt -w "$FILE_PATH" 2>/dev/null
        fi
        ;;
esac

echo '{"decision": "allow"}'
```

**添加 MCP 服务器**

MCP（Model Context Protocol）是插件中最强大也最敏感的组件。它让 Claude 能够连接数据库、调用 API、访问文件系统等外部资源。在插件根目录创建  .mcp.json 文件来配置 MCP 服务器。

.mcp.json

```
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-postgres"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-filesystem"],
      "env": {
        "ALLOWED_PATHS": "${HOME}/projects"
      }
    }
  }
}
```

MCP 配置中可以使用  ${VAR_NAME} 引用环境变量。这是一个关键的设计决策——不要在配置文件中硬编码数据库密码或 API Token。用户安装插件后，需要在自己的环境中设置这些变量：

```
export DATABASE_URL="postgres://user:pass@localhost/db"
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
```

![img](https://static001.geekbang.org/resource/image/43/5c/43aa3c1a1784259a99976565b3b7985c.jpg?wh=1957x1286)

> 一个简单的判断标准：如果你不敢把  .mcp.json 里的连接信息发到公开频道，那说明这个配置有泄露风险，需要改用环境变量。

## 实战项目：团队能力包

前面我们逐一介绍了插件的各个组件。现在，让我们把它们组合在一起，构建一个完整的团队能力包插件。

项目背景是假设你在一个使用以下技术栈的团队：

- 前端：React + TypeScript
- 后端：Node.js + PostgreSQL
- 测试：Jest + Cypress
- 部署：Docker + Kubernetes

你要创建一个插件，包含代码审查命令、测试运行命令、部署命令、安全扫描代理、快速修复代理、React 最佳实践 Skill、安全检查 Hook，以及数据库查询 MCP。这些组件覆盖了开发流程的各个环节——从编码到审查，从测试到部署，从安全到知识沉淀。

![img](https://static001.geekbang.org/resource/image/e5/6e/e51c04415024f2df4799bc27b9d88b6e.png?wh=1536x1024)

下面是这个团队能力包的完整目录树。每个文件的内容我们在前面的章节中都已经详细介绍过，这里把它们按照插件规范组织在一起。

```
team-toolkit/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── review.md
│   ├── test.md
│   └── deploy.md
├── agents/
│   ├── security-scanner.md
│   └── quick-fix.md
├── skills/
│   └── react-patterns/
│       ├── SKILL.md
│       └── chapters/
│           ├── hooks.md
│           ├── context.md
│           └── performance.md
├── hooks/
│   ├── hooks.json
│   ├── check-bash.sh
│   └── auto-format.sh
├── .mcp.json
└── README.md
```

plugin.json

团队能力包的 plugin.json 如下

```
{
  "name": "team-toolkit",
  "version": "2.0.0",
  "description": "团队标准开发工具包：代码审查、测试、部署、安全扫描一体化",
  "author": "Platform Team",
  "repository": "https://github.com/our-company/team-toolkit",
  "license": "MIT",
  "keywords": [
    "team",
    "devops",
    "code-review",
    "testing",
    "deployment",
    "security"
  ]
}
```

代码审查命令

这是团队能力包中最常用的命令。它不仅检查代码质量，还覆盖了 TypeScript 类型安全、React 特定规范和安全问题。审查报告的结构化输出让团队成员能快速定位和修复问题。

commands/review.md

```
---
name: review
description: 对代码进行全面审查，输出结构化报告
---

当用户运行 `/review [target]` 时，执行代码审查。

## 审查维度

1. **代码质量**
   - 命名规范（camelCase/PascalCase）
   - DRY 原则（重复代码）
   - 函数长度（建议 < 30 行）
   - 圈复杂度（建议 < 10）

2. **TypeScript 特定**
   - 类型安全（避免 any）
   - 空值处理（可选链、空值合并）
   - 接口设计

3. **React 特定**
   - Hooks 规则
   - 组件拆分
   - 状态管理

4. **安全**
   - 输入验证
   - XSS 防护
   - 敏感数据处理

5. **测试**
   - 测试覆盖率
   - 边界条件

## 输出格式

\```markdown
# 代码审查报告

**目标**: {target}
**时间**: {timestamp}
**审查者**: Claude (team-toolkit v2.0.0)

## 总览

| 类别 | 发现 | 严重性 |
|------|------|--------|
| 代码质量 | X | 中 |
| 安全 | Y | 高 |
| 性能 | Z | 低 |

## 必须修复

### [问题标题]
**文件**: path/to/file.ts:42
**类型**: 安全漏洞

**问题**:
[详细描述]

**修复建议**:
\```typescript
// 建议的修复代码
\```

## 建议修复
...

## 可选改进
...

## 亮点

[做得好的地方]

---
*由 team-toolkit 生成*
\```
```

测试命令

测试命令不只是运行测试，它还会分析失败原因，判断是代码 bug 还是测试过时，并提供具体的修复建议。这个命令的  --fix 选项让 Claude 尝试自动修复失败的测试，把“发现问题”和“解决问题”合二为一。

commands/test.md

```
---
name: test
description: 运行测试并分析结果，失败时提供修复建议
---

用法：`/test [scope] [options]`

## 参数

- `scope`（可选）：
  - `unit` - 只运行单元测试
  - `e2e` - 只运行端到端测试
  - `all` - 运行全部（默认）

- `options`：
  - `--fix` - 尝试自动修复失败的测试
  - `--coverage` - 生成覆盖率报告

## 工作流程

1. 运行指定范围的测试
2. 收集测试结果
3. 对失败的测试：
   - 分析失败原因
   - 检查是代码 bug 还是测试过时
   - 提供修复建议
4. 如果指定了 --fix，尝试自动修复

## 输出格式

\```markdown
# 测试报告

## 结果

| 指标 | 值 |
|------|------|
| 总计 | 150 |
| 通过 | 147 |
| 失败 | 3 |
| 跳过 | 0 |
| 覆盖率 | 85% |

## 失败的测试

### test_user_creation
**文件**: tests/user.test.ts:42
**错误**: AssertionError: expected 'active' but got 'pending'

**分析**: User 模型的默认状态在 commit abc123 中从 'active' 改为 'pending'，但测试未更新。

**建议**: 更新测试以期望 'pending' 状态。

\```diff
- expect(user.status).toBe('active');
+ expect(user.status).toBe('pending');
\```

---
*由 team-toolkit 生成*
\```
```

部署命令

部署是最需要规范化的操作之一。手动部署时，每个人的步骤可能不同，遗漏检查项的风险很高。这个命令把部署流程固化为标准步骤，并内置了安全检查，确保没有硬编码密钥、没有已知漏洞的依赖、所有环境变量都已配置。

commands/deploy.md

```
---
name: deploy
description: 部署应用到指定环境
---

用法：`/deploy [environment]`

## 环境

- `staging` - 测试环境（默认）
- `production` - 生产环境（需要额外确认）

## 部署流程

### Staging

1. 运行 lint 检查
2. 运行单元测试
3. 构建 Docker 镜像
4. 推送到 staging 集群
5. 运行冒烟测试
6. 报告部署状态

### Production

1. 确认 staging 部署成功
2. 确认所有测试通过
3. 请求用户确认
4. 创建 Git tag
5. 构建生产镜像
6. 蓝绿部署到生产集群
7. 健康检查
8. 报告部署状态

## 安全检查

部署前自动检查：
- [ ] 没有硬编码的密钥
- [ ] 依赖没有已知漏洞
- [ ] 所有环境变量已配置

## 回滚

如果部署失败，自动提供回滚命令：
\```
kubectl rollout undo deployment/app -n production
\```
```

团队能力包的 README.md

README 是插件的门面。它决定了用户是否愿意安装你的插件，也是安装后的第一份参考文档。一个好的 README 应该让用户在 30 秒内了解插件能做什么、怎么安装、怎么使用。

```
# Team Toolkit

团队标准开发工具包，提供代码审查、测试、部署、安全扫描一体化解决方案。

## 安装

\```bash
/plugin install team-toolkit@our-company
\```

## 功能

### 命令

| 命令 | 说明 |
|------|------|
| `/review [target]` | 代码审查 |
| `/test [scope]` | 运行测试 |
| `/deploy [env]` | 部署应用 |

### 代理

| 代理 | 说明 |
|------|------|
| `security-scanner` | 安全漏洞扫描 |
| `quick-fix` | 快速修复小问题 |

### Skills

| Skill | 说明 |
|-------|------|
| `react-patterns` | React 最佳实践 |

### MCP 服务器

| 服务器 | 说明 |
|--------|------|
| `postgres` | 数据库查询 |
| `github` | GitHub API |

## 环境变量

\```bash
# 数据库连接（用于 postgres MCP）
export DATABASE_URL="postgres://..."

# GitHub Token（用于 github MCP）
export GITHUB_TOKEN="ghp_..."
\```

## 更新日志

### v2.0.0

- 新增：`/deploy` 命令
- 新增：`security-scanner` 代理
- 改进：`/review` 输出格式
- 修复：Hook 脚本兼容性问题

### v1.0.0

- 初始版本

## 贡献

欢迎提交 PR！请确保：
1. 代码通过 lint 检查
2. 更新相关文档
3. 添加测试（如适用）

## 许可证

MIT
```

**发布与分发**

插件开发完成后，下一步是让别人能够使用它。Claude Code 的插件分发基于 Git，插件本质上就是一个 Git 仓库。

在发布前，使用  --plugin-dir 参数从本地目录加载插件进行测试。这个步骤很重要，它让你在不发布的情况下验证所有组件是否正常工作。

```
claude --plugin-dir ./team-toolkit
```

加载成功后，你可以测试所有命令（/team-toolkit:review、/team-toolkit:test、/team-toolkit:deploy），确认代理和 Skills 是否被正确识别，以及 Hooks 是否在预期时机触发。

插件发布就是推送到远程 Git 仓库。使用 Git tag 标记版本号，让用户可以安装特定版本。

```
cd team-toolkit
git init
git add .
git commit -m "Initial release v1.0.0"
git tag v1.0.0
git remote add origin https://github.com/our-company/team-toolkit
git push -u origin main --tags
```

**创建私有市场**

如果你的团队有多个插件需要管理，可以创建一个私有市场。私有市场本身也是一个 Git 仓库，包含一个  marketplace.json 文件，列出所有可用的插件及其版本。

marketplace.json

```
{
  "name": "Our Company Plugins",
  "description": "内部插件市场",
  "plugins": [
    {
      "name": "team-toolkit",
      "description": "团队标准开发工具包",
      "repository": "https://github.com/our-company/team-toolkit",
      "version": "2.0.0"
    },
    {
      "name": "db-tools",
      "description": "数据库操作工具",
      "repository": "https://github.com/our-company/db-tools",
      "version": "1.2.0"
    }
  ]
}
```

用户可以添加你的市场，然后从中安装插件：

```
/plugin marketplace add our-company/claude-plugins
```

然后就可以安装市场中的插件：

```
/plugin install team-toolkit@our-company
```

发布新版本时，需要同步更新四个地方：

1. 更新  plugin.json 中的版本号
2. 更新  README.md 中的更新日志
3. 创建新的 Git tag
4. 如果有私有市场，更新  marketplace.json

用户更新插件只需一条命令：

```
/plugin update team-toolkit
```

## Plugins 最佳实践

经过前面的实战，让我们提炼几条插件设计的核心原则。

单一职责，一个插件应该解决一类问题。不要创建万能插件，这与软件工程中的单一职责原则是同一个道理：职责越集中，维护越容易，复用越灵活。

```
好的：
- db-tools — 数据库操作
- git-workflow — Git 工作流
- security-check — 安全检查

不好的：
- everything-plugin — 什么都有
```

渐进式复杂度，从简单开始，逐步添加功能。不要试图在第一个版本就做到完美。每个版本解决一个明确的问题，让用户有时间适应和反馈。

```
v1.0.0: 基础的代码审查命令
v1.1.0: 添加安全扫描代理
v1.2.0: 添加 React Skill
v2.0.0: 添加 MCP 集成
```

最小权限，只请求必要的工具权限。一个只做分析的代理不需要 Write 和 Edit 工具，一个只做查询的 MCP 不需要写入权限。

```
# 只需要读取的代理
tools: Read, Grep, Glob

# 不要这样（权限过大）
tools: Read, Write, Edit, Bash, Task
```

文档是第一优先级，没有文档的插件是没有价值的。你可能觉得代码和配置“不言自明“，但安装你插件的用户不这么想。他们需要知道每个命令怎么用、每个环境变量什么意思、出了问题怎么排查。文档中必须包含安装方法、每个命令的用法和示例、环境变量说明、更新日志；最好包含使用场景、常见问题和贡献指南。

版本管理——使用语义化版本（Semantic Versioning），让用户清楚每次更新的影响范围。

![img](https://static001.geekbang.org/resource/image/71/3a/7172f9ea57cdb5796da29df821ff573a.jpg?wh=2220x823)

![img](https://static001.geekbang.org/resource/image/27/91/272028995ed06998f0f10ea3f3aa8f91.jpg?wh=2791x1789)

![img](https://static001.geekbang.org/resource/image/2c/be/2c3e8a760f037ecebbb451ed24f434be.png?wh=1536x1024)

## 总结一下

这一讲，我们学习了 Claude Code 插件系统的完整内容，并构建了一个“团队能力包”插件。

插件是 Claude Code 扩展能力的标准打包方式。它可以包含斜杠命令（快捷操作）、子代理（专业助手）、Skills（领域知识）、Hooks（自动化行为）和 MCP 服务器（外部工具连接）。这些组件打包在一起，用户只需一条命令就能安装全部功能。

插件的目录结构是固定的：.claude-plugin/plugin.json 是必需的元数据文件，commands/、agents/、skills/、hooks/ 目录存放各类组件，.mcp.json 配置外部工具连接。所有组件目录都在插件根目录下，只有  plugin.json 在  .claude-plugin/ 内。

发布插件就是推送 Git 仓库。你可以发布到公开的社区市场，也可以创建私有市场供团队使用。用户通过  /plugin marketplace add 添加市场，通过  /plugin install 安装插件。

设计插件时要遵循单一职责、最小权限、文档优先的原则。一个好的插件应该专注于解决一类问题，只请求必要的权限，并提供完整的使用文档。版本管理使用语义化版本，让用户清楚每次更新的影响。

回顾这一讲的内容，你会发现一个有趣的模式。Commands、Agents、Skills、Hooks、MCP，这些我们在前 20 讲中逐一学习的独立组件，在插件系统中被统一成了一个整体。这不是简单的“打包”，而是一种系统级的思维转变：从“我有一堆好用的工具”到“我有一个可安装的解决方案”。这个转变的意义在于，它让你的工程经验变得可传递、可版本化、可持续迭代。把知识变成资产，把重复变成复用，把个人经验变成团队能力。