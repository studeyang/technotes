## 一、管理npm镜像

安装nrm

```
npm install -g nrm
```

设置镜像

```shell
#设置淘宝镜像
npm config set registry http://registry.npm.taobao.org
#查看
npm get registry
```

查看可使用的镜像地址

```javascript
nrm ls
```

切换选择

```
nrm use cnpm
```

## 二、管理Node版本

安装n

```
npm install -g n
```

管理本地node

```shell
# 列出目前已经安装的 `Node.js` 版本
n ls
# 列出远程所有的 `Node.js` 版本(可以通过 `--all` 列举所有的)
n ls-remote

# 安装指定版本
sudo n 16.10.0
#安装最新正式发布版本
sudo n latest
# 安装最新的长期支持正式发布版本
sudo n lts

#切换版本
sudo n

# 卸载版本
sudo n rm 12.22.1

# 查看你当前的node版本
node -v
```





