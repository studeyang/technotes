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

- 第一模块，我会给你介绍一些可以==提升编码效率==的特性，比如说档案类。

  学完这一部分内容，你能够使用这些新特性，大幅度提高自己的编码效率，降低编码错误。保守估计，你的编码效率可以提高 20%。这也就意味着，如果工作量不变，每一个星期你都可以多休息一天。

- 第二模块，我们会把焦点放在==提升代码性能==上，比如错误处理的最新成果。

  学完这一部分内容，你将能够使用这些新特性，大幅度提高软件产品的性能，帮助公司提高用户满意度，节省运营费用。保守估计，你编写代码的性能可以提高 20%，甚至更多。

- 第三模块，我会跟你讲讲如何通过新特性==降低维护难度==，比如模块化和安全性、兼容性问题。


学完这一部分内容，你将能够编写出更健壮，更容易维护的代码，并且能够知道怎么高效地把旧系统升级到 Java 的新版本。这一部分的目标，就是帮助你把代码的维护成本降低 20% 或者更多。

# ==提升编码效率==

# 01 | JShell（9）：怎么快速验证简单的小问题？

JShell 这个特性，是在 JDK 9 正式发布的，是 Java 的脚本语言。

**拖后腿的学习效率**

完成 Java 语言的第一个小程序，要学习使用编辑器、使用编译器、使用运行环境。例如下面的这段代码，需要经过编辑、编译、运行、观察这四个步骤。

```java
class HowAreYou {
    public static void main(String[] args) {
        System.out.println("Hello, world!");
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

- JShell 的命令

```
jshell> /help
| Type a Java language expression, statement, or declaration.
| Or type one of the following commands:
| /list [<name or id>|-all|-start]
| list the source you have typed
... snipped ...
| /help [<command>|<subject>]
| get information about using the jshell tool
... snipped ...
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

**思考题**

在前面的讨论里，我们使用了一个例子，来说明 Java 处理字符串常量的方式。

```shell
jshell> "Hello, world" == "Hello, world"
$2 ==> true
| created scratch variable $2 : boolean
```

你有没有办法，让这个例子更容易理解？使用多个 JShell 片段，是不是更好理解？

可以定义 s1="Hello, world", s2="Hello, world", 再判断 s1==s2。

# 02 | 文字块（15）：怎么编写所见即所得的字符串？

文字块这个特性，首先在 JDK 13 中以预览版的形式发布。在 JDK 14 中，改进的文字块再次以预览版的形式发布。最后，文字块在 JDK 15 正式发布。

**阅读案例**

下面的例子中，我们要构造一个简单的表示"Hello，World！"的 HTML 字符串。

```java
String stringBlock =
        "<!DOCTYPE html>\n" +
        "<html>\n" +
        " <body>\n" +
        " <h1>\"Hello World!\"</h1>\n" +
        " </body>\n" +
        "</html>\n";
```

这样的字符串不好写，不好看，也不好读。并且，这样的实际例子还比较多，比如 HTML, SQL, XML, JSON, HTTP，随便就可以列一大堆。

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

**思考题**

在有些场景里，要想完全地实现“所见即所得”，仅仅使用文字块，可能还是要费一点周折的。比如我们看到的诗，有的时候是页面居中对齐的。比如下面的这首小诗，采用的格式就是居中对齐。

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/202305172225375.png)

居中对齐这种形式，在 HTML 或者文档的世界里，很容易处理，设置一下格式就可以了。如果是用 Java 语言，该怎么处理好这首小诗的居中对齐问题？

可以这样写：

```java
String s = """
\s           No man is an island,
\s             Entire of itself,
\s    Every man is a picec of the continent,
\s            A part of the main.
""";
```

# 03 | record（16）：怎么精简地表达不可变数据？

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

这个圆形类之所以典型，是因为它交代了面向对象设计的关键思想，包括面向对象编程的三大支柱性原则：封装、继承和多态。

这个圆形类有哪些严重的缺陷呢？

**案例分析**

上面这个例子，最重要的问题，就是它的接口不是多线程安全的。如果在一个多线程的环境中，有些线程调用了 setRadius 方法，有些线程调用 getRadius 方法，这些调用的最终结果是难以预料的。这也就是我们常说的多线程安全问题。

解决多线程安全的问题，通常做法是在方法上增加线程同步，但这样它的吞吐量损失也有十数倍。

这样的代价就有点大了。最有效的办法，就是在接口设计的时候，争取做到即使不使用线程同步，也能做到多线程安全。也就是说，==这个对象是一个只读的对象，不支持修改。==

下面的代码，是一个修改过的 Circle 类实现。在这个实现里，圆形的对象一旦实例化，就不能再修改它的半径了。相应地，我们删除了设置半径的方法。也就是说，这个对象是一个只读的对象，不支持修改。通常地，我们称这样的对象为不可变对象。

```java
package co.ivi.jus.record.immute;

public final class Circle implements Shape {
    private final double radius; // 属性设为final
    public Circle(double radius) {
        this.radius = radius;
    }
    @Override
    public double area() {
        return Math.PI * radius * radius;
    }
    public double getRadius() {
        return radius;
    }
}
```

对于只读的圆形类的设计，好处就是天生的多线程安全。

还有没有进一步简化的空间呢？

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

使用构造方法的形式来生成 Circle 档案类实例。

```java
Circle circle = new Circle(10.0);
```

读取这个圆形档案类的半径，变量的标识符就是等价方法的标识符。

```java
double radius = circle.radius();
```

需要注意的是，由于档案类表示的是不可变数据，除了构造方法之外，并没有给不可变变量赋值的方法。

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

**不可变的数据**

如果一个 Java 类一旦实例化就不能再修改，那么用它表述的数据就是不可变数据。Java 档案类就是表述不可变数据的。为了强化“不可变”这一原则，避免面向对象设计的陷阱，Java 档案类还做了以下的限制：

1. Java 档案类不支持扩展子句，用户不能定制它的父类。隐含的，它的父类是 java.lang.Record。父类不能定制，也就意味着我们不能通过修改父类来影响 Java 档案的行为。
2. Java 档案类是个终极（final）类，不支持子类，也不能是抽象类。没有子类，也就意味着我们不能通过修改子类来改变 Java 档案的行为。
3. Java 档案类声明的变量是不可变的变量。这就是我们前面反复强调的，一旦实例化就不能再修改的关键所在。
4. Java 档案类不能声明本地（native）方法。如果允许了本地方法，也就意味着打开了修改不可变变量的后门。

常地，我们把 Java 档案类看成是一种特殊形式的 Java 类。除了上述的限制，Java 档案类和普通类的用法是一样的。

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

- 不推荐重载 toString 方法

为了更个性化的显示，我们有时候也需要重载 toString 方法。但是，我们通常不建议重载不可变数据的读取方法。因为，这样的重载往往意味着需要变更缺省的不可变数值，从而打破实例的状态，进而造成许多无法预料的、让人费解的后果。

比如说，我们设想定义一个数，如果是负值的话，我们希望读取的是它的相反数。下面的例子，就是一个味道很坏的示范。

```shell
jshell> record Number(int x) {
...> public int x() {
...> return x > 0 ? x : (-1) * x;
...> }
...> }
| created record Number

jshell> Number n = new Number(-1);
n ==> Number[x=-1]

jshell> n.x();
$9 ==> 1

jshell> Number m = new Number(n.x());
m ==> Number[x=1]

jshell> m.equals(n);
$11 ==> false
```

这让代码变得难以理解，很容易出错。更严重的问题是，这样的重载不再能够支持实例的拷贝。比如说，我们把实例 n 拷贝到另一个实例 m。这两个实例按照道理来说应该相等。而由于重载了读取的方法，实际的结果，这两个实例是不相等的。这样的结果，也可能会使代码容易出错，而且难以调试。

**思考题**

我们都知道，社会保障号是高度敏感的信息，不能被泄漏，也不能被盗取。可以用字节数组用来表示社会保障号。你来想一想，equals(), hashCode(), toString() 有哪些方法需要重载？为什么？代码看起来是什么样子的？有难以克服的困难吗？

```java
record SocialSecurityNumber(byte[] ssn) {
    // Here is your code.
    // 字节数据判等，需要重载：equals(), hashCode(), 
    // 由于不能被泄漏，toString() 就不用重载了
}
```

# 04 | sealed（17）：怎么刹住失控的扩展性？

封闭类这个特性，首先在 JDK 15 中以预览版的形式发布。在 JDK 16 中，改进的封闭类再次以预览版的形式发布。最后，封闭类在 JDK 17 正式发布。

**阅读案例**

下面的这段代码，是形状类的抽象，名字是 Shape，它有一个抽象方法 area()，用来计算形状的面积。它还有一个公开的属性 id，用来标识这个形状的对象。

```java
public abstract class Shape {
    public final String id;
    public Shape(String id) {
        this.id = id;
    }
    public abstract double area();
}
```

正方形是一个形状。

```java
public class Square extends Shape {
    public final double side;
    public Square(String id, double side) {
        super(id);
        this.side = side;
    }
    @Override
    public double area() {
        return side * side;
    }
}
```

那么，到底怎么判断一个形状是不是正方形呢？如果只有上面一个形状，答案似乎很简单。

```java
static boolean isSquare(Shape shape) {
    return (shape instanceof Square);
}
```

**案例分析**

上面的这个例子，判断的只是“一个形状的对象是不是一个正方形的实例”。但实际上，一个长方形的每一个边的长度都是一样的，其实它就是一个正方形，但是表示它的类是长方形的类，而不是正方形类。所以，上面的这段代码还是有缺陷的，并不总是能够正确判断一个形状是不是正方形。

```java
public class Rectangle extends Shape {
    public final double length;
    public final double width;
    public Rectangle(String id, double length, double width) {
        super(id);
        this.length = length;
        this.width = width;
    }
    @Override
    public double area() {
        return length * width;
    }
}
```

对于“怎么判断一个形状是不是正方形”这个问题，我想应该有进一步的判断。

```java
public static boolean isSquare(Shape shape) {
    if (shape instanceof Rectangle rect) {
        return (rect.length == rect.width);
    }
    return (shape instanceof Square);
}
```

但其实，这个问题我们还没有搞定。因为正方形也是一个特殊的菱形，如果一个对象是一个菱形类的实例，上面的代码就有缺陷。

更令人窘迫的是，正方形还是一个特殊的梯形，还是一个特殊的多边形。随着我们学习一步一步的深入，我们知道还有很多形状的特殊形式是正方形，而且我们并不知道我们知识范围外的那些形状，当然更不能提穷举它们了。

无限制的扩展性，是问题的根源。

**怎么限制住扩展性？**

JDK 17 之前的 Java 语言，限制住可扩展性只有两个方法，使用私有类或者 final 修饰符。显而易见，私有类不是公开接口，只能内部使用；而 final 修饰符彻底放弃了可扩展性。要么全开放，要么全封闭，可扩展性只能在可能性的两个极端游走。

JDK 17 之后，有了第三种方法。这个办法，就是使用 Java 的 sealed 关键字。

**怎么声明封闭类**

```java
public abstract sealed class Shape permits Circle, Square {
    public final String id;
    public Shape(String id) {
        this.id = id;
    }
    public abstract double area();
}
```

这里定义的形状这个类，只允许有圆形和正方形两个子类。

如果子类和封闭类在同一个源代码文件里，封闭类可以不使用 permits 语句。

```java
public abstract sealed class Shape {
    public final String id;
    public Shape(String id) {
        this.id = id;
    }
    public abstract double area();
    public static final class Circle extends Shape {
        // snipped
    }
    public static final class Square extends Shape {
        // snipped
    }
}
```

**怎么声明许可类**

许可类必须声明是否继续保持封闭：

- 许可类可以声明为终极类（final），从而关闭扩展性；
- 许可类可以声明为封闭类（sealed），从而延续受限制的扩展性；
- 许可类可以声明为解封类（non-sealed）, 从而支持不受限制的扩展性。

**思考题**

文中解决“怎么判断一个形状是不是正方形”这个问题的代码是版本 1.0。假设在版本 2.0 里，需要增加另一个许可类，用来支持长方形（Rectangle）。那么：

1. 封闭类的代码该怎么改动，才能支持长方形？
2. “判断一个形状是不是正方形”的代码该怎么改动，才能适应封闭类的改变？
3. 增加一个许可类，会有兼容性的影响吗？比如说，使用版本 1.0 来判断一个形状是不是正方形的代码还能使用吗？

```java
//封闭类支持长方形
public abstract sealed class Shape permits Circle, Square, Rectangle {
    public final String id;
    public Shape(String id) {
        this.id = id;
    }
    public abstract double area();
}
```

```java
//判断一个形状是不是正方形
public static boolean isSquare(Shape shape) {
    if (shape instanceof Rectangle rect) {
        return (rect.length == rect.width);
    }
    return (shape instanceof Square);
}
```

第三个问题，不能使用。

# 05 | 类型匹配（16）：怎么切除臃肿的强制转换？

**阅读案例**

我们要设计一个方法，来判断一个形状是不是正方形。

```java
static boolean isSquare(Shape shape) {
    if (shape instanceof Rectangle) {
        Rectangle rect = (Rectangle) shape;
        return (rect.length == rect.width);
    }
    return (shape instanceof Square);
}
```

我们可以用什么方法改进这个模式，提高生产效率呢？ 这个问题的答案就是类型匹配。

**类型匹配**

我们先来看看使用了类型匹配的代码的样子。下面的例子，就是使用类型匹配的一段代码。

```java
if (shape instanceof Rectangle rect) {
    return (rect.length == rect.width);
}
```

**匹配变量的作用域**

第一段代码，我们看看最常规的使用。我们可以在确认类型匹配的条件语句之内使用匹配变量。这个条件语句之外，不是匹配变量的作用域。

```java
public static boolean isSquareImplA(Shape shape) {
    if (shape instanceof Rectangle rect) {
        // rect is in scope
        return rect.length() == rect.width();
    }
    // rect is not in scope here
    return shape instanceof Square;
}
```

第二段代码，我们看看有点意外的使用。我们可以在确认类型不匹配的条件语句之后使用匹配变量。这个条件语句之内，不是匹配变量的作用域。

```java
public static boolean isSquareImplB(Shape shape) {
    if (!(shape instanceof Rectangle rect)) {
        // rect is not in scope here
        return shape instanceof Square;
    }
    // rect is in scope
    return rect.length() == rect.width();
}
```

第三段代码，我们看看紧凑的方式。这一段代码的逻辑，和第一段代码一样，我们只是换成了一种更紧凑的表示方法。

```java
public static boolean isSquareImplC(Shape shape) {
    return shape instanceof Square || // rect is not in scope here
        (shape instanceof Rectangle rect &&
         rect.length() == rect.width()); // rect is in scope here
}
```

第四段代码，我们看看逻辑或运算。它类似于第三段代码，只是我们把逻辑与运算符替换成了逻辑或运算符。这时候的逻辑，就变成了“类型匹配或者匹配变量满足某一个条件”。逻辑或运算符也是从左到右计算。

不过和逻辑与运算符不同的是，一般来说，只有第一个运算不成立，也就是说类型不匹配时，才能进行下一步的运算。下一步的运算，匹配变量并没有被赋值，我们不能够在这一部分使用匹配变量。所以，这一段代码并不能通过编译器的审查。

```java
public static boolean isSquareImplD(Shape shape) {
    return shape instanceof Square || // rect is not in scope here
        (shape instanceof Rectangle rect ||
         rect.length() == rect.width()); // rect is not in scope here
}
```

第五段代码，我们看看位与运算。这段代码和第三段代码类似，只是我们把逻辑与运算符（&&）替换成了位与运算符（&）。不过（&）可没有短路的特性，所以，下面这一段代码，也不能通过编译器的审查。

```java
public static boolean isSquareImplE(Shape shape) {
    return shape instanceof Square | // rect is not in scope here
        (shape instanceof Rectangle rect &
         rect.length() == rect.width()); // rect is in scope here
}
```

第六段代码，我们把匹配变量的作用域的影响延展一下，看看它对影子变量（Shadowed Variable）的影响。

```java
public final class Shadow {
    private static final Rectangle rect = null;
    public static boolean isSquare(Shape shape) {
        if (shape instanceof Rectangle rect) {
            // Field rect is shadowed, local rect is in scope
            System.out.println("This should be the local rect: " + rect);
            return rect.length() == rect.width();
        }
        // Field rect is in scope, local rect is not in scope here
        System.out.println("This should be the field rect: " + rect);
        return shape instanceof Shape.Square;
    }
}
```

第七段代码，我们还是来看一看影子变量。只不过，这一次，我们使用类似于第二段代码的代码组织方式，来表述类型匹配部分的逻辑。

```java
public final class Shadow {
    private static final Rectangle rect = null;
    public static boolean isSquare(Shape shape) {
        if (!(shape instanceof Rectangle rect)) {
            // Field rect is in scope, local rect is not in scope here
            System.out.println("This should be the field rect: " + rect);
            return shape instanceof Shape.Square;
        }
        // Field rect is shadowed, local rect is in scope
        System.out.println("This should be the local rect: " + rect);
        return rect.length() == rect.width();
    }
}
```

我们把这些代码放在一起，分析一下它们的特点。

第四段和第五段代码，不能通过编译器的审查，所以我们不能使用这两种编码方式。

第二段和第七段代码，匹配变量的作用域，远离了类型匹配语句。这种距离上的疏远，无论在视觉上还是心理上，都不是很舒适的选择。不舒适，就给错误留下了空间，不容易编码，也不容易排错。这种代码逻辑和语法上都没有问题，但是不太容易阅读。

第一段和第六段代码，匹配变量的作用域，紧跟着类型匹配语句。这是我们感觉舒适的代码布局，也是最安全的代码布局，不容易出错，也容易阅读。

第三段代码，它的编排方式不太容易阅读，阅读者需要认真拆解每一个条件，才能确认逻辑是正确的。相对于第一段和第六段代码，第三段代码的组织方式，是一个次优的选择。

# 06 | switch表达式（14）：怎么简化多情景操作？

**阅读案例**

生活中，我们熟悉这样的顺口溜，“一三五七八十腊，三十一天永不差，四六九冬三十整，平年二月二十八，闰年二月把一加”。

下面的这段代码，就是按照这个顺口溜的逻辑来计算了一下，今天所在的这个月，一共有多少天。

```java
class DaysInMonth {
    public static void main(String[] args) {
        Calendar today = Calendar.getInstance();
        int month = today.get(Calendar.MONTH);
        int year = today.get(Calendar.YEAR);
        int daysInMonth;
        switch (month) {
            case Calendar.JANUARY:
            case Calendar.MARCH:
            case Calendar.MAY:
            case Calendar.JULY:
            case Calendar.AUGUST:
            case Calendar.OCTOBER:
            case Calendar.DECEMBER:
                daysInMonth = 31;
                break;
            case Calendar.APRIL:
            case Calendar.JUNE:
            case Calendar.SEPTEMBER:
            case Calendar.NOVEMBER:
                daysInMonth = 30;
                break;
            case Calendar.FEBRUARY:
                if (((year % 4 == 0) && !(year % 100 == 0))
                    || (year % 400 == 0)) {
                    daysInMonth = 29;
                } else {
                    daysInMonth = 28;
                }
                break;
            default:
                throw new RuntimeException(
                    "Calendar in JDK does not work");
        }
        System.out.println("There are " + daysInMonth + " days in this month.");
    }
}
```

这样的 switch 语句至少有两个容易犯错误的地方。

第一个容易犯错的地方，就是在 break 关键字的使用上。上面的代码里，如果多使用一个 break 关键字，代码的逻辑就会发生变化；同样的，少使用一个 break 关键字也会出现问题。

第二个容易犯错的地方，是反复出现的赋值语句。

**switch 表达式**

```java
class DaysInMonth {
    public static void main(String[] args) {
        Calendar today = Calendar.getInstance();
        int month = today.get(Calendar.MONTH);
        int year = today.get(Calendar.YEAR);
        int daysInMonth = switch (month) {
            case Calendar.JANUARY,
                Calendar.MARCH,
                Calendar.MAY,
                Calendar.JULY,
                Calendar.AUGUST,
                Calendar.OCTOBER,
                Calendar.DECEMBER -> 31;
            case Calendar.APRIL,
                Calendar.JUNE,
                Calendar.SEPTEMBER,
                Calendar.NOVEMBER -> 30;
            case Calendar.FEBRUARY -> {
                if (((year % 4 == 0) && !(year % 100 == 0))
                    || (year % 400 == 0)) {
                    yield 29;
                } else {
                    yield 28;
                }
            }
            default -> throw new RuntimeException(
                "Calendar in JDK does not work");
        };
        System.out.println(
            "There are " + daysInMonth + " days in this month.");
    }
}
```

大多数情况下，switch 表达式箭头标识符的右侧是一个数值或者是一个表达式。 如果需要一个或者多个语句，我们就要使用代码块的形式。这时候，我们就需要引入一个新的 yield 语句来产生一个值，这个值就成为这个封闭代码块代表的数值。

为了便于理解，我们可以把 yield 语句产生的值看成是 switch 表达式的返回值。所以，yield 只能用在 switch 表达式里，而不能用在 switch 语句里。

```java
case Calendar.FEBRUARY -> {
    if (((year % 4 == 0) && !(year % 100 == 0))
        || (year % 400 == 0)) {
        yield 29;
    } else {
        yield 28;
    }
}
```

如果没有最后的 default 情景分支，编译器就会报错。这是一个影响深远的改进，它会使得 switch 表达式的代码更加健壮，大幅度降低维护成本。

# 07 | switch匹配：能不能适配不同的类型？



# ==提升代码性能==





# ==降低维护难度==

















