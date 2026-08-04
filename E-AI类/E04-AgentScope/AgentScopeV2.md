> 参考资料：https://java.agentscope.io/v2/zh/docs/index.html

# 01 | 快速开始

`ReActAgent` 只有”请求-推理-工具-回复”一轮循环。harness 要回答的是另一组问题：下一轮怎么办、下一天怎么办、上下文爆了怎么办、状态丢了怎么办、任务太重怎么办。

引入依赖：

```xml
<dependency>
    <groupId>io.agentscope</groupId>
    <artifactId>agentscope-harness</artifactId>
    <version>${agentscope.version}</version>
</dependency>
```

下面的例子用 `HarnessAgent` 跑通三件事：工作区驱动的人格（`AGENTS.md`）、会话自动持久化（相同 `sessionId` 的第二轮记得第一轮）、对话压缩（超阈值后自动压缩 + 长期事实落到 `MEMORY.md`）。

```java
import io.agentscope.core.agent.RuntimeContext;
import io.agentscope.core.message.UserMessage;
import io.agentscope.harness.agent.HarnessAgent;
import io.agentscope.harness.agent.memory.compaction.CompactionConfig;
import java.nio.file.Paths;

public class FirstAgent {
    public static void main(String[] args) {
        HarnessAgent agent = HarnessAgent.builder()
                .name("note-taker")
                .sysPrompt("你是一个帮助用户做笔记的助手。")
                .model("dashscope:qwen-plus")
                // 工作区驱动的人格（AGENTS.md）在这个目录
                .workspace(Paths.get(".agentscope/workspace"))
                // 对话压缩
                .compaction(CompactionConfig.builder()
                        .triggerMessages(30)
                        .keepMessages(10)
                        .build())
                .build();

        // 会话自动持久化
        RuntimeContext ctx = RuntimeContext.builder()
                .sessionId("demo-session")
                .userId("alice")
                .build();

        // 第一轮：自我介绍 + 当天的事
        agent.call(new UserMessage("我叫天宇，今天准备一个关于 ReAct 的技术分享。"), ctx).block();
        // 第二轮：同 sessionId，自动恢复上一轮状态后回答
        agent.call(new UserMessage("我叫什么？我今天要干什么？"), ctx).block();
    }
}
```

**流式查看推理与工具调用**

```java
import io.agentscope.core.event.AgentEventType;
import io.agentscope.core.event.TextBlockDeltaEvent;
import io.agentscope.core.event.ToolCallStartEvent;

agent.streamEvents(new UserMessage("帮我把今天的关键点列三条。"))
        .doOnNext(event -> {
            if (event.getType() == AgentEventType.TEXT_BLOCK_DELTA) {
                // 模型返回的流式文本片段 —— 追加到界面或标准输出
                System.out.print(((TextBlockDeltaEvent) event).getDelta());
            } else if (event.getType() == AgentEventType.TOOL_CALL_START) {
                // 智能体即将调用工具 —— 展示调用信息
                System.out.println("\n[tool] " + ((ToolCallStartEvent) event).getToolCallName());
            }
            // 其他事件：思考块、工具结果、回复结束等
        })
        .blockLast();
```

# 02 | 核心组件

## 2.1 智能体

`Agent`（接口位于 `io.agentscope.core.agent.Agent`，默认实现是 `ReActAgent`）是 AgentScope 的核心抽象。

**概述**

智能体在每次 `call` 调用时运行推理-行动循环，下图展示了主要控制流程：

![image-20260727164246993](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202607271642693.png)

**配置智能体**

```java
import io.agentscope.core.ReActAgent;
import io.agentscope.core.tool.Toolkit;

ReActAgent agent =
        ReActAgent.builder()
                .name("my_agent")
                .sysPrompt("你是一个有帮助的助手。")
                // 由 ModelRegistry 解析；自动读取 DASHSCOPE_API_KEY
                // 切换其他厂商时改成 "openai:gpt-5.5" / "anthropic:claude-sonnet-4-5"
                // / "deepseek:deepseek-v4-flash" / "gemini:gemini-2.0-flash" / "ollama:llama3" 即可。
                .model("dashscope:qwen-plus")
                .toolkit(new Toolkit())
                .build();
```

**中断执行（Interrupt）**

当需要从外部中断一个正在运行的 agent call 时（用户取消、超时、优雅停机），使用 `interrupt`：

```java
import io.agentscope.core.agent.RuntimeContext;

// 构造标识目标 session 的 RuntimeContext
RuntimeContext target = RuntimeContext.builder()
        .userId("alice")
        .sessionId("session-001")
        .build();

// 中断该 session 正在进行的 call
agent.interrupt(target);

// 带消息中断——中断消息会被 LLM 在恢复时看到
agent.interrupt(target, new UserMessage("用户已取消操作"));
```

中断是 per-session 的：只影响指定 `(userId, sessionId)` 的 in-flight call，不会波及同一 agent 上其他 session 的并发请求。

中断后的行为：

- 当前推理/工具执行在下一个检查点（reasoning 开始、acting 开始、streaming 每个 chunk）被拦截
- agent 返回一个带 `GenerateReason.INTERRUPTED` 标记的 Msg
- 对话上下文（AgentState）自动保存——下次对同一 session 发起 `call()` 时从中断点恢复

**运行智能体**

`streamEvents` 逐一产出 `AgentEvent` 对象，让你实时将文本输出、工具调用进度和生命周期事件流式传输给用户。

```java
import io.agentscope.core.event.AgentEventType;
import io.agentscope.core.event.TextBlockDeltaEvent;
import io.agentscope.core.event.ToolCallStartEvent;

agent.streamEvents(new UserMessage("总结一下 README 的内容。"))
        .doOnNext(event -> {
            if (event.getType() == AgentEventType.TEXT_BLOCK_DELTA) {
                // 模型返回的流式文本片段 —— 追加到界面或标准输出
                System.out.print(((TextBlockDeltaEvent) event).getDelta());
            } else if (event.getType() == AgentEventType.TOOL_CALL_START) {
                // 智能体即将调用工具 —— 展示调用信息
                System.out.println("\n[tool] " + ((ToolCallStartEvent) event).getToolCallName());
            }
            // 其他事件：思考块、工具结果、回复结束等
        })
        .blockLast();
```

**RuntimeContext (per-call 上下文)**

```java
import io.agentscope.core.agent.RuntimeContext;
import io.agentscope.core.message.Msg;
import io.agentscope.core.message.UserMessage;
import java.util.List;

RuntimeContext ctx = RuntimeContext.builder()
                // 可选；null 表示匿名
                .userId("alice")
                // 选择状态槽位
                .sessionId("session-001")
                // 字符串层
                .put("request_id", "req-abc-123")
                // 类型层（业务 POJO）
                .put(UserContext.class, new UserContext("alice", "en"))
                .build();

Msg result = agent.call(List.of(new UserMessage("Hi.")), ctx).block();
```

**人机交互**

1、用户确认

当权限系统判断某个工具调用需要用户批准时，智能体会发出 `RequireUserConfirmEvent` 并暂停。

```java
//接收 RequireUserConfirmEvent —— 用 streamEvents 监听暂停
agent.streamEvents(msg)
        .doOnNext(event -> {
            if (event instanceof RequireUserConfirmEvent confirm) {
                confirm.getToolCalls().forEach(tc -> {
                    System.out.println("工具: " + tc.getName() + ", 输入: " + tc.getInput());
                    System.out.println("建议规则: " + tc.getSuggestedRules());
                });
            }
        })
        .blockLast();

//构建确认结果 —— 为每个待处理工具调用构造一个 ConfirmResult
List<ConfirmResult> confirmResults = new ArrayList<>();
for (var tc : confirmEvent.getToolCalls()) {
    confirmResults.add(
            new ConfirmResult(
                    // false 表示拒绝
                    /* confirmed = */ true,
                    // 传回（可选择修改）
                    /* toolCall  = */ tc,                   
                    // 接受规则 → 未来调用自动放行
                    /* rules     = */ tc.getSuggestedRules()
                    ));
}

//恢复智能体 —— 将 confirmResults 通过 metadata 传给下一次 call
UserMessage resumeMsg = UserMessage.builder()
                .metadata(java.util.Map.of(
                        Msg.METADATA_CONFIRM_RESULTS, confirmResults))
                .build();
Msg result = agent.call(List.of(resumeMsg), untimeContext.empty()).block();
```

2、外部工具执行

```java
import io.agentscope.core.event.RequireExternalExecutionEvent;

agent.streamEvents(msg)
        .doOnNext(event -> {
            if (event instanceof RequireExternalExecutionEvent ext) {
                ext.getToolCalls().forEach(tc ->
                        System.out.println("外部执行: " + tc.getName() + "(" + tc.getInput() + ")"));
            }
        })
        .blockLast();
```

**配置状态持久化（AgentStateStore）**

`AgentState` 是 agent 的全部可恢复状态——对话上下文、压缩摘要、权限规则、工具状态和当前 reply 位置。[`AgentStateStore`](https://java.agentscope.io/v2/zh/integration/session/index.html) 是它的存储抽象。

只需在 builder 上配 `stateStore(...)`，agent 就会自动持久化与恢复：每次 `call` 结束把 `AgentState` 写回，下次用同一 `(userId, sessionId)` 调用时自动加载。

```java
import io.agentscope.core.agent.RuntimeContext;
import io.agentscope.core.state.JsonFileAgentStateStore;
import java.nio.file.Paths;

ReActAgent agent = ReActAgent.builder()
        .name("my_agent")
        .sysPrompt("你是一个有帮助的助手。")
        .model(model)
        .toolkit(new Toolkit())
        .stateStore(new JsonFileAgentStateStore(
                Paths.get(System.getProperty("user.home"), ".agentscope/sessions")))
        .build();
```

**结构化输出**

```java
import io.agentscope.core.message.Msg;
import io.agentscope.core.message.UserMessage;

// 定义输出结构
public record WeatherResponse(String location, String temperature, String condition) {}

Msg result = agent.call(List.of(new UserMessage("旧金山天气如何？")), WeatherResponse.class).block();

// 从结果中取出强类型数据
WeatherResponse weather = result.getStructuredData(WeatherResponse.class);
System.out.println(weather.location());      // "San Francisco"
System.out.println(weather.temperature());   // "18°C"
```

**更多能力**

1、技能系统（Skills）

```java
ReActAgent.builder()
        .skillRepository(new MysqlSkillRepository(dataSource))
        .build();
```

## 2.2 消息与事件

消息（Message）与事件（Event）是 AgentScope 中两种基础数据结构。

- 消息 — 智能体间通信与持久化的基本单元。每个 `Msg` 代表一个完整的对话轮次，存储在上下文中并在智能体之间传递。
- 事件 — 前端交互与流式传输的基本单元。事件携带增量进度更新（文本 token、工具调用片段、权限请求等），驱动实时界面和人工介入工作流。

**消息**

1、创建消息

```java
import io.agentscope.core.message.AssistantMessage;
import io.agentscope.core.message.Base64Source;
import io.agentscope.core.message.DataBlock;
import io.agentscope.core.message.SystemMessage;
import io.agentscope.core.message.TextBlock;
import io.agentscope.core.message.UserMessage;

// 用户消息 —— 文本
UserMessage userText = new UserMessage("user", "这张图片里有什么？");

// 多模态用户消息
UserMessage userMulti =
        new UserMessage(
                "user",
                TextBlock.builder().text("描述这张图片：").build(),
                DataBlock.builder()
                        .source(Base64Source.builder()
                                .data("...")
                                .mediaType("image/png")
                                .build())
                        .build());

// 系统消息 —— 仅文本
SystemMessage systemMsg = new SystemMessage("system", "你是一个有用的助手。");

// 助手消息 —— 允许所有块类型
AssistantMessage assistantMsg = new AssistantMessage("agent", "结果如下...");
```

2、访问内容

```java
import io.agentscope.core.message.ToolUseBlock;
import io.agentscope.core.message.ToolResultBlock;

// 获取所有文本内容
String text = msg.getTextContent();

// 获取所有工具调用
List<ToolUseBlock> toolCalls = msg.getContentBlocks(ToolUseBlock.class);

// 检查消息是否包含工具结果
if (msg.hasContentBlocks(ToolResultBlock.class)) {
    // ...
}
```

**事件**

生命周期事件

- AgentStartEvent — 智能体开始新的回复。
- AgentEndEvent — 智能体完成回复。
- ExceedMaxItersEvent — 智能体达到最大推理-执行迭代次数。
- RequestStopEvent — 中间件或工具发起的提前停止请求。

文本流式事件

- TextBlockStartEvent — 新的文本块开始。
- TextBlockDeltaEvent — 增量文本内容到达。
- TextBlockEndEvent — 文本块完成。

思考流式事件

- ThinkingBlockStartEvent / ThinkingBlockDeltaEvent / ThinkingBlockEndEvent —— 与文本流式事件结构对应，仅用于模型的思维链内容；`blockId` 同样表示当前回复中的关联键。

数据流式事件

- DataBlockStartEvent / DataBlockDeltaEvent / DataBlockEndEvent —— 与文本流式事件结构对应，承载图片 / 音频 / 视频等二进制数据。

工具调用流式事件

- ToolCallStartEvent — 智能体开始一次工具调用。
- ToolCallDeltaEvent — 增量工具调用参数到达；`getDelta()` 返回 JSON 参数片段。
- ToolCallEndEvent — 工具调用参数完成。

![image-20260727181630457](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202607271816025.png)

工具结果流式事件

- ToolResultStartEvent — 工具开始执行（带 `toolCallId`、`toolCallName`）。
- ToolResultTextDeltaEvent — 工具的增量文本输出；`getDelta()` 返回文本片段。
- ToolResultDataDeltaEvent — 工具的二进制数据输出；与 `DataBlockDeltaEvent` 类似，包含 `mediaType` / `data` / `url` 字段。
- ToolResultEndEvent — 工具执行完成。

模型调用事件

- ModelCallStartEvent — 模型 API 调用开始（带 `modelName`）。
- ModelCallEndEvent — 模型 API 调用完成（带 `inputTokens` / `outputTokens`）。

人工介入事件

- RequireUserConfirmEvent — 智能体暂停等待用户确认。
- RequireExternalExecutionEvent — 智能体暂停等待外部执行。
- UserConfirmResultEvent — 用户提供确认结果（输入事件）。携带 `List<ConfirmResult>`。
- ExternalExecutionResultEvent — 外部系统提供执行结果（输入事件）。携带 `List<ToolResultBlock>`。
- AllToolsDeniedEvent — 用户通过 HITL 确认拒绝了最近一轮推理产出的全部工具调用。该事件通过 `onActing` middleware 链发出，middleware 可据此发出 `RequestStopEvent` 停止 agent。若无 middleware 处理，agent 默认继续下一轮推理（向后兼容）。

子 Agent 事件

- SubagentExposedEvent — 通过 `agent_spawn(expose_to_user=true)` 生成的子 Agent 被暴露为用户可寻址的入口点。SSE / 流式消费端可据此在 UI 上渲染新的会话入口。

**从事件流重建消息**

构建流式界面的典型模式（Spring WebFlux SSE 形态可参考 `streaming/StreamingWebExample.java`）：

```java
import io.agentscope.core.event.AgentEndEvent;
import io.agentscope.core.event.AgentStartEvent;
import io.agentscope.core.event.TextBlockDeltaEvent;
import io.agentscope.core.event.ToolCallStartEvent;
import io.agentscope.core.event.ToolResultEndEvent;
import io.agentscope.core.message.UserMessage;

agent.streamEvents(new UserMessage("user", "帮我修复这个 bug"))
        .doOnNext(event -> {
            if (event instanceof AgentStartEvent start) {
                System.out.println("[start replyId=" + start.getReplyId() + "]");
            } else if (event instanceof TextBlockDeltaEvent delta) {
                System.out.print(delta.getDelta());
            } else if (event instanceof ToolCallStartEvent tc) {
                System.out.println("\n[正在调用 " + tc.getToolCallName() + "...]");
            } else if (event instanceof ToolResultEndEvent end) {
                System.out.println("[工具执行完成：" + end.getState() + "]");
            } else if (event instanceof AgentEndEvent end) {
                System.out.println("\n[完成]");
            }
        })
        .blockLast();
```

## 2.3 Middleware

**概述**

Agent middleware 是在不修改 agent 或 model 代码的前提下，向 agent 执行流程中的关键位置注入自定义逻辑（日志、追踪、输入改写、访问控制等）的机制。

AgentScope Java 中，可以在 5 个位置上设置 hook：

| 位置             | 类型        | 说明                                                         |
| ---------------- | ----------- | ------------------------------------------------------------ |
| `onAgent`        | Onion       | 包裹一次完整的 reply 流程，覆盖其中所有 ReAct 轮次、工具执行与最终输出 |
| `onReasoning`    | Onion       | 包裹一轮 ReAct 中的推理步骤（输入组装 → 模型调用 → 流式解码） |
| `onActing`       | Onion       | 包裹一次工具调用的执行                                       |
| `onModelCall`    | Onion       | 包裹一次底层 `ChatModel` API 调用，最贴近模型                |
| `onSystemPrompt` | Transformer | 在每次组装 system prompt 时触发；多个 middleware 串行接力，每一个把上一个的输出再做一次变换 |

> 两种类型的差别：
>
> - Onion（洋葱式）—— middleware 包裹下一层 handler，可以在 `next.apply(input)` 前后插入逻辑、观察中间事件流。
> - Transformer（变换式）—— middleware 之间串成流水线，前一个的输出作为后一个的输入，不存在「内层」概念。

下图展示这些 hook 在 agent 生命周期中的嵌套关系。

```
onAgent/
└── ReAct loop（每一轮）/
    ├── onReasoning/
    │   ├── onSystemPrompt（组装 system prompt）
    │   └── onModelCall（模型 API 调用）
    └── onActing（每次工具调用）
```

**装备 Middleware**

```java
import io.agentscope.core.ReActAgent;
import io.agentscope.core.middleware.MiddlewareBase;
import io.agentscope.core.tracing.OtelTracingMiddleware;
import java.util.List;

ReActAgent agent = ReActAgent.builder()
                .name("assistant")
                .sysPrompt("You are a helpful assistant.")
                .model(model)
                .toolkit(toolkit)
                .middlewares(List.of(new OtelTracingMiddleware()))
                .build();
```

**内置 Middleware**

- OtelTracingMiddleware - 为 agent 全生命周期接入 [OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/gen-ai/) 追踪。
- TaskReminderMiddleware - 与内置 `TodoTools` 配合使用，在每个 reasoning step 之前把当前 `AgentState.tasksContext` 渲染成 `<system-reminder>` 注入上下文，避免长任务期间 agent 偏离计划。

**自定义 Middleware**

实现 `MiddlewareBase` 接口（位于 `io.agentscope.core.middleware`），只重写需要的 hook 即可，其它的不用管。

```java
import io.agentscope.core.agent.Agent;
import io.agentscope.core.agent.RuntimeContext;
import io.agentscope.core.event.AgentEvent;
import io.agentscope.core.middleware.ActingInput;
import io.agentscope.core.middleware.AgentInput;
import io.agentscope.core.middleware.MiddlewareBase;
import io.agentscope.core.middleware.ModelCallInput;
import io.agentscope.core.middleware.ReasoningInput;
import java.util.function.Function;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

/** 同时观察 agent / reasoning / model_call / system_prompt 四个位置。 */
public class FullObservabilityMiddleware implements MiddlewareBase {

    @Override
    public Flux<AgentEvent> onAgent(
            Agent agent, RuntimeContext ctx, AgentInput input, Function<AgentInput, Flux<AgentEvent>> next) {
        System.out.println("[agent] start for " + agent.getName());
        return next.apply(input)
                .doOnComplete(() -> System.out.println("[agent] end for " + agent.getName()));
    }

    @Override
    public Flux<AgentEvent> onReasoning(
            Agent agent, RuntimeContext ctx, ReasoningInput input, Function<ReasoningInput, Flux<AgentEvent>> next) {
        System.out.println("[reasoning] start");
        return next.apply(input).doOnComplete(() -> System.out.println("[reasoning] end"));
    }

    @Override
    public Flux<AgentEvent> onModelCall(
            Agent agent, RuntimeContext ctx, ModelCallInput input, Function<ModelCallInput, Flux<AgentEvent>> next) {
        System.out.println("[model_call] " + input.model().getClass().getSimpleName());
        return next.apply(input).doOnComplete(() -> System.out.println("[model_call] done"));
    }

    @Override
    public Mono<String> onSystemPrompt(Agent agent, RuntimeContext ctx, String currentPrompt) {
        System.out.println("[system_prompt] length=" + currentPrompt.length());
        return Mono.just(currentPrompt);
    }
}
```

**实用示例**

1、计时 middleware

下面的 middleware 记录每次模型调用的耗时：

```java
import io.agentscope.core.agent.Agent;
import io.agentscope.core.event.AgentEvent;
import io.agentscope.core.middleware.MiddlewareBase;
import io.agentscope.core.middleware.ModelCallInput;
import java.util.function.Function;
import reactor.core.publisher.Flux;

public class TimingMiddleware implements MiddlewareBase {
    @Override
    public Flux<AgentEvent> onModelCall(
            Agent agent, ModelCallInput input, Function<ModelCallInput, Flux<AgentEvent>> next) {
        long start = System.nanoTime();
        return next.apply(input)
                .doFinally(sig -> {
                    long ms = (System.nanoTime() - start) / 1_000_000;
                    System.out.println(
                            "[timing] " + agent.getName() + ": " + ms + "ms");
                });
    }
}
```

2、限速 middleware

下面的 middleware 在两次模型调用之间强制留出最小间隔：

```java
import io.agentscope.core.agent.Agent;
import io.agentscope.core.event.AgentEvent;
import io.agentscope.core.middleware.MiddlewareBase;
import io.agentscope.core.middleware.ModelCallInput;
import java.time.Duration;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Function;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

public class RateLimitMiddleware implements MiddlewareBase {

    private final long minIntervalMs;
    private final AtomicLong lastCall = new AtomicLong(0);

    public RateLimitMiddleware(Duration minInterval) {
        this.minIntervalMs = minInterval.toMillis();
    }

    @Override
    public Flux<AgentEvent> onModelCall(
            Agent agent, ModelCallInput input, Function<ModelCallInput, Flux<AgentEvent>> next) {
        long now = System.currentTimeMillis();
        long wait = minIntervalMs - (now - lastCall.get());
        Mono<Void> delay = wait > 0 ? Mono.delay(Duration.ofMillis(wait)).then() : Mono.empty();
        return delay.thenMany(next.apply(input))
                .doOnSubscribe(s -> lastCall.set(System.currentTimeMillis()));
    }
}
```

3、动态 system prompt middleware

下面的 middleware 在 system prompt 中注入实时上下文。也可以直接复用示例 `middleware/SystemPromptMiddlewareExample.java`：

```java
import io.agentscope.core.agent.Agent;
import io.agentscope.core.middleware.MiddlewareBase;
import java.time.Instant;
import java.util.function.Supplier;
import reactor.core.publisher.Mono;

public class DynamicContextMiddleware implements MiddlewareBase {

    private final Supplier<String> contextFn;

    public DynamicContextMiddleware(Supplier<String> contextFn) {
        this.contextFn = contextFn;
    }

    @Override
    public Mono<String> onSystemPrompt(Agent agent, String currentPrompt) {
        return Mono.just(currentPrompt + "\n\n## Current Context\n" + contextFn.get());
    }
}

// 装配：
// .middlewares(List.of(new DynamicContextMiddleware(() -> "Time: " + Instant.now())))
```

4、模型回退 middleware

下面的 middleware 在主模型失败时切换到备用模型：

```java
import io.agentscope.core.agent.Agent;
import io.agentscope.core.event.AgentEvent;
import io.agentscope.core.middleware.MiddlewareBase;
import io.agentscope.core.middleware.ModelCallInput;
import io.agentscope.core.model.Model;
import java.util.function.Function;
import reactor.core.publisher.Flux;

public class ModelFallbackMiddleware implements MiddlewareBase {

    private final Model fallback;

    public ModelFallbackMiddleware(Model fallback) {
        this.fallback = fallback;
    }

    @Override
    public Flux<AgentEvent> onModelCall(
            Agent agent, ModelCallInput input, Function<ModelCallInput, Flux<AgentEvent>> next) {
        return next.apply(input)
                .onErrorResume(err -> {
                    System.err.println("Primary model failed: " + err.getMessage()
                            + ", switching to fallback");
                    return next.apply(
                            new ModelCallInput(
                                    input.messages(),
                                    input.tools(),
                                    input.options(),
                                    fallback));
                });
    }
}
```

## 2.4 模型

**概述**

运行时模型层采用两层结构：上层是 Credential，承载某个提供商的 API 鉴权字段；下层是 Chat Model，即在该凭证基础上对接的具体推理模型实现。

```
CredentialBase/
└── ChatModelBase/
    ├── OpenAIChatModel
    ├── AnthropicChatModel
    ├── DashScopeChatModel
    ├── GeminiChatModel
    └── OllamaChatModel
```

Credential 承载某个提供商的 API 认证字段（`apiKey`、`baseUrl` 等）。

**模型扩展模块**

特定模型提供商的实现已经从 `agentscope-core` 迁移到独立扩展模块中。每个模型适配模块自己维护 chat model、credential、formatter、DTO、异常、SDK/API client 等。

| 提供商    | Maven artifact                          | 主要包名                                   |
| --------- | --------------------------------------- | ------------------------------------------ |
| OpenAI    | `agentscope-extensions-model-openai`    | `io.agentscope.extensions.model.openai`    |
| DashScope | `agentscope-extensions-model-dashscope` | `io.agentscope.extensions.model.dashscope` |
| Gemini    | `agentscope-extensions-model-gemini`    | `io.agentscope.extensions.model.gemini`    |
| Anthropic | `agentscope-extensions-model-anthropic` | `io.agentscope.extensions.model.anthropic` |
| Ollama    | `agentscope-extensions-model-ollama`    | `io.agentscope.extensions.model.ollama`    |

**选择模型创建方式**

1、字符串 model id

```java
ReActAgent agent =
        ReActAgent.builder()
                .name("assistant")
                .model("dashscope:qwen-plus") // 底层由 ModelRegistry.resolve(modelId) 解析
                .build();
```

2、显式 Model builder

```java
import io.agentscope.extensions.model.dashscope.DashScopeChatModel;
import io.agentscope.extensions.model.dashscope.formatter.DashScopeChatFormatter;

DashScopeChatModel model =
        DashScopeChatModel.builder()
                .apiKey(System.getenv("DASHSCOPE_API_KEY"))
                .modelName("qwen-plus")
                .stream(true)
                .formatter(new DashScopeChatFormatter())
                .build();

ReActAgent agent =
        ReActAgent.builder()
                .name("assistant")
                .model(model)
                .build();
```

3、Spring Boot 应用

Spring Boot 场景下，优先使用特定模型提供商的 starter，例如 `agentscope-openai-spring-boot-starter`、`agentscope-dashscope-spring-boot-starter`、`agentscope-gemini-spring-boot-starter`、`agentscope-anthropic-spring-boot-starter`、`agentscope-ollama-spring-boot-starter`。

```yaml
agentscope:
  model:
    provider: openai
  openai:
    api-key: ${OPENAI_API_KEY}
    model-name: gpt-4.1-mini
    stream: true
```

各模型提供商的 Spring Boot starter 还提供了有序的 builder customizer bean。它适合用于需要设置 builder 专属能力的场景，例如自定义 formatter、默认生成参数、代理/client 配置，或其他提供商专属开关。

```java
import io.agentscope.core.model.GenerateOptions;
import io.agentscope.spring.boot.openai.OpenAIChatModelBuilderCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.annotation.Order;

@Configuration(proxyBeanMethods = false)
class ModelCustomizerConfiguration {

    @Bean
    @Order(0)
    OpenAIChatModelBuilderCustomizer openAIModelDefaults() {
        return builder ->
                builder.defaultOptions(
                        GenerateOptions.builder()
                                .temperature(0.2)
                                .parallelToolCalls(false)
                                .build());
    }
}
```

## 2.5 权限系统

Permission system（`io.agentscope.core.permission`）拦截 agent 的每一次工具调用，给出三种决策之一：允许（ALLOW） 执行、拒绝（DENY） 执行，或者询问用户（ASK） 确认。

**Permission Mode**

可以在创建 agent 时通过 `permissionContext(...)` 设置 mode：

```java
import io.agentscope.core.ReActAgent;
import io.agentscope.core.permission.PermissionContextState;
import io.agentscope.core.permission.PermissionMode;

PermissionContextState permCtx =
        PermissionContextState.builder()
                .mode(PermissionMode.DEFAULT)
                .build();

ReActAgent agent =
        ReActAgent.builder()
                .name("my_agent")
                .sysPrompt("...")
                .model(model)
                .permissionContext(permCtx)
                .build();
```

**Permission Rule**

`PermissionRule`（record）把某个 tool 与具体的调用模式映射到三种行为之一：`ALLOW`、`DENY`、`ASK`。

```java
import io.agentscope.core.permission.PermissionBehavior;
import io.agentscope.core.permission.PermissionContextState;
import io.agentscope.core.permission.PermissionMode;
import io.agentscope.core.permission.PermissionRule;

PermissionContextState permCtx =
        PermissionContextState.builder()
                .mode(PermissionMode.DEFAULT)
                .addAllowRule(
                        "safe_read",
                        new PermissionRule(
                                "safe_read", null, PermissionBehavior.ALLOW, "userSettings"))
                .addAskRule(
                        "dangerous_delete",
                        new PermissionRule(
                                "dangerous_delete",
                                null,
                                PermissionBehavior.ASK,
                                "userSettings"))
                .addDenyRule(
                        "drop_table",
                        new PermissionRule(
                                "drop_table", null, PermissionBehavior.DENY, "userSettings"))
                .build();
```

**常见配方**

1、只读探索

```java
// EXPLORE 模式：agent 可以自由调用只读工具，所有写工具会被自动拒绝。
PermissionContextState explore =
        PermissionContextState.builder()
                .mode(PermissionMode.EXPLORE)
                .build();

ReActAgent explorer =
        ReActAgent.builder()
                .name("explorer")
                .sysPrompt("...")
                .model(model)
                .permissionContext(explore)
                .build();
```

2、无人值守自动化

```java
import io.agentscope.core.permission.PermissionBehavior;
import io.agentscope.core.permission.PermissionRule;

PermissionContextState ci =
        PermissionContextState.builder()
                .mode(PermissionMode.DONT_ASK)
                .addAllowRule(
                        "deploy",
                        new PermissionRule(
                                "deploy", "staging", PermissionBehavior.ALLOW, "project"))
                .addAllowRule(
                        "git_commit",
                        new PermissionRule(
                                "git_commit", null, PermissionBehavior.ALLOW, "project"))
                .build();

ReActAgent ciAgent =
        ReActAgent.builder()
                .name("ci_agent")
                .sysPrompt("...")
                .model(model)
                .permissionContext(ci)
                .build();
// 只有显式放行的命令会执行；其余调用被静默拒绝
```

3、阻止危险命令

```java
PermissionContextState bypassWithDeny =
        PermissionContextState.builder()
                .mode(PermissionMode.BYPASS)
                .addDenyRule(
                        "drop_table",
                        new PermissionRule(
                                "drop_table", null, PermissionBehavior.DENY, "userSettings"))
                .addDenyRule(
                        "force_push",
                        new PermissionRule(
                                "force_push", null, PermissionBehavior.DENY, "userSettings"))
                .build();
// 除显式拒绝的工具外，其余均放行（deny 规则不可绕过）
```

## 2.6 工具

AgentScope 把 tool 相关的构件组织成三个概念：

- Tool —— 任意实现 `AgentTool` 接口（通常通过继承 `ToolBase`）或在普通类的方法上标注 `@Tool` 注解的对象。Java 端把后者称为 *reflective function tool*，由 `Toolkit#registerTool(Object)` 自动反射注册。
- Toolkit —— 容器，负责注册 tool、MCP 客户端与 skill，向模型暴露它们的 JSON schema，并把每次工具调用分发到对应的 tool 对象。
- Tool Group —— 一组带名称的 tool / MCP / skill 集合，可以作为整体激活或停用。Agent 在运行时通过内置 meta tool 切换 group，让上下文保持聚焦。

**Java Tool**

Java tool 是任意满足 `AgentTool` 契约的对象。AgentScope 同时提供了一个 `ToolBase` 抽象基类用于显式建模带参数 schema 的 tool，以及一个反射适配器用于把普通方法包装成 tool。

需要自定义权限策略、外部执行或更复杂的 schema 时，继承 `ToolBase`：

```java
import io.agentscope.core.message.TextBlock;
import io.agentscope.core.message.ToolResultBlock;
import io.agentscope.core.permission.PermissionBehavior;
import io.agentscope.core.permission.PermissionDecision;
import io.agentscope.core.tool.ToolBase;
import io.agentscope.core.tool.ToolCallParam;
import io.agentscope.core.tool.ToolExecutionContext;
import java.util.List;
import java.util.Map;
import reactor.core.publisher.Mono;

public class WebSearchTool extends ToolBase {

    public WebSearchTool() {
        super(
                ToolBase.builder()
                        .name("WebSearch")
                        .description("Search the web for information on a given query.")
                        .inputSchema(Map.of(
                                "type", "object",
                                "properties", Map.of(
                                        "query", Map.of(
                                                "type", "string",
                                                "description", "The search query.")),
                                "required", List.of("query")))
                        .readOnly(true)
                        .concurrencySafe(true));
    }

    @Override
    public Mono<PermissionDecision> checkPermissions(
            Map<String, Object> toolInput, ToolExecutionContext context) {
        return Mono.just(PermissionDecision.allow("Web search is read-only."));
    }

    @Override
    public Mono<ToolResultBlock> callAsync(ToolCallParam param) {
        String query = (String) param.getInput().get("query");
        return doSearchAsync(query)
                .map(text ->
                        ToolResultBlock.builder()
                                .id(param.getId())
                                .name(getName())
                                .output(List.of(TextBlock.builder().text(text).build()))
                                .build());
    }
}
```

**MCP**

MCP tool 在 toolkit 中以 `mcp__{server_name}__{tool_name}` 命名，避免冲突；标注了 `readOnlyHint` 的 tool 会被权限系统自动放行。

注册 MCP Tool

```java
// STDIO
import io.agentscope.core.tool.Toolkit;
import io.agentscope.core.tool.mcp.McpClientBuilder;
import io.agentscope.core.tool.mcp.McpClientWrapper;

McpClientWrapper filesystem =
        McpClientBuilder.stdio()
                .name("filesystem")
                .command("mcp-server-filesystem")
                .args("--root", "/my/project")
                .build();

Toolkit toolkit = new Toolkit();
toolkit.registerMcpClient(filesystem).block();

// SSE
import io.agentscope.core.tool.mcp.McpClientBuilder;
import io.agentscope.core.tool.mcp.McpClientWrapper;

McpClientWrapper search =
        McpClientBuilder.sse()
                .name("search")
                .url("https://api.search.com/mcp/sse")
                .build();

Toolkit toolkit = new Toolkit();
toolkit.registerMcpClient(search).block();
```

**Skill**

1、注册 Skill

```java
import io.agentscope.core.ReActAgent;
import io.agentscope.core.skill.repository.FileSystemSkillRepository;
import java.nio.file.Paths;

ReActAgent agent =
        ReActAgent.builder()
                .name("SkillCreator")
                .sysPrompt("...")
                .model(model)
                .skillRepository(new FileSystemSkillRepository(Paths.get("/path/to/skills"), false))
                .build();
```

2、Skill 的工作方式

`Toolkit` 在含 skill 时，注册与查看分两阶段进行。

初始化阶段：

- Toolkit 扫描所有注册的 skill 来源，收集每个 skill 的名称、描述与目录。
- 自动把内置查看器工具 `load_skill_through_path`（实现位于 `io.agentscope.core.skill.SkillToolFactory`）注册到 `skill-build-in-tools` 这个 tool group。
- 组装一段 system prompt 片段，列出可用 skill（仅名称与描述），并指示 agent 通过 `load_skill_through_path` 读取完整内容。

运行时阶段，agent 用两个必填参数调用查看器：

| 参数      | 类型                                | 说明                                                         |
| --------- | ----------------------------------- | ------------------------------------------------------------ |
| `skillId` | `string`（枚举：已注册的 skill ID） | 要加载的 skill。                                             |
| `path`    | `string`                            | 传 `"SKILL.md"` 取该 skill 的 markdown 指令；或传 skill 声明过的精确资源路径，例如 `"references/guide.md"`、`"scripts/run.py"`。不要传 `"."`、`"./"`、目录或绝对路径。 |

调用示例：

```json
{
  "name": "load_skill_through_path",
  "input": { "skillId": "pdf-extractor", "path": "SKILL.md" }
}
```

## 2.7 上下文与 AgentState

**无状态 Agent 引擎**

agent 实例本身只持有不可变的配置，所有 per-session 的可变数据都放在 `AgentState` 里，以 `(userId, sessionId)` 为索引。一个 agent 实例可以同时服务多个用户和会话，调用方只需在每次 `call()` 时传入不同的 `RuntimeContext`。

**AgentState**

自动持久化与恢复链路：

```
call(msgs, RuntimeContext(userId, sessionId))
  │
  ├─ per-session 门: 相同 (uid, sid) 串行, 不同会话并行
  │
  ▼
  从缓存或 stateStore 加载 AgentState
  │   注入到 RuntimeContext: rc.setAgentState(state)
  │
  ▼
  推理循环
  │   中间件就地改写 state.contextMutable()
  │   (压缩、Plan、todo_write、权限调整……都在改它)
  │
  ▼
  保存 AgentState
  │   stateStore.save(userId, sessionId, "agent_state", state)
  │
  ▼
  返回结果
```

内置与扩展实现：

```java
// 默认(单机):省略 .stateStore(...) 即可,自动用本地 JsonFileAgentStateStore
HarnessAgent agent = HarnessAgent.builder()
    .name("MyAgent")
    .model(model)
    .workspace(workspace)
    .build();

// 多副本生产:使用 DistributedStore
JedisPooled jedis = new JedisPooled("redis://redis.prod:6379");
HarnessAgent agent = HarnessAgent.builder()
        .name("MyAgent")
        .model(model)
        .workspace(workspace)
        .stateStore(new RedisAgentStateStore(jedis))
        .distributedStore(RedisDistributedStore.fromJedis(jedis))
        .build();
```

同 (userId, sessionId) 跨进程、跨机器实时恢复：

```java
// 节点 A:开了一段对话
HarnessAgent agentA = HarnessAgent.builder()
    .stateStore(redisStore)
    /* ... */ .build();
agentA.call(msg, RuntimeContext.builder()
    .sessionId("alice-2026-06-02-001")
    .userId("alice")
    .build()).block();

// 节点 B:不同物理机,完全独立的 JVM
HarnessAgent agentB = HarnessAgent.builder()
    .stateStore(redisStore)
    /* 同一份存储后端 */ .build();

// 节点 B 第一次用相同 (userId, sessionId) 的 call() 会自动从 Redis 拉到节点 A 之前留下的 AgentState
agentB.call(nextMsg, RuntimeContext.builder()
    .sessionId("alice-2026-06-02-001")
    .userId("alice")
    .build()).block();
```

# 03 | Harness

## 3.1 Harness 架构

**核心工作原理**

理解 Harness 只需要记住三件事：

1. 能力是叠加在推理循环关键时机上的，不是改写循环。 
2. 能力之间互不依赖，只通过共享对象通信。它们之间靠三个共享对象交流：`RuntimeContext`、工作区、`AgentStateStore`。
3. 内置 middleware 注册顺序固定，你自己加的跑在最前面。 

**状态怎么流转**

状态分三层，框架自动在层之间搬数据。

- 调用内状态 —— `AgentState`（对话上下文、权限规则、Plan Mode 状态、工具状态）、`RuntimeContext`（`sessionId`、`userId`、沙箱句柄、extra）。
- 跨调用状态 —— 每次 `call()` 结束自动写盘，下次自动加载：`AgentStateStore`（默认 `~/.agentscope/state/<agentId>/`）里的 `AgentState` 运行时快照、`sessions/<sessionId>.log.jsonl` 里的对话日志、子任务记录、沙箱元数据。
- 长期记忆 —— 跨 session 累积 `memory/YYYY-MM-DD.md` ，后台节流任务会周期把它合并到 `MEMORY.md`。

## 3.2 上下文压缩

**HarnessAgent 内置的几种策略**

| 策略               | 解决的问题                              | 触发时机             | 中间件                                |
| ------------------ | --------------------------------------- | -------------------- | ------------------------------------- |
| **对话摘要压缩**   | 上下文太”深”——消息条数 / token 累计太多 | 每次模型推理前       | `CompactionMiddleware`                |
| **大工具结果卸载** | 上下文太”宽”——单条工具结果体量过大      | 工具执行后           | `ToolResultEvictionMiddleware`        |
| **上下文溢出兜底** | 撞到模型 `context_length_exceeded`      | `call()` 抛错时      | `HarnessAgent.recoverFromOverflow`    |
| **预压缩参数截断** | 工具调用参数体量大但后期没人看          | 摘要之前的轻量预处理 | `CompactionConfig.TruncateArgsConfig` |

## 3.3 工作区（Workspace）

**工作区目录布局**

```
.agentscope/workspace/
├── AGENTS.md                    ← 静态：人格 + 行为约定
├── MEMORY.md                    ← 长期记忆：策划后的长期事实
├── tools.json                   ← 静态：MCP server + 工具白名单（可选）
├── memory/                      ← 长期记忆：每天追加的事实流水账
│   └── YYYY-MM-DD.md
├── knowledge/                   ← 静态：领域知识入口 + 任意参考文件
│   ├── KNOWLEDGE.md
│   └── ...
├── skills/                      ← 静态：技能目录，每个子目录一份 SKILL.md
│   └── <skill-name>/SKILL.md
├── subagents/                   ← 静态：子 agent 声明（文件名即 agent_id）
│   └── <agent-id>.md
├── plans/                       ← 运行时：Plan Mode 写下的计划文件
│   └── PLAN.md
└── agents/<agentId>/            ← 运行时：每个 agent 自己的运行时根
    ├── sessions/                ← 运行时：会话索引 + 永不压缩对话日志
    │   ├── sessions.json
    │   └── <sessionId>.log.jsonl
    └── tasks/                   ← 运行时：子 agent 后台任务记录
        └── <sessionId>.json
```

workspace 的解析顺序：

| 优先级 | 来源                                    | 说明                                          |
| ------ | --------------------------------------- | --------------------------------------------- |
| 1      | `workspace(Path)` / `workspace(String)` | Builder 显式设置，覆盖一切                    |
| 2      | `agentscope.workspace` 系统属性         | `-Dagentscope.workspace=/data/workspace`      |
| 3      | `AGENTSCOPE_WORKSPACE` 环境变量         | `export AGENTSCOPE_WORKSPACE=/data/workspace` |
| 4      | 默认值                                  | `${user.dir}/.agentscope/workspace`           |

**运行时数据与 Memory 怎么存**

| 数据面                      | 是什么                                                       | 落在哪                                                       |
| --------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **`AgentState`**            | 易失的运行期上下文：对话缓冲、压缩摘要、权限 / 工具 / 任务 / Plan-Mode 上下文，以及指向工作区产物的元数据 | **`AgentStateStore`** —— 独立子系统，**不在**工作区（默认 `~/.agentscope/state/<agentId>/`） |
| **工作区运行时 / 长期文件** | 持久产物：会话日志、任务记录、`MEMORY.md` + `memory/`        | 在工作区树内，物理位置随 filesystem 模式而定                 |

## 3.4 记忆

让 agent “记住跨会话的事实”，同时避免对话上下文无限增长。Harness 把记忆拆成两层：

- 第一层：日流水账 `memory/YYYY-MM-DD.md` —— 每天追加，原始且未去重；
- 第二层：策划后长期记忆 `MEMORY.md` —— 周期性 LLM 合并去重的产物；每轮推理时作为长期记忆注入 system prompt。

两层记忆是怎么工作的？

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608032012265.png)

## 3.5 文件系统

`HarnessAgent` 把 agent 对工作区的访问从”一定是本机磁盘”抽象成统一接口。所有文件工具（`read_file` / `write_file` / `edit_file` / `grep_files` / `glob_files` / `list_files`）和可选的 `execute`（shell）都从这个抽象走。

这样做让你能在三种部署模式之间切换，而不改 agent 代码：

- 本机 + shell —— 单进程、本地、信任环境；
- 共享存储 —— 多副本 / 多 pod 共享同一份长期记忆；
- 沙箱 —— 文件与命令都在隔离容器里执行，跨调用恢复同一份工作区。

| 模式                         | 配置                                                         | 提供 shell？      | 适用场景                                                     |
| ---------------------------- | ------------------------------------------------------------ | ----------------- | ------------------------------------------------------------ |
| **1 · 共享存储**             | `filesystem(new RemoteFilesystemSpec(store))`                | ❌                 | 多副本要共享 `MEMORY.md` / 对话日志 / 子任务到 KV；**不希望在宿主上跑 shell** |
| **2 · 沙箱**                 | `filesystem(new DockerFilesystemSpec()...)` 或 K8s / Daytona / E2B / AgentRun | ✅（在沙箱内）     | 隔离执行、跨调用恢复同一份工作区、可选快照 + 分布式          |
| **3 · 本机 + shell**（默认） | `filesystem(new LocalFilesystemSpec()...)` 或**不写**        | ✅（宿主 `sh -c`） | 单进程 / 本机 / 信任环境 / 简单脚本与测试                    |

**模式 1：共享存储（`RemoteFilesystemSpec`）**

示例场景：多副本客服 agent

三个 pod 各跑一个 `HarnessAgent`，用同一个 Redis 做 `BaseStore`：

```java
DistributedStore store = RedisDistributedStore.fromJedis(
        new JedisPooled("redis://shared-redis:6379"));

HarnessAgent agent = HarnessAgent.builder()
    .name("customer-service")
    .model(model)
    .workspace(Paths.get("/opt/agent/workspace"))
    .distributedStore(store)                  // stateStore + baseStore 一键配置
    .filesystem(new RemoteFilesystemSpec()
        .isolationScope(IsolationScope.USER)      // 每个用户独立命名空间
        .anonymousUserId("anonymous"))            // 未登录用户的兜底
    .build();
```

- 三个 pod 上本地磁盘的 `AGENTS.md` / `knowledge/` / `skills/` 作为只读模板（git 同步）；
- 运行时产物（`MEMORY.md`、`memory/`、对话日志）自动存到 Redis，任意 pod 都能读到最新状态；
- 用户 alice 的记忆在 KV 键 `agents/customer-service/users/alice/memory/...` 下。

**模式 2：沙箱（`SandboxFilesystemSpec` 系列）**

适合”代码会执行不可信操作、或要隔离生产环境”。所有文件操作和 shell 命令都发到沙箱里执行，宿主完全不受影响。

示例场景：编程助手（Docker + 本地快照）

```java
HarnessAgent codingAgent = HarnessAgent.builder()
    .name("coder")
    .model(model)
    .workspace(Paths.get(".agentscope/workspace"))
    .filesystem(new DockerFilesystemSpec()
        .image("node:20-slim")
        .isolationScope(IsolationScope.USER)
        .memorySizeBytes(1024 * 1024 * 1024L)
        .snapshotSpec(new LocalSnapshotSpec("/data/sandbox-snapshots")))
    .distributedStore(store)
    .build();

// alice 第一次调用：沙箱里 npm install，装好后快照保存
RuntimeContext rc = RuntimeContext.builder()
    .userId("alice")
    .sessionId("dev-session-1")
    .build();
agent.call(Msg.user("npm install && npm test"), rc).block();

// alice 第二次调用：恢复快照，node_modules 还在，无需重新安装
agent.call(Msg.user("npm run build"), rc).block();
```

**模式 3：本机 + shell（默认）**

什么都不写就是这个：工作区落到 `${cwd}/.agentscope/workspace/`

示例场景：本地开发助手

```java
HarnessAgent devHelper = HarnessAgent.builder()
    .name("dev-helper")
    .model(model)
    .workspace(Paths.get(".agentscope/workspace"))
    .filesystem(new LocalFilesystemSpec()
        .project(Paths.get("/Users/alice/my-project"))
        .addRoot(Paths.get("/Users/alice/.config"))
        .mode(LocalFsMode.ROOTED)
        .inheritEnv(true)
        .executeTimeoutSeconds(300))
    .build();
```

## 3.6 子 Agent

让主 agent 把”可独立处理、上下文重、可并行”的任务委派出去，避免主线程膨胀。每个子 agent 都是一个临时实例（本地的 `HarnessAgent` 或远程 stub），跑自己的会话，结果通过工具返回给父 agent。

最简单的用法：把子 agent 的 spec 写到工作区里就行。文件名就是 `agent_id`：

```yaml
workspace/subagents/reviewer.md

---
description: 代码审查专家。当用户需要 review PR、找代码问题、检查代码规范时使用。
---

你是一个专注代码评审的子 agent。请按以下流程工作：
1. 先 read_file / grep_files 收集上下文
2. 给出按文件 / 行号的具体建议
3. 末尾给一个 1-5 的总体评分
```

然后主 agent 就能在推理时调用：

```
agent_spawn agent_id="reviewer" task="review 这次 PR 的所有改动"
```

不需要做任何注册。

## 3.7 技能

一个 skill 就是一份写好的能力包：一个目录里放一份 `SKILL.md`（说明用途、给 agent 看的指令），可以再带一些参考文档、脚本或样例。写好后丢给 agent，它会在合适的时候自己用。

Harness 让你从两个地方装 skill：

- 技能市场 —— Git 仓库、Nacos、MySQL、classpath、自定义后端
- 工作区 —— `workspace/skills/` 下大家共用；`<userId>/skills/` 下按用户隔离

把团队的 skill 仓库接进来，agent 立刻就能用：

```java
HarnessAgent agent = HarnessAgent.builder()
        .name("assistant")
        .model(model)
        .workspace(workspace)
        .skillRepository(new GitSkillRepository("https://github.com/your-org/team-skills.git"))
        .build();
```

**Agent 是怎么读取和执行 skill 的**

1、每轮推理时，agent 会在 system prompt 里看到一个 `<available_skills>` 块，列出当前可见的所有 skill：

```xml
<available_skills>
<skill>
  <name>code-reviewer</name>
  <description>当用户需要代码评审、风格反馈或 PR 审核时使用。</description>
  <skill-id>code-reviewer_workspace-namespaced</skill-id>
  <files-root>/workspace/skills/code-reviewer</files-root>
</skill>
...
</available_skills>
```

2、读 SKILL.md 和资源文件

加载某个 skill 时 agent 会调用内置工具 `load_skill_through_path`：

- `load_skill_through_path(skillId, path="SKILL.md")` 返回 markdown 正文
- `load_skill_through_path(skillId, path="references/style-guide.md")` 返回该 skill 目录下的任意文件

3、shell 执行

当一个 skill 自带脚本（例如 `scripts/run-checks.sh`），agent 需要绝对路径才能通过 `execute_shell_command` 调用它。这个绝对路径就是 skill 条目里的 `<files-root>`。

## 3.8 计划模式

Plan Mode 让 agent 在动手前先”把意图想清楚 + 写下来”再执行。开启后 agent 进入一个只读阶段：

- 只能调用只读工具和 4 个白名单工具：`plan_enter` / `plan_write` / `plan_exit` / `todo_write`；
- 其它工具调用一律被拒绝（agent 看到一条”plan 阶段拒绝”提示）；
- 退出 Plan Mode 走 HITL 确认（复用权限系统的 ASK），避免模型一意孤行直接进入执行。

这条流程明确把”设计 → 写计划 → 人确认 → 执行”四步固化下来，配合 `todo_write` 与子 agent，能在长任务里有效降低”边想边改、改坏一片”的概率。

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608041944309.png)

## 3.9 Channel

**快速开始**

```java
HarnessAgent agent = HarnessAgent.builder()
    .name("assistant")
    .sysPrompt("你是一个有用的助手。")
    .model("dashscope:qwen-plus")
    .build();

// 绑定一个 ChatUI channel。
ChatUiChannel chat = agent.channel(ChatUiChannel.create());

// 发送消息。每个 userId 自动获得独立的 session。
Msg reply = chat.send(SendOptions.userId("user-1"), "你好！").block();

// 同一个用户，同一个 session——对话继续。
Msg followUp = chat.send(SendOptions.userId("user-1"), "再多说一些。").block();

// 不同用户，不同 session。
Msg otherUser = chat.send(SendOptions.userId("user-2"), "你好").block();
```

**Spring Boot SSE Controller**

```java
@GetMapping(value = "/chat", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<ServerSentEvent<String>> chat(@RequestParam String message,
                                          @RequestParam String userId,
                                          @RequestParam(required = false) String sessionId) {
    SendOptions options = sessionId != null
            ? SendOptions.of(userId, sessionId)
            : SendOptions.userId(userId);

    return chat.sendStream(options, message)
            .map(event -> {
                Map<String, Object> payload = new LinkedHashMap<>();
                payload.put("type", event.getType().name());
                payload.put("id", event.getId());
                if (event instanceof TextBlockDeltaEvent delta) {
                    payload.put("delta", delta.getDelta());
                } else if (event instanceof SubagentExposedEvent se) {
                    payload.put("subagentId", se.getSubagentId());
                    payload.put("agentId", se.getAgentId());
                    payload.put("label", se.getLabel());
                }
                return ServerSentEvent.<String>builder()
                        .data(objectMapper.writeValueAsString(payload))
                        .build();
            });
}
```

**多 HarnessAgent 路由**

如果有多个 `HarnessAgent` 实例，使用 `GatewayBootstrap`：

```java
HarnessAgent salesAgent = HarnessAgent.builder()
    .name("sales").sysPrompt("你是一个销售助手。")
    .model("dashscope:qwen-plus").build();

HarnessAgent supportAgent = HarnessAgent.builder()
    .name("support").sysPrompt("你是一个客服 agent。")
    .model("dashscope:qwen-plus").build();

GatewayBootstrap gw = GatewayBootstrap.builder()
    .agent("sales", salesAgent)
    .agent("support", supportAgent)
    .mainAgent("sales")          // 没有指定 agent 时的默认
    .build();

ChatUiChannel chat = gw.chatUiChannel();
```

使用 `SendOptions.withAgentId()` 把消息路由到指定 agent：

```java
// 路由到 sales（默认 main agent）
chat.send(SendOptions.userId("user-1"), "有什么产品？").block();

// 显式路由到 support
chat.send(SendOptions.userId("user-1").withAgentId("support"), "账单问题").block();
```

**自定义 Channel**

实现 `Channel` 接口来适配新的消息平台：

```java
public class MySlackChannel implements Channel {
    @Override public String channelId() { return "slack"; }
    @Override public ChannelConfig config() { return myConfig; }
    @Override public void init(Gateway gateway) { this.gateway = gateway; }
    @Override public void start() { /* 连接 Slack */ }
    @Override public void stop() { /* 断开连接 */ }

    @Override
    public Mono<Msg> dispatch(InboundMessage message) {
        RouteResult route = router.resolveRoute(config(), message);
        return gateway.run(route.context(), message.messages(), route.outboundAddress());
    }

    // 可选：流式分发
    @Override
    public Flux<AgentEvent> dispatchStream(InboundMessage message) {
        RouteResult route = router.resolveRoute(config(), message);
        return gateway.runStream(route.context(), message.messages(), route.outboundAddress());
    }
}
```

通过 `GatewayBootstrap` 注册：

```java
GatewayBootstrap gw = GatewayBootstrap.builder()
    .agent("main", agent)
    .channel(new MySlackChannel())
    .build();

gw.start();   // 调用所有 channel 的 init() + start()
// ...
gw.stop();    // 调用所有 channel 的 stop()
```

















