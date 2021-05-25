> 来源：https://tech.meituan.com/2021/05/20/shepherd-api-gateway.html

# 01 | 背景介绍

**1.1 API 网关是什么？**

API网关是运行于外部请求与内部服务之间的一个流量入口，实现对外部请求的协议转换、鉴权、流控、参数校验、监控等通用功能。

**1.2 为什么要做 Shepherd API 网关** 

为美团提供高性能、高可用、可扩展的统一API网关解决方案，让业务研发人员通过配置的方式即可对外开放功能和数据。

![image-20210524213716338](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210524213716.png)

目前接入 Shepherd API 网关的 API 数量超过18000多个，线上运行的集群数量90多个，日均总调用次数在百亿以上。

**1.3 使用 Shepherd 带来的收益是什么？** 

- 提升研发效率
- 降低沟通成本
- 提升资源利用率

# 02 | 技术设计与实现

**2.1 整体架构**

![image-20210524214038571](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210524214038.png)

- 控制面

  包括管理平台（完成 API 的全生命周期管理）和监控中心（完成 API 请求监控数据的收集和业务告警功能）。

  ![image-20210524214931388](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210524214931.png)

- 配置中心

  完成控制面与数据面的信息交互。配置中心存放 API 的相关配置信息。

  ![image-20210524215822291](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210524215822.png)

- 数据面

  泛化后端服务，响应结果。

  提供了 API 路由、功能组件集成、协议转换和服务调用。

**2.2 高可用设计**

- 排除性能隐患

  QPS 达 15000 以上。

- 服务隔离

  支持集群隔离、请求隔离（快慢线程池隔离）。

- 稳定性保障

  保障手段有：流量管控、请求缓存、超时管理、熔断降级。

- 请求安全

  集成了安全相关的系统组件。

- 可灰度

- 监控告警

  提供立体化监控、多维度告警功能。

- 故障自愈

  支持根据 CPU 指标进行扩缩容，还支持摘除问题节点。

- 可迁移

**2.3 易用性设计**

自动生成 DSL、API 操作提效。

**2.4 可扩展性设计**

- 自定义组件

  ![image-20210524223321317](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210524223321.png)

- 服务编排

  ![image-20210524223640090](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210524223640.png)

