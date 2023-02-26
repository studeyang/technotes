# ChatGPT 今后可能是我编程路上的好帮手

> 本文转载自：https://www.wdbyte.com/java/chatgpt-files-list.html

今天在测试一个准备上线的新功能时，里面有一段简单的函数，出现了一个 BUG。我先说一下这个函数的功能，看下你会怎么写。

## 功能描述

输入：一个文件夹路径。

输出：这个文件夹中的文件夹数量。

这是一个实现起来比较简单的函数，我顺手写了下面的代码：

```java
String pathString = "/Users/darcy/";
File fileDir = new File(pathString);
if (!fileDir.exists() || !fileDir.isDirectory()) {
    throw new RuntimeException("xxx....");
}
String[] fileList = fileDir.list();
int count = 0;
for (String filePath : fileList) {
    if (new File(pathString + filePath).isDirectory()) {
        count++;
    }
}
System.out.println(count);
```

功能是实现了，但是很明显，代码比较繁琐，于是我又顺手优化了一下。

```java
Path path = Paths.get("/Users/darcy/");
if (!Files.exists(path) || !Files.isDirectory(path)) {
    throw new RuntimeException("xxx....");
}
long dirCount = Files.list(path).filter(Files::isDirectory).count();
System.out.println(dirCount);
```

效果是一样的，因为使用了 JDK 7 引入的 Files 类，让代码简单了不少。

不过正是这段代码，触发了 BUG，我先卖个关子，你先看下 BUG 在什么地方。

## 问题分析

你看出问题了吗？改造后的代码运行少量次数的情况下，都是可以正常输出的。但是它有一个问题，就是 Files.list 返回的 Stream 流没有进行关闭，这就导致如果这段代码被频繁的调用，一段时间后将会因为打开的文件过多而报错，可以测试出这种异常情况。

我们来复现这个问题，在循环中不断运行这段代码：

```java
 while (true) {
     Path path = Paths.get("/Users/darcy/");
     if (!Files.exists(path) || !Files.isDirectory(path)) {
         throw new RuntimeException("xxx....");
     }
     long dirCount = Files.list(path).filter(Files::isDirectory).count();
     System.out.println(dirCount);
 }
```

一段时间后控制台收到报错：Too many open files

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202302262345237.jpeg)

## 问题原因

报错的原因是因为每个进程可以打开的文件数量是有限制的，如果一直打开不进行关闭，在达到限制时会报出这个错误。

不妨让代码运行速度降低，然后监控下随着程序的运行，运行进程持有的文件数是否不断增加。

```java
while (true) {
    Path path = Paths.get("/Users/darcy/");
    if (!Files.exists(path) || !Files.isDirectory(path)) {
        throw new RuntimeException("xxx....");
    }
    long dirCount = Files.list(path).filter(Files::isDirectory).count();
    System.out.println(dirCount);
    Thread.sleep(1000);
}
```

下面是用到的命令。

```shell
## 查找进程 ID
➜  ~ jps -mlVv | grep testFileList
## 查看指定进程引用的文件数量
➜  ~ lsof -p 62248 | wc -l
```

从测试结果中可以看到随着程序的运行，进程持有的文件数量不断上升。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202302262346847.jpeg)

## 问题解决

原因已经知道了，既然 Files.list 返回的 Stream 流没有进行关闭，那么进行关闭就可以解决问题。

```java
while (true){
    Path path = Paths.get("/Users/darcy/");
    if (!Files.exists(path) || !Files.isDirectory(path)) {
        throw new RuntimeException("xxx....");
    }
    // 方式1：手动关闭流
    // Stream<Path> pathStream = Files.list(path);
    // long dirCount = pathStream.filter(Files::isDirectory).count();
    // pathStream.close();
    // 方式2：使用 try resource 自动关闭流
    try (Stream<Path> pathStream = Files.list(path);){
        long dirCount = pathStream.filter(Files::isDirectory).count();
        System.out.println(dirCount);
    }
    Thread.sleep(1000);
}
```

再次运行后，引用的文件数量不再上涨，BUG 解决。

```shell
~ lsof -p 62879 | wc -l
  321
~ lsof -p 62879 | wc -l
  321
~ lsof -p 62879 | wc -l
  321
~ lsof -p 62879 | wc -l
  321
~ lsof -p 62879 | wc -l
  321
~ lsof -p 62879 | wc -l
  321
```

## ChatGPT 分析

如果这段代码使用 ChatGPT 分析，它能发现问题吗？我先告诉你答案，它能发现，而且描述的很好，并且给出了修复建议。

**我问：**

下面这段 Java 代码有什么问题吗？

```java
Path path = Paths.get("/Users/darcy/");
if (!Files.exists(path) || !Files.isDirectory(path)) {
    throw new RuntimeException("fileDir.isDirectory() error");
}
long dirCount = Files.list(path).filter(Files::isDirectory).count();
System.out.println(dirCount);
```

**ChatGPT：**

这段代码首先会检查 `/Users/darcy/` 目录是否存在并且是一个目录，如果不是，则会抛出 `RuntimeException`。接着，它会计算 `/Users/darcy/` 目录下的子目录数量并将其打印到控制台。

这段代码看起来没有语法错误，但是在运行时可能会抛出 `IOException`，因为对文件系统进行操作时可能会出现各种异常情况。特别是，如果指定的路径不存在，则会抛出 `NoSuchFileException`。因此，在代码中最好捕获可能发生的异常并进行处理，或者在方法签名中声明抛出异常以通知调用方。

此外，还需要注意的是，`Files.list(path)` 方法返回的是一个 `Stream<Path>` 对象，需要注意其资源释放问题，以避免潜在的资源泄漏问题。通常情况下，可以使用 `try-with-resources` 语句来自动关闭流，例如：

```java
try (Stream<Path> stream = Files.list(path)) {
    long dirCount = stream.filter(Files::isDirectory).count();
    System.out.println(dirCount);
} catch (IOException e) {
    // 处理异常
}
```

下面是对话截图：

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202302262349413.jpeg)

## ChatGPT 实现功能

**问：**

帮我用 Java 写一串代码。 功能描述。

输入：一个文件夹路径。

输出：这个文件夹中的文件夹数量。

**ChatGPT 回答：**

以下是 Java 代码示例，用于计算指定文件夹路径下的文件夹数量：

```java
import java.io.File;

public class FolderCount {
    public static void main(String[] args) {
        String path = "path/to/folder"; // 替换成你的文件夹路径
        File folder = new File(path);
        int count = 0;
        if (folder.isDirectory()) {
            File[] files = folder.listFiles();
            for (File file : files) {
                if (file.isDirectory()) {
                    count++;
                }
            }
        }
        System.out.println("该文件夹中的文件夹数量为：" + count);
    }
}
```

该程序首先接收一个文件夹路径作为输入，然后创建一个 File 对象来代表该文件夹。然后它遍历该文件夹中的所有文件，如果找到一个文件夹，则将计数器加一。最后，它输出计数器的值作为结果。

下面是对话截图：

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202302262349196.jpeg)

## 总结

在本文中，我们介绍了一个简单功能的 Java 代码 BUG，即未关闭 `Files.list()` 返回的流对象，导致程序运行时可能会打开过多的文件而出现异常。我们通过手动分析代码和测试，找出了问题所在，并提供了两种解决方案，一种是手动关闭流，另一种是使用 try-with-resources 自动关闭流。最后，我们还使用 ChatGPT 测试了是否可以用 AI 自动识别代码中存在的问题，结果表明 ChatGPT 可以帮助我们发现这类问题，为我们的编程工作提供了有力的支持。

上面这个总结，也是 ChatGPT 帮我写的，相对于 ChatGPT 能给出具体的代码，我更震惊于 ChatGPT 对于语义的理解，不仅能理解我的输入，还能对代码意思进行自然语言描述。今后你很可能分辨不出你所阅读的文章是人类写的，还是 ChatGPT 自动生成的。

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/ends.gif)

## 封面

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202302262342445.jpg)
