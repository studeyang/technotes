# spring initializr食用方法, 自制脚手架

前段时间，我在xx一文中讲述了敝司微服务脚手架落地过程中的前世今生，并提到了基于 spring initializr 的搭建了 2.0 版本的脚手架。今天我打算和你分享一下这其中的实现过程与细节，项目已经开源在 Github 上。

> start-parent：https://github.com/studeyang/start-parent
>
> 欢迎 star

## 工程结构介绍

```
start-parent
  |- initializr                    代码生成
    |- initializr-actuator
    |- initializr-bom
    |- initializr-docs
    |- initializr-generator         生成基础工程代码
    |- initializr-generator-spring  生成 spring 工程代码
    |- initializr-generator-test    单元测试的封装
    |- initializr-generator-zebra   生成 zebra 分层架构
    |- initializr-metadata          工程元数据（pom 相关定义）
    |- initializr-parent
    |- initializr-service-sample
    |- initializr-version-resolver  版本解析
    |- initializr-web
  |- start-client                   start.io 前端
  |- start-site                     start.io 后端
```

![依赖关系图](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221020152301967.png)

## 集成Gitlab

![image-20221122110635578](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221122110635578.png)

![image-20221122111147696](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221122111147696.png)

![image-20221122111241122](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221122111241122.png)





![image-20221122142356022](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221122142356022.png)

![image-20221122142337155](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221122142337155.png)

![image-20221122142420051](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221122142420051.png)

对应的配置是：

```yaml
security:
  base-url: https://gitlab.com
  authorization-uri: ${security.base-url}/oauth/authorize
  token-uri: ${security.base-url}/oauth/token
  user-info-uri: ${security.base-url}/api/v4/user
  redirect-uri: http://127.0.0.1:8081/oauth/redirect
  client-id: gitlab client id
  client-secret: gitlab client secret
  admin:
    name: your gitlab admin username
    password: your gitlab admin password
```

- base-url：如果你使用`gitlab`管理项目，`base-url`可以设置成你搭建的`gitlab`地址；
- redirect-uri：gitlab 认证后跳转的地址，这里最好使用后端来接收跳转，因为跳转会携带 code 参数，避免暴露在浏览器，提高安全性；

## 添加组件

如果你的组件仅支持部分版本的 SpringBoot，那可以配置 compatibility-range，例如：

```
compatibility-range: "[1.4.2.RELEASE,1.5.7.RELEASE]"
```

```yaml
initializr:
  dependencies:
    - name: 基础组件库
      bom: infra
      repository: my-rep
      content:
        - name: Example
          id: example
          groupId: com.dbses.open
          artifactId: example-spring-boot-starter
          description: 示例组件说明
          starter: true
          links:
            - rel: guide
              href: {用户手册}
              description: Example 快速开始
            - rel: reference
              href: {参考文档}
```



## 部署应用

### 步骤一：工程打包

```shell
# 打包前端工程
cd {projectRoot}/start-client
sh ../mvnw install

# 打包 initializr 项目
cd {projectRoot}/initializr
sh ../mvnw clean install -Dmaven.test.skip=true

# 打包 start-site
cd {projectRoot}/start-site
sh ../mvnw clean install -Dmaven.test.skip=true
```

### 步骤二：打 Docker 镜像

```shell
cd {projectRoot}/start-site
docker build -t start-site:0.0.1 .
```

### 步骤三：部署至 kubernetes



## 在IDEA中使用脚手架



注意社区版的 IDEA 是没有这个功能的。





