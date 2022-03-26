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

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220321213117.png" alt="image (3).png" style="zoom:50%;" />

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

在 Kubernetes 中，一般有 ConfigMap 和 Secret 两种对象，可以用来做配置管理。

**ConfigMap**

首先我们来讲一下 ConfigMap 这个对象，它主要用来保存一些非敏感数据，可以用作环境变量、命令行参数或者挂载到存储卷中。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220323215028.png" alt="image-20220323215028302" style="zoom:50%;" />

ConfigMap 通过键值对来存储信息，是个 namespace 级别的资源。在 kubectl 使用时，我们可以简写成 cm。

我们来看一下两个 ConfigMap 的 API 定义：

```yaml
$ cat cm-demo-mix.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cm-demo-mix # 对象名字
  namespace: demo # 所在的命名空间
data: # 这是跟其他对象不太一样的地方，其他对象这里都是spec
  # 每一个键都映射到一个简单的值
  player_initial_lives: "3" # 注意这里的值如果是数字的话，必须用字符串来表示
  ui_properties_file_name: "user-interface.properties"
  # 也可以来保存多行的文本
  game.properties: |
    enemy.types=aliens,monsters
    player.maximum-lives=5
  user-interface.properties: |
    color.good=purple
    color.bad=yellow
    allow.textmode=true
$ cat cm-demo-all-env.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cm-demo-all-env
  namespace: demo
data:
  SPECIAL_LEVEL: very
  SPECIAL_TYPE: charm
```

可见，我们通过 ConfigMap 既可以存储简单的键值对，也能存储多行的文本。现在我们来创建这两个 ConfigMap：

```shell
$ kubectl create -f cm-demo-mix.yaml
configmap/cm-demo-mix created
$ kubectl create -f cm-demo-all-env.yaml
configmap/cm-demo-all-env created
```

下面我们看看怎么和 Pod 结合起来使用。在使用的时候，有几个地方需要特别注意：

- Pod 必须和 ConfigMap 在同一个 namespace 下面；
- 在创建 Pod 之前，请务必保证 ConfigMap 已经存在，否则 Pod 创建会报错。

```yaml
$ cat cm-demo-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: cm-demo-pod
  namespace: demo
spec:
  containers:
    - name: demo
      image: busybox:1.28
      command:
        - "bin/sh"
        - "-c"
        - "echo PLAYER_INITIAL_LIVES=$PLAYER_INITIAL_LIVES && sleep 10000"
      env:
        # 定义环境变量
        - name: PLAYER_INITIAL_LIVES # 请注意这里和 ConfigMap 中的键名是不一样的
          valueFrom:
            configMapKeyRef:
              name: cm-demo-mix         # 这个值来自 ConfigMap
              key: player_initial_lives # 需要取值的键
        - name: UI_PROPERTIES_FILE_NAME
          valueFrom:
            configMapKeyRef:
              name: cm-demo-mix
              key: ui_properties_file_name
      envFrom:  # 可以将 configmap 中的所有键值对都通过环境变量注入容器中
        - configMapRef:
            name: cm-demo-all-env
      volumeMounts:
      - name: full-config # 这里是下面定义的 volume 名字
        mountPath: "/config" # 挂载的目标路径
        readOnly: true
      - name: part-config
        mountPath: /etc/game/
        readOnly: true
  volumes: # 您可以在 Pod 级别设置卷，然后将其挂载到 Pod 内的容器中
    - name: full-config # 这是 volume 的名字
      configMap:
        name: cm-demo-mix # 提供你想要挂载的 ConfigMap 的名字
    - name: part-config
      configMap:
        name: cm-demo-mix
        items: # 我们也可以只挂载部分的配置
        - key: game.properties
          path: properties
```

在上面的这个例子中，几乎囊括了 ConfigMap 的几大使用场景：

- 命令行参数；
- 环境变量，可以只注入部分变量，也可以全部注入；
- 挂载文件，可以是单个文件，也可以是所有键值对，用每个键值作为文件名。

我们接着来创建：

```shell
$ kubectl create -f cm-demo-pod.yaml
pod/cm-demo-pod created
```

创建成功后，我们 exec 到容器中看看：

```shell
$ kubectl exec -it cm-demo-pod -n demo sh
kubectl exec [POD] [COMMAND] is DEPRECATED and will be removed in a future version. Use kubectl kubectl exec [POD] -- [COMMAND] instead.
/ # env
KUBERNETES_SERVICE_PORT=443
KUBERNETES_PORT=tcp://10.96.0.1:443
UI_PROPERTIES_FILE_NAME=user-interface.properties
HOSTNAME=cm-demo-pod
SHLVL=1
HOME=/root
SPECIAL_LEVEL=very
TERM=xterm
KUBERNETES_PORT_443_TCP_ADDR=10.96.0.1
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
KUBERNETES_PORT_443_TCP_PORT=443
KUBERNETES_PORT_443_TCP_PROTO=tcp
KUBERNETES_SERVICE_PORT_HTTPS=443
KUBERNETES_PORT_443_TCP=tcp://10.96.0.1:443
PLAYER_INITIAL_LIVES=3
KUBERNETES_SERVICE_HOST=10.96.0.1
PWD=/
SPECIAL_TYPE=charm
/ # ls /config/
game.properties            ui_properties_file_name
player_initial_lives       user-interface.properties
/ # ls -alh /config/
total 12
drwxrwxrwx    3 root     root        4.0K Aug 27 09:54 .
drwxr-xr-x    1 root     root        4.0K Aug 27 09:54 ..
drwxr-xr-x    2 root     root        4.0K Aug 27 09:54 ..2020_08_27_09_54_31.007551221
lrwxrwxrwx    1 root     root          31 Aug 27 09:54 ..data -> ..2020_08_27_09_54_31.007551221
lrwxrwxrwx    1 root     root          22 Aug 27 09:54 game.properties -> ..data/game.properties
lrwxrwxrwx    1 root     root          27 Aug 27 09:54 player_initial_lives -> ..data/player_initial_lives
lrwxrwxrwx    1 root     root          30 Aug 27 09:54 ui_properties_file_name -> ..data/ui_properties_file_name
lrwxrwxrwx    1 root     root          32 Aug 27 09:54 user-interface.properties -> ..data/user-interface.properties
/ # cat /config/game.properties
enemy.types=aliens,monsters
player.maximum-lives=5
/ # cat /etc/game/properties
enemy.types=aliens,monsters
player.maximum-lives=5
```

可以看到，环境变量都已经正确注入，对应的文件和目录也都挂载进来了。
在上面ls -alh /config/后，我们看到挂载的文件中存在软链接，都指向了..data目录下的文件。这样做的好处，是 kubelet 会定期同步检查已经挂载的 ConfigMap 是否是最新的，如果更新了，就是创建一个新的文件夹存放最新的内容，并同步修改..data指向的软链接。

一般我们只把一些非敏感的数据保存到 ConfigMap 中，敏感的数据就要保存到 Secret 中了。

**Secret**

我们可以用 Secret 来保存一些敏感的数据信息，比如密码、密钥、token 等。在使用的时候， 跟 ConfigMap 的用法基本保持一致，都可以用来作为环境变量或者文件挂载。

第一，类型是 kubernetes.io/dockerconfigjson 的 Secret。

我们先来创建一个 Secret 来保存访问私有容器仓库的身份信息：

```shell
$ kubectl create secret -n demo docker-registry regcred \
   --docker-server=yourprivateregistry.com \
   --docker-username=allen \
   --docker-password=mypassw0rd \
--docker-email=allen@example.com
 secret/regcred created
 $ kubectl get secret -n demo regcred
 NAME      TYPE                             DATA   AGE
 regcred   kubernetes.io/dockerconfigjson   1      28s
```

这里我们可以看到，创建出来的 Secret 类型是kubernetes.io/dockerconfigjson：

```shell
$ kubectl describe secret -n demo regcred
Name:         regcred
Namespace:    demo
Labels:       <none>
Annotations:  <none>
Type:  kubernetes.io/dockerconfigjson
Data
====
.dockerconfigjson:  144 bytes
```

我们用 base64 解压试试看：

```shell
$ kubectl get secret regcred -n demo --output="jsonpath={.data.\.dockerconfigjson}" | base64 --decode
{"auths":{"yourprivateregistry.com":{"username":"allen","password":"mypassw0rd","email":"allen@example.com","auth":"YWxsZW46bXlwYXNzdzByZA=="}}}
```

这实际上跟我们通过 docker login 后的~/.docker/config.json中的内容一样。

第二，Opaque类型的 Secret。

我们平时使用较为广泛的还有另外一种Opaque类型的 Secret：

```yaml
$ cat secret-demo.yaml
apiVersion: v1
kind: Secret
metadata:
  name: dev-db-secret
  namespace: demo
type: Opaque
data: # 这里的值都是 base64 加密后的
  password: UyFCXCpkJHpEc2I9
  username: ZGV2dXNlcg==
```

或者我们也可以通过如下等价的 kubectl 命令来创建出来：

```shell
$ kubectl create secret generic dev-db-secret -n demo \
  --from-literal=username=devuser \
  --from-literal=password='S!B\*d$zDsb='
```

或通过文件来创建对象，比如：

```shell
$ echo -n 'username=devuser' > ./db_secret.txt
$ echo -n 'password=S!B\*d$zDsb=' >> ./db_secret.txt
$ kubectl create secret generic dev-db-secret -n demo \
  --from-file=./db_secret.txt
```

有时候为了方便，你也可以使用stringData，这样可以避免自己事先手动用 base64 进行加密。

```shell
$ cat secret-demo-stringdata.yaml
apiVersion: v1
kind: Secret
metadata:
  name: dev-db-secret
  namespace: demo
type: Opaque
stringData:
  password: devuser
  username: S!B\*d$zDsb=
```

第三，下面我们在 Pod 中使用 Secret：

```yaml
$ cat pod-secret.yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-test-pod
  namespace: demo
spec:
  containers:
    - name: demo-container
      image: busybox:1.28
      command: [ "/bin/sh", "-c", "env" ]
      envFrom:
      - secretRef:
          name: dev-db-secret
  restartPolicy: Never
$ kubectl create -f pod-secret.yaml
pod/secret-test-pod created
```

创建成功后，我们来查看下：

```shell
$ kubectl get pod -n demo secret-test-pod
NAME              READY   STATUS      RESTARTS   AGE
secret-test-pod   0/1     Completed   0          14s
$ kubectl logs -f -n demo secret-test-pod
KUBERNETES_SERVICE_PORT=443
KUBERNETES_PORT=tcp://10.96.0.1:443
HOSTNAME=secret-test-pod
SHLVL=1
username=devuser
HOME=/root
KUBERNETES_PORT_443_TCP_ADDR=10.96.0.1
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
KUBERNETES_PORT_443_TCP_PORT=443
password=S!B\*d$zDsb=
KUBERNETES_PORT_443_TCP_PROTO=tcp
KUBERNETES_SERVICE_PORT_HTTPS=443
KUBERNETES_PORT_443_TCP=tcp://10.96.0.1:443
KUBERNETES_SERVICE_HOST=10.96.0.1
PWD=/
```

我们可以在日志中看到命令env的输出，看到环境变量username和password已经正确注入。

> 类似地，我们也可以将 Secret 作为 Volume 挂载到 Pod 内。

# 09 | 存储类型：如何挑选合适的存储插件？

**Kubernetes 中的 Volume 是如何设计的？**

Kubernetes 中 Volume 的生命周期是直接和 Pod 挂钩的。在 Pod 被删除时，才会对 Volume 进行解绑（unmount）、删除等操作。至于 Volume 中的数据是否会被删除，取决于Volume 的具体类型。

为了丰富可以对接的存储后端，Kubernetes 中提供了很多volume plugin可供使用。

![image-20220325222424963](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/20220325222425.png)

**常见的几种内置 Volume 插件**

这里我介绍几个日常工作和生产环境中经常使用到的几个插件。

- ConfigMap 和 Secret

- Downward API

  DownwardAPI 可以帮助你获取 Pod 对象中定义的字段，比如 Pod 的标签（Labels）、Pod 的 IP 地址及 Pod 所在的命名空间（namespace）等。Downward API 有两种使用方法，既支持环境变量注入，也支持通过 Volume 挂载。

  我们来看个 Volume 挂载的例子，如下是一个 Pod 的 yaml 文件：

  ```yaml
  $ cat downwardapi-volume-demo.yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: downwardapi-volume-demo
    namespace: demo
    labels:
      zone: us-east-coast
      cluster: downward-api-test-cluster1
      rack: rack-123
    annotations:
      annotation1: "345"
      annotation2: "456"
  spec:
    containers:
      - name: volume-test-container
        image: busybox:1.28
        command: ["sh", "-c"]
        args:
        - while true; do
            if [[ -e /etc/podinfo/labels ]]; then
              echo -en '\n\n'; cat /etc/podinfo/labels; fi;
            if [[ -e /etc/podinfo/annotations ]]; then
              echo -en '\n\n'; cat /etc/podinfo/annotations; fi;
            sleep 5;
          done;
        volumeMounts:
          - name: podinfo
            mountPath: /etc/podinfo
    volumes:
      - name: podinfo
        downwardAPI:
          items:
            - path: "labels"
              fieldRef:
                fieldPath: metadata.labels
            - path: "annotations"
              fieldRef:
                fieldPath: metadata.annotations
  ```

  我们先创建这个 Pod，并通过kubectl logs来查看它的输出日志：

  ```shell
  $ kubectl create -f downwardapi-volume-demo.yaml
  pod/downwardapi-volume-demo created
  $ kubectl get pod -n demo
  NAME                      READY   STATUS    RESTARTS   AGE
  downwardapi-volume-demo   1/1     Running   0          5s
  $ kubectl logs -n demo -f downwardapi-volume-demo
  
  cluster="downward-api-test-cluster1"
  rack="rack-123"
  zone="us-east-coast"
  
  annotation1="345"
  annotation2="456"
  kubernetes.io/config.seen="2020-09-03T12:01:58.1728583Z"
  kubernetes.io/config.source="api"
  
  cluster="downward-api-test-cluster1"
  rack="rack-123"
  zone="us-east-coast"
  
  annotation1="345"
  annotation2="456"
  kubernetes.io/config.seen="2020-09-03T12:01:58.1728583Z"
  kubernetes.io/config.source="api"
  ```

  从上面的日志输出，我们可以看到 Downward API 可以通过 Volume 挂载到 Pod 里面，并被容器获取。

- EmptyDir

  在 Kubernetes 中，我们也可以使用临时存储，类似于创建一个 temp dir。我们将这种类型的插件叫作 EmptyDir，从名字就可以知道，在刚开始创建的时候，就是空的临时文件夹。在 Pod 被删除后，也一同被删除，所以并不适合保存关键数据。

  在使用的时候，可以参照如下的方式使用 EmptyDir：

  ```yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: empty-dir-vol-demo
    namespace: demo
  spec:
    containers:
    - image: busybox:1.28
      name: volume-test-container
      volumeMounts:
      - mountPath: /cache
        name: cache-volume
    volumes:
    - name: cache-volume
      emptyDir: {}
  ```

  一般来说，EmptyDir 可以用来做一些临时存储，比如为耗时较长的计算任务存储中间结果或者作为共享卷为同一个 Pod 内的容器提供数据等等。

- HostPath

  我们再来看 HostPath，它和 EmptyDir 一样，都是利用宿主机的存储为容器分配资源。但是两者有个很大的区别，就是 HostPath 中的数据并不会随着 Pod 被删除而删除，而是会持久地存放在该节点上。

  下面是一个使用 HostPath 的例子：

  ```yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: hostpath-demo
    namespace: demo
  spec:
    containers:
    - image: nginx:1.19.2
      name: container-demo
      volumeMounts:
        - mountPath: /test-pd
          name: hostpath-volume
    volumes:
    - name: hostpath-volume 
      hostPath:
        path: /data  # 对应宿主机上的绝对路径
        type: Directory # 可选字段，默认是 Directory
  ```

上述介绍的这几款插件，目前依然能够照常使用，也是社区自身稳定支持的插件。但是对于一些云厂商和第三方的插件，社区已经不推荐继续使用内置的方式了，而是推荐你通过 CSI（Container Storage Interface，容器存储接口）来使用这些插件。

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







