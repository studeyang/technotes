# 前言

最近将我写的服务发现组件开源了：https://github.com/dbses/cloud-discovery，分享一下 Jar 包上传中央仓库过程遇到的问题与总结。

# Sonatype Jira 账号注册

## 第一，注册账号

注册地址：https://issues.sonatype.org/secure/Signup!default.jspa

## 第二，创建问题

![image-20221108104859001](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221108104859001.png)

![image-20221108105108646](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221108105108646.png)

等待审核人员审核通过。

![image-20221108105219957](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221108105219957.png)

```
https://central.sonatype.org/publish/publish-guide/#deployment
https://central.sonatype.org/publish/release/
```

# 安装GnuPG软件

```
C:\Users\Administrator>gpg --gen-key
gpg (GnuPG) 2.3.8; Copyright (C) 2021 g10 Code GmbH
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.

Note: Use "gpg --full-generate-key" for a full featured key generation dialog.

GnuPG needs to construct a user ID to identify your key.

Real name: yanglulu
Email address: yanglu_u@126.com
You selected this USER-ID:
    "yanglulu <yanglu_u@126.com>"

Change (N)ame, (E)mail, or (O)kay/(Q)uit?
```



```
Change (N)ame, (E)mail, or (O)kay/(Q)uit? o
We need to generate a lot of random bytes. It is a good idea to perform
some other action (type on the keyboard, move the mouse, utilize the
disks) during the prime generation; this gives the random number
generator a better chance to gain enough entropy.
We need to generate a lot of random bytes. It is a good idea to perform
some other action (type on the keyboard, move the mouse, utilize the
disks) during the prime generation; this gives the random number
generator a better chance to gain enough entropy.
gpg: directory 'C:\\Users\\Administrator\\AppData\\Roaming\\gnupg\\openpgp-revocs.d' created
gpg: revocation certificate stored as 'C:\\Users\\Administrator\\AppData\\Roaming\\gnupg\\openpgp-revocs.d\\6381681E82726235773B17D753A149DCE9EE4910.rev'
public and secret key created and signed.

pub   ed25519 2022-11-07 [SC] [expires: 2024-11-06]
      6381681E82726235773B17D753A149DCE9EE4910
uid                      yanglulu <yanglu_u@126.com>
sub   cv25519 2022-11-07 [E] [expires: 2024-11-06]
```



```
C:\Users\Administrator>gpg --list-key
gpg: checking the trustdb
gpg: marginals needed: 3  completes needed: 1  trust model: pgp
gpg: depth: 0  valid:   1  signed:   0  trust: 0-, 0q, 0n, 0m, 0f, 1u
gpg: next trustdb check due at 2024-11-06
C:\Users\Administrator\AppData\Roaming\gnupg\pubring.kbx
--------------------------------------------------------
pub   rsa4096 2021-10-25 [SC] [expires: 2025-10-25]
      1121AFDE66C7246282A7610448CB2369E978B6BA
uid           [ unknown] yanglulu <yanglu_u@126.com>
sub   rsa4096 2021-10-25 [E] [expires: 2025-10-25]

pub   ed25519 2022-11-07 [SC] [expires: 2024-11-06]
      6381681E82726235773B17D753A149DCE9EE4910
uid           [ultimate] yanglulu <yanglu_u@126.com>
sub   cv25519 2022-11-07 [E] [expires: 2024-11-06]
```

踩坑1：

```
C:\Users\Administrator>gpg --keyserver hkp://keyserver.ubuntu.com:11371 --send-keys 1121AFDE66C7246282A7610448CB2369E978B6BA
gpg: sending key 48CB2369E978B6BA to hkp://keyserver.ubuntu.com
```

```
C:\Users\Administrator>gpg --keyserver hkp://keyserver.ubuntu.com:11371 --recv-keys 1121AFDE66C7246282A7610448CB2369E978B6BA
gpg: key 48CB2369E978B6BA: "yanglulu <yanglu_u@126.com>" not changed
gpg: Total number processed: 1
gpg:              unchanged: 1
```

```
D:\github\cloud-discovery>mvn -U clean deploy -P release
```

![image-20221108105950662](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20221108105950662.png)

53a149dce9ee4910

踩坑2：401

踩坑3：--recv-keys No data

```
D:\github\cloud-discovery>gpg --keyserver hkp://keyserver.ubuntu.com:11371 --recv-keys 6381681E82726235773B17D753A149DCE9EE4910
gpg: keyserver receive failed: No data
```



```
D:\github\cloud-discovery>gpg --keyserver hkp://keyserver.ubuntu.com:11371 --send-keys 6381681E82726235773B17D753A149DCE9EE4910
gpg: sending key 53A149DCE9EE4910 to hkp://keyserver.ubuntu.com:11371
```

```
D:\github\cloud-discovery>gpg --keyserver hkp://keyserver.ubuntu.com:11371 --recv-keys 6381681E82726235773B17D753A149DCE9EE4910
gpg: key 53A149DCE9EE4910: "yanglulu <yanglu_u@126.com>" not changed
gpg: Total number processed: 1
gpg:              unchanged: 1
```





```
# 查看版本来检查
gpg --version
# 生成密钥对
gpg --gen-key
# 查看生成的公钥
gpg --list-keys
# 将公钥发布到GPG密钥服务器
gpg --keyserver hkp://keyserver.ubuntu.com:11371 --send-keys 6381681E82726235773B17D753A149DCE9EE4910
# 查询是否已将公钥发布到服务器
gpg --keyserver hkp://keyserver.ubuntu.com:11371 --recv-keys 6381681E82726235773B17D753A149DCE9EE4910



mvn clean install deploy -P release -Dgpg.passphrase=Geilidaxue2



53a149dce9ee4910
```



```
<name>,<description>,<url>,<licenses>,<scm>,<developers>
```

```
maven-javadoc-plugin,maven-gpg-plugin
```

没有`.asc`文件。

nexus-staging-maven-plugin

完整的`pom.xml`配置可以参考github工程。



> 参考文章：
>
> 个人开源项目如何上传maven中央仓库：https://juejin.cn/post/7130363900813377567#heading-0
>
> 将github项目上传到Maven中央仓库操作小记：https://juejin.cn/post/7089301165929660446



