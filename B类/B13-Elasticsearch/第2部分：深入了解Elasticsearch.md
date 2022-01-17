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

![image-20220117225232717](https://gitee.com/yanglu_u/img2022/raw/master/learn/20220117225238.png)

整个 Match Query 的查询过程如下：

![image-20220117225353805](https://gitee.com/yanglu_u/img2022/raw/master/learn/20220117225353.png)



结构化搜索

搜索的相关性算分

Query Context&Filtering Context

多字符串多字段查询



# 第5章：分布式特性及分布式搜索的机制

# 第6章：深入聚合分析

# 第7章：数据建模

