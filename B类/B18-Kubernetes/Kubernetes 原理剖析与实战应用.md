> 来自拉勾教育《Kubernetes 原理剖析与实战应用》--正范

# 开篇词 | 如何深入掌握 Kubernetes？

**为什么要学习 Kubernetes**

目前，国内诸多大厂都已经在生产环境中大规模使用容器以及Kubernetes。在这场云原生浪潮中，Kubernetes无疑是最重要也绕不开的一个话题。

**如何学习 Kubernetes**

学习难点：

- 网上检索大量资料来学习，往往会一头雾水。
- 大部分图书更为体系化，但重理论多于实践。

总结来说，跟随专栏作者，从实践中学习。

分 5 个模块：

- 云原生基石：初识 Kubernetes

介绍 Kubernetes 的前世今生、基本架构，以及设计哲学。

- Kubernetes 进阶：部署高可用的业务

讲解 Kubernetes 中的一些高级对象，帮助你理解如何部署高可用的业务应用。

- 守护神：业务的日志与监控

教你围绕 Kubernetes 构建日志和监控系统。

- 安全无忧：集群的安全性与稳定性

介绍大量 Kubernetes 安全技巧及最佳实践。

- 知其所以然：底层核心原理及可扩展性

通过介绍 CRD 以及 Operator，让你可以“站在巨人的肩膀上”对 Kubernetes 进行“二次”开发。

# 模块一：初识 Kubernetes

# 01 | 前世今生：Kubernetes 是如何火起来的？

Kubernetes 的前世今生要从“云计算”的兴起开始讲起。

**云计算平台**

我们可以将经典的云计算架构分为三大服务层：也就是 IaaS（Infrastructure as a Service，基础设施即服务）、PaaS（Platform as a Service，平台即服务）和 SaaS（Software as a Service，软件即服务）。

- IaaS 层通过虚拟化技术提供计算、存储、网络等基础资源，可以在上面部署各种 OS 以及应用程序。开发者可以通过云厂商提供的 API 控制整个基础架构，无须对其进行物理上的维护和管理。
- PaaS 层提供软件部署平台（runtime），抽象掉了硬件和操作系统，可以无缝地扩展（scaling）。开发者只需要关注自己的业务逻辑，不需要关注底层。
- SaaS 层直接为开发者提供软件服务，将软件的开发、管理、部署等全部都交给第三方，用户不需要再关心技术问题，可以拿来即用。

![Drawing 0.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211222222908.png)

对应到我们生活中，可以想象自己要去一个地方旅行，那么首先就需要解决住的问题。

IaaS 服务就相当于直接在当地购买了一套商品房，像搭建系统、维护运行环境这种“装修”的事情就必须由我们自己来，但优点是“装修风格”可以自己定。

PaaS 则要简单一点，我们到了一个陌生的城市，可以选择住民宿或青旅，这样就不需要考虑装修和买家具的事情了，系统和环境都是现成的，我们只需要安装自己的运行程序就可以了。

SaaS 就更简单了，相当于直接住酒店，一切需求都由供应商搞定了，我们只需要选择自己喜欢的房间风格和户型就可以了，这时从操作系统到运行的具体软件都不再需要我们自己操心了。

那么我们该如何让系统上云呢？

**Docker**

Docker 镜像解决了环境打包的问题，它直接打包了应用运行所需要的整个“操作系统”，而且不会出现任何兼容性问题，它赋予了本地环境和云端环境无差别的能力。

有了 Docker，开发人员可以轻松地将其生产环境复制为可立即运行的容器应用程序，让工作更有效率。我们来看看CNCF （Cloud Native Computing Foundation，云计算基金会）在2019年做的调研报告。

![Drawing 6.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211222225533.png)

可以预见的是，未来企业应用容器化会越来越常见，使用容器进行交付、生产、部署是大势所趋，也是企业进行技术改造，业务快速升级的利器。

**为什么需要容器调度平台**

如果我们大规模地使用容器，就不得不考虑容器调度、部署、跨多节点访问、自动伸缩等问题。

我们来看看一个容器编排引擎到底需要哪些能力才能解决上述这些棘手的问题。

![Drawing 7.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211222223441.png)

同时满足上面所述的八大能力的容器调度平台，其实非 Kubernetes 莫属了。以前绝大多数人都是采用自建的方式来管理 Kubernetes 集群的，现在已经逐渐采用公有云的 Kubernetes 服务。可见，Kubernetes 越来越成熟，也越来越受到市场的青睐。

依据 Google Trends 收集的数据，自 Kubernetes出现以后，便呈黑马态势一路开挂，迅速并牢牢占据头把交椅位置，最终成为容器调度的事实标准。

![Drawing 10.png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211222225940.png)

**Kubernetes 成为事实标准**

我们来看看 Kubernetes 是如何凭借自身的优势走红的。

Kubernetes 并不会跟任何平台绑定，它可以跑在任何环境里，包括公有云、私有云、物理机，甚至笔记本和树莓派都可以运行，避免了用户对于厂商锁定 (vendor-lockin) 的担忧。

Kubernetes 的上手门槛很低。通过 minikube 这类工具，就可以在你的笔记本上快速搭建一套 Kubernetes 集群出来。

Kubernetes 使用了声明式API。所谓声明式，就是指你只需要提交一个定义好的 API 对象来声明你所期望的对象是什么样子即可，而无须过多关注如何达到最终的状态。Kubernetes 可以在无外界干预的情况下，完成对实际状态和期望状态的调和（Reconcile）工作。

# 02 | 高屋建瓴：Kubernetes 的架构为什么是这样的？

Kubernetes 的架构设计参考了 Borg 的架构设计，我们先来看看 Borg 架构长什么样？

**Borg 的架构**

我们先来看看 Borg 定义的两个概念，Cell 和 Cluster。

Borg 用Cell 来定义一组机器资源。Cluster 即集群，一个数据中心可以同时运行一个或者多个集群，每个集群又可以有多个 Cell。

![image (3).png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211224225320.png)

Borg 主要模块包括 BorgMaster、Borglet 和调度器。

下面我们来看看 Kuberenetes 的架构。

**Kubernetes 的架构**

Kubernetes 借鉴了 Borg 的整体架构思想，主要由 Master 和 Node 共同组成。

![image (4).png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211224225510.png)

在 Kubernetes 集群中也采用了分布式存储系统 Etcd，用于保存集群中的所有对象以及状态信息。

**Kubernetes 的组件**

Kubernetes 的控制面包含着 kube-apiserver、kube-scheduler、kube-controller-manager 这三大组件，我们也称为 Kubernetes 的三大件。

kube-apiserver 是所有内部和外部的 API 请求操作的唯一入口。同时也负责整个集群的认证、授权、访问控制、服务发现等能力。

Kube-Controller-Manager 负责维护整个 Kubernetes 集群的状态，比如多副本创建、滚动更新等。

Kube-scheduler 的工作简单来说就是监听未调度的 Pod，按照预定的调度策略绑定到满足条件的节点上。

了解完了控制面组件，我们再来看看 Node 节点。一般来说 Node 节点上会运行以下组件。

- 容器运行时主要负责容器的镜像管理以及容器创建及运行。
- Kubelet 负责维护 Pod 的生命周期，比如创建和删除 Pod 对应的容器。同时也负责存储和网络的管理。一般会配合 CSI、CNI 插件一起工作。
- Kube-Proxy 主要负责 Kubernetes 内部的服务通信，在主机上维护网络规则并提供转发及负载均衡能力。

除了上述这些核心组件外，通常我们还会在 Kubernetes 集群中部署一些 Add-on 组件，常见的有：

- CoreDNS 负责为整个集群提供 DNS 服务；
- Ingress Controller 为服务提供外网接入能力；
- Dashboard 提供 GUI 可视化界面；
- Fluentd + Elasticsearch 为集群提供日志采集、存储与查询等能力。

**Master 和 Node 的交互方式**

Kubernetes 中所有的状态都是采用上报的方式实现的。APIServer 不会主动跟 Kubelet 建立请求链接，所有的容器状态汇报都是由 Kubelet 主动向 APIServer 发起的。一旦启动 Kubelet 进程以后，它会主动向 APIServer 注册自己，这是 Kubernetes 推荐的 Node 管理方式。

一旦新增的 Node 被 APIServer 纳管进来后，Kubelet 进程就会定时向 APIServer 汇报“心跳”，即汇报自身的状态，包括自身健康状态、负载数据统计等。当一段时间内心跳包没有更新，那么此时 kube-controller-manager 就会将其标记为NodeLost（失联）。

# 03 | 集群搭建：手把手教你玩转 Kubernetes 集群搭建





![image (4).png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211224225510.png)

**常见的集群搭建方法**



**集群升级**







# 04 | 核心定义：Kubernetes 是如何搞定“不可变基础设施”的？



![image (19).png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211225151648.png)

**Pod 背后的设计理念**







# 05 | K8s Pod：最小调度单元的使用进阶及实践

# 部署高可用的业务

# 06 | 无状态应用：剖析 Kubernetes 业务副本及水平扩展底层原理

# 07 | 有状态应用：Kubernetes 如何通过 StatefulSet 支持有状态应用？

# 08 | 配置管理：Kubernetes 管理业务配置方式有哪些？

# 09 | 存储类型：如何挑选合适的存储插件？

# 10 | 存储管理：怎样对业务数据进行持久化存储？

# 11 | K8s Service：轻松搞定服务发现和负载均衡

# 12 | Helm Charts：如何在生产环境中释放部署生产力？

# 业务的日志与监控

# 13 | 服务守护进程：如何在 Kubernetes 中运行 DaemonSet 守护进程？

# 14 | 日志采集：如何在 Kubernetes 中做日志收集与管理？

# 15 | Prometheus：Kubernetes 怎样实现自动化服务监控告警？

# 16 | 迎战流量峰值：Kubernetes 怎样控制业务的资源水位？

# 17 | 案例实战：教你快速搭建 Kubernetes 监控平台

# 集群的安全性与稳定性

# 18 | 权限分析：Kubernetes 集群权限管理那些事儿

# 19 | 资源限制：如何保障你的 Kubernetes 集群资源不会被打爆

# 20 | 资源优化：Kubernetes 中有 GC（垃圾回收）吗？

# 21 | 优先级调度：你必须掌握的 Pod 抢占式资源调度

# 22 | 安全机制：Kubernetes 如何保障集群安全？

# 23 | 最后的防线：怎样对 Kubernetes 集群进行灾备和恢复？

# 底层核心原理及可扩展性

# 24 | 调度引擎：Kubernetes 如何高效调度 Pod？

# 25 | 稳定基石：带你剖析容器运行时以及 CRI 原理

# 26 | 网络插件：Kubernetes 搞定网络原来可以如此简单？

# 27 | K8s CRD：如何根据需求自定义你的 API？

# 28 | 面向 K8s 编程：如何通过 Operator 扩展 Kubernetes API？



