

# neo4j整理

> author : yanglulu
> date : 2019-06-29

# 1. 简介

## 与RDBMS对比

简单地说，我们可以说图数据库主要用于存储更多的关系数据。

如果我们使用RDBMS数据库来存储更多关系的数据，那么它们不能提供用于遍历大量数据的适当性能。 在这些情况下，Graph Database提高了应用程序性能。

t_user

| id   | name   |
| :--- | ------ |
| 1    | John   |
| 2    | Kate   |
| 3    | Aleksa |
| 4    | Jack   |
| 5    | Jonas  |
| 6    | Anne   |

t_user_friend

| id   | user_1 | user_2 |
| ---- | ------ | ------ |
| 1000 | 1      | 2      |
| 1001 | 3      | 5      |
| 1002 | 4      | 1      |
| 1003 | 6      | 2      |
| 1004 | 4      | 5      |
| 1005 | 1      | 4      |

获取一个特定用户的直接朋友，语句是：

```sql
select count(distinct uf.*) from t_user_friend uf where uf.user_1 = ?
```

查找一个用户的朋友的所有朋友，典型的做法是将表t_user_friend与它自身连接：

```sql
select count(distinct uf2.*) from t_user_friend uf1
inner join t_user_friend uf2 on uf1.user1 = uf2.user_2
where uf1.user_1 = ?
```

社交网络朋友推荐功能，需要找到朋友的朋友的朋友，这时只需要加一个join操作：

```sql
select count(distinct uf3.*) from t_user_friend uf1
inner join t_user_friend uf2 on uf1.user_1 = uf2.user_2
inner join t_user_friend uf3 on uf2.user_1 = uf3.user_2
where uf1.user_1 = ?
```

使用MySQL数据库引擎对一个有1000个用户的数据使用多个join查询的运行时间：

| 深度 | 查询1000个用户的运行时间（秒） | 计数结果 |
| ---- | ------------------------------ | -------- |
| 2    | 0.28                           | ~900     |
| 3    | 0.213                          | ~999     |
| 4    | 10.273                         | ~999     |
| 5    | 92.613                         | ~999     |

Neo4j对一个有1000个用户的图形数据库遍历的运行时间：

| 深度 | 查询1000个用户的运行时间（秒） | 计数结果 |
| ---- | ------------------------------ | -------- |
| 2    | 0.04                           | ~900     |
| 3    | 0.06                           | ~999     |
| 4    | 0.07                           | ~999     |
| 5    | 0.07                           | ~999     |

## Neo4j的特点

- SQL就像简单的查询语言Neo4j CQL
- 它遵循属性图数据模型
- 它通过使用Apache Lucence支持索引
- 它支持UNIQUE约束
- 它包含一个用于执行CQL命令的UI：Neo4j数据浏览器
- 它支持完整的ACID（原子性，一致性，隔离性和持久性）规则
- 它采用原生图形库与本地GPE（图形处理引擎）
- 它支持查询的数据导出到JSON和XLS格式
- 它提供了REST API，可以被任何编程语言（如Java，Spring，Scala等）访问
- 它提供了可以通过任何UI MVC框架（如Node JS）访问的Java脚本
- 它支持两种Java API：Cypher API和Native Java API来开发Java应用程序

## Neo4j的优点

- 它很容易表示连接的数据
- 检索/遍历/导航更多的连接数据是非常容易和快速的
- 它非常容易地表示半结构化数据
- Neo4j CQL查询语言命令是人性化的可读格式，非常容易学习
- 它使用简单而强大的数据模型
- 它不需要复杂的连接来检索连接的/相关的数据，因为它很容易检索它的相邻节点或关系细节没有连接或索引

## Neo4j数据模型

属性图模型规则

- 表示节点，关系和属性中的数据
- 节点和关系都包含属性
- 关系连接节点
- 属性是键值对
- 节点用圆圈表示，关系用方向键表示。
- 关系具有方向：单向和双向。
- 每个关系包含“开始节点”或“从节点”和“到节点”或“结束节点”

图形数据库数据模型的主要构建块是：

- 节点
- 关系
- 属性

------

## Neo4j学习资料

学习教程：https://www.w3cschool.cn/neo4j/

官网：https://neo4j.com/

neo4j中文社区：http://neo4j.com.cn/

国内下载：<ftp://neo4j.55555.io/neo4j>

书籍推荐：《Neo4j权威指南》

# 2. Cypher语句

## CQL简介

CQL代表Cypher查询语言。 像Oracle数据库具有查询语言SQL，Neo4j具有CQL作为查询语言。

- 它是Neo4j图形数据库的查询语言。
- 它是一种声明性模式匹配语言
- 它遵循SQL语法。
- 它的语法是非常简单且人性化、可读的格式。
- Neo4j CQL 以命令来执行数据库操作。
- Neo4j CQL 支持多个子句像在哪里，顺序等，以非常简单的方式编写非常复杂的查询。
- NNeo4j CQL 支持一些功能，如字符串，Aggregation.In 加入他们，它还支持一些关系功能。

## Neo4j CQL数据类型

这些数据类型与Java语言类似。 它们用于定义节点或关系的属性

Neo4j CQL支持以下数据类型：

| S.No. | CQL数据类型 | 用法                            |
| ----- | ----------- | ------------------------------- |
| 1.    | boolean     | 用于表示布尔文字：true，false。 |
| 2.    | byte        | 用于表示8位整数。               |
| 3.    | short       | 用于表示16位整数。              |
| 4.    | int         | 用于表示32位整数。              |
| 5.    | long        | 用于表示64位整数。              |
| 6.    | float       | I用于表示32位浮点数。           |
| 7.    | double      | 用于表示64位浮点数。            |
| 8.    | char        | 用于表示16位字符。              |
| 9.    | String      | 用于表示字符串。                |

## Neo4j CQL常用命令

读命令

| CQL命令/条        | 用法                                                         |
| ----------------- | ------------------------------------------------------------ |
| MATCH             | 用指定的模式检索数据库                                       |
| OPTINAL MATCH     | 用于搜索模式中描述的匹配项，对于找不到的项目用null代替       |
| WHERE             | 如果是在WITH和START中，它用于过滤结果，如果用在MATCH和OPTINAL<br/>MATCH，WHERE为模式增加约束条件 |
| START             | START语句应当仅用于访问遗留的索引。所有其他的情况，都应使用MATCH代替 |
| Aggregation(聚合) | count, sum, avg, stdev, min, max, collect, distinct          |
| LOAD CSV          | 用于从CSV文件中导入数据。                                    |

写命令

| CQL命令/条    | 用法                                                         |
| ------------- | ------------------------------------------------------------ |
| CREATE        | 创建节点，关系和属性                                         |
| MERGE         | MERGE可以确保图数据库中存在某个特定的模式。如果该模式不存在，那就创建它。 |
| SET           | 用于更新节点的标签以及节点和关系的属性。                     |
| DELETE        | 用于删除图元素（节点、关系或路径）                           |
| REMOVE        | 用于删除图元素的属性和标签。                                 |
| ~~FOREACH~~   | 用于更新列表中的数据，或者来自路径的组件，或者来自聚合的结果。 |
| CREATE UNIQUE | 相当于MATCH和CREATE的混合体--尽可能地匹配，然后创建未匹配到的。 |

通用命令

| CQL命令/条 | 用法                                                         |
| ---------- | ------------------------------------------------------------ |
| RETURN     | RETURN语句定义了查询结果集中返回的内容<br/>RETURN语句有三个子语句，分别为SKIP、LIMIT、ORDER BY。《Neo4j权威指南》page.67 |
| ORDER BY   | ORDER BY是紧跟RETURN或者WITH的子句，它指定了输出的结果应该如何排序。<br/>不能对节点或关系进行排序，只能对它们的属性进行排序。 |
| LIMIT      | 限制输出的行数。                                             |
| SKIP       | 定义了从哪行开始返回结果。                                   |
| WITH       | 将分段的查询部分连接在一起，查询结果从一部分以管道形式传递给另一部分作为开始点<br/>用法一：WITH的一个常见用法就是限制传递给其他MATCH语句的结果数。<br/>用法二：另一个用法就是在聚合值上过滤。<br/>用法三：用于将图的读语句和更新语句分开。<br/>（当写部分的语句是基于读语句的结果时，这两者之间的转换必须使用WITH）<br/>当希望使用聚合数据进行过滤时，必须使用WITH将两个读语句部分连接在一起。第一部分做聚合，第二部分过滤来自第一部分的结果。《Neo4j权威指南》page.67 |
| ~~UNWIND~~ | 将一个列表展开为一个行的序列。                               |
| ~~UNION~~  | 用于将多个查询结果组合起来。                                 |
| CALL       | 用于调用数据库中的过程。                                     |

## Neo4j CQL - CREATE命令

Neo4j使用CQL“CREATE”命令

- 创建没有属性的节点
- 使用属性创建节点
- 在没有属性的节点之间创建关系
- 使用属性创建节点之间的关系
- 为节点或关系创建单个或多个标签

**创建一个没有属性的节点**

CREATE命令语法

```CQL
CREATE (<node-name>:<label-name>)
```

语法说明

| 语法元素     | 描述                       |
| ------------ | -------------------------- |
| CREATE       | 它是一个Neo4j CQL命令。    |
| <node-name>  | 它是我们要创建的节点名称。 |
| <label-name> | 它是一个节点标签名称       |

注意事项 -
1、Neo4j数据库服务器使用此<node-name>将此节点详细信息存储在Database.As中作为Neo4j DBA或Developer，我们不能使用它来访问节点详细信息。
2、Neo4j数据库服务器创建一个<label-name>作为内部节点名称的别名。作为Neo4j DBA或Developer，我们应该使用此标签名称来访问节点详细信息。

实例：

```CQL
CREATE (emp:Employee)
```

这里emp是一个节点名，Employee是emp节点的标签名称

**创建具有属性的节点**

CREATE命令语法： 

```CQL
CREATE (
   <node-name>:<label-name>
   { 	
      <Property1-name>:<Property1-Value>
      ........
      <Propertyn-name>:<Propertyn-Value>
   }
)
```

语法说明：

| 语法元素                              | 描述                                            |
| ------------------------------------- | ----------------------------------------------- |
| <node-name>                           | 它是我们将要创建的节点名称。                    |
| <label-name>                          | 它是一个节点标签名称                            |
| <Property1-name>...<Propertyn-name>   | 属性是键值对。 定义将分配给创建节点的属性的名称 |
| <Property1-value>...<Propertyn-value> | 属性是键值对。 定义将分配给创建节点的属性的值   |

实例：

```CQL
CREATE (dept:Dept { deptno:10,dname:"Accounting",location:"Hyderabad" })
```

这里的属性名称是deptno，dname，location，属性值为10，"Accounting","Hyderabad"。正如我们讨论的，属性一个名称 - 值对。

Property = deptno:10
因为deptno是一个整数属性，所以我们没有使用单引号或双引号定义其值10。

由于dname和location是String类型属性，因此我们使用单引号或双引号定义其值10。

**注意 -** 要定义字符串类型属性值，我们需要使用单引号或双引号。

## Neo4j CQL - MATCH命令

Neo4j CQL MATCH命令用于 - 

- 从数据库获取有关节点和属性的数据
- 从数据库获取有关节点，关系和属性的数据

MATCH命令语法：

```CQL
MATCH 
(
   <node-name>:<label-name>
)
```

语法说明

| 语法元素     | 描述                         |
| ------------ | ---------------------------- |
| <node-name>  | 这是我们要创建一个节点名称。 |
| <label-name> | 这是一个节点的标签名称       |

注意事项 -

- Neo4j数据库服务器使用此<node-name>将此节点详细信息存储在Database.As中作为Neo4j DBA或Developer，我们不能使用它来访问节点详细信息。
- Neo4j数据库服务器创建一个<label-name>作为内部节点名称的别名。作为Neo4j DBA或Developer，我们应该使用此标签名称来访问节点详细信息。

实例：

```CQL
MATCH (dept:Dept)
```

## Neo4j CQL - RETURN子句

Neo4j CQL RETURN子句用于 -

- 检索节点的某些属性
- 检索节点的所有属性
- 检索节点和关联关系的某些属性
- 检索节点和关联关系的所有属性

RETURN命令语法：

```CQL
RETURN 
   <node-name>.<property1-name>,
   ........
   <node-name>.<propertyn-name>
```

语法说明:

| 语法元素                            | 描述                                                         |
| ----------------------------------- | ------------------------------------------------------------ |
| <node-name>                         | 它是我们将要创建的节点名称。                                 |
| <Property1-name>...<Propertyn-name> | 属性是键值对。 <Property-name>定义要分配给创建节点的属性的名称 |

实例：

```CQL
RETURN dept.deptno
```

## Neo4j CQL - MATCH & RETURN匹配和返回

在Neo4j CQL中，我们不能单独使用MATCH或RETURN命令，因此我们应该合并这两个命令以从数据库检索数据。

Neo4j使用CQL MATCH + RETURN命令 - 

- 检索节点的某些属性
- 检索节点的所有属性
- 检索节点和关联关系的某些属性
- 检索节点和关联关系的所有属性

MATCH RETURN命令语法：

```CQL
MATCH Command RETURN Command
```

语法说明：

| 语法元素   | 描述                       |
| ---------- | -------------------------- |
| MATCH命令  | 这是Neo4j CQL MATCH命令。  |
| RETURN命令 | 这是Neo4j CQL RETURN命令。 |

实例：

```CQL
MATCH (dept: Dept) RETURN dept.deptno,dept.dname
```

这里 -

- dept是节点名称
- 这里Dept是一个节点标签名
- deptno是dept节点的属性名称
- dname是dept节点的属性名

## Neo4j CQL - CREATE+MATCH+RETURN命令

在Neo4j CQL中，我们不能单独使用MATCH或RETURN命令，因此我们应该结合这两个命令从数据库检索数据。

本示例演示如何使用属性和这两个节点之间的关系创建两个节点。

我们将创建两个节点：客id，name，dob属性。

- 客户节点包含：ID，姓名，出生日期属性
- CreditCard节点包含：id，number，cvv，expiredate属性
- 客户与信用卡关系：DO_SHOPPING_WITH
- CreditCard到客户关系：ASSOCIATED_WITH

我们将在以下步骤中处理此示例： -

- 创建客户节点
- 创建CreditCard节点
- 观察先前创建的两个节点：Customer和CreditCard
- 创建客户和CreditCard节点之间的关系
- 查看新创建的关系详细信息
- 详细查看每个节点和关系属性

**创建客户节点**

```CQL
CREATE (e:Customer{id:"1001",name:"Abc",dob:"01/10/1982"})
```

这里 -

- e是节点名称
- 在这里Customer是节点标签名称
- id，name和dob是Customer节点的属性名称

**创建CreditCard节点**

```CQL
CREATE (cc:CreditCard{id:"5001",number:"1234567890",cvv:"888",expiredate:"20/17"})
```

这里c是一个节点名

这里CreditCard是节点标签名称

id，number，cvv和expiredate是CreditCard节点的属性名称

**查看客户节点详细信息**

```CQL
MATCH (e:Customer) RETURN e.id,e.name,e.dob
```

这里e是节点名

在这里Customer是节点标签名称

id，name和dob是Customer节点的属性名称

**查看CreditCard节点详细信息**

```CQL
MATCH (cc:CreditCard)
RETURN cc.id,cc.number,cc.cvv,cc.expiredate
```

这里cc是一个节点名

这里CreditCard是节点标签名称

id，number，cvv，expiredate是CreditCard节点的属性名称

## Neo4j CQL - CREATE创建标签

**Neo4j CQL创建节点标签**

Label是Neo4j数据库中的节点或关系的名称或标识符。

我们可以将此标签名称称为关系为“关系类型”。

我们可以使用CQL CREATE命令为节点或关系创建单个标签，并为节点创建多个标签。 这意味着Neo4j仅支持两个节点之间的单个关系类型。

我们可以在UI模式和网格模式下在CQL数据浏览器中观察此节点或关系的标签名称。 并且我们引用它执行CQL命令。

到目前为止，我们只创建了一个节点或关系的标签，但我们没有讨论它的语法。

使用Neo4j CQL CREATE命令

- 为节点创建单个标签
- 为节点创建多个标签
- 为关系创建单个标签

**单个标签到节点**

语法：

```CQL
CREATE (<node-name>:<label-name>)
```

说明：

| S.No. | 语法元素               | 描述                      |
| ----- | ---------------------- | ------------------------- |
| 1     | CREATE 创建            | 它是一个Neo4j CQL关键字。 |
| 2     | <node-name> <节点名称> | 它是一个节点的名称。      |
| 3     | <label-name><标签名称> | 这是一个节点的标签名      |

**注意 -**

- 我们应该使用colon（:)运算符来分隔节点名和标签名。
- Neo4j数据库服务器使用此名称将此节点详细信息存储在Database.As Neo4j DBA或Developer中，我们不能使用它来访问节点详细信息
- Neo4j数据库服务器创建一个标签名称作为内部节点名称的别名。作为Neo4j DBA或开发人员，我们应该使用此标签名称来访问节点详细信息。

实例：

```CQL
CREATE (google1:GooglePlusProfile)
```

这里google1是一个节点名。GooglePlusProfile 是 google1 node的标签名称

**多个标签到节点**

语法：

```CQL
CREATE (<node-name>:<label-name1>:<label-name2>.....:<label-namen>)
```

说明：

| S.No. | 语法元素                                         | 描述                           |
| ----- | ------------------------------------------------ | ------------------------------ |
| 1。   | CREATE 创建                                      | 这是一个Neo4j CQL关键字。      |
| 2。   | <node-name> <节点名称>                           | 它是一个节点的名称。           |
| 3。   | <label-name1>,<label-name2> <标签名1>，<标签名2> | 它是一个节点的标签名称的列表。 |

**注意 -**

- 我们应该使用colon（:)运算符来分隔节点名和标签名。
- 我们应该使用colon（:)运算符将一个标签名称分隔到另一个标签名称。

实例：

```CQL
CREATE (m:Movie:Cinema:Film:Picture)
```

这里m是一个节点名，Movie, Cinema, Film, Picture是m节点的多个标签名称

**单个标签到关系**

语法：

```CQL
CREATE (<node1-name>:<label1-name>)-
	[(<relationship-name>:<relationship-label-name>)]
	->(<node2-name>:<label2-name>)
```

语法说明：

| S.No. | 语法元素                                 | 描述                      |
| ----- | ---------------------------------------- | ------------------------- |
| 1     | CREATE 创建                              | 它是一个Neo4J CQL关键字。 |
| 2     | <node1-name> <节点1名>                   | 它是From节点的名称。      |
| 3     | <node2-name> <节点2名>                   | 它是To节点的名称。        |
| 4     | <label1-name> <LABEL1名称>               | 它是From节点的标签名称    |
| 5     | <label1-name> <LABEL1名称>               | 它是To节点的标签名称。    |
| 6     | <relationship-name> <关系名称>           | 它是一个关系的名称。      |
| 7     | <relationship-label-name> <相关标签名称> | 它是一个关系的标签名称。  |

**注意 -**

- 我我们应该使用colon（:)运算符来分隔节点名和标签名。
- 我们应该使用colon（:)运算符来分隔关系名称和关系标签名称。
- 我们应该使用colon（:)运算符将一个标签名称分隔到另一个标签名称。
- Neo4J数据库服务器使用此名称将此节点详细信息存储在Database.As中作为Neo4J DBA或开发人员，我们不能使用它来访问节点详细信息。
- Neo4J Database Server创建一个标签名称作为内部节点名称的别名。作为Neo4J DBA或Developer，我们应该使用此标签名称来访问节点详细信息。

## Neo4j CQL - WHERE子句

像SQL一样，Neo4j CQL在CQL MATCH命令中提供了WHERE子句来过滤MATCH查询的结果。

简单WHERE子句语法

```
WHERE <condition>
```

复杂WHERE子句语法

```
WHERE <condition> <boolean-operator> <condition>
```

<condition>语法：

```CQL
<property-name> <comparison-operator> <value>
```

语法说明：

| S.No. | 语法元素                           | 描述                                                         |
| ----- | ---------------------------------- | ------------------------------------------------------------ |
| 1     | WHERE                              | 它是一个Neo4j CQL关键字。                                    |
| 2     | <property-name> <属性名称>         | 它是节点或关系的属性名称。                                   |
| 3     | <comparison-operator> <比较运算符> | 它是Neo4j CQL比较运算符之一。请参考下一节查看Neo4j CQL中可用的比较运算符。 |
| 4     | <value> <值>                       | 它是一个字面值，如数字文字，字符串文字等。                   |

**Neo4j CQL中的布尔运算符**

Neo4j支持以下布尔运算符在Neo4j CQL WHERE子句中使用以支持多个条件。

| S.No. | 布尔运算符 | 描述                                   |
| ----- | ---------- | -------------------------------------- |
| 1     | AND        | 它是一个支持AND操作的Neo4j CQL关键字。 |
| 2     | OR         | 它是一个Neo4j CQL关键字来支持OR操作。  |
| 3     | NOT        | 它是一个Neo4j CQL关键字支持NOT操作。   |
| 4     | XOR        | 它是一个支持XOR操作的Neo4j CQL关键字。 |

**Neo4j CQL中的比较运算符**

Neo4j 支持以下的比较运算符，在 Neo4j CQL WHERE 子句中使用来支持条件。

| **S.No.** | 布尔运算符 | **描述**                              |
| --------- | ---------- | ------------------------------------- |
| 1.        | =          | 它是Neo4j CQL“等于”运算符。           |
| 2.        | <>         | 它是一个Neo4j CQL“不等于”运算符。     |
| 3.        | <          | 它是一个Neo4j CQL“小于”运算符。       |
| 4.        | >          | 它是一个Neo4j CQL“大于”运算符。       |
| 5.        | <=         | 它是一个Neo4j CQL“小于或等于”运算符。 |
| 6.        | >=         | 它是一个Neo4j CQL“大于或等于”运算符。 |

实例：

```CQL
MATCH (emp:Employee) 
WHERE emp.name = 'Abc' OR emp.name = 'Xyz'
RETURN emp
```

**使用WHERE子句创建关系**

在Neo4J CQL中，我们可以以不同的方式创建拖曳节点之间的关系。

- 创建两个现有节点之间的关系
- 一次创建两个节点和它们之间的关系
- 使用WHERE子句创建两个现有节点之间的关系

我们已经讨论了前两章中的前两种方法。 现在我们将在本章中讨论“使用WHERE子句创建两个现有节点之间的关系”。

语法

```
MATCH (<node1-label-name>:<node1-name>),(<node2-label-name>:<node2-name>) 
WHERE <condition>
CREATE (<node1-label-name>)-[<relationship-label-name>:<relationship-name>
       {<relationship-properties>}]->(<node2-label-name>) 
```

语法说明：

| S.No. | 语法元素                  | 描述                                                         |
| ----- | ------------------------- | ------------------------------------------------------------ |
| 1     | MATCH,WHERE,CREATE        | 他们是Neo4J CQL关键字。                                      |
| 2     | <node1-label-name>        | 它是一个用于创建关系的节点一标签名称。                       |
| 3     | <node1-name>              | 它是一个用于创建关系的节点名称。                             |
| 4     | <node2-label-name>        | 它是一个用于创建关系的节点一标签名称。                       |
| 5     | <node2-name>              | 它是一个用于创建关系的节点名称。                             |
| 6     | <condition>               | 它是一个Neo4J CQL WHERE子句条件。 它可以是简单的或复杂的。   |
| 7     | <relationship-label-name> | 这是新创建的节点一和节点二之间的关系的标签名称。             |
| 8     | <relationship-name>       | 这是新创建的节点1和节点2之间的关系的名称。                   |
| 9     | <relationship-properties> | 这是一个新创建节点一和节点二之间关系的属性列表（键 - 值对）。 |

实例：

```CQL
MATCH (cust:Customer),(cc:CreditCard) 
WHERE cust.id = "1001" AND cc.id= "5001" 
CREATE (cust)-[r:DO_SHOPPING_WITH{shopdate:"12/12/2014",price:55000}]->(cc) 
RETURN r
```

## Neo4j CQL - DELETE删除

Neo4j使用CQL DELETE子句

- 删除节点。
- 删除节点及相关节点和关系。

通过使用此命令，我们可以从数据库永久删除节点及其关联的属性。

**DELETE节点子句语法**

```
DELETE <node-name-list>
```

| S.No. | 语法元素         | 描述                                     |
| ----- | ---------------- | ---------------------------------------- |
| 1.    | DELETE           | 它是一个Neo4j CQL关键字。                |
| 2.    | <node-name-list> | 它是一个要从数据库中删除的节点名称列表。 |

注意 -

我们应该使用逗号（，）运算符来分隔节点名。

实例：

```CQL
MATCH (e: Employee) DELETE e
```

**DELETE节点和关系子句语法**

```CQL
DELETE <node1-name>,<node2-name>,<relationship-name>
```

| S.No. | 语法元素            | 描述                                                       |
| ----- | ------------------- | ---------------------------------------------------------- |
| 1.    | DELETE              | 它是一个Neo4j CQL关键字。                                  |
| 2.    | <node1-name>        | 它是用于创建关系<relationship-name>的一个结束节点名称。    |
| 3.    | <node2-name>        | 它是用于创建关系<relationship-name>的另一个节点名称。      |
| 4.    | <relationship-name> | 它是一个关系名称，它在<node1-name>和<node2-name>之间创建。 |

注意 -

我们应该使用逗号（，）运算符来分隔节点名称和关系名称。

实例：

```CQL
MATCH (cc: CreditCard)-[rel]-(c:Customer) 
DELETE cc,c,rel
```

## Neo4j CQL - REMOVE删除

有时基于我们的客户端要求，我们需要向现有节点或关系添加或删除属性。我们使用Neo4j CQL SET子句向现有节点或关系添加新属性。我们使用Neo4j CQL REMOVE子句来删除节点或关系的现有属性。

Neo4j CQL REMOVE命令用于

- 删除节点或关系的标签
- 删除节点或关系的属性

Neo4j CQL DELETE和REMOVE命令之间的主要区别 - 

- DELETE操作用于删除节点和关联关系。
- REMOVE操作用于删除标签和属性。

Neo4j CQL DELETE和REMOVE命令之间的相似性 - 

- 这两个命令不应单独使用。
- 两个命令都应该与MATCH命令一起使用。

**删除节点/关系的属性**

我们可以使用相同的语法从数据库中永久删除节点或关系的属性或属性列表。

REMOVE属性子句语法

```
REMOVE <property-name-list>
```

| S.No. | 语法元素             | 描述                                                 |
| ----- | -------------------- | ---------------------------------------------------- |
| 1。   | REMOVE               | 它是一个Neo4j CQL关键字。                            |
| 2。   | <property-name-list> | 它是一个属性列表，用于永久性地从节点或关系中删除它。 |

<property-name-list> <属性名称列表>语法

```
<node-name>.<property1-name>,
<node-name>.<property2-name>, 
.... 
<node-name>.<propertyn-name> 
```

语法说明：

| S.No. | 语法元素        | 描述                 |
| ----- | --------------- | -------------------- |
| 1。   | <node-name>     | 它是节点的名称。     |
| 2。   | <property-name> | 它是节点的属性名称。 |

**注意 -**

- 我们应该使用逗号（，）运算符来分隔标签名称列表。
- 我们应该使用dot（。）运算符来分隔节点名称和标签名称。

实例：

```CQL
CREATE (book:Book {id:122,title:"Neo4j Tutorial",pages:340,price:250}) 
```

```CQL
MATCH (book { id:122 })
REMOVE book.price
RETURN book
```

**删除节点/关系的标签**

我们可以使用相同的语法从数据库中永久删除节点或关系的标签或标签列表。

REMOVE一个Label子句语法：

```
REMOVE <label-name-list> 
```

| S.No. | 语法元素          | 描述                                                 |
| ----- | ----------------- | ---------------------------------------------------- |
| 1.    | REMOVE            | 它是一个Neo4j CQL关键字。                            |
| 2.    | <label-name-list> | 它是一个标签列表，用于永久性地从节点或关系中删除它。 |

<label-name-list>语法

```
<node-name>:<label2-name>, 
.... 
<node-name>:<labeln-name> 
```

语法说明：

| S.No. | 语法元素                | 描述                     |
| ----- | ----------------------- | ------------------------ |
| 1。   | <node-name> <节点名称>  | 它是一个节点的名称。     |
| 2。   | <label-name> <标签名称> | 这是一个节点的标签名称。 |

**注意 -**

- 我们应该使用逗号（，）运算符来分隔标签名称列表。
- 我们应该使用colon（:)运算符来分隔节点名和标签名。

实例：

```CQL
MATCH (m:Movie) RETURN m
```

```CQL
MATCH (m:Movie) 
REMOVE m:Picture
```

## Neo4j CQL - SET子句

有时，根据我们的客户端要求，我们需要向现有节点或关系添加新属性。

要做到这一点，Neo4j CQL提供了一个SET子句。

Neo4j CQL已提供SET子句来执行以下操作。

- 向现有节点或关系添加新属性
- 添加或更新属性值

SET子句语法

```CQL
SET <property-name-list>
```

| S.No. | 语法元素             | 描述                                                       |
| ----- | -------------------- | ---------------------------------------------------------- |
| 1     | SET                  | 它是一个Neo4j的CQL关键字。                                 |
| 2     | <property-name-list> | 它是一个属性列表，用于执行添加或更新操作以满足我们的要求。 |

<属性名称列表>语法：

```
<node-label-name>.<property1-name>,
<node-label-name>.<property2-name>, 
.... 
<node-label-name>.<propertyn-name> 
```

语法说明：

| S.No. | 语法元素                         | 描述                     |
| ----- | -------------------------------- | ------------------------ |
| 1     | <node-label-name> <节点标签名称> | 这是一个节点的标签名称。 |
| 2     | <property-name> <属性名称>       | 它是一个节点的属性名。   |

注意 -

我们应该使用逗号（，）运算符来分隔属性名列表。

实例：

```CQL
MATCH (dc:DebitCard)
SET dc.atm_pin = 3456
RETURN dc
```

## Neo4j CQL - Sorting排序

Neo4j CQL ORDER BY子句

Neo4j CQL在MATCH命令中提供了“ORDER BY”子句，对MATCH查询返回的结果进行排序。

我们可以按升序或降序对行进行排序。

默认情况下，它按升序对行进行排序。 如果我们要按降序对它们进行排序，我们需要使用DESC子句。

**ORDER BY子句语法**

```CQL
ORDER BY  <property-name-list>  [DESC]	 
```

| S.No. | Syntax Element       | Description                                                  |
| ----- | -------------------- | ------------------------------------------------------------ |
| 1.    | ORDER BY             | It is a Neo4j CQL keyword.                                   |
| 2.    | <property-name-list> | It is a list of properties used in sorting.                  |
| 3.    | DESC                 | It is a Neo4j CQL keyword used to specify descending order.It is optional. |

<property-name-list>语法：

```
<node-label-name>.<property1-name>,
<node-label-name>.<property2-name>, 
.... 
<node-label-name>.<propertyn-name>
```

语法说明：

| S.No. | 语法元素          | 描述                 |
| ----- | ----------------- | -------------------- |
| 1。   | <node-label-name> | 它是节点的标签名称。 |
| 2。   | <property-name>   | 它是节点的属性名称。 |

**注意 -**

我们应该使用逗号（，）运算符来分隔属性名列表。

实例：

```CQL
MATCH (emp:Employee)
RETURN emp.empid,emp.name,emp.salary,emp.deptno
ORDER BY emp.name
```

```CQL
MATCH (emp:Employee)
RETURN emp.empid,emp.name,emp.salary,emp.deptno
ORDER BY emp.name DESC
```

## Neo4j CQL - UNION联盟

与SQL一样，Neo4j CQL有两个子句，将两个不同的结果合并成一组结果

- UNION
- UNION ALL

**UNION子句**

它将两组结果中的公共行组合并返回到一组结果中。 它不从两个节点返回重复的行。

限制：

结果列类型和来自两组结果的名称必须匹配，这意味着列名称应该相同，列的数据类型应该相同。

UNION子句语法

```CQL
<MATCH Command1>
   UNION
<MATCH Command2>
```

语法说明：

| S.No. | 语法元素         | 描述                                   |
| ----- | ---------------- | -------------------------------------- |
| 1。   | <MATCH COMMAND1> | 它是CQL MATCH命令，由UNION子句使用。   |
| 2。   | <MATCH Command2> | 它是CQL MATCH命令两个由UNION子句使用。 |
| 3。   | UNION            | 它是UNION子句的Neo4j CQL关键字。       |

注意 -

如果这两个查询不返回相同的列名和数据类型，那么它抛出一个错误。

实例：

```CQL
MATCH (cc:CreditCard) RETURN cc
```

![](https://atts.w3cschool.cn/attachments/tuploads/neo4j/neo4j_cql_union1.png)

```CQL
MATCH (dc:DebitCard) RETURN dc
```

![](https://atts.w3cschool.cn/attachments/tuploads/neo4j/neo4j_cql_union2.png)

```CQL
MATCH (cc:CreditCard) RETURN cc.id,cc.number
UNION
MATCH (dc:DebitCard) RETURN dc.id,dc.number
```

看到成功消息数据浏览器

![](https://atts.w3cschool.cn/attachments/tuploads/neo4j/neo4j_cql_union4.png)

这表明，这两个查询应具有相同的列名。

首先查询有：cc.id，cc.number。

第二个查询有：dc.id，dc.number。

这里既有信用卡式和借记卡具有相同的属性名：身份证和号码，但他们有不同的节点名称前缀。这就是为什么UNION命令显示此错误消息。为了避免这种错误，Neo4j的CQL提供“AS”子句。

像CQL，CQL Neo4j的“AS”子句用于给一些别名。

```CQL
MATCH (cc:CreditCard)
RETURN cc.id as id,cc.number as number,cc.name as name,
   cc.valid_from as valid_from,cc.valid_to as valid_to
UNION
MATCH (dc:DebitCard)
RETURN dc.id as id,dc.number as number,dc.name as name,
   dc.valid_from as valid_from,dc.valid_to as valid_to
```

![](https://atts.w3cschool.cn/attachments/tuploads/neo4j/neo4j_cql_union5.png)

在这里，因为UNION子句过滤它们，我们可以看到该命令返回9行没有重复的行。

**UNION ALL子句**

它结合并返回两个结果集的所有行成一个单一的结果集。它还返回由两个节点重复行。

限制

结果列类型，并从两个结果集的名字必须匹配，这意味着列名称应该是相同的，列的数据类型应该是相同的。

UNION ALL子句语法

```
<MATCH Command1>
UNION ALL
<MATCH Command2>
```

语法说明

| S.No. | 语法元素         | 描述                                       |
| ----- | ---------------- | ------------------------------------------ |
| 1。   | <MATCH COMMAND1> | 这是CQL match命令由UNION子句中使用的一个。 |
| 2。   | <MATCH命令2>     | 这是CQL match命令两到由UNION子句中使用。   |
| 3。   | UNION ALL        | 这是UNION ALL子句的Neo4j的CQL关键字。      |

注意 -

如果这两个查询不返回相同的列名和数据类型，那么它抛出一个错误。

```CQL
MATCH (cc:CreditCard)
RETURN cc.id as id,cc.number as number,cc.name as name,
   cc.valid_from as valid_from,cc.valid_to as valid_to
UNION ALL
MATCH (dc:DebitCard)
RETURN dc.id as id,dc.number as number,dc.name as name,
   dc.valid_from as valid_from,dc.valid_to as valid_to
```

![](https://atts.w3cschool.cn/attachments/tuploads/neo4j/neo4j_cql_unionall1.png)

## Neo4j CQL - LIMIT和SKIP子句

**Neo4j CQL LIMIT子句**

Neo4j CQL已提供“LIMIT”子句来过滤或限制查询返回的行数。 它修剪CQL查询结果集底部的结果。如果我们要修整CQL查询结果集顶部的结果，那么我们应该使用CQL SKIP子句。

LIMIT子句语法

```
LIMIT <number>
```

语法说明：

| S.No. | 语法元素 | 描述                      |
| ----- | -------- | ------------------------- |
| 1。   | LIMIT    | 它是一个Neo4j CQL关键字。 |
| 2。   | <number> | 它是一个跨值。            |

实例：

```CQL
MATCH (emp:Employee) 
RETURN emp
LIMIT 2
```

**Neo4j CQL SKIP子句**

Neo4j CQL已提供“SKIP”子句来过滤或限制查询返回的行数。 它修整了CQL查询结果集顶部的结果。如果我们要从CQL查询结果集底部修整结果，那么我们应该使用CQL LIMIT子句。

SKIP子句语法：

```
SKIP <number>
```

语法说明：

| S.No. | 语法元素 | 描述                      |
| ----- | -------- | ------------------------- |
| 1。   | SKIP     | 它是一个Neo4j CQL关键字。 |
| 2。   | <number> | 它是一个间隔值。          |

实例：

```CQL
MATCH (emp:Employee) 
RETURN emp
SKIP 2
```

## Neo4j CQL - 合并

Neo4j使用CQL MERGE命令 - 

- 创建节点，关系和属性
- 为从数据库检索数据

MERGE命令是CREATE命令和MATCH命令的组合。

```
MERGE = CREATE + MATCH
```

Neo4j CQL MERGE命令在图中搜索给定模式，如果存在，则返回结果；如果它不存在于图中，则它创建新的节点/关系并返回结果。

Neo4j CQL MERGE语法

```CQL
MERGE (<node-name>:<label-name>
{
   <Property1-name>:<Pro<rty1-Value>
   .....
   <Propertyn-name>:<Propertyn-Value>
})
```

语法说明：

| S.No. | 语法元素         | 描述                                                |
| ----- | ---------------- | --------------------------------------------------- |
| 1     | MERGE            | 它是一个Neo4j CQL关键字。                           |
| 2     | <node-name>      | 它是节点或关系的名称。                              |
| 3     | <label-name>     | 它是节点或关系的标签名称。                          |
| 4     | <property_name>  | 它是节点或关系的属性名称。                          |
| 5     | <property_value> | 它是节点或关系的属性值。                            |
| 6     | ：               | 使用colon（:)运算符来分隔节点或关系的属性名称和值。 |

**注意 -**

Neo4j CQL MERGE命令语法与CQL CREATE命令类似。

我们将使用这两个命令执行以下操作 - 

- 创建具有一个属性的配置文件节点：Id，名称
- 创建具有相同属性的同一个Profile节点：Id，Name
- 检索所有Profile节点详细信息并观察结果

我们将使用CREATE命令执行这些操作

实例：

```CQL
MERGE (gp2:GoogleProfile2{ Id: 201402,Name:"Nokia"})
```

执行后，可以看到，Added 1 label, created 1node, set 2 properties, return 0 rows in 568ms.

## Neo4j CQL - NULL值

Neo4j CQL将空值视为对节点或关系的属性的缺失值或未定义值。

当我们创建一个具有现有节点标签名称但未指定其属性值的节点时，它将创建一个具有NULL属性值的新节点。  

实例：

```CQL
MATCH (e:Employee) 
WHERE e.id IS NOT NULL
RETURN e.id,e.name,e.sal,e.deptno
```

## Neo4j CQL - IN操作符

与SQL一样，Neo4j CQL提供了一个IN运算符，以便为CQL命令提供值的集合。

IN操作符语法

```CQL
IN [<Collection-of-values>]
```

语法说明：

| S.No. | 语法元素               | 描述                                  |
| ----- | ---------------------- | ------------------------------------- |
| 1。   | IN                     | 它是一个Neo4j CQL关键字。             |
| 2。   | [                      | 它告诉Neo4j CQL，一个值的集合的开始。 |
| 3。   | ]                      | 它告诉Neo4j CQL，值集合的结束。       |
| 4。   | <Collection-of-values> | 它是由逗号运算符分隔的值的集合。      |

让我们用一个例子来研究一下。

```CQL
MATCH (e:Employee) 
WHERE e.id IN [123,124]
RETURN e.id,e.name,e.sal,e.deptno
```

## Neo4j CQL - 方向关系

在Neo4j中，两个节点之间的关系是有方向性的。 它们是单向或双向的。

由于Neo4j遵循属性图数据模型，它应该只支持方向关系。 如果我们尝试创建一个没有任何方向的关系，那么Neo4j DB服务器应该抛出一个错误。

我们使用以下语法来创建两个节点之间的关系。

```
CREATE (<node1-details>)-[<relationship-details>]->(<node2-details>)
```

这里 -

- <node1-details>是“From Node”节点详细信息

- <node2-details>是“到节点”节点详细信息

- relationship-details>是关系详细信息

如果我们观察上面的语法，它使用一个箭头标记：（） - []→（）。 它表示从左侧节点到右侧节点的方向。

如果我们尝试使用相同的语法，没有箭头标记like（） - [] - （），这意味着没有方向的关系。 然后Neo4j DB服务器应该抛出一个错误消息

实例：

```CQL
CREATE (n1:Node1)-[r1:Relationship]->(n2:Node2)
```

## Neo4j CQL - 函数

**断言(Predicate)函数**

| 函数     | 用法                                                     |
| -------- | -------------------------------------------------------- |
| all()    | 判断一个断言是否适用于列表中的所有元素                   |
| any()    | 判断一个断言至少适用于列表中的一个元素                   |
| none()   | 如果断言不适用于列表中的任何元素，则返回true             |
| single() | 如果断言刚好只适用于列表中的某一个元素，则返回true       |
| exists() | 如果数据库中存在该模式或者节点中存在该属性时，则返回true |

**标量(Scalar)函数**

| 函数                  | 用法                                                    |
| --------------------- | ------------------------------------------------------- |
| size()                | 返回表中元素的个数。RETURN size(['A', 'B', 'c']) AS col |
| length()              | 返回路径/字符串的长度                                   |
| type()                | 返回关系类型                                            |
| id()                  | 返回关系或者节点的id                                    |
| head()/last()         | 返回列表中的第一个/最后一个元素                         |
| timestamp()           | 以毫秒返回当前时间                                      |
| startNode()/endNode() | 返回关系的开始/结束节点                                 |
| properties()          | 返回节点或者关系的属性map                               |
| toInt()/toFloat()     | 将实参转换为一个整数/浮点数                             |

**列表(List)函数**

| 函数            | 用法                     |
| --------------- | ------------------------ |
| nodes()         | 返回一条路径中的所有节点 |
| relationships() | 返回一条路径中的所有关系 |
|                 |                          |

**字符串函数**

| S.No. | 功能      | 描述                             |
| ----- | --------- | -------------------------------- |
| 1。   | UPPER     | 它用于将所有字母更改为大写字母。 |
| 2。   | LOWER     | 它用于将所有字母改为小写字母。   |
| 3。   | SUBSTRING | 它用于获取给定String的子字符串。 |
| 4。   | REPLACE   | 它用于替换一个字符串的子字符串。 |

UPPER

```CQL
MATCH (e:Employee) 
RETURN e.id,UPPER(e.name),e.sal,e.deptno
```

LOWER

```
MATCH (e:Employee) 
RETURN e.id,LOWER(e.name),e.sal,e.deptno
```

SUBSTRING

```
MATCH (e:Employee) 
RETURN e.id,SUBSTRING(e.name,0,2),e.sal,e.deptno
```

**AGGREGATION聚合**

聚合函数列表

| S.No. | 聚集功能 | 描述                                    |
| ----- | -------- | --------------------------------------- |
| 1。   | COUNT    | 它返回由MATCH命令返回的行数。           |
| 2。   | MAX      | 它从MATCH命令返回的一组行返回最大值。   |
| 3。   | MIN      | 它返回由MATCH命令返回的一组行的最小值。 |
| 4。   | SUM      | 它返回由MATCH命令返回的所有行的求和值。 |
| 5。   | AVG      | 它返回由MATCH命令返回的所有行的平均值。 |

COUNT

```CQL
MATCH (e:Employee) RETURN COUNT(*)
```

MAX, MIN

```CQL
MATCH (e:Employee) 
RETURN MAX(e.sal),MIN(e.sal)
```

AVG

```
AVG(<property-name> )
```

SUM

```CQL
MATCH (e:Employee) 
RETURN SUM(e.sal),AVG(e.sal)
```

**关系函数**

| S.No. | 功能      | 描述                                     |
| ----- | --------- | ---------------------------------------- |
| 1。   | STARTNODE | 它用于知道关系的开始节点。               |
| 2。   | ENDNODE   | 它用于知道关系的结束节点。               |
| 3。   | ID        | 它用于知道关系的ID。                     |
| 4。   | TYPE      | 它用于知道字符串表示中的一个关系的TYPE。 |

STARTNODE

```CQL
MATCH (a)-[movie:ACTION_MOVIES]->(b) 
RETURN STARTNODE(movie)
```

ENDNODE

```CQL
MATCH (a)-[movie:ACTION_MOVIES]->(b) 
RETURN ENDNODE(movie)
```

ID, TYPE

```CQL
MATCH (a)-[movie:ACTION_MOVIES]->(b) 
RETURN ID(movie),TYPE(movie)
```

# 3. Neo4j CQL - 索引

Neo4j SQL支持节点或关系属性上的索引，以提高应用程序的性能。
我们可以为具有相同标签名称的所有节点的属性创建索引。
我们可以在MATCH或WHERE或IN运算符上使用这些索引列来改进CQL Command的执行。

Neo4J索引操作

- Create Index 创建索引
- Drop Index 丢弃索引

创建索引的语法：

```CQL
CREATE INDEX ON :<label_name> (<property_name>)
```

例：

```CQL
CREATE INDEX ON :Customer (name)
```

Drop Index语法：

```CQL
DROP INDEX ON :<label_name> (<property_name>)
```

例：

```CQL
DROP INDEX ON :Customer (name)
```

# 4. Neo4j CQL - UNIQUE约束

在Neo4j数据库中，CQL CREATE命令始终创建新的节点或关系，这意味着即使您使用相同的值，它也会插入一个新行。 根据我们对某些节点或关系的应用需求，我们必须避免这种重复。 然后我们不能直接得到这个。 我们应该使用一些数据库约束来创建节点或关系的一个或多个属性的规则。

像SQL一样，Neo4j数据库也支持对NODE或Relationship的属性的UNIQUE约束

UNIQUE约束的优点

- 避免重复记录。
- 强制执行数据完整性规则。

创建UNIQUE约束

```CQL
CREATE CONSTRAINT ON (<label_name>)
ASSERT <property_name> IS UNIQUE
```

语法说明：

| S.No. | 语法元素             | 描述                                                         |
| ----- | -------------------- | ------------------------------------------------------------ |
| 1。   | CREATE CONSTRAINT ON | 它是一个Neo4j CQL关键字。                                    |
| 2。   | <label_name>         | 它是节点或关系的标签名称。                                   |
| 3。   | ASSERT               | 它是一个Neo4j CQL关键字。                                    |
| 4。   | <property_name>      | 它是节点或关系的属性名称。                                   |
| 5。   | IS UNIQUE            | 它是一个Neo4j CQL关键字，通知Neo4j数据库服务器创建一个唯一约束。 |

例：

```CQL
MATCH (cc:CreditCard) 
RETURN cc.id,cc.number,cc.name,cc.expiredate,cc.cvv
```

```CQL
CREATE CONSTRAINT ON (cc:CreditCard)
ASSERT cc.number IS UNIQUE
```

删除UNIQUE约束

```CQL
DROP CONSTRAINT ON (<label_name>)
ASSERT <property_name> IS UNIQUE
```

语法说明

| S.No. | 语法元素           | 描述                                                         |
| ----- | ------------------ | ------------------------------------------------------------ |
| 1。   | DROP CONSTRAINT ON | 它是一个Neo4j CQL关键字。                                    |
| 2。   | <label_name>       | 它是节点或关系的标签名称。                                   |
| 3。   | ASSERT             | 它是一个Neo4j CQL关键字。                                    |
| 4。   | <property_name>    | 它是节点或关系的属性名称。                                   |
| 5。   | IS UNIQUE          | 它是一个Neo4j CQL关键字，通知Neo4j数据库服务器创建一个唯一约束。 |

例：

```CQL
DROP CONSTRAINT ON (cc:CreditCard)
ASSERT cc.number IS UNIQUE
```

# 5. 与Java交互

## 1). Cypher - API

使用Cypher api相当于执行一条sql语句对数据库进行操作。有两种实现方式：

驱动包开发模式（支持多语言）和JDBC。

创建Neo4j数据库

```java
GraphDatabaseFactory dbFactory = new GraphDatabaseFactory();
GraphDatabaseService db= dbFactory.newEmbeddedDatabase("C:/TPNeo4jDB");
```

创建Neo4j Cypher执行引擎。它用于在Java应用程序中执行Neo4j CQL命令。

```java
ExecutionEngine execEngine = new ExecutionEngine(graphDb);
```

通过使用Neo4j Cypher Execution Engine，执行Neo4j CQL Command以检索CQL MATCH命令的结果。

```java
ExecutionResult execResult = execEngine.execute("MATCH (java:JAVA) RETURN java");
```

获取CQL命令结果的字符串，以在控制台中打印结果。

```java
String results = execResult.dumpToString();
System.out.println(results);
```

完整代码：

```java
package com.tp.neo4j.java.cql.examples;

import org.neo4j.cypher.javacompat.ExecutionEngine;
import org.neo4j.cypher.javacompat.ExecutionResult;
import org.neo4j.graphdb.GraphDatabaseService;
import org.neo4j.graphdb.factory.GraphDatabaseFactory;

public class JavaNeo4jCQLRetrivalTest {
    
   public static void main(String[] args) {
      GraphDatabaseFactory graphDbFactory = new GraphDatabaseFactory();

      GraphDatabaseService graphDb = graphDbFactory.newEmbeddedDatabase("C:/TPNeo4jDB");

      ExecutionEngine execEngine = new ExecutionEngine(graphDb);
      ExecutionResult execResult = execEngine.execute("MATCH (java:JAVA) RETURN java");
      String results = execResult.dumpToString();
      System.out.println(results);
   }
}
```

## 2). REST API

<http://localhost:7474/db/data/node/21>

## 3). Native Java API

创建Neo4j数据库

```java
GraphDatabaseFactory dbFactory = new GraphDatabaseFactory();
GraphDatabaseService db= dbFactory.newEmbeddedDatabase("C:/TPNeo4jDB");
```

启动Neo4j数据库事务以提交我们的更改

```java
try (Transaction tx = graphDb.beginTx()) {
	// Perform DB operations				
	tx.success();
}
```

创建节点，我们需要标签名称。 通过实现Neo4j Java API "Label"接口创建一个枚举。

```java
package com.tp.ne4oj.java.examples;
import org.neo4j.graphdb.Label;
public enum Tutorials implements Label {
	JAVA,SCALA,SQL,NEO4J;
}
```

创建节点并为其设置属性

```java
Node javaNode = db.createNode(Tutorials.JAVA);
Node scalaNode = db.createNode(Tutorials.SCALA);
```

设置属性

```java
javaNode.setProperty("TutorialID", "JAVA001");
javaNode.setProperty("Title", "Learn Java");
javaNode.setProperty("NoOfChapters", "25");
javaNode.setProperty("Status", "Completed");	
	
scalaNode.setProperty("TutorialID", "SCALA001");
scalaNode.setProperty("Title", "Learn Scala");
scalaNode.setProperty("NoOfChapters", "20");
scalaNode.setProperty("Status", "Completed");
```

创建关系，我们需要关系类型。 通过实现Neo4j“关系类型”创建枚举。

```java
package com.tp.neo4j.java.examples;
import org.neo4j.graphdb.RelationshipType;
public enum TutorialRelationships implements RelationshipType{
	JVM_LANGIAGES,NON_JVM_LANGIAGES;
}
```

创建节点之间的关系并设置它的属性。

```java
Relationship relationship = javaNode.createRelationshipTo(scalaNode,
	TutorialRelationships.JVM_LANGIAGES);
```

将属性设置为此关系

```java
relationship.setProperty("Id","1234");
relationship.setProperty("OOPS","YES");
relationship.setProperty("FP","YES");
```

完整代码：

```java
package com.tp.neo4j.java.examples;

import org.neo4j.graphdb.GraphDatabaseService;
import org.neo4j.graphdb.Node;
import org.neo4j.graphdb.Relationship;
import org.neo4j.graphdb.Transaction;
import org.neo4j.graphdb.factory.GraphDatabaseFactory;

public class Neo4jJavaAPIDBOperation {
    public static void main(String[] args) {
        GraphDatabaseFactory dbFactory = new GraphDatabaseFactory();
        GraphDatabaseService db= dbFactory.newEmbeddedDatabase("C:/TPNeo4jDB");
        try (Transaction tx = db.beginTx()) {

            Node javaNode = db.createNode(Tutorials.JAVA);
            javaNode.setProperty("TutorialID", "JAVA001");
            javaNode.setProperty("Title", "Learn Java");
            javaNode.setProperty("NoOfChapters", "25");
            javaNode.setProperty("Status", "Completed");				

            Node scalaNode = db.createNode(Tutorials.SCALA);
            scalaNode.setProperty("TutorialID", "SCALA001");
            scalaNode.setProperty("Title", "Learn Scala");
            scalaNode.setProperty("NoOfChapters", "20");
            scalaNode.setProperty("Status", "Completed");

            Relationship relationship = javaNode.createRelationshipTo
                (scalaNode,TutorialRelationships.JVM_LANGIAGES);
            relationship.setProperty("Id","1234");
            relationship.setProperty("OOPS","YES");
            relationship.setProperty("FP","YES");

            tx.success();
        }
        System.out.println("Done successfully");
    }
}
```

## 5). Spring-Data-Neo4j

Spring DATA Neo4j存储库

它提供了不同的API来支持不同的场景

- GraphRepository
- GraphTemplate
- CrudRepository
- PaginationAndSortingRepository

这些是Java类。 每个具有执行Neo4j数据库操作的特定目的

| S.No. | Spring 数据 Neo4j 类           | 用法                                                |
| ----- | ------------------------------ | --------------------------------------------------- |
| 1。   | GraphRepository                | 它用于执行Basic Neo4j DB操作。                      |
| 2。   | GraphTemplate                  | 像其他模块一样，它是执行Neo4j DB操作的Spring模板。  |
| 3。   | CrudRepository                 | 它用于使用Cypher查询语言（CQL）执行Neo4j CRUD操作。 |
| 4。   | PaginationAndSortingRepository | 它用于执行Neo4j CQL查询结果的分页和排序。           |

Spring DATA Neo4j模块Jar文件

```xml
<dependency>
   <groupId> org.springframework.data </groupId>
   <artifactId> spring-data-neo4j </artifactId>
   <version> 3.1.2.RELEASE </version>
</dependency>
```

Neo4j Jar文件，由Spring DATA Neo4j模块Jar文件内部使用

```xml
<dependency>
   <groupId> org.neo4j </groupId>
   <artifactId> neo4j-kernel </artifactId>
   <version> 2.1.3 </version>
</dependency>
```

Java事务API jar文件，由Spring DATA Neo4j模块Jar文件内部使用

```xml
<dependency>
   <groupId> javax.transaction </groupId>
   <artifactId> jta </artifactId>
   <version> 1.1 </version>
</dependency>
```

Java验证API jar文件，由Spring DATA Neo4j模块Jar文件内部使用

```xml
<dependency>
   <groupId> javax.validation </groupId>
   <artifactId> validation-api </artifactId>
   <version> 1.0.0.GA </version>
</dependency>
```

示例：

Spring DATA Neo4j模块注释

我们将使用以下Spring Framework注释来开发此应用程序。

| S.No. | Spring DATA Neo4j注释 | 用法                 |
| ----- | --------------------- | -------------------- |
| 1。   | @GraphEntity          | 定义域类Neo4j Entity |
| 2。   | @GraphID              | 定义节点或关系id     |
| 3。   | @GraphProperty        | 定义节点或关系属性   |

实现Spring DATA Neo4j应用程序的简要步骤 - 

- 开发图表实体或域或POJO类
- 开发DAO或存储库
- 开发服务层（如果需要）
- Spring DATA Neo4j XML配置

**开发图表实体或域或POJO类**

我们要实现equals（）和hashCode（）方法。
它不需要为“id”属性提供setter方法，因为Neo4j将负责分配此属性

```java
package com.tp.springdata.neo4j.domain;

import org.springframework.data.neo4j.annotation.GraphId;
import org.springframework.data.neo4j.annotation.NodeEntity;

@NodeEntity
public class GoogleProfile {
   @GraphId Long id;			
   private String name;
   private String address;
   private String sex;
   private String dob;

   public Long getId() {
      return id;
   }		
   public String getName() {
      return name;
   }
   public void setName(String name) {
      this.name = name;
   }
   public String getAddress() {
      return address;
   }
   public void setAddress(String address) {
      this.address = address;
   }
   public String getSex() {
      return sex;
   }
   public void setSex(String sex) {
      this.sex = sex;
   }
   public String getDob() {
      return dob;
   }
   public void setDob(String dob) {
      this.dob = dob;
   }
   public boolean equals(Object other) {
      if (this == other)
         return true;
      if (id == null) 
         return false;
      if (! (other instanceof GoogleProfile)) 
         return false;
      return id.equals(((GoogleProfile) other).id);
   }
   public int hashCode() {
      return id == null ? System.identityHashCode(this) : id.hashCode();
   }	
   public String toString(){
      return "Profile[id:"+ id +",name:"+ name +",sex:" + sex+ ",address:" + address + ",dob:" + dob +"]";
   }			
}
```

@GraphProperty是可选的，所以我们可以省略这个。 上面的实体同下。

```java
package com.tp.springdata.neo4j.domain;

import org.springframework.data.neo4j.annotation.GraphId;
import org.springframework.data.neo4j.annotation.NodeEntity;

@NodeEntity
public class GoogleProfile {
   @GraphId 
   private Long id;

   private String name;
   private String address;
   private String sex;
   private String dob;

   // Getter for id
   // Setters and Getters for rest of properties
   // implement equals() and hashCode() methods
}
```

**开发Spring DATA Neo4j存储库**

正如我们前面讨论的，我们需要通过扩展Spring DATA Neo4j API接口“GraphRepository”而不需要它的实现来开发接口。
Spring DATA Neo4j将在内部为此接口提供实现。
为我们的Domain类定义一个存储库或DAO接口：GoogleProfile

```java
package com.tp.springdata.neo4j.dao;

import org.springframework.data.neo4j.repository.GraphRepository;

public interface GoogleProfileRepository extends GraphRepository<GoogleProfile> { 
}
```

**发展服务层工件：接口和实现。**

最好在我们的应用程序中在DAO层之上提供一个Service层。

Service组件接口：

```java
package com.tp.springdata.neo4j.service;

import org.springframework.data.neo4j.conversion.Result;
import com.tp.springdata.neo4j.domain.GoogleProfile;

public interface GoogleProfileService {

   GoogleProfile create(GoogleProfile profile);
   void delete(GoogleProfile profile);		
   GoogleProfile findById(long id);		
   Result<GoogleProfile> findAll();
}
```

Service组件的实现：

```java
package com.tp.springdata.neo4j.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.neo4j.conversion.Result;
import org.springframework.stereotype.Service;

import com.tp.springdata.neo4j.dao.GoogleProfileRepository;
import com.tp.springdata.neo4j.domain.GoogleProfile;

@Service("googleProfileService")
public class GoogleProfileServiceImpl implements GoogleProfileService {

   @Autowired
   private GoogleProfileRepository googleProfileRepository;	

   public GoogleProfile create(GoogleProfile profile) {
      return googleProfileRepository.save(profile);
   }
   public void delete(GoogleProfile profile) {		
      googleProfileRepository.delete(profile);
   }
   public GoogleProfile findById(long id) {		
      return googleProfileRepository.findOne(id);
   }
   public Result<GoogleProfile> findAll() {		
      return googleProfileRepository.findAll();
   }
}
```

**Spring DATA Neo4j XML配置**

要运行基于Spring的应用程序，我们需要提供一些XML配置。
我们需要在Spring XML配置文件中提供以下详细信息

提供Spring Data Neo4j命名空间

```
xmlns:neo4j=http://www.springframework.org/schema/data/neo4j
```

提供Spring数据Neo4j模式定义（XSD文件）

```
xsi:schemaLocation="http://www.springframework.org/schema/data/neo4j    http://www.springframework.org/schema/data/neo4j/spring-neo4j.xsd"
```

spring-neo4j.xsd文件包含所有Spring Data Neo4j相关的XML标签

提供我们的Neo4j数据库位置和我们的图实体（域或POJO类）基础包

```xml
<neo4j:config storeDirectory="C:TPNeo4jDB" base-package="com.tp.springdata.neo4j.domain"/?>
```

这里storeDirectory =“C：\ TPNeo4jDB”指定我们的Neo4j数据库文件存储在我们的文件系统中的C：\ TPNeo4jDB位置。
base-package =“com.tp.springdata.neo4j.domain”
我们的所有图实体都有com.tp.springdata.neo4j.domain作为我们的应用程序类路径中的基础包

提供我们的Spring Data Neo4j存储库（DAO Interfaces）基础包。

```xml
<neo4j:repositories base-package="com.tp.springdata.neo4j.dao"/?>
```

我们的所有组件或服务都可以在我们的应用程序类路径中的“com.tp.springdata.neo4j.service”包完成“googleprofile.xml”

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<beans xmlns="http://www.springframework.org/schema/beans"
   xmlns:context="http://www.springframework.org/schema/context"
   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   xmlns:neo4j="http://www.springframework.org/schema/data/neo4j"
   xmlns:tx="http://www.springframework.org/schema/tx"
   xsi:schemaLocation="
      http://www.springframework.org/schema/beans 
      http://www.springframework.org/schema/beans/spring-beans.xsd
      http://www.springframework.org/schema/context 
      http://www.springframework.org/schema/context/spring-context.xsd
      http://www.springframework.org/schema/data/neo4j
      http://www.springframework.org/schema/data/neo4j/spring-neo4j.xsd
      http://www.springframework.org/schema/tx
      http://www.springframework.org/schema/tx/spring-tx.xsd">

   <context:component-scan base-package="com.tp.springdata.neo4j.service" />

   <neo4j:config storeDirectory="C:TPNeo4jDB" 
      base-package="com.tp.springdata.neo4j.domain"/>

   <neo4j:repositories base-package="com.tp.springdata.neo4j.dao"/>

   <tx:annotation-driven />
</beans>
```

**开发测试程序并测试所有操作**

```java
import java.util.Iterator;

import org.springframework.context.ApplicationContext;
import org.springframework.context.support.ClassPathXmlApplicationContext;
import org.springframework.data.neo4j.conversion.Result;

import com.tp.springdata.neo4j.service.GoogleProfileService;
import com.tp.springdata.neo4j.domain.GoogleProfile;

public class GoogleProfileTest {
   public static void main(String[] args) {
      ApplicationContext context = new ClassPathXmlApplicationContext("googleprofile.xml");		
      GoogleProfileService service = (GoogleProfileService) context.getBean("googleProfileService");

      // Please uncomment one of the operation section 
      // and comment remaining section to test only one operation at a time
      // Here I've uncommented CREATE operation and 
      // commented other operations: FIND ONE, FIND ALL, DELETE
      // CREATE Operation
      GoogleProfile profile = createPofile();
      createProfile(service,profile);		
      System.out.println("GoogleProfile created successfully.");

      // FIND ONE 
      /*
      GoogleProfile profile = getOneProfileById(service,67515L);		
      System.out.println(profile);
      */

      // FIND ALL
      /*
      getAllProfiles(service);		
      */

      // DELETE 
      /*
      GoogleProfile profile = createPofile();
      deleteProfile(service,profile);		
      System.out.println("GoogleProfile deleted successfully.");		
      */
   }
   
   private static GoogleProfile createProfile(GoogleProfileService service, GoogleProfile profile){
      return service.create(profile);
   }	
   
   private static void deleteProfile(GoogleProfileService service,GoogleProfile profile){
      service.delete(profile);
   }	
   
   private static GoogleProfile getOneProfileById(GoogleProfileService service,Long id){
      return service.findById(id);
   }	
   
   private static void getAllProfiles(GoogleProfileService service){
      Result<GoogleProfile> result = service.findAll();			
      Iterator<GoogleProfile> iterator = result.iterator();
      
      while(iterator.hasNext()){
         System.out.println(iterator.next());
      }
   }
   
   private static GoogleProfile createPofile(){
      GoogleProfile profile = new GoogleProfile();		
      profile.setName("Profile-2");
      profile.setAddress("Hyderabad");
      profile.setSex("Male");
      profile.setDob("02/02/1980");		
      return profile;
   }
}
```

# 4. 高级

## 分布式



