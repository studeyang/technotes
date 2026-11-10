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

> MCP协议是一个采用基于日期版本控制（格式为YYYY-MM-DD）的不断演进的标准。当前协议版本为2025-11-25。您可查看最新版本的[协议规范](https://modelcontextprotocol.io/specification/2025-11-25/)。

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

# 02 | MCP 安全：AI 系统的全面保护

**AI 特有的安全威胁**

1、间接提示注入

攻击者将恶意指令嵌入外部内容中——文档、网页、邮件或数据源，AI 系统随后将其作为合法命令处理。

攻击场景：

- 基于文档的注入：恶意指令藏匿于处理文档中，触发 AI 产生意外行为
- 网页内容利用：被篡改网页包含嵌入提示，爬取后操控 AI 行为
- 邮件攻击：邮件内恶意提示导致 AI 助手泄露信息或执行未授权操作
- 数据源污染：被感染的数据库或 API 向 AI 系统提供受污染内容

现实影响：这些攻击可能导致数据外泄、隐私侵犯、有害内容生成及用户交互操控。详见[《MCP 中的提示注入》（Simon Willison）](https://simonwillison.net/2025/Apr/9/mcp-prompt-injection/)。

![提示注入攻击示意图](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/prompt-injection.ed9fbfde297ca877.webp)

2、工具中毒攻击

工具中毒 针对定义 MCP 工具的元数据发起攻击，利用大语言模型对工具描述和参数的解释决策过程。

攻击机制：

- 元数据操控：攻击者向工具描述、参数定义或使用示例注入恶意指令
- 隐形指令：工具元数据中隐藏的提示被 AI 模型处理，但对人类用户不可见
- 动态工具变更（“放鸽子”）：用户批准的工具后来被修改执行恶意操作，用户无察觉
- 参数注入：恶意内容嵌入工具参数模式，影响模型行为

托管服务器风险：远程MCP服务器存在较高风险，因为工具定义可以在用户初次批准后更新，这可能导致之前安全的工具变为恶意。有关全面分析，请参见[工具中毒攻击（Invariant Labs）](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)。

![工具注入攻击示意图](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/tool-injection.3b0b4a6b24de6bef.webp)

**微软AI安全解决方案**

微软AI提示盾牌通过多层安全机制，为直接和间接的提示注入攻击提供全面防御：

![微软提示盾牌保护示意](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/prompt-shield.ff5b95be76e9c78c.webp)



# ==构建阶段==

# 03 | 构建你的第一个服务器和客户端

## 3.1 第一个服务器

**基本 MCP 服务器结构**

一个 MCP 服务器通常包含：

- 服务器配置：设置端口、身份验证及其他参数
- 资源：提供给 LLM 的数据和上下文
- 工具：模型可以调用的功能
- 提示：用于生成或构造文本的模板

**构建您的第一个 MCP 服务器**

创建服务器需要按照以下步骤：

- 安装 MCP SDK。
- 创建项目并设置项目结构。
- 编写服务器代码。
- 测试服务器。

1、创建项目

创建一个 Spring Boot 项目：

```bash
curl https://start.spring.io/starter.zip \
  -d dependencies=web \
  -d javaVersion=21 \
  -d type=maven-project \
  -d groupId=com.example \
  -d artifactId=calculator-server \
  -d name=McpServer \
  -d packageName=com.microsoft.mcp.sample.server \
  -o calculator-server.zip
```

解压 zip 文件：

```bash
unzip calculator-server.zip -d calculator-server
cd calculator-server
# 可选地移除未使用的测试
rm -rf src/test/java
```

2、添加依赖

将以下完整配置添加到您的 *pom.xml* 文件中：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <!-- Spring Boot parent for dependency management -->
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.5.0</version>
        <relativePath />
    </parent>

    <!-- Project coordinates -->
    <groupId>com.example</groupId>
    <artifactId>calculator-server</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>Calculator Server</name>
    <description>Basic calculator MCP service for beginners</description>

    <!-- Properties -->
    <properties>
        <java.version>21</java.version>
        <maven.compiler.source>21</maven.compiler.source>
        <maven.compiler.target>21</maven.compiler.target>
    </properties>

    <!-- Spring AI BOM for version management -->
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

    <!-- Dependencies -->
    <dependencies>
        <dependency>
            <groupId>org.springframework.ai</groupId>
            <artifactId>spring-ai-starter-mcp-server-webflux</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        <dependency>
         <groupId>org.springframework.boot</groupId>
         <artifactId>spring-boot-starter-test</artifactId>
         <scope>test</scope>
      </dependency>
    </dependencies>

    <!-- Build configuration -->
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <configuration>
                    <release>21</release>
                </configuration>
            </plugin>
        </plugins>
    </build>

    <!-- Repositories for Spring AI snapshots -->
    <repositories>
        <repository>
            <id>spring-milestones</id>
            <name>Spring Milestones</name>
            <url>https://repo.spring.io/milestone</url>
            <snapshots>
                <enabled>false</enabled>
            </snapshots>
        </repository>
        <repository>
            <id>spring-snapshots</id>
            <name>Spring Snapshots</name>
            <url>https://repo.spring.io/snapshot</url>
            <releases>
                <enabled>false</enabled>
            </releases>
        </repository>
    </repositories>
</project>
```

3、编写服务器代码

首先，修改主应用类：

*src/main/java/com/microsoft/mcp/sample/server/McpServerApplication.java*:

```java
package com.microsoft.mcp.sample.server;

import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.ai.tool.method.MethodToolCallbackProvider;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import com.microsoft.mcp.sample.server.service.CalculatorService;

@SpringBootApplication
public class McpServerApplication {

    public static void main(String[] args) {
        SpringApplication.run(McpServerApplication.class, args);
    }
    
    @Bean
    public ToolCallbackProvider calculatorTools(CalculatorService calculator) {
        return MethodToolCallbackProvider.builder().toolObjects(calculator).build();
    }
}
```

4、添加工具和资源

创建计算器服务 *src/main/java/com/microsoft/mcp/sample/server/service/CalculatorService.java*：

```java
package com.microsoft.mcp.sample.server.service;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.stereotype.Service;

/**
 * Service for basic calculator operations.
 * This service provides simple calculator functionality through MCP.
 */
@Service
public class CalculatorService {

    /**
     * Add two numbers
     * @param a The first number
     * @param b The second number
     * @return The sum of the two numbers
     */
    @Tool(description = "Add two numbers together")
    public String add(double a, double b) {
        double result = a + b;
        return formatResult(a, "+", b, result);
    }

    /**
     * Subtract one number from another
     * @param a The number to subtract from
     * @param b The number to subtract
     * @return The result of the subtraction
     */
    @Tool(description = "Subtract the second number from the first number")
    public String subtract(double a, double b) {
        double result = a - b;
        return formatResult(a, "-", b, result);
    }

    /**
     * Multiply two numbers
     * @param a The first number
     * @param b The second number
     * @return The product of the two numbers
     */
    @Tool(description = "Multiply two numbers together")
    public String multiply(double a, double b) {
        double result = a * b;
        return formatResult(a, "*", b, result);
    }

    /**
     * Divide one number by another
     * @param a The numerator
     * @param b The denominator
     * @return The result of the division
     */
    @Tool(description = "Divide the first number by the second number")
    public String divide(double a, double b) {
        if (b == 0) {
            return "Error: Cannot divide by zero";
        }
        double result = a / b;
        return formatResult(a, "/", b, result);
    }

    /**
     * Calculate the power of a number
     * @param base The base number
     * @param exponent The exponent
     * @return The result of raising the base to the exponent
     */
    @Tool(description = "Calculate the power of a number (base raised to an exponent)")
    public String power(double base, double exponent) {
        double result = Math.pow(base, exponent);
        return formatResult(base, "^", exponent, result);
    }

    /**
     * Calculate the square root of a number
     * @param number The number to find the square root of
     * @return The square root of the number
     */
    @Tool(description = "Calculate the square root of a number")
    public String squareRoot(double number) {
        if (number < 0) {
            return "Error: Cannot calculate square root of a negative number";
        }
        double result = Math.sqrt(number);
        return String.format("√%.2f = %.2f", number, result);
    }

    /**
     * Calculate the modulus (remainder) of division
     * @param a The dividend
     * @param b The divisor
     * @return The remainder of the division
     */
    @Tool(description = "Calculate the remainder when one number is divided by another")
    public String modulus(double a, double b) {
        if (b == 0) {
            return "Error: Cannot divide by zero";
        }
        double result = a % b;
        return formatResult(a, "%", b, result);
    }

    /**
     * Calculate the absolute value of a number
     * @param number The number to find the absolute value of
     * @return The absolute value of the number
     */
    @Tool(description = "Calculate the absolute value of a number")
    public String absolute(double number) {
        double result = Math.abs(number);
        return String.format("|%.2f| = %.2f", number, result);
    }

    /**
     * Get help about available calculator operations
     * @return Information about available operations
     */
    @Tool(description = "Get help about available calculator operations")
    public String help() {
        return "Basic Calculator MCP Service\n\n" +
               "Available operations:\n" +
               "1. add(a, b) - Adds two numbers\n" +
               "2. subtract(a, b) - Subtracts the second number from the first\n" +
               "3. multiply(a, b) - Multiplies two numbers\n" +
               "4. divide(a, b) - Divides the first number by the second\n" +
               "5. power(base, exponent) - Raises a number to a power\n" +
               "6. squareRoot(number) - Calculates the square root\n" + 
               "7. modulus(a, b) - Calculates the remainder of division\n" +
               "8. absolute(number) - Calculates the absolute value\n\n" +
               "Example usage: add(5, 3) will return 5 + 3 = 8";
    }

    /**
     * Format the result of a calculation
     */
    private String formatResult(double a, String operator, double b, double result) {
        return String.format("%.2f %s %.2f = %.2f", a, operator, b, result);
    }
}
```

5、启动服务器

```bash
./mvnw clean install -DskipTests
java -jar target/calculator-server-0.0.1-SNAPSHOT.jar
```

**测试与调试**

MCP 提供一些工具，帮助您测试和调试服务器：

- Inspector 工具：这是一种图形界面，允许您连接服务器，测试工具、提示和资源。
- curl：您还可以使用 curl 等命令行工具，或其他可创建并运行 HTTP 命令的客户端连接服务器。

[MCP Inspector](https://github.com/modelcontextprotocol/inspector) 是一款可视化测试工具，帮助您：

1. 发现服务器功能：自动检测可用资源、工具和提示
2. 测试工具执行：尝试不同参数并实时查看响应
3. 查看服务器元数据：检查服务器信息、模式和配置

```bash
# 例如 TypeScript，安装和运行 MCP Inspector
npx @modelcontextprotocol/inspector node build/index.js
```

运行上述命令后，MCP Inspector 会在您的浏览器中启动一个本地 Web 界面。您将看到一个仪表盘，展示您注册的 MCP 服务器及其可用的工具、资源和提示。此界面允许您交互式测试工具执行，检查服务器元数据，并查看实时响应，方便验证和调试 MCP 服务器实现。

下面是界面截图：

![MCP Inspector server connection](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/connected.73d1e042c24075d3.webp)

## 3.2 第一个客户端



## 3.3 搭载 LLM 的客户端

## 3.4 VS Code 集成

## 3.5 stdio 服务器

## 3.6 HTTP 流

## 3.7 Microsoft Foundry 工具包

## 3.8 测试

## 3.9 部署

## 3.10 高级服务器使用

## 3.11 简单认证

## 3.12 MCP 主机

## 3.13 MCP 检查器

## 3.14 采样

## 3.15 MCP 应用





# ==成长阶段==

# 04

# 05

# ==精通阶段==

# 06

# 07

# 08

# 09

# 10

# 11



