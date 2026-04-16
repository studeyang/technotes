# 01 | SQL语句执行顺序

![image-20211207155619563](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/image-20211207155619563.png)

1. FORM: 对FROM的左边的表和右边的表计算笛卡尔积。产生虚表VT1
2. ON: 对虚表VT1进行ON筛选，只有那些符合`<join-condition>`的行才会被记录在虚表VT2中。
3. JOIN： 如果指定了OUTER JOIN（比如left join、 right join），那么保留表中未匹配的行就会作为外部行添加到虚拟表VT2中，产生虚拟表VT3, 如果 from子句中包含两个以上的表的话，那么就会对上一个join连接产生的结果VT3和下一个表重复执行步骤1~3这三个步骤，一直到处理完所有的表为止。
4. WHERE： 对虚拟表VT3进行WHERE条件过滤。只有符合`<where-condition>`的记录才会被插入到虚拟表VT4中。
5. GROUP BY: 根据group by子句中的列，对VT4中的记录进行分组操作，产生VT5.（从此开始使用select中的别名，后面的语句中都可以使用）
6. CUBE|ROLLUP|SUM|AVG: 对表VT5进行sum或者avg操作，产生表VT6.
7. HAVING： 对虚拟表VT6应用having过滤，只有符合`<having-condition>`的记录才会被 插入到虚拟表VT7中。
8. SELECT： 执行select操作，选择指定的列，插入到虚拟表VT8中。
9. DISTINCT： 对VT8中的记录进行去重。产生虚拟表VT9.
10. ORDER BY: 将虚拟表VT9中的记录按照<order_by_list>进行排序操作，产生虚拟表VT10.
11. LIMIT：取出指定行的记录，产生虚拟表VT11, 并将结果返回。  

# 02 | 看懂执行计划

![image-20211207155807199](https://technotes.oss-cn-shenzhen.aliyuncs.com/2021/image-20211207155807199.png)

1. id： id是一组数字，表示查询中执行select子句或操作表的顺序，如果id相同，则执行顺序从上至下，如果是子查询， id的序号会递增， id越大则优先级越高，越先会被执行。
2. select_type：查询类型，有simple、 primary、 subquery、 dependent subquery、 derived、 union、 dependent union、 union result等
3. table：显示的查询表名，如果查询使用了别名，那么这里显示的是别名。如果不涉及对数据表的操作，那么这显示为null。如果显示为尖括号括起来的`<derived N>`就表示这个是临时表，后边的N就是执行计划中的id，表示结果来自于这个查询产生。  
4. **type**：依次从好到差： system， const， eq_ref， ref， fulltext， ref_or_null， unique_subquery，index_subquery， range， index_merge， index， ALL。除了all之外，其他的type都可以使用到索引，除了index_merge之外，其他的type只可以用到一个索引。
5. **possible_keys**：查询可能使用到的索引都会在这里列出来。
6. **key**：查询真正使用到的索引， select_type为index_merge时，这里可能出现两个以上的索引，其他的select_type这里只会出现一个。  
7. key_len：用于处理查询的索引长度，如果是单列索引，那就整个索引长度算进去，如果是多列索引，那么查询不一定都能使用到所有的列，具体使用到了多少个列的索引，这里就会计算进去，没有使用到的列，这里不会计算进去。
8. ref：如果是使用的常数等值查询，这里会显示const，如果是连接查询，被驱动表的执行计划这里会显示驱动表的关联字段，如果是条件使用了表达式或者函数，或者条件列发生了内部隐式转换，这里可能显示为func。
9. **rows**：这里是执行计划中估算的扫描行数，不是精确值。
10. extra：这个列可以显示的信息非常多，有几十种，常用的有： distinct、 using filesort、 using index、 using temporary

# 03 | 计算字段区分度

计算公式：对字段去重统计值/表总行统计值。

例：select count(distinct pay_time)/count(1) from trade_flow  







