> 来自：https://github.com/microsoft/mcp-for-beginners

# README

**学习路径概览**

- 基础阶段：理解基础知识（模块 0-2）

你将了解什么是MCP，为什么它存在，以及它如何融入更广泛的人工智能开发领域。

- 构建阶段：创建你的第一个实现（模块 3）

你将获得构建 MCP 服务器和客户端的实战经验。别担心——我们将从简单开始，并引导你完成每一步。

- 成长阶段：高级概念与实际应用（模块 4-5）

我们将涵盖实用的实现策略、调试技术以及多模态 AI 集成等高级话题。

你还将学习如何将 MCP 实现扩展到生产环境，并集成如 Azure 这样的云平台。这些模块将助你构建能够应对现实需求的 MCP 解决方案。

- 精通阶段：社区与专业方向（模块 6-11）

你将学习如何为开源 MCP 项目做贡献，实施高级认证模式，以及构建全面集成数据库的解决方案。

模块 11 特别值得一提——它是一个完整的 13 实验动手学习路径，教授你构建带有 PostgreSQL 集成的生产级 MCP 服务器。它就像一个总结项目，将你所学的内容汇聚一堂！

# ==基础阶段==

# 00 | 模型上下文协议（MCP）简介：为什么它对可扩展的 AI 应用至关重要

**什么是模型上下文协议（MCP）？**

模型上下文协议（MCP） 是一个 开放的、标准化的接口，允许大型语言模型（LLM）无缝地与外部工具、API 及数据源交互。

**为什么 AI 标准化至关重要**

随着生成式 AI 应用变得更加复杂，采用能够保证可扩展性、可扩展性、可维护性及避免供应商锁定的标准变得必不可少。

**MCP 的实际好处**

使用 MCP 的实际优势包括：

- 信息新鲜度：模型可以访问训练数据之外的最新信息
- 能力扩展：模型可以利用专用工具处理未训练过的任务
- 减少幻觉：外部数据源提供事实依据
- 隐私保护：敏感数据可保留在安全环境中，而非嵌入提示中

# 01 | MCP核心概念：掌握AI集成的模型上下文协议

**MCP架构：深入解析**

MCP核心遵循客户端-服务器架构，主机应用可连接多个服务器：

![image-20261105224730170](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/image-20261105224730170.png)

- MCP主机：如VSCode、Claude Desktop、IDE或想通过MCP访问数据的AI工具程序
- MCP客户端：与服务器保持一对一连接的协议客户端
- MCP服务器：轻量级程序，通过标准化模型上下文协议暴露特定能力
- 本地数据源：您计算机上的文件、数据库和服务，MCP服务器可安全访问
- 远程服务：通过互联网可访问的外部系统，MCP服务器可通过API连接

> MCP协议是一个采用基于日期版本控制（格式为YYYY-MM-DD）的不断演进的标准。当前协议版本为<strong>2025-11-25</strong>。您可查看最新版本的[协议规范](https://modelcontextprotocol.io/specification/2025-11-25/)。

**MCP中的信息流**

模型上下文协议（MCP）定义了主机、客户端、服务器和模型之间结构化的信息流。

- 主机发起连接：主机应用（例如IDE或聊天界面）通过STDIO、WebSocket或其他支持的传输方式建立与MCP服务器的连接。

- 功能协商：客户端（嵌入在主机中）和服务器交换关于其支持的功能、工具、资源和协议版本的信息，确保双方理解会话可用的能力。

- 用户请求：用户与主机进行交互（例如输入提示或命令）。主机收集此输入并传递给客户端处理。

- 资源或工具使用：如果模型判断需要调用工具（例如获取数据、执行计算或调用API），客户端发送工具调用请求给服务器，指定工具名称和参数。

- 服务器执行：服务器接收资源或工具请求，执行必要操作（如运行函数、查询数据库或检索文件），并以结构化格式将结果返回给客户端。

- 响应生成：客户端将服务器响应（资源数据、工具输出等）集成到进行中的模型交互中。模型利用这些信息生成全面且语境相关的响应。

- 结果呈现：主机从客户端接收最终输出并呈现给用户，通常包括模型生成的文本以及任何工具执行或资源查询的结果。

**代码示例：关键组件**

下面代码演示了如何定义和注册工具、处理请求以及使用模型上下文协议连接服务器。

```java
import io.modelcontextprotocol.server.McpServer;
import io.modelcontextprotocol.server.McpToolDefinition;
import io.modelcontextprotocol.server.transport.StdioServerTransport;
import io.modelcontextprotocol.server.tool.ToolExecutionContext;
import io.modelcontextprotocol.server.tool.ToolResponse;

public class WeatherMcpServer {
    public static void main(String[] args) throws Exception {
        // 创建一个 MCP 服务器
        McpServer server = McpServer.builder()
            .name("Weather MCP Server")
            .version("1.0.0")
            .build();
            
        // 注册天气工具
        server.registerTool(McpToolDefinition.builder("weatherTool")
            .description("Gets current weather for a location")
            .parameter("location", String.class)
            .execute((ToolExecutionContext ctx) -> {
                String location = ctx.getParameter("location", String.class);
                
                // 获取天气数据（简化版）
                WeatherData data = getWeatherData(location);
                
                // 返回格式化的响应
                return ToolResponse.content(
                    String.format("Temperature: %.1f°F, Conditions: %s, Location: %s", 
                    data.getTemperature(), 
                    data.getConditions(), 
                    data.getLocation())
                );
            })
            .build());
        
        // 使用 stdio 传输连接服务器
        try (StdioServerTransport transport = new StdioServerTransport()) {
            server.connect(transport);
            System.out.println("Weather MCP Server started");
            // 保持服务器运行直到进程终止
            Thread.currentThread().join();
        }
    }
    
    private static WeatherData getWeatherData(String location) {
        // 实现将调用天气 API
        // 为示例目的简化处理
        return new WeatherData(72.5, "Sunny", location);
    }
}

class WeatherData {
    private double temperature;
    private String conditions;
    private String location;
    
    public WeatherData(double temperature, String conditions, String location) {
        this.temperature = temperature;
        this.conditions = conditions;
        this.location = location;
    }
}
```









02

# ==构建阶段==

03

# ==成长阶段==

04

05

# ==精通阶段==

06

07

08

09

10

11



