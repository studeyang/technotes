# 目录



# 第7章 一起来看 AOP

> 本章内容：
>
> - AOP 的尴尬
> - AOP 走向现实
> - Java 平台上的 AOP 实现机制
> - AOP 国家的公民

**7.1 AOP 的尴尬**

AOP 现在没有主权，所以，现时代的AOP实现都需要“寄生”于 OOP 的主权领土中，系统的维度也依然保持曾经 OOP 持有的“维度世界纪录”。

**7.2 AOP 走向现实**

Java 界的 AOP 框架或者说产品，可谓 AOP 土地上的一朵奇葩，在 Xerox 公司的 PARC (Paro Alto Research Center) 提出 AOP 的一套理论之后，Java 业界各种 AOP 框架就如雨后春笋般涌现，其走过的路亦不可谓不精彩，所以，让我们来回顾一下这段精彩历史如何？

- 7.2.1 静态 AOP 时代

  静态 AOP，即第一代 AOP，以最初的 AspectJ 为杰出代表，其特点是，相应的横切关注点以 Aspect 形式实现之后，会通过特定的编译器，将实现后的 Aspect 编译并织入到系统的静态类中。

- 7.2.2 动态 AOP 时代

  动态 AOP，又称为第二代 AOP，该时代的 AOP 框架或产品，大都通过 Java 语言提供的各种动态特性来实现 Aspect 织入到当前系统的过程，如 JBoss AOP, Spring AOP 以及 Nanning 等 AOP 框架。

**7.3 Java 平台上的 AOP 实现机制**

- 7.3.1 动态代理

  我们可以将横切关注点逻辑封装到动态代理的 InvocationHandler 中，然后在系统运行期间，根据横切关注点需要织入的模块位置，将横切逻辑织入到相应的代理类中。

- 7.3.2 动态字节码增强

  可以使用 ASM 或者 CGLIB 等 Java 工具库，在程序运行期间，动态构建字节码的 class 文件。Spring AOP 在无法采用动态代理机制进行 AOP 功能扩展的时候，会使用 CGLIB 库的动态字节码增强支持来实现 AOP 的功能扩展。

- 7.3.3 Java 代码生成

  EJB 容器根据部署描述符文件提供的织入信息，会为相应的功能模块类根据描述符所提供的信息生成对应的 Java 代码，然后通过部署工具或者部署接口编译 Java 代码生成相应的 Java 类。之后，部署到 EJB 容器的功能模块类就可以正常工作了。

  这种方式比较古老，也就早期的 EJB 容器使用最多，现在已经了退休了。

- 7.3.4 自定义类加载器

  自定义类加载器通过读取外部文件规定的织入规则和必要信息，在加载 class 文件期间就可以将横切逻辑添加到系统模块类的现有逻辑中，然后将改动后的 class 交给 Java 虚拟机运行。

- 7.3.5 AOL 扩展

  在这种方式中，AOP 各种概念在 AOL 中大都有一一对应的实体。我们可以使用扩展的 AOL，实现任何 AOP 概念实体甚至 OOP 概念实体，比如 Aspect 以及 Class。

**7.4 AOP 国家的公民**

- 7.4.1 Joinpoint

  这些将要在其之上进行织入操作的系统执行点称之为 Joinpoint。

  ![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/一般程序流程图.png)

  基本上，只要允许，程序执行过程中的任何时点都可以作为横切逻辑的织入点，而所有这些执行时点都是 Joinpoint。

- 7.4.2 Pointcut

  我们使用自然语言声明一个 Pointcut，该 Pointcut 指定了系统中符合条件的一组 Joinpoint。不过，在实际系统中我们不可能使用自然语言形式的 Pointcut。

- 7.4.3 Advice

  After Advice 就是在相应连接点之后执行的 Advice 类型，但该类型的 Advice 还可以细分为三种：After returning Advice; After throwing Advice; After Advice。

  ![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/各种Advice的执行时机.png)

  Around Advice：在 Joinpoint 前后都执行。

  Introduction：可以为原有的对象添加新的特性或行为。

- 7.4.4 Aspect

  Aspect 是对系统中的横切关注点逻辑进行模块化封装的 AOP 概念实体。

- 7.4.5 织入和织入器

  织入（Weaving）过程就是“飞架” AOP 和 OOP 的那座桥，只有经过织入过程之后，以 Aspect 模块化的横切关注点才会集成到 OOP 的现存系统中。

- 7.4.6 目标对象

  符合 Pointcut 所指定的条件，将在织入过程中被织入横切逻辑的对象，称为目标对象。

  ![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/AOP 各个概念所处的场景.png)

# 第8章 Spring AOP概述及其实现机制

> 本章内容
>
> - Spring AOP 概述
> - Spring AOP 的实现机制

**8.1 Spring AOP 概述**

Spring AOP 的设计哲学简单而强大，它不打算将所有的 AOP 需求全部囊括在内，而是以有限的 20% 的 AOP 支持，来满足 80% 的 AOP 需求。

Spring AOP 的 AOL 语言为 Java，所在 Spring AOP 对 AOP 的概念进行了适当的抽象和实现，使得每个 AOP 的概念都可以落到实处。

**8.2 Spring AOP 的实现机制**

- 8.2.1 设计模式之代理模式

  ![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/代理模式相关类关系示意图.jpg)

  SubjectProxy 内部持有 SubjectImpl 的引用，实现请求的转发。

- 8.2.2 动态代理

  动态代理机制的实现主要由 java.lang.reflect.Proxy 类和 java.lang.reflect.InvocationHandler 接口组成。

- 8.2.3 动态字节码生成

  CGLIB官网：http://cglib.sourceforge.net/

# 第9章 Spring AOP 一世

> 本章内容
>
> - Spring AOP 中的 Joinpoint
> - Spring AOP 中的 Pointcut
> - Spring AOP 中的 Advice
> - Spring AOP 中的 Aspect
> - Spring AOP 的织入

**9.1 Spring AOP 中的 Joinpoint**

Spring AOP 仅提供方法拦截，如果需求特殊，不妨使用现有的其他 AOP 实现产品如 AspectJ。AspectJ 是 Java 平台对 AOP 支持最完善的产品。

**9.2 Spring AOP 中的 Pointcut**

Spring 中以接口定义 org.springframework.aop.Pointcut 作为其 AOP 框架中所有 Pointcut 的最顶层抽象。

- 9.2.1 常见的 Pointcut

  ![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/常见的Pointcut.jpg)

- 9.2.2 扩展 Pointcut (Customize Pointcut)

  Spring AOP 的 Pointcut 类型可以划分为 StaticMethodMatcherPointcut 和 DynamicMethodMatcherPointcut 两类。要实现自定义 Pointcut，通常在这两个抽象类的基础上实现相应子类即可。

**9.3 Spring AOP 中的 Advice**

Spring AOP 加入了开源组织 AOP Alliance（http://aopalliance.sourceforge.net/），图 9-4 中就是 Spring 中各种 Advice 类型实现与 AOP Alliance 中标准接口之间的关系。

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/Spring中Advice略图.jpg)

- 9.3.1 per-class 类型的 Advice

  Before Advice、ThrowsAdvice、AfterReturningAdvice、Aroud Advice

- 9.3.2 per-instance 类型的 Advice

  per-instance 类型的 Advice 不会在目标类所有对象实例之间共享，而是会为不同的实例对象保存它们各自的状态以及相关逻辑。（类似于每个员工各自的电脑）

**9.4 Spring AOP 中的 Aspect**

当所有的 Pointcut 和 Advice 准备好之后，就到了该把它们分门别类地装进箱子的时候了，箱子就是 Aspect。

Advisor 代表 Spring 中的 Aspect，但是，与正常的 Aspect 不同，Advisor 通常只持有一个 Pointcut 和一个 Advice。而理论上，Aspect 定义中可以有多个 Pointcut 和多个 Advice，所以，我们可以认为 Advisor 是一种特殊的 Aspect。

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/Advisor分支.jpg)

- 9.4.1 PointcutAdvisor 家族

  实际上，org.springframework.aop.PointcutAdvisor 才是真正的定义一个 Pointcut 和一个 Advice 的Advisor。

  常用的实现有：DefaultPointcutAdvisor、NameMatchMethodPointcutAdvisor、RegexpMethodPointcutAdvisor、DefaultBeanFactoryPointcutAdvisor。

- 9.4.2 IntroductionAdvisor 分支

  IntroductionAdvisor 与 Point

**9.5 Spring AOP 的织入**





# 第10章 Spring AOP 二世

> 本章内容
>
> - @AspectJ 形式的 Spring AOP
> - 基于 Schema 的 AOP

**10.1 @AspectJ 形式的 Spring AOP**



**10.2 基于 Schema 的 AOP**









# 第11章 AOP 应用案例







# 第12章 Spring AOP 之扩展



























