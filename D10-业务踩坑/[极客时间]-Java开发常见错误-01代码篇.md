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

- 原因分析

使用了 ThreadLocal 来缓存获取到的用户信息。程序运行在 Tomcat 中，Tomcat 的工作线程是基于线程池的。

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
        int gap = ITEM_COUNT - concurrentHashMap.size();
        log.info("gap size:{}", gap);
        concurrentHashMap.putAll(getData(gap));
    }));
    forkJoinPool.shutdown();
    forkJoinPool.awaitTermination(1, TimeUnit.HOURS);

    log.info("finish size:{}", concurrentHashMap.size());
    return "OK";
}
```

输出日志如下：

![image-20210603214203964](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20210603214204.png)

- 原因分析

诸如 size、isEmpty 和 containsValue 等聚合方法，在并发情况下反映的是 ConcurrentHashMap 的中间状态。

- 解决方案

```java
@GetMapping("right")
public String right() throws InterruptedException {
    ConcurrentHashMap<String, Long> concurrentHashMap = getData(ITEM_COUNT - 100);
    log.info("init size:{}", concurrentHashMap.size());

    ForkJoinPool forkJoinPool = new ForkJoinPool(THREAD_COUNT);
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

1. 使用 ConcurrentHashMap 来统计，Key 的范围是 10；
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

**踩坑4：在写操作很多的场景下使用 CopyOnWriteArrayList 导致性能问题**

- 案例场景

之前在排查一个生产性能问题时，我们发现一段简单的非数据库操作的业务逻辑，消耗了超出预期的时间，在修改数据时操作本地缓存比回写数据库慢许多。查看代码发现，开发同学使用了 CopyOnWriteArrayList 来缓存大量的数据，而数据变化又比较频繁。

- 原因分析

在 Java 中，CopyOnWriteArrayList 虽然是一个线程安全的 ArrayList，但因为其实现方式是，每次修改数据时都会用 Arrays.copyOf 复制一份数据出来。

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

所以有明显的适用场景，即读多写少或者说希望无锁读的场景。

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

# 02 | 代码加锁：不要让“锁”事成为烦心事

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



**踩坑8：**

- 案例场景
- 原因分析
- 解决方案



**踩坑8：**

- 案例场景
- 原因分析
- 解决方案



**踩坑8：**

- 案例场景
- 原因分析
- 解决方案



**踩坑8：**

- 案例场景
- 原因分析
- 解决方案



**踩坑8：**

- 案例场景
- 原因分析
- 解决方案