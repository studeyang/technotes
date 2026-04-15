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





