> 参考资料：
>
> - https://github.com/AmoyLab/Unla
> - https://docs.unla.amoylab.com/cn

# 01 | Unla 介绍

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

# 02 | 快速开始

All-in-One 部署将所有服务打包在一个容器中，适合单机部署或本机使用。包含以下服务：

- API Server: 管理平台后端，可理解为控制面
- MCP Gateway: 核心服务，负责实际的网关服务，可理解为数据面
- Mock User Service: 模拟用户服务，提供测试用的用户服务
- Web 前端: 管理平台前端，提供可视化的管理界面
- Nginx: 反向代理其他几个服务

建议挂载以下目录：

- `/app/configs`: 配置文件目录
- `/app/data`: 数据目录
- `/app/.env`: 环境变量文件

**部署步骤**

1、创建目录并下载配置

```bash
mkdir -p unla/{configs,data}
cd unla/
curl -sL https://raw.githubusercontent.com/amoylab/unla/refs/heads/main/configs/apiserver.yaml -o configs/apiserver.yaml
curl -sL https://raw.githubusercontent.com/amoylab/unla/refs/heads/main/configs/mcp-gateway.yaml -o configs/mcp-gateway.yaml
curl -sL https://raw.githubusercontent.com/amoylab/unla/refs/heads/main/.env.example -o .env.allinone
```

2、启动容器

```bash
# 使用阿里云容器镜像服务镜像（建议在中国境内使用）
docker run -d \
           --name unla \
           -p 8080:80 \
           -p 5234:5234 \
           -p 5235:5235 \
           -p 5335:5335 \
           -p 5236:5236 \
           -e ENV=production \
           -v $(pwd)/configs:/app/configs \
           -v $(pwd)/data:/app/data \
           -v $(pwd)/.env.allinone:/app/.env \
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
MCP SSE: http://localhost:5235/gateway/user/sse
MCP SSE Message: http://localhost:5235/gateway/user/message
MCP Streamable HTTP: http://localhost:5235/gateway/user/mcp
```

# 03 | 配置说明

## 3.1 API Server 配置

```yaml
# 日志配置 - 用于控制应用程序的日志输出行为
logger:
  level: "${APISERVER_LOGGER_LEVEL:info}"                                         # 日志级别：debug, info, warn, error
  format: "${APISERVER_LOGGER_FORMAT:console}"                                    # 日志格式：json, console
  output: "${APISERVER_LOGGER_OUTPUT:stdout}"                                     # 输出方式：stdout, file
  file_path: "${APISERVER_LOGGER_FILE_PATH:/var/log/unla/apiserver.log}"          # 日志文件路径（当 output 为 file 时）
  max_size: ${APISERVER_LOGGER_MAX_SIZE:100}                                      # 日志文件最大大小（MB）
  max_backups: ${APISERVER_LOGGER_MAX_BACKUPS:3}                                  # 保留的备份文件数量
  max_age: ${APISERVER_LOGGER_MAX_AGE:7}                                          # 备份文件保留天数
  compress: ${APISERVER_LOGGER_COMPRESS:true}                                     # 是否压缩备份文件
  color: ${APISERVER_LOGGER_COLOR:true}                                           # 控制台输出是否使用颜色
  stacktrace: ${APISERVER_LOGGER_STACKTRACE:true}                                 # 错误日志是否包含堆栈跟踪

# 国际化配置 - 用于支持多语言界面
i18n:
  path: "${APISERVER_I18N_PATH:/etc/unla/i18n}"                                   # 翻译文件路径

# 聊天消息数据库配置
database:
  type: "${APISERVER_DB_TYPE:sqlite}"               # 数据库类型（sqlite,postgres, mysql）
  host: "${APISERVER_DB_HOST:localhost}"            # 数据库主机地址
  port: ${APISERVER_DB_PORT:5432}                   # 数据库端口
  user: "${APISERVER_DB_USER:postgres}"             # 数据库用户名
  password: "${APISERVER_DB_PASSWORD:example}"      # 数据库密码
  dbname: "${APISERVER_DB_NAME:./unla.db}"          # 数据库名称或文件路径
  sslmode: "${APISERVER_DB_SSL_MODE:disable}"       # 数据库连接的 SSL 模式

# 网关代理存储配置 - 从 MCP 到 API 映射的配置
storage:
  type: "${GATEWAY_STORAGE_TYPE:db}"                                      # 存储类型：db, api
  revision_history_limit: ${GATEWAY_STORAGE_REVISION_HISTORY_LIMIT:10}    # 保留的版本历史数量
  # 数据库配置（当 type 为 'db' 时使用）
  database:
    type: "${GATEWAY_DB_TYPE:sqlite}"                   # 数据库类型（sqlite,postgres, mysql）
    host: "${GATEWAY_DB_HOST:localhost}"                # 数据库主机地址
    port: ${GATEWAY_DB_PORT:5432}                       # 数据库端口
    user: "${GATEWAY_DB_USER:postgres}"                 # 数据库用户名
    password: "${GATEWAY_DB_PASSWORD:example}"          # 数据库密码
    dbname: "${GATEWAY_DB_NAME:./unla.db}"              # 数据库名称或文件路径
    sslmode: "${GATEWAY_DB_SSL_MODE:disable}"           # 数据库连接的 SSL 模式
  # API 配置（当 type 为 'api' 时使用）
  api:
    url: "${GATEWAY_STORAGE_API_URL:}"                  # API 端点 URL
    configJSONPath: "${GATEWAY_STORAGE_API_CONFIG_JSON_PATH:}"  # API 响应中配置的 JSON 路径
    timeout: "${GATEWAY_STORAGE_API_TIMEOUT:30s}"       # 请求超时时间

# 通知配置 - 作用是当配置更新的时候如何让 mcp-gateway 感知到更新并进行热重载而无需重启服务
notifier:
  role: "${APISERVER_NOTIFIER_ROLE:sender}"  # 角色：'sender'（发送者）或 'receiver'（接收者）
  type: "${APISERVER_NOTIFIER_TYPE:signal}"  # 类型：'signal'（信号）、'api'、'redis' 或 'composite'（组合）
  # 信号配置（当 type 为 'signal' 时使用）
  signal:
    signal: "${APISERVER_NOTIFIER_SIGNAL:SIGHUP}"                       # 要发送的信号
    pid: "${APISERVER_NOTIFIER_SIGNAL_PID:/var/run/mcp-gateway.pid}"    # PID 文件路径
  # API 配置（当 type 为 'api' 时使用）
  api:
    port: ${APISERVER_NOTIFIER_API_PORT:5235}                                           # API 端口
    target_url: "${APISERVER_NOTIFIER_API_TARGET_URL:http://localhost:5235/_reload}"    # 重载端点
  # Redis 配置（当 type 为 'redis' 时使用）
  redis:
    addr: "${APISERVER_NOTIFIER_REDIS_ADDR:localhost:6379}"                             # Redis 地址
    password: "${APISERVER_NOTIFIER_REDIS_PASSWORD:UseStrongPasswordIsAGoodPractice}"   # Redis 密码
    db: ${APISERVER_NOTIFIER_REDIS_DB:0}                                                # Redis 数据库编号
    topic: "${APISERVER_NOTIFIER_REDIS_TOPIC:mcp-gateway:reload}"                       # Redis 发布/订阅主题

# 超级管理员配置
super_admin:
  username: "${SUPER_ADMIN_USERNAME:admin}"                                     # 超级管理员用户名
  password: "${SUPER_ADMIN_PASSWORD:changeme-please-use-a-secure-password}"     # 超级管理员密码（生产环境请修改）

# JWT 配置
jwt:
  secret_key: "${APISERVER_JWT_SECRET_KEY:changeme-please-generate-a-random-secret}"  # JWT密钥（生产环境请修改）
  duration: "${APISERVER_JWT_DURATION:24h}"                                           # Token有效期

# OAuth 登录配置
oauth:
  # Google OAuth 配置
  google:
    client_id: "${OAUTH_GOOGLE_CLIENT_ID:}"                    # Google OAuth Client ID
    client_secret: "${OAUTH_GOOGLE_CLIENT_SECRET:}"            # Google OAuth Client Secret
  # GitHub OAuth 配置
  github:
    client_id: "${OAUTH_GITHUB_CLIENT_ID:}"                    # GitHub OAuth Client ID
    client_secret: "${OAUTH_GITHUB_CLIENT_SECRET:}"            # GitHub OAuth Client Secret
```

## 3.2 MCP Gateway 配置





## 3.3 网关代理配置



## 3.4 Go Template 使用指南



# 04 | Web 配置



# 05 | 客户端使用



# 06 | 开发文档



# 07 | API 文档



# 08 | 端点示例



