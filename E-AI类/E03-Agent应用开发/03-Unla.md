> 参考资料：
>
> - https://github.com/AmoyLab/Unla
> - https://docs.unla.amoylab.com/cn

# 01 | 快速开始

## 1.1 Unla - MCP Gateway

Unla 是一个网关服务，它能够通过配置将现有的 MCP 服务和 API 转换为符合 [MCP 协议](https://modelcontextprotocol.io/) 的服务 — 全程无需更改代码。

**架构**

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2026/202608052025550.webp)

**核心功能**

- 协议与代理能力
  - ✅ 支持将 RESTful API 转换为 MCP 服务
  - ✅ 支持代理 MCP 服务
  - ✅ 支持 MCP SSE
  - ✅ 支持 MCP Streamable HTTP
  - ✅ 支持包括文本、图像和音频的 MCP 响应
  - 🔄 支持将 gRPC 转换为 MCP 服务（开发中）
  - 🔄 支持将 WebSocket 转换为 MCP 服务（开发中）
- 会话与多租户支持
  - ✅ 持久化和可恢复的会话支持
  - ✅ 多租户支持
  - 🔄 支持 MCP 服务分组和聚合（开发中）
- 配置与管理
  - ✅ 自动配置获取和无缝热重载
  - ✅ 配置持久化（磁盘/SQLite/PostgreSQL/MySQL）
  - ✅ 通过 OS 信号、HTTP 或 Redis PubSub 进行配置同步
  - ✅ 配置版本控制
- 安全与认证
  - ✅ 基于 OAuth 的 MCP 服务预认证支持
- 部署与运维
  - ✅ 多副本服务支持
  - ✅ Docker 支持
  - ✅ Kubernetes 和 Helm 部署支持

## 1.2 快速开始

**一键启动 MCP Gateway**

使用阿里云镜像启动：

```bash
docker run -d \
  --name unla \
  -p 8080:80 \
  -p 5234:5234 \
  -p 5235:5235 \
  -p 5335:5335 \
  -p 5236:5236 \
  -e ENV=production \
  -e TZ=Asia/Shanghai \
  -e APISERVER_JWT_SECRET_KEY=${APISERVER_JWT_SECRET_KEY} \
  -e SUPER_ADMIN_USERNAME=${SUPER_ADMIN_USERNAME} \
  -e SUPER_ADMIN_PASSWORD=${SUPER_ADMIN_PASSWORD} \
  --restart unless-stopped \
  registry.ap-southeast-1.aliyuncs.com/amoylab/unla-allinone:latest
```

**访问和配置**

在浏览器中打开 http://localhost:8080/ 使用配置的管理员账号密码登录

添加 MCP Server

1. 复制配置文件：https://github.com/AmoyLab/Unla/blob/main/configs/proxy-mock-server.yaml
2. 在 Web 界面上点击 “Add MCP Server”
3. 粘贴配置并保存

**可用端点**

配置完成后，服务将在以下端点可用：

```
MCP 端点
MCP SSE: http://localhost:5235/gateway/user/sse
MCP SSE Message: http://localhost:5235/gateway/user/message
MCP Streamable HTTP: http://localhost:5235/gateway/user/mcp
```



# 02 | 安装部署

# 03 | 配置说明

# 04 | Web 配置

# 05 | 客户端使用

# 06 | 开发文档

# 07 | API 文档

# 08 | 端点示例



