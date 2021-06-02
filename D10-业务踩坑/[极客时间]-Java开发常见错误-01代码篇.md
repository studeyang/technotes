# 01 | 使用了并发工具类库，线程安全就高枕无忧了吗？

我们来看看在使用并发工具时，经常遇到哪些坑，以及如何解决、避免这些坑。

**踩坑1：没有意识到线程重用导致用户信息错乱的 Bug**

- 案例场景

某业务组同学在生产上有时获取到的用户信息是别人的。使用的代码如下。

![image-20210602230951886](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210602230952.png)

- 原因分析

使用了 ThreadLocal 来缓存获取到的用户信息。程序运行在 Tomcat 中，Tomcat 的工作线程是基于线程池的。

- 解决方案

![image-20210602231311621](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210602231311.png)

**踩坑2：使用了线程安全的并发工具，并不代表解决了所有线程安全问题**

- 案例场景

有一个含 900 个元素的 Map，现在再补充 100 个元素进去，这个补充操作由 10 个线程并发进行。

![image-20210602231944461](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210602231944.png)

![image-20210602232005717](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210602232005.png)

- 解决方案

![image-20210602233230575](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210602233230.png)

**踩坑3：没有充分了解并发工具的特性，从而无法发挥其威力**

- 案例场景

使用 Map 来统计 Key 出现的次数。

使用 ConcurrentHashMap 来统计，Key 的范围是 10；

使用最多 10 个并发，循环操作 1000 万次，每次操作累加随机的 Key；

如果 Key 不存在的话，首次设置值为 1。

![image-20210602233956556](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210602233956.png)