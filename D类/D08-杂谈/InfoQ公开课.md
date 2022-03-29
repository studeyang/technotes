# 微服务构架下的分布式事务解决方案

> 作者：季敏<br>阿里中间件分布式事务团队负责人

## 微服务构架中的常见痛点分析

**微服务架构**

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201120094800.jpg)

**微服务开发的痛点**

![image-20200802111455248](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201120094806.png)

**微服务构架为什么需要分布式事务**

![image-20200802114801456](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201120094811.png)

**微服务构架下的分布式事务解决方案有哪些？**

定时任务做数据补尝

## 分布式事务解决方案--Seata

**事务角色**

![image-20200802115650329](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201120094815.png)

**事务过程动作**

![image-20200802115813627](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201120094819.png)

**微服务分布式事务调用**

![image-20200802120129023](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201120094824.png)

**Seata 4 种模式**

![image-20200802120445254](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201120094828.png)

![image-20200802121316934](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201120094832.png)

![image-20200802121504296](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201120094837.png)

**Seata 高可用**

![image-20200802121601430](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201120094841.png)

**事务模式对比**

![image-20200802122134200](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201120094846.png)

## Seata 社区

**现状**

![image-20200802122922151](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201120094851.png)

**用户案例**

![image-20200802123005198](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201120094855.png)

**版本演进**

![image-20200802123134861](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201120094900.png)

**实战演练**

![image-20200802123238726](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20201120094905.png)

