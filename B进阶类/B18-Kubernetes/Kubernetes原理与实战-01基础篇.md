> 来自拉勾教育《Kubernetes 原理剖析与实战应用》--正范

模块一，云原生基石：初识 Kubernetes。

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

# 01 | 前世今生：Kubernetes 是如何火起来的？

Kubernetes 的前世今生要从“云计算”的兴起开始讲起。

**云计算平台**

我们可以将经典的云计算架构分为三大服务层：也就是 IaaS（Infrastructure as a Service，基础设施即服务）、PaaS（Platform as a Service，平台即服务）和 SaaS（Software as a Service，软件即服务）。

- IaaS 层通过虚拟化技术提供计算、存储、网络等基础资源，可以在上面部署各种 OS 以及应用程序。开发者可以通过云厂商提供的 API 控制整个基础架构，无须对其进行物理上的维护和管理。
- PaaS 层提供软件部署平台（runtime），抽象掉了硬件和操作系统，可以无缝地扩展（scaling）。开发者只需要关注自己的业务逻辑，不需要关注底层。
- SaaS 层直接为开发者提供软件服务，将软件的开发、管理、部署等全部都交给第三方，用户不需要再关心技术问题，可以拿来即用。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211222222908.png" alt="Drawing 0.png" style="zoom: 67%;" />

对应到我们生活中，可以想象自己要去一个地方旅行，那么首先就需要解决住的问题。

IaaS 服务就相当于直接在当地购买了一套商品房，像搭建系统、维护运行环境这种“装修”的事情就必须由我们自己来，但优点是“装修风格”可以自己定。

PaaS 则要简单一点，我们到了一个陌生的城市，可以选择住民宿或青旅，这样就不需要考虑装修和买家具的事情了，系统和环境都是现成的，我们只需要安装自己的运行程序就可以了。

SaaS 就更简单了，相当于直接住酒店，一切需求都由供应商搞定了，我们只需要选择自己喜欢的房间风格和户型就可以了，这时从操作系统到运行的具体软件都不再需要我们自己操心了。

那么我们该如何让系统上云呢？

**Docker**

Docker 镜像解决了环境打包的问题，它直接打包了应用运行所需要的整个“操作系统”，而且不会出现任何兼容性问题，它赋予了本地环境和云端环境无差别的能力。

有了 Docker，开发人员可以轻松地将其生产环境复制为可立即运行的容器应用程序，让工作更有效率。我们来看看CNCF （Cloud Native Computing Foundation，云计算基金会）在2019年做的调研报告。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211222225533.png" alt="Drawing 6.png" style="zoom:67%;" />

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

Borg 用 Cell 来定义一组机器资源。Cluster 即集群，一个数据中心可以同时运行一个或者多个集群，每个集群又可以有多个 Cell。

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

# 04 | 核心定义：Kubernetes 是如何搞定“不可变基础设施”的？

CNCF 官方是这样定义云原生的：云原生的代表技术包括容器、服务网格、微服务、不可变基础设施和声明式API。

那么这个不可变基础设施到底是什么含义？

**怎么理解不可变基础设施？**

这里的基础设施，我们可以理解为服务器、虚拟机或者是容器。不可变基础设施是指，部署完成以后，便成为一种只读状态，不可对其进行任何更改。如果需要更新或修改，就使用新的环境或服务器去替代旧的。

不可变基础设施带来了更一致、更可靠、更可预测的设计理念，可以缓解或完全避免可变基础设施中遇到的各种常见问题。

Kubernetes 中的不可变基础设施就是 Pod。

**Pod 是什么？**

Pod 由一个或多个容器组成，如下图所示。Pod 中的容器不可分割，会作为一个整体运行在一个 Node 节点上，也就是说 Pod 是你在 Kubernetes 中可以创建和部署的最原子化的单位。

![image (19).png](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211225151648.png)

> 通常来说，如果在一个 Pod 内有多个容器，那么这几个容器最好是密切相关的，且可以共享一些资源的，比如网络、存储等。

**Pod 背后的设计理念**

看完上面 Pod 的存在形式，你也许会有下面两个疑问。

1、为什么 Kubernetes 不直接管理容器，而用 Pod 来管理呢？

因为使用一个新的逻辑对象 Pod 来管理容器，可以在不重载容器信息的基础上，添加更多的属性，而且也方便跟容器运行时进行解耦，兼容度高。比如：

- 存活探针（Liveness Probe）；
- 容器启动后和终止前可以进行的操作，比如，在容器停止前，可能需要做一些清理工作，或者不能马上结束进程；
- 定义了容器终止后要采取的策略，比如始终重启、正常退出才重启等；

2、为什么要允许一个 Pod 内可以包含多个容器？

第一，用一个 Pod 管理多个容器，既能够保持容器之间的隔离性，还能保证相关容器的环境一致性。第二，使用粒度更小的容器，不仅可以使应用间的依赖解耦，还便于使用不同技术栈进行开发，同时还可以方便各个开发团队复用，减少重复造轮子。

**如何声明一个 Pod？**

在 Kubernetes 中，所有对象都可以通过一个相似的 API 模板来描述，即元数据 （metadata）、规范（spec）和状态（status）。

- 元数据（metadata）

  metadata 中一般要包含如下 3 个对该对象至关重要的元信息：namespace（命名空间）、name（对象名）和 uid（对象 ID）。

  namespace 主要用于逻辑上的隔离，Kubernetes 中有几个内置的 namespace 有：default，kube-system，kube-public，kube-node-lease。

  name 就是用来标识对象的名称，在 namespace 内具有唯一性，在不同的 namespace 下，可以创建相同名字的对象。

  uid 是由系统自动生成的，主要用于 Kubernetes 内部标识使用，比如某个对象经历了删除重建，单纯通过名字是无法判断该对象的新旧，这个时候就可以通过 uid 来进行唯一确定。

- 规范 （Spec）

  在 Spec 中描述了该对象的详细配置信息，即用户希望的状态（Desired State）。

- 状态（Status）

  在 Kubernetes 中，不同组件之间进行信息同步，就可以通过 status 进行。像 Node 的 status 就记录了该节点的一些状态信息，其他的控制器，就可以通过 status 知道该 Node 的情况，做一些操作，比如节点宕机修复、可分配资源等。

**一个 Pod 的真实例子**

下面是一个 Pod 的 Yaml 定义：

```yaml
apiVersion: v1 #指定当前描述文件遵循v1版本的Kubernetes API
kind: Pod #我们在描述一个pod
metadata:
  name: twocontainers #指定pod的名称
  namespace: default #指定当前描述的pod所在的命名空间
  labels: #指定pod标签
    app: twocontainers
  annotations: #指定pod注释
    version: v0.5.0
    releasedBy: david
    purpose: demo
spec:
  containers:
  - name: sise #容器的名称
    image: quay.io/openshiftlabs/simpleservice:0.5.0 #创建容器所使用的镜像
    ports:
    - containerPort: 9876 #应用监听的端口
  - name: shell #容器的名称
    image: centos:7 #创建容器所使用的镜像
    command: #容器启动命令
      - "bin/bash"
      - "-c"
      - "sleep 10000"
```

你可以通过 kubectl 命令在集群中创建这个 Pod。

```shell
$ kubectl create -f ./twocontainers.yaml
$ kubectl get pods
NAME                      READY     STATUS    RESTARTS   AGE
twocontainers             2/2       Running   0          7s
```

等该 Pod 运行成功后，我们可以通过 exec 进入 shell 这个容器，来访问 sise 服务：

```shell
$ kubectl exec twocontainers -c shell -i -t -- bash
[root@twocontainers /]# curl -s localhost:9876/info
{"host": "localhost:9876", "version": "0.5.0", "from": "127.0.0.1"}
```

# 05 | K8s Pod：最小调度单元的使用进阶及实践

在实际生产使用的过程中，通过 kubectl 可以很方便地部署一个 Pod。但是 Pod 运行过程中还会出现一些意想不到的问题，比如：

- Pod 里的某一个容器异常退出了怎么办？
- 如何知道业务的真实运行情况，比如容器运行正常，但是业务不工作了？
- 容器在启动或删除前后，如果需要做一些特殊处理怎么办？比如做一些清理工作。
- 如果容器所在节点宕机，重启后会对你的容器产生影响吗？

在了解 Pod 的高阶用法之前，我们先聊聊 Pod 的运行状态。

**Pod 的运行状态**

我们先回到上一节 04 课时中的例子：

```yaml
apiVersion: v1 #指定当前描述文件遵循v1版本的Kubernetes API
kind: Pod #我们在描述一个pod
metadata:
  name: twocontainers #指定pod的名称
  namespace: default #指定当前描述的pod所在的命名空间
  labels: #指定pod标签
    app: twocontainers
  annotations: #指定pod注释
    version: v1
    releasedBy: david
    purpose: demo
spec:
  containers:
  - name: sise #容器的名称
    image: quay.io/openshiftlabs/simpleservice:0.5.0 #创建容器所使用的镜像
    ports:
    - containerPort: 9876 #应用监听的端口
  - name: shell #容器的名称
    image: centos:7 #创建容器所使用的镜像
    command: #容器启动命令
      - "bin/bash"
      - "-c"
      - "sleep 10000"
```

我们通过 kubectl 创建 Pod 成功后，可以通过如下命令看到 Pod 的状态:

```shell
# 注：我们这里使用了 kubectl 命令行 JSONPATH 模板能力
$ kubectl get pod twocontainers -o=jsonpath='{.status.phase}'
Running
```

你也可以使用 kubectl get 命令来查看容器的状态：

```shell
$ kubectl get pod twocontainers
NAME            READY   STATUS    RESTARTS   AGE
twocontainers   2/2     Running   0          2m
```

Pod 的 Status 有：

- Pending：一般来说，处于Pending状态的 Pod，不外乎以下 2 个原因，Pod 还未被调度；Pod 内的容器镜像在待运行的节点上不存在，需要从镜像中心拉取。
- Running
- Succeeded：表示 Pod 内的所有容器均成功运行结束，即正常退出，退出码为 0；
- Failed：表示 Pod 内的所有容器均运行终止，且至少有一个容器终止失败了，一般这种情况，都是由于容器运行异常退出，或者被系统终止掉了；
- Unknown：一般是由于 Node 失联导致的 Pod 状态无法获取到。

既然 Pod 内的容器会出现异常退出状态，那么有没有一些重启策略可以让 Kubelet 对容器进行重启呢？

**Pod 的重启策略**

Kubernetes 中定义了如下三种重启策略，可以通过spec.restartPolicy字段在 Pod 定义中进行设置。

- Always 表示一直重启，这也是默认的重启策略。Kubelet 会定期查询容器的状态，一旦某个容器处于退出状态，就对其执行重启操作；
- OnFailure 表示只有在容器异常退出，即退出码不为 0 时，才会对其进行重启操作；
- Never 表示从不重启；

虽然我们可以设置一些重启策略，确保容器异常退出时可以重启。但是对于运行中的容器，是不是就意味着容器内的服务正常了呢？

**Pod 中的健康检查**

为此，Kubernetes 中提供了一系列的健康检查，可以定制调用，来帮助解决类似的问题，我们称之为 Probe（探针）。目前有如下三种 Probe：

- livenessProbe：可以用来探测容器是否真的在“运行”，即“探活”。如果检测失败的话，这个时候 kubelet 就会停掉该容器，容器的后续操作会受到其重启策略的影响。
- readinessProbe：常常用于指示容器是否可以对外提供正常的服务请求，即“就绪”，比如 nginx 容器在 reload 配置的时候无法对外提供 HTTP 服务。
- startupProbe：则可以用于判断容器是否已经启动好。

如果某个 Probe 没有设置的话，我们默认其是成功的。为了简化一些通用的处理逻辑，Kubernetes 也为这些 Probe 内置了如下三个 Handler：

- ExecAction：可以在容器内执行 shell 脚本；
- HTTPGetAction：方便对指定的端口和 IP 地址执行 HTTP Get 请求；
- TCPSocketAction：可以对指定端口进行 TCP 检查；

> 注：对于每一种 Probe，Kubelet 只会执行其中一种 Handler。如果你定义了多个 Handler，则会按照 Exec、HTTPGet、TCPSocket 的优先级顺序，选择第一个定义的 Handler。

下面我们通过一个例子，来了解这三个 Probe 的工作流程。

```shell
apiVersion: v1
kind: Pod
metadata:
  name: probe-demo
  namespace: demo
spec:
  containers:
  - name: sise
    image: quay.io/openshiftlabs/simpleservice:0.5.0
    ports:
    - containerPort: 9876
    readinessProbe:
      tcpSocket:
        port: 9876
      periodSeconds: 10
    livenessProbe:
      periodSeconds: 5
      httpGet:
        path: /health
        port: 9876
    startupProbe:
      httpGet:
        path: /health
        port: 9876
      failureThreshold: 3
      periodSeconds: 2
```

在平常使用中，建议你对全部服务同时设置 readiness 和 liveness 的健康检查。

除了健康检查以外，我们有时候在容器退出前要做一些清理工作，此时我们就需要一个 hook（钩子程序）来帮助我们达到这个目的了。

**容器生命周期内的 hook**

目前在 Kubernetes 中，有如下两种 hook。

- PostStart：可以在容器启动之后就执行。但需要注意的是，此 hook 和容器里的 ENTRYPOINT 命令的执行顺序是不确定的。
- PreStop 则在容器被终止之前被执行，是一种阻塞式的方式。执行完成后，Kubelet 才真正开始销毁容器。

同上面的 Probe 一样，hook 也有类似的 Handler：

- Exec：用来执行 Shell 命令；
- HTTPGet：可以执行 HTTP 请求。

我们来看个例子：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: lifecycle-demo
  namespace: demo
spec:
  containers:
  - name: lifecycle-demo-container
    image: nginx:1.19
    lifecycle:
      postStart:
        exec:
          command: ["/bin/sh", "-c", "echo Hello from the postStart handler > /usr/share/message"]
      preStop:
        exec:
          command: ["/usr/sbin/nginx","-s","quit"]
```

可以看出来，我们可以借助preStop以优雅的方式停掉 Nginx 服务，从而避免强制停止容器，造成正在处理的请求无法响应。

**init 容器**

在 Kubernetes 中还有一种特殊的容器，即 init 容器。这个容器工作在正常容器（为了方便区分，我们这里称为应用容器）启动之前，通常用来做一些初始化工作，比如环境检测、OSS 文件下载、工具安装，等等。

我们来看一个 Init 容器的例子：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
  namespace: demo
  labels:
    app: myapp
spec:
  containers:
  - name: myapp-container
    image: busybox:1.31
    command: [‘sh’, ‘-c’, ‘echo The app is running! && sleep 3600‘]
  initContainers:
  - name: init-myservice
    image: busybox:1.31
    command: ['sh', '-c', 'until nslookup myservice; do echo waiting for myservice; sleep 2; done;']
  - name: init-mydb
    image: busybox:1.31
    command: ['sh', '-c', 'until nslookup mydb; do echo waiting for mydb; sleep 2; done;']
```

在 myapp-container 启动之前，它会依次启动 init-myservice、init-mydb，分别来检查依赖的服务是否可用。

