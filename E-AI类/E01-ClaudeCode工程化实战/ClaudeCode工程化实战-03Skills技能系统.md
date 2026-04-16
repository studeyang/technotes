> 来自极客时间《Claude Code工程化实战》--黄佳

# <mark>Skills 技能系统（09~14）</mark>

# 09｜触类旁通：SKILL.md 结构与触发机制

**什么是 Skills**

Skills 是一种可被语义触发的能力包，它包含领域知识、执行步骤、输出规范与约束条件。

Skills 解决的核心问题是，在有限的上下文窗口中，让 Agent 在正确的时刻拥有正确的领域知识。

**深入理解 Skill 触发机制**

在 Claude Code 中，Skills 默认情况下支持两种触发方式。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202604151019848.jpeg)

> 语义触发Skills的机制

Claude 读取所有 Skills 的 description，通过语义理解判断当前对话是否匹配某个 Skill。当用户发送消息时，Claude 的处理流程如下图所示：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202604151020583.jpeg)

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
allowed-tools:                     # 可选：限制可用工具
  - Read
  - Grep
  - Glob
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

**Skills vs Commands**

早期，斜杠命令 /Comands 和 Skills 是两个独立组件。但在新版 Claude Code 中，Commands 已合并到 Skills，成为 Skills 的子集。

因此，在 .claude/commands/review.md 和  .claude/skills/review/SKILL.md 两个不同目录的文件，都会创建  /review。。如果同名 Skill 和 Command 共存，Skill 优先。

> Skills 目录的额外优势是支持辅助文件目录（模板、示例、脚本等）。

**通过 ARGUMENTS 给 Skill 传参**

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

- 单参数——$ARGUMENTS 接收所有参数。

```markdown
---
description: Quick git commit
argument-hint: [commit message]
disable-model-invocation: true
---

Create a git commit with message: $ARGUMENTS
```

用法：`/commit fix login bug`

- 多参数—— $1，$2 接收位置参数：

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

**! `command` 动态上下文注入**

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

**实战项目：团队标准命令集**

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

- 命令一：智能提交 /commit

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

- 命令二：代码审查 /review

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

- 命令三：创建 PR /pr-create

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

**渐进式披露的设计哲学**



**认知经济学：上下文窗口是稀缺资源**



**渐进式的设计模式与最佳实践**



**内容拆分的工程方法论**















