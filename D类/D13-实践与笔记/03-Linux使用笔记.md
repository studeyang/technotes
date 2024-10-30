## 一、循环调用接口

```shell
# !/bin/bash

for i in {100..786}
do
  id="sdbc0$i"
  data="{\"ids\":[\"$id\"],\"startTime\":\"2021-07-03 00:00:00\",\"endTime\":\"2021-07-03 23:59:59\"}"
  curl -v -H "accept: */*" -H "Content-Type:application/json" -X POST http://xxx/a -d "$data" >> reconsume.log
done
```

## 二、带颜色输出

```shell
# 蓝色
echo -e "\033[32m success. \033[0m"
```

##  三、查看某个进程的线程数

```shell
cat /proc/1/status | grep Threads
```

## 四、查看某命令的进程号

```shell
pgrep -f 'docsify serve -p 4000'
```

## 五、查看本机ip地址

```shell
hostname -I
```

