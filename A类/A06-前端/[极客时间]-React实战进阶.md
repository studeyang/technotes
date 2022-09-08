# 第一章 React 基础

## 01 出现的历史背景及特性介绍

**简单功能一再出现 Bug**

![image-20220908223516980](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082235680.png)

问题出现的根源：

1. 传统 UI 操作关注太多细节；
2. 应用程序状态分散在各处，难以追踪和维护；

而 React 始终整体"刷新"页面，无需关心细节。

![image-20220908223910543](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082239581.png)

**React 解决了 UI 细节问题**

数据模型如何解决?

![image-20220908224039515](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082240552.png)

![image-20220908224051081](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082240114.png)

## 02 以组件方式考虑 UI 的构建

![image-20220908224244516](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082242549.png)

**理解 React 组件**

![image-20220908224309056](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082243090.png)

1. React 组件一般不提供方法，而是某种状态机；
2. React 组件可以理解为一个纯函数；
3. 单向数据绑定；

**受控组件 vs 非受控组件**

![image-20220908224517076](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082245112.png)

**何时创建组件：单一职责原则**

1. 每个组件只做一件事；
2. 如果组件变得复杂，那么应该拆分成小组件；

**数据状态管理：DRY 原则**

1. 能计算得到的状态就不要单独存储；
2. 组件尽量无状态，所需数据通过 props 获取；

## 03 理解 JSX：不是模板语言，只是一种语法糖

**JSX：在 JavaScript 代码中直接写 HTML 标记**

![image-20220908224801367](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082248405.png)

JSX 的本质：动态创建组件的语法糖

![image-20220908224841967](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082248006.png)

![image-20220908224917142](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082249187.png)

![image-20220908225122129](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082251172.png)

**JSX 优点**

1. 声明式创建界面的直观；
2. 代码动态创建界面的灵活；
3. 无需学习新的模板语言；

约定：自定义组件以大写字母开头

1. React 认为小写的 tag 是原生 DOM 节点，如 div；
2. 大写字母开头为自定义组件；
3. JSX 标记可以直接使用属性语法，例如<menu.Item />；





