> 来自极客时间《Claude Code工程化实战》--黄佳

# <mark>工程化进阶（17~20）</mark>

# 19｜无人值守：Headless 模式与 CI/CD 集成



# 20｜有章可循：Rules 规则系统深度剖析

上一讲我们学习了 Headless 模式，让 Claude Code 在无人值守的情况下嵌入 CI/CD 流水线自动运行。Headless 解决了没有人盯着的问题，但也让一个追问变得更加尖锐，没人盯着的时候，谁来定规矩？

这就引出了今天的主题——规则系统。

我发现一个有趣的现象：很多同学把两种“规则“搞混了。有人问“rules 目录里能不能禁止 Claude 执行  rm 命令？”答案是不能，那是权限规则的事；也有人问“settings.json 里能不能告诉 Claude 用 TypeScript 写代码？”答案也是不能，那是指令规则的事。

这两种规则解决的是完全不同的问题。今天我们就来把 Claude Code 中所有规则的全貌讲清楚。

## 两种规则，两个世界

Claude Code 中的“规则”分布在两个完全不同的层面：

![img](https://static001.geekbang.org/resource/image/b5/4e/b5e2690885bdd4edf4172a16d24a494e.jpg?wh=3145x1485)

我用一个比喻来帮你区分它们，指令规则像公司的员工手册，写着“代码提交前必须跑测试”，员工可以遵守，也可以偷懒。权限规则像门禁系统——没有卡就进不了机房，系统不给你选择。

![img](https://static001.geekbang.org/resource/image/30/1a/300a0d19d9c046aab881a87a45ea561a.jpg?wh=1639x1046)

指令规则是 Claude 的认知约束，权限规则是客户端的行为约束。

![img](https://static001.geekbang.org/resource/image/4c/86/4c5c473a3d4c3a7ayy7b59ayye3d0786.jpg?wh=2504x1195)

## 指令规则——.claude/rules/ 完全指南

也许看完前面说的你还是有点懵，别急，咱们继续探索规则背后的工作机制。

**它到底是什么？**

.claude/rules/ 目录下的每个  .md 文件，本质上就是一段会被注入 System Prompt 的文本。它和 CLAUDE.md 没有本质区别——都是 Claude 在每轮 API 调用中“看到”的指令。唯一的结构化优势是，它可以按主题拆分成多个文件，还支持条件加载。

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

模式一：全局加载（无 paths 字段）

```
# security.md —— 没有 YAML 头部，或有头部但不含 paths

## 安全规范
- 不在代码中硬编码密码或 API Key
- 所有用户输入必须做 sanitize
- SQL 查询使用参数化，不拼接字符串
```

这种 rule 在会话启动时就加载进上下文，行为和写在 CLAUDE.md 里完全一样。拆出来的唯一好处是文件组织更清晰。

模式二：条件加载（有 paths 字段）

```
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

这个设计很精妙——如果你的测试规范有 50 行，而你这次只是在改一个 CSS 样式，那这 50 行规范就不会浪费上下文空间。

但有一个关键细节，一旦加载，就不会卸载。paths 控制的是何时加载，不是何时生效。如果你在会话中先编辑了一个测试文件，testing.md 被加载了，然后你去改 CSS，testing.md 仍然在上下文里。

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
│   │
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

## 实战：一个全栈项目的 rules 拆分

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

拆分出的 rules 文件

.claude/rules/frontend.md：

```
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

.claude/rules/backend.md：

```
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

.claude/rules/testing.md：

```
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

.claude/rules/security.md（注意，没有 paths，全局生效）：

```
# 安全规范

- 用户输入在使用前必须 validate + sanitize
- SQL 参数化（Prisma 默认做到了）
- XSS 防护：不使用 dangerouslySetInnerHTML
- CORS 只允许白名单域名
- 敏感信息（API Key、数据库密码）只放 .env
- 认证 token 用 httpOnly cookie，不存 localStorage
```

拆完之后，CLAUDE.md 从 600 行变成 80 行，但规范一条都没少——只是按需加载了。当 Claude 在改前端组件时，它看到的是 CLAUDE.md + frontend.md + security.md。当它在写测试时，看到的是 CLAUDE.md + testing.md + security.md。精准、高效。

![img](https://static001.geekbang.org/resource/image/d1/20/d1a7bee9448f17bc595a2c023269e820.jpg?wh=2454x1584)

## 权限规则——行为管控的硬约束

指令规则告诉 Claude“你应该怎么做”，权限规则告诉 Claude“你被允许做什么”。

权限规则写在  .claude/settings.json 或  .claude/settings.local.json 中，由 Claude Code 客户端在工具调用前硬拦截。Claude 根本看不到这些规则——它只知道某个操作被允许了或被拒绝了。

**基本结构与评估逻辑**

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

评估顺序：deny → ask → allow。 第一个匹配的规则胜出，deny 总是优先。就算你在 allow 里写了  Bash(rm -rf *)，如果 deny 里也有这条，deny 赢。安全规则应该有最高话语权。

**权限规则覆盖的工具范围**

```
内置工具的权限控制：

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

**配置层级体系**

权限配置可以在四个层级设置，高优先级覆盖低优先级。

![img](https://static001.geekbang.org/resource/image/d1/9f/d1264e131a814c20bbbc5e2a87e7809f.jpg?wh=3327x1839)

关键规则：高层级的 deny 不可被低层级覆盖。 如果组织策略禁止了  Bash(curl *)，项目配置和个人配置都无法解除这个限制。这是企业级安全管控的基石。

**权限规则在扩展机制中的渗透**

权限规则不仅存在于 settings.json 中，它还渗透到了 Claude Code 的各个扩展机制里。

Skills 中的 allowed-tools，Skill 被触发时只能使用白名单中的工具：

```
---
name: code-reviewing
description: Review code for quality and security issues
allowed-tools:
  - Read
  - Grep
  - Glob
---
```

Sub-Agents 中的 tools，子代理的工具集更加严格，甚至拿不到主对话的 CLAUDE.md。

```
---
name: code-reviewer
tools: Read, Grep, Glob
model: sonnet
---
```

Hooks 中的动态拦截，最灵活的权限控制，可以根据动态条件决定是否放行。

```
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

## **两种规则的协同——一个完整案例**

让我们用一个真实场景把两种规则串起来：你的团队有一个支付服务项目，既需要编码规范（指令规则），也需要安全管控（权限规则）。

**指令规则部分**

CLAUDE.md（精简版，~60 行）：

```
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

.claude/rules/stripe.md：

```
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

.claude/settings.json（团队共享）：

```
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

- 禁止  curl/wget——防止 Claude 自行调用外部 API（包括 Stripe API）
- 禁止读写  .env——保护 Stripe Secret Key 等敏感配置
- 禁止  stripe *——防止 Claude 用 Stripe CLI 直接操作生产环境
- 禁止  rm -rf 和  --force——防止破坏性操作

两种规则各司其职， 指令规则告诉 Claude“处理 webhook 要验签、金额用 cents”——这是认知层面的约束，让 Claude 写出正确的代码。权限规则告诉客户端“不许读 .env、不许执行 stripe CLI”——这是行为层面的约束，从系统层面堵住安全漏洞。

即使 Claude“忘记”了指令规则中不在日志中打印卡号的要求，权限规则也能确保它无法读取 .env 中的 Stripe Key。纵深防御，不依赖单一层面。

![img](https://static001.geekbang.org/resource/image/d0/80/d0c5eb669fdf10fea5645a495608a080.jpg?wh=8886x4094)

## 架构定位与最佳实践

**Rules 在架构中的定位**

“规则”不是架构中的一个方块，而是渗透在每一层中的横切关注点。

![image-20260521200043975](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202605212001009.png)

- 指令层有指令规则（CLAUDE.md、.claude/rules/）
- 能力层有能力规则（Skills 的 allowed-tools、Agent 的 tools）
- 管控层有权限规则（settings.json、Hooks、CLI 参数）

这就像安全不是软件中的一个模块，而是贯穿所有模块的设计原则。这里我也顺便说明一下 Rules 的正确学习路径。

![img](https://static001.geekbang.org/resource/image/48/1b/481839c6e52e1ede9fb59b5d935de71b.jpg?wh=2615x965)

每一讲都在从自己的角度教 Rules 的一个切面。这一讲的价值，就是帮你把这些碎片拼成全景图。

**实用模型**

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

```
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

这个模版你要根据你的项目调整。如果用 Python 就把  pnpm 换成  pip/uv；如果需要 Claude 访问特定 API，就在 allow 中加  WebFetch(domain:your-api.com)。

**常见错误清单**

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

## 总结一下

这一讲我们把 Claude Code 中所有的“规则“做了一次全景梳理。

两种规则，两个世界，明白两个规则的本质是用对它们的前提。指令规则（CLAUDE.md、.claude/rules/）是认知约束，注入 System Prompt 让 Claude 知道该怎么做；权限规则（settings.json permissions）是行为约束，由客户端硬拦截让 Claude 做不了不该做的事。

指令规则有两种加载模式，无 paths 字段的全局加载，有 paths 字段的条件加载。条件加载省 token 又精准，但加载后不会卸载。CLAUDE.md 超过 200 行就考虑拆分，超过 500 行必须拆分。3-5 个 rules 文件是最佳规模。

权限规则重点掌握它的纵深防御设计，settings.json deny → Hooks PreToolUse → Skill/Agent allowed-tools → settings.json allow / 用户审批，四层拦截逐级递进。高层级 deny 不可被低层级覆盖。

Rules 不是独立组件，是横切关注点，它渗透在 Memory、Tools、Skills、SubAgents、Hooks 每一讲中。指令规则让 Claude 做对，权限规则让 Claude 做不了错。两者协同，才是完整的规则体系。

到这里，我们已经完整学习了 Claude Code 的所有核心扩展机制——Memory（记忆）、SubAgents（分工）、Skills（领域能力）、Commands（标准流程）、Hooks（安全防护）、MCP（外部连接）、Tools（工具基础）、Rules（行为约束）。所有这些都有一个共同前提：需要人在终端前交互。下一讲，我们将打破这个前提。