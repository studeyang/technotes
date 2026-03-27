> 参考资料：https://docs.trae.cn/

# 一、什么是 TRAE ？

TRAE（/treɪ/）是一名能够理解需求、调用工具并独立完成各类开发任务的“AI 开发工程师”，帮助你高效推进每一个项目。

TRAE 不仅将 AI 集成进 IDE，也让 Al 使用更多开发工具。TRAE 目前拥有双重开发模式：

- **IDE 模式**：保留原有流程，控制感更强；
- [**SOLO 模式**]()：让 AI 主导任务，自动推进开发任务。

# 二、教程&最佳实践

## 2.1 研发场景十大热门 Skill 推荐

1、前端设计

https://github.com/anthropics/skills/tree/main/skills/frontend-design

应用场景：

- 构建网页组件或页面
- 开发完整的 Web 应用或网站
- 美化或重塑现有界面

2、前端开发

https://github.com/vercel/next.js/tree/canary/.claude-plugin/plugins/cache-components/skills/cache-components

应用场景

- 自动生成缓存优化的数据组件
- 自动实现数据变更后的缓存失效
- 智能化页面构建与代码现代化

3、全栈开发

https://github.com/Shubhamsaboo/awesome-llm-apps/tree/main/awesome_agent_skills/fullstack-developer

应用场景

- 构建完整的 Web 应用
- 开发 API：创建 RESTful 或 GraphQL 风格的后端接口。
- 创建前端界面：使用 React 或 Next.js 构建现代化的用户界面。
- 数据库和数据建模：设计和设置如 PostgreSQL 或 MongoDB 等数据库。
- 实现用户认证与授权：集成 JWT、OAuth 等认证机制。
- 部署与扩展应用：提供在 Vercel、Netlify 等平台上的部署指导。
- 集成第三方服务：在应用中接入外部服务。

4、代码审查（通用）

https://github.com/google-gemini/gemini-cli/tree/main/.gemini/skills/code-reviewer

应用场景

- 审查远程 PR
- 审查本地代码变更
- 提供深度分析与结构化反馈

5、网页应用测试

https://github.com/anthropics/skills/tree/main/skills/webapp-testing

应用场景

- 自动验证前端功能：用自然语言告知 AI 测试需求（例如：“帮我测试登录功能”）
- 调试与分析 UI 行为

6、技术文档更新

https://github.com/vercel/next.js/tree/canary/.claude/skills/update-docs

应用场景

- 分析代码变更对文档的影响
- 更新现有的文档
- 为新功能创建脚手架文档

7、查找 Skill

https://github.com/vercel-labs/skills/tree/main/skills/find-skills

应用场景

- 探索未知的 Skill：询问 “你能帮我评审代码吗？” 或 “如何为我的项目生成文档？” 时，该 Skill 会被激活，主动在技能市场中搜索与 “代码评审” 或“ 文档生成” 相关的能力，并将找到的可用技能呈现给你。
- 查找特定的 Skill：你可以直接说 “帮我找一个用于 React 性能优化的 skill”，该 Skill 会将 “React 性能优化” 作为关键词进行搜索，并返回最匹配的技能选项，如 “vercel-react-best-practices”。

## 2.2 如何写好一个 Skill：从创建到迭代的最佳实践

一个 Skill 是一份清晰、严谨、可执行的指令文档，用于明确告诉模型——在什么条件下（When），按照哪些步骤（How），产出什么结果（What）。

**Skill 的设计标准与原则**

1、精准的元数据内容

Skill 的元数据（name 和 description）是模型发现和识别 Skill 的入口，其设计直接影响触发准确率。

2、指导方式的自由度分级

- 提供启发式策略（给原则）
- 提供模板/伪代码（给框架）
- 提供可执行的脚本（给代码）

3、五个核心标准

- 边界明确：Skill 的触发必须有明确的正向条件和负向条件，否则命中率会很低。
- 输入输出结构化：推荐用类似函数签名的方式明确 Input 和 Output，保证可解析性。
- 步骤明确、可执行：Skill 的核心是“步骤”，必须是**指令式、具体动作**，而不是概括性描述，确保模型可以按步骤执行。
- 失败策略完备：必须明确定义“失败路径”，告诉模型在不同失败情况下如何处理。
- 职责绝对单一：避免把多个功能捆绑在一个 Skill 中，否则复杂性和不确定性会增加，模型难以准确理解。

4、让 Skill 可维护与可拓展

为了确保 Skill 在长期运行中保持稳定、易用且可持续拓展，需要从信息结构、工作流设计和脚本可靠性三个维度进行规划。

信息结构（渐进式披露）：

```markdown
<!--
1、保持 SKILL.md 简洁：主体内容尽量控制在 500 行以内，只包含必要信息。
2、避免深度嵌套：所有引用文件最好直接由 SKILL.md 链接，保持一层引用深度，避免链式引用（A → B → C），防止模型只读取部分内容。
3、为长文件添加目录：对于超过 100 行的参考文件，在文件顶部添加一个目录（Table of Contents），帮助模型快速了解文件结构。
-->

# SKILL.md

## 基础用法
描述如何触发 CI/CD 流水线：
- 检查 PR 状态
- 执行单元测试
- 更新 PR 测试状态

## 高级功能
详细说明请参见 `ci-advanced-features.md`：
- 并行执行多分支测试
- 条件触发不同类型的测试
- 自定义失败处理策略

## API 参考
所有方法与参数说明请参见 `ci-api-reference.md`：
- startPipeline(prId: string, branch: string)
- getPipelineStatus(pipelineId: string)
- cancelPipeline(pipelineId: string)

```

工作流设计（反馈闭环）：

对于包含多个步骤、且中间结果会影响最终质量的复杂任务，仅提供最终目标是不够的。必须显式定义工作流（Workflow）和 检查清单（Checklist），引导模型按步骤执行，并在关键节点建立 “验证 → 修正 → 再验证” 的反馈闭环。

工作流负责约束任务执行顺序，检查清单负责追踪任务的执行状态和质量。两者结合可以显著降低遗漏和跑偏的风险。

脚本可靠性（加固原则）：

Skill 本身不会理解或阅读你的代码逻辑，它只感知输入与输出。一旦脚本行为不可预测，模型就只能猜测，最终导致不稳定或错误的调用结果。因此，脚本必须做到：失败可预期、输出可理解、参数可解释。

5、使用 AI 来创建和迭代 Skill

你负责定义问题和验收结果，AI 负责反复试错、总结规律并封装成可复用的 Skill。

阶段一：初次创建（从具体任务中抽象）

1. 让 AI 直接执行真实任务：提供完整目标与上下文，让 AI 自行尝试完成任务。
2. 引导 AI 进行结构化复盘：任务完成后，要求 AI 从以下维度复盘：
   - 成功执行任务的完整步骤；
   - 任务执行过程中的不确定性与失败点；
   - 可抽象的固定流程与判断逻辑；
   - 该流程和判断逻辑的适用场景与不适用场景。
3. 基于复盘生成 Skill 初稿：要求 AI 按 Skill 规范生成 SKILL.md，明确：触发条件（When）、如何执行（How）、输出结果（What）、预设失败策略。
4. 人工快速评审并入库：你只需关注边界是否合理、步骤是否可执行，其余交由 AI 完成。确认后，让 AI 调用 skills-creator 正式创建该 Skill 并添加至你的项目。

阶段二：持续迭代（从使用反馈中优化）

# 三、SOLO

## 3.1 SOLO 模式概览











