> 官方文档：https://docs.spring.io/spring-ai/reference/index.html
>
> 中文文档：https://springdoc.cn/spring-ai/

# 一、概述

Spring AI 解决了 AI 集成的根本难题：`将企业数据和 API 与 AI 模型连接起来`。

![image-20251208224647025](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202512082246117.png)

Spring AI 提供了以下功能：

- 跨多家 AI 提供商的 Chat、文本转图像和嵌入模型的可移植 API 支持。支持同步和流式A PI 选项。还可访问特定于模型的功能。

- 支持所有主要的 AI 模型提供商，如 Anthropic、OpenAI、微软、亚马逊、谷歌和 Ollama。支持的模型类型包括：[对话补全](https://springdoc.cn/spring-ai/api/chatmodel.html)、[嵌入](https://springdoc.cn/spring-ai/api/embeddings.html)、[文生图](https://springdoc.cn/spring-ai/api/imageclient.html)、[音频转录](https://springdoc.cn/spring-ai/api/audio/transcriptions.html)、[文本转语音](https://springdoc.cn/spring-ai/api/audio/speech.html)、[内容审核](https://springdoc.cn/spring-ai/#api/moderation)。

- [结构化输出](https://springdoc.cn/spring-ai/api/structured-output-converter.html) - 将 AI 模型输出映射到 POJO。
- 支持所有主要的 [向量数据库提供商](https://springdoc.cn/spring-ai/api/vectordbs.html)，如 Apache Cassandra、Azure Cosmos DB、Azure Vector Search、Chroma、Elasticsearch、GemFire、MariaDB、Milvus、MongoDB Atlas、Neo4j、OpenSearch、Oracle、PostgreSQL/PGVector、PineCone、Qdrant、Redis、SAP Hana、Typesense 和 Weaviate。
- 跨向量数据库提供商的可移植 API，包括一种新颖的类似 SQL 的元数据过滤器 API。
- [工具/函数调用](https://springdoc.cn/spring-ai/api/tools.html) - 允许模型请求执行客户端工具和函数，从而根据需要访问必要的实时信息并执行操作。
- [可观测性](https://springdoc.cn/spring-ai/observability/index.html) - 深入了解 AI 相关操作。
- 用于数据工程的文档摄取 [ETL 框架](https://springdoc.cn/spring-ai/api/etl-pipeline.html)。
- [AI 模型评估](https://springdoc.cn/spring-ai/api/testing.html) - 帮助评估生成内容和防止幻觉反应的实用工具。
- 针对 AI 模型和向量存储的 Spring Boot 自动配置和 Starter。
- [ChatClient API](https://springdoc.cn/spring-ai/api/chatclient.html) - 用于与 AI 聊天模型通信的 Fluent API，与 `WebClient` 和 `RestClient` API 相似。
- [Advisor API](https://springdoc.cn/spring-ai/api/advisors.html) - 封装了重复的生成式 AI 模式，转换发送到和从语言模型（LLMs）返回的数据，并在各种模型和用例之间提供可移植性。
- 支持 [聊天对话记忆](https://springdoc.cn/spring-ai/api/chatclient.html#_chat_memory) 和 [检索增强生成（RAG）](https://springdoc.cn/spring-ai/api/chatclient.html#_retrieval_augmented_generation)。

## 1.1 AI 概念

**Model（模型）**

人工智能模型（AI Model）是一种用于处理和生成信息的算法，可以做出预测、文本、图像或其他输出，从而增强各行业的各种应用。下表根据输入和输出类型对几种模型进行了分类：

![模型类别](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202512082257216.jpg)

Spring AI 目前支持处理语言、图像和音频输入和输出的模型。上表中的最后一行接受文本作为输入并输出数字，通常被称为嵌入文本（**Embedding Text**），代表人工智能模型中使用的内部数据结构。

**Embedding（嵌入）**

嵌入是将文本、图像或视频转化为数值表示的技术，能够捕捉输入数据之间的关联性。

通过计算两段文本向量表示之间的数值距离，应用程序即可判定原始对象在嵌入向量空间中的相似程度。

![Embedding（嵌入）](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202512082308459.jpg)

**结构化输出**

AI 模型的输出传统上以 `java.lang.String` 形式返回，在提示词中简单要求 “输出 JSON” 并不能百分百保证结果准确性。

这一复杂性催生了一个专门领域：既要设计能生成预期输出的提示词，又需将返回的原始字符串转换为可供应用程序集成的数据结构。

![结构化输出 Converter 架构](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202512082316399.jpg)

**评估 AI 响应**

有效评估 AI 系统对用户请求的响应输出，对于确保最终应用的准确性和实用性至关重要。目前已有多种新兴技术可利用预训练模型自身实现这一目标。

该评估流程需要分析生成内容是否契合用户意图及查询上下文，通过相关性、连贯性和事实准确性等指标来衡量 AI 响应的质量。

一种方法是将用户请求和 AI 模型响应同时提交给模型，询问该响应是否符合所提供的数据。

此外，利用向量数据库中存储的信息作为补充数据可以增强评估过程，有助于确定响应的相关性。

## 1.2 将你的数据与 API 接入 AI 模型

现有三种技术可定制 AI 模型以整合你的数据：

- **微调（Fine-Tuning）**：不仅需要专业机器学习知识，还因模型规模导致计算资源消耗极大。

- **提示词填充（Prompt Stuffing）**：一种更实用的替代方案是将数据直接嵌入到提供给模型的提示词中。鉴于模型的 Token 限制，需要特定技术确保相关数据能适配上下文窗口。这种方法俗称 “提示词填充”。Spring AI 库能帮助你基于该技术（现多称为检索增强生成/RAG）实现解决方案。

  ![提示词填充（Prompt Stuffing）](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202512082322921.jpg)

- **[工具调用（Tool Calling）](https://springdoc.cn/spring-ai/concepts.html#concept-fc)**：该技术支持注册工具（用户自定义服务），将大语言模型与外部系统 API 连接。Spring AI 大幅简化了实现 [工具调用](https://springdoc.cn/spring-ai/api/tools.html) 所需的代码量。

**检索增强生成（RAG）**

该技术采用批处理编程模型：首先从文档中读取非结构化数据，经转换后写入向量数据库。本质上这是一个 ETL（抽取-转换-加载）流程，而向量数据库正是 RAG 技术中检索环节的核心组件。

RAG 的下一阶段是处理用户输入。当需要 AI 模型回答用户问题时，系统会将问题与所有 “相似” 的文档片段一起放入提示词中发送给模型。这正是使用向量数据库的原因 — 它极其擅长快速定位语义相似的内容。

![Spring AI RAG](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202512082327127.jpg)

**工具调用**

大语言模型（LLM）在训练完成后即固化，导致知识陈旧，且无法直接访问或修改外部数据。

[工具调用机制（Tool Calling）](https://springdoc.cn/spring-ai/api/tools.html) 有效解决了这些局限。该功能允许你将自定义服务注册为工具，将大语言模型与外部系统 API 连接，使 LLM 能获取实时数据并委托这些系统执行数据处理操作。

![工具调用的主要操作顺序](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202512082333097.jpg)

1. 要让模型能够调用某个工具，需要在聊天请求中包含该工具的定义。每个工具定义包含名称、描述以及输入参数的 Schema。
2. 当模型决定调用工具时，它会返回一个响应，其中包含工具名称和按照定义 Schema 建模的输入参数。
3. 应用程序负责根据工具名称识别并执行对应工具，同时使用提供的输入参数进行操作。
4. 工具调用的结果由应用程序负责处理。
5. 应用程序将工具调用的结果返回给模型。
6. 模型利用工具调用结果作为额外上下文生成最终响应。

# 二、入门

## 1.1 配置组件仓库

将以下 Repository 定义添加到 Maven 或 Gradle 构建文件中：

```xml
<repositories>
  <repository>
    <id>spring-snapshots</id>
    <name>Spring Snapshots</name>
    <url>https://repo.spring.io/snapshot</url>
    <releases>
      <enabled>false</enabled>
    </releases>
  </repository>
  <repository>
    <name>Central Portal Snapshots</name>
    <id>central-portal-snapshots</id>
    <url>https://central.sonatype.com/repository/maven-snapshots/</url>
    <releases>
      <enabled>false</enabled>
    </releases>
    <snapshots>
      <enabled>true</enabled>
    </snapshots>
  </repository>
</repositories>
```

**NOTE:** 使用 Maven 构建 Spring AI 快照版本时，请特别注意镜像配置。若你的 `settings.xml` 文件中配置了如下镜像：

```xml
<mirror>
    <id>my-mirror</id>
    <mirrorOf>*</mirrorOf>
    <url>https://my-company-repository.com/maven</url>
</mirror>
```

通配符 `*` 会将所有仓库请求重定向至镜像，导致无法访问 Spring 快照仓库。需修改 `mirrorOf` 配置排除 Spring 仓库：

```xml
<mirror>
    <id>my-mirror</id>
    <mirrorOf>*,!spring-snapshots,!central-portal-snapshots</mirrorOf>
    <url>https://my-company-repository.com/maven</url>
</mirror>
```

此配置允许 Maven 直接访问 Spring 快照仓库，同时其他依赖仍通过镜像获取。

## 1.2 依赖管理

Spring AI 物料清单（BOM）声明了指定版本所有依赖的推荐版本。你可使用 Spring Boot Parent POM 或 Spring Boot 的 BOM（spring-boot-dependencies）来管理 Spring Boot 版本。

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.ai</groupId>
            <artifactId>spring-ai-bom</artifactId>
            <version>1.0.0-SNAPSHOT</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

# 三、Reference

## 3.1 聊天客户端 API

`ChatClient` 通过 Fluent API 与 AI 模型交互，同时支持同步和流式编程模型。

### 1、创建 ChatClient

**使用自动配置的 ChatClient.Builder**

以下是获取用户简单请求 `String` 响应的基础示例：

```java
@RestController
class MyController {

    private final ChatClient chatClient;

    public MyController(ChatClient.Builder chatClientBuilder) {
        this.chatClient = chatClientBuilder.build();
    }

    @GetMapping("/ai")
    String generation(String userInput) {
        return this.chatClient.prompt()
            .user(userInput)
            .call()
            .content();
    }
}
```

此示例中，`userInput` 为用户消息内容。`call()` 方法向 AI 模型发送请求， `content()` 方法以 `String` 形式返回模型响应。

**多聊天模型协作**

Spring AI 默认自动配置单个 `ChatClient.Builder` Bean，但应用中可能需要使用多个聊天模型。处理方法如下：

所有场景均需通过设置属性 `spring.ai.chat.client.enabled=false` 来禁用 `ChatClient.Builder` 自动配置。该设置允许手动创建多个 `ChatClient` 实例。

- 单一模型类型下的多ChatClient实例

```java
// 以编程式创建 ChatClient实例
ChatModel myChatModel = ... // 已由Spring Boot自动配置完成
ChatClient chatClient = ChatClient.create(myChatModel);

// 或使用 Builder 实现更精细控制
ChatClient.Builder builder = ChatClient.builder(myChatModel);
ChatClient customChatClient = builder
    .defaultSystemPrompt("You are a helpful assistant.")
    .build();
```

- 不同模型类型的 ChatClient 配置

```java
// 使用多 AI 模型时，可为每个模型定义独立的 ChatClient Bean：
@Configuration
public class ChatClientConfig {

    @Bean
    public ChatClient openAiChatClient(OpenAiChatModel chatModel) {
        return ChatClient.create(chatModel);
    }

    @Bean
    public ChatClient anthropicChatClient(AnthropicChatModel chatModel) {
        return ChatClient.create(chatModel);
    }
}

// 随后可通过 @Qualifier 注解将这些 Bean 注入应用组件：
@Configuration
public class ChatClientExample {

    @Bean
    CommandLineRunner cli(
            @Qualifier("openAiChatClient") ChatClient openAiChatClient,
            @Qualifier("anthropicChatClient") ChatClient anthropicChatClient) {

        return args -> {
            var scanner = new Scanner(System.in);
            ChatClient chat;

            // Model selection
            System.out.println("\nSelect your AI model:");
            System.out.println("1. OpenAI");
            System.out.println("2. Anthropic");
            System.out.print("Enter your choice (1 or 2): ");

            String choice = scanner.nextLine().trim();

            if (choice.equals("1")) {
                chat = openAiChatClient;
                System.out.println("Using OpenAI model");
            } else {
                chat = anthropicChatClient;
                System.out.println("Using Anthropic model");
            }

            // Use the selected chat client
            System.out.print("\nEnter your question: ");
            String input = scanner.nextLine();
            String response = chat.prompt(input).call().content();
            System.out.println("ASSISTANT: " + response);

            scanner.close();
        };
    }
}
```

- 多 OpenAI 兼容 API 端点

```java
// OpenAiApi 与 OpenAiChatModel 类提供的 mutate() 方法，支持基于现有实例创建不同属性的变体，特别适用于需对接多个 OpenAI 兼容 API 的场景。
@Service
public class MultiModelService {

    private static final Logger logger = LoggerFactory.getLogger(MultiModelService.class);

    @Autowired
    private OpenAiChatModel baseChatModel;

    @Autowired
    private OpenAiApi baseOpenAiApi;

    public void multiClientFlow() {
        try {
            // Derive a new OpenAiApi for Groq (Llama3)
            OpenAiApi groqApi = baseOpenAiApi.mutate()
                .baseUrl("https://api.groq.com/openai")
                .apiKey(System.getenv("GROQ_API_KEY"))
                .build();

            // Derive a new OpenAiApi for OpenAI GPT-4
            OpenAiApi gpt4Api = baseOpenAiApi.mutate()
                .baseUrl("https://api.openai.com")
                .apiKey(System.getenv("OPENAI_API_KEY"))
                .build();

            // Derive a new OpenAiChatModel for Groq
            OpenAiChatModel groqModel = baseChatModel.mutate()
                .openAiApi(groqApi)
                .defaultOptions(OpenAiChatOptions.builder().model("llama3-70b-8192").temperature(0.5).build())
                .build();

            // Derive a new OpenAiChatModel for GPT-4
            OpenAiChatModel gpt4Model = baseChatModel.mutate()
                .openAiApi(gpt4Api)
                .defaultOptions(OpenAiChatOptions.builder().model("gpt-4").temperature(0.7).build())
                .build();

            // Simple prompt for both models
            String prompt = "What is the capital of France?";

            String groqResponse = ChatClient.builder(groqModel).build().prompt(prompt).call().content();
            String gpt4Response = ChatClient.builder(gpt4Model).build().prompt(prompt).call().content();

            logger.info("Groq (Llama3) response: {}", groqResponse);
            logger.info("OpenAI GPT-4 response: {}", gpt4Response);
        }
        catch (Exception e) {
            logger.error("Error in multi-client flow", e);
        }
    }
}
```

`ChatClient` Fluent 式 API 通过重载 `prompt` 方法提供三种提示词创建方式：

- `prompt()`：无参方法启动 Fluent 式API，支持逐步构建用户消息、系统消息等提示词组件。
- `prompt(Prompt prompt)`：接收 `Prompt` 参数，支持通过非 Fluent 式 API 构建的 Prompt 实例。
- `prompt(String content)`：便捷方法，接收用户文本内容，功能类似前项重载。

### 2、ChatClient 响应

- 返回 ChatResponse

```java
ChatResponse chatResponse = chatClient.prompt()
    .user("Tell me a joke")
    .call()
    .chatResponse();
```

- 返回实体

```java
// 例如，给定一个 Java record
record ActorFilms(String actor, List<String> movies) {}

// 通过 entity() 方法可轻松将 AI 模型输出映射至该 record 类
ActorFilms actorFilms = chatClient.prompt()
    .user("Generate the filmography for a random actor.")
    .call()
    .entity(ActorFilms.class);

// 支持泛型集合等复杂类型指定
List<ActorFilms> actorFilms = chatClient.prompt()
    .user("Generate the filmography of 5 movies for Tom Hanks and Bill Murray.")
    .call()
    .entity(new ParameterizedTypeReference<List<ActorFilms>>() {});
```

- 流式响应

```java
// stream() 方法支持异步获取响应
Flux<String> output = chatClient.prompt()
    .user("Tell me a joke")
    .stream()
    .content();
```

### 3、提示模版

`ChatClient` Fuent 式 API 支持提供含变量的用户/系统消息模板，运行时进行替换。

```java
String answer = ChatClient.create(chatModel).prompt()
    .user(u -> u
            .text("Tell me the names of 5 movies whose soundtrack was composed by {composer}")
            .param("composer", "John Williams"))
    .call()
    .content();
```

默认模板变量采用 `{}` 语法。若提示词中包含 JSON，建议改用 `<>` 等分隔符避免冲突。

```java
String answer = ChatClient.create(chatModel).prompt()
    .user(u -> u
            .text("Tell me the names of 5 movies whose soundtrack was composed by <composer>")
            .param("composer", "John Williams"))
    .templateRenderer(StTemplateRenderer.builder().startDelimiterToken('<').endDelimiterToken('>').build())
    .call()
    .content();
```

如需改用其他模板引擎，可直接向 `ChatClient` 提供 `TemplateRenderer` 接口的自定义实现。

### 4、使用默认值

- 默认的系统消息

在 `@Configuration` 类中为 `ChatClient` 配置默认 `system`（系统）消息可简化运行时代码。预设默认值后，调用时仅需指定 `user` 消息，无需每次请求重复设置系统消息。

```java
// 将系统消息配置为始终以海盗口吻回复
@Configuration
class Config {

    @Bean
    ChatClient chatClient(ChatClient.Builder builder) {
        return builder.defaultSystem("You are a friendly chat bot that answers question in the voice of a Pirate")
                .build();
    }

}

// 通过 @RestController 调用
@RestController
class AIController {

	private final ChatClient chatClient;

	AIController(ChatClient chatClient) {
		this.chatClient = chatClient;
	}

	@GetMapping("/ai/simple")
	public Map<String, String> completion(@RequestParam(value = "message", defaultValue = "Tell me a joke") String message) {
		return Map.of("completion", this.chatClient.prompt().user(message).call().content());
	}
}
```

- 带参数的默认系统消息

```java
// 以下示例将在系统消息中使用占位符，以便在运行时（而非设计时）指定回复语气。
@Configuration
class Config {

    @Bean
    ChatClient chatClient(ChatClient.Builder builder) {
        return builder.defaultSystem("You are a friendly chat bot that answers question in the voice of a {voice}")
                .build();
    }

}

@RestController
class AIController {
	private final ChatClient chatClient;

	AIController(ChatClient chatClient) {
		this.chatClient = chatClient;
	}

	@GetMapping("/ai")
	Map<String, String> completion(@RequestParam(value = "message", defaultValue = "Tell me a joke") String message, String voice) {
		return Map.of("completion",
				this.chatClient.prompt()
						.system(sp -> sp.param("voice", voice))
						.user(message)
						.call()
						.content());
	}

}
```

### 5、Advisor

[Advisor API](https://springdoc.cn/spring-ai/api/advisors.html) 为 Spring 应用中的 AI 驱动交互提供灵活强大的拦截、修改和增强能力。

- ChatClient 中的 Advisor 配置

```java
// ChatClient Fluent 式 API 提供 AdvisorSpec 接口用于配置 Advisor
interface AdvisorSpec {
    AdvisorSpec param(String k, Object v);
    AdvisorSpec params(Map<String, Object> p);
    AdvisorSpec advisors(Advisor... advisors);
    AdvisorSpec advisors(List<Advisor> advisors);
}

// Advisor 加入链的顺序至关重要，每个 Advisor 都会以某种方式修改提示词或上下文，更改后会传递给链中的下一个 Advisor
ChatClient.builder(chatModel)
    .build()
    .prompt()
    .advisors(
        MessageChatMemoryAdvisor.builder(chatMemory).build(),
        QuestionAnswerAdvisor.builder(vectorStore).build()
    )
    .user(userText)
    .call()
    .content();
```

在此配置中，`MessageChatMemoryAdvisor` 将首先执行，将对话历史添加到提示词中。随后，`QuestionAnswerAdvisor` 将基于用户问题和添加的对话历史执行搜索，可能提供更相关的结果。

- 检索增强生成

请参阅 [R检索增强生成指南](https://springdoc.cn/spring-ai/api/retrieval-augmented-generation.html)。

- 日志

`SimpleLoggerAdvisor` 是一个记录 `ChatClient` 请求和响应数据的 Advisor，可用于调试和监控 AI 交互。

```java
// 启用日志记录需在创建 ChatClient 时向 Advisor 链添加 SimpleLoggerAdvisor，建议将其添加至链的末端
ChatResponse response = ChatClient.create(chatModel).prompt()
        .advisors(new SimpleLoggerAdvisor())
        .user("Tell me a joke?")
        .call()
        .chatResponse();
```

要查看日志，请将 `advisor` 包的日志级别设为 `DEBUG`，将此配置添加到 `application.properties` 或 `application.yaml` 文件中。

```properties
logging.level.org.springframework.ai.chat.client.advisor=DEBUG
```

可通过以下构造函数自定义 `AdvisedRequest` 和 `ChatResponse` 的日志记录内容：

```java
SimpleLoggerAdvisor(
    Function<AdvisedRequest, String> requestToString,
    Function<ChatResponse, String> responseToString
)

// 示例用法：
SimpleLoggerAdvisor customLogger = new SimpleLoggerAdvisor(
    request -> "Custom request: " + request.userText,
    response -> "Custom response: " + response.getResult()
);
```

### 6、聊天记忆

`ChatMemory` 接口定义了聊天对话记忆的存储机制，提供添加消息、检索消息及清空对话历史的方法。

当前内置实现为：`MessageWindowChatMemory`。

`MessageWindowChatMemory` 是聊天记忆实现，维护最多指定数量（默认 20 条）的消息窗口。当消息超出限制时，旧消息会被移除（系统消息除外）。若添加新系统消息，则清除所有旧系统消息，确保始终保留最新上下文的同时控制内存占用。

`MessageWindowChatMemory` 基于 `ChatMemoryRepository` 抽象层实现，该抽象层提供多种聊天记忆存储方案，包括：

- `InMemoryChatMemoryRepository`（内存存储）
- `JdbcChatMemoryRepository`（JDBC 关系型数据库存储）
- `CassandraChatMemoryRepository`（Cassandra 存储）
- `Neo4jChatMemoryRepository`（Neo4j 图数据库存储）

详见 [聊天记忆功能](https://springdoc.cn/spring-ai/api/chat-memory.html) 文档获取详细说明和使用示例。

## 3.2 提示（Prompt）

### 1、提示词工程

在生成式 AI 中，提示（Prompt）能引导人工智能模型产生特定的输出。

该领域研究常涉及分析和比较不同提示词在各种情境下的有效性。例如，一项重要研究表明，以 “深呼吸后逐步解决这个问题” 开头的提示词能显著提升解题效率，这凸显了精心设计的语言对生成式AI系统性能的影响。

例如，一个简单的提示词模板如下：

```
Tell me a {adjective} joke about {content}.
```

在 Spring AI 中，提示词模板可类比 Spring MVC 架构中的 “View” 层。系统会提供一个模型对象（通常是 `java.util.Map`）来填充模板中的占位符，最终 “渲染” 生成的字符串将作为传递给 AI 模型的提示内容。

### 2、API 概览

**Message**

`Message` 接口封装了文本内容、元数据属性集合以及称为 `MessageType` 的分类标识。

接口定义如下：

```java
public interface Content {

	String getContent();

	Map<String, Object> getMetadata();
}

public interface Message extends Content {

    /**
    主要角色包括：
    - System：指导 AI 的行为和响应风格，类似于在开始对话前向 AI 提供指令。
    - User：代表用户的输入 — 包括问题、命令或对 AI 的陈述。
    - Assistant：AI 对用户输入的响应，不仅是答案或反应，更对维持对话流至关重要。
    - Tool：专注于响应工具调用类助手消息，返回附加信息。
    */
	MessageType getMessageType();
}
```

`Message` 接口的多种实现对应 AI 模型可处理的不同消息类别，模型根据对话角色区分消息类型。

![Spring AI Message API](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202512152302234.jpg)

**Prompt**

`Prompt` 类作为有序 `Message` 对象和请求 `ChatOptions` 的容器。每个 `Message` 在提示中扮演独特角色，其内容和意图各异。

以下是 `Prompt` 类的简化版本（省略构造函数和工具方法）：

```java
public class Prompt implements ModelRequest<List<Message>> {

    private final List<Message> messages;

    private ChatOptions chatOptions;
}
```

**PromptTemplate**

Spring AI 中提示词模板化的核心组件是 `PromptTemplate` 类，专为简化结构化提示词的创建而设计，这些提示词随后会发送给 AI 模型处理。

```java
public class PromptTemplate implements PromptTemplateActions, PromptTemplateMessageActions {

    // Other methods to be discussed later
}
```

### 3、示例用法

以下是 AI Workshop 中关于 [PromptTemplates](https://github.com/Azure-Samples/spring-ai-azure-workshop/blob/main/2-README-prompt-templating.md) 的简单示例：

```java
PromptTemplate promptTemplate = new PromptTemplate("Tell me a {adjective} joke about {topic}");

Prompt prompt = promptTemplate.create(Map.of("adjective", adjective, "topic", topic));

return chatModel.call(prompt).getResult();
```

以下是 AI Workshop 中关于 [Role](https://github.com/Azure-Samples/spring-ai-azure-workshop/blob/main/3-README-prompt-roles.md) 的另一个示例：

```java
String userText = """
    Tell me about three famous pirates from the Golden Age of Piracy and why they did.
    Write at least a sentence for each pirate.
    """;

Message userMessage = new UserMessage(userText);

String systemText = """
  You are a helpful AI assistant that helps people find information.
  Your name is {name}
  You should reply to the user's request with your name and also in the style of a {voice}.
  """;

SystemPromptTemplate systemPromptTemplate = new SystemPromptTemplate(systemText);
Message systemMessage = systemPromptTemplate.createMessage(Map.of("name", name, "voice", voice));

Prompt prompt = new Prompt(List.of(userMessage, systemMessage));

List<Generation> response = chatModel.call(prompt).getResults();
```

该示例展示如何通过 `SystemPromptTemplate` 构建 `Prompt` 实例：使用 `system` 角色创建含占位值的 `Message`，再与 `user` 角色的 `Message` 组合成提示，最终传递给 `ChatModel` 获取生成式响应。

**使用自定义模板渲染器**

若提示中包含 JSON，建议改用 `<` 和 `>` 等分隔符以避免与JSON语法冲突。

```java
PromptTemplate promptTemplate = PromptTemplate.builder()
    .renderer(StTemplateRenderer.builder().startDelimiterToken('<').endDelimiterToken('>').build())
    .template("""
            Tell me the names of 5 movies whose soundtrack was composed by <composer>.
            """)
    .build();

String prompt = promptTemplate.render(Map.of("composer", "John Williams"));
```

**使用 Resource 替代原始字符串**

Spring AI 支持 `org.springframework.core.io.Resource` 抽象，因此可将提示数据存入文件并直接用于 `PromptTemplate`。例如：在 Spring 托管组件中定义字段来获取 `Resource`。

```java
@Value("classpath:/prompts/system-message.st")
private Resource systemResource;
```

然后将该资源直接传递给 `SystemPromptTemplate`。

```java
SystemPromptTemplate systemPromptTemplate = new SystemPromptTemplate(systemResource);
```

### 4、Token

令牌（Token）是 AI 模型运作的基础单元。输入时，模型将词语转换为令牌；输出时，再将令牌转换回词语。

在英语中，1 个 Token 大约对应 0.75 个单词。作为参考，莎士比亚全集约 90 万单词，对应约 120 万 Token。

![Token](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202512082311539.png)

## 3.3 结构化输出

## 3.4 多模态

## 3.5 模型

## 3.6 聊天记忆

## 3.7 工具调用

## 3.8 模型上下文协议（MCP）

## 3.9 检索增强生成（RAG）

## 3.10 模型评估

## 3.11 向量数据库

## 3.12 可观测性

## 3.13 Development-time Services

## 3.14 Testing







# 四、Guides



