> 来自极客时间《Claude Code工程化实战》--黄佳

# <mark>Skills 技能系统（09~14）</mark>

# 09｜触类旁通：SKILL.md 结构与触发机制

**什么是 Skills**

Skills 是一种可被语义触发的能力包，它包含领域知识、执行步骤、输出规范与约束条件。

Skills 解决的核心问题是，在有限的上下文窗口中，让 Agent 在正确的时刻拥有正确的领域知识。

**深入理解 Skill 触发机制**

在 Claude Code 中，Skills 默认情况下支持两种触发方式。

| 触发方式     | 说明                                        | 示例                                                       |
| ------------ | ------------------------------------------- | ---------------------------------------------------------- |
| 用户显式触发 | 输入 `/skill-name`                          | `/review src/auth.ts`                                      |
| 分层评审     | Claude 读取 description，语义匹配后自动加载 | 用户说"帮我审查这段代码"，Claude 激活 code-reviewing Skill |

> 语义触发Skills的机制

Claude 读取所有 Skills 的 description，通过语义理解判断当前对话是否匹配某个 Skill。当用户发送消息时，Claude 的处理流程如下图所示：

```
                         ┌─────────────┐
                         │   用户输入   │
                         └──────┬──────┘
        ┌───────────────────────↓───────────────────────┐
        │  扫描所有 Skills 的 description (~100 tokens)  │
        └───────────────────────┬───────────────────────┘
        ┌───────────────────────↓───────────────────────┐
        │            语义推理匹配找到最相关的              │
        └───────────────────────┬───────────────────────┘
        ┌───────────────────────↓───────────────────────┐
        │                  是否找到匹配？                 │
        └───────────────────────┬───────────────────────┘
                  ┌─────────────┴─────────────┐
                  ↓是                         ↓否
      ┌───────────────────────────┐   ┌───────────────────────┐
      │  加载 SKILL.md            │    │    正常处理用户请求    │
      └───────────────────────────┘   └───────────────────────┘
```

当用户请求可能匹配多个 Skills 时，Claude 会：

1. 评估每个 Skill 的 description 与用户请求的相关性。
2. 选择最相关的那个。
3. 如果不确定，可能会询问用户。

**两大类型的 Skills：参考型和任务型**

从工程角度，Skill 内容分为两类，参考型和任务型。参考型 Skill 影响“怎么做”，任务型 Skill 决定“做什么”。前者是语义环境，后者是具体行动。

你在写 description 时需要明确它属于哪种类型。

```markdown
# 参考型——Claude 自动选择是否使用
name: api-conventions
description: API design patterns for this codebase. Use when writing or reviewing API endpoints.
<!-- 强调“怎么做” -->
<!-- 场景：API规范、代码风格、领域知识 -->

# 任务型——通常由用户手动触发
name: deploy
description: Deploy the application to production
<!-- 强调“做什么” -->
disable-model-invocation: true
<!-- 常由用户手动触发 -->
<!-- 场景：部署流程、提交规范、代码生成 -->
```

> 设有  disable-model-invocation: true 的 Skill，其 description 不会加载到上下文——Claude 完全看不到它，只有用户  /name 才能触发。

**创建一个参考型 SKILL.md 文件**

我们即将要创建的这个参考型 Skill 是一个“API 设计规范”：

```
.claude/skills/api-conventions/     # 目录名称即skill名
└── SKILL.md                        # 主文件（必需）
```

注意这个 Skill 的关键特征——它是一个典型的参考型 Skill。这个文件有两个部分：

- YAML frontmatter，是通过---包裹的元数据
- Markdown 正文，是技能的具体说明

```markdown
---
name: api-conventions
description: API design patterns and conventions for this project. Covers RESTful URL naming, response format standards, error handling, and authentication requirements. Use when writing or reviewing API endpoints, designing new APIs, or making decisions about request/response formats.
allowed-tools:
  - Read
  - Grep
  - Glob
---
<!-- 特征一：没有设disable-model-invocation：Claude 可以自动判断何时需要 -->
<!-- 特征二：只读工具：allowed-tools  限制为 Read/Grep/Glob，因为规范查阅不需要改代码。 -->

# API Design Conventions

These are the API design standards for our project. Apply these conventions whenever working with API endpoints.
<!-- 特征三：没有执行步骤（不是先做 A 再做 B，而是“遵循这些规范”） -->

<!-- 特征四：没有输出模板：不要求 Claude 输出固定格式的报告 -->

## URL Naming

- Use plural nouns for resources: `/users`, `/orders`, `/products`
- Use kebab-case for multi-word resources: `/order-items`, `/user-profiles`
- Nested resources for belongsTo relationships: `/users/{id}/orders`
- Maximum two levels of nesting; beyond that, use query parameters
- Use query parameters for filtering: `/orders?status=active&limit=20`

## Response Format

All API responses must follow this structure:

{
  "data": {},        // 成功时返回的数据
  "error": null,     // 错误时返回错误对象 { code, message, details }
  "meta": {          // 分页和元信息
    "page": 1,
    "limit": 20,
    "total": 100
  }
}

## HTTP Status Codes

- 200: 成功返回数据
- 201: 成功创建资源
- 400: 请求参数错误
- 401: 未认证
- 403: 无权限
- 404: 资源不存在
- 422: 业务逻辑错误
- 500: 服务器内部错误

## Authentication

- All endpoints require Bearer token unless explicitly marked as public
- Public endpoints must be documented with `@public` annotation
- Token format: `Authorization: Bearer <jwt-token>`

## Versioning

- API version in URL path: `/api/v1/users`
- Breaking changes require new version

```

在这里，description 是 Skill 的灵魂，因为它不是给人看的文档，而是给 Claude 看的触发器。Claude 选择是否激活一个 Skill，完全依赖于阅读 description。这不是关键词匹配，而是语义理解。

我给你总结了一个 description 写作公式：

```
description = [做什么] + [什么时候用]
```

套用公式创作几个示例 Skill：

```markdown
# 代码审查 Skill
description: Review code for quality, security, and best practices. Checks for bugs, performance issues, and style violations. Use when the user asks for code review, wants feedback on their code, mentions reviewing changes, or asks about code quality.

# API 文档 Skill
description: Generate API documentation from code. Extracts endpoints, parameters, and response schemas. Use when the user wants to document APIs, create API reference, generate endpoint documentation, or needs help with OpenAPI/Swagger specs.

# 数据库查询 Skill
description: Query databases and analyze results. Supports SQL generation, query optimization, and result interpretation. Use when the user asks about data, wants to run queries, needs database information, or mentions tables/schemas.
```

当你有多个 Skills 时，确保它们的 description 有明确区分：

```markdown
# ❌ 容易冲突
name: unit-testing
description: Write tests for code

name: integration-testing
description: Write tests for code

# ✅ 明确区分
name: unit-testing
description: Write and run unit tests for individual functions. Use when testing single functions or methods in isolation, mocking dependencies, and verifying function behavior.

name: integration-testing
description: Write and run integration tests for system components. Use when testing how multiple components work together, testing API endpoints end-to-end, or verifying database interactions.
```

**Skills Frontmatter 字段详解**

Claude Code 官方支持的完整 frontmatter 字段如下。

```markdown
---
name: my-skill-name                # 可选：Skill 标识符（省略则用目录名）
description: What this does        # 推荐：触发器（最重要！）
argument-hint: "[issue-number]"    # 可选：自动补全时的参数提示
disable-model-invocation: true     # 可选：禁止 Claude 自动触发
user-invocable: false              # 可选：对用户隐藏 /skill-name
allowed-tools: Read,Grep,Glob      # 可选：限制可用工具
model: sonnet                      # 可选：指定执行模型
context: fork                      # 可选：在子代理中隔离执行
agent: Explore                     # 可选：context: fork 时的代理类型
hooks:                             # 可选：作用域为此 Skill 的 Hooks
  PreToolUse:
    - matcher: Write
      hooks:
        - type: command
          command: "echo 'Write called in skill'"
---
```

# 10｜令行禁止：任务型 Skills （斜杠命令 /Command）实战

> 释题：在 Claude Code 里，令行禁止几乎可以直接翻译为：disable-model-invocation: true 。也就是说——没有用户触发，Claude 绝不主动执行。

## Skills vs Commands

早期，斜杠命令 /Comands 和 Skills 是两个独立组件。但在新版 Claude Code 中，Commands 已合并到 Skills，成为 Skills 的子集。

因此，在 .claude/commands/review.md 和  .claude/skills/review/SKILL.md 两个不同目录的文件，都会创建  /review。。如果同名 Skill 和 Command 共存，Skill 优先。

> Skills 目录的额外优势是支持辅助文件目录（模板、示例、脚本等）。

> See: https://code.claude.com/docs/zh-CN/skills

## 通过 ARGUMENTS 给 Skill 传参

当你通过  /skill-name args 调用 Skill 时，args 会通过  $ARGUMENTS 注入到 Skill 内容中。

举例来说，当运行  /fix-issue 123 时，Claude 收到的内容是“Fix GitHub issue 123 following our coding standards…”。

```markdown
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---

Fix GitHub issue $ARGUMENTS following our coding standards.

1. Read the issue description
2. Understand the requirements
3. Implement the fix
4. Write tests
5. Create a commit
```

Skill 支持两种参数传递方式。

**单参数——$ARGUMENTS 接收所有参数**

```markdown
---
description: Quick git commit
argument-hint: [commit message]
disable-model-invocation: true
---

Create a git commit with message: $ARGUMENTS
```

用法：`/commit fix login bug`

**多参数—— $1，$2 接收位置参数**

```markdown
---
description: Create a pull request
argument-hint: [title] [description]
disable-model-invocation: true
---

Title: $1
Description: $2
```

用法：`/pr-create "Add auth" "JWT"`

Claude Code 是非常灵活的，如果 Skill 中根本就没有定义 $ARGUMENTS，而你在调用 Skill 的时候又偏偏传递了参数进去。那也不怕，Claude Code 会自动在内容末尾追加  ARGUMENTS: <用户输入>，确保参数不会丢失。

## 动态上下文注入

当用户输入  /pr-create "Add auth" 时，模型收到的只是 Prompt 文本。它不知道：当前在哪个分支？有哪些 commit 待合并？改了哪些文件？

如果不预注入上下文，其实模型也会先花多轮工具调用去收集这些信息，任务虽然还是能完成，但浪费 token 和时间。

而 ! `command` 是 Skill 文件的预处理器——在文件内容发送给模型  之前，先在 shell 中执行这些预设的命令，然后把它们的输出结果内联替换到 Prompt 中，再去执行新的命令。

下面的示例中，我们为 pr-create 命令设置 ! `command` ，让它能够动态接收上下文（上下文就是在技能中预设的 ! `command` 的输出）。

```markdown
## Current Context (Auto-detected)

Current branch:
!`git branch --show-current`

Recent commits on this branch:
!`git log origin/main..HEAD --oneline 2>/dev/null || echo "No commits ahead of main"`

Files changed:
!`git diff --stat origin/main 2>/dev/null || git diff --stat HEAD~3`
```

LLM 实际收到的 Prompt（替换后）：

```markdown
## Current Context (Auto-detected)

Current branch:
feature/auth

Recent commits on this branch:
a1b2c3d Add JWT middleware
d4e5f6g Add login endpoint
g7h8i9j Add user model

Files changed:
 src/auth/middleware.ts | 45 +++
 src/auth/login.ts     | 82 +++
 src/models/user.ts    | 34 +++
 3 files changed, 161 insertions(+)
```

## 实战项目：团队标准命令集

现在让我们来创建一套真正实用的团队命令，目录结构如下：

```
.claude/skills/                    # 推荐：Skills 目录
├── committing/SKILL.md            # /committing  快速提交
├── reviewing/SKILL.md             # /reviewing   代码审查
├── pr-creating/SKILL.md           # /pr-creating 创建 PR
└── testing/SKILL.md               # /testing     运行测试

.claude/commands/                   # 兼容：Commands 目录
└── git/
    ├── status.md                  # /git:status
    └── log.md                     # /git:log
```

**命令一：智能提交 /commit**

```markdown
---
description: Quick git commit with auto-generated or specified message
argument-hint: [optional: commit message]
disable-model-invocation: true

allowed-tools: Bash(git status:*), Bash(git add:*), Bash(git commit:*), Bash(git diff:*)
<!-- 只授权 git 相关命令 -->

model: haiku
<!-- 使用 haiku 模型，响应快 -->
---

Create a git commit.

If a message is provided: $ARGUMENTS
- Use that as the commit message

If no message is provided:
- Analyze the changes with `git diff --staged` (or `git diff` if nothing staged)
- Generate a concise, meaningful commit message

<!-- 有参数用参数，没参数自动生成 -->

## Steps

1. Check `git status` to see current state
2. If nothing staged, run `git add .` to stage all changes
3. Review what will be committed with `git diff --staged`
4. Create commit:
   - If `$ARGUMENTS` is provided, use it as the message
   - Otherwise, generate a message based on the diff
5. Show the commit result

## Commit Message Format

- Start with type: `feature:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Be concise but descriptive (max 72 chars for first line)
- Example: `feat: add user authentication with JWT`
<!-- 强制遵循 conventional commits 格式 -->

## Output

Show a brief confirmation:
✓ Committed: [commit message] [number] files changed
```

使用方式：

```bash
# 自动生成 commit message
/commit

# 使用指定的 message
/commit fix: resolve login validation bug
```

**命令二：代码审查 /review**

~~~markdown
---
description: Review code for quality, bugs, and improvements
argument-hint: [optional: file path]
disable-model-invocation: true

allowed-tools: Read, Grep, Glob, Bash(git diff:*)
<!-- 只授权读权限，不能修改代码 -->
---

Review code and provide feedback.

Target: $ARGUMENTS (or current git diff if not specified)
<!-- 审查特定文件 或者 审查当前变更 -->

## Review Focus Areas

1. **Bugs & Errors**: Logic errors, null checks, edge cases
2. **Security**: Input validation, injection risks, sensitive data exposure
3. **Performance**: Obvious inefficiencies, N+1 queries, memory leaks
4. **Readability**: Naming, complexity, documentation needs

## Steps

1. If file path provided, read that file
2. If no path, run `git diff` to see current changes
3. Analyze the code against the focus areas
4. Provide structured feedback

## Output Format

```markdown
## Code Review

### Summary
[One sentence overall assessment]

### Issues Found

#### Critical (Must Fix)
- [issue]: [location] - [brief explanation]

#### Warnings (Should Fix)
- [issue]: [location] - [brief explanation]

#### Suggestions (Nice to Have)
- [suggestion]: [location] - [brief explanation]

<!-- 优先级分类功能：Critical > Warning > Suggestion -->

### What's Good
- [positive observation]

<!-- 统一的反馈格式，便于团队理解 -->

## Guidelines
Be specific about locations (file:line if possible)
Provide actionable feedback, not just criticism
Don't nitpick style unless it impacts readability
Acknowledge good patterns you see
~~~

使用方式：

```bash
# 审查当前 git diff
/review

# 审查特定文件
/review src/auth/login.ts
```

**命令三：创建 PR /pr-create**

~~~markdown
---
description: Create a pull request with auto-detected context
argument-hint: [title] [description]
disable-model-invocation: true
allowed-tools: Bash(git:*), Bash(gh:*)
---

Create a pull request.

Title: $1
Description: $2

## Current Context (Auto-detected)

Current branch:
!`git branch --show-current`
<!-- 动态上下文注入 -->

Recent commits on this branch:
!`git log origin/main..HEAD --oneline 2>/dev/null || echo "No commits ahead of main"`
<!-- 动态上下文注入 -->

Files changed:
!`git diff --stat origin/main 2>/dev/null || git diff --stat HEAD~3`
<!-- 动态上下文注入 -->

## Steps

1. Ensure we're not on main/master branch
2. Push current branch to remote (if not already)
3. Create PR using `gh pr create`:
   - Title: $1 (or auto-generate from branch name)
   <!-- 用户未指定，则自动生成标题和描述-->
   - Body: $2 (or auto-generate from commits)
   <!-- 用户未指定，则自动生成标题和描述-->
4. Return the PR URL

## PR Body Template

If $2 is not provided, generate:

```markdown
## Summary
[Auto-generated from commit messages]

## Changes
[List of changed files with brief descriptions]

## Testing
- [ ] Tests pass locally
- [ ] Manual testing completed

---
Created with `/pr-create`

## Output
✓ PR Created: [URL]

Title: [title]
Branch: [branch] → main
Changes: [n] files
~~~

使用方式：

```bash
# 自动生成标题和描述
/pr-create

# 指定标题
/pr-create "Add user authentication"

# 指定标题和描述
/pr-create "Add user authentication" "Implements JWT-based auth with refresh tokens"
```

当命令越来越多时，可以用目录结构组织它们：

```
.claude/commands/
├── commit.md           →  /commit
├── review.md           →  /review
├── git/
│   ├── status.md       →  /git:status
│   ├── log.md          →  /git:log
│   └── sync.md         →  /git:sync
└── test/
    ├── unit.md         →  /test:unit
    └── e2e.md          →  /test:e2e
```

# ==11｜循序渐进：渐进式披露架构设计==

## 渐进式披露的设计哲学

让我们用图书馆来类比渐进式披露的设计哲学。走进一个图书馆找资料时，你不会一次把所有书都读一遍。你是先看目录找到相关分类，再选一本具体的书，最后翻到需要的章节深入阅读。信息是逐层展开的，而不是一次性全部载入大脑。

Skill 的渐进式披露设计也是一样：第一层只扫描 description 作为“目录”，第二层在触发时加载 SKILL.md 主文件作为“章节”，第三层再按需加载被引用的具体文件作为“附录”。结构化分层替代信息堆叠，让系统在规模变大时依然高效、可控。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202604161515754.jpg)

**认知经济学：上下文窗口是稀缺资源**

Token 节省效果方面。让我们用数字说话。假设一个复杂的 Skill 是这样的：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202604161517324.jpeg)

不同场景下的 Token 消耗（大概估算）：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202604161518860.jpeg)

不难发现，大多数请求只需要部分资源，渐进式披露在这些场景下大幅节省 tokens。

## 财务分析 Skill

**三层架构详解**

我们今天要设计的这个财务分析 Skill，本质上是一个结构化的财务能力包：当用户提出与收入、成本、利润、增长率、毛利率、ROE/ROA 或整体财务表现相关的问题时，它会被激活。

它的目标是在明确数据前提下，提供可复现、可解释、可结构化的财务分析支持，用最少的上下文投入完成高质量的专业判断。

下面来看看这个 Skill 的三层渐进式的架构设计，我们用看书时经常采用的目录、章节、附录来对渐进式架构做类比。

- 层级 1：目录页（Entry Point）

这是 Skills 系统扫描阶段读取的内容——只有 description。

```
---
name: financial-analyzing
description: Analyze financial data, calculate ratios, and generate reports. Use when the user asks about revenue, costs, profits, margins, financial metrics, or needs financial analysis.
---
```

目录页的设计原则是，description 足够丰富，让 Claude 能准确判断相关性。但不要太长，因为所有  Skill 的 description 共享 15,000 字符的总预算。如果 Skill 数量多导致 description 被截断，可以通过  SLASH_COMMAND_TOOL_CHAR_BUDGET 环境变量调整。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202604161526174.jpeg)

- 层级 2：章节（Main Content）

章节指的是 SKILL.md 的正文部分——激活后才加载。

```markdown
# Financial Analysis Skill

## Quick Start
基础的财务分析流程...

## Available Analyses

### Revenue Analysis
For detailed formulas, see `reference/revenue.md`

### Cost Analysis
For detailed formulas, see `reference/costs.md`

### Profitability Analysis
For detailed formulas, see `reference/profitability.md`

## When to Load Additional Resources
- 需要具体公式 → 加载对应的 reference/\*.md
- 需要行业基准 → 加载 data/benchmarks.json
- 需要报告模板 → 加载 templates/\*.md
```

这一部分的设计原则是主文件提供“路线图”，通过文件引用指向详细内容，然后 Claude 根据用户请求决定加载哪些具体内容。

- 层级 3：附录（On-Demand Resources）

只有当 SKILL.md 中引用了这些文件，Claude 才会去读取这一类文件。

```
.claude/skills/financial-analyzing/    # 标准 Skill 目录
├── SKILL.md                           # 主文件（总是加载）
├── reference/                         # 参考资料
│   ├── revenue.md                    # 收入分析公式
│   ├── costs.md                      # 成本分析公式
│   └── profitability.md              # 盈利分析公式
├── templates/                         # 报告模板
│   ├── quarterly_report.md
│   └── annual_report.md
├── data/                              # 数据文件
│   └── industry_benchmarks.json
└── scripts/                           # 分析脚本
    ├── calculate_ratios.py
    └── generate_report.sh
```

这一部分内容的设计原则是文件名要有描述性（revenue.md 而非  ref1.md）——Claude 根据文件名判断是否需要加载。

**项目设计细节**

下面我们还原这个财务分析 Skill 的构建细节，从零构建一个完整的财务分析 Skill。这个 Skill 标准部署结构如下：

```
your-project/.claude/skills/financial-analyzing/
├── SKILL.md                    # 主 Skill 文件
├── reference/
│   ├── revenue.md             # 收入分析
│   ├── costs.md               # 成本分析
│   └── profitability.md       # 盈利分析
├── templates/
│   └── analysis_report.md     # 分析报告模板
└── scripts/
    └── calculate_ratios.py    # 比率计算脚本
```

主文件 SKILL.md 设计如下。

~~~markdown
---
name: financial-analyzing
description: Analyze financial data, calculate financial ratios, and generate analysis reports. Use when the user asks about revenue, costs, profits, margins, ROI, financial metrics, or needs financial analysis of a company or project.

allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(python:*)
<!-- 只允许 Read、Grep、Glob 和特定的 Bash 命令 -->
---

# Financial Analysis Skill

You are a financial analyst. Help users analyze financial data, calculate key metrics, and generate insightful reports.

## Quick Reference

| Analysis Type | When to Use | Reference |
|--------------|-------------|-----------|
| Revenue Analysis | 收入、营收、销售额相关 | `reference/revenue.md` |
| Cost Analysis | 成本、费用、支出相关 | `reference/costs.md` |
| Profitability | 利润、毛利率、净利率相关 | `reference/profitability.md` |

<!-- 让 Claude 快速定位需要哪个参考文件 -->

## Analysis Process

### Step 1: Understand the Question
- What financial aspect is the user asking about?
- What data do they have available?
- What format do they need the answer in?

### Step 2: Gather Data
- Request necessary financial data from user
- Or read from provided files/sources

### Step 3: Calculate Metrics
For specific formulas and calculations:
- Revenue metrics → see `reference/revenue.md`
- Cost metrics → see `reference/costs.md`
- Profitability metrics → see `reference/profitability.md`

To run calculations programmatically:
```bash
python scripts/calculate_ratios.py <data_file>

### Step 4: Generate Report
Use the template in `templates/analysis_report.md` for structured output.

## Output Guidelines

1. Always show your calculations
2. Explain what each metric means
3. Provide context (industry benchmarks when available)
4. Give actionable recommendations

## Important Notes

- Never make up financial data
- Ask for clarification if data is incomplete
- Flag any unusual numbers that might be errors
~~~

上面的 SKILL.md 设计，你会发现它本质上是一个路由器——根据用户请求的类型，将 Claude 导向不同的资源文件：

```
用户请求 → SKILL.md（路由判断） → 目标资源
                │
                ├─ "收入相关" → reference/revenue.md
                ├─ "成本相关" → reference/costs.md
                ├─ "利润相关" → reference/profitability.md
                ├─ "要报告"   → templates/analysis_report.md
                └─ "要计算"   → scripts/calculate_ratios.py
```

写好路由表格的经验法则包括。

1. 用“用户可能说的关键词”作为路由条件（而非“文件内容的技术名称”）
2. 每个路由条目一行，不要超过 10 个条目（超过就需要分层）
3. 高频路由放前面

除主文件之外，这个 Skill 中还包括下面几个参考文件，也就是附录。

- 参考文件：reference/revenue.md

只有当用户问到收入相关问题时，Claude 才会根据 SKILL.md 中 Quick Reference 表格的路由指引加载这个文件。它包含收入增长率、同比 / 环比、ARPU 等核心公式和异常信号判断标准。

~~~markdown
# Revenue Analysis Reference

## Key Metrics

### Revenue Growth Rate
```
Revenue Growth Rate = (Current Period Revenue - Previous Period Revenue) / Previous Period Revenue × 100%
```
**Interpretation:**
- > 20%: High growth
- 10-20%: Moderate growth
- < 10%: Low growth
- < 0%: Declining

### Year-over-Year (YoY) Growth
```
YoY Growth = (This Year Revenue - Last Year Revenue) / Last Year Revenue × 100%
```

### Quarter-over-Quarter (QoQ) Growth
```
QoQ Growth = (This Quarter - Previous Quarter) / Previous Quarter × 100%
```

## Revenue Composition Analysis

### Revenue by Product/Service
```
Product Revenue Share = Product Revenue / Total Revenue × 100%
```
### Revenue by Region
```
Regional Revenue Share = Regional Revenue / Total Revenue × 100%
```
## Average Revenue Metrics

### Average Revenue Per User (ARPU)
```
ARPU = Total Revenue / Number of Users
```
### Average Revenue Per Account (ARPA)
```
ARPA = Total Revenue / Number of Accounts
```

## Red Flags to Watch

1. **Revenue concentration** > 30% from single customer
2. **Declining growth rate** over 3+ consecutive quarters
3. **Large discrepancy** between booked and recognized revenue
4. **Unusual seasonality** patterns
~~~

- 参考文件：reference/profitability.md

这个文件聚焦盈利能力分析。包含毛利率、营业利润率、净利率三大 Margin 指标，以及 ROI、ROA、ROE 三大 Return 指标，并附带行业基准数据供对比参考。

~~~markdown
# Profitability Analysis Reference

## Margin Metrics

### Gross Profit Margin
```
Gross Margin = (Revenue - Cost of Goods Sold) / Revenue × 100%
```
**Industry Benchmarks:**
| Industry | Typical Range |
|----------|--------------|
| Software/SaaS | 70-85% |
| Retail | 20-50% |
| Manufacturing | 25-35% |
| Services | 50-70% |

### Operating Profit Margin
```
Operating Margin = Operating Income / Revenue × 100%

Operating Income = Revenue - COGS - Operating Expenses
```
### Net Profit Margin
```
Net Margin = Net Income / Revenue × 100%

Net Income = Revenue - All Expenses - Taxes
```
## Return Metrics

### Return on Investment (ROI)
```
ROI = (Gain from Investment - Cost of Investment) / Cost of Investment × 100%
```
### Return on Assets (ROA)

```
ROA = Net Income / Total Assets × 100%
```
### Return on Equity (ROE)
```
ROE = Net Income / Shareholders' Equity × 100%
```

## Profitability Red Flags

1. **Gross margin declining** while revenue grows (pricing pressure)
2. **Operating margin < 0** (not operationally profitable)
3. **ROE significantly higher than ROA** (high leverage risk)
4. **Net margin < industry average** for 3+ years
~~~

- 报告模板：templates/analysis_report.md

模板文件是渐进式披露中的特殊资源——它不提供“知识”，而是提供“输出格式”。当用户要求“生成分析报告”时，Claude 加载这个模板来确保输出结构统一、专业。这就是企业知识管理中“标准化输出”的技术映射。

```markdown
# Financial Analysis Report Template

## Executive Summary
[One paragraph summarizing key findings and recommendations]

## Company/Project Overview
- **Name**: [Entity name]
- **Period Analyzed**: [Date range]
- **Data Sources**: [Where data came from]

## Key Metrics

| Metric | Value | Industry Avg | Assessment |
|--------|-------|--------------|------------|
| Revenue Growth | X% | Y% | Above/Below |
| Gross Margin | X% | Y% | Above/Below |
| Net Margin | X% | Y% | Above/Below |
| ROI | X% | Y% | Above/Below |

## Detailed Analysis

### Revenue Analysis
[Findings about revenue trends, composition, growth]

### Cost Analysis
[Findings about cost structure, efficiency]

### Profitability Analysis
[Findings about margins, returns]

## Trend Analysis
[How metrics have changed over time]

## Recommendations

### Immediate Actions
1. [High priority recommendation]
2. [High priority recommendation]

### Medium-term Improvements
1. [Medium priority recommendation]

### Long-term Strategy
1. [Strategic recommendation]

## Risk Factors
- [Key risk 1]
- [Key risk 2]

## Appendix
[Supporting calculations, data tables, charts]
```

- 计算脚本：scripts/calculate_ratios.py

Claude 不需要理解计算逻辑，只需执行  python calculate_ratios.py data.json 即可获得准确结果。这比让 LLM 自己做数学运算更可靠、更省 token。

```markdown
#!/usr/bin/env python3
"""
Financial Ratios Calculator

Usage:
    python calculate_ratios.py <data_file>

Data file format (JSON):
{
    "revenue": 1000000,
    "cogs": 400000,
    "operating_expenses": 300000,
    "net_income": 150000,
    "total_assets": 2000000,
    "shareholders_equity": 800000,
    "previous_revenue": 900000
}
"""

import json
import sys


def calculate_ratios(data):
    """Calculate common financial ratios."""
    ratios = {}

    # Revenue Growth
    if 'previous_revenue' in data and data['previous_revenue'] > 0:
        ratios['revenue_growth'] = (
            (data['revenue'] - data['previous_revenue'])
            / data['previous_revenue'] * 100
        )

    # Gross Margin
    if 'cogs' in data:
        gross_profit = data['revenue'] - data['cogs']
        ratios['gross_margin'] = gross_profit / data['revenue'] * 100

    # Operating Margin
    if 'cogs' in data and 'operating_expenses' in data:
        operating_income = data['revenue'] - data['cogs'] - data['operating_expenses']
        ratios['operating_margin'] = operating_income / data['revenue'] * 100

    # Net Margin
    if 'net_income' in data:
        ratios['net_margin'] = data['net_income'] / data['revenue'] * 100

    # ROA
    if 'net_income' in data and 'total_assets' in data:
        ratios['roa'] = data['net_income'] / data['total_assets'] * 100

    # ROE
    if 'net_income' in data and 'shareholders_equity' in data:
        ratios['roe'] = data['net_income'] / data['shareholders_equity'] * 100

    return ratios


def main():
    if len(sys.argv) < 2:
        print("Usage: python calculate_ratios.py <data_file>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        data = json.load(f)

    ratios = calculate_ratios(data)

    print("\n=== Financial Ratios ===\n")
    for name, value in ratios.items():
        print(f"{name.replace('_', ' ').title()}: {value:.2f}%")


if __name__ == '__main__':
    main()
```

**渐进式加载实战演示**

- 场景 1：简单问题

用户：毛利率怎么计算？

Claude 加载过程：

1. 扫描 Skills → 发现  financial-analyzing 匹配
2. 加载 SKILL.md → 看到 “Profitability → see reference/profitability.md”
3. 加载  reference/profitability.md → 找到毛利率公式
4. 回答用户

Token 消耗：~100（扫描）+ 800（主文件）+ 600（profitability.md 部分）= ~1500 tokens

其他文件（revenue.md、costs.md、templates、scripts）完全没有加载。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202604161546114.png)

- 场景 2：完整分析

用户：帮我分析 data 目录中的财务数据，生成一份完整的分析报告。

Claude 加载过程：

1. 扫描 Skills，发现  financial-analyzing 匹配
2. 加载 SKILL.md
3. 分析任务需要，加载所有 reference/*.md
4. 需要报告格式，加载 templates/analysis_report.md
5. 需要计算 ，执行 scripts/calculate_ratios.py

Token 消耗：全部资源都用到了。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202604161548937.png)

两个场景的关键对比如下。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202604161553856.jpeg)

## 渐进式的设计模式与最佳实践

**文件组织模式**

首先谈文件组织模式，有按功能分类和按使用频率分类两种。

如果你的 Skill 有多种类型的资源（知识 + 模板 + 脚本），用功能分类（推荐），例如：

```
.claude/skills/my-skill/
├── SKILL.md           # 入口 + 路由（< 500 行）
├── reference/         # 知识库（公式、规范、基准）
├── templates/         # 输出模板（报告、代码骨架）
├── examples/          # 示例集（输入输出样本）
├── scripts/           # 可执行脚本（计算、生成、验证）
└── data/              # 静态数据（JSON、CSV）
```

如果只有不同深度的知识文档，用频率分类，例如：

```
.claude/skills/my-skill/
├── SKILL.md           # 核心内容（高频，总是加载）
├── QUICKREF.md        # 快速参考（高频，常被加载）
├── DETAILED.md        # 详细说明（中频，按需加载）
└── ADVANCED.md        # 高级用法（低频，很少加载）
```

**主文件设计原则**

主文件应该控制在  500 行以内（官方建议：Keep SKILL.md under 500 lines. Move detailed reference material to separate files.）。然后应该提供路线图，用 Quick Reference 表格做个快速路由，而非让 Claude 逐行扫描。

什么内容放主文件，什么内容放引用文件？答案是高频内容内联，低频内容外链。比如偶尔用到的详细信息放在引用文件，用契约式引用。

> 到底啥是契约式引用？ SKILL.md 引用辅助文件时，不要只写一个路径——要写一个契约，让 Claude 知道什么时候该加载、加载后能得到什么：
>
> ```markdown
> # ❌ 弱引用（Claude 不知道何时该加载）
> See `reference/revenue.md` for more details.
> 
> # ✅ 契约式引用（Claude 清楚加载条件和预期内容）
> ## Revenue Analysis
> When the user asks about revenue growth, ARPU, or revenue composition:
> → Load `reference/revenue.md` for calculation formulas and industry benchmarks
> ```

## 内容拆分的工程方法论

我们来解决一个更根本的问题：面对一坨知识，怎么决定什么放 SKILL.md、什么放引用文件、什么放脚本？

官方建议 SKILL.md 控制在  500 行以内。为什么是 500 行？

- 500 行 ≈ 2000-3000 tokens，是一个 Skill 激活后的合理上下文开销。
- 加上 Claude 自身的系统提示和对话上下文，总 token 数保持在可控范围。
- 超过 500 行意味着你可能把“参考资料”混进了“路由指令”。

超过 500 行时的重构信号和对策如下：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202604161607384.jpeg)

# 12｜珠联璧合：Skills 与 SubAgent 配合实战

在这一讲中，我们先建立起全局视角，再设计一个好的 Skill，再来看怎么把 Skills 和 SubAgents 配合起来用。

## 两个组合方向：谁包含谁

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202604161705332.jpeg)

当你犹豫到底是用 Skill 还是用 SubAgent 的时候，做出选择的核心判断标准在于：这件事到底需要“另一个人”来承担，还是只需要“多一本手册”来指导？

而更常见的情况是：结合起来使用

**方向 A：SubAgent 包含 Skill（skills 字段）**

此时，SubAgent 是老板，Skill 是工具书。

```markdown
# .claude/agents/api-doc-generator.md
---
name: api-doc-generator
description: Generate API documentation by scanning Express route files.
tools: [Read, Grep, Glob, Write, Bash]
skills:
  - api-generating           # ← 关键：预加载 Skill 作为领域知识
---

You are an API documentation specialist.

## Your Mission
Generate or update API documentation for Express.js routes.
```

这种情况下，Claude Code 的执行流程如下：

```
Claude 主对话: "用 api-doc-generator 为 src/ 生成 API 文档"

主对话                              SubAgent (api-doc-generator)
  │                                    │
  ├─ 创建子代理 + 注入 Skill ──────→ │
  │                                    ├─ 上下文中已有：角色定义 + SKILL.md 全文
  │                                    ├─ 按 SKILL.md 步骤执行任务
  │                                    ├─ 使用 Skill 提供的脚本和模板
  │                                    ├─ 生成文档
  │  ←──── 返回结果摘要 ──────────── │
  ├─ 继续对话                          （子代理结束）
```

适用场景：

- 包括子代理需要特定领域的专业知识来完成任务
- 同一个 Skill 可以被不同角色的 SubAgent 复用

**方向 B：Skill 包含 SubAgent（context: fork）**

在这种情况下，Skill 是老板，SubAgent 是执行者。

```markdown
---
name: deep-research
description: Research a topic thoroughly in the codebase
context: fork           # ← 关键：让 Skill 在独立子代理中执行
agent: Explore          # ← 子代理类型
---

Research $ARGUMENTS thoroughly:

1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

此时的 Claude Code 执行流程如下：

```
用户: /deep-research authentication flow

主对话                              子代理（Explore）
  │                                    │
  ├─ 创建隔离上下文 ────────────────→ │
  │                                    ├─ 收到任务："Research authentication flow..."
  │                                    ├─ Glob/Grep 搜索相关文件
  │                                    ├─ Read 分析代码
  │                                    ├─ 生成结构化摘要
  │  ←──── 返回结果摘要 ──────────── │
  ├─ 继续对话（上下文干净）            （子代理结束）
```

适用场景：

- 研究型任务（深度探索代码库，不污染主对话）
- 重型生成（批量生成文档，中间过程不需要用户看到）
- 安全隔离（Skill 的操作不应影响主对话状态）

下面是两个方向的对照说明表。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202604162226603.jpeg)

## 三种组合模式：具体咋用

**模式一：SubAgent 预加载 Skills（方向 A 的单次应用）**

一个子代理预加载一个或多个 Skill，用领域知识增强自己的能力。这是最常见的模式，也是本讲的实战重点。

```
# 子代理在创建时预加载 Skill 作为领域知识
---
name: api-doc-generator
skills:
  - api-generating              # 预加载 API 文档生成知识
---
```

配置了 Skill 的子代理好比一个经过培训的专业技师。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202604162242538.jpeg)

现在我们来完成最后一步——把  Skill 装进 SubAgent，组装一个领域专家。

> 参考我的代码库06-agent-skill-combo。

```
#.claude/agents/api-doc-generator.md
---
name: api-doc-generator
description: Generate comprehensive API documentation by scanning Express route files.
model: sonnet
tools: [Read, Grep, Glob, Write, Bash]
skills:
  - api-generating           ← 预加载 Skill
---

You are an API documentation specialist.

## Your Mission

Generate or update API documentation for Express.js routes.

### Workflow

1. Run the route detection script as specified in the Skill
2. For each discovered route, analyze the handler code
3. Generate documentation using the Skill's template
4. Verify all routes are covered (cross-check with script output)

### Output

- Write documentation files to `docs/api/`
- Return a summary to the main conversation:
  - Number of routes documented
  - Any routes that could not be fully analyzed (with reasons)
  - Warnings (missing auth, undocumented parameters, etc.)
```

完整项目结构如下所示。

```
06-agent-skill-combo/
├── .claude/
│   ├── agents/
│   │   └── api-doc-generator.md     # SubAgent：角色 + 使命（WHO/WHAT）
│   ├── skills/
│   │   └── api-generating/
│   │       ├── SKILL.md              # Skill：工作流程 + 规则（HOW）
│   │       ├── scripts/
│   │       │   └── detect-routes.py  # 路由检测脚本（处理链式路由）
│   │       └── templates/
│   │           └── api-doc.md        # 文档模板
│   └── settings.local.json           # 权限预配置
├── src/
│   └── routes/
│       ├── users.js                  # 标准 CRUD（5 条路由）
│       └── orders.js                 # 含链式路由（5 条路由）
├── docs/api/                         # 生成的文档（输出目录）
└── README.md
```

下面，在 Claude Code 中，运行 SubAgent：

```
> 用 api-doc-generator 为 src/ 目录生成 API 文档
```

**模式二：Skill + context: fork（方向 B 的直接应用）**

Skill 自带任务指令，Skill 包含 SubAgent，通过 context: fork 派一个子代理去执行。这种模式的适用场景是一个独立完整的任务，不需要与主对话交互，执行完把结果送回来就行。

```markdown
---
name: codebase-research
description: Deep research into codebase topics
context: fork # 关键点！
agent: Explore
---

Research $ARGUMENTS thoroughly...
```

**模式三：流水线中的 Skill 分工（方向 A 的多阶段串联）**

下面我们再往前走一步。思考一下模式一的自然延伸——多个子代理各自预加载不同的 Skill，按阶段串联执行。每个阶段的输出作为下一阶段的输入。

> 配套项目：04-Skills/projects/08-skill-pipeline/

项目整体结构如下。

```
08-skill-pipeline/
├── CLAUDE.md                              ← 流水线编排指令
├── .claude/
│   ├── agents/
│   │   ├── route-scanner.md               ← 阶段 1: 路由扫描专家 (haiku)
│   │   ├── doc-writer.md                  ← 阶段 2: 文档编写专家 (sonnet)
│   │   └── quality-checker.md             ← 阶段 3: 质量检查专家 (haiku)
│   ├── skills/
│   │   ├── route-scanning/
│   │   │   ├── SKILL.md                   ← 扫描工作流程
│   │   │   └── scripts/scan-routes.py     ← 路由扫描脚本
│   │   ├── doc-writing/
│   │   │   ├── SKILL.md                   ← 文档生成工作流程
│   │   │   └── templates/endpoint-doc.md  ← 文档模板
│   │   └── quality-checking/
│   │       ├── SKILL.md                   ← 质量检查工作流程
│   │       └── rules/doc-standards.md     ← 质量标准规则
│   └── settings.local.json
├── src/routes/
│   ├── products.js                        ← 7 条路由（含链式路由）
│   └── categories.js                      ← 5 条路由
└── docs/                                  ← 生成的文档输出
```

一个完整的 API 文档流程可以拆分为三个阶段，每个阶段需要不同的专业能力。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202604202121505.jpeg)

每一个阶段的输入输出流程如下。

```
阶段 1: 分析子代理
  └─ skills: ["code-analyzing"]
  └─ 输出：代码分析报告

阶段 2: 重构子代理
  └─ skills: ["refactoring-patterns"]
  └─ 输入：阶段 1 的报告
  └─ 输出：重构方案

阶段 3: 测试子代理
  └─ skills: ["testing-conventions"]
  └─ 输入：阶段 2 的代码变更
  └─ 输出：测试结果
```

阶段 1：Route Scanner。对应 Skill route-scanning/SKILL.md：包含扫描脚本  scan-routes.py，输出 JSON 格式的路由清单。

```
# .claude/agents/route-scanner.md
---
name: route-scanner
model: haiku                    # 轻量任务用 haiku
tools: [Read, Grep, Glob, Bash]
skills:
  - route-scanning              # 预加载扫描知识
---
You are a route scanning specialist. You are Stage 1 of a documentation pipeline.
```

阶段 2：Doc Writer。对应 Skill doc-writing/SKILL.md：包含文档模板  endpoint-doc.md，按模板生成标准化文档。

```
# .claude/agents/doc-writer.md
---
name: doc-writer
model: sonnet                   # 需要理解代码逻辑，用 sonnet
tools: [Read, Write, Glob]
skills:
  - doc-writing                 # 预加载文档编写知识
---
You are a documentation writing specialist. You are Stage 2 of a documentation pipeline.
```

阶段 3：Quality Checker。对应 Skill quality-checking/SKILL.md：包含质量标准规则  doc-standards.md，逐项检查文档质量。

```
# .claude/agents/quality-checker.md
---
name: quality-checker
model: haiku                    # 规则检查用 haiku 足够
tools: [Read, Grep, Glob]       # 只读，不修改文档
skills:
  - quality-checking            # 预加载质量检查知识
---
You are a documentation quality specialist. You are Stage 3 of a documentation pipeline.
```

流水线的编排逻辑写在  CLAUDE.md 中：

```
# API Documentation Pipeline

When the user asks to run the documentation pipeline:

### Stage 1: Route Scanning
Use the `route-scanner` agent to scan the source directory.
Collect the route manifest (JSON) from its output.

### Stage 2: Documentation Generation
Use the `doc-writer` agent to generate documentation.
Pass the route manifest from Stage 1 as input context.

### Stage 3: Quality Validation
Use the `quality-checker` agent to validate the generated docs.
Report the quality verdict to the user.
```

编排的关键在于每个阶段的输出是下一阶段的输入。下面进行运行与验证。

```
# 先验证扫描脚本
python3 .claude/skills/route-scanning/scripts/scan-routes.py src/
# 预期：发现 12 条路由（products 7 条 + categories 5 条）

# 运行完整流水线
> 对 src/ 目录运行文档流水线

# 或者分阶段手动运行
> 用 route-scanner 扫描 src/ 目录的路由
> 用 doc-writer 根据上面的路由清单生成文档
> 用 quality-checker 验证 docs/ 目录下生成的文档
```

**三种模式完整对照**

为了帮你更好地理解和区分，我将这三种模式总结成了一张表。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202604202130264.jpeg)

实际项目中，你觉得哪种模式最常用？——我感觉当然是第一种。

# 13｜纲举目张：Skills 架构定位与高级能力



## Skills 在 Claude Code 架构中的位置



## 三级进化——从 SOP 到组织智能

## Skill 设计的四种模式

## 权限体系与安全设计

