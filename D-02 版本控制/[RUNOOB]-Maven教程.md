> 来自：https://www.runoob.com/maven/maven-tutorial.html

# Maven 简介

Maven 翻译为"专家"、"内行"，是 Apache 下的一个纯 Java 开发的开源项目。基于项目对象模型（缩写：POM）概念，Maven利用一个中央信息片断能管理一个项目的构建、报告和文档等步骤。

Maven 是一个项目管理工具，可以对 Java 项目进行构建、依赖管理。Maven 也可被用于构建和管理各种项目，例如 C#，Ruby，Scala 和其他语言编写的项目。Maven 曾是 Jakarta 项目的子项目，现为由 Apache 软件基金会主持的独立 Apache 项目。

**Maven 功能**

Maven 能够帮助开发者完成以下工作：构建，文档生成，报告，依赖，SCMs，发布，分发，邮件列表

**约定配置**

Maven 提倡使用一个共同的标准目录结构，Maven 使用约定优于配置的原则，大家尽可能的遵守这样的目录结构。如下所示：

| 目录                               | 目的                                                         |
| :--------------------------------- | :----------------------------------------------------------- |
| ${basedir}                         | 存放pom.xml和所有的子目录                                    |
| ${basedir}/src/main/java           | 项目的java源代码                                             |
| ${basedir}/src/main/resources      | 项目的资源，比如说property文件，springmvc.xml                |
| ${basedir}/src/test/java           | 项目的测试类，比如说Junit代码                                |
| ${basedir}/src/test/resources      | 测试用的资源                                                 |
| ${basedir}/src/main/webapp/WEB-INF | web应用文件目录，web项目的信息，比如存放web.xml、本地图片、jsp视图页面 |
| ${basedir}/target                  | 打包输出目录                                                 |
| ${basedir}/target/classes          | 编译输出目录                                                 |
| ${basedir}/target/test-classes     | 测试编译输出目录                                             |
| Test.java                          | Maven只会自动运行符合该命名规则的测试类                      |
| ~/.m2/repository                   | Maven默认的本地仓库目录位置                                  |

**Maven 特点**

- **基于模型的构建** − Maven能够将任意数量的项目构建到预定义的输出类型中，如 JAR，WAR 或基于项目元数据的分发，而不需要在大多数情况下执行任何脚本。
- **项目信息的一致性站点** − 使用与构建过程相同的元数据，Maven 能够生成一个网站或PDF，包括您要添加的任何文档，并添加到关于项目开发状态的标准报告中。
- **发布管理和发布单独的输出** − Maven 将不需要额外的配置，就可以与源代码管理系统（如 Subversion 或 Git）集成，并可以基于某个标签管理项目的发布。它也可以将其发布到分发位置供其他项目使用。Maven 能够发布单独的输出，如 JAR，包含其他依赖和文档的归档，或者作为源代码发布。
- **向后兼容性** − 您可以很轻松的从旧版本 Maven 的多个模块移植到 Maven 3 中。
- **并行构建** − 编译的速度能普遍提高20 - 50 %。
- **更好的错误报告** − Maven 改进了错误报告，它为您提供了 Maven wiki 页面的链接，您可以点击链接查看错误的完整描述。

**Maven 的 Snapshot 版本与 Release 版本**

1、Snapshot 版本代表不稳定、尚处于开发中的版本。

2、Release 版本则代表稳定的版本。

3、什么情况下该用 SNAPSHOT?

协同开发时，如果 A 依赖构件 B，由于 B 会更新，B 应该使用 SNAPSHOT 来标识自己。这种做法的必要性可以反证如下：

- a. 如果 B 不用 SNAPSHOT，而是每次更新后都使用一个稳定的版本，那版本号就会升得太快，每天一升甚至每个小时一升，这就是对版本号的滥用。
- b.如果 B 不用 SNAPSHOT, 但一直使用一个单一的 Release 版本号，那当 B 更新后，A 可能并不会接受到更新。因为 A 所使用的 repository 一般不会频繁更新 release 版本的缓存（即本地 repository)，所以B以不换版本号的方式更新后，A在拿B时发现本地已有这个版本，就不会去远程Repository下载最新的 B

4、 不用 Release 版本，在所有地方都用 SNAPSHOT 版本行不行？     

不行。正式环境中不得使用 snapshot 版本的库。 比如说，今天你依赖某个 snapshot 版本的第三方库成功构建了自己的应用，明天再构建时可能就会失败，因为今晚第三方可能已经更新了它的 snapshot 库。你再次构建时，Maven 会去远程 repository 下载 snapshot 的最新版本，你构建时用的库就是新的 jar 文件了，这时正确性就很难保证了。

# Maven POM

POM( Project Object Model，项目对象模型 ) 是 Maven 工程的基本工作单元，是一个XML文件，包含了项目的基本信息，用于描述项目如何构建，声明项目依赖，等等。

执行任务或目标时，Maven 会在当前目录中查找 POM。它读取 POM，获取所需的配置信息，然后执行目标。

POM 中可以指定以下配置：

- 项目依赖
- 插件
- 执行目标
- 项目构建 profile
- 项目版本
- 项目开发者列表
- 相关邮件列表信息

在创建 POM 之前，我们首先需要描述项目组 (groupId), 项目的唯一ID。

```xml
<project xmlns = "http://maven.apache.org/POM/4.0.0"
    xmlns:xsi = "http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation = "http://maven.apache.org/POM/4.0.0
    http://maven.apache.org/xsd/maven-4.0.0.xsd">
    
    <!-- 模型版本 -->
    <modelVersion>4.0.0</modelVersion>
    <!-- 公司或者组织的唯一标志，并且配置时生成的路径也是由此生成， 如com.companyname.project-group，maven会将该项目打成的jar包放本地路径：/com/companyname/project-group -->
    <groupId>com.companyname.project-group</groupId>
    <!-- 项目的唯一ID，一个groupId下面可能多个项目，就是靠artifactId来区分的 -->
    <artifactId>project</artifactId>
    <!-- 版本号 -->
    <version>1.0</version>
</project>
```

所有 POM 文件都需要 project 元素和三个必需字段：groupId，artifactId，version。

| 节点         | 描述                                                         |
| :----------- | :----------------------------------------------------------- |
| project      | 工程的根标签。                                               |
| modelVersion | 模型版本需要设置为 4.0。                                     |
| groupId      | 这是工程组的标识。它在一个组织或者项目中通常是唯一的。例如，一个银行组织 com.companyname.project-group 拥有所有的和银行相关的项目。 |
| artifactId   | 这是工程的标识。它通常是工程的名称。例如，消费者银行。groupId 和 artifactId 一起定义了 artifact 在仓库中的位置。 |
| version      | 这是工程的版本号。在 artifact 的仓库中，它用来区分不同的版本。例如：com.company.bank:consumer-banking:1.0 <br />com.company.bank:consumer-banking:1.1 |

**父（Super）POM**

父（Super）POM是 Maven 默认的 POM。所有的 POM 都继承自一个父 POM（无论是否显式定义了这个父 POM）。父 POM 包含了一些可以被继承的默认设置。因此，当 Maven 发现需要下载 POM 中的 依赖时，它会到 Super POM 中配置的默认仓库 http://repo1.maven.org/maven2 去下载。

Maven 使用 effective pom（Super pom 加上工程自己的配置）来执行相关的目标，它帮助开发者在 pom.xml 中做尽可能少的配置，当然这些配置可以被重写。

使用以下命令来查看 Super POM 默认配置：

```
mvn help:effective-pom
```

接下来我们创建目录 MVN/project，在该目录下创建 pom.xml，内容如下：

```xml
<project xmlns = "http://maven.apache.org/POM/4.0.0"
    xmlns:xsi = "http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation = "http://maven.apache.org/POM/4.0.0
    http://maven.apache.org/xsd/maven-4.0.0.xsd">
 
    <!-- 模型版本 -->
    <modelVersion>4.0.0</modelVersion>
    <!-- 公司或者组织的唯一标志，并且配置时生成的路径也是由此生成， 如com.companyname.project-group，maven会将该项目打成的jar包放本地路径：/com/companyname/project-group -->
    <groupId>com.companyname.project-group</groupId>
 
    <!-- 项目的唯一ID，一个groupId下面可能多个项目，就是靠artifactId来区分的 -->
    <artifactId>project</artifactId>
 
    <!-- 版本号 -->
    <version>1.0</version>
</project>
```

在命令控制台，进入 MVN/project 目录，执行以下命令：

```
C:\MVN\project>mvn help:effective-pom
```

Maven 将会开始处理并显示 effective-pom。

```
[INFO] Scanning for projects...
Downloading: https://repo.maven.apache.org/maven2/org/apache/maven/plugins/maven-clean-plugin/2.5/maven-clean-plugin-2.5.pom
...
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time: 01:36 min
[INFO] Finished at: 2018-09-05T11:31:28+08:00
[INFO] Final Memory: 15M/149M
[INFO] ------------------------------------------------------------------------
```

Effective POM 的结果就像在控制台中显示的一样，经过继承、插值之后，使配置生效。

# Maven 构建生命周期

Maven 构建生命周期定义了一个项目构建跟发布的过程。一个典型的 Maven 构建（build）生命周期是由以下几个阶段的序列组成的：

| 阶段          | 处理     | 描述                                                     |
| :------------ | :------- | :------------------------------------------------------- |
| 验证 validate | 验证项目 | 验证项目是否正确且所有必须信息是可用的                   |
| 编译 compile  | 执行编译 | 源代码编译在此阶段完成                                   |
| 测试 Test     | 测试     | 使用适当的单元测试框架（例如JUnit）运行测试。            |
| 包装 package  | 打包     | 创建JAR/WAR包如在 pom.xml 中定义提及的包                 |
| 检查 verify   | 检查     | 对集成测试的结果进行检查，以保证质量达标                 |
| 安装 install  | 安装     | 安装打包的项目到本地仓库，以供其他项目使用               |
| 部署 deploy   | 部署     | 拷贝最终的工程包到远程仓库中，以共享给其他开发人员和工程 |

为了完成 default 生命周期，这些阶段（包括其他未在上面罗列的生命周期阶段）将被按顺序地执行。

Maven 有以下三个标准的生命周期：

- **clean**：项目清理的处理
- **default(或 build)**：项目部署的处理
- **site**：项目站点文档创建的处理

**Clean 生命周期**

当我们执行 mvn post-clean 命令时，Maven 调用 clean 生命周期，它包含以下阶段：

- pre-clean：执行一些需要在clean之前完成的工作
- clean：移除所有上一次构建生成的文件
- post-clean：执行一些需要在clean之后立刻完成的工作

mvn clean 中的 clean 就是上面的 clean，在一个生命周期中，运行某个阶段的时候，它之前的所有阶段都会被运行，也就是说，如果执行 mvn clean 将运行以下两个生命周期阶段：

```
pre-clean, clean
```

如果我们运行 mvn post-clean ，则运行以下三个生命周期阶段：

```
pre-clean, clean, post-clean
```

**Default (Build) 生命周期**

这是 Maven 的主要生命周期，被用于构建应用，包括下面的 23 个阶段：

| 生命周期阶段                                | 描述                                                         |
| :------------------------------------------ | :----------------------------------------------------------- |
| validate（校验）                            | 校验项目是否正确并且所有必要的信息可以完成项目的构建过程。   |
| initialize（初始化）                        | 初始化构建状态，比如设置属性值。                             |
| generate-sources（生成源代码）              | 生成包含在编译阶段中的任何源代码。                           |
| process-sources（处理源代码）               | 处理源代码，比如说，过滤任意值。                             |
| generate-resources（生成资源文件）          | 生成将会包含在项目包中的资源文件。                           |
| process-resources （处理资源文件）          | 复制和处理资源到目标目录，为打包阶段最好准备。               |
| compile（编译）                             | 编译项目的源代码。                                           |
| process-classes（处理类文件）               | 处理编译生成的文件，比如说对Java class文件做字节码改善优化。 |
| generate-test-sources（生成测试源代码）     | 生成包含在编译阶段中的任何测试源代码。                       |
| process-test-sources（处理测试源代码）      | 处理测试源代码，比如说，过滤任意值。                         |
| generate-test-resources（生成测试资源文件） | 为测试创建资源文件。                                         |
| process-test-resources（处理测试资源文件）  | 复制和处理测试资源到目标目录。                               |
| test-compile（编译测试源码）                | 编译测试源代码到测试目标目录.                                |
| process-test-classes（处理测试类文件）      | 处理测试源码编译生成的文件。                                 |
| test（测试）                                | 使用合适的单元测试框架运行测试（Juint是其中之一）。          |
| prepare-package（准备打包）                 | 在实际打包之前，执行任何的必要的操作为打包做准备。           |
| package（打包）                             | 将编译后的代码打包成可分发格式的文件，比如JAR、WAR或者EAR文件。 |
| pre-integration-test（集成测试前）          | 在执行集成测试前进行必要的动作。比如说，搭建需要的环境。     |
| integration-test（集成测试）                | 处理和部署项目到可以运行集成测试环境中。                     |
| post-integration-test（集成测试后）         | 在执行集成测试完成后进行必要的动作。比如说，清理集成测试环境。 |
| verify （验证）                             | 运行任意的检查来验证项目包有效且达到质量标准。               |
| install（安装）                             | 安装项目包到本地仓库，这样项目包可以用作其他本地项目的依赖。 |
| deploy（部署）                              | 将最终的项目包复制到远程仓库中与其他开发者和项目共享。       |

有一些与 Maven 生命周期相关的重要概念需要说明：

当一个阶段通过 Maven 命令调用时，例如 mvn compile，只有该阶段之前以及包括该阶段在内的所有阶段会被执行。不同的 maven 目标将根据打包的类型（JAR / WAR / EAR），被绑定到不同的 Maven 生命周期阶段。

在开发环境中，使用下面的命令去构建、安装工程到本地仓库

```
mvn install
```

这个命令在执行 install 阶段前，按顺序执行了 default 生命周期的阶段 （validate，compile，package，等等），我们只需要调用最后一个阶段，如这里是 install。

在构建环境中，使用下面的调用来纯净地构建和部署项目到共享仓库中

```
mvn clean deploy
```

这行命令也可以用于多模块的情况下，即包含多个子项目的项目，Maven 会在每一个子项目执行 clean 命令，然后再执行 deploy 命令。

**Site 生命周期**

Maven Site 插件一般用来创建新的报告文档、部署站点等。

- pre-site：执行一些需要在生成站点文档之前完成的工作
- site：生成项目的站点文档
- post-site： 执行一些需要在生成站点文档之后完成的工作，并且为部署做准备
- site-deploy：将生成的站点文档部署到特定的服务器上

# Maven 构建配置文件


