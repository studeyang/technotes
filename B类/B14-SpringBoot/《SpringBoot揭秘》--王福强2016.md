> 代码基于 SpringBoot 2.6.4 分析。

# 第3章 SpringBoot的工作机制

## 3.2 @SpringBootApplication 背后的秘密

**怎么创建 ApplicationContext 的？**





```java
@SpringBootConfiguration
@EnableAutoConfiguration
@ComponentScan(excludeFilters = { @Filter(type = FilterType.CUSTOM, classes = TypeExcludeFilter.class),
		@Filter(type = FilterType.CUSTOM, classes = AutoConfigurationExcludeFilter.class) })
public @interface SpringBootApplication {
}
```

**@Configuration**

表示本身是 IoC 容器的配置类。@SpringBootConfiguration 这个注解只是更好区分这是 SpringBoot 的配置注解，本质还是用了 Spring 提供的 @Configuration 注解。

**@EnableAutoConfiguration**

```java
@AutoConfigurationPackage
@Import(AutoConfigurationImportSelector.class)
public @interface EnableAutoConfiguration {
}
```

`@AutoConfigurationPackage`的作用是：应用去加载启动类所在包下面的所有类。

`AutoConfigurationImportSelector`的作用是：AutoConfiguration 的 ImportSelector，加载所有`spring.factories`文件中的`org.springframework.boot.autoconfigure.EnableAutoConfiguration`的值。

**@ComponentScan**

> 跟踪一下

## 3.3 SpringApplication: SpringBoot程序启动的一站式解决方案

首先遍历执行所有通过 SpringFactoriesLoader 可以查找到并加载的 SpringApplicationRunListener，调用它他的 started() 方法。（代码A）

```java
public ConfigurableApplicationContext run(String... args) {
	long startTime = System.nanoTime();
	DefaultBootstrapContext bootstrapContext = createBootstrapContext();
	ConfigurableApplicationContext context = null;
	configureHeadlessProperty();
	SpringApplicationRunListeners listeners = getRunListeners(args);  // A
	listeners.starting(bootstrapContext, this.mainApplicationClass);
	try {
		ApplicationArguments applicationArguments = new DefaultApplicationArguments(args);
		ConfigurableEnvironment environment = prepareEnvironment(listeners, bootstrapContext, applicationArguments);
		configureIgnoreBeanInfo(environment);
		Banner printedBanner = printBanner(environment);
		context = createApplicationContext();
		context.setApplicationStartup(this.applicationStartup);
		prepareContext(bootstrapContext, context, environment, listeners, applicationArguments, printedBanner);
		refreshContext(context);
		afterRefresh(context, applicationArguments);
		Duration timeTakenToStartup = Duration.ofNanos(System.nanoTime() - startTime);
		if (this.logStartupInfo) {
			new StartupInfoLogger(this.mainApplicationClass).logStarted(getApplicationLog(), timeTakenToStartup);
		}
		listeners.started(context, timeTakenToStartup);  // A1
		callRunners(context, applicationArguments);
	} catch (Throwable ex) {
		handleRunFailure(context, ex, listeners);
		throw new IllegalStateException(ex);
	}
	try {
		Duration timeTakenToReady = Duration.ofNanos(System.nanoTime() - startTime);
		listeners.ready(context, timeTakenToReady);
	} catch (Throwable ex) {
		handleRunFailure(context, ex, null);
		throw new IllegalStateException(ex);
	}
	return context;
}
```



## 3.4 再读自动配置



# 第4章 了解纷杂的 spring-boot-starter

## 4.1 应用日志和 spring-boot-starter-logging

## 4.2 快速 Web 应用开发与 spring-boot-starter-web

## 4.3 数据访问与 spring-boot-starter-jdbc

# 第5章 SpringBoot 微服务实践探索

## 5.1 使用 SpringBoot 构建微服务

## 5.2 SpringBoot 微服务的发布与部署

## 5.3 SpringBoot 微服务的注册与发现

## 5.4 SpringBoot 微服务的监控与运维

## 5.5 SpringBoot 微服务的安全与防护

## 5.6 SpringBoot 微服务体系的脊梁：发布与部署平台



