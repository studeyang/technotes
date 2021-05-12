# 课程介绍

基础篇

- Go 语言简介
- 基本程序结构
- 常用集合
- 字符串
- 函数
- 面向对象编程
- 编写好的错误处理
- 包和依赖管理

进阶篇

- 并发编程
- 典型并发任务
- 测试
- 反射和 Unsafe
- 常见架构模式的实现
- 常见任务
- 性能调优
- 高可用性服务设计

# 基础篇

# 01 | 第一个 Go 程序

hello_world.go

```go
package main

import (
	"fmt"
	"os"
)

func main() {
	if len(os.Args) > 1 {
		fmt.Println("Hello World", os.Args[1])
	}
}
```

# 02 | 基本程序结构

**常量**

constant_try_test.go

```go
package constant_test

import "testing"

const (
	Monday = 1 + iota
	Tuesday
	Wednesday
)

const (
	Readable = 1 << iota
	Writable
	Executable
)

func TestConstantTry(t *testing.T) {
	t.Log(Monday, Tuesday)
}

func TestConstantTry1(t *testing.T) {
	a := 1 //0001
	t.Log(a&Readable == Readable, a&Writable == Writable, a&Executable == Executable)
}
```

**数据类型**

```go
package type_test

import "testing"

type MyInt int64

func TestImplicit(t *testing.T) {
	var a int32 = 1
	var b int64
	b = int64(a)
	var c MyInt
	c = MyInt(b)
	t.Log(a, b, c)
}

func TestPoint(t *testing.T) {
	a := 1
	aPtr := &a
	//aPtr = aPtr + 1
	t.Log(a, aPtr)
	t.Logf("%T %T", a, aPtr)
}

func TestString(t *testing.T) {
	var s string
	t.Log("*" + s + "*") //初始化零值是“”
	t.Log(len(s))
}
```



# 03 | 常用集合



# 04 | 字符串

# 05 | 函数

# 06 | 面向对象编程

# 07 | 编写好的错误处理

# 08 | 包和依赖管理

# 进阶篇

# 09 | 并发编程

# 10 | 典型并发任务

# 11 | 测试

# 12 | 反射和 Unsafe

# 13 | 常见架构模式的实现

# 14 | 常见任务

# 15 | 性能调优

# 16 | 高可用性服务设计