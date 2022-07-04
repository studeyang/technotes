# 01 | 新文件加作者信息

![image-20220322141132826](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220322141132826.png)

# 02 | 快速生成作者信息

![image-20220322140938127](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220322140938127.png)

添加变量：

![image-20220322141017670](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220322141017670.png)

# 03 | IDEA 2022.01 激活

**1. 下载激活工具**

![image-20220704095658718](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220704095658718.png)

将激活工具解压到路径下，注意该路径不要包含空格。

**2. 修改启动参数**

![image-20220704095951874](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220704095951874.png)

```text
-Xmx2027m
-javaagent:D:\jetbrain_activate\ja-netfilter.jar
```

**3. 激活**

![image-20220704100116373](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220704100116373.png)

```textt
https://jetbra.in/
```

# 04 | 设置右键IDEA打开

**1. 设置注册表**

```
win+R 键输入 regedit
计算机\HKEY_LOCAL_MACHINE\SOFTWARE\Classes\Directory\shell
```

![image-20220704103634192](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220704103634192.png)

新增字符串选项 Icon，值为你的 IDEA 安装路径。

![img](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/1351763-20191030091334888-991713327.png)

 在IDEA下面新增项command， 修改默认值为 "安装路径" "%V"：

![image-20220704103922327](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220704103922327.png)

**2. 重启电脑后看效果！**







