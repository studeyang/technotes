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

<!-- 20260601 -->

## 实战项目：完整的 CI/CD 审查系统

前面我们分别学习了 Headless 模式的各个组件——输出格式、管道集成、GitHub Actions、Pre-commit Hook。现在让我们把它们组装成一个完整的自动化审查系统。这个系统涵盖了从本地开发到远程 CI 的完整链路。

![img](https://static001.geekbang.org/resource/image/dc/49/dc120ec7e1a9e4c3dd49c9a99d013049.jpg?wh=2461x1834)

下面的目录结构展示了一个完整的 CI/CD 审查系统需要哪些文件。.github/workflows/ 下是 GitHub Actions 配置，scripts/ 下是本地审查脚本，.git/hooks/ 下是 pre-commit hook，CLAUDE.md 则为所有环节提供统一的审查规范。

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

CLAUDE.md 在 Headless 模式中扮演着关键角色。无论是 pre-commit hook 还是 GitHub Actions 中的 Claude，都会读取项目根目录的 CLAUDE.md 来了解审查规范。这意味着你可以通过一份配置文件，统一所有环节的审查标准。

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

scripts/review.sh 是一个独立的本地审查脚本，开发者可以在任何时候手动运行它来审查代码。它与 CI 中的审查使用相同的 Claude 能力，但运行在本地环境中。脚本包含了完整的错误处理、检查 API Key 是否设置、Claude Code 是否安装以及结果保存功能，每次审查的报告都会保存为带时间戳的 Markdown 文件。

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

# 检查 Claude Code
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

【新修订内容】

下面是生产级的 GitHub Action 配置。目前这个版本增加了变更文件计数、结构化的审查 prompt、以及关键问题检测逻辑。如果 Claude 给出 request_changes 结论，工作流将以失败状态退出，从而阻止 PR 合并。

设计要点包括以下几条。

- Verdict 用唯一 sentinel token（request_changes），不能用“Approved / Needs Changes / Request Changes”这种单词列表，否则 grep 会把 prompt 模板里列出的选项当成实际结论，几乎每次都误判。
- 多行变量通过 env: 传，不通过 ${{ }} 直接拼进 shell，避免命令注入。
- wc -l 在空 diff 时返回 1，改用 grep -c .。
- claude 失败时显式报错，不要让 set -eo pipefail 静默挂掉。
- 下游全部从 review.md 文件读，不通过 ${{ steps.review.outputs.result }} 把多行 markdown 拼进 shell / JS。

完整文件参见 .github/workflows/claude-review.yml：

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

      - name: Get changed files
        id: changed
        run: |
          FILES=$(git diff --name-only "origin/${{ github.base_ref }}...HEAD" || true)
          # grep -c . 在空字符串时返回 0；wc -l 会把空字符串错误地计成 1
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
          # 通过 env 传变量，避免 ${{ }} 直接拼进 shell 导致命令注入
          CHANGED_FILES: ${{ steps.changed.outputs.files }}
          CHANGED_COUNT: ${{ steps.changed.outputs.count }}
        run: |
          PROMPT="Review this Pull Request.

          ## Changed Files (${CHANGED_COUNT} files)
          ${CHANGED_FILES}

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

          ### Verdict
          Output EXACTLY ONE sentinel token on its own line — do not echo
          the option list:
          <VERDICT>approved</VERDICT>
          <VERDICT>needs_changes</VERDICT>
          <VERDICT>request_changes</VERDICT>"

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

> 勘误：本讲早期版本的这个示例用“Approved / Needs Changes / Request Changes”做 verdict，再用 grep -qF "Request Changes" 判定，结果 grep 把 prompt 模板里列出的选项也当成结论，导致 workflow 几乎每次都被自己的 verdict 检查触发 exit 1。感谢 Geek_122fe2 朋友的 bug 报告。



**安全与成本控制**

在 CI/CD 中运行 AI 代理，安全是绕不开的话题。与人类开发者不同，AI 代理不会主动判断“这个操作是否安全”，它只会尽力完成你给它的任务。所以安全的责任在配置端——你需要通过参数和权限设置，确保 Claude 只能做你允许它做的事。

根据 [eesel.ai](https://www.eesel.ai/blog/claude-code-automation) 的指南，在 CI/CD 中运行 Claude Code 时应该限制权限。最小权限原则的核心思想是：只给 Claude 完成任务所需的最少权限，不多给一分。对于只读审查任务，只允许 Read、Grep、Glob 三个工具就够了；如果不需要执行任意命令，明确禁用 Bash 工具；对于简单任务，限制执行轮次以防止无限循环。

```bash
# 只读操作
claude -p "分析代码" --allowedTools Read,Grep,Glob

# 禁用危险工具
claude -p "任务" --disallowedTools Bash

# 限制执行轮次
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

[Skywork AI](https://skywork.ai/blog/how-to-integrate-claude-code-ci-cd-guide-2025/) 的指南中有这样的警告：

> 在 CI/CD 流水线中使用无人监督的 Claude Code 自动化的主要风险是：AI 可能引入细微 Bug、误解核心目标，或在尝试完成任务时增加技术债务。最好从有监督的任务开始，并在让 AI 对生产代码库进行无监督修改之前加入人工审查步骤。

这段警告值得反复阅读。AI 代理在无人监管环境中的最大风险不是“做错事”，而是看起来做对了，但引入了微妙的问题。一个 AI 自动修复的 Bug 可能通过了所有现有测试，但在某个边缘条件下引入了新的问题。比如 AI 可能自动“优化”了一段缓存逻辑，代码更简洁了，也通过了所有测试。但它不小心去掉了一个过期清除的判断逻辑，结果缓存数据长期不更新，线上就会悄悄变脏。

建议采用渐进式采纳策略。

1. 从只读开始：先让 Claude 只做审查，不做修改。
2. 人工审批：Claude 的修改建议需要人工确认后才能合并。
3. 限制范围：不要让 Claude 自动修改核心业务逻辑。
4. 审计日志：记录所有 Claude 的操作。

![img](https://static001.geekbang.org/resource/image/56/66/56cd235f412dab9b4a0cfb5c07966966.jpg?wh=2634x1269)

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
    ANTHROPIC_API_KEY: $ANTHROPIC_API_KEY
  only:
    - merge_requests
```

> 注意变量引用方式的差异——GitLab 使用  $VARIABLE_NAME，而不是 GitHub 的  ${{ secrets.VARIABLE_NAME }}。

CircleCI：CircleCI 使用 `config.yml`，放在 .circleci/ 目录下。它的配置结构是 jobs -> steps，与 GitHub Actions 的 jobs -> steps 概念对应。

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

## 总结一下

这一讲我们学习了 Claude Code 的 Headless 模式，让 AI 助手在无人值守的情况下自动工作。

Headless 模式的核心是  -p 标志。它告诉 Claude Code 不要打开交互界面，直接执行任务并输出结果。配合  --output-format 可以选择 text、json 或 stream-json 三种输出格式，分别适用于人类阅读、程序解析和实时监控。

Claude Code 的一个独特优势是它能无缝融入 Unix 管道。你可以用  cat file | claude -p "分析" 将文件内容传给 Claude，也可以将 Claude 的输出通过管道传给其他工具。这种设计让 Claude 成为你工具链中的一环，而不是一个孤立的应用。

GitHub Actions 是 Headless 模式最常见的应用场景。Anthropic 提供了官方 Action，支持 @claude 提及触发和自动化 prompt 两种模式。通过配置工作流，你可以实现 PR 自动审查、lint 错误自动修复、文档自动生成等功能。

安全是 CI/CD 集成的关键考量。应该限制 Claude 可用的工具（用  --allowedTools）、控制执行轮次（用  --max-turns）、使用 Secrets 管理 API Key，并在让 Claude 自动修改代码前加入人工审查步骤。

Headless 模式让 Claude Code 从一个“需要人坐在终端前”的工具，进化为可以 7x24 小时自动工作的智能助手。开篇故事中，那个跨时区团队的 PR 审查周期从 36 小时缩短到 8 小时，正是这种进化的体现。

最后说个题外话（但我们在工程里要引起重视），最近发生的源码泄露事件，再次提醒我们，CI/CD 发布管道是安全链中最薄弱的环节。面对“无人值守”的诱惑，要有设计完善的、真正启用的防护和审核机制兜底。更多关于这个热点事件的启示和架构探讨，可以移步去看我这周三发布的加餐，期待你在评论区分享交流。

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

今天我们要更进一步，学习 Claude Agent SDK——它把 Claude Code 的所有能力封装成了可编程的接口。你可以用 Python 或 TypeScript 编写代码，像调用普通函数一样调用 AI Agent。

## 什么是 Agent SDK

Claude Agent SDK 提供了可编程的 Claude Code。它不是一个新的模型 API，而是对 Claude Code 这个 Agent 系统的完整封装。你通过 SDK 调用的不是一个简单的文本生成接口，而是一个完整的 Agent 循环——Claude 会自主决定使用哪些工具、读取哪些文件、执行哪些命令，然后把结果返回给你。

正如 Anthropic 官方文档所述：

> Claude Agent SDK 让你能够构建自主运行的 AI Agent——它们可以读取文件、执行命令、搜索网络、编辑代码等。SDK 提供了驱动 Claude Code 的相同工具、代理循环和上下文管理能力。

简单来说，这三种方式形成了一个递进关系：CLI 是手动操作，Headless 是自动化脚本，SDK 是可编程集成。每一步都在降低人工干预的程度，提升集成的灵活性。

![img](https://static001.geekbang.org/resource/image/58/f8/58eaa16e20968156faafc65814d46af8.jpg?wh=2711x750)

![img](https://static001.geekbang.org/resource/image/b0/8b/b0569f9757943d81ef5bc243ff9b368b.jpg?wh=2641x1449)

**SDK 能力一览**

下面这张表列出了 Agent SDK 赋予你的全部能力。每一项都对应 Claude Code 本身的一种工具，SDK 让你可以在自己的代码中精确控制这些工具的使用。

![img](https://static001.geekbang.org/resource/image/44/17/447c5ba9dfaf1ce2cc300796da2c0617.jpg?wh=2649x1127)



理解了这张表，你就能回答前面问题了：用户上传代码后，Agent 可以用 Read 读取文件、用 Grep 搜索模式、用 Glob 遍历目录、用 Bash 运行测试——所有这些操作都在你的应用后端自动完成，用户只需要等待报告生成。

**安装与环境配置**

在开始编写代码之前，你需要安装 SDK 并配置好环境。这个过程很简单，但有几个关键点需要注意。

Python 安装要求 Python 3.10 及以上版本。之所以有这个版本要求，是因为 SDK 大量使用了async/await 语法和  match/case 模式匹配等现代 Python 特性。如果你的系统 Python 版本较低，建议使用  pyenv 或  conda 管理多个 Python 版本。

```
# 要求 Python 3.10+
pip install claude-agent-sdk
```

安装完成后，用一段简单的代码验证安装是否成功：

```
from claude_agent_sdk import query
print("Claude Agent SDK installed successfully!")
```

SDK 需要 Anthropic API Key 才能运行。这个 Key 是你与 Anthropic 服务器通信的凭证，所有的模型调用和 Token 消耗都会计入这个 Key 对应的账户。

最常见的配置方式是通过环境变量：

```
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

**两种使用方式**

Agent SDK 提供了两种使用方式，适用于不同场景。理解它们的区别是正确使用 SDK 的第一步。你可以把它们类比为 Python 中的  requests.get() 和  requests.Session()，前者是无状态的一次性调用，后者是有状态的会话管理。

1、query() 函数：简洁高效

query() 是最简单的方式，适合轻量级用例。它接收一个 Prompt 字符串，返回一个异步迭代器，你可以逐条接收 Agent 产生的消息。整个过程不需要手动管理连接、配置选项或处理会话状态，SDK 帮你搞定一切。

这种设计的好处是显而易见的：当你只想快速验证一个想法、写一个脚本、或者做一次性的分析时，不需要写二十行初始化代码。一个函数调用就够了。

```
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

与开箱即用的query() 不同，ClaudeSDKClient 要求你显式地创建客户端、配置选项、管理连接生命周期。这种显式性是刻意为之的，在生产环境中，你需要明确知道 Agent 能做什么、不能做什么、在什么条件下停止。隐式的默认值在生产中往往是 Bug 的温床。

```
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

![img](https://static001.geekbang.org/resource/image/12/e9/127842f6c949d6fa59be8d380ca8e7e9.jpg?wh=2597x895)

一个简单的经验法则是，如果你在终端里用一行命令就能完成的事情，用query()；如果你需要在代码里做任何“配置”或“控制”，用  ClaudeSDKClient。

在实际项目中，常见的演进路径是先用  query() 快速验证想法，然后在功能成型后迁移到  ClaudeSDKClient 进行工程化。两种方式的消息格式完全兼容，迁移成本很低。

**ClaudeAgentOptions 配置详解**

ClaudeAgentOptions 是控制 Agent 行为的核心配置类。你可以把它理解为 Agent 的“说明书”，它告诉 Agent 该用什么模型、能用什么工具、最多跑几轮、在什么目录下工作。每一个配置项都会直接影响 Agent 的行为和成本。

下面是完整的配置项。不需要一次记住所有配置，你可以先关注最常用的四个：allowed_tools、permission_mode、max_turns、model。其余的在需要时查阅即可。

```
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    # === 模型选择 ===
    model="sonnet",  # "sonnet" | "opus" | "haiku"

    # === 工具控制 ===
    allowed_tools=["Read", "Write", "Bash", "Grep", "Glob"],
    disallowed_tools=["Task"],

    # === 权限模式 ===
    permission_mode="default",  # "default" | "acceptEdits" | "plan" | "bypass"

    # === 执行控制 ===
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

权限模式决定了 Agent 执行操作时的确认行为。这是安全性与自动化程度之间的一个权衡——你给 Agent 越多的自主权，它就能越快地完成任务，但风险也越高。

选择权限模式时，问自己一个问题：如果 Agent 做了一件错事，最坏的结果是什么？如果最坏结果“改错了一个文件，我  git checkout 恢复一下”，那可以放宽权限；如果最坏结果是“删除了生产数据库”，那必须严格控制。

![img](https://static001.geekbang.org/resource/image/5a/5a/5ac340ffeef62c4db2027334bcb38e5a.jpg?wh=2897x820)

下面的代码展示了两种典型场景下的权限配置。代码审查只需要读取代码，不需要任何修改能力，所以用  plan 模式加上只读工具；自动修复则需要编辑文件的能力，但不需要执行任意命令，所以用  acceptEdits 模式搭配  Read/Write/Edit 工具。

```
# 代码审查场景：只读
options = ClaudeAgentOptions(
    permission_mode="plan",
    allowed_tools=["Read", "Grep", "Glob"]
)

# 自动修复场景：接受编辑
options = ClaudeAgentOptions(
    permission_mode="acceptEdits",
    allowed_tools=["Read", "Write", "Edit"]
)
```

你可以精确控制 Agent 能使用哪些工具。SDK 提供了两种控制方式，白名单（allowed_tools）和黑名单（disallowed_tools）。

白名单是“只允许这些”，黑名单是“除了这些都允许”。在安全敏感的场景中，推荐使用白名单，明确列出 Agent 能用的工具，而不是试图列出所有它不能用的工具。

内置工具列表：

![img](https://static001.geekbang.org/resource/image/36/1e/36a6b1151da4bf0cbf162fa8e0070c1e.jpg?wh=2404x1294)

下面展示了三种不同的工具限制策略。注意第三个例子——你可以用  Bash(git:*) 这样的语法来限制 Bash 工具只能执行特定前缀的命令，这比完全禁用 Bash 更加灵活。

```
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

![img](https://static001.geekbang.org/resource/image/8c/26/8c29cfdedf15f3d73140c015689e1926.jpg?wh=2760x1395)

**消息类型与响应处理**

理解消息类型是正确处理 Agent 响应的关键。Agent 不是一次性返回结果的——它是一个异步流，在执行过程中会源源不断地产生不同类型的消息。你的代码需要根据消息类型分别处理，就像处理不同类型的网络事件一样。

Agent 在执行过程中会产生五种类型的消息。

text 是 Claude 生成的文本内容，比如分析结论、代码解释；tool_use 表示 Agent 正在调用某个工具；tool_result 是工具执行后返回的结果；error 表示执行过程中遇到了错误；result 是最终的汇总消息，包含执行时间、成本等元数据。

```
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

```
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

```
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

这个模式的好处是，调用方可以直接从  result["output"] 获取 Agent 的文本输出，从  result["tools_used"] 获取工具调用记录（用于审计），从  result["metadata"] 获取成本和性能数据（用于监控）。

**会话管理**

你让 Agent 分析一个项目的代码结构，分析完之后想让它基于分析结果生成文档。如果没有会话管理，Agent 在第二次调用时完全不记得它之前分析过什么，你得重新传一遍所有上下文。

因此，通过会话管理保持对话上下文，或者恢复之前的会话。这对于长时间运行的任务或需要分阶段完成的工作特别有用。

在同一个  ClaudeSDKClient 实例中，你可以进行多轮对话。Agent 会自动记住之前的上下文——它知道自己读过哪些文件、执行过哪些命令、做过哪些分析。每次新的  query() 调用都是在之前的上下文基础上继续，而不是从零开始。

```
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

有时候你需要在不同的程序运行之间保持对话连续性。比如，你的 Agent 在一次 CI 运行中分析了代码，你想在下一次 CI 运行中让它继续从上次的结论出发。这时候就需要保存  session_id，然后在下次启动时通过  resume 参数恢复会话。

```
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

下面是一个完整的会话持久化方案。它把  session_id 保存到本地 JSON 文件中，支持按名称存取多个会话。这个方案适用于开发环境和小型项目。

在生产环境中，你可能需要把会话 ID 存到 Redis 或数据库中，并设置过期时间——长时间不活跃的会话应该被清理，否则会累积大量上下文，导致 Token 消耗急剧增加。

```
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

![img](https://static001.geekbang.org/resource/image/0c/66/0c48b962981b293cd5b7c4e0efe54366.jpg?wh=1243x455)

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

<u></u>