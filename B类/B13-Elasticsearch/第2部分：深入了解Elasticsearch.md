# 第4章：深入搜索

**基于 Term 的查询**

Term 是表达语意的最小单位。在 ES 中， Term 查询不会对输入做分词，而是将输入作为一个整体，在倒排索引中查找准确的词项， 并且使用相关度算分公式为每个包含该词项的文档进行相关度算分。

首先，创建4条记录。

```json
POST /products/_bulk
{ "index": { "_id": 1 }}
{ "productID" : "XHDK-A-1293-#fJ3","desc":"iPhone" }
{ "index": { "_id": 2 }}
{ "productID" : "KDKE-B-9947-#kL5","desc":"iPad" }
{ "index": { "_id": 3 }}
{ "productID" : "JODL-X-1937-#pV7","desc":"MBP" }
```

再通过 productID 查询：

```json
POST /products/_search
{
  "query": {
    "term": {
      "productID": {
        "value": "XHDK-A-1293-#fJ3"
      }
    }
  }
}
```

查出的结果为空，可以通过对 "XHDK-A-1293-#fJ3" 进行分词分析。改为下述搜索，就可以查出结果了。

```json
POST /products/_search
{
  //"explain": true,
  "query": {
    "term": {
      "productID.keyword": {
        "value": "XHDK-A-1293-#fJ3"
      }
    }
  }
}
```

**全文本查询**

全文查询时会进行分词，查询字符串首先会传递到一个合适的分词器，然后生成一个供查询的词项列表，并对每个词项进行查询，最后将结果进行合并。

例如查 “Matrix reloaded”，会查到包括 Matrix 或者 reload的所有结果。

![image-20220117225232717](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220117225238.png)

整个 Match Query 的查询过程如下：

![image-20220117225353805](/Users/yanglulu/Library/Application Support/typora-user-images/image-20220117225353805.png)

**结构化搜索**

结构化搜索（Structured search） 是指对结构化数据的搜索。

样例数据如下：

```json
DELETE products
POST /products/_bulk
{ "index": { "_id": 1 }}
{ "price" : 10,"avaliable":true,"date":"2018-01-01", "productID" : "XHDK-A-1293-#fJ3" }
{ "index": { "_id": 2 }}
{ "price" : 20,"avaliable":true,"date":"2019-01-01", "productID" : "KDKE-B-9947-#kL5" }
{ "index": { "_id": 3 }}
{ "price" : 30,"avaliable":true, "productID" : "JODL-X-1937-#pV7" }
{ "index": { "_id": 4 }}
{ "price" : 30,"avaliable":false, "productID" : "QQPX-R-3956-#aD8" }
```

- 布尔值

```json
#对布尔值 match 查询，有算分
POST products/_search
{
  "profile": "true",
  "explain": true,
  "query": {
    "term": {
      "avaliable": true
    }
  }
}
```

- 数字类型

```json
#数字类型 Term
POST products/_search
{
  "profile": "true",
  "explain": true,
  "query": {
    "term": {
      "price": 30
    }
  }
}
```

- 日期类型

```json
# 日期 range
POST products/_search
{
    "query" : {
        "constant_score" : {
            "filter" : {
                "range" : {
                    "date" : {
                      "gte" : "now-1y"
                    }
                }
            }
        }
    }
}
```

**搜索的相关性算分**

搜索的相关性(Relevance)算分，描述了一个⽂档和查询语句匹配的程度。 ES 会对每个匹配查询条件的结果进行算分(_score)。

打分的本质是排序，需要把最符合用户需求的文档排在前面。 ES 5 之前，默认的相关性算分采用 TF-IDF，现在采用 BM 25。先来了解 TF-IDF。

- 词频 TF（Term Frequency）

检索词在⼀篇文档中出现的频率，即检索词出现的次数除以⽂档的总字数。

- 逆⽂档频率 IDF（Inverse Document Frequency）

DF：检索词在所有文档中出现的频率。IDF= log(全部⽂档数/检索词出现过的文档总数）

TF-IDF 被公认为是信息检索领域最重要的发明，Lucene 中的 TF-IDF 评分公式如下：

![image-20220118222933895](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220118222934.png)

再来看 BM 25。和经典的TF-IDF相比，当 TF 无限增加时，BM 25算分会趋于⼀个数值。

![image-20220118223145299](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220118223145.png)

我们可以通过 explain 查看 TF-IDF的值。

![image-20220118224352821](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220118224352.png)

也可以对算分的规则进行自定义。

![image-20220118224435909](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220118224435.png)

**多字符串多字段查询**

假设要搜索一本电影，包含了以下一些条件：

评论中包含了 Guitar，⽤户打分高于 3 分，同时上映⽇期要在 1993 与 2000 年之间。

这时就需要用到多字段查询了，即 bool 查询。

![image-20220118230218718](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220118230218.png)

在 Elasticsearch 中，有Query 和 Filter 两种不同的 Contex。Query Context 表示进行相关性算分；Filter Context 表示不需要算分（ Yes or No），可以利⽤ Cache， 获得更好的性能。

bool 查询，总共包括 4 种子句。其中 2 种会影响算分， 2 种不影响算分。

以下面数据为例。

```json
POST /products/_bulk
{ "index": { "_id": 1 }}
{ "price" : 10,"avaliable":true,"date":"2018-01-01", "productID" : "XHDK-A-1293-#fJ3" }
{ "index": { "_id": 2 }}
{ "price" : 20,"avaliable":true,"date":"2019-01-01", "productID" : "KDKE-B-9947-#kL5" }
{ "index": { "_id": 3 }}
{ "price" : 30,"avaliable":true, "productID" : "JODL-X-1937-#pV7" }
{ "index": { "_id": 4 }}
{ "price" : 30,"avaliable":false, "productID" : "QQPX-R-3956-#aD8" }
```

![image-20220118230332261](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220118230332.png)

![image-20220118230345412](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220118230345.png)

**单字符串多字段查询**

在 Google 搜索引擎中就是这样一种场景，对于这种场景，通常需要用到 Disjunction Max Query。

样例数据如下：

```json
PUT /blogs/_doc/1
{
    "title": "Quick brown rabbits",
    "body": "Brown rabbits are commonly seen."
}

PUT /blogs/_doc/2
{
    "title": "Keeping pets healthy",
    "body": "My quick brown fox eats rabbits on a regular basis."
}
```

![image-20220120221441851](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/learn/20220120221441.png)



