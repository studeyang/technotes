# 第一章 React 基础

## 01 出现的历史背景及特性介绍

**简单功能一再出现 Bug**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082235680.png" alt="image-20220908223516980" style="zoom:50%;" />

问题出现的根源：

1. 传统 UI 操作关注太多细节；
2. 应用程序状态分散在各处，难以追踪和维护；

而 React 始终整体"刷新"页面，无需关心细节。

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082239581.png" alt="image-20220908223910543" style="zoom:50%;" />

**React 解决了 UI 细节问题**

数据模型如何解决?

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082240552.png" alt="image-20220908224039515" style="zoom:50%;" />

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082240114.png" alt="image-20220908224051081" style="zoom:50%;" />

## 02 以组件方式考虑 UI 的构建

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082242549.png" alt="image-20220908224244516" style="zoom: 50%;" />

**理解 React 组件**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082243090.png" alt="image-20220908224309056" style="zoom:50%;" />

1. React 组件一般不提供方法，而是某种状态机；
2. React 组件可以理解为一个纯函数；
3. 单向数据绑定；

**受控组件 vs 非受控组件**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082245112.png" alt="image-20220908224517076" style="zoom:50%;" />

**何时创建组件：单一职责原则**

1. 每个组件只做一件事；
2. 如果组件变得复杂，那么应该拆分成小组件；

**数据状态管理：DRY 原则**

1. 能计算得到的状态就不要单独存储；
2. 组件尽量无状态，所需数据通过 props 获取；

## 03 理解 JSX：不是模板语言，只是一种语法糖

**JSX：在 JavaScript 代码中直接写 HTML 标记**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082248405.png" alt="image-20220908224801367" style="zoom:50%;" />

JSX 的本质：动态创建组件的语法糖

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082248006.png" alt="image-20220908224841967" style="zoom:50%;" />

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082249187.png" alt="image-20220908224917142" style="zoom:50%;" />

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209082251172.png" alt="image-20220908225122129" style="zoom:50%;" />

**JSX 优点**

1. 声明式创建界面的直观；
2. 代码动态创建界面的灵活；
3. 无需学习新的模板语言；

约定：自定义组件以大写字母开头

1. React 认为小写的 tag 是原生 DOM 节点，如 div；
2. 大写字母开头为自定义组件；
3. JSX 标记可以直接使用属性语法，例如<menu.Item />；

## 04 React 组件的生命周期及其使用场景

![image-20220909215141778](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209092151874.png)

**constructor**

1. 用于初始化内部状态，很少使用；
2. 唯一可以直接修改 state 的地方；

**getDerivedStateFromProps**

1. 当 state 需要从 props 初始化时使用；
2. 尽量不要使用：维护两者状态一致性会增加复杂度；
3. 每次 render 都会调用；
4. 典型场景：表单控件获取默认值；

**componnentDidMount**

1. UI 渲染完成后调用；
2. 只执行一次；
3. 典型场景：获取外部资源；

**componentWillUnmount**

1. 组件移除时被调用；
2. 典型场景：资源释放；

**getSnapshotBeforeUpdate**

1. 在页面 render 之前调用，state 已更新；
2. 典型场景：获取 render 之前的 DOM 状态；

**componentDidUpdate**

1. 每次 UI 更新时被调用；
2. 典型场景：页面需要根据 props 变化重新获取数据；

**shouldComponentUpdate**

1. 决定 Virtual DOM 是否要重绘；
2. 一般可以由 PureComponent 自动实现；
3. 典型场景：性能优化；

## 05 理解 Virtual DOM 的工作原理，理解 key 属性的作用

**虚拟 DOM 是如何工作的**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209132131511.png" alt="image-20220913213158407" style="zoom:50%;" />

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209132132133.png" alt="image-20220913213213061" style="zoom:50%;" />

**虚拟 DOM 的两个假设**

1. 组件的 DOM 结构是相对稳定的；
2. 类型相同的兄弟节点可以被唯一标识；；

## 06 组件设计模式：高阶组件和函数作为组件

**高阶组件（HOC）**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209132145072.png" alt="image-20220913214546027" style="zoom:50%;" />

**函数作为子组件**

![image-20220913214614979](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209132146021.png)

## 07 理解 Context API 的使用场景

**React 16.3 新特性：Context API**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209132157874.png" alt="image-20220913215704819" style="zoom:33%;" />

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209132157257.png" alt="image-20220913215739193" style="zoom:50%;" />

## 08 使用脚手架工具创建 React 应用

**为什么需要脚手架工具**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209132208214.png" alt="image-20220913220824166" style="zoom:33%;" />

![image-20220913220838858](/Users/yanglulu/Library/Application Support/typora-user-images/image-20220913220838858.png)

**create-react-app**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209132209745.png" alt="image-20220913220937677" style="zoom:50%;" />

**Rekit**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209132209194.png" alt="image-20220913220949148" style="zoom:50%;" />

**Online: Codesandbox.io**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209132210852.png" alt="image-20220913221003809" style="zoom:50%;" />

## 09 打包和部署

**为什么需要打包？**

1. 编译 ES6 语法特性，编译 JSX；
2. 整合资源，例如图片，Less/Sass；
3. 优化代码体积；

**使用 Webpack 进行打包**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209142143497.png" alt="image-20220914214348372" style="zoom:50%;" />

**打包注意事项**

1. 设置 nodejs 环境为 production；
2. 禁用开发时专用代码，比如 logger；
3. 设置应用根路径；

# 第二章 React 生态圈

## 10 Redux(1) 前端为何需要状态管理库

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209142153903.png" alt="image-20220914215354842" style="zoom:50%;" />

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209142154760.png" alt="image-20220914215409714" style="zoom:50%;" />

**Redux 特性：Single Source of Truth**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209142154626.png" alt="image-20220914215438570" style="zoom:50%;" />

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209142154272.png" alt="image-20220914215450202" style="zoom: 33%;" />

**Redux 特性：可预测性**

state + action = new state

**Redux 特性：纯函数更新 Store**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209142203319.png" alt="image-20220914220313218" style="zoom:67%;" />

## 11 Redux(2) 深入理解 Store, Action, Reducer

**理解 Store**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209142220223.png" alt="image-20220914222000175" style="zoom:50%;" />

**理解 Action**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209142220263.png" alt="image-20220914222024193" style="zoom: 50%;" />

**理解 Reducer**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209142207597.png" alt="image-20220914220730529" style="zoom:50%;" />

**理解 combineReducers**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209142221802.png" alt="image-20220914222136747" style="zoom: 50%;" />

**理解 bindActionCreators**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209142222232.png" alt="image-20220914222220164" style="zoom:50%;" />

**理解 bindActionCreators**

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202209142222327.png" alt="image-20220914222249268" style="zoom:50%;" />

## 12 Redux(3) 在React中使用Redux























