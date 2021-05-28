# 01 | 背景介绍

**1.1 API 网关是什么？**

API网关是运行于外部请求与内部服务之间的一个流量入口，实现对外部请求的协议转换、鉴权、流控、参数校验、监控等通用功能。

总结来说，网关主要解决两个问题：第一，统一 API 的管理；第二，整合微服务的重复功能；

**1.2 为什么要做 Shepherd API 网关** 

主要原因有三点。

1、提高研发效率：在没有 Shepherd API 网关之前，美团业务研发人员如果要对外一个 HTTP API 接口，通常要先完成基础的鉴权、限流、日志监控、参数校验、协议转换等工作，同时需要维护代码逻辑，研发效率相对较低。

2、降低沟通成本：有了 Shepherd API 网关之后，业务研发人员配置好 API，可以自动生成 API 的前后端交互文档和客户端 SDK，方便前后端开发人员进行交互、联调。

3、提升资源利用率：这点怎么理解？像基础的鉴权、限流、日志监控、参数校验、协议转换等工作，如果每个 Web 应用都需要维护机器、配置、数据库，资源利用率非常差。

为美团提供高性能、高可用、可扩展的统一 API 网关解决方案，让业务研发人员通过配置的方式即可对外开放功能和数据。

![image-20210524213716338](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210524213716.png)

目前接入 Shepherd API 网关的 API 数量超过18000多个，线上运行的集群数量90多个，日均总调用次数在百亿以上。

# 02 |  整体架构

![image-20210524214038571](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210524214038.png)

**2.1 控制面**

包括管理平台（完成 API 的全生命周期管理）和监控中心（完成 API 请求监控数据的收集和业务告警功能）。

![image-20210528161002496](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210528161002.png)

业务研发人员从创建 API 开始，完成参数录入、DSL 脚本生成；接着可以通过文档和 MOCK 功能进行 API 测试；

API 测试完成后，为了保证上线稳定性，Shepherd 管理平台提供了发布审批、灰度上线、版本回滚等一系列安全保证措施；

到这两步会监控 API 的调用失败情况、记录请求日志，一旦发现异常及时发出告警；

最后，对于不再使用的 API 进行下线操作后，会回收 API 所占用的各类资源并等待重新启用。

**2.2 配置中心**

配置中心是用来完成控制面与数据面的信息交互。存放的是 API 的配置信息，这些配置信息是使用 DSL 领域专用语言来描述。DSL 语言所描述的 API 如下所示。

![image-20210528161104176](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210528161104.png)

- Filters：API 使用到的功能组件；
- Request：请求的域名、路径、参数等信息；
- Response：响应的结果如异常处理、Header、Cookies 信息；
- Invokers：后端服务（RPC/HTTP/Function）的请求规则；
- FilterConfigs：API 使用到的功能组件的配置信息；

**2.3 数据面**

泛化后端服务，响应结果。

当请求流量命中API请求路径进入服务端，具体处理逻辑由DSL中配置的一系列功能组件完成。

![image-20210528161202370](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210528161202.png)

当请求流量进入 Shepherd 服务端，具体处理逻辑由 API DSL 中配置的一系列功能组件完成。网关提供了 API 路由、功能组件集成、协议转换和服务调用。

API 路由的实现：

![image-20210528161248763](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210528161248.png)

API 调用的最后一步，就是协议转换以及服务调用了。

![image-20210528161334312](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210528161334.png)

# 03 | 高性能设计

**3.1 性能优化**

Shepherd对API请求做了全异步化处理：

![image-20210525224516711](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210525224516.png)

QPS 为 2000。

性能优化一：打开 Nginx 与 Web 应用之间的长连接，性能提升到了 10000 以上。

性能优化二：对 Shepherd 服务进行 API 请求预热，减少主链路的本地日志打印，QPS 再次提升 30% 即 13000。

性能优化三：将 Jetty 容器替换为 Netty 网络框架，QPS 再提升 10% 达 15000 以上。

![image-20210525225358258](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210525225358.png)

# 04 | 高可用设计

**4.1 服务隔离**

服务隔离类型有两种：

一种是按业务线维度进行集群隔离。另一种是服务节点维度，快慢线程池隔离主要用于一些使用了同步阻塞组件的 API，例如 SSO 鉴权、自定义鉴权等，可能导致长时间阻塞共享业务线程池。

![image-20210525225614915](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210525225614.png)

快慢隔离的原理是统计 API 请求的处理时间，将请求处理耗时较长，超过容忍阈值的 API 请求隔离到慢线程池，避免影响其他正常 API 的调用。

![image-20210528142824419](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210528142824.png)

**4.2 稳定性保障**

保障手段有：流量管控、请求缓存、超时管理、熔断降级。

- 流量管控：从 App 限流、IP 限流、集群限流等多个维度提供流量保护。
- 请求缓存：对于一些查询频繁的、数据及时性不敏感的请求，业务研发人员可开启请求缓存功能。
- 超时管理：每个 API 都设置了处理超时时间，对于超时的请求，进行快速失败的处理，避免资源占用。
- 熔断降级：达到配置的失败阈值后，自动熔断，返回默认值。

![image-20210528143028421](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210528143028.png)

**4.3 监控告警**

Shepherd 从机器指标（1）、业务指标（234）、服务状态指标（5）提供了监控，如下表所示。

![image-20210525231006254](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210525231006.png)

主要的告警能力如下表所示：

![image-20210525231127312](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210525231127.png)

**4.4 易用性设计**

自动生成 DSL。

![image-20210525231339671](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210525231339.png)

# 05 | 可扩展设计

**5.1 自定义组件**

Shepherd 通过提供加载自定义组件能力，支持业务完成一些自定义逻辑的扩展。

这是自定义组件实现的一个实例。Invoke 方法中实现自定义组件的业务逻辑，如继续执行、进行页面跳转、直接返回结果、抛出异常等。

![image-20210524223321317](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210524223321.png)

**5.2 服务编排**

对于一些业务场景，需要通过调用多个接口来满足的，可以通过服务编排来实现。

Shepherd 在创建 API 时，支持这种服务编排的 API，以满足扩展性需求。

![image-20210528142026069](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210528142026.png)

![image-20210528142039740](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210528142039.png)

# 参考资料

- https://tech.meituan.com/2021/05/20/shepherd-api-gateway.html
- https://tech.meituan.com/2018/07/26/sep-service-arrange.html
- https://www.infoq.cn/article/qxcl87g3fsiubnvulkoi