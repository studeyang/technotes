# 目录

![](并发工具类.png)



------

第二部分：并发工具类 (14讲)

# 14 | Lock：隐藏在并发包中的管程

Java SDK 并发包通过 Lock 和 Condition 两个接口来实现管程，其中 Lock 用于解决互斥问题，Condition 用于解决同步问题。synchronized 也是管程的一种实现，很显然它们之间是有巨大区别的。那区别在哪里呢？

**再造管程的理由**

我们前面在介绍死锁问题的时候，提出了一个**破坏不可抢占条件**方案，但是这个方案 synchronized 没有办法解决。原因是 synchronized 申请资源的时候，如果申请不到，线程直接进入阻塞状态了，而线程进入阻塞状态，啥都干不了，也释放不了线程已经占有的资源。但我们希望的是：

> 对于“不可抢占”这个条件，占用部分资源的线程进一步申请其他资源时，如果申请不到，可以主动释放它占有的资源，这样不可抢占这个条件就破坏掉了。

如果我们重新设计一把互斥锁去解决这个问题，那该怎么设计呢？我觉得有三种方案。

1. **能够响应中断**。synchronized 的问题是，持有锁 A 后，如果尝试获取锁 B 失败，那么线程就进入阻塞状态，一旦发生死锁，就没有任何机会来唤醒阻塞的线程。但如果阻塞状态的线程能够响应中断信号，也就是说当我们给阻塞的线程发送中断信号的时候，能够唤醒它，那它就有机会释放曾经持有的锁 A。这样就破坏了不可抢占条件了。
2. **支持超时**。如果线程在一段时间之内没有获取到锁，不是进入阻塞状态，而是返回一个错误，那这个线程也有机会释放曾经持有的锁。这样也能破坏不可抢占条件。
3. **非阻塞地获取锁**。如果尝试获取锁失败，并不进入阻塞状态，而是直接返回，那这个线程也有机会释放曾经持有的锁。这样也能破坏不可抢占条件。

这三种方案可以全面弥补 synchronized 的问题。也就是“重复造轮子”的主要原因。Lock接口有三个方法：

```java
// 支持中断的 API
void lockInterruptibly() throws InterruptedException;
// 支持超时的 API
boolean tryLock(long time, TimeUnit unit) throws InterruptedException;
// 支持非阻塞获取锁的 API
boolean tryLock();
```

**如何保证可见性**

你已经知道 Java 里多线程的可见性是通过 Happens-Before 规则保证的，而 synchronized 之所以能够保证可见性，也是因为有一条 synchronized 相关的规则：synchronized 的解锁 Happens-Before 于后续对这个锁的加锁。那 Java SDK 里面 Lock 靠什么保证可见性呢？例如在下面的代码中，线程 T1 对 value 进行了 +=1 操作，那后续的线程 T2 能够看到 value 的正确结果吗？

```java
class X {
    private final Lock rtl = new ReentrantLock();
    int value;
    public void addOne() {
        // 获取锁
        rtl.lock();  
        try {
            value+=1;
        } finally {
            // 保证锁能释放
            rtl.unlock();
        }
    }
}
```

答案必须是肯定的。**Java SDK 里面锁**的原理是**利用了 volatile 相关的 Happens-Before 规则**。

 ReentrantLock，内部持有一个 volatile 的成员变量 state，获取锁的时候，会读写 state 的值；解锁的时候，也会读写 state 的值（简化后的代码如下面所示）。

```java
class SampleLock {
    volatile int state;
    // 加锁
    lock() {
        // 省略代码无数
        state = 1;
    }
    // 解锁
    unlock() {
        // 省略代码无数
        state = 0;
    }
}
```

也就是说，在执行 value+=1 之前，程序先读写了一次 volatile 变量 state，在执行 value+=1 之后，又读写了一次 volatile 变量 state。根据相关的 Happens-Before 规则：

1. **顺序性规则**：对于线程 T1，value += 1 Happens-Before 释放锁的操作 unlock()；
2. **volatile 变量规则**：由于 state = 1 会先读取 state，所以线程 T1 的 unlock() 操作 Happens-Before 线程 T2 的 lock() 操作；
3. **传递性规则**：线程 T1 的 value +=1 Happens-Before 线程 T2 的 lock() 操作。

**深入理解 Lock 锁**

Lock 锁是基于 Java 实现的锁，Lock 是一个接口类，常用的实现类有 ReentrantLock、ReentrantReadWriteLock（RRW），它们都是依赖 AbstractQueuedSynchronizer（AQS）类实现的。

详细可参考 [多线程性能调优](../B-10%20性能调优/[极客时间]-性能调优实战-02多线程调优.md) 《第13讲 | 多线程之锁优化（中）：深入理解 Lock 同步锁优化方法》

**什么是可重入锁**

**所谓可重入锁，顾名思义，指的是线程可以重复获取同一把锁**。例如下面代码中，当线程 T1 执行到【1】处时，已经获取到了锁 rtl ，当在【1】处调用 get() 方法时，会在【2】再次对锁 rtl 执行加锁操作。此时，如果锁 rtl 是可重入的，那么线程 T1 可以再次加锁成功；如果锁 rtl 是不可重入的，那么线程 T1 此时会被阻塞。

```java
class X {
  private final Lock rtl = new ReentrantLock();
  int value;
  public int get() {
    // 获取锁
    rtl.lock();         // 2
    try {
      return value;
    } finally {
      // 保证锁能释放
      rtl.unlock();
    }
  }
  public void addOne() {
    // 获取锁
    rtl.lock();  
    try {
      value = 1 + get(); // 1
    } finally {
      // 保证锁能释放
      rtl.unlock();
    }
  }
}
```

除了可重入锁，可能你还听说过可重入函数，可重入函数怎么理解呢？

所谓**可重入函数，指的是多个线程可以同时调用该函数**，每个线程都能得到正确结果；同时在一个线程内支持线程切换，无论被切换多少次，结果都是正确的。多线程可以同时执行，还支持线程切换，这意味着什么呢？线程安全啊。所以，可重入函数是线程安全的。

**公平锁与非公平锁**

ReentrantLock 这个类有两个构造函数，一个是无参构造函数，一个是传入 fair 参数的构造函数。fair 参数代表的是锁的公平策略，如果传入 true 就表示需要构造一个公平锁，反之则表示要构造一个非公平锁。

```java
// 无参构造函数：默认非公平锁
public ReentrantLock() {
    sync = new NonfairSync();
}
// 根据公平策略参数创建锁
public ReentrantLock(boolean fair) {
    sync = fair ? new FairSync() : new NonfairSync();
}
```

在前面《08 | 管程：并发编程的万能钥匙》中，我们介绍过入口等待队列，锁都对应着一个等待队列，如果一个线程没有获得锁，就会进入等待队列，当有线程释放锁的时候，就需要从等待队列中唤醒一个等待的线程。如果是公平锁，唤醒的策略就是谁等待的时间长，就唤醒谁，很公平；如果是非公平锁，则不提供这个公平保证，有可能等待时间短的线程反而先被唤醒。

**用锁的最佳实践**

最值得推荐的是并发大师 Doug Lea《Java 并发编程：设计原则与模式》一书中，推荐的三个用锁的最佳实践，它们分别是：

1. 永远只在更新对象的成员变量时加锁；
2. 永远只在访问可变的成员变量时加锁；
3. 永远不在调用其他对象的方法时加锁；

最后一条你可能会觉得过于严苛，因为调用其他对象的方法，实在是太不安全了，也许“其他”方法里面有线程 sleep() 的调用，也可能会有奇慢无比的 I/O 操作，这些都会严重影响性能。更可怕的是，“其他”类的方法可能也会加锁，然后双重加锁就可能导致死锁。

**课后思考**

你已经知道 tryLock() 支持非阻塞方式获取锁，下面这段关于转账的程序就使用到了 tryLock()，你来看看，它是否存在死锁问题呢？

```java
class Account {
    private int balance;
    private final Lock lock = new ReentrantLock();
    // 转账
    void transfer(Account tar, int amt) {
        while (true) {
            if (this.lock.tryLock()) {
                try {
                    if (tar.lock.tryLock()) {
                        try {
                            this.balance -= amt;
                            tar.balance += amt;
                        } finally {
                            tar.lock.unlock();
                        }
                    }//if
                } finally {
                    this.lock.unlock();
                }
            }//if
        }//while
    }//transfer
}
```

我的解读：甲拿到了A账本，同时乙拿到了B账本。甲看B账本不在，立即放回账本架，乙看A账本不在，也立即放回账本架。一直这样循环发生活锁。

# 15 | Condition：Dubbo如何用管程实现异步转同步？

在上一篇文章中，我们讲到 Java SDK 并发包里的 Lock 有别于 synchronized 隐式锁的三个特性：能够响应中断、支持超时和非阻塞地获取锁。那今天我们接着再来详细聊聊 Java SDK 并发包里的 Condition，**Condition 实现了管程模型里面的条件变量**。

Java 语言内置的管程与 Lock&Condition 实现的管程的区别：前者只有一个条件变量，而后者是支持多个条件变量的。

**那如何利用两个条件变量快速实现阻塞队列呢？**

这个例子我们前面在介绍管程的时候详细说过。

注意：

Lock&Condition 实现的管程里只能使用 await()、signal()、signalAll()<br>synchronized 实现的管程里才能使用  wait()、notify()、notifyAll()。

切不可在 Lock&Condition 实现的管程里调用 wait()、notify()、notifyAll()。

下面我们就来看看在知名项目 Dubbo 中，Lock 和 Condition 是怎么用的。不过在开始介绍源码之前，我还先要介绍两个概念：同步和异步。

**同步与异步**

通俗点来讲就是调用方是否需要等待结果，如果需要等待结果，就是同步；如果不需要等待结果，就是异步。

两种方式来实现异步：

1. 调用方创建一个子线程，在子线程中执行方法调用，这种调用我们称为异步调用；

   ```java
   new Thread(
       @Override
       public void run() {
           pai1M();
       }
   ).start();
   printf("hello world")
   ```

2. 方法实现的时候，创建一个新的线程执行主要逻辑，主线程直接 return，这种方法我们一般称为异步方法。

   ```java
   new Thread(
       @Override
       public void run() {
           // 逻辑代码
       }
   ).start();
   return "";
   ```

**Dubbo 源码分析**

在编程领域，异步的场景还是挺多的，比如 TCP 协议本身就是异步的，我们工作中经常用到的 RPC 调用，**在 TCP 协议层面，发送完 RPC 请求后，线程是不会等待 RPC 的响应结果的**。可能你会觉得奇怪，平时工作中的 RPC 调用大多数都是同步的啊？这是怎么回事呢？

其实很简单，一定是有人帮你做了异步转同步的事情。那它是怎么做的呢？

对于下面一个简单的 RPC 调用，默认情况下 sayHello() 方法，是个同步方法，也就是说，执行`service.sayHello(“dubbo”)`的时候，线程会停下来等结果。

```java
DemoService service = 初始化部分省略
String message = service.sayHello("dubbo");
System.out.println(message);
```

如果此时你将调用线程 dump 出来的话，会是下图这个样子。

![调用栈信息](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/调用栈信息.png)

本来发送请求是异步的，但是调用线程却阻塞了，说明 Dubbo 帮我们做了异步转同步的事情。通过调用栈，你能看到线程是阻塞在 DefaultFuture.get() 方法上，所以可以推断：Dubbo 异步转同步的功能应该是通过 DefaultFuture 这个类实现的。

不过为了理清前后关系，还是有必要分析一下调用 DefaultFuture.get() 之前发生了什么。DubboInvoker 的 108 行调用了 DefaultFuture.get()，这一行很关键，我稍微修改了一下列在了下面。这一行先调用了 request(inv, timeout) 方法，这个方法其实就是发送 RPC 请求，之后通过调用 get() 方法等待 RPC 返回结果。

```java
public class DubboInvoker {
  Result doInvoke(Invocation inv) {
    // 下面这行就是源码中 108 行
    // 为了便于展示，做了修改
    return currentClient.request(inv, timeout).get();
  }
}
```

DefaultFuture 这个类是很关键，我把相关的代码精简之后，列到了下面。不过在看代码之前，你还是有必要重复一下我们的需求：当 RPC 返回结果之前，阻塞调用线程，让调用线程等待；当 RPC 返回结果后，唤醒调用线程，让调用线程重新执行。不知道你有没有似曾相识的感觉，这不就是经典的等待 - 通知机制吗？这个时候想必你的脑海里应该能够浮现出管程的解决方案了。有了自己的方案之后，我们再来看看 Dubbo 是怎么实现的。

```java
// 创建锁与条件变量
private final Lock lock = new ReentrantLock();
private final Condition done = lock.newCondition();
 
// 调用方通过该方法等待结果
Object get(int timeout) {
  long start = System.nanoTime();
  lock.lock();
  try {
	while (!isDone()) {
	  done.await(timeout);
      long cur = System.nanoTime();
	  if (isDone() || cur - start > timeout) {
	    break;
	  }
	}
  } finally {
	lock.unlock();
  }
  if (!isDone()) {
	throw new TimeoutException();
  }
  return returnFromResponse();
}
// RPC 结果是否已经返回
boolean isDone() {
  return response != null;
}
// RPC 结果返回时调用该方法   
private void doReceived(Response res) {
  lock.lock();
  try {
    response = res;
    if (done != null) {
      done.signal();
    }
  } finally {
    lock.unlock();
  }
}
```

调用线程通过调用 get() 方法等待 RPC 返回结果，当 RPC 结果返回时，会调用 doReceived() 方法，这个方法里面，调用 lock() 获取锁，在 finally 里面调用 unlock() 释放锁，获取锁后通过调用 signal() 来通知调用线程，结果已经返回，不用继续等待了。

**总结**

 Java SDK 并发包里锁和条件变量是如何实现的？可以参考《Java 并发编程的艺术》一书的第 5 章《Java 中的锁》。

Dubbo 的源代码在[Github](https://github.com/apache/incubator-dubbo)上。

**课后思考**

DefaultFuture 里面唤醒等待的线程，用的是 signal()，而不是 signalAll()，你来分析一下，这样做是否合理呢？

答：不合理，会导致很多请求超时，看了源码是调用 signalAll()。

作者回复: 写这一章的时候还是 signal，后来有人提了个 bug，就改成 signalAll 了。

# 16 | Semaphore：如何快速实现一个限流器？

信号量是由大名鼎鼎的计算机科学家迪杰斯特拉（Dijkstra）于 1965 年提出，在这之后的 15 年，信号量一直都是并发编程领域的终结者，直到 1980 年管程被提出来，我们才有了第二选择。目前几乎所有支持并发编程的语言都支持信号量机制，所以学好信号量还是很有必要的。

下面我们首先介绍信号量模型，之后介绍如何使用信号量，最后我们再用信号量来实现一个限流器。

**信号量模型**

信号量模型可以简单概括为：**一个计数器，一个等待队列，三个方法**。在信号量模型里，计数器和等待队列对外是不可见的，所以只能通过信号量模型提供的三个方法来访问它们，这三个方法分别是：init()、down() 和 up()。你可以结合下图来形象化地理解。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/信号量模型图.png" alt="信号量模型图" style="zoom:67%;" />

这三个方法详细的语义具体如下所示。

- init()：设置计数器的初始值。
- down()：计数器的值减 1；如果此时计数器的值小于 0，则当前线程将被阻塞，否则当前线程可以继续执行。
- up()：计数器的值加 1；如果此时计数器的值小于或者等于 0，则唤醒等待队列中的一个线程，并将其从等待队列中移除。

这里提到的 init()、down() 和 up() 三个方法都是原子性的，并且这个原子性是由信号量模型的实现方保证的。在 Java SDK 里面，信号量模型是由 java.util.concurrent.Semaphore 实现的，Semaphore 这个类能够保证这三个方法都是原子操作。

可以参考下面这个代码化的信号量模型。

```java
class Semaphore {
    // 计数器
    int count;
    // 等待队列
    Queue queue;
    // 初始化操作
    Semaphore(int c) {
        this.count = c;
    }
    // 
    void down() {
        this.count--;
        if(this.count < 0) {
            // 将当前线程插入等待队列
            // 阻塞当前线程
        }
    }
    void up() {
        this.count++;
        if(this.count <= 0) {
            // 移除等待队列中的某个线程 T
            // 唤醒线程 T
        }
    }
}
```

信号量模型里面，down()、up() 这两个操作历史上最早称为 P 操作和 V 操作，所以信号量模型也被称为 PV 原语。

另外，还有些人喜欢用 semWait() 和 semSignal() 来称呼它们，虽然叫法不同，但是语义都是相同的。在 Java SDK 并发包里，down() 和 up() 对应的则是 acquire() 和 release()。

**如何使用信号量**

具体该如何使用信号量呢？其实你想想红绿灯就可以了。十字路口的红绿灯可以控制交通，得益于它的一个关键规则：车辆在通过路口前必须先检查是否是绿灯，只有绿灯才能通行。这个规则和我们前面提到的锁规则是不是很类似？

例如，在累加器的例子里面，count+=1 操作是个临界区，只允许一个线程执行，也就是说要保证互斥。那这种情况用信号量怎么控制呢？

```java
static int count;
// 初始化信号量
static final Semaphore s = new Semaphore(1);
// 用信号量保证互斥    
static void addOne() {
    s.acquire();
    try {
        count+=1;
    } finally {
        s.release();
    }
}
```

**快速实现一个限流器**

实现一个互斥锁，仅仅是 Semaphore 的部分功能，Semaphore 还有一个功能是 Lock 不容易实现的，那就是：**Semaphore 可以允许多个线程访问一个临界区**。

前不久，我在工作中也遇到了一个对象池的需求。所谓对象池呢，指的是一次性创建出 N 个对象，之后所有的线程重复利用这 N 个对象，当然对象在被释放前，也是不允许其他线程使用的。对象池，可以用 List 保存实例对象，这个很简单。但关键是限流器的设计，这里的限流，指的是不允许多于 N 个线程同时进入临界区。那如何快速实现一个这样的限流器呢？这种场景，我立刻就想到了信号量的解决方案。

```java
class ObjPool<T, R> {
  final List<T> pool;
  // 用信号量实现限流器
  final Semaphore sem;
  // 构造函数
  ObjPool(int size, T t) {
    pool = new Vector<T>() {};
    for(int i = 0; i < size; i++) {
      pool.add(t);
    }
    sem = new Semaphore(size);
  }
  // 利用对象池的对象，调用 func
  R exec(Function<T, R> func) {
    T t = null;
    sem.acquire();
    try {
      t = pool.remove(0);
      return func.apply(t);
    } finally {
      pool.add(t);
      sem.release();
    }
  }
}
// 创建对象池
ObjPool<Long, String> pool = new ObjPool<Long, String>(10, 2);
// 通过对象池获取 t，之后执行  
pool.exec(t -> {
    System.out.println(t);
    return t.toString();
});
```

对于通过信号灯的线程，我们为每个线程分配了一个对象 t（这个分配工作是通过 pool.remove(0) 实现的），分配完之后会执行一个回调函数 func，而函数的参数正是前面分配的对象 t ；执行完回调函数之后，它们就会释放对象（这个释放工作是通过 pool.add(t) 实现的），同时调用 release() 方法来更新信号量的计数器。如果此时信号量里计数器的值小于等于 0，那么说明有线程在等待，此时会自动唤醒等待的线程。

**课后思考**

在上面对象池的例子中，对象保存在了 Vector 中，Vector 是 Java 提供的线程安全的容器，如果我们把 Vector 换成 ArrayList，是否可以呢？

答：需要用线程安全的vector，因为信号量支持多个线程进入临界区，执行list的add和remove方法时可能是多线程并发执行。

# 17 | ReadWriteLock：如何快速实现一个完备的缓存？

今天我们介绍一种非常普遍的并发场景：读多写少场景。实际工作中，为了优化性能，我们经常会使用缓存，例如缓存元数据、缓存基础数据等，这就是一种典型的读多写少应用场景。缓存之所以能提升性能，一个重要的条件就是缓存的数据一定是读多写少的，例如元数据和基础数据基本上不会发生变化（写少），但是使用它们的地方却很多（读多）。

针对读多写少这种并发场景，Java SDK 并发包提供了读写锁——ReadWriteLock，非常容易使用，并且性能很好。

**什么是读写锁呢？**

读写锁，并不是 Java 语言特有的，而是一个广为使用的通用技术，所有的读写锁都遵守以下三条基本原则：

1. 允许多个线程同时读共享变量；
2. 只允许一个线程写共享变量；
3. 如果一个写线程正在执行写操作，此时禁止读线程读共享变量。

读写锁与互斥锁的一个重要区别就是**读写锁允许多个线程同时读共享变量**，而互斥锁是不允许的，这是读写锁在读多写少场景下性能优于互斥锁的关键。但**读写锁的写操作是互斥的**，当一个线程在写共享变量的时候，是不允许其他线程执行写操作和读操作。

**快速实现一个缓存**

下面我们就实践起来，用 ReadWriteLock 快速实现一个通用的缓存工具类。

```java
class Cache<K,V> {
    final Map<K, V> m = new HashMap<>();
    final ReadWriteLock rwl = new ReentrantReadWriteLock();
    // 读锁
    final Lock r = rwl.readLock();
    // 写锁
    final Lock w = rwl.writeLock();
    // 读缓存
    V get(K key) {
        r.lock();
        try {
            return m.get(key); 
        } finally {
            r.unlock();
        }
    }
    // 写缓存
    V put(String key, Data v) {
        w.lock();
        try {
            return m.put(key, v);
        } finally {
            w.unlock();
        }
    }
}
```

如果你曾经使用过缓存的话，你应该知道**使用缓存首先要解决缓存数据的初始化问题**。缓存数据的初始化，可以采用一次性加载的方式，也可以使用按需加载的方式。

如果源头数据的数据量不大，就可以采用一次性加载的方式，这种方式最简单（可参考下图），只需在应用启动的时候把源头数据查询出来，依次调用类似上面示例代码中的 put() 方法就可以了。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/缓存一次性加载示意图.png" alt="缓存一次性加载示意图" style="zoom:67%;" />

如果源头数据量非常大，那么就需要按需加载了，按需加载也叫懒加载，指的是只有当应用查询缓存，并且数据不在缓存里的时候，才触发加载源头相关数据进缓存的操作。下面你可以结合文中示意图看看如何利用 ReadWriteLock 来实现缓存的按需加载。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/缓存按需加载示意图.png" alt="缓存按需加载示意图" style="zoom:67%;" />

**实现缓存的按需加载**

文中下面的这段代码实现了按需加载的功能，这里我们假设缓存的源头是数据库。

需要注意的是，在获取写锁之后，我们并没有直接去查询数据库，而是在代码【6】【7】处，重新验证了一次缓存中是否存在，再次验证如果还是不存在，我们才去查询数据库并更新本地缓存。为什么我们要再次验证呢？

```java
class Cache<K,V> {
  final Map<K, V> m = new HashMap<>();
  final ReadWriteLock rwl = new ReentrantReadWriteLock();
  final Lock r = rwl.readLock();
  final Lock w = rwl.writeLock();
  
  V get(K key) {
    V v = null;
    // 读缓存
    r.lock();         //【1】
    try {
      v = m.get(key); //【2】
    } finally {
      r.unlock();     //【3】
    }
    // 缓存中存在，返回
    if(v != null) {   //【4】
      return v;
    }  
    // 缓存中不存在，查询数据库
    w.lock();         //【5】
    try {
      // 再次验证
      // 其他线程可能已经查询过数据库
      v = m.get(key); //【6】
      if(v == null) { //【7】
        // 查询数据库
        v = 省略代码无数
        m.put(key, v);
      }
    } finally {
      w.unlock();
    }
    return v; 
  }
}
```

原因是在高并发的场景下，有可能会有多线程竞争写锁。假设缓存是空的，没有缓存任何东西，如果此时有三个线程 T1、T2 和 T3 同时调用 get() 方法，并且参数 key 也是相同的。那么它们会同时执行到代码⑤处，但此时只有一个线程能够获得写锁，假设是线程 T1，线程 T1 获取写锁之后查询数据库并更新缓存，最终释放写锁。此时线程 T2 和 T3 会再有一个线程能够获取写锁，假设是 T2，如果不采用再次验证的方式，此时 T2 会再次查询数据库。T2 释放写锁之后，T3 也会再次查询一次数据库。而实际上线程 T1 已经把缓存的值设置好了，T2、T3 完全没有必要再次查询数据库。所以，再次验证的方式，能够避免高并发场景下重复查询数据的问题。

**读写锁的升级与降级**

上面按需加载的示例代码中，在【1】处获取读锁，在【3】处释放读锁，那是否可以在【2】处的下面增加验证缓存并更新缓存的逻辑呢？详细的代码如下。

```java
// 读缓存
r.lock();         //【1】
try {
  v = m.get(key); //【2】
  if (v == null) {
    w.lock();
    try {
      // 再次验证并更新缓存
      // 省略详细代码
    } finally{
      w.unlock();
    }
  }
} finally{
  r.unlock();     //【3】
}
```

这样看上去好像是没有问题的，先是获取读锁，然后再升级为写锁，对此还有个专业的名字，叫**锁的升级**。可惜 ReadWriteLock 并不支持这种升级。在上面的代码示例中，读锁还没有释放，此时获取写锁，会导致写锁永久等待，最终导致相关线程都被阻塞，永远也没有机会被唤醒。锁的升级是不允许的，这个你一定要注意。

（测试代码在 [github](https://github.com/dbses/Test4yang/tree/master/JavaThread/src/main/java/char17/LevelUpLockDemo.java) 上）

不过，虽然锁的升级是不允许的，但是锁的降级却是允许的。以下代码来源自 ReentrantReadWriteLock 的官方示例，略做了改动。你会发现在代码【1】处，获取读锁的时候线程还是持有写锁的，这种锁的降级是支持的。

```java
class CachedData {
  Object data;
  volatile boolean cacheValid;
  final ReadWriteLock rwl = new ReentrantReadWriteLock();
  // 读锁  
  final Lock r = rwl.readLock();
  // 写锁
  final Lock w = rwl.writeLock();
  
  void processCachedData() {
    // 获取读锁
    r.lock();
    if (!cacheValid) {
      // 释放读锁，因为不允许读锁的升级
      r.unlock();
      // 获取写锁
      w.lock();
      try {
        // 再次检查状态  
        if (!cacheValid) {
          data = ...
          cacheValid = true;
        }
        // 释放写锁前，降级为读锁
        // 降级是可以的
        r.lock(); //【1】
      } finally {
        // 释放写锁
        w.unlock(); 
      }
    }
    // 此处仍然持有读锁
    try {use(data);} 
    finally {r.unlock();}
  }
}
```

**总结**

读写锁类似于 ReentrantLock，也支持公平模式和非公平模式。读锁和写锁都实现了 java.util.concurrent.locks.Lock 接口，所以除了支持 lock() 方法外，tryLock()、lockInterruptibly() 等方法也都是支持的。但是有一点需要注意，那就是只有写锁支持条件变量，读锁是不支持条件变量的，读锁调用 newCondition() 会抛出 UnsupportedOperationException 异常。

今天我们用 ReadWriteLock 实现了一个简单的缓存，这个缓存虽然解决了缓存的初始化问题，但是没有解决缓存数据与源头数据的同步问题，这里的数据同步指的是保证缓存数据和源头数据的一致性。解决数据同步问题的一个最简单的方案就是**超时机制**。所谓超时机制指的是加载进缓存的数据不是长久有效的，而是有时效的，当缓存的数据超过时效，也就是超时之后，这条数据在缓存中就失效了。而访问缓存中失效的数据，会触发缓存重新从源头把数据加载进缓存。

当然也可以在源头数据发生变化时，快速反馈给缓存，但这个就要依赖具体的场景了。例如 MySQL 作为数据源头，可以通过近实时地解析 binlog 来识别数据是否发生了变化，如果发生了变化就将最新的数据推送给缓存。另外，还有一些方案采取的是数据库和缓存的双写方案。

总之，具体采用哪种方案，还是要看应用的场景。

**课后思考**

有同学反映线上系统停止响应了，CPU 利用率很低，你怀疑有同学一不小心写出了读锁升级写锁的方案，那你该如何验证自己的怀疑呢？

# 18 | StampedLock：有没有比读写锁更快的锁？

读写锁允许多个线程同时读共享变量，适用于读多写少的场景。那在读多写少的场景中，还有没有更快的技术方案呢？Java 在 1.8 这个版本里，提供了一种叫 StampedLock 的锁，它的性能就比读写锁还要好。

下面我们就来介绍一下 StampedLock 的使用方法、内部工作原理以及在使用过程中需要注意的事项。

**StampedLock 支持的三种锁模式**

我们先来看看在使用上 StampedLock 和 ReadWriteLock 有哪些区别。

- 区别一

  ReadWriteLock 支持两种模式：一种是读锁，一种是写锁。而 StampedLock 支持三种模式，分别是：**写锁**、**悲观读锁**和**乐观读**。

  其中，写锁、悲观读锁的语义和 ReadWriteLock 的写锁、读锁的语义非常类似，允许多个线程同时获取悲观读锁，但是只允许一个线程获取写锁，写锁和悲观读锁是互斥的。

- 区别二

  StampedLock 里的写锁和悲观读锁加锁成功之后，都会返回一个 stamp；然后解锁的时候，需要传入这个 stamp。相关的示例代码如下。

  ```java
  final StampedLock sl = new StampedLock();
  
  // 获取 / 释放悲观读锁示意代码
  long stamp = sl.readLock();
  try {
    // 省略业务相关代码
  } finally {
    sl.unlockRead(stamp);
  }
   
  // 获取 / 释放写锁示意代码
  long stamp = sl.writeLock();
  try {
    // 省略业务相关代码
  } finally {
    sl.unlockWrite(stamp);
  }
  ```

- 区别三

  StampedLock 的性能之所以比 ReadWriteLock 还要好，其关键是 StampedLock 支持乐观读的方式。ReadWriteLock 支持多个线程同时读，但是当多个线程同时读的时候，所有的写操作会被阻塞；而 StampedLock 提供的乐观读，是允许一个线程获取写锁的，也就是说不是所有的写操作都被阻塞。

  注意这里，我们用的是“乐观读”这个词，而不是“乐观读锁”，是要提醒你，**乐观读这个操作是无锁的**，所以相比较 ReadWriteLock 的读锁，乐观读的性能更好一些。

  下面这段代码是出自 Java SDK 官方示例，并略做了修改。在 distanceFromOrigin() 这个方法中，首先通过调用 tryOptimisticRead() 获取了一个 stamp，这里的 tryOptimisticRead() 就是我们前面提到的乐观读。之后将共享变量 x 和 y 读入方法的局部变量中，不过需要注意的是，由于 tryOptimisticRead() 是无锁的，所以共享变量 x 和 y 读入方法局部变量时，x 和 y 有可能被其他线程修改了。因此最后读完之后，还需要再次验证一下是否存在写操作，这个验证操作是通过调用 validate(stamp) 来实现的。

  ```java
  class Point {
    private int x, y;
    final StampedLock sl = new StampedLock();
    // 计算到原点的距离  
    int distanceFromOrigin() {
      // 乐观读
      long stamp = sl.tryOptimisticRead();
      // 读入局部变量，
      // 读的过程数据可能被修改
      int curX = x, curY = y;
      // 判断执行读操作期间，
      // 是否存在写操作，如果存在，
      // 则 sl.validate 返回 false
      if (!sl.validate(stamp)) {
        // 升级为悲观读锁
        stamp = sl.readLock();
        try {
          curX = x;
          curY = y;
        } finally {
          // 释放悲观读锁
          sl.unlockRead(stamp);
        }
      }
      return Math.sqrt(curX * curX + curY * curY);
    }
  }
  ```

**进一步理解乐观读**

StampedLock 的乐观读和数据库的乐观锁有异曲同工之妙。所以这里有必要再介绍一下数据库里的乐观锁。

还记得我第一次使用数据库乐观锁的场景是这样的：在 ERP 的生产模块里，会有多个人通过 ERP 系统提供的 UI 同时修改同一条生产订单，那如何保证生产订单数据是并发安全的呢？我采用的方案就是乐观锁。

乐观锁的实现很简单，在生产订单的表 product_doc 里增加了一个数值型版本号字段 version，每次更新 product_doc 这个表的时候，都将 version 字段加 1。生产订单的 UI 在展示的时候，需要查询数据库，此时将这个 version 字段和其他业务字段一起返回给生产订单 UI。假设用户查询的生产订单的 id=777，那么 SQL 语句类似下面这样：

```sql
select id，... ，version
from product_doc
where id=777
```

用户在生产订单 UI 执行保存操作的时候，后台利用下面的 SQL 语句更新生产订单，此处我们假设该条生产订单的 version=9。

```sql
update product_doc 
set version=version+1，...
where id=777 and version=9
```

如果这条 SQL 语句执行成功并且返回的条数等于 1，那么说明从生产订单 UI 执行查询操作到执行保存操作期间，没有其他人修改过这条数据。因为如果这期间其他人修改过这条数据，那么版本号字段一定会大于 9。

你会发现数据库里的乐观锁，查询的时候需要把 version 字段查出来，更新的时候要利用 version 字段做验证。这个 version 字段就类似于 StampedLock 里面的 stamp。这样对比着看，相信你会更容易理解 StampedLock 里乐观读的用法。

**StampedLock 使用注意事项**

对于读多写少的场景 StampedLock 性能很好，简单的应用场景基本上可以替代 ReadWriteLock，但是**StampedLock 的功能仅仅是 ReadWriteLock 的子集**，在使用的时候，还是有几个地方需要注意一下。

1. StampedLock 不支持重入。

2. StampedLock 的悲观读锁、写锁都不支持条件变量。

3. 如果线程阻塞在 StampedLock 的 readLock() 或者 writeLock() 上时，此时调用该阻塞线程的 interrupt() 方法，会导致 CPU 飙升。

例如下面的代码中，线程 T1 获取写锁之后将自己阻塞，线程 T2 尝试获取悲观读锁，也会阻塞；如果此时调用线程 T2 的 interrupt() 方法来中断线程 T2 的话，你会发现线程 T2 所在 CPU 会飙升到 100%。

```java
final StampedLock lock = new StampedLock();
Thread T1 = new Thread(()->{
  // 获取写锁
  lock.writeLock();
  // 永远阻塞在此处，不释放写锁
  LockSupport.park();
});
T1.start();
// 保证 T1 获取写锁
Thread.sleep(100);
Thread T2 = new Thread(()->
  // 阻塞在悲观读锁
  lock.readLock()
);
T2.start();
// 保证 T2 阻塞在读锁
Thread.sleep(100);
// 中断线程 T2
// 会导致线程 T2 所在 CPU 飙升
T2.interrupt();
T2.join();
```

所以，**使用 StampedLock 一定不要调用中断操作，如果需要支持中断功能，一定使用可中断的悲观读锁 readLockInterruptibly() 和写锁 writeLockInterruptibly()**。这个规则一定要记清楚。

**总结**

StampedLock 的使用看上去有点复杂，但是如果你能理解乐观锁背后的原理，使用起来还是比较流畅的。建议你认真揣摩 Java 的官方示例，这个示例基本上就是一个最佳实践。我们把 Java 官方示例精简后，形成下面的代码模板，建议你在实际工作中尽量按照这个模板来使用 StampedLock。

StampedLock 读模板：

```java
final StampedLock sl = new StampedLock();
 
// 乐观读
long stamp = sl.tryOptimisticRead();
// 读入方法局部变量
......
// 校验 stamp
if (!sl.validate(stamp)){
  // 升级为悲观读锁
  stamp = sl.readLock();
  try {
    // 读入方法局部变量
    .....
  } finally {
    // 释放悲观读锁
    sl.unlockRead(stamp);
  }
}
// 使用方法局部变量执行业务操作
......
```

StampedLock 写模板：

```java
long stamp = sl.writeLock();
try {
  // 写共享变量
  ......
} finally {
  sl.unlockWrite(stamp);
}
```

**课后思考**

StampedLock 支持锁的降级（通过 tryConvertToReadLock() 方法实现）和升级（通过 tryConvertToWriteLock() 方法实现），但是建议你要慎重使用。下面的代码也源自 Java 的官方示例，我仅仅做了一点修改，隐藏了一个 Bug，你来看看 Bug 出在哪里吧。

```java
private double x, y;
final StampedLock sl = new StampedLock();
// 存在问题的方法
void moveIfAtOrigin(double newX, double newY){
 long stamp = sl.readLock();
 try {
  while(x == 0.0 && y == 0.0){
    long ws = sl.tryConvertToWriteLock(stamp);
    if (ws != 0L) {
      x = newX;
      y = newY;
      break;
    } else {
      sl.unlockRead(stamp);
      stamp = sl.writeLock();
    }
  }
 } finally {
  sl.unlock(stamp);
}
```

答：在锁升级成功的时候，最后没有释放最新的写锁，可以在if块的break上加个stamp=ws进行释放。

# 19 | CountDownLatch 和 CyclicBarrier：如何让多线程步调一致？

前几天老板突然匆匆忙忙过来，说对账系统最近越来越慢了，能不能快速优化一下。我了解了对账系统的业务后，发现还是挺简单的，用户通过在线商城下单，会生成电子订单，保存在订单库；之后物流会生成派送单给用户发货，派送单保存在派送单库。为了防止漏派送或者重复派送，对账系统每天还会校验是否存在异常订单。

对账系统的处理逻辑很简单，你可以参考下面的对账系统流程图。目前对账系统的处理逻辑是首先查询订单，然后查询派送单，之后对比订单和派送单，将差异写入差异库。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/对账系统流程图.png" alt="对账系统流程图" style="zoom:67%;" />

对账系统的代码抽象之后，也很简单，核心代码如下，就是在一个单线程里面循环查询订单、派送单，然后执行对账，最后将写入差异库。

```java
while(存在未对账订单) {
  // 查询未对账订单
  pos = getPOrders();
  // 查询派送单
  dos = getDOrders();
  // 执行对账操作
  diff = check(pos, dos);
  // 差异写入差异库
  save(diff);
} 
```

**利用并行优化对账系统**

老板要我优化性能，那我就首先要找到这个对账系统的瓶颈所在。

目前的对账系统，由于订单量和派送单量巨大，所以查询未对账订单 getPOrders() 和查询派送单 getDOrders() 相对较慢，那有没有办法快速优化一下呢？目前对账系统是单线程执行的，图形化后是下图这个样子。对于串行化的系统，优化性能首先想到的是能否**利用多线程并行处理**。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/对账系统单线程执行示意图.png" alt="对账系统单线程执行示意图" style="zoom:67%;" />

所以，这里你应该能够看出来这个对账系统里的瓶颈：查询未对账订单 getPOrders() 和查询派送单 getDOrders() 是否可以并行处理呢？显然是可以的，因为这两个操作并没有先后顺序的依赖。这两个最耗时的操作并行之后，执行过程如下图所示。对比一下单线程的执行示意图，你会发现同等时间里，并行执行的吞吐量近乎单线程的 2 倍，优化效果还是相对明显的。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/对账系统并行执行示意图.png" alt="对账系统并行执行示意图" style="zoom:67%;" />

思路有了，下面我们再来看看如何用代码实现。在下面的代码中，我们创建了两个线程 T1 和 T2，并行执行查询未对账订单 getPOrders() 和查询派送单 getDOrders() 这两个操作。在主线程中执行对账操作 check() 和差异写入 save() 两个操作。不过需要注意的是：主线程需要等待线程 T1 和 T2 执行完才能执行 check() 和 save() 这两个操作，为此我们通过调用 T1.join() 和 T2.join() 来实现等待，当 T1 和 T2 线程退出时，调用 T1.join() 和 T2.join() 的主线程就会从阻塞态被唤醒，从而执行之后的 check() 和 save()。

```java
while(存在未对账订单){
  // 查询未对账订单
  Thread T1 = new Thread(()->{
    pos = getPOrders();
  });
  T1.start();
  // 查询派送单
  Thread T2 = new Thread(()->{
    dos = getDOrders();
  });
  T2.start();
  // 等待 T1、T2 结束
  T1.join();
  T2.join();
  // 执行对账操作
  diff = check(pos, dos);
  // 差异写入差异库
  save(diff);
} 
```

**用 CountDownLatch 实现线程等待**

经过上面的优化之后，基本上可以跟老板汇报收工了，但还是有点美中不足，相信你也发现了，while 循环里面每次都会创建新的线程，而创建线程可是个耗时的操作。所以最好是创建出来的线程能够循环利用，估计这时你已经想到线程池了，是的，线程池就能解决这个问题。

而下面的代码就是用线程池优化后的：我们首先创建了一个固定大小为 2 的线程池，之后在 while 循环里重复利用。一切看上去都很顺利，但是有个问题好像无解了，那就是主线程如何知道 getPOrders() 和 getDOrders() 这两个操作什么时候执行完。前面主线程通过调用线程 T1 和 T2 的 join() 方法来等待线程 T1 和 T2 退出，但是在线程池的方案里，线程根本就不会退出，所以 join() 方法已经失效了。

```java
// 创建 2 个线程的线程池
Executor executor = Executors.newFixedThreadPool(2);
while(存在未对账订单) {
  // 查询未对账订单
  executor.execute(() -> {
    pos = getPOrders();
  });
  // 查询派送单
  executor.execute(() -> {
    dos = getDOrders();
  });
  
  /* ？？如何实现等待？？*/
  
  // 执行对账操作
  diff = check(pos, dos);
  // 差异写入差异库
  save(diff);
}   
```

那如何解决这个问题呢？你可以开动脑筋想出很多办法，最直接的办法是弄一个计数器，初始值设置成 2，当执行完`pos = getPOrders();`这个操作之后将计数器减 1，执行完`dos = getDOrders();`之后也将计数器减 1，在主线程里，等待计数器等于 0；当计数器等于 0 时，说明这两个查询操作执行完了。等待计数器等于 0 其实就是一个条件变量，用管程实现起来也很简单。

不过我并不建议你在实际项目中去实现上面的方案，因为 Java 并发包里已经提供了实现类似功能的工具类：**CountDownLatch**，我们直接使用就可以了。下面的代码示例中，在 while 循环里面，我们首先创建了一个 CountDownLatch，计数器的初始值等于 2，之后在`pos = getPOrders();`和`dos = getDOrders();`两条语句的后面对计数器执行减 1 操作，这个对计数器减 1 的操作是通过调用 `latch.countDown();` 来实现的。在主线程中，我们通过调用 `latch.await()` 来实现对计数器等于 0 的等待。

```java
// 创建 2 个线程的线程池
Executor executor = Executors.newFixedThreadPool(2);
while(存在未对账订单){
  // 计数器初始化为 2
  CountDownLatch latch = new CountDownLatch(2);
  // 查询未对账订单
  executor.execute(() -> {
    pos = getPOrders();
    latch.countDown();
  });
  // 查询派送单
  executor.execute(() -> {
    dos = getDOrders();
    latch.countDown();
  });
  
  // 等待两个查询操作结束
  latch.await();
  
  // 执行对账操作
  diff = check(pos, dos);
  // 差异写入差异库
  save(diff);
}
```

**进一步优化性能**

经过上面的重重优化之后，长出一口气，终于可以交付了。不过在交付之前还需要再次审视一番，看看还有没有优化的余地，仔细看还是有的。

前面我们将 getPOrders() 和 getDOrders() 这两个查询操作并行了，但这两个查询操作和对账操作 check()、save() 之间还是串行的。很显然，这两个查询操作和对账操作也是可以并行的，也就是说，在执行对账操作的时候，可以同时去执行下一轮的查询操作，这个过程可以形象化地表述为下面这幅示意图。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/完全并行执行示意图.png" alt="完全并行执行示意图" style="zoom:67%;" />

那接下来我们再来思考一下如何实现这步优化，两次查询操作能够和对账操作并行，对账操作还依赖查询操作的结果，这明显有点生产者 - 消费者的意思，两次查询操作是生产者，对账操作是消费者。既然是生产者 - 消费者模型，那就需要有个队列，来保存生产者生产的数据，而消费者则从这个队列消费数据。

不过针对对账这个项目，我设计了两个队列，并且两个队列的元素之间还有对应关系。具体如下图所示，订单查询操作将订单查询结果插入订单队列，派送单查询操作将派送单插入派送单队列，这两个队列的元素之间是有一一对应的关系的。两个队列的好处是，对账操作可以每次从订单队列出一个元素，从派送单队列出一个元素，然后对这两个元素执行对账操作，这样数据一定不会乱掉。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/双队列示意图.png" alt="双队列示意图" style="zoom:67%;" />

下面再来看如何用双队列来实现完全的并行。一个最直接的想法是：一个线程 T1 执行订单的查询工作，一个线程 T2 执行派送单的查询工作，当线程 T1 和 T2 都各自生产完 1 条数据的时候，通知线程 T3 执行对账操作。这个想法虽看上去简单，但其实还隐藏着一个条件，那就是线程 T1 和线程 T2 的工作要步调一致，不能一个跑得太快，一个跑得太慢，只有这样才能做到各自生产完 1 条数据的时候，通知线程 T3。

下面这幅图形象地描述了上面的意图：线程 T1 和线程 T2 只有都生产完 1 条数据的时候，才能一起向下执行，也就是说，线程 T1 和线程 T2 要互相等待，步调要一致；同时当线程 T1 和 T2 都生产完一条数据的时候，还要能够通知线程 T3 执行对账操作。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/同步执行示意图.png" alt="同步执行示意图" style="zoom:67%;" />

**用 CyclicBarrier 实现线程同步**

下面我们就来实现上面提到的方案。这个方案的难点有两个：一个是线程 T1 和 T2 要做到步调一致，另一个是要能够通知到线程 T3。

你依然可以利用一个计数器来解决这两个难点，计数器初始化为 2，线程 T1 和 T2 生产完一条数据都将计数器减 1，如果计数器大于 0 则线程 T1 或者 T2 等待。如果计数器等于 0，则通知线程 T3，并唤醒等待的线程 T1 或者 T2，与此同时，将计数器重置为 2，这样线程 T1 和线程 T2 生产下一条数据的时候就可以继续使用这个计数器了。

同样，还是建议你不要在实际项目中这么做，因为 Java 并发包里也已经提供了相关的工具类：**CyclicBarrier**。在下面的代码中，我们首先创建了一个计数器初始值为 2 的 CyclicBarrier，你需要注意的是创建 CyclicBarrier 的时候，我们还传入了一个回调函数，当计数器减到 0 的时候，会调用这个回调函数。

线程 T1 负责查询订单，当查出一条时，调用 `barrier.await()` 来将计数器减 1，同时等待计数器变成 0；线程 T2 负责查询派送单，当查出一条时，也调用 `barrier.await()` 来将计数器减 1，同时等待计数器变成 0；当 T1 和 T2 都调用 `barrier.await()` 的时候，计数器会减到 0，此时 T1 和 T2 就可以执行下一条语句了，同时会调用 barrier 的回调函数来执行对账操作。

非常值得一提的是，CyclicBarrier 的计数器有自动重置的功能，当减到 0 的时候，会自动重置你设置的初始值。这个功能用起来实在是太方便了。

```java
// 订单队列
Vector<P> pos;
// 派送单队列
Vector<D> dos;
// 执行回调的线程池 
Executor executor = Executors.newFixedThreadPool(1);
final CyclicBarrier barrier = new CyclicBarrier(2, () -> {
    executor.execute(() -> check());
  });
  
void check() {
  P p = pos.remove(0);
  D d = dos.remove(0);
  // 执行对账操作
  diff = check(p, d);
  // 差异写入差异库
  save(diff);
}
  
void checkAll() {
  // 循环查询订单库
  Thread T1 = new Thread(() -> {
    while(存在未对账订单) {
      // 查询订单库
      pos.add(getPOrders());
      // 等待
      barrier.await();
    }
  });
  T1.start();  
  // 循环查询运单库
  Thread T2 = new Thread(() -> {
    while(存在未对账订单) {
      // 查询运单库
      dos.add(getDOrders());
      // 等待
      barrier.await();
    }
  });
  T2.start();
}
```

**总结**

1. **CountDownLatch 主要用来解决一个线程等待多个线程的场景**，可以类比旅游团团长要等待所有的游客到齐才能去下一个景点；而**CyclicBarrier 是一组线程之间互相等待**，更像是几个驴友之间不离不弃。
2. CountDownLatch 的计数器是不能循环利用的，也就是说一旦计数器减到 0，再有线程调用 await()，该线程会直接通过。但**CyclicBarrier 的计数器是可以循环利用的**，而且具备自动重置的功能，一旦计数器减到 0 会自动重置到你设置的初始值。
3. CyclicBarrier 还可以设置回调函数。

**课后思考**

本章最后的示例代码中，CyclicBarrier 的回调函数我们使用了一个固定大小的线程池，你觉得是否有必要呢？

答：线程池大小为1是必要的，如果设置为多个，有可能会两个线程 A 和 B 同时查询，A 的订单先返回，B 的派送单先返回，造成队列中的数据不匹配；所以1个线程实现生产数据串行执行，保证数据安全。

# 20 | 并发容器：都有哪些“坑”需要我们填？

Java 1.5 之前提供的**同步容器**虽然也能保证线程安全，但是性能很差，而 Java 1.5 版本之后提供的并发容器在性能方面则做了很多优化，并且容器的类型也更加丰富了。下面我们就对比二者来学习这部分的内容。

**同步容器及其注意事项**

Java 中的容器主要可以分为四个大类，分别是 List、Map、Set 和 Queue。

在容器领域**一个容易被忽视的“坑”是用迭代器遍历容器**，例如在下面的代码中，通过迭代器遍历容器 list，对每个元素调用 foo() 方法，这就存在并发问题，这些组合的操作不具备原子性。

```java
List list = Collections.synchronizedList(new ArrayList());
Iterator i = list.iterator(); 
while (i.hasNext()) {
  foo(i.next());
}
```

而正确做法是下面这样，锁住 list 之后再执行遍历操作。如果你查看 Collections 内部的包装类源码，你会发现包装类的公共方法锁的是对象的 this，其实就是我们这里的 list，所以锁住 list 绝对是线程安全的。

```java
List list = Collections.synchronizedList(new ArrayList());
synchronized (list) {  
  Iterator i = list.iterator(); 
  while (i.hasNext()) {}
    foo(i.next());
  }
}    
```

上面我们提到的这些经过包装后线程安全容器，都是基于 synchronized 这个同步关键字实现的，所以也被称为**同步容器**。Java 提供的同步容器还有 Vector、Stack 和 Hashtable，这三个容器不是基于包装类实现的，但同样是基于 synchronized 实现的，对这三个容器的遍历，同样要加锁保证互斥。

**并发容器及其注意事项**

同步容器和并发容器的区别：

Java 在 1.5 版本之前所谓的线程安全的容器，主要指的就是**同步容器**。不过同步容器有个最大的问题，那就是性能差，所有方法都用 synchronized 来保证互斥，串行度太高了。因此 Java 在 1.5 及之后版本提供了性能更高的容器，我们一般称为**并发容器**。

并发容器虽然数量非常多，但依然是前面我们提到的四大类：List、Map、Set 和 Queue，下面的并发容器关系图，基本上把我们经常用的容器都覆盖到了。

![并发容器关系图](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/并发容器关系图.png)

- （一）List

  CopyOnWrite 的定义：

  顾名思义就是写的时候会将共享变量新复制一份出来，这样做的好处是读操作完全无锁。

  CopyOnWriteArrayList 的实现原理：

  CopyOnWriteArrayList 内部维护了一个数组，成员变量 array 就指向这个内部数组，所有的读操作都是基于 array 进行的，如下图所示，迭代器 Iterator 遍历的就是 array 数组。

  ![执行迭代的内部结构图](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/执行迭代的内部结构图.png)

  如果在遍历 array 的同时，还有一个写操作，例如增加元素，CopyOnWriteArrayList 是如何处理的呢？CopyOnWriteArrayList 会将 array 复制一份，然后在新复制处理的数组上执行增加元素的操作，执行完之后再将 array 指向这个新的数组。通过下图你可以看到，读写是可以并行的，遍历操作一直都是基于原 array 执行，而写操作则是基于新 array 进行。

  ![执行增加元素的内部结构图](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/执行增加元素的内部结构图.png)

  使用 CopyOnWriteArrayList 需要注意的“坑”主要有两个方面。

  一个是应用场景，CopyOnWriteArrayList 仅适用于写操作非常少的场景，而且能够容忍读写的短暂不一致。例如上面的例子中，写入的新元素并不能立刻被遍历到。

  另一个需要注意的是，CopyOnWriteArrayList 迭代器是只读的，不支持增删改。因为迭代器遍历的仅仅是一个快照，而对快照进行增删改是没有意义的。

- （二）Map

  Map 接口的两个实现是 ConcurrentHashMap 和 ConcurrentSkipListMap。

  不同点。从应用的角度来看，主要区别在于**ConcurrentHashMap 的 key 是无序的，而 ConcurrentSkipListMap 的 key 是有序的**。所以如果你需要保证 key 的顺序，就只能使用 ConcurrentSkipListMap。

  相同点。它们的 key 和 value 都不能为空，否则会抛出`NullPointerException`这个运行时异常。

  下面这个表格总结了 Map 相关的实现类对于 key 和 value 的要求，你可以对比学习。

  <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/Map 相关的实现类对于 key 和 value 的要求.png" alt="Map 相关的实现类对于 key 和 value 的要求" style="zoom:80%;" />

  ConcurrentSkipListMap 里面的 SkipList 本身就是一种数据结构，中文一般都翻译为“跳表”。跳表插入、删除、查询操作平均的时间复杂度是 O(log n)，理论上和并发线程数没有关系，所以在并发度非常高的情况下，若你对 ConcurrentHashMap 的性能还不满意，可以尝试一下 ConcurrentSkipListMap。

- （三）Set

  Set 接口的两个实现是 CopyOnWriteArraySet 和 ConcurrentSkipListSet，使用场景可以参考前面讲述的 CopyOnWriteArrayList 和 ConcurrentSkipListMap，它们的原理都是一样的，这里就不再赘述了。

- （四）Queue

  Java 并发包里面 Queue 这类并发容器是最复杂的，你可以从以下两个维度来分类。

  一个维度是**阻塞与非阻塞**，所谓阻塞指的是当队列已满时，入队操作阻塞；当队列已空时，出队操作阻塞。<br>另一个维度是**单端与双端**，单端指的是只能队尾入队，队首出队；而双端指的是队首队尾皆可入队出队。

  Java 并发包里**阻塞队列都用 Blocking 关键字标识，单端队列使用 Queue 标识，双端队列使用 Deque 标识**。

  这两个维度组合后，可以将 Queue 细分为四大类，分别是：

  1. 单端阻塞队列 BlockingQueue

     其实现有 ArrayBlockingQueue、LinkedBlockingQueue、SynchronousQueue、LinkedTransferQueue、PriorityBlockingQueue 和 DelayQueue。内部一般会持有一个队列，这个队列可以是数组（其实现是 ArrayBlockingQueue）也可以是链表（其实现是 LinkedBlockingQueue）；甚至还可以不持有队列（其实现是 SynchronousQueue），此时生产者线程的入队操作必须等待消费者线程的出队操作。而 LinkedTransferQueue 融合 LinkedBlockingQueue 和 SynchronousQueue 的功能，性能比 LinkedBlockingQueue 更好；PriorityBlockingQueue 支持按照优先级出队；DelayQueue 支持延时出队。

     <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/单端阻塞队列示意图.png" alt="单端阻塞队列示意图" style="zoom:80%;" />

  2. **双端阻塞队列**：其实现是 LinkedBlockingDeque。

     <img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/双端阻塞队列示意图.png" alt="双端阻塞队列示意图" style="zoom:80%;" />

  3. **单端非阻塞队列**：其实现是 ConcurrentLinkedQueue。

  4. **双端非阻塞队列**：其实现是 ConcurrentLinkedDeque。

     另外，使用队列时，需要格外注意队列是否支持有界（所谓有界指的是内部的队列是否有容量限制）。实际工作中，一般都不建议使用无界的队列，因为数据量大了之后很容易导致 OOM。上面我们提到的这些 Queue 中，只有 ArrayBlockingQueue 和 LinkedBlockingQueue 是支持有界的，所以**在使用其他无界队列时，一定要充分考虑是否存在导致 OOM 的隐患**。

**总结**

在实际工作中，你不单要清楚每种容器的特性，还要能**选对容器，这才是关键**。

**课后思考**

线上系统 CPU 突然飙升，你怀疑有同学在并发场景里使用了 HashMap，因为在 1.8 之前的版本里并发执行 HashMap.put() 可能会导致 CPU 飙升到 100%，你觉得该如何验证你的猜测呢？

答：Java7中的HashMap在执行put操作时会涉及到扩容，由于扩容时链表并发操作会造成链表成环，所以可能导致 CPU 飙升100%。

# 21 | 原子类：无锁工具类的典范

前面我们多次提到一个累加器的例子，示例代码如下。

```java
public class Test {
  long count = 0;
  void add10K() {
    int idx = 0;
    while(idx++ < 10000) {
      count += 1;
    }
  }
}
```

在这个例子中，add10K() 这个方法不是线程安全的，问题就出在变量 count 的可见性和 count+=1 的原子性上。可见性问题可以用 volatile 来解决，而原子性问题我们前面一直都是采用的互斥锁方案。

其实对于简单的原子性问题，还有一种**无锁方案**。

```java
public class Test {
  AtomicLong count = new AtomicLong(0);
  void add10K() {
    int idx = 0;
    while(idx++ < 10000) {
      count.getAndIncrement();
    }
  }
}
```

无锁方案相对互斥锁方案，最大的好处就是**性能**。

互斥锁方案为了保证互斥性，需要执行加锁、解锁操作，而加锁、解锁操作本身就消耗性能；同时拿不到锁的线程还会进入阻塞状态，进而触发线程切换，线程切换对性能的消耗也很大。

无锁方案则完全没有加锁、解锁的性能消耗，同时还能保证互斥性，既解决了问题，又没有带来新的问题，可谓绝佳方案。

**无锁方案的实现原理**

其实原子类性能高的秘密很简单，硬件支持而已。CPU 为了解决并发问题，提供了 CAS 指令（CAS，全称是 Compare And Swap，即“比较并交换”）。

CAS 指令包含 3 个参数：共享变量的内存地址 A、用于比较的值 B 和共享变量的新值 C；并且只有当内存中地址 A 处的值等于 B 时，才能将内存中地址 A 处的值更新为新值 C。**作为一条 CPU 指令，CAS 指令本身是能够保证原子性的**。

可以通过下面 CAS 指令的模拟代码来理解 CAS 的工作原理。在下面的模拟程序中有两个参数，一个是期望值 expect，另一个是需要写入的新值 newValue，**只有当目前 count 的值和期望值 expect 相等时，才会将 count 更新为 newValue**。

```java
class SimulatedCAS {
  int count；
  synchronized int cas(int expect, int newValue) {
    // 读目前 count 的值
    int curValue = count;
    // 比较目前 count 值是否 == 期望值
    if(curValue == expect) {
      // 如果是，则更新 count 的值
      count = newValue;
    }
    // 返回写入前的值
    return curValue;
  }
}
```

使用 CAS 来解决并发问题，一般都会伴随着自旋，而所谓自旋，其实就是循环尝试。例如，实现一个线程安全的`count += 1`操作，“CAS + 自旋”的实现方案如下所示，首先计算 newValue = count+1，如果 cas(count,newValue) 返回的值不等于 count，则意味着线程在执行完代码【1】处之后，执行代码②处之前，count 的值被其他线程更新过。那此时该怎么处理呢？可以采用自旋方案，就像下面代码中展示的，可以重新读 count 最新的值来计算 newValue 并尝试再次更新，直到成功。

```java
class SimulatedCAS {
  volatile int count;
  // 实现 count+=1
  addOne() {
    do {
      newValue = count + 1; // 【1】
    } while(count != cas(count,newValue) // 【2】
  }
  // 模拟实现 CAS，仅用来帮助理解
  synchronized int cas(int expect, int newValue) {
    // 读目前 count 的值
    int curValue = count;
    // 比较目前 count 值是否 == 期望值
    if (curValue == expect) {
      // 如果是，则更新 count 的值
      count = newValue;
    }
    // 返回写入前的值
    return curValue;
  }
}
```

**CAS 的 ABA 问题**

在 CAS 方案中，有一个问题可能会常被你忽略，那就是**ABA**的问题。

前面我们提到“如果 cas(count,newValue) 返回的值**不等于**count，意味着线程在执行完代码【1】处之后，执行代码【2】处之前，count 的值被其他线程**更新过**”，那如果 cas(count,newValue) 返回的值**等于**count，是否就能够认为 count 的值没有被其他线程**更新过**呢？显然不是的，假设 count 原本是 A，线程 T1 在执行完代码【1】处之后，执行代码【2】处之前，有可能 count 被线程 T2 更新成了 B，之后又被 T3 更新回了 A，这样线程 T1 虽然看到的一直是 A，但是其实已经被其他线程更新过了，这就是 ABA 问题。

可能大多数情况下我们并不关心 ABA 问题，例如数值的原子递增，但也不能所有情况下都不关心，例如原子化的更新对象很可能就需要关心 ABA 问题，因为两个 A 虽然相等，但是第二个 A 的属性可能已经发生变化了。所以在使用 CAS 方案的时候，一定要先 check 一下。

**看 Java 如何实现原子化的 count += 1**

在 Java 1.8 版本中，getAndIncrement() 方法会转调 unsafe.getAndAddLong() 方法。这里 this 和 valueOffset 两个参数可以唯一确定共享变量的内存地址。

```java
final long getAndIncrement() {
  return unsafe.getAndAddLong(this, valueOffset, 1L);
}
```

unsafe.getAndAddLong() 方法的源码如下，该方法首先会在内存中读取共享变量的值，之后循环调用 compareAndSwapLong() 方法来尝试设置共享变量的值，直到成功为止。compareAndSwapLong() 是一个 native 方法，只有当内存中共享变量的值等于 expected 时，才会将共享变量的值更新为 x，并且返回 true；否则返回 fasle。compareAndSwapLong 的语义和 CAS 指令的语义的差别仅仅是返回值不同而已。

```java
public final long getAndAddLong(Object o, long offset, long delta) {
  long v;
  do {
    // 读取内存中的值
    v = getLongVolatile(o, offset);
  } while (!compareAndSwapLong(o, offset, v, v + delta));
  return v;
}
// 原子性地将变量更新为 x
// 条件是内存中的值等于 expected
// 更新成功则返回 true
native boolean compareAndSwapLong(Object o, long offset, long expected, long x);
```

**原子类概览**

Java SDK 并发包里提供的原子类内容很丰富，我们可以将它们分为五个类别：**原子化的基本数据类型、原子化的对象引用类型、原子化数组、原子化对象属性更新器**和**原子化的累加器**。这五个类别提供的方法基本上是相似的，并且每个类别都有若干原子类，你可以通过下面的原子类组成概览图来获得一个全局的印象。下面我们详细解读这五个类别。

![原子类组成概览图](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/原子类组成概览图.png)

1. 原子化的基本数据类型

   相关实现有 AtomicBoolean、AtomicInteger 和 AtomicLong，提供的方法主要有以下这些，详情你可以参考 SDK 的源代码。

   ```java
   getAndIncrement() // 原子化 i++
   getAndDecrement() // 原子化的 i--
   incrementAndGet() // 原子化的 ++i
   decrementAndGet() // 原子化的 --i
   // 当前值 +=delta，返回 += 前的值
   getAndAdd(delta) 
   // 当前值 +=delta，返回 += 后的值
   addAndGet(delta)
   //CAS 操作，返回是否成功
   compareAndSet(expect, update)
   // 以下四个方法
   // 新值可以通过传入 func 函数来计算
   getAndUpdate(func)
   updateAndGet(func)
   getAndAccumulate(x,func)
   accumulateAndGet(x,func)
   ```

2. 原子化的对象引用类型

   相关实现有 AtomicReference、AtomicStampedReference 和 AtomicMarkableReference，利用它们可以实现对象引用的原子化更新。

   AtomicReference 提供的方法和原子化的基本数据类型差不多。对象引用的更新需要重点关注 ABA 问题。

   AtomicStampedReference 和 AtomicMarkableReference 这两个原子类可以解决 ABA 问题。解决 ABA 问题的思路其实很简单，增加一个版本号维度就可以了，与乐观锁机制很类似，每次执行 CAS 操作，附加再更新一个版本号，只要保证版本号是递增的，那么即便 A 变成 B 之后再变回 A，版本号也不会变回来（版本号递增的）。

   AtomicStampedReference 实现的 CAS 方法就增加了版本号参数，方法签名如下：

   ```java
   boolean compareAndSet(
       V expectedReference, 
       V newReference, 
       int expectedStamp, 
       int newStamp) 
   ```

   AtomicMarkableReference 的实现机制则更简单，将版本号简化成了一个 Boolean 值，方法签名如下：

   ```java
   boolean compareAndSet(
     V expectedReference,
     V newReference,
     boolean expectedMark,
     boolean newMark)
   ```

3. 原子化数组

   相关实现有 AtomicIntegerArray、AtomicLongArray 和 AtomicReferenceArray，利用这些原子类，我们可以原子化地更新数组里面的每一个元素。这些类提供的方法和原子化的基本数据类型的区别仅仅是：每个方法多了一个数组的索引参数。

4. 原子化对象属性更新器

   相关实现有 AtomicIntegerFieldUpdater、AtomicLongFieldUpdater 和 AtomicReferenceFieldUpdater，利用它们可以原子化地更新对象的属性，这三个方法都是利用反射机制实现的，创建更新器的方法如下：

   ```java
   public static <U> AtomicXXXFieldUpdater<U> newUpdater(
       Class<U> tclass,
       String fieldName)
   ```

   需要注意的是，**对象属性必须是 volatile 类型的，只有这样才能保证可见性**；如果对象属性不是 volatile 类型的，newUpdater() 方法会抛出 IllegalArgumentException 这个运行时异常。

   你会发现 newUpdater() 的方法参数只有类的信息，没有对象的引用，而更新**对象**的属性，一定需要对象的引用，那这个参数是在哪里传入的呢？是在原子操作的方法参数中传入的。例如 compareAndSet() 这个原子操作，相比原子化的基本数据类型多了一个对象引用 obj。原子化对象属性更新器相关的方法，相比原子化的基本数据类型仅仅是多了对象引用参数。

   ```java
   boolean compareAndSet(
     T obj, 
     int expect, 
     int update)
   ```

5. 原子化的累加器

   DoubleAccumulator、DoubleAdder、LongAccumulator 和 LongAdder，这四个类仅仅用来执行累加操作，相比原子化的基本数据类型，速度更快，但是不支持 compareAndSet() 方法。如果你仅仅需要累加操作，使用原子化的累加器性能会更好。

**总结**

无锁方案相对于互斥锁方案，优点非常多。首先性能好，其次是基本不会出现死锁问题（但可能出现饥饿和活锁问题，因为自旋会反复重试）。Java 提供的原子类大部分都实现了 compareAndSet() 方法，基于 compareAndSet() 方法，你可以构建自己的无锁数据结构，但是**建议你不要这样做，这个工作最好还是让大师们去完成**，原因是无锁算法没你想象的那么简单。

**课后思考**

下面的示例代码是合理库存的原子化实现，仅实现了设置库存上限 setUpper() 方法，你觉得 setUpper() 方法的实现是否正确呢？

```java
public class SafeWM {
  class WMRange {
    final int upper;
    final int lower;
    WMRange(int upper, int lower) {
    // 省略构造函数实现
    }
  }
  final AtomicReference<WMRange> rf = new AtomicReference<>(new WMRange(0, 0));
  // 设置库存上限
  void setUpper(int v) {
    WMRange nr;
    WMRange or = rf.get();
    do{
      // 检查参数合法性
      if(v < or.lower) {
        throw new IllegalArgumentException();
      }
      nr = new WMRange(v, or.lower);
    } while(!rf.compareAndSet(or, nr));
  }
}
```

答：如果线程1 运行到WMRange or = rf.get();停止，切换到线程2 更新了值，切换回到线程1，进入循环将永远比较失败死循环，解决方案是将读取的那一句放入循环里，CAS每次自旋必须要重新检查新的值才有意义。

# 22 | Executor与线程池：如何创建正确的线程池？

**创建对象与创建线程**

虽然在 Java 语言中创建线程看上去就像创建一个对象一样简单，只需要 new Thread() 就可以了，但实际上创建线程远不是创建一个对象那么简单。

创建对象，仅仅是在 JVM 的堆里分配一块内存而已；

而创建一个线程，却需要调用操作系统内核的 API，然后操作系统要为线程分配一系列的资源，这个成本就很高了，所以**线程是一个重量级的对象，应该避免频繁创建和销毁**。

**线程池是一种生产者 - 消费者模式**

线程池的设计，没有直接采用一般意义上池化资源的设计方法。目前业界线程池的设计，普遍采用的都是**生产者 - 消费者模式**。线程池的使用方是生产者，线程池本身是消费者。在下面的示例代码中，我们创建了一个非常简单的线程池 MyThreadPool，你可以通过它来理解线程池的工作原理。

```java
// 简化的线程池，仅用来说明工作原理
class MyThreadPool{
  // 利用阻塞队列实现生产者 - 消费者模式
  BlockingQueue<Runnable> workQueue;
  // 保存内部工作线程
  List<WorkerThread> threads = new ArrayList<>();
  // 构造方法
  MyThreadPool(int poolSize, BlockingQueue<Runnable> workQueue) {
    this.workQueue = workQueue;
    // 创建工作线程
    for(int idx = 0; idx < poolSize; idx++) {
      WorkerThread work = new WorkerThread();
      work.start();
      threads.add(work);
    }
  }
  // 提交任务
  void execute(Runnable command) {
    workQueue.put(command);
  }
  // 工作线程负责消费任务，并执行任务
  class WorkerThread extends Thread {
    public void run() {
      // 循环取任务并执行
      while(true) { // 【1】
        Runnable task = workQueue.take();
        task.run();
      } 
    }
  }  
}
 
/** 下面是使用示例 **/
// 创建有界阻塞队列
BlockingQueue<Runnable> workQueue = new LinkedBlockingQueue<>(2);
// 创建线程池  
MyThreadPool pool = new MyThreadPool(10, workQueue);
// 提交任务  
pool.execute(() -> System.out.println("hello"));
```

在 MyThreadPool 的内部，我们维护了一个阻塞队列 workQueue 和一组工作线程，工作线程的个数由构造函数中的 poolSize 来指定。用户通过调用 execute() 方法来提交 Runnable 任务，execute() 方法的内部实现仅仅是将任务加入到 workQueue 中。MyThreadPool 内部维护的工作线程会消费 workQueue 中的任务并执行任务，相关的代码就是代码①处的 while 循环。

**如何使用 Java 中的线程池**

Java 提供的线程池相关的工具类中，最核心的是**ThreadPoolExecutor**。ThreadPoolExecutor 的构造函数非常复杂，如下面代码所示，这个最完备的构造函数有 7 个参数。

```java
ThreadPoolExecutor(
  int corePoolSize,
  int maximumPoolSize,
  long keepAliveTime,
  TimeUnit unit,
  BlockingQueue<Runnable> workQueue,
  ThreadFactory threadFactory,
  RejectedExecutionHandler handler) 
```

你可以**把线程池类比为一个项目组，而线程就是项目组的成员**。

- **corePoolSize**：表示线程池保有的最小线程数。有些项目很闲，但是也不能把人都撤了，至少要留 corePoolSize 个人坚守阵地。
- **maximumPoolSize**：表示线程池创建的最大线程数。当项目很忙时，就需要加人，但是也不能无限制地加，最多就加到 maximumPoolSize 个人。当项目闲下来时，就要撤人了，最多能撤到 corePoolSize 个人。
- **keepAliveTime & unit**：上面提到项目根据忙闲来增减人员，那在编程世界里，如何定义忙和闲呢？很简单，一个线程如果在一段时间内，都没有执行任务，说明很闲，keepAliveTime 和 unit 就是用来定义这个“一段时间”的参数。也就是说，如果一个线程空闲了`keepAliveTime & unit`这么久，而且线程池的线程数大于 corePoolSize ，那么这个空闲的线程就要被回收了。
- **workQueue**：工作队列，和上面示例代码的工作队列同义。
- **threadFactory**：通过这个参数你可以自定义如何创建线程，例如你可以给线程指定一个有意义的名字。
- handler：通过这个参数你可以自定义任务的拒绝策略。如果线程池中所有的线程都在忙碌，并且工作队列也满了（前提是工作队列是有界队列），那么此时提交任务，线程池就会拒绝接收。至于拒绝的策略，你可以通过 handler 这个参数来指定。ThreadPoolExecutor 已经提供了以下 4 种策略。
  - CallerRunsPolicy：提交任务的线程自己去执行该任务。
  - AbortPolicy：默认的拒绝策略，会 throws RejectedExecutionException。
  - DiscardPolicy：直接丢弃任务，没有任何异常抛出。
  - DiscardOldestPolicy：丢弃最老的任务，其实就是把最早进入工作队列的任务丢弃，然后把新任务加入到工作队列。

Java 在 1.6 版本还增加了 allowCoreThreadTimeOut(boolean value) 方法，它可以让所有线程都支持超时，这意味着如果项目很闲，就会将项目组的成员都撤走。

**使用线程池要注意些什么**

考虑到 ThreadPoolExecutor 的构造函数实在是有些复杂，所以 Java 并发包里提供了一个线程池的静态工厂类 Executors，利用 Executors 你可以快速创建线程池。不过目前大厂的编码规范中基本上都不建议使用 Executors 了。

不建议使用 Executors 的最重要的原因是：Executors 提供的很多方法默认使用的都是无界的 LinkedBlockingQueue，高负载情境下，无界队列很容易导致 OOM，而 OOM 会导致所有请求都无法处理，这是致命问题。所以**强烈建议使用有界队列**。

使用有界队列，当任务过多时，线程池会触发执行拒绝策略，线程池默认的拒绝策略会 throw RejectedExecutionException 这是个运行时异常，对于运行时异常编译器并不强制 catch 它，所以开发人员很容易忽略。因此**默认拒绝策略要慎重使用**。如果线程池处理的任务非常重要，建议自定义自己的拒绝策略；并且在实际工作中，自定义的拒绝策略往往和降级策略配合使用。

使用线程池，还要注意异常处理的问题，例如通过 ThreadPoolExecutor 对象的 execute() 方法提交任务时，如果任务在执行的过程中出现运行时异常，会导致执行任务的线程终止；不过，最致命的是任务虽然异常了，但是你却获取不到任何通知，这会让你误以为任务都执行得很正常。虽然线程池提供了很多用于异常处理的方法，但是最稳妥和简单的方案还是捕获所有异常并按需处理，你可以参考下面的示例代码。

```java
try {
  // 业务逻辑
} catch (RuntimeException x) {
  // 按需处理
} catch (Throwable x) {
  // 按需处理
} 
```

**总结**

《Java 并发编程实战》的第 7 章《取消与关闭》的 7.3 节“处理非正常的线程终止” 详细介绍了异常处理的方案；

第 8 章《线程池的使用》对线程池的使用也有更深入的介绍，如果你感兴趣或有需要的话，建议你仔细阅读。

**课后思考**

使用线程池，默认情况下创建的线程名字都类似`pool-1-thread-2`这样，没有业务含义。而很多情况下为了便于诊断问题，都需要给线程赋予一个有意义的名字，那你知道有哪些办法可以给线程池里的线程指定名字吗？

# 23 | Future：如何用多线程实现最优的“烧水泡茶”程序？

在上一篇文章中，我们介绍了 ThreadPoolExecutor 的 `void execute(Runnable command)` 方法，利用这个方法虽然可以提交任务，但是却没有办法获取任务的执行结果（execute() 方法没有返回值）。而很多场景下，我们又都是需要获取任务的执行结果的。

下面我们就来介绍一下使用 ThreadPoolExecutor 的时候，如何获取任务执行结果。

**如何获取任务执行结果**

Java 通过 ThreadPoolExecutor 提供的 3 个 submit() 方法和 1 个 FutureTask 工具类来支持获得任务执行结果的需求。

下面我们先来介绍这 3 个 submit() 方法，这 3 个方法的方法签名如下。

```java
// 提交 Runnable 任务
Future<?> submit(Runnable task);
// 提交 Callable 任务
<T> Future<T> submit(Callable<T> task);
// 提交 Runnable 任务及结果引用  
<T> Future<T> submit(Runnable task, T result);
```

它们的返回值都是 Future 接口，Future 接口有 5 个方法：

```java
// 取消任务
boolean cancel(boolean mayInterruptIfRunning);
// 判断任务是否已取消  
boolean isCancelled();
// 判断任务是否已结束
boolean isDone();
// 获得任务执行结果
get();
// 获得任务执行结果，支持超时
get(long timeout, TimeUnit unit);
```

这 3 个 submit() 方法之间的区别在于方法参数不同，下面我们简要介绍一下。

1. 提交 Runnable 任务 `submit(Runnable task)` ：这个方法的参数是一个 Runnable 接口，Runnable 接口的 run() 方法是没有返回值的，所以 `submit(Runnable task)` 这个方法返回的 Future 仅可以用来断言任务已经结束了，类似于 Thread.join()。

2. 提交 Callable 任务 `submit(Callable<T> task)`：这个方法的参数是一个 Callable 接口，它只有一个 call() 方法，并且这个方法是有返回值的，所以这个方法返回的 Future 对象可以通过调用其 get() 方法来获取任务的执行结果。

3. 提交 Runnable 任务及结果引用 `submit(Runnable task, T result)`：这个方法很有意思，假设这个方法返回的 Future 对象是 f，f.get() 的返回值就是传给 submit() 方法的参数 result。这个方法该怎么用呢？下面这段示例代码展示了它的经典用法。

   ```java
   ExecutorService executor = Executors.newFixedThreadPool(1);
   // 创建 Result 对象 r
   Result r = new Result();
   r.setAAA(a);
   // 提交任务
   Future<Result> future = executor.submit(new Task(r), r);  
   Result fr = future.get();
   // 下面等式成立
   fr === r;
   fr.getAAA() === a;
   fr.getXXX() === x
    
   class Task implements Runnable {
     Result r;
     // 通过构造函数传入 result
     Task(Result r) {
       this.r = r;
     }
     void run() {
       // 可以操作 result
       a = r.getAAA();
       r.setXXX(x);
     }
   }
   ```

   需要你注意的是 Runnable 接口的实现类 Task 声明了一个有参构造函数 `Task(Result r)` ，创建 Task 对象的时候传入了 result 对象，这样就能在类 Task 的 run() 方法中对 result 进行各种操作了。result 相当于主线程和子线程之间的桥梁，通过它主子线程可以共享数据。

下面我们再来介绍 FutureTask 工具类。

前面我们提到的 Future 是一个接口，而 FutureTask 是一个实实在在的工具类，这个工具类有两个构造函数，它们的参数和前面介绍的 submit() 方法类似。

```java
FutureTask(Callable<V> callable);
FutureTask(Runnable runnable, V result);
```

FutureTask 实现了 Runnable 和 Future 接口，由于实现了 Runnable 接口，所以可以将 FutureTask 对象作为任务提交给 ThreadPoolExecutor 去执行，也可以直接被 Thread 执行；又因为实现了 Future 接口，所以也能用来获得任务的执行结果。下面的示例代码是将 FutureTask 对象提交给 ThreadPoolExecutor 去执行。

```java
// 创建 FutureTask
FutureTask<Integer> futureTask = new FutureTask<>(() -> 1 + 2);
// 创建线程池
ExecutorService es = Executors.newCachedThreadPool();
// 提交 FutureTask 
es.submit(futureTask);
// 获取计算结果
Integer result = futureTask.get();
```

FutureTask 对象直接被 Thread 执行的示例代码如下所示。利用 FutureTask 对象可以很容易获取子线程的执行结果。

```java
// 创建 FutureTask
FutureTask<Integer> futureTask = new FutureTask<>(()-> 1+2);
// 创建并启动线程
Thread T1 = new Thread(futureTask);
T1.start();
// 获取计算结果
Integer result = futureTask.get();
```

**实现最优的"烧水泡茶"程序**

以前初中语文课文里有一篇著名数学家华罗庚先生的文章《统筹方法》，这篇文章里介绍了一个烧水泡茶的例子，文中提到最优的工序应该是下面这样：

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/烧水泡茶最优工序.png" alt="烧水泡茶最优工序" style="zoom:67%;" />

下面我们用程序来模拟一下这个最优工序。我们专栏前面曾经提到，并发编程可以总结为三个核心问题：分工、同步和互斥。编写并发程序，首先要做的就是分工，所谓分工指的是如何高效地拆解任务并分配给线程。对于烧水泡茶这个程序，一种最优的分工方案可以是下图所示的这样：用两个线程 T1 和 T2 来完成烧水泡茶程序，T1 负责洗水壶、烧开水、泡茶这三道工序，T2 负责洗茶壶、洗茶杯、拿茶叶三道工序，其中 T1 在执行泡茶这道工序时需要等待 T2 完成拿茶叶的工序。对于 T1 的这个等待动作，你应该可以想出很多种办法，例如 Thread.join()、CountDownLatch，甚至阻塞队列都可以解决，不过今天我们用 Future 特性来实现。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/烧水泡茶最优分工方案.png" alt="烧水泡茶最优分工方案" style="zoom:67%;" />

下面的示例代码就是用这一章提到的 Future 特性来实现的。首先，我们创建了两个 FutureTask——ft1 和 ft2，ft1 完成洗水壶、烧开水、泡茶的任务，ft2 完成洗茶壶、洗茶杯、拿茶叶的任务；这里需要注意的是 ft1 这个任务在执行泡茶任务前，需要等待 ft2 把茶叶拿来，所以 ft1 内部需要引用 ft2，并在执行泡茶之前，调用 ft2 的 get() 方法实现等待。

```java
// 创建任务 T2 的 FutureTask
FutureTask<String> ft2 = new FutureTask<>(new T2Task());
// 创建任务 T1 的 FutureTask
FutureTask<String> ft1 = new FutureTask<>(new T1Task(ft2));
// 线程 T1 执行任务 ft1
Thread T1 = new Thread(ft1);
T1.start();
// 线程 T2 执行任务 ft2
Thread T2 = new Thread(ft2);
T2.start();
// 等待线程 T1 执行结果
System.out.println(ft1.get());
 
// T1Task 需要执行的任务：
// 洗水壶、烧开水、泡茶
class T1Task implements Callable<String> {
  FutureTask<String> ft2;
  // T1 任务需要 T2 任务的 FutureTask
  T1Task(FutureTask<String> ft2) {
    this.ft2 = ft2;
  }
  @Override
  String call() throws Exception {
    System.out.println("T1: 洗水壶...");
    TimeUnit.SECONDS.sleep(1);
    
    System.out.println("T1: 烧开水...");
    TimeUnit.SECONDS.sleep(15);
    // 获取 T2 线程的茶叶  
    String tf = ft2.get();
    System.out.println("T1: 拿到茶叶:"+tf);
 
    System.out.println("T1: 泡茶...");
    return " 上茶:" + tf;
  }
}
// T2Task 需要执行的任务:
// 洗茶壶、洗茶杯、拿茶叶
class T2Task implements Callable<String> {
  @Override
  String call() throws Exception {
    System.out.println("T2: 洗茶壶...");
    TimeUnit.SECONDS.sleep(1);
 
    System.out.println("T2: 洗茶杯...");
    TimeUnit.SECONDS.sleep(2);
 
    System.out.println("T2: 拿茶叶...");
    TimeUnit.SECONDS.sleep(1);
    return " 龙井 ";
  }
}
// 一次执行结果：
T1: 洗水壶...
T2: 洗茶壶...
T1: 烧开水...
T2: 洗茶杯...
T2: 拿茶叶...
T1: 拿到茶叶: 龙井
T1: 泡茶...
上茶: 龙井
```

**总结**

利用 Java 并发包提供的 Future 可以很容易获得异步任务的执行结果，无论异步任务是通过线程池 ThreadPoolExecutor 执行的，还是通过手工创建子线程来执行的。Future 可以类比为现实世界里的提货单，比如去蛋糕店订生日蛋糕，蛋糕店都是先给你一张提货单，你拿到提货单之后，没有必要一直在店里等着，可以先去干点其他事，比如看场电影；等看完电影后，基本上蛋糕也做好了，然后你就可以凭提货单领蛋糕了。

利用多线程可以快速将一些串行的任务并行化，从而提高性能；如果任务之间有依赖关系，比如当前任务依赖前一个任务的执行结果，这种问题基本上都可以用 Future 来解决。在分析这种问题的过程中，建议你用有向图描述一下任务之间的依赖关系，同时将线程的分工也做好，类似于烧水泡茶最优分工方案那幅图。对照图来写代码，好处是更形象，且不易出错。

**课后思考**

不久前听说小明要做一个询价应用，这个应用需要从三个电商询价，然后保存在自己的数据库里。核心示例代码如下所示，由于是串行的，所以性能很慢，你来试着优化一下吧。

```java
// 向电商 S1 询价，并保存
r1 = getPriceByS1();
save(r1);
// 向电商 S2 询价，并保存
r2 = getPriceByS2();
save(r2);
// 向电商 S3 询价，并保存
r3 = getPriceByS3();
save(r3);
```

# 24 | CompletableFuture：异步编程没那么难

**CompletableFuture 的核心优势**

我们用 CompletableFuture 重新实现前面曾提及的烧水泡茶程序。在下面的程序中，我们分了 3 个任务：任务 1 负责洗水壶、烧开水，任务 2 负责洗茶壶、洗茶杯和拿茶叶，任务 3 负责泡茶。其中任务 3 要等待任务 1 和任务 2 都完成后才能开始。这个分工如下图所示。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/烧水泡茶分工方案.png" alt="烧水泡茶分工方案" style="zoom:67%;" />

下面是代码实现。

（测试代码在 [github](https://github.com/dbses/Test4yang/tree/master/JavaThread/src/main/java/char24/BubbleTeaDemo.java) 上）

```java
// 任务 1：洗水壶 -> 烧开水
CompletableFuture<Void> f1 =  CompletableFuture.runAsync(() -> {
  System.out.println("T1: 洗水壶...");
  sleep(1, TimeUnit.SECONDS);
 
  System.out.println("T1: 烧开水...");
  sleep(15, TimeUnit.SECONDS);
});
// 任务 2：洗茶壶 -> 洗茶杯 -> 拿茶叶
CompletableFuture<String> f2 = CompletableFuture.supplyAsync(() -> {
  System.out.println("T2: 洗茶壶...");
  sleep(1, TimeUnit.SECONDS);
 
  System.out.println("T2: 洗茶杯...");
  sleep(2, TimeUnit.SECONDS);
 
  System.out.println("T2: 拿茶叶...");
  sleep(1, TimeUnit.SECONDS);
  return " 龙井 ";
});
// 任务 3：任务 1 和任务 2 完成后执行：泡茶
CompletableFuture<String> f3 = f1.thenCombine(f2, (__, tf) -> {
    System.out.println("T1: 拿到茶叶:" + tf);
    System.out.println("T1: 泡茶...");
    return " 上茶:" + tf;
  });
// 等待任务 3 执行结果
System.out.println(f3.join());
 
void sleep(int t, TimeUnit u) {
  try {
    u.sleep(t);
  } catch(InterruptedException e) {}
}
// 一次执行结果：
T1: 洗水壶...
T2: 洗茶壶...
T1: 烧开水...
T2: 洗茶杯...
T2: 拿茶叶...
T1: 拿到茶叶: 龙井
T1: 泡茶...
上茶: 龙井
```

从大局上看，你会发现：

1. 无需手工维护线程，没有繁琐的手工维护线程的工作，给任务分配线程的工作也不需要我们关注；
2. 语义更清晰，例如 `f3 = f1.thenCombine(f2, ()->{})` 能够清晰地表述“任务 3 要等待任务 1 和任务 2 都完成后才能开始”；
3. 代码更简练并且专注于业务逻辑，几乎所有代码都是业务逻辑相关的。

**创建 CompletableFuture 对象**

创建 CompletableFuture 对象主要靠下面代码中展示的这 4 个静态方法。

1. runAsync(Runnable runnable)
2. supplyAsync(Supplier<U> supplier)
3. runAsync(Runnable runnable, Executor executor)
4. supplyAsync(Supplier<U> supplier, Executor executor)

1和2之间的区别是：Runnable 接口的 run() 方法没有返回值，而 Supplier 接口的 get() 方法是有返回值的。

12和34之间的区别是：后两个方法可以指定线程池参数。

默认情况下 CompletableFuture 会使用公共的 ForkJoinPool 线程池，这个线程池默认创建的线程数是 CPU 的核数（也可以通过 JVM option:-Djava.util.concurrent.ForkJoinPool.common.parallelism 来设置 ForkJoinPool 线程池的线程数）。如果所有 CompletableFuture 共享一个线程池，那么一旦有任务执行一些很慢的 I/O 操作，就会导致线程池中所有线程都阻塞在 I/O 操作上，从而造成线程饥饿，进而影响整个系统的性能。所以，强烈建议你要**根据不同的业务类型创建不同的线程池，以避免互相干扰**。

创建完 CompletableFuture 对象之后，会自动地异步执行 runnable.run() 方法或者 supplier.get() 方法，对于一个异步操作，你需要关注两个问题：

一个是异步操作什么时候结束，另一个是如何获取异步操作的执行结果。

因为 CompletableFuture 类实现了 Future 接口，所以这两个问题你都可以通过 Future 接口来解决。另外，CompletableFuture 类还实现了 CompletionStage 接口，这个接口内容实在是太丰富了，在 1.8 版本里有 40 个方法，这些方法我们该如何理解呢？

**如何理解 CompletionStage 接口**

你可以站在分工的角度类比一下工作流。任务是有时序关系的，比如有**串行关系、并行关系、汇聚关系**等。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/串行关系.png" alt="串行关系" style="zoom:67%;" />

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/并行关系.png" alt="并行关系" style="zoom:67%;" />

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/汇聚关系.png" alt="汇聚关系" style="zoom:67%;" />

烧水泡茶程序中的汇聚关系是一种 AND 聚合关系，这里的 AND 指的是所有依赖的任务（烧开水和拿茶叶）都完成后才开始执行当前任务（泡茶）。OR 聚合关系指的是依赖的任务只要有一个完成就可以执行当前任务。

下面我们就来一一介绍，CompletionStage 接口如何描述串行关系、AND 聚合关系、OR 聚合关系以及异常处理。

1. 描述串行关系

   CompletionStage 接口里面描述串行关系，主要是 thenApply、thenAccept、thenRun 和 thenCompose 这四个系列的接口。

   ```java
   CompletionStage<R> thenApply(fn);
   CompletionStage<R> thenApplyAsync(fn);
   CompletionStage<Void> thenAccept(consumer);
   CompletionStage<Void> thenAcceptAsync(consumer);
   CompletionStage<Void> thenRun(action);
   CompletionStage<Void> thenRunAsync(action);
   CompletionStage<R> thenCompose(fn);
   CompletionStage<R> thenComposeAsync(fn);
   ```

   thenApply 系列函数里参数 fn 的类型是接口 Function<T, R>，这个接口里与 CompletionStage 相关的方法是 `R apply(T t)`，这个方法既能接收参数也支持返回值，所以 thenApply 系列方法返回的是`CompletionStage<R>`。

   而 thenAccept 系列方法里参数 consumer 的类型是接口`Consumer<T>`，这个接口里与 CompletionStage 相关的方法是 `void accept(T t)`，这个方法虽然支持参数，但却不支持返回值，所以 thenAccept 系列方法返回的是`CompletionStage<Void>`。

   thenRun 系列方法里 action 的参数是 Runnable，所以 action 既不能接收参数也不支持返回值，所以 thenRun 系列方法返回的也是`CompletionStage<Void>`。

   这些方法里面 Async 代表的是异步执行 fn、consumer 或者 action。其中，需要你注意的是 thenCompose 系列方法，这个系列的方法会新创建出一个子流程，最终结果和 thenApply 系列是相同的。

   通过下面的示例代码，你可以看一下 thenApply() 方法是如何使用的。首先通过 supplyAsync() 启动一个异步流程，之后是两个串行操作，整体看起来还是挺简单的。不过，虽然这是一个异步流程，但任务【1】【2】【3】却是串行执行的，【2】依赖【1】的执行结果，【3】依赖【2】的执行结果。

   ```java
   CompletableFuture<String> f0 = CompletableFuture
     .supplyAsync(() -> "Hello World")  //【1】
     .thenApply(s -> s + " QQ")         //【2】
     .thenApply(String::toUpperCase);   //【3】
    
   System.out.println(f0.join());
   // 输出结果
   Hello World QQ
   ```

2. 描述 AND 汇聚关系

   CompletionStage 接口里面描述 AND 汇聚关系，主要是 thenCombine、thenAcceptBoth 和 runAfterBoth 系列的接口，这些接口的区别也是源自 fn、consumer、action 这三个核心参数不同。

   ```java
   CompletionStage<R> thenCombine(other, fn);
   CompletionStage<R> thenCombineAsync(other, fn);
   CompletionStage<Void> thenAcceptBoth(other, consumer);
   CompletionStage<Void> thenAcceptBothAsync(other, consumer);
   CompletionStage<Void> runAfterBoth(other, action);
   CompletionStage<Void> runAfterBothAsync(other, action);
   ```

3. 描述 OR 汇聚关系

   CompletionStage 接口里面描述 OR 汇聚关系，主要是 applyToEither、acceptEither 和 runAfterEither 系列的接口，这些接口的区别也是源自 fn、consumer、action 这三个核心参数不同。

   ```java
   CompletionStage applyToEither(other, fn);
   CompletionStage applyToEitherAsync(other, fn);
   CompletionStage acceptEither(other, consumer);
   CompletionStage acceptEitherAsync(other, consumer);
   CompletionStage runAfterEither(other, action);
   CompletionStage runAfterEitherAsync(other, action);
   ```

   下面的示例代码展示了如何使用 applyToEither() 方法来描述一个 OR 汇聚关系。

   ```java
   CompletableFuture<String> f1 = CompletableFuture.supplyAsync(() -> {
       int t = getRandom(5, 10);
       sleep(t, TimeUnit.SECONDS);
       return String.valueOf(t);
   });
    
   CompletableFuture<String> f2 = CompletableFuture.supplyAsync(() -> {
       int t = getRandom(5, 10);
       sleep(t, TimeUnit.SECONDS);
       return String.valueOf(t);
   });
    
   CompletableFuture<String> f3 = f1.applyToEither(f2,s -> s);
    
   System.out.println(f3.join());
   ```

4. 异常处理

虽然上面我们提到的 fn、consumer、action 它们的核心方法都**不允许抛出可检查异常，但是却无法限制它们抛出运行时异常**，例如下面的代码，执行 `7/0` 就会出现除零错误这个运行时异常。非异步编程里面，我们可以使用 try{}catch{}来捕获并处理异常，那在异步编程里面，异常该如何处理呢？

```java
CompletableFuture<Integer> f0 = CompletableFuture.
    .supplyAsync(() -> (7 / 0))
    .thenApply(r -> r * 10);
System.out.println(f0.join());
```

CompletionStage 接口给我们提供的方案非常简单，比 try{}catch{}还要简单，下面是相关的方法，使用这些方法进行异常处理和串行操作是一样的，都支持链式编程方式。

```java
CompletionStage exceptionally(fn);
CompletionStage<R> whenComplete(consumer);
CompletionStage<R> whenCompleteAsync(consumer);
CompletionStage<R> handle(fn);
CompletionStage<R> handleAsync(fn);
```

下面的示例代码展示了如何使用 exceptionally() 方法来处理异常，exceptionally() 的使用非常类似于 try{}catch{}中的 catch{}，但是由于支持链式编程方式，所以相对更简单。既然有 try{}catch{}，那就一定还有 try{}finally{}，whenComplete() 和 handle() 系列方法就类似于 try{}finally{}中的 finally{}，无论是否发生异常都会执行 whenComplete() 中的回调函数 consumer 和 handle() 中的回调函数 fn。whenComplete() 和 handle() 的区别在于 whenComplete() 不支持返回结果，而 handle() 是支持返回结果的。

```java
CompletableFuture<Integer> f0 = CompletableFuture
    .supplyAsync(() -> 7 / 0))
    .thenApply(r -> r * 10)
    .exceptionally(e -> 0);
System.out.println(f0.join());
```

**总结**

CompletableFuture 已经能够满足简单的异步编程需求，如果你对异步编程感兴趣，可以重点关注 RxJava 这个项目，利用 RxJava，即便在 Java 1.6 版本也能享受异步编程的乐趣。

**课后思考**

创建采购订单的时候，需要校验一些规则，例如最大金额是和采购员级别相关的。有同学利用 CompletableFuture 实现了这个校验的功能，逻辑很简单，首先是从数据库中把相关规则查出来，然后执行规则校验。你觉得他的实现是否有问题呢？

```java
// 采购订单
PurchersOrder po;
CompletableFuture<Boolean> cf = CompletableFuture.supplyAsync(() -> {
    // 在数据库中查询规则
    return findRuleByJdbc();
  }).thenApply(r -> {
    // 规则校验
    return check(po, r);
});
Boolean isOk = cf.join();
```

答：

1，读数据库属于io操作，应该放在单独线程池，避免线程饥饿；
2，异常未处理。

# 25 | CompletionService：如何批量执行异步任务？

在第23篇的思考题，如何优化一个询价应用的核心代码？如果采用“ThreadPoolExecutor+Future”的方案，你的优化结果很可能是下面示例代码这样：用三个线程异步执行询价，通过三次调用 Future 的 get() 方法获取询价结果，之后将询价结果保存在数据库中。

```java
// 创建线程池
ExecutorService executor = Executors.newFixedThreadPool(3);
// 异步向电商 S1 询价
Future<Integer> f1 = executor.submit(() -> getPriceByS1());
// 异步向电商 S2 询价
Future<Integer> f2 = executor.submit(() -> getPriceByS2());
// 异步向电商 S3 询价
Future<Integer> f3 = executor.submit(() -> getPriceByS3());
    
// 获取电商 S1 报价并保存
r = f1.get();
executor.execute(() -> save(r));
  
// 获取电商 S2 报价并保存
r = f2.get();
executor.execute(() -> save(r));
  
// 获取电商 S3 报价并保存  
r = f3.get();
executor.execute(() -> save(r));
```

上面的这个方案本身没有太大问题，但是有个地方的处理需要你注意，那就是如果获取电商 S1 报价的耗时很长，那么即便获取电商 S2 报价的耗时很短，也无法让保存 S2 报价的操作先执行，因为这个主线程都阻塞在了 `f1.get()` 操作上。这点小瑕疵你该如何解决呢？

```java
// 创建阻塞队列
BlockingQueue<Integer> bq = new LinkedBlockingQueue<>();
// 电商 S1 报价异步进入阻塞队列  
executor.execute(() -> bq.put(f1.get()));
// 电商 S2 报价异步进入阻塞队列  
executor.execute(() -> bq.put(f2.get()));
// 电商 S3 报价异步进入阻塞队列  
executor.execute(() -> bq.put(f3.get()));
// 异步保存所有报价  
for (int i=0; i<3; i++) {
  Integer r = bq.take();
  executor.execute(() -> save(r));
} 
```

**利用 CompletionService 实现询价系统**

不过在实际项目中，并不建议你这样做，因为 Java SDK 并发包里已经提供了设计精良的 CompletionService。利用 CompletionService 不但能帮你解决先获取到的报价先保存到数据库的问题，而且还能让代码更简练。

CompletionService 的实现原理也是内部维护了一个阻塞队列，当任务执行结束就把任务的执行结果加入到阻塞队列中，不同的是 CompletionService 是把任务执行结果的 Future 对象加入到阻塞队列中，而上面的示例代码是把任务最终的执行结果放入了阻塞队列中。

那到底该如何创建 CompletionService 呢？

CompletionService 接口的实现类是 ExecutorCompletionService，这个实现类的构造方法有两个，分别是：

```java
// 1
ExecutorCompletionService(Executor executor);
// 2
ExecutorCompletionService(
    Executor executor, BlockingQueue<Future<V>> completionQueue);
```

这两个构造方法都需要传入一个线程池，如果不指定 completionQueue，那么默认会使用无界的 LinkedBlockingQueue。任务执行结果的 Future 对象就是加入到 completionQueue 中。

下面的示例代码完整地展示了如何利用 CompletionService 来实现高性能的询价系统。其中，我们没有指定 completionQueue，因此默认使用无界的 LinkedBlockingQueue。之后通过 CompletionService 接口提供的 submit() 方法提交了三个询价操作，这三个询价操作将会被 CompletionService 异步执行。最后，我们通过 CompletionService 接口提供的 take() 方法获取一个 Future 对象（前面我们提到过，加入到阻塞队列中的是任务执行结果的 Future 对象），调用 Future 对象的 get() 方法就能返回询价操作的执行结果了。

```java
// 创建线程池
ExecutorService executor = Executors.newFixedThreadPool(3);
// 创建 CompletionService
CompletionService<Integer> cs = new ExecutorCompletionService<>(executor);
// 异步向电商 S1 询价
cs.submit(() -> getPriceByS1());
// 异步向电商 S2 询价
cs.submit(() -> getPriceByS2());
// 异步向电商 S3 询价
cs.submit(() -> getPriceByS3());
// 将询价结果异步保存到数据库
for (int i = 0; i < 3; i++) {
  Integer r = cs.take().get();
  executor.execute(() -> save(r));
}
```

**CompletionService 接口说明**

下面我们详细地介绍一下 CompletionService 接口提供的方法，CompletionService 接口提供的方法有 5 个，这 5 个方法的方法签名如下所示。

```java
Future<V> submit(Callable<V> task);
Future<V> submit(Runnable task, V result);
Future<V> take() throws InterruptedException;
Future<V> poll();
Future<V> poll(long timeout, TimeUnit unit) throws InterruptedException;
```

其中，submit() 相关的方法有两个。一个方法参数是`Callable<V> task`，前面利用 CompletionService 实现询价系统的示例代码中，我们提交任务就是用的它。另外一个方法有两个参数，分别是`Runnable task`和`V result`，这个方法类似于 ThreadPoolExecutor 的 `<T> Future<T> submit(Runnable task, T result)`。

CompletionService 接口其余的 3 个方法，都是和阻塞队列相关的，take()、poll() 都是从阻塞队列中获取并移除一个元素；它们的区别在于如果阻塞队列是空的，那么调用 take() 方法的线程会被阻塞，而 poll() 方法会返回 null 值。 `poll(long timeout, TimeUnit unit)`方法支持以超时的方式获取并移除阻塞队列头部的一个元素，如果等待了 timeout unit 时间，阻塞队列还是空的，那么该方法会返回 null 值。

**利用 CompletionService 实现 Dubbo 中的 Forking Cluster**

Dubbo 中有一种叫做**Forking 的集群模式**，这种集群模式下，支持**并行地调用多个查询服务，只要有一个成功返回结果，整个服务就可以返回了**。例如你需要提供一个地址转坐标的服务，为了保证该服务的高可用和性能，你可以并行地调用 3 个地图服务商的 API，然后只要有 1 个正确返回了结果 r，那么地址转坐标这个服务就可以直接返回 r 了。这种集群模式可以容忍 2 个地图服务商服务异常，但缺点是消耗的资源偏多。

```java
geocoder(addr) {
  // 并行执行以下 3 个查询服务， 
  r1=geocoderByS1(addr);
  r2=geocoderByS2(addr);
  r3=geocoderByS3(addr);
  // 只要 r1,r2,r3 有一个返回
  // 则返回
  return r1|r2|r3;
}
```

利用 CompletionService 可以快速实现 Forking 这种集群模式，比如下面的示例代码就展示了具体是如何实现的。

```java
// 创建线程池
ExecutorService executor = Executors.newFixedThreadPool(3);
// 创建 CompletionService
CompletionService<Integer> cs = new ExecutorCompletionService<>(executor);
// 用于保存 Future 对象
List<Future<Integer>> futures = new ArrayList<>(3);
// 提交异步任务，并保存 future 到 futures 
futures.add(cs.submit(() -> geocoderByS1()));
futures.add(cs.submit(() -> geocoderByS2()));
futures.add(cs.submit(() -> geocoderByS3()));
// 获取最快返回的任务执行结果
Integer r = 0;
try {
  // 只要有一个成功返回，则 break
  for (int i = 0; i < 3; ++i) {
    r = cs.take().get();
    // 简单地通过判空来检查是否成功返回
    if (r != null) {
      break;
    }
  }
} finally {
  // 取消所有任务
  for(Future<Integer> f : futures)
    f.cancel(true);
}
// 返回结果
return r;
```

首先我们创建了一个线程池 executor 、一个 CompletionService 对象 cs 和一个`Future<Integer>`类型的列表 futures，每次通过调用 CompletionService 的 submit() 方法提交一个异步任务，会返回一个 Future 对象，我们把这些 Future 对象保存在列表 futures 中。通过调用 `cs.take().get()`，我们能够拿到最快返回的任务执行结果，只要我们拿到一个正确返回的结果，就可以取消所有任务并且返回最终结果了。

**总结**

当需要批量提交异步任务的时候建议你使用 CompletionService。CompletionService 将线程池 Executor 和阻塞队列 BlockingQueue 的功能融合在了一起，能够让批量异步任务的管理更简单。除此之外，CompletionService 能够让异步任务的执行结果有序化，先执行完的先进入阻塞队列，利用这个特性，你可以轻松实现后续处理的有序性，避免无谓的等待，同时还可以快速实现诸如 Forking Cluster 这样的需求。

CompletionService 的实现类 ExecutorCompletionService，需要你自己创建线程池，虽看上去有些啰嗦，但好处是你可以让多个 ExecutorCompletionService 的线程池隔离，这种隔离性能避免几个特别耗时的任务拖垮整个应用的风险。

**课后思考**

本章使用 CompletionService 实现了一个询价应用的核心功能，后来又有了新的需求，需要计算出最低报价并返回，下面的示例代码尝试实现这个需求，你看看是否存在问题呢？

```java
// 创建线程池
ExecutorService executor = Executors.newFixedThreadPool(3);
// 创建 CompletionService
CompletionService<Integer> cs = new ExecutorCompletionService<>(executor);
// 异步向电商 S1 询价
cs.submit(() -> getPriceByS1());
// 异步向电商 S2 询价
cs.submit(() -> getPriceByS2());
// 异步向电商 S3 询价
cs.submit(() -> getPriceByS3());
// 将询价结果异步保存到数据库
// 并计算最低报价
AtomicReference<Integer> m = new AtomicReference<>(Integer.MAX_VALUE);
for (int i=0; i<3; i++) {
  executor.execute(() -> {
    Integer r = null;
    try {
      r = cs.take().get();
    } catch (Exception e) {}
    save(r);
    m.set(Integer.min(m.get(), r));
  });
}
return m;
```

答：问题出在return m这里需要等待三个线程执行完成，但是并没有。

# 26 | Fork/Join：单机版的MapReduce

前面几篇文章我们介绍了线程池、Future、CompletableFuture 和 CompletionService，仔细观察你会发现这些工具类都是在帮助我们站在任务的视角来解决并发问题，而不是让我们纠缠在线程之间如何协作的细节上（比如线程之间如何实现等待、通知等）。**对于简单的并行任务，你可以通过“线程池 +Future”的方案来解决；如果任务之间有聚合关系，无论是 AND 聚合还是 OR 聚合，都可以通过 CompletableFuture 来解决；而批量的并行任务，则可以通过 CompletionService 来解决。**

我们一直讲，并发编程可以分为三个层面的问题，分别是分工、协作和互斥，当你关注于任务的时候，你会发现你的视角已经从并发编程的细节中跳出来了，你应用的更多的是现实世界的思维模式，类比的往往是现实世界里的分工，所以我把线程池、Future、CompletableFuture 和 CompletionService 都列到了分工里面。

下面我用现实世界里的工作流程图描述了并发编程领域的简单并行任务、聚合任务和批量并行任务，辅以这些流程图，相信你一定能将你的思维模式转换到现实世界里来。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/简单并行任务、聚合任务和批量并行任务示意图.png" alt="简单并行任务、聚合任务和批量并行任务示意图" style="zoom:67%;" />

上面提到的简单并行、聚合、批量并行这三种任务模型，基本上能够覆盖日常工作中的并发场景了，但还是不够全面，因为还有一种“分治”的任务模型没有覆盖到。**分治**，顾名思义，即分而治之，是一种解决复杂问题的思维方法和模式；具体来讲，指的是**把一个复杂的问题分解成多个相似的子问题，然后再把子问题分解成更小的子问题，直到子问题简单到可以直接求解**。理论上来讲，解决每一个问题都对应着一个任务，所以对于问题的分治，实际上就是对于任务的分治。

分治思想在很多领域都有广泛的应用，例如算法领域有分治算法（归并排序、快速排序都属于分治算法，二分法查找也是一种分治算法）；大数据领域知名的计算框架 MapReduce 背后的思想也是分治。既然分治这种任务模型如此普遍，那 Java 显然也需要支持，Java 并发包里提供了一种叫做 Fork/Join 的并行计算框架，就是用来支持分治这种任务模型的。

**分治任务模型**

这里你需要先深入了解一下分治任务模型，分治任务模型可分为两个阶段：一个阶段是**任务分解**，也就是将任务迭代地分解为子任务，直至子任务可以直接计算出结果；另一个阶段是**结果合并**，即逐层合并子任务的执行结果，直至获得最终结果。下图是一个简化的分治任务模型图，你可以对照着理解。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/简版分治任务模型图.png" alt="简版分治任务模型图" style="zoom:67%;" />

在这个分治任务模型里，任务和分解后的子任务具有相似性，这种相似性往往体现在任务和子任务的算法是相同的，但是计算的数据规模是不同的。具备这种相似性的问题，我们往往都采用递归算法。

**Fork/Join 的使用**

Fork/Join 是一个并行计算的框架，主要就是用来支持分治任务模型的，这个计算框架里的**Fork 对应的是分治任务模型里的任务分解，Join 对应的是结果合并**。Fork/Join 计算框架主要包含两部分，一部分是**分治任务的线程池 ForkJoinPool**，另一部分是**分治任务 ForkJoinTask**。这两部分的关系类似于 ThreadPoolExecutor 和 Runnable 的关系，都可以理解为提交任务到线程池，只不过分治任务有自己独特类型 ForkJoinTask。

ForkJoinTask 是一个抽象类，它的方法有很多，最核心的是 fork() 方法和 join() 方法，其中 fork() 方法会异步地执行一个子任务，而 join() 方法则会阻塞当前线程来等待子任务的执行结果。ForkJoinTask 有两个子类——RecursiveAction 和 RecursiveTask，通过名字你就应该能知道，它们都是用递归的方式来处理分治任务的。这两个子类都定义了抽象方法 compute()，不过区别是 RecursiveAction 定义的 compute() 没有返回值，而 RecursiveTask 定义的 compute() 方法是有返回值的。这两个子类也是抽象类，在使用的时候，需要你定义子类去扩展。

接下来我们就来实现一下，看看如何用 Fork/Join 这个并行计算框架计算斐波那契数列（下面的代码源自 Java 官方示例）。首先我们需要创建一个分治任务线程池以及计算斐波那契数列的分治任务，之后通过调用分治任务线程池的 invoke() 方法来启动分治任务。由于计算斐波那契数列需要有返回值，所以 Fibonacci 继承自 RecursiveTask。分治任务 Fibonacci 需要实现 compute() 方法，这个方法里面的逻辑和普通计算斐波那契数列非常类似，区别之处在于计算 `Fibonacci(n - 1)` 使用了异步子任务，这是通过 `f1.fork()` 这条语句实现的。

```java
static void main(String[] args) {
  // 创建分治任务线程池  
  ForkJoinPool fjp = new ForkJoinPool(4);
  // 创建分治任务
  Fibonacci fib = new Fibonacci(30);   
  // 启动分治任务  
  Integer result = fjp.invoke(fib);
  // 输出结果  
  System.out.println(result);
}
// 递归任务
static class Fibonacci extends RecursiveTask<Integer> {
  final int n;
  Fibonacci(int n) {this.n = n;}
  protected Integer compute(){
    if (n <= 1)
      return n;
    Fibonacci f1 = new Fibonacci(n - 1);
    // 创建子任务  
    f1.fork();
    Fibonacci f2 = new Fibonacci(n - 2);
    // 等待子任务结果，并合并结果  
    return f2.compute() + f1.join();
  }
}
```

**ForkJoinPool 工作原理**

Fork/Join 并行计算的核心组件是 ForkJoinPool，所以下面我们就来简单介绍一下 ForkJoinPool 的工作原理。

通过专栏前面文章的学习，你应该已经知道 ThreadPoolExecutor 本质上是一个生产者 - 消费者模式的实现，内部有一个任务队列，这个任务队列是生产者和消费者通信的媒介；ThreadPoolExecutor 可以有多个工作线程，但是这些工作线程都共享一个任务队列。

ForkJoinPool 本质上也是一个生产者 - 消费者的实现，但是更加智能，你可以参考下面的 ForkJoinPool 工作原理图来理解其原理。ThreadPoolExecutor 内部只有一个任务队列，而 ForkJoinPool 内部有多个任务队列，当我们通过 ForkJoinPool 的 invoke() 或者 submit() 方法提交任务时，ForkJoinPool 根据一定的路由规则把任务提交到一个任务队列中，如果任务在执行过程中会创建出子任务，那么子任务会提交到工作线程对应的任务队列中。

如果工作线程对应的任务队列空了，是不是就没活儿干了呢？不是的，ForkJoinPool 支持一种叫做“**任务窃取**”的机制，如果工作线程空闲了，那它可以“窃取”其他工作任务队列里的任务，例如下图中，线程 T2 对应的任务队列已经空了，它可以“窃取”线程 T1 对应的任务队列的任务。如此一来，所有的工作线程都不会闲下来了。

ForkJoinPool 中的任务队列采用的是双端队列，工作线程正常获取任务和“窃取任务”分别是从任务队列不同的端消费，这样能避免很多不必要的数据竞争。我们这里介绍的仅仅是简化后的原理，ForkJoinPool 的实现远比我们这里介绍的复杂。

<img src="https://gitee.com/yanglu_u/ImgRepository/raw/master/images/ForkJoinPool 工作原理图.png" alt="ForkJoinPool 工作原理图" style="zoom:67%;" />

**模拟 MapReduce 统计单词数量**

学习 MapReduce 有一个入门程序，统计一个文件里面每个单词的数量，下面我们来看看如何用 Fork/Join 并行计算框架来实现。

我们可以先用二分法递归地将一个文件拆分成更小的文件，直到文件里只有一行数据，然后统计这一行数据里单词的数量，最后再逐级汇总结果，你可以对照前面的简版分治任务模型图来理解这个过程。

思路有了，我们马上来实现。下面的示例程序用一个字符串数组 `String[] fc` 来模拟文件内容，fc 里面的元素与文件里面的行数据一一对应。关键的代码在 `compute()` 这个方法里面，这是一个递归方法，前半部分数据 fork 一个递归任务去处理（关键代码 mr1.fork()），后半部分数据则在当前任务中递归处理（mr2.compute()）。

```java
static void main(String[] args){
    String[] fc = {"hello world",
                   "hello me",
                   "hello fork",
                   "hello join",
                   "fork join in world"};
    // 创建 ForkJoin 线程池    
    ForkJoinPool fjp = new ForkJoinPool(3);
    // 创建任务    
    MR mr = new MR(fc, 0, fc.length);  
    // 启动任务    
    Map<String, Long> result = fjp.invoke(mr);
    // 输出结果    
    result.forEach((k, v) -> System.out.println(k+":"+v));
}
//MR 模拟类
static class MR extends RecursiveTask<Map<String, Long>> {
    private String[] fc;
    private int start, end;
    // 构造函数
    MR(String[] fc, int fr, int to){
        this.fc = fc;
        this.start = fr;
        this.end = to;
    }
    @Override 
    protected Map<String, Long> compute() {
        if (end - start == 1) {
            return calc(fc[start]);
        } else {
            int mid = (start+end) / 2;
            MR mr1 = new MR(fc, start, mid);
            mr1.fork();
            MR mr2 = new MR(fc, mid, end);
            // 计算子任务，并返回合并的结果    
            return merge(mr2.compute(), mr1.join());
        }
    }
    // 合并结果
    private Map<String, Long> merge(Map<String, Long> r1, Map<String, Long> r2) {
        Map<String, Long> result = new HashMap<>();
        result.putAll(r1);
        // 合并结果
        r2.forEach((k, v) -> {
            Long c = result.get(k);
            if (c != null) {
                result.put(k, c+v);
            } else {
                result.put(k, v);
            } 
        });
        return result;
    }
    // 统计单词数量
    private Map<String, Long> calc(String line) {
        Map<String, Long> result = new HashMap<>();
        // 分割单词    
        String [] words = line.split("\\s+");
        // 统计单词数量    
        for (String w : words) {
            Long v = result.get(w);
            if (v != null) 
                result.put(w, v+1);
            else
                result.put(w, 1L);
        }
        return result;
    }
}
```

**总结**

Java 1.8 提供的 Stream API 里面并行流也是以 ForkJoinPool 为基础的。不过需要你注意的是，默认情况下所有的并行流计算都共享一个 ForkJoinPool，这个共享的 ForkJoinPool 默认的线程数是 CPU 的核数；如果所有的并行流计算都是 CPU 密集型计算的话，完全没有问题，但是如果存在 I/O 密集型的并行流计算，那么很可能会因为一个很慢的 I/O 计算而拖慢整个系统的性能。所以**建议用不同的 ForkJoinPool 执行不同类型的计算任务**。

**课后思考**

对于一个 CPU 密集型计算程序，在单核 CPU 上，使用 Fork/Join 并行计算框架是否能够提高性能呢？

CPU同一时间只能处理一个线程，所以理论上，纯cpu密集型计算任务单线程就够了。多线程的话，线程上下文切换带来的线程现场保存和恢复也会带来额外开销。



