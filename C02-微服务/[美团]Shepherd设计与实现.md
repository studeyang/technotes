> 来源：https://tech.meituan.com/2021/05/20/shepherd-api-gateway.html

# 01 | 背景介绍

**1.1 API 网关是什么？**

API网关是运行于外部请求与内部服务之间的一个流量入口，实现对外部请求的协议转换、鉴权、流控、参数校验、监控等通用功能。

**1.2 为什么要做 Shepherd API 网关** 

为美团提供高性能、高可用、可扩展的统一 API 网关解决方案，让业务研发人员通过配置的方式即可对外开放功能和数据。

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

  完成控制面与数据面的信息交互。配置中心存放的是 API 的配置信息（使用 DSL 领域专用语言来描述）。

  ![image-20210524215822291](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210524215822.png)

  Filters：API 使用到的功能组件；

  Request：请求的域名、路径、参数等信息；

  Response：响应的结果组装、异常处理、Header、Cookies 信息；

  Invokers：后端服务（RPC/HTTP/Function）的请求规则；

  FilterConfigs：API 使用到的功能组件的配置信息；

- 数据面

  泛化后端服务，响应结果。

  提供了 API 路由、功能组件集成、协议转换和服务调用。
  
  API 路由的实现：
  
  <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210525222600.png" alt="image-20210525222600291" style="zoom:50%;" />
  
  当请求流量命中API请求路径进入服务端，具体处理逻辑由DSL中配置的一系列功能组件完成。
  
  ![image-20210525223229796](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210525223229.png)
  
  API 调用的最后一步，就是协议转换以及服务调用了。
  
  ![image-20210525223507745](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210525223507.png)

**2.2 高可用设计**

- 排除性能隐患

  Shepherd对API请求做了全异步化处理：

  ![image-20210525224516711](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210525224516.png)

  QPS 为 2000。

  性能优化一：打开 Nginx 与 Web 应用之间的长连接，性能提升到了 10000 以上。

  性能优化二：对 Shepherd 服务进行 API 请求预热，减少主链路的本地日志打印，QPS 再次提升 30% 即 13000。

  性能优化三：将 Jetty 容器替换为 Netty 网络框架，QPS 再提升 10% 达 15000 以上。

  ![image-20210525225358258](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210525225358.png)

- 服务隔离

  支持集群隔离、请求隔离（快慢线程池隔离）以保证重要业务独立部署。

  ![image-20210525225614915](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210525225614.png)

- 稳定性保障

  保障手段有：流量管控、请求缓存、超时管理、熔断降级。

  流量管控：通过 App 限流、IP 限流、集群限流等多个维度提供流量保护。

  <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210525230038.png" alt="image-20210525230038824"  />

  请求缓存：对于一些查询频繁的、数据及时性不敏感的请求，开启请求缓存功能。

  ![image-20210525230254344](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210525230254.png)

  超时管理：对每个 API 设置超时时间，进行快速失败，避免资源占用。

  ![image-20210525230416069](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210525230416.png)

  熔断降级：达到配置的失败阈值后，自动熔断，返回默认值。

  ![image-20210525230512510](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210525230512.png)

- 请求安全

  集成了安全相关的系统组件。

- 监控告警

  提供立体化监控、多维度告警功能。

  ![image-20210525231006254](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210525231006.png)

  ![image-20210525231127312](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210525231127.png)

- 故障自愈

  支持根据 CPU 指标进行扩缩容，还支持摘除问题节点。

**2.3 易用性设计**

自动生成 DSL。

![image-20210525231339671](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210525231339.png)

**2.4 可扩展性设计**

自定义组件

![image-20210524223321317](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210524223321.png)

