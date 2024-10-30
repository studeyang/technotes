## 一、统计失败的日期范围

```sql
SELECT MIN(created_at), MAX(created_at) FROM fail_message;
```

## 二、按日期统计消费失败记录数

```sql
SELECT DATE_FORMAT(created_at, '%Y-%m-%d'), COUNT(*) 
FROM fail_message 
GROUP BY DATE_FORMAT(created_at, '%Y-%m-%d');
```

##  三、统计失败原因

```sql
SELECT reason, count(*) 
FROM fail_message 
WHERE created_at BETWEEN '2021-01-04 00:00:00' AND '2021-01-04 23:59:59' 
GROUP BY right(reason, 100);
```

