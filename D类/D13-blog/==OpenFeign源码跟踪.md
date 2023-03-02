全局搜索`DiscoveryClient`的使用。以下是逆向调用链路。

```
new DiscoveryClientServiceInstanceListSupplier
-> 根据调用堆栈 ServiceInstanceListSupplierBuilder # withBlockingDiscoveryClient()
> new DiscoveryClientServiceInstanceListSupplier()
> ServiceInstanceListSupplier # build()
-> Bean定义 LoadBalancerClientConfiguration BlockingSupportConfiguration # discoveryClientServiceInstanceListSupplier()
```

Feign, Ribbon, Discovery



## 如何自定义修改 FeignClient 的 url ？

> 这种技术太细节了，用到的时候再看一下就可以了。没有必要特地去研究，还是要把重点放在全局观上。