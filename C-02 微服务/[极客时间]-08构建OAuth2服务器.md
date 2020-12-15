# 139 | 课程概述和背景

**Why Golang?**

- 简单入门门槛低，适合课程讲解
- Google 开发支持，社区生态好
- 云原生基础语言（k8s/docker/etcd/istio）
- 微服务多语言（polyglot）开发趋势
- OAuth2实现和具体语言无关

**课程大纲**

139. 课程概述和背景
140. 架构和设计
141. 开发环境搭建（Lab01）
142. 基础代码（Code Review）
143. 数据访问模块（Code Review）
144. OAuth2服务模块（Code Review）
145. Web服务模块（Code Review）
146. 启动流程（Code Review）
147. 起步准备实验（Lab02）
148. OAuth2授权码模式实验（Lab03）
149. OAuth2简化模式实验（Lab04）
150. OAuth2用户名密码模式实验（Lab05）
151. OAuth2客户端模式实验（Lab06）
152. OAuth2令牌校验实验（Lab07）
153. OAuth2令牌刷新实验（Lab08）
154. 项目复盘和扩展环境
155. 参考资料

# 140 | 架构和设计

**总体架构**

![image-20201213223546190](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201213223556.png)

**数据模型**

![image-20201215225448872](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201215225448.png)

**接口模型**

![image-20201213224924821](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201213224924.png)

以上三个方面是一个系统本质，无论使用什么语言实现，都离不开这三方面。

# 141 | 开发环境搭建

实验代码：spring2go/gravitee_lab

工程代码：spring2go/gravitee

大致步骤：

1. 安装 GO（Golang中国下载）

   GOROOT：GO安装目录；

   GOPATH：GO工作目录；

   这2个目录的 bin 可以添加到环境变量 Path。

2. 下载 VS CODE；

3. 安装 go 扩展插件；

4. Hello World；

5. 安装 glide 包管理工具

   ```
   go get github.com/Masterminds/glide
   go install github.com/Masterminds/glide
   ```

   ```
   glide install
   ```

   install 后会多一个 vendor 目录。

# 142 | 基础代码（Code Review）

**项目结构**

```
|--cmd
|--config
|--database
|--health
|--log
|--models    领域模型
|--oauth
|--public
|--services
|--session
|--test-util
|--user
|--util
|--vendor    依赖库
|--web
```

# 143 | 数据访问模块（Code Review）

**common.go**

- MyGormModel

  这是一个超类，定义了公共字段。

**migrations.go**

创建表、建立模型间的依赖关系。

**oauth.go**

使用gorm定义ORM。

# 144 | OAuth2服务模块（Code Review）

先从简单的 health 模块入手。

**health模块**

- service_interface.go

  定义接口 interface

- service

  服务类

- handlers.go

  服务逻辑

- routes.go

  路由

**routes.go**

- POST : oauth_tokens
- POST : oauth_introspect

# 145 | OAuth2服务模块（Code Review）



# 146 | Web服务模块（Code Review）

# 147 | 启动流程（Code Review）

