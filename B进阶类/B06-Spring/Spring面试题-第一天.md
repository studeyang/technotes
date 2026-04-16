# 01 | 如何利用反射实现 Autowired 注解？

**Autowired 的使用方式**

Autowired 可以标注于类定义的多个位置，包括以下几个。

- 域（Field）或者说属性（Property）

  ```java
  public class FXNewsPProvider {
      @Autowired
      private IFXNewsListener newsListener;
      @Autowired
      private IFXNewsPersister newPersistener;
  }
  ```

- 构造方法定义（Constructor）

- 方法定义（Method）

**@Autowired 依赖注入原型代码**

```java
Object[] beans = ...;
for(Object bean : beans) {
    if(autowriedExistsOnField(bean)) {
        Field f = getQulifiedField(bean);
        setAccessiableIfNecessary(f);
        f.set(getBeanByTypeFromContainer());
    }
    if(autowiredExistsOnConstructor(bean)) {
        ...
    }
    if(autowiredExistsOnMethos(bean)) {
        ...
    }
}
```

# 02 | 手撕 Spring IOC 源码



# 03 | Spring 程序是如何启动的？



# 04 | Spring 是如何加载配置文件到应用程序的？



# 05 | 核心接口 BeanDefinitionReader



# 06 | 核心接口 BeanFactory



# 07 | 彻底搞懂 Spring 的 refresh 方法



# 08 | BeanPostProcessor 接口的作用及实现



# 09 | BeanFactoryPostProcessor 接口的作用及实现





# 10 | Spring Bean 有没有必要实现 Aware 接口？

# 11 | Spring Bean 的实例化过程大揭秘

# 12 | Spring Bean 初始化到底干了什么？

# 13 | 彻底理解 FactoryBean 接口

# 14 | Spring Bean 的生命周期

# 15 | Spring 的 Environment 接口有什么作用？

# 16 | 为什么会产生循环依赖问题？

# 17 | 循环依赖在 Spring 中是如何解决的？

