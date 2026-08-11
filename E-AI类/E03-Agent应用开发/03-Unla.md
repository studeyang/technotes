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

### 日志配置

日志配置用于控制应用程序的日志输出行为：

```yaml
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
```

### 国际化配置

用于支持多语言界面：

```yaml
i18n:
  path: "${APISERVER_I18N_PATH:/etc/unla/i18n}"                                   # 翻译文件路径
```

### 聊天消息数据库配置

该配置主要针对后台的聊天消息存储的配置（当然这里是可以和代理配置存放在同一个数据库），主要用于存储 Web 界面中的聊天会话和消息数据。

```yaml
# 聊天消息数据库配置
database:
  type: "${APISERVER_DB_TYPE:sqlite}"               # 数据库类型（sqlite,postgres, mysql）
  host: "${APISERVER_DB_HOST:localhost}"            # 数据库主机地址
  port: ${APISERVER_DB_PORT:5432}                   # 数据库端口
  user: "${APISERVER_DB_USER:postgres}"             # 数据库用户名
  password: "${APISERVER_DB_PASSWORD:example}"      # 数据库密码
  dbname: "${APISERVER_DB_NAME:./unla.db}"          # 数据库名称或文件路径
  sslmode: "${APISERVER_DB_SSL_MODE:disable}"       # 数据库连接的 SSL 模式
```

### 网关代理存储配置

这里是用来存放网关代理配置的，也就是对应的从 MCP 到 API 映射的那个配置。

目前支持 2 种存储方式：

- db 存储：存到数据库，每个配置是一条记录。目前支持三种数据库：SQLite3、PostgreSQL、MySQL
- api 存储：通过 API 端点存储配置，允许使用外部配置管理系统

```yaml
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
```

### 通知配置

通知配置模块主要是用来当配置更新的时候如何让 `mcp-gateway` 感知到更新并进行热重载而无需重启服务。

```yaml
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
```

### 超级管理员配置

超级管理员配置用于设置系统初始管理员账户，每次启动 `apiserver` 会自动检测是否存在，若不存在会自动创建。

```yaml
# 超级管理员配置
super_admin:
  username: "${SUPER_ADMIN_USERNAME:admin}"                                     # 超级管理员用户名
  password: "${SUPER_ADMIN_PASSWORD:changeme-please-use-a-secure-password}"     # 超级管理员密码（生产环境请修改）


```

### JWT 配置

JWT 配置用于设置 web 认证相关的参数：

```yaml
# JWT 配置
jwt:
  secret_key: "${APISERVER_JWT_SECRET_KEY:changeme-please-generate-a-random-secret}"  # JWT密钥（生产环境请修改）
  duration: "${APISERVER_JWT_DURATION:24h}"                                           # Token有效期
```

### OAuth 登录配置

OAuth 配置用于支持第三方登录功能，目前支持 `Google` 和 `GitHub` 登录。配置了对应的 `client_id` 和 `client_secret` 后，Web 界面会自动启用 OAuth 登录选项。

```yaml
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

### 基础配置

```yaml
#基础配置
port: ${MCP_GATEWAY_PORT:5235}                      # 服务监听端口
pid: "${MCP_GATEWAY_PID:/var/run/mcp-gateway.pid}"  # PID文件路径
```

### 存储配置

存储配置模块主要用于存储网关的代理配置信息。目前支持两种存储方式：

- db 存储：存到数据库，每个配置是一条记录，支持 SQLite3、PostgreSQL、MySQL
- api 存储：通过 API 端点存储配置，允许使用外部配置管理系统

```yaml
#存储配置
storage:
  type: "${GATEWAY_STORAGE_TYPE:db}"                    # 存储类型：db, api

  # 数据库配置（当 type 为 'db' 时使用）
  database:
    type: "${GATEWAY_DB_TYPE:sqlite}"                   # 数据库类型（sqlite,postgres, mysql）
    host: "${GATEWAY_DB_HOST:localhost}"                # 数据库主机地址
    port: ${GATEWAY_DB_PORT:5432}                       # 数据库端口
    user: "${GATEWAY_DB_USER:postgres}"                 # 数据库用户名
    password: "${GATEWAY_DB_PASSWORD:example}"          # 数据库密码
    dbname: "${GATEWAY_DB_NAME:./data/mcp-gateway.db}"  # 数据库名称或文件路径
    sslmode: "${GATEWAY_DB_SSL_MODE:disable}"           # 数据库连接的 SSL 模式

  # API 配置（当 type 为 'api' 时使用）
  api:
    url: "${GATEWAY_STORAGE_API_URL:}"                  # API 端点 URL
    configJSONPath: "${GATEWAY_STORAGE_API_CONFIG_JSON_PATH:}"  # API 响应中配置的 JSON 路径
    timeout: "${GATEWAY_STORAGE_API_TIMEOUT:30s}"       # 请求超时时间
```

### 通知配置

支持的通知方式：

- signal：通过发送操作系统信号量来通知，类似 `kill -SIGHUP <pid>` 或者 `nginx -s reload` 这种方式
- api：通过调用一个 API 的方式通知，`mcp-gateway` 会监听一个独立的端口
- redis：通过 redis 的发布/订阅功能通知，适合单机或集群部署时使用
- composite：组合通知，通过多种方式组合，默认 `signal` 和 `api` 一定会开启

```yaml
#通知配置
notifier:
  role: "${NOTIFIER_ROLE:receiver}" # 角色：'sender'（发送者）或 'receiver'（接收者）
  type: "${NOTIFIER_TYPE:signal}"   # 类型：'signal'（信号）、'api'、'redis' 或 'composite'（组合）

  # 信号配置（当 type 为 'signal' 时使用）
  signal:
    signal: "${NOTIFIER_SIGNAL:SIGHUP}"                     # 要发送的信号
    pid: "${NOTIFIER_SIGNAL_PID:/var/run/mcp-gateway.pid}"  # PID 文件路径

  # API 配置（当 type 为 'api' 时使用）
  api:
    port: ${NOTIFIER_API_PORT:5235}                                         # API 端口
    target_url: "${NOTIFIER_API_TARGET_URL:http://localhost:5235/_reload}"  # 重载端点

  # Redis 配置（当 type 为 'redis' 时使用）
  redis:
    addr: "${NOTIFIER_REDIS_ADDR:localhost:6379}"                               # Redis 地址
    password: "${NOTIFIER_REDIS_PASSWORD:UseStrongPasswordIsAGoodPractice}"     # Redis 密码
    db: ${NOTIFIER_REDIS_DB:0}                                                  # Redis 数据库编号
    topic: "${NOTIFIER_REDIS_TOPIC:mcp-gateway:reload}"                         # Redis 发布/订阅主题
```

### 会话存储配置

会话存储配置用于存储 MCP 中的会话信息。根据不同的部署场景，可以选择不同的存储方式：

- memory 存储：内存存储，适合单机部署（需注意，重启会失去会话信息）
- redis 存储：Redis 存储，适合单机或集群部署，支持持久化

```yaml
#会话存储配置
session:
  type: "${SESSION_STORAGE_TYPE:memory}"                    # 存储类型：memory, redis
  redis:
    addr: "${SESSION_REDIS_ADDR:localhost:6379}"            # Redis 地址
    password: "${SESSION_REDIS_PASSWORD:}"                  # Redis 密码
    db: ${SESSION_REDIS_DB:0}                               # Redis 数据库编号
    topic: "${SESSION_REDIS_TOPIC:mcp-gateway:session}"     # Redis 发布/订阅主题
```

### Forward Headers 配置

Forward Headers 配置允许 MCP Gateway 将客户端请求中的 HTTP 头部转发到下游服务。此功能对于身份验证、请求追踪和自定义头部传播非常有用。

```yaml
#Forward Headers 配置
forward:
  enabled: ${FORWARD_ENABLED:false}                                     # 启用 forward headers（默认：false）
  
  mcp_arg:
    key_for_header: "${FORWARD_MCP_ARG_KEY_FOR_HEADER:__forwardHeaders}" # 工具参数的参数名
  
  header:
    allow_headers: "${FORWARD_ALLOW_HEADERS:}"                          # 允许的头部列表，逗号分隔（优先级更高）
    ignore_headers: "${FORWARD_IGNORE_HEADERS:Accept, Accept-Encoding, Accept-Language, Host, Cookie, Connection, User-Agent, Content-Length, Content-Type}" # 要忽略的头部
    case_insensitive: ${FORWARD_HEADER_CASE_INSENSITIVE:true}           # 大小写不敏感的头部匹配
    override_existing: ${FORWARD_HEADER_OVERRIDE_EXISTING:false}        # 覆盖现有头部而不是添加
```

**示例 1: 只允许特定头部**

只有 `Authorization`、`X-API-Key` 和 `X-Request-ID` 头部会被转发。

```yaml
forward:
  enabled: true
  header:
    allow_headers: "Authorization, X-API-Key, X-Request-ID"
    ignore_headers: "Host, Cookie"  # 这个会被忽略
    case_insensitive: true
```

**示例 2: 阻止特定头部**

除了 `Accept`、`Host`、`Cookie` 和 `User-Agent` 外，所有头部都会被转发。

```yaml
forward:
  enabled: true
  header:
    allow_headers: ""  # 空值 - 使用忽略列表
    ignore_headers: "Accept, Host, Cookie, User-Agent"
    case_insensitive: true
```

**示例 3: 工具参数头部**


```yaml
forward:
  enabled: true
  mcp_arg:
    key_for_header: "custom_headers"
  header:
    override_existing: true
```

工具现在可以通过 `custom_headers` 参数传递头部：


```yaml
{
  "name": "api_call",
  "arguments": {
    "url": "https://api.example.com/data",
    "custom_headers": {
      "Authorization": "Bearer token123",
      "X-Custom-Header": "value"
    }
  }
}
```

### 链路追踪

MCP Gateway 支持通过 OpenTelemetry 将链路追踪数据导出到 Jaeger。该功能可选，默认关闭。


```yaml
tracing:
  enabled: ${TRACING_ENABLED:false}
  service_name: "${TRACING_SERVICE_NAME:mcp-gateway}"
  endpoint: "${TRACING_ENDPOINT:localhost:4317}"   # Jaeger OTLP 采集端：gRPC(4317) 或 HTTP(4318)
  protocol: "${TRACING_PROTOCOL:grpc}"             # grpc 或 http
  insecure: ${TRACING_INSECURE:true}
  sampler_rate: ${TRACING_SAMPLER_RATE:0.1}         # 0.0 ~ 1.0
  environment: "${TRACING_ENV:dev}"
  headers: {}                                       # 可选导出器请求头
  capture:
    downstream_error:
      enabled: ${TRACING_ERR_BODY_ENABLED:false}
      max_body_length: ${TRACING_ERR_BODY_MAX_LEN:256}
    # 全局抓取设置 — 谨慎使用，避免泄露敏感信息。
    downstream_request:
      enabled: ${TRACING_REQ_ARGS_ENABLED:false}
      body_enabled: ${TRACING_REQ_BODY_ENABLED:false}
      body_max_length: ${TRACING_REQ_BODY_MAX_LEN:256}
      max_field_length: ${TRACING_REQ_ARG_MAX_LEN:256}
      include_fields: "${TRACING_INCLUDE_FIELDS:}"   # CSV 或 JSON Map: key=模板
```

## 3.3 网关代理配置



## 3.4 Go Template 使用指南



# 04 | Web 配置



# 05 | 客户端使用



# 06 | 开发文档



# 07 | API 文档



# 08 | 端点示例



