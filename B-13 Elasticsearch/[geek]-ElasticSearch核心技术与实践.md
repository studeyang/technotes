# 第一部分：初识 Elasticsearch

## 第1章：概述

**课程介绍**

本课程基于 es 7.1 版本

**内容综述及学习建议**

从三个层面学习：
开发：基本功能，底层原理，数据建模；
运维：容量规划；性能优化；问题诊断；滚动升级；
方案：解决搜索问题；大数据分析实践

## 第2章：安装上手

**Elasticsearch 的安装与简单配置**

- 安装插件

  bin/elasticsearch-plugin list

  安装分词插件：bin/elasticsearch-plugin install analysis-icu

- 集群

  bin/elasticsearch -E node.name=node1 -E cluster.name=geektime -E path.data=node1_data -d

  删除进程：ps grep | elasticsearch / kill pid

  查看集群：localhost:9200/_cat/nodes

**Kibana 的安装与界面快速浏览**

- localhost:5601

- 工具：Dev Tools

- Kibana Plugins

**在 Docker 容器中运行 Elasticsearch Kibana 和 Cerebro**

- Docker 中运行

  运行 docker-compose up

  docker-compose down

  docker-compose down -v

  docker stop / rm containerID

- Cerebro

  查看集群状态

  localhost:9000

**Logstash 安装与导入数据**

可导入csv数据

- 相关操作命令

  sudo ./logstash -f logstash.conf

## 第3章：Elasticsearch 入门

**基本概念：索引、文档和 REST API**

- 文档

  文档是所有可探索数据的最小单元，相当于 MySQL 表中的一条记录；

  元数据：_index, _type, _id, _source, _all, _version, _score

- 索引

  索引是文档的容器，是一类文档的结合；

- Type

  7.0 之前，一个 Index 可以设置多个 Types

- REST API

  ![image-20200917235323174](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/image-20200917235323174.png)

**基本概念：节点、集群、分片及副本**

- 分布式特性

  高可用&可扩展

- 节点

  是一个 Elasticsearch 实例，每一个节点的名字可通过配置文件配置，或者启动时 -E node.name=node1 指定；

  1. Master-eligible nodes 和 Master Node

     每个节点启动后，默认就是一个 Master eligible 节点，Master-eligible 节点可以参加选主流程，成为 Master 节点；

  2. Data Node & Coordinating Node

     Data Node：可以保存数据的节点，负责保存分片数据；

     Coordinating Node：负责接受 Client 的请求，将请求分发到合适的节点，最终把结果汇集到一起；

  3. 其他的节点类型

     Hot & Warm Node：不同硬件配置的 Data Node，用来实现 Hot & Warm 架构；

     Machine Learning Node：负责跑机器学习的 Job，用来做异常检测；

     Tribe Node：连接到不同的 Elasticsearch 集群，支持将这些集群当成一个单独的集群处理；（5.3开始使用 Cross Cluster Search）

- 分片

  主分片（Primary Shard）：用以解决数据水平扩展的问题，将数据分布到集群内的所有节点之上；

  副本（Replica Shard）：用以解决数据高可用的问题，分片是主分片的拷贝；

  ![image-20200918001419658](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/image-20200918001419658.png)

  查看集群的健康状况：GET _cluster/health

**文档的基本 CRUD 与批量操作**

- Index

  Type 名，约定都用 _doc。

  如果 ID 不存在，则创建新的文档；否则，先删除现有的文档，再创建新的文档，版本会增加。

  ```json
  PUT my_index/_doc/1
  {"user":"mike", "comment":"You know, for search"}
  ```

- Create

  如果 ID 已经存在，会失败。

  ```json
  PUT my_index/_create/1
  {"user":"mike", "comment":"You know, for search"}
  
  PUT my_index/_doc // 不指定 ID，自动生成
  {"user":"mike", "comment":"You know, for search"}
  ```

- Read

  ```json
  GET users/_doc/1
  ```

- Update

  文档必须已经存在，更新只会对相应字段做增量修改。

  ```json
  POST my_index/_update/1
  {"doc":{"user":"mike", "comment":"You know, for search"}}
  ```

- Delete

  ```json
  DELETE my_index/_doc/1
  ```

- Bulk API

  支持在一次 API 调用中，对不同的索引进行操作。支持四种类型操作：Index、Create、Update、Delete

  ```json
  POST _bulk
  {"index": {"_index": "test", "_id": "1"}}
  {"field1": "value1"}
  {"delete": {"_index": "test", "_id": "2"}}
  {"create": {"_index": "test2", "_id": "3"}}
  ```

- 批量读取 - mget

  批量操作，可以减少网络连接所产生的开销，提高性能。

  ```json
  GET _mget
  {
      "docs": [
          {
              "_index": "user",
              "_id": 1
          },
          {
              "_index": "comment",
              "_id": 1
          }
      ]
  }
  ```

  

- 批量查询 - msearch

  ```json
  POST kibana_sample_data_ecommerce/_msearch
  {}
  {"query": {"match_all": {}}, "size": 1}
  {"index": "kibana_sample_data_flights"}
  {"query": {"match_all": {}}, "size": 2}
  ```

**倒排索引介绍**

- 正排索引

  类似于书的目录页，是文档 Id 到文档内容的关联。

  ![image-20200918234732001](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/image-20200918234732001.png)

- 倒排索引

  类似于书的索引页，是单词到文档 Id 的关系。

  ![image-20200918234824217](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/image-20200918234824217.png)

- 倒排索引的核心组成

  1. 单词词典（Term Dictionary）

     记录所有文档的单词，记录单词到倒排列表的关联关系。单词词典一般比较大，可以通过 B+ 树或哈希链法实现，以满足高性能的插入与查询。

  2. 倒排列表（Posting List）

     记录了单词对应的文档集合，由倒排索引项组成。倒排索引项分为：文档 ID、词频 TF、位置（Position）、偏移（Offset）。

     ![image-20200918235940141](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/image-20200918235940141.png)

**通过 Analyzer 进行分词**

- Analysis 与 Analyzer

  Analysis：把全文本转换一系列单词的过程，也叫分词。Analysis 是通过 Analyzer 来实现的。

- Analyzer 的组成

  Analyzer 由三部分组成：

  1. Character Filters（针对原始文本处理，例如去除 html）
  2. Tokenizer（按照规则切分为单词）
  3. Token Filter（将切分的单词进行加工，例如小写、删除 stopwords、增加同义词）

- 使用 _analyzer API

  指定 Analyzer 进行测试：

  ```json
  GET /_analyze
  {
      "analyzer":"standard",
      "text":"Mastering Elasticsearch, elasticsearch in Action"
  }
  ```

  指定索引的字段进行测试：

  ```json
  POST books/_analyze
  {
      "field":"title",
      "text":"Mastering Elasticsearch"
  }
  ```

  自定义分词器进行测试：

  ```json
  POST /_analyze
  {
      "tokenizer":"standard",
      "filter":["lowercase"],
      "text":"Mastering Elasticsearch"
  }
  ```

- Standard Analyzer

  是 Elasticsearch 的默认分词器，按词切分，并进行小写处理。

  Tokenizer: Standard

  Tolen Filters: Standard, Lower Case, Stop(默认关闭)

- Simple Analyzer

  按照非字母切分，非字母的都被去除，并进行小写处理。

- Whitespace Analyzer

  按照空格切分。

- Stop Analyzer

  相比 Simple Analyzer，多了 stop filter，会把 the, a, is 等修饰性词语去除。

- Pattern Analyzer

  通过正则表达式进行分词，默认是`\W+`，非字符的符号进行分隔。

  Tokenizer: Pattern

  Token Filters: Lower Case, Stop

- ICU Analyzer

  提供了 Unicode 的支持，更好的支持亚洲语言。

  Character Filters: Normalization

  Tokenizer: ICU Tokenizer

  Token Filters: Normalization, Folding, Collation, Transform

- 更多的中文分词器

  [IK](https://github.com/medcl/elasticsearch-analysis-ik)：支持自定义词库，支持热更新分词字典。

  [THULAC](https://github.com/microbun/elasticsearch-thulac-plugin)：THU Lexucal Analyzer for Chinese，清华大学自然语言处理和社会人文计算实验室的一套中文分词器。

**Search API 概览**

- Search API

  Search API 可以分为两大类：

  1. URI Search: 在URL中使用查询参数；

  2. Request Body Search: 使用 Elasticsearch 提供的，基于 JSON 格式的更加完备的 Query Domain Specific Language(DSL)；

     | 语法                   | 范围              |
     | ---------------------- | ----------------- |
     | /_search               | 集群上所有的索引  |
     | /index1/_search        | index1            |
     | /index1,index2/_search | index1和index2    |
     | /index*/_search        | 以index开关的索引 |

- URI 查询

  使用"q"，指定查询字符串；使用"query string syntax"，指定KV键值对。 

  ```http
  curl -XGET "http://elasticsearch:9200/kibana_sample_data_ecommerce/_search?q=customer_first_name:Eddie"
  ```

  上面例子是搜索名叫 Eddie 的客户。

- Request Body

  ```http
  curl -XGET "http://elasticsearch:9200/kibana_sample_data_ecommerce/_search" -H 'Content-Type:application/json' -d'
  {
    "query":{
      "match_all":{}
    }
  }'
  ```

  match_all：表示返回所有的文档；

- 搜索 Response

  ```json
  {
      "took":10, // 花费的时间
      "timed_out":false,
      "_shards":{
          "total":1,
          "successful":1,
          "skipped":0,
          "failed":0
      },
      "hits":{
          "total":4675, // 符合条件的总文档数
          "max_score":1,
          "hits":[
              {// 结果集，默认前10个文档
                  "_index":"kibana_sample_data_ecommerce",
                  "_type":"_doc",
                  "_id":"CbLKM2kBi-meogBbuexM",
                  "_score":1,// 相关度评分
                  "_source":{// 原始文档信息
                      "category":[
                          "Men's Clothing"
                      ],
                      "currency":"EL",
                      "customer_first_name":"Eddie"
                  }
              }
          ]
      }
  }
  ```

**URI Search 详解**

- URI Search

  通过 URI query 实现搜索。

  ```json
  GET /movies/_search?q=2012&df=title&sort=year:desc&from=0&size=10&timeout=1s
  {
      "profile":"true"
  }
  ```

  q: 指定查询语句，使用Query String Syntax

  df: 默认字段，不指定时，会对所有字段进行查询

  sort: 排序 / from 和 size 用于分页

  profile: 可以查看查询是如何被执行的

- Query String Syntax

  1. 指定字段 vs 泛查询

     q=title:2012 / q=2012

     ```json
     GET /movies/_search?q=2012&df=title
     {
         "profile":"true"
     }
     ```

  2. Term vs Phrase

     Beautiful Mind 等效于 Beautiful OR Mind

     "Beautiful Mind"，等效于 Beautiful AND Mind。Phrase 查询，还要求前后顺序保持一致

     ```json
     GET /movies/_search?q=title:"Beautiful Mind"
     {
         "profile":"true"
     }
     ```

  3. 分组与引号

     title:(Beautiful AND Mind)

     title="Beautiful Mind"

  4. 布尔操作

     AND / OR / NOT 或者 && / || / !

  5. 范围查询

     区间表示：[] 闭区间，{} 开区间

     year:{2019 TO 2018}

     year:[* TO 2018]

  6. 通配符查询

     ? 代表 1个字符，* 代表 0 或多个字符

  7. 正则表达式

     title:[bt]oy

  8. 模糊匹配与近似查询

     title:beautifl~1

     title:"Lord Rings"~2

**Request Body 与 Query DSL 简介**

- Request Body Search

  分页，排序，_source filtering

- 脚本字段

  可对字段使用脚本进行计算

- 使用查询表达式 - Match

  ```json
  GET /comments/_doc/_search
  {
      "query":{
          "match":{
              "comment":"Last Christmas",
              "operator":"AND" // Last Christmas同时出现
          }
      }
  }
  ```

- 短语搜索 - Match Phrase

  ```json
  GET /comments/_doc/_search
  {
      "query":{
          "match_phrase":{
              "comment":{
                  "query":"Song Last Chrismas"
                  "slop":1 // 每个词语中间可以有1个字符出现
              }
          }
      }
  }
  ```

**Query String & Simple Query String 查询**

- Query String

  ```json
  POST users/_search
  {
      "query":{
          "query_string":{
              "default_field":"name",
              "query":"Ruan AND Yiming"
          }
      }
  }
  ```

- Simple Query String

  ```json
  POST user/_search
  {
      "query":{
          "simple_query_string":{
              "query":"Ruan Yiming",
              "fields":["name"],
              "default_operator":"AND"
          }
      }
  }
  ```

**Dynamic Mapping 和常见字段类型**

- 什么是 Mapping

  Mapping 类似数据库中的 schema 的定义，作用如下：
  定义索引中的字段的名称、定义字段的数据类型、倒排索引的相关配置。

- 字段的数据类型

  简单类型：Text/Keyword, Date, Integer/Floating, Boolean, IPv4 & IPv6

  复杂类型：对象和嵌套对象

  特殊类型：geo_point & geo_shape / percolator

- 什么是 Dynamic Mapping

  在写入文档时，如果索引不存在，会自动创建索引

- 类型的自动识别

  | JSON 类型 | Elasticsearch 类型                                           |
  | --------- | ------------------------------------------------------------ |
  | 字符串    | 匹配日期格式，设置成 Date<br />配置数字设置为 float 或者 long，该选项默认关闭<br />设置为 Text，并且增加 keyword 子字段 |
  | 布尔值    | boolean                                                      |
  | 浮点数    | float                                                        |
  | 整数      | long                                                         |
  | 对象      | Object                                                       |
  | 数组      | 由第一个非空数值的类型所决定                                 |
  | 空值      | 忽略                                                         |

- 更改 Mapping 的字段类型

  1. 对新增加字段

     Dynamic 设为 true 时，一旦有新增字段的文档写入，Mapping 也同时被更新；

     Dynamic 设为 false，Mapping 不会被更新，新增字段的数据无法被索引，但是信息会出现在 _source 中；

     Dynamic 设为 Strict，文档写入失败；

  2. 对已有字段

     一旦有数据写入，就不再支持修改字段定义，基于 Lucence 实现的倒排索引，一旦生成后，就不允许修改。

     如果希望改变字段类型，必须 Reindex API，重建索引。

- 控制 Dynamic Mappings

  |                | true | false | strict |
  | -------------- | ---- | ----- | ------ |
  | 文档可索引     | YES  | YES   | NO     |
  | 字段可索引     | YES  | NO    | NO     |
  | Mapping 被更新 | YES  | NO    | NO     |

**显示 Mapping 设置与常见参数介绍**

```json
PUT users
{
    "mappings":{
        "properties":{
            "firstName":{
                "type":"text"
            },
            "lastName":{
                "type":"text"
            },
            "mobile":{
                "type":"text",
                "index":false
            },
            "bio":{
                "type":"text",
                "index_options":"offsets"
            }
        }
    }
}
```

四种不同级别的 Index Options 配置，可以控制倒排索引记录的内容：

- docs：记录doc id
- freqs：记录 doc id 和 term frequencies
- positions：记录 doc id / term frequencies / term position
- offsets：doc id / term frequencies / term position / character offects

**多字段特性及 Mapping 中配置自定义 Analyzer**

- 多字段类型

  厂商名字实现精确匹配

- 自定义分词

  当 Elasticsearch 自带的分词器无法满足时，可以自定义分词器。

  Character Filters：在 Tokenizer 之前对文本进行处理；

  Tokenizer：将原始的文本按照一定的规则，切分为词；

  Token Filters：将 Tokenizer 输出的单词进行增加、修改、删除；

**Index Template 和 Dynamic Template**

- Index Template

  Index Template 可以帮助你设定 Mappings 和 Settings，并按照一定的规则，自动匹配到新创建的索引之上。

- Dynamic Template

  根据 Elasticsearch 识别的数据类型，结合字段名称，来动态设定字段类型。

**Elasticsearch 聚合分析简介**

- 聚合（Aggregation）

  Elasticsearch 除搜索以外，提供的针对 ES 数据进行统计分析的功能。

- 集合的分类

  Bucket Aggregation：一些满足特定条件的文档的集合；

  Metric Aggregation：一些数学运算，可以对文档字段进行统计分析；

  Pipeline Aggregation：对其他的聚合结果进行二次聚合；

  Matrix Aggregration：支持对多个字段的操作并提供一个结果矩阵；

**第一部分总结**

- 产品与使用场景

  搜索和聚合两大功能。

- 基本概念

  节点、索引、分片、文档、索引（indexing）

- 搜索和 Aggregation

  Precosion、Recall、全文本、Analysis、Analyzer、_analyze API、URI Search、REST Body

  Bucket、Metric、Pipeline、Matrix

- 文档 CRUD 与 Index Mapping

  bulk, mget, msearch

  每个索引都有一个 Mapping 定义；Mapping 可以被动态的创建；Mapping可以动态创建；可自定义 analyzer；Index Template 可以定义 Mapping 和 Settings；Dynamic Template 支持在具体的索引上指定规则；

# 第二部分：深入了解 Elasticsearch

## 第4章：深入搜索

## 第5章：分布式特性及分布式搜索的机制

## 第6章：深入聚合分析

## 第7章：数据建模

# 第三部分：管理 Elasticsearch 集群

## 第8章：保护你的数据

## 第9章：水平扩展 Elasticsearch 集群

## 第10章：生产环境中的集群运维

## 第11章：索引生命周期管理

# 第四部分：利用 ELK 做大数据分析

## 第12章：用 Logstash 和 Beats 构建数据管道

## 第13章：用 Kibana 进行数据可视化分析

## 第14章：探索 X-Pack 套件

# 第五部分：应用实战工作坊

## 实战1：电影探索服务

## 实战2：Stackoverfow 用户调查问卷分析

## 备战：Elastic 认证

