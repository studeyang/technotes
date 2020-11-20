# 开篇词：JVM，一块难啃的骨头

1. 基础原理（01-04）：主要讲解 JVM 基础概念，以及内存区域划分和类加载机制等。最后，会根据需求实现一个自定义类加载器。
2. 垃圾回收（05-08）：Java 中有非常丰富的垃圾回收器，此部分以理论为主，是通往高级工程师之路无法绕过的知识点。我会横向比较工作中常用的垃圾回收器并以主题深入的方式讲解 G1、GMS、ZGC 等主流垃圾回收器。
3. 实战部分（09-16）：我会模拟工作中涉及的 OOM 溢出全场景，用 23 个大型工作实例分析线上问题，并针对这些问题提供排查的具体工具的使用介绍，还会提供一个高阶的对堆外内存问题的排查思路。
4. 进阶部分（17-23）：介绍 JMM，以及从字节码层面来剖析 Java 的基础特性以及并发方面的问题。还会重点分析应用较多的 Java Agent 技术。这部分内容比较底层，可以加深我们对 Java 底层实现的理解。
5. 彩蛋（24-25）：带你回顾 JVM 的历史并展望未来，即使 JVM 版本不断革新也能够洞悉未来掌握先机，最后会给你提供一份全面的 JVM 面试题，助力高级 Java 岗位面试。

------

第一部分 基础原理（01-04）

# 第01讲：一探究竟：为什么需要 JVM？它处在什么位置？

**Java 虚拟机规范和 Java 语言规范的关系**

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/CgpOIF4UXzOAbzFUAAAhKnX7ea0980.png" style="zoom:50%;" />

Java 虚拟机规范，其实就是为输入和执行字节码提供一个运行环境。Java 语法规范，比如 switch、for、泛型、lambda 等相关的程序，最终都会编译成字节码。而连接左右两部分的桥梁依然是 Java 的字节码。

**Java 代码到底是如何运行起来的？**

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello World");
    }
}
```

使用 JDK 的工具 javac 进行编译后，会产生 HelloWorld 的字节码。下面使用 javap 来稍微看一下字节码到底长什么样子。

```text
0 getstatic     #2 <java/lang/System.out>
3 ldc           #3 <Hello World>
5 invokevirtual #4 <java/io/PrintStream.println>
8 return
```

Java 指令由操作码和操作数组成。这些字节码指令，就叫作 opcode，getstatic、ldc、invokevirtual、return 等，就是 opcode。

我们继续使用 hexdump 看一下字节码的二进制内容。

```text
b2 00 02 12 03 b6 00 04 b1
```

它们的对应关系如下。

```text
0xb2   getstatic       获取静态字段的值
0x12   ldc             常量池中的常量值入栈
0xb6   invokevirtual   运行时方法绑定调用方法
0xb1   return          void 函数返回
```

opcode 有一个字节的长度(0~255)，意味着指令集的操作码个数不能操作 256 条。而紧跟在 opcode 后面的是被操作数。比如 b2 00 02，就代表了 getstatic #2 <java/lang/System.out>。

JVM 就是靠解析这些 opcode 和操作数来完成程序的执行的。当我们使用 Java 命令运行 .class 文件的时候，实际上就相当于启动了一个 JVM 进程。

# 第02讲：大厂面试题：你不得不掌握的 JVM 内存管理

> - JVM 是如何进行内存区域划分的？
>
> - JVM 如何高效进行内存管理？
>
> - 为什么需要有元空间，它又涉及什么问题？

**JVM 内存布局**

Java 8 及之后的版本，彻底移除了持久代，而使用 Metaspace 来进行替代。这也表示着 -XX:PermSize 和 -XX:MaxPermSize 等参数调优，已经没有了意义。

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/Cgq2xl4VrjWAPqAuAARqnz6cigo666.png)

**虚拟机栈**

在每个 Java 方法被调用的时候，都会创建一个栈帧，并入栈。一旦完成相应的调用，则出栈。所有的栈帧都出栈后，线程也就结束了。每个栈帧，都包含四个区域：局部变量表、操作数栈、动态连接、返回地址。

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/Cgq2xl4VrjWABK2qAATDn4DQbvE629.png)

**程序计数器**

如果我们的程序在线程之间进行切换，就代表它在获取 CPU 时间片上，是不可预知的，需要有一个地方，对线程正在运行的点位进行缓冲记录，以便在获取 CPU 时间片时能够快速恢复。

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/Cgq2xl4VrjaANruFAAQKxZvgfSs652.png)

可以看到，程序计数器也是因为线程而产生的，与虚拟机栈配合完成计算操作。程序计数器还存储了当前正在运行的流程，包括正在执行的指令、跳转、分支、循环、异常处理等。

**堆（Heap）**

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/Cgq2xl4VrjaAXnuQAANJIXDvNhI844.png)

Java 的对象可以分为基本数据类型和普通对象。

对于普通对象来说，JVM 会首先在堆上创建对象，然后在其他地方使用的其实是它的引用。

对于基本数据类型来说（byte、short、int、long、float、double、boolean、char)，当你在方法体内声明了基本数据类型的对象，它就会在栈上直接分配，其他情况，都是在堆上分配。

> 注意，像 int[] 数组这样的内容，是在堆上分配的。数组并不是基本数据类型。

**元空间**

在 Java 8 之前，这些类的信息是放在一个叫 Perm 区的内存里面的，这个区域有大小限制，很容易造成 JVM 内存溢出，从而造成 JVM 崩溃。

Perm 区在 Java 8 中已经被彻底废除，取而代之的是 Metaspace。原来的 Perm 区是在堆上的，现在的元空间是在非堆上的。可以看下这张图。

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/Cgq2xl4VrjaAIlgaAAJKReuKXII670.png)

元空间的好处也是它的坏处。使用非堆可以使用操作系统的内存，JVM 不会再出现方法区的内存溢出；但是，无限制的使用会造成操作系统的死亡。所以，一般也会使用参数 -XX:MaxMetaspaceSize 来控制大小。

# 第03讲：大厂面试题：从覆盖 JDK 的类开始掌握类的加载机制

> - 我们能够通过一定的手段，覆盖 HashMap 类的实现么？
> - 有哪些地方打破了 Java 的类加载机制？
> - 如何加载一个远程的 .class 文件？怎样加密 .class 文件？

**类加载过程**

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/Cgq2xl4cQNeAO_j6AABZKdVbw1w802.png" style="zoom:67%;" />

- 加载

  加载的主要作用是将外部的 .class 文件，加载到 Java 的方法区内。

- 验证

  不符合规范的将抛出 java.lang.VerifyError 错误。像一些低版本的 JVM，是无法加载一些高版本的类库的，就是在这个阶段完成的。

- 准备

  为一些类变量分配内存，并将其初始化为默认值。

- 解析

  将符号引用替换为直接引用的过程。几个经常发生的异常，就与这个阶段有关。

  ```text
  java.lang.NoSuchFieldError   根据继承关系从下往上，找不到相关字段时的报错。
  java.lang.IllegalAccessError 字段或者方法，访问权限不具备时的错误。
  java.lang.NoSuchMethodError  找不到相关方法时的错误。
  ```

- 初始化

  初始化成员变量，执行\<cinit\> 方法。

  \<cinit\> 方法和 \<init\> 方法有什么区别？

  ![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/CgpOIF4cQNeAYYhRAADbeRet_7k581.png)

**类加载器**

- Bootstrap ClassLoader

  -Xbootclasspath 参数可以完成指定操作。

- Extention ClassLoader

  系统变量 java.ext.dirs 可以指定这个目录。

- App ClassLoader

  用来加载 classpath 下的其他所有 jar 包和 .class 文件。

- Custom ClassLoader

  自定义加载器，支持一些个性化的扩展功能。

**双亲委派机制**

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/Cgq2xl4cQNeAG0ECAAA_CbVCY1M014.png" style="zoom:67%;" />

比如 Object 类，这个毫无疑问应该交给最上层的加载器进行加载，即使是你覆盖了它，最终也是由系统默认的加载器进行加载的。

如果没有双亲委派模型，就会出现很多个不同的 Object 类，应用程序会一片混乱。

**一些自定义加载器**

下面我们就来聊一聊可以打破双亲委派机制的一些案例。

- 案例一：tomcat

  <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/Cgq2xl4cQNeAZ4FuAABzsqSozok762.png" style="zoom:80%;" />

  那么 tomcat 是怎么打破双亲委派机制的呢？可以看图中的 WebAppClassLoader，它加载自己目录下的 .class 文件，并不会传递给父类的加载器。但是，它却可以使用 SharedClassLoader 所加载的类，实现了共享和分离的功能。

**如何替换 JDK 的类**

比如，我们现在就拿 HashMap为例。我们需要将自己的 HashMap 类，打包成一个 jar 包，然后放到 -Djava.endorsed.dirs 指定的目录中。

# 第04讲：动手实践：从栈帧看字节码是如何在 JVM 中进行流转的

> - 怎么查看字节码文件？
> - 字节码文件长什么样子？
> - 对象初始化之后，具体的字节码又是怎么执行的？

**工具介绍**

- javap

  在使用 javap 时我一般会添加 -v 参数，尽量多打印一些信息。同时，我也会使用 -p 参数，打印一些私有的字段和方法。

- jclasslib

  jclasslib 是一个图形化的工具，它还提供了 Idea 的插件，你可以从 plugins 中搜索到它。jclasslib 的下载地址：https://github.com/ingokegel/jclasslib

**类加载和对象创建的时机**

```java
class B {
    private int a = 1234;
    static long C = 1111;
    public long test(long num) {
        long ret = this.a + num + C;
        return ret;
    }
}
public class A {
    private B b = new B();
    public static void main(String[] args) {
        A a = new A();
        long num = 4321 ;
        long ret = a.b.test(num);
        System.out.println(ret);
    }
}
```

那对象都有哪些创建方式呢？除了我们常用的 new，还有下面这些方式：

- 使用 Class 的 newInstance 方法。
- 使用 Constructor 类的 newInstance 方法。
- 反序列化。
- 使用 Object 的 clone 方法。

上面执行 A 代码，在调用 private B b = new B() 时，就会触发 B 类的加载。

（未完）

------

第二部分 垃圾回收（05-08）

# 第05讲：大厂面试题：得心应手应对 OOM 的疑难杂症

**GC Roots 有哪些**

这些 GC Roots 大体可以分为三大类，下面这种说法更加好记一些：

- 活动线程相关的各种引用。
- 类的静态变量的引用。
- JNI 引用。

![](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/Cgq2xl4hefWAWKFZAAMwndGjScg437.png)

**引用级别**

- 强引用 Strong references
- 软引用 Soft references
- 弱引用 Weak references
- 虚引用 Phantom References。主要用来跟踪对象被垃圾回收的活动。

**典型 OOM 场景**

OOM 到底是什么引起的呢？有几个原因：

- 内存的容量太小了，需要扩容，或者需要调整堆的空间。
- 错误的引用方式，发生了内存泄漏。没有及时的切断与 GC Roots 的关系。比如线程池里的线程，在复用的情况下忘记清理 ThreadLocal 的内容。
- 接口没有进行范围校验，外部传参超出范围。比如数据库查询时的每页条数等。
- 对堆外内存无限制的使用。这种情况一旦发生更加严重，会造成操作系统内存耗尽。

# 第06讲：深入剖析：垃圾回收你真的了解吗？（上）

> - JVM 中有哪些垃圾回收算法？它们各自有什么优劣？
> - CMS 垃圾回收器是怎么工作的？有哪些阶段？
> - 服务卡顿的元凶到底是谁？

本课时将首先介绍几种非常重要的回收算法，然后着重介绍分代垃圾回收的内存划分和 GC 过程，最后介绍当前 JVM 中的几种常见垃圾回收器。

**垃圾回收算法**

- 标记-清除（Mark-Sweep）

  找出活跃的对象，把未被标记的对象回收掉。

  效率一般，缺点是会造成内存碎片问题。

- 复制算法（Copy）

  将存活的对象复制过去，然后清除原内存空间。

  复制算法是所有算法里面效率最高的，缺点是会造成一定的空间浪费。

- 标记-整理（Mark-Compact）

  找出活跃的对象，移动所有存活的对象，且按照内存地址顺序依次排列，然后将末端内存地址以后的内存全部回收。

  效率比前两者要差，但没有空间浪费，也消除了内存碎片问题。

**分代（年轻代&老年代）**

- 年轻代

  年轻代使用的垃圾回收算法是复制算法。因为年轻代发生 GC 后，只会有非常少的对象存活，复制这部分对象是非常高效的。

- 老年代

  老年代一般使用“标记-清除”、“标记-整理”算法，因为老年代的对象存活率一般是比较高的，空间又比较大，拷贝起来并不划算，还不如采取就地收集的方式。

有的对象可能在 Eden 区，有的可能在老年代，那么这种跨代的引用是如何处理的呢？

老年代是被分成众多的卡页（card page），卡表（Card Table）就是用于标记卡页状态的一个集合，每个卡表项对应一个卡页。如果年轻代有对象分配，而且老年代有对象指向这个新对象， 那么这个老年代对象所对应内存的卡页，就会标识为 dirty，卡表只需要非常小的存储空间就可以保留这些状态。垃圾回收时，就可以先读这个卡表，进行快速判断。

**HotSpot 垃圾回收器**

年轻代垃圾回收器

- Serial 垃圾收集器

  处理 GC 的只有一条线程。

- ParNew 垃圾收集器

  ParNew 是 Serial 的多线程版本。

- Parallel Scavenge 垃圾收集器

  追求 CPU 吞吐量。

老年代垃圾收集器

- Serial Old 垃圾收集器

  与年轻代的 Serial 垃圾收集器对应。

- Parallel Old

  Parallel Old 收集器是 Parallel Scavenge 的老年代版本，追求 CPU 吞吐量。

- CMS 垃圾收集器

  CMS（Concurrent Mark Sweep）收集器是以获取最短 GC 停顿时间为目标的收集器，它在垃圾收集时使得用户线程和 GC 线程能够并发执行，因此在垃圾收集过程中用户也不会感到明显的卡顿。

除了上面几个垃圾回收器，我们还有 G1、ZGC 等更加高级的垃圾回收器，它们都有专门的配置参数来使其生效。以下是一些配置参数：

- -XX:+UseSerialGC 年轻代和老年代都用串行收集器

- -XX:+UseParNewGC 年轻代使用 ParNew，老年代使用 Serial Old

- **-XX:+UseParallelGC 年轻代使用 Parallel Scavenge，老年代使用 Serial Old**

  >  Java8 默认使用

- -XX:+UseParallelOldGC 新生代和老年代都使用并行收集器

- -XX:+UseConcMarkSweepGC，表示年轻代使用 ParNew，老年代的用 CMS

- -XX:+UseG1GC 使用 G1垃圾回收器

- -XX:+UseZGC 使用 ZGC 垃圾回收器

**stop-the-world**

标记阶段，大多数是要 STW 的。如果不暂停用户进程，在标记对象的时候，有可能有其他用户线程会产生一些新的对象和引用，造成混乱。

# 第06讲：CMS 垃圾回收器

我们在这一课时重点讲解上一课时中提到的 CMS 垃圾回收器，让你可以更好的理解垃圾回收的过程。

在这里首先给你介绍几个概念：

- Minor GC：发生在年轻代的 GC。
- Major GC：发生在老年代的 GC。
- Full GC：全堆垃圾回收。比如 Metaspace 区引起年轻代和老年代的回收。

CMS 并发­标记­清除­垃圾收集器，它在年轻代使用复制算法，而对老年代使用标记-清除算法。CMS 的设计目标，是避免在老年代 GC 时出现长时间的卡顿）。如果你不希望有长时间的停顿，同时你的 CPU 资源也比较丰富，使用 CMS 是比较合适的。

它的主要问题是碎片化。随着 JVM 的长时间运行，碎片化会越来越严重，只有通过 Full GC 才能完成整理。

**CMS 回收过程**

- 初始标记（Initial Mark）

  初始标记阶段，只标记直接关联 GC root 的对象，不用向下追溯。因为最耗时的就在 tracing 阶段，这样就极大地缩短了初始标记时间。

- 并发标记（Concurrent Mark）

  主要是 tracinng 的过程，用于标记所有可达的对象。这个过程会持续比较长的时间，但却可以和用户线程并行。

- 并发预清理（Concurrent Preclean）

  由于这个阶段也是可以并发的，在执行过程中引用关系依然会发生一些变化。

- 并发可取消的预清理（Concurrent Abortable Preclean）

  在满足某些条件的时候，可以终止，比如迭代次数、有用工作量、消耗的系统时间等。

- 最终标记（Final Remark）

  完成老年代中所有存活对象的标记。

- 并发清除（Concurrent Sweep）

  删掉不可达的对象，并回收它们的空间。

- 并发重置（Concurrent Reset）

  此阶段与应用程序并发执行，重置 CMS 算法相关的内部数据，为下一次 GC 循环做准备。

**内存碎片**

由于 CMS 在执行过程中，用户线程还需要运行，那就需要保证有充足的内存空间供用户使用。这部分空间预留，一般在 30% 左右即可。

另外，CMS 对老年代回收的时候，并没有内存的整理阶段。这就造成程序在长时间运行之后，碎片太多。如果你申请一个稍大的对象，就会引起分配失败。

CMS 提供了两个参数来解决这个问题：

（1） UseCMSCompactAtFullCollection（默认开启），表示在要进行 Full GC 的时候，进行内存碎片整理。内存整理的过程是无法并发的，所以停顿时间会变长。

（2）CMSFullGCsBeforeCompaction，每隔多少次不压缩的 Full GC 后，执行一次带压缩的 Full GC。默认值为 0，表示每次进入 Full GC 时都进行碎片整理。

**总结**

优势：

低延迟，尤其对于大堆来说。大部分垃圾回收过程并发执行。

劣势：

内存碎片问题。Full GC 的整理阶段，会造成较长时间的停顿。

需要预留空间，用来分配收集阶段产生的“浮动垃圾”。

使用更多的 CPU 资源，在应用运行的同时进行堆扫描。

# 第07讲：有了 G1 还需要其他垃圾回收器吗？

> - G1 的回收原理是什么？为什么 G1 比传统 GC 回收性能好？
> - 为什么 G1 如此完美仍然会有 ZGC？

