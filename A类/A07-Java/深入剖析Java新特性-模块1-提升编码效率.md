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

# 02 | 文字块：怎么编写所见即所得的字符串？

文字块这个特性，首先在 JDK 13 中以预览版的形式发布。在 JDK 14 中，改进的文字块再次以预览版的形式发布。最后，文字块在 JDK 15 正式发布。

**所见即所得的文字块**

```java
String textBlock = """
    <!DOCTYPE html>
    <html>
        <body>
            <h1>"Hello World!"</h1>
        </body>
    </html>
    """;
System.out.println("Here is the text block:\n" + textBlock);
```

文字块由零个或多个内容字符组成，从开始分隔符开始，到结束分隔符结束。开始分隔符是由三个双引号字符 (""") ，后面跟着的零个或多个空格，以及行结束符组成的序列。结束分隔符是一个由三个双引号字符 (""") 组成的序列。

需要注意的是，开始分隔符必须单独成行。三个双引号字符后面的空格和换行符都属于开始分隔符。所以，一个文字块至少有两行代码。即使是一个空字符，结束分隔符也不能和开始分隔符放在同一行代码里。

```shell
jshell> String s = """""";
| Error:
| illegal text block open delimiter sequence, missing line terminator
| String s = """""";
```

**文字块的编译过程**

上述代码打印结果如下：

```
Here is the text block:
<!DOCTYPE html>
<html>
    <body>
        <h1>"Hello World!"</h1>
    </body>
</html>
```

我们可以看到，为了代码整洁而使用的缩进空格并没有出现在打印的结果里。那文字块是怎么处理缩进空格的呢？

首先，我们从整体上来理解一下文字块的编译期处理这种方式。

```java
package co.ivi.jus.text.modern;

public class TextBlocks {
    public static void main(String[] args) {
        String stringBlock =
                "<!DOCTYPE html>\n" +
                "<html>\n" +
                    " <body>\n" +
                        " <h1>\"Hello World!\"</h1>\n" +
                    " </body>\n" +
                "</html>\n";
        String textBlock = """
                <!DOCTYPE html>
                <html>
                    <body>
                        <h1>"Hello World!"</h1>
                    </body>
                </html>
                """;
        System.out.println(
                "Does the text block equal to the regular string? " +
                stringBlock.equals(textBlock));
        System.out.println(
                "Does the text block refer to the regular string? " +
                (stringBlock == textBlock));
    }
}
```

使用传统方式声明的字符串和使用文字块声明的字符串，它们的内容是一样的，而且指向的是同一个对象。

这就说明了，文字块是在编译期处理的，并且在编译期被转换成了常量字符串，然后就被当作常规的字符串了。所以，如果文字块代表的内容，和传统字符串代表的内容一样，那么这两个常量字符串变量就指向同一内存地址，代表同一个对象。

# 03 | 档案类：怎么精简地表达不可变数据？

档案类这个特性，首先在 JDK 14 中以预览版的形式发布。在 JDK 15 中，改进的档案类再次以预览版的形式发布。最后，档案类在 JDK 16 正式发布。

那么，什么是档案类呢？官方的说法，Java 档案类是用来表示不可变数据的透明载体。这样的表述，有两个关键词，一个是不可变的数据，另一个是透明的载体。

**阅读案例**

下面的这段代码是一个简单的圆形类的定义。这个抽象类的名字是 Circle。

```java
package co.ivi.jus.record.former;

public final class Circle implements Shape {
    private double radius;
    public Circle(double radius) {
        this.radius = radius;
    }
    @Override
    public double getArea() {
        return Math.PI * radius * radius;
    }
    public double getRadius() {
        return radius;
    }
    public void setRadius(double radius) {
        this.radius = radius;
    }
}
```

它有一个私有的变量 radius，用来表示圆的半径。有一个构造方法，用来生成圆形的实例。有一个设置半径的方法 setRadius，一个读取半径的方法 getRadius。还有一个重载的方法 getArea，用来计算圆形的面积。

可是，这样的设计有哪些严重的缺陷呢？

**案例分析**

上面这个例子，最重要的问题，就是它的接口不是多线程安全的。如果在一个多线程的环境中，有些线程调用了 setRadius 方法，有些线程调用 getRadius 方法，这些调用的最终结果是难以预料的。这也就是我们常说的多线程安全问题。

考虑多线程安全的问题，我们增加线程同步。

```java
package co.ivi.jus.record.former;

public final class Circle implements Shape {
    private double radius;
    public Circle(double radius) {
        this.radius = radius;
    }
    @Override
    public synchronized double getArea() {
        return Math.PI * radius * radius;
    }
    public synchronized double getRadius() {
        return radius;
    }
    public synchronized void setRadius(double radius) {
        this.radius = radius;
    }
}
```

可是，线程同步并不是免费的午餐。哪怕最简单的同步，比如上面代码里同步的 getRadius 方法，它的吞吐量损失也有十数倍。

这样的代价就有点大了。最有效的办法，就是在接口设计的时候，争取做到即使不使用线程同步，也能做到多线程安全。也就是说，这个对象是一个只读的对象，不支持修改。

```java
package co.ivi.jus.record.immute;

public final class Circle implements Shape {
    public final double radius;
    public Circle(double radius) {
        this.radius = radius;
    }
    @Override
    public double area() {
        return Math.PI * radius * radius;
    }
}
```

对于只读的圆形类的设计，有两个好处。第一个好处，就是天生的多线程安全。第二个好处，就是简化的代码。

不过，这样的设计似乎破坏了面向对象编程的封装原则。公开半径变量 radius，相当于公开的实现细节。

**声明档案类**

我们前面说过，Java 档案类是用来表示不可变数据的透明载体。那么，怎么使用档案类来表示不可变数据呢？

```java
package co.ivi.jus.record.modern;

public record Circle(double radius) implements Shape {
    @Override
    public double area() {
        return Math.PI * radius * radius;
    }
}
```

对比一下传统的 Circle 类的代码，首先，最常见的 class 关键字不见了，取而代之的是 record 关键字。然后，类标识符 Circle 后面，有用小括号括起来的参数。最后，在大括号里，也就是档案类的实现代码里，变量的声明没有了，构造方法也没有了。

我们已经知道怎么生成一个档案类实例了，但还有一个问题是，我们能读取这个圆形档案类的半径吗？

其实，类标识符声明后面的小括号里的参数，就是等价的不可变变量。在档案类里，这样的不可变变量是私有的变量，我们不可以直接使用它们。但是我们可以通过等价的方法来调用它们。

```java
double radius = circle.radius();
```

变量的标识符就是等价方法的标识符。

在档案类里，方法调用的形式又回来了。调用形式依然保持着良好的封装形式。打破封装原则的顾虑也就不复存在了。

**档案类的其他改进**

下面的这段代码，Circle 的实现使用的是传统类。

```java
package co.ivi.jus.record;

import co.ivi.jus.record.immute.Circle;

public class ImmuteUseCases {
    public static void main(String[] args) {
        Circle c1 = new Circle(10.0);
        Circle c2 = new Circle(10.0);
        System.out.println("Equals? " + c1.equals(c2));
    }
}
```

运行结果告诉我们，两个半径为 10 厘米的圆形的实例，并不是相等的实例。

如果需要比较两个实例是不是相等，我们可以添加 equals、hashCode 和 toString 这三个方法的重载实现。

然而，这三个方法的重载，尤其是 equals 方法和 hashCode 方法的重载实现，一直是代码安全的重灾区。即便是经验丰富的程序员，也可能忘记重载这三个方法；就算没有遗忘，equals 方法和 hashCode 方法也可能没有正确实现，从而带来各种各样的问题。这实在难以让人满意，但是一直以来，我们也没有更好的办法。

我们再来看看使用档案类的代码。下面的这段代码，Circle 的实现使用的是档案类。

```java
package co.ivi.jus.record;

import co.ivi.jus.record.modern.Circle;

public class ModernUseCases {
    public static void main(String[] args) {
        Circle c1 = new Circle(10.0);
        Circle c2 = new Circle(10.0);
        System.out.println("Equals? " + c1.equals(c2));
    }
}
```

这段代码运行的结果告诉我们，两个半径为 10 厘米的圆形的档案类实例，是相等的实例。

这是因为，档案类内置了缺省的 equals 方法、hashCode 方法以及 toString 方法的实现。一般情况下，我们就再也不用担心这三个方法的重载问题了。

**透明的载体**

透明载体的意思，通俗地说，就是档案类承载有缺省实现的方法，这些方法可以直接使用，也可以替换掉。

- 重载构造方法

最常见的替换，是要在构造方法里对档案类声明的变量添加必要的检查。

```java
package co.ivi.jus.record.improved;

public record Circle(double radius) implements Shape {
    public Circle {
        if (radius < 0) {
            throw new IllegalArgumentException(
                "The radius of a circle cannot be negative [" + radius + "]");
        }
    }
    
    @Override
    public double area() {
        return Math.PI * radius * radius;
    }
}
```

> 如果你阅读了上面的代码，应该已经注意到了一点不太常规的形式。构造方法的声明没有参数，也没有给实例变量赋值的语句。
>
> 这并不是说，构造方法就没有参数，或者实例变量不需要赋值。实际上，为了简化代码，Java 编译的时候，已经替我们把这些东西加上去了。

在下面这张表里，我列出了两种构造方法形式上的差异，你可以看看它们的差异。

![image-20220507225848324](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202205072258550.png)

- 重载 equals 方法

还有一类常见的替换，如果缺省的 equals 方法或者 hashCode 方法不能正常工作或者存在安全的问题，就需要替换掉缺省的方法。

比如，如果不可变的变量是一个数组，通过下面的例子，我们来看看它的 equals 方法能不能正常工作。

```shell
jshell> record Password(byte[] password) {}；
| modified record Password

jshell> Password pA = new Password("123456".getBytes());
pA ==> Password[password=[B@2ef1e4fa]

jshell> Password pB = new Password("123456".getBytes());
pB ==> Password[password=[B@b81eda8]

jshell> pA.equals(pB);
$16 ==> false
```

运算的结果显示，这两个实例并不相等。这不是我们期望的结果。其中的原因，就是因为数组这个变量的 equals 方法并不能正常工作。





