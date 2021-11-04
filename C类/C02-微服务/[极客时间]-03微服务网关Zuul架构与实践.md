# 50 | Zuul基本应用场景

**介绍**

Netflix 于 2012 年初开源，2014 年被 Pivotal 集成入 Spring Cloud 体系。

亮点：可动态发布的过滤器机制。

![image-20210730231828599](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210730231828.png)

**网关基本功能**

![image-20210730231326839](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210730231327.png)

**Netflix 使用情况（2017）**

- 支持超过 1000 种设备类型
- 超过 50+ 前置 ELB
- 每天处理百亿+请求
- 支持 3个 AWS 区域（regions）
- 部署超过 20+ 生产 Zuul 集群

**国内公司落地案例**

- 携程

部署生产实例 150+（分集群）；<br>
覆盖无线、H5、分销联盟、支付业务等场景；<br>
日流量超 50 亿；

- 拍拍贷

部署实例 40+（分集群）；<br>覆盖无线、H5、第三方开放平台、联盟商等场景；<br>日流量超 5 亿；

# 51 | Zuul高级应用场景

**红绿部署**

![image-20210730233035233](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210730233035.png)

**开发者测试分支**

![image-20210730233150596](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210730233150.png)

**埋点测试**

![image-20210730233220214](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210730233220.png)

**跨区域高可用（异地多活）**

![image-20210730233947685](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210730233947.png)

# 52 | Zuul架构剖析

**架构剖析**

模块一：网关过滤器管理模块；

模块二：网关过滤器加载模块；

模块三：网关过滤器核心运行时模块；

![image-20210730234216913](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210730234216.png)

**请求处理生命周期**

![image-20210730234621463](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210730234621.png)

**过滤器关键概念**

- 类型 Type

  分为前置(PRE)、路由(ROUTING)、后置(POST)、错误(ERROR)过滤器。

- 执行顺序 Execution Order

  在同一个 Type 中，过滤器可以定义执行顺序。

- 条件 Criteria

  过滤器执行的条件。

- 动作 Action

  如果条件满足，过滤器中将执行的动作。

# 53 | Zuul核心源码

netfix 源码：https://github.com/netflix/zuul

Zuul 教学源码：https://github.com/spring2go/s2g-zuul

**过滤器管理工具**













