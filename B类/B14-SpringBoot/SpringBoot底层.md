# 01 | Spring Boot 核心运行原理

Spring Boot自动配置功能核心运行原理图。

![image-20220303214852180](https://gitee.com/yanglu_u/img2022/raw/master/learn/20220303214852.png)

**AutoConfigurationImportSelector源码解析**

AutoConfigurationImportSelector 并没有直接实现ImportSelector接口，而是实现了它的子接口DeferredImportSelector。DeferredImportSelector接口与ImportSelector的区别是，前者会在所有的@Configuration类加载完成之后再加载返回的配置类，而ImportSelector是在加载完@Configuration类之前先去加载返回的配置类。

AutoConfigurationImportSelector核心功能及流程图。

![image-20220303222452216](https://gitee.com/yanglu_u/img2022/raw/master/learn/20220303222452.png)





**NacosPropertySourcePostProcessor实现BeanDefinitionRegistryPostProcessor的目的?**



