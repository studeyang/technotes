# 01 | Lua 简介

**设计目的**

为了嵌入应用程序中，从而为应用程序提供灵活的扩展和定制功能。

**应用场景**

- 游戏开发
- 独立应用脚本
- Web 应用脚本
- 扩展和数据库插件（如 MySQL Proxy 和 MySQL WorkBench）
- 安全系统，如入侵检测系统

# 02 | Lua 基础

**交互式编程**

在命令行中输入以下命令进行交互模式：

```bash
lua -i 或 lua
```

**脚本式编程**

保存为以 lua 结尾的文件，例如 hello.lua，执行：

```bash
lua hello.lua
```

也可以在开头添加：

```lua
#!/usr/local/bin/lua

print("Hello World！")
```

**全局变量**

```bash
> print(b)
nil
> b=10
10
>
```

删除全局变量

```bash
b=nil
print(b)
```

**数据类型**

Lua 中有 8 个基本类型分别为：nil、boolean、number、string、userdata、function、thread 和 table。













