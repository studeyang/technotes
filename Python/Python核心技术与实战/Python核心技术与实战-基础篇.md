# 开篇词 | 从工程的角度深入理解Python

专栏的所有内容都基于 Python 最新的 3.7 版本，其中有大量独家解读、案例，以及不少我阅读源码后的发现和体会。

专栏主要分为四大版块。

**1. Python 基础篇**

- 列表和元组存储结构的差异是怎样的？它们性能的详细比较又如何？
- 字符串相加的时间复杂度，你真的清楚吗？

**2. Python 进阶篇**

比如装饰器、并发编程等等。

**3. Python 规范篇**

这部分着重于教你把程序写得更加规范、更加稳定。

**4. Python 实战篇**

这部分，我会通过量化交易系统这个具体的实战案例，带你综合运用前面所学的 Python 知识。

# 01 | 如何逐步突破，成为Python高手？

对于一门新语言，Facebook 工程师基本上一两周后，日常编程便毫无压力了。他们遵循的方法就是“从工程的角度去学习 Python”。

**不同语言，需融会贯通**

比如，在学习 Python 的条件与循环语句时，多回忆一下其他语言的语法是怎样的。

根据我多年的学习工作经验，我把编程语言的学习重点，总结成了下面这三步，无论你是否有其他语言的基础，都可以对照来做，稳步进阶。

**第一步：大厦之基，勤加练习**

在掌握必要的基础时，就得多上手操作了。

**第二步：代码规范，必不可少**

如果有不遵守代码规范的例子，哪怕只是一个函数或是一个变量的命名，我们都会要求原作者加以修改，严格规范才能保证代码库的代码质量。

**第三步：开发经验，质的突破**

想要真正熟练地掌握 Python 或者是任何一门其他的编程语言，拥有大中型产品的开发经验是必不可少的。因为实战经验才能让你站得更高，望得更远。

> 第1篇，说了很多废话。

# 02 | Jupyter Notebook为什么是现代Python的必学技术？

为什么 Python 如此适合数学统计和机器学习呢？作为“老司机”的我可以肯定地告诉你，Jupyter Notebook （https://jupyter.org/）功不可没。

**什么是 Jupyter Notebook？**

按照 Jupyter 创始人 Fernando Pérez 的说法，他最初的梦想是做一个综合 Ju （Julia）、Py （Python）和 R 三种科学运算语言的计算工具平台，所以将其命名为 Ju-Py-te-R。发展到现在，Jupyter 已经成为一个几乎支持所有语言，能够把软件代码、计算输出、解释文档、多媒体资源整合在一起的多功能科学运算平台。

**Jupyter Notebook 的影响力**

从 2017 年开始，已有大量的北美顶尖计算机课程，开始完全使用 Jupyter Notebook 作为工具。比如李飞飞的 CS231N《计算机视觉与神经网络》课程，在 16 年时作业还是命令行 Python 的形式，但是 17 年的作业就全部在 Jupyter Notebook 上完成了。再如 UC Berkeley 的《数据科学基础》课程，从 17 年起，所有作业也全部用 Jupyter Notebook 完成。

而 Jupyter Notebook 在工业界的影响力更甚。在 Facebook，虽然大规模的后台开发仍然借助于功能齐全的 IDE，但是几乎所有的中小型程序，比如内部的一些线下分析软件，机器学习模块的训练都是借助于 Jupyter Notebook 完成的。据我了解，在别的硅谷一线大厂，例如 Google 的 AI Research 部门 Google Brain，也是清一色地全部使用 Jupyter Notebook，虽然用的是他们自己的改进定制版，叫 Google Colab。

**Jupyter 的优点**

- 整合所有的资源

在真正的软件开发中，上下文切换占用了大量的时间。

Jupyter 通过把所有和软件编写有关的资源全部放在一个地方，解决了这个问题。当你打开一个 Jupyter Notebook 时，就已经可以看到相应的文档、图表、视频和相应的代码。这样，你就不需要切换窗口去找资料，只要看一个文件，就可以获得项目的所有信息。

- 交互性编程体验

在机器学习和数学统计领域，Python 编程的实验性特别强，经常出现的情况是，一小块代码需要重写 100 遍，比如为了尝试 100 种不同的方法，但别的代码都不想动。

Jupyter Notebook 引进了 Cell 的概念，每次实验可以只跑一小个 Cell 里的代码；并且，所见即所得，在代码下面立刻就可以看到结果。这样强的互动性，让 Python 研究员可以专注于问题本身，不被繁杂的工具链所累，不用在命令行直接切换，所有科研工作都能在 Jupyter 上完成。

- 零成本重现结果

同样在机器学习和数学统计领域，Python 的使用是非常短平快的。常见的场景是，我在论文里看到别人的方法效果很好，可是当我去重现时，却发现需要 pip 重新安装一堆依赖软件。这些准备工作可能会消耗你 80% 的时间，却并不是真正的生产力。

Jupyter 官方的 Binder 平台（介绍文档：https://mybinder.readthedocs.io/en/latest/index.html）和 Google 提供的 Google Colab 环境（介绍：https://colab.research.google.com/notebooks/welcome.ipynb）。它们让 Jupyter Notebook 变得和石墨文档、Google Doc 在线文档一样，在浏览器点开链接就能运行。

所以，现在当你用 Binder 打开一份 GitHub 上的 Jupyter Notebook 时，你不需要安装任何软件，直接在浏览器打开一份代码，就能在云端运行。

**Jupyter Notebook 初体验**

比如这样一个[GitHub 文件](https://github.com/binder-examples/python2_with_3/blob/master/index3.ipynb)。在[Binder](https://mybinder.org/)中，你只要输入其对应的 GitHub Repository 的名字或者 URL，就能在云端打开整个 Repository，选择你需要的[notebook](https://mybinder.org/v2/gh/binder-examples/python2_with_3/master?filepath=index3.ipynb)，你就能看到下图这个界面。

![image-20211207232540300](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20211207232540.png)

每一个 Jupyter 的运行单元都包含了 In、Out 的 Cell。如图所示，你可以使用 Run 按钮，运行单独的一个 Cell。当然，你也可以在此基础上加以修改，或者新建一个 notebook，写成自己想要的程序。

**推荐网站**

- 第一个是 Jupyter 官方：https://mybinder.org/v2/gh/binder-examples/matplotlib-versions/mpl-v2.0/?filepath=matplotlib_versions_demo.ipynb
- 第二个是 Google Research 提供的 Colab 环境，尤其适合机器学习的实践应用：https://colab.research.google.com/notebooks/basic_features_overview.ipynb

> 如果你想在本地或者远程的机器上安装 Jupyter Notebook，可以参考下面的两个文档。

> 安装：https://jupyter.org/install.html

> 运行：https://jupyter.readthedocs.io/en/latest/running.html#running



