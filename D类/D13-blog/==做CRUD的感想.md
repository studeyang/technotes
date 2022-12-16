#35岁与技术瓶颈，哪一个先到来？

写了一个月的 CRUD 了，其实发现，写业务代码并不是简单的代码搬运，也就是“搬砖”。

它还有一些有趣的地方。

#从简单的CRUD中寻找/创造轮子

项目中引入了 MyBatisPlus，从此告别了写 MyBatis Mapper；

###查询表

比如我要查询下面的 SQL 语句。

```sql
select id, invoice_code, invoice_no from invoice where invoice_code in (?, ?) and invoice_no in(?, ?)
```

使用 MyBatis 会怎么做呢？首先在 InvoiceMapper.xml 添加相应的查询配置。

然而现在我只需要写下面代码就可完成。

```java
Wrapper condition = new Condition()
                .in("invoice_code", invoiceCode)
                .in("invoice_no", invoiceNo)
                .setSqlSelect("id", "invoice_code", "invoice_no");

List<InvoiceEntity> entities = selectList(condition);
```

#勤劳能致富吗？

环卫工人每天4，5点就起床了，

> 请不要误解，这里我只想以此来加强我的观点。

勤奋学习成绩就一定好吗？以我自身为例，高中时期