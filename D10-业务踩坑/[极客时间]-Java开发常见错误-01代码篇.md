# 01 | 正确使用并发工具类库

我们来看看在使用并发工具时，经常遇到哪些坑，以及如何解决、避免这些坑。

**踩坑1：线程池中使用 ThreadLocal 导致数据串了**

- 案例场景

某业务组同学在生产上有时获取到的用户信息是别人的。使用的代码如下。

```java
@GetMapping("wrong")
public Map wrong(@RequestParam("userId") Integer userId) {
    String before = Thread.currentThread().getName() + ":" + currentUser.get();
    currentUser.set(userId);
    String after = Thread.currentThread().getName() + ":" + currentUser.get();
    Map result = new HashMap();
    result.put("before", before);
    result.put("after", after);
    return result;
}
```

为了更快地重现这个问题，我在配置文件中设置一下 Tomcat 的参数，把工作线程池最大线程数设置为 1，这样始终是同一个线程在处理请求：

```properties
server.tomcat.max-threads=1
```

先让用户 1 来请求接口，然后调用接口得到如下结果：

```json
{
  "before": "http-nio-8080-exec-1:null",
  "after": "http-nio-8080-exec-1:1"
}
```

可以看到第一和第二次获取到用户 ID 分别是 null 和 1，符合预期。接口用户 2 来请求接口，这次就出现了 Bug：

```json
{
  "before": "http-nio-8080-exec-1:1",
  "after": "http-nio-8080-exec-1:2"
}
```

第一次和第二次获取到用户 ID 分别是 1 和 2，显然第一次获取到了用户 1 的信息，原因就是 Tomcat 的线程池重用了线程。从上面结果可以看到，两次请求的线程都是同一个线程：http-nio-8080-exec-1。

- 原因分析

ThreadLocal 适用于变量在线程间隔离，上述代码使用了 ThreadLocal 来缓存获取到的用户信息。程序运行在 Tomcat 中，而 Tomcat 的工作线程是基于线程池的。

- 解决方案

```java
@GetMapping("right")
public Map right(@RequestParam("userId") Integer userId) {
    String before = Thread.currentThread().getName() + ":" + currentUser.get();
    currentUser.set(userId);
    try {
        String after = Thread.currentThread().getName() + ":" + currentUser.get();
        Map result = new HashMap();
        result.put("before", before);
        result.put("after", after);
        return result;
    } finally {
        currentUser.remove();
    }
}
```

**踩坑2：使用 ConcurrentHashMap 没对复合逻辑加锁导致业务逻辑错误**

- 案例场景

有一个含 900 个元素的 Map，现在再补充 100 个元素进去，这个补充操作由 10 个线程并发进行。

开发人员误以为使用了 ConcurrentHashMap 就不会有线程安全问题。于是写出了下面的代码：

```java
private static int THREAD_COUNT = 10;
private static int ITEM_COUNT = 1000;

private ConcurrentHashMap<String, Long> getData(int count) {
    return LongStream.rangeClosed(1, count)
            .boxed()
            .collect(Collectors.toConcurrentMap(i -> UUID.randomUUID().toString(), Function.identity(),
                    (o1, o2) -> o1, ConcurrentHashMap::new));
}

@GetMapping("wrong")
public String wrong() throws InterruptedException {
    ConcurrentHashMap<String, Long> concurrentHashMap = getData(ITEM_COUNT - 100);
    log.info("init size:{}", concurrentHashMap.size());

    ForkJoinPool forkJoinPool = new ForkJoinPool(THREAD_COUNT);
    forkJoinPool.execute(() -> IntStream.rangeClosed(1, 10).parallel().forEach(i -> {
        // 计算还需要补充多少元素
        int gap = ITEM_COUNT - concurrentHashMap.size();
        log.info("gap size:{}", gap);
        // 将缺少的元素添加进去
        concurrentHashMap.putAll(getData(gap));
    }));
    forkJoinPool.shutdown();
    forkJoinPool.awaitTermination(1, TimeUnit.HOURS);

    log.info("finish size:{}", concurrentHashMap.size());
    return "OK";
}
```

结果输出日志如下：

![image-20210603214203964](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210603214204.png)

初始大小 900 符合预期，还需要填充 100 个元素。

worker1 线程查询到当前需要填充的元素为 36，竟然还不是 100 的倍数。worker13 线程查询到需要填充的元素数是负的，显然已经过度填充了。最后 HashMap 的总项目数是 1536，显然不符合填充满 1000 的预期。

- 原因分析

ConcurrentHashMap 就像是一个大篮子， 现在这个篮子里有 900 个桔子，我们期望把这个篮子装满 1000 个桔子，也就是再装 100 个桔子。有 10 个工人来干这件事儿，大家先后到岗后会计算还需要补多少个桔子进去，最后把桔子装入篮子。

但是，工人往这个篮子装 100 个桔子的操作不是原子性的，在别人看来可能会有一个瞬间篮子里有 964 个桔子，还需要补 36 个桔子。

回到 ConcurrentHashMap，它只能保证原子性读写的操作是线程安全的。而诸如 size、isEmpty 和 containsValue 等聚合方法，在并发情况下反映的都是 ConcurrentHashMap 的中间状态。

- 解决方案

解决思路，还是以上面的场景举例。哪个工人先拿到这个篮子，就由这个工人将剩下的桔子放进篮子里去。

```java
@GetMapping("right")
public String right() throws InterruptedException {
    ConcurrentHashMap<String, Long> concurrentHashMap = getData(ITEM_COUNT - 100);
    log.info("init size:{}", concurrentHashMap.size());

    ForkJoinPool forkJoinPool = new ForkJoinPool(THREAD_COUNT);
    // parallel 默认是 cpu-1 个并发
    forkJoinPool.execute(() -> IntStream.rangeClosed(1, 10).parallel().forEach(i -> {
        synchronized (concurrentHashMap) {
            int gap = ITEM_COUNT - concurrentHashMap.size();
            log.info("gap size:{}", gap);
            concurrentHashMap.putAll(getData(gap));
        }
    }));
    forkJoinPool.shutdown();
    forkJoinPool.awaitTermination(1, TimeUnit.HOURS);

    log.info("finish size:{}", concurrentHashMap.size());
    return "OK";
}
```

输出日志如下：

![image-20210603214437847](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210603214437.png)

**踩坑3：使用了 ConcurrentHashMap 但没有充分利用其基于 CAS 安全的方法导致性能问题**

- 案例场景

使用 Map 来统计 Key 出现的次数。具体使用如下：

1. 使用 ConcurrentHashMap 来统计，Key 的范围是 item0~item10；
2. 使用最多 10 个并发，循环操作 1000 万次，每次操作累加随机的 Key；
3. 如果 Key 不存在的话，首次设置值为 1。

```java
private static int LOOP_COUNT = 10000000;
private static int THREAD_COUNT = 10;
private static int ITEM_COUNT = 10;

private Map<String, Long> normaluse() throws InterruptedException {
    ConcurrentHashMap<String, Long> freqs = new ConcurrentHashMap<>(ITEM_COUNT);
    ForkJoinPool forkJoinPool = new ForkJoinPool(THREAD_COUNT);
    forkJoinPool.execute(() -> IntStream.rangeClosed(1, LOOP_COUNT).parallel().forEach(i -> {
                String key = "item" + ThreadLocalRandom.current().nextInt(ITEM_COUNT);
                synchronized (freqs) {
                    if (freqs.containsKey(key)) {
                        freqs.put(key, freqs.get(key) + 1);
                    } else {
                        freqs.put(key, 1L);
                    }
                }
            }
    ));
    forkJoinPool.shutdown();
    forkJoinPool.awaitTermination(1, TimeUnit.HOURS);
    return freqs;
}
```

> 为什么要对 freqs 加锁？
>
> 如果没有锁，2个线程判断 item0 在集合中不存在，同时走到 else 块，会造成统计 item0 应该为 2，而实际为 1。

这种实现方式是一般的实现，所以叫 normal use。不会导致错误的结果，但在性能上却存在问题，因为锁的粒度较大。

- 原因分析

computeIfAbsent 高效的原因是它使用了 Java 自带的 Unsafe 实现的 CAS，它在虚拟机层面确 保了写入数据的原子性，比加锁的效率高得多。

> [computeIfAbsent 和 putIfAbsent 的区别](https://blog.csdn.net/wang_8101/article/details/82191146)

```java
static final <K,V> boolean casTabAt(Node<K,V>[] tab, int i,
                                    Node<K,V> c, Node<K,V> v) {
    return U.compareAndSwapObject(tab, ((long)i << ASHIFT) + ABASE, c, v);
}
```

- 解决方案

```java
private Map<String, Long> gooduse() throws InterruptedException {
    // 这里的 Key 变成 LongAdder 了
    ConcurrentHashMap<String, LongAdder> freqs = new ConcurrentHashMap<>(ITEM_COUNT);
    ForkJoinPool forkJoinPool = new ForkJoinPool(THREAD_COUNT);
    forkJoinPool.execute(() -> IntStream.rangeClosed(1, LOOP_COUNT).parallel().forEach(i -> {
                String key = "item" + ThreadLocalRandom.current().nextInt(ITEM_COUNT);
                // LongAdder # increment() 是线程安全的
                freqs.computeIfAbsent(key, k -> new LongAdder()).increment();
            }
    ));
    forkJoinPool.shutdown();
    forkJoinPool.awaitTermination(1, TimeUnit.HOURS);
    return freqs.entrySet().stream()
            .collect(Collectors.toMap(
                    e -> e.getKey(),
                    e -> e.getValue().longValue())
            );
}
```

来做一个性能测试，测试代码如下：

```java
@GetMapping("good")
public String good() throws InterruptedException {
    StopWatch stopWatch = new StopWatch();
    stopWatch.start("normaluse");
    Map<String, Long> normaluse = normaluse();
    stopWatch.stop();
    Assert.isTrue(normaluse.size() == ITEM_COUNT, "normaluse size error");
    Assert.isTrue(normaluse.entrySet().stream()
                    .mapToLong(item -> item.getValue())
                    .reduce(0, Long::sum) == LOOP_COUNT
            , "normaluse count error");
    stopWatch.start("gooduse");
    Map<String, Long> gooduse = gooduse();
    stopWatch.stop();
    Assert.isTrue(gooduse.size() == ITEM_COUNT, "gooduse size error");
    Assert.isTrue(gooduse.entrySet().stream()
                    .mapToLong(item -> item.getValue())
                    .reduce(0, Long::sum) == LOOP_COUNT
            , "gooduse count error");
    log.info(stopWatch.prettyPrint());
    return "OK";
}
```

结果如下：

![image-20210603222119527](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210603222119.png)

性能提升了 2.8s/0.3s = 9.3 倍。

**踩坑4：在写操作很多的场景下使用 CopyOnWriteArrayList 导致性能问题**

- 案例场景

之前在排查一个生产性能问题时，我们发现一段简单的非数据库操作的业务逻辑，消耗了超出预期的时间，在修改数据时操作本地缓存比回写数据库慢许多。查看代码发现，开发同学使用了 CopyOnWriteArrayList 来缓存大量的数据，而数据变化又比较频繁。

- 原因分析

在 Java 中，CopyOnWriteArrayList 虽然是一个线程安全的 ArrayList，但因为其实现方式是，每次修改数据时都会用 Arrays.copyOf 复制一份数据出来。下面是 CopyOnWriteArrayList 部分源码。

```java
public boolean add(E e) {
    final ReentrantLock lock = this.lock;
    lock.lock();
    try {
        Object[] elements = getArray();
        int len = elements.length;
        Object[] newElements = Arrays.copyOf(elements, len + 1);
        newElements[len] = e;
        setArray(newElements);
        return true;
    } finally {
        lock.unlock();
    }
}
```

每次 add 时，都会用 Arrays.copyOf 创建一个新数组，频繁 add 时内存的申请释放消耗会很大。所以有明显的适用场景，即读多写少或者说希望无锁读的场景。

通过下面代码来分析一下 CopyOnWriteArrayList 和普通加锁方式 ArrayList 的读写性能。

```java
@GetMapping("write")
public Map testWrite() {
    List<Integer> copyOnWriteArrayList = new CopyOnWriteArrayList<>();
    List<Integer> synchronizedList = Collections.synchronizedList(new ArrayList<>());
    StopWatch stopWatch = new StopWatch();
    int loopCount = 100000;
    stopWatch.start("Write:copyOnWriteArrayList");
    IntStream.rangeClosed(1, loopCount)
            .parallel()
            .forEach(__ -> copyOnWriteArrayList.add(ThreadLocalRandom.current().nextInt(loopCount)));
    stopWatch.stop();
    stopWatch.start("Write:synchronizedList");
    IntStream.rangeClosed(1, loopCount)
            .parallel()
            .forEach(__ -> synchronizedList.add(ThreadLocalRandom.current().nextInt(loopCount)));
    stopWatch.stop();
    log.info(stopWatch.prettyPrint());
    Map result = new HashMap();
    result.put("copyOnWriteArrayList", copyOnWriteArrayList.size());
    result.put("synchronizedList", synchronizedList.size());
    return result;
}

private void addAll(List<Integer> list) {
    list.addAll(IntStream.rangeClosed(1, 1000000).boxed().collect(Collectors.toList()));
}

@GetMapping("read")
public Map testRead() {
    List<Integer> copyOnWriteArrayList = new CopyOnWriteArrayList<>();
    List<Integer> synchronizedList = Collections.synchronizedList(new ArrayList<>());
    addAll(copyOnWriteArrayList);
    addAll(synchronizedList);
    StopWatch stopWatch = new StopWatch();
    int loopCount = 1000000;
    int count = copyOnWriteArrayList.size();
    stopWatch.start("Read:copyOnWriteArrayList");
    IntStream.rangeClosed(1, loopCount)
            .parallel()
            .forEach(__ -> copyOnWriteArrayList.get(ThreadLocalRandom.current().nextInt(count)));
    stopWatch.stop();
    stopWatch.start("Read:synchronizedList");
    IntStream.range(0, loopCount)
            .parallel()
            .forEach(__ -> synchronizedList.get(ThreadLocalRandom.current().nextInt(count)));
    stopWatch.stop();
    log.info(stopWatch.prettyPrint());
    Map result = new HashMap();
    result.put("copyOnWriteArrayList", copyOnWriteArrayList.size());
    result.put("synchronizedList", synchronizedList.size());
    return result;
}
```

测试结果如下。

10 万次写操作，CopyOnWriteArray 比同步的 ArrayList 慢 11 倍：

![image-20210603223419463](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210603223419.png)

100 万次读操作，CopyOnWriteArray 比同步的 ArrayList 快 5 倍：

![image-20210603223834431](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210603223834.png)

- 解决方案

使用 ConcurrentHashMap 来缓存。

# 02 | 正确地给代码加锁

**踩坑5：锁加在了不同层面上导致结果不符合预期**

- 案例场景

```java
class Data {
    @Getter
    private static int counter = 0;

    public static int reset() {
        counter = 0;
        return counter;
    }
  
    public synchronized void wrong() {
        counter++;
    }
}
```

测试代码如下：

```java
@GetMapping("wrong")
public int wrong(@RequestParam(value = "count", defaultValue = "1000000") int count) {
    Data.reset();
    IntStream.rangeClosed(1, count).parallel().forEach(i -> new Data().wrong());
    return Data.getCounter();
}
```

预期执行后应该输出 100 万，但页面输出的是 639242。

- 原因分析

静态字段属于类，类级别的锁才能保护；而非静态字段属于类实例，实例级别的锁才可以保护。

- 解决方案

把锁都加在类对象上。

```java
class Data {
    @Getter
    private static int counter = 0;
    private static Object locker = new Object();

    public static int reset() {
        counter = 0;
        return counter;
    }
  
    public void right() {
        synchronized (locker) {
            counter++;
        }
    }
}
```

**踩坑6：锁的粒度过大导致性能问题**

- 案例场景

在业务代码中，有一个 ArrayList 因为会被多个线程操作而需要保护，又有一段比较耗时的操作（代码中的 slow 方法）不涉及线程安全问题。具体代码如下：

```java
private List<Integer> data = new ArrayList<>();

private void slow() {
    try {
        TimeUnit.MILLISECONDS.sleep(10);
    } catch (InterruptedException e) {
    }
}

@GetMapping("wrong")
public int wrong() {
    long begin = System.currentTimeMillis();
    IntStream.rangeClosed(1, 1000).parallel().forEach(i -> {
        synchronized (this) {
            slow();
            data.add(i);
        }
    });
    log.info("took:{}", System.currentTimeMillis() - begin);
    return data.size();
}
```

这样加锁性能很低。

- 原因分析

即使我们确实有一些共享资源需要保护，也要尽可能降低锁的粒度，仅对必要的代码块甚至是需要保护的资源本身加锁。

- 解决方案

```java
@GetMapping("right")
public int right() {
    long begin = System.currentTimeMillis();
    IntStream.rangeClosed(1, 1000).parallel().forEach(i -> {
        slow();
        synchronized (data) {
            data.add(i);
        }
    });
    log.info("took:{}", System.currentTimeMillis() - begin);
    return data.size();
}
```

同样是 1000 次业务操作，个性前后对比耗时分别是 11 秒和 1.4 秒。

**踩坑7：下单时出现了死锁导致下单失败率很高**

- 案例场景

下单操作需要锁定订单中多个商品的库存，拿到所有商品的锁之后进行下单扣减库存操作，全部操作完成之后释放所有的锁。代码上线后发现，下单失败概率很高，失败后需要用户重新下单，极大影响了用户体验，还影响到了销量。

商品定义：

```java
@Data
@RequiredArgsConstructor
static class Item {
    final String name;
    int remaining = 1000;
    @ToString.Exclude
    ReentrantLock lock = new ReentrantLock();
}
```

购物车添加商品：

```java
private ConcurrentHashMap<String, Item> items = new ConcurrentHashMap<>();

public DeadLockController() {
    IntStream.range(0, 10).forEach(i -> items.put("item" + i, new Item("item" + i)));
}

private List<Item> createCart() {
    return IntStream.rangeClosed(1, 3)
            .mapToObj(i -> "item" + ThreadLocalRandom.current().nextInt(items.size()))
            .map(name -> items.get(name)).collect(Collectors.toList());
}
```

下单：

```java
private boolean createOrder(List<Item> order) {
    List<ReentrantLock> locks = new ArrayList<>();

    for (Item item : order) {
        try {
            if (item.lock.tryLock(10, TimeUnit.SECONDS)) {
                locks.add(item.lock);
            } else {
                locks.forEach(ReentrantLock::unlock);
                return false;
            }
        } catch (InterruptedException e) {
        }
    }
    try {
        order.forEach(item -> item.remaining--);
    } finally {
        locks.forEach(ReentrantLock::unlock);
    }
    return true;
}
```

测试代码：

```java
@GetMapping("wrong")
public long wrong() {
    long begin = System.currentTimeMillis();
    long success = IntStream.rangeClosed(1, 100).parallel()
            .mapToObj(i -> {
                List<Item> cart = createCart();
                return createOrder(cart);
            })
            .filter(result -> result)
            .count();
    log.info("success:{} totalRemaining:{} took:{}ms items:{}",
            success,
            items.entrySet().stream().map(item -> item.getValue().remaining).reduce(0, Integer::sum),
            System.currentTimeMillis() - begin, items);
    return success;
}
```

输出日志如下：

![image-20210605232953516](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210605232953.png)

可以看到，100 次下单操作成功了 65 次，10 种商品总计 10000 件，库存总计为 9805， 消耗了 195 件符合预期（65 次下单成功，每次下单包含三件商品），总耗时 50 秒。

- 原因分析

使用 JDK 自带的 VisualVM 工具来跟踪一下，重新执行方法后不久就可以看到，线程 Tab 中提示了死锁问题，根据提示点击右侧线程 Dump 按钮进行线程抓取操作：

![image-20210605233231724](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210605233231.png)

查看抓取出的线程栈，在页面中部可以看到如下日志：

![image-20210605233302370](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210605233302.png)

为什么会有死锁问题呢?

购物车添加商品，首先随机添加了三种商品，假设一个购物车中的商品 是 item1 和 item2，另一个购物车中的商品是 item2 和 item1，一个线程先获取到了 item1 的锁，同时另一个线程获取到了 item2 的锁，然后两个线程接下来要分别获取 item2 和 item1 的锁，这个时候锁已经被对方获取了，只能相互等待一直到 10 秒超时。

- 解决方案

为购物车中的商品排一下序，让所有的线程一定是先获取 item1 的锁然后获取 item2 的锁，就不会有问题了。

```java
@GetMapping("right")
public long right() {
    long begin = System.currentTimeMillis();
    long success = IntStream.rangeClosed(1, 100).parallel()
            .mapToObj(i -> {
                List<Item> cart = createCart().stream()
                        .sorted(Comparator.comparing(Item::getName))
                        .collect(Collectors.toList());
                return createOrder(cart);
            })
            .filter(result -> result)
            .count();
    log.info("success:{} totalRemaining:{} took:{}ms items:{}",
            success,
            items.entrySet().stream().map(item -> item.getValue().remaining).reduce(0, Integer::sum),
            System.currentTimeMillis() - begin, items);
    return success;
}
```

测试一下 right 方法，不管执行多少次都是 100 次成功下单，而且性能相当高，达到了 3000 以上的 TPS：

![image-20210605233946803](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210605233946.png)

> 这里通过避免循环等待从而避免了死锁。
>
> [了解 wrk 压测工具](https://www.cnblogs.com/xinzhao/p/6233009.html)

# 03 | 线程池使用最佳实践

**实践8：线程池需要手动声明**

- 案例场景

使用 FixedThreadPool 的场景如下。

```java
@GetMapping("oom1")
public void oom1() throws InterruptedException {

    ThreadPoolExecutor threadPool = (ThreadPoolExecutor) Executors.newFixedThreadPool(1);
    printStats(threadPool);
    for (int i = 0; i < 100000000; i++) {
        threadPool.execute(() -> {
            String payload = IntStream.rangeClosed(1, 1000000)
                    .mapToObj(__ -> "a")
                    .collect(Collectors.joining("")) + UUID.randomUUID().toString();
            try {
                TimeUnit.HOURS.sleep(1);
            } catch (InterruptedException e) {
            }
            log.info(payload);
        });
    }

    threadPool.shutdown();
    threadPool.awaitTermination(1, TimeUnit.HOURS);
}
```

执行程序后不久，日志中就出现了如下 OOM：

```log
Exception in thread "http-nio-45678-ClientPoller" java.lang.OutOfMemoryError: GC overhead limit exceeded
```

使用 CachedThreadPool 场景如下。

```java
@GetMapping("oom2")
public void oom2() throws InterruptedException {

    ThreadPoolExecutor threadPool = (ThreadPoolExecutor) Executors.newCachedThreadPool();
    printStats(threadPool);
    for (int i = 0; i < 100000000; i++) {
        threadPool.execute(() -> {
            String payload = UUID.randomUUID().toString();
            try {
                TimeUnit.HOURS.sleep(1);
            } catch (InterruptedException e) {
            }
            log.info(payload);
        });
    }
    threadPool.shutdown();
    threadPool.awaitTermination(1, TimeUnit.HOURS);
}
```

程序执行不久后，同样有如下异常：

```log
[11:30:30.487] [http-nio-45678-exec-1] [ERROR] [.a.c.c.C.[.[.[/].[dispatcherServletrue]
java.lang.OutOfMemoryError: unable to create new native thread
```

- 原因分析

newFixedThreadPool 直接 new 了一个 LinkedBlockingQueue，长度是 Integer.MAX_VALUE，可以认为是无界的。如果任务较多并且执行较慢的话，队列可能会快速积压，撑爆内存导致 OOM。

newCachedThreadPool 线程池的最大线程数是 Integer.MAX_VALUE，可以认为是没有上限的，而其工作队列 SynchronousQueue 是一个没有存储空间的阻塞队列。只要有请求到来，就会创建一条新的线程来处理。

大量的任务进来后会创建大量的线程，而线程是需要分配一定的内存空间作为线程栈的，比如 1MB，因此无限制创建线程必然会导致 OOM。

- 解决方案

我们需要根据自己的场景、并发情况来评估线程池的几个核心参数，包括核心线程数、最大线程数、线程回收策略、工作队列的类型，以及拒绝策略，确保线程池的工作行为符合需求，一般都需要设置有界的工作队列和可控的线程数。

任何时候，都应该为自定义线程池指定有意义的名称，以方便排查问题。当出现线程数量暴增、线程死锁、线程占用大量 CPU、线程执行出现异常等问题时，我们往往会抓取线程栈。此时，有意义的线程名称，就可以方便我们定位问题。

我们还应该用一些监控手段来观察线程池的状态，提前观察线程池队列的积压，或者线程数量的快速膨胀，往往可以提早发现并解决问题。

**实践8：务必确认清楚线程池本身是不是复用的**

- 案例场景

某项目生产环境时不时报警提示线程数过多，超过 2000 个，但过一会儿又会降下来，而应用的访问量变化并不大。

为了定位问题，我们在线程数比较高的时候进行线程栈抓取，抓取后发现内存中有 1000 多个自定义线程池。

在项目代码里，找到如下代码：

```java
@GetMapping("wrong")
public String wrong() throws InterruptedException {
    ThreadPoolExecutor threadPool = ThreadPoolHelper.getThreadPool();
    IntStream.rangeClosed(1, 10).forEach(i -> {
        threadPool.execute(() -> {
            String payload = IntStream.rangeClosed(1, 1000000)
                    .mapToObj(__ -> "a")
                    .collect(Collectors.joining("")) + UUID.randomUUID().toString();
            try {
                TimeUnit.SECONDS.sleep(1);
            } catch (InterruptedException e) {
            }
            log.debug(payload);
        });
    });
    return "OK";
}
```

```java
static class ThreadPoolHelper {
    public static ThreadPoolExecutor getThreadPool() {
        return (ThreadPoolExecutor) Executors.newCachedThreadPool();
    }
}
```

- 原因分析

为什么我们能在监控中看到线程数量会下降，而不会撑爆内存呢?

newCachedThreadPool 的核心线程数是 0，而 keepAliveTime 是 60 秒，也就是在 60 秒之后所有的线程都是可以回收的。就因为这个特性，我们的业务程序死得没太难看。

- 解决方案

```java
static class ThreadPoolHelper {
    private static ThreadPoolExecutor threadPoolExecutor = new ThreadPoolExecutor(
            10, 50,
            2, TimeUnit.SECONDS,
            new ArrayBlockingQueue<>(1000),
            new ThreadFactoryBuilder().setNameFormat("demo-threadpool-%d").get());

    static ThreadPoolExecutor getRightThreadPool() {
        return threadPoolExecutor;
    }
}
```

**实践9：仔细斟酌线程池的混用策略**

- 案例场景

某项目业务代码使用了线程池异步处理一些内存中的数据，但通过监控发现处理得非常慢，整个处理过程都是内存中的计算不涉及 IO 操作，也需要数秒的处理时间，应用程序 CPU 占用也不是特别高，有点不可思议。

经排查发现，业务代码使用的线程池，还被一个后台的文件批处理任务用到了。

线程池定义如下：

```java
private static ThreadPoolExecutor threadPool = new ThreadPoolExecutor(
        2, 2,
        1, TimeUnit.HOURS,
        new ArrayBlockingQueue<>(100),
        new ThreadFactoryBuilder().setNameFormat("batchfileprocess-threadpool-%d").get(),
        new ThreadPoolExecutor.CallerRunsPolicy());
```

正常业务处理如下：

```java
private Callable<Integer> calcTask() {
    return () -> {
        TimeUnit.MILLISECONDS.sleep(10);
        return 1;
    };
}

@GetMapping("wrong")
public int wrong() throws ExecutionException, InterruptedException {
    return threadPool.submit(calcTask()).get();
}
```

其他场景混用逻辑如下：

```java
@PostConstruct
public void init() {
    printStats(threadPool);

    new Thread(() -> {
        String payload = IntStream.rangeClosed(1, 1_000_000)
                .mapToObj(__ -> "a")
                .collect(Collectors.joining(""));
        while (true) {
            threadPool.execute(() -> {
                try {
                    Files.write(Paths.get("demo.txt"), Collections.singletonList(LocalTime.now().toString() + ":" + payload), UTF_8, CREATE, TRUNCATE_EXISTING);
                } catch (IOException e) {
                    e.printStackTrace();
                }
                log.info("batch file processing done");
            });
        }
    }).start();
}
```

日志打印如下：

![image-20210606233305715](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210606233305.png)

- 原因分析

线程池的 2 个线程始终处于活跃状态，队列也基本处于打满状态。因为开启了 CallerRunsPolicy 拒绝处理策略，所以当线程满载队列也满的情况下，任务会在提交任务的线程上执行。

- 解决方案

使用独立的线程池来做这样的任务即可。IO 密集型操作的的线程池线程数设置太小会限制吞吐能力。

```java
private static ThreadPoolExecutor asyncCalcThreadPool = new ThreadPoolExecutor(
        200, 200,
        1, TimeUnit.HOURS,
        new ArrayBlockingQueue<>(1000),
        new ThreadFactoryBuilder().setNameFormat("asynccalc-threadpool-%d").get());
        
@GetMapping("right")
public int right() throws ExecutionException, InterruptedException {
    return asyncCalcThreadPool.submit(calcTask()).get();
}
```

调整后，TPS 从 75 增长到了 1737。

# 04 | 连接池：别让连接池帮了倒忙

**连接池的结构**

连接池一般对客户端提供获得连接、归还连接的接口，并暴露最小空闲连接数、最大连接数等可配置参数，在内部则实现连接建立、连接心跳保持、连接管理、空闲连接回收、连接可用性检测等功能。连接池的结构示意图，如下所示：

![image-20210608214800283](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210608214800.png)

涉及 TCP 连接的客户端 SDK，对外提供 API 有三种方式。

- 连接池和连接分离的 API

XXXPool 类负责连接池实现，并且它是线程安全的；从连接池中可以获得连接 XXXConnection，非线程安全的。

（对应上图“连接池”框）

- 内部带有连接池的 API

对外提供一个 XXXClient 类，这个类内部维护了连接池，并且它是线程安全的 。SDK 使用者无需考虑连接的获取和归还问题。

（对应上图蓝色框包裹的部分）

- 非连接池的 API

一般命名为 XXXConnection，每次使 用都需要创建和断开连接，性能一般，且通常不是线程安全的。

（对应上图去掉“连接池”的框）

我们今天就以数据库连接池、Redis 连接池和 HTTP 连接池为例，聊聊使用和配置连接池容易出错的地方。

**踩坑10：误用 Jedis API 导致程序错误**

- 案例场景

先通过一个案例来分析一下 Jedis 属于哪种类型的 API。

数据初始化代码如下：

```java
@PostConstruct
public void init() {
    // 初始化数据
    try (Jedis jedis = new Jedis("127.0.0.1", 6379)) {
        Assert.isTrue("OK".equals(jedis.set("a", "1")), "set a = 1 return OK");
        Assert.isTrue("OK".equals(jedis.set("b", "2")), "set b = 2 return OK");
    }
}
```

测试代码如下：

```java
@GetMapping("/wrong")
public void wrong() throws InterruptedException {
    Jedis jedis = new Jedis("127.0.0.1", 6379);
    new Thread(() -> {
        for (int i = 0; i < 1000; i++) {
            String result = jedis.get("a");
            if (!"1".equals(result)) {
                log.warn("Expect a to be 1 but found {}", result);
                return;
            }
        }
    }).start();
    new Thread(() -> {
        for (int i = 0; i < 1000; i++) {
            String result = jedis.get("b");
            if (!"2".equals(result)) {
                log.warn("Expect b to be 2 but found {}", result);
                return;
            }
        }
    }).start();
    TimeUnit.SECONDS.sleep(5);
}
```

程序执行结果如下：

```java
// 错误1：数据错乱
[14:56:19.069] [Thread-28] [WARN ] [.t.c.c.redis.JedisMisreuseController:45  ] - Expect b to be 2 but found 1

// 错误2：流未正常关闭
redis.clients.jedis.exceptions.JedisConnectionException: Unexpected end of  stream.
  at redis.clients.jedis.util.RedisInputStream.ensureFill(RedisInputStream.java:202)
  at redis.clients.jedis.util.RedisInputStream.readLine(RedisInputStream.java:50)
  at redis.clients.jedis.Protocol.processError(Protocol.java:114)
  at redis.clients.jedis.Protocol.process(Protocol.java:166)
  at redis.clients.jedis.Protocol.read(Protocol.java:220)
  at redis.clients.jedis.Connection.readProtocolWithCheckingBroken(Connection.java:318)
  at redis.clients.jedis.Connection.getBinaryBulkReply(Connection.java:255)
  at redis.clients.jedis.Connection.getBulkReply(Connection.java:245)
  at redis.clients.jedis.Jedis.get(Jedis.java:181)
  at org.geekbang.time.commonmistakes.connectionpool.redis.JedisMisreuseController.lambda$wrong$1(JedisMisreuseController.java:43)
  at java.lang.Thread.run(Thread.java:748)

// 错误3：Redis关闭客户端连接
java.io.IOException: Socket Closed
  at java.net.AbstractPlainSocketImpl.getOutputStream(AbstractPlainSocketImpl.java:440)
  at java.net.Socket$3.run(Socket.java:954)
  at java.net.Socket$3.run(Socket.java:952)
  at java.security.AccessController.doPrivileged(Native Method)
  at java.net.Socket.getOutputStream(Socket.java:951)
  at redis.clients.jedis.Connection.connect(Connection.java:200)
  ... 7 more
```

- 原因分析

对源码分析后，类结构图如下：

![image-20210607223205707](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210607223205.png)

Jedis 继承了 BinaryJedis，BinaryJedis 中保存了单个 Client 的实例，Client 最终继承了 Connection，Connection 中保存了单个 Socket 的实例，和 Socket 对应的两个读写流。

- 解决方案

```java
private static JedisPool jedisPool = new JedisPool("127.0.0.1", 6379);

@GetMapping("/right")
public void right() throws InterruptedException {

    new Thread(() -> {
        try (Jedis jedis = jedisPool.getResource()) {
            for (int i = 0; i < 1000; i++) {
                String result = jedis.get("a");
                if (!"1".equals(result)) {
                    log.warn("Expect a to be 1 but found {}", result);
                    return;
                }
            }
        }
    }).start();
    new Thread(() -> {
        try (Jedis jedis = jedisPool.getResource()) {
            for (int i = 0; i < 1000; i++) {
                String result = jedis.get("b");
                if (!"2".equals(result)) {
                    log.warn("Expect b to be 2 but found {}", result);
                    return;
                }
            }
        }
    }).start();
    TimeUnit.SECONDS.sleep(5);

}
```

**踩坑11：使用连接池务必确保复用**

- 案例场景

```java
@GetMapping("wrong1")
public String wrong1() {
    CloseableHttpClient client = HttpClients.custom()
            .setConnectionManager(new PoolingHttpClientConnectionManager())
            // 空闲时间
            .evictIdleConnections(60, TimeUnit.SECONDS).build();
    try (CloseableHttpResponse response = client.execute(new HttpGet("http://127.0.0.1:45678/httpclientnotreuse/test"))) {
        return EntityUtils.toString(response.getEntity());
    } catch (Exception ex) {
        ex.printStackTrace();
    }
    return null;
}
```

访问这个接口几次后查看应用线程情况，可以看到有大量叫作 Connection evictor 的线程，且这些线程不会销毁：

![image-20210608223510845](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210608223510.png)

- 原因分析

对这个接口进行几秒的压测（压测使用 wrk，1 个并发 1 个连接），可以看到，已经建立了三千多个 TCP 连接到 45678 端口（其中有 1 个是压测客户端到 Tomcat 的连接，大部分都是 HttpClient 到 Tomcat 的连接）：

```shell
~ lsof -nP -i4TCP:45678 | wc -l
3686
```

60 秒之后连接处于 CLOSE_WAIT 状态，最终彻底关闭。

![image-20210608224132693](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210608224132.png)

这 2 点证明，CloseableHttpClient 属于第二种模式，即内部带有连接池的 API，其背后是 连接池，最佳实践一定是复用。

- 解决方案

```java
private static CloseableHttpClient httpClient;

static {
    httpClient = HttpClients.custom().setMaxConnPerRoute(1).setMaxConnTotal(1).evictIdleConnections(60, TimeUnit.SECONDS).build();

    Runtime.getRuntime().addShutdownHook(new Thread(() -> {
        try {
            httpClient.close();
        } catch (IOException ignored) {
        }
    }));
}

@GetMapping("right")
public String right() {
    try (CloseableHttpResponse response = httpClient.execute(new HttpGet("http://127.0.0.1:45678/httpclientnotreuse/test"))) {
        return EntityUtils.toString(response.getEntity());
    } catch (Exception ex) {
        ex.printStackTrace();
    }
    return null;
}
```

**踩坑12：Hikari 连接池配置的调优过程**

连接池提供了许多参数，包括最小（闲置）连接、最大连接、闲置连接生存时间、连接生存时间等。

其中，最重要的参数是最大连接数。但如果最大连接数太大，客户端需要耗费过多的资源维护连接。且每个客户端都保持大量的连接，会给服务端带来更大的压力。

如果最大连接数太小，很可能会因为获取连接的等待时间太长，导致吞吐量低下，甚至超时无法获取连接。

- 案例场景

我们模拟下压力增大导致数据库连接池打满的情况，来实践下如何确认连接池的使用情况，以及有针对性地进行参数优化。

首先，定义一个用户注册方法，通过 @Transactional 注解为方法开启事务。其中包含了 500 毫秒的休眠，一个数据库事务对应一个 TCP 连接，所以 500 多毫秒的时间都会占用数据库连接：

```java
@Transactional
public User register() {
    User user = new User();
    user.setName("new-user-" + System.currentTimeMillis());
    userRepository.save(user);
    try {
        TimeUnit.MILLISECONDS.sleep(500);
    } catch (InterruptedException e) {
        e.printStackTrace();
    }
    return user;
}
```

随后，修改配置文件启用 register-mbeans，使 Hikari 连接池能通过 JMX MBean 注册连 接池相关统计信息，方便观察连接池：

```properties
spring.datasource.hikari.register-mbeans=true
```

- 原因分析

启动程序并通过 JConsole 连接进程后，可以看到默认情况下最大连接数为 10：

![image-20210608225553808](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210608225553.png)

使用 wrk 对应用进行压测，可以看到连接数一下子从 0 到了 10，有 20 个线程在等待获取连接:

![image-20210608225629304](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210608225629.png)

不久就出现了无法获取数据库连接的异常，如下所示：

```java
[15:37:56.156] [http-nio-45678-exec-15] [ERROR] [.a.c.c.C.[.[.[/].[dispatcherServlet]:175 ] - Servlet.service() for servlet [dispatcherServlet] in context with path [] threw exception [Request processing failed; nested exception is org.springframework.dao.DataAccessResourceFailureException: unable to obtain isolated JDBC connection; nested exception is org.hibernate.exception.JDBCConnectionException: unable to obtain isolated JDBC connection] with root cause java.sql.SQLTransientConnectionException: HikariPool-1 - Connection is not  available, request timed out after 30000ms.
```

- 解决方案

修改一下配置文件，调整数据库连接池最大连接参数到 50 即可。

```properties
spring.datasource.hikari.maximum-pool-size=50
```

然后，再观察一下这个参数是否适合当前压力，满足需求的同时也不占用过多资源。从监控来看这个调整是合理的，有一半的富余资源，再也没有线程需要等待连接了：

![image-20210608230846125](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210608230846.png)

> 其实，看到错误日志后再调整已经有点儿晚了。更合适的做法是，对类似数据库连接池的重要资源进行持续检测，并设置一半的使用量作为报警阈值，出现预警后及时扩容。

# 05 | HTTP调用：你考虑到超时、重试、并发了吗?

**连接超时参数**

连接超时参数 ConnectTimeout 是建立连阶的最长等待时间。

- 连接超时配置得很长（60秒）可以吗？

如果几秒连接不上，那么可能永远也连接不上。设置特别长的连接超时意义不大，将其配置得短一些（比如 1~5 秒）即可。在下游服务离线无法连接的时候，可以快速失败。

**读取超时参数**

读取超时参数 ReadTimeout 是用来控制从 Socket 上读取数据的最长等待时间。也就是向 Socket 写入数据后，我们等到 Socket 返回数据的超时时间，其中绝大部分的时间是服务端处理业务逻辑的时间。

- 客户端读取超时，服务端的执行会中断吗？

类似 Tomcat 的 Web 服务器都是把服务端请求提交到线程池处理的，只要服务端收到了请求，网络层面的超时和断开便不会影响服务端的执行。

- 读取超时配置得越长成功率越高吗？

进行 HTTP 请求一般是需要获得结果的，属于同步调用。如果超时时间很长，在等待服务端返回数据的同时，客户端线程也在等待，当下游服务出现大量超时的时候，程序可能也会受到拖累创建大量线程，最终崩溃。

**Feign 和 Ribbon 如何配置超时？**

坑点一：默认情况下 Feign 的读取超时是 1 秒。

RibbonClientConfiguration 类如下：

```java
/**
 * Ribbon client default connect timeout.
 */
public static final int DEFAULT_CONNECT_TIMEOUT = 1000;

/**
 * Ribbon client default read timeout.
 */
public static final int DEFAULT_READ_TIMEOUT = 1000;

@Bean
@ConditionalOnMissingBean
public IClientConfig ribbonClientConfig() {
    DefaultClientConfigImpl config = new DefaultClientConfigImpl();
    config.loadProperties(this.name);
    config.set(CommonClientConfigKey.ConnectTimeout, DEFAULT_CONNECT_TIMEOUT);
    config.set(CommonClientConfigKey.ReadTimeout, DEFAULT_READ_TIMEOUT);
    config.set(CommonClientConfigKey.GZipPayload, DEFAULT_GZIP_PAYLOAD);
    return config;
}
```

读取超时太短，可以通过以下配置设置超时时间：

```properties
feign.client.config.default.readTimeout=3000
feign.client.config.default.connectTimeout=3000
```

坑点二：如果要配置 Feign 的读取超时，就必须同时配置连接超时。

打开 FeignClientFactoryBean 可以看到，只有同时设置 ConnectTimeout 和 ReadTimeout，Request.Options 才会被覆盖：

```java
protected void configureUsingProperties(
        FeignClientProperties.FeignClientConfiguration config,
        Feign.Builder builder) {
    // ...
    if (config.getConnectTimeout() != null && config.getReadTimeout() != null) {
        builder.options(new Request.Options(config.getConnectTimeout(),
                config.getReadTimeout()));
    }
    // ...
}
```

坑点三：如果同时配置了 Feign 和 Ribbon 参数，最终生效的是 Feign 的超时。

配置 Ribbon 时，两个超时参数首字母要大写。

```properties
ribbon.ReadTimeout=400
ribbon.ConnectTimeout=400
```

在 LoadBalancerFeignClient 源码中可以看到，如果 Request.Options 不是默认值，就会创建一个 FeignOptionsClientConfig 代替原来 Ribbon 的 DefaultClientConfigImpl，导致 Ribbon 的配置被 Feign 覆盖：

```java
IClientConfig getClientConfig(Request.Options options, String clientName) {
    IClientConfig requestConfig;
    if (options == DEFAULT_OPTIONS) {
        requestConfig = this.clientFactory.getClientConfig(clientName);
    }
    else {
        requestConfig = new FeignOptionsClientConfig(options);
    }
    return requestConfig;
}
```

**Ribbon 的重试请求**

HTTP 协议认为 Get 请求是数据查询操作，是无状态的，又考虑到网络出现丢包是比较常见的事情，有些 HTTP 客户端或代理服务器会自动重试 Get/Head 请求。

源码如下：

```java
// DefaultClientConfigImpl
public static final int DEFAULT_MAX_AUTO_RETRIES_NEXT_SERVER = 1;
public static final int DEFAULT_MAX_AUTO_RETRIES = 0;

// RibbonLoadBalancedRetryPolicy
public boolean canRetry(LoadBalancedRetryContext context) {
    HttpMethod method = context.getRequest().getMethod();
    return HttpMethod.GET == method || lbContext.isOkToRetryOnAllOperations();
}

@Override
public boolean canRetrySameServer(LoadBalancedRetryContext context) {
    return sameServerCount < lbContext.getRetryHandler().getMaxRetriesOnSameServer()
            && canRetry(context);
}

@Override
public boolean canRetryNextServer(LoadBalancedRetryContext context) {
    // this will be called after a failure occurs and we increment the counter
    // so we check that the count is less than or equals to too make sure
    // we try the next server the right number of times
    return nextServerCount <= lbContext.getRetryHandler().getMaxRetriesOnNextServer()
            && canRetry(context);
}
```

如果想关闭自动重试，可将 Get 改为 Post，也可将 MaxAutoRetriesNextServer 参数配置为 0：

```properties
ribbon.MaxAutoRetriesNextServer=0
```

**踩坑13：并发数限制了程序的处理能力**

- 案例场景

我之前遇到过一个爬虫项目，整体爬取数据的效率很低，增加线程池数量也无济于事，只能堆更多的机器做分布式的爬虫。现在，我们就来模拟下这个场景，看看问题出在了哪里。

模拟代码如下：

```java
static CloseableHttpClient httpClient1;

static {
    httpClient1 = HttpClients.custom().setConnectionManager(new PoolingHttpClientConnectionManager()).build();
}

@GetMapping("wrong")
public int wrong(@RequestParam(value = "count", defaultValue = "10") int count) throws InterruptedException {
    return sendRequest(count, () -> httpClient1);
}

private int sendRequest(int count, Supplier<CloseableHttpClient> client) throws InterruptedException {
    AtomicInteger atomicInteger = new AtomicInteger();
    ExecutorService threadPool = Executors.newCachedThreadPool();
    long begin = System.currentTimeMillis();
    IntStream.rangeClosed(1, count).forEach(i -> {
        threadPool.execute(() -> {
            try (CloseableHttpResponse response = client.get().execute(
                    new HttpGet("http://127.0.0.1:45678/routelimit/server"))
            ) {
                atomicInteger.addAndGet(Integer.parseInt(EntityUtils.toString(response.getEntity())));
            } catch (Exception ex) {
                ex.printStackTrace();
            }
        });
    });
    threadPool.shutdown();
    threadPool.awaitTermination(1, TimeUnit.HOURS);
    log.info("发送 {} 次请求，耗时 {} ms", atomicInteger.get(), System.currentTimeMillis() - begin);
    return atomicInteger.get();
}

@GetMapping("server")
public int server() throws InterruptedException {
    TimeUnit.SECONDS.sleep(1);
    return 1;
}
```

按道理说，10 个请求并发处理的时间基本相当于 1 个请求的处理时间，也就是 1 秒，但日志中显示实际耗时 5 秒。

- 原因分析

查看 PoolingHttpClientConnectionManager 源码：

```java
// PoolingHttpClientConnectionManager
public PoolingHttpClientConnectionManager(
    final HttpClientConnectionOperator httpClientConnectionOperator,
    final HttpConnectionFactory<HttpRoute, ManagedHttpClientConnection> connFactory,
    final long timeToLive, final TimeUnit timeUnit) {
    // ...
    this.pool = new CPool(new InternalConnectionFactory(
            this.configData, connFactory), 2, 20, timeToLive, timeUnit);
   // ...
}

// CPool
public CPool(
        final ConnFactory<HttpRoute, ManagedHttpClientConnection> connFactory,
        final int defaultMaxPerRoute, final int maxTotal,
        final long timeToLive, final TimeUnit timeUnit) {
    // ...
}
```

可以注意到有两个重要参数：

defaultMaxPerRoute=2，也就是同一个主机 / 域名的最大并发请求数为 2。我们的爬虫需要 10 个并发，显然是默认值太小限制了爬虫的效率。

maxTotal=20，也就是所有主机整体最大并发为 20，这也是 HttpClient 整体的并发度。目前，我们请求数是 10，最大并发是 10，20 不会成为瓶颈。

限制同一个域名两个并发请求其实是 HTTP 1.1 协议要求的。

- 解决方案

声明一个新的 HttpClient：

```java
httpClient2 = HttpClients.custom().setMaxConnPerRoute(10).setMaxConnTotal(20).build();
```

结果 10 次请求在 1 秒左右执行完成。

# 06 | 20%的业务代码的Spring声明式事务，可能都没处理正确

**踩坑14：因为配置不正确，导致方法上的事务没生效**

- 案例场景

Controller 实现如下：

```java
@Autowired
private UserService userService;

@GetMapping("wrong1")
public int wrong1(@RequestParam("name") String name) {
    userService.createUserWrong1(name);
    return userService.getUserCount(name);
}
```

UserService 实现如下：

```java
@Autowired
private UserRepository userRepository;

public int createUserWrong1(String name) {
    try {
        this.createUserPrivate(new UserEntity(name));
    } catch (Exception ex) {
        log.error("create user failed because {}", ex.getMessage());
    }
    return userRepository.findByName(name).size();
}

@Transactional
private void createUserPrivate(UserEntity entity) {
    userRepository.save(entity);
    if (entity.getName().contains("test")) {
        throw new RuntimeException("invalid username!");
    }
}

public int getUserCount(String name) {
    return userRepository.findByName(name).size();
}
```

调用接口后发现，即便用户名不合法，用户也能创建成功。

- 原因分析

@Transactional 生效原则 1，除非特殊配置（比如使用 AspectJ 静态织入实现 AOP），否则只有定义在 public 方法上的 @Transactional 才能生效。原因是 Spring 默认通过动态代理的方式实现 AOP，对目标方法进行增强，private 方法无法代理到， Spring 自然也无法动态增强事务处理逻辑。

然而改为 createUserPublic 后：

```java
@Transactional
public void createUserPublic(UserEntity entity) {
    userRepository.save(entity);
    if (entity.getName().contains("test"))
}
```

这是因为 @Transactional 生效的原则 2，必须通过代理过的类从外部调用目标方法才能生效。

- 解决方案

将 UserService 修改一下：

```java
@Autowired
private UserService self;

public int createUserWrong1(String name) {
    try {
        self.createUserPrivate(new UserEntity(name));
    } catch (Exception ex) {
        log.error("create user failed because {}", ex.getMessage());
    }
    return userRepository.findByName(name).size();
}
```

把 this 改为 self 后测试发现，在 Controller 中调用可以验证事务是生效的。

我们务必确认调用 @Transactional 注解标记的方法是 public 的，并且是通过 Spring 注入的 Bean 进行调用的。

**踩坑15：因为异常处理不正确，导致事务虽然生效但出现异常时没回滚**

- 案例场景

事务不生效的 UserService 实现如下：

```java
@Autowired
private UserRepository userRepository;

// 异常无法传播出方法，导致事务无法回滚 @Transactional
public void createUserWrong1(String name) {
    try {
        userRepository.save(new UserEntity(name));
        throw new RuntimeException("error");
    } catch (Exception ex) {
        log.error("create user failed", ex);
    }
}
```

或者下面的实现：

```java
// 即使出了受检异常也无法让事务回滚
@Transactional
public void createUserWrong2(String name) throws IOException {
    userRepository.save(new UserEntity(name));
    otherTask();
}

// 因为文件不存在，一定会抛出一个IOException
private void otherTask() throws IOException {
    Files.readAllLines(Paths.get("file-that-not-exist"));
}
```

这 2 种方法的实现和调用，因为异常处理不当，导致程序没有如我们期望的文件操作出现异常时回滚事务。

- 原因分析

第一，只有异常传播出了标记了 @Transactional 注解的方法，事务才能回滚。

第二，默认情况下，出现 RuntimeException 或 Error 的时候，Spring 才会回滚事务。

- 解决方案

第一，手动设置让当前事务处于回滚状态：

```java
@Transactional
public void createUserWrong1(String name) {
    try {
        userRepository.save(new UserEntity(name));
        throw new RuntimeException("error");
    } catch (Exception ex) {
        log.error("create user failed", ex);
        TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();
    }
}
```

第二，在注解中声明，期望遇到所有的 Exception 都回滚事务：

```java
@Transactional(rollbackFor = Exception.class)
public void createUserRight2(String name) throws IOException {
    userRepository.save(new UserEntity(name));
    otherTask();
}
```

**踩坑16：事务传播配置不当导致事务回滚**

- 案例场景

一个用户注册的操作，会插入一个主用户到用户表，还会注册一个关联的子用户。我们希望将子用户注册的数据库操作作为一个独立事务来处理，即使失败也不会影响主流程，即不影响主用户的注册。

Controller 的实现如下：

```java
@GetMappin("wrong")
public int wrong(@RequestParam("name") String name) {
    try {
        userService.createUserWrong(new UserEntity(name));
    } catch (Exception e) {
        log.error("createUserWrong failed, reason:{}", e.getMessage());
    }
}
```

UserService 的实现如下：

```java
@Autowired
private UserRepository userRepository;
@Autowired
private SubUserService subUserService;

@Transactional
public void createUserWrong(UserEntity entity) {
    createMainUser(entity);
    try {
        subUserService.createSubUserWithExceptionWrong(entity);
    } catch (Exception e) {
        log.error("create sub user error:{}", ex.getMessage());
    }
}

private void createMainUser(UserEntity entity) {
    userRepository.save(entity);
    log.info("createMainUser finish");
}
```

SubUserService 的实现如下：

```java
@Transactional
public void createSubUserWithExceptionWrong(UserEntity entity) {
    log.info("createSubUserWithExceptionWrong start");
    userRepository.save(entity);
    throw new RuntimeException("invalid status");
}
```

结果 Controller 里出现了一个 UnexpectedRollbackException，异常描述提示最终这个事务回滚了，而且是静默回滚的。之所以说是静默，是因为 createUserWrong 方法本身并没有出异常，只不过提交后发现子方法已经把当前事务设置为了回滚，无法完成提交。

- 原因分析

虽然捕获了异常，但是因为没有开启新事务，而当前事务因为异常已经被标记为 rollback 了。

- 解决方案

想办法让子逻辑在独立事务中运行，也就是执行到这个方法时需要开启新的事务，并挂起当前事务：

```java
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void createSubUserWithExceptionRight(UserEntity entity) {
    log.info("createSubUserWithExceptionRight start");
    userRepository.save(entity);
    throw new RuntimeException("invalid status");
}
```

# 07 | 数据库索引：索引并不是万能药

> 名词汇总：数据页、页目录、槽、回表、索引覆盖

日常工作中，有些同学一遇到查询性能问题，就盲目要求 DBA 给表字段创建索引。显然，这种想法是错误的。今天，我们就以 MySQL 为例来深入理解下索引的原理，以及相关误区。

**InnoDB 是如何存储数据的?**

MySQL 支持多种存储引擎，最常使用的是 InnoDB，因为它支持事务。

虽然数据保存在磁盘中，但其处理是在内存中进行的。为了减少磁盘随机读取次数， InnoDB 采用页而不是行的粒度来保存数据，即数据被分成若干页，以页为单位保存在磁盘中。InnoDB 的页大小，一般是 16KB。

各个数据页组成一个双向链表，每个数据页中的记录按照主键顺序组成单向链表；每一个数据页中有一个页目录，方便按照主键查询记录。数据页的结构如下：

![image-20210618221306629](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210618221306.png)

> 这里最大记录上面一条记录应该是”记录22 PK=22“

页目录通过槽把记录分成不同的小组，每个小组有若干条记录。如图所示，记录中最前面的小方块中的数字，代表的是当前分组的记录条数，最小和最大的槽指向 2 个特殊的伪记录。有了槽之后，我们按照主键搜索页中记录时，就可以采用二分法快速搜索，无需从最小记录开始遍历整个页中的记录链表。

举一个例子，如果要搜索主键(PK)=15 的记录：

```
1. 先二分得出槽中间位是 (0+6)/2=3，看到其指向的记录是 12<15，所以需要从 #3 槽后继续搜索记录;
2. 再使用二分搜索出 #3 槽和 #6 槽的中间位是 (3+6)/2=4.5 取整 4，#4 槽对应的记录是 16>15，所以记录一定在 #4 槽中;
3. 再从 #3 槽指向的 12 号记录开始向下搜索 3 次，定位到 15 号记录。

总结：先找到数据在哪个槽，再在槽中逐个向下搜索。
```

MySQL InnoDB 引擎就是这么存储数据的。

**聚簇索引和二级索引**

说到索引，页目录就是最简单的索引。但当数据页有无数个时，就需要考虑建立索引，才能定位到记录所在的页。

为了解决这个问题，InnoDB 引入了 B+ 树。

![image-20210618221415794](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210618221415.png)

上图叶子节点下面方块中的省略号是实际数据，这样的 B+ 树就是聚簇索引。由于数据在物理上只会保存一份，所以聚簇索引只能有一个。

InnoDB 会自动使用主键作为聚簇索引的索引键，如果没有主键，就选择第一个不包含 NULL 值的唯一列。

> 如果所有列都含有 NULL 值呢？

为了实现非主键字段的快速搜索，就引出了二级索引，如下图所示：

![image-20210618230129544](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210618230129.png)

这次二级索引的叶子节点中保存的不是实际数据，而是主键，获得主键值后去聚簇索引中获得数据行。这个过程就叫作回表。

**额外创建二级索引的维护代价**

创建二级索引的代价，主要表现在维护代价、空间代价和回表代价三个方面。

创建 N 个二级索引，就需要再创建 N 棵 B+ 树，新增数据时不仅要修改聚簇索引，还需要修改这 N 个二级索引。

我们通过实验测试一下创建索引的代价。

```sql
create TABLE `person` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `score` int(11) NOT NULL,
  `create_time` timestamp NOT NULL,
  PRIMARY KEY (`id`),
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

通过下面的存储过程循环创建 10 万条测试数据：

```sql
create DEFINER=`root`@`%` PROCEDURE `insert_person`()
begin
    declare c_id integer default 1;
    while c_id<=100000 do
    insert into person values(c_id, concat('name',c_id), c_id+100, date_sub(NOW(), interval c_id second));
    -- 需要注意，因为使用的是now()，所以对于后续的例子，使用文中的SQL你需要自己调整条件，否则可能看不到文中的效果
    set c_id=c_id+1;
    end while;
end
```

我的机器的耗时是 140 秒(本文的例子 均在 MySQL 5.7.26 中执行)。

如果再创建两个索引：

```sql
KEY `name_score` (`name`,`score`) USING BTREE,
KEY `create_time` (`create_time`) USING BTREE
```

那么创建 10 万条记录的耗时提高到 154 秒。

> 这里还有一个代价。页中的记录都是按照索引值从小到大的顺序存放的，新增记录就需 要往页中插入数据，现有的页满了就需要新创建一个页，把现有页的部分数据移过去，这就是页分裂；
>
> 如果删除了许多数据使得页比较空闲，还需要进行页合并。页分裂和合并，都会 有 IO 代价，并且可能在操作过程中产生死锁。

**额外创建二级索引的空间代价**

虽然二级索引不保存原始数据，但要保存索引列的数据，所以会占用更多的空间。比如，person 表创建了两个索引后，使用下面的 SQL 查看数据和索引占用的磁盘：

```sql
select DATA_LENGTH, INDEX_LENGTH from information_schema.TABLES where TABLE_NAME='person';
```

结果显示，数据本身只占用了 4.7M，而索引占用了 8.4M。

**额外创建二级索引的回表代价**

使用 SELECT * 按照 name 字段查询用户，使用 EXPLAIN 查看执行计划：

```sql
explain select * from person where NAME='name1';
```

![image-20210618233223988](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210618233224.png)

可以发现，key 字段代表实际走的是哪个索引，其值是 name_score，说明走的是 name_score 这个索引。

type 字段代表了访问表的方式，其值 ref 说明是二级索引等值匹配，符合我们的查询。

把 SQL 中的 * 修改为 NAME 和 SCORE，也就是 SELECT name_score 联合索引包含的两列，查看执行计划：

```sql
explain select NAME,SCORE from person where NAME='name1';
```

![image-20210618233518044](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210618233518.png)

可以看到，Extra 列多了一行 Using index 的提示，证明这次查询直接查的是二级索引，免去了回表。

> 如果我们需要查询的是索引列索引或联合索引能覆盖的数据，则不再需要回表查询。这种情况叫作**索引覆盖**。

**索引开销的最佳实践**

第一，无需一开始就建立索引。

可以等到业务场景明确后，或者是数据量超过 1 万、查询变慢后，再针对需要查询、排序或分组的字段创建索引。创建索引后可以使用 EXPLAIN 命 令，确认查询是否可以使用索引。

第二，尽量索引轻量级的字段。

比如能索引 int 字段就不要索引 varchar 字段。索引字段也可以是部分前缀，在创建的时候指定字段索引长度。针对长文本的搜索，可以考虑使用 Elasticsearch 等专门用于文本搜索的索引数据库。

第三，尽量不要在 SQL 语句中 SELECT *。

应该 SELECT 必要的字段，甚至可以考虑使用联合索引来包含我们要搜索的字段（即索引覆盖），既能实现索引加速，又可以避免回表的开销。

**索引失效的情况**

第一，后模糊查询索引会失效。

比如下面的 LIKE 语句：

```sql
EXPLAIN SELECT * FROM person WHERE NAME LIKE '%name123' LIMIT 100
```

![image-20210619215651693](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210619215651.png)

type=ALL 代表了全表扫描。

把百分号放到后面：

```sql
EXPLAIN SELECT * FROM person WHERE NAME LIKE 'name123%' LIMIT 100
```

![image-20210619215815097](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210619215815.png)

type=range 表示走索引扫描，key=name_score 看到实际走了 name_score 索引。

第二，条件涉及函数操作无法走索引。

比如搜索条件用到了 LENGTH 函数：

```sql
EXPLAIN SELECT * FROM person WHERE LENGTH(NAME)=7
```

![image-20210619220237343](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210619220237.png)

索引保存的是索引列的原始值，而不是经过函数计算后的值。如果需要针对函数调用走数据库索引的话，只能保存一份函数变换后的值，然后重新针对这个计算列做索引。

第三，索引中断不走索引。

如果对 name 和 score 建了联合索引，但是仅按照 score 列搜索无法走索引：

```sql
EXPLAIN SELECT * FROM person WHERE SCORE>45678
```

![image-20210619220555444](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210619220555.png)

在联合索引的情况下，数据是按照索引第一列排序，第一列数据相同时才会按照第二列排序。尝试把搜索条件加入 name 列：

```sql
EXPLAIN SELECT * FROM person WHERE SCORE>45678 AND NAME LIKE 'NAME45%'
```

![image-20210619220819281](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210619220819.png)

可以看到走了 name_score 索引。

> 因为有查询优化器，所以 name 作为 WHERE 子句的第几个条件并不是很 重要。

> 建联合索引还是多个独立索引?
>
> 如果你的搜索条件经常会使用多个字段进行搜索，那么可以考虑针对这几个字段建联合索引。同时，针对多字段建立联合索引，使用索引覆盖的可能更大。
>
> 如果只会查询单个字段，可以考虑建单独的索引，毕竟联合索引保存了不必要字段也有成本。

**数据库如何基于成本决定是否走索引？**

- 案例场景

我们用下面的 SQL 查询 name>‘name84059’ AND create_time>‘2020- 01-24 05:00:00’

```sql
explain select * from person where NAME>'name84059' and create_time>'2020-01-24 05:00:00'
```

![image-20210619223039194](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210619223039.png)

type=All，其执行计划是全表扫描。

把 create_time 条件中的 5 点改为 6 点：

```sql
explain select * from person where NAME>'name84059' and create_time>'2020-01-24 06:00:00'
```

![image-20210619223258891](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210619223259.png)

type=range，key=create_time，走了 create_time 索引，而不是 name_score 联合索引。

- 原因分析

MySQL 在查询数据之前，会先对可能的方案做执行计划，然后依据成本决定走哪个执行计划。这里的成本，包括 IO 成本和 CPU 成本：

IO 成本，是从磁盘把数据加载到内存的成本。默认情况下，读取数据页的 IO 成本常数是 1（也就是读取 1 个页成本是 1）。

CPU 成本，是检测数据是否满足条件和排序等 CPU 操作的成本。默认情况下，检测记录的成本是 0.2。

MySQL 维护了表的统计信息，可以使用下面的命令查看：

```sql
SHOW TABLE STATUS LIKE 'person'
```

![image-20210619223540752](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210619223540.png)

总行数是 100086 行，CPU 成本是 100086*0.2=20017 左右。

> 为什么这里多了 86 行？MySQL 的统计信息是一个估算。

数据长度是 4734976 字节。InnoDB 每个页面的大小是 16KB，大概计算出页的数量是 289，因此 IO 成本是 289 左右。

> 对于 InnoDB 来说，4734976 就是聚簇索引占用的空间，等于聚簇索引的页数量 * 每个页面的大小。

所以，全表扫描的总成本是 20306 左右。

在 MySQL 5.6 及之后的版本中，我们可以使用 optimizer trace 功能查看优化器生成执行计划的整个过程。

```sql
SET optimizer_trace="enabled=on";
explain select * from person where NAME >'name84059' and create_time>'2020-01-24 05:00:00';
select * from information_schema.OPTIMIZER_TRACE;
SET optimizer_trace="enabled=off";
```

对于按照 create_time>'2020-01-24 05:00:00’ 条件走全表扫描的 SQL，我从 OPTIMIZER_TRACE 的执行结果中，摘出了几个重要片段来重点分析：

1. 使用 name_score 对 name84059<name 条件进行索引扫描需要扫描 25362 行，成本是 30435。

   ```json
   {
     "index": "name_score",
     "ranges": [
       "name84059 < name"
     ],
     "rows": 25362,
     "cost": 30435,
     "chosen": false,
     "cause": "cost"
   }
   ```

   > 30435 是查询二级索引的 IO 成本和 CPU 成本之和，再加上回表查询聚簇索引的 IO 成本和 CPU 成本之和。

2. 使用 create_time 进行索引扫描需要扫描 23758 行，成本是 28511。

   ```json
   {
     "index": "create_time",
     "ranges": [
       "0x5e2a79d0 < create_time"
     ],
     "rows": 23758,
     "cost": 28511,
     "chosen": false,
     "cause": "cost"
   }
   ```

3. 全表扫描 100086 条记录的成本是 20306。（和上面计算的一致）

   ```json
   {
     "considered_execution_plans": [{
       "table": "`person`",
       "best_access_path": {
         "considered_access_paths": [{
           "rows_to_scan": 100086,
           "access_type": "scan",
           "resulting_rows": 100086,
           "cost": 20306,
           "chosen": true
         }]
       },
       "rows_for_plan": 100086,
       "cost_for_plan": 20306,
       "chosen": true
     }]
   }
   ```

所以 MySQL 最终选择了全表扫描方式作为执行计划。

把 SQL 中的 create_time 条件从 05:00 改为 06:00，再次分析 OPTIMIZER_TRACE 可以看到：

```json
{
  "index": "create_time",
  "ranges": [
    "0x5e2a87e0 < create_time"
  ],
  "rows": 16588,
  "cost": 19907,
  "chosen": true
}
```

因为是查询更晚时间的数据，走 create_time 索引需要扫描的行数从 23758 减少到了 16588。这次走这个索引的成本 19907 小于全表扫描的 20306，更小于走 name_score 索引的 30435。

所以这次执行计划选择的是走 create_time 索引。

- 解决方案

有时会因为统计信息的不准确或成本估算的问题，实际开销会和 MySQL 统计出来的差距较大，导致 MySQL 选择错误的索引或是直接选择走全表扫描，这个时候就需要人工干预，使用强制索引了。

比如，像这样强制走 name_score 索引：

```sql
explain select * from person FORCE INDEX(name_score) where NAME >'name84059' and create_time>'2020-01-24 00:00:00'
```

**总结**

1、type 取值有：ref、all、range。

# 08 | 判等问题：程序里如何确定你就是你？

**踩坑17：滥用 String 的 intern 方法导致性能问题**

- 案例场景

虽然使用 new 声明的字符串调用 intern 方法，也可以让字符串进行驻留，但在业务代码中滥用 intern，可能会产生性能问题。

```java
List<String> list = new ArrayList<>();

@GetMapping("internperformance")
public int internperformance(@RequestParam(value = "size", defaultValue = "10000000") int size) {
    //-XX:+PrintStringTableStatistics
    //-XX:StringTableSize=10000000
    long begin = System.currentTimeMillis();
    list = IntStream.rangeClosed(1, size)
            .mapToObj(i -> String.valueOf(i).intern())
            .collect(Collectors.toList());
    log.info("size:{} took:{}", size, System.currentTimeMillis() - begin);
    return list.size();
}
```

在启动程序时设置 JVM 参数 -XX:+PrintStringTableStatistic，程序退出时可以打印出字符串常量表的统计信息。调用接口后关闭程序，输出如下：

```tex
StringTable statistics:
Number of buckets       :    60013 =    480104 bytes, avg   8.000
Number of entries       : 10030230 = 240725520 bytes, avg  24.000
Number of literals      : 10030230 = 563005568 bytes, avg  56.131
Total footprint         :          = 804211192 bytes
Average bucket size     : 167.134
Variance of bucket size :  55.808
Std. dev. of bucket size:   7.471
Maximum bucket size     :     198
```

1000 万次 intern 操作耗时居然超过了 44 秒。

- 原因分析

原因在于字符串常量池是一个固定容量的 Map。如果容量太小（Number of buckets=60013）、字符串太多（1000 万个字符串），那么每一个桶中的字符串数量会非常多，所以搜索起来就很慢。输出结果中的 Average bucket size=167，代表了 Map 中桶的平均长度是 167。

- 解决方案

解决方式是，设置 JVM 参数 -XX:StringTableSize，指定更多的桶。设置 -XX:StringTableSize=10000000 后，重启应用：

```tex
StringTable statistics:
Number of buckets       : 10000000 =  80000000 bytes, avg   8.000
Number of entries       : 10030156 = 240723744 bytes, avg  24.000
Number of literals      : 10030156 = 562999472 bytes, avg  56.131
Total footprint         :          = 883723216 bytes
Average bucket size     :    1.003
Variance of bucket size :    1.587
Std. dev. of bucket size:    1.260
Maximum bucket size     :       10
```

可以看到，1000 万次调用耗时只有 5.5 秒，Average bucket size 降到了 1，效果明显。

> 没事别轻易用 intern，如果要用一定要注意控制驻留的字符串的数量，并留意常量表的各项指标。

**实现一个 equals 没有这么简单**

假设有这样一个描述点的类 Point，有 x、y 和描述三个属性：

```java
class Point {
    private final String desc;
    private int x;
    private int y;

    public Point(int x, int y, String desc) {
        this.x = x;
        this.y = y;
        this.desc = desc;
    }
}
```

我们期望的逻辑是，只要 x 和 y 这 2 个属性一致就代表是同一个点，所以重写了 equals 方法：

```java
@Override
public boolean equals(Object o) {
    PointWrong that = (PointWrong) o;
    return x == that.x && y == that.y;
}
```

为测试改进后的 Point 是否可以满足需求，我们定义了三个用例：

```java
// 用例1：比较一个 Point 对象和 null
// 结果：空指针
PointRight p1 = new PointRight(1, 2, "a");
try {
    log.info("p1.equals(null) ? {}", p1.equals(null));
} catch (Exception ex) {
    log.error(ex.toString());
}

// 用例2：比较一个 Object 对象和一个 Point 对象
// 结果：类型转换异常
Object o = new Object();
try {
    log.info("p1.equals(expression) ? {}", p1.equals(o));
} catch (Exception ex) {
    log.error(ex.toString());
}

// 用例3：比较两个 x 和 y 属性值相同的 Point 对象
// 输出 true
PointRight p2 = new PointRight(1, 2, "b");
log.info("p1.equals(p2) ? {}", p1.equals(p2));

HashSet<PointRight> points = new HashSet<>();
points.add(p1);
log.info("points.contains(p2) ? {}", points.contains(p2));
```

通过日志中的结果可以看到，第一次比较出现了空指针异常,第二次比较出现了类型转换异常，第三次比较符合预期输出了 true。

通过这些失效的用例，我们大概可以总结出实现一个更好的 equals 应该注意的点：

1. 考虑到性能，可以先进行指针判等，如果对象是同一个那么直接返回 true；
2. 需要对另一方进行判空，空对象和自身进行比较，结果一定是 fasle；
3. 需要判断两个对象的类型，如果类型都不同，那么直接返回 false；

确保类型相同的情况下再进行类型强制转换，然后逐一判断所有字段。 修复和改进后的 equals 方法如下：

```java
@Override
public boolean equals(Object o) {
    if (this == o) {
        return true;
    }
    if (o == null || getClass() != o.getClass()) {
        return false;
    }
    PointRight that = (PointRight) o;
    return x == that.x && y == that.y;
}
```

**踩坑18：重写了 equals 但未重写 hashCode**

- 案例场景

```java
PointWrong p1 = new PointWrong(1, 2, "a");
PointWrong p2 = new PointWrong(1, 2, "b");

HashSet<PointWrong> points = new HashSet<>();
points.add(p1);
log.info("points.contains(p2) ? {}", points.contains(p2));
```

重写了 equals 方法后，这 2 个对象可以认为是同一个，Set 中已经存在了 p1，那就应该包含 p2，但结果却是 false。

- 原因分析

出现这个 Bug 的原因是，散列表需要使用 hashCode 来定位元素放到哪个桶。如果自定义对象没有实现自定义的 hashCode 方法，就会使用 Object 超类的默认实现，得到的两个 hashCode 是不同的，导致无法满足需求。

- 解决方案

直接使用 Objects.hash 方法来重写 hashCode 方法：

```java
@Override
public int hashCode() {
    return Objects.hash(x, y);
}
```

**踩坑19：重写了 equals 但未重写 compareTo**

- 案例场景

我之前遇到过这么一个问题，代码里本来使用了 ArrayList 的 indexOf 方法进行元素搜索，但是一位好心的开发同学觉得逐一比较的时间复杂度是 O(n)，效率太低了，于是改为了排序后通过 Collections.binarySearch 方法进行搜索，实现了 O(log n) 的时间复杂度。 

```java
@Data
@AllArgsConstructor
class Student implements Comparable<Student> {
    private int id;
    private String name;

    @Override
    public int compareTo(Student other) {
        int result = Integer.compare(other.id, id);
        if (result == 0)
            log.info("this {} == other {}", this, other);
        return result;
    }
}
```

```java
@GetMapping("wrong")
public void wrong() {
    List<Student> list = new ArrayList<>();
    list.add(new Student(1, "zhang"));
    list.add(new Student(2, "wang"));
    Student student = new Student(2, "li");

    log.info("ArrayList.indexOf");
    int index1 = list.indexOf(student);
    Collections.sort(list);
    log.info("Collections.binarySearch");
    int index2 = Collections.binarySearch(list, student);

    log.info("index1 = " + index1);// 搜索不到
    log.info("index2 = " + index2);// 1
}
```

没想到，这么一改却出现了 Bug。搜索到的结果是 id 为 2，name 是 wang 的学生。

- 原因分析

binarySearch 方法内部调用了元素的 compareTo 方法进行比较。

- 解决方案

```java
@Override
public int compareTo(StudentRight other) {
    return Comparator.comparing(StudentRight::getName)
            .thenComparingInt(StudentRight::getId)
            .compare(this, other);
}
```

**Lombok @Data 生成代码的坑**

定义一个 Person 类型，包含姓名和身份证两个字段：

```java
@Data
class Person {
    private String name;
    private String identity;

    public Person(String name, String identity) {
        this.name = name;
        this.identity = identity;
    }
}
```

对于身份证相同、姓名不同的两个 Person 对象：

```java
Person person1 = new Person("zhuye", "001");
Person person2 = new Person("Joseph", "001");
log.info("person1.equals(person2) ? {}", person1.equals(person2)); // false
```

判等的结果是 false。如果希望只要身份证一致就认为是同一个人的话，可以使用下面的实现：

```java
@EqualsAndHashCode.Exclude
private String name;
```

如果类型之间有继承：

```java
@Data
class Employee extends Person {
  
    private String company;
    public Employee(String name, String identity, String company) {
        super(name, identity);
        this.company = company;
    }
}
```

```java
Employee employee1 = new Employee("zhuye", "001", "bkjk.com");
Employee employee2 = new Employee("Joseph", "002", "bkjk.com");
log.info("employee1.equals(employee2) ? {}", employee1.equals(employee2)); // true
```

然而结果是 true，显然是没有考虑父类的属性，而认为这两个员工是同一人。原因是 @Data 包含了 @EqualsAndHashCode 注解，而 @EqualsAndHashCode 默认实现没有使用父类属性。修改如下：

```java
@Data
@EqualsAndHashCode(callSuper = true)
class Employee extends Person {
```

# 09 | 数值计算：注意精度、舍入和溢出问题

在人看来，浮点数只是具有小数点的数字，0.1 和 1 都是一样精确的数字。但计算机其实无法精确保存浮点数，因此浮点数的计算结果也不可能精确。

在人看来，一个超大的数字只是位数多一点而已，多写几个 1 并不会让大脑死机。但计算机是把数值保存在了变量中，不同类型的数值变量能保存的数值范围不同，当数值超过类型能表达的数值上限则会发生溢出问题。

接下来，我们就具体看看这些问题吧。

**“危险”的 Double**

对几个简单的浮点数进行加减乘除运算：

```java
// 0.30000000000000004
System.out.println(0.1+0.2);
// 0.19999999999999996
System.out.println(1.0-0.8);
// 401.49999999999994
System.out.println(4.015*100);
// 1.2329999999999999
System.out.println(123.3/100);

double amount1 = 2.15;
double amount2 = 1.10;
// false
System.out.println(amount1 - amount2 == 1.05);
```

出现这种问题的主要原因是，计算机是以二进制存储数值的，浮点数也不例外。比如，0.1 的二进制表示为 0.0 0011 0011 0011... (0011 无限循环)，再转换为十进制就是 0.1000000000000000055511151231257827021181583404541015625。对于计算机而言，0.1 无法精确表达，这是浮点数计算造成精度损失的根源。

浮点数精确表达和运算的场景一定要用 BigDecimal 这个类型。

**踩坑20：使用 BigDecimal 表示和计算浮点数，务必使用字符串的构造方法来初始化 BigDecimal**

- 案例场景

我们用 BigDecimal 把之前的四则运算改 一下：

```java
//0.3000000000000000166533453693773481063544750213623046875
System.out.println(new BigDecimal(0.1).add(new BigDecimal(0.2)));
//0.1999999999999999555910790149937383830547332763671875
System.out.println(new BigDecimal(1.0).subtract(new BigDecimal(0.8)));
//401.49999999999996802557689079549163579940795898437500
System.out.println(new BigDecimal(4.015).multiply(new BigDecimal(100)));
//1.232999999999999971578290569595992565155029296875
System.out.println(new BigDecimal(123.3).divide(new BigDecimal(100)));
```

可以看到，运算结果还是不精确，只不过是精度高了而已。

- 原因分析

使用 BigDecimal 表示和计算浮点数，务必使用字符串的构造方法来初始化 BigDecimal。

- 解决方案

```java
// 0.3
System.out.println(new BigDecimal("0.1").add(new BigDecimal("0.2")));
// 0.2
System.out.println(new BigDecimal("1.0").subtract(new BigDecimal("0.8")));
// 401.500
System.out.println(new BigDecimal("4.015").multiply(new BigDecimal("100")));
// 1.233
System.out.println(new BigDecimal("123.3").divide(new BigDecimal("100")));
```

改进后，就能得到我们想要的输出了。

**BigDecimal 的 scale 和 precision**

不能调用 BigDecimal 传入 Double 的构造方法，但手头只有 一个 Double，如何转换为精确表达的 BigDecimal 呢?

我们试试用 Double.toString 把 double 转换为字符串：

```java
System.out.println(new BigDecimal("4.015").multiply(new BigDecimal(Double.toString(100));
```

输出为 401.5000。

与上面字符串初始化 100 和 4.015 相乘得到的结果 401.500 相比，这里为什么多了一个 0 呢？原因是 BigDecimal 有 scale 和 precision 的概念，scale 表示小数点右边的位数，而 precision 表示精度，也就是有效数字的长度。

调试一下可以发现，`new BigDecimal(Double.toString(100))`得到的 BigDecimal 的 scale=1、precision=4；而 `new BigDecimal(“100”)`得到的 BigDecimal 的 scale=0、 precision=3。对于 BigDecimal 乘法操作，返回值的 scale 是两个数的 scale 相加。

所以，初始化 100 的两种不同方式，导致最后结果的 scale 分别是 4 和 3。

如果一定要用 Double 来初始化 BigDecimal 的话，可以使用 `BigDecimal.valueOf()`方法，以确保其表现和字符串形式的构造方法一致，这也是官方文档更推荐的方式：

```java
System.out.println(new BigDecimal("4.015").multiply(BigDecimal.valueOf(100)));
```

**使用 BigDecimal 来格式化浮点数**

我们看一个例子吧，对于一个浮点数，我们想要保留一位小数。

```java
double num1 = 3.35;
float num2 = 3.35f;
System.out.println(String.format("%.1f", num1));//四舍五入
System.out.println(String.format("%.1f", num2));
```

得到的结果居然是 3.4 和 3.3。

这就是由精度问题和舍入方式共同导致的，double 和 float 的 3.35 其实相当于 3.350xxx 和 3.349xxx:

```tex
3.350000000000000088817841970012523233890533447265625
3.349999904632568359375
```

String.format 采用四舍五入的方式进行舍入，取 1 位小数，double 的 3.350 四舍五入为 3.4，而 float 的 3.349 四舍五入为 3.3。

上面的方式无法精确存储浮点数，应该使用 BigDecimal 来格式化数字 3.35：

```java
BigDecimal num1 = new BigDecimal("3.35");
BigDecimal num2 = num1.setScale(1, BigDecimal.ROUND_DOWN);
System.out.println(num2);
BigDecimal num3 = num1.setScale(1, BigDecimal.ROUND_HALF_UP);
System.out.println(num3);
```

这次得到的结果是 3.3 和 3.4，符合预期。

**BigDecimal 的判等问题**

我们来看下面的例子。使用 equals 方法比较 1.0 和 1 这两个 BigDecimal：

```java
// false
System.out.println(new BigDecimal("1.0").equals(new BigDecimal("1")))
```

BigDecimal 的 equals 方法的注释中说明了原因，equals 比较的是 BigDecimal 的 value 和 scale，1.0 的 scale 是 1，1 的 scale 是 0，所以结果一定是 false。

如果我们希望只比较 BigDecimal 的 value，可以使用 compareTo 方法：

```java
// true
System.out.println(new BigDecimal("1.0").compareTo(new BigDecimal("1"))==0);
```

BigDecimal 的 equals 和 hashCode 方法会同时考虑 value 和 scale，如果结合 HashSet 或 HashMap 使用的话就可能会出现问题。

```java
Set<BigDecimal> hashSet = new HashSet();
hashSet.add(new BigDecimal("1.0"));
// false
System.out.println(hashSet.contains(new BigDecimal("1")));
```

解决这个问题的办法有两个：

第一个方法是，使用 TreeSet 替换 HashSet。TreeSet 不使用 hashCode 方法，也不使 用 equals 比较元素，而是使用 compareTo 方法，所以不会有问题。

```java
Set<BigDecimal> treeSet = new TreeSet<>();
treeSet.add(new BigDecimal("1.0"));
// true
System.out.println(treeSet.contains(new BigDecimal("1")));
```

第二个方法是，把 BigDecimal 存入 HashSet 或 HashMap 前，先使用 stripTrailingZeros 方法去掉尾部的零，比较的时候也去掉尾部的 0，确保 value 相同的 BigDecimal，scale 也是一致的：

```java
Set<BigDecimal> hashSet = new HashSet<>();
hashSet.add(new BigDecimal("1.0").stripTrailingZeros());
// true
System.out.println(hashSet.contains(new BigDecimal("1.000").stripTrailingZeros()));
```

**如何避免数值溢出问题**

数值计算还有一个要小心的点是溢出，不管是 int 还是 long，所有的基本数值类型都有超出表达范围的可能性。比如，对 Long 的最大值进行 +1 操作：

```java
long l = Long.MAX_VALUE;
// -9223372036854775808
System.out.println(l + 1);
// true
System.out.println(l + 1 == Long.MIN_VALUE);
```

输出结果是一个负数，因为 Long 的最大值 +1 变为了 Long 的最小值。显然这是发生了溢出，而且是默默的溢出，并没有任何异常。这类问题非常容易被忽略，改进方式有下面 2 种。

方法一是，考虑使用 Math 类的 addExact、subtractExact 等 xxExact 方法进行数值运算，这些方法可以在数值溢出时主动抛出异常。

```java
try {
    long l = Long.MAX_VALUE;
    System.out.println(Math.addExact(l, 1));
} catch (Exception ex) {
    ex.printStackTrace();
}
```

执行后，可以得到一个 ArithmeticException。

方法二是，使用大数类 BigInteger。BigDecimal 是处理浮点数的专家，而 BigInteger 则是对大数进行科学计算的专家。

```java
BigInteger i = new BigInteger(String.valueOf(Long.MAX_VALUE));
System.out.println(i.add(BigInteger.ONE).toString());
try {
    long l = i.add(BigInteger.ONE).longValueExact();
} catch (Exception ex) {
    ex.printStackTrace();
}
```

在转换出现溢出时，同 样会抛出 ArithmeticException。

# 10 | 集合类：坑满地的List列表操作

今天，我们就从“把数组转换为 List 集合”、“对 List 进行切片操作”、“List 搜索的性能问题”等几个方面着手，来聊聊其中最可能遇到的一些坑。

**踩坑21：不能直接使用 Arrays.asList 来转换基本类型数组**

- 案例场景

在业务开发中，我们常常会把原始的数组转换为 List 类数据结构，来继续展开各种 Stream 操作。

在如下代码中，我们初始化三个数字的 int[] 数组，然后使用 Arrays.asList 把数组转换为 List：

```java
int[] arr = {1, 2, 3};
List list = Arrays.asList(arr);
log.info("list:{} size:{} class:{}", list, list.size(), list.get(0).getClass());
```

得到结果如下：

```log
22:00:21.553 [main] INFO org.geekbang.time.commonmistakes.collection.aslist.AsListApplication - list:[[I@8acd0f2a] size:1 class:class [I
```

通过日志可以发现，这个 List 包含的其实是一个 int 数组，整个 List 的元素个数是 1，元素类型是整数数组。

- 原因分析

Arrays.asList 方法传入的是一个泛型 T 类型可变参数，最终 int 数组整体作为了一个对象成为了泛型类型 T：

```java
public static <T> List<T> asList(T... a) {
    return new ArrayList<>(a);
}
```

- 解决方案

Java8 以上版本可以使 用 Arrays.stream 方法来转换，也可以把 int 数组声明为包装类型 Integer 数组。

```java
int[] arr1 = {1, 2, 3};
List list1 = Arrays.stream(arr1).boxed().collect(Collectors.toList());
log.info("list:{} size:{} class:{}", list1, list1.size(), list1.get(0).getClass());

Integer[] arr2 = {1, 2, 3};
List list2 = Arrays.asList(arr2);
log.info("list:{} size:{} class:{}", list2, list2.size(), list2.get(0).getClass());
```

得到结果如下：

```log
22:05:59.374 [main] INFO org.geekbang.time.commonmistakes.collection.aslist.AsListApplication - list:[1, 2, 3] size:3 class:class java.lang.Integer
22:05:59.382 [main] INFO org.geekbang.time.commonmistakes.collection.aslist.AsListApplication - list:[1, 2, 3] size:3 class:class java.lang.Integer
```

**踩坑22：Arrays.asList 返回的 List 不支持增删操作**

- 案例场景

使用 Arrays.asList 转换为 List 后，进行以下操作：

```java
String[] arr = {"1", "2", "3"};
List<String> list = Arrays.asList(arr);
try {
    // 为list添加一个字符串
    list.add("5");
} catch (Exception ex) {
    ex.printStackTrace();
}
log.info("arr:{} list:{}", Arrays.toString(arr), list);
```

结果如下：

```log
java.lang.UnsupportedOperationException
	at java.util.AbstractList.add(AbstractList.java:148)
	at java.util.AbstractList.add(AbstractList.java:108)
	at org.geekbang.time.commonmistakes.collection.aslist.AsListApplication.wrong2(AsListApplication.java:45)
	at org.geekbang.time.commonmistakes.collection.aslist.AsListApplication.main(AsListApplication.java:18)
22:14:22.765 [main] INFO org.geekbang.time.commonmistakes.collection.aslist.AsListApplication - arr:[1, 2, 3] list:[1, 4, 3]
```

可以看到，为 List 新增字符串的操作抛出了 UnsupportedOperationException 异常。

- 原因分析

Arrays.asList 返回的 List 并不是 java.util.ArrayList，而是 Arrays 的内部类 ArrayList。ArrayList 内部类继承自 AbstractList 类，并没有覆写父类的 add 方法，而父类中 add 方法的实现，就是抛出 UnsupportedOperationException。相关源码如下所示：

```java
public class Arrays {
  
    public static <T> List<T> asList(T... a) {
        return new ArrayList<>(a);
    }
    
    private static class ArrayList<E> extends AbstractList<E>
        implements RandomAccess, java.io.Serializable {
        //...
    }
}
```

```java
public abstract class AbstractList<E> extends AbstractCollection<E> 
    implements List<E> {
  
    public void add(int index, E element) {
        throw new UnsupportedOperationException();
    }
}
```

- 解决方案

同下。

**踩坑23：对原始数组的修改会影响到我们获得的那个 List**

- 案例场景

使用 Arrays.asList 转换为 List 后，进行以下操作：

```java
String[] arr = {"1", "2", "3"};
List<String> list = Arrays.asList(arr);
// 修改数组的第二个字符串
arr[1] = "4";
log.info("arr:{} list:{}", Arrays.toString(arr), list);
```

结果如下：

```log
22:28:24.425 [main] INFO org.geekbang.time.commonmistakes.collection.aslist.AsListApplication - arr:[1, 4, 3] list:[1, 4, 3]
```

可以看到，把原始数组的第二个元素从 2 修改为 4 后，asList 获得的 List 中的第二个元素也被修改为 4 了。

- 原因分析

看一下 ArrayList 的实现，可以发现 ArrayList 其实是直接使用了原始的数组。

```java
private static class ArrayList<E> extends AbstractList<E>
    implements RandomAccess, java.io.Serializable {
    private final E[] a;
    ArrayList(E[] array) {
        a = Objects.requireNonNull(array);
    }
    //...
}
```

所以，我们要特别小心，把通过 Arrays.asList 获得的 List 交给其他方法处理，很容易因为共享了数组，相互修改产生 Bug。

- 解决方案

重新 new 一个 ArrayList 初始化 Arrays.asList 返回的 List 即可。

```java
String[] arr = {"1", "2", "3"};
List<String> list = new ArrayList<>(Arrays.asList(arr));
arr[1] = "4";
try {
    list.add("5");
} catch (Exception ex) {
    ex.printStackTrace();
}
log.info("arr:{} list:{}", Arrays.toString(arr), list);
```

结果如下：

```log
22:36:54.375 [main] INFO org.geekbang.time.commonmistakes.collection.aslist.AsListApplication - arr:[1, 4, 3] list:[1, 2, 3, 5]
```

**踩坑24：使用 List.subList 进行切片操作居然会导致 OOM?**

- 案例场景

业务开发时常常要对 List 做切片处理，即取出其中部分元素构成一个新的 List。例如下面的操作：

```java
private static List<List<Integer>> data = new ArrayList<>();
private static void oom() {
    for (int i = 0; i < 1000; i++) {
        List<Integer> rawList = IntStream.rangeClosed(1, 1000000).boxed().collect(Collectors.toList());
        data.add(rawList.subList(0, 1));
    }
}
```

程序运行不久就出现了 OOM：

```log
Exception in thread "main" java.lang.OutOfMemoryError: Java heap space
  at java.util.Arrays.copyOf(Arrays.java:3181)
  at java.util.ArrayList.grow(ArrayList.java:265)
```

- 原因分析

出现 OOM 的原因是，datas 中 1000 个 List 都具有 10 万个元素，且始终得不到回收，因为它始终被 subList 方法返回的 List 强引用。我们分析下 ArrayList 的源码：

```java
public class ArrayList<E> extends AbstractList<E>
        implements List<E>, RandomAccess, Cloneable, java.io.Serializable {
    // [1] 表示集合结构性修改的次数，即影响集合size修改的次数
    protected transient int modCount = 0;
    
    private void ensureExplicitCapacity(int minCapacity) {
        modCount++;
        // overflow-conscious code
        if (minCapacity - elementData.length > 0)
            grow(minCapacity);
    }
  
    public boolean add(E e) {
        ensureCapacityInternal(size + 1);  // Increments modCount!!
        elementData[size++] = e;
        return true;
    }
  
    // [2]<<
    public List<E> subList(int fromIndex, int toIndex) {
        subListRangeCheck(fromIndex, toIndex, size);
        return new SubList(this, 0, fromIndex, toIndex);
    } // [2]>>
  
    // [3]<<
    private class SubList extends AbstractList<E> implements RandomAccess {
        private final AbstractList<E> parent;
        private final int parentOffset;
        private final int offset;
        int size;

        SubList(AbstractList<E> parent,
                int offset, int fromIndex, int toIndex) {
            this.parent = parent;
            this.parentOffset = fromIndex;
            this.offset = offset + fromIndex;
            this.size = toIndex - fromIndex;
            this.modCount = ArrayList.this.modCount;
        } // [3]>>

        public E set(int index, E e) {
            rangeCheck(index);
            checkForComodification();
            E oldValue = ArrayList.this.elementData(offset + index);
            ArrayList.this.elementData[offset + index] = e;
            return oldValue;
        }
        // [4]<<
        public ListIterator<E> listIterator(final int index) {
            checkForComodification();
            // ...
        }
      
        private void checkForComodification() {
            if (ArrayList.this.modCount != this.modCount)
                throw new ConcurrentModificationException();
        } // [4]>>
    }
}
```

分析第 [2] 部分的 subList 方法可以看到，获得的 List 其实是内部类 SubList， 并不是普通的 ArrayList，在初始化的时候传入了 this。

分析第 [3] 部分的代码可以发现，这个 SubList 中的 parent 字段就是原始的 List。SubList 初始化的时候，并没有把原始 List 中的元素复制到独立的变量中保存。SubList 强引用了原始的 List，所以大量保存这样的 SubList 会导致 OOM。

> 如果进行下面代码操作，会抛出异常：
>
> ```java
> List<Integer> list = IntStream.rangeClosed(1, 10).boxed().collect(Collectors.toList());
> List<Integer> subList = list.subList(1, 4);
> list.add(0);
> try {
>     subList.forEach(System.out::println);
> } catch (Exception ex) {
>     ex.printStackTrace();
> }
> ```
>
> 分析第 [4] 部分代码可以发现，遍历 SubList 的时候会先获得迭代器，比较原始 ArrayList modCount 的值和 SubList 当前 modCount 的值。获得了 SubList 后，我们为原始 List 新增了一个元素导致修改了其 modCount，所以会抛出 ConcurrentModificationException 异常。 

- 解决方案

避免相互影响的修复方式有两种：

一种是，不直接使用 subList 方法返回的 SubList，而是重新使用 new ArrayList，在构造方法传入 SubList，来构建一个独立的 ArrayList；

另一种是，对于 Java 8 使用 Stream 的 skip 和 limit API 来跳过流中的元素，以及限制流中元素的个数，同样可以达到 SubList 切片的目的。

```java
// 方式一
List<Integer> subList = new ArrayList<>(list.subList(1, 4));

// 方式二
List<Integer> subList = list.stream().skip(1).limit(3).collect(Collectors.toList());
```

**如何分析类的内存占用？**

现在有一个 ArrayList 和一个 HashMap 各存储 100 万个 Order 对象。代码如下：

```java
@Data
@NoArgsConstructor
@AllArgsConstructor
static class Order {
    private int orderId;
}
```

```java
List<Order> list = IntStream.rangeClosed(1, 1000_000)
        .mapToObj(Order::new)
        .collect(Collectors.toList());

Map<Integer, Order> map = IntStream.rangeClosed(1, 1000_000)
        .boxed()
        .collect(Collectors.toMap(Function.identity(), Order::new));
```

我们使用 JDK ObjectSizeCalculator 工具打印 ArrayList 和 HashMap 的内存占用。

```java
System.out.println(ObjectSizeCalculator.getObjectSize(list)); // 21M
System.out.println(ObjectSizeCalculator.getObjectSize(map)); // 72M
```

ArrayList 占用内存 21M，HashMap 占用的内存 72M。使用 MAT 工具进一步分析堆可以证明，ArrayList 在内存占用上性价比很高， 77% 是实际的数据（16000000/20861992）。

![image-20210625222048765](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210625222048.png)

而 HashMap 只有 22%（16000000/72386640）。

![image-20210625222155881](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210625222155.png)

**踩坑25：LinkedList 插入元素一定比 ArrayList 快吗？**

- 案例场景

对于数组，随机元素访问的时间复杂度是 O(1)，元素插入操作是 O(n)；

对于链表，随机元素访问的时间复杂度是 O(n)，元素插入操作是 O(1)。

我们分别来对 ArrayList 和 LinkedList 进行插入、访问操作。

```java
private static void linkedListGet(int elementCount, int loopCount) {
    List<Integer> list = IntStream.rangeClosed(1, elementCount).boxed().collect(Collectors.toCollection(LinkedList::new));
    IntStream.rangeClosed(1, loopCount).forEach(i -> list.get(ThreadLocalRandom.current().nextInt(elementCount)));
}

private static void arrayListGet(int elementCount, int loopCount) {
    List<Integer> list = IntStream.rangeClosed(1, elementCount).boxed().collect(Collectors.toCollection(ArrayList::new));
    IntStream.rangeClosed(1, loopCount).forEach(i -> list.get(ThreadLocalRandom.current().nextInt(elementCount)));
}

private static void linkedListAdd(int elementCount, int loopCount) {
    List<Integer> list = IntStream.rangeClosed(1, elementCount).boxed().collect(Collectors.toCollection(LinkedList::new));
    IntStream.rangeClosed(1, loopCount).forEach(i -> list.add(ThreadLocalRandom.current().nextInt(elementCount), 1));
}

private static void arrayListAdd(int elementCount, int loopCount) {
    List<Integer> list = IntStream.rangeClosed(1, elementCount).boxed().collect(Collectors.toCollection(ArrayList::new));
    IntStream.rangeClosed(1, loopCount).forEach(i -> list.add(ThreadLocalRandom.current().nextInt(elementCount), 1));
}
```

测试代码如下：

```java
int elementCount = 100000;
int loopCount = 100000;
StopWatch stopWatch = new StopWatch();
stopWatch.start("linkedListGet");
linkedListGet(elementCount, loopCount);
stopWatch.stop();
stopWatch.start("arrayListGet");
arrayListGet(elementCount, loopCount);
stopWatch.stop();
System.out.println(stopWatch.prettyPrint());

StopWatch stopWatch2 = new StopWatch();
stopWatch2.start("linkedListAdd");
linkedListAdd(elementCount, loopCount);
stopWatch2.stop();
stopWatch2.start("arrayListAdd");
arrayListAdd(elementCount, loopCount);
stopWatch2.stop();
System.out.println(stopWatch2.prettyPrint());
```

结果如下：

```log
--------------------------------------------
ns        %        Task name
--------------------------------------------
6604199591 100% linkedListGet
011494583 000% arrayListGet

StopWatch '': running time = 10729378832 ns
---------------------------------------------
ns        %       Task name
---------------------------------------------
9253355484 086% linkedListAdd
1476023348 014% arrayListAdd
```

可以看到，ArrayList 访问元素耗时 11 毫秒，而 LinkedList 耗时 6.6 秒，这符合上面我们所说的时间复杂度；但，随机插入操作居然也是 LinkedList 落败，耗时 9.3 秒，ArrayList 只要 1.5 秒。

- 原因分析

LinkedList 源码如下：

```java
public void add(int index, E element) {
    checkPositionIndex(index);
    if (index == size)
        linkLast(element);
    else
        linkBefore(element, node(index));
}

Node<E> node(int index) {
    // assert isElementIndex(index);
    if (index < (size >> 1)) {
        Node<E> x = first;
        for (int i = 0; i < index; i++)
            x = x.next;
        return x;
    } else {
        Node<E> x = last;
        for (int i = size - 1; i > index; i--
            x = x.prev;
        return x;
    }
}
```

可以看到，插入操作的时间复杂度是 O(1) 的前提是，你已经有了那个要插入节点的指针。但在实现的时候，我们需要先通过循环获取到那个节点的 Node，然后再执行插入操作。前者也是有开销的，不可能只考虑插入操作本身的代价。

- 解决方案

对于插入操作，LinkedList 的时间复杂度其实也是 O(n)。继续做更多实验的话你会发现，在各种常用场景下，LinkedList 几乎都不能在性能上胜出 ArrayList。

# 11 | 空值处理：分不清楚的null和恼人的空指针

**如何修复空指针异常？**

Java 代码中出现 NullPointerException 场景有以下 5 种：

1. 包装类型拆箱：参数值是 Integer 等包装类型，使用时因为自动拆箱出现了空指针异常；

   例如：i + 1。

   解决：可以使用 Optional.ofNullable 来构造一个 Optional，然后使用 orElse(0) 把 null 替换为默认值再进行 +1 操作。

2. 字符串比较：字符串比较出现空指针异常；

   例如：s.equals("OK")。

   解决：可以把字面量放在前面 "OK".equals(s)。

3. 容器操作：使用不支持 Key 和 Value 为 null 的容器（例如 ConcurrentHashMap），强行 put null 的 Key 或 Value；

   例如：new ConcurrentHashMap<String, String>().put(null, null)。

4. 级联调用：A 对象包含了 B，在通过 A 对象的字段获得 B 之后，没有对字段判空就级联调用 B 的方法；

   例如：fooService.getBarService().bar().equals(“OK”)。

   解决：使用 Optional，如：

   ```java
   Optional.ofNullable(fooService)
       .map(FooService::getBarService)
       .filter(barService -> "OK".equals(barService.bar()))
       .ifPresent(result -> log.info("OK"));
   ```

5. 容器为空：方法或远程服务返回的 List 不是空而是 null，没有进行判空就直接调用 List 的方法。

**如何定位空指针问题？**

线上可以使用 Arths。

![image-20210627215345967](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210627215351.png)

第二个红框表示，Arthas 启动后被附加到了 JVM 进程;

第三个红框表示，通过 watch 命令监控 wrongMethod 方法的入参。

**小心 MySQL 中有关 NULL 的三个坑**

1. MySQL 中 sum 函数没统计到任何记录时，会返回 null 而不是 0，可以使用 IFNULL 函数把 null 转换为 0；

   例如：

   ```sql
   SELECT SUM(score) FROM `user`
   ```

   解决：

   ```sql
   SELECT IFNULL(SUM(score),0) FROM `user`
   ```

2. MySQL 中 count 字段不统计 null 值，COUNT(*) 才是统计所有记录数量的正确方式。

   例如：

   ```sql
   SELECT COUNT(score) FROM `user`
   ```

   解决：

   ```sql
   SELECT COUNT(*) FROM `user`
   ```

3. MySQL 中 =NULL 并不是判断条件而是赋值，对 NULL 进行判断只能使用 IS NULL 或 者 IS NOT NULL。

   例如：

   ```sql
   SELECT * FROM `user` WHERE score=null
   ```

   解决：

   ```sql
   SELECT * FROM `user` WHERE score IS NULL
   ```

> 在 MySQL 的使用中，对于索引列，建议都设置为not null，因为如果有 null 的话，MySQL需要单独专门处理 null 值，会额外耗费性能。

**思考与讨论**

思考一：ConcurrentHashMap 的 Key 和 Value 都不能为 null，而 HashMap 却可以，你知道这么设计的原因是什么吗?TreeMap、Hashtable 等 Map 的 Key 和 Value 是否支持 null 呢?

答：ConcurrentMaps（ConcurrentHashMaps，ConcurrentSkipListMaps）不允许使用null的主要原因是，无法容纳在非并行映射中几乎无法容忍的歧义。最主要的是，如果 map.get(key) return null，则无法检测到该键是否显式映射到 null 该键。在非并行映射中，您可以通过进行检查 map.contains(key)，但在并行映射中，两次调用之间的映射可能已更改。

hashtable也是线程安全的，所以也是key和value也是不可以null的；

treeMap 线程不安全，但是因为需要排序，进行key的compareTo方法，所以key是不能null中，value是可以的；

思考二：对于 Hibernate 框架可以使用 @DynamicUpdate 注解实现字段的动态更新，对于 MyBatis 框架如何实现类似的动态 SQL 功能，实现插入和修改 SQL 只包含 POJO 中的 非空字段?

答：MyBatis @Column注解的updateIfNull属性，可以控制，当对应的列value为null时，updateIfNull的true和false可以控制。

# 12 | 异常处理：别让自己在出问题的时候变为瞎子

**处理异常容易犯的错**

- 错误一：不在业务代码层面考虑异常处理，仅在框架层面粗犷捕获和处理异常

Repository 层出现异常可以忽略。如果一律捕获异常仅记录日志，很可能业务逻辑已经出错，而用户和程序却完全感知不到。

Service 层出现异常同样不适合捕获。该层往往涉及数据库事务，如果业务异常都被框架捕获了，业务功能就会不正常。

Controller 层往往会给予用户友好提示，或是根据每一个 API 的异常表返回指定的异常类型，同样不能对所有异常一视同仁。

例如下面的代码：

```java
@RestControllerAdvice
@Slf4j
public class RestControllerExceptionHandler {

    private static int GENERIC_SERVER_ERROR_CODE = 2000;
    private static String GENERIC_SERVER_ERROR_MESSAGE = "服务器忙，请稍后再试";

    @ExceptionHandler
    public APIResponse handle(HttpServletRequest req, 
                              HandlerMethod method, Exception ex) {
        if (ex instanceof BusinessException) {
            BusinessException exception = (BusinessException) ex;
            log.warn(String.format("访问 %s -> %s 出现业务异常！", req.getRequestURI(), 
                                   method.toString()), ex);
            return new APIResponse(false, null, exception.getCode(), exception.getMessage());
        } else {
            log.error(String.format("访问 %s -> %s 出现系统异常！", req.getRequestURI(), 
                                    method.toString()), ex);
            return new APIResponse(false, null, GENERIC_SERVER_ERROR_CODE, GENERIC_SERVER_ERROR_MESSAGE);
        }
    }
}
```

- 错误二：捕获了异常后直接生吞

在任何时候，我们捕获了异常都不应该生吞。

- 错误三：丢弃异常的原始信息

比如有这么一个会抛出受检异常的方法 readFile：

```java
@GetMapping("wrong1")
public void wrong1() {
    try {
        readFile();
    } catch (IOException e) {
        // 原始异常信息丢失
        throw new RuntimeException("系统忙请稍后再试");
    }
}

private void readFile() throws IOException {
    Files.readAllLines(Paths.get("a_file"));
}
```

这样捕获异常后，出了问题不知道 IOException 具体是哪里引起的。

或者是这样，只记录了异常消息，却丢失了异常的类型、栈等重要信息：

```java
catch (IOException e) {
    // 只保留了异常消息，栈没有记录
    log.error("文件读取错误, {}", e.getMessage());
    throw new RuntimeException("系统忙请稍后再试");
}
```

上面两种处理方式都不太合理，可以改为如下方式：

```java
catch (IOException e) {
    log.error("文件读取错误", e);
    throw new RuntimeException("系统忙请稍后再试");
}
// 或
catch (IOException e) {
    throw new RuntimeException("系统忙请稍后再试", e);
}
```

- 错误四：抛出异常时不指定任何消息

例如直接 `throw new RuntimeException();`

**踩坑26：try 中的逻辑出现了异常，但却被 finally 中的异常覆盖了**

- 案例场景

```java
@GetMapping("wrong")
public void wrong() {
    try {
        log.info("try");
        throw new RuntimeException("try");
    } finally {
        log.info("finally");
        throw new RuntimeException("finally");
    }
}
```

结果日志只打印了 finally 中的异常。

- 原因分析

一个方法无法出现两个异常。

- 解决方案

方案一：finally 代码块自己负责异常捕获和处理。

```java
@GetMapping("right")
public void right() {
    try {
        log.info("try");
        throw new RuntimeException("try");
    } finally {
        log.info("finally");
        try {
            throw new RuntimeException("finally");
        } catch (Exception ex) {
            log.error("finally", ex);
        }
    }
}
```

方案二：把 try 中的异常作为主异常抛出，使用 addSuppressed 方法把 finally 中的异常附加到主异常上。

```java
@GetMapping("right2")
public void right2() throws Exception {
    Exception e = null;
    try {
        log.info("try");
        throw new RuntimeException("try");
    } catch (Exception ex) {
        e = ex;
    } finally {
        log.info("finally");
        try {
            throw new RuntimeException("finally");
        } catch (Exception ex) {
            if (e != null) {
                e.addSuppressed(ex);
            } else {
                e = ex;
            }
        }
    }
    throw e;
}
```

> 这正是 try-with-resources 语法所做的事情。

**踩坑27：将异常定义为静态变量，导致异常栈信息错乱**

- 案例场景

在排查某项目生产问题时，遇到了一件非常诡异的事情：我发现异常堆信息显示的方法调用路径，在当前入参的情况下根本不可能产生。

经过艰难的排查，最终定位到原因是把异常定义为了静态变量，导致异常栈信息错乱。模拟代码如下：

```java
@GetMapping("wrong")
public void wrong() {
    try {
        createOrderWrong();
    } catch (Exception ex) {
        log.error("createOrder got error", ex);
    }
    try {
        cancelOrderWrong();
    } catch (Exception ex) {
        log.error("cancelOrder got error", ex);
    }
}

private void createOrderWrong() {
    // 这里有问题
    throw Exceptions.ORDEREXISTS;
}

private void cancelOrderWrong() {
    // 这里有问题
    throw Exceptions.ORDEREXISTS;
}
```

```java
public class Exceptions {

    public static BusinessException ORDEREXISTS = new BusinessException("订单已经存在", 3001);
}
```

结果 cancelOrder got error 的提示对应了 createOrderWrong 方法。

- 原因分析
- 解决方案

改一下 Exceptions 类的实现，通过不同的方法把每一种异常都 new 出来抛出即可。

```java
public class Exceptions {

    public static BusinessException orderExists() {
        return new BusinessException("订单已经存在", 3001);
    }
}
```

**踩坑28：捕获线程池任务异常导致线程重建**

- 案例场景

我们来看一个例子:提交 10 个任务到线程池异步处理，第 5 个任务抛出一个 RuntimeException，每个任务完成后都会输出一行日志。

```java
@GetMapping("execute")
public void execute() throws InterruptedException {

    String prefix = "test";
    ExecutorService threadPool = Executors.newFixedThreadPool(1, new ThreadFactoryBuilder()
            .setNameFormat(prefix + "%d")
            .get());
    IntStream.rangeClosed(1, 10).forEach(i -> threadPool.execute(() -> {
        if (i == 5) throw new RuntimeException("error");
        log.info("I'm done : {}", i);
    }));

    threadPool.shutdown();
    threadPool.awaitTermination(1, TimeUnit.HOURS);
}
```

结果是：任务 1 到 4 所在的线程是 test0，任务 6 开始运行在线程 test1。

因为没有手动捕获异常进行处理，向标准错误输出打印了出现异常的线程名称和异常信息。

- 原因分析

从线程名的改变可以知 道因为异常的抛出老线程退出了，线程池只能重新创建一个线程。如果每个异步任务都以异常结束，那么线程池可能完全起不到线程重用的作用。

Thread 的想着源码如下：

```java
public UncaughtExceptionHandler getUncaughtExceptionHandler() {
	if (exceptionHandler == null)
    // 没设置 exceptionHandler 则返回 ThreadGroup
		return getThreadGroup();
	return exceptionHandler;
}
```

ThreadGroup 的相关源码如下所示：

```java
public void uncaughtException(Thread t, Throwable e) {
	Thread.UncaughtExceptionHandler handler;
	if (parent != null) {
		parent.uncaughtException(t,e);
	} else if ((handler = Thread.getDefaultUncaughtExceptionHandler()) != null) {
		handler.uncaughtException(t, e);
	} else if (!(e instanceof ThreadDeath)) {
		// No parent group, has to be 'system' Thread Group
		// K0319 = Exception in thread "{0}" 
		System.err.print(com.ibm.oti.util.Msg.getString("K0319", t.getName())); //$NON-NLS-1$
		e.printStackTrace(System.err);
	}
}
```

- 解决方案

修复方式有 2 步：

第一，以 execute 方法提交到线程池的异步任务，最好在任务内部做好异常处理；

第二，设置自定义的异常处理程序作为保底，比如在声明线程池时自定义线程池的未捕获异常处理程序：

```java
new ThreadFactoryBuilder()
        .setNameFormat(prefix + "%d")
        .setUncaughtExceptionHandler(
            (thread, throwable) -> log.error("ThreadPool {} got exception", thread, throwable))
        .get()
```

或者设置全局的默认未捕获异常处理程序：

```java
static {
    Thread.setDefaultUncaughtExceptionHandler(
        (thread, throwable) -> log.error("Thread {} got exception", thread, throwable)
    );
}
```

# 13 | 日志:日志记录真没你想象的那么简单

使用日志容易出错主要在于以下几个方面：

1. 日志框架众多。

Logback、Log4j、Log4j2、commons-logging、JDK 自带的 java.util.logging 等，都是 Java 体系的日志框架。而不同的类库，还可能选择使用不同的日志框架， 这样一来，日志的兼容与统一管理就变得非常困难。

2. 配置复杂且容易出错。

日志配置文件通常很复杂，改配置容易造成很多问题。比如，重复记录日志的问题、同步日志的性能问题、异步记录的错误配置问题。

3. 没考虑日志内容获取的代价。
4. 胡乱使用日志级别。

SLF4J（Simple Logging Facade For Java）是为了统一各类日志框架而诞生的。如下图所示：

![image-20210703223513586](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210703223513.png)

SLF4J 实现了三种功能：

一是提供了统一的日志门面 API，即图中紫色部分，实现了中立的日志记录 API。

二是桥接功能，即图中蓝色部分，用来把各种日志框架的 API（图中绿色部分）桥接到 SLF4J API。

三是适配功能，即图中红色部分，可以实现 SLF4J API 和实际日志框架（图中灰色部分）的绑定。

> SLF4J 只是日志标准，我们还是需要一个实际的日志框架。而日志框架本身没有实现 SLF4J API，所以需要有一个前置转换。Logback 就是按照 SLF4J API 标准实现的，因此不需要绑定模块做转换。

> 注意：我们可以使用 log4j-over-slf4j 来实现 Log4j 桥接到 SLF4J，也可以使用 slf4j-log4j12 实现 SLF4J 适配到 Log4j。但是它不能同时使用它们，否则就会产生死循环。jcl 和 jul 也是同样的道理。

> 图中有 4 个灰色的日志实现框架，业务系统使用最广泛的是 Logback 和 Log4j，它们是同一人开发的。Logback 可以认为是 Log4j 的改进版本，更推荐使用。

**踩坑29：logger 配置了继承关系导致日志重复记录**

- 案例场景

首先，定义一个方法实现 debug、info、warn 和 error 四种日志的记录：

```java
@Slf4j
@RequestMapping("logging")
@RestController
public class LoggingController {

    @GetMapping("log")
    public void log() {
        log.debug("debug");
        log.info("info");
        log.warn("warn");
        log.error("error");
    }
}
```

然后，配置 Logback：

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<configuration>
    <!-- [2] << -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <layout class="ch.qos.logback.classic.PatternLayout">
            <pattern>[%d{yyyy-MM-dd HH:mm:ss.SSS}] [%thread] [%-5level] [%logger{40}:%line] - %msg%n</pattern>
        </layout>
    </appender> <!-- >> -->
    <!-- [3] << -->
    <logger name="org.geekbang.time.commonmistakes.logging" level="DEBUG">
        <appender-ref ref="CONSOLE"/> <!-- [4] -->
    </logger> <!-- >> -->
    <!-- [1] << -->
    <root level="INFO">
        <appender-ref ref="CONSOLE"/> <!-- [5] -->
    </root> <!-- >> -->
</configuration>
```

[1] 处设置了全局的日志级别为 INFO，日志输出使用 CONSOLE Appender。

[2] 处将 CONSOLE 定义为 ConsoleAppender，且定义了日志的输出格式。

[3] 处实现了一个 Logger 配置，将应用包的日志级别设置为 DEBUG、日志输出使用 CONSOLE Appender。

执行方法后出现了日志重复记录的问题：

![image-20210703232939441](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210703232939.png)

- 原因分析

从 [4]、[5] 可以看到，CONSOLE 这个 Appender 同时挂载到了两个 Logger 上，一个是我们定义的，一个是继承自 root 的。所以同一条日志既会通过 logger 记录，也会发送到 root 记录，因此应用 package 下的日志出现了重复记录。

经了解，该同学如此配置的初衷是让应用内的日志暂时开启 DEBUG 级别的日志记录。

- 解决方案

方案一：去掉挂载的 Appender。

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<configuration>
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <layout class="ch.qos.logback.classic.PatternLayout">
            <pattern>[%d{yyyy-MM-dd HH:mm:ss.SSS}] [%thread] [%-5level] [%logger{40}:%line] - %msg%n</pattern>
        </layout>
    </appender>
    <logger name="org.geekbang.time.commonmistakes.logging" level="DEBUG"/>
    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
    </root>

</configuration>
```

方案二：把日志输出到不同的 Appender。

将应用的日志输出到文件 app.log，并把其他框架的日志输出到控制台，且 additivity 属性为 false，这样就不会继承的 Appender 了。

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<configuration>
    <appender name="FILE" class="ch.qos.logback.core.FileAppender">
        <file>app.log</file>
        <encoder class="ch.qos.logback.classic.encoder.PatternLayoutEncoder">
            <pattern>[%d{yyyy-MM-dd HH:mm:ss.SSS}] [%thread] [%-5level] [%logger{40}:%line] - %msg%n</pattern>
        </encoder>
    </appender>
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
		<layout class="ch.qos.logback.classic.PatternLayout">
            <pattern>[%d{yyyy-MM-dd HH:mm:ss.SSS}] [%thread] [%-5level] [%logger{40}:%line] - %msg%n</pattern>
		</layout>
	</appender>
    <logger name="org.geekbang.time.commonmistakes.logging" level="DEBUG" additivity="false">
        <appender-ref ref="FILE"/>
    </logger>
	<root level="INFO">
		<appender-ref ref="CONSOLE" />
	</root>
</configuration>
```

**踩坑30**

- 案例场景
- 原因分析
- 解决方案



**踩坑31**

- 案例场景
- 原因分析
- 解决方案



**踩坑32**

- 案例场景
- 原因分析
- 解决方案



**踩坑33**

- 案例场景
- 原因分析
- 解决方案

