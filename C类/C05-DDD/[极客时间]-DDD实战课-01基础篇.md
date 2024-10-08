> 来源极客时间《DDD实战课》--欧创新

# 开篇词 | 学好了DDD，你能做什么？

**什么是DDD?**

DDD 是一种设计思想，它可以同时指导中台业务建模和微服务设计。其次，就是通过战略设计，建立领域模型，划分微服务边界。最后，通过战术设计，从领域模型转向微服务设计和落地。

要想应用 DDD，首要任务就是要吃透 DDD 的核心设计思想，搞清楚 DDD、微服务和中台之间的关系。

遵循以上过程，这门课的设计思路也就诞生了。

专栏所能带来的收获：

1. **概念思想**：了解 DDD 必知必会的 10 大核心概念，深入设计思想；
2. **微服务架构**：弄懂微服务架构各层之间的关系，深化微服务架构设计原则和注意事项；
3. **领域/中台建模**：完成领域建模和企业级中台业务建模；
4. **技术要点**：学习 DDD 在领域模型和微服务设计过程中的技术要点；

**基础篇**

主要讲解 DDD 的核心知识体系，具体包括：领域、子域、核心域、通用域、支撑域、限界上下文、实体、值对象、聚合和聚合根等概念。

![image-20211109221143097](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211109221143.png)

**进阶篇**

主要讲解领域事件、DDD 分层架构、几种常见的微服务架构模型以及中台设计思想等内容。具体包括：

- 如何通过领域事件实现微服务解耦？
- 怎样进行微服务分层设计？
- 如何实现层与层之间的服务协作？
- 通过几种微服务架构模型的对比分析，让你了解领域模型和微服务分层的作用和价值。
- 如何实现前中后台的协同和融合？如何利用 DDD 进行中台设计？

**实战篇**

- 中台和领域建模的实战
- 微服务设计实战

# 01 | 领域驱动设计：微服务设计为什么要选择DDD？

我经常看到项目团队为微服务到底应该拆多小而争得面红耳赤。那是否有合适的理论或设计方法来指导微服务设计呢？

答案就是 DDD。

**微服务设计和拆分的困境**

在微服务实践过程中产生了不少的争论和疑惑：微服务的粒度应该多大呀？微服务到底应该如何拆分和设计呢？微服务的边界应该在哪里？

在较长一段时间里，就有不少人对微服务的理解产生了一些曲解。有人认为：“微服务很简单，不过就是把原来一个单体包拆分为多个部署包，或者将原来的单体应用架构替换为一套支持微服务架构的技术框架，就算是微服务了。” 还有人说：“微服务嘛，就是要微要小，拆得越小效果越好。”

但我想这两年，你在技术圈中一定听说过一些项目因为前期微服务拆分过度，导致项目复杂度过高，无法上线和运维。

综合来看，微服务拆分困境产生的根本原因就是不知道业务或者微服务的边界到底在什么地方。如果确定了业务边界和应用边界，这个困境也就迎刃而解了。

那如何确定，是否有相关理论或知识体系支持呢？DDD 核心思想是通过领域驱动设计方法定义领域模型，从而确定业务和应用边界。

**为什么 DDD 适合微服务？**

什么是DDD？

DDD 是一种处理高度复杂领域的设计思想，它试图分离技术实现的复杂性，并围绕业务概念构建领域模型来控制业务的复杂性。DDD 不是架构，而是一种架构设计方法论，它通过边界划分将复杂业务领域简单化，帮我们设计出清晰的领域和应用边界。

包括战略设计和战术设计两部分。

战略设计主要从业务视角出发，建立业务领域模型，划分领域边界，建立通用语言的限界上下文，限界上下文可以作为微服务设计的参考边界。

战术设计则从技术视角出发，侧重于领域模型的技术实现，完成软件开发和落地，包括：聚合根、实体、值对象、领域服务、应用服务和资源库等代码逻辑的设计和实现。

我们不妨来看看 DDD 是如何进行战略设计的。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211109222811.png" alt="image-20211109222811532" style="zoom: 50%;" />

第一步：在事件风暴中梳理出领域实体等领域对象。

事件风暴是建立领域模型的主要方法，它是一个从发散到收敛的过程。它通常采用用例分析、场景分析和用户旅程分析，尽可能全面不遗漏地分解业务领域，并梳理领域对象之间的关系，这是一个发散的过程。事件风暴过程会产生很多的实体、命令、事件等领域对象，我们将这些领域对象从不同的维度进行聚类，形成如聚合、限界上下文等边界，建立领域模型，这就是一个收敛的过程。

第二步：将业务紧密相关的实体进行组合形成聚合。

根据领域实体之间的业务关联性，将业务紧密相关的实体进行组合形成聚合，同时确定聚合中的聚合根、值对象和实体。在这个图里，聚合之间的边界是第一层边界，它们在同一个微服务实例中运行，这个边界是逻辑边界，所以用虚线表示。

第三步：根据业务及语义边界等因素，将一个或者多个聚合划定在一个限界上下文内，形成领域模型。

在这个图里，限界上下文之间的边界是第二层边界，这一层边界可能就是未来微服务的边界，不同限界上下文内的领域逻辑被隔离在不同的微服务实例中运行，物理上相互隔离，所以是物理边界，边界之间用实线来表示。

有了这两层边界，微服务的设计就不是什么难事了。

**DDD 与微服务的关系**

DDD 是一种架构设计方法，微服务是一种架构风格。

- 相同

两者从本质上都是为了追求高响应力，而从业务视角去分离应用系统建设复杂度的手段。

两者都强调从业务出发，其核心要义是强调根据业务发展，合理划分领域边界，持续调整现有架构，优化现有代码，以保持架构和代码的生命力，也就是我们常说的演进式架构。

- 不同

DDD 主要关注：从业务领域视角划分领域边界，建立领域模型。

微服务主要关注：运行时的进程间通信、容错和故障隔离，关注微服务的独立开发、测试、构建和部署。

# 02 | 领域、子域、核心域、通用域和支撑域

**如何理解领域和子域？**

在研究和解决业务问题时，DDD 会按照一定的规则将业务领域进行细分，当领域细分到一定的程度后，DDD 会将问题范围限定在特定的边界内，在这个边界内建立领域模型。

领域可以进一步划分为子领域，称为子域，每个子域对应一个更小的问题域或更小的业务范围。

DDD 的研究方法与自然科学的研究方法类似。当人们在自然科学研究中遇到复杂问题时，通常的做法就是将问题一步一步地细分，再针对细分出来的问题域，逐个深入研究，探索和建立所有子域的知识体系。当所有问题子域完成研究时，我们就建立了全部领域的完整知识体系了。

![image-20211110223702072](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/images/20211110223702.png)

上面这张图是在讲如何给桃树建立一个完整的生物学知识体系。初中生物课其实早就告诉我们研究方法了。它的研究过程是这样的。

第一步：确定研究对象，即研究领域，这里是一棵桃树。

第二步：对研究对象进行细分，将桃树细分为器官。

第三步：对器官进行细分，将器官细分为组织。

第四步：对组织进行细分，将组织细分为细胞，细胞成为我们研究的最小单元。细胞之间的细胞壁确定了单元的边界，也确定了研究的最小边界。

**如何理解核心域、通用域和支撑域？**

子域可以根据自身重要性和功能属性划分为三类，它们分别是：核心域、通用域和支撑域。

- 决定产品和公司核心竞争力的子域是核心域。
- 没有太多个性化的诉求，同时被多个子域使用的是通用域。
- 既不包含决定产品和公司核心竞争力的功能，也不包含通用功能的子域，它就是支撑域。

举例来说，通用域是你需要用到的通用系统，比如认证、权限等等，这类应用很容易买到，没有企业特点限制，不需要做太多的定制化。而支撑域则具有企业特性，但不具有通用性，例如数据代码类的数据字典等系统。

那为什么要划分核心域、通用域和支撑域，主要目的是什么呢？

公司在 IT 系统建设过程中，由于预算和资源有限，对不同类型的子域应有不同的关注度和资源投入策略。

# 03 | 限界上下文：定义领域边界的利器

在 DDD 领域建模和系统建设过程中，有很多的参与者，包括领域专家、产品经理、项目经理、架构师、开发经理和测试经理等。

对同样的领域知识，不同的参与角色可能会有不同的理解，那大家交流起来就会有障碍，怎么办呢？因此，在 DDD 中就出现了“通用语言”和“限界上下文”这两个重要的概念。

**什么是通用语言？**

在事件风暴过程中，通过团队交流达成共识的，能够简单、清晰、准确描述业务涵义和规则的语言就是通用语言。

也就是说，通用语言是团队统一的语言，不管你在团队中承担什么角色，在同一个领域的软件生命周期里都使用统一的语言进行交流。

通用语言包含术语和用例场景，并且能够直接反映在代码中。通用语言中的名词可以给领域对象命名，如商品、订单等，对应实体对象；而动词则表示一个动作或事件，如商品已下单、订单已付款等，对应领域事件或者命令。

下面我带你看一张图，这张图描述了从事件风暴建立通用语言到领域对象设计和代码落地的完整过程。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202409062249846.png" alt="image-20240906224903754" style="zoom: 67%;" />

1. 在事件风暴的过程中，领域专家会和设计、开发人员一起建立领域模型，在领域建模的过程中会形成通用的业务术语和用户故事。事件风暴也是一个项目团队统一语言的过程。
2. 通过用户故事分析会形成一个个的领域对象，这些领域对象对应领域模型的业务对象，每一个业务对象和领域对象都有通用的名词术语，并且一一映射。
3. 微服务代码模型来源于领域模型，每个代码模型的代码对象跟领域对象一一对应。

这里我再给你分享一条经验，我自己经常用，特别有效。==设计过程中我们可以用一些表格，来记录事件风暴和微服务设计过程中产生的领域对象及其属性。==比如，领域对象在 DDD 分层架构中的位置、属性、依赖关系以及与代码模型对象的映射关系等。

下面是一个微服务设计实例的部分数据，表格中的这些名词术语就是项目团队在事件风暴过程中达成一致、可用于团队内部交流的通用语言。

![image-20220123210103685](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220123210103.png)

**什么是限界上下文？**

我们知道语言都有它的语义环境，同样，通用语言也有它的上下文环境。为了避免同样的概念或语义在不同的上下文环境中产生歧义，DDD 在战略设计上提出了“限界上下文”这个概念，用来确定语义所在的领域边界。

我们可以将限界上下文拆解为两个词：限界和上下文。限界就是领域的边界，而上下文则是语义环境。通过领域的限界上下文，我们就可以在统一的领域边界内用统一的语言进行交流。

综合一下，我认为限界上下文的定义就是：用来封装通用语言和领域对象，提供上下文环境，保证在领域之内的一些术语、业务相关对象等（通用语言）有一个确切的含义，没有二义性。这个边界定义了模型的适用范围，使团队所有成员能够明确地知道什么应该在模型中实现，什么不应该在模型中实现。

**进一步理解限界上下文**

正如电商领域的商品一样，商品在不同的阶段有不同的术语，在销售阶段是商品，而在运输阶段则变成了货物。同样的一个东西，由于业务领域的不同，赋予了这些术语不同的涵义和职责边界，这个边界就可能会成为未来微服务设计的边界。

看到这，我想你应该非常清楚了，领域边界就是通过限界上下文来定义的。

**限界上下文和微服务的关系**

接下来，我们对这个概念做进一步的延伸。看看限界上下文和微服务具体存在怎样的关系。

我想你买过车险吧。车险承保的流程包含了投保、缴费、出单等几个主要流程。如果出险了还会有报案、查勘、定损、理算等理赔流程。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220123220849.png" alt="image-20220123220849741" style="zoom:50%;" />

首先，领域可以拆分为多个子领域。一个领域相当于一个问题域，领域拆分为子域的过程就是大问题拆分为小问题的过程。在这个图里面保险领域被拆分为：投保、支付、保单管理和理赔四个子域。

子域还可根据需要进一步拆分为子子域，比如，支付子域可继续拆分为收款和付款子子域。拆到一定程度后，有些子子域的领域边界就可能变成限界上下文的边界了。

子域可能会包含多个限界上下文，如理赔子域就包括报案、查勘和定损等多个限界上下文。也有可能子域本身的边界就是限界上下文边界，如投保子域。

理论上限界上下文就是微服务的边界。我们将限界上下文内的领域模型映射到微服务，就完成了从问题域到软件的解决方案。

# 04 | 实体和值对象：从领域模型的基础单元看系统设计

今天我们来学习 DDD 战术设计中的两个重要概念：实体和值对象。

**实体**

在 DDD 中有这样一类对象，它们拥有唯一标识符，且标识符在历经各种状态变更后仍能保持一致。对这些对象而言，重要的不是其属性，而是其延续性和标识，对象的延续性和标识会跨越甚至超出软件的生命周期。我们把这样的对象称为实体。

在 DDD 不同的设计过程中，实体的形态是不同的。

1. 实体的业务形态

领域模型中的实体是多个属性、操作或行为的载体。在事件风暴中，我们可以根据命令、操作或者事件，找出产生这些行为的业务实体对象，进而按照一定的业务规则将依存度高和业务关联紧密的多个实体对象和值对象进行聚类，形成聚合。你可以这么理解，实体和值对象是组成领域模型的基础单元。

2. 实体的代码形态

在代码模型中，实体的表现形式是实体类，这个类包含了实体的属性和方法，通过这些方法实现实体自身的业务逻辑。在 DDD 里，这些实体类通常采用充血模型，与这个实体相关的所有业务逻辑都在实体类的方法中实现，跨多个实体的领域逻辑则在领域服务中实现。

3. 实体的运行形态

实体以 DO（领域对象）的形式存在，每个实体对象都有唯一的 ID。我们可以对一个实体对象进行多次修改，修改后的数据和原来的数据可能会大不相同。但是，由于它们拥有相同的 ID，它们依然是同一个实体。比如商品是商品上下文的一个实体，通过唯一的商品 ID 来标识，不管这个商品的数据如何变化，商品的 ID 一直保持不变，它始终是同一个商品。

4. 实体的数据库形态

与传统数据模型设计优先不同，DDD 是先构建领域模型，针对实际业务场景构建实体对象和行为，再将实体对象映射到数据持久化对象。

在领域模型映射到数据模型时，一个实体可能对应 0 个、1 个或者多个数据库持久化对象。大多数情况下实体与持久化对象是一对一。在某些场景中，有些实体只是暂驻静态内存的一个运行态实体，它不需要持久化。比如，基于多个价格配置数据计算后生成的折扣实体。

**值对象**

值对象相对实体来说，会更加抽象一些，概念上我们会结合例子来讲。

值对象是 DDD 领域模型中的一个基础对象，它跟实体一样，都包含了若干个属性，它与实体一起构成聚合。

![image-20240909234910594](https://technotes.oss-cn-shenzhen.aliyuncs.com/2024/202409092349699.png)

如上图所示。我们可以将“省、市、县和街道等属性”拿出来构成一个“地址属性集合”，这个集合就是值对象。

1. 值对象的业务形态。

本质上，实体是看得到、摸得着的实实在在的业务对象，实体具有业务属性、业务行为和业务逻辑。而值对象只是若干个属性的集合。

2. 值对象的代码形态。

我们看一下下面这段代码，person 这个实体有若干个单一属性的值对象，比如 Id、name 等属性；同时它也包含多个属性的值对象，比如地址 address。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220124224851.png" alt="image-20220124224851540" style="zoom:67%;" />

3. 值对象的运行形态。

实体实例化后的 DO 对象的业务属性和业务行为非常丰富，但值对象实例化的对象则相对简单。

值对象嵌入到实体的话，有这样两种不同的数据格式，也可以说是两种方式，分别是属性嵌入的方式和序列化大对象的方式。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220124225147.png" alt="image-20220124225147082" style="zoom:50%;" />

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220124225205.png" alt="image-20220124225205733" style="zoom:50%;" />

4. 值对象的数据库形态。

举个例子，还是基于上述人员和地址那个场景，实体和数据模型设计通常有两种解决方案：第一是把地址值对象的所有属性都放到人员实体表中，创建人员实体，创建人员数据表；第二是创建人员和地址两个实体，同时创建人员和地址两张表。

第一个方案会破坏地址的业务涵义和概念完整性，第二个方案增加了不必要的实体和表，需要处理多个实体和表的关系，从而增加了数据库设计的复杂性。

那到底应该怎样设计，才能让业务含义清楚，同时又不让数据库变得复杂呢？

在领域建模时，我们可以将部分对象设计为值对象，保留对象的业务涵义，同时又减少了实体的数量；在数据建模时，我们可以将值对象嵌入实体，减少实体表的数量，简化数据库设计。

5. 值对象的优势和局限。

值对象采用序列化大对象的方法简化了数据库设计，减少了实体表的数量，可以简单、清晰地表达业务概念。这种设计方式虽然降低了数据库设计的复杂度，但却无法满足基于值对象的快速查询，会导致搜索值对象属性值变得异常困难。

**实体和值对象的关系**

DDD 提倡从领域模型设计出发，而不是先设计数据模型。

传统的数据模型设计通常是一个表对应一个实体，一个主表关联多个从表，当实体表太多的时候就很容易陷入无穷无尽的复杂的数据库设计，领域模型就很容易被数据模型绑架。可以说，值对象的诞生，在一定程度上，和实体是互补的。

我们还是以前面的图示为例：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220124224428.png" alt="image-20220124224428629" style="zoom:67%;" />

在领域模型中人员是实体，地址是值对象，地址值对象被人员实体引用。在数据模型设计时，地址值对象可以作为一个属性集整体嵌入人员实体中，组合形成上图这样的数据模型；也可以以序列化大对象的形式加入到人员的地址属性中，前面表格有展示。

从这个例子中，我们可以看出，同样的对象在不同的场景下，可能会设计出不同的结果。有些场景中，地址会被某一实体引用，它只承担描述实体的作用，并且它的值只能整体替换，这时候你就可以将地址设计为值对象，比如收货地址。而在某些业务场景中，地址会被经常修改，地址是作为一个独立对象存在的，这时候它应该设计为实体，比如行政区划中的地址信息维护。

# 05 | 聚合和聚合根：怎样设计聚合？

在事件风暴中，我们会根据一些业务操作和行为找出实体（Entity）或值对象（ValueObject），进而将业务关联紧密的实体和值对象进行组合，构成聚合，再根据业务语义将多个聚合划定到同一个限界上下文（Bounded Context）中，并在限界上下文内完成领域建模。

那你知道为什么要在限界上下文和实体之间增加聚合和聚合根这两个概念吗？它们的作用是什么？

**聚合**

在 DDD 中，实体和值对象是很基础的领域对象。实体一般对应业务对象，它具有业务属性和业务行为；而值对象主要是属性集合，对实体的状态和特征进行描述。

举个例子。社会是由一个个的个体组成的，我们每一个人就是一个个体。随着社会的发展，慢慢出现了社团、机构、部门等组织，我们也从个人变成了组织的一员，在组织内，大家协同工作，朝着更大的目标，发挥出更大的力量。

领域模型内的实体和值对象就好比个体，而能让实体和值对象协同工作的组织就是聚合，它用来确保这些领域对象在实现共同的业务逻辑时，能保证数据的一致性。

> 领域服务和应用服务的区别？

**聚合根**

如果把聚合比作组织，那聚合根就是这个组织的负责人。聚合根也称为根实体，它不仅是实体，还是聚合的管理者。

在聚合之间，通过聚合根 ID 关联引用，如果需要访问其它聚合的实体，就要先访问聚合根，再导航到聚合内部实体，外部对象不能直接访问聚合内实体。

**怎样设计聚合？**

以保险的投保业务场景为例。

![image-20220125223730684](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220125223730.png)

第 1 步：采用事件风暴，梳理出在投保过程中发生这些行为的所有的实体和值对象，比如投保单、标的、客户、被保人等等。

第 2 步：从众多实体中选出适合作为对象管理者的根实体，也就是聚合根。

判断一个实体是否是聚合根，你可以结合以下场景分析：是否有独立的生命周期？是否有全局唯一 ID？是否可以创建或修改其它对象？是否有专门的模块来管这个实体。

第 3 步：根据业务单一职责和高内聚原则，找出与聚合根关联的所有紧密依赖的实体和值对象。构建出 1 个包含聚合根（唯一）、多个实体和值对象的对象集合，这个集合就是聚合。

第 4 步：在聚合内根据聚合根、实体和值对象的依赖关系，画出对象的引用和依赖模型。

这里我需要说明一下：投保人和被保人的数据，是通过关联客户 ID 从客户聚合中获取的，在投保聚合里它们是投保单的值对象，这些值对象的数据是客户的冗余数据，即使未来客户聚合的数据发生了变更，也不会影响投保单的值对象数据。从图中我们还可以看出实体之间的引用关系，比如在投保聚合里投保单聚合根引用了报价单实体，报价单实体则引用了报价规则子实体。

第 5 步：多个聚合根据业务语义和上下文一起划分到同一个限界上下文内。

**聚合的一些设计原则**

1. 聚合用来封装真正的不变性，而不是简单地将对象组合在一起。
2. 设计小聚合。小聚合设计则可以降低由于业务过大导致聚合重构的可能性，让领域模型更能适应业务的变化。
3. 通过唯一标识引用其它聚合。聚合之间是通过关联外部聚合根 ID 的方式引用，而不是直接对象引用的方式。
4. 在边界之外使用最终一致性。聚合内数据强一致性，而聚合之间数据最终一致性。
5. 通过应用层实现跨聚合的服务调用。应避免跨聚合的领域服务调用和跨聚合的数据库表关联。

在系统设计过程时，适合自己的才是最好的，一切以解决实际问题为出发点。

