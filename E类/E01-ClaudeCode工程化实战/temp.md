# 02｜过目不忘：Claude Code记忆系统与CLAUDE.md

CLAUDE.md 是一份给 Claude 的“项目入职手册”——Claude 每次开始对话时，都会自动阅读这份手册，了解你的项目背景，明确它在干活时应该遵循的一系列底层规则。

这一讲，我们就来学习 Claude Code 如何对抗“失忆症”，记住必要信息。

**Claude Code 记忆系统的工作原理**

当你在项目目录启动 Claude Code 时，发生的“记忆系统初始化”过程如下图所示。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202603092030365.jpeg)

CLAUDE.md 的内容会每次对话都加载，所以要精简。把“每次都需要”的内容放这里，把“偶尔需要”的内容放到 Skills 或文档里。

**Claude Code 的四层记忆架构**

Claude Code 提供四个层级的记忆，按优先级从高到低：

```
┌─────────────────────────────────┐
│     ~/.claude/CLAUDE.md         │  ← 用户级（全局）
├─────────────────────────────────┤
│     ./CLAUDE.md                 │  ← 项目级（团队共享）
├─────────────────────────────────┤
│     ./CLAUDE.local.md           │  ← 项目本地（个人）
├─────────────────────────────────┤
│     ./.claude/rules/*.md        │  ← 规则目录（分类规则）
└─────────────────────────────────┘
```

1、用户级（全局）

用户级内容设定承载的是你的全局偏好，即跨所有项目生效的个人偏好，如个人代码风格，沟通语言设置，通用工作习惯等。

位置：~/.claude/CLAUDE.md

示例：

```markdown
# 个人偏好

## 沟通方式
- 使用中文回复
- 代码注释使用英文
- 解释简洁直接，不要过多铺垫

## 通用代码风格
- 缩进使用 2 空格
- 优先使用 async/await
- 变量命名使用 camelCase
- 常量命名使用 UPPER_SNAKE_CASE

## 我的常用工具
- 包管理器: uv
- 编辑器: VS Code
- 终端: zsh
```

2、项目级（团队共享规范）

团队共享规范是团队共享的项目知识，应该提交到 Git。适合存放的内容包括项目架构和技术栈、团队编码规范、重要的设计决策和常用命令。

位置：项目根目录的  ./CLAUDE.md

示例（一个后端 API 项目）：

~~~markdown
# 项目：订单服务 API

## 技术栈
- Node.js 20 + TypeScript
- Fastify（Web 框架）
- Prisma（ORM）
- PostgreSQL + Redis
- Zod（数据验证）

## 目录结构
src/ 
├── routes/ # 路由定义 
├── controllers/ # 请求处理 
├── services/ # 业务逻辑 
├── repositories/ # 数据访问 
├── schemas/ # Zod schemas 
└── types/ # 类型定义

## API 响应格式
```typescript
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: { code: string; message: string };
}
编码规范
- TypeScript strict 模式
- 禁止使用 any，使用 unknown + 类型守卫
- 所有 API 端点必须有 Zod schema 验证
- 业务错误使用自定义 Error 类
常用命令
- pnpm dev - 启动开发服务器
- pnpm test - 运行测试
- pnpm prisma migrate dev - 运行数据库迁移
~~~

3、项目本地（个人）

个人工作空间用于记载个人工作笔记，不提交到 Git，适合内容包括本地环境配置、个人调试技巧、当前工作备注，敏感信息（测试账号等）。

> 这里重点强调一下：记得把  CLAUDE.local.md 加入  .gitignore！

位置：项目根目录的./CLAUDE.local.md

示例：

```markdown
# 本地开发笔记

## 我的环境
- 本地 API: http://localhost:3000
- 测试数据库: order_service_dev
- Redis: localhost:6379

## 测试账号
- admin@test.com / test123
- user@test.com / test123

## 当前工作
- 正在重构支付模块
- 参考 PR #234 的讨论
- 周五前完成

## 调试技巧
- 订单状态机日志: LOG_LEVEL=debug pnpm dev
- 查看 Redis 缓存: redis-cli KEYS "order:*"
```

4、规则目录（分类规则）

Rules 是按主题组织的规则文件，支持条件作用域（也就是视情况来确定是否加载该记忆内容），适合场景包括 CLAUDE.md 变得太长时，不同文件类型需要不同规范时，以及前后端分离的项目。

位置：.claude/rules/*.md

目录结构：

```
.claude/
└── rules/
    ├── typescript.md      # TypeScript 规范
    ├── testing.md         # 测试规范
    ├── api-design.md      # API 设计规范
    └── security.md        # 安全规范
```

条件作用域示例：.claude/rules/testing.md

> 此处的关键特性是paths字段让这个规则只在编辑测试文件时生效，不会浪费其他场景的上下文空间。

~~~markdown
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
使用 Arrange-Act-Assert 模式：

```typescript
describe('OrderService', () => {
  describe('createOrder', () => {
    it('should create order when stock is available', async () => {
      // Arrange
      const mockProduct = createMockProduct({ stock: 10 });

      // Act
      const order = await orderService.createOrder(mockProduct.id, 1);

      // Assert
      expect(order.status).toBe('created');
    });
  });
});

## 覆盖率要求
- 业务逻辑: > 80%
- 工具函数: > 90%
- 路由/控制器: 可以较低
~~~

**编写高效的 CLAUDE.md**

- 核心原则 1：Less is More

CLAUDE.md 的每一行，都会在每一次对话开始时被自动注入上下文。所以必须保持精简。

- 核心原则 2：具体优于泛泛

先来看一个非常常见、但几乎没有任何效果的写法。

```markdown
# 项目规范
## 代码质量
请写出高质量的代码。代码应该是可读的。使用有意义的变量名。
保持代码整洁。遵循最佳实践。不要写重复的代码。
```

真正有价值的 CLAUDE.md，应该长这样。

~~~markdown
# 项目规范

## TypeScript
- 使用 `interface` 定义对象结构，`type` 用于联合类型
- 禁止 `any`，使用 `unknown` + 类型守卫
- 函数参数 > 3 个时，使用对象参数

## 错误处理
```typescript
// 业务错误
throw new BusinessError('ORDER_NOT_FOUND', '订单不存在');

// 验证错误（Zod 自动抛出）
const data = orderSchema.parse(input);

// controller 中不要 try-catch
// 由全局错误中间件统一处理
~~~

- 核心原则 3：关键三问题 WHY / WHAT / HOW

一份真正“能用”的 CLAUDE.md，通常都在回答三个问题。不是一次性回答，而是在关键地方给出明确指引。

WHY —— 为什么要这样做？

```markdown
## 为什么使用 Zod？
- TypeScript 只有编译时类型检查
- API 输入需要运行时验证
- Zod 可以同时生成 TS 类型和验证逻辑
- 错误信息自动生成，对用户友好
```

这一部分的作用，不是让 Claude “记住一个库”，而是让它理解背后的决策逻辑。当 Claude 明白了为什么，它在面对相似但不完全相同的场景时，才更可能做出一致的判断。

WHAT —— 具体要做什么，不要做什么？

```markdown
## 数据库操作规范
- 所有查询通过 Prisma ORM
- 复杂查询封装在 `src/repositories/`
- 禁止在 controller/service 中直接写 SQL
- 事务使用 `prisma.$transaction()`
```

这一部分的重点是边界。什么是允许的，什么是禁止的，决策应该发生在哪一层？对 Claude 来说，这比“最佳实践”四个字重要得多。

HOW —— 按什么步骤去做？

```markdown
## 创建新 API 端点

1. 在 `src/schemas/` 创建请求/响应 Zod schema
2. 在 `src/routes/` 添加路由定义
3. 在 `src/controllers/` 实现请求处理
4. 在 `src/services/` 实现业务逻辑
5. 在 `tests/` 添加测试用例

示例参考: `src/routes/orders.ts`
```

当步骤清晰、路径明确、还有参考文件时，Claude 才会稳定复用同一套工作流，而不是每次自由发挥。

- 核心原则 4：渐进式披露：不要把一切都塞进 CLAUDE.md

CLAUDE.md 的职责是定义默认决策，而不是承载全部知识。对于非核心、但可能被用到的内容，正确的做法是引用，而不是复制。

```markdown
# 项目规范

## 核心
[精简的核心规范]

## 详细文档
- 数据库设计: 见 `docs/database.md`
- API 规范: 见 `docs/api-spec.md`
- 部署流程: 见 `docs/deployment.md`
```

**CLAUDE.md 实战演练一：为新项目创建记忆**

假设你刚接手一个 React + TypeScript 前端项目，让我们从零配置记忆。

Step 1：创建基础 CLAUDE.md

先通过 /init 命令自动初始化 CLAUDE.md 文件，或使用下面的命令在项目根目录手动创建记忆文件。

Step 2：创建本地记忆

Step 3：添加条件规则（可选）

**CLAUDE.md 实战演练二：优化已有的 CLAUDE.md**

假设你的 CLAUDE.md 已经有 500 行，Claude 开始变慢。此时就需要给它瘦个身，做一些优化了。

识别核心内容：

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202603092142451.jpeg)

**CLAUDE.md 实战演练三：记忆管理命令**

查看当前记忆：

```
/memory
```

编辑记忆的命令参数如下：

```
/memory edit         # 编辑项目级 CLAUDE.md
/memory edit user    # 编辑用户级记忆
/memory edit local   # 编辑本地级记忆
```

你也可以通过自然语言指令，让 Claude 帮你更新记忆！

```
你：请记住，我们项目使用 pnpm 而不是 npm

Claude：好的，我可以将这个信息添加到项目的 CLAUDE.md 中。
        要我现在更新吗？
```

**Auto Memory 解读**

Claude Code 本身拥有自动记忆功能，随着项目的演进和对话的深入，会在 ~/.claude/projects//memory/ 目录下自动生成 Auto Memory，用于记录模型在项目中学习到的模式、调试经验与结构认知。

CLAUDE.md 决定“系统被告知什么”，而 Auto Memory 决定“系统在实践中学到了什么”。记忆因此成为一种结构化的工程能力，而不是简单的对话缓存。

