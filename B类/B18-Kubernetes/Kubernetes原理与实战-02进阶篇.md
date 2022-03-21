> 来自拉勾教育《Kubernetes 原理剖析与实战应用》--正范

模块二，Kubernetes进阶：部署高可用的业务。

# 06 | 无状态应用：剖析 Kubernetes 业务副本及水平扩展底层原理

单独地用一个 Pod 来承载业务，是没办法保证高可用、可伸缩、负载均衡等要求。这时我们就需要在 Pod 之上做一层抽象，通过多个副本（Replica）来保证可用 Pod 的数量，避免业务不可用。

在介绍 Kubernetes 中对这种抽象的实现之前，我们先来看看应用的业务类型。

**有状态服务 VS 无状态服务**

一般来说，业务的服务类型可分为无状态服务和有状态服务。判断两种请求的关键在于，两个来自相同发起者的请求在服务器端是否具备上下文关系。

- 如果是有状态服务，其请求是状态化的，服务器端需要保存请求的相关信息，这样每个请求都可以默认地使用之前的请求上下文。
- 而无状态服务就不需要这样，每次请求都包含了需要的所有信息，每次请求都和之前的没有任何关系。

**Kubernetes 中的无状态工作负载**

Kubernetes 中各个对象的 metadata 字段都有 label（标签）和 annotation（注解） 两个对象，可以用来标识一些元数据信息。

- annotation 主要用来记录一些非识别的信息，并不用于标识和选择对象。
- label 主要用来标识一些有意义且和对象密切相关的信息，用来支持 labelSelector（标签选择器）以及一些查询操作，还有选择对象。

**ReplicaSet**

社区开发了下一代的 Pod 控制器 ReplicaSet（可简写为 rs） 用来替代 ReplicaController。ReplicaSet 具备更强大的基于集合的标签选择器，目前支持三种操作符：in、notin和exists。

例如，你可以用environment in (production, qa)来匹配 label 中带有environment=production或environment=qa的 Pod。

了解了标签选择器，我们就可以通过如下的 kubectl 命令查找 Pod：

```shell
kubectl get pods -l environment=production,tier=frontend
```

或者使用：

```shell
kubectl get pods -l 'environment in (production),tier in (frontend)'
```

虽然 Replicaset 可以独立使用，但是为了能够更好地协调 Pod 的创建、删除以及更新等操作，我们都是直接使用更高级的 Deployment来管理 Replicaset。

**Deployment**

通过 Deployment，我们就不需要再关心和操作 ReplicaSet 了。

![image (3).png](https://gitee.com/yanglu_u/img2022/raw/master/learn/20220321213117.png)

Deployment、ReplicaSet 和 Pod 这三者之间的关系见上图。我们来看一个定义 Deployment 的例子：

```yaml
$ cat deploy-demo.yaml 
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment-demo
  namespace: demo
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
        version: v1
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
```

我们这里定义了副本数 spec.replicas 为 3，同时在 spec.selector.matchLabels 中设置了 app=nginx 的 label，用于匹配 spec.template.metadata.labels 的 label。我们还增加了 version=v1 的 label 用于后续滚动升级做比较。

> 注意，spec.selector.matchLabels 中写的 label 一定要能匹配得了 spec.template.metadata.labels 中的 label。否则该 Deployment 无法关联创建出来的 ReplicaSet。

# 07 | 有状态应用：Kubernetes 如何通过 StatefulSet 支持有状态应用？

这节课，我们从一个具体的例子来逐渐了解、认识 StatefulSet。在 kubectl 命令行中，我们一般将 StatefulSet 简写为 sts。在部署一个 StatefulSet 的时候，有个前置依赖对象，即 Service（服务）。

我们先看如下一个 Service：

```yaml
$ cat nginx-svc.yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-demo
  namespace: demo
  labels:
    app: nginx
spec:
  clusterIP: None
  ports:
  - port: 80
    name: web
  selector:
    app: nginx
```

上面这段 yaml 的意思是，在 demo 这个命名空间中，创建一个名为 nginx-demo 的服务，这个服务暴露了 80 端口，可以访问带有app=nginx这个 label 的 Pod。

我们现在利用上面这段 yaml 在集群中创建出一个 Service：

```shell
$ kubectl create ns demo
$ kubectl create -f nginx-svc.yaml
service/nginx-demo created
$ kubectl get svc -n demo
NAME         TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)   AGE
nginx-demo   ClusterIP   None             <none>        80/TCP    5s
```

创建好了这个前置依赖的 Service，下面我们就可以开始创建真正的 StatefulSet 对象，可参照如下的 yaml 文件：

```yaml
$ cat web-sts.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web-demo
  namespace: demo
spec:
  serviceName: "nginx-demo"
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.19.2-alpine
        ports:
        - containerPort: 80
          name: web
$ kubectl create -f web-sts.yaml
$ kubectl get sts -n demo
NAME       READY   AGE
web-demo   0/2     9s
```

可以看到，到这里我已经将名为 web-demo 的 StatefulSet 部署完成了。下面我们来一点点探索 StatefulSet 的秘密，看看它有哪些特性，为何可以保障服务有状态的运行。

**StatefulSet 的特性**

通过 kubectl 的watch功能（命令行加参数-w），我们可以观察到 Pod 状态的一步步变化。

```shell
$ kubectl get pod -n demo -w
NAME         READY   STATUS              RESTARTS   AGE
web-demo-0   0/1     ContainerCreating   0          18s
web-demo-0   1/1     Running             0          20s
web-demo-1   0/1     Pending             0          0s
web-demo-1   0/1     Pending             0          0s
web-demo-1   0/1     ContainerCreating   0          0s
web-demo-1   1/1     Running             0          2s
```

通过 StatefulSet 创建出来的 Pod 名字有一定的规律，即`$(statefulset名称)-$(序号)`，比如这个例子中的web-demo-0、web-demo-1。

特性一：对于一个拥有 N 个副本的 StatefulSet 来说，Pod 在部署时按照 {0 …… N-1} 的序号顺序创建的，而删除的时候按照逆序逐个删除。

接着我们来看，StatefulSet 创建出来的 Pod 都具有固定的、且确切的主机名，并且会为每个 Pod 创建一个 DNS 域名，这个域名的格式为`$(podname).(headless service name)`。

我们通过kubectl run在同一个命名空间demo中创建一个名为 dns-test 的 Pod，同时 attach 到容器中，类似于docker run -it --rm这个命令。

```shell
$ kubectl run -it --rm --image busybox:1.28 dns-test -n demo
If you don't see a command prompt, try pressing enter.

/ # nslookup web-demo-0.nginx-demo
Server:    10.96.0.10
Address 1: 10.96.0.10 kube-dns.kube-system.svc.cluster.local
Name:      web-demo-0.nginx-demo
Address 1: 10.244.0.39 web-demo-0.nginx-demo.demo.svc.cluster.local

/ # nslookup web-demo-1.nginx-demo
Server:    10.96.0.10
Address 1: 10.96.0.10 kube-dns.kube-system.svc.cluster.local
Name:      web-demo-1.nginx-demo
Address 1: 10.244.0.40 web-demo-1.nginx-demo.demo.svc.cluster.local
```

我们现在删除一下这些 Pod，看看会有什么变化：

```shell
$ kubectl delete pod -l app=nginx -n demo
pod "web-demo-0" deleted
pod "web-demo-1" deleted
$ kubectl get pod -l app=nginx -n demo -o wide
NAME         READY   STATUS    RESTARTS   AGE   IP            NODE     NOMINATED NODE   READINESS GATES
web-demo-0   1/1     Running   0          15s   10.244.0.50   kraken   <none>           <none>
web-demo-1   1/1     Running   0          13s   10.244.0.51   kraken   <none>           <none>
```

特性二：删除成功后，可以发现 StatefulSet 立即生成了新的 Pod，但是 Pod 名称维持不变。唯一变化的就是 IP 发生了改变。

特性三：对于有状态的服务来说，每个副本都会用到持久化存储，且各自使用的数据是不一样的。

StatefulSet 通过 PersistentVolumeClaim（PVC）可以保证 Pod 的存储卷之间一一对应的绑定关系。同时，删除 StatefulSet 关联的 Pod 时，不会删除其关联的 PVC。

**如何更新升级 StatefulSet**

在 StatefulSet 中，支持两种更新升级策略，即 RollingUpdate 和 OnDelete。

- RollingUpdate策略是默认的更新策略。可以实现 Pod 的滚动升级，跟我们上一节课中 Deployment 介绍的 RollingUpdate 策略一样。

  比如我们这个时候做了镜像更新操作，那么整个的升级过程大致如下，先逆序删除所有的 Pod，然后依次用新镜像创建新的 Pod 出来。这里你可以通过`kubectl get pod -n demo -w -l app=nginx`来动手观察下。

- 当你把更新策略设置为 OnDelete 时，我们就必须手动先删除 Pod，才能触发新的 Pod 更新。

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







