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

**Prompt（提示）**

提示（Prompt）是引导人工智能模型产生特定输出的语言输入的基础。

ChatGPT 专为人类对话而设计，由于这种交互方式的重要性，“Prompt Engineering（提示工程）” 一词已成为一门独立的学科。提高提示有效性的技术层出不穷。在制作提示语方面投入时间，可以大大提高结果输出。

例如，一个简单的提示词模板如下：

```
Tell me a {adjective} joke about {content}.
```

在 Spring AI 中，提示词模板可类比 Spring MVC 架构中的 “View” 层。系统会提供一个模型对象（通常是 `java.util.Map`）来填充模板中的占位符，最终 “渲染” 生成的字符串将作为传递给 AI 模型的提示内容。

**Embedding（嵌入）**

嵌入是将文本、图像或视频转化为数值表示的技术，能够捕捉输入数据之间的关联性。

通过计算两段文本向量表示之间的数值距离，应用程序即可判定原始对象在嵌入向量空间中的相似程度。

![Embedding（嵌入）](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202512082308459.jpg)

**Token**

令牌（Token）是 AI 模型运作的基础单元。输入时，模型将词语转换为令牌；输出时，再将令牌转换回词语。

在英语中，1 个 Token 大约对应 0.75 个单词。作为参考，莎士比亚全集约 90 万单词，对应约 120 万 Token。

![Token](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202512082311539.png)

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

# 三、Reference

# 四、Guides

