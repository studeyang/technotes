# 01 | KubeShpere全景图

![](./KubeShpere_view.png)

7大功能。

**1. 多租户管理**

集群：F2B、电商

企业空间：

项目：团队（组）
对应的是 k8s 的 namespace

集群（cluster） > 企业空间（workspace） > 项目

**2. 工作负载**

部署（Deployment）

有状态副本集（StatefulSet）

守护进程集（DeamonSet）

任务（Job）

定时任务（CronJob）

**3. 执行化存储卷**



**4. 服务与网络**

通过服务（Service）、应用路由（Ingress）来暴露服务。

**5. 配置中心**

Secret、ConfigMap

**6. DevOps 工程资源**

CI/CD流水线

**7. 监控中心**

从不同视角进行监控：集群、企业空间、项目、工作负载（容器组）、容器。

# 02 | 发布一个服务

首先进入到 Project 下，创建Secret/ConfigMap -> Application - Deploy New Application ->  填写环境变量。

- 如何连接云上的 K8S？









