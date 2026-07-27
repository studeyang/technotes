## 一、下载镜像

选择镜像网站：docker.1ms.run

```
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



