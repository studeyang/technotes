> 参考资料：https://spring.io/projects/spring-statemachine
>
> Github: https://github.com/spring-projects/spring-statemachine

# 一、概述

Spring Statemachine 是一个框架，供应用程序开发人员在 Spring 应用程序中使用状态机概念。

Spring Statemachine 旨在提供以下功能：

- 易于使用的扁平一级状态机，适用于简单的用例。
- 分层状态机结构可简化复杂的状态配置。
- 状态机区域提供更复杂的状态配置。
- 触发器、转换、防护和操作的使用。
- 类型安全配置适配器。
- 构建器模式可轻松实例化以在 Spring 应用程序上下文之外使用
- 常见的使用示例
- 基于Zookeeper的分布式状态机
- 状态机事件监听器。
- UML Eclipse Papyrus 建模。
- 将机器配置存储在持久存储中。
- Spring IOC 集成将 bean 与状态机关联起来。

# 二、前言

## 2.1 专业术语

**Extended State 扩展状态**

扩展状态是保存在状态机中的一组特殊变量，用于减少所需状态的数量。

**Transition 过渡**

转换是源状态和目标状态之间的关系。它可以是复合转换的一部分，复合转换将状态机从一种状态配置转换为另一种状态配置，表示状态机对特定类型事件发生的完整响应。

**Event 事件**

发送到状态机然后驱动各种状态更改的实体。

**Initial State 初始状态**

状态机启动的特殊状态。初始状态总是绑定到特定的状态机或区域。具有多个区域的状态机可以具有多个初始状态。

**End State 最终状态**

（也称为最终状态。）一种特殊的状态，表示封闭区域已完成。如果包围区域直接包含在状态机中并且状态机中的所有其他区域也完成，则整个状态机完成。

**History State 历史状态**

一种伪状态，让状态机记住其最后的活动状态。存在两种类型的历史状态：*浅层*（仅记住顶级状态）和*深层*（记住子机中的活动状态）。

**Choice State 选择状态**

一种伪状态，允许基于（例如）事件头或扩展状态变量进行转换选择。

**Junction State 结态**

一种伪状态，与选择状态相对相似，但允许多个传入转换，而选择仅允许一个传入转换。

**Fork State 分叉状态**

一种伪状态，可控制进入某个区域。

**Join State 加入状态**

一种伪状态，可控制从某个区域的退出。

**Entry Point 切入点**

允许受控进入子机的伪状态。

**Exit Point 退出点**

允许从子机受控退出的伪状态。

**Region 地区**

区域是复合状态或状态机的正交部分。它包含状态和转换。

**Guard 警卫**

根据扩展状态变量和事件参数的值动态评估的布尔表达式。保护条件通过仅在评估为`TRUE`时启用操作或转换并在评估为`FALSE`时禁用它们来影响状态机的行为。

**Action 行动**

操作是在触发转换期间运行的行为。

## 2.2 状态机速成课程

**States 状态**

状态是状态机所在的模型。将状态概念与编程联系起来，意味着您可以依赖状态、状态变量或与状态机的其他交互，而不是使用标志、嵌套的 if/else/break 子句或其他不切实际（有时是曲折的）逻辑。

**Pseudo States 伪状态**

伪状态是一种特殊类型的状态，通常通过赋予状态特殊含义（例如初始状态）来将更多高级逻辑引入状态机。然后，状态机可以通过执行 UML 状态机概念中可用的各种操作来在内部对这些状态做出反应。

**Initial 最初的**

每个状态机始终需要**初始伪**状态，无论您有一个简单的单级状态机还是由子机或区域组成的更复杂的状态机。初始状态定义状态机启动时应进入的位置。没有它，状态机就是不正确的。

**End 结尾**

**Terminate 伪状态**（也称为“结束状态”）指示特定状态机已达到其最终状态。实际上，这意味着状态机不再处理任何事件并且不会转换到任何其他状态。然而，在子机是区域的情况下，状态机可以从其最终状态重新启动。

**Choice 选择**

您可以使用**Choice 伪状态**选择从此状态转换的动态条件分支。守卫评估动态条件，以便选择一个分支。通常使用简单的 if/elseif/else 结构来确保选择一个分支。否则，状态机可能会陷入死锁，并且配置格式不正确。

**Junction 交界处**

**Junction 伪状态**在功能上与 choice 类似，因为两者都是通过 if/elseif/else 结构实现的。唯一真正的区别是 junction 允许多个传入转换，而 choice 只允许一个。因此，差异主要是学术性的，但确实存在一些差异，例如当设计状态机与真实的 UI 建模框架一起使用时。

**History 历史**

您可以使用**历史伪状态**来记住最后一个活动状态配置。状态机退出后，您可以使用历史状态来恢复以前已知的配置。有两种类型的历史状态可用： `SHALLOW` （只记住状态机本身的活动状态）和`DEEP` （也记住嵌套状态）。

**Fork 叉**

您可以使用**Fork 伪状态**显式进入一个或多个区域。下图显示了叉子的工作原理：

![statechart7](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202501112306454.png)

**Join 加入**

**Join 伪状态**将来自不同区域的多个转换合并在一起。它通常用于等待和阻止参与区域进入其加入目标状态。下图显示了连接的工作原理：

**Entry Point 切入点**

**入口点伪状态**表示状态机或提供状态机或状态机内部封装的复合状态的入口点。在拥有入口点的状态机或复合状态的每个区域中，最多存在从入口点到该区域内的顶点的单个转换。

**Exit Point 退出点**

**退出点伪状态**是状态机或复合状态的退出点，它提供状态或状态机内部的封装。在复合状态（或子机状态引用的状态机）的任何区域内的退出点终止的转换意味着退出该复合状态或子机状态（执行其关联的退出行为）。

**Guard Conditions 守卫条件**

保护条件是计算结果为`TRUE`或 `FALSE` ，基于扩展状态变量和事件参数。防护与操作和转换一起使用，以动态选择是否应运行特定操作或转换。保护、事件参数和扩展状态变量的各个方面的存在使状态机设计变得更加简单。

**Events 事件**

事件是驱动状态机最常用的触发行为。还有其他方法可以触发状态机中的行为（例如计时器），但事件是真正让用户与状态机交互的方法。事件也称为“信号”。它们基本上表示可能改变状态机状态的东西。

**Transitions 过渡**

转换是源状态和目标状态之间的关系。从一种状态到另一种状态的切换是由触发器引起的状态转换。

**Internal Transition 内部转变**

当需要运行操作而不引起状态转换时，使用内部转换。在内部转换中，源状态和目标状态始终相同，并且与没有状态进入和退出动作的自转换相同。

**External versus Local Transitions 外部转换与本地转换**

在大多数情况下，外部和局部转换在功能上是等效的，除非转换发生在超级状态和子状态之间。如果目标状态是源状态的子状态，则局部转换不会导致退出和进入源状态。相反，如果目标是源状态的超状态，则局部转换不会导致退出和进入目标状态。下图显示了具有非常简单的超级和子状态的本地和外部转换之间的差异：

![statechart4](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202501112310897.png)

**Triggers 触发器**

触发器开始转换。触发器可以由事件或计时器驱动。

**Actions 行为**

行为确实将状态机状态更改粘合到用户自己的代码中。状态机可以对各种更改和状态机中的步骤（例如进入或退出状态）或进行状态转换运行操作。

行为通常可以访问状态上下文，这使运行的代码可以选择以各种方式与状态机交互。状态上下文公开了整个状态机，以便用户可以访问扩展状态变量、事件标头（如果转换基于事件）或实际转换（可以在其中查看有关此状态更改发生位置的更多详细信息）从哪里来以及要去哪里）。

**Hierarchical State Machines 分层状态机**

当特定状态必须同时存在时，分层状态机的概念用于简化状态设计。

分层状态实际上是 UML 状态机相对于传统状态机（例如 Mealy 或 Moore 机）的创新。分层状态允许您定义某种抽象级别（类似于 Java 开发人员如何使用抽象类定义类结构）。例如，使用嵌套状态机，您可以定义多个状态级别的转换（可能具有不同的条件）。状态机总是尝试查看当前状态是否能够处理事件以及转换保护条件。如果这些条件的计算结果不为`TRUE` ，则状态机仅查看超级状态可以处理的内容。

**Regions 地区**

区域（也称为正交区域）通常被视为应用于状态的异或 (XOR) 运算。状态机方面的区域概念通常有点难以理解，但通过一个简单的示例，事情会变得更简单。

我们中的一些人拥有全尺寸键盘，主键位于左侧，数字键位于右侧。您可能已经注意到，双方确实都有自己的状态，如果您按“numlock”键（仅改变数字键盘本身的行为），您就会看到这种状态。如果您没有全尺寸键盘，您可以购买外部 USB 数字键盘。由于键盘的左侧和右侧可以单独存在，因此它们必须具有完全不同的状态，这意味着它们在不同的状态机上运行。在状态机术语中，键盘的主要部分是一个区域，而数字键盘是另一区域。

将两个不同的状态机作为完全独立的实体来处理会有点不方便，因为它们仍然以某种方式一起工作。这种独立性使得正交区域可以在状态机的单个状态内的多个同时状态中组合在一起。

## 2.3 使用场景

在以下情况下，项目是使用状态机的良好候选者：

- 您可以将应用程序或其结构的一部分表示为状态。
- 您希望将复杂的逻辑拆分为更小的可管理任务。
- 应用程序已经遇到了并发问题（例如）异步发生的事情。

当您执行以下操作时，您已经在尝试实现状态机：

- 使用布尔标志或枚举来模拟情况。
- 具有仅对应用程序生命周期的某些部分有意义的变量。
- 循环遍历 if-else 结构（或者更糟糕的是多个此类结构），检查是否设置了特定标志或枚举，然后进一步排除当标志和枚举的某些组合存在或不存在时要执行的操作。

# 三、入门

**pom.xml 依赖**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
	<modelVersion>4.0.0</modelVersion>

	<groupId>com.example</groupId>
	<artifactId>demo</artifactId>
	<version>0.0.1-SNAPSHOT</version>
	<packaging>jar</packaging>

	<name>gs-statemachine</name>
	<description>Demo project for Spring Statemachine</description>

	<parent>
		<groupId>org.springframework.boot</groupId>
		<artifactId>spring-boot-starter-parent</artifactId>
		<version>3.1.6</version>
		<relativePath/> <!-- lookup parent from repository -->
	</parent>

	<properties>
		<project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
		<project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
		<java.version>1.8</java.version>
		<spring-statemachine.version>4.0.0</spring-statemachine.version>
	</properties>

	<dependencies>
		<dependency>
			<groupId>org.springframework.statemachine</groupId>
			<artifactId>spring-statemachine-starter</artifactId>
		</dependency>

		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-test</artifactId>
			<scope>test</scope>
		</dependency>
	</dependencies>

	<dependencyManagement>
		<dependencies>
			<dependency>
				<groupId>org.springframework.statemachine</groupId>
				<artifactId>spring-statemachine-bom</artifactId>
				<version>${spring-statemachine.version}</version>
				<type>pom</type>
				<scope>import</scope>
			</dependency>
		</dependencies>
	</dependencyManagement>

	<build>
		<plugins>
			<plugin>
				<groupId>org.springframework.boot</groupId>
				<artifactId>spring-boot-maven-plugin</artifactId>
			</plugin>
		</plugins>
	</build>

	<repositories>
		<repository>
			<id>spring-snapshots</id>
			<name>Spring Snapshots</name>
			<url>https://repo.spring.io/snapshot</url>
			<snapshots>
				<enabled>true</enabled>
			</snapshots>
		</repository>
		<repository>
			<id>spring-milestones</id>
			<name>Spring Milestones</name>
			<url>https://repo.spring.io/milestone</url>
			<snapshots>
				<enabled>false</enabled>
			</snapshots>
		</repository>
	</repositories>

	<pluginRepositories>
		<pluginRepository>
			<id>spring-snapshots</id>
			<name>Spring Snapshots</name>
			<url>https://repo.spring.io/snapshot</url>
			<snapshots>
				<enabled>true</enabled>
			</snapshots>
		</pluginRepository>
		<pluginRepository>
			<id>spring-milestones</id>
			<name>Spring Milestones</name>
			<url>https://repo.spring.io/milestone</url>
			<snapshots>
				<enabled>false</enabled>
			</snapshots>
		</pluginRepository>
	</pluginRepositories>

</project>
```

**开发您的第一个 Spring 状态机应用程序**

您可以首先创建一个实现`CommandLineRunner`的简单 Spring Boot `Application`类。以下示例展示了如何执行此操作：

```java
@SpringBootApplication
public class Application implements CommandLineRunner {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

}
```

然后您需要添加状态和事件，如以下示例所示：

```
public enum States {
    SI, S1, S2
}

public enum Events {
    E1, E2
}
```

然后需要添加状态机配置，如下例所示：

```
@Configuration
@EnableStateMachine
public class StateMachineConfig
        extends EnumStateMachineConfigurerAdapter<States, Events> {

    @Override
    public void configure(StateMachineConfigurationConfigurer<States, Events> config)
            throws Exception {
        config
            .withConfiguration()
                .autoStartup(true)
                .listener(listener());
    }

    @Override
    public void configure(StateMachineStateConfigurer<States, Events> states)
            throws Exception {
        states
            .withStates()
                .initial(States.SI)
                    .states(EnumSet.allOf(States.class));
    }

    @Override
    public void configure(StateMachineTransitionConfigurer<States, Events> transitions)
            throws Exception {
        transitions
            .withExternal()
                .source(States.SI).target(States.S1).event(Events.E1)
                .and()
            .withExternal()
                .source(States.S1).target(States.S2).event(Events.E2);
    }

    @Bean
    public StateMachineListener<States, Events> listener() {
        return new StateMachineListenerAdapter<States, Events>() {
            @Override
            public void stateChanged(State<States, Events> from, State<States, Events> to) {
                System.out.println("State change to " + to.getId());
            }
        };
    }
}
```

然后您需要实现`CommandLineRunner`和自动装配`StateMachine` 。以下示例展示了如何执行此操作：

```java
@SpringBootApplication
public class Application implements CommandLineRunner {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
    
    @Autowired
    private StateMachine<States, Events> stateMachine;

    @Override
    public void run(String... args) throws Exception {
        stateMachine.sendEvent(Events.E1);
        stateMachine.sendEvent(Events.E2);
    }

}
```

该命令的结果应该是正常的 Spring Boot 输出。但是，您还应该找到以下几行：

```
State change to SI
State change to S1
State change to S2
```

# 四、最新特性

## 4.1 版本1.1

Spring Statemachine 1.1 专注于安全性以及与 Web 应用程序更好的互操作性。它包括以下内容：

- 添加了对 Spring Security 的全面支持。请参阅[状态机安全](https://docs.spring.io/spring-statemachine/docs/4.0.0/reference/index.html#sm-security)。
- 与“@WithStateMachine”的上下文集成已得到极大增强。请参阅[上下文集成](https://docs.spring.io/spring-statemachine/docs/4.0.0/reference/index.html#sm-context)。
- `StateContext`现在是一等公民，让您可以与状态机交互。请参阅[使用`StateContext`](https://docs.spring.io/spring-statemachine/docs/4.0.0/reference/index.html#sm-statecontext) 。
- 通过对 Redis 的内置支持，增强了有关持久性的功能。请参阅[使用 Redis](https://docs.spring.io/spring-statemachine/docs/4.0.0/reference/index.html#sm-persist-redis) 。
- 一项新功能有助于持久操作。看 [使用`StateMachinePersister`](https://docs.spring.io/spring-statemachine/docs/4.0.0/reference/index.html#sm-persist-statemachinepersister) 。
- 配置模型类现在位于公共 API 中。
- 基于计时器的事件的新功能。
- 新`Junction`伪状态。请[参阅Junction状态](https://docs.spring.io/spring-statemachine/docs/4.0.0/reference/index.html#statemachine-config-states-junction)。
- 新的退出点和入口点伪状态。请参阅[退出和进入点状态](https://docs.spring.io/spring-statemachine/docs/4.0.0/reference/index.html#statemachine-config-states-exitentry)。
- 配置模型验证器。
- 新示例。请参阅[安全](https://docs.spring.io/spring-statemachine/docs/4.0.0/reference/index.html#statemachine-examples-security)和[事件服务](https://docs.spring.io/spring-statemachine/docs/4.0.0/reference/index.html#statemachine-examples-eventservice)。
- 使用 Eclipse Papyrus 的 UI 建模支持。请参阅[Eclipse 建模支持](https://docs.spring.io/spring-statemachine/docs/4.0.0/reference/index.html#sm-papyrus)。

## 4.2 版本1.2

# 五、使用 Spring 状态机

## 5.1 状态机配置

### 使用`enable`注释

我们使用两个熟悉的 Spring*启用器*注释来简化配置： `@EnableStateMachine`和`@EnableStateMachineFactory` 。这些注释当放置在`@Configuration`类中时，可以启用状态机所需的一些基本功能。

当您需要配置来创建`StateMachine`实例时，可以使用`@EnableStateMachine` 。通常， `@Configuration`类扩展适配器（ `EnumStateMachineConfigurerAdapter` 或`StateMachineConfigurerAdapter` ），它允许您覆盖配置回调方法。我们自动检测您是否使用这些适配器类并相应地修改运行时配置逻辑。

当您需要配置来创建`StateMachineFactory`实例时，可以使用`@EnableStateMachineFactory` 。

### 配置状态

我们稍后将在本指南中介绍更复杂的配置示例，但我们首先从简单的事情开始。对于最简单的状态机，您可以使用 `EnumStateMachineConfigurerAdapter` 并定义可能的状态并选择初始状态和可选的结束状态。

```
@Configuration
@EnableStateMachine
public class Config1Enums
		extends EnumStateMachineConfigurerAdapter<States, Events> {

	@Override
	public void configure(StateMachineStateConfigurer<States, Events> states)
			throws Exception {
		states
			.withStates()
				.initial(States.S1)
				.end(States.SF)
				.states(EnumSet.allOf(States.class));
	}

}
```

您还可以使用`StateMachineConfigurerAdapter`使用字符串而不是枚举作为状态和事件，如下一个示例所示。大多数配置示例都使用枚举，但是一般来说，您可以互换字符串和枚举。

```java
@Configuration
@EnableStateMachine
public class Config1Strings
		extends StateMachineConfigurerAdapter<String, String> {

	@Override
	public void configure(StateMachineStateConfigurer<String, String> states)
			throws Exception {
		states
			.withStates()
				.initial("S1")
				.end("SF")
				.states(new HashSet<String>(Arrays.asList("S1","S2","S3","S4")));
	}

}
```

### 配置分层状态

您可以通过使用多个`withStates()`来定义分层状态 调用，您可以在其中使用`parent()`来指示这些特定状态是某些其他状态的子状态。以下示例展示了如何执行此操作：

```
@Configuration
@EnableStateMachine
public class Config2
		extends EnumStateMachineConfigurerAdapter<States, Events> {

	@Override
	public void configure(StateMachineStateConfigurer<States, Events> states)
			throws Exception {
		states
			.withStates()
				.initial(States.S1)
				.state(States.S1)
				.and()
				.withStates()
					.parent(States.S1)
					.initial(States.S2)
					.state(States.S2);
	}

}
```

### 配置区域

没有特殊的配置方法可以将状态集合标记为正交状态的一部分。简单地说，当同一个分层状态机具有多组状态，并且每组状态都有一个初始状态时，就会创建正交状态。因为单个状态机只能有一个初始状态，多个初始状态必然意味着一个特定的状态必须有多个独立的区域。以下示例展示了如何定义区域：

```
@Configuration
@EnableStateMachine
public class Config10
		extends EnumStateMachineConfigurerAdapter<States2, Events> {

	@Override
	public void configure(StateMachineStateConfigurer<States2, Events> states)
			throws Exception {
		states
			.withStates()
				.initial(States2.S1)
				.state(States2.S2)
				.and()
				.withStates()
					.parent(States2.S2)
					.initial(States2.S2I)
					.state(States2.S21)
					.end(States2.S2F)
					.and()
				.withStates()
					.parent(States2.S2)
					.initial(States2.S3I)
					.state(States2.S31)
					.end(States2.S3F);
	}

}
```

当持久化具有区域的计算机或通常依赖任何功能来重置计算机时，您可能需要有一个区域的专用 ID。默认情况下，此 ID 是生成的 UUID。如以下示例所示， `StateConfigurer`有一个名为`region(String id)`的方法，可让您设置区域的 ID：

```
@Configuration
@EnableStateMachine
public class Config10RegionId
		extends EnumStateMachineConfigurerAdapter<States2, Events> {

	@Override
	public void configure(StateMachineStateConfigurer<States2, Events> states)
			throws Exception {
		states
			.withStates()
				.initial(States2.S1)
				.state(States2.S2)
				.and()
				.withStates()
					.parent(States2.S2)
					.region("R1")
					.initial(States2.S2I)
					.state(States2.S21)
					.end(States2.S2F)
					.and()
				.withStates()
					.parent(States2.S2)
					.region("R2")
					.initial(States2.S3I)
					.state(States2.S31)
					.end(States2.S3F);
	}

}
```

### 配置转换

我们支持三种不同类型的转换： `external` 、 `internal`和`local` 。转换由信号（发送到状态机的事件）或计时器触发。以下示例显示如何定义所有三种转换：

```
@Configuration
@EnableStateMachine
public class Config3
		extends EnumStateMachineConfigurerAdapter<States, Events> {

	@Override
	public void configure(StateMachineStateConfigurer<States, Events> states)
			throws Exception {
		states
			.withStates()
				.initial(States.S1)
				.states(EnumSet.allOf(States.class));
	}

	@Override
	public void configure(StateMachineTransitionConfigurer<States, Events> transitions)
			throws Exception {
		transitions
			.withExternal()
				.source(States.S1).target(States.S2)
				.event(Events.E1)
				.and()
			.withInternal()
				.source(States.S2)
				.event(Events.E2)
				.and()
			.withLocal()
				.source(States.S2).target(States.S3)
				.event(Events.E3);
	}

}
```

### 配置守卫

您可以使用守卫来保护状态转换。您可以使用`Guard`接口进行评估，其中方法可以访问`StateContext` 。以下示例展示了如何执行此操作：

```
@Configuration
@EnableStateMachine
public class Config4
		extends EnumStateMachineConfigurerAdapter<States, Events> {

	@Override
	public void configure(StateMachineTransitionConfigurer<States, Events> transitions)
			throws Exception {
		transitions
			.withExternal()
				.source(States.S1).target(States.S2)
				.event(Events.E1)
				.guard(guard())
				.and()
			.withExternal()
				.source(States.S2).target(States.S3)
				.event(Events.E2)
				.guardExpression("true");

	}

	@Bean
	public Guard<States, Events> guard() {
		return new Guard<States, Events>() {

			@Override
			public boolean evaluate(StateContext<States, Events> context) {
				return true;
			}
		};
	}

}
```

我们使用了两种不同类型的防护配置。首先，我们创建了一个简单的`Guard`作为 bean 并将其附加到状态`S1`和`S2`之间的转换。

其次，我们使用 SPeL 表达式作为保护来指示该表达式必须返回`BOOLEAN`值。在幕后，这个基于表达式的防护是`SpelExpressionGuard` 。我们将其附加到状态`S2`和`S3`之间的转换。两个守卫总是评估为`true` 。

### 配置操作 Actions

您可以定义要通过转换和状态执行的操作。操作始终作为源自触发器的转换的结果而运行。以下示例显示如何定义操作：

```
@Configuration
@EnableStateMachine
public class Config51
		extends EnumStateMachineConfigurerAdapter<States, Events> {

	@Override
	public void configure(StateMachineTransitionConfigurer<States, Events> transitions)
			throws Exception {
		transitions
			.withExternal()
				.source(States.S1)
				.target(States.S2)
				.event(Events.E1)
				.action(action());
	}

	@Bean
	public Action<States, Events> action() {
		return new Action<States, Events>() {

			@Override
			public void execute(StateContext<States, Events> context) {
				// do something
			}
		};
	}

}
```

在上面的示例中，单个`Action`被定义为名为`action` bean，并与从`S1`到`S2`的转换相关联。以下示例展示了如何多次使用一个操作：

```
@Configuration
@EnableStateMachine
public class Config52
		extends EnumStateMachineConfigurerAdapter<States, Events> {

	@Override
	public void configure(StateMachineStateConfigurer<States, Events> states)
			throws Exception {
		states
			.withStates()
				.initial(States.S1, action())
				.state(States.S1, action(), null)
				.state(States.S2, null, action())
				.state(States.S2, action())
				.state(States.S3, action(), action());
	}

	@Bean
	public Action<States, Events> action() {
		return new Action<States, Events>() {

			@Override
			public void execute(StateContext<States, Events> context) {
				// do something
			}
		};
	}

}
```

在前面的示例中，单个`Action`由名为`action` bean 定义，并与状态`S1` 、 `S2`和`S3`关联。我们需要澄清这里发生了什么：

- 我们为初始状态`S1`定义了一个动作。
- 我们为状态`S1`定义了进入操作，并将退出操作留空。
- 我们为状态`S2`定义了退出操作，并将进入操作留空。
- 我们为状态`S2`定义了单个状态操作。
- 我们定义了状态`S3`的进入和退出操作。
- 请注意，状态`S1`通过`initial()`和`state()`使用了两次 功能。仅当您想定义进入或退出时才需要执行此操作 具有初始状态的动作。

### 配置伪状态

**初始状态**

您可以使用`initial()`将特定状态标记为初始状态 方法。这个初始动作很好，例如初始化 扩展状态变量。以下示例展示了如何使用`initial()`方法：

```
@Configuration
@EnableStateMachine
public class Config11
		extends EnumStateMachineConfigurerAdapter<States, Events> {

	@Override
	public void configure(StateMachineStateConfigurer<States, Events> states)
			throws Exception {
		states
			.withStates()
				.initial(States.S1, initialAction())
				.end(States.SF)
				.states(EnumSet.allOf(States.class));
	}

	@Bean
	public Action<States, Events> initialAction() {
		return new Action<States, Events>() {

			@Override
			public void execute(StateContext<States, Events> context) {
				// do something initially
			}
		};
	}

}
```

**终止状态**

您可以使用`end()`方法将特定状态标记为结束状态。您最多可以为每个单独的子计算机或区域执行一次此操作。以下示例显示如何使用`end()`方法：

```
代码同上
```

**历史状态**

您可以为每个单独的状态机定义一次状态历史记录。您需要选择其状态标识符并设置`History.SHALLOW`或 `History.DEEP` .深.以下示例使用`History.SHALLOW` ：

```
@Configuration
@EnableStateMachine
public class Config12
		extends EnumStateMachineConfigurerAdapter<States3, Events> {

	@Override
	public void configure(StateMachineStateConfigurer<States3, Events> states)
			throws Exception {
		states
			.withStates()
				.initial(States3.S1)
				.state(States3.S2)
				.and()
				.withStates()
					.parent(States3.S2)
					.initial(States3.S2I)
					.state(States3.S21)
					.state(States3.S22)
					.history(States3.SH, History.SHALLOW);
	}

	@Override
	public void configure(StateMachineTransitionConfigurer<States3, Events> transitions)
			throws Exception {
		transitions
			.withHistory()
				.source(States3.SH)
				.target(States3.S22);
	}

}
```

**选择状态**

需要在状态和转换中定义选择才能正常工作。您可以使用`choice()`将特定状态标记为选择状态 方法。当转换发生时，该状态需要与源状态匹配 为此选择进行配置。

您可以使用`withChoice()`配置转换，在其中定义源状态和`first/then/last`一个结构，这相当于普通的转换 `if/elseif/else` 。使用`first`和`then` ，您可以指定一个防护，就像在`if/elseif`子句中使用条件一样。

转换需要能够存在，因此您必须确保使用`last` 。否则，配置格式不正确。以下示例显示如何定义选择状态：

```
@Configuration
@EnableStateMachine
public class Config13
		extends EnumStateMachineConfigurerAdapter<States, Events> {

	@Override
	public void configure(StateMachineStateConfigurer<States, Events> states)
			throws Exception {
		states
			.withStates()
				.initial(States.SI)
				.choice(States.S1)
				.end(States.SF)
				.states(EnumSet.allOf(States.class));
	}

	@Override
	public void configure(StateMachineTransitionConfigurer<States, Events> transitions)
			throws Exception {
		transitions
			.withChoice()
				.source(States.S1)
				.first(States.S2, s2Guard())
				.then(States.S3, s3Guard())
				.last(States.S4);
	}

	@Bean
	public Guard<States, Events> s2Guard() {
		return new Guard<States, Events>() {

			@Override
			public boolean evaluate(StateContext<States, Events> context) {
				return false;
			}
		};
	}

	@Bean
	public Guard<States, Events> s3Guard() {
		return new Guard<States, Events>() {

			@Override
			public boolean evaluate(StateContext<States, Events> context) {
				return true;
			}
		};
	}

}
```

### 配置通用设置

您可以使用以下命令设置部分公共状态机配置 `ConfigurationConfigurer` 。使用它，您可以设置`BeanFactory`和状态机的自动启动标志。它还允许您注册`StateMachineListener`实例、配置转换冲突策略和区域执行策略。以下示例展示了如何使用`ConfigurationConfigurer` ：

```
@Configuration
@EnableStateMachine
public class Config17
		extends EnumStateMachineConfigurerAdapter<States, Events> {

	@Override
	public void configure(StateMachineConfigurationConfigurer<States, Events> config)
			throws Exception {
		config
			.withConfiguration()
				.autoStartup(true)
				.machineId("myMachineId")
				.beanFactory(new StaticListableBeanFactory())
				.listener(new StateMachineListenerAdapter<States, Events>())
				.transitionConflictPolicy(TransitionConflictPolicy.CHILD)
				.regionExecutionPolicy(RegionExecutionPolicy.PARALLEL);
	}
}
```

## 5.2 State Machine ID 状态机ID

各种类和接口使用`machineId`作为变量或作为 方法中的参数。本节将详细介绍如何 `machineId`与正常机器操作和实例化相关。

### 使用`@EnableStateMachine`

在 Java 配置中将`machineId`设置为`mymachine`然后公开该值以用于日志。也可以从以下位置获得相同的`machineId` `StateMachine.getId()`方法。以下示例使用`machineId`方法：

```
@Override
public void configure(StateMachineConfigurationConfigurer<String, String> config)
		throws Exception {
	config
		.withConfiguration()
			.machineId("mymachine");
}
```

以下日志输出示例显示了`mymachine` ID：

```
11:23:54,509  INFO main support.LifecycleObjectSupport [main] -
started S2 S1  / S1 / uuid=8fe53d34-8c85-49fd-a6ba-773da15fcaf1 / id=mymachine
```

### 使用`@EnableStateMachineFactory`

如果`machineId`使用 `StateMachineFactory`并使用该 ID 请求新机器，如以下示例所示：

```
StateMachineFactory<String, String> factory = context.getBean(StateMachineFactory.class);
StateMachine<String, String> machine = factory.getStateMachine("mymachine");
```

### 使用`StateMachineModelFactory`



## 5.3 状态机工厂

### 通过适配器工厂

实际上使用`@EnableStateMachine`创建状态机 通过工厂工作，因此`@EnableStateMachineFactory`只是公开 该工厂通过其接口。下面的例子使用 `@EnableStateMachineFactory` ：

```
@Configuration
@EnableStateMachineFactory
public class Config6
		extends EnumStateMachineConfigurerAdapter<States, Events> {

	@Override
	public void configure(StateMachineStateConfigurer<States, Events> states)
			throws Exception {
		states
			.withStates()
				.initial(States.S1)
				.end(States.SF)
				.states(EnumSet.allOf(States.class));
	}

}
```

现在您已经使用`@EnableStateMachineFactory`创建了一个工厂而不是状态机 bean，您可以注入它并使用它（按原样）来请求新的状态机。以下示例展示了如何执行此操作：

```
public class Bean3 {

	@Autowired
	StateMachineFactory<States, Events> factory;

	void method() {
		StateMachine<States,Events> stateMachine = factory.getStateMachine();
		stateMachine.startReactively().subscribe();
	}
}
```

### 通过构建器的状态机

```
StateMachine<String, String> buildMachine1() throws Exception {
	Builder<String, String> builder = StateMachineBuilder.builder();
	builder.configureStates()
		.withStates()
			.initial("S1")
			.end("SF")
			.states(new HashSet<String>(Arrays.asList("S1","S2","S3","S4")));
	return builder.build();
}
```

## 5.4 使用延迟事件

## 5.5 使用范围

## 5.6 使用动作

## 5.7 使用守卫

## 5.8 使用扩展状态

## 5.9 触发转换

## 5.10 监听状态机事件

## 5.11 Context Integration

## 5.12 使用`StateMachineAccessor`

## 5.13 使用`StateMachineInterceptor`

## 5.14 状态机安全

## 5.15 状态机错误处理

## 5.16 状态机服务

## 5.17 持久化状态机

## 5.18 Spring Boot Support 

## 5.19 监控状态机

## 5.20 使用分布式状态

## 5.21 测试支持

## 5.22 Eclipse 建模支持

## 5.23 存储库支持

