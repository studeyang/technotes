# 开篇词 | 掌握 Go 和微服务，跟进未来服务端开发的主流趋势

**为什么要学习 Go 微服务**



**课程设置**

第一部分（01~05）

- 云原生
- 微服务
- DDD
- Service Mesh

第二部分（06~11）

- Go 开发的基础知识（Go 语法和流程控制、Go 并发和 Go Web 应用开发等）
- 采用 DDD 对货运平台的业务进行划分
- 案例应用实战（微服务部署、容器编排、持续集成和自动化测试等）

第三部分（12~35）

- 微服务架构中基础组件的原理
- Go 业务案例的实战（服务注册与发现、RPC 调用、网关、容错处理、负载均衡、统一认证与授权，以及分布式链路追踪等）
- 如何通过 Service Mesh 来整合这些组件提供的能力

第四部分（36~38）

- Go 微服务开发中的相关经验和要点（日志采集、Go 错误处理、并发陷阱和系统监控等）

# 第一部分（01~05）

# 01 | 为什么说云原生重构了互联网产品开发模式？

**云计算的前世今生**

- 阶段1：虚拟化技术



- 阶段2：虚拟机的市场化应用



- 阶段3：容器化和容器编排的兴起



**云原生出现的背景**



**云原生解决了哪些问题**



**不断更新的云原生定义**



# 02 | 云原生基础架构的组成以及云原生应用的特征

**云原生的基础架构**

1. 微服务
2. 容器
3. 服务网格
4. 不可变基础设施与 DevOps
5. 声明式 API

**云原生应用的特征：云原生与“12 因素”**

1. 方法论和核心思想
2. 编码、部署和运维原则
3. 具体内容



# 03 | 微服务架构是如何演进的？

**服务端架构的演进**

1. 单体架构
2. 垂直分层架构
3. SOA 面向服务架构
4. 微服务架构

**微服务框架的选型**

1. Go 语言的独特优势
2. Go Kit框架
3. Go Micro 框架
4. Go Kit 与 Go Micro 的对比

**云原生与微服务架构是什么关系**

# 04 | DDD 领域场景分析的战略模式

**微服务就是“小”服务吗？**



**DDD 应对软件复杂度之法**



**DDD 是不是银弹？**



**DDD 战略模式**

1. 领域和子域
2. 限界上下文和通用语言

# 05 | 为什么说 Service Mesh 是下一代微服务架构？

**Service Mesh 背后的诉求**

1. 微服务架构的复杂性
2. 微服务本身的挑战
3. 本质诉求

**什么是 Service Mesh**



**Service Mesh 的开源组件**

1. Istio
2. Linkerd
3. Envoy

# 第二部分（06~11）

# 06 | Go 语言开发快速回顾：语法、数据结构和流程控制

**基础语法**

```go
// fileName: simple.go
package main
import (
	"fmt"
	"sync"
)
func input(ch chan string)  {
	defer wg.Done()
	defer close(ch)
	var input string
	fmt.Println("Enter 'EOF' to shut down: ")
	for {
		_, err := fmt.Scanf("%s", &input)
		if err != nil{
			fmt.Println("Read input err: ", err.Error())
			break
		}
		if input == "EOF"{
			fmt.Println("Bye!")
			break
		}
		ch <- input
	}
}
func output(ch chan string)  {
	defer wg.Done()
	for value := range ch{
		fmt.Println("Your input: ", value)
	}
}
var wg sync.WaitGroup
func main() {
	ch := make(chan string)
	wg.Add(2)
	go input(ch) // 读取输入
	go output(ch) // 输出到命令行
	wg.Wait()
	fmt.Println("Exit!")
}
```

1. 函数声明
2. 变量的声明与初始化
3. 指针
4. struct

**数据结构**

1. array（数组）
2. slice（切片）
3. map（字典）

**流程控制**

1. for 循环
2. 分支控制
3. defer 延迟执行

# 07 | 如何使用 Go 更好地开发并发程序？

**Go 的 MPG 线程模型**



**goroutine 和 channel**

1. select 多路复用

2. Context 上下文



# 08 | 如何基于 Go-kit 开发 Web 应用：从接口层到业务层再到数据层

**使用 Go Modules 管理项目依赖**



**一个基于 Go-kit 简单的 User 应用**

https://github.com/longjoy/micro-go-course



**使用 gorm 连接 My SQL 数据库**



# 09 | 案例：货运平台应用的微服务划分



# 10 | 案例：微服务 Docker 容器化部署和 Kubernetes 容器编排



# 11 | 案例：如何结合 Jenkins 完成持续化集成和自动化测试？





# 第三部分（12~35）

# 12 | 服务注册与发现如何满足服务治理？

![image-20210512221432993](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210512221603.png)

# 13 | 案例：如何基于 Consul 给微服务添加服务注册与发现？

# 14 | 案例：如何在 Go-kit 和 Service Mesh 中进行服务注册与发现？

# 15 | 微服务间如何进行远程方法调用？



















