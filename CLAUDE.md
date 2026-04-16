# CLAUDE.md

本文件为 Claude Code（claude.ai/code）在此仓库中工作时提供指导。

## 仓库简介

这是一个基于 Docsify 的静态文档站点，用于记录个人互联网技术学习笔记，发布地址：https://studeyang.cn/technotes

无需构建步骤——站点通过从 CDN 加载的 Docsify 直接在浏览器中渲染 Markdown 文件。

## 常用命令

**提交并推送变更：**
```bash
./commit.sh "提交信息"
```

**重新生成 sitemap.xml**（添加或删除页面后执行）：
```bash
bash sitemap.sh
```

**本地搜索内容：**
```bash
grep -nri [关键词] . | cat --number
```

## 仓库结构

笔记按五个顶级分类目录组织，每个目录都有独立的 `sidebar.md`：

| 目录 | 分类 |
|------|------|
| `A基础类/` | Java 基础、MySQL、网络协议、算法、前端 |
| `B进阶类/` | 进阶主题 |
| `C架构类/` | 架构视角 |
| `D扩展类/` | 行业观察 |
| `E-AI类/` | AI 工具与开发（Claude Code、Cursor、Spring AI） |

## 导航文件

Docsify 的导航由 Markdown 文件驱动——添加或删除笔记时必须同步更新以下文件：

- **`sidebar.md`**（根目录）——`A基础类/` 内容的左侧边栏
- **`<分类>/sidebar.md`**——各分类的侧边栏，通过 `navbar.md` 中的链接加载
- **`navbar.md`**——顶部导航栏，链接到各分类的侧边栏
- **`index.html`**——Docsify 配置（搜索深度、插件、主题等）

添加新笔记时，需在对应的 `sidebar.md` 中添加条目。添加新分类时，需同时更新 `navbar.md` 和根目录的 `README.md`。

## 笔记文件命名规范

文件名遵循以下格式：`[来源]-主题-子主题.md`

示例：
- `[极客时间]-Java并发编程-并发理论基础.md`
- `[拉勾教育]-高性能MySQL实战-01基础篇.md`
- `ClaudeCode工程化实战-01基础篇.md`