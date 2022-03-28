> 来自拉勾教育《Kubernetes 原理剖析与实战应用》--正范

模块四，安全无忧：集群的安全性与稳定性。

# 18 | 权限分析：Kubernetes 集群权限管理那些事儿

任何请求访问 Kubernetes 的 kube-apiserver 时，都要依次经历三个阶段：认证（Authentication，有时简写成 AuthN）、授权（Authorization，有时简写成 AuthZ）和准入控制（Admission Control）。

![image-20220328224657895](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202203282246983.png)

上述三个阶段，任何一个阶段验证失败都会导致该请求被拒绝访问，我们现在深入认识一下每个阶段。

**认证**

认证就是做身份校验，解决“你是谁？”的问题。这里我们简单介绍一下 Kubernetes 中几种常见的用户认证方式。

- x509 证书

  Kubernetes 集群各个组件间相互通信，都是基于 x509 证书进行身份校验的。比如使用openssl命令行工具生成一个证书签名请求（CSR）：

  ```shell
  openssl req -new -key zhangsan.pem -out zhangsan-csr.pem -subj "/CN=zhangsan/O=app1/O=app2"
  ```

  这条命令会使用用户名zhangsan生成一个 CSR，且它属于 "app1" 和 "app2" 两个用户组，然后我们使用 CA 证书根据这个 CSR 就可以签发出一对证书。当用这对证书去访问 APIServer 时，它拿到的用户就是zhangsan了。

- Token

  我们接着来看基于 Token 的验证方式，它又可以分为几种类型。

  第一种是用户自己提供的静态 Token；

  还有一种是ServiceAccount Token。当你创建一个 ServiceAccount 的时候，kube-controller-manager 会自动帮你创建出一个Secret来保存 Token，比如：

  ```shell
  $ kubectl create sa demo
  serviceaccount/demo created
  ➜  ~ kubectl get sa demo
  NAME   SECRETS   AGE
  demo   1         6s
  ➜  ~ kubectl describe sa demo
  Name:                demo
  Namespace:           default
  Labels:              <none>
  Annotations:         <none>
  Image pull secrets:  <none>
  Mountable secrets:   demo-token-fvsjg
  Tokens:              demo-token-fvsjg
  Events:              <none>
  ```

  可以看到这里自动创建了一个名为demo-token-fvsjg的 Secret，我们来查看一下其中的内容：

  ```shell
  $ kubectl get secret demo-token-fvsjg
  NAME               TYPE                                  DATA   AGE
  demo-token-fvsjg   kubernetes.io/service-account-token   3      27s
  $ kubectl describe secret demo-token-fvsjg
  Name:         demo-token-fvsjg
  Namespace:    default
  Labels:       <none>
  Annotations:  kubernetes.io/service-account.name: demo
                kubernetes.io/service-account.uid: f8fe4799-9add-4a36-8c29-a6b2744ba9a2
  Type:  kubernetes.io/service-account-token
  Data
  ====
  token:      eyJhbGciOi...
  ca.crt:     1025 bytes
  namespace:  7 bytes
  ```

**授权**

授权负责做权限管控，解决“你能干什么？”的问题。

Kubernetes 内部有多种授权模块，比如 Node、ABAC、RBAC、Webhook。授权阶段会根据从 AuthN 拿到的用户信息，依次按配置的授权次序逐一进行权限验证。任一授权模块验证通过，即允许该请求继续访问。

我们这里简要讲一下 ABAC 和 RBAC 这两种授权模式。

- ABAC

  ABAC (Attribute Based Access Control) 是一种基于属性的访问控制，可以给 APIServer 指定一个 JSON 文件--authorization-policy-file=SOME_FILENAME，该文件描述了一组属性组合策略，比如：

  ```json
  {
      "apiVersion": "abac.authorization.kubernetes.io/v1beta1", 
      "kind": "Policy", 
      "spec": {
          "user": "zhangsan", 
          "namespace": "*", 
          "resource": "pods", 
          "readonly": true
      }
  }
  ```

  这条策略表示，用户 zhangsan 可以以只读的方式读取任何 namespace 中的 Pod。

  不过在实际使用中，ABAC 使用得比较少，跟我们上面 AuthN 中提到的静态 Token 一样，不方便修改、更新，每次变更后都需要重启 APIServer。所以在实际使用中，RBAC 最常见，使用更广泛。

- RBAC

  相对而言，RBAC 使用起来就非常方便了，通过 Kubernetes 的对象就可以直接进行管理，也便于动态调整权限。

  RBAC 中引入了角色，所有的权限都是围着这个角色进行展开的，每个角色里面定义了可以操作的资源以及操作方式。在 Kubernetes 中有两种角色，一种是 namespace 级别的 Role，比如 Pod、Service，一种是集群级别的 ClusterRole，比如 Node、PV 等。

  我们来看个例子：

  ```yaml
  kind: Role
  apiVersion: rbac.authorization.k8s.io/v1
  metadata:
    namespace: default
    name: pod-reader
  rules:
  - apiGroups: [""] # 空字符串""表明使用core API group
    resources: ["pods"]
    verbs: ["get", "watch", "list"]
  ```

  这样一个角色表示可以访问 default 命名空间下面的 Pods，并可以对其进行 get、watch 以及 list 操作。

  ClusterRole 除了可以定义集群方位的资源外，比如 Node，还可以定义跨 namespace 的资源访问，比如你想访问所有命名空间下面的 Pod，就可以这么定义：

  ```yaml
  kind: ClusterRole
  apiVersion: rbac.authorization.k8s.io/v1
  metadata:
    # 鉴于ClusterRole是集群范围对象，所以这里不需要定义"namespace"字段
    name: pods-reader
  rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "watch", "list"]
  ```

**准入控制**

准入控制其实就是由一组控制逻辑级联而成，对对象进行拦截校验、更改等操作。

比如你打算在一个名为 test 的 namespace 中创建一个 Pod，如果这个 namespace 不存在，集群要不要自动创建出来？或者直接拒绝掉该请求？这些逻辑都可以通过准入控制进行配置。

准入控制可以帮助我们在 APIServer 真正处理对象前做一些校验以及修改的工作。

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







