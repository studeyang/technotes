## 一、分支操作

### 合并分支，将 feature-a 合并到 develop

```shell
# 切换到 develop
git checkout develop
git pull
# 将 feature-a 分支合并到 develop
git merge --no-ff origin/feature-a
```

### 删除远端分支

```shell
git push origin --delete feature-a
```



## 二、日志操作

查看日志

```shell
$ git log --pretty=oneline
185ad4681b2f75867ff640d341ddc4d60bf24a51 (HEAD -> master, origin/master) 1.5.0-SNAPSHOT
cfdd931caeb3eeb0cf011abaec2875acf4748b35 (tag: v1.4.1) 1.4.1版本
0279906190bb2abdc1bfb3573fffc9554518239f 升级1.5.0-SNAPSHOT
fb7e7527dc8da20e69b6b2b02f0118985bcba03a merge release-Aston51 to develop
...
```

##  三、标签操作

### 查看 tag

```shell
$ git tag
V1.0.3
v1.0.0
v1.0.0C01
v1.0.1
v1.0.2
v1.0.4
v1.1.0
```

### 查看 tag，带上 tag message

```shell
$ git tag -n1
V1.0.3          消息可视化
v1.0.0          正式版本
v1.0.0C01       正式版本
v1.0.1          v1.0.1 正式版本
v1.0.2          正式版本
v1.0.4          20迭代 正式版本
v1.1.0          22迭代正式版本
```

### 查看 tag 的详细信息

```shell
$ git show v1.4
tag v1.4
Tagger: Ben Straub <ben@straub.cc>
Date:   Sat May 3 20:19:12 2014 -0700

my version 1.4

commit ca82a6dff817ec66f44342007202690a93763949
Author: Scott Chacon <schacon@gee-mail.com>
Date:   Mon Mar 17 21:52:11 2008 -0700

    changed the version number
```

### tag 数量很多，如果只对 v1.0 系列感兴趣

```shell
$ git tag -l v1.0*
v1.0.0
v1.0.0C01
v1.0.1
v1.0.2
v1.0.4
```

### 创建 tag 并推送至远端

```shell
$ git tag -a v0.0.1 -m 'msg'
$ git push origin v0.0.1
```

### 轻量标签

```shell
$ git tag v0.0.1-lw
```

### 更新 tag

```shell
$ git push origin --delete v0.0.1
$ git log --pretty=oneline
15027957951b64cf874c3557a0f3547bd83b3ff6 Merge branch 'experiment'
a6b4c97498bd301d84096da251c98a07c7723e65 beginning write support
0d52aaab4479697da7686c15f77a3d64d9165190 one more thing
6d52a271eda8725415634dd79daabbc4d9b6008e Merge branch 'experiment'
0b7434d86859cc7b8c3d5e1dddfed66ff742fcbc added a commit function
4682c3261057305bdd616e23b64b0857d832627b added a todo file
166ae0c4d3f420721acbb115cc33848dfcc2121a started write support
9fceb02d0ae598e95dc970b74767f19372d61af8 updated rakefile
964f16d36dfccde844893cac5b347e7b3d44abbc commit the todo
8a5cbc430f1a9c3d00faaeffd07798508422908a updated readme
$ git tag -a v0.0.1 9fceb02
$ git push origin v0.0.1
```



