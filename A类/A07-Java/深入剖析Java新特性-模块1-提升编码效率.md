> 来自极客时间《深入剖析 Java 新特性》--范学雷

# 开篇词 | 拥抱Java新特性，像设计者一样工作和思考

保守估计，你如果从 JDK 8 迁移到 JDK 17，并且能够恰当使用 JDK 8 以后的新特性的话，产品的代码量可以减少 20%，代码错误可以减少 20%，产品性能可以提高 20%，维护成本可以降低 20%。这些，都是实实在在的收益。

**拥抱 Java 新特性，掌握主动权**

很多技术，你不了解它，它是不会进入你的意识里来的，你也不会知道什么时候该使用它。

**像 Java 语言的设计者一样思考**

Java 的有些新技术，甚至能催生一个新行业。比如 Java 代理的技术，就至少催生了动态监控和入侵检测两大领域的颠覆性变革，并且诞生了数家明星公司和明星产品。

了解一个新特性背后的这些逻辑和实际运用，发掘它未来的潜力，远远比学会这个新特性更重要。

**我们会一起学习哪些新特性？**

在这门课程里，我从 JDK 9 到 JDK 17 的新特性中筛选出了最核心、有用的 18 条特性。我会分三个模块给你讲解一般软件工程师需要经常使用的 Java 语言新技能。

- 第一模块，我会给你介绍一些可以提升编码效率的特性，比如说档案类。

  学完这一部分内容，你能够使用这些新特性，大幅度提高自己的编码效率，降低编码错误。保守估计，你的编码效率可以提高 20%。这也就意味着，如果工作量不变，每一个星期你都可以多休息一天。

- 第二模块，我们会把焦点放在提升代码性能上，比如错误处理的最新成果。

  学完这一部分内容，你将能够使用这些新特性，大幅度提高软件产品的性能，帮助公司提高用户满意度，节省运营费用。保守估计，你编写代码的性能可以提高 20%，甚至更多。

- 第三模块，我会跟你讲讲如何通过新特性降低维护难度，比如模块化和安全性、兼容性问题。

  学完这一部分内容，你将能够编写出更健壮，更容易维护的代码，并且能够知道怎么高效地把旧系统升级到 Java 的新版本。这一部分的目标，就是帮助你把代码的维护成本降低 20% 或者更多。

# 01 | JShell：怎么快速验证简单的小问题？

JShell 这个特性，是在 JDK 9 正式发布的，是 Java 的脚本语言。

**拖后腿的学习效率**

完成 Java 语言的第一个小程序，要学习使用编辑器、使用编译器、使用运行环境。例如下面的这段代码，需要经过编辑、编译、运行、观察这四个步骤。

```java
class HowAreYou {
    public static void main(String[] args) {
        System.out.println("How are you?");
    }
}
```

我们再来看看 bash 脚本语言的处理。

```shell
bash $ echo Hello，World！
Hello, world!
bash $
```

显然，使用 bash 编写的“Hello, world!”要简单得多。

**及时反馈的 JShell**

JShell API 和工具提供了一种在 JShell 状态下交互式评估 Java 编程语言的声明、语句和表达式的方法。为了便于快速调查和编码，语句和表达式不需要出现在方法中，变量和方法也不需要出现在类中。

- 启动 JShell

```shell
$ jshell
| Welcome to JShell -- Version 17
| For an introduction type: /help intro
jshell>
```

- 退出 JShell

```shell
jshell> /exit
| Goodbye
```

- 立即执行的语句

```shell
jshell> System.out.println("Hello, world!");
Hello, world!
jshell>
```

**可覆盖的声明**

JShell 还有一个特别好用的功能。那就是，它支持变量的重复声明。

```shell
jshell> String greeting;
greeting ==> null
|  created variable greeting : String

jshell> String language = "English";
language ==> "English"
|  created variable language : String

jshell> greeting = switch (language) {
  ...> case "English" -> "Hello";
  ...> case "Spanish" -> "Hola";
  ...> case "Chinese" -> "Nihao";
  ...> default -> throw new RuntimeException("Unsupported language");
  ...> };
greeting ==> "Hello"
|  assigned to greeting : String

jshell> System.out.println(greeting);
Hello

jshell>
```

我们可以再次声明只带问候语的变量。

```shell
jshell> String greeting = "Hola";
greeting ==> "Hola"
|  modified variable greeting : String
|    update overwrote variable greeting : String
```

或者，把这个变量声明成一个其他的类型，以便后续的代码使用。

```shell
jshell> Integer greeting;
greeting ==> null
|  replaced variable greeting : Integer
|    update overwrote variable greeting : String
```

**独白的表达式**

JShell 工具可以接受的输入包括 Java 语言的表达式、语句或者声明。

```shell
jshell> 1 + 1
$1 ==> 2
| created scratch variable $1 : int
```

有了独立的表达式，我们就可以直接评估表达式，而不再需要把它附着在一个语句上了。这简化了表达式的评估工作，使得我们可以更快地评估表达式。

```shell
jshell> "Hello, world" == "Hello, world"
$2 ==> true
| created scratch variable $2 : boolean

jshell> "Hello, world" == new String("Hello, world")
$3 ==> false
| created scratch variable $3 : boolean
```

JShell 的设计并不是为了取代 IDE。JShell 在处理简单的小逻辑，验证简单的小问题时，比 IDE 更有效率。如果我们能够在有限的几行代码中，把要验证的问题表达清楚，JShell 就能够快速地给出计算的结果。



