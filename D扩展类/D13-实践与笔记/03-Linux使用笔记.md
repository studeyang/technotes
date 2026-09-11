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

## 六、文件操作

```shell
# 查找 /etc 目录下是否存在 nginx.conf 文件
find /etc -name "nginx.conf"
# 查找log目录
find / -type d -name "log"

# 查关键字 HR11 并输出后 10 行
line=$(grep -n "HR11" info.log | tail -1 | cut -d: -f1); tail -n +$line info.log | head -n 10
```

## 七、用户操作

```bash
# 给mwopr用户授权访问 /home/mwopr/及所有子目录下的文件
sudo chown -R mwopr:mwopr /home/mwopr/
```

## 八、Docker

### 下载镜像

选择镜像网站：docker.1ms.run

```bash
docker pull docker.1ms.run/zookeeper:latest
```


### 打镜像

```bash
docker build -t fcbox/gp-skyeye-server:v1.47.0 .
```

### 启动容器

```bash
docker run -d \
  -p 8080:8080 \
  -e SPRING_PROFILES_ACTIVE=uat6 \
  -e JAVA_OPTS="-Xms512m -Xmx2048m -XX:+UseG1GC" \
  --name=gp-skyeye-server \
  fcbox/gp-skyeye-server:v1.47.0
```

### 删除镜像

```bash
#停止容器
docker stop gp-skyeye-server
#删除容器
docker rm gp-skyeye-server
#删除镜像
docker rmi fcbox/gp-skyeye-server:v1.47.0
```

### 本地镜像

```bash
#打包镜像
docker save fcbox/gp-skyeye-server:v1.47.0 | gzip > gp-skyeye-server-v1.47.0.tar.gz
#加载镜像
docker load -i gp-skyeye-server-v1.47.0.tar.gz
```

## 九、Kubernetes

```bash
# 查看 pod
kubectl get pods -n sit6
# 进入 pod 命令行
kubectl exec -it fc-ops-agent-sit6-5d5cd4d9bf-w5n9c -n sit6 -- /bin/bash
# 查看日志
cat /app/applogs/fc-ops-agent/info.log | grep "stream request | agent="
```

