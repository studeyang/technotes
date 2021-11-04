# 目录

![](性能调优实战-01Java编程调优.png)

# 开篇词 | 怎样才能做好性能调优？

**1. 扎实的计算机基础**

我们需要储备计算机组成原理、操作系统、网络协议以及数据库等基础知识。

**2. 习惯透过源码了解技术本质**

我们需要深入源码，通过分析来学习、总结一项技术的实现原理和优缺点，这样我们就能更客观地去学习一项技术。

**3. 善于追问和总结**

“知其然且知所以然”才是我们积累经验的关键。

专栏具体是怎么设计的呢？

模块一（01-02），概述。两个标准。一个是性能调优标准，另一个是调优过程标准。

模块二（03-11），Java 编程性能调优。会从基础的数据类型讲起，还有网络通信调优。

模块三（12-19），多线程性能调优。同步锁；多线程高并发带来的性能问题。

模块四（20-25），JVM 性能监测及调优。Java 对象的创建和回收、内存分配。

模块五（26-31），设计模式调优。结合应用场景，分享设计优化案例。

模块六（32-39），数据库性能调优。重点解析一些数据库的常用调优方法。

模块七（41-44），实战演练场。进入综合的应用场景，学习整体调优方法。

整个专栏，目的就是交付给你一套“学完就用的调优方法论”。

------

模块一（01-02），概述

# 01 | 如何制定性能调优标准？

**为什么要做性能调优？**

好的系统性能调优不仅仅可以提高系统的性能，还能为公司节省资源。

**什么时候开始介入调优？**

在系统编码完成之后，对系统进行性能测试。<br>在项目成功上线后，根据线上的实际情况修复问题。

**有哪些参考因素可以体现系统的性能？**

哪些计算机资源会成为系统的性能瓶颈。

- CPU：例如，代码递归导致的无限循环，正则表达式引起的回溯，JVM 频繁的 FULL GC，以及多线程编程造成的大量上下文切换等，这些都有可能导致 CPU 资源繁忙。
- 内存：内存溢出、内存泄露。
- 磁盘 I/O：与内存的读写速度相关很大。
- 网络：带宽过低网络就很容易成为性能瓶颈。
- 异常：持续地进行异常处理，系统的性能就会明显地受到影响。
- 数据库：大量的数据库读写操作，会导致磁盘 I/O 性能瓶颈。
- 锁竞争：上下文切换，给系统带来性能开销。<br>通过偏向锁、自旋锁、轻量级锁、锁粗化、锁消除等JVM内部已经做了很多优化。

下面几个指标可以衡量系统的性能。

- 响应时间

  数据库响应时间、服务端响应时间、网络响应时间、客户端响应时间。

- 吞吐量

  TPS 越大，性能越好。吞吐量分为两种：磁盘吞吐量和网络吞吐量。

- 计算机资源分配使用率

  木板效应。

- 负载承受能力

  例如，当你对系统进行压测时，系统的响应时间会随着系统并发数的增加而延长，直到系统无法处理这么多请求，抛出大量错误时，就到了极限。

# 02 | 如何制定性能调优策略？

面对日渐复杂的系统，制定合理的性能测试，可以提前发现性能瓶颈，然后有针对性地制定调优策略。总结一下就是“测试 - 分析 - 调优”三步走。

**性能测试攻略**

1. 微基准性能测试

   微基准性能测试可以精准定位到某个模块或者某个方法的性能问题，特别适合做一个功能模块或者一个方法在不同实现方式下的性能对比。例如，对比一个方法使用同步实现和非同步实现的性能。

2. 宏基准性能测试

   宏基准性能测试是一个综合测试，需要考虑到测试环境、测试场景和测试目标。

   测试环境：需要模拟线上的真实环境。

   测试场景：需要确定在测试某个接口时，是否有其他业务接口同时也在平行运行，造成干扰。

   测试目标：可以通过吞吐量以及响应时间来衡量系统是否达标。

性能测试存在干扰因子，会使测试结果不准确。所以，我们在做性能测试时，还要注意一些问题。

1. 热身问题

   当我们做性能测试时，我们的系统会运行得越来越快。这是因为即时编译器将热点代码缓存起来了。

2. 性能测试结果不稳定

   我们可以通过多次测试，将测试结果求平均，或者统计一个曲线图，只要保证我们的平均值是在合理范围之内，而且波动不是很大，这种情况下，性能测试就是通过的。

3. 多 JVM 情况下的影响

   我们应该尽量避免线上环境中一台机器部署多个 JVM 的情况。

**合理分析结果，制定调优策略**

首先从操作系统层面，查看系统的 CPU、内存、I/O、网络的使用率是否存在异常，再通过命令查找异常日志，最后通过分析日志，找到导致瓶颈的原因；

还可以从 Java 应用的 JVM 层面，查看 JVM 的垃圾回收频率以及内存分配情况是否存在异常，分析日志，找到导致瓶颈的原因。

如果系统和 JVM 层面都没有出现异常情况，我们可以查看应用服务业务层是否存在性能瓶颈，例如 Java 编程的问题、读写数据瓶颈等等。

我们解决系统性能问题，则可以采用自上而下的方式逐级优化。下面我来介绍下从应用层到操作系统层的几种调优策略。

1. 优化代码

   应用层的问题代码往往会因为耗尽系统资源而暴露出来。例如，我们某段代码导致内存溢出；

   还有一些是非问题代码导致的性能问题。例如，我们经常使用的 LinkedList 集合，如果使用 for 循环遍历该容器，将大大降低读的效率，但这种效率的降低很难导致系统性能参数异常。

2. 优化设计

   面向对象有很多设计模式。优化后，不仅可以精简代码，还能提高整体性能。例如，单例模式在频繁调用创建对象的场景中，可以共享一个创建对象，这样可以减少频繁地创建和销毁对象所带来的性能消耗。

3. 优化算法

   好的算法可以帮助我们大大地提升系统性能。例如，在不同的场景中，使用合适的查找算法可以降低时间复杂度。

4. 时间换空间

   有时候系统对查询时的速度并没有很高的要求，反而对存储空间要求苛刻。

   例如，用 String 对象的 intern 方法，可以将重复率比较高的数据集存储在常量池，重复使用一个相同的对象，这样可以大大节省内存存储空间。但由于常量池使用的是 HashMap 数据结构类型，如果我们存储数据过多，查询的性能就会下降。

5. 空间换时间

   这种方法是使用存储空间来提升访问速度。例如 MySQL 分库分表，因为 MySQL 单表在存储千万数据以上时，读写性能会明显下降。

6. 参数调优

   根据自己的业务场景，合理地设置 JVM 的内存空间以及垃圾回收算法可以提升系统性能。例如，如果我们业务中会创建大量的大对象，我们可以通过设置，将这些大对象直接放进老年代。这样可以减少年轻代频繁发生小的垃圾回收（Minor GC），减少 CPU 占用时间，提升系统性能。

   Web 容器线程池的设置以及 Linux 操作系统的内核参数设置不合理也有可能导致系统性能瓶颈，根据自己的业务场景优化这两部分，可以提升系统性能。

**兜底策略，确保系统稳定性**

第一，限流，对系统的入口设置最大访问限制。这里可以参考性能测试中探底接口的 TPS 。同时采取熔断措施，友好地返回没有成功的请求。

第二，实现智能化横向扩容。智能化横向扩容可以保证当访问量超过某一个阈值时，系统可以根据需求自动横向新增服务。

第三，提前扩容。这种方法通常应用于高并发系统，例如，瞬时抢购业务系统。这是因为横向扩容无法满足大量发生在瞬间的请求，即使成功了，抢购也结束了。

目前很多公司使用 Docker 容器来部署应用服务。这是因为 Docker 容器是使用 Kubernetes 作为容器管理系统，而 Kubernetes 可以实现智能化横向扩容和提前扩容 Docker 服务。

**总结**

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/性能调优策略.jpg" style="zoom: 67%;" />

**思考题**

假设你现在负责一个电商系统，马上就有新品上线了，还要有抢购活动，那么你会将哪些功能做微基准性能测试，哪些功能做宏基准性能测试呢？

答：

1. 新品上线需要对系统基础功能、尤其是上线涉及改动、有耦合的业务做宏基准测试，如：用户服务、商品服务、订单服务、支付服务、优惠券服务等。从而保证支撑抢购活动的服务正常运行；
2. 针对抢购活动，如：秒杀团购等促销。需要做微基准测试以验证服务是否达到预期。测试过程中需要留意诸如 qps、内存、cpu、网络带宽、线程堆栈等指标是否达标。不仅考虑单机性能，更要拓展到集群时性能的阈值能达到多少从而给出更加准确的性能测试评估报告；
3. 多说一句：此外还要考虑服务的质量，要测试出抢购活动的瓶颈在哪儿从而应对即将到来的大促活动，以方便开发、运维团队制定更好的如服务限流、降级、动态伸缩等方案。

------

模块二（03-11），Java 编程性能调优

# 03 | 字符串性能优化不容小觑，百M内存轻松存储几十G数据

高效地使用字符串，可以提升系统的整体性能。接下来我们就从 String 对象的实现、特性以及实际使用中的优化这三个方面入手，深入了解。

在开始之前，先看一个老生常谈的问题。

```java
String str1 = "abc";
String str2 = new String("abc");
String str3 = str2.intern();
assertSame(str1 == str2); // false
assertSame(str2 == str3); // false
assertSame(str1 == str3); // true
```

**String 对象是如何实现的？**

一起来看看 Java 对 String 的优化过程，如下图所示：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/Java对String的优化.jpg" style="zoom:50%;" />

1. 在 Java 6 以及之前的版本中，String 对象是对 char 数组进行了封装实现的对象。

   String 对象是通过 offset 和 count 两个属性来定位 char[] 数组，获取字符串。这么做可以高效、快速地共享数组对象，同时节省内存空间，[但这种方式很有可能会导致内存泄漏](https://www.javazhiyin.com/26774.html)。

2. 从 Java 7 版本开始到 Java 8 版本，Java 对 String 类做了一些改变。

   String 类中不再有 offset 和 count 两个变量了。这样的好处是 String 对象占用的内存稍微少了些，同时，String.substring 方法也不再共享 char[]，从而解决了使用该方法可能导致的内存泄漏问题。

3. 从 Java9 版本开始，工程师将 char[] 字段改为了 byte[] 字段，又维护了一个新的属性 coder，它是一个编码格式的标识。

   工程师为什么这样修改呢？

   我们知道一个 char 字符占 16 位，2 个字节。这个情况下，存储单字节编码内的字符（占一个字节的字符）就显得非常浪费。JDK1.9 的 String 类为了节约内存空间，于是使用了占 8 位，1 个字节的 byte 数组来存放字符串。

   而新属性 coder 的作用是，在计算字符串长度或者使用 indexOf() 函数时，我们需要根据这个字段，判断如何计算字符串长度。coder 属性默认有 0 和 1 两个值，0 代表 Latin-1（单字节编码），1 代表 UTF-16。

   详细可点击：[Java 9 新特性 - Compact Strings](https://reionchan.github.io/2017/09/25/java-9-compact-string/)

**String 对象的不可变性**

了解了 String 对象的实现后，你有没有发现在实现代码中 String 类被 final 关键字修饰了，而且变量 char 数组也被 final 修饰了。

Java 这样做的好处在哪里呢？

第一，保证 String 对象的安全性。假设 String 对象是可变的，那么 String 对象将可能被恶意修改。

第二，保证 hash 属性值不会频繁变更，确保了唯一性，使得类似 HashMap 容器才能实现相应的 key-value 缓存功能。

第三，可以实现字符串常量池。在 Java 中，通常有两种创建字符串对象的方式，一种是通过字符串常量的方式创建，如`String str = “abc”`；另一种是字符串变量通过 new 形式的创建，如`String str = new String(“abc”)`。

当代码中使用第一种方式创建字符串对象时，JVM 首先会检查该对象是否在字符串常量池中，如果在，就返回该对象引用，否则新的字符串将在常量池中被创建。

String str = new String(“abc”) 这种方式，首先在编译类文件时，"abc" 常量字符串将会放入到常量结构中，在类加载时，“abc"将会在常量池中创建；其次，在调用 new 时，JVM 命令将会调用 String 的构造函数，同时引用常量池中的 "abc” 字符串，在堆内存中创建一个 String 对象；最后，str 将引用 String 对象。

Java 实现的这个特性叫作 String 对象的不可变性，即 String 对象一旦创建成功，就不能再对它进行改变。

这里你可能会想到一个经典反例。平常编程时，对一个 String 对象 str 赋值 “hello”，然后又让 str 值为 “world”，这个时候 str 的值变成了 “world”。那么 str 值确实改变了，为什么我还说 String 对象不可变呢？

这是因为 str 只是 String 对象的引用，并不是对象本身。对象在内存中是一块内存地址，str 则是一个指向该内存地址的引用。所以在刚刚我们说的这个例子中，第一次赋值的时候，创建了一个 “hello” 对象，str 引用指向 “hello” 地址；第二次赋值的时候，又重新创建了一个对象 “world”，str 引用指向了 “world”，但 “hello” 对象依然存在于内存中。

**String 对象的优化**

1. 如何构建超大字符串？

   编程过程中，字符串的拼接很常见。是不是就会产生多个对象呢？

   ```java
   String str= "ab" + "cd" + "ef";
   ```

   实际运行中，编译器自动优化了这行代码，最终只有一个对象生成。

   ```java
   String str= "abcdef";
   ```

   字符串变量的累计又是怎样的呢？

   ```java
   String str = "abcdef";
   for(int i = 0; i < 1000; i++) {
         str = str + i;
   }
   ```

   编译器同样对这段代码进行了优化。

   ```java
   String str = "abcdef";
   for(int i = 0; i < 1000; i++) {
   	str = (new StringBuilder(String.valueOf(str))).append(i).toString();
   }
   ```

   [JVM里最大可以创建多长的字符串呢？](https://cloud.tencent.com/developer/article/1511731)

   ```java
   /**
    * 运行参数: -Xmx8g -Xms8g
    */
   public class StringMaxLength {
       // 65534个a, 65535个a编译会报错
       private final static String latinString = "a...a";
       public static void main(String[] args) {
           StringBuilder builder = new StringBuilder();
           // 最长为 Integer.MAX_VALUE - 8个
           for (int i = 0; i < Integer.MAX_VALUE - 8; i++) {
               builder.append("a");
           }
           System.out.println(builder.length());
       }
       /*
        * 问题：String最长可以分配多少个内存?
        * 结论：
        * 1. 如果是在编译时，最长为65534个
        * 2. 如果是在运行时，最长为Integer.MAX_VALUE - 8个
        * ArrayList 的 MAX_ARRAY_SIZE 字段作出了解释
        */
   }
   ```

   2. 如何使用`String.intern`节省内存？

      在每次赋值的时候使用 String 的 intern 方法，如果常量池中有相同值，就会重复使用该对象，返回对象引用。

      ```java
      SharedLocation sharedLocation = new SharedLocation();
       
      sharedLocation.setCity(messageInfo.getCity().intern());		sharedLocation.setCountryCode(messageInfo.getRegion().intern());
      sharedLocation.setRegion(messageInfo.getCountryCode().intern());
       
      Location location = new Location();
      location.set(sharedLocation);
      location.set(messageInfo.getLongitude());
      location.set(messageInfo.getLatitude());
      ```

      其中的原理是怎么样的？

      在字符串常量中，默认会将对象放入常量池；

      在字符串变量中，对象是会创建在堆内存中，同时也会在常量池中创建一个字符串对象，复制到堆内存对象中，并返回堆内存对象引用。

      如果调用 intern 方法，会去查看字符串常量池中是否有等于该对象的字符串，如果没有，就在常量池中新增该对象，并返回该对象引用；如果有，就返回常量池中的字符串引用。堆内存中原有的对象由于没有引用指向它，将会通过垃圾回收器回收。

      举个例子：

      ```java
      String a = new String("abc").intern();
      String b = new String("abc").intern();
      System.out.print(a == b); // true
      ```

      在一开始创建 a 变量时，会在堆内存中创建一个对象，同时会在加载类时，在常量池中创建一个字符串对象，在调用 intern 方法之后，会去常量池中查找是否有等于该字符串的对象，有就返回引用。

      在创建 b 字符串变量时，也会在堆中创建一个对象，此时常量池中有该字符串对象，就不再创建。调用 intern 方法则会去常量池中判断是否有等于该字符串的对象，发现有等于"abc"字符串的对象，就直接返回引用。而在堆内存中的对象，由于没有引用指向它，将会被垃圾回收。所以 a 和 b 引用的是同一个对象。

      下面我用一张图来总结下 String 字符串的创建分配内存地址情况：

      ![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/String字符串的创建分配内存地址情况.jpg)

      使用 intern 方法需要注意的一点是，一定要结合实际场景。因为常量池的实现是类似于一个 HashTable 的实现方式，HashTable 存储的数据越大，遍历的时间复杂度就会增加。如果数据过大，会增加整个字符串常量池的负担。

   3. 如何使用字符串的分割方法？

      Split() 方法使用了正则表达式实现了其强大的分割功能，而正则表达式的性能是非常不稳定的，使用不恰当会引起回溯问题，很可能导致 CPU 居高不下。

      所以我们应该慎重使用 Split() 方法，我们可以用 String.indexOf() 方法代替 Split() 方法完成字符串的分割。如果实在无法满足需求，你就在使用 Split() 方法时，对回溯问题加以重视就可以了。

# 04 | 慎重使用正则表达式

**什么是正则表达式？**

正则表达式使用一些特定的元字符来检索、匹配以及替换符合规则的字符串。

构造正则表达式语法的元字符，由普通字符、标准字符、限定字符（量词）、定位字符（边界字符）组成。详情可见下图：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/正则表达式元字符.jpg" style="zoom: 50%;" />

**正则表达式引擎**

正则表达式是一个用正则符号写出的公式，程序对这个公式进行语法分析并建立语法分析树，再根据这个分析树生成执行程序，这个执行程序我们把它称作状态自动机。

目前实现正则表达式引擎的方式有两种：DFA 自动机（Deterministic Final Automata 确定有限状态自动机）和 NFA 自动机（Non deterministic Finite Automaton 非确定有限状态自动机）。在编程语言里，使用的正则表达式库都是基于 NFA 实现的。

那么 NFA 自动机到底是怎么进行匹配的呢？

```
text = "aabcab"
regex = "bc"
```

首先，读取正则表达式的第一个匹配符和字符串的第一个字符进行比较，b 对 a，不匹配；继续换字符串的下一个字符，也是 a，不匹配；继续换下一个，是 b，匹配。

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/NFA自动机匹配过程.jpg)

读取正则表达式的第二个匹配符和字符串的第四个字符进行比较，c 对 c，匹配；继续读取正则表达式的下一个字符，然而后面已经没有可匹配的字符了，结束。

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/NFA自动机匹配过程2.jpg)

**NFA 自动机的回溯**

用 NFA 自动机实现的比较复杂的正则表达式，在匹配过程中经常会引起回溯问题。大量的回溯会长时间地占用 CPU，从而带来系统性能开销。

```
text = "abbc"
regex = "ab{1,3}c"
```

首先，读取正则表达式第一个匹配符 a 和字符串第一个字符 a 进行比较，a 对 a，匹配。

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/NFA回溯1.jpg)

然后，读取正则表达式第二个匹配符 b{1,3} 和字符串的第二个字符 b 进行比较，匹配。但因为 b{1,3} 表示 1-3 个 b 字符串，NFA 自动机又具有贪婪特性，所以此时不会继续读取正则表达式的下一个匹配符，而是依旧使用 b{1,3} 和字符串的第三个字符 b 进行比较，结果还是匹配。

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/NFA回溯2.jpg)

接着继续使用 b{1,3} 和字符串的第四个字符 c 进行比较，发现不匹配了，此时就会发生回溯，已经读取的字符串第四个字符 c 将被吐出去，指针回到第三个字符 b 的位置。

![](images/NFA回溯3.jpg)

发生回溯以后，程序会读取正则表达式的下一个匹配符 c，和字符串中的第四个字符 c 进行比较，结果匹配，结束。

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/NFA回溯4.jpg)

**如何避免回溯问题？**

避免回溯的方法就是：使用懒惰模式和独占模式。

1. 贪婪模式（Greedy）

   如果单独使用 +、 ? 、* 或{min,max} 等量词，正则表达式会匹配尽可能多的内容。

   例如：

   ```
   text = "abbc"
   regex = "ab{1,3}c"
   ```

2. 懒惰模式（Reluctant）

   在该模式下，正则表达式会尽可能少地重复匹配字符。如果匹配成功，它会继续匹配剩余的字符串。

   例如，在上面例子的字符后面加一个“？”，就可以开启懒惰模式。

   ```
   text = "abc"
   regex = "ab{1,3}?c"
   ```

3. 独占模式（Possessive）

   同贪婪模式一样，独占模式一样会最大限度地匹配更多内容；不同的是，在独占模式下，匹配失败就会结束匹配，不会发生回溯问题。

   例如：在字符后面加一个“+”，就可以开启独占模式。

   ```
   text = "abbc"
   regex = "ab{1,3}+bc"
   ```

**正则表达式的优化**

1. 少用贪婪模式，多用独占模式

2. 减少分支选择

   分支选择类型“(X|Y|Z)”的正则表达式会降低性能，我们需要考虑选择的顺序，将比较常用的选择项放在前面；

   其次，我们可以尝试提取共用模式，例如，将“(abcd|abef)”替换为“ab(cd|ef)”，因为 NFA 自动机会尝试匹配 ab，如果没有找到，就不会再尝试任何选项；

3. 减少捕获嵌套

   捕获组：指把正则表达式中，子表达式匹配的内容保存到以数字编号或显式命名的数组中，方便后面引用。一般一个 () 就是一个捕获组，捕获组可以进行嵌套。

   ```java
   public static void main( String[] args ) {
       String text = "<input high=\"20\" weight=\"70\">test</input>";
       // 捕获组
       String reg = "(<input.*?>)(.*?)(</input>)";
       Pattern p = Pattern.compile(reg);
       Matcher m = p.matcher(text);
       while (m.find()) {
           // 整个匹配到的内容:<input high=\"20\" weight=\"70\">test</input>
           System.out.println(m.group(0));
           // (<input.*?>):<input high=\"20\" weight=\"70\">
           System.out.println(m.group(1));
           // (.*?):test
           System.out.println(m.group(2));
           // (</input>):</input>
           System.out.println(m.group(3));
       }
   }
   ```

   非捕获组：指参与匹配却不进行分组编号的捕获组，其表达式一般由（?:exp）组成。

   ```java
   public static void main( String[] args ) {
       String text = "<input high=\"20\" weight=\"70\">test</input>";
       // 非捕获组
       String reg = "(?:<input.*?>)(.*?)(?:</input>)";
       Pattern p = Pattern.compile(reg);
       Matcher m = p.matcher(text);
       while (m.find()) {
           // 整个匹配到的内容:<input high=\"20\" weight=\"70\">test</input>
           System.out.println(m.group(0));
           // (.*?):test
           System.out.println(m.group(1));
       }
   }
   ```

   在正则表达式中，每个捕获组都有一个编号，编号 0 代表整个匹配到的内容。减少不需要获取的分组，可以提高正则表达式的性能。

**思考题**

JDK 里面，还有哪些工具方法用到了正则表达式？

答：replaceAll

# 05 | ArrayList还是LinkedList？使用不当性能差千倍

**初识 List 接口**

 List 集合类的接口和类的实现关系：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/List 集合类的接口和类的实现关系.jpg" style="zoom: 80%;" />

 ArrayList、Vector、LinkedList 集合类继承了 AbstractList 抽象类，而 AbstractList 实现了 List 接口，同时也继承了 AbstractCollection 抽象类。

**ArrayList 是如何实现的？**

1. ArrayList 实现类

   ```java
   public class ArrayList<E> 
       extends AbstractList<E> 
       implements List<E>, RandomAccess, Cloneable, java.io.Serializable
   ```

   ArrayList 实现了 List 接口，继承了 AbstractList 抽象类，底层是数组实现的，并且实现了自增扩容数组大小。

   ArrayList 还实现了 Cloneable 接口和 Serializable 接口，所以他可以实现克隆和序列化。

   ArrayList 还实现了 RandomAccess 接口。这个接口其实是一个空接口，他标志着“只要实现该接口的 List 类，都能实现快速随机访问”。

2. ArrayList 属性

   ```java
   // 默认初始化容量
   private static final int DEFAULT_CAPACITY = 10;
   // 对象数组
   transient Object[] elementData; 
   // 数组长度
   private int size;
   ```

   ArrayList 为了避免这些没有存储数据的内存空间被序列化，内部提供了两个私有方法 writeObject 以及 readObject 来自我完成序列化与反序列化，从而在序列化与反序列化数组时节省了空间和时间。

   使用 transient 修饰数组，是防止对象数组被其他外部方法序列化。

3. ArrayList 构造函数

   ```java
   public ArrayList(int initialCapacity) {
       // 初始化容量不为零时，将根据初始化值创建数组大小
       if (initialCapacity > 0) {
           this.elementData = new Object[initialCapacity];
       } else if (initialCapacity == 0) {// 初始化容量为零时，使用默认的空数组
           this.elementData = EMPTY_ELEMENTDATA;
       } else {
           throw new IllegalArgumentException("Illegal Capacity: " + initialCapacity);
       }
   }
   
   public ArrayList() {
       // 初始化默认为空数组
       this.elementData = DEFAULTCAPACITY_EMPTY_ELEMENTDATA;
   }
   
   public ArrayList(Collection<? extends E> c) {
       elementData = c.toArray();
       if ((size = elementData.length) != 0) {
           // c.toArray might (incorrectly) not return Object[] (see 6260652)
           if (elementData.getClass() != Object[].class)
               elementData = Arrays.copyOf(elementData, size, Object[].class);
       } else {
           // replace with empty array.
           this.elementData = EMPTY_ELEMENTDATA;
       }
   }
   ```

   我们在初始化 ArrayList 时，可以通过第一个构造函数合理指定数组初始大小，这样有助于减少数组的扩容次数，从而提高系统性能。

4. ArrayList 新增元素

   ArrayList 新增元素的方法有两种，一种是直接将元素加到数组的末尾，另外一种是添加元素到任意位置。

   ```java
   public boolean add(E e) {
       ensureCapacityInternal(size + 1);  // Increments modCount!!
       elementData[size++] = e;
       return true;
   }
   
   public void add(int index, E element) {
       rangeCheckForAdd(index);
       ensureCapacityInternal(size + 1);  // Increments modCount!!
       System.arraycopy(elementData, index, elementData, index + 1, size - index);
       elementData[index] = element;
       size++;
   }
   ```

   两个方法的相同之处是在添加元素之前，都会先确认容量大小，如果容量不够大，就会按照原来数组的 1.5 倍大小进行扩容，在扩容之后需要将数组复制到新分配的内存地址。

   如果我们在初始化时就比较清楚存储数据的大小，就可以在 ArrayList 初始化时指定数组容量大小，并且在添加元素时，只在数组末尾添加元素，那么 ArrayList 在大量新增元素的场景下，性能并不会变差，反而比其他 List 集合的性能要好。

**LinkedList 是如何实现的？**

LinkedList 是基于双向链表数据结构实现的。

```java
private static class Node<E> {
    E item;
    Node<E> next;
    Node<E> prev;
    
    Node(Node<E> prev, E element, Node<E> next) {
        this.item = element;
        this.next = next;
        this.prev = prev;
    }
}
```

在 JDK1.7 之前，LinkedList 中只包含了一个 Entry 结构的 header 属性，并在初始化的时候默认创建一个空的 Entry，用来做 header，前后指针指向自己，形成一个循环双向链表。

在 JDK1.7 之后，链表的 Entry 结构换成了 Node，LinkedList 里面的 header 属性去掉了，新增了一个 Node 结构的 first 属性和一个 Node 结构的 last 属性。

这样做有以下几点好处：

- first/last 属性能更清晰地表达链表的链头和链尾概念；
- first/last 方式可以在初始化 LinkedList 的时候节省 new 一个 Entry；
- first/last 方式最重要的性能优化是链头和链尾的插入删除操作更加快捷了。

1. LinkedList 实现类

   ```java
   public class LinkedList<E>
       extends AbstractSequentialList<E>
       implements List<E>, Deque<E>, Cloneable, java.io.Serializable
   ```

2. LinkedList 属性

   ```java
   transient int size = 0;
   transient Node<E> first;
   transient Node<E> last;
   ```

   我们在序列化的时候不会只对头尾进行序列化，所以 LinkedList 也是自行实现 readObject 和 writeObject 进行序列化与反序列化。

3. LinkedList 新增元素

   ```java
   // 添加的元素加到队尾
   public boolean add(E e) {}
   void linkLast(E e) {}
   // 添加元素到任意位置的方法
   public void add(int index, E element) {}
   void linkBefore(E e, Node<E> succ) {}
   ```

4. LinkedList 删除元素

   首先要通过循环找到要删除的元素，如果要删除的位置处于 List 的前半段，就从前往后找；若其位置处于后半段，就从后往前找。

5. LinkedList 遍历元素

   在 LinkedList 循环遍历时，我们可以使用 iterator 方式迭代循环，直接拿到我们的元素，而不需要通过循环查找 List。

**思考题**

下面2种 ArrayList 遍历删除写法，哪种是正确的？

写法1：

```java
public static void remove(ArrayList<String> list) {
    Iterator<String> it = list.iterator();
    while (it.hasNext()) {
        String str = it.next();
        if (str.equals("b")) {
            it.remove();
        }
    }
}
```

写法2：

```java
public static void remove(ArrayList<String> list) {
    for (String s : list) {
        if (s.equals("b")) {
            list.remove(s);
        }
    }
}
```

答：第一个是正确的，第二个虽然用的是`foreach`语法糖，遍历的时候用的也是迭代器遍历，但是在`remove`操作时使用的是原始数组`list`的`remove`，而不是迭代器的`remove`。这样就会造成`modCound != exceptedModeCount`，进而抛出`ConcurrentModificationException`异常。

# 06 | Stream如何提高遍历集合效率？

在 Java8 中，Collection 新增了两个流方法，分别是 Stream() 和 parallelStream()。

**什么是 Stream？**

Java8 中添加了一个新的接口类 Stream，他和我们之前接触的字节流概念不太一样，Java8 集合中的 Stream 相当于高级版的 Iterator，他可以通过 Lambda 表达式对集合进行各种非常便利、高效的聚合操作（Aggregate Operation），或者大批量数据操作 (Bulk Data Operation)。

Stream 的聚合操作与数据库 SQL 的聚合操作 sorted、filter、map 等类似。我们在应用层就可以高效地实现类似数据库 SQL 的聚合操作了。

而在数据操作方面，Stream 不仅可以通过串行的方式实现数据操作，还可以通过并行的方式处理大批量数据，提高数据的处理效率。

这个 Demo 的需求是过滤分组一所中学里身高在 160cm 以上的男女同学，我们先用传统的迭代方式来实现，代码如下：

```java
Map<String, List<Student>> stuMap = new HashMap<String, List<Student>>();
for (Student stu: studentsList) {
    if (stu.getHeight() > 160) { // 如果身高大于 160
        if (stuMap.get(stu.getSex()) == null) { // 该性别还没分类
            List<Student> list = new ArrayList<Student>(); // 新建该性别学生的列表
            list.add(stu);// 将学生放进去列表
            stuMap.put(stu.getSex(), list);// 将列表放到 map 中
        } else { // 该性别分类已存在
            stuMap.get(stu.getSex()).add(stu);// 该性别分类已存在，则直接放进去即可
        }
    }
}

```

我们再使用 Java8 中的 Stream API 进行实现：

串行实现

```java
Map<String, List<Student>> stuMap = stuList.stream()
    .filter((Student s) -> s.getHeight() > 160)
    .collect(Collectors.groupingBy(Student ::getSex)); 
```

并行实现

```java
Map<String, List<Student>> stuMap = stuList.parallelStream()
    .filter((Student s) -> s.getHeight() > 160)
    .collect(Collectors.groupingBy(Student ::getSex)); 
```

**Stream 如何优化遍历？**

Stream 是如何做到优化迭代的呢？并行又是如何实现的？下面我们就透过 Stream 源码剖析 Stream 的实现原理。

1. Stream 操作分类

   官方将 Stream 中的操作分为两大类：中间操作（Intermediate operations）和终结操作（Terminal operations）。

   中间操作只对操作进行了记录，即只会返回一个流，不会进行计算操作，而终结操作是实现了计算操作。

   中间操作又可以分为无状态（Stateless）与有状态（Stateful）操作，前者是指元素的处理不受之前元素的影响，后者是指该操作只有拿到所有元素之后才能继续下去。

   终结操作又可以分为短路（Short-circuiting）与非短路（Unshort-circuiting）操作，前者是指遇到某些符合条件的元素就可以得到最终结果，后者是指必须处理完所有元素才能得到最终结果。操作分类详情如下图所示：

   <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120091624.jpg" style="zoom: 50%;" />

   我们通常还会将中间操作称为懒操作，也正是由这种懒操作结合终结操作、数据源构成的处理管道（Pipeline），实现了 Stream 的高效。

2. Stream 源码实现

   ![](images/Stream源码实现.jpg)

   BaseStream 和 Stream 为最顶端的接口类。BaseStream 主要定义了流的基本接口方法，例如，spliterator、isParallel 等；Stream 则定义了一些流的常用操作方法，例如，map、filter 等。

   ReferencePipeline 是一个结构类，他通过定义内部类组装了各种操作流。他定义了 Head、StatelessOp、StatefulOp 三个内部类，实现了 BaseStream 与 Stream 的接口方法。

   Sink 接口是定义每个 Stream 操作之间关系的协议，他包含 begin()、end()、cancellationRequested()、accpt() 四个方法。ReferencePipeline 最终会将整个 Stream 流操作组装成一个调用链，而这条调用链上的各个 Stream 操作的上下关系就是通过 Sink 接口协议来定义实现的。

3. Stream 操作叠加

   我们知道，一个 Stream 的各个操作是由处理管道组装，并统一完成数据处理的。在 JDK 中每次的中断操作会以使用阶段（Stage）命名。

   管道结构通常是由 ReferencePipeline 类实现的，前面讲解 Stream 包结构时，我提到过 ReferencePipeline 包含了 Head、StatelessOp、StatefulOp 三种内部类。

   Head 类主要用来定义数据源操作，在我们初次调用 names.stream() 方法时，会初次加载 Head 对象，此时为加载数据源操作；接着加载的是中间操作，分别为无状态中间操作 StatelessOp 对象和有状态操作 StatefulOp 对象，此时的 Stage 并没有执行，而是通过 AbstractPipeline 生成了一个中间操作 Stage 链表；当我们调用终结操作时，会生成一个最终的 Stage，通过这个 Stage 触发之前的中间操作，从最后一个 Stage 开始，递归产生一个 Sink 链。如下图所示：

   <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120091635.jpg" style="zoom: 50%;" />

   下面我们再通过一个例子来感受下 Stream 的操作分类是如何实现高效迭代大数据集合的。

   ```java
   List<String> names = Arrays.asList(" 张三 ", " 李四 ", " 王老五 ", " 李三 ", " 刘老四 ", " 王小二 ", " 张四 ", " 张五六七 ");
    
   String maxLenStartWithZ = names.stream()
       	            .filter(name -> name.startsWith(" 张 "))
       	            .mapToInt(String::length)
       	            .max()
       	            .toString();
   ```

   这个例子的需求是查找出一个长度最长，并且以张为姓氏的名字。从代码角度来看，你可能会认为是这样的操作流程：首先遍历一次集合，得到以“张”开头的所有名字；然后遍历一次 filter 得到的集合，将名字转换成数字长度；最后再从长度集合中找到最长的那个名字并且返回。

   这里我要很明确地告诉你，实际情况并非如此。我们来逐步分析下这个方法里所有的操作是如何执行的。

   首先 ，因为 names 是 ArrayList 集合，所以 names.stream() 方法将会调用集合类基础接口 Collection 的 Stream 方法：

   ```java
   default Stream<E> stream() {
       return StreamSupport.stream(spliterator(), false);
   }
   ```

   然后，Stream 方法就会调用 StreamSupport 类的 Stream 方法，方法中初始化了一个 ReferencePipeline 的 Head 内部类对象：

   ```java
   public static <T> Stream<T> stream(Spliterator<T> spliterator, boolean parallel) {
       Objects.requireNonNull(spliterator);
       return new ReferencePipeline.Head<>(spliterator,
                                           StreamOpFlag.fromCharacteristics(spliterator),
                                           parallel);
   }
   ```

   再调用 filter 和 map 方法，这两个方法都是无状态的中间操作，所以执行 filter 和 map 操作时，并没有进行任何的操作，而是分别创建了一个 Stage 来标识用户的每一次操作。

   而通常情况下 Stream 的操作又需要一个回调函数，所以一个完整的 Stage 是由数据来源、操作、回调函数组成的三元组来表示。如下图所示，分别是 ReferencePipeline 的 filter 方法和 map 方法：

   ```java
   @Override
   public final Stream<P_OUT> filter(Predicate<? super P_OUT> predicate) {
       Objects.requireNonNull(predicate);
       return new StatelessOp<P_OUT, P_OUT>(this, StreamShape.REFERENCE,
                                            StreamOpFlag.NOT_SIZED) {
           @Override
           Sink<P_OUT> opWrapSink(int flags, Sink<P_OUT> sink) {
               return new Sink.ChainedReference<P_OUT, P_OUT>(sink) {
                   @Override
                   public void begin(long size) {
                       downstream.begin(-1);
                   }
   
                   @Override
                   public void accept(P_OUT u) {
                       if (predicate.test(u))
                           downstream.accept(u);
                   }
               };
           }
       };
   }
   ```

   ```java
   @Override
   @SuppressWarnings("unchecked")
   public final <R> Stream<R> map(Function<? super P_OUT, ? extends R> mapper) {
       Objects.requireNonNull(mapper);
       return new StatelessOp<P_OUT, R>(this, StreamShape.REFERENCE,
                                        StreamOpFlag.NOT_SORTED | StreamOpFlag.NOT_DISTINCT) {
           @Override
           Sink<P_OUT> opWrapSink(int flags, Sink<R> sink) {
               return new Sink.ChainedReference<P_OUT, R>(sink) {
                   @Override
                   public void accept(P_OUT u) {
                       downstream.accept(mapper.apply(u));
                   }
               };
           }
       };
   }
   ```

   new StatelessOp 将会调用父类 AbstractPipeline 的构造函数，这个构造函数将前后的 Stage 联系起来，生成一个 Stage 链表：

   ```java
   AbstractPipeline(AbstractPipeline<?, E_IN, ?> previousStage, int opFlags) {
       if (previousStage.linkedOrConsumed)
           throw new IllegalStateException(MSG_STREAM_LINKED);
       previousStage.linkedOrConsumed = true;
       previousStage.nextStage = this;// 将当前的 stage 的 next 指针指向之前的 stage
   
       this.previousStage = previousStage;// 赋值当前 stage 当全局变量 previousStage 
       this.sourceOrOpFlags = opFlags & StreamOpFlag.OP_MASK;
       this.combinedFlags = StreamOpFlag.combineOpFlags(opFlags, previousStage.combinedFlags);
       this.sourceStage = previousStage.sourceStage;
       if (opIsStateful())
           sourceStage.sourceAnyStateful = true;
       this.depth = previousStage.depth + 1;
   }
   ```

   因为在创建每一个 Stage 时，都会包含一个 opWrapSink() 方法，该方法会把一个操作的具体实现封装在 Sink 类中，Sink 采用（处理 -> 转发）的模式来叠加操作。

   当执行 max 方法时，会调用 ReferencePipeline 的 max 方法，此时由于 max 方法是终结操作，所以会创建一个 TerminalOp 操作，同时创建一个 ReducingSink，并且将操作封装在 Sink 类中。

   ```java
   @Override
   public final Optional<P_OUT> max(Comparator<? super P_OUT> comparator) {
       return reduce(BinaryOperator.maxBy(comparator));
   }
   ```

   最后，调用 AbstractPipeline 的 wrapSink 方法，该方法会调用 opWrapSink 生成一个 Sink 链表，Sink 链表中的每一个 Sink 都封装了一个操作的具体实现。

   ```java
   @Override
   @SuppressWarnings("unchecked")
   final <P_IN> Sink<P_IN> wrapSink(Sink<E_OUT> sink) {
       Objects.requireNonNull(sink);
   
       for ( @SuppressWarnings("rawtypes") AbstractPipeline p=AbstractPipeline.this; p.depth > 0; p=p.previousStage) {
           sink = p.opWrapSink(p.previousStage.combinedFlags, sink);
       }
       return (Sink<P_IN>) sink;
   }
   ```

   当 Sink 链表生成完成后，Stream 开始执行，通过 spliterator 迭代集合，执行 Sink 链表中的具体操作。

   ```java
   @Override
   final <P_IN> void copyInto(Sink<P_IN> wrappedSink, Spliterator<P_IN> spliterator) {
       Objects.requireNonNull(wrappedSink);
   
       if (!StreamOpFlag.SHORT_CIRCUIT.isKnown(getStreamAndOpFlags())) {
           wrappedSink.begin(spliterator.getExactSizeIfKnown());
           spliterator.forEachRemaining(wrappedSink);
           wrappedSink.end();
       }
       else {
           copyIntoWithCancel(wrappedSink, spliterator);
       }
   }
   ```

   Java8 中的 Spliterator 的 forEachRemaining 会迭代集合，每迭代一次，都会执行一次 filter 操作，如果 filter 操作通过，就会触发 map 操作，然后将结果放入到临时数组 object 中，再进行下一次的迭代。完成中间操作后，就会触发终结操作 max。

   这就是串行处理方式了，那么 Stream 的另一种处理数据的方式又是怎么操作的呢？

4. Stream 并行处理

   Stream 处理数据的方式有两种，串行处理和并行处理。要实现并行处理，我们只需要在例子的代码中新增一个 Parallel() 方法，代码如下所示：

   ```java
   List<String> names = Arrays.asList(" 张三 ", " 李四 ", " 王老五 ", " 李三 ", " 刘老四 ", " 王小二 ", " 张四 ", " 张五六七 ");
    
   String maxLenStartWithZ = names.stream()
                       .parallel()
       	            .filter(name -> name.startsWith(" 张 "))
       	            .mapToInt(String::length)
       	            .max()
       	            .toString();
   ```

   Stream 的并行处理在执行终结操作之前，跟串行处理的实现是一样的。而在调用终结方法之后，实现的方式就有点不太一样，会调用 TerminalOp 的 evaluateParallel 方法进行并行处理。

   ```java
   final <R> R evaluate(TerminalOp<E_OUT, R> terminalOp) {
       assert getOutputShape() == terminalOp.inputShape();
       if (linkedOrConsumed)
           throw new IllegalStateException(MSG_STREAM_LINKED);
       linkedOrConsumed = true;
   
       return isParallel()
           ? terminalOp.evaluateParallel(this, sourceSpliterator(terminalOp.getOpFlags()))
           : terminalOp.evaluateSequential(this, sourceSpliterator(terminalOp.getOpFlags()));
   }
   ```

   这里的并行处理指的是，Stream 结合了 ForkJoin 框架，对 Stream 处理进行了分片，Splititerator 中的 estimateSize 方法会估算出分片的数据量。

   ForkJoin 框架和估算算法，在这里我就不具体讲解了，如果感兴趣，你可以深入源码分析下该算法的实现。

   通过预估的数据量获取最小处理单元的阀值，如果当前分片大小大于最小处理单元的阀值，就继续切分集合。每个分片将会生成一个 Sink 链表，当所有的分片操作完成后，ForkJoin 框架将会合并分片任何结果集。

**合理使用 Stream**

看到这里，你应该对 Stream API 是如何优化集合遍历有个清晰的认知了。Stream API 用起来简洁，还能并行处理，那是不是使用 Stream API，系统性能就更好呢？通过一组测试，我们一探究竟。

我们将对常规的迭代、Stream 串行迭代以及 Stream 并行迭代进行性能测试对比，迭代循环中，我们将对数据进行过滤、分组等操作。分别进行以下几组测试：

- 多核 CPU 服务器配置环境下，对比长度 100 的 int 数组的性能；
- 多核 CPU 服务器配置环境下，对比长度 1.00E+8 的 int 数组的性能；
- 多核 CPU 服务器配置环境下，对比长度 1.00E+8 对象数组过滤分组的性能；
- 单核 CPU 服务器配置环境下，对比长度 1.00E+8 对象数组过滤分组的性能。

由于篇幅有限，我这里直接给出统计结果，你也可以自己去验证一下，具体的测试代码可以在[Github](https://github.com/nickliuchao/stream)上查看。通过以上测试，我统计出的测试结果如下（迭代使用时间）：

- 常规的迭代 < Stream 并行迭代 < Stream 串行迭代
- Stream 并行迭代 < 常规的迭代 < Stream 串行迭代
- Stream 并行迭代 < 常规的迭代 < Stream 串行迭代
- 常规的迭代 < Stream 串行迭代 < Stream 并行迭代

通过以上测试结果，我们可以看到：在循环迭代次数较少的情况下，常规的迭代方式性能反而更好；在单核 CPU 服务器配置环境中，也是常规迭代方式更有优势；而在大数据循环迭代中，如果服务器是多核 CPU 的情况下，Stream 的并行迭代优势明显。所以我们在平时处理大数据的集合时，应该尽量考虑将应用部署在多核 CPU 环境下，并且使用 Stream 的并行迭代方式进行处理。

用事实说话，我们看到其实使用 Stream 未必可以使系统性能更佳，还是要结合应用场景进行选择，也就是合理地使用 Stream。

**思考题**

这里有一个简单的并行处理案例，请你找出其中存在的问题。

```java
// 使用一个容器装载 100 个数字，通过 Stream 并行处理的方式将容器中为单数的数字转移到容器 parallelList
List<Integer> integerList = new ArrayList<Integer>();
 
for (int i = 0; i < 100; i++) {
      integerList.add(i);
}

List<Integer> parallelList = new ArrayList<Integer>() ;
integerList.stream()
           .parallel()
           .filter(i -> i % 2 == 1)
           .forEach(i -> parallelList.add(i));
```

答：会存在线程不安全问题。

# 07 | 深入浅出HashMap的设计与优化

**常用的数据结构**

数组：采用一段连续的存储单元来存储数据。对于指定下标的查找，时间复杂度为 O(1)，但在数组中间以及头部插入数据时，需要复制移动后面的元素。

链表：一种在物理存储单元上非连续、非顺序的存储结构，数据元素的逻辑顺序是通过链表中的指针链接次序实现的。

哈希表：根据关键码值（Key value）直接进行访问的数据结构。通过把关键码值映射到表中一个位置来访问记录，以加快查找的速度。这个映射函数叫做哈希函数，存放记录的数组就叫做哈希表。

树：由 n（n≥1）个有限结点组成的一个具有层次关系的集合，就像是一棵倒挂的树。

**HashMap 的实现结构**

HashMap 是基于哈希表实现的，根据键的 Hash 值来决定对应值的存储位置。

哈希表是怎么解决哈希冲突的呢？

- 开放定址法

  当发生哈希冲突时，如果哈希表未被装满，说明在哈希表中必然还有空位置，那么可以把 key 存放到冲突位置的空位置上去。

  这种方法存在着很多缺点，例如，查找、扩容等，所以我不建议你作为解决哈希冲突的首选。

- 再哈希法

  就是在同义词产生地址冲突时再计算另一个哈希函数地址，直到冲突不再发生。

  这种方法不易产生“聚集”，但却增加了计算时间。如果我们不考虑添加元素的时间成本，且对查询元素的要求极高，就可以考虑使用这种算法设计。

- 链地址法

  这种方法是采用了数组（哈希表）+ 链表的数据结构，当发生哈希冲突时，就用一个链表结构存储相同 Hash 值的数据。

**HashMap 的重要属性**

从 HashMap 的源码中，我们可以发现，HashMap 是由一个 Node 数组构成，每个 Node 包含了一个 key-value 键值对。

```java
transient Node<K,V>[] table;
```

```java
static class Node<K,V> implements Map.Entry<K,V> {
    final int hash;
    final K key;
    V value;
    Node<K,V> next;

    Node(int hash, K key, V value, Node<K,V> next) {
        this.hash = hash;
        this.key = key;
        this.value = value;
        this.next = next;
    }
}
```

HashMap 还有两个重要的属性：加载因子（loadFactor）和边界值（threshold）。

- 加载因子（loadFactor）

  LoadFactor 属性是用来间接设置 Entry 数组（哈希表）的内存空间大小，在初始 HashMap 不设置参数的情况下，默认 LoadFactor 值为 0.75。

  为什么是 0.75 这个值呢？

  因此加载因子越大，对空间的利用就越充分，这就意味着链表的长度越长，查找效率也就越低。如果设置的加载因子太小，那么哈希表的数据将过于稀疏，对空间造成严重浪费。

- 边界值（threshold）

  Entry 数组的 Threshold 是通过初始容量和 LoadFactor 计算所得，在初始 HashMap 不设置参数的情况下，默认边界值为 12。

  如果我们在初始化时，设置的初始化容量较小，HashMap 就会调用 resize() 方法重新分配 table 数组。这将会导致 HashMap 的数组复制，从而影响 HashMap 的效率。

**HashMap 添加元素优化**

从下面源码可以看出，程序首先会根据该 key 的 hashCode() 返回值，通过 hash() 方法计算出 hash 值。

```java
static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
```

再通过 putVal 方法中的 (n - 1) & hash 决定该 Node 的存储位置。

```java
if ((tab = table) == null || (n = tab.length) == 0)
    n = (tab = resize()).length;
// 通过 putVal 方法中的 (n - 1) & hash 决定该 Node 的存储位置
if ((p = tab[i = (n - 1) & hash]) == null)
    tab[i] = newNode(hash, key, value, null);
```

如果我们没有使用 hash() 方法计算 hashCode，而是直接使用对象的 hashCode 值，会出现什么问题呢？

假设要添加两个对象 a 和 b，如果数组长度是 16，这时对象 a 和 b 通过公式 (n - 1) & hash 运算，也就是 (16-1)＆a.hashCode 和 (16-1)＆b.hashCode，15 的二进制为 0000000000000000000000000001111，假设对象 A 的 hashCode 为 1000010001110001000001111000000，对象 B 的 hashCode 为 0111011100111000101000010100000，你会发现上述与运算结果都是 0。这样的哈希结果就太让人失望了，很明显不是一个好的哈希算法。

但如果我们将 hashCode 值右移 16 位（h >>> 16 代表无符号右移 16 位），也就是取 int 类型的一半，刚好可以将该二进制数对半切开，并且使用位异或运算。这样的话，就能尽量打乱 hashCode 真正参与运算的低 16 位。

我再来解释下 (n - 1) & hash 是怎么设计的。哈希表习惯将长度设置为 2 的 n 次方，这样恰好可以保证 (n - 1) & hash 的计算得到的索引值总是位于 table 数组的索引之内，相当于 hash % n，但是前者运算速率更快。

例如：hash=15，n=16 时，结果为 15；hash=17，n=16 时，结果为 1。

在 JDK1.8 中，HashMap 引入了红黑树数据结构来提升链表的查询效率。

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/Java8 HashMap优化.png)

> 图片来源：https://blog.csdn.net/u011240877/article/details/53358305

链表的长度超过 8 后，红黑树的查询效率要比链表高，所以当链表超过 8 时，HashMap 就会将链表转换为红黑树。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/Java8 HashMap数据结构图.jpg" style="zoom: 67%;" />

**HashMap 扩容优化**

在 JDK1.7 中，HashMap 整个扩容过程就是分别取出数组元素，一般该元素是最后一个放入链表中的元素，然后遍历以该元素为头的单向链表元素，依据每个被遍历元素的 hash 值计算其在新数组中的下标，然后进行交换。这样的扩容方式会将原来哈希冲突的单向链表尾部变成扩容后单向链表的头部。

而在 JDK 1.8 中，HashMap 对扩容操作做了优化。由于扩容数组的长度是 2 倍关系，所以对于假设初始 tableSize = 4 要扩容到 8 来说就是 0100 到 1000 的变化（左移一位就是 2 倍），在扩容中只用判断原来的 hash 值和左移动的一位（newtable 的值）按位与操作是 0 或 1 就行，0 的话索引不变，1 的话索引变成原索引加上扩容前数组。

之所以能通过这种“与运算“来重新分配索引，是因为 hash 值本来就是随机的，而 hash 按位与上 newTable 得到的 0（扩容前的索引位置）和 1（扩容前索引位置加上扩容前数组长度的数值索引处）就是随机的，所以扩容的过程就能把之前哈希冲突的元素再随机分布到不同的索引中去。

（没有太理解。）

# 08 | 网络通信优化之I/O模型：如何解决高并发下I/O瓶颈？

**什么是 I/O**

Java 的 I/O 操作类在包 java.io 下，分为4个基本类：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120091642.jpg" style="zoom: 67%;" />

不管是文件读写还是网络发送接收，信息的最小存储单元都是字节，那为什么 I/O 流操作要分为字节流操作和字符流操作呢？

我们知道字符到字节必须经过转码，这个过程非常耗时，如果我们不知道编码类型就很容易出现乱码问题。所以 I/O 流提供了一个直接操作字符的接口，方便我们平时对字符进行流操作。下面我们就分别了解下“字节流”和“字符流”。

- 字节流

  <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120091648.jpg" style="zoom: 50%;" />

  如果是文件的读写操作，就使用 FileInputStream/FileOutputStream；

  如果是数组的读写操作，就使用 ByteArrayInputStream/ByteArrayOutputStream；

  如果是普通字符串的读写操作，就使用 BufferedInputStream/BufferedOutputStream；

- 字符流

  <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120091653.jpg" style="zoom:50%;" />

**传统 I/O 的性能问题**

我们知道，I/O 操作分为磁盘 I/O 操作和网络 I/O 操作。在传统 I/O 中都存在严重的性能问题。

- 多次内存复制

  输入操作在操作系统中的具体流程，如下图所示：

  ![](images/输入操作在操作系统中的具体流程.jpg)

  在这个过程中，数据先从外部设备复制到内核空间，再从内核空间复制到用户空间，这就发生了两次内存复制操作。这种操作会导致不必要的数据拷贝和上下文切换，从而降低 I/O 的性能。

- 阻塞

  在传统 I/O 中，InputStream 的 read() 是一个 while 循环操作，它会一直等待数据读取，直到数据就绪才会返回。这就意味着如果没有数据就绪，这个读取操作将会一直被挂起，用户线程将会处于阻塞状态。

  （通过 jstack 看到是：）

  ![](images/ServerSocket accept方法运行时栈.png)

  在少量连接请求的情况下，使用这种方式没有问题，响应速度也很高。但在发生大量连接请求时，就需要创建大量监听线程，这时如果线程没有数据就绪就会被挂起，然后进入阻塞状态。一旦发生线程阻塞，这些线程将会不断地抢夺 CPU 资源，从而导致大量的 CPU 上下文切换，增加系统的性能开销。

**如何优化 I/O 操作**

JDK1.4 发布了 java.nio 包（new I/O 的缩写），NIO 的发布优化了内存复制以及阻塞导致的严重性能问题。<br>JDK1.7 又发布了 NIO2，提出了从操作系统层面实现的异步 I/O。

下面我们就来了解下具体的优化实现。

- 使用缓冲区优化读写流操作

  传统 I/O 中，提供了基于流的实现以字节为单位处理数据，面向的是流，边读文件边处理数据。

  NIO 与传统 I/O 不同，它是基于块（Block）的，它以块为基本单位处理数据，面向的是Buffer。Buffer 是一块连续的内存块，是 NIO 读写数据的中转地，可以将文件一次性读入内存再做后续处理。

  Channel 表示缓冲数据的源头或者目的地，它用于读取缓冲或者写入数据，是访问缓冲的接口。

- 使用 DirectBuffer 减少内存复制

  DirectBuffer 类可以直接访问物理内存。普通的 Buffer 分配的是 JVM 堆内存，而 DirectBuffer 是直接分配物理内存。

  我们知道数据要输出到外部设备，必须先从用户空间复制到内核空间，再复制到输出设备，而 DirectBuffer 则是直接将步骤简化为从内核空间复制到外部设备，减少了数据拷贝。

- 避免阻塞，优化 I/O 操作

  NIO 发布后，通道和多路复用器这两个基本组件实现了 NIO 的非阻塞，下面我们就一起来了解下这两个组件的优化原理。

  **通道（Channel）：**

  最开始，在应用程序调用操作系统 I/O 接口时，是由 CPU 完成分配，这种方式最大的问题是“发生大量 I/O 请求时，非常消耗 CPU“；

  之后，操作系统引入了 DMA（直接存储器存储），内核空间与磁盘之间的存取完全由 DMA 负责，但这种方式依然需要向 CPU 申请权限，且需要借助 DMA 总线来完成数据的复制操作，如果 DMA 总线过多，就会造成总线冲突。

  通道的出现解决了以上问题，Channel 有自己的处理器，可以完成内核空间和磁盘之间的 I/O 操作。在 NIO 中，我们读取和写入数据都要通过 Channel，由于 Channel 是双向的，所以读、写可以同时进行。

  **多路复用器（Selector）：**

  Selector 是基于事件驱动实现的，我们可以在 Selector 中注册 accpet、read 监听事件，Selector 会不断轮询注册在其上的 Channel，如果某个 Channel 上面发生监听事件，这个 Channel 就处于就绪状态，然后进行 I/O 操作。

  一个线程使用一个 Selector，通过轮询的方式，可以监听多个 Channel 上的事件。我们可以在注册 Channel 时设置该通道为非阻塞，当 Channel 上没有 I/O 操作时，该线程就不会一直等待了，而是会不断轮询所有 Channel，从而避免发生阻塞。

  目前操作系统的 I/O 多路复用机制都使用了 epoll，相比传统的 select 机制，epoll 没有最大连接句柄 1024 的限制。所以 Selector 在理论上可以轮询成千上万的客户端。

**思考题**

在 JDK1.7 版本中，Java 发布了 NIO 的升级包 NIO2，也就是 AIO。AIO 实现了真正意义上的异步 I/O，它是直接将 I/O 操作交给操作系统进行异步处理。这也是对 I/O 操作的一种优化，那为什么现在很多容器的通信框架都还是使用 NIO 呢？

答：在 Linux 中，AIO并未真正使用操作系统所提供的异步I/O，它仍然使用 poll 或 epoll，并将 API 封装为异步 I/O 的样子，但是其本质仍然是同步非阻塞 I/O，加上第三方产品的出现，Java 网络编程明显落后，所以没有成为主流。

# 09 | 网络通信优化之序列化：避免使用Java序列化

**Java 序列化**

Java序列化<br>    |- writeObject() 序列化重写接口<br>    |- readObject() 反序列化重写接口<br>    |- writeReplace() 序列化之前的操作方法，可对序列化之前的对象进行处理<br>    |- readResolve() 在序列化之后的操作方法，可对序列化之后的对象进行处理<br>    |- ObjectOutputStream() 输出流实现序列化<br>    |- ObjectInputStream() 输入流实现反序列化<br>    |- transient 修饰属性，不进行序列化<br>    |- serialVersionUID 版本号，识别相同类对象

ObjectOutputStream 不会序列化对象的 transient 的实例变量，也不会序列化静态变量。

**Java 序列化的缺陷**

- 无法跨语言

  如果是两个基于不同语言编写的应用程序相互通信，则无法实现两个应用服务之间传输对象的序列化与反序列化。

- 易被攻击

  Javav 官网：“对不信任数据的反序列化，从本质上来说是危险的，应该予以避免。”

  例如攻击者可以创建循环对象链，然后将序列化后的对象传输到程序中反序列化，这种情况会导致 hashCode 方法被调用次数呈次方爆发式增长，从而引发栈溢出。

- 序列化后的流太大

  序列化后的二进制数组越大，占用的存储空间就越多，存储硬件的成本就越高。如果是进行网络传输，则占用的带宽就越多，这时就会影响到系统的吞吐量。

  比较一下 Java ObjectOutputStream 和 NIO 中的 ByteBuffer 实现的二进制编码完成的数组大小。

  ```java
  User user = new User();
  user.setUserName("test");
  user.setPassword("test");
  
  ByteArrayOutputStream os =new ByteArrayOutputStream();
  ObjectOutputStream out = new ObjectOutputStream(os);
  out.writeObject(user);
  
  byte[] testByte = os.toByteArray();
  System.out.print("ObjectOutputStream 字节编码长度：" + testByte.length + "\n");
  ```

  ```java
  ByteBuffer byteBuffer = ByteBuffer.allocate( 2048);
  
  byte[] userName = user.getUserName().getBytes();
  byte[] password = user.getPassword().getBytes();
  byteBuffer.putInt(userName.length);
  byteBuffer.put(userName);
  byteBuffer.putInt(password.length);
  byteBuffer.put(password);
  
  byteBuffer.flip();
  byte[] bytes = new byte[byteBuffer.remaining()];
  System.out.print("ByteBuffer 字节编码长度：" + bytes.length+ "\n");
  ```

  运行结果：

  ```
  ObjectOutputStream 字节编码长度：99
  ByteBuffer 字节编码长度：16
  ```

- 序列化性能太差

  Java 序列化与 NIO ByteBuffer 编码的性能对比。

  ```java
  User user = new User();
  user.setUserName("test");
  user.setPassword("test");
  
  long startTime = System.currentTimeMillis();
  for(int i = 0; i < 1000; i++) {
      ByteArrayOutputStream os =new ByteArrayOutputStream();
      ObjectOutputStream out = new ObjectOutputStream(os);
      out.writeObject(user);
      out.flush();
      out.close();
      byte[] testByte = os.toByteArray();
      os.close();
  }
  long endTime = System.currentTimeMillis();
  System.out.print("ObjectOutputStream 序列化时间：" + (endTime - startTime) + "\n");
  ```

  ```java
  long startTime1 = System.currentTimeMillis();
  for(int i = 0; i < 1000; i++) {
      ByteBuffer byteBuffer = ByteBuffer.allocate( 2048);
  
      byte[] userName = user.getUserName().getBytes();
      byte[] password = user.getPassword().getBytes();
      byteBuffer.putInt(userName.length);
      byteBuffer.put(userName);
      byteBuffer.putInt(password.length);
      byteBuffer.put(password);
  
      byteBuffer.flip();
      byte[] bytes = new byte[byteBuffer.remaining()];
  }
  long endTime1 = System.currentTimeMillis();
  System.out.print("ByteBuffer 序列化时间：" + (endTime1 - startTime1)+ "\n");
  ```

  运行结果：

  ```
  ObjectOutputStream 序列化时间：29
  ByteBuffer 序列化时间：6
  ```

**使用 Protobuf 序列化替换 Java 序列化**

最近几年比较流行的 FastJson、Kryo、Protobuf、Hessian 等，都避免了 Java 默认序列化的一些缺陷。

Protobuf 通过 .proto 文件描述来生成 Protocol Buffers 格式的编码。

Protocol Buffers 存储格式是什么样的？（后续专门学习吧，这里看不懂）

**思考题**

这是一个使用单例模式实现的类，如果我们将该类实现 Java 的 Serializable 接口，它还是单例吗？如果要你来写一个实现了 Java 的 Serializable 接口的单例，你会怎么写呢？

```java
public class Singleton implements Serializable{
 
    private final static Singleton singleInstance = new Singleton();
 
    private Singleton() {}
 
    public static Singleton getInstance(){
       return singleInstance; 
    }
}
```

答：序列化会通过反射调用无参构造器返回一个新对象，破坏单例模式。
解决方法是添加`readResolve()`方法，自定义返回对象策略。

# 10 | 网络通信优化之通信协议：如何优化RPC网络通信？

**RPC 服务框架该如何选型？**

目前，很多微服务框架中的服务通信是基于 RPC 通信实现的，在没有进行组件扩展的前提下，SpringCloud 是基于 Feign 组件实现的 RPC 通信（基于 Http+Json 序列化实现），Dubbo 是基于 SPI 扩展了很多 RPC 通信框架，包括 RMI、Dubbo、Hessian 等 RPC 通信框架（默认是 Dubbo+Hessian 序列化）。不同的业务场景下，RPC 通信的选择和优化标准也不同。

我们部门在选择微服务框架时，选择了 Dubbo。当时的选择标准就是 RPC 通信可以支持抢购类的高并发，在这个业务场景中，请求的特点是瞬时高峰、请求量大和传入、传出参数数据包较小。而 Dubbo 中的 Dubbo 协议就很好地支持了这个请求。

以下是基于 Dubbo:2.6.4 版本进行的简单的性能测试。分别测试 Dubbo+Protobuf 序列化以及 Http+Json 序列化的通信性能（这里主要模拟单一 TCP 长连接 +Protobuf 序列化和短连接的 Http+Json 序列化的性能对比）。为了验证在数据量不同的情况下二者的性能表现，我分别准备了小对象和大对象的性能压测，通过这样的方式我们也可以间接地了解下二者在 RPC 通信方面的水平。

![](images/通信协议RT对比.jpg)

![](images/通信协议TPS对比.jpg)

通过以上测试结果可以发现：无论从响应时间还是吞吐量上来看，单一 TCP 长连接 +Protobuf 序列化实现的 RPC 通信框架都有着非常明显的优势。

**什么是 RPC 通信**

你可以通过下面这张图来了解下这些架构的演变史。

![](images/微服务架构演变史.jpg)

无论是微服务、SOA、还是 RPC 架构，它们都是分布式服务架构，都需要实现服务之间的互相通信，我们通常把这种通信统称为 RPC 通信。

**RMI：JDK 自带的 RPC 通信框架**

RMI 实现了一台虚拟机应用对远程方法的调用可以同对本地方法的调用一样，RMI 帮我们封装好了其中关于远程通信的内容。

- RMI 的实现原理

  我们可以通过一张图来详细地了解下整个 RMI 的通信过程：

  ![](images/RMI通信过程.jpg)

- RMI 在高并发场景下的性能瓶颈

  1. Java默认序列化

     RMI 的序列化采用的是 Java 默认的序列化方式，它的性能并不是很好。

  2. TCP 短连接

     RMI 是基于 TCP 短连接实现，在高并发情况下，大量请求会带来大量连接的创建和销毁，这对于系统来说无疑是非常消耗性能的。

  3. 阻塞式网络 I/O

     在高并发场景下基于短连接实现的网络通信就很容易产生 I/O 阻塞，性能将会大打折扣。

**一个高并发场景下的 RPC 通信优化路径**

SpringCloud 的 RPC 通信和 RMI 通信的性能瓶颈就非常相似。SpringCloud 是基于 Http 通信协议（短连接）和 Json 序列化实现的，在高并发场景下并没有优势。 那么，在瞬时高并发的场景下，我们又该如何去优化一个 RPC 通信呢？

RPC 通信包括了建立通信、实现报文、传输协议以及传输数据编解码等操作，接下来我们就从每一层的优化出发，逐步实现整体的性能优化。

1. 选择合适的通信协议

   通过以下两张图，我们可以大概了解到基于 TCP 和 UDP 协议实现的 Socket 网络通信是怎样的一个流程。

   ![](images/TCP和UDP协议通信流程.jpg)

   基于 TCP 协议传输数据是没有边界的，采用的是字节流模式。

   UDP 发送的数据采用的是数据报模式，每个 UDP 的数据报都有一个长度，该长度将与数据一起发送到服务端。

   通过对比，我们可以得出优化方法：为了保证数据传输的可靠性，通常情况下我们会采用 TCP 协议。如果在局域网且对数据传输的可靠性没有要求的情况下，我们也可以考虑使用 UDP 协议，毕竟这种协议的效率要比 TCP 协议高。

2. 使用单一长连接

   基于长连接实现，就可以省去大量的 TCP 建立和关闭连接的操作，从而减少系统的性能消耗，节省时间。

3. 优化 Socket 通信

   实现非阻塞 I/O、使用高效的 Reactor 线程模型、串行设计、零拷贝。

   除了以上这些优化，我们还可以针对套接字编程提供的一些 TCP 参数配置项，提高网络吞吐量，Netty 可以基于 ChannelOption 来设置这些参数。

   - TCP_NODELAY

     TCP_NODELAY 选项是用来控制是否开启 Nagle 算法。Nagle 算法通过缓存的方式将小的数据包组成一个大的数据包，从而避免大量的小数据包发送阻塞网络，提高网络传输的效率。我们可以关闭该算法，优化对于时延敏感的应用场景。

   - SO_RCVBUF 和 SO_SNDBUF

     可以根据场景调整套接字发送缓冲区和接收缓冲区的大小。

   - SO_BACKLOG

     backlog 参数指定了客户端连接请求缓冲队列的大小。服务端处理客户端连接请求是按顺序处理的，所以同一时间只能处理一个客户端连接，当有多个客户端进来的时候，服务端就会将不能处理的客户端连接请求放在队列中等待处理。

   - SO_KEEPALIVE

     当设置该选项以后，连接会检查长时间没有发送数据的客户端的连接状态，检测到客户端断开连接后，服务端将回收该连接。我们可以将该时间设置得短一些，来提高回收连接的效率。

4. 量身定做报文格式

   为了提高传输的效率，我们可以根据自己的业务和架构来考虑设计，尽量实现报体小、满足功能、易解析等特性。我们可以参考下面的数据格式：

   ![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120091743.jpg)

   <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120091659.jpg" style="zoom:67%;" />

5. 编码、解码

   我们可以选择性能相对较好的 Protobuf 序列化，有利于提高网络通信的性能。

6. 调整 Linux 的 TCP 参数设置选项

   如果 RPC 是基于 TCP 短连接实现的，我们可以通过修改 Linux TCP 配置项来优化网络通信。

   我们可以通过 sysctl -a | grep net.xxx 命令运行查看 Linux 系统默认的的 TCP 参数设置，如果需要修改某项配置，可以通过编辑 vim/etc/sysctl.conf，加入需要修改的配置项， 并通过 sysctl -p 命令运行生效修改后的配置项设置。通常我们会通过修改以下几个配置项来提高网络吞吐量和降低延时。

   ![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120091725.jpg)

**思考题**

目前实现 Java RPC 通信的框架有很多，实现 RPC 通信的协议也有很多，除了 Dubbo 协议以外，你还使用过其它 RPC 通信协议吗？通过这讲的学习，你能对比谈谈各自的优缺点了吗？

# 11 | 答疑课堂：深入了解NIO的优化实现原理

**Java NIO**

Socket 通信中的 conect、accept、read 以及 write 为阻塞操作，在 Selector 中分别对应 SelectionKey 的四个监听事件 OP_ACCEPT、OP_CONNECT、OP_READ 以及 OP_WRITE。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120091705.png"  />

在 NIO 服务端通信编程中，首先会创建一个 Channel，用于监听客户端连接；接着，创建多路复用器 Selector，并将 Channel 注册到 Selector，程序会通过 Selector 来轮询注册在其上的 Channel，当发现一个或多个 Channel 处于就绪状态时，返回就绪的监听事件，最后程序匹配到监听事件，进行相关的 I/O 操作。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201120091711.jpg" style="zoom: 80%;" />

在创建 Selector 时，程序会根据操作系统版本选择使用哪种 I/O 复用函数。在 JDK1.5 版本中，如果程序运行在 Linux 操作系统，且内核版本在 2.6 以上，NIO 中会选择 epoll 来替代传统的 select/poll，这也极大地提升了 NIO 通信的性能。

**零拷贝**

Linux 内核中的 mmap 函数可以代替 read、write 的 I/O 读写操作，实现用户空间和内核空间共享一个缓存数据。mmap 将用户空间的一块地址和内核空间的一块地址同时映射到相同的一块物理内存地址，不管是用户空间还是内核空间都是虚拟地址，最终要通过地址映射映射到物理内存地址。这种方式避免了内核空间与用户空间的数据交换。I/O 复用中的 epoll 函数中就是使用了 mmap 减少了内存拷贝。

在 Java 的 NIO 编程中，则是使用到了 Direct Buffer 来实现内存的零拷贝。Java 直接在 JVM 内存空间之外开辟了一个物理内存空间，这样内核和用户进程都能共享一份缓存数据。

