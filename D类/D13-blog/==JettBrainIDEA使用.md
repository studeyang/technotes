# 01 | 新文件加作者信息

![image-20220322141132826](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220322141132826.png)

```java
/**
 * @author <a href="https://github.com/studeyang">studeyang</a>
 * @since 1.0 ${DATE}
 */
```

# 02 | 快速生成作者信息

![image-20220705101234159](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220705101234159.png)

```text
/**
 * @author <a href="mailto:yanglu_u@126.com">dbses</a>
 * @since 1.0 $date$
 */

date{"yyyy-MM-dd"}

/**
 * @author <a href="https://github.com/studeyang">studeyang</a>
 * @since 2.0 2022/5/25
 */
```

添加变量：

![image-20220322141017670](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220322141017670.png)

# 03 | IDEA 2022.01 激活

> 参考文章：https://www.exception.site/essay/idea-reset-eval

**1. 下载激活工具**

![image-20220707174052806](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/image-20220707174052806.png)

将激活工具解压到路径下，注意该路径不要包含空格和中文。

**2. 执行脚本**

![打开 IDEA 2022.1.3 激活脚本文件夹](https://img.chajianxw.com/chajian/164412033477656)

**3. 指定激活码完成激活**

```
4W9NP3KV9E-eyJsaWNlbnNlSWQiOiI0VzlOUDNLVjlFIiwibGljZW5zZWVOYW1lIjoic2NyaXAgd2FuZSIsImFzc2lnbmVlTmFtZSI6IiIsImFzc2lnbmVlRW1haWwiOiIiLCJsaWNlbnNlUmVzdHJpY3Rpb24iOiIiLCJjaGVja0NvbmN1cnJlbnRVc2UiOmZhbHNlLCJwcm9kdWN0cyI6W3siY29kZSI6IklJIiwiZmFsbGJhY2tEYXRlIjoiMjAyMy0wMS0yNCIsInBhaWRVcFRvIjoiMjAyMy0wMS0yNCIsImV4dGVuZGVkIjpmYWxzZX0seyJjb2RlIjoiUERCIiwiZmFsbGJhY2tEYXRlIjoiMjAyMy0wMS0yNCIsInBhaWRVcFRvIjoiMjAyMy0wMS0yNCIsImV4dGVuZGVkIjp0cnVlfSx7ImNvZGUiOiJQV1MiLCJmYWxsYmFja0RhdGUiOiIyMDIzLTAxLTI0IiwicGFpZFVwVG8iOiIyMDIzLTAxLTI0IiwiZXh0ZW5kZWQiOnRydWV9LHsiY29kZSI6IlBHTyIsImZhbGxiYWNrRGF0ZSI6IjIwMjMtMDEtMjQiLCJwYWlkVXBUbyI6IjIwMjMtMDEtMjQiLCJleHRlbmRlZCI6dHJ1ZX0seyJjb2RlIjoiUFBTIiwiZmFsbGJhY2tEYXRlIjoiMjAyMy0wMS0yNCIsInBhaWRVcFRvIjoiMjAyMy0wMS0yNCIsImV4dGVuZGVkIjp0cnVlfSx7ImNvZGUiOiJQUEMiLCJmYWxsYmFja0RhdGUiOiIyMDIzLTAxLTI0IiwicGFpZFVwVG8iOiIyMDIzLTAxLTI0IiwiZXh0ZW5kZWQiOnRydWV9LHsiY29kZSI6IlBSQiIsImZhbGxiYWNrRGF0ZSI6IjIwMjMtMDEtMjQiLCJwYWlkVXBUbyI6IjIwMjMtMDEtMjQiLCJleHRlbmRlZCI6dHJ1ZX0seyJjb2RlIjoiUFNXIiwiZmFsbGJhY2tEYXRlIjoiMjAyMy0wMS0yNCIsInBhaWRVcFRvIjoiMjAyMy0wMS0yNCIsImV4dGVuZGVkIjp0cnVlfSx7ImNvZGUiOiJQU0kiLCJmYWxsYmFja0RhdGUiOiIyMDIzLTAxLTI0IiwicGFpZFVwVG8iOiIyMDIzLTAxLTI0IiwiZXh0ZW5kZWQiOnRydWV9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
```

![填入 IDEA 2022.1.3 激活码](https://img.chajianxw.com/chajian/164412373711216)

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

# 05 | 插件

下划线转驼峰：https://www.bejson.com/convert/camel_underscore/







