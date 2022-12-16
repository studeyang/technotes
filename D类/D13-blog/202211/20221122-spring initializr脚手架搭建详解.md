# spring initializr脚手架搭建详解

前段时间，我在[「基于start.spring.io，我实现了Java脚手架定制」](https://mp.weixin.qq.com/s?__biz=MzkwMTI4NTI1NA==&mid=2247483902&idx=1&sn=2e117fec67cdfb9064369835c0af41d8&chksm=c0b65517f7c1dc01be4080f4fd0f86cd534cf8d59244af34b5aed3340c653e5d697154e4742b&token=1554827504&lang=zh_CN#rd)一文中讲述了敝司的微服务脚手架落地过程中的前世今生，并提到了基于 spring initializr 的搭建了 2.0 版本的脚手架。今天我打算和你分享一下这其中的实现过程与细节，项目已经开源在 Github 上。

> start-parent：https://github.com/studeyang/start-parent
>
> 欢迎 star

# 1、项目结构介绍

项目分为 initializr、start-client、start-site 三个部分，重要部分说明如下。

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
  |- start-client                   脚手架前端
  |- start-site                     脚手架后端
```

工程间的依赖关系图我作了简化，图示如下。

![依赖关系图](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221020152301967.png)

了解了项目的整体情况，下面请跟随我的思路，一起将工程搭建起来。

# 2、集成Gitlab

如果你想使用项目中的「创建工程」功能，则需要进行此步骤的配置。这里我以`gitlab.com`为例，介绍如何完成与 Gitlab 的集成。

首先需要让 Gitlab 信任我们的应用，以完成后面的登录授权跳转。在 Gitlab 平台配置脚手架应用。

![添加Applications](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221122142337155.png)

这里我配置了本地开发环境的 Redirect URI，如果后续需要部署到服务器，则应该配置脚手架服务器的后端地址。

![Application ID](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221122142420051.png)

配置完成后，Gitlab 就将我们的应用记录了下来，并分配了 Application ID 和 Secret，这两个字段值我们需要配置到 start-site application.yml 文件中：

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

这里我简单介绍一下相关字段，authorization-uri, token-uri, user-info-uri 这三个字段是固定的，不需要配置。

- base-url：如果你使用`gitlab`管理项目，`base-url`可以设置成你搭建的`gitlab`地址；
- redirect-uri：gitlab 认证后跳转的地址，这里使用了后端来接收跳转，因为跳转会携带 code 参数，避免暴露在浏览器，提高安全性；
- client-id：gitlab 分配的 Application ID；
- client-secret：gitlab 分配的 Secret；
- admin.name：gitlab 的账号，用于创建工程，并将初始的工程代码提交，建议配置管理员账号；
- admin.password：gitlab 的账号密码；

# 3、添加组件

接下来添加组件依赖。这里我以`casslog-spring-boot-starter`Jar 包为例，如果该组件仅支持部分版本的 SpringBoot，那可以配置 compatibility-range，例如：

```
compatibility-range: "[1.4.2.RELEASE,1.5.7.RELEASE]"
```

完整的配置如下。

```yaml
initializr:
  dependencies:
    - name: 开源基础设施
      bom: kmw
      repository: my-rep
      content:
        - name: Casslog
          id: casslog
          groupId: io.github.studeyang
          artifactId: casslog-spring-boot-starter
          description: 日志工具类
          starter: true
          compatibility-range: "[1.4.2.RELEASE,1.5.7.RELEASE]"
          links:
            - rel: guide
              href: {用户手册}
              description: Example 快速开始
            - rel: reference
              href: {参考文档}
```

配置dependencies。

- 「name」组件依赖类别的名称，例如：开源基础设施
- 「bom」该类别下的依赖包管理库
- 「repository」该类别下的依赖包所属仓库
- 「content」具体的依赖包

配置content。

- 「name」依赖包名称
- 「id」依赖包唯一标识（代码中使用）
- 「groupId」依赖包 groupId
- 「artifactId」依赖包 artifactId
- 「description」依赖包 description
- 「starter」是否是 spring-boot-starter
- 「compatibility-range」依赖的 springboot 版本
- 「links」组件的使用文档

配置好的效果图如下。

![组件添加效果图](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202211271349589.png)

# 4、部署应用

下面就可以将脚手架部署到服务器上了。

> 这里提醒一下，记得修改 Gitlab 的 redirect-uri 为脚手架服务器的地址。

## 4.1 步骤一：工程打包

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

## 4.2 步骤二：打 Docker 镜像

```shell
cd {projectRoot}/start-site
docker build -t start-site:0.0.1 .
```

运行镜像即可。效果图如下。

![脚手架主界面](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202211271058880.png)

# 5、使用脚手架的正确姿势

## 5.1 通过HELP.md管理使用文档

在「3、添加组件」过程中所配置的文档链接将会在 HELP.md 文件中展示，示意图如下：

![HELP.md](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202211271355264.png)

## 5.2 保存/分享工程

你配置好的工程可以通过「分享...」功能保存下来。

![分享](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202211271357591.png)

## 5.3 在IDEA中使用脚手架

可在 IDEA 中快速创建工程，只需要配置好脚手架服务器地址即可。需要注意的是社区版的 IDEA 是没有这个功能的。

![IDEA](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202211271359221.png)

# 小结

本文向你介绍了 Spring Initializr 脚手架的搭建过程，如果你在此过程中遇到了问题，可以提 ISSUE 或者在公众号「杨同学technotes」后台给我留言。
