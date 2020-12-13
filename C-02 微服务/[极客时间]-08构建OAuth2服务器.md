# 140 | 架构和设计

**总体架构**

![image-20201213223546190](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201213223556.png)

**数据模型**

![image-20201213224217150](https://gitee.com/yanglu_u/ImgRepository/raw/master/images/20201213224217.png)

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









